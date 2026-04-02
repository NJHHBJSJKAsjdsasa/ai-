"""
修仙境界配置模块
定义七层修仙境界体系
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Realm:
    """境界数据类"""
    name: str              # 境界名称
    lifespan: int          # 寿元（年）
    exp_required: int      # 突破所需经验
    exp_to_next: int       # 到下一境界所需经验
    title_self: str        # 自称（如：贫道、本座）
    title_others: str      # 对他人的称呼（如：道友、前辈）
    description: str       # 境界描述
    abilities: List[str]   # 能力列表
    breakthrough_bonus: Dict[str, any]  # 突破奖励


# 七层修仙境界定义
REALMS: Dict[int, Realm] = {
    0: Realm(
        name="凡人",
        lifespan=80,
        exp_required=0,
        exp_to_next=100,
        title_self="在下",
        title_others="兄台",
        description="未入仙道的普通人，寿元有限，生老病死。",
        abilities=["无"],
        breakthrough_bonus={"lifespan": 120}
    ),
    1: Realm(
        name="练气期",
        lifespan=120,
        exp_required=100,
        exp_to_next=500,
        title_self="小修",
        title_others="道友",
        description="引气入体，淬炼肉身，初步感知天地灵气。",
        abilities=["感知灵气", "简单法术", "御器飞行（短暂）"],
        breakthrough_bonus={"lifespan": 200, "spiritual_power": 100}
    ),
    2: Realm(
        name="筑基期",
        lifespan=200,
        exp_required=600,
        exp_to_next=2000,
        title_self="在下",
        title_others="道兄",
        description="筑就道基，稳固根基，可修炼基础功法。",
        abilities=["筑基法术", "炼丹入门", "炼器入门", "御剑飞行"],
        breakthrough_bonus={"lifespan": 500, "spiritual_power": 500}
    ),
    3: Realm(
        name="金丹期",
        lifespan=500,
        exp_required=2600,
        exp_to_next=5000,
        title_self="本修",
        title_others="前辈",
        description="凝结金丹，法力大增，可称一方高手。",
        abilities=["金丹神通", "炼丹精通", "炼器精通", "瞬移短距离"],
        breakthrough_bonus={"lifespan": 1000, "spiritual_power": 2000}
    ),
    4: Realm(
        name="元婴期",
        lifespan=1000,
        exp_required=7600,
        exp_to_next=10000,
        title_self="本座",
        title_others="前辈",
        description="元婴成形，神识大增，可夺舍重生。",
        abilities=["元婴出窍", "神识扫描", "瞬移", "虚空飞行"],
        breakthrough_bonus={"lifespan": 2000, "spiritual_power": 5000}
    ),
    5: Realm(
        name="化神期",
        lifespan=2000,
        exp_required=17600,
        exp_to_next=20000,
        title_self="本尊",
        title_others="大人",
        description="化神成功，触摸天地法则，实力通天。",
        abilities=["法则感悟", "空间神通", "时间感知", "领域展开"],
        breakthrough_bonus={"lifespan": 5000, "spiritual_power": 10000}
    ),
    6: Realm(
        name="渡劫期",
        lifespan=5000,
        exp_required=37600,
        exp_to_next=50000,
        title_self="本圣",
        title_others="圣者",
        description="渡劫成仙，经历天劫考验，半步仙人。",
        abilities=["天劫之力", "法则掌控", "创造小世界", "长生不老"],
        breakthrough_bonus={"lifespan": 999999, "spiritual_power": 50000}
    ),
    7: Realm(
        name="大乘期",
        lifespan=999999,  # 永生
        exp_required=87600,
        exp_to_next=999999,
        title_self="本仙",
        title_others="仙尊",
        description="大乘圆满，飞升仙界，与天地同寿。",
        abilities=["飞升仙界", "不死不灭", "创造生命", "掌控法则"],
        breakthrough_bonus={"immortal": True}
    ),
    8: Realm(
        name="真仙期",
        lifespan=9999999,  # 永生
        exp_required=999999,
        exp_to_next=9999999,
        title_self="本真仙",
        title_others="真仙",
        description="飞升仙界，成为真仙，拥有仙界法则。",
        abilities=["仙界法则", "仙力运用", "长生不老", "瞬移万里"],
        breakthrough_bonus={"immortal": True}
    ),
    9: Realm(
        name="金仙期",
        lifespan=99999999,  # 永生
        exp_required=9999999,
        exp_to_next=99999999,
        title_self="本金仙",
        title_others="金仙",
        description="仙界强者，金仙之位，威震仙界。",
        abilities=["金仙神通", "法则掌控", "创造世界", "万劫不灭"],
        breakthrough_bonus={"immortal": True}
    ),
}

# 境界名称到等级的映射
REALM_NAME_TO_LEVEL = {realm.name: level for level, realm in REALMS.items()}


def get_realm_info(level: int) -> Optional[Realm]:
    """
    获取境界信息
    
    Args:
        level: 境界等级（0-7）
        
    Returns:
        境界信息对象，如果不存在则返回None
    """
    return REALMS.get(level)


def get_realm_by_name(name: str) -> Optional[Realm]:
    """
    根据名称获取境界信息
    
    Args:
        name: 境界名称
        
    Returns:
        境界信息对象，如果不存在则返回None
    """
    level = REALM_NAME_TO_LEVEL.get(name)
    if level is not None:
        return REALMS.get(level)
    return None


def get_realm_title(level: int, for_self: bool = True) -> str:
    """
    获取境界对应的称谓
    
    Args:
        level: 境界等级
        for_self: 是否用于自称
        
    Returns:
        称谓字符串
    """
    realm = REALMS.get(level)
    if realm:
        return realm.title_self if for_self else realm.title_others
    return "道友"


def get_breakthrough_success_rate(current_level: int, player_stats: Dict) -> float:
    """
    计算突破成功率
    
    Args:
        current_level: 当前境界等级
        player_stats: 玩家属性字典
        
    Returns:
        成功率（0-1之间）
    """
    # 基础成功率
    base_rates = {
        0: 0.95,  # 凡人突破到练气
        1: 0.80,  # 练气突破到筑基
        2: 0.60,  # 筑基突破到金丹
        3: 0.40,  # 金丹突破到元婴
        4: 0.25,  # 元婴突破到化神
        5: 0.15,  # 化神突破到渡劫
        6: 0.10,  # 渡劫突破到大乘
    }
    
    base_rate = base_rates.get(current_level, 0.5)
    
    # 福缘加成（每点福缘增加1%成功率）
    fortune_bonus = player_stats.get("fortune", 0) * 0.01
    
    # 业力影响（善业增加，恶业减少）
    karma = player_stats.get("karma", 0)
    karma_bonus = max(-0.2, min(0.2, karma * 0.001))  # 限制在±20%
    
    # 丹药加成（如果有）
    pill_bonus = player_stats.get("pill_bonus", 0)
    
    # 总成功率
    success_rate = base_rate + fortune_bonus + karma_bonus + pill_bonus
    
    # 限制在5%-95%之间
    return max(0.05, min(0.95, success_rate))


def get_realm_progress(current_exp: int, realm_level: int) -> Tuple[int, int, float]:
    """
    获取当前境界的进度
    
    Args:
        current_exp: 当前经验值
        realm_level: 当前境界等级
        
    Returns:
        (当前经验, 需要经验, 进度百分比)
    """
    realm = REALMS.get(realm_level)
    if not realm:
        return (0, 1, 0.0)
    
    exp_required = realm.exp_required
    exp_to_next = realm.exp_to_next
    
    # 计算当前境界内的经验
    exp_in_realm = current_exp - exp_required
    
    # 计算进度
    progress = min(1.0, max(0.0, exp_in_realm / exp_to_next))
    
    return (exp_in_realm, exp_to_next, progress)


def can_breakthrough(current_exp: int, realm_level: int) -> bool:
    """
    检查是否可以突破
    
    Args:
        current_exp: 当前经验值
        realm_level: 当前境界等级
        
    Returns:
        是否可以突破
    """
    realm = REALMS.get(realm_level)
    if not realm:
        return False
    
    return current_exp >= realm.exp_required + realm.exp_to_next


def get_all_realms() -> List[Tuple[int, Realm]]:
    """
    获取所有境界信息
    
    Returns:
        境界列表（等级, 境界信息）
    """
    return [(level, realm) for level, realm in sorted(REALMS.items())]


# 境界图标（用于CLI显示）
REALM_ICONS = {
    0: "👤",  # 凡人
    1: "🌱",  # 练气
    2: "🪨",  # 筑基
    3: "🔮",  # 金丹
    4: "👶",  # 元婴
    5: "👑",  # 化神
    6: "⚡",  # 渡劫
    7: "✨",  # 大乘
}


def get_realm_icon(level: int) -> str:
    """
    获取境界图标
    
    Args:
        level: 境界等级
        
    Returns:
        图标字符串
    """
    return REALM_ICONS.get(level, "❓")
