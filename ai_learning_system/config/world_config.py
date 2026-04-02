"""
世界演化配置模块
定义世界演化相关的配置数据，包括事件类型、天材地宝、势力配置等
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class WorldEventCategory(Enum):
    """世界事件分类"""
    WAR = "war"                    # 战争
    DISCOVERY = "discovery"        # 发现
    DISASTER = "disaster"          # 灾难
    CELEBRATION = "celebration"    # 庆典
    CONFLICT = "conflict"          # 冲突
    POLITICAL = "political"        # 政治
    MYSTERY = "mystery"            # 神秘
    NATURAL = "natural"            # 自然


class WorldEventScope(Enum):
    """世界事件范围"""
    LOCAL = "local"          # 局部（单个地点）
    REGIONAL = "regional"    # 区域（多个地点）
    GLOBAL = "global"        # 全局（整个世界）


@dataclass
class WorldEventTemplate:
    """世界事件模板"""
    event_type: str
    category: WorldEventCategory
    title_templates: List[str]
    description_templates: List[str]
    min_importance: int = 1
    max_importance: int = 10
    scope: WorldEventScope = WorldEventScope.LOCAL
    duration_days: int = 30
    can_repeat: bool = True
    required_realm: int = 0
    effects: Dict[str, Any] = field(default_factory=dict)


# 世界事件模板配置
WORLD_EVENT_TEMPLATES: List[WorldEventTemplate] = [
    # 战争类事件
    WorldEventTemplate(
        event_type="正魔大战",
        category=WorldEventCategory.WAR,
        title_templates=[
            "正魔大战爆发",
            "正道与魔道全面开战",
            "修仙界正魔之争",
            "正邪之战"
        ],
        description_templates=[
            "正道联盟与魔道势力爆发大规模冲突，整个修仙界陷入战火。",
            "正魔两道积怨已久，终于爆发全面战争，无数修士卷入其中。",
            "一场席卷整个修仙界的大战开始了，正魔双方势不两立。"
        ],
        min_importance=8,
        max_importance=10,
        scope=WorldEventScope.GLOBAL,
        duration_days=365,
        can_repeat=False,
        effects={"war_state": True, "faction_tension": 100}
    ),
    WorldEventTemplate(
        event_type="门派战争",
        category=WorldEventCategory.WAR,
        title_templates=[
            "{faction1}与{faction2}开战",
            "{faction1}讨伐{faction2}",
            "{faction1}与{faction2}的冲突"
        ],
        description_templates=[
            "{faction1}与{faction2}因资源争夺爆发战争。",
            "两大门派因恩怨开战，双方弟子互相厮杀。",
            "{faction1}正式向{faction2}宣战，战火蔓延。"
        ],
        min_importance=5,
        max_importance=8,
        scope=WorldEventScope.REGIONAL,
        duration_days=180,
        effects={"war_state": True, "faction_tension": 80}
    ),

    # 发现类事件
    WorldEventTemplate(
        event_type="秘境开启",
        category=WorldEventCategory.DISCOVERY,
        title_templates=[
            "{location}秘境开启",
            "上古秘境现世",
            "神秘秘境出现在{location}",
            "{location}发现新秘境"
        ],
        description_templates=[
            "{location}突然出现一处上古秘境，据说里面藏有重宝。",
            "天地异变，{location}出现神秘空间入口，吸引无数修士前往探索。",
            "一处失落已久的秘境在{location}开启，各方势力蠢蠢欲动。"
        ],
        min_importance=6,
        max_importance=9,
        scope=WorldEventScope.REGIONAL,
        duration_days=90,
        effects={"exploration_bonus": 0.5, "treasure_spawn": True}
    ),
    WorldEventTemplate(
        event_type="遗迹发现",
        category=WorldEventCategory.DISCOVERY,
        title_templates=[
            "{location}发现上古遗迹",
            "{location}出土古代洞府",
            "{location}发现失传传承"
        ],
        description_templates=[
            "修士在{location}发现一处上古遗迹，可能藏有珍贵功法。",
            "{location}出土古代修士洞府，引起各方关注。",
            "一处失传已久的传承在{location}被发现。"
        ],
        min_importance=4,
        max_importance=7,
        scope=WorldEventScope.LOCAL,
        duration_days=60,
        effects={"technique_discovery": True}
    ),

    # 灾难类事件
    WorldEventTemplate(
        event_type="妖兽潮",
        category=WorldEventCategory.DISASTER,
        title_templates=[
            "{location}妖兽暴动",
            "妖兽潮袭击{location}",
            "{location}兽潮来袭"
        ],
        description_templates=[
            "{location}周边妖兽突然暴动，形成兽潮袭击人类聚集地。",
            "大量妖兽从{location}涌出，威胁周边安全。",
            "{location}发生兽潮，修士们正在组织防御。"
        ],
        min_importance=5,
        max_importance=8,
        scope=WorldEventScope.REGIONAL,
        duration_days=45,
        effects={"monster_spawn_rate": 2.0, "danger_level": "high"}
    ),
    WorldEventTemplate(
        event_type="天灾",
        category=WorldEventCategory.DISASTER,
        title_templates=[
            "{location}发生{disaster_type}",
            "{disaster_type}袭击{location}",
            "{location}遭遇{disaster_type}"
        ],
        description_templates=[
            "{location}突然发生{disaster_type}，造成巨大破坏。",
            "天地异变，{disaster_type}降临{location}。",
            "{location}遭遇罕见{disaster_type}，修士们纷纷躲避。"
        ],
        min_importance=4,
        max_importance=7,
        scope=WorldEventScope.LOCAL,
        duration_days=30,
        effects={"damage_to_npcs": True, "resource_depletion": True}
    ),

    # 神秘类事件
    WorldEventTemplate(
        event_type="天材地宝出世",
        category=WorldEventCategory.MYSTERY,
        title_templates=[
            "{location}有宝物现世",
            "{treasure_name}出现在{location}",
            "{location}发现{treature_name}"
        ],
        description_templates=[
            "{location}突然出现异象，{treasure_name}即将出世。",
            "天地灵气汇聚{location}，{treasure_name}现世。",
            "{treasure_name}在{location}出现，吸引各方修士争夺。"
        ],
        min_importance=5,
        max_importance=9,
        scope=WorldEventScope.REGIONAL,
        duration_days=30,
        effects={"treasure_spawn": True, "pvp_enabled": True}
    ),
    WorldEventTemplate(
        event_type="异象",
        category=WorldEventCategory.MYSTERY,
        title_templates=[
            "{location}出现异象",
            "天地异变",
            "{location}天现异象"
        ],
        description_templates=[
            "{location}天空出现奇异景象，不知吉凶。",
            "天地灵气异常波动，{location}出现神秘异象。",
            "{location}发生无法解释的天地异变。"
        ],
        min_importance=3,
        max_importance=6,
        scope=WorldEventScope.LOCAL,
        duration_days=15,
        effects={"cultivation_bonus": 0.2}
    ),

    # 政治类事件
    WorldEventTemplate(
        event_type="势力崛起",
        category=WorldEventCategory.POLITICAL,
        title_templates=[
            "{faction}崛起",
            "{faction}实力大增",
            "{faction}成为新势力"
        ],
        description_templates=[
            "{faction}近年来发展迅速，成为修仙界新兴势力。",
            "{faction}通过一系列行动，声望大增。",
            "{faction}崛起，改变了当地势力格局。"
        ],
        min_importance=4,
        max_importance=7,
        scope=WorldEventScope.REGIONAL,
        duration_days=365,
        effects={"faction_power": 1.2}
    ),
    WorldEventTemplate(
        event_type="势力衰落",
        category=WorldEventCategory.POLITICAL,
        title_templates=[
            "{faction}衰落",
            "{faction}遭遇危机",
            "{faction}实力大减"
        ],
        description_templates=[
            "{faction}遭遇重大打击，势力大不如前。",
            "{faction}内部出现问题，实力衰退。",
            "{faction}衰落，其势力范围被其他势力蚕食。"
        ],
        min_importance=4,
        max_importance=7,
        scope=WorldEventScope.REGIONAL,
        duration_days=365,
        effects={"faction_power": 0.8}
    ),

    # 庆典类事件
    WorldEventTemplate(
        event_type="修仙大会",
        category=WorldEventCategory.CELEBRATION,
        title_templates=[
            "{location}举办修仙大会",
            "修仙界盛会",
            "{faction}举办论道大会"
        ],
        description_templates=[
            "{location}即将举办修仙大会，各路修士齐聚一堂。",
            "修仙界盛会在{location}举行，交流修炼心得。",
            "{faction}举办论道大会，邀请各方修士参加。"
        ],
        min_importance=4,
        max_importance=6,
        scope=WorldEventScope.REGIONAL,
        duration_days=30,
        effects={"social_bonus": 0.3, "technique_exchange": True}
    ),
]


# 天材地宝配置
TREASURE_TYPES: Dict[str, Dict[str, Any]] = {
    "spirit_stone_vein": {
        "name": "灵石矿脉",
        "type": "resource",
        "rarity": "common",
        "description": "富含灵石的矿脉，开采可获得大量灵石。",
        "effects": {"spirit_stones": 1000},
        "guardian_chance": 0.3
    },
    "herb_garden": {
        "name": "灵药园",
        "type": "resource",
        "rarity": "uncommon",
        "description": "生长着各种珍稀灵药的园地。",
        "effects": {"herbs": ["千年灵芝", "万年人参", "九叶剑草"]},
        "guardian_chance": 0.4
    },
    "ancient_relic": {
        "name": "上古遗物",
        "type": "artifact",
        "rarity": "rare",
        "description": "上古修士遗留的宝物，蕴含神秘力量。",
        "effects": {"attribute_bonus": 10, "special_ability": True},
        "guardian_chance": 0.6
    },
    "immortal_grass": {
        "name": "仙草",
        "type": "consumable",
        "rarity": "epic",
        "description": "传说中的仙草，服用可大幅提升修为。",
        "effects": {"exp_boost": 10000, "lifespan_increase": 100},
        "guardian_chance": 0.7
    },
    "dragon_blood": {
        "name": "龙血",
        "type": "material",
        "rarity": "legendary",
        "description": "真龙之血，炼体至宝。",
        "effects": {"body_refinement": 50, "strength": 30},
        "guardian_chance": 0.8
    },
    "phoenix_feather": {
        "name": "凤凰羽",
        "type": "material",
        "rarity": "legendary",
        "description": "凤凰涅槃时脱落的羽毛，蕴含不死之力。",
        "effects": {"resurrection": 1, "fire_resistance": 100},
        "guardian_chance": 0.8
    },
    "immortal_stone": {
        "name": "不朽石",
        "type": "material",
        "rarity": "mythic",
        "description": "传说中可炼制仙器的材料。",
        "effects": {"equipment_quality": "immortal", "durability": 999},
        "guardian_chance": 0.9
    },
}


# 稀有度等级
RARITY_LEVELS: Dict[str, Dict[str, Any]] = {
    "common": {"name": "普通", "color": "#808080", "spawn_weight": 50, "value_multiplier": 1.0},
    "uncommon": {"name": "稀有", "color": "#00FF00", "spawn_weight": 30, "value_multiplier": 2.0},
    "rare": {"name": "珍贵", "color": "#0000FF", "spawn_weight": 15, "value_multiplier": 5.0},
    "epic": {"name": "史诗", "color": "#800080", "spawn_weight": 8, "value_multiplier": 10.0},
    "legendary": {"name": "传说", "color": "#FFA500", "spawn_weight": 4, "value_multiplier": 25.0},
    "mythic": {"name": "神话", "color": "#FF0000", "spawn_weight": 1, "value_multiplier": 100.0},
}


# 势力类型配置
FACTION_TYPES: Dict[str, Dict[str, Any]] = {
    "righteous": {
        "name": "正道",
        "description": "遵循正道修行的门派，注重道德和秩序。",
        "typical_traits": ["正义", "秩序", "仁慈"],
        "relations": {"righteous": "friendly", "demonic": "hostile", "neutral": "neutral"}
    },
    "demonic": {
        "name": "魔道",
        "description": "追求力量的门派，不择手段提升修为。",
        "typical_traits": ["野心", "力量", "残忍"],
        "relations": {"righteous": "hostile", "demonic": "friendly", "neutral": "neutral"}
    },
    "neutral": {
        "name": "中立",
        "description": "不参与正魔之争的门派，专注于自身修行。",
        "typical_traits": ["中立", "独立", "务实"],
        "relations": {"righteous": "neutral", "demonic": "neutral", "neutral": "friendly"}
    },
    "heretic": {
        "name": "邪道",
        "description": "修行邪术的门派，为正道所不容。",
        "typical_traits": ["诡异", "邪恶", "疯狂"],
        "relations": {"righteous": "hostile", "demonic": "neutral", "neutral": "hostile"}
    }
}


# NPC演化配置
NPC_EVOLUTION_CONFIG: Dict[str, Any] = {
    "breakthrough_chance": 0.05,           # 突破概率
    "exploration_chance": 0.1,             # 探索概率
    "social_chance": 0.15,                 # 社交概率
    "combat_chance": 0.08,                 # 战斗概率
    "death_chance_base": 0.01,             # 基础死亡概率
    "max_age_multiplier": 1.5,             # 最大寿命倍率
    "realm_lifespan_bonus": {              # 境界寿命加成
        0: 100,    # 凡人
        1: 150,    # 炼气
        2: 200,    # 筑基
        3: 300,    # 金丹
        4: 500,    # 元婴
        5: 800,    # 化神
        6: 1200,   # 炼虚
        7: 2000,   # 合体
        8: 5000,   # 大乘
        9: 10000,  # 渡劫
    }
}


# 世界经济配置
WORLD_ECONOMY_CONFIG: Dict[str, Any] = {
    "resources": {
        "spirit_stones": {"base_price": 1, "volatility": 0.1},
        "herbs": {"base_price": 10, "volatility": 0.2},
        "ores": {"base_price": 15, "volatility": 0.15},
        "pellets": {"base_price": 50, "volatility": 0.25},
        "materials": {"base_price": 20, "volatility": 0.18},
    },
    "price_update_interval_days": 30,
    "max_price_change": 0.3,
    "event_impact_multiplier": 2.0,
}


# 世界演化时间配置
WORLD_TIME_CONFIG: Dict[str, Any] = {
    "days_per_month": 30,
    "months_per_year": 12,
    "event_check_interval_days": 7,        # 事件检查间隔
    "treasure_spawn_chance": 0.05,         # 宝物生成概率
    "npc_evolution_interval_days": 30,     # NPC演化间隔
    "faction_update_interval_days": 90,    # 势力更新间隔
    "economy_update_interval_days": 30,    # 经济更新间隔
}


def get_event_template(event_type: str) -> WorldEventTemplate:
    """
    获取指定类型的事件模板

    Args:
        event_type: 事件类型

    Returns:
        事件模板，找不到返回None
    """
    for template in WORLD_EVENT_TEMPLATES:
        if template.event_type == event_type:
            return template
    return None


def get_random_treasure_type() -> str:
    """
    根据权重随机获取宝物类型

    Returns:
        宝物类型key
    """
    import random
    total_weight = sum(RARITY_LEVELS[t["rarity"]]["spawn_weight"] for t in TREASURE_TYPES.values())
    rand = random.randint(1, total_weight)
    current = 0
    for key, treasure in TREASURE_TYPES.items():
        current += RARITY_LEVELS[treasure["rarity"]]["spawn_weight"]
        if rand <= current:
            return key
    return "spirit_stone_vein"


def calculate_treasure_value(treasure_type: str, base_value: int = 100) -> int:
    """
    计算宝物价值

    Args:
        treasure_type: 宝物类型
        base_value: 基础价值

    Returns:
        计算后的价值
    """
    if treasure_type not in TREASURE_TYPES:
        return base_value
    rarity = TREASURE_TYPES[treasure_type]["rarity"]
    multiplier = RARITY_LEVELS[rarity]["value_multiplier"]
    return int(base_value * multiplier)
