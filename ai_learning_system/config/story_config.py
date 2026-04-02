"""
剧情系统配置模块
定义主线剧情和支线剧情的数据
参考凡人修仙传小说设计
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class StoryChoice:
    """剧情选择数据类"""
    id: str
    text: str
    next_scene_id: Optional[str] = None
    effects: Dict[str, Any] = field(default_factory=dict)
    condition_type: Optional[str] = None
    condition_value: Optional[str] = None


@dataclass
class StoryDialogue:
    """剧情对话数据类"""
    id: str
    speaker_type: str  # 'npc', 'player', 'narrator'
    speaker_id: Optional[str] = None
    speaker_name: str = ""
    content: str = ""
    emotion: Optional[str] = None
    animation: Optional[str] = None


@dataclass
class StoryScene:
    """剧情场景数据类"""
    id: str
    scene_number: int
    title: str
    background: Optional[str] = None
    location: Optional[str] = None
    npcs: List[str] = field(default_factory=list)
    dialogues: List[StoryDialogue] = field(default_factory=list)
    choices: List[StoryChoice] = field(default_factory=list)


@dataclass
class StoryChapter:
    """剧情章节数据类"""
    id: str
    chapter_number: int
    title: str
    description: str
    story_type: str = "main"  # 'main', 'side'
    realm_required: int = 0
    location_required: Optional[str] = None
    pre_chapter_id: Optional[str] = None
    is_repeatable: bool = False
    scenes: List[StoryScene] = field(default_factory=list)
    rewards: List[Dict[str, Any]] = field(default_factory=list)


# ==================== 凡人修仙传主线剧情 ====================

MAIN_STORY_CHAPTERS: List[StoryChapter] = [
    StoryChapter(
        id="chapter_01",
        chapter_number=1,
        title="七玄门试炼",
        description="韩立参加七玄门入门试炼，开始了修仙之路。",
        story_type="main",
        realm_required=0,
        location_required="彩霞山",
        scenes=[
            StoryScene(
                id="scene_01_01",
                scene_number=1,
                title="入门试炼",
                background="彩霞山山脚，七玄门入门试炼现场",
                location="彩霞山",
                npcs=["王护法", "张铁"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_01_01_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="你站在彩霞山脚下，望着云雾缭绕的山峰，心中充满了对修仙之路的向往。"
                    ),
                    StoryDialogue(
                        id="dlg_01_01_02",
                        speaker_type="npc",
                        speaker_id="wang_hufa",
                        speaker_name="王护法",
                        content="小子，想要入我七玄门，需通过三项试炼。第一项，测灵根！"
                    ),
                    StoryDialogue(
                        id="dlg_01_01_03",
                        speaker_type="player",
                        speaker_name="你",
                        content="弟子明白，请护法开始测试。"
                    ),
                    StoryDialogue(
                        id="dlg_01_01_04",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="灵根测试石发出微弱的光芒..."
                    ),
                    StoryDialogue(
                        id="dlg_01_01_05",
                        speaker_type="npc",
                        speaker_id="wang_hufa",
                        speaker_name="王护法",
                        content="四灵根...资质平庸，但也不是不能修炼。第二项，毅力测试！"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_01_01_01",
                        text="坚定地说：弟子虽资质平庸，但必以勤补拙！",
                        effects={"npc_favor": {"wang_hufa": 10}, "karma": 5}
                    ),
                    StoryChoice(
                        id="choice_01_01_02",
                        text="沉默地点头，默默接受。",
                        effects={"npc_favor": {"wang_hufa": 5}}
                    ),
                    StoryChoice(
                        id="choice_01_01_03",
                        text="面露失望，但还是坚持参加试炼。",
                        effects={"npc_favor": {"wang_hufa": -5}, "karma": -2}
                    ),
                ]
            ),
            StoryScene(
                id="scene_01_02",
                scene_number=2,
                title="毅力考验",
                background="七玄门练功场",
                location="彩霞山",
                npcs=["王护法"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_01_02_01",
                        speaker_type="npc",
                        speaker_id="wang_hufa",
                        speaker_name="王护法",
                        content="这第二项试炼，需要你在烈日下站桩三个时辰。中途退出者，淘汰！"
                    ),
                    StoryDialogue(
                        id="dlg_01_02_02",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="烈日当空，汗水浸透了衣衫。周围已经有不少人放弃离开..."
                    ),
                    StoryDialogue(
                        id="dlg_01_02_03",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="两个时辰过去了，你感到头晕目眩，双腿如灌铅般沉重。"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_01_02_01",
                        text="咬牙坚持，绝不放弃！",
                        next_scene_id="scene_01_03",
                        effects={"health": -10, "willpower": 10, "npc_favor": {"wang_hufa": 15}}
                    ),
                    StoryChoice(
                        id="choice_01_02_02",
                        text="服用随身携带的补气丹（如果有）",
                        next_scene_id="scene_01_03",
                        condition_type="has_item",
                        condition_value="补气丹",
                        effects={"item_consume": "补气丹", "willpower": 5, "npc_favor": {"wang_hufa": 10}}
                    ),
                    StoryChoice(
                        id="choice_01_02_03",
                        text="实在坚持不住，选择放弃。",
                        effects={"story_end": True, "npc_favor": {"wang_hufa": -20}}
                    ),
                ]
            ),
            StoryScene(
                id="scene_01_03",
                scene_number=3,
                title="第三项试炼",
                background="七玄门后山",
                location="彩霞山",
                npcs=["王护法", "墨大夫"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_01_02_04",
                        speaker_type="npc",
                        speaker_id="wang_hufa",
                        speaker_name="王护法",
                        content="好！能在毅力测试中坚持下来，说明你心性尚可。第三项，悟性测试！"
                    ),
                    StoryDialogue(
                        id="dlg_01_02_05",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="你被带到一块刻满符文的石碑前..."
                    ),
                    StoryDialogue(
                        id="dlg_01_02_06",
                        speaker_type="npc",
                        speaker_id="wang_hufa",
                        speaker_name="王护法",
                        content="这是本门的基础功法《长春功》的入门心法，给你一个时辰领悟。"
                    ),
                    StoryDialogue(
                        id="dlg_01_02_07",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="你凝视着石碑上的符文，努力理解其中的含义..."
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_01_03_01",
                        text="专注领悟，进入冥想状态。",
                        effects={"exp": 50, "technique": "长春功入门", "story_complete": True}
                    ),
                    StoryChoice(
                        id="choice_01_03_02",
                        text="尝试用特殊方法记忆符文。",
                        effects={"exp": 30, "intelligence": 2, "story_complete": True}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 100, "condition": "complete"},
            {"type": "item", "item": "七玄门弟子令牌", "quantity": 1, "condition": "complete"},
            {"type": "technique", "item": "长春功", "condition": "complete"},
        ]
    ),
    
    StoryChapter(
        id="chapter_02",
        chapter_number=2,
        title="神手谷奇遇",
        description="在神手谷中，你遇到了神秘的墨大夫...",
        story_type="main",
        realm_required=0,
        location_required="神手谷",
        pre_chapter_id="chapter_01",
        scenes=[
            StoryScene(
                id="scene_02_01",
                scene_number=1,
                title="神秘医者",
                background="神手谷深处，一座简陋的草庐",
                location="神手谷",
                npcs=["墨大夫"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_02_01_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="通过试炼后，你被分配到神手谷，跟随墨大夫学习医术和炼丹。"
                    ),
                    StoryDialogue(
                        id="dlg_02_01_02",
                        speaker_type="npc",
                        speaker_id="mo_doctor",
                        speaker_name="墨大夫",
                        content="小子，我观你资质平庸，但心性尚可。想学我的医术吗？"
                    ),
                    StoryDialogue(
                        id="dlg_02_01_03",
                        speaker_type="player",
                        speaker_name="你",
                        content="弟子愿意学习，请大夫指教。"
                    ),
                    StoryDialogue(
                        id="dlg_02_01_04",
                        speaker_type="npc",
                        speaker_id="mo_doctor",
                        speaker_name="墨大夫",
                        content="学医先学德，我且问你，若遇敌人和友人同时受伤，你先救谁？"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_02_01_01",
                        text="先救友人，因为情谊重要。",
                        effects={"npc_favor": {"mo_doctor": 5}, "karma": 5, "affinity": {"friends": 10}}
                    ),
                    StoryChoice(
                        id="choice_02_01_02",
                        text="先救伤势更重者，不论敌友。",
                        effects={"npc_favor": {"mo_doctor": 15}, "karma": 10, "medical_ethic": 10}
                    ),
                    StoryChoice(
                        id="choice_02_01_03",
                        text="先救敌人，以德报怨。",
                        effects={"npc_favor": {"mo_doctor": 20}, "karma": 15, "reputation": "仁慈"}
                    ),
                ]
            ),
            StoryScene(
                id="scene_02_02",
                scene_number=2,
                title="夜探禁地",
                background="神手谷地下室入口",
                location="神手谷",
                npcs=["墨大夫"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_02_02_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="一个月黑风高的夜晚，你无意中发现墨大夫进入了草庐的地下室..."
                    ),
                    StoryDialogue(
                        id="dlg_02_02_02",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="地下室传来奇怪的声音，似乎有人在痛苦呻吟。"
                    ),
                    StoryDialogue(
                        id="dlg_02_02_03",
                        speaker_type="player",
                        speaker_name="你",
                        content="（心中疑惑）大夫在地下室做什么？"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_02_02_01",
                        text="悄悄跟进去查看。",
                        next_scene_id="scene_02_03",
                        effects={"courage": 5, "stealth": 2}
                    ),
                    StoryChoice(
                        id="choice_02_02_02",
                        text="守在门外，等待大夫出来。",
                        effects={"patience": 5, "npc_favor": {"mo_doctor": 5}}
                    ),
                    StoryChoice(
                        id="choice_02_02_03",
                        text="装作什么都没看见，回去睡觉。",
                        effects={"wisdom": 3, "caution": 5}
                    ),
                ]
            ),
            StoryScene(
                id="scene_02_03",
                scene_number=3,
                title="真相大白",
                background="神手谷地下室",
                location="神手谷",
                npcs=["墨大夫", "张铁"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_02_03_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="地下室中，你看到了令人震惊的一幕——张铁被绑在一张石台上，墨大夫正在对他进行某种仪式..."
                    ),
                    StoryDialogue(
                        id="dlg_02_03_02",
                        speaker_type="npc",
                        speaker_id="zhang_tie",
                        speaker_name="张铁",
                        content="韩立...救...救我...",
                        emotion="痛苦"
                    ),
                    StoryDialogue(
                        id="dlg_02_03_03",
                        speaker_type="npc",
                        speaker_id="mo_doctor",
                        speaker_name="墨大夫",
                        content="哼，既然被你发现了，那就别怪我不客气！"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_02_03_01",
                        text="冲上去救张铁！",
                        effects={"combat": True, "npc_favor": {"zhang_tie": 50}, "karma": 10}
                    ),
                    StoryChoice(
                        id="choice_02_03_02",
                        text="先观察情况，寻找机会。",
                        effects={"wisdom": 5, "stealth": 3}
                    ),
                    StoryChoice(
                        id="choice_02_03_03",
                        text="悄悄退出去，寻求门派帮助。",
                        effects={"wisdom": 3, "caution": 5, "npc_favor": {"zhang_tie": -10}}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 200, "condition": "complete"},
            {"type": "item", "item": "墨大夫的医书", "quantity": 1, "condition": "complete"},
            {"type": "reputation", "value": "识破阴谋", "condition": "complete"},
        ]
    ),
    
    StoryChapter(
        id="chapter_03",
        chapter_number=3,
        title="黄枫谷入门",
        description="离开七玄门，你来到了越国七大派之一的黄枫谷...",
        story_type="main",
        realm_required=1,
        location_required="黄枫谷",
        pre_chapter_id="chapter_02",
        scenes=[
            StoryScene(
                id="scene_03_01",
                scene_number=1,
                title="入门考核",
                background="黄枫谷山门",
                location="黄枫谷",
                npcs=["李化元", "陈师姐"],
                dialogues=[
                    StoryDialogue(
                        id="dlg_03_01_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="经过多年的修炼，你终于达到了练气期，有资格拜入黄枫谷。"
                    ),
                    StoryDialogue(
                        id="dlg_03_01_02",
                        speaker_type="npc",
                        speaker_id="li_huayuan",
                        speaker_name="李化元",
                        content="小子，想要入我黄枫谷，需要通过升仙大会。你可准备好了？"
                    ),
                    StoryDialogue(
                        id="dlg_03_01_03",
                        speaker_type="player",
                        speaker_name="你",
                        content="弟子已经准备好了。"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="choice_03_01_01",
                        text="展示你的修炼成果。",
                        effects={"npc_favor": {"li_huayuan": 10}, "exp": 50}
                    ),
                    StoryChoice(
                        id="choice_03_01_02",
                        text="谦虚地请求前辈指点。",
                        effects={"npc_favor": {"li_huayuan": 15}, "wisdom": 3}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 300, "condition": "complete"},
            {"type": "item", "item": "黄枫谷弟子服饰", "quantity": 1, "condition": "complete"},
            {"type": "technique", "item": "黄枫谷基础功法", "condition": "complete"},
        ]
    ),
]

# ==================== 支线剧情 ====================

SIDE_STORY_CHAPTERS: List[StoryChapter] = [
    StoryChapter(
        id="side_01",
        chapter_number=1,
        title="山中奇遇",
        description="在彩霞山采药时，你遇到了一位神秘的老者...",
        story_type="side",
        realm_required=0,
        location_required="彩霞山",
        is_repeatable=False,
        scenes=[
            StoryScene(
                id="side_01_scene_01",
                scene_number=1,
                title="神秘老者",
                background="彩霞山深处，一片幽静的山谷",
                location="彩霞山",
                npcs=["神秘老者"],
                dialogues=[
                    StoryDialogue(
                        id="side_01_dlg_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="你在山中采药时，遇到了一位仙风道骨的老者。"
                    ),
                    StoryDialogue(
                        id="side_01_dlg_02",
                        speaker_type="npc",
                        speaker_id="mysterious_old_man",
                        speaker_name="神秘老者",
                        content="小友，我看你骨骼清奇，是个修仙的好苗子。这有一本功法，你可愿意学习？"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="side_choice_01_01",
                        text="欣然接受，拜谢老者。",
                        effects={"exp": 100, "technique": "神秘功法", "karma": 5}
                    ),
                    StoryChoice(
                        id="side_choice_01_02",
                        text="婉言谢绝，无功不受禄。",
                        effects={"wisdom": 5, "karma": 10, "npc_favor": {"mysterious_old_man": 20}}
                    ),
                    StoryChoice(
                        id="side_choice_01_03",
                        text="怀疑老者的身份，谨慎对待。",
                        effects={"caution": 10, "wisdom": 3}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 100, "condition": "complete"},
            {"type": "item", "item": "神秘丹药", "quantity": 1, "condition": "choice_accept"},
        ]
    ),
    
    StoryChapter(
        id="side_02",
        chapter_number=2,
        title="除妖任务",
        description="村庄附近出现了妖兽，村民请求你帮忙除妖...",
        story_type="side",
        realm_required=1,
        location_required="新手村",
        is_repeatable=True,
        scenes=[
            StoryScene(
                id="side_02_scene_01",
                scene_number=1,
                title="村民的委托",
                background="新手村广场",
                location="新手村",
                npcs=["村长", "村民"],
                dialogues=[
                    StoryDialogue(
                        id="side_02_dlg_01",
                        speaker_type="npc",
                        speaker_id="village_chief",
                        speaker_name="村长",
                        content="仙长，求求您帮帮我们！村外出现了妖兽，已经伤了几个村民了！"
                    ),
                    StoryDialogue(
                        id="side_02_dlg_02",
                        speaker_type="player",
                        speaker_name="你",
                        content="村长莫急，我这就去查看。"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="side_choice_02_01",
                        text="立即出发，为民除害。",
                        effects={"karma": 10, "reputation": "侠义", "combat": True}
                    ),
                    StoryChoice(
                        id="side_choice_02_02",
                        text="先询问妖兽的具体情况。",
                        effects={"wisdom": 3, "preparation": True}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 150, "condition": "complete"},
            {"type": "item", "item": "村民谢礼", "quantity": 1, "condition": "complete"},
            {"type": "spirit_stones", "value": 50, "condition": "complete"},
        ]
    ),
    
    StoryChapter(
        id="side_03",
        chapter_number=3,
        title="丹药之争",
        description="在坊市中，你目睹了一场因丹药引起的争执...",
        story_type="side",
        realm_required=1,
        location_required="天元坊市",
        is_repeatable=False,
        scenes=[
            StoryScene(
                id="side_03_scene_01",
                scene_number=1,
                title="坊市争执",
                background="天元坊市，丹药摊位前",
                location="天元坊市",
                npcs=["摊主", "争执修士A", "争执修士B"],
                dialogues=[
                    StoryDialogue(
                        id="side_03_dlg_01",
                        speaker_type="narrator",
                        speaker_name="旁白",
                        content="你正在坊市闲逛，突然听到前方传来争吵声。"
                    ),
                    StoryDialogue(
                        id="side_03_dlg_02",
                        speaker_type="npc",
                        speaker_id="cultivator_a",
                        speaker_name="争执修士A",
                        content="这粒筑基丹是我先看上的！"
                    ),
                    StoryDialogue(
                        id="side_03_dlg_03",
                        speaker_type="npc",
                        speaker_id="cultivator_b",
                        speaker_name="争执修士B",
                        content="明明是我先出价的！"
                    ),
                ],
                choices=[
                    StoryChoice(
                        id="side_choice_03_01",
                        text="出面调解，提议平分。",
                        effects={"karma": 5, "wisdom": 3, "diplomacy": 5}
                    ),
                    StoryChoice(
                        id="side_choice_03_02",
                        text="高价买下丹药，化解争端。",
                        effects={"spirit_stones": -200, "karma": 10, "reputation": "豪爽"}
                    ),
                    StoryChoice(
                        id="side_choice_03_03",
                        text="冷眼旁观，不插手此事。",
                        effects={"caution": 5, "karma": -2}
                    ),
                ]
            ),
        ],
        rewards=[
            {"type": "exp", "value": 80, "condition": "mediate"},
            {"type": "reputation", "value": "公正", "condition": "mediate"},
        ]
    ),
]

# ==================== 剧情触发条件配置 ====================

STORY_TRIGGERS = {
    "chapter_01": {
        "type": "location",
        "condition": "彩霞山",
        "auto_trigger": True,
        "description": "到达彩霞山时自动触发"
    },
    "chapter_02": {
        "type": "location",
        "condition": "神手谷",
        "pre_chapter": "chapter_01",
        "auto_trigger": True,
        "description": "进入神手谷时自动触发"
    },
    "chapter_03": {
        "type": "realm",
        "condition": 1,
        "location": "黄枫谷",
        "pre_chapter": "chapter_02",
        "auto_trigger": False,
        "description": "达到练气期后，在黄枫谷触发"
    },
    "side_01": {
        "type": "random",
        "probability": 0.1,
        "location": "彩霞山",
        "auto_trigger": True,
        "description": "在彩霞山有概率随机触发"
    },
    "side_02": {
        "type": "quest",
        "condition": "接受除妖任务",
        "location": "新手村",
        "auto_trigger": False,
        "description": "在新手村接受任务后触发"
    },
    "side_03": {
        "type": "location",
        "condition": "天元坊市",
        "auto_trigger": True,
        "cooldown_days": 30,
        "description": "进入天元坊市时触发（有冷却时间）"
    },
}

# ==================== 剧情效果类型定义 ====================

CHOICE_EFFECT_TYPES = {
    "exp": "获得经验值",
    "spirit_stones": "获得灵石",
    "item": "获得物品",
    "technique": "学习功法",
    "npc_favor": "NPC好感度变化",
    "karma": "业力变化",
    "reputation": "获得声望标签",
    "health": "生命值变化",
    "combat": "进入战斗",
    "story_end": "剧情结束",
    "story_complete": "剧情完成",
}


def get_chapter_by_id(chapter_id: str) -> Optional[StoryChapter]:
    """
    根据ID获取剧情章节
    
    Args:
        chapter_id: 章节ID
        
    Returns:
        章节数据，不存在返回None
    """
    for chapter in MAIN_STORY_CHAPTERS + SIDE_STORY_CHAPTERS:
        if chapter.id == chapter_id:
            return chapter
    return None


def get_available_chapters(realm_level: int, location: str, completed_chapters: List[str]) -> List[StoryChapter]:
    """
    获取可用的剧情章节
    
    Args:
        realm_level: 当前境界等级
        location: 当前位置
        completed_chapters: 已完成的章节ID列表
        
    Returns:
        可用章节列表
    """
    available = []
    
    for chapter in MAIN_STORY_CHAPTERS + SIDE_STORY_CHAPTERS:
        # 检查境界要求
        if chapter.realm_required > realm_level:
            continue
            
        # 检查位置要求
        if chapter.location_required and chapter.location_required != location:
            continue
            
        # 检查前置章节
        if chapter.pre_chapter_id and chapter.pre_chapter_id not in completed_chapters:
            continue
            
        # 检查是否可重复
        if chapter.id in completed_chapters and not chapter.is_repeatable:
            continue
            
        available.append(chapter)
    
    return available


def generate_random_side_story(realm_level: int, location: str) -> Optional[StoryChapter]:
    """
    生成随机支线剧情
    
    Args:
        realm_level: 当前境界等级
        location: 当前位置
        
    Returns:
        随机生成的支线剧情，如果没有可用剧情返回None
    """
    import random
    
    # 随机剧情模板
    templates = [
        {
            "title": "偶遇散修",
            "description": "你在{}遇到了一位正在寻找材料的散修...",
            "npcs": ["散修"],
            "choices": [
                {"text": "帮助他寻找材料", "effects": {"karma": 5, "npc_favor": {"散修": 20}}},
                {"text": "提出交换条件", "effects": {"wisdom": 3, "trade": True}},
                {"text": "婉言拒绝", "effects": {"caution": 2}},
            ]
        },
        {
            "title": "妖兽袭击",
            "description": "一只{}妖兽突然出现在你面前！",
            "npcs": [],
            "choices": [
                {"text": "迎战", "effects": {"combat": True, "courage": 5}},
                {"text": "逃跑", "effects": {"speed": 2, "caution": 3}},
                {"text": "使用隐匿符", "effects": {"item_consume": "隐匿符", "stealth": 3}},
            ]
        },
        {
            "title": "古修洞府",
            "description": "你发现了一个隐藏的古修洞府入口...",
            "npcs": [],
            "choices": [
                {"text": "进入探索", "effects": {"exploration": True, "risk": 0.5}},
                {"text": "先观察再决定", "effects": {"wisdom": 5, "caution": 3}},
                {"text": "离开，不冒险", "effects": {"caution": 5}},
            ]
        },
        {
            "title": "灵草成熟",
            "description": "你发现了一株即将成熟的{}灵草...",
            "npcs": [],
            "choices": [
                {"text": "守候采摘", "effects": {"item": "灵草", "patience": 3}},
                {"text": "布置陷阱保护", "effects": {"wisdom": 3, "trap": True}},
                {"text": "标记位置，以后再来", "effects": {"caution": 2}},
            ]
        },
    ]
    
    # 随机选择一个模板
    template = random.choice(templates)
    
    # 生成剧情数据
    chapter = StoryChapter(
        id=f"random_side_{random.randint(1000, 9999)}",
        chapter_number=0,
        title=template["title"],
        description=template["description"].format(location),
        story_type="side",
        realm_required=realm_level,
        location_required=location,
        is_repeatable=True,
        scenes=[
            StoryScene(
                id=f"random_scene_{random.randint(1000, 9999)}",
                scene_number=1,
                title=template["title"],
                background=location,
                location=location,
                npcs=template["npcs"],
                choices=[
                    StoryChoice(
                        id=f"random_choice_{i}",
                        text=choice["text"],
                        effects=choice["effects"]
                    )
                    for i, choice in enumerate(template["choices"])
                ]
            )
        ],
        rewards=[
            {"type": "exp", "value": random.randint(50, 150), "condition": "complete"},
        ]
    )
    
    return chapter
