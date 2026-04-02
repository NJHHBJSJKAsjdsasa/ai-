"""
世界系统模块
管理地图、时间等
支持动态生成地点
集成NPC独立系统
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import json
import time

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG, get_realm_info, SECT_DETAILS
from storage.database import Database

# 导入NPC系统
from game.npc import NPC, NPCManager
from game.world_evolution_system import WorldEvolutionManager


@dataclass
class GeneratedLocation:
    """动态生成的地点数据类"""
    id: str
    name: str
    description: str
    realm_required: int
    map_type: str = ""
    level: int = 1
    size: str = "中型"
    history: str = ""
    environment: str = ""
    connections: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    monsters: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    is_generated: bool = True
    
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


@dataclass
class Location:
    """地点数据类"""
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
        from config import get_realm_info
        realm_info = get_realm_info(self.realm_required)
        return realm_info.name if realm_info else "凡人"
    
    def is_accessible(self, player_realm_level: int) -> bool:
        """检查玩家是否可以进入该地点"""
        return player_realm_level >= self.realm_required


class GameTime:
    """游戏时间类"""
    
    def __init__(self, year: int = 1, month: int = 1, day: int = 1):
        """
        初始化游戏时间
        
        Args:
            year: 年
            month: 月
            day: 日
        """
        self.year = year
        self.month = month
        self.day = day
    
    def advance(self, days: int = 1):
        """
        推进时间
        
        Args:
            days: 天数
        """
        for _ in range(days):
            self.day += 1
            if self.day > 30:
                self.day = 1
                self.month += 1
                if self.month > 12:
                    self.month = 1
                    self.year += 1
    
    def to_string(self) -> str:
        """转换为字符串"""
        return f"第{self.year}年{self.month}月{self.day}日"
    
    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
        }


class World:
    """世界类
    
    支持静态地点（从配置加载）和动态地点（从数据库加载或生成）
    集成NPC独立系统
    """
    
    def __init__(self, db: Database = None):
        """
        初始化世界
        
        Args:
            db: 数据库实例，如果为None则创建新实例
        """
        self.locations: Dict[str, Location] = {}
        self.generated_locations: Dict[str, GeneratedLocation] = {}
        self.db = db or Database()
        
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
            ("初始化地点", self._init_locations),
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
            sys.stdout.write(f"\r🎭 正在{step_name} [{bar}] {i+1}/{total_steps} ({progress*100:.0f}%)")
            sys.stdout.flush()
            
            # 执行初始化步骤
            step_func()
        
        print(f"\n✅ 世界初始化完成！")
    
    def _init_locations(self):
        """初始化地点 - 支持树形结构"""
        locations_config = GAME_CONFIG["world"]["locations"]

        # 第一遍：创建所有地点
        for loc_config in locations_config:
            location = Location(
                name=loc_config["name"],
                description=loc_config["description"],
                realm_required=loc_config.get("realm_required", 0),
                danger_level=loc_config.get("danger_level", "普通"),
                location_type=loc_config.get("location_type", "普通"),
                parent_location=loc_config.get("parent_location", ""),
            )
            self.locations[location.name] = location

        # 第二遍：建立父子关系
        for location in self.locations.values():
            if location.parent_location and location.parent_location in self.locations:
                parent = self.locations[location.parent_location]
                if location.name not in parent.sub_locations:
                    parent.sub_locations.append(location.name)

        # 第三遍：建立同层级地点之间的连接
        for location in self.locations.values():
            if location.parent_location:
                # 找到同父的所有兄弟节点
                siblings = [
                    loc for loc in self.locations.values()
                    if loc.parent_location == location.parent_location and loc.name != location.name
                ]
                # 添加到连接
                for sibling in siblings:
                    if sibling.name not in location.connections:
                        location.connections.append(sibling.name)

        # 为根节点（没有父节点的地点）之间也建立连接
        root_locations = [loc for loc in self.locations.values() if not loc.parent_location]
        for i, loc in enumerate(root_locations):
            if i > 0:
                if root_locations[i-1].name not in loc.connections:
                    loc.connections.append(root_locations[i-1].name)
            if i < len(root_locations) - 1:
                if root_locations[i+1].name not in loc.connections:
                    loc.connections.append(root_locations[i+1].name)
    
    def get_location(self, name: str) -> Optional[Location]:
        """
        获取地点
        
        Args:
            name: 地点名称
            
        Returns:
            地点对象
        """
        return self.locations.get(name)
    
    def can_enter(self, location_name: str, realm_level: int) -> bool:
        """
        检查是否可以进入地点
        
        Args:
            location_name: 地点名称
            realm_level: 境界等级
            
        Returns:
            是否可以进入
        """
        location = self.locations.get(location_name)
        if not location:
            return False
        return realm_level >= location.realm_required
    
    def get_accessible_locations(self, current_location: str, realm_level: int) -> List[str]:
        """
        获取可到达的地点
        
        Args:
            current_location: 当前地点
            realm_level: 境界等级
            
        Returns:
            地点名称列表
        """
        location = self.locations.get(current_location)
        if not location:
            return []
        
        accessible = []
        for conn in location.connections:
            if self.can_enter(conn, realm_level):
                accessible.append(conn)
        
        return accessible
    
    def get_location_description(self, name: str) -> str:
        """
        获取地点描述
        
        Args:
            name: 地点名称
            
        Returns:
            描述文本
        """
        location = self.locations.get(name)
        if not location:
            return "未知之地"
        
        realm_info = get_realm_info(location.realm_required)
        realm_name = realm_info.name if realm_info else "凡人"
        
        # 构建门派信息
        sect_info = ""
        if location.sects:
            sect_details = []
            for sect_name in location.sects:
                if sect_name in SECT_DETAILS:
                    sect_data = SECT_DETAILS[sect_name]
                    sect_type = sect_data.get("type", "未知")
                    sect_details.append(f"{sect_name}({sect_type})")
                else:
                    sect_details.append(sect_name)
            sect_info = f"\n║  门派: {', '.join(sect_details)}" if sect_details else ""
        
        description = f"""
╔══════════════════════════════════════════════════════════╗
║  📍 {location.name}                                          ║
╠══════════════════════════════════════════════════════════╣
║  {location.description}                                  ║
╠══════════════════════════════════════════════════════════╣
║  进入要求: {realm_name}                                        ║
║  可前往: {', '.join(location.connections)}                          ║
{sect_info}
╚══════════════════════════════════════════════════════════╝
"""
        return description
    
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
        for loc_name, location in self.locations.items():
            if sect_name in location.sects:
                return loc_name
        return None
    
    def get_all_locations(self) -> List[Location]:
        """获取所有地点"""
        return list(self.locations.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            name: {
                "name": loc.name,
                "description": loc.description,
                "realm_required": loc.realm_required,
                "connections": loc.connections,
            }
            for name, loc in self.locations.items()
        }
    
    # ==================== 动态地点管理 ====================
    
    def _load_generated_locations(self):
        """从数据库加载生成的地点"""
        try:
            # 确保数据库表已创建
            self.db.init_generated_tables()
            
            # 从数据库加载所有生成的地图
            for level in range(1, 10):
                maps = self.db.get_generated_maps_by_level(level)
                for map_data in maps:
                    gen_loc = GeneratedLocation.from_dict(map_data)
                    self.generated_locations[gen_loc.name] = gen_loc
                    
                    # 同时添加到locations字典以便统一访问
                    if gen_loc.name not in self.locations:
                        self.locations[gen_loc.name] = Location(
                            name=gen_loc.name,
                            description=gen_loc.description,
                            realm_required=gen_loc.realm_required,
                            connections=gen_loc.connections,
                        )
        except Exception as e:
            print(f"加载生成地点时出错: {e}")
    
    def add_generated_location(self, gen_loc: GeneratedLocation) -> bool:
        """
        添加动态生成的地点
        
        Args:
            gen_loc: 生成的地点对象
            
        Returns:
            是否添加成功
        """
        try:
            # 保存到内存
            self.generated_locations[gen_loc.name] = gen_loc
            
            # 同时添加到locations字典以便统一访问
            self.locations[gen_loc.name] = Location(
                name=gen_loc.name,
                description=gen_loc.description,
                realm_required=gen_loc.realm_required,
                connections=gen_loc.connections,
            )
            
            # 保存到数据库
            self.db.save_generated_map(gen_loc.to_dict())
            
            return True
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
        loc1 = self.locations.get(loc1_name)
        loc2 = self.locations.get(loc2_name)
        
        if not loc1 or not loc2:
            return False
        
        # 避免重复连接
        updated = False
        
        # 单向连接：loc1 -> loc2
        if loc2_name not in loc1.connections:
            loc1.connections.append(loc2_name)
            updated = True
        
        # 双向连接：loc2 -> loc1
        if bidirectional and loc1_name not in loc2.connections:
            loc2.connections.append(loc1_name)
            updated = True
        
        # 如果是生成地点，更新数据库
        if loc1_name in self.generated_locations:
            gen_loc = self.generated_locations[loc1_name]
            if loc2_name not in gen_loc.connections:
                gen_loc.connections.append(loc2_name)
                self.db.save_generated_map(gen_loc.to_dict())
        
        if bidirectional and loc2_name in self.generated_locations:
            gen_loc = self.generated_locations[loc2_name]
            if loc1_name not in gen_loc.connections:
                gen_loc.connections.append(loc1_name)
                self.db.save_generated_map(gen_loc.to_dict())
        
        return updated
    
    def get_generated_location(self, name: str) -> Optional[GeneratedLocation]:
        """
        获取生成的地点详情
        
        Args:
            name: 地点名称
            
        Returns:
            生成的地点对象
        """
        return self.generated_locations.get(name)
    
    def get_all_generated_locations(self) -> List[GeneratedLocation]:
        """获取所有生成的地点"""
        return list(self.generated_locations.values())
    
    def is_generated_location(self, name: str) -> bool:
        """
        检查地点是否为动态生成
        
        Args:
            name: 地点名称
            
        Returns:
            是否为生成地点
        """
        return name in self.generated_locations
    
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
        gen_loc = self.generated_locations.get(name)
        if not gen_loc:
            return self.get_location_description(name)
        
        realm_info = get_realm_info(gen_loc.realm_required)
        realm_name = realm_info.name if realm_info else "凡人"
        
        # 构建NPC信息
        npcs_info = ""
        npcs = self.get_location_npcs(name)
        if npcs:
            npc_names = [npc.get('full_name', npc.get('name', '未知')) for npc in npcs[:5]]
            npcs_info = f"\n║  居民: {', '.join(npc_names)}"
            if len(npcs) > 5:
                npcs_info += f" 等{len(npcs)}人"
        
        # 构建妖兽信息
        monsters_info = ""
        monsters = self.get_location_monsters(name)
        if monsters:
            monster_names = [m.get('name', '未知') for m in monsters[:3]]
            monsters_info = f"\n║  妖兽: {', '.join(monster_names)}"
            if len(monsters) > 3:
                monsters_info += f" 等{len(monsters)}只"
        
        description = f"""
╔══════════════════════════════════════════════════════════╗
║  📍 {gen_loc.name}                                          ║
╠══════════════════════════════════════════════════════════╣
║  {gen_loc.description[:40]}...                                  ║
╠══════════════════════════════════════════════════════════╣
║  类型: {gen_loc.map_type}  规模: {gen_loc.size}  等级: {gen_loc.level}                    ║
║  进入要求: {realm_name}                                        ║
║  可前往: {', '.join(gen_loc.connections) if gen_loc.connections else '无'}                          ║
{npcs_info}{monsters_info}
╚══════════════════════════════════════════════════════════╝
"""
        return description
    
    # ==================== NPC独立系统整合 ====================
    
    def _init_npcs(self):
        """为所有地点初始化NPC - 优先从数据库加载完整数据，没有则生成"""
        # 为每个地点加载或生成NPC
        npc_count_per_location = GAME_CONFIG.get("npc", {}).get("npc_count_per_location", 3)
        location_names = list(self.locations.keys())
        
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
                        from game.npc import NPC
                        npc = NPC.from_dict(npc_data)
                        self.npc_manager.npcs[npc.data.id] = npc
                        self.npc_manager.independent_manager.add_npc(npc.independent, location_name)
                    except Exception as e:
                        continue
            else:
                # 数据库中没有，生成新的NPC
                npcs = self.npc_manager.generate_npcs_for_location(location_name, npc_count_per_location, self.db, show_progress=False)
                generated_count += len(npcs)
    
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
