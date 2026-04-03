"""
世界系统适配器模块
将新的领域模型与现有的游戏系统集成
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

from domain.entities.world import World as DomainWorld
from domain.entities.location import Location as DomainLocation
from domain.value_objects.location import LocationValue, GeneratedLocationValue
from domain.services.world_service import WorldService
from domain.services.time_service import RealTimeSystem

from config import GAME_CONFIG, get_realm_info, SECT_DETAILS
from storage.database import Database
from game.npc import NPC, NPCManager
from game.world_evolution_system import WorldEvolutionManager


@dataclass
class Location:
    """地点数据类（兼容旧接口）"""
    name: str
    description: str
    realm_required: int
    connections: List[str] = None
    sects: List[str] = None  # 该地点的门派
    danger_level: str = "安全"  # 危险等级：安全、普通、危险、绝境
    parent_location: str = ""  # 父地点（用于树形结构）
    sub_locations: List[str] = None  # 子地点列表
    location_type: str = "普通"  # 地点类型：区域、城镇、门派、洞府、野外等
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.sects is None:
            self.sects = []
        if self.sub_locations is None:
            self.sub_locations = []
    
    def get_realm_name(self) -> str:
        """获取境界要求的名称"""
        realm_info = get_realm_info(self.realm_required)
        return realm_info.name if realm_info else "凡人"
    
    def is_accessible(self, player_realm_level: int) -> bool:
        """检查玩家是否可以进入该地点"""
        return player_realm_level >= self.realm_required


@dataclass
class GeneratedLocation:
    """动态生成的地点数据类（兼容旧接口）"""
    id: str
    name: str
    description: str
    realm_required: int
    map_type: str = ""
    level: int = 1
    size: str = "中型"
    history: str = ""
    environment: str = ""
    connections: List[str] = None
    npcs: List[str] = None
    monsters: List[str] = None
    items: List[str] = None
    is_generated: bool = True
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.npcs is None:
            self.npcs = []
        if self.monsters is None:
            self.monsters = []
        if self.items is None:
            self.items = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'realm_required': self.realm_required,
            'map_type': self.map_type,
            'level': self.level,
            'size': self.size,
            'history': self.history,
            'environment': self.environment,
            'connections': self.connections,
            'npcs': self.npcs,
            'monsters': self.monsters,
            'items': self.items,
            'is_generated': self.is_generated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedLocation':
        """从字典创建"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            realm_required=data.get('realm_required', 0),
            map_type=data.get('map_type', ''),
            level=data.get('level', 1),
            size=data.get('size', '中型'),
            history=data.get('history', ''),
            environment=data.get('environment', ''),
            connections=data.get('connections', []),
            npcs=data.get('npcs', []),
            monsters=data.get('monsters', []),
            items=data.get('items', []),
            is_generated=data.get('is_generated', True),
        )


