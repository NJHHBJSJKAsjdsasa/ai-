"""
任务配置模块
定义主线任务、支线任务模板和日常任务配置
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class QuestType(Enum):
    """任务类型"""
    MAIN = "main"      # 主线任务
    SIDE = "side"      # 支线任务
    DAILY = "daily"    # 日常任务


class ObjectiveType(Enum):
    """任务目标类型"""
    CULTIVATION = "cultivation"    # 修炼
    COMBAT = "combat"              # 战斗
    COLLECTION = "collection"      # 收集
    EXPLORATION = "exploration"    # 探索


@dataclass
class QuestReward:
    """任务奖励数据类"""
    exp: int = 0                    # 经验值
    spirit_stones: int = 0          # 灵石
    items: List[Dict[str, Any]] = field(default_factory=list)  # 道具列表 [{"name": "道具名", "count": 数量}]
    techniques: List[str] = field(default_factory=list)        # 功法奖励
    reputation: int = 0             # 声望
    karma: int = 0                  # 业力

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "exp": self.exp,
            "spirit_stones": self.spirit_stones,
            "items": self.items,
            "techniques": self.techniques,
            "reputation": self.reputation,
            "karma": self.karma
        }


@dataclass
class QuestTemplate:
    """任务模板数据类"""
    id: str                         # 任务唯一ID
    name: str                       # 任务名称
    description: str                # 任务描述
    quest_type: QuestType           # 任务类型
    objective_type: ObjectiveType   # 目标类型
    objective_target: str           # 目标对象
    objective_count: int = 1        # 目标数量
    min_level: int = 0              # 最低境界要求
    max_level: int = 99             # 最高境界要求
    pre_quest_id: str = None        # 前置任务ID
    rewards: QuestReward = field(default_factory=QuestReward)  # 奖励
    is_repeatable: bool = False     # 是否可重复

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "objective_type": self.objective_type.value,
            "objective_target": self.objective_target,
            "objective_count": self.objective_count,
            "min_level": self.min_level,
            "max_level": self.max_level,
            "pre_quest_id": self.pre_quest_id,
            "rewards": self.rewards.to_dict(),
            "is_repeatable": self.is_repeatable
        }


# ==================== 主线任务配置 ====================
# 凡人修仙传风格的主线剧情任务

MAIN_QUESTS: List[QuestTemplate] = [
    # 第一章：初入修仙
    QuestTemplate(
        id="main_001",
        name="初入七玄",
        description="你来到彩霞山七玄门，开始了修仙之路。先进行基础修炼，熟悉灵气运转。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="practice",
        objective_count=5,
        min_level=0,
        max_level=0,
        rewards=QuestReward(exp=100, spirit_stones=50, reputation=10)
    ),
    QuestTemplate(
        id="main_002",
        name="神手谷试炼",
        description="墨大夫要求你前往神手谷采集草药，途中可能会遇到危险。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="神手谷",
        objective_count=1,
        min_level=0,
        max_level=0,
        pre_quest_id="main_001",
        rewards=QuestReward(exp=150, spirit_stones=80, items=[{"name": "止血草", "count": 3}])
    ),
    QuestTemplate(
        id="main_003",
        name="突破炼气",
        description="积累足够的修为，突破到炼气期，正式踏入修仙之门。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="breakthrough",
        objective_count=1,
        min_level=0,
        max_level=0,
        pre_quest_id="main_002",
        rewards=QuestReward(
            exp=300,
            spirit_stones=200,
            reputation=50,
            techniques=["基础吐纳法"]
        )
    ),

    # 第二章：黄枫谷
    QuestTemplate(
        id="main_004",
        name="前往黄枫谷",
        description="七玄门已无法满足你的修炼需求，前往越国七大派之一的黄枫谷。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="黄枫谷",
        objective_count=1,
        min_level=1,
        max_level=1,
        pre_quest_id="main_003",
        rewards=QuestReward(exp=200, spirit_stones=100, reputation=30)
    ),
    QuestTemplate(
        id="main_005",
        name="谷中修炼",
        description="在黄枫谷中潜心修炼，提升修为。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="practice",
        objective_count=10,
        min_level=1,
        max_level=1,
        pre_quest_id="main_004",
        rewards=QuestReward(exp=400, spirit_stones=150)
    ),
    QuestTemplate(
        id="main_006",
        name="初次试炼",
        description="黄枫谷安排新入弟子进行试炼，击败试炼妖兽证明自己的实力。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.COMBAT,
        objective_target="defeat_monster",
        objective_count=3,
        min_level=1,
        max_level=2,
        pre_quest_id="main_005",
        rewards=QuestReward(
            exp=500,
            spirit_stones=300,
            items=[{"name": "炼气丹", "count": 2}],
            reputation=50
        )
    ),
    QuestTemplate(
        id="main_007",
        name="筑基之路",
        description="为突破筑基期做准备，收集筑基所需的材料。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.COLLECTION,
        objective_target="collect_material",
        objective_count=5,
        min_level=1,
        max_level=2,
        pre_quest_id="main_006",
        rewards=QuestReward(exp=600, spirit_stones=400, items=[{"name": "筑基丹", "count": 1}])
    ),
    QuestTemplate(
        id="main_008",
        name="突破筑基",
        description="服用筑基丹，突破到筑基期，寿元大增。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="breakthrough",
        objective_count=1,
        min_level=1,
        max_level=2,
        pre_quest_id="main_007",
        rewards=QuestReward(
            exp=1000,
            spirit_stones=800,
            reputation=100,
            techniques=["御剑术"]
        )
    ),

    # 第三章：血色禁地
    QuestTemplate(
        id="main_009",
        name="禁地传闻",
        description="听说血色禁地即将开启，里面藏有上古修士留下的宝物。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="血色禁地",
        objective_count=1,
        min_level=2,
        max_level=3,
        pre_quest_id="main_008",
        rewards=QuestReward(exp=500, spirit_stones=200, reputation=30)
    ),
    QuestTemplate(
        id="main_010",
        name="禁地探险",
        description="在血色禁地中探索，寻找机缘。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="explore_secret",
        objective_count=3,
        min_level=2,
        max_level=3,
        pre_quest_id="main_009",
        rewards=QuestReward(
            exp=800,
            spirit_stones=500,
            items=[{"name": "千年灵草", "count": 2}, {"name": "古宝碎片", "count": 1}]
        )
    ),
    QuestTemplate(
        id="main_011",
        name="禁地厮杀",
        description="禁地内危机四伏，击败其他觊觎宝物的修士和妖兽。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.COMBAT,
        objective_target="defeat_enemy",
        objective_count=5,
        min_level=2,
        max_level=4,
        pre_quest_id="main_010",
        rewards=QuestReward(exp=1000, spirit_stones=600, karma=-20)
    ),
    QuestTemplate(
        id="main_012",
        name="结丹准备",
        description="收集结丹所需的珍贵材料，为突破金丹期做准备。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.COLLECTION,
        objective_target="collect_rare_material",
        objective_count=3,
        min_level=2,
        max_level=3,
        pre_quest_id="main_011",
        rewards=QuestReward(
            exp=1200,
            spirit_stones=1000,
            items=[{"name": "结丹期丹药", "count": 1}]
        )
    ),
    QuestTemplate(
        id="main_013",
        name="突破结丹",
        description="凝聚金丹，突破到结丹期，成为真正的强者。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="breakthrough",
        objective_count=1,
        min_level=2,
        max_level=3,
        pre_quest_id="main_012",
        rewards=QuestReward(
            exp=2000,
            spirit_stones=1500,
            reputation=200,
            techniques=["金丹真火"]
        )
    ),

    # 第四章：乱星海
    QuestTemplate(
        id="main_014",
        name="远赴星海",
        description="为了寻找更多的修炼资源，决定前往乱星海。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="乱星海",
        objective_count=1,
        min_level=3,
        max_level=4,
        pre_quest_id="main_013",
        rewards=QuestReward(exp=800, spirit_stones=500, reputation=50)
    ),
    QuestTemplate(
        id="main_015",
        name="星宫入门",
        description="拜入星宫，获得更好的修炼环境。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="星宫",
        objective_count=1,
        min_level=3,
        max_level=4,
        pre_quest_id="main_014",
        rewards=QuestReward(exp=1000, spirit_stones=800, reputation=100)
    ),
    QuestTemplate(
        id="main_016",
        name="虚天殿开启",
        description="虚天殿即将开启，据说里面有上古至宝虚天鼎。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="虚天殿",
        objective_count=1,
        min_level=4,
        max_level=5,
        pre_quest_id="main_015",
        rewards=QuestReward(exp=1500, spirit_stones=1000)
    ),
    QuestTemplate(
        id="main_017",
        name="元婴之路",
        description="为突破元婴期做准备，需要大量的积累和机缘。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="practice",
        objective_count=30,
        min_level=4,
        max_level=5,
        pre_quest_id="main_016",
        rewards=QuestReward(exp=3000, spirit_stones=2000)
    ),
    QuestTemplate(
        id="main_018",
        name="突破元婴",
        description="元婴大成，突破到元婴期，成为一方老祖。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="breakthrough",
        objective_count=1,
        min_level=4,
        max_level=5,
        pre_quest_id="main_017",
        rewards=QuestReward(
            exp=5000,
            spirit_stones=3000,
            reputation=500,
            techniques=["元婴出窍"]
        )
    ),

    # 第五章：化神飞升
    QuestTemplate(
        id="main_019",
        name="飞升之秘",
        description="寻找飞升灵界的方法，这是每个化神修士的终极目标。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="飞升通道",
        objective_count=1,
        min_level=5,
        max_level=6,
        pre_quest_id="main_018",
        rewards=QuestReward(exp=2000, spirit_stones=1500)
    ),
    QuestTemplate(
        id="main_020",
        name="化神大成",
        description="突破到化神期，成为人界顶尖存在。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.CULTIVATION,
        objective_target="breakthrough",
        objective_count=1,
        min_level=5,
        max_level=6,
        pre_quest_id="main_019",
        rewards=QuestReward(
            exp=8000,
            spirit_stones=5000,
            reputation=1000,
            techniques=["化神领域"]
        )
    ),
    QuestTemplate(
        id="main_021",
        name="飞升灵界",
        description="成功飞升灵界，开启新的修仙篇章。",
        quest_type=QuestType.MAIN,
        objective_type=ObjectiveType.EXPLORATION,
        objective_target="灵界",
        objective_count=1,
        min_level=6,
        max_level=7,
        pre_quest_id="main_020",
        rewards=QuestReward(
            exp=10000,
            spirit_stones=10000,
            reputation=2000,
            karma=100
        )
    ),
]

# ==================== 支线任务模板配置 ====================
# 用于随机生成支线任务

SIDE_QUEST_TEMPLATES: List[Dict[str, Any]] = [
    # 修炼类支线
    {
        "name_prefix": ["潜心", "苦修", "闭关", "勤加"],
        "name_suffix": ["修炼", "打坐", "吐纳", "炼气"],
        "description_templates": [
            "{location}的灵气浓郁，适合修炼。完成{count}次修炼。",
            "听闻{location}有灵气汇聚，前往修炼{count}次。",
            "为了提升修为，需要在{location}修炼{count}次。"
        ],
        "objective_type": ObjectiveType.CULTIVATION,
        "objective_target": "practice",
        "min_count": 3,
        "max_count": 15,
        "rewards": {
            "exp_multiplier": 20,
            "spirit_stones_multiplier": 10,
            "reputation_range": [5, 20]
        }
    },
    # 战斗类支线
    {
        "name_prefix": ["除妖", "斩魔", "讨伐", "清剿"],
        "name_suffix": ["妖兽", "邪修", "魔道", "恶徒"],
        "description_templates": [
            "{location}附近出现了{enemy}，前往击败{count}只。",
            "村民求助，{location}有{enemy}作乱，击败{count}只为民除害。",
            "门派任务：清剿{location}的{enemy}，需击败{count}只。"
        ],
        "objective_type": ObjectiveType.COMBAT,
        "objective_target": "defeat_monster",
        "min_count": 2,
        "max_count": 10,
        "rewards": {
            "exp_multiplier": 30,
            "spirit_stones_multiplier": 15,
            "reputation_range": [10, 30],
            "karma_range": [-15, -5]
        }
    },
    # 收集类支线
    {
        "name_prefix": ["采集", "搜寻", "收集", "寻觅"],
        "name_suffix": ["灵草", "矿石", "材料", "灵药"],
        "description_templates": [
            "炼丹师需要{material}，前往{location}收集{count}份。",
            "{location}盛产{material}，收集{count}份交给门派。",
            "炼器急需{material}，去{location}找{count}份回来。"
        ],
        "objective_type": ObjectiveType.COLLECTION,
        "objective_target": "collect_material",
        "min_count": 3,
        "max_count": 10,
        "rewards": {
            "exp_multiplier": 15,
            "spirit_stones_multiplier": 20,
            "reputation_range": [5, 15]
        }
    },
    # 探索类支线
    {
        "name_prefix": ["探索", "调查", "寻访", "勘察"],
        "name_suffix": ["秘境", "古迹", "洞府", "遗迹"],
        "description_templates": [
            "{location}发现了一处{place}，前往探索{count}次。",
            "传闻{location}有{place}现世，探索{count}次寻找机缘。",
            "门派长老怀疑{location}有{place}，前去调查{count}次。"
        ],
        "objective_type": ObjectiveType.EXPLORATION,
        "objective_target": "explore_location",
        "min_count": 1,
        "max_count": 5,
        "rewards": {
            "exp_multiplier": 25,
            "spirit_stones_multiplier": 12,
            "reputation_range": [10, 25]
        }
    },
]

# 支线任务地点池
SIDE_QUEST_LOCATIONS = [
    "彩霞山", "神手谷", "黄枫谷", "万兽山脉", "天元城",
    "天元坊市", "血色禁地", "星宫", "虚天殿", "灵界入口"
]

# 支线任务敌人池
SIDE_QUEST_ENEMIES = [
    "野狼", "山猪", "妖蛇", "毒蝎", "邪修", "魔道弟子",
    "妖兽", "鬼物", "僵尸", "恶灵"
]

# 支线任务材料池
SIDE_QUEST_MATERIALS = [
    "止血草", "回灵草", "百年人参", "灵芝", "朱果",
    "玄铁矿石", "寒铁", "灵木", "妖兽内丹", "灵石碎片"
]

# 支线任务地点类型池
SIDE_QUEST_PLACES = [
    "古修洞府", "废弃药园", "妖兽巢穴", "地下溶洞",
    "神秘祭坛", "上古战场", "灵泉之眼", "藏宝之地"
]

# ==================== 日常任务配置 ====================

DAILY_QUEST_TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "每日修炼",
        "description": "坚持每日修炼，完成{count}次修炼。",
        "objective_type": ObjectiveType.CULTIVATION,
        "objective_target": "practice",
        "min_count": 3,
        "max_count": 5,
        "rewards": {
            "exp": 100,
            "spirit_stones": 50,
            "reputation": 5
        }
    },
    {
        "name": "除妖卫道",
        "description": "维护一方平安，击败{count}只妖兽。",
        "objective_type": ObjectiveType.COMBAT,
        "objective_target": "defeat_monster",
        "min_count": 2,
        "max_count": 5,
        "rewards": {
            "exp": 150,
            "spirit_stones": 80,
            "reputation": 10
        }
    },
    {
        "name": "采集灵草",
        "description": "为门派采集{count}份灵草。",
        "objective_type": ObjectiveType.COLLECTION,
        "objective_target": "collect_herb",
        "min_count": 3,
        "max_count": 8,
        "rewards": {
            "exp": 80,
            "spirit_stones": 60,
            "reputation": 5
        }
    },
    {
        "name": "探索秘境",
        "description": "探索未知区域{count}次，寻找机缘。",
        "objective_type": ObjectiveType.EXPLORATION,
        "objective_target": "explore",
        "min_count": 1,
        "max_count": 3,
        "rewards": {
            "exp": 120,
            "spirit_stones": 40,
            "reputation": 8
        }
    },
    {
        "name": "打坐静心",
        "description": "静心打坐{count}次，稳固道心。",
        "objective_type": ObjectiveType.CULTIVATION,
        "objective_target": "meditate",
        "min_count": 2,
        "max_count": 4,
        "rewards": {
            "exp": 60,
            "spirit_stones": 30,
            "karma": 5
        }
    },
]

# 日常任务每天可接取数量
DAILY_QUEST_COUNT = 3

# 日常任务刷新时间（小时）
DAILY_QUEST_REFRESH_HOUR = 0


# ==================== 辅助函数 ====================

def get_main_quest_by_id(quest_id: str) -> Optional[QuestTemplate]:
    """根据ID获取主线任务"""
    for quest in MAIN_QUESTS:
        if quest.id == quest_id:
            return quest
    return None


def get_next_main_quest(current_quest_id: str) -> Optional[QuestTemplate]:
    """获取下一个主线任务"""
    current = get_main_quest_by_id(current_quest_id)
    if not current:
        return None

    for quest in MAIN_QUESTS:
        if quest.pre_quest_id == current_quest_id:
            return quest
    return None


def get_available_main_quests(player_level: int, completed_quests: List[str]) -> List[QuestTemplate]:
    """
    获取玩家可接取的主线任务

    Args:
        player_level: 玩家境界等级
        completed_quests: 已完成的主线任务ID列表

    Returns:
        可接取的主线任务列表
    """
    available = []
    for quest in MAIN_QUESTS:
        # 检查等级要求
        if quest.min_level > player_level or quest.max_level < player_level:
            continue

        # 检查是否已完成
        if quest.id in completed_quests:
            continue

        # 检查前置任务
        if quest.pre_quest_id and quest.pre_quest_id not in completed_quests:
            continue

        available.append(quest)

    return available


def get_main_quest_chapter(quest_id: str) -> int:
    """
    获取主线任务所属章节

    Args:
        quest_id: 任务ID

    Returns:
        章节号（1-5）
    """
    chapter_map = {
        "main_001": 1, "main_002": 1, "main_003": 1,
        "main_004": 2, "main_005": 2, "main_006": 2, "main_007": 2, "main_008": 2,
        "main_009": 3, "main_010": 3, "main_011": 3, "main_012": 3, "main_013": 3,
        "main_014": 4, "main_015": 4, "main_016": 4, "main_017": 4, "main_018": 4,
        "main_019": 5, "main_020": 5, "main_021": 5,
    }
    return chapter_map.get(quest_id, 0)


def get_chapter_name(chapter: int) -> str:
    """获取章节名称"""
    chapter_names = {
        1: "初入修仙",
        2: "黄枫谷",
        3: "血色禁地",
        4: "乱星海",
        5: "化神飞升"
    }
    return chapter_names.get(chapter, "未知章节")
