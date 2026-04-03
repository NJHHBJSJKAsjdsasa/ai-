"""
地图系统实体模块
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from domain.value_objects.location import LocationValue, GeneratedLocationValue


@dataclass
class Location:
    """地点实体"""
    name: str
    location_value: LocationValue
    generated_value: Optional[GeneratedLocationValue] = None
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.name:
            raise ValueError("地点名称不能为空")
        if not self.location_value:
            raise ValueError("地点值对象不能为空")
    
    def is_accessible(self, player_realm_level: int) -> bool:
        """检查玩家是否可以进入该地点"""
        return self.location_value.is_accessible(player_realm_level)
    
    def add_connection(self, location_name: str):
        """添加连接地点"""
        if location_name not in self.location_value.connections:
            # 创建新的LocationValue对象（因为是不可变的）
            new_connections = self.location_value.connections.copy()
            new_connections.append(location_name)
            
            self.location_value = LocationValue(
                name=self.location_value.name,
                description=self.location_value.description,
                realm_required=self.location_value.realm_required,
                connections=new_connections,
                sects=self.location_value.sects,
                danger_level=self.location_value.danger_level,
                parent_location=self.location_value.parent_location,
                sub_locations=self.location_value.sub_locations,
                location_type=self.location_value.location_type
            )
    
    def remove_connection(self, location_name: str):
        """移除连接地点"""
        if location_name in self.location_value.connections:
            # 创建新的LocationValue对象（因为是不可变的）
            new_connections = self.location_value.connections.copy()
            new_connections.remove(location_name)
            
            self.location_value = LocationValue(
                name=self.location_value.name,
                description=self.location_value.description,
                realm_required=self.location_value.realm_required,
                connections=new_connections,
                sects=self.location_value.sects,
                danger_level=self.location_value.danger_level,
                parent_location=self.location_value.parent_location,
                sub_locations=self.location_value.sub_locations,
                location_type=self.location_value.location_type
            )
    
    def add_sub_location(self, location_name: str):
        """添加子地点"""
        if location_name not in self.location_value.sub_locations:
            # 创建新的LocationValue对象（因为是不可变的）
            new_sub_locations = self.location_value.sub_locations.copy()
            new_sub_locations.append(location_name)
            
            self.location_value = LocationValue(
                name=self.location_value.name,
                description=self.location_value.description,
                realm_required=self.location_value.realm_required,
                connections=self.location_value.connections,
                sects=self.location_value.sects,
                danger_level=self.location_value.danger_level,
                parent_location=self.location_value.parent_location,
                sub_locations=new_sub_locations,
                location_type=self.location_value.location_type
            )
    
    def add_sect(self, sect_name: str):
        """添加门派"""
        if sect_name not in self.location_value.sects:
            # 创建新的LocationValue对象（因为是不可变的）
            new_sects = self.location_value.sects.copy()
            new_sects.append(sect_name)
            
            self.location_value = LocationValue(
                name=self.location_value.name,
                description=self.location_value.description,
                realm_required=self.location_value.realm_required,
                connections=self.location_value.connections,
                sects=new_sects,
                danger_level=self.location_value.danger_level,
                parent_location=self.location_value.parent_location,
                sub_locations=self.location_value.sub_locations,
                location_type=self.location_value.location_type
            )
    
    def is_generated(self) -> bool:
        """检查是否为动态生成的地点"""
        return self.generated_value is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = self.location_value.to_dict()
        if self.generated_value:
            result.update(self.generated_value.to_dict())
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """从字典创建Location实体"""
        location_value = LocationValue.from_dict(data)
        
        generated_value = None
        if data.get('is_generated', False):
            generated_value = GeneratedLocationValue.from_dict(data)
        
        return cls(
            name=data.get('name', ''),
            location_value=location_value,
            generated_value=generated_value
        )