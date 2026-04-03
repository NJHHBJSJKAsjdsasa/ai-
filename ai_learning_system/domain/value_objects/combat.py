"""战斗相关的值对象"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class CombatMode(Enum):
    """战斗模式枚举"""
    SPAR = "切磋"           # 切磋模式：不会死亡，结束后恢复
    DEATHMATCH = "死斗"     # 死斗模式：可能死亡，掉落物品


class DamageType(Enum):
    """伤害类型枚举"""
    PHYSICAL = "物理"       # 物理伤害
    MAGIC = "法术"          # 法术伤害
    TRUE = "真实"           # 真实伤害（无视防御）


class CombatStatus(Enum):
    """战斗状态枚举"""
    ONGOING = "进行中"
    PLAYER_WIN = "玩家胜利"
    ENEMY_WIN = "敌人胜利"
    FLED = "逃跑"
    DRAW = "平局"


@dataclass(frozen=True)
class CombatSkill:
    """战斗技能值对象"""
    name: str                           # 技能名称
    description: str = ""               # 技能描述
    damage: int = 0                     # 基础伤害
    damage_type: DamageType = DamageType.PHYSICAL  # 伤害类型
    mana_cost: int = 0                  # 灵力消耗
    cooldown: int = 0                   # 冷却回合
    is_aoe: bool = False                # 是否范围攻击
    effects: List[Dict[str, Any]] = field(default_factory=list)  # 附加效果


@dataclass
class CombatResult:
    """战斗结果值对象"""
    status: CombatStatus
    winner_id: Optional[str] = None
    loser_id: Optional[str] = None
    exp_reward: int = 0
    spirit_stones_reward: int = 0
    loot: List[str] = field(default_factory=list)
    combat_log: List[str] = field(default_factory=list)
    turns: int = 0
    mode: CombatMode = CombatMode.SPAR
    # 处决相关字段（死斗模式专用）
    execution_pending: bool = False  # 是否等待处决选择
    can_execute: bool = False  # 是否可以处决
    enemy_npc_id: Optional[str] = None  # 敌人NPC ID，用于处决
