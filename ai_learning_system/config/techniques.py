"""
功法系统配置 - 包含《凡人修仙传》等小说中的功法秘籍
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TechniqueType(Enum):
    """功法类型"""
    CULTIVATION = "功法"      # 修炼功法
    COMBAT = "武技"           # 战斗武技
    MOVEMENT = "身法"         # 身法轻功
    SECRET = "秘术"           # 秘术神通
    FORBIDDEN = "禁术"        # 禁术


class ElementType(Enum):
    """属性类型"""
    NONE = "无"
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"
    WIND = "风"
    THUNDER = "雷"
    ICE = "冰"
    DEMON = "魔"
    IMMORTAL = "仙"


class DamageType(Enum):
    """伤害类型"""
    PHYSICAL = "物理"      # 物理伤害
    MAGIC = "法术"         # 法术伤害
    TRUE = "真实"          # 真实伤害


@dataclass
class Technique:
    """功法数据类"""
    name: str                           # 功法名称
    description: str                    # 功法描述
    technique_type: TechniqueType       # 功法类型
    element: ElementType                # 属性
    realm_required: int                 # 所需境界等级
    effects: List[str] = field(default_factory=list)  # 功法效果
    learning_difficulty: int = 50       # 学习难度 (1-100)
    cultivation_speed_bonus: float = 0.0  # 修炼速度加成
    combat_power_bonus: float = 0.0     # 战斗力加成
    special_abilities: List[str] = field(default_factory=list)  # 特殊能力
    origin: str = ""                    # 功法来源
    is_combat_skill: bool = False       # 是否为战斗技能
    mana_cost: int = 10                 # 法力消耗
    cooldown: int = 0                   # 冷却时间
    damage_type: DamageType = DamageType.PHYSICAL  # 伤害类型
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.technique_type.value,
            "element": self.element.value,
            "realm_required": self.realm_required,
            "effects": self.effects,
            "learning_difficulty": self.learning_difficulty,
            "cultivation_speed_bonus": self.cultivation_speed_bonus,
            "combat_power_bonus": self.combat_power_bonus,
            "special_abilities": self.special_abilities,
            "origin": self.origin,
            "is_combat_skill": self.is_combat_skill,
            "mana_cost": self.mana_cost,
            "cooldown": self.cooldown,
            "damage_type": self.damage_type.value
        }


# 境界等级映射
REALM_LEVELS = {
    "凡人": 0,
    "练气期": 1,
    "筑基期": 2,
    "金丹期": 3,
    "元婴期": 4,
    "化神期": 5,
    "炼虚期": 6,
    "合体期": 7,
    "大乘期": 8,
    "渡劫期": 9
}


# 功法数据库 - 来自《凡人修仙传》等小说
TECHNIQUES_DB: Dict[str, Technique] = {
    # 凡人修仙传功法
    "长春功": Technique(
        name="长春功",
        description="木属性基础功法，韩立修仙之路的起点。修炼此功可延年益寿，固本培元。",
        technique_type=TechniqueType.CULTIVATION,
        element=ElementType.WOOD,
        realm_required=1,  # 练气期
        effects=["延年益寿", "固本培元", "木属性亲和"],
        learning_difficulty=30,
        cultivation_speed_bonus=0.1,
        combat_power_bonus=0.05,
        special_abilities=["催熟灵药感知"],
        origin="《凡人修仙传》- 韩立早期主修功法",
        is_combat_skill=False
    ),
    
    "眨眼剑法": Technique(
        name="眨眼剑法",
        description="墨大夫传授的凡俗剑法，以快制胜，出其不意。虽非修仙功法，但在凡人阶段威力不俗。",
        technique_type=TechniqueType.COMBAT,
        element=ElementType.NONE,
        realm_required=0,  # 凡人
        effects=["剑速极快", "出其不意"],
        learning_difficulty=40,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.3,
        special_abilities=["快剑连击"],
        origin="《凡人修仙传》- 墨大夫传授",
        is_combat_skill=True,
        mana_cost=5,
        damage_type=DamageType.PHYSICAL
    ),
    
    "罗烟步": Technique(
        name="罗烟步",
        description="轻身功法，身形如烟，难以捉摸。修炼至大成可瞬息千里。",
        technique_type=TechniqueType.MOVEMENT,
        element=ElementType.NONE,
        realm_required=1,  # 练气期
        effects=["身形飘忽", "闪避提升", "移动加速"],
        learning_difficulty=45,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.1,
        special_abilities=["烟遁", "闪避强化"],
        origin="《凡人修仙传》- 韩立早期身法",
        is_combat_skill=False
    ),
    
    "青元剑诀": Technique(
        name="青元剑诀",
        description="韩立主修功法，由青元子所创，可修炼至化神期。剑气纵横，威力巨大。",
        technique_type=TechniqueType.CULTIVATION,
        element=ElementType.WOOD,
        realm_required=2,  # 筑基期
        effects=["剑气纵横", "威力巨大", "木属性强化"],
        learning_difficulty=60,
        cultivation_speed_bonus=0.2,
        combat_power_bonus=0.3,
        special_abilities=["剑芒", "剑丝", "青元剑盾"],
        origin="《凡人修仙传》- 青元子所创",
        is_combat_skill=True,
        mana_cost=20,
        damage_type=DamageType.PHYSICAL
    ),
    
    "大衍决": Technique(
        name="大衍决",
        description="大衍神君所创，强化神识的绝世功法。修炼后可神识倍增，分心多用。",
        technique_type=TechniqueType.SECRET,
        element=ElementType.NONE,
        realm_required=4,  # 元婴期
        effects=["神识倍增", "分心多用", "感知强化"],
        learning_difficulty=80,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.2,
        special_abilities=["神识攻击", "分心控制", "傀儡操控"],
        origin="《凡人修仙传》- 大衍神君所创",
        is_combat_skill=False
    ),
    
    "梵圣真魔功": Technique(
        name="梵圣真魔功",
        description="魔界顶级功法，韩立主修功法之一。修炼后肉身强横，魔气滔天。",
        technique_type=TechniqueType.CULTIVATION,
        element=ElementType.DEMON,
        realm_required=5,  # 化神期
        effects=["肉身强化", "魔气滔天", "力量暴增"],
        learning_difficulty=85,
        cultivation_speed_bonus=0.25,
        combat_power_bonus=0.5,
        special_abilities=["魔化", "巨力", "不灭之身"],
        origin="《凡人修仙传》- 魔界功法",
        is_combat_skill=True,
        mana_cost=25,
        damage_type=DamageType.PHYSICAL
    ),
    
    "炼神术": Technique(
        name="炼神术",
        description="仙界禁术，可无限强化神识。修炼难度极高，但效果逆天。",
        technique_type=TechniqueType.FORBIDDEN,
        element=ElementType.IMMORTAL,
        realm_required=8,  # 大乘期
        effects=["神识无限增长", "逆天改命", "神魂不灭"],
        learning_difficulty=95,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.4,
        special_abilities=["神识化形", "神魂攻击", "不灭神魂"],
        origin="《凡人修仙传》- 仙界禁术",
        is_combat_skill=False
    ),
    
    # 通用功法
    "基础吐纳术": Technique(
        name="基础吐纳术",
        description="最基础的修炼功法，所有修士入门必修。",
        technique_type=TechniqueType.CULTIVATION,
        element=ElementType.NONE,
        realm_required=1,  # 练气期
        effects=["基础修炼", "吸纳灵气"],
        learning_difficulty=10,
        cultivation_speed_bonus=0.05,
        combat_power_bonus=0.0,
        special_abilities=[],
        origin="通用功法",
        is_combat_skill=False
    ),
    
    "火球术": Technique(
        name="火球术",
        description="最基础的火属性法术，练气期修士必修。",
        technique_type=TechniqueType.COMBAT,
        element=ElementType.FIRE,
        realm_required=1,  # 练气期
        effects=["火焰攻击", "范围伤害"],
        learning_difficulty=20,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.15,
        special_abilities=["火球连发"],
        origin="通用法术",
        is_combat_skill=True,
        mana_cost=8,
        damage_type=DamageType.MAGIC
    ),
    
    "御风术": Technique(
        name="御风术",
        description="基础飞行法术，练气期修士可学习。",
        technique_type=TechniqueType.MOVEMENT,
        element=ElementType.WIND,
        realm_required=1,  # 练气期
        effects=["御风飞行", "速度提升"],
        learning_difficulty=25,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.05,
        special_abilities=["短距离飞行"],
        origin="通用法术",
        is_combat_skill=False
    ),
    
    "金刚罩": Technique(
        name="金刚罩",
        description="防御法术，可形成护盾保护自己。",
        technique_type=TechniqueType.SECRET,
        element=ElementType.METAL,
        realm_required=1,  # 练气期
        effects=["护盾防御", "减伤"],
        learning_difficulty=30,
        cultivation_speed_bonus=0.0,
        combat_power_bonus=0.1,
        special_abilities=["护盾反震"],
        origin="通用法术",
        is_combat_skill=True,
        mana_cost=12,
        damage_type=DamageType.PHYSICAL
    ),
}


def get_technique(name: str) -> Optional[Technique]:
    """
    获取功法信息
    
    Args:
        name: 功法名称
        
    Returns:
        功法信息，不存在则返回None
    """
    return TECHNIQUES_DB.get(name)


def get_techniques_by_realm(realm_level: int) -> List[Technique]:
    """
    获取指定境界可学习的功法
    
    Args:
        realm_level: 境界等级
        
    Returns:
        功法列表
    """
    return [t for t in TECHNIQUES_DB.values() if t.realm_required <= realm_level]


def get_techniques_by_element(element: ElementType) -> List[Technique]:
    """
    获取指定属性的功法
    
    Args:
        element: 属性类型
        
    Returns:
        功法列表
    """
    return [t for t in TECHNIQUES_DB.values() if t.element == element]


def get_techniques_by_type(technique_type: TechniqueType) -> List[Technique]:
    """
    获取指定类型的功法
    
    Args:
        technique_type: 功法类型
        
    Returns:
        功法列表
    """
    return [t for t in TECHNIQUES_DB.values() if t.technique_type == technique_type]


def can_learn_technique(technique_name: str, realm_level: int, spirit_root: str = "") -> bool:
    """
    检查是否可以学习功法
    
    Args:
        technique_name: 功法名称
        realm_level: 当前境界等级
        spirit_root: 灵根类型（可选）
        
    Returns:
        是否可以学习
    """
    technique = get_technique(technique_name)
    if not technique:
        return False
    
    # 检查境界
    if realm_level < technique.realm_required:
        return False
    
    # 检查灵根属性（简单实现）
    if technique.element != ElementType.NONE and spirit_root:
        element_map = {
            "金": ElementType.METAL,
            "木": ElementType.WOOD,
            "水": ElementType.WATER,
            "火": ElementType.FIRE,
            "土": ElementType.EARTH,
            "风": ElementType.WIND,
            "雷": ElementType.THUNDER,
            "冰": ElementType.ICE
        }
        required_element = element_map.get(spirit_root[0])
        if required_element and required_element != technique.element:
            # 允许不同属性修炼，但效果打折
            pass
    
    return True


def calculate_learning_success_rate(technique_name: str, realm_level: int, 
                                    comprehension: int = 50) -> float:
    """
    计算学习功法的成功率
    
    Args:
        technique_name: 功法名称
        realm_level: 当前境界等级
        comprehension: 悟性 (1-100)
        
    Returns:
        成功率 (0-1)
    """
    technique = get_technique(technique_name)
    if not technique:
        return 0.0
    
    # 基础成功率
    base_rate = 0.5
    
    # 境界加成
    realm_bonus = (realm_level - technique.realm_required) * 0.1
    
    # 悟性加成
    comprehension_bonus = (comprehension - 50) / 100
    
    # 难度减成
    difficulty_penalty = (technique.learning_difficulty - 50) / 200
    
    success_rate = base_rate + realm_bonus + comprehension_bonus - difficulty_penalty
    
    return max(0.1, min(0.95, success_rate))


def get_all_techniques() -> Dict[str, Technique]:
    """获取所有功法"""
    return TECHNIQUES_DB.copy()


# 功法学习记录（玩家数据，应该在数据库中）
class TechniqueLearningRecord:
    """功法学习记录"""
    
    def __init__(self):
        self.learned_techniques: Dict[str, Dict] = {}  # 已学习的功法
        self.learning_progress: Dict[str, float] = {}  # 学习进度
    
    def learn_technique(self, technique_name: str, technique_data: Dict = None) -> bool:
        """学习功法
        
        Args:
            technique_name: 功法名称
            technique_data: 功法数据（可选，用于生成的功法）
        
        Returns:
            是否学习成功
        """
        if technique_name in self.learned_techniques:
            return False
        
        # 如果是生成的功法，直接使用提供的数据
        if technique_data:
            self.learned_techniques[technique_name] = {
                "name": technique_name,
                "level": 1,
                "mastery": 0.0,
                "learned_at": "",
                "is_generated": True,
                "technique_type": technique_data.get("technique_type", "未知"),
                "rarity": technique_data.get("rarity", "凡阶"),
                "realm_required": technique_data.get("realm_required", 0),
            }
            self.learning_progress[technique_name] = 0.0
            return True
        
        # 否则从配置中查找
        technique = get_technique(technique_name)
        if not technique:
            return False
        
        self.learned_techniques[technique_name] = {
            "name": technique_name,
            "level": 1,
            "mastery": 0.0,
            "learned_at": ""
        }
        self.learning_progress[technique_name] = 0.0
        return True
    
    def practice_technique(self, technique_name: str, amount: float = 0.1) -> bool:
        """练习功法，增加熟练度"""
        if technique_name not in self.learned_techniques:
            return False
        
        self.learning_progress[technique_name] = min(
            1.0, 
            self.learning_progress.get(technique_name, 0.0) + amount
        )
        
        # 检查是否升级
        if self.learning_progress[technique_name] >= 1.0:
            self.learned_techniques[technique_name]["level"] += 1
            self.learning_progress[technique_name] = 0.0
        
        return True
    
    def get_technique_level(self, technique_name: str) -> int:
        """获取功法等级"""
        if technique_name not in self.learned_techniques:
            return 0
        return self.learned_techniques[technique_name]["level"]
    
    def get_mastery(self, technique_name: str) -> float:
        """获取功法熟练度"""
        return self.learning_progress.get(technique_name, 0.0)


if __name__ == "__main__":
    # 测试功法系统
    print("=" * 60)
    print("功法系统测试")
    print("=" * 60)
    
    print("\n【所有功法】")
    for name, technique in TECHNIQUES_DB.items():
        print(f"  {name} ({technique.technique_type.value}) - {technique.element.value}属性")
        print(f"    描述: {technique.description[:40]}...")
        print(f"    所需境界: {technique.realm_required}")
        print(f"    学习难度: {technique.learning_difficulty}")
    
    print("\n【练气期可学功法】")
    techniques = get_techniques_by_realm(1)
    for t in techniques:
        print(f"  {t.name}")
    
    print("\n【木属性功法】")
    techniques = get_techniques_by_element(ElementType.WOOD)
    for t in techniques:
        print(f"  {t.name}")
    
    print("\n【功法学习测试】")
    record = TechniqueLearningRecord()
    print(f"学习长春功: {record.learn_technique('长春功')}")
    print(f"练习长春功: {record.practice_technique('长春功', 0.5)}")
    print(f"长春功等级: {record.get_technique_level('长春功')}")
    print(f"长春功熟练度: {record.get_mastery('长春功'):.2f}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
