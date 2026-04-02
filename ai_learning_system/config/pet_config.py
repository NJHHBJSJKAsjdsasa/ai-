"""
灵兽系统配置
包含灵兽类型、灵兽模板、技能、进化路线等配置
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class PetType(Enum):
    """灵兽类型"""
    ATTACK = "attack"       # 攻击型
    DEFENSE = "defense"     # 防御型
    SUPPORT = "support"     # 辅助型
    SPEED = "speed"         # 速度型


class PetRarity(Enum):
    """灵兽稀有度"""
    COMMON = "普通"         # 普通
    UNCOMMON = "优秀"       # 优秀
    RARE = "稀有"           # 稀有
    EPIC = "史诗"           # 史诗
    LEGENDARY = "传说"      # 传说
    MYTHIC = "神话"         # 神话


class SkillType(Enum):
    """技能类型"""
    ATTACK = "attack"       # 攻击技能
    DEFENSE = "defense"     # 防御技能
    HEAL = "heal"           # 治疗技能
    BUFF = "buff"           # 增益技能
    DEBUFF = "debuff"       # 减益技能
    SPECIAL = "special"     # 特殊技能


@dataclass
class PetSkill:
    """灵兽技能数据类"""
    skill_id: str                       # 技能ID
    name: str                           # 技能名称
    description: str                    # 技能描述
    skill_type: SkillType               # 技能类型
    level: int = 1                      # 当前等级
    max_level: int = 10                 # 最大等级
    damage: int = 0                     # 基础伤害
    effect_type: str = ""               # 效果类型
    effect_value: float = 0.0           # 效果数值
    cooldown: int = 0                   # 冷却回合
    mana_cost: int = 0                  # 灵力消耗
    learn_level: int = 1                # 学习所需等级
    learn_stage: int = 1                # 学习所需阶段


@dataclass
class EvolutionStage:
    """进化阶段数据类"""
    stage: int                          # 阶段数
    name: str                           # 阶段名称
    description: str                    # 阶段描述
    required_level: int                 # 所需等级
    required_intimacy: int              # 所需亲密度
    required_items: Dict[str, int]      # 所需物品
    attribute_bonus: Dict[str, int]     # 属性加成
    new_skills: List[str]               # 新技能ID列表
    appearance_change: str = ""         # 外观变化描述


@dataclass
class PetTemplate:
    """灵兽模板数据类"""
    template_id: str                    # 模板ID
    name: str                           # 灵兽名称
    description: str                    # 灵兽描述
    pet_type: PetType                   # 灵兽类型
    rarity: PetRarity                   # 稀有度
    
    # 基础属性
    base_attack: int = 10
    base_defense: int = 10
    base_health: int = 100
    base_speed: int = 10
    
    # 资质范围
    min_attack_potential: int = 30
    max_attack_potential: int = 70
    min_defense_potential: int = 30
    max_defense_potential: int = 70
    min_health_potential: int = 30
    max_health_potential: int = 70
    min_speed_potential: int = 30
    max_speed_potential: int = 70
    
    # 成长率
    min_growth_rate: float = 1.0
    max_growth_rate: float = 1.5
    
    # 进化路线
    evolution_stages: List[EvolutionStage] = field(default_factory=list)
    
    # 初始技能
    initial_skills: List[str] = field(default_factory=list)
    
    # 出现地点
    spawn_locations: List[str] = field(default_factory=list)
    
    # 捕捉难度 (0-1)
    catch_difficulty: float = 0.5
    
    # 出现等级范围
    min_spawn_level: int = 1
    max_spawn_level: int = 10


# ==================== 灵兽技能数据库 ====================

PET_SKILLS_DB: Dict[str, PetSkill] = {
    # ===== 攻击型技能 =====
    "claw_strike": PetSkill(
        skill_id="claw_strike",
        name="利爪猛击",
        description="用锋利的爪子攻击敌人",
        skill_type=SkillType.ATTACK,
        damage=20,
        cooldown=0,
        mana_cost=5,
        learn_level=1
    ),
    "fire_breath": PetSkill(
        skill_id="fire_breath",
        name="火焰吐息",
        description="喷出火焰攻击敌人",
        skill_type=SkillType.ATTACK,
        damage=35,
        cooldown=2,
        mana_cost=15,
        learn_level=5
    ),
    "thunder_strike": PetSkill(
        skill_id="thunder_strike",
        name="雷霆一击",
        description="召唤雷电攻击敌人，有几率麻痹",
        skill_type=SkillType.ATTACK,
        damage=50,
        effect_type="stun",
        effect_value=0.3,
        cooldown=3,
        mana_cost=25,
        learn_level=10,
        learn_stage=2
    ),
    "savage_bite": PetSkill(
        skill_id="savage_bite",
        name="野蛮撕咬",
        description="用尖牙撕咬敌人，造成大量伤害",
        skill_type=SkillType.ATTACK,
        damage=45,
        cooldown=2,
        mana_cost=20,
        learn_level=8
    ),
    
    # ===== 防御型技能 =====
    "iron_shell": PetSkill(
        skill_id="iron_shell",
        name="铁甲护体",
        description="提升自身防御力",
        skill_type=SkillType.DEFENSE,
        effect_type="defense_up",
        effect_value=0.3,
        cooldown=3,
        mana_cost=10,
        learn_level=1
    ),
    "protective_shield": PetSkill(
        skill_id="protective_shield",
        name="守护护盾",
        description="为队友提供护盾",
        skill_type=SkillType.DEFENSE,
        effect_type="shield",
        effect_value=50,
        cooldown=4,
        mana_cost=20,
        learn_level=5
    ),
    "damage_reflect": PetSkill(
        skill_id="damage_reflect",
        name="伤害反弹",
        description="反弹部分受到的伤害",
        skill_type=SkillType.DEFENSE,
        effect_type="reflect",
        effect_value=0.3,
        cooldown=3,
        mana_cost=15,
        learn_level=10,
        learn_stage=2
    ),
    
    # ===== 辅助型技能 =====
    "healing_light": PetSkill(
        skill_id="healing_light",
        name="治愈之光",
        description="恢复自身或队友生命值",
        skill_type=SkillType.HEAL,
        effect_type="heal",
        effect_value=30,
        cooldown=3,
        mana_cost=15,
        learn_level=1
    ),
    "spirit_boost": PetSkill(
        skill_id="spirit_boost",
        name="灵气增幅",
        description="提升队友的攻击力",
        skill_type=SkillType.BUFF,
        effect_type="attack_up",
        effect_value=0.2,
        cooldown=4,
        mana_cost=20,
        learn_level=5
    ),
    "purification": PetSkill(
        skill_id="purification",
        name="净化术",
        description="清除负面状态",
        skill_type=SkillType.HEAL,
        effect_type="cleanse",
        cooldown=4,
        mana_cost=20,
        learn_level=8
    ),
    "revive": PetSkill(
        skill_id="revive",
        name="复苏之术",
        description="复活倒下的队友",
        skill_type=SkillType.HEAL,
        effect_type="revive",
        effect_value=0.3,
        cooldown=10,
        mana_cost=50,
        learn_level=15,
        learn_stage=3
    ),
    
    # ===== 速度型技能 =====
    "quick_attack": PetSkill(
        skill_id="quick_attack",
        name="迅捷攻击",
        description="快速攻击敌人，优先出手",
        skill_type=SkillType.ATTACK,
        damage=15,
        cooldown=0,
        mana_cost=5,
        learn_level=1
    ),
    "shadow_step": PetSkill(
        skill_id="shadow_step",
        name="影步",
        description="提升自身速度",
        skill_type=SkillType.BUFF,
        effect_type="speed_up",
        effect_value=0.5,
        cooldown=3,
        mana_cost=15,
        learn_level=5
    ),
    "multi_strike": PetSkill(
        skill_id="multi_strike",
        name="连击",
        description="连续攻击敌人多次",
        skill_type=SkillType.ATTACK,
        damage=25,
        effect_type="multi_hit",
        effect_value=3,
        cooldown=4,
        mana_cost=25,
        learn_level=10,
        learn_stage=2
    ),
    "evasion": PetSkill(
        skill_id="evasion",
        name="闪避",
        description="大幅提升闪避率",
        skill_type=SkillType.BUFF,
        effect_type="dodge_up",
        effect_value=0.5,
        cooldown=4,
        mana_cost=20,
        learn_level=8
    ),
    
    # ===== 特殊技能 =====
    "intimidate": PetSkill(
        skill_id="intimidate",
        name="威吓",
        description="降低敌人的攻击力",
        skill_type=SkillType.DEBUFF,
        effect_type="attack_down",
        effect_value=0.2,
        cooldown=3,
        mana_cost=15,
        learn_level=3
    ),
    "life_drain": PetSkill(
        skill_id="life_drain",
        name="生命吸取",
        description="攻击敌人并恢复自身生命",
        skill_type=SkillType.SPECIAL,
        damage=25,
        effect_type="life_steal",
        effect_value=0.3,
        cooldown=3,
        mana_cost=20,
        learn_level=7
    ),
    "elemental_shield": PetSkill(
        skill_id="elemental_shield",
        name="元素护盾",
        description="获得元素伤害减免",
        skill_type=SkillType.DEFENSE,
        effect_type="element_resist",
        effect_value=0.5,
        cooldown=4,
        mana_cost=25,
        learn_level=12,
        learn_stage=2
    ),
}


# ==================== 灵兽模板数据库 ====================

PET_TEMPLATES_DB: Dict[str, PetTemplate] = {
    # ===== 攻击型灵兽 =====
    "flame_tiger": PetTemplate(
        template_id="flame_tiger",
        name="烈焰虎",
        description="生活在火山地带的凶猛虎类妖兽，浑身燃烧着火焰",
        pet_type=PetType.ATTACK,
        rarity=PetRarity.RARE,
        base_attack=25,
        base_defense=12,
        base_health=90,
        base_speed=15,
        min_attack_potential=60,
        max_attack_potential=95,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="烈焰虎",
                description="幼年期的烈焰虎，火焰还不够炽热",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["claw_strike"]
            ),
            EvolutionStage(
                stage=2,
                name="赤焰虎王",
                description="成熟期的烈焰虎，火焰威力大增",
                required_level=20,
                required_intimacy=80,
                required_items={"火灵珠": 3, "妖兽内丹": 5},
                attribute_bonus={"attack": 30, "health": 20},
                new_skills=["fire_breath", "thunder_strike"],
                appearance_change="体型增大，火焰更加炽热，毛发呈现赤红色"
            ),
            EvolutionStage(
                stage=3,
                name="焚天炎虎",
                description="完全体的烈焰虎，可以焚尽一切",
                required_level=50,
                required_intimacy=100,
                required_items={"天火精华": 5, "龙血": 3},
                attribute_bonus={"attack": 60, "health": 40, "speed": 20},
                new_skills=["savage_bite"],
                appearance_change="全身被金色火焰包围，威风凛凛"
            )
        ],
        initial_skills=["claw_strike"],
        spawn_locations=["火山", "熔岩洞窟", "火焰山脉"],
        catch_difficulty=0.6,
        min_spawn_level=5,
        max_spawn_level=25
    ),
    
    "thunder_wolf": PetTemplate(
        template_id="thunder_wolf",
        name="雷霆狼",
        description="掌控雷电之力的狼类妖兽，速度极快",
        pet_type=PetType.ATTACK,
        rarity=PetRarity.EPIC,
        base_attack=22,
        base_defense=10,
        base_health=85,
        base_speed=20,
        min_attack_potential=65,
        max_attack_potential=100,
        min_speed_potential=60,
        max_speed_potential=95,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="雷霆狼",
                description="幼年雷霆狼，能够释放微弱的电流",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["quick_attack"]
            ),
            EvolutionStage(
                stage=2,
                name="雷狼王",
                description="雷霆狼的王者，掌控更强的雷电之力",
                required_level=25,
                required_intimacy=85,
                required_items={"雷灵珠": 3, "妖兽内丹": 5},
                attribute_bonus={"attack": 25, "speed": 30},
                new_skills=["thunder_strike", "shadow_step"],
                appearance_change="毛发呈现银白色，身上环绕着电弧"
            ),
            EvolutionStage(
                stage=3,
                name="九天雷狼",
                description="传说中的雷狼，可召唤九天神雷",
                required_level=55,
                required_intimacy=100,
                required_items={"雷神之泪": 3, "天雷石": 5},
                attribute_bonus={"attack": 55, "speed": 50, "health": 30},
                new_skills=["multi_strike"],
                appearance_change="体型巨大，周身环绕着紫色雷霆"
            )
        ],
        initial_skills=["quick_attack"],
        spawn_locations=["雷霆峡谷", "风暴高原", "雷云山脉"],
        catch_difficulty=0.7,
        min_spawn_level=10,
        max_spawn_level=35
    ),
    
    # ===== 防御型灵兽 =====
    "stone_turtle": PetTemplate(
        template_id="stone_turtle",
        name="玄石龟",
        description="背负坚硬石壳的龟类妖兽，防御力惊人",
        pet_type=PetType.DEFENSE,
        rarity=PetRarity.UNCOMMON,
        base_attack=8,
        base_defense=30,
        base_health=150,
        base_speed=5,
        min_defense_potential=60,
        max_defense_potential=95,
        min_health_potential=60,
        max_health_potential=95,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="玄石龟",
                description="幼年的玄石龟，壳还不够坚硬",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["iron_shell"]
            ),
            EvolutionStage(
                stage=2,
                name="玄甲灵龟",
                description="壳变得更加坚硬，能够抵御更强的攻击",
                required_level=18,
                required_intimacy=75,
                required_items={"玄铁矿石": 10, "妖兽内丹": 3},
                attribute_bonus={"defense": 40, "health": 50},
                new_skills=["protective_shield", "damage_reflect"],
                appearance_change="龟壳呈现玄黑色，布满神秘纹路"
            ),
            EvolutionStage(
                stage=3,
                name="玄武后裔",
                description="拥有玄武血脉的灵龟，防御无双",
                required_level=45,
                required_intimacy=100,
                required_items={"玄武精血": 2, "万年玄铁": 5},
                attribute_bonus={"defense": 80, "health": 100, "attack": 20},
                new_skills=["elemental_shield"],
                appearance_change="龟壳上浮现玄武图腾，威严庄重"
            )
        ],
        initial_skills=["iron_shell"],
        spawn_locations=["深潭", "地下洞穴", "岩石地带"],
        catch_difficulty=0.4,
        min_spawn_level=3,
        max_spawn_level=20
    ),
    
    "iron_rhino": PetTemplate(
        template_id="iron_rhino",
        name="铁甲犀牛",
        description="身披铁甲的犀牛妖兽，冲锋时无可阻挡",
        pet_type=PetType.DEFENSE,
        rarity=PetRarity.RARE,
        base_attack=15,
        base_defense=25,
        base_health=130,
        base_speed=8,
        min_defense_potential=55,
        max_defense_potential=90,
        min_health_potential=55,
        max_health_potential=90,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="铁甲犀牛",
                description="幼年的铁甲犀牛，铁甲还不够厚重",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["iron_shell"]
            ),
            EvolutionStage(
                stage=2,
                name="重甲战犀",
                description="身披重甲的战犀，冲锋威力惊人",
                required_level=22,
                required_intimacy=80,
                required_items={"精铁矿石": 15, "妖兽内丹": 4},
                attribute_bonus={"defense": 35, "health": 40, "attack": 15},
                new_skills=["protective_shield"],
                appearance_change="铁甲变得更加厚重，头部长出尖角"
            ),
            EvolutionStage(
                stage=3,
                name="金刚战犀",
                description="金刚不坏的战犀，是战场上的堡垒",
                required_level=48,
                required_intimacy=100,
                required_items={"金刚砂": 5, "玄铁": 10},
                attribute_bonus={"defense": 70, "health": 80, "attack": 30},
                new_skills=["damage_reflect"],
                appearance_change="全身覆盖金色铠甲，威风凛凛"
            )
        ],
        initial_skills=["iron_shell"],
        spawn_locations=["草原", "荒野", "铁矿山"],
        catch_difficulty=0.5,
        min_spawn_level=6,
        max_spawn_level=28
    ),
    
    # ===== 辅助型灵兽 =====
    "spirit_deer": PetTemplate(
        template_id="spirit_deer",
        name="灵鹿",
        description="拥有治愈能力的鹿类妖兽，性格温和",
        pet_type=PetType.SUPPORT,
        rarity=PetRarity.UNCOMMON,
        base_attack=10,
        base_defense=12,
        base_health=100,
        base_speed=18,
        min_health_potential=50,
        max_health_potential=85,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="灵鹿",
                description="幼年的灵鹿，拥有微弱的治愈能力",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["healing_light"]
            ),
            EvolutionStage(
                stage=2,
                name="九色灵鹿",
                description="传说中的九色鹿，治愈能力大增",
                required_level=20,
                required_intimacy=80,
                required_items={"灵芝草": 20, "妖兽内丹": 3},
                attribute_bonus={"health": 30, "speed": 20, "defense": 15},
                new_skills=["spirit_boost", "purification"],
                appearance_change="毛发呈现九种颜色，美丽神圣"
            ),
            EvolutionStage(
                stage=3,
                name="圣光神鹿",
                description="拥有神圣力量的神鹿，可以起死回生",
                required_level=50,
                required_intimacy=100,
                required_items={"圣光石": 3, "万年灵芝": 5},
                attribute_bonus={"health": 60, "speed": 40, "defense": 30, "attack": 20},
                new_skills=["revive"],
                appearance_change="全身散发圣光，鹿角如同白玉"
            )
        ],
        initial_skills=["healing_light"],
        spawn_locations=["森林", "灵草地", "仙境"],
        catch_difficulty=0.5,
        min_spawn_level=4,
        max_spawn_level=22
    ),
    
    "jade_fox": PetTemplate(
        template_id="jade_fox",
        name="碧玉狐",
        description="聪慧的狐类妖兽，精通各种辅助法术",
        pet_type=PetType.SUPPORT,
        rarity=PetRarity.RARE,
        base_attack=12,
        base_defense=10,
        base_health=85,
        base_speed=22,
        min_speed_potential=55,
        max_speed_potential=90,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="碧玉狐",
                description="幼年的碧玉狐，聪明伶俐",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["healing_light", "intimidate"]
            ),
            EvolutionStage(
                stage=2,
                name="六尾灵狐",
                description="长出六条尾巴的灵狐，法力大增",
                required_level=25,
                required_intimacy=85,
                required_items={"月华石": 5, "妖兽内丹": 4},
                attribute_bonus={"speed": 35, "health": 25, "attack": 15},
                new_skills=["spirit_boost", "purification"],
                appearance_change="长出六条尾巴，毛色更加光亮"
            ),
            EvolutionStage(
                stage=3,
                name="九尾天狐",
                description="传说中的九尾狐，拥有通天彻地之能",
                required_level=55,
                required_intimacy=100,
                required_items={"天狐内丹": 1, "九转金丹": 3},
                attribute_bonus={"speed": 60, "health": 50, "attack": 40, "defense": 20},
                new_skills=["revive"],
                appearance_change="九条尾巴展开，威势惊人"
            )
        ],
        initial_skills=["healing_light", "intimidate"],
        spawn_locations=["青丘", "幻境", "月光森林"],
        catch_difficulty=0.6,
        min_spawn_level=8,
        max_spawn_level=30
    ),
    
    # ===== 速度型灵兽 =====
    "wind_eagle": PetTemplate(
        template_id="wind_eagle",
        name="疾风鹰",
        description="翱翔于天际的鹰类妖兽，速度极快",
        pet_type=PetType.SPEED,
        rarity=PetRarity.RARE,
        base_attack=18,
        base_defense=8,
        base_health=80,
        base_speed=28,
        min_speed_potential=65,
        max_speed_potential=100,
        min_attack_potential=50,
        max_attack_potential=85,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="疾风鹰",
                description="幼年的疾风鹰，飞行速度已经很快",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["quick_attack"]
            ),
            EvolutionStage(
                stage=2,
                name="风暴神雕",
                description="掌控风暴之力的神雕",
                required_level=23,
                required_intimacy=80,
                required_items={"风灵珠": 3, "妖兽内丹": 4},
                attribute_bonus={"speed": 40, "attack": 25},
                new_skills=["shadow_step", "multi_strike"],
                appearance_change="翼展更大，羽毛呈现青蓝色"
            ),
            EvolutionStage(
                stage=3,
                name="九天神鹏",
                description="传说中的神鹏，一翅九万里",
                required_level=52,
                required_intimacy=100,
                required_items={"鹏羽": 5, "风之精华": 5},
                attribute_bonus={"speed": 80, "attack": 50, "health": 30},
                new_skills=["evasion"],
                appearance_change="体型巨大，双翅展开遮天蔽日"
            )
        ],
        initial_skills=["quick_attack"],
        spawn_locations=["悬崖", "高山", "风暴之眼"],
        catch_difficulty=0.65,
        min_spawn_level=7,
        max_spawn_level=28
    ),
    
    "shadow_leopard": PetTemplate(
        template_id="shadow_leopard",
        name="暗影豹",
        description="潜伏于暗影中的豹类妖兽，神出鬼没",
        pet_type=PetType.SPEED,
        rarity=PetRarity.EPIC,
        base_attack=20,
        base_defense=10,
        base_health=85,
        base_speed=30,
        min_speed_potential=70,
        max_speed_potential=100,
        min_attack_potential=55,
        max_attack_potential=90,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="暗影豹",
                description="幼年的暗影豹，已经能够融入阴影",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["quick_attack", "shadow_step"]
            ),
            EvolutionStage(
                stage=2,
                name="幽影猎豹",
                description="更加强大的暗影豹，几乎无法被察觉",
                required_level=28,
                required_intimacy=85,
                required_items={"暗影石": 5, "妖兽内丹": 5},
                attribute_bonus={"speed": 45, "attack": 30, "defense": 10},
                new_skills=["multi_strike", "evasion"],
                appearance_change="身体几乎完全融入阴影，只有眼睛发光"
            ),
            EvolutionStage(
                stage=3,
                name="暗影之王",
                description="暗影中的王者，可以操控阴影",
                required_level=58,
                required_intimacy=100,
                required_items={"暗影之心": 3, "虚空石": 5},
                attribute_bonus={"speed": 85, "attack": 55, "defense": 25, "health": 30},
                new_skills=["life_drain"],
                appearance_change="全身笼罩在黑暗之中，如同阴影本身"
            )
        ],
        initial_skills=["quick_attack", "shadow_step"],
        spawn_locations=["暗影森林", "幽暗洞穴", "黑夜平原"],
        catch_difficulty=0.75,
        min_spawn_level=12,
        max_spawn_level=38
    ),
    
    # ===== 传说级灵兽 =====
    "divine_dragon": PetTemplate(
        template_id="divine_dragon",
        name="神龙",
        description="传说中的神兽，拥有毁天灭地之能",
        pet_type=PetType.ATTACK,
        rarity=PetRarity.LEGENDARY,
        base_attack=50,
        base_defense=30,
        base_health=200,
        base_speed=25,
        min_attack_potential=80,
        max_attack_potential=100,
        min_defense_potential=70,
        max_defense_potential=100,
        min_health_potential=70,
        max_health_potential=100,
        min_speed_potential=60,
        max_speed_potential=95,
        evolution_stages=[
            EvolutionStage(
                stage=1,
                name="幼龙",
                description="刚出生的神龙幼崽，已经拥有不俗的力量",
                required_level=1,
                required_intimacy=0,
                required_items={},
                attribute_bonus={},
                new_skills=["claw_strike", "fire_breath"]
            ),
            EvolutionStage(
                stage=2,
                name="成年龙",
                description="成年的神龙，可以呼风唤雨",
                required_level=40,
                required_intimacy=90,
                required_items={"龙珠": 5, "龙血": 10, "妖兽内丹": 10},
                attribute_bonus={"attack": 50, "defense": 30, "health": 80, "speed": 20},
                new_skills=["thunder_strike", "elemental_shield"],
                appearance_change="体型巨大，龙威浩荡"
            ),
            EvolutionStage(
                stage=3,
                name="龙王",
                description="龙族之王，统领万龙",
                required_level=80,
                required_intimacy=100,
                required_items={"龙王之心": 1, "龙神之血": 5},
                attribute_bonus={"attack": 100, "defense": 60, "health": 150, "speed": 40},
                new_skills=["savage_bite", "life_drain"],
                appearance_change="五爪金龙，威严无比"
            )
        ],
        initial_skills=["claw_strike", "fire_breath"],
        spawn_locations=["龙脉", "天空之城", "神域"],
        catch_difficulty=0.9,
        min_spawn_level=30,
        max_spawn_level=60
    ),
}


# ==================== 便捷函数 ====================

def get_pet_template(template_id: str) -> Optional[PetTemplate]:
    """获取灵兽模板"""
    return PET_TEMPLATES_DB.get(template_id)


def get_pet_skill(skill_id: str) -> Optional[PetSkill]:
    """获取技能信息"""
    return PET_SKILLS_DB.get(skill_id)


def get_pets_by_type(pet_type: PetType) -> List[PetTemplate]:
    """获取指定类型的灵兽模板"""
    return [p for p in PET_TEMPLATES_DB.values() if p.pet_type == pet_type]


def get_pets_by_rarity(rarity: PetRarity) -> List[PetTemplate]:
    """获取指定稀有度的灵兽模板"""
    return [p for p in PET_TEMPLATES_DB.values() if p.rarity == rarity]


def get_pets_by_location(location: str) -> List[PetTemplate]:
    """获取在指定地点出现的灵兽模板"""
    return [p for p in PET_TEMPLATES_DB.values() if location in p.spawn_locations]


def get_random_pet_by_location(location: str, player_level: int = 1) -> Optional[PetTemplate]:
    """
    根据地点随机获取一只灵兽
    
    Args:
        location: 地点名称
        player_level: 玩家等级，用于筛选合适的灵兽
        
    Returns:
        随机选中的灵兽模板
    """
    available_pets = [
        p for p in PET_TEMPLATES_DB.values()
        if location in p.spawn_locations
        and p.min_spawn_level <= player_level + 10
        and p.max_spawn_level >= player_level - 5
    ]
    
    if not available_pets:
        return None
    
    # 根据稀有度加权随机
    weights = {
        PetRarity.COMMON: 40,
        PetRarity.UNCOMMON: 30,
        PetRarity.RARE: 20,
        PetRarity.EPIC: 8,
        PetRarity.LEGENDARY: 2,
        PetRarity.MYTHIC: 0.5
    }
    
    pet_weights = [weights.get(p.rarity, 10) for p in available_pets]
    return random.choices(available_pets, weights=pet_weights, k=1)[0]


def calculate_catch_success_rate(
    pet_template: PetTemplate,
    pet_health_percent: float,
    player_level: int,
    player_spiritual_power: int,
    catch_item_bonus: float = 0.0
) -> float:
    """
    计算捕捉成功率
    
    Args:
        pet_template: 灵兽模板
        pet_health_percent: 灵兽剩余血量百分比
        player_level: 玩家等级
        player_spiritual_power: 玩家灵力
        catch_item_bonus: 捕捉道具加成
        
    Returns:
        捕捉成功率 (0-1)
    """
    # 基础成功率
    base_rate = 1.0 - pet_template.catch_difficulty
    
    # 血量越低成功率越高
    health_bonus = (1.0 - pet_health_percent) * 0.3
    
    # 等级差距影响
    avg_spawn_level = (pet_template.min_spawn_level + pet_template.max_spawn_level) / 2
    level_diff = player_level - avg_spawn_level
    level_bonus = level_diff * 0.02
    
    # 灵力影响
    spirit_bonus = min(player_spiritual_power / 1000, 0.2)
    
    # 计算最终成功率
    final_rate = base_rate + health_bonus + level_bonus + spirit_bonus + catch_item_bonus
    
    # 限制在合理范围内
    return max(0.05, min(0.95, final_rate))


def calculate_exp_to_next_level(current_level: int, growth_rate: float = 1.0) -> int:
    """计算升到下一级所需经验"""
    base_exp = 100
    return int(base_exp * (current_level ** 1.5) * growth_rate)


def calculate_level_up_attributes(
    pet_type: PetType,
    level: int,
    potentials: Dict[str, int],
    growth_rate: float
) -> Dict[str, int]:
    """
    计算升级后的属性增长
    
    Args:
        pet_type: 灵兽类型
        level: 当前等级
        potentials: 资质字典
        growth_rate: 成长率
        
    Returns:
        属性增长字典
    """
    # 类型加成
    type_bonus = {
        PetType.ATTACK: {"attack": 1.5, "defense": 1.0, "health": 1.0, "speed": 1.1},
        PetType.DEFENSE: {"attack": 1.0, "defense": 1.5, "health": 1.3, "speed": 0.8},
        PetType.SUPPORT: {"attack": 0.9, "defense": 1.1, "health": 1.2, "speed": 1.2},
        PetType.SPEED: {"attack": 1.2, "defense": 0.9, "health": 0.9, "speed": 1.5}
    }
    
    bonuses = type_bonus.get(pet_type, {"attack": 1.0, "defense": 1.0, "health": 1.0, "speed": 1.0})
    
    # 计算属性增长
    growth = {
        "attack": int((potentials.get("attack_potential", 50) / 50) * 3 * bonuses["attack"] * growth_rate),
        "defense": int((potentials.get("defense_potential", 50) / 50) * 2 * bonuses["defense"] * growth_rate),
        "health": int((potentials.get("health_potential", 50) / 50) * 10 * bonuses["health"] * growth_rate),
        "speed": int((potentials.get("speed_potential", 50) / 50) * 2 * bonuses["speed"] * growth_rate)
    }
    
    return growth


def get_random_potential(min_val: int, max_val: int) -> int:
    """获取随机资质值"""
    # 使用正态分布，让高资质更稀有
    mean = (min_val + max_val) / 2
    std = (max_val - min_val) / 4
    potential = int(random.gauss(mean, std))
    return max(min_val, min(max_val, potential))


def get_type_name(pet_type: PetType) -> str:
    """获取类型名称"""
    type_names = {
        PetType.ATTACK: "攻击型",
        PetType.DEFENSE: "防御型",
        PetType.SUPPORT: "辅助型",
        PetType.SPEED: "速度型"
    }
    return type_names.get(pet_type, "未知")


def get_rarity_color(rarity: PetRarity) -> str:
    """获取稀有度对应的颜色"""
    colors = {
        PetRarity.COMMON: "#808080",      # 灰色
        PetRarity.UNCOMMON: "#228B22",    # 绿色
        PetRarity.RARE: "#4169E1",        # 蓝色
        PetRarity.EPIC: "#9932CC",        # 紫色
        PetRarity.LEGENDARY: "#FFD700",   # 金色
        PetRarity.MYTHIC: "#FF4500"       # 橙红色
    }
    return colors.get(rarity, "#808080")


# 初始化时将所有模板ID设置为它们的名称（便于查找）
def _init_ids():
    """初始化ID映射"""
    global PET_TEMPLATES_DB, PET_SKILLS_DB
    
    # 为灵兽模板添加名称映射
    for name, template in list(PET_TEMPLATES_DB.items()):
        PET_TEMPLATES_DB[template.template_id] = template
    
    # 为技能添加名称映射
    for name, skill in list(PET_SKILLS_DB.items()):
        PET_SKILLS_DB[skill.skill_id] = skill


_init_ids()
