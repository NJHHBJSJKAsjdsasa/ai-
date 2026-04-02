"""
世界事件系统模块
管理世界范围内的重要事件，实现NPC对事件的响应机制
"""

import random
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG


class WorldEventType(Enum):
    """世界事件类型枚举"""
    PLAYER_BREAKTHROUGH = auto()      # 玩家突破
    PLAYER_GET_TREASURE = auto()      # 获得宝物
    SECRET_REALM_OPEN = auto()        # 秘境开启
    SECT_WAR = auto()                 # 门派战争
    MARKET_FLUCTUATION = auto()       # 市场波动
    NPC_DEATH = auto()                # NPC死亡
    WORLD_BOSS_APPEAR = auto()        # 世界BOSS出现


class EventScope(Enum):
    """事件影响范围枚举"""
    LOCAL = "local"           # 局部（单个地点）
    REGIONAL = "regional"     # 区域（多个地点）
    GLOBAL = "global"         # 全局（整个世界）


class NPCResponseType(Enum):
    """NPC响应类型枚举"""
    ADMIRE = auto()           # 敬佩
    ENVY = auto()             # 嫉妒
    EXCITE = auto()           # 兴奋
    FEAR = auto()             # 恐惧
    SADNESS = auto()          # 悲伤
    CAUTION = auto()          # 警惕
    GREED = auto()            # 贪婪
    IGNORE = auto()           # 无视


@dataclass
class WorldEvent:
    """
    世界事件数据类
    
    用于描述在世界中发生的重要事件，包含事件的完整信息
    """
    event_id: str                          # 事件唯一标识
    event_type: WorldEventType             # 事件类型
    title: str                             # 事件标题
    description: str                       # 事件描述
    importance: int = 5                    # 重要性 (1-10)
    scope: EventScope = EventScope.LOCAL   # 影响范围
    location: str = ""                     # 发生地点
    timestamp: float = field(default_factory=time.time)  # 发生时间
    source_id: str = ""                    # 事件源ID（玩家或NPC）
    source_name: str = ""                  # 事件源名称
    related_npcs: List[str] = field(default_factory=list)  # 相关NPC列表
    data: Dict[str, Any] = field(default_factory=dict)     # 额外数据字典
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保重要性在有效范围内
        self.importance = max(1, min(10, self.importance))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            包含事件数据的字典
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.name,
            "title": self.title,
            "description": self.description,
            "importance": self.importance,
            "scope": self.scope.value,
            "location": self.location,
            "timestamp": self.timestamp,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "related_npcs": self.related_npcs,
            "data": self.data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldEvent':
        """
        从字典创建事件
        
        Args:
            data: 包含事件数据的字典
            
        Returns:
            WorldEvent对象
        """
        return cls(
            event_id=data.get("event_id", ""),
            event_type=WorldEventType[data.get("event_type", "PLAYER_BREAKTHROUGH")],
            title=data.get("title", ""),
            description=data.get("description", ""),
            importance=data.get("importance", 5),
            scope=EventScope(data.get("scope", "local")),
            location=data.get("location", ""),
            timestamp=data.get("timestamp", time.time()),
            source_id=data.get("source_id", ""),
            source_name=data.get("source_name", ""),
            related_npcs=data.get("related_npcs", []),
            data=data.get("data", {}),
        )


@dataclass
class NPCEventResponse:
    """
    NPC事件响应数据类
    
    记录NPC对事件的响应信息
    """
    npc_id: str                            # NPC ID
    event_id: str                          # 事件ID
    response_type: NPCResponseType         # 响应类型
    response_description: str              # 响应描述
    behavior_changes: Dict[str, Any] = field(default_factory=dict)  # 行为变化
    timestamp: float = field(default_factory=time.time)             # 响应时间


