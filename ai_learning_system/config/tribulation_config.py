"""
天劫系统配置模块
定义天劫的各个阶段、雷劫威力、奖励等配置
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class TribulationType(Enum):
    """天劫类型"""
    NORMAL = "normal"           # 普通天劫
    ENHANCED = "enhanced"       # 强化天劫（业力影响）
    HEAVENLY = "heavenly"       # 天道天劫（特殊触发）
    DEMONIC = "demonic"         # 魔劫（业力为负）


class TribulationStatus(Enum):
    """天劫状态"""
    PENDING = "pending"         # 待触发
    PREPARING = "preparing"     # 准备中
    IN_PROGRESS = "in_progress" # 进行中
    SUCCESS = "success"         # 成功
    FAILURE = "failure"         # 失败
    DEATH = "death"             # 死亡


class ThunderType(Enum):
    """雷劫类型"""
    NORMAL = "普通雷劫"
    YIN_YANG = "阴阳雷劫"
    FIVE_ELEMENTS = "五行雷劫"
    DESTRUCTION = "毁灭雷劫"
    HEAVENLY_PUNISHMENT = "天罚雷劫"


@dataclass
class ThunderStrike:
    """雷劫数据类"""
    number: int                 # 第几道雷劫
    name: str                   # 雷劫名称
    base_power: int             # 基础威力
    power_multiplier: float     # 威力倍率
    thunder_type: ThunderType   # 雷劫类型
    special_effect: Optional[str] = None  # 特殊效果
    description: str = ""       # 描述


@dataclass
class TribulationStage:
    """天劫阶段数据类"""
    realm_level: int            # 对应境界等级
    realm_name: str             # 境界名称
    tribulation_name: str       # 天劫名称
    description: str            # 描述
    total_thunder: int          # 雷劫总数
    base_power: int             # 基础威力
    power_growth: float         # 威力增长系数
    thunder_types: List[ThunderType]  # 雷劫类型序列
    required_resistance: float  # 所需雷抗
    time_limit: int             # 时间限制（回合数）
    rewards: Dict[str, any]     # 奖励配置
    failure_penalty: Dict[str, any]  # 失败惩罚


@dataclass
class TribulationReward:
    """天劫奖励数据类"""
    reward_type: str            # 奖励类型
    name: str                   # 奖励名称
    description: str            # 描述
    min_value: float            # 最小值
    max_value: float            # 最大值
    probability: float          # 触发概率


@dataclass
class PreparationItem:
    """天劫准备物品数据类"""
    item_type: str              # 物品类型（法宝/丹药/阵法）
    name: str                   # 名称
    description: str            # 描述
    effect_type: str            # 效果类型
    effect_value: float         # 效果值
    required_realm: int         # 所需境界
    rarity: str                 # 稀有度


# ==================== 天劫阶段配置 ====================

TRIBULATION_STAGES: Dict[int, TribulationStage] = {
    1: TribulationStage(
        realm_level=1,
        realm_name="练气期",
        tribulation_name="小雷劫",
        description="练气期突破筑基期时触发的小型雷劫，共3道",
        total_thunder=3,
        base_power=50,
        power_growth=1.2,
        thunder_types=[ThunderType.NORMAL, ThunderType.NORMAL, ThunderType.NORMAL],
        required_resistance=0.1,
        time_limit=10,
        rewards={
            "max_health": 50,
            "max_spiritual_power": 30,
            "defense": 5,
            "special_reward_probability": 0.3
        },
        failure_penalty={
            "health_loss": 0.3,
            "exp_loss": 0.1,
            "injury_days": 30
        }
    ),
    2: TribulationStage(
        realm_level=2,
        realm_name="筑基期",
        tribulation_name="筑基雷劫",
        description="筑基期突破金丹期时触发的雷劫，共5道",
        total_thunder=5,
        base_power=100,
        power_growth=1.3,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.NORMAL,
            ThunderType.YIN_YANG,
            ThunderType.YIN_YANG,
            ThunderType.NORMAL
        ],
        required_resistance=0.2,
        time_limit=15,
        rewards={
            "max_health": 100,
            "max_spiritual_power": 60,
            "defense": 10,
            "attack": 5,
            "special_reward_probability": 0.4
        },
        failure_penalty={
            "health_loss": 0.4,
            "exp_loss": 0.15,
            "injury_days": 60,
            "realm_fall_probability": 0.1
        }
    ),
    3: TribulationStage(
        realm_level=3,
        realm_name="金丹期",
        tribulation_name="金丹大劫",
        description="金丹期突破元婴期时触发的大劫，共7道",
        total_thunder=7,
        base_power=200,
        power_growth=1.4,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.YIN_YANG,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.YIN_YANG,
            ThunderType.NORMAL,
            ThunderType.DESTRUCTION
        ],
        required_resistance=0.3,
        time_limit=20,
        rewards={
            "max_health": 200,
            "max_spiritual_power": 120,
            "defense": 20,
            "attack": 15,
            "crit_rate": 0.02,
            "special_reward_probability": 0.5
        },
        failure_penalty={
            "health_loss": 0.5,
            "exp_loss": 0.2,
            "injury_days": 90,
            "realm_fall_probability": 0.2
        }
    ),
    4: TribulationStage(
        realm_level=4,
        realm_name="元婴期",
        tribulation_name="元婴天劫",
        description="元婴期突破化神期时触发的天劫，共9道",
        total_thunder=9,
        base_power=350,
        power_growth=1.5,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.YIN_YANG,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.DESTRUCTION,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.YIN_YANG,
            ThunderType.DESTRUCTION
        ],
        required_resistance=0.4,
        time_limit=25,
        rewards={
            "max_health": 350,
            "max_spiritual_power": 200,
            "defense": 35,
            "attack": 30,
            "crit_rate": 0.03,
            "dodge_rate": 0.02,
            "special_reward_probability": 0.6
        },
        failure_penalty={
            "health_loss": 0.6,
            "exp_loss": 0.25,
            "injury_days": 120,
            "realm_fall_probability": 0.3
        }
    ),
    5: TribulationStage(
        realm_level=5,
        realm_name="化神期",
        tribulation_name="化神大劫",
        description="化神期突破渡劫期时触发的大劫，共12道",
        total_thunder=12,
        base_power=550,
        power_growth=1.6,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.YIN_YANG,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.DESTRUCTION,
            ThunderType.DESTRUCTION,
            ThunderType.HEAVENLY_PUNISHMENT,
            ThunderType.DESTRUCTION,
            ThunderType.DESTRUCTION,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.HEAVENLY_PUNISHMENT
        ],
        required_resistance=0.5,
        time_limit=30,
        rewards={
            "max_health": 500,
            "max_spiritual_power": 300,
            "defense": 50,
            "attack": 50,
            "crit_rate": 0.05,
            "dodge_rate": 0.03,
            "special_reward_probability": 0.7
        },
        failure_penalty={
            "health_loss": 0.7,
            "exp_loss": 0.3,
            "injury_days": 180,
            "realm_fall_probability": 0.4,
            "death_probability": 0.1
        }
    ),
    6: TribulationStage(
        realm_level=6,
        realm_name="渡劫期",
        tribulation_name="飞升仙劫",
        description="渡劫期突破大乘期时触发的飞升劫，共18道",
        total_thunder=18,
        base_power=800,
        power_growth=1.7,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.YIN_YANG,
            ThunderType.YIN_YANG,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.DESTRUCTION,
            ThunderType.DESTRUCTION,
            ThunderType.HEAVENLY_PUNISHMENT,
            ThunderType.HEAVENLY_PUNISHMENT,
            ThunderType.DESTRUCTION,
            ThunderType.DESTRUCTION,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.FIVE_ELEMENTS,
            ThunderType.YIN_YANG,
            ThunderType.YIN_YANG,
            ThunderType.HEAVENLY_PUNISHMENT
        ],
        required_resistance=0.6,
        time_limit=40,
        rewards={
            "max_health": 800,
            "max_spiritual_power": 500,
            "defense": 80,
            "attack": 80,
            "crit_rate": 0.08,
            "dodge_rate": 0.05,
            "special_reward_probability": 0.8
        },
        failure_penalty={
            "health_loss": 0.8,
            "exp_loss": 0.35,
            "injury_days": 240,
            "realm_fall_probability": 0.5,
            "death_probability": 0.2
        }
    ),
    7: TribulationStage(
        realm_level=7,
        realm_name="大乘期",
        tribulation_name="真仙天劫",
        description="大乘期突破真仙期时触动的真仙劫，共27道",
        total_thunder=27,
        base_power=1200,
        power_growth=1.8,
        thunder_types=[
            ThunderType.NORMAL,
            ThunderType.YIN_YANG, ThunderType.YIN_YANG,
            ThunderType.FIVE_ELEMENTS, ThunderType.FIVE_ELEMENTS, ThunderType.FIVE_ELEMENTS,
            ThunderType.DESTRUCTION, ThunderType.DESTRUCTION, ThunderType.DESTRUCTION,
            ThunderType.HEAVENLY_PUNISHMENT, ThunderType.HEAVENLY_PUNISHMENT,
            ThunderType.DESTRUCTION, ThunderType.DESTRUCTION, ThunderType.DESTRUCTION,
            ThunderType.FIVE_ELEMENTS, ThunderType.FIVE_ELEMENTS, ThunderType.FIVE_ELEMENTS,
            ThunderType.YIN_YANG, ThunderType.YIN_YANG,
            ThunderType.DESTRUCTION, ThunderType.DESTRUCTION, ThunderType.DESTRUCTION,
            ThunderType.HEAVENLY_PUNISHMENT, ThunderType.HEAVENLY_PUNISHMENT,
            ThunderType.FIVE_ELEMENTS, ThunderType.FIVE_ELEMENTS,
            ThunderType.HEAVENLY_PUNISHMENT
        ],
        required_resistance=0.7,
        time_limit=50,
        rewards={
            "max_health": 1200,
            "max_spiritual_power": 800,
            "defense": 120,
            "attack": 120,
            "crit_rate": 0.1,
            "dodge_rate": 0.08,
            "special_reward_probability": 0.9
        },
        failure_penalty={
            "health_loss": 0.9,
            "exp_loss": 0.4,
            "injury_days": 365,
            "realm_fall_probability": 0.6,
            "death_probability": 0.3
        }
    ),
}


# ==================== 雷劫名称生成 ====================

THUNDER_NAMES = {
    ThunderType.NORMAL: ["普通天雷", "青木神雷", "庚金神雷", "癸水神雷", "丙火神雷", "戊土神雷"],
    ThunderType.YIN_YANG: ["阴阳神雷", "太阴神雷", "太阳神雷", "两仪神雷", "太极神雷"],
    ThunderType.FIVE_ELEMENTS: ["五行神雷", "金行神雷", "木行神雷", "水行神雷", "火行神雷", "土行神雷"],
    ThunderType.DESTRUCTION: ["毁灭神雷", "寂灭神雷", "灭世神雷", "混沌神雷", "虚无神雷"],
    ThunderType.HEAVENLY_PUNISHMENT: ["天罚神雷", "天道神雷", "惩戒神雷", "审判神雷", "天谴神雷"],
}


def generate_thunder_name(thunder_type: ThunderType, number: int) -> str:
    """生成雷劫名称"""
    names = THUNDER_NAMES.get(thunder_type, ["神雷"])
    base_name = random.choice(names)
    return f"第{number}道·{base_name}"


# ==================== 天劫奖励配置 ====================

TRIBULATION_REWARDS: Dict[str, List[TribulationReward]] = {
    "common": [
        TribulationReward("attribute", "气血提升", "渡劫后气血上限提升", 10, 50, 1.0),
        TribulationReward("attribute", "灵力提升", "渡劫后灵力上限提升", 10, 30, 1.0),
        TribulationReward("attribute", "防御提升", "渡劫后防御力提升", 5, 20, 0.9),
    ],
    "rare": [
        TribulationReward("attribute", "攻击提升", "渡劫后攻击力提升", 10, 30, 0.7),
        TribulationReward("attribute", "暴击提升", "渡劫后暴击率提升", 0.01, 0.05, 0.6),
        TribulationReward("attribute", "闪避提升", "渡劫后闪避率提升", 0.01, 0.05, 0.6),
        TribulationReward("special", "雷抗提升", "获得雷属性抗性", 0.05, 0.15, 0.5),
    ],
    "legendary": [
        TribulationReward("special", "天劫之力", "获得操控天劫的能力", 1, 1, 0.2),
        TribulationReward("special", "雷体", "转化为雷灵之体", 1, 1, 0.15),
        TribulationReward("special", "天道感悟", "获得天道法则感悟", 1, 1, 0.1),
        TribulationReward("technique", "雷系功法", "领悟雷系功法", 1, 1, 0.25),
    ]
}


# ==================== 天劫准备物品配置 ====================

TRIBULATION_PREPARATION_ITEMS: Dict[str, List[PreparationItem]] = {
    "treasure": [
        PreparationItem("法宝", "避雷珠", "可吸收部分天雷之力", "thunder_absorb", 0.15, 2, "稀有"),
        PreparationItem("法宝", "护身镜", "可反射部分天雷伤害", "thunder_reflect", 0.10, 2, "稀有"),
        PreparationItem("法宝", "金刚伞", "可抵挡天雷攻击", "damage_reduction", 0.20, 3, "史诗"),
        PreparationItem("法宝", "天雷盾", "专门抵御天雷的法宝", "thunder_resistance", 0.25, 4, "传说"),
        PreparationItem("法宝", "混元钟", "可震散天雷", "thunder_dispel", 0.30, 5, "神话"),
    ],
    "pill": [
        PreparationItem("丹药", "避雷丹", "临时提升雷抗", "thunder_resistance", 0.10, 1, "普通"),
        PreparationItem("丹药", "回春丹", "战斗中恢复气血", "health_regen", 50, 1, "普通"),
        PreparationItem("丹药", "回灵丹", "战斗中恢复灵力", "spirit_regen", 30, 1, "普通"),
        PreparationItem("丹药", "金刚丹", "临时提升防御", "defense_boost", 20, 2, "稀有"),
        PreparationItem("丹药", "渡劫丹", "专门辅助渡劫的丹药", "tribulation_boost", 0.15, 3, "史诗"),
        PreparationItem("丹药", "九转金丹", "大幅提升渡劫成功率", "tribulation_great_boost", 0.25, 5, "传说"),
    ],
    "formation": [
        PreparationItem("阵法", "聚灵阵", "聚集灵气恢复状态", "spirit_recovery", 0.20, 1, "普通"),
        PreparationItem("阵法", "防御阵", "提升防御力", "defense_formation", 0.15, 2, "稀有"),
        PreparationItem("阵法", "避雷阵", "专门抵御天雷的阵法", "thunder_formation", 0.25, 3, "史诗"),
        PreparationItem("阵法", "九宫八卦阵", "高级防御阵法", "great_defense", 0.30, 4, "传说"),
        PreparationItem("阵法", "周天星斗大阵", "传说中的防御大阵", "ultimate_defense", 0.40, 6, "神话"),
    ]
}


# ==================== 便捷函数 ====================

def get_tribulation_stage(realm_level: int) -> Optional[TribulationStage]:
    """获取指定境界的天劫阶段配置"""
    return TRIBULATION_STAGES.get(realm_level)


def get_all_tribulation_stages() -> List[Tuple[int, TribulationStage]]:
    """获取所有天劫阶段"""
    return [(level, stage) for level, stage in sorted(TRIBULATION_STAGES.items())]


def calculate_thunder_power(base_power: int, thunder_number: int, growth_rate: float) -> int:
    """
    计算雷劫威力

    Args:
        base_power: 基础威力
        thunder_number: 雷劫序号
        growth_rate: 增长系数

    Returns:
        计算后的威力
    """
    multiplier = growth_rate ** (thunder_number - 1)
    return int(base_power * multiplier)


def generate_thunder_sequence(stage: TribulationStage) -> List[ThunderStrike]:
    """
    生成雷劫序列

    Args:
        stage: 天劫阶段配置

    Returns:
        雷劫列表
    """
    thunders = []
    for i in range(stage.total_thunder):
        thunder_type = stage.thunder_types[i % len(stage.thunder_types)]
        power = calculate_thunder_power(stage.base_power, i + 1, stage.power_growth)
        name = generate_thunder_name(thunder_type, i + 1)

        thunder = ThunderStrike(
            number=i + 1,
            name=name,
            base_power=power,
            power_multiplier=stage.power_growth,
            thunder_type=thunder_type,
            description=f"第{i+1}道雷劫，威力{power}"
        )
        thunders.append(thunder)

    return thunders


def get_preparation_items(item_type: str, realm_level: int) -> List[PreparationItem]:
    """
    获取指定类型的准备物品

    Args:
        item_type: 物品类型
        realm_level: 境界等级

    Returns:
        符合条件的物品列表
    """
    items = TRIBULATION_PREPARATION_ITEMS.get(item_type, [])
    return [item for item in items if item.required_realm <= realm_level]


def calculate_tribulation_success_rate(
    base_rate: float,
    player_resistance: float,
    preparation_bonus: float,
    karma: int
) -> float:
    """
    计算渡劫成功率

    Args:
        base_rate: 基础成功率
        player_resistance: 玩家雷抗
        preparation_bonus: 准备物品加成
        karma: 业力值

    Returns:
        最终成功率
    """
    # 基础成功率
    success_rate = base_rate

    # 雷抗加成
    success_rate += player_resistance * 0.5

    # 准备物品加成
    success_rate += preparation_bonus

    # 业力影响
    karma_bonus = max(-0.2, min(0.2, karma * 0.0005))
    success_rate += karma_bonus

    # 限制在合理范围
    return max(0.05, min(0.95, success_rate))


def generate_tribulation_rewards(
    realm_level: int,
    success: bool,
    special_probability: float
) -> List[Dict[str, any]]:
    """
    生成天劫奖励

    Args:
        realm_level: 境界等级
        success: 是否成功
        special_probability: 特殊奖励概率

    Returns:
        奖励列表
    """
    rewards = []

    if not success:
        return rewards

    # 基础奖励
    for reward in TRIBULATION_REWARDS["common"]:
        if random.random() <= reward.probability:
            value = random.uniform(reward.min_value, reward.max_value)
            rewards.append({
                "type": reward.reward_type,
                "name": reward.name,
                "description": reward.description,
                "value": value
            })

    # 稀有奖励
    for reward in TRIBULATION_REWARDS["rare"]:
        if random.random() <= reward.probability * special_probability:
            value = random.uniform(reward.min_value, reward.max_value)
            rewards.append({
                "type": reward.reward_type,
                "name": reward.name,
                "description": reward.description,
                "value": value
            })

    # 传说奖励
    for reward in TRIBULATION_REWARDS["legendary"]:
        if random.random() <= reward.probability * special_probability:
            rewards.append({
                "type": reward.reward_type,
                "name": reward.name,
                "description": reward.description,
                "value": 1
            })

    return rewards


def get_tribulation_type_by_karma(karma: int) -> TribulationType:
    """根据业力获取天劫类型"""
    if karma < -300:
        return TribulationType.DEMONIC
    elif karma > 300:
        return TribulationType.ENHANCED
    else:
        return TribulationType.NORMAL


def calculate_failure_penalty(
    stage: TribulationStage,
    thunder_survived: int,
    total_thunder: int
) -> Dict[str, any]:
    """
    计算失败惩罚

    Args:
        stage: 天劫阶段
        thunder_survived: 已承受的雷劫数
        total_thunder: 总雷劫数

    Returns:
        惩罚详情
    """
    penalty = stage.failure_penalty.copy()

    # 根据渡劫进度减轻惩罚
    progress = thunder_survived / total_thunder
    if progress >= 0.8:
        # 完成80%以上，惩罚减轻
        penalty["health_loss"] *= 0.5
        penalty["exp_loss"] *= 0.5
        penalty["injury_days"] = int(penalty["injury_days"] * 0.5)
        penalty["realm_fall_probability"] *= 0.5

    return penalty
