"""
游戏数值配置模块
定义游戏的各种数值参数
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import random


@dataclass
class SpiritRoot:
    """灵根数据类"""
    name: str              # 灵根名称
    probability: float     # 出现概率（0-1）
    speed_multiplier: float  # 修炼速度倍率
    description: str       # 描述
    elements: List[str]    # 五行属性


# 灵根配置
SPIRIT_ROOTS: Dict[str, SpiritRoot] = {
    "tian": SpiritRoot(
        name="天灵根",
        probability=0.01,
        speed_multiplier=2.0,
        description="天赐灵根，修炼速度极快，万中无一的天才。",
        elements=["金", "木", "水", "火", "土"]
    ),
    "shuang": SpiritRoot(
        name="双灵根",
        probability=0.05,
        speed_multiplier=1.5,
        description="双属性灵根，修炼速度较快，门派核心弟子。",
        elements=["随机两种"]
    ),
    "san": SpiritRoot(
        name="三灵根",
        probability=0.20,
        speed_multiplier=1.0,
        description="三属性灵根，修炼速度普通，大多数修士。",
        elements=["随机三种"]
    ),
    "si": SpiritRoot(
        name="四灵根",
        probability=0.50,
        speed_multiplier=0.7,
        description="四属性灵根，修炼速度较慢，资质平庸。",
        elements=["随机四种"]
    ),
    "wu": SpiritRoot(
        name="五灵根",
        probability=0.24,
        speed_multiplier=0.5,
        description="五属性灵根，修炼速度极慢，俗称伪灵根。",
        elements=["金", "木", "水", "火", "土"]
    ),
}


# 游戏主配置
GAME_CONFIG = {
    # 修炼相关
    "cultivation": {
        "base_exp_per_practice": 10,      # 基础每次修炼获得经验
        "practice_time_days": 30,          # 每次修炼消耗天数
        "max_practice_per_session": 10,    # 每次最多连续修炼次数
        "breakthrough_cooldown_days": 365, # 突破冷却时间（天）
    },
    
    # 时间相关
    "time": {
        "start_year": 1,                   # 游戏开始年份
        "start_month": 1,                  # 游戏开始月份
        "start_day": 1,                    # 游戏开始日期
        "days_per_month": 30,              # 每月天数
        "months_per_year": 12,             # 每年月数
    },
    
    # 属性相关
    "stats": {
        "initial_health": 100,             # 初始生命值
        "initial_spiritual_power": 50,     # 初始灵力
        "initial_spirit_stones": 100,      # 初始灵石
        "initial_fortune": 50,             # 初始福缘（0-100）
        "initial_karma": 0,                # 初始业力（-1000到1000）
        "max_health_multiplier": 10,       # 生命值上限 = 境界 * 倍率
        "max_spiritual_power_multiplier": 5,  # 灵力上限 = 境界 * 倍率
    },
    
    # 突破相关
    "breakthrough": {
        "injury_chance": 0.3,              # 失败受伤概率
        "injury_duration_days": 180,       # 受伤持续时间
        "exp_loss_on_failure": 0.1,        # 失败经验损失比例
        "death_chance_on_failure": 0.05,   # 失败死亡概率
        "fortune_bonus_per_point": 0.01,   # 每点福缘增加的成功率
        "karma_penalty_threshold": -100,   # 业力惩罚阈值
        "karma_bonus_threshold": 100,      # 业力奖励阈值
    },
    
    # 死亡相关
    "death": {
        "inheritance_ratio": 0.3,          # 转世继承比例
        "min_inheritance": 100,            # 最小继承经验
        "npc_memory_persistence": 0.5,     # NPC记忆保留比例
    },
    
    # NPC相关
    "npc": {
        "npc_count_per_location": 5,       # 每个地点NPC数量
        "npc_age_min": 16,                 # NPC最小年龄
        "npc_age_max": 500,                # NPC最大年龄
        "npc_realm_max": 5,                # NPC最大境界（化神）
        "npc_interaction_memory_limit": 10, # NPC记忆上限
    },
    
    # 事件相关
    "events": {
        "random_event_chance": 0.1,        # 随机事件触发概率
        "event_cooldown_days": 30,         # 事件冷却时间
        "fortune_event_bonus": 0.05,       # 福缘对事件的影响
    },
    
    # 地图相关
    "world": {
        "locations": [
            # 凡人界 - 区域
            {"name": "镜州", "description": "凡人修仙传故事起始之地，野狼帮与七玄门争斗之处。", "realm_required": 0, "danger_level": "安全", "location_type": "区域", "parent_location": ""},

            # 镜州下属地点
            {"name": "新手村", "description": "凡人居住的村落，灵气稀薄，适合初入修仙之路。", "realm_required": 0, "danger_level": "安全", "location_type": "城镇", "parent_location": "镜州"},
            {"name": "彩霞山", "description": "七玄门所在之地，山上有彩霞笼罩，风景秀丽。", "realm_required": 0, "danger_level": "普通", "location_type": "门派", "parent_location": "镜州"},
            {"name": "神手谷", "description": "彩霞山后山山谷，墨大夫隐居之地。", "realm_required": 0, "danger_level": "危险", "location_type": "野外", "parent_location": "彩霞山"},

            # 越国 - 区域
            {"name": "越国", "description": "越国七大派所在之地，修仙资源丰富。", "realm_required": 1, "danger_level": "普通", "location_type": "区域", "parent_location": ""},

            # 越国下属地点
            {"name": "黄枫谷", "description": "越国七大派之一，韩立曾在此修行。", "realm_required": 1, "danger_level": "普通", "location_type": "门派", "parent_location": "越国"},
            {"name": "掩月宗", "description": "越国七大派之一，以女修为主。", "realm_required": 1, "danger_level": "普通", "location_type": "门派", "parent_location": "越国"},
            {"name": "血色禁地", "description": "越国境内的危险秘境，藏有重宝但也危机四伏。", "realm_required": 2, "danger_level": "危险", "location_type": "秘境", "parent_location": "越国"},

            # 天元城
            {"name": "天元城", "description": "修仙大城，繁华热闹，各种资源汇聚。", "realm_required": 1, "danger_level": "安全", "location_type": "城镇", "parent_location": ""},
            {"name": "天元坊市", "description": "天元城的修仙坊市，可以交易各种物品。", "realm_required": 1, "danger_level": "安全", "location_type": "城镇", "parent_location": "天元城"},

            # 万兽山脉
            {"name": "万兽山脉", "description": "妖兽横行的山脉，危险与机遇并存。", "realm_required": 2, "danger_level": "危险", "location_type": "区域", "parent_location": ""},
            {"name": "山脉外围", "description": "万兽山脉外围，有低阶妖兽出没。", "realm_required": 2, "danger_level": "普通", "location_type": "野外", "parent_location": "万兽山脉"},
            {"name": "山脉深处", "description": "万兽山脉深处，高阶妖兽盘踞。", "realm_required": 3, "danger_level": "危险", "location_type": "野外", "parent_location": "万兽山脉"},
            {"name": "妖兽巢穴", "description": "万兽山脉最深处，元婴期妖兽的领地。", "realm_required": 4, "danger_level": "绝境", "location_type": "野外", "parent_location": "万兽山脉"},

            # 海外
            {"name": "海外", "description": "海外修仙圣地，灵气充沛。", "realm_required": 3, "danger_level": "普通", "location_type": "区域", "parent_location": ""},
            {"name": "星宫", "description": "乱星海最大势力，统治乱星海多年。", "realm_required": 3, "danger_level": "普通", "location_type": "门派", "parent_location": "海外"},
            {"name": "虚天殿", "description": "上古修士遗留的宫殿，藏有至宝虚天鼎。", "realm_required": 4, "danger_level": "危险", "location_type": "秘境", "parent_location": "海外"},

            # 灵界
            {"name": "灵界", "description": "人界之上的界面，灵气更加充沛。", "realm_required": 5, "danger_level": "危险", "location_type": "区域", "parent_location": ""},
            {"name": "天渊城", "description": "灵界人族边境重镇，抵御异族入侵。", "realm_required": 5, "danger_level": "危险", "location_type": "城镇", "parent_location": "灵界"},
            {"name": "蛮荒世界", "description": "灵界蛮荒之地，有各种异兽和天才地宝。", "realm_required": 6, "danger_level": "绝境", "location_type": "野外", "parent_location": "灵界"},

            # 仙界
            {"name": "真仙界", "description": "仙界，真仙居住之地。", "realm_required": 8, "danger_level": "普通", "location_type": "区域", "parent_location": ""},
            {"name": "天庭", "description": "仙界最高统治机构，统御万仙。", "realm_required": 9, "danger_level": "安全", "location_type": "门派", "parent_location": "真仙界"},
        ],
    },
}


def generate_spirit_root() -> Tuple[str, SpiritRoot]:
    """
    随机生成灵根
    
    Returns:
        (灵根key, 灵根信息)
    """
    rand = random.random()
    cumulative = 0.0
    
    for key, spirit_root in SPIRIT_ROOTS.items():
        cumulative += spirit_root.probability
        if rand <= cumulative:
            return key, spirit_root
    
    # 默认返回五灵根
    return "wu", SPIRIT_ROOTS["wu"]


def get_spirit_root_info(key: str) -> SpiritRoot:
    """
    获取灵根信息
    
    Args:
        key: 灵根key
        
    Returns:
        灵根信息
    """
    return SPIRIT_ROOTS.get(key, SPIRIT_ROOTS["wu"])


def calculate_cultivation_speed(spirit_root_key: str, location_bonus: float = 1.0, 
                                 pill_bonus: float = 0.0) -> float:
    """
    计算修炼速度
    
    Args:
        spirit_root_key: 灵根key
        location_bonus: 地点加成
        pill_bonus: 丹药加成
        
    Returns:
        修炼速度倍率
    """
    spirit_root = get_spirit_root_info(spirit_root_key)
    base_speed = spirit_root.speed_multiplier
    
    # 总速度 = 基础速度 * 地点加成 + 丹药加成
    total_speed = base_speed * location_bonus + pill_bonus
    
    return max(0.1, total_speed)  # 最低0.1倍速度


def get_config(path: str, default=None):
    """
    获取配置项（带默认值处理）
    
    Args:
        path: 配置路径，如"cultivation.base_exp_per_practice"
        default: 默认值
        
    Returns:
        配置值
    """
    if not path or not isinstance(path, str):
        return default
    
    keys = path.split(".")
    value = GAME_CONFIG
    
    for key in keys:
        if not key:  # 跳过空键
            continue
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def get_config_int(path: str, default: int = 0) -> int:
    """获取整数配置项"""
    value = get_config(path, default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_config_float(path: str, default: float = 0.0) -> float:
    """获取浮点数配置项"""
    value = get_config(path, default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_config_bool(path: str, default: bool = False) -> bool:
    """获取布尔配置项"""
    value = get_config(path, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    return bool(value)