class World:
    """世界类（兼容旧接口）
    
    支持静态地点（从配置加载）和动态地点（从数据库加载或生成）
    集成NPC独立系统
    """
    
    def __init__(self, db: Database = None):
        """
        初始化世界
        
        Args:
            db: 数据库实例，如果为None则创建新实例
        """
        self.db = db or Database()
        
        # 初始化领域模型
        self.world_service = WorldService()
        self.domain_world = self.world_service.initialize_world("world_1", "修仙世界")
        
        # 初始化时间系统
        self.time_system = RealTimeSystem()
        
        # 初始化NPC管理器
        self.npc_manager = NPCManager()
        self._last_npc_update = 0.0

        # 初始化世界演化管理器
        self.world_evolution_manager = WorldEvolutionManager(self.db)

        # 使用统一进度条初始化所有内容
        self._init_with_progress()
    
    def _init_with_progress(self):
        """使用统一进度条初始化世界"""
        # 定义所有初始化步骤
        init_steps = [
            ("加载已生成地点", self._load_generated_locations),
            ("初始化NPC", self._init_npcs),
        ]
        
        total_steps = len(init_steps)
        
        for i, (step_name, step_func) in enumerate(init_steps):
            # 计算进度
            progress = (i + 1) / total_steps
            bar_length = 30
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # 显示进度条
            import sys
            sys.stdout.write(f"\r🎭 正在{step_name} [{bar}] {i+1}/{total_steps} ({progress*100:.0f}%)")
            sys.stdout.flush()
            
            # 执行初始化步骤
            step_func()
        
        print(f"\n✅ 世界初始化完成！")
    
    def _load_generated_locations(self):
        """从数据库加载生成的地点"""
        try:
            # 确保数据库表已创建
            self.db.init_generated_tables()
            
            # 从数据库加载所有生成的地图
            for level in range(1, 10):
                maps = self.db.get_generated_maps_by_level(level)
                for map_data in maps:
                    # 创建GeneratedLocationValue
                    gen_loc_value = GeneratedLocationValue(
                        id=map_data.get('id', ''),
                        name=map_data.get('name', ''),
                        description=map_data.get('description', ''),
                        realm_required=map_data.get('realm_required', 0),
                        map_type=map_data.get('map_type', ''),
                        level=map_data.get('level', 1),
                        size=map_data.get('size', '中型'),
                        history=map_data.get('history', ''),
                        environment=map_data.get('environment', ''),
                        connections=map_data.get('connections', []),
                        npcs=map_data.get('npcs', []),
                        monsters=map_data.get('monsters', []),
                        items=map_data.get('items', []),
                        is_generated=map_data.get('is_generated', True)
                    )
                    
                    # 添加到领域世界
                    self.world_service.add_generated_location(self.domain_world, gen_loc_value)
        except Exception as e:
            print(f"加载生成地点时出错: {e}")
    
    def _init_npcs(self):
        """为所有地点初始化NPC - 优先从数据库加载完整数据，没有则生成"""
        # 为每个地点加载或生成NPC
        npc_count_per_location = GAME_CONFIG.get("npc", {}).get("npc_count_per_location", 3)
        location_names = [loc.name for loc in self.domain_world.get_all_locations()]
        
        # 统计信息
        loaded_count = 0
        generated_count = 0
        
        # 静默加载所有NPC（进度条由上层统一显示）
        for location_name in location_names:
            # 先尝试从数据库加载该地点的NPC（使用完整加载方法）
            saved_npcs = self.db.get_npcs_by_location_full(location_name)
            
            if saved_npcs:
                # 从数据库加载NPC
                loaded_count += len(saved_npcs)
                for npc_data in saved_npcs:
                    # 检查NPC是否已存在（避免重复加载）
                    npc_id = npc_data.get('id')
                    if npc_id and npc_id in self.npc_manager.npcs:
                        continue  # 跳过已存在的NPC
                    
                    # 使用NPC.from_dict()从完整数据创建NPC对象
                    try:
                        npc = NPC.from_dict(npc_data)
                        self.npc_manager.npcs[npc.data.id] = npc
                        self.npc_manager.independent_manager.add_npc(npc.independent, location_name)
                    except Exception as e:
                        continue
            else:
                # 数据库中没有，生成新的NPC
                npcs = self.npc_manager.generate_npcs_for_location(location_name, npc_count_per_location, self.db, show_progress=False)
                generated_count += len(npcs)
    
    def get_location(self, name: str) -> Optional[Location]:
        """
        获取地点
        
        Args:
            name: 地点名称
            
        Returns:
            地点对象
        """
        domain_location = self.domain_world.get_location(name)
        if not domain_location:
            return None
        
        # 转换为旧接口的Location对象
        loc_value = domain_location.location_value
        return Location(
            name=loc_value.name,
            description=loc_value.description,
            realm_required=loc_value.realm_required,
            connections=loc_value.connections,
            sects=loc_value.sects,
            danger_level=loc_value.danger_level,
            parent_location=loc_value.parent_location,
            sub_locations=loc_value.sub_locations,
            location_type=loc_value.location_type
        )
    
    def can_enter(self, location_name: str, realm_level: int) -> bool:
        """
        检查是否可以进入地点
        
        Args:
            location_name: 地点名称
            realm_level: 境界等级
            
        Returns:
            是否可以进入
        """
        return self.world_service.can_enter(self.domain_world, location_name, realm_level)
    
    def get_accessible_locations(self, current_location: str, realm_level: int) -> List[str]:
        """
        获取可到达的地点
        
        Args:
            current_location: 当前地点
            realm_level: 境界等级
            
        Returns:
            地点名称列表
        """
        return self.domain_world.get_accessible_locations(current_location, realm_level)
    
    def get_location_description(self, name: str) -> str:
        """
        获取地点描述
        
        Args:
            name: 地点名称
            
        Returns:
            描述文本
        """
        return self.world_service.get_location_description(self.domain_world, name)
    
    def get_sect_info(self, sect_name: str) -> Optional[Dict[str, Any]]:
        """
        获取门派详细信息
        
        Args:
            sect_name: 门派名称
            
        Returns:
            门派信息字典
        """
        if sect_name in SECT_DETAILS:
            return SECT_DETAILS[sect_name]
        return None
    
    def get_location_by_sect(self, sect_name: str) -> Optional[str]:
        """
        根据门派获取所在地点
        
        Args:
            sect_name: 门派名称
            
        Returns:
            地点名称
        """
        return self.world_service.get_location_by_sect(self.domain_world, sect_name)
    
    def get_all_locations(self) -> List[Location]:
        """获取所有地点"""
        locations = []
        for domain_location in self.domain_world.get_all_locations():
            loc_value = domain_location.location_value
            location = Location(
                name=loc_value.name,
                description=loc_value.description,
                realm_required=loc_value.realm_required,
                connections=loc_value.connections,
                sects=loc_value.sects,
                danger_level=loc_value.danger_level,
                parent_location=loc_value.parent_location,
                sub_locations=loc_value.sub_locations,
                location_type=loc_value.location_type
            )
            locations.append(location)
        return locations
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            name: {
                "name": loc.name,
                "description": loc.description,
                "realm_required": loc.realm_required,
                "connections": loc.connections,
            }
            for name, loc in {loc.name: loc for loc in self.get_all_locations()}.items()
        }
    
    def add_generated_location(self, gen_loc: GeneratedLocation) -> bool:
        """
        添加动态生成的地点
        
        Args:
            gen_loc: 生成的地点对象
            
        Returns:
            是否添加成功
        """
        try:
            # 创建GeneratedLocationValue
            gen_loc_value = GeneratedLocationValue(
                id=gen_loc.id,
                name=gen_loc.name,
                description=gen_loc.description,
                realm_required=gen_loc.realm_required,
                map_type=gen_loc.map_type,
                level=gen_loc.level,
                size=gen_loc.size,
                history=gen_loc.history,
                environment=gen_loc.environment,
                connections=gen_loc.connections,
                npcs=gen_loc.npcs,
                monsters=gen_loc.monsters,
                items=gen_loc.items,
                is_generated=gen_loc.is_generated
            )
            
            # 添加到领域世界
            success = self.world_service.add_generated_location(self.domain_world, gen_loc_value)
            
            # 保存到数据库
            if success:
                self.db.save_generated_map(gen_loc.to_dict())
            
            return success
        except Exception as e:
            print(f"添加生成地点时出错: {e}")
            return False
    
    def connect_locations(self, loc1_name: str, loc2_name: str, bidirectional: bool = True) -> bool:
        """
        建立两个地点之间的连接
        
        Args:
            loc1_name: 地点1名称
            loc2_name: 地点2名称
            bidirectional: 是否双向连接，默认为True
            
        Returns:
            是否连接成功
        """
        return self.domain_world.connect_locations(loc1_name, loc2_name, bidirectional)
    
    def get_generated_location(self, name: str) -> Optional[GeneratedLocation]:
        """
        获取生成的地点详情
        
        Args:
            name: 地点名称
            
        Returns:
            生成的地点对象
        """
        domain_location = self.domain_world.get_location(name)
        if not domain_location or not domain_location.generated_value:
            return None
        
        gen_value = domain_location.generated_value
        return GeneratedLocation(
            id=gen_value.id,
            name=gen_value.name,
            description=gen_value.description,
            realm_required=gen_value.realm_required,
            map_type=gen_value.map_type,
            level=gen_value.level,
            size=gen_value.size,
            history=gen_value.history,
            environment=gen_value.environment,
            connections=gen_value.connections,
            npcs=gen_value.npcs,
            monsters=gen_value.monsters,
            items=gen_value.items,
            is_generated=gen_value.is_generated
        )
    
    def get_all_generated_locations(self) -> List[GeneratedLocation]:
        """获取所有生成的地点"""
        generated_locations = []
        for domain_location in self.domain_world.get_all_locations():
            if domain_location.generated_value:
                gen_value = domain_location.generated_value
                gen_loc = GeneratedLocation(
                    id=gen_value.id,
                    name=gen_value.name,
                    description=gen_value.description,
                    realm_required=gen_value.realm_required,
                    map_type=gen_value.map_type,
                    level=gen_value.level,
                    size=gen_value.size,
                    history=gen_value.history,
                    environment=gen_value.environment,
                    connections=gen_value.connections,
                    npcs=gen_value.npcs,
                    monsters=gen_value.monsters,
                    items=gen_value.items,
                    is_generated=gen_value.is_generated
                )
                generated_locations.append(gen_loc)
        return generated_locations
    
    def is_generated_location(self, name: str) -> bool:
        """
        检查地点是否为动态生成
        
        Args:
            name: 地点名称
            
        Returns:
            是否为生成地点
        """
        domain_location = self.domain_world.get_location(name)
        return domain_location is not None and domain_location.is_generated()
    
    def get_location_npcs(self, location_name: str) -> List[Dict[str, Any]]:
        """
        获取地点的NPC列表
        
        Args:
            location_name: 地点名称
            
        Returns:
            NPC数据列表
        """
        try:
            return self.db.get_generated_npcs_by_location(location_name)
        except Exception as e:
            print(f"获取地点NPC时出错: {e}")
            return []
    
    def get_location_monsters(self, location_name: str) -> List[Dict[str, Any]]:
        """
        获取地点的妖兽列表
        
        Args:
            location_name: 地点名称
            
        Returns:
            妖兽数据列表
        """
        try:
            return self.db.get_generated_monsters_by_location(location_name)
        except Exception as e:
            print(f"获取地点妖兽时出错: {e}")
            return []
    
    def get_generated_location_description(self, name: str) -> str:
        """
        获取生成地点的详细描述
        
        Args:
            name: 地点名称
            
        Returns:
            描述文本
        """
        return self.world_service.get_generated_location_description(self.domain_world, name)
    
    def update_npcs(self, current_time: float = None, player_location: str = None):
        """
        更新所有NPC（独立系统）
        
        Args:
            current_time: 当前时间戳
            player_location: 玩家当前位置
        """
        if current_time is None:
            current_time = time.time()
        
        # 限制更新频率（每秒最多一次）
        if current_time - self._last_npc_update < 1.0:
            return
        
        self._last_npc_update = current_time
        
        # 更新NPC
        self.npc_manager.update_all(current_time, player_location)
    
    def get_npcs_in_location(self, location: str) -> List[NPC]:
        """
        获取地点的所有NPC
        
        Args:
            location: 地点名称
            
        Returns:
            NPC列表
        """
        return self.npc_manager.get_npcs_in_location(location)
    
    def get_npc_by_name(self, name: str) -> Optional[NPC]:
        """
        根据名字获取NPC
        
        Args:
            name: NPC名字
            
        Returns:
            NPC对象
        """
        return self.npc_manager.get_npc_by_name(name)
    
    def get_npc_stats(self) -> Dict[str, Any]:
        """获取NPC系统统计信息"""
        return self.npc_manager.get_independent_stats()
    
    def socialize_npcs(self, npc_id1: str, npc_id2: str):
        """
        两个NPC之间进行社交
        
        Args:
            npc_id1: 第一个NPC的ID
            npc_id2: 第二个NPC的ID
        """
        self.npc_manager.socialize_npcs(npc_id1, npc_id2)
    
    def get_location_with_npcs(self, name: str) -> str:
        """
        获取地点描述（包含NPC信息）
        
        Args:
            name: 地点名称
            
        Returns:
            描述文本
        """
        # 获取基础描述
        if self.is_generated_location(name):
            description = self.get_generated_location_description(name)
        else:
            description = self.get_location_description(name)
        
        # 获取该地点的NPC
        npcs = self.get_npcs_in_location(name)
        if npcs:
            npc_info = "\n👥 当前在此的修士:\n"
            for npc in npcs[:5]:  # 最多显示5个
                status = npc.get_independent_status()
                npc_info += f"  • {npc.data.dao_name} ({npc.get_realm_name()}) - {status['current_activity']}\n"
            if len(npcs) > 5:
                npc_info += f"  ... 还有{len(npcs) - 5}位修士\n"
            description += npc_info
        
        return description