"""NPC相关的值对象"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class EmotionType(Enum):
    """情感类型"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"


class MemoryCategory(Enum):
    """记忆类别"""
    ACHIEVEMENT = "achievement"
    SOCIAL = "social"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    DAILY = "daily"
    WORLD_EVENT = "world_event"


@dataclass(frozen=True)
class NPCMemory:
    """NPC记忆值对象"""
    content: str
    importance: int = 5  # 重要性（0-10）
    timestamp: int = 0  # 游戏时间戳
    emotion: EmotionType = EmotionType.NEUTRAL
    category: MemoryCategory = MemoryCategory.DAILY

    def __post_init__(self):
        # 验证重要性范围
        if not 0 <= self.importance <= 10:
            raise ValueError("重要性必须在0-10之间")


class RelationshipType(Enum):
    """关系类型"""
    ACQUAINTANCE = "acquaintance"  # 认识
    FRIEND = "friend"  # 朋友
    ENEMY = "enemy"  # 敌人
    TEACHER = "teacher"  # 师傅
    STUDENT = "student"  # 徒弟
    FAMILY = "family"  # 家人


@dataclass(frozen=True)
class Relationship:
    """NPC关系值对象"""
    npc_id: str
    relationship_type: RelationshipType
    affinity: int = 0  # 好感度 (-100 to 100)
    intimacy: int = 0  # 亲密度 (0 to 100)
    hatred: int = 0  # 仇恨度 (0 to 100)
    last_interaction: int = 0  # 最后互动时间

    def __post_init__(self):
        # 验证数值范围
        if not -100 <= self.affinity <= 100:
            raise ValueError("好感度必须在-100到100之间")
        if not 0 <= self.intimacy <= 100:
            raise ValueError("亲密度必须在0到100之间")
        if not 0 <= self.hatred <= 100:
            raise ValueError("仇恨度必须在0到100之间")

    def with_updates(self, **kwargs) -> 'Relationship':
        """创建带有更新值的新关系对象"""
        new_values = {**self.__dict__}
        new_values.update(kwargs)
        return Relationship(**new_values)


@dataclass(frozen=True)
class Dialogue:
    """对话值对象"""
    content: str
    speaker_id: str
    speaker_name: str
    context: str = ""
    emotion: EmotionType = EmotionType.NEUTRAL
    timestamp: int = 0


class PersonalityTrait(Enum):
    """个性特质"""
    DILIGENCE = "diligence"  # 勤奋
    BRAVERY = "bravery"  # 勇敢
    WISDOM = "wisdom"  # 智慧
    KINDNESS = "kindness"  # 善良
    AMBITION = "ambition"  # 野心
    PATIENCE = "patience"  # 耐心
    TEMPER = "temper"  # 脾气


@dataclass(frozen=True)
class Personality:
    """个性值对象"""
    traits: Dict[PersonalityTrait, float]  # 特质值 (0-1)
    personality_type: str  # 个性类型名称

    def __post_init__(self):
        # 验证特质值范围
        for trait, value in self.traits.items():
            if not 0 <= value <= 1:
                raise ValueError(f"特质{str(trait)}的值必须在0-1之间")


@dataclass(frozen=True)
class CultivationInfo:
    """修炼信息值对象"""
    realm_level: int
    realm_name: str
    lifespan: int
    cultivation_speed: float = 1.0  # 修炼速度倍率


@dataclass(frozen=True)
class NPCStats:
    """NPC属性值对象"""
    attack: int
    defense: int
    speed: int
    crit_rate: float
    dodge_rate: float

    def __post_init__(self):
        # 验证数值范围
        if self.attack < 0:
            raise ValueError("攻击力不能为负")
        if self.defense < 0:
            raise ValueError("防御力不能为负")
        if self.speed < 0:
            raise ValueError("速度不能为负")
        if not 0 <= self.crit_rate <= 1:
            raise ValueError("暴击率必须在0-1之间")
        if not 0 <= self.dodge_rate <= 1:
            raise ValueError("闪避率必须在0-1之间")


@dataclass(frozen=True)
class ScheduleActivity:
    """日程活动值对象"""
    activity_type: str
    start_time: int  # 开始小时 (0-23)
    duration: int  # 持续小时
    location: str
    priority: int = 5  # 优先级 (1-10)

    def __post_init__(self):
        # 验证时间范围
        if not 0 <= self.start_time <= 23:
            raise ValueError("开始时间必须在0-23之间")
        if self.duration <= 0:
            raise ValueError("持续时间必须大于0")
        if not 1 <= self.priority <= 10:
            raise ValueError("优先级必须在1-10之间")
