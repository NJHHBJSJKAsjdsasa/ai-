"""
NPC成长轨迹系统模块
记录NPC的人生事件、生成人生故事、分析性格特征
"""

import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_realm_info


class EventType(Enum):
    """事件类型枚举"""
    CULTIVATION = "修炼突破"
    COMBAT = "战斗"
    SOCIAL = "社交"
    DECISION = "决策"
    ACHIEVEMENT = "成就"
    FAILURE = "失败"


class EmotionType(Enum):
    """情感色彩枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class LifeEvent:
    """
    人生事件数据类
    
    Attributes:
        event_type: 事件类型
        description: 事件描述
        timestamp: 发生时间戳
        importance: 重要性 (1-10)
        emotion: 情感色彩
        related_npcs: 相关NPC列表
        location: 发生地点
        outcome: 事件结果
        details: 额外详情
    """
    event_type: EventType
    description: str
    timestamp: float = field(default_factory=time.time)
    importance: int = 5
    emotion: EmotionType = EmotionType.NEUTRAL
    related_npcs: List[str] = field(default_factory=list)
    location: str = ""
    outcome: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not isinstance(self.emotion, EmotionType):
            self.emotion = EmotionType(self.emotion) if self.emotion in [e.value for e in EmotionType] else EmotionType.NEUTRAL
        if not isinstance(self.event_type, EventType):
            self.event_type = EventType(self.event_type) if self.event_type in [e.value for e in EventType] else EventType.DECISION
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "emotion": self.emotion.value if isinstance(self.emotion, EmotionType) else self.emotion,
            "related_npcs": self.related_npcs,
            "location": self.location,
            "outcome": self.outcome,
            "details": self.details,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifeEvent':
        """从字典创建"""
        return cls(
            event_type=EventType(data.get("event_type", "决策")),
            description=data.get("description", ""),
            timestamp=data.get("timestamp", time.time()),
            importance=data.get("importance", 5),
            emotion=EmotionType(data.get("emotion", "neutral")),
            related_npcs=data.get("related_npcs", []),
            location=data.get("location", ""),
            outcome=data.get("outcome", ""),
            details=data.get("details", {}),
        )


class NPCLifeRecord:
    """
    NPC成长轨迹记录器
    
    记录NPC的人生事件，提供查询和故事生成功能
    """
    
    def __init__(self):
        """初始化NPC成长轨迹记录器"""
        self.records: Dict[str, List[LifeEvent]] = defaultdict(list)
    
    def record_event(self, npc_id: str, event_type: EventType, description: str,
                    importance: int = 5, emotion: EmotionType = EmotionType.NEUTRAL,
                    location: str = "", related_npcs: List[str] = None,
                    outcome: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录通用事件
        
        Args:
            npc_id: NPC ID
            event_type: 事件类型
            description: 事件描述
            importance: 重要性 (1-10)
            emotion: 情感色彩
            location: 发生地点
            related_npcs: 相关NPC列表
            outcome: 事件结果
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        event = LifeEvent(
            event_type=event_type,
            description=description,
            importance=importance,
            emotion=emotion,
            location=location,
            related_npcs=related_npcs or [],
            outcome=outcome,
            details=details or {}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_cultivation(self, npc_id: str, old_realm: int, new_realm: int, 
                          location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录修炼突破事件
        
        Args:
            npc_id: NPC ID
            old_realm: 原境界等级
            new_realm: 新境界等级
            location: 突破地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        old_realm_name = self._get_realm_name(old_realm)
        new_realm_name = self._get_realm_name(new_realm)
        
        # 根据境界差距确定重要性
        realm_diff = new_realm - old_realm
        importance = min(10, 5 + realm_diff * 2)
        
        event = LifeEvent(
            event_type=EventType.CULTIVATION,
            description=f"从{old_realm_name}突破至{new_realm_name}",
            importance=importance,
            emotion=EmotionType.POSITIVE,
            location=location,
            outcome=f"成功突破到{new_realm_name}",
            details=details or {
                "old_realm": old_realm,
                "new_realm": new_realm,
                "old_realm_name": old_realm_name,
                "new_realm_name": new_realm_name,
            }
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_combat(self, npc_id: str, opponent: str, result: str, 
                     location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录战斗事件
        
        Args:
            npc_id: NPC ID
            opponent: 对手名称
            result: 战斗结果 (win/loss/draw)
            location: 战斗地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        # 根据结果确定情感色彩
        if result == "win":
            emotion = EmotionType.POSITIVE
            description = f"战胜{opponent}"
            outcome = "获得胜利"
            importance = 6
        elif result == "loss":
            emotion = EmotionType.NEGATIVE
            description = f"败于{opponent}"
            outcome = "战斗失败"
            importance = 5
        else:
            emotion = EmotionType.NEUTRAL
            description = f"与{opponent}战成平手"
            outcome = "平局收场"
            importance = 4
        
        # 根据战斗重要性调整
        if details and details.get("is_deathmatch"):
            importance = min(10, importance + 3)
            if result == "win":
                outcome = "生死战中获胜"
            elif result == "loss":
                outcome = "生死战中落败"
        
        event = LifeEvent(
            event_type=EventType.COMBAT,
            description=description,
            importance=importance,
            emotion=emotion,
            related_npcs=[opponent] if isinstance(opponent, str) else opponent,
            location=location,
            outcome=outcome,
            details=details or {"result": result}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_social(self, npc_id: str, other_npc: str, interaction_type: str,
                     location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录社交事件
        
        Args:
            npc_id: NPC ID
            other_npc: 对方NPC名称
            interaction_type: 互动类型 (交友/结仇/师徒/结拜/双修等)
            location: 社交地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        # 根据互动类型确定描述和重要性
        interaction_descriptions = {
            "交友": (f"与{other_npc}结为好友", EmotionType.POSITIVE, 5),
            "结仇": (f"与{other_npc}结下仇怨", EmotionType.NEGATIVE, 6),
            "师徒": (f"拜{other_npc}为师", EmotionType.POSITIVE, 7),
            "收徒": (f"收{other_npc}为徒", EmotionType.POSITIVE, 7),
            "结拜": (f"与{other_npc}结为兄弟", EmotionType.POSITIVE, 8),
            "双修": (f"与{other_npc}结为道侣", EmotionType.POSITIVE, 8),
            "决裂": (f"与{other_npc}恩断义绝", EmotionType.NEGATIVE, 7),
            "重逢": (f"与{other_npc}久别重逢", EmotionType.POSITIVE, 4),
            "交易": (f"与{other_npc}进行交易", EmotionType.NEUTRAL, 3),
        }
        
        desc, emotion, importance = interaction_descriptions.get(
            interaction_type, 
            (f"与{other_npc}{interaction_type}", EmotionType.NEUTRAL, 4)
        )
        
        event = LifeEvent(
            event_type=EventType.SOCIAL,
            description=desc,
            importance=importance,
            emotion=emotion,
            related_npcs=[other_npc] if isinstance(other_npc, str) else other_npc,
            location=location,
            outcome=f"{interaction_type}关系建立",
            details=details or {"interaction_type": interaction_type}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_decision(self, npc_id: str, decision: str, reason: str,
                       location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录重大决策事件
        
        Args:
            npc_id: NPC ID
            decision: 决策内容
            reason: 决策原因
            location: 决策地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        # 根据决策类型确定重要性
        high_importance_keywords = ["背叛", "牺牲", "放弃", "选择", "离开", "加入", "创立"]
        importance = 7 if any(kw in decision for kw in high_importance_keywords) else 5
        
        event = LifeEvent(
            event_type=EventType.DECISION,
            description=decision,
            importance=importance,
            emotion=EmotionType.NEUTRAL,
            location=location,
            outcome=reason,
            details=details or {"reason": reason}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_achievement(self, npc_id: str, achievement: str,
                          location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录成就事件
        
        Args:
            npc_id: NPC ID
            achievement: 成就内容
            location: 成就地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        # 根据成就类型确定重要性
        achievement_importance = {
            "飞升": 10,
            "渡劫": 10,
            "悟道": 9,
            "创立门派": 9,
            "获得传承": 8,
            "炼制神丹": 8,
            "打造神兵": 8,
            "击败强敌": 7,
            "获得宝物": 6,
            "完成任务": 4,
        }
        
        importance = 5
        for key, value in achievement_importance.items():
            if key in achievement:
                importance = value
                break
        
        event = LifeEvent(
            event_type=EventType.ACHIEVEMENT,
            description=f"达成成就：{achievement}",
            importance=importance,
            emotion=EmotionType.POSITIVE,
            location=location,
            outcome=f"成功{achievement}",
            details=details or {"achievement": achievement}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def record_failure(self, npc_id: str, failure: str,
                      location: str = "", details: Dict[str, Any] = None) -> LifeEvent:
        """
        记录失败事件
        
        Args:
            npc_id: NPC ID
            failure: 失败内容
            location: 失败地点
            details: 额外详情
            
        Returns:
            创建的LifeEvent对象
        """
        # 根据失败类型确定重要性
        failure_importance = {
            "陨落": 10,
            "死亡": 10,
            "渡劫失败": 9,
            "走火入魔": 8,
            "突破失败": 7,
            "被逐出师门": 7,
            "失去重要之物": 6,
            "任务失败": 4,
        }
        
        importance = 5
        for key, value in failure_importance.items():
            if key in failure:
                importance = value
                break
        
        event = LifeEvent(
            event_type=EventType.FAILURE,
            description=f"遭遇失败：{failure}",
            importance=importance,
            emotion=EmotionType.NEGATIVE,
            location=location,
            outcome=failure,
            details=details or {"failure": failure}
        )
        
        self.records[npc_id].append(event)
        return event
    
    def get_life_story(self, npc_id: str) -> str:
        """
        生成完整人生故事
        
        Args:
            npc_id: NPC ID
            
        Returns:
            格式化的人生故事文本
        """
        events = self.get_sorted_events(npc_id)
        if not events:
            return "暂无人生记录"
        
        story_parts = []
        story_parts.append("=" * 50)
        story_parts.append("【人生传记】")
        story_parts.append("=" * 50)
        
        # 按类型分组事件
        events_by_type = defaultdict(list)
        for event in events:
            events_by_type[event.event_type].append(event)
        
        # 生成各章节
        chapter_num = 1
        
        # 修炼历程
        if events_by_type[EventType.CULTIVATION]:
            story_parts.append(f"\n第{chapter_num}章：修炼之路")
            story_parts.append("-" * 30)
            for event in events_by_type[EventType.CULTIVATION]:
                story_parts.append(self._format_event(event))
            chapter_num += 1
        
        # 战斗经历
        if events_by_type[EventType.COMBAT]:
            story_parts.append(f"\n第{chapter_num}章：战斗历程")
            story_parts.append("-" * 30)
            for event in events_by_type[EventType.COMBAT]:
                story_parts.append(self._format_event(event))
            chapter_num += 1
        
        # 人际关系
        if events_by_type[EventType.SOCIAL]:
            story_parts.append(f"\n第{chapter_num}章：人际往来")
            story_parts.append("-" * 30)
            for event in events_by_type[EventType.SOCIAL]:
                story_parts.append(self._format_event(event))
            chapter_num += 1
        
        # 重大决策
        if events_by_type[EventType.DECISION]:
            story_parts.append(f"\n第{chapter_num}章：人生抉择")
            story_parts.append("-" * 30)
            for event in events_by_type[EventType.DECISION]:
                story_parts.append(self._format_event(event))
            chapter_num += 1
        
        # 成就与失败
        if events_by_type[EventType.ACHIEVEMENT] or events_by_type[EventType.FAILURE]:
            story_parts.append(f"\n第{chapter_num}章：荣辱得失")
            story_parts.append("-" * 30)
            for event in events_by_type[EventType.ACHIEVEMENT]:
                story_parts.append(self._format_event(event))
            for event in events_by_type[EventType.FAILURE]:
                story_parts.append(self._format_event(event))
        
        story_parts.append("\n" + "=" * 50)
        
        return "\n".join(story_parts)
    
    def get_story_summary(self, npc_id: str) -> str:
        """
        生成故事摘要
        
        Args:
            npc_id: NPC ID
            
        Returns:
            故事摘要文本
        """
        events = self.get_sorted_events(npc_id)
        if not events:
            return "暂无人生记录"
        
        # 统计信息
        total_events = len(events)
        cultivation_count = len([e for e in events if e.event_type == EventType.CULTIVATION])
        combat_count = len([e for e in events if e.event_type == EventType.COMBAT])
        social_count = len([e for e in events if e.event_type == EventType.SOCIAL])
        achievement_count = len([e for e in events if e.event_type == EventType.ACHIEVEMENT])
        failure_count = len([e for e in events if e.event_type == EventType.FAILURE])
        
        # 计算情感倾向
        positive_count = len([e for e in events if e.emotion == EmotionType.POSITIVE])
        negative_count = len([e for e in events if e.emotion == EmotionType.NEGATIVE])
        
        # 获取关键成就
        key_achievements = [e for e in events if e.event_type == EventType.ACHIEVEMENT and e.importance >= 7]
        key_failures = [e for e in events if e.event_type == EventType.FAILURE and e.importance >= 7]
        
        # 构建摘要
        summary_parts = []
        summary_parts.append("【人生摘要】")
        summary_parts.append(f"总事件数：{total_events}")
        summary_parts.append(f"修炼突破：{cultivation_count}次")
        summary_parts.append(f"战斗经历：{combat_count}次")
        summary_parts.append(f"社交互动：{social_count}次")
        summary_parts.append(f"重大成就：{achievement_count}项")
        summary_parts.append(f"重大失败：{failure_count}项")
        summary_parts.append(f"\n情感倾向：积极{positive_count} / 消极{negative_count} / 中立{total_events - positive_count - negative_count}")
        
        if key_achievements:
            summary_parts.append("\n【主要成就】")
            for achievement in key_achievements[:3]:
                summary_parts.append(f"  • {achievement.description}")
        
        if key_failures:
            summary_parts.append("\n【主要挫折】")
            for failure in key_failures[:3]:
                summary_parts.append(f"  • {failure.description}")
        
        return "\n".join(summary_parts)
    
    def get_key_moments(self, npc_id: str, min_importance: int = 7) -> List[LifeEvent]:
        """
        获取关键moments
        
        Args:
            npc_id: NPC ID
            min_importance: 最小重要性阈值
            
        Returns:
            关键事件列表
        """
        events = self.records.get(npc_id, [])
        key_events = [e for e in events if e.importance >= min_importance]
        return sorted(key_events, key=lambda e: e.timestamp)
    
    def get_cultivation_history(self, npc_id: str) -> List[LifeEvent]:
        """
        获取修炼历程
        
        Args:
            npc_id: NPC ID
            
        Returns:
            修炼事件列表
        """
        events = self.records.get(npc_id, [])
        cultivation_events = [e for e in events if e.event_type == EventType.CULTIVATION]
        return sorted(cultivation_events, key=lambda e: e.timestamp)
    
    def get_relationship_history(self, npc_id: str) -> Dict[str, List[LifeEvent]]:
        """
        获取人际关系变化
        
        Args:
            npc_id: NPC ID
            
        Returns:
            按NPC分组的事件字典
        """
        events = self.records.get(npc_id, [])
        social_events = [e for e in events if e.event_type == EventType.SOCIAL]
        
        # 按相关NPC分组
        relationships = defaultdict(list)
        for event in social_events:
            for related_npc in event.related_npcs:
                relationships[related_npc].append(event)
        
        # 对每个NPC的事件按时间排序
        for npc in relationships:
            relationships[npc] = sorted(relationships[npc], key=lambda e: e.timestamp)
        
        return dict(relationships)
    
    def get_sorted_events(self, npc_id: str) -> List[LifeEvent]:
        """
        获取按时间排序的所有事件
        
        Args:
            npc_id: NPC ID
            
        Returns:
            排序后的事件列表
        """
        events = self.records.get(npc_id, [])
        return sorted(events, key=lambda e: e.timestamp)
    
    def get_events_by_type(self, npc_id: str, event_type: EventType) -> List[LifeEvent]:
        """
        获取特定类型的事件
        
        Args:
            npc_id: NPC ID
            event_type: 事件类型
            
        Returns:
            事件列表
        """
        events = self.records.get(npc_id, [])
        return [e for e in events if e.event_type == event_type]
    
    def get_events_by_time_range(self, npc_id: str, start_time: float, end_time: float) -> List[LifeEvent]:
        """
        获取时间范围内的事件
        
        Args:
            npc_id: NPC ID
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            事件列表
        """
        events = self.records.get(npc_id, [])
        return [e for e in events if start_time <= e.timestamp <= end_time]
    
    def delete_event(self, npc_id: str, event: LifeEvent) -> bool:
        """
        删除特定事件
        
        Args:
            npc_id: NPC ID
            event: 要删除的事件
            
        Returns:
            是否成功删除
        """
        events = self.records.get(npc_id, [])
        if event in events:
            events.remove(event)
            return True
        return False
    
    def clear_records(self, npc_id: str):
        """
        清空NPC的所有记录
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.records:
            self.records[npc_id] = []
    
    def export_records(self, npc_id: str) -> List[Dict[str, Any]]:
        """
        导出NPC记录为字典列表
        
        Args:
            npc_id: NPC ID
            
        Returns:
            事件字典列表
        """
        events = self.get_sorted_events(npc_id)
        return [e.to_dict() for e in events]
    
    def import_records(self, npc_id: str, events_data: List[Dict[str, Any]]):
        """
        从字典列表导入NPC记录
        
        Args:
            npc_id: NPC ID
            events_data: 事件字典列表
        """
        self.records[npc_id] = [LifeEvent.from_dict(e) for e in events_data]
    
    def _format_event(self, event: LifeEvent) -> str:
        """
        格式化单个事件
        
        Args:
            event: 事件对象
            
        Returns:
            格式化字符串
        """
        emotion_mark = {
            EmotionType.POSITIVE: "【喜】",
            EmotionType.NEGATIVE: "【悲】",
            EmotionType.NEUTRAL: "【平】",
        }.get(event.emotion, "【平】")
        
        location_str = f" [{event.location}]" if event.location else ""
        
        lines = [f"  {emotion_mark} {event.description}{location_str}"]
        
        if event.outcome:
            lines.append(f"      结果：{event.outcome}")
        
        if event.related_npcs:
            lines.append(f"      相关：{', '.join(event.related_npcs)}")
        
        return "\n".join(lines)
    
    def _get_realm_name(self, realm_level: int) -> str:
        """
        获取境界名称
        
        Args:
            realm_level: 境界等级
            
        Returns:
            境界名称
        """
        realm_info = get_realm_info(realm_level)
        return realm_info.name if realm_info else f"境界{realm_level}"


class NPCStoryGenerator:
    """
    NPC故事生成器
    
    根据人生事件生成各种形式的故事内容
    """
    
    def __init__(self):
        """初始化故事生成器"""
        self.chapter_titles = {
            EventType.CULTIVATION: [
                "问道之路", "苦修岁月", "突破桎梏", "悟道求真", "境界飞升",
                "灵根觉醒", "心法传承", "丹田初成", "金丹大道", "元婴化形",
            ],
            EventType.COMBAT: [
                "血战八方", "剑气纵横", "生死搏杀", "威震四方", "一战成名",
                "狭路相逢", "以弱胜强", "浴血奋战", "绝处逢生", "战无不胜",
            ],
            EventType.SOCIAL: [
                "红尘结缘", "知己相逢", "恩怨情仇", "师门情谊", "道侣双修",
                "萍水相逢", "一见如故", "生死之交", "反目成仇", "冰释前嫌",
            ],
            EventType.DECISION: [
                "命运抉择", "十字路口", "一念之差", "舍与得", "破釜沉舟",
                "义无反顾", "背水一战", "改弦更张", "迷途知返", "矢志不渝",
            ],
            EventType.ACHIEVEMENT: [
                "功成名就", "荣耀时刻", "登峰造极", "名垂青史", "万古流芳",
                "一鸣惊人", "独占鳌头", "誉满天下", "功德圆满", "飞升成仙",
            ],
            EventType.FAILURE: [
                "命运多舛", "挫折磨难", "跌入谷底", "痛定思痛", "浴火重生",
                "功亏一篑", "马失前蹄", "时运不济", "命途多舛", "东山再起",
            ],
        }
    
    def generate_story(self, life_events: List[LifeEvent]) -> str:
        """
        根据事件生成故事
        
        Args:
            life_events: 人生事件列表
            
        Returns:
            生成的故事文本
        """
        if not life_events:
            return "暂无故事可讲述..."
        
        # 按时间排序
        sorted_events = sorted(life_events, key=lambda e: e.timestamp)
        
        # 提取重要事件
        important_events = [e for e in sorted_events if e.importance >= 5]
        
        story_parts = []
        story_parts.append("【传奇人生】\n")
        
        # 生成故事段落
        current_chapter = 1
        for i, event in enumerate(important_events):
            # 每3-5个事件分一章
            if i > 0 and i % 4 == 0:
                current_chapter += 1
                story_parts.append(f"\n第{current_chapter}章：{self.generate_chapter_title(event)}")
            elif i == 0:
                story_parts.append(f"第{current_chapter}章：{self.generate_chapter_title(event)}")
            
            # 生成段落
            paragraph = self._generate_paragraph(event, i, important_events)
            story_parts.append(paragraph)
        
        return "\n\n".join(story_parts)
    
    def generate_timeline(self, life_events: List[LifeEvent]) -> str:
        """
        生成时间线
        
        Args:
            life_events: 人生事件列表
            
        Returns:
            格式化的时间线文本
        """
        if not life_events:
            return "暂无时间线数据"
        
        sorted_events = sorted(life_events, key=lambda e: e.timestamp)
        
        lines = []
        lines.append("【人生时间线】")
        lines.append("")
        
        for i, event in enumerate(sorted_events):
            # 时间标记
            time_str = self._format_timestamp(event.timestamp)
            
            # 重要性标记
            importance_marks = "★" * (event.importance // 2)
            
            # 情感标记
            emotion_emoji = {
                EmotionType.POSITIVE: "😊",
                EmotionType.NEGATIVE: "😢",
                EmotionType.NEUTRAL: "😐",
            }.get(event.emotion, "😐")
            
            lines.append(f"{time_str} {emotion_emoji} [{event.event_type.value}] {importance_marks}")
            lines.append(f"    {event.description}")
            if event.outcome:
                lines.append(f"    → {event.outcome}")
            lines.append("")
        
        return "\n".join(lines)
    
    def analyze_personality(self, life_events: List[LifeEvent]) -> Dict[str, Any]:
        """
        分析性格特征
        
        Args:
            life_events: 人生事件列表
            
        Returns:
            性格分析结果字典
        """
        if not life_events:
            return {"personality": "未知", "traits": []}
        
        # 统计各类事件
        event_counts = defaultdict(int)
        emotion_counts = defaultdict(int)
        
        for event in life_events:
            event_counts[event.event_type] += 1
            emotion_counts[event.emotion] += 1
        
        total = len(life_events)
        
        # 计算倾向
        traits = []
        
        # 战斗倾向
        combat_ratio = event_counts[EventType.COMBAT] / total if total > 0 else 0
        if combat_ratio > 0.3:
            traits.append("好战")
        elif combat_ratio > 0.15:
            traits.append("尚武")
        elif combat_ratio < 0.05:
            traits.append("和平")
        
        # 社交倾向
        social_ratio = event_counts[EventType.SOCIAL] / total if total > 0 else 0
        if social_ratio > 0.3:
            traits.append("外向")
        elif social_ratio < 0.1:
            traits.append("孤僻")
        else:
            traits.append("合群")
        
        # 进取心
        cultivation_ratio = event_counts[EventType.CULTIVATION] / total if total > 0 else 0
        if cultivation_ratio > 0.3:
            traits.append("刻苦")
        elif cultivation_ratio > 0.15:
            traits.append("勤奋")
        else:
            traits.append("随性")
        
        # 决策风格
        decision_ratio = event_counts[EventType.DECISION] / total if total > 0 else 0
        if decision_ratio > 0.15:
            traits.append("果断")
        else:
            traits.append("谨慎")
        
        # 情感倾向
        positive_ratio = emotion_counts[EmotionType.POSITIVE] / total if total > 0 else 0
        negative_ratio = emotion_counts[EmotionType.NEGATIVE] / total if total > 0 else 0
        
        if positive_ratio > negative_ratio * 2:
            traits.append("乐观")
        elif negative_ratio > positive_ratio * 1.5:
            traits.append("悲观")
        else:
            traits.append("沉稳")
        
        # 成就导向
        achievement_ratio = event_counts[EventType.ACHIEVEMENT] / total if total > 0 else 0
        failure_ratio = event_counts[EventType.FAILURE] / total if total > 0 else 0
        
        if achievement_ratio > failure_ratio:
            traits.append("成功导向")
        elif failure_ratio > achievement_ratio * 1.5:
            traits.append("命运多舛")
        
        # 确定主要性格
        personality = "均衡"
        if "好战" in traits and "果断" in traits:
            personality = "激进"
        elif "和平" in traits and "谨慎" in traits:
            personality = "保守"
        elif "刻苦" in traits and "成功导向" in traits:
            personality = "进取"
        elif "孤僻" in traits:
            personality = "内敛"
        elif "外向" in traits and "乐观" in traits:
            personality = "开朗"
        
        return {
            "personality": personality,
            "traits": traits,
            "event_distribution": dict(event_counts),
            "emotion_distribution": {
                "positive": emotion_counts[EmotionType.POSITIVE],
                "negative": emotion_counts[EmotionType.NEGATIVE],
                "neutral": emotion_counts[EmotionType.NEUTRAL],
            },
            "statistics": {
                "total_events": total,
                "combat_ratio": round(combat_ratio, 2),
                "social_ratio": round(social_ratio, 2),
                "cultivation_ratio": round(cultivation_ratio, 2),
                "positive_ratio": round(positive_ratio, 2),
            }
        }
    
    def generate_chapter_title(self, event: LifeEvent) -> str:
        """
        生成章节标题
        
        Args:
            event: 事件对象
            
        Returns:
            章节标题
        """
        titles = self.chapter_titles.get(event.event_type, ["风云变幻"])
        
        # 根据重要性选择标题
        if event.importance >= 8:
            return titles[0] if len(titles) > 0 else "重大时刻"
        elif event.importance >= 6:
            return titles[1] if len(titles) > 1 else "关键时刻"
        else:
            return random.choice(titles[2:]) if len(titles) > 2 else "日常点滴"
    
    def format_story(self, story_parts: List[str]) -> str:
        """
        格式化故事输出
        
        Args:
            story_parts: 故事段落列表
            
        Returns:
            格式化后的故事文本
        """
        formatted = []
        formatted.append("=" * 60)
        formatted.append("")
        
        for part in story_parts:
            formatted.append(part)
            formatted.append("")
        
        formatted.append("=" * 60)
        
        return "\n".join(formatted)
    
    def generate_epilogue(self, life_events: List[LifeEvent]) -> str:
        """
        生成故事尾声
        
        Args:
            life_events: 人生事件列表
            
        Returns:
            尾声文本
        """
        if not life_events:
            return ""
        
        # 分析整体人生
        personality_analysis = self.analyze_personality(life_events)
        
        # 统计成就与失败
        achievements = [e for e in life_events if e.event_type == EventType.ACHIEVEMENT]
        failures = [e for e in life_events if e.event_type == EventType.FAILURE]
        
        # 获取最高境界
        cultivation_events = [e for e in life_events if e.event_type == EventType.CULTIVATION]
        highest_realm = "凡人"
        if cultivation_events:
            for event in sorted(cultivation_events, key=lambda e: e.timestamp, reverse=True):
                if event.details and "new_realm_name" in event.details:
                    highest_realm = event.details["new_realm_name"]
                    break
        
        lines = []
        lines.append("\n【尾声】")
        lines.append("-" * 30)
        lines.append(f"此人一生{personality_analysis['personality']}，")
        
        if achievements and not failures:
            lines.append(f"一路顺遂，共达成{len(achievements)}项成就，")
        elif failures and not achievements:
            lines.append(f"命运多舛，经历{len(failures)}次重大挫折，")
        elif achievements and failures:
            lines.append(f"历经磨难，有{len(achievements)}项成就也有{len(failures)}次失败，")
        else:
            lines.append("平平淡淡，")
        
        lines.append(f"最终修至{highest_realm}。")
        
        # 添加性格特征
        if personality_analysis["traits"]:
            lines.append(f"其性格{'、'.join(personality_analysis['traits'][:3])}，")
            lines.append("留给后人无尽传说。")
        
        return "\n".join(lines)
    
    def _generate_paragraph(self, event: LifeEvent, index: int, all_events: List[LifeEvent]) -> str:
        """
        生成故事段落
        
        Args:
            event: 当前事件
            index: 事件索引
            all_events: 所有事件列表
            
        Returns:
            段落文本
        """
        # 根据事件类型生成不同风格的描述
        paragraphs = {
            EventType.CULTIVATION: [
                f"在{event.location if event.location else '某处'}，{event.description}。",
                f"经过苦修，终于{event.outcome}。",
                f"这一突破，让修为更上一层楼。",
            ],
            EventType.COMBAT: [
                f"一场激战在{event.location if event.location else '某处'}展开，{event.description}。",
                f"最终{event.outcome}，",
                "此战之后，名声大噪。" if event.emotion == EmotionType.POSITIVE else "此战令人唏嘘。",
            ],
            EventType.SOCIAL: [
                f"在{event.location if event.location else '某处'}，{event.description}。",
                f"这段{event.details.get('interaction_type', '交往')}关系，",
                "成为人生中重要的一笔。",
            ],
            EventType.DECISION: [
                f"面临人生抉择，{event.description}。",
                f"之所以如此选择，是因为{event.outcome}。",
                "这个决定改变了命运的轨迹。",
            ],
            EventType.ACHIEVEMENT: [
                f"经过不懈努力，{event.description}。",
                f"在{event.location if event.location else '某处'}，这一成就被载入史册。",
                "这是人生中最辉煌的时刻之一。",
            ],
            EventType.FAILURE: [
                f"命运弄人，{event.description}。",
                f"在{event.location if event.location else '某处'}，遭遇了人生最大的挫折。",
                "但失败并未击垮意志，反而激发了更强的斗志。" if index < len(all_events) - 1 else "这一失败成为永远的遗憾。",
            ],
        }
        
        templates = paragraphs.get(event.event_type, [f"{event.description}。", f"{event.outcome}。"])
        return "".join(templates)
    
    def _format_timestamp(self, timestamp: float) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp: 时间戳
            
        Returns:
            格式化的时间字符串
        """
        try:
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y年%m月%d日")
        except:
            return "未知时间"


# 全局实例
npc_life_record = NPCLifeRecord()
npc_story_generator = NPCStoryGenerator()


def get_life_record() -> NPCLifeRecord:
    """获取全局NPC成长轨迹记录器实例"""
    return npc_life_record


def get_story_generator() -> NPCStoryGenerator:
    """获取全局NPC故事生成器实例"""
    return npc_story_generator
