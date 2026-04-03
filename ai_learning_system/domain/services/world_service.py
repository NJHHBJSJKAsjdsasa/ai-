"""
世界领域服务模块
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from domain.entities.world import World
from domain.entities.location import Location
from domain.value_objects.location import LocationValue, GeneratedLocationValue
from config import GAME_CONFIG


@dataclass
class WorldService:
    """世界领域服务"""
    
    def initialize_world(self, world_id: str, world_name: str) -> World:
        """
        初始化世界
        
        Args:
            world_id: 世界ID
            world_name: 世界名称
            
        Returns:
            世界实体
        """
        world = World(id=world_id, name=world_name)
        self._init_locations(world)
        return world
    
    def _init_locations(self, world: World):
        """
        初始化地点 - 支持树形结构
        
        Args:
            world: 世界实体
        """
        locations_config = GAME_CONFIG.get("world", {}).get("locations", [])
        
        # 第一遍：创建所有地点
        for loc_config in locations_config:
            location_value = LocationValue(
                name=loc_config.get("name", ""),
                description=loc_config.get("description", ""),
                realm_required=loc_config.get("realm_required", 0),
                danger_level=loc_config.get("danger_level", "普通"),
                location_type=loc_config.get("location_type", "普通"),
                parent_location=loc_config.get("parent_location", "")
            )
            
            location = Location(
                name=location_value.name,
                location_value=location_value
            )
            
            world.add_location(location)
        
        # 第二遍：建立父子关系
        for location in world.get_all_locations():
            if location.location_value.parent_location:
                parent_name = location.location_value.parent_location
                parent_location = world.get_location(parent_name)
                if parent_location:
                    parent_location.add_sub_location(location.name)
        
        # 第三遍：建立同层级地点之间的连接
        for location in world.get_all_locations():
            if location.location_value.parent_location:
                # 找到同父的所有兄弟节点
                siblings = [
                    loc for loc in world.get_all_locations()
                    if loc.location_value.parent_location == location.location_value.parent_location 
                    and loc.name != location.name
                ]
                # 添加到连接
                for sibling in siblings:
                    world.connect_locations(location.name, sibling.name)
        
        # 为根节点（没有父节点的地点）之间也建立连接
        root_locations = [loc for loc in world.get_all_locations() if not loc.location_value.parent_location]
        for i, loc in enumerate(root_locations):
            if i > 0:
                world.connect_locations(loc.name, root_locations[i-1].name)
            if i < len(root_locations) - 1:
                world.connect_locations(loc.name, root_locations[i+1].name)
    
    def add_generated_location(self, world: World, generated_location: GeneratedLocationValue) -> bool:
        """
        添加动态生成的地点
        
        Args:
            world: 世界实体
            generated_location: 生成的地点值对象
            
        Returns:
            是否添加成功
        """
        try:
            # 创建LocationValue
            location_value = LocationValue(
                name=generated_location.name,
                description=generated_location.description,
                realm_required=generated_location.realm_required,
                connections=generated_location.connections
            )
            
            # 创建Location实体
            location = Location(
                name=generated_location.name,
                location_value=location_value,
                generated_value=generated_location
            )
            
            world.add_location(location)
            return True
        except Exception:
            return False
    
    def get_location_description(self, world: World, location_name: str) -> str:
        """
        获取地点描述
        
        Args:
            world: 世界实体
            location_name: 地点名称
            
        Returns:
            描述文本
        """
        location = world.get_location(location_name)
        if not location:
            return "未知之地"
        
        loc_value = location.location_value
        
        # 构建门派信息
        sect_info = ""
        if loc_value.sects:
            sect_details = []
            for sect_name in loc_value.sects:
                sect_details.append(sect_name)
            sect_info = f"\n║  门派: {', '.join(sect_details)}" if sect_details else ""
        
        description = f"""
╔══════════════════════════════════════════════════════════╗
║  📍 {loc_value.name}                                          ║
╠══════════════════════════════════════════════════════════╣
║  {loc_value.description}                                  ║
╠══════════════════════════════════════════════════════════╣
║  进入要求: {self._get_realm_name(loc_value.realm_required)}                                        ║
║  可前往: {', '.join(loc_value.connections)}                          ║
{sect_info}
╚══════════════════════════════════════════════════════════╝
"""
        
        return description
    
    def get_generated_location_description(self, world: World, location_name: str) -> str:
        """
        获取生成地点的详细描述
        
        Args:
            world: 世界实体
            location_name: 地点名称
            
        Returns:
            描述文本
        """
        location = world.get_location(location_name)
        if not location or not location.generated_value:
            return self.get_location_description(world, location_name)
        
        gen_loc = location.generated_value
        
        description = f"""
╔══════════════════════════════════════════════════════════╗
║  📍 {gen_loc.name}                                          ║
╠══════════════════════════════════════════════════════════╣
║  {gen_loc.description[:40]}...                                  ║
╠══════════════════════════════════════════════════════════╣
║  类型: {gen_loc.map_type}  规模: {gen_loc.size}  等级: {gen_loc.level}                    ║
║  进入要求: {self._get_realm_name(gen_loc.realm_required)}                                        ║
║  可前往: {', '.join(gen_loc.connections) if gen_loc.connections else '无'}                          ║
╚══════════════════════════════════════════════════════════╝
"""
        
        return description
    
    def _get_realm_name(self, realm_level: int) -> str:
        """
        获取境界名称
        
        Args:
            realm_level: 境界等级
            
        Returns:
            境界名称
        """
        from config import get_realm_info
        realm_info = get_realm_info(realm_level)
        return realm_info.name if realm_info else "凡人"
    
    def can_enter(self, world: World, location_name: str, realm_level: int) -> bool:
        """
        检查是否可以进入地点
        
        Args:
            world: 世界实体
            location_name: 地点名称
            realm_level: 境界等级
            
        Returns:
            是否可以进入
        """
        location = world.get_location(location_name)
        if not location:
            return False
        return location.is_accessible(realm_level)
    
    def get_location_by_sect(self, world: World, sect_name: str) -> Optional[str]:
        """
        根据门派获取所在地点
        
        Args:
            world: 世界实体
            sect_name: 门派名称
            
        Returns:
            地点名称
        """
        for location in world.get_all_locations():
            if sect_name in location.location_value.sects:
                return location.name
        return None