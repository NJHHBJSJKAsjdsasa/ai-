"""
世界实体模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from domain.entities.location import Location
from domain.value_objects.time import GameTime


@dataclass
class World:
    """世界实体"""
    id: str
    name: str
    locations: Dict[str, Location] = field(default_factory=dict)
    current_time: GameTime = field(default_factory=GameTime)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.id:
            raise ValueError("世界ID不能为空")
        if not self.name:
            raise ValueError("世界名称不能为空")
    
    def add_location(self, location: Location):
        """添加地点"""
        if location.name in self.locations:
            raise ValueError(f"地点 {location.name} 已存在")
        self.locations[location.name] = location
    
    def remove_location(self, location_name: str):
        """移除地点"""
        if location_name in self.locations:
            del self.locations[location_name]
    
    def get_location(self, location_name: str) -> Optional[Location]:
        """获取地点"""
        return self.locations.get(location_name)
    
    def get_all_locations(self) -> List[Location]:
        """获取所有地点"""
        return list(self.locations.values())
    
    def get_accessible_locations(self, current_location: str, realm_level: int) -> List[str]:
        """获取可到达的地点"""
        location = self.get_location(current_location)
        if not location:
            return []
        
        accessible = []
        for conn in location.location_value.connections:
            target_location = self.get_location(conn)
            if target_location and target_location.is_accessible(realm_level):
                accessible.append(conn)
        
        return accessible
    
    def connect_locations(self, loc1_name: str, loc2_name: str, bidirectional: bool = True) -> bool:
        """建立两个地点之间的连接"""
        loc1 = self.get_location(loc1_name)
        loc2 = self.get_location(loc2_name)
        
        if not loc1 or not loc2:
            return False
        
        # 单向连接：loc1 -> loc2
        loc1.add_connection(loc2_name)
        
        # 双向连接：loc2 -> loc1
        if bidirectional:
            loc2.add_connection(loc1_name)
        
        return True
    
    def advance_time(self, hours: int = 1):
        """推进时间"""
        self.current_time = self.current_time.advance(hours)
    
    def get_current_time(self) -> GameTime:
        """获取当前游戏时间"""
        return self.current_time
    
    def add_event(self, event: Dict[str, Any]):
        """添加事件"""
        self.events.append(event)
    
    def get_events(self) -> List[Dict[str, Any]]:
        """获取事件列表"""
        return self.events
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "locations": {name: loc.to_dict() for name, loc in self.locations.items()},
            "current_time": self.current_time.to_dict(),
            "events": self.events
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """从字典创建World实体"""
        current_time = GameTime.from_dict(data.get("current_time", {}))
        world = cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            current_time=current_time,
            events=data.get("events", [])
        )
        
        # 加载地点
        locations_data = data.get("locations", {})
        for loc_name, loc_data in locations_data.items():
            location = Location.from_dict(loc_data)
            world.add_location(location)
        
        return world