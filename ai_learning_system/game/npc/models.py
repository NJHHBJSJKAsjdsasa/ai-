"""
NPC数据模型模块
包含NPCMemory和NPCData数据类
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class NPCMemory:
    """NPC记忆数据类"""
    content: str
    importance: int = 5  # 重要性（0-10）
    timestamp: int = 0  # 游戏时间戳
    emotion: str = "neutral"  # 情感（positive/negative/neutral）


@dataclass
class NPCData:
    """NPC数据类"""
    id: str
    name: str
    dao_name: str
    age: int
    lifespan: int
    realm_level: int
    sect: str
    personality: str
    occupation: str
    location: str

    # 门派相关信息
    sect_type: str = ""  # 门派类型（正道/邪道/中立）
    sect_specialty: str = ""  # 门派专长

    # 关系
    favor: Dict[str, int] = field(default_factory=dict)  # 对玩家的好感度

    # 记忆
    memories: List[NPCMemory] = field(default_factory=list)

    # 状态
    is_alive: bool = True

    # 死亡相关
    death_info: Dict = field(default_factory=dict)  # 死亡信息字典
    can_resurrect: bool = True  # 是否可复活

    # 善恶值 (-100到100，负数邪恶，正数善良)
    morality: int = 0

    # 战斗属性
    attack: int = 10  # 基础攻击力
    defense: int = 5  # 基础防御力
    speed: int = 8  # 基础速度
    crit_rate: float = 0.03  # 暴击率
    dodge_rate: float = 0.03  # 闪避率
    combat_wins: int = 0  # 胜利次数
    combat_losses: int = 0  # 失败次数
    
    # 新增属性
    race: str = "人类"  # 种族
    special_trait: str = ""  # 特殊特质
    unique_ability: str = ""  # 独特能力

    def __post_init__(self):
        if not self.memories:
            self.memories = []