class WorldEventManager:
    """
    世界事件管理器
    
    管理世界事件的广播、存储和查询，以及NPC的事件监听机制
    """
    
    def __init__(self):
        """初始化世界事件管理器"""
        self.events: List[WorldEvent] = []              # 事件列表（按时间排序）
        self.event_index: Dict[str, WorldEvent] = {}    # 事件索引
        self.npc_listeners: Dict[str, Set[WorldEventType]] = {}  # NPC监听器
        self.npc_responses: Dict[str, List[NPCEventResponse]] = {}  # NPC响应记录
        self._event_counter = 0                         # 事件计数器
        self._max_events = 1000                         # 最大事件数量
    
    def _generate_event_id(self) -> str:
        """
        生成事件ID
        
        Returns:
            唯一的事件ID
        """
        self._event_counter += 1
        return f"evt_{int(time.time())}_{self._event_counter}"
    
    def broadcast_event(
        self,
        event_type: WorldEventType,
        title: str,
        description: str,
        importance: int = 5,
        scope: EventScope = EventScope.LOCAL,
        location: str = "",
        source_id: str = "",
        source_name: str = "",
        related_npcs: List[str] = None,
        data: Dict[str, Any] = None
    ) -> WorldEvent:
        """
        广播事件到世界
        
        Args:
            event_type: 事件类型
            title: 事件标题
            description: 事件描述
            importance: 重要性 (1-10)
            scope: 影响范围
            location: 发生地点
            source_id: 事件源ID
            source_name: 事件源名称
            related_npcs: 相关NPC列表
            data: 额外数据
            
        Returns:
            创建的事件对象
        """
        event = WorldEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            title=title,
            description=description,
            importance=importance,
            scope=scope,
            location=location,
            source_id=source_id,
            source_name=source_name,
            related_npcs=related_npcs or [],
            data=data or {},
        )
        
        # 添加到事件列表
        self.events.append(event)
        self.event_index[event.event_id] = event
        
        # 限制事件数量
        if len(self.events) > self._max_events:
            old_event = self.events.pop(0)
            del self.event_index[old_event.event_id]
        
        return event
    
    def register_npc_listener(self, npc_id: str, event_types: List[WorldEventType]):
        """
        注册NPC事件监听
        
        Args:
            npc_id: NPC ID
            event_types: 要监听的事件类型列表
        """
        if npc_id not in self.npc_listeners:
            self.npc_listeners[npc_id] = set()
        self.npc_listeners[npc_id].update(event_types)
    
    def unregister_npc_listener(self, npc_id: str):
        """
        注销NPC监听
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.npc_listeners:
            del self.npc_listeners[npc_id]
    
    def get_npc_listening_types(self, npc_id: str) -> Set[WorldEventType]:
        """
        获取NPC监听的事件类型
        
        Args:
            npc_id: NPC ID
            
        Returns:
            NPC监听的事件类型集合
        """
        return self.npc_listeners.get(npc_id, set())
    
    def get_recent_events(
        self,
        limit: int = 10,
        scope: Optional[EventScope] = None,
        event_type: Optional[WorldEventType] = None,
        min_importance: int = 1
    ) -> List[WorldEvent]:
        """
        获取最近事件
        
        Args:
            limit: 返回事件数量限制
            scope: 筛选范围，None表示不筛选
            event_type: 筛选事件类型，None表示不筛选
            min_importance: 最小重要性
            
        Returns:
            符合条件的事件列表
        """
        filtered_events = []
        
        # 从后向前遍历（最新的在前）
        for event in reversed(self.events):
            # 范围筛选
            if scope is not None and event.scope != scope:
                continue
            
            # 类型筛选
            if event_type is not None and event.event_type != event_type:
                continue
            
            # 重要性筛选
            if event.importance < min_importance:
                continue
            
            filtered_events.append(event)
            
            if len(filtered_events) >= limit:
                break
        
        return filtered_events
    
    def get_events_for_npc(
        self,
        npc_id: str,
        limit: int = 10,
        include_related_only: bool = False
    ) -> List[WorldEvent]:
        """
        获取NPC相关事件
        
        Args:
            npc_id: NPC ID
            limit: 返回事件数量限制
            include_related_only: 是否只返回直接相关的事件
            
        Returns:
            NPC相关的事件列表
        """
        relevant_events = []
        
        for event in reversed(self.events):
            # 检查是否是事件源
            if event.source_id == npc_id:
                relevant_events.append(event)
                continue
            
            # 检查是否在相关NPC列表中
            if npc_id in event.related_npcs:
                relevant_events.append(event)
                continue
            
            # 如果不只返回直接相关的事件，检查NPC是否监听了该类型
            if not include_related_only:
                listening_types = self.npc_listeners.get(npc_id, set())
                if event.event_type in listening_types:
                    relevant_events.append(event)
                    continue
            
            if len(relevant_events) >= limit:
                break
        
        return relevant_events[:limit]
    
    def clear_old_events(self, max_age: float = 86400.0) -> int:
        """
        清理旧事件
        
        Args:
            max_age: 最大保留时间（秒），默认24小时
            
        Returns:
            清理的事件数量
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # 保留新事件
        new_events = []
        removed_count = 0
        
        for event in self.events:
            # 保留重要事件（重要性>=8）
            if event.importance >= 8:
                new_events.append(event)
                continue
            
            # 检查时间
            if event.timestamp < cutoff_time:
                del self.event_index[event.event_id]
                removed_count += 1
            else:
                new_events.append(event)
        
        self.events = new_events
        return removed_count
    
    def record_npc_response(self, response: NPCEventResponse):
        """
        记录NPC响应
        
        Args:
            response: NPC响应对象
        """
        if response.npc_id not in self.npc_responses:
            self.npc_responses[response.npc_id] = []
        
        self.npc_responses[response.npc_id].append(response)
        
        # 限制记录数量
        if len(self.npc_responses[response.npc_id]) > 100:
            self.npc_responses[response.npc_id] = self.npc_responses[response.npc_id][-100:]
    
    def get_npc_responses(self, npc_id: str, limit: int = 10) -> List[NPCEventResponse]:
        """
        获取NPC的响应记录
        
        Args:
            npc_id: NPC ID
            limit: 返回记录数量限制
            
        Returns:
            NPC响应记录列表
        """
        responses = self.npc_responses.get(npc_id, [])
        return responses[-limit:] if responses else []
    
    def get_event(self, event_id: str) -> Optional[WorldEvent]:
        """
        获取指定事件
        
        Args:
            event_id: 事件ID
            
        Returns:
            事件对象，不存在则返回None
        """
        return self.event_index.get(event_id)
    
    def get_event_stats(self) -> Dict[str, Any]:
        """
        获取事件统计信息
        
        Returns:
            统计信息字典
        """
        type_counts = {}
        scope_counts = {}
        
        for event in self.events:
            type_counts[event.event_type.name] = type_counts.get(event.event_type.name, 0) + 1
            scope_counts[event.scope.value] = scope_counts.get(event.scope.value, 0) + 1
        
        return {
            "total_events": len(self.events),
            "type_distribution": type_counts,
            "scope_distribution": scope_counts,
            "active_listeners": len(self.npc_listeners),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            包含管理器数据的字典
        """
        return {
            "events": [event.to_dict() for event in self.events],
            "npc_listeners": {
                npc_id: [et.name for et in event_types]
                for npc_id, event_types in self.npc_listeners.items()
            },
            "event_counter": self._event_counter,
        }


class NPCEventHandler:
    """
    NPC事件处理器
    
    处理NPC对世界事件的响应，生成相应的行为变化
    """
    
    def __init__(self, event_manager: WorldEventManager):
        """
        初始化NPC事件处理器
        
        Args:
            event_manager: 世界事件管理器
        """
        self.event_manager = event_manager
    
    def handle_event(self, npc, event: WorldEvent) -> Optional[NPCEventResponse]:
        """
        处理事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            NPC响应对象，如果不关心则返回None
        """
        # 判断NPC是否关心此事件
        if not self.should_npc_care(npc, event):
            return None
        
        # 生成响应
        response = self.generate_response(npc, event)
        
        # 更新NPC行为
        self.update_behavior(npc, event, response)
        
        # 记录响应
        self.event_manager.record_npc_response(response)
        
        return response
    
    def should_npc_care(self, npc, event: WorldEvent) -> bool:
        """
        判断NPC是否关心此事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            是否关心此事件
        """
        # 如果是事件源，不关心
        if npc.data.id == event.source_id:
            return False
        
        # 根据事件范围判断
        if event.scope == EventScope.LOCAL:
            # 局部事件：只有同地点的NPC关心
            if npc.data.location != event.location:
                return False
        elif event.scope == EventScope.REGIONAL:
            # 区域事件：根据重要性判断
            if event.importance < 5 and npc.data.location != event.location:
                return False
        # 全局事件：所有NPC都关心
        
        # 根据NPC监听类型判断
        listening_types = self.event_manager.get_npc_listening_types(npc.data.id)
        if listening_types and event.event_type not in listening_types:
            # 如果NPC设置了监听，但不在监听列表中
            # 检查是否是直接相关的事件
            if npc.data.id not in event.related_npcs:
                return False
        
        # 根据重要性判断（重要性低的随机关心）
        if event.importance < 3:
            return random.random() < 0.3
        
        return True
    
    def generate_response(self, npc, event: WorldEvent) -> NPCEventResponse:
        """
        生成响应行为
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            NPC响应对象
        """
        response_type = NPCResponseType.IGNORE
        description = ""
        
        # 根据事件类型和NPC性格生成响应
        if event.event_type == WorldEventType.PLAYER_BREAKTHROUGH:
            response_type, description = self._handle_player_breakthrough(npc, event)
        elif event.event_type == WorldEventType.PLAYER_GET_TREASURE:
            response_type, description = self._handle_player_get_treasure(npc, event)
        elif event.event_type == WorldEventType.SECRET_REALM_OPEN:
            response_type, description = self._handle_secret_realm_open(npc, event)
        elif event.event_type == WorldEventType.SECT_WAR:
            response_type, description = self._handle_sect_war(npc, event)
        elif event.event_type == WorldEventType.MARKET_FLUCTUATION:
            response_type, description = self._handle_market_fluctuation(npc, event)
        elif event.event_type == WorldEventType.NPC_DEATH:
            response_type, description = self._handle_npc_death(npc, event)
        elif event.event_type == WorldEventType.WORLD_BOSS_APPEAR:
            response_type, description = self._handle_world_boss_appear(npc, event)
        
        return NPCEventResponse(
            npc_id=npc.data.id,
            event_id=event.event_id,
            response_type=response_type,
            response_description=description,
        )
    
    def update_behavior(self, npc, event: WorldEvent, response: NPCEventResponse):
        """
        更新NPC行为策略
        
        Args:
            npc: NPC对象
            event: 世界事件
            response: NPC响应
        """
        behavior_changes = {}
        
        if response.response_type == NPCResponseType.ADMIRE:
            # 敬佩：增加对事件源的好感
            if event.source_id:
                npc.independent.update_relationship(event.source_id, random.uniform(5, 15))
            behavior_changes["social_preference"] = "admire_source"
            
        elif response.response_type == NPCResponseType.ENVY:
            # 嫉妒：可能产生敌意
            if event.source_id:
                npc.independent.update_relationship(event.source_id, random.uniform(-10, -3))
            behavior_changes["social_preference"] = "avoid_source"
            
        elif response.response_type == NPCResponseType.EXCITE:
            # 兴奋：增加探索欲望
            if hasattr(npc.independent, 'needs'):
                from game.npc_independent import NeedType
                if NeedType.CULTIVATION in npc.independent.needs:
                    npc.independent.needs[NeedType.CULTIVATION].value += 20
            behavior_changes["activity_preference"] = "explore"
            
        elif response.response_type == NPCResponseType.FEAR:
            # 恐惧：增加谨慎，可能逃离
            behavior_changes["activity_preference"] = "hide"
            behavior_changes["location_change"] = "seek_safety"
            
        elif response.response_type == NPCResponseType.SADNESS:
            # 悲伤：降低社交欲望
            if hasattr(npc.independent, 'needs'):
                from game.npc_independent import NeedType
                if NeedType.SOCIAL in npc.independent.needs:
                    npc.independent.needs[NeedType.SOCIAL].value -= 20
            behavior_changes["social_preference"] = "isolate"
            
        elif response.response_type == NPCResponseType.CAUTION:
            # 警惕：增加防御性
            behavior_changes["combat_preference"] = "defensive"
            
        elif response.response_type == NPCResponseType.GREED:
            # 贪婪：寻求获取宝物
            behavior_changes["activity_preference"] = "seek_treasure"
        
        # 添加记忆
        importance = min(10, event.importance + 2)
        emotion = "positive" if response.response_type in [NPCResponseType.ADMIRE, NPCResponseType.EXCITE] else "negative"
        npc.add_memory(
            content=f"得知{event.title}: {response.response_description}",
            importance=importance,
            emotion=emotion
        )
        
        # 更新响应对象
        response.behavior_changes = behavior_changes
    
    def _handle_player_breakthrough(self, npc, event: WorldEvent) -> tuple:
        """
        处理玩家突破事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        # 获取NPC性格
        kindness = getattr(npc.independent.personality, 'kindness', 0.5)
        greed = getattr(npc.independent.personality, 'greed', 0.5)
        
        # 根据境界差距判断
        player_realm = event.data.get("realm_level", 0)
        npc_realm = npc.data.realm_level
        realm_diff = player_realm - npc_realm
        
        if realm_diff > 2:
            # 玩家境界远高于NPC
            if kindness > 0.6:
                return NPCResponseType.ADMIRE, f"{event.source_name}真乃天纵之才，令人敬佩！"
            elif greed > 0.6:
                return NPCResponseType.ENVY, f"为何{event.source_name}能有如此机缘..."
            else:
                return NPCResponseType.ADMIRE, f"{event.source_name}的突破令人叹服。"
        elif realm_diff >= 0:
            # 玩家境界相近或略高
            if kindness > 0.5:
                return NPCResponseType.ADMIRE, f"恭喜{event.source_name}道友突破！"
            elif greed > 0.7:
                return NPCResponseType.ENVY, f"哼，不过是运气好罢了。"
            else:
                return NPCResponseType.IGNORE, ""
        else:
            # 玩家境界低于NPC
            return NPCResponseType.IGNORE, ""
    
    def _handle_player_get_treasure(self, npc, event: WorldEvent) -> tuple:
        """
        处理获得宝物事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        greed = getattr(npc.independent.personality, 'greed', 0.5)
        curiosity = getattr(npc.independent.personality, 'curiosity', 0.5)
        
        treasure_rarity = event.data.get("rarity", 1)
        
        if treasure_rarity >= 8:
            # 稀世珍宝
            if greed > 0.7:
                return NPCResponseType.GREED, f"那{event.data.get('treasure_name', '宝物')}若能归我..."
            elif curiosity > 0.6:
                return NPCResponseType.EXCITE, f"真想见识一下那{event.data.get('treasure_name', '宝物')}！"
            else:
                return NPCResponseType.ADMIRE, f"{event.source_name}真是福缘深厚。"
        elif treasure_rarity >= 5:
            # 珍贵宝物
            if greed > 0.8:
                return NPCResponseType.GREED, "若能得到那件宝物..."
            else:
                return NPCResponseType.IGNORE, ""
        else:
            return NPCResponseType.IGNORE, ""
    
    def _handle_secret_realm_open(self, npc, event: WorldEvent) -> tuple:
        """
        处理秘境开启事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        curiosity = getattr(npc.independent.personality, 'curiosity', 0.5)
        bravery = getattr(npc.independent.personality, 'bravery', 0.5)
        
        realm_danger = event.data.get("danger_level", 5)
        
        if curiosity > 0.6:
            if bravery > 0.5 or realm_danger < 5:
                return NPCResponseType.EXCITE, "秘境开启！这正是探索的好机会！"
            else:
                return NPCResponseType.CAUTION, "秘境虽诱人，但也需小心为上。"
        elif bravery > 0.7 and realm_danger < 7:
            return NPCResponseType.EXCITE, "如此机缘，岂能错过！"
        else:
            return NPCResponseType.IGNORE, ""
    
    def _handle_sect_war(self, npc, event: WorldEvent) -> tuple:
        """
        处理门派战争事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        bravery = getattr(npc.independent.personality, 'bravery', 0.5)
        
        # 检查NPC是否属于相关门派
        sect1 = event.data.get("sect1", "")
        sect2 = event.data.get("sect2", "")
        
        if npc.data.sect in [sect1, sect2]:
            # NPC属于参战门派
            if bravery > 0.6:
                return NPCResponseType.EXCITE, f"为了{npc.data.sect}的荣耀！"
            else:
                return NPCResponseType.FEAR, "这场战争...希望能平安度过。"
        else:
            # NPC不属于参战门派
            if event.importance >= 7:
                return NPCResponseType.CAUTION, "门派大战，需小心被波及。"
            else:
                return NPCResponseType.IGNORE, ""
    
    def _handle_market_fluctuation(self, npc, event: WorldEvent) -> tuple:
        """
        处理市场波动事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        greed = getattr(npc.independent.personality, 'greed', 0.5)
        occupation = npc.data.occupation
        
        # 商人NPC特别关心
        if "商" in occupation or "贩" in occupation:
            fluctuation_type = event.data.get("type", "unknown")
            if fluctuation_type == "price_rise":
                return NPCResponseType.EXCITE, "价格上涨，正是出货的好时机！"
            elif fluctuation_type == "price_drop":
                return NPCResponseType.CAUTION, "价格下跌，需要谨慎进货。"
            else:
                return NPCResponseType.CAUTION, "市场波动，需密切关注。"
        
        # 贪婪的NPC也关心
        if greed > 0.7 and event.importance >= 6:
            return NPCResponseType.GREED, "市场变动，或许有赚钱的机会。"
        
        return NPCResponseType.IGNORE, ""
    
    def _handle_npc_death(self, npc, event: WorldEvent) -> tuple:
        """
        处理NPC死亡事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        kindness = getattr(npc.independent.personality, 'kindness', 0.5)
        bravery = getattr(npc.independent.personality, 'bravery', 0.5)
        
        deceased_id = event.source_id
        deceased_name = event.source_name
        
        # 检查与死者的关系
        if deceased_id:
            relationship = npc.independent.get_relationship(deceased_id)
            affinity = relationship.affinity if relationship else 0
            
            if affinity > 30:
                # 好友死亡
                return NPCResponseType.SADNESS, f"{deceased_name}...竟就这样走了..."
            elif affinity < -30:
                # 敌人死亡
                return NPCResponseType.IGNORE, f"{deceased_name}死了，少了一个麻烦。"
        
        # 检查死亡原因
        reason = event.data.get("reason", "")
        if "murder" in reason or "killed" in reason:
            # 被谋杀
            if bravery < 0.4:
                return NPCResponseType.FEAR, "这地方太危险了，我要小心..."
            else:
                return NPCResponseType.CAUTION, "凶手还在逍遥法外，需提高警惕。"
        
        # 普通死亡
        if kindness > 0.6:
            return NPCResponseType.SADNESS, f"修行之路艰险，{deceased_name}一路走好。"
        
        return NPCResponseType.CAUTION, "又少了一个修士..."
    
    def _handle_world_boss_appear(self, npc, event: WorldEvent) -> tuple:
        """
        处理世界BOSS出现事件
        
        Args:
            npc: NPC对象
            event: 世界事件
            
        Returns:
            (响应类型, 描述)
        """
        bravery = getattr(npc.independent.personality, 'bravery', 0.5)
        boss_power = event.data.get("power_level", 5)
        
        if bravery > 0.8 and boss_power < 8:
            return NPCResponseType.EXCITE, "如此强大的存在，若能击败必有大收获！"
        elif bravery > 0.5:
            return NPCResponseType.CAUTION, "那怪物强大，需要联合众人才能对付。"
        else:
            return NPCResponseType.FEAR, f"太可怕了！必须远离{event.location}！"


# 全局事件管理器实例
world_event_manager = WorldEventManager()
npc_event_handler = NPCEventHandler(world_event_manager)
