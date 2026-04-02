"""
洞府系统配置
包含洞府等级、灵田作物、聚灵阵、护山大阵等配置
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class CaveLevel(Enum):
    """洞府等级"""
    SIMPLE = 0      # 简陋洞府
    NORMAL = 1      # 普通洞府
    SPIRITUAL = 2   # 灵气洞府
    BLESSED = 3     # 洞天福地
    IMMORTAL = 4    # 仙山洞府


class CropType(Enum):
    """作物类型"""
    HERB = "灵草"       # 灵草类
    SPIRITUAL = "灵物"   # 灵物类
    MEDICINAL = "药材"   # 药材类


class CropStage(Enum):
    """作物生长阶段"""
    SEED = "种子期"
    SPROUT = "发芽期"
    GROWTH = "生长期"
    MATURE = "成熟期"
    WITHERED = "枯萎期"


@dataclass
class CaveLevelConfig:
    """洞府等级配置"""
    level: CaveLevel
    name: str
    description: str
    base_price: int
    upgrade_price: int
    cultivation_bonus: float      # 修炼速度加成
    max_fields: int               # 最大灵田数量
    max_spirit_array_level: int   # 聚灵阵最高等级
    max_defense_level: int        # 护山大阵最高等级
    spirit_recovery: int          # 灵力恢复速度
    defense_power: int            # 基础防御力


@dataclass
class CropConfig:
    """作物配置"""
    id: str
    name: str
    description: str
    crop_type: CropType
    growth_days: int              # 生长天数
    yield_amount: int             # 产量
    sell_price: int               # 售价
    effects: Dict[str, any]       # 效果（用于炼丹）
    required_realm: int           # 所需境界
    seed_price: int               # 种子价格


@dataclass
class SpiritArrayConfig:
    """聚灵阵配置"""
    level: int
    name: str
    description: str
    upgrade_cost: int             # 升级灵石消耗
    cultivation_bonus: float      # 修炼速度加成
    spirit_gathering: int         # 灵气聚集量


@dataclass
class DefenseArrayConfig:
    """护山大阵配置"""
    level: int
    name: str
    description: str
    upgrade_cost: int             # 升级灵石消耗
    defense_power: int            # 防御力
    attack_power: int             # 反击攻击力
    enemy_repel: float            # 敌人驱散概率


@dataclass
class CaveLocation:
    """洞府地点配置"""
    id: str
    name: str
    description: str
    min_realm: int                # 最低境界要求
    max_cave_level: CaveLevel     # 最高可建造洞府等级
    price_multiplier: float       # 价格倍率
    special_bonus: Dict[str, float]  # 特殊加成


# ==================== 洞府等级配置 ====================

CAVE_LEVELS: Dict[CaveLevel, CaveLevelConfig] = {
    CaveLevel.SIMPLE: CaveLevelConfig(
        level=CaveLevel.SIMPLE,
        name="简陋洞府",
        description="一处简陋的洞府，勉强可以居住修炼",
        base_price=1000,
        upgrade_price=5000,
        cultivation_bonus=0.1,
        max_fields=2,
        max_spirit_array_level=2,
        max_defense_level=1,
        spirit_recovery=5,
        defense_power=50
    ),
    CaveLevel.NORMAL: CaveLevelConfig(
        level=CaveLevel.NORMAL,
        name="普通洞府",
        description="一处普通的洞府，灵气较为充沛",
        base_price=5000,
        upgrade_price=20000,
        cultivation_bonus=0.2,
        max_fields=4,
        max_spirit_array_level=4,
        max_defense_level=2,
        spirit_recovery=10,
        defense_power=100
    ),
    CaveLevel.SPIRITUAL: CaveLevelConfig(
        level=CaveLevel.SPIRITUAL,
        name="灵气洞府",
        description="灵气浓郁的洞府，修炼事半功倍",
        base_price=20000,
        upgrade_price=100000,
        cultivation_bonus=0.4,
        max_fields=6,
        max_spirit_array_level=6,
        max_defense_level=3,
        spirit_recovery=20,
        defense_power=200
    ),
    CaveLevel.BLESSED: CaveLevelConfig(
        level=CaveLevel.BLESSED,
        name="洞天福地",
        description="传说中的洞天福地，天地灵气汇聚",
        base_price=100000,
        upgrade_price=500000,
        cultivation_bonus=0.7,
        max_fields=9,
        max_spirit_array_level=9,
        max_defense_level=4,
        spirit_recovery=40,
        defense_power=400
    ),
    CaveLevel.IMMORTAL: CaveLevelConfig(
        level=CaveLevel.IMMORTAL,
        name="仙山洞府",
        description="仙人遗留的洞府，蕴含无穷玄妙",
        base_price=500000,
        upgrade_price=0,  # 无法升级
        cultivation_bonus=1.0,
        max_fields=12,
        max_spirit_array_level=10,
        max_defense_level=5,
        spirit_recovery=80,
        defense_power=800
    ),
}


# ==================== 灵田作物配置 ====================

CROPS_DB: Dict[str, CropConfig] = {
    # ===== 灵草类 =====
    "spirit_grass": CropConfig(
        id="spirit_grass",
        name="灵草",
        description="最基础的灵草，蕴含微弱灵气",
        crop_type=CropType.HERB,
        growth_days=3,
        yield_amount=5,
        sell_price=10,
        effects={"spirit_power": 5},
        required_realm=0,
        seed_price=5
    ),
    "moon_grass": CropConfig(
        id="moon_grass",
        name="月灵草",
        description="吸收月华生长的灵草",
        crop_type=CropType.HERB,
        growth_days=5,
        yield_amount=3,
        sell_price=30,
        effects={"spirit_power": 15, "night_bonus": 0.1},
        required_realm=1,
        seed_price=15
    ),
    "sun_flower": CropConfig(
        id="sun_flower",
        name="日阳花",
        description="吸收日精生长的灵花",
        crop_type=CropType.HERB,
        growth_days=5,
        yield_amount=3,
        sell_price=30,
        effects={"spirit_power": 15, "day_bonus": 0.1},
        required_realm=1,
        seed_price=15
    ),
    "thousand_year_herb": CropConfig(
        id="thousand_year_herb",
        name="千年灵参",
        description="生长千年的灵参，药效显著",
        crop_type=CropType.HERB,
        growth_days=30,
        yield_amount=1,
        sell_price=500,
        effects={"spirit_power": 100, "max_health": 20},
        required_realm=3,
        seed_price=200
    ),
    
    # ===== 灵物类 =====
    "spirit_mushroom": CropConfig(
        id="spirit_mushroom",
        name="灵芝",
        description="生长在灵气充沛之地的菌类",
        crop_type=CropType.SPIRITUAL,
        growth_days=7,
        yield_amount=2,
        sell_price=50,
        effects={"spirit_power": 25, "heal": 20},
        required_realm=2,
        seed_price=25
    ),
    "jade_bamboo": CropConfig(
        id="jade_bamboo",
        name="金雷竹",
        description="蕴含雷电之力的灵竹",
        crop_type=CropType.SPIRITUAL,
        growth_days=15,
        yield_amount=1,
        sell_price=200,
        effects={"spirit_power": 50, "thunder_damage": 10},
        required_realm=3,
        seed_price=100
    ),
    "ice_lotus": CropConfig(
        id="ice_lotus",
        name="冰魄雪莲",
        description="极寒之地生长的雪莲",
        crop_type=CropType.SPIRITUAL,
        growth_days=20,
        yield_amount=1,
        sell_price=400,
        effects={"spirit_power": 80, "ice_resistance": 0.2},
        required_realm=4,
        seed_price=200
    ),
    "fire_orchid": CropConfig(
        id="fire_orchid",
        name="火灵兰",
        description="地火旁生长的兰花",
        crop_type=CropType.SPIRITUAL,
        growth_days=20,
        yield_amount=1,
        sell_price=400,
        effects={"spirit_power": 80, "fire_damage": 15},
        required_realm=4,
        seed_price=200
    ),
    
    # ===== 药材类 =====
    "healing_herb": CropConfig(
        id="healing_herb",
        name="疗伤草",
        description="常见的疗伤药材",
        crop_type=CropType.MEDICINAL,
        growth_days=4,
        yield_amount=4,
        sell_price=20,
        effects={"heal": 30},
        required_realm=0,
        seed_price=10
    ),
    "detox_grass": CropConfig(
        id="detox_grass",
        name="解毒草",
        description="可解百毒的药草",
        crop_type=CropType.MEDICINAL,
        growth_days=6,
        yield_amount=3,
        sell_price=40,
        effects={"detox": True},
        required_realm=1,
        seed_price=20
    ),
    "ginseng": CropConfig(
        id="ginseng",
        name="人参",
        description="大补元气的药材",
        crop_type=CropType.MEDICINAL,
        growth_days=10,
        yield_amount=2,
        sell_price=100,
        effects={"max_health": 10, "regeneration": 2},
        required_realm=2,
        seed_price=50
    ),
    "dragon_blood_herb": CropConfig(
        id="dragon_blood_herb",
        name="龙血草",
        description="沾染龙血生长的珍稀药材",
        crop_type=CropType.MEDICINAL,
        growth_days=60,
        yield_amount=1,
        sell_price=2000,
        effects={"max_health": 50, "regeneration": 10, "strength": 5},
        required_realm=5,
        seed_price=1000
    ),
}


# ==================== 聚灵阵配置 ====================

SPIRIT_ARRAY_LEVELS: Dict[int, SpiritArrayConfig] = {
    0: SpiritArrayConfig(
        level=0,
        name="无聚灵阵",
        description="未布置聚灵阵",
        upgrade_cost=0,
        cultivation_bonus=0.0,
        spirit_gathering=0
    ),
    1: SpiritArrayConfig(
        level=1,
        name="初级聚灵阵",
        description="基础的聚灵阵法，可聚集少量灵气",
        upgrade_cost=1000,
        cultivation_bonus=0.1,
        spirit_gathering=10
    ),
    2: SpiritArrayConfig(
        level=2,
        name="中级聚灵阵",
        description="较为完善的聚灵阵法",
        upgrade_cost=3000,
        cultivation_bonus=0.2,
        spirit_gathering=25
    ),
    3: SpiritArrayConfig(
        level=3,
        name="高级聚灵阵",
        description="高级的聚灵阵法，灵气充沛",
        upgrade_cost=8000,
        cultivation_bonus=0.35,
        spirit_gathering=50
    ),
    4: SpiritArrayConfig(
        level=4,
        name="玄级聚灵阵",
        description="玄奥的聚灵阵法",
        upgrade_cost=20000,
        cultivation_bonus=0.5,
        spirit_gathering=100
    ),
    5: SpiritArrayConfig(
        level=5,
        name="地级聚灵阵",
        description="地级聚灵阵，灵气如潮",
        upgrade_cost=50000,
        cultivation_bonus=0.7,
        spirit_gathering=200
    ),
    6: SpiritArrayConfig(
        level=6,
        name="天级聚灵阵",
        description="天级聚灵阵，天地灵气汇聚",
        upgrade_cost=100000,
        cultivation_bonus=0.9,
        spirit_gathering=400
    ),
    7: SpiritArrayConfig(
        level=7,
        name="仙级聚灵阵",
        description="仙级聚灵阵，灵气化液",
        upgrade_cost=300000,
        cultivation_bonus=1.2,
        spirit_gathering=800
    ),
    8: SpiritArrayConfig(
        level=8,
        name="神级聚灵阵",
        description="神级聚灵阵，灵气化形",
        upgrade_cost=800000,
        cultivation_bonus=1.5,
        spirit_gathering=1500
    ),
    9: SpiritArrayConfig(
        level=9,
        name="圣级聚灵阵",
        description="圣级聚灵阵，灵气如海",
        upgrade_cost=2000000,
        cultivation_bonus=2.0,
        spirit_gathering=3000
    ),
    10: SpiritArrayConfig(
        level=10,
        name="混沌聚灵阵",
        description="传说中的混沌聚灵阵，可聚混沌之气",
        upgrade_cost=5000000,
        cultivation_bonus=3.0,
        spirit_gathering=8000
    ),
}


# ==================== 护山大阵配置 ====================

DEFENSE_ARRAY_LEVELS: Dict[int, DefenseArrayConfig] = {
    0: DefenseArrayConfig(
        level=0,
        name="无护山大阵",
        description="未布置护山大阵",
        upgrade_cost=0,
        defense_power=0,
        attack_power=0,
        enemy_repel=0.0
    ),
    1: DefenseArrayConfig(
        level=1,
        name="基础护阵",
        description="简单的防御阵法",
        upgrade_cost=2000,
        defense_power=100,
        attack_power=20,
        enemy_repel=0.1
    ),
    2: DefenseArrayConfig(
        level=2,
        name="五行护阵",
        description="以五行为基的护山大阵",
        upgrade_cost=8000,
        defense_power=300,
        attack_power=50,
        enemy_repel=0.2
    ),
    3: DefenseArrayConfig(
        level=3,
        name="八卦迷阵",
        description="八卦迷踪阵，困敌于无形",
        upgrade_cost=30000,
        defense_power=800,
        attack_power=150,
        enemy_repel=0.35
    ),
    4: DefenseArrayConfig(
        level=4,
        name="九天雷阵",
        description="引九天神雷的杀阵",
        upgrade_cost=100000,
        defense_power=2000,
        attack_power=500,
        enemy_repel=0.5
    ),
    5: DefenseArrayConfig(
        level=5,
        name="周天星斗大阵",
        description="传说中的周天星斗大阵",
        upgrade_cost=500000,
        defense_power=5000,
        attack_power=1500,
        enemy_repel=0.7
    ),
}


# ==================== 洞府地点配置 ====================

CAVE_LOCATIONS: Dict[str, CaveLocation] = {
    "newbie_village": CaveLocation(
        id="newbie_village",
        name="新手村",
        description="凡人居住的村落，灵气稀薄",
        min_realm=0,
        max_cave_level=CaveLevel.NORMAL,
        price_multiplier=0.8,
        special_bonus={}
    ),
    "colorful_cloud_mountain": CaveLocation(
        id="colorful_cloud_mountain",
        name="彩霞山",
        description="七玄门所在之地，灵气较为充沛",
        min_realm=0,
        max_cave_level=CaveLevel.SPIRITUAL,
        price_multiplier=1.0,
        special_bonus={"cultivation_bonus": 0.05}
    ),
    "yellow_maple_valley": CaveLocation(
        id="yellow_maple_valley",
        name="黄枫谷",
        description="越国七大派之一，灵气浓郁",
        min_realm=1,
        max_cave_level=CaveLevel.BLESSED,
        price_multiplier=1.5,
        special_bonus={"cultivation_bonus": 0.1}
    ),
    "ten_thousand_beast_mountain": CaveLocation(
        id="ten_thousand_beast_mountain",
        name="万兽山脉",
        description="妖兽横行的山脉，危险与机遇并存",
        min_realm=2,
        max_cave_level=CaveLevel.BLESSED,
        price_multiplier=1.2,
        special_bonus={"defense_bonus": 0.1}
    ),
    "overseas": CaveLocation(
        id="overseas",
        name="海外",
        description="海外修仙圣地，灵气充沛",
        min_realm=3,
        max_cave_level=CaveLevel.IMMORTAL,
        price_multiplier=2.0,
        special_bonus={"cultivation_bonus": 0.15, "spirit_recovery": 0.1}
    ),
    "spirit_world": CaveLocation(
        id="spirit_world",
        name="灵界",
        description="人界之上的界面，灵气更加充沛",
        min_realm=5,
        max_cave_level=CaveLevel.IMMORTAL,
        price_multiplier=3.0,
        special_bonus={"cultivation_bonus": 0.2, "spirit_recovery": 0.2}
    ),
}


# ==================== 便捷函数 ====================

def get_cave_level_config(level: CaveLevel) -> Optional[CaveLevelConfig]:
    """获取洞府等级配置"""
    return CAVE_LEVELS.get(level)


def get_crop_config(crop_id: str) -> Optional[CropConfig]:
    """获取作物配置"""
    return CROPS_DB.get(crop_id)


def get_spirit_array_config(level: int) -> Optional[SpiritArrayConfig]:
    """获取聚灵阵配置"""
    return SPIRIT_ARRAY_LEVELS.get(level)


def get_defense_array_config(level: int) -> Optional[DefenseArrayConfig]:
    """获取护山大阵配置"""
    return DEFENSE_ARRAY_LEVELS.get(level)


def get_cave_location(location_id: str) -> Optional[CaveLocation]:
    """获取洞府地点配置"""
    return CAVE_LOCATIONS.get(location_id)


def get_available_crops(realm_level: int) -> List[CropConfig]:
    """获取指定境界可种植的作物"""
    return [crop for crop in CROPS_DB.values() if crop.required_realm <= realm_level]


def get_crops_by_type(crop_type: CropType) -> List[CropConfig]:
    """获取指定类型的作物"""
    return [crop for crop in CROPS_DB.values() if crop.crop_type == crop_type]


def calculate_cave_price(base_price: int, location_multiplier: float, level: CaveLevel) -> int:
    """计算洞府价格"""
    level_multiplier = 1.0 + level.value * 0.5
    return int(base_price * location_multiplier * level_multiplier)


def get_next_cave_level(current: CaveLevel) -> Optional[CaveLevel]:
    """获取下一个洞府等级"""
    levels = list(CaveLevel)
    current_index = levels.index(current)
    if current_index < len(levels) - 1:
        return levels[current_index + 1]
    return None


def calculate_total_cultivation_bonus(
    cave_level: CaveLevel,
    spirit_array_level: int,
    location_id: str
) -> float:
    """计算总修炼速度加成"""
    cave_config = get_cave_level_config(cave_level)
    spirit_config = get_spirit_array_config(spirit_array_level)
    location = get_cave_location(location_id)
    
    total = 0.0
    if cave_config:
        total += cave_config.cultivation_bonus
    if spirit_config:
        total += spirit_config.cultivation_bonus
    if location and "cultivation_bonus" in location.special_bonus:
        total += location.special_bonus["cultivation_bonus"]
    
    return total
