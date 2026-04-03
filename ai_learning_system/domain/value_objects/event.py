"""
世界事件系统值对象模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum, auto


class WorldEventCategory(Enum):
    """世界事件分类"""
    WAR = "war"                    # 战争
    DISCOVERY = "discovery"        # 发现
    DISASTER = "disaster"          # 灾难
    CELEBRATION = "celebration"    # 庆典
    CONFLICT = "conflict"          # 冲突
    POLITICAL = "political"        # 政治
    MYSTERY = "mystery"            # 神秘
    NATURAL = "natural"            # 自然


class WorldEventScope(Enum):
    """世界事件范围"""
    LOCAL = "local"          # 局部（单个地点）
    REGIONAL = "regional"    # 区域（多个地点）
    GLOBAL = "global"        # 全局（整个世界）


@dataclass(frozen=True)
class WorldEventTemplate:
    """世界事件模板"""
    event_type: str
    category: WorldEventCategory
    title_templates: List[str]
    description_templates: List[str]
    min_importance: int = 1
    max_importance: int = 10
    scope: WorldEventScope = WorldEventScope.LOCAL
    duration_days: int = 30
    can_repeat: bool = True
    required_realm: int = 0
    effects: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_type": self.event_type,
            "category": self.category.value,
            "title_templates": self.title_templates,
            "description_templates": self.description_templates,
            "min_importance": self.min_importance,
            "max_importance": self.max_importance,
            "scope": self.scope.value,
            "duration_days": self.duration_days,
            "can_repeat": self.can_repeat,
            "required_realm": self.required_realm,
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldEventTemplate':
        """从字典创建WorldEventTemplate对象"""
        return cls(
            event_type=data.get("event_type", ""),
            category=WorldEventCategory(data.get("category", "local")),
            title_templates=data.get("title_templates", []),
            description_templates=data.get("description_templates", []),
            min_importance=data.get("min_importance", 1),
            max_importance=data.get("max_importance", 10),
            scope=WorldEventScope(data.get("scope", "local")),
            duration_days=data.get("duration_days", 30),
            can_repeat=data.get("can_repeat", True),
            required_realm=data.get("required_realm", 0),
            effects=data.get("effects", {})
        )


@dataclass(frozen=True)
class WorldEvent:
    """世界事件值对象"""
    id: str
    event_type: str
    title: str
    description: str
    category: WorldEventCategory
    scope: WorldEventScope
    importance: int
    location: str
    start_time: Dict[str, int]
    end_time: Dict[str, int]
    effects: Dict[str, Any]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "scope": self.scope.value,
            "importance": self.importance,
            "location": self.location,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "effects": self.effects,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldEvent':
        """从字典创建WorldEvent对象"""
        return cls(
            id=data.get("id", ""),
            event_type=data.get("event_type", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            category=WorldEventCategory(data.get("category", "local")),
            scope=WorldEventScope(data.get("scope", "local")),
            importance=data.get("importance", 1),
            location=data.get("location", ""),
            start_time=data.get("start_time", {}),
            end_time=data.get("end_time", {}),
            effects=data.get("effects", {}),
            is_active=data.get("is_active", True)
        )