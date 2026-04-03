"""
地图系统值对象模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class LocationValue:
    """地点值对象"""
    name: str
    description: str
    realm_required: int
    connections: List[str] = field(default_factory=list)
    sects: List[str] = field(default_factory=list)  # 该地点的门派
    danger_level: str = "安全"  # 危险等级：安全、普通、危险、绝境
    parent_location: str = ""  # 父地点（用于树形结构）
    sub_locations: List[str] = field(default_factory=list)  # 子地点列表
    location_type: str = "普通"  # 地点类型：区域、城镇、门派、洞府、野外等
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.name:
            raise ValueError("地点名称不能为空")
        if self.realm_required < 0:
            raise ValueError("境界要求不能为负数")
    
    def is_accessible(self, player_realm_level: int) -> bool:
        """检查玩家是否可以进入该地点"""
        return player_realm_level >= self.realm_required
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "realm_required": self.realm_required,
            "connections": self.connections,
            "sects": self.sects,
            "danger_level": self.danger_level,
            "parent_location": self.parent_location,
            "sub_locations": self.sub_locations,
            "location_type": self.location_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationValue':
        """从字典创建LocationValue对象"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            realm_required=data.get("realm_required", 0),
            connections=data.get("connections", []),
            sects=data.get("sects", []),
            danger_level=data.get("danger_level", "安全"),
            parent_location=data.get("parent_location", ""),
            sub_locations=data.get("sub_locations", []),
            location_type=data.get("location_type", "普通")
        )


@dataclass(frozen=True)
class GeneratedLocationValue:
    """动态生成的地点值对象"""
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
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.id:
            raise ValueError("地点ID不能为空")
        if not self.name:
            raise ValueError("地点名称不能为空")
        if self.realm_required < 0:
            raise ValueError("境界要求不能为负数")
        if self.level < 1:
            raise ValueError("地点等级不能小于1")
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedLocationValue':
        """从字典创建GeneratedLocationValue对象"""
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