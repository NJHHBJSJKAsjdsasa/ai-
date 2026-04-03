from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict

class PlayerState(Enum):
    """玩家状态枚举"""
    IDLE = "idle"  # 空闲
    CULTIVATING = "cultivating"  # 修炼中
    MEDITATING = "meditating"  # 冥想中
    EXPLORING = "exploring"  # 探索中
    FIGHTING = "fighting"  # 战斗中
    TRADING = "trading"  # 交易中
    SOCIALIZING = "socializing"  # 社交中
    ALCHEMY = "alchemy"  # 炼丹中
    REFINING = "refining"  # 炼器中
    QUESTING = "questing"  # 任务中
    RESTING = "resting"  # 休息中
    DEAD = "dead"  # 死亡
    REBIRTHING = "rebirthing"  # 转世中
    BREAKING_THROUGH = "breaking_through"  # 突破中
    TRIBULATION = "tribulation"  # 渡劫中
    ASCENDING = "ascending"  # 飞升中

class AfflictionType(Enum):
    """ affliction类型枚举"""
    POISON = "poison"  # 中毒
    CURSE = "curse"  # 诅咒
    ILLNESS = "illness"  # 疾病
    INJURY = "injury"  # 受伤
    EXHAUSTION = "exhaustion"  # 疲惫
    MADNESS = "madness"  # 疯狂

@dataclass(frozen=True)
class Affliction:
    """玩家状态值对象"""
    type: AfflictionType
    severity: int  # 严重程度（1-10）
    duration: int  # 持续时间（分钟）
    description: str

@dataclass(frozen=True)
class PlayerStatus:
    """玩家状态值对象"""
    current_state: PlayerState = PlayerState.IDLE
    is_alive: bool = True
    is_immortal: bool = False
    is_in_sect: bool = False
    is_in_cave: bool = False
    is_in_world: bool = True
    is_meditating: bool = False
    is_cultivating: bool = False
    is_exploring: bool = False
    is_fighting: bool = False
    is_trading: bool = False
    is_socializing: bool = False
    is_alchemy: bool = False
    is_refining: bool = False
    is_questing: bool = False
    is_resting: bool = False
    is_dead: bool = False
    is_rebirthing: bool = False
    is_breaking_through: bool = False
    is_tribulation: bool = False
    is_ascending: bool = False
    afflictions: List[Affliction] = None
    current_location: str = "新手村"
    current_sect: Optional[str] = None
    current_cave: Optional[str] = None
    current_world: str = "主世界"
    current_quest: Optional[str] = None
    current_enemy: Optional[str] = None
    current_friend: Optional[str] = None
    current_technique: Optional[str] = None
    current_pill: Optional[str] = None
    current_material: Optional[str] = None
    current_treasure: Optional[str] = None
    current_weapon: Optional[str] = None
    current_armor: Optional[str] = None
    current_pet: Optional[str] = None
    current_event: Optional[str] = None
    current_memory: Optional[str] = None
    current_achievement: Optional[str] = None
    current_sect_rank: Optional[str] = None
    current_cultivation_progress: float = 0.0
    current_breakthrough_progress: float = 0.0
    current_tribulation_progress: float = 0.0
    current_ascension_progress: float = 0.0
    current_rest_progress: float = 0.0
    current_meditation_progress: float = 0.0
    current_exploration_progress: float = 0.0
    current_alchemy_progress: float = 0.0
    current_refining_progress: float = 0.0
    current_trade_progress: float = 0.0
    current_social_progress: float = 0.0
    current_quest_progress: float = 0.0
    current_fight_progress: float = 0.0

    def __post_init__(self):
        if self.afflictions is None:
            object.__setattr__(self, 'afflictions', [])

    def update(self, **kwargs) -> 'PlayerStatus':
        """更新状态并返回新的状态对象"""
        new_status = self.__dict__.copy()
        new_status.update(kwargs)
        return PlayerStatus(**new_status)

    def add_affliction(self, affliction: Affliction) -> 'PlayerStatus':
        """添加状态"""
        new_afflictions = self.afflictions.copy()
        new_afflictions.append(affliction)
        return self.update(afflictions=new_afflictions)

    def remove_affliction(self, affliction_type: AfflictionType) -> 'PlayerStatus':
        """移除状态"""
        new_afflictions = [a for a in self.afflictions if a.type != affliction_type]
        return self.update(afflictions=new_afflictions)

    def has_affliction(self, affliction_type: AfflictionType) -> bool:
        """检查是否有特定状态"""
        return any(a.type == affliction_type for a in self.afflictions)

    def get_affliction_severity(self, affliction_type: AfflictionType) -> int:
        """获取状态严重程度"""
        for a in self.afflictions:
            if a.type == affliction_type:
                return a.severity
        return 0

    def is_in_combat(self) -> bool:
        """检查是否在战斗中"""
        return self.current_state == PlayerState.FIGHTING

    def is_available(self) -> bool:
        """检查是否可用"""
        return self.current_state in [PlayerState.IDLE, PlayerState.RESTING]

    def is_busy(self) -> bool:
        """检查是否忙碌"""
        return not self.is_available()

    def is_in_danger(self) -> bool:
        """检查是否处于危险中"""
        return self.current_state in [PlayerState.FIGHTING, PlayerState.TRIBULATION]

    def get_current_activity(self) -> str:
        """获取当前活动"""
        return self.current_state.value

    def get_location_info(self) -> Dict[str, str]:
        """获取位置信息"""
        return {
            "world": self.current_world,
            "location": self.current_location,
            "sect": self.current_sect or "无",
            "cave": self.current_cave or "无"
        }
