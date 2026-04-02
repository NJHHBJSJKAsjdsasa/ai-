"""
成就配置模块
定义成就系统的数据结构、成就类型和成就奖励
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AchievementCategory(Enum):
    """成就分类"""
    CULTIVATION = "cultivation"  # 修炼类
    COMBAT = "combat"            # 战斗类
    EXPLORATION = "exploration"  # 探索类
    SOCIAL = "social"            # 社交类
    COLLECTION = "collection"    # 收集类
    SPECIAL = "special"          # 特殊类


class AchievementTier(Enum):
    """成就等级"""
    BRONZE = "bronze"      # 铜
    SILVER = "silver"      # 银
    GOLD = "gold"          # 金
    DIAMOND = "diamond"    # 钻石


class AchievementConditionType(Enum):
    """成就条件类型"""
    # 修炼类
    REALM_BREAKTHROUGH = "realm_breakthrough"  # 突破境界
    PRACTICE_COUNT = "practice_count"          # 修炼次数
    PRACTICE_TIME = "practice_time"            # 修炼时长
    TRIBULATION_SUCCESS = "tribulation_success"  # 渡劫成功

    # 战斗类
    DEFEAT_ENEMY = "defeat_enemy"              # 击败敌人
    DEFEAT_BOSS = "defeat_boss"                # 击败BOSS
    WIN_STREAK = "win_streak"                  # 连胜
    TOTAL_WINS = "total_wins"                  # 总胜利次数

    # 探索类
    DISCOVER_LOCATION = "discover_location"    # 发现地点
    EXPLORE_COUNT = "explore_count"            # 探索次数
    DISCOVER_SECRET = "discover_secret"        # 发现秘境

    # 社交类
    MAKE_FRIEND = "make_friend"                # 结交朋友
    FIND_PARTNER = "find_partner"              # 结交道侣
    ACCEPT_APPRENTICE = "accept_apprentice"    # 收徒
    JOIN_SECT = "join_sect"                    # 加入门派
    SECT_CONTRIBUTION = "sect_contribution"    # 门派贡献

    # 收集类
    COLLECT_ITEM = "collect_item"              # 收集物品
    COLLECT_TECHNIQUE = "collect_technique"    # 收集功法
    COLLECT_PET = "collect_pet"                # 收集灵兽
    REACH_LEVEL = "reach_level"                # 达到等级

    # 特殊类
    FIRST_DEATH = "first_death"                # 首次死亡
    REBIRTH = "rebirth"                        # 转世重生
    SPECIAL_EVENT = "special_event"            # 特殊事件


@dataclass
class AchievementReward:
    """成就奖励数据类"""
    exp: int = 0                    # 经验值
    spirit_stones: int = 0          # 灵石
    items: List[Dict[str, Any]] = field(default_factory=list)  # 道具列表
    title: str = ""                 # 称号奖励
    karma: int = 0                  # 业力
    reputation: int = 0             # 声望
    special_effect: str = ""        # 特殊效果描述

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "exp": self.exp,
            "spirit_stones": self.spirit_stones,
            "items": self.items,
            "title": self.title,
            "karma": self.karma,
            "reputation": self.reputation,
            "special_effect": self.special_effect
        }


@dataclass
class AchievementTemplate:
    """成就模板数据类"""
    id: str                         # 成就唯一ID
    name: str                       # 成就名称
    description: str                # 成就描述
    category: AchievementCategory   # 成就分类
    tier: AchievementTier           # 成就等级
    condition_type: AchievementConditionType  # 条件类型
    condition_target: str           # 条件目标
    condition_value: int = 1        # 条件数值
    icon: str = "🏆"                # 成就图标
    hidden: bool = False            # 是否隐藏成就
    pre_achievement_id: str = None  # 前置成就ID
    rewards: AchievementReward = field(default_factory=AchievementReward)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "tier": self.tier.value,
            "condition_type": self.condition_type.value,
            "condition_target": self.condition_target,
            "condition_value": self.condition_value,
            "icon": self.icon,
            "hidden": self.hidden,
            "pre_achievement_id": self.pre_achievement_id,
            "rewards": self.rewards.to_dict()
        }


# ==================== 成就等级配置 ====================

TIER_CONFIG = {
    AchievementTier.BRONZE: {
        "name": "铜",
        "color": "#cd7f32",
        "point_value": 10,
        "exp_multiplier": 1.0,
        "spirit_stone_multiplier": 1.0
    },
    AchievementTier.SILVER: {
        "name": "银",
        "color": "#c0c0c0",
        "point_value": 25,
        "exp_multiplier": 2.0,
        "spirit_stone_multiplier": 2.0
    },
    AchievementTier.GOLD: {
        "name": "金",
        "color": "#ffd700",
        "point_value": 50,
        "exp_multiplier": 4.0,
        "spirit_stone_multiplier": 4.0
    },
    AchievementTier.DIAMOND: {
        "name": "钻石",
        "color": "#b9f2ff",
        "point_value": 100,
        "exp_multiplier": 10.0,
        "spirit_stone_multiplier": 10.0
    }
}


# ==================== 修炼类成就 ====================

CULTIVATION_ACHIEVEMENTS: List[AchievementTemplate] = [
    # 突破境界成就
    AchievementTemplate(
        id="cultivation_001",
        name="初入仙途",
        description="成功突破到炼气期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_1",
        condition_value=1,
        icon="🌱",
        rewards=AchievementReward(exp=100, spirit_stones=50, title="初入仙途")
    ),
    AchievementTemplate(
        id="cultivation_002",
        name="筑基成功",
        description="成功突破到筑基期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_2",
        condition_value=1,
        icon="🌿",
        rewards=AchievementReward(exp=300, spirit_stones=150, title="筑基修士")
    ),
    AchievementTemplate(
        id="cultivation_003",
        name="金丹大道",
        description="成功突破到结丹期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_3",
        condition_value=1,
        icon="💎",
        rewards=AchievementReward(exp=800, spirit_stones=400, title="金丹真人")
    ),
    AchievementTemplate(
        id="cultivation_004",
        name="元婴老祖",
        description="成功突破到元婴期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_4",
        condition_value=1,
        icon="👶",
        rewards=AchievementReward(exp=2000, spirit_stones=1000, title="元婴老祖")
    ),
    AchievementTemplate(
        id="cultivation_005",
        name="化神之境",
        description="成功突破到化神期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_5",
        condition_value=1,
        icon="✨",
        rewards=AchievementReward(exp=5000, spirit_stones=2500, title="化神大能")
    ),
    AchievementTemplate(
        id="cultivation_006",
        name="炼虚合道",
        description="成功突破到炼虚期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_6",
        condition_value=1,
        icon="🌟",
        rewards=AchievementReward(exp=10000, spirit_stones=5000, title="炼虚真君")
    ),
    AchievementTemplate(
        id="cultivation_007",
        name="合体大乘",
        description="成功突破到合体期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.DIAMOND,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_7",
        condition_value=1,
        icon="🌌",
        rewards=AchievementReward(exp=20000, spirit_stones=10000, title="合体圣君")
    ),
    AchievementTemplate(
        id="cultivation_008",
        name="渡劫飞升",
        description="成功突破到大乘期",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.DIAMOND,
        condition_type=AchievementConditionType.REALM_BREAKTHROUGH,
        condition_target="realm_8",
        condition_value=1,
        icon="🌈",
        rewards=AchievementReward(exp=50000, spirit_stones=25000, title="大乘仙尊")
    ),

    # 修炼次数成就
    AchievementTemplate(
        id="cultivation_101",
        name="勤修不辍",
        description="累计修炼10次",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.PRACTICE_COUNT,
        condition_target="practice",
        condition_value=10,
        icon="📿",
        rewards=AchievementReward(exp=50, spirit_stones=30)
    ),
    AchievementTemplate(
        id="cultivation_102",
        name="苦修之士",
        description="累计修炼100次",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.PRACTICE_COUNT,
        condition_target="practice",
        condition_value=100,
        icon="🧘",
        rewards=AchievementReward(exp=300, spirit_stones=150)
    ),
    AchievementTemplate(
        id="cultivation_103",
        name="修炼狂人",
        description="累计修炼1000次",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.PRACTICE_COUNT,
        condition_target="practice",
        condition_value=1000,
        icon="🔥",
        rewards=AchievementReward(exp=2000, spirit_stones=1000, title="修炼狂人")
    ),
    AchievementTemplate(
        id="cultivation_104",
        name="万年苦修",
        description="累计修炼10000次",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.DIAMOND,
        condition_type=AchievementConditionType.PRACTICE_COUNT,
        condition_target="practice",
        condition_value=10000,
        icon="⏳",
        rewards=AchievementReward(exp=10000, spirit_stones=5000, title="万年修士")
    ),

    # 渡劫成就
    AchievementTemplate(
        id="cultivation_201",
        name="初渡天劫",
        description="成功渡过1次天劫",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.TRIBULATION_SUCCESS,
        condition_target="tribulation",
        condition_value=1,
        icon="⚡",
        rewards=AchievementReward(exp=200, spirit_stones=100)
    ),
    AchievementTemplate(
        id="cultivation_202",
        name="雷劫无惧",
        description="成功渡过10次天劫",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.TRIBULATION_SUCCESS,
        condition_target="tribulation",
        condition_value=10,
        icon="🌩️",
        rewards=AchievementReward(exp=1000, spirit_stones=500)
    ),
    AchievementTemplate(
        id="cultivation_203",
        name="天劫主宰",
        description="成功渡过50次天劫",
        category=AchievementCategory.CULTIVATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.TRIBULATION_SUCCESS,
        condition_target="tribulation",
        condition_value=50,
        icon="👑",
        rewards=AchievementReward(exp=5000, spirit_stones=2500, title="天劫主宰")
    ),
]


# ==================== 战斗类成就 ====================

COMBAT_ACHIEVEMENTS: List[AchievementTemplate] = [
    # 击败敌人成就
    AchievementTemplate(
        id="combat_001",
        name="初战告捷",
        description="首次击败敌人",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.DEFEAT_ENEMY,
        condition_target="enemy",
        condition_value=1,
        icon="⚔️",
        rewards=AchievementReward(exp=50, spirit_stones=30)
    ),
    AchievementTemplate(
        id="combat_002",
        name="百战勇士",
        description="累计击败100个敌人",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.DEFEAT_ENEMY,
        condition_target="enemy",
        condition_value=100,
        icon="🗡️",
        rewards=AchievementReward(exp=200, spirit_stones=100)
    ),
    AchievementTemplate(
        id="combat_003",
        name="千斩修罗",
        description="累计击败1000个敌人",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.DEFEAT_ENEMY,
        condition_target="enemy",
        condition_value=1000,
        icon="🔪",
        rewards=AchievementReward(exp=1000, spirit_stones=500, title="千斩修罗")
    ),
    AchievementTemplate(
        id="combat_004",
        name="万人屠",
        description="累计击败10000个敌人",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.DEFEAT_ENEMY,
        condition_target="enemy",
        condition_value=10000,
        icon="💀",
        rewards=AchievementReward(exp=5000, spirit_stones=2500, title="万人屠", karma=-100)
    ),

    # 击败BOSS成就
    AchievementTemplate(
        id="combat_101",
        name="首杀",
        description="首次击败BOSS级敌人",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.DEFEAT_BOSS,
        condition_target="boss",
        condition_value=1,
        icon="🎯",
        rewards=AchievementReward(exp=100, spirit_stones=50)
    ),
    AchievementTemplate(
        id="combat_102",
        name="BOSS猎人",
        description="累计击败10个BOSS",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.DEFEAT_BOSS,
        condition_target="boss",
        condition_value=10,
        icon="🏹",
        rewards=AchievementReward(exp=500, spirit_stones=250)
    ),
    AchievementTemplate(
        id="combat_103",
        name="BOSS终结者",
        description="累计击败100个BOSS",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.DEFEAT_BOSS,
        condition_target="boss",
        condition_value=100,
        icon="☠️",
        rewards=AchievementReward(exp=3000, spirit_stones=1500, title="BOSS终结者")
    ),

    # 连胜成就
    AchievementTemplate(
        id="combat_201",
        name="连胜",
        description="取得5场连胜",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.WIN_STREAK,
        condition_target="streak",
        condition_value=5,
        icon="🔥",
        rewards=AchievementReward(exp=100, spirit_stones=50)
    ),
    AchievementTemplate(
        id="combat_202",
        name="势不可挡",
        description="取得20场连胜",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.WIN_STREAK,
        condition_target="streak",
        condition_value=20,
        icon="🌊",
        rewards=AchievementReward(exp=500, spirit_stones=250)
    ),
    AchievementTemplate(
        id="combat_203",
        name="战神",
        description="取得100场连胜",
        category=AchievementCategory.COMBAT,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.WIN_STREAK,
        condition_target="streak",
        condition_value=100,
        icon="👑",
        rewards=AchievementReward(exp=3000, spirit_stones=1500, title="战神")
    ),
]


# ==================== 探索类成就 ====================

EXPLORATION_ACHIEVEMENTS: List[AchievementTemplate] = [
    AchievementTemplate(
        id="exploration_001",
        name="初出茅庐",
        description="首次探索新地点",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.DISCOVER_LOCATION,
        condition_target="location",
        condition_value=1,
        icon="🗺️",
        rewards=AchievementReward(exp=50, spirit_stones=30)
    ),
    AchievementTemplate(
        id="exploration_002",
        name="足迹遍布",
        description="探索10个不同地点",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.DISCOVER_LOCATION,
        condition_target="location",
        condition_value=10,
        icon="🧭",
        rewards=AchievementReward(exp=200, spirit_stones=100)
    ),
    AchievementTemplate(
        id="exploration_003",
        name="探险家",
        description="探索50个不同地点",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.DISCOVER_LOCATION,
        condition_target="location",
        condition_value=50,
        icon="🌍",
        rewards=AchievementReward(exp=800, spirit_stones=400, title="探险家")
    ),
    AchievementTemplate(
        id="exploration_004",
        name="世界行者",
        description="探索100个不同地点",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.DISCOVER_LOCATION,
        condition_target="location",
        condition_value=100,
        icon="🌐",
        rewards=AchievementReward(exp=3000, spirit_stones=1500, title="世界行者")
    ),

    # 探索次数成就
    AchievementTemplate(
        id="exploration_101",
        name="好奇心",
        description="累计探索10次",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.EXPLORE_COUNT,
        condition_target="explore",
        condition_value=10,
        icon="🔍",
        rewards=AchievementReward(exp=50, spirit_stones=30)
    ),
    AchievementTemplate(
        id="exploration_102",
        name="寻宝者",
        description="累计探索100次",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.EXPLORE_COUNT,
        condition_target="explore",
        condition_value=100,
        icon="💰",
        rewards=AchievementReward(exp=300, spirit_stones=150)
    ),
    AchievementTemplate(
        id="exploration_103",
        name="寻宝大师",
        description="累计探索1000次",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.EXPLORE_COUNT,
        condition_target="explore",
        condition_value=1000,
        icon="👑",
        rewards=AchievementReward(exp=2000, spirit_stones=1000, title="寻宝大师")
    ),

    # 秘境成就
    AchievementTemplate(
        id="exploration_201",
        name="秘境初探",
        description="首次发现秘境",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.DISCOVER_SECRET,
        condition_target="secret",
        condition_value=1,
        icon="🚪",
        rewards=AchievementReward(exp=300, spirit_stones=150)
    ),
    AchievementTemplate(
        id="exploration_202",
        name="秘境行者",
        description="发现10个秘境",
        category=AchievementCategory.EXPLORATION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.DISCOVER_SECRET,
        condition_target="secret",
        condition_value=10,
        icon="🗝️",
        rewards=AchievementReward(exp=1500, spirit_stones=750, title="秘境行者")
    ),
]


# ==================== 社交类成就 ====================

SOCIAL_ACHIEVEMENTS: List[AchievementTemplate] = [
    # 交友成就
    AchievementTemplate(
        id="social_001",
        name="广结善缘",
        description="结交5位好友",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.MAKE_FRIEND,
        condition_target="friend",
        condition_value=5,
        icon="🤝",
        rewards=AchievementReward(exp=100, spirit_stones=50)
    ),
    AchievementTemplate(
        id="social_002",
        name="人脉广泛",
        description="结交20位好友",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.MAKE_FRIEND,
        condition_target="friend",
        condition_value=20,
        icon="👥",
        rewards=AchievementReward(exp=400, spirit_stones=200)
    ),
    AchievementTemplate(
        id="social_003",
        name="交际花",
        description="结交50位好友",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.MAKE_FRIEND,
        condition_target="friend",
        condition_value=50,
        icon="🌸",
        rewards=AchievementReward(exp=1500, spirit_stones=750, title="交际花")
    ),

    # 道侣成就
    AchievementTemplate(
        id="social_101",
        name="双修道侣",
        description="首次结交道侣",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.FIND_PARTNER,
        condition_target="partner",
        condition_value=1,
        icon="💕",
        rewards=AchievementReward(exp=500, spirit_stones=250, title="有道侣的人")
    ),
    AchievementTemplate(
        id="social_102",
        name="多情种子",
        description="累计结交道侣3人",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.FIND_PARTNER,
        condition_target="partner",
        condition_value=3,
        icon="💘",
        rewards=AchievementReward(exp=1500, spirit_stones=750, karma=-50)
    ),

    # 师徒成就
    AchievementTemplate(
        id="social_201",
        name="为人师表",
        description="首次收徒",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.ACCEPT_APPRENTICE,
        condition_target="apprentice",
        condition_value=1,
        icon="👨‍🏫",
        rewards=AchievementReward(exp=400, spirit_stones=200, title="师父")
    ),
    AchievementTemplate(
        id="social_202",
        name="桃李满天下",
        description="累计收徒5人",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.ACCEPT_APPRENTICE,
        condition_target="apprentice",
        condition_value=5,
        icon="🎓",
        rewards=AchievementReward(exp=1500, spirit_stones=750, title="名师")
    ),

    # 门派成就
    AchievementTemplate(
        id="social_301",
        name="门派弟子",
        description="加入一个门派",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.JOIN_SECT,
        condition_target="sect",
        condition_value=1,
        icon="🏛️",
        rewards=AchievementReward(exp=100, spirit_stones=50)
    ),
    AchievementTemplate(
        id="social_302",
        name="门派栋梁",
        description="累计贡献1000点门派贡献",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.SECT_CONTRIBUTION,
        condition_target="contribution",
        condition_value=1000,
        icon="⭐",
        rewards=AchievementReward(exp=500, spirit_stones=250)
    ),
    AchievementTemplate(
        id="social_303",
        name="门派支柱",
        description="累计贡献10000点门派贡献",
        category=AchievementCategory.SOCIAL,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.SECT_CONTRIBUTION,
        condition_target="contribution",
        condition_value=10000,
        icon="🏆",
        rewards=AchievementReward(exp=2000, spirit_stones=1000, title="门派支柱")
    ),
]


# ==================== 收集类成就 ====================

COLLECTION_ACHIEVEMENTS: List[AchievementTemplate] = [
    # 物品收集
    AchievementTemplate(
        id="collection_001",
        name="收藏家",
        description="收集10种不同物品",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.COLLECT_ITEM,
        condition_target="item",
        condition_value=10,
        icon="📦",
        rewards=AchievementReward(exp=100, spirit_stones=50)
    ),
    AchievementTemplate(
        id="collection_002",
        name="收藏家·进阶",
        description="收集50种不同物品",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.COLLECT_ITEM,
        condition_target="item",
        condition_value=50,
        icon="🎁",
        rewards=AchievementReward(exp=500, spirit_stones=250)
    ),
    AchievementTemplate(
        id="collection_003",
        name="收藏家·大师",
        description="收集100种不同物品",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.COLLECT_ITEM,
        condition_target="item",
        condition_value=100,
        icon="💎",
        rewards=AchievementReward(exp=2000, spirit_stones=1000, title="收藏大师")
    ),

    # 功法收集
    AchievementTemplate(
        id="collection_101",
        name="博采众长",
        description="学习5种功法",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.COLLECT_TECHNIQUE,
        condition_target="technique",
        condition_value=5,
        icon="📜",
        rewards=AchievementReward(exp=150, spirit_stones=75)
    ),
    AchievementTemplate(
        id="collection_102",
        name="功法大师",
        description="学习20种功法",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.COLLECT_TECHNIQUE,
        condition_target="technique",
        condition_value=20,
        icon="📚",
        rewards=AchievementReward(exp=600, spirit_stones=300)
    ),
    AchievementTemplate(
        id="collection_103",
        name="万法归宗",
        description="学习50种功法",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.COLLECT_TECHNIQUE,
        condition_target="technique",
        condition_value=50,
        icon="🔮",
        rewards=AchievementReward(exp=2500, spirit_stones=1250, title="万法归宗")
    ),

    # 灵兽收集
    AchievementTemplate(
        id="collection_201",
        name="灵兽伙伴",
        description="拥有3只灵兽",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.COLLECT_PET,
        condition_target="pet",
        condition_value=3,
        icon="🐾",
        rewards=AchievementReward(exp=150, spirit_stones=75)
    ),
    AchievementTemplate(
        id="collection_202",
        name="灵兽大师",
        description="拥有10只灵兽",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.COLLECT_PET,
        condition_target="pet",
        condition_value=10,
        icon="🦊",
        rewards=AchievementReward(exp=600, spirit_stones=300)
    ),
    AchievementTemplate(
        id="collection_203",
        name="万兽之王",
        description="拥有30只灵兽",
        category=AchievementCategory.COLLECTION,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.COLLECT_PET,
        condition_target="pet",
        condition_value=30,
        icon="🐉",
        rewards=AchievementReward(exp=2500, spirit_stones=1250, title="万兽之王")
    ),
]


# ==================== 特殊类成就 ====================

SPECIAL_ACHIEVEMENTS: List[AchievementTemplate] = [
    AchievementTemplate(
        id="special_001",
        name="出师未捷",
        description="首次死亡",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        condition_type=AchievementConditionType.FIRST_DEATH,
        condition_target="death",
        condition_value=1,
        icon="💀",
        hidden=True,
        rewards=AchievementReward(exp=0, spirit_stones=0, karma=10)
    ),
    AchievementTemplate(
        id="special_002",
        name="轮回转世",
        description="转世重生一次",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.REBIRTH,
        condition_target="rebirth",
        condition_value=1,
        icon="🔄",
        rewards=AchievementReward(exp=500, spirit_stones=250, title="转世者")
    ),
    AchievementTemplate(
        id="special_003",
        name="百世轮回",
        description="转世重生10次",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        condition_type=AchievementConditionType.REBIRTH,
        condition_target="rebirth",
        condition_value=10,
        icon="♾️",
        rewards=AchievementReward(exp=3000, spirit_stones=1500, title="百世轮回")
    ),
    AchievementTemplate(
        id="special_004",
        name="天命之子",
        description="触发一次特殊事件",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        condition_type=AchievementConditionType.SPECIAL_EVENT,
        condition_target="event",
        condition_value=1,
        icon="🌟",
        hidden=True,
        rewards=AchievementReward(exp=300, spirit_stones=150, karma=50)
    ),
]


# ==================== 所有成就汇总 ====================

ALL_ACHIEVEMENTS: List[AchievementTemplate] = (
    CULTIVATION_ACHIEVEMENTS +
    COMBAT_ACHIEVEMENTS +
    EXPLORATION_ACHIEVEMENTS +
    SOCIAL_ACHIEVEMENTS +
    COLLECTION_ACHIEVEMENTS +
    SPECIAL_ACHIEVEMENTS
)


# ==================== 辅助函数 ====================

def get_achievement_by_id(achievement_id: str) -> Optional[AchievementTemplate]:
    """根据ID获取成就模板"""
    for achievement in ALL_ACHIEVEMENTS:
        if achievement.id == achievement_id:
            return achievement
    return None


def get_achievements_by_category(category: AchievementCategory) -> List[AchievementTemplate]:
    """根据分类获取成就列表"""
    return [a for a in ALL_ACHIEVEMENTS if a.category == category]


def get_achievements_by_tier(tier: AchievementTier) -> List[AchievementTemplate]:
    """根据等级获取成就列表"""
    return [a for a in ALL_ACHIEVEMENTS if a.tier == tier]


def get_category_name(category: AchievementCategory) -> str:
    """获取分类名称"""
    category_names = {
        AchievementCategory.CULTIVATION: "修炼",
        AchievementCategory.COMBAT: "战斗",
        AchievementCategory.EXPLORATION: "探索",
        AchievementCategory.SOCIAL: "社交",
        AchievementCategory.COLLECTION: "收集",
        AchievementCategory.SPECIAL: "特殊"
    }
    return category_names.get(category, "未知")


def get_tier_name(tier: AchievementTier) -> str:
    """获取等级名称"""
    return TIER_CONFIG.get(tier, {}).get("name", "未知")


def get_tier_color(tier: AchievementTier) -> str:
    """获取等级颜色"""
    return TIER_CONFIG.get(tier, {}).get("color", "#ffffff")


def get_tier_point_value(tier: AchievementTier) -> int:
    """获取等级积分值"""
    return TIER_CONFIG.get(tier, {}).get("point_value", 0)
