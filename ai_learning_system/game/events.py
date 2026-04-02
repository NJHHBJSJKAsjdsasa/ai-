"""
事件系统模块
管理随机事件、剧情事件等
"""

import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG


class EventType(Enum):
    """事件类型枚举"""
    RANDOM = "random"           # 随机事件
    PLOT = "plot"               # 剧情事件
    KARMA = "karma"             # 因果事件
    NPC = "npc"                 # NPC事件
    CULTIVATION = "cultivation" # 修炼事件


@dataclass
class Event:
    """事件数据类"""
    id: str
    name: str
    description: str
    event_type: EventType
    conditions: Dict[str, Any]
    effects: Dict[str, Any]
    choices: List[Dict[str, Any]] = None


class EventSystem:
    """事件系统类"""
    
    def __init__(self):
        """初始化事件系统"""
        self.events: Dict[str, Event] = {}
        self.event_history: List[str] = []
        self._init_events()
    
    def _init_events(self):
        """初始化事件库"""
        # 随机事件
        self._add_event(Event(
            id="random_beast_attack",
            name="妖兽袭击",
            description="一只妖兽突然从林中窜出，向你扑来！",
            event_type=EventType.RANDOM,
            conditions={"realm_min": 1},
            effects={"health": -20, "exp": 50},
            choices=[
                {"text": "迎战", "effects": {"health": -20, "exp": 50}},
                {"text": "逃跑", "effects": {"spiritual_power": -10}},
            ]
        ))
        
        self._add_event(Event(
            id="random_secret_realm",
            name="秘境现世",
            description="天空中突然出现一道裂缝，似乎是一个秘境入口！",
            event_type=EventType.RANDOM,
            conditions={"realm_min": 2, "fortune_min": 60},
            effects={"exp": 200, "spirit_stones": 100},
            choices=[
                {"text": "进入探索", "effects": {"exp": 200, "spirit_stones": 100}},
                {"text": "谨慎观望", "effects": {"exp": 50}},
            ]
        ))
        
        self._add_event(Event(
            id="random_auction",
            name="拍卖会",
            description="天元城正在举办一场盛大的拍卖会，据说有不少宝物。",
            event_type=EventType.RANDOM,
            conditions={"location": "天元城", "spirit_stones_min": 50},
            effects={"spirit_stones": -50, "fortune": 5},
            choices=[
                {"text": "参加拍卖", "effects": {"spirit_stones": -50, "fortune": 5}},
                {"text": "旁观", "effects": {"exp": 20}},
            ]
        ))
        
        self._add_event(Event(
            id="random_inheritance",
            name="前辈遗泽",
            description="你在山洞中发现了一位坐化的前辈修士，留下了一些遗物。",
            event_type=EventType.RANDOM,
            conditions={"fortune_min": 70},
            effects={"exp": 300, "spirit_stones": 200, "karma": 10},
            choices=[
                {"text": "恭敬收下", "effects": {"exp": 300, "spirit_stones": 200, "karma": 10}},
                {"text": "只取所需", "effects": {"exp": 100, "spirit_stones": 50, "karma": 20}},
            ]
        ))
        
        self._add_event(Event(
            id="random_robbery",
            name="遭遇劫修",
            description="几个蒙面修士拦住了你的去路，要你交出财物。",
            event_type=EventType.RANDOM,
            conditions={"realm_min": 1},
            effects={"spirit_stones": -100, "karma": -10},
            choices=[
                {"text": "交出灵石", "effects": {"spirit_stones": -100}},
                {"text": "拼死反抗", "effects": {"health": -30, "karma": 10}},
            ]
        ))
        
        # 修炼事件
        self._add_event(Event(
            id="cultivation_insight",
            name="顿悟",
            description="修炼中突然心有所感，对大道有了新的理解！",
            event_type=EventType.CULTIVATION,
            conditions={},
            effects={"exp": 100},
        ))
        
        self._add_event(Event(
            id="cultivation_deviation",
            name="走火入魔",
            description="修炼时心神不宁，差点走火入魔！",
            event_type=EventType.CULTIVATION,
            conditions={},
            effects={"health": -20, "is_injured": True},
        ))
        
        # 因果事件
        self._add_event(Event(
            id="karma_good_reward",
            name="善有善报",
            description="你曾经的善举得到了回报，一位受你帮助的人送来了谢礼。",
            event_type=EventType.KARMA,
            conditions={"karma_min": 50},
            effects={"spirit_stones": 150, "fortune": 5},
        ))
        
        self._add_event(Event(
            id="karma_bad_retribution",
            name="恶有恶报",
            description="你曾经结下的仇家找上门来，要与你算账！",
            event_type=EventType.KARMA,
            conditions={"karma_max": -50},
            effects={"health": -40, "karma": 10},
        ))
    
    def _add_event(self, event: Event):
        """添加事件"""
        self.events[event.id] = event
    
    def check_random_event(self, player_stats: Dict[str, Any]) -> Optional[Event]:
        """
        检查是否触发随机事件
        
        Args:
            player_stats: 玩家属性
            
        Returns:
            触发的事件，如果没有则返回None
        """
        # 基础触发概率
        base_chance = GAME_CONFIG["events"]["random_event_chance"]
        
        # 福缘加成
        fortune_bonus = player_stats.get("fortune", 50) * 0.001
        
        # 业力影响（善业增加好事件概率）
        karma = player_stats.get("karma", 0)
        
        if random.random() > base_chance + fortune_bonus:
            return None
        
        # 筛选符合条件的事件
        valid_events = []
        for event in self.events.values():
            if not self._check_conditions(event, player_stats):
                continue
            
            # 根据业力筛选
            if event.event_type == EventType.RANDOM:
                if karma > 0 and random.random() < 0.3:
                    # 善业更容易触发正面事件
                    if self._is_positive_event(event):
                        valid_events.append(event)
                elif karma < 0 and random.random() < 0.3:
                    # 恶业更容易触发负面事件
                    if not self._is_positive_event(event):
                        valid_events.append(event)
                else:
                    valid_events.append(event)
            else:
                valid_events.append(event)
        
        if not valid_events:
            return None
        
        return random.choice(valid_events)
    
    def _check_conditions(self, event: Event, player_stats: Dict[str, Any]) -> bool:
        """检查事件条件"""
        conditions = event.conditions
        
        for key, value in conditions.items():
            if key == "realm_min":
                if player_stats.get("realm_level", 0) < value:
                    return False
            elif key == "fortune_min":
                if player_stats.get("fortune", 0) < value:
                    return False
            elif key == "karma_min":
                if player_stats.get("karma", 0) < value:
                    return False
            elif key == "karma_max":
                if player_stats.get("karma", 0) > value:
                    return False
            elif key == "location":
                if player_stats.get("location") != value:
                    return False
            elif key == "spirit_stones_min":
                if player_stats.get("spirit_stones", 0) < value:
                    return False
        
        return True
    
    def _is_positive_event(self, event: Event) -> bool:
        """判断是否为正面事件"""
        effects = event.effects
        positive = 0
        negative = 0
        
        for key, value in effects.items():
            if key in ["exp", "spirit_stones", "fortune", "health"]:
                if value > 0:
                    positive += value
                elif value < 0:
                    negative += abs(value)
        
        return positive > negative
    
    def apply_event_effects(self, event: Event, choice_index: int = 0) -> Dict[str, Any]:
        """
        应用事件效果
        
        Args:
            event: 事件
            choice_index: 选择索引
            
        Returns:
            效果字典
        """
        if event.choices and choice_index < len(event.choices):
            return event.choices[choice_index]["effects"]
        return event.effects
    
    def record_event(self, event_id: str):
        """记录事件历史"""
        self.event_history.append(event_id)
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """获取事件"""
        return self.events.get(event_id)
