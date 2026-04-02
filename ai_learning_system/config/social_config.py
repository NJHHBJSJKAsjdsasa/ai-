"""
社交系统配置模块
定义社交关系类型、双修加成、师徒传承等配置
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class RelationType(Enum):
    """社交关系类型"""
    FRIEND = "好友"
    CLOSE_FRIEND = "挚友"
    DAO_LV = "道侣"
    MASTER = "师父"
    APPRENTICE = "徒弟"
    ENEMY = "仇敌"
    RIVAL = "宿敌"
    ACQUAINTANCE = "熟人"
    STRANGER = "陌生人"


class InteractionType(Enum):
    """社交互动类型"""
    CHAT = "交谈"
    GIFT = "赠送礼物"
    HELP = "协助"
    DUEL = "切磋"
    DUAL_CULTIVATION = "双修"
    TEACH = "传授功法"
    SEEK_ADVICE = "请教"
    OFFEND = "冒犯"
    BETRAY = "背叛"


@dataclass
class DualCultivationConfig:
    """双修配置"""
    base_exp_bonus: int = 50
    intimacy_bonus_per_level: int = 10
    max_daily_count: int = 3
    cooldown_hours: int = 8
    intimacy_increase: int = 5

    # 亲密度等级加成
    intimacy_bonus = {
        "初识": 1.0,
        "熟悉": 1.2,
        "亲近": 1.5,
        "情深": 2.0,
        "至爱": 3.0
    }

    # 境界差距惩罚
    realm_penalty = {
        0: 1.0,   # 同境界
        1: 0.9,   # 相差1级
        2: 0.7,   # 相差2级
        3: 0.5,   # 相差3级
        4: 0.3    # 相差4级以上
    }


@dataclass
class MasterApprenticeConfig:
    """师徒配置"""
    max_apprentices: int = 3
    teaching_cooldown_days: int = 7
    respect_decay_per_day: int = 1
    respect_gain_per_teaching: int = 5

    # 拜师条件
    apprentice_requirements = {
        "max_realm_diff": 3,  # 最大境界差距
        "min_intimacy": 30,   # 最低亲密度
    }

    # 可传授功法限制
    teachable_techniques = {
        "common": True,
        "rare": True,
        "epic": False,  # 史诗功法需要特殊条件
        "legendary": False  # 传说功法不可传授
    }


@dataclass
class SocialBonus:
    """社交加成效果"""
    cultivation_speed: float = 0.0
    exp_bonus: float = 0.0
    combat_bonus: float = 0.0
    luck_bonus: float = 0.0


# ==================== 道侣双修加成配置 ====================

DAO_LV_BONUSES = {
    "cultivation_speed": 0.15,  # 修炼速度加成15%
    "exp_bonus": 0.20,          # 经验获取加成20%
    "breakthrough_bonus": 0.10, # 突破成功率加成10%
    "dual_cultivation_exp": {   # 双修经验加成
        "base": 100,
        "per_intimacy": 2,      # 每点亲密度额外加成
    },
    "combat_bonus": 0.10,       # 组队战斗加成10%
}

# ==================== 师徒传承加成配置 ====================

MASTER_APPRENTICE_BONUSES = {
    "apprentice": {
        "cultivation_speed": 0.10,  # 徒弟修炼速度加成10%
        "exp_bonus": 0.15,          # 徒弟经验获取加成15%
        "technique_learning": 0.20, # 功法学习成功率加成20%
    },
    "master": {
        "respect_bonus": 0.05,      # 师父声望获取加成5%
        "karma_bonus": 0.10,        # 师父业力获取加成10%
        "teaching_reward_exp": 50,  # 每次传授获得修为
    }
}

# ==================== 好友互动配置 ====================

FRIEND_INTERACTIONS = {
    "chat": {
        "name": "交谈",
        "description": "与好友交谈，增进感情",
        "intimacy_change": 2,
        "trust_change": 1,
        "cooldown_hours": 1,
        "exp_bonus": 0,
        "cultivation_bonus": 0,
    },
    "gift": {
        "name": "赠送礼物",
        "description": "赠送礼物给好友，大幅提升好感",
        "intimacy_change": 5,
        "trust_change": 3,
        "cooldown_hours": 24,
        "exp_bonus": 0,
        "cultivation_bonus": 0,
    },
    "help": {
        "name": "帮助",
        "description": "帮助好友解决问题",
        "intimacy_change": 8,
        "trust_change": 5,
        "cooldown_hours": 12,
        "exp_bonus": 0,
        "cultivation_bonus": 0,
    },
    "duel": {
        "name": "切磋",
        "description": "与好友切磋武艺，增加好感度和战斗经验",
        "intimacy_change": 3,
        "trust_change": 2,
        "cooldown_hours": 6,
        "exp_bonus": 50,  # 战斗经验加成
        "cultivation_bonus": 0,
    },
    "discuss_dao": {
        "name": "论道",
        "description": "与好友论道，交流修炼心得，增加修炼感悟",
        "intimacy_change": 4,
        "trust_change": 3,
        "cooldown_hours": 4,
        "exp_bonus": 0,
        "cultivation_bonus": 0.05,  # 5%修炼速度加成（持续）
        "insight_bonus": 10,  # 修炼感悟
    },
    "cultivate_together": {
        "name": "共修",
        "description": "与好友共同修炼，双方修炼效率提升",
        "intimacy_change": 6,
        "trust_change": 4,
        "cooldown_hours": 8,
        "exp_bonus": 100,
        "cultivation_bonus": 0.10,  # 10%修炼速度加成（本次）
    },
}

# ==================== 仇敌互动配置 ====================

ENEMY_INTERACTIONS = {
    "offend": {
        "hatred_change": 10,
        "intimacy_change": -5,
        "trust_change": -5,
    },
    "defeat": {
        "hatred_change": 20,
        "intimacy_change": -10,
        "trust_change": -10,
    },
    "revenge": {
        "hatred_change": -30,
        "intimacy_change": -5,
        "trust_change": 0,
    },
    "forgive": {
        "hatred_change": -50,
        "intimacy_change": 5,
        "trust_change": 10,
    },
}

# ==================== 亲密度等级配置 ====================

INTIMACY_LEVELS = [
    {"name": "初识", "min": 0, "max": 20, "bonus": SocialBonus()},
    {"name": "熟悉", "min": 21, "max": 40, "bonus": SocialBonus(cultivation_speed=0.02)},
    {"name": "亲近", "min": 41, "max": 60, "bonus": SocialBonus(cultivation_speed=0.05, exp_bonus=0.05)},
    {"name": "情深", "min": 61, "max": 80, "bonus": SocialBonus(cultivation_speed=0.08, exp_bonus=0.08, combat_bonus=0.05)},
    {"name": "至爱", "min": 81, "max": 100, "bonus": SocialBonus(cultivation_speed=0.10, exp_bonus=0.10, combat_bonus=0.10, luck_bonus=0.05)},
]

# ==================== 信任度等级配置 ====================

TRUST_LEVELS = [
    {"name": "怀疑", "min": 0, "max": 20},
    {"name": "谨慎", "min": 21, "max": 40},
    {"name": "信任", "min": 41, "max": 60},
    {"name": "信赖", "min": 61, "max": 80},
    {"name": "生死之交", "min": 81, "max": 100},
]

# ==================== 仇恨度等级配置 ====================

HATRED_LEVELS = [
    {"name": "轻微不满", "min": 0, "max": 20},
    {"name": "厌恶", "min": 21, "max": 40},
    {"name": "憎恨", "min": 41, "max": 60},
    {"name": "深仇大恨", "min": 61, "max": 80},
    {"name": "不共戴天", "min": 81, "max": 100},
]

# ==================== 结为道侣条件 ====================

DAO_LV_REQUIREMENTS = {
    "min_intimacy": 80,
    "min_trust": 70,
    "max_hatred": 0,
    "min_realm": 1,  # 最低炼气期
    "both_consent": True,
}

# ==================== 拜师条件 ====================

APPRENTICE_REQUIREMENTS = {
    "min_intimacy": 30,
    "min_trust": 40,
    "max_realm_diff": 2,  # 师父境界不能低于徒弟超过2级
    "master_min_realm": 2,  # 师父最低筑基期
}

# ==================== 复仇任务配置 ====================

REVENGE_QUEST_TEMPLATES = [
    {
        "name": "血债血偿",
        "description": "击败仇敌{name}，为过去的恩怨做个了断",
        "objective": "defeat_enemy",
        "rewards": {
            "exp": 500,
            "karma": -10,
            "reputation": 20,
        }
    },
    {
        "name": "讨回公道",
        "description": "在众人面前击败{name}，让其颜面尽失",
        "objective": "public_defeat",
        "rewards": {
            "exp": 800,
            "karma": -5,
            "reputation": 50,
        }
    },
    {
        "name": "以牙还牙",
        "description": "对{name}进行报复，让其也尝尝被羞辱的滋味",
        "objective": "humiliate",
        "rewards": {
            "exp": 1000,
            "karma": -20,
            "reputation": 30,
        }
    },
]

# ==================== 社交事件配置 ====================

SOCIAL_EVENTS = {
    "friend_meet": {
        "name": "偶遇好友",
        "description": "在{location}偶遇{friend_name}，相谈甚欢",
        "intimacy_change": 5,
        "probability": 0.1,
    },
    "enemy_encounter": {
        "name": "狭路相逢",
        "description": "在{location}遇到仇敌{enemy_name}，气氛紧张",
        "hatred_change": 5,
        "probability": 0.05,
    },
    "dao_lv_support": {
        "name": "道侣相助",
        "description": "你的道侣{partner_name}在修炼中给予你指点",
        "exp_bonus": 50,
        "probability": 0.2,
    },
    "master_guidance": {
        "name": "师父指点",
        "description": "师父{master_name}传授你修炼心得",
        "exp_bonus": 100,
        "probability": 0.15,
    },
}


# ==================== 辅助函数 ====================

def get_intimacy_level(intimacy: int) -> Dict[str, Any]:
    """根据亲密度获取等级信息"""
    for level in INTIMACY_LEVELS:
        if level["min"] <= intimacy <= level["max"]:
            return level
    return INTIMACY_LEVELS[0]


def get_trust_level(trust: int) -> Dict[str, Any]:
    """根据信任度获取等级信息"""
    for level in TRUST_LEVELS:
        if level["min"] <= trust <= level["max"]:
            return level
    return TRUST_LEVELS[0]


def get_hatred_level(hatred: int) -> Dict[str, Any]:
    """根据仇恨度获取等级信息"""
    for level in HATRED_LEVELS:
        if level["min"] <= hatred <= level["max"]:
            return level
    return HATRED_LEVELS[0]


def can_become_dao_lv(intimacy: int, trust: int, hatred: int) -> bool:
    """检查是否可以结为道侣"""
    return (
        intimacy >= DAO_LV_REQUIREMENTS["min_intimacy"] and
        trust >= DAO_LV_REQUIREMENTS["min_trust"] and
        hatred <= DAO_LV_REQUIREMENTS["max_hatred"]
    )


def can_become_apprentice(intimacy: int, trust: int, master_realm: int, apprentice_realm: int) -> bool:
    """检查是否可以拜师"""
    realm_diff = master_realm - apprentice_realm
    return (
        intimacy >= APPRENTICE_REQUIREMENTS["min_intimacy"] and
        trust >= APPRENTICE_REQUIREMENTS["min_trust"] and
        realm_diff <= APPRENTICE_REQUIREMENTS["max_realm_diff"] and
        master_realm >= APPRENTICE_REQUIREMENTS["master_min_realm"]
    )


def calculate_dual_cultivation_exp(base_exp: int, intimacy: int, realm_diff: int) -> int:
    """计算双修获得的经验"""
    # 基础经验
    exp = base_exp

    # 亲密度加成
    intimacy_level = get_intimacy_level(intimacy)
    intimacy_multiplier = DualCultivationConfig.intimacy_bonus.get(intimacy_level["name"], 1.0)
    exp = int(exp * intimacy_multiplier)

    # 境界差距惩罚
    penalty_key = min(abs(realm_diff), max(DualCultivationConfig.realm_penalty.keys()))
    realm_multiplier = DualCultivationConfig.realm_penalty.get(penalty_key, 0.3)
    exp = int(exp * realm_multiplier)

    return exp


def get_dao_lv_bonuses() -> Dict[str, Any]:
    """获取道侣加成配置"""
    return DAO_LV_BONUSES


def get_master_apprentice_bonuses() -> Dict[str, Any]:
    """获取师徒加成配置"""
    return MASTER_APPRENTICE_BONUSES
