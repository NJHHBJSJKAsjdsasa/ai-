"""
炼丹/炼器系统配置
包含丹方、炼器图纸、材料类型、品质等级等配置
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class MaterialType(Enum):
    """材料类型"""
    HERB = "草药"           # 草药
    ORE = "矿石"            # 矿石
    BEAST_MATERIAL = "妖兽材料"  # 妖兽材料
    SPIRITUAL_ITEM = "灵物"      # 天地灵物


class PillType(Enum):
    """丹药类型"""
    RECOVERY = "恢复"       # 恢复类（回血回蓝）
    BREAKTHROUGH = "突破"   # 突破类（境界突破辅助）
    BUFF = "增益"           # 增益类（临时属性提升）
    PERMANENT = "永久"      # 永久提升类


class EquipmentType(Enum):
    """装备类型"""
    WEAPON = "武器"         # 武器
    ARMOR = "护甲"          # 护甲
    ACCESSORY = "饰品"      # 饰品
    TREASURE = "法宝"       # 法宝


class ItemQuality(Enum):
    """物品品质"""
    DEFECTIVE = "次品"      # 次品
    COMMON = "普通"         # 普通
    UNCOMMON = "优秀"       # 优秀
    RARE = "稀有"           # 稀有
    EPIC = "史诗"           # 史诗
    LEGENDARY = "传说"      # 传说
    MYTHIC = "神话"         # 神话


class ItemRarity(Enum):
    """物品稀有度（用于材料）"""
    COMMON = "普通"
    UNCOMMON = "优秀"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"


@dataclass
class Material:
    """材料数据类"""
    name: str                           # 材料名称
    description: str                    # 材料描述
    material_type: MaterialType         # 材料类型
    rarity: ItemRarity                  # 稀有度
    level: int = 1                      # 等级
    effects: Dict[str, any] = field(default_factory=dict)  # 材料效果
    value: int = 10                     # 价值
    source: str = ""                    # 来源描述


@dataclass
class Recipe:
    """丹方数据类"""
    id: str                             # 丹方ID
    name: str                           # 丹方名称
    description: str                    # 丹方描述
    pill_type: PillType                 # 丹药类型
    rarity: ItemRarity                  # 稀有度
    realm_required: int                 # 所需境界等级
    materials: Dict[str, int]           # 所需材料 {材料名: 数量}
    effects: Dict[str, any]             # 丹药效果
    base_success_rate: float = 0.5      # 基础成功率
    quality_multipliers: Dict[str, float] = field(default_factory=dict)  # 品质加成


@dataclass
class Blueprint:
    """炼器图纸数据类"""
    id: str                             # 图纸ID
    name: str                           # 图纸名称
    description: str                    # 图纸描述
    equipment_type: EquipmentType       # 装备类型
    rarity: ItemRarity                  # 稀有度
    realm_required: int                 # 所需境界等级
    materials: Dict[str, int]           # 所需材料 {材料名: 数量}
    base_attributes: Dict[str, int]     # 基础属性
    special_effects: List[str]          # 特殊效果
    base_success_rate: float = 0.5      # 基础成功率


# ==================== 材料数据库 ====================

MATERIALS_DB: Dict[str, Material] = {
    # ===== 草药 =====
    "灵芝草": Material(
        name="灵芝草",
        description="生长在山林中的普通草药，有微弱的恢复效果",
        material_type=MaterialType.HERB,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"heal": 10},
        value=10,
        source="山林采集"
    ),
    "百年人参": Material(
        name="百年人参",
        description="生长百年的野山参，药效显著",
        material_type=MaterialType.HERB,
        rarity=ItemRarity.UNCOMMON,
        level=2,
        effects={"heal": 30, "spirit_power": 20},
        value=50,
        source="深山采集"
    ),
    "千年灵芝": Material(
        name="千年灵芝",
        description="千年难遇的灵草，蕴含浓郁灵气",
        material_type=MaterialType.HERB,
        rarity=ItemRarity.RARE,
        level=3,
        effects={"heal": 80, "spirit_power": 50, "breakthrough_boost": 0.1},
        value=200,
        source="秘境采集"
    ),
    "九叶剑草": Material(
        name="九叶剑草",
        description="传说中的剑形灵草，蕴含剑意",
        material_type=MaterialType.HERB,
        rarity=ItemRarity.EPIC,
        level=5,
        effects={"attack_boost": 20, "crit_rate": 0.05},
        value=500,
        source="剑冢采集"
    ),
    "龙血草": Material(
        name="龙血草",
        description="沾染龙血生长的灵草，极为珍贵",
        material_type=MaterialType.HERB,
        rarity=ItemRarity.LEGENDARY,
        level=6,
        effects={"max_health": 100, "regeneration": 5},
        value=2000,
        source="龙脉之地"
    ),

    # ===== 矿石 =====
    "铁矿石": Material(
        name="铁矿石",
        description="普通的铁矿石，可提炼精铁",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"defense": 2},
        value=15,
        source="矿洞采集"
    ),
    "铜矿石": Material(
        name="铜矿石",
        description="蕴含微弱灵气的铜矿",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"spirit_conductivity": 5},
        value=15,
        source="矿洞采集"
    ),
    "秘银": Material(
        name="秘银",
        description="珍贵的魔法金属，灵力传导性极佳",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.UNCOMMON,
        level=2,
        effects={"spirit_conductivity": 20, "speed": 5},
        value=80,
        source="深层矿脉"
    ),
    "玄铁": Material(
        name="玄铁",
        description="坚硬无比的稀有金属",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.RARE,
        level=3,
        effects={"defense": 15, "durability": 50},
        value=150,
        source="深层矿脉"
    ),
    "星辰铁": Material(
        name="星辰铁",
        description="陨落星辰中提炼的金属，蕴含星力",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.EPIC,
        level=5,
        effects={"attack": 25, "spirit_power": 30},
        value=600,
        source="陨石采集"
    ),
    "万年寒铁": Material(
        name="万年寒铁",
        description="极寒之地孕育的金属，寒气逼人",
        material_type=MaterialType.ORE,
        rarity=ItemRarity.LEGENDARY,
        level=6,
        effects={"attack": 40, "ice_damage": 20},
        value=2500,
        source="极寒之地"
    ),

    # ===== 妖兽材料 =====
    "妖兽皮毛": Material(
        name="妖兽皮毛",
        description="普通妖兽的皮毛，质地坚韧",
        material_type=MaterialType.BEAST_MATERIAL,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"defense": 3},
        value=20,
        source="妖兽掉落"
    ),
    "妖兽骨": Material(
        name="妖兽骨",
        description="妖兽的骨骼，可用于炼制骨器",
        material_type=MaterialType.BEAST_MATERIAL,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"attack": 2},
        value=25,
        source="妖兽掉落"
    ),
    "妖兽内丹": Material(
        name="妖兽内丹",
        description="妖兽体内凝结的内丹，蕴含妖力",
        material_type=MaterialType.BEAST_MATERIAL,
        rarity=ItemRarity.RARE,
        level=3,
        effects={"spirit_power": 40, "cultivation_speed": 0.1},
        value=300,
        source="妖兽掉落"
    ),
    "妖兽精血": Material(
        name="妖兽精血",
        description="妖兽的精血，蕴含强大生命力",
        material_type=MaterialType.BEAST_MATERIAL,
        rarity=ItemRarity.UNCOMMON,
        level=2,
        effects={"max_health": 30, "regeneration": 2},
        value=100,
        source="妖兽掉落"
    ),
    "龙鳞": Material(
        name="龙鳞",
        description="真龙脱落的鳞片，坚不可摧",
        material_type=MaterialType.BEAST_MATERIAL,
        rarity=ItemRarity.LEGENDARY,
        level=7,
        effects={"defense": 50, "fire_resistance": 0.3},
        value=5000,
        source="龙族相关"
    ),

    # ===== 天地灵物 =====
    "灵泉水": Material(
        name="灵泉水",
        description="蕴含灵气的泉水",
        material_type=MaterialType.SPIRITUAL_ITEM,
        rarity=ItemRarity.COMMON,
        level=1,
        effects={"spirit_power": 10},
        value=20,
        source="灵泉采集"
    ),
    "地火精华": Material(
        name="地火精华",
        description="地底火脉凝聚的精华",
        material_type=MaterialType.SPIRITUAL_ITEM,
        rarity=ItemRarity.RARE,
        level=4,
        effects={"fire_damage": 15, "alchemy_bonus": 0.1},
        value=400,
        source="地火采集"
    ),
    "万年灵乳": Material(
        name="万年灵乳",
        description="天地灵物，可瞬间恢复全部法力",
        material_type=MaterialType.SPIRITUAL_ITEM,
        rarity=ItemRarity.LEGENDARY,
        level=6,
        effects={"full_restore": True, "max_spirit_power": 50},
        value=3000,
        source="洞天福地"
    ),
}


# ==================== 丹方数据库 ====================

RECIPES_DB: Dict[str, Recipe] = {
    # ===== 恢复类丹药 =====
    "回气丹": Recipe(
        id="recipe_001",
        name="回气丹",
        description="基础恢复丹药，可恢复少量法力",
        pill_type=PillType.RECOVERY,
        rarity=ItemRarity.COMMON,
        realm_required=0,
        materials={"灵芝草": 2, "灵泉水": 1},
        effects={"restore_spirit_power": 30},
        base_success_rate=0.8,
        quality_multipliers={"次品": 0.5, "普通": 1.0, "优秀": 1.5, "稀有": 2.0}
    ),
    "回春丹": Recipe(
        id="recipe_002",
        name="回春丹",
        description="恢复伤势的丹药",
        pill_type=PillType.RECOVERY,
        rarity=ItemRarity.COMMON,
        realm_required=0,
        materials={"灵芝草": 3, "妖兽精血": 1},
        effects={"restore_health": 50},
        base_success_rate=0.75,
        quality_multipliers={"次品": 0.5, "普通": 1.0, "优秀": 1.5, "稀有": 2.0}
    ),
    "大还丹": Recipe(
        id="recipe_003",
        name="大还丹",
        description="高级恢复丹药，可同时恢复生命和法力",
        pill_type=PillType.RECOVERY,
        rarity=ItemRarity.UNCOMMON,
        realm_required=1,
        materials={"百年人参": 2, "妖兽精血": 2, "灵泉水": 2},
        effects={"restore_health": 100, "restore_spirit_power": 80},
        base_success_rate=0.7,
        quality_multipliers={"次品": 0.5, "普通": 1.0, "优秀": 1.5, "稀有": 2.0, "史诗": 2.5}
    ),

    # ===== 突破类丹药 =====
    "筑基丹": Recipe(
        id="recipe_004",
        name="筑基丹",
        description="练气期突破筑基期必备丹药",
        pill_type=PillType.BREAKTHROUGH,
        rarity=ItemRarity.RARE,
        realm_required=0,
        materials={"百年人参": 3, "妖兽内丹": 1, "灵泉水": 3},
        effects={"breakthrough_boost": 0.3, "realm": "筑基期"},
        base_success_rate=0.6,
        quality_multipliers={"次品": 0.3, "普通": 0.8, "优秀": 1.0, "稀有": 1.3, "史诗": 1.6}
    ),
    "结金丹": Recipe(
        id="recipe_005",
        name="结金丹",
        description="辅助凝结金丹的珍贵丹药",
        pill_type=PillType.BREAKTHROUGH,
        rarity=ItemRarity.EPIC,
        realm_required=2,
        materials={"千年灵芝": 2, "妖兽内丹": 3, "地火精华": 1},
        effects={"breakthrough_boost": 0.4, "realm": "金丹期", "jade_quality": "提升"},
        base_success_rate=0.5,
        quality_multipliers={"次品": 0.2, "普通": 0.6, "优秀": 0.9, "稀有": 1.2, "史诗": 1.5, "传说": 1.8}
    ),

    # ===== 增益类丹药 =====
    "增元丹": Recipe(
        id="recipe_006",
        name="增元丹",
        description="临时提升修为的丹药",
        pill_type=PillType.BUFF,
        rarity=ItemRarity.UNCOMMON,
        realm_required=1,
        materials={"百年人参": 2, "妖兽内丹": 1},
        effects={"exp_boost": 0.2, "duration": 3600},
        base_success_rate=0.65,
        quality_multipliers={"次品": 0.5, "普通": 1.0, "优秀": 1.5, "稀有": 2.0}
    ),
    "狂暴丹": Recipe(
        id="recipe_007",
        name="狂暴丹",
        description="短时间内大幅提升攻击力",
        pill_type=PillType.BUFF,
        rarity=ItemRarity.RARE,
        realm_required=2,
        materials={"妖兽精血": 3, "妖兽内丹": 2, "九叶剑草": 1},
        effects={"attack_boost": 50, "duration": 600, "side_effect": "虚弱"},
        base_success_rate=0.55,
        quality_multipliers={"次品": 0.4, "普通": 0.8, "优秀": 1.2, "稀有": 1.6, "史诗": 2.0}
    ),

    # ===== 永久提升类丹药 =====
    "洗髓丹": Recipe(
        id="recipe_008",
        name="洗髓丹",
        description="洗髓伐骨，永久提升少量资质",
        pill_type=PillType.PERMANENT,
        rarity=ItemRarity.EPIC,
        realm_required=3,
        materials={"千年灵芝": 3, "万年灵乳": 1, "龙血草": 1},
        effects={"max_health": 20, "max_spirit_power": 15},
        base_success_rate=0.4,
        quality_multipliers={"次品": 0.3, "普通": 0.7, "优秀": 1.0, "稀有": 1.3, "史诗": 1.6}
    ),
}


# ==================== 炼器图纸数据库 ====================

BLUEPRINTS_DB: Dict[str, Blueprint] = {
    # ===== 武器 =====
    "精铁剑": Blueprint(
        id="blueprint_001",
        name="精铁剑",
        description="用精铁锻造的普通长剑",
        equipment_type=EquipmentType.WEAPON,
        rarity=ItemRarity.COMMON,
        realm_required=0,
        materials={"铁矿石": 3, "铜矿石": 2},
        base_attributes={"attack": 10, "durability": 100},
        special_effects=[],
        base_success_rate=0.85
    ),
    "秘银剑": Blueprint(
        id="blueprint_002",
        name="秘银剑",
        description="秘银锻造的灵剑，灵力传导性佳",
        equipment_type=EquipmentType.WEAPON,
        rarity=ItemRarity.UNCOMMON,
        realm_required=1,
        materials={"秘银": 3, "铁矿石": 2, "妖兽骨": 1},
        base_attributes={"attack": 25, "spirit_power": 15, "durability": 150},
        special_effects=["灵力传导"],
        base_success_rate=0.75
    ),
    "玄铁重剑": Blueprint(
        id="blueprint_003",
        name="玄铁重剑",
        description="玄铁铸造的重剑，威力巨大",
        equipment_type=EquipmentType.WEAPON,
        rarity=ItemRarity.RARE,
        realm_required=2,
        materials={"玄铁": 4, "秘银": 2, "妖兽骨": 2},
        base_attributes={"attack": 50, "defense": 10, "durability": 300},
        special_effects=["重击", "破甲"],
        base_success_rate=0.65
    ),
    "星辰剑": Blueprint(
        id="blueprint_004",
        name="星辰剑",
        description="以星辰铁为主材料炼制的飞剑",
        equipment_type=EquipmentType.WEAPON,
        rarity=ItemRarity.EPIC,
        realm_required=4,
        materials={"星辰铁": 3, "玄铁": 2, "妖兽内丹": 2, "地火精华": 1},
        base_attributes={"attack": 80, "spirit_power": 50, "speed": 20, "durability": 500},
        special_effects=["星光斩", "飞剑术", "星辰之力"],
        base_success_rate=0.5
    ),

    # ===== 护甲 =====
    "皮甲": Blueprint(
        id="blueprint_005",
        name="皮甲",
        description="妖兽皮毛制作的护甲",
        equipment_type=EquipmentType.ARMOR,
        rarity=ItemRarity.COMMON,
        realm_required=0,
        materials={"妖兽皮毛": 3, "铁矿石": 1},
        base_attributes={"defense": 8, "durability": 80},
        special_effects=[],
        base_success_rate=0.8
    ),
    "玄铁甲": Blueprint(
        id="blueprint_006",
        name="玄铁甲",
        description="玄铁打造的坚固护甲",
        equipment_type=EquipmentType.ARMOR,
        rarity=ItemRarity.RARE,
        realm_required=2,
        materials={"玄铁": 5, "秘银": 2, "妖兽皮毛": 2},
        base_attributes={"defense": 40, "max_health": 50, "durability": 400},
        special_effects=["坚固", "伤害减免"],
        base_success_rate=0.6
    ),
    "龙鳞甲": Blueprint(
        id="blueprint_007",
        name="龙鳞甲",
        description="以龙鳞为主材料炼制的宝甲",
        equipment_type=EquipmentType.ARMOR,
        rarity=ItemRarity.LEGENDARY,
        realm_required=5,
        materials={"龙鳞": 3, "万年寒铁": 2, "妖兽内丹": 3},
        base_attributes={"defense": 100, "max_health": 200, "fire_resistance": 0.5, "durability": 1000},
        special_effects=["龙威", "火焰免疫", "自动修复"],
        base_success_rate=0.35
    ),

    # ===== 饰品 =====
    "灵玉佩": Blueprint(
        id="blueprint_008",
        name="灵玉佩",
        description="蕴含灵气的玉佩",
        equipment_type=EquipmentType.ACCESSORY,
        rarity=ItemRarity.UNCOMMON,
        realm_required=1,
        materials={"秘银": 2, "灵泉水": 2, "妖兽精血": 1},
        base_attributes={"spirit_power": 20, "max_spirit_power": 30},
        special_effects=["灵气恢复"],
        base_success_rate=0.7
    ),
    "储物戒指": Blueprint(
        id="blueprint_009",
        name="储物戒指",
        description="内含储物空间的戒指",
        equipment_type=EquipmentType.ACCESSORY,
        rarity=ItemRarity.RARE,
        realm_required=2,
        materials={"秘银": 3, "玄铁": 2, "妖兽内丹": 1, "地火精华": 1},
        base_attributes={"storage_space": 20},
        special_effects=["储物空间"],
        base_success_rate=0.55
    ),

    # ===== 法宝 =====
    "火灵珠": Blueprint(
        id="blueprint_010",
        name="火灵珠",
        description="蕴含火灵之力的宝珠",
        equipment_type=EquipmentType.TREASURE,
        rarity=ItemRarity.EPIC,
        realm_required=3,
        materials={"地火精华": 3, "星辰铁": 2, "妖兽内丹": 2},
        base_attributes={"fire_damage": 30, "spirit_power": 40},
        special_effects=["火球术", "火焰护盾", "火灵亲和"],
        base_success_rate=0.45
    ),
    "寒冰镜": Blueprint(
        id="blueprint_011",
        name="寒冰镜",
        description="万年寒铁炼制的宝镜",
        equipment_type=EquipmentType.TREASURE,
        rarity=ItemRarity.LEGENDARY,
        realm_required=5,
        materials={"万年寒铁": 4, "星辰铁": 2, "万年灵乳": 1, "龙鳞": 1},
        base_attributes={"ice_damage": 50, "defense": 30, "spirit_power": 60},
        special_effects=["冰冻术", "寒冰护盾", "寒气逼人", "镜面反射"],
        base_success_rate=0.3
    ),
}


# ==================== 品质相关配置 ====================

QUALITY_SUCCESS_BONUS = {
    # 材料品质对成功率的加成
    ItemRarity.COMMON: 0.0,
    ItemRarity.UNCOMMON: 0.05,
    ItemRarity.RARE: 0.1,
    ItemRarity.EPIC: 0.15,
    ItemRarity.LEGENDARY: 0.2,
    ItemRarity.MYTHIC: 0.3,
}

QUALITY_RESULT_DISTRIBUTION = {
    # 根据成功率决定产出品质的概率分布
    "high": {  # 高成功率 (>0.7)
        ItemQuality.DEFECTIVE: 0.05,
        ItemQuality.COMMON: 0.25,
        ItemQuality.UNCOMMON: 0.35,
        ItemQuality.RARE: 0.25,
        ItemQuality.EPIC: 0.08,
        ItemQuality.LEGENDARY: 0.02,
    },
    "medium": {  # 中等成功率 (0.4-0.7)
        ItemQuality.DEFECTIVE: 0.15,
        ItemQuality.COMMON: 0.30,
        ItemQuality.UNCOMMON: 0.30,
        ItemQuality.RARE: 0.18,
        ItemQuality.EPIC: 0.06,
        ItemQuality.LEGENDARY: 0.01,
    },
    "low": {  # 低成功率 (<0.4)
        ItemQuality.DEFECTIVE: 0.30,
        ItemQuality.COMMON: 0.35,
        ItemQuality.UNCOMMON: 0.20,
        ItemQuality.RARE: 0.10,
        ItemQuality.EPIC: 0.04,
        ItemQuality.LEGENDARY: 0.01,
    }
}


# ==================== 便捷函数 ====================

def get_material(name: str) -> Optional[Material]:
    """获取材料信息"""
    return MATERIALS_DB.get(name)


def get_recipe(recipe_id: str) -> Optional[Recipe]:
    """获取丹方信息"""
    return RECIPES_DB.get(recipe_id)


def get_blueprint(blueprint_id: str) -> Optional[Blueprint]:
    """获取炼器图纸信息"""
    return BLUEPRINTS_DB.get(blueprint_id)


def get_recipes_by_type(pill_type: PillType) -> List[Recipe]:
    """获取指定类型的丹方"""
    return [r for r in RECIPES_DB.values() if r.pill_type == pill_type]


def get_recipes_by_rarity(rarity: ItemRarity) -> List[Recipe]:
    """获取指定稀有度的丹方"""
    return [r for r in RECIPES_DB.values() if r.rarity == rarity]


def get_blueprints_by_type(equipment_type: EquipmentType) -> List[Blueprint]:
    """获取指定类型的炼器图纸"""
    return [b for b in BLUEPRINTS_DB.values() if b.equipment_type == equipment_type]


def get_materials_by_type(material_type: MaterialType) -> List[Material]:
    """获取指定类型的材料"""
    return [m for m in MATERIALS_DB.values() if m.material_type == material_type]


def calculate_quality(success_rate: float) -> ItemQuality:
    """
    根据成功率计算产出品质

    Args:
        success_rate: 最终成功率

    Returns:
        产出的品质
    """
    if success_rate > 0.7:
        distribution = QUALITY_RESULT_DISTRIBUTION["high"]
    elif success_rate > 0.4:
        distribution = QUALITY_RESULT_DISTRIBUTION["medium"]
    else:
        distribution = QUALITY_RESULT_DISTRIBUTION["low"]

    qualities = list(distribution.keys())
    weights = list(distribution.values())

    return random.choices(qualities, weights=weights)[0]


def get_quality_multiplier(quality: ItemQuality) -> float:
    """获取品质对应的属性倍率"""
    multipliers = {
        ItemQuality.DEFECTIVE: 0.5,
        ItemQuality.COMMON: 1.0,
        ItemQuality.UNCOMMON: 1.3,
        ItemQuality.RARE: 1.6,
        ItemQuality.EPIC: 2.0,
        ItemQuality.LEGENDARY: 2.5,
        ItemQuality.MYTHIC: 3.0,
    }
    return multipliers.get(quality, 1.0)


def check_materials_available(inventory: Dict[str, int], required: Dict[str, int]) -> bool:
    """
    检查材料是否充足

    Args:
        inventory: 当前拥有的材料 {材料名: 数量}
        required: 需要的材料 {材料名: 数量}

    Returns:
        是否充足
    """
    for material_name, count in required.items():
        if inventory.get(material_name, 0) < count:
            return False
    return True


def get_random_gathering_result(location_level: int, location_type: str = "general") -> List[Tuple[str, int]]:
    """
    获取随机采集结果

    Args:
        location_level: 地点等级
        location_type: 地点类型 (forest:森林, mountain:山脉, cave:洞窟等)

    Returns:
        采集结果列表 [(材料名, 数量), ...]
    """
    results = []

    # 根据地点类型筛选材料
    if location_type == "forest":
        available_materials = [m for m in MATERIALS_DB.values() if m.material_type == MaterialType.HERB]
    elif location_type == "mountain":
        available_materials = [m for m in MATERIALS_DB.values() if m.material_type == MaterialType.ORE]
    elif location_type == "cave":
        available_materials = [m for m in MATERIALS_DB.values()
                               if m.material_type in [MaterialType.ORE, MaterialType.SPIRITUAL_ITEM]]
    else:
        available_materials = list(MATERIALS_DB.values())

    # 根据地点等级筛选合适的材料
    suitable_materials = [m for m in available_materials if abs(m.level - location_level) <= 2]

    if not suitable_materials:
        suitable_materials = available_materials

    # 随机选择1-3种材料
    num_materials = random.randint(1, 3)
    selected = random.sample(suitable_materials, min(num_materials, len(suitable_materials)))

    for material in selected:
        quantity = random.randint(1, 3)
        # 稀有材料数量减少
        if material.rarity in [ItemRarity.EPIC, ItemRarity.LEGENDARY, ItemRarity.MYTHIC]:
            quantity = 1
        results.append((material.name, quantity))

    return results


# 初始化时将所有丹方和图纸的ID设置为它们的名称（便于查找）
def _init_ids():
    """初始化ID映射"""
    global RECIPES_DB, BLUEPRINTS_DB

    # 为丹方添加名称映射
    for name, recipe in list(RECIPES_DB.items()):
        RECIPES_DB[recipe.id] = recipe

    # 为图纸添加名称映射
    for name, blueprint in list(BLUEPRINTS_DB.items()):
        BLUEPRINTS_DB[blueprint.id] = blueprint


_init_ids()
