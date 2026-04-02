"""
妖兽/敌人数据配置 - 包含各种妖兽、怪物的属性和掉落
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class BeastType(Enum):
    """妖兽类型"""
    NORMAL = "普通"    # 普通妖兽
    ELITE = "精英"     # 精英妖兽
    BOSS = "首领"      # 首领级
    MYTHIC = "神话"    # 神话级


@dataclass
class Beast:
    """妖兽数据类"""
    name: str                           # 妖兽名称
    level: int                          # 等级
    realm_level: int                    # 境界等级 0-9
    beast_type: BeastType               # 妖兽类型
    health: int                         # 生命值
    mana: int                           # 法力值
    attack: int                         # 攻击力
    defense: int                        # 防御力
    speed: int                          # 速度
    crit_rate: float                    # 暴击率 (0-1)
    dodge_rate: float                   # 闪避率 (0-1)
    skills: List[Dict] = field(default_factory=list)  # 技能列表
    loot: List[Tuple[str, float]] = field(default_factory=list)  # 掉落物品和概率
    description: str = ""               # 描述
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "level": self.level,
            "realm_level": self.realm_level,
            "beast_type": self.beast_type.value,
            "health": self.health,
            "mana": self.mana,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "crit_rate": self.crit_rate,
            "dodge_rate": self.dodge_rate,
            "skills": self.skills,
            "loot": self.loot,
            "description": self.description
        }
    
    def get_scaled_stats(self, scale_factor: float = 1.0) -> Dict:
        """获取按比例缩放后的属性"""
        return {
            "health": int(self.health * scale_factor),
            "mana": int(self.mana * scale_factor),
            "attack": int(self.attack * scale_factor),
            "defense": int(self.defense * scale_factor),
            "speed": int(self.speed * scale_factor),
        }


# 妖兽数据库 - 10种常见妖兽
BEASTS_DB: Dict[str, Beast] = {
    # ===== 普通妖兽 =====
    "野狼": Beast(
        name="野狼",
        level=1,
        realm_level=0,
        beast_type=BeastType.NORMAL,
        health=80,
        mana=20,
        attack=15,
        defense=5,
        speed=12,
        crit_rate=0.05,
        dodge_rate=0.05,
        skills=[
            {"name": "撕咬", "damage": 1.0, "type": "physical", "description": "用利齿撕咬目标"},
            {"name": "扑击", "damage": 1.2, "type": "physical", "description": "扑向目标造成额外伤害"}
        ],
        loot=[
            ("狼皮", 0.6),
            ("狼牙", 0.4),
            ("下品灵石", 0.3),
            ("狼肉", 0.8)
        ],
        description="山林中常见的野狼，群居动物，虽然单个实力不强，但成群结队时颇为危险。"
    ),
    
    "猛虎": Beast(
        name="猛虎",
        level=3,
        realm_level=0,
        beast_type=BeastType.NORMAL,
        health=150,
        mana=30,
        attack=35,
        defense=12,
        speed=15,
        crit_rate=0.1,
        dodge_rate=0.08,
        skills=[
            {"name": "虎啸", "damage": 1.0, "type": "physical", "description": "震慑敌人的咆哮"},
            {"name": "猛扑", "damage": 1.5, "type": "physical", "description": "强力扑击，造成大量伤害"},
            {"name": "尾鞭", "damage": 1.1, "type": "physical", "description": "用尾巴抽打敌人"}
        ],
        loot=[
            ("虎皮", 0.7),
            ("虎骨", 0.5),
            ("下品灵石", 0.4),
            ("虎肉", 0.9)
        ],
        description="山林之王，凶猛异常。虎骨和虎皮都是珍贵的材料，常被凡人猎杀。"
    ),
    
    # ===== 炼气期妖兽 =====
    "铁背熊": Beast(
        name="铁背熊",
        level=5,
        realm_level=1,
        beast_type=BeastType.NORMAL,
        health=300,
        mana=50,
        attack=45,
        defense=35,
        speed=8,
        crit_rate=0.05,
        dodge_rate=0.03,
        skills=[
            {"name": "熊掌拍击", "damage": 1.2, "type": "physical", "description": "用巨大的熊掌拍击"},
            {"name": "铁背防御", "damage": 0, "type": "buff", "description": "提升防御力", "effect": {"defense": 20}},
            {"name": "狂暴", "damage": 0, "type": "buff", "description": "攻击力提升", "effect": {"attack": 15}}
        ],
        loot=[
            ("熊皮", 0.8),
            ("熊胆", 0.6),
            ("熊掌", 0.4),
            ("下品灵石", 0.5),
            ("中品灵石", 0.1)
        ],
        description="背部坚硬如铁的巨熊，防御力惊人。熊胆是炼制丹药的珍贵材料。"
    ),
    
    "火狐": Beast(
        name="火狐",
        level=4,
        realm_level=1,
        beast_type=BeastType.NORMAL,
        health=120,
        mana=120,
        attack=25,
        defense=8,
        speed=20,
        crit_rate=0.15,
        dodge_rate=0.15,
        skills=[
            {"name": "火球术", "damage": 1.5, "type": "fire", "description": "喷吐火球攻击"},
            {"name": "火焰缠绕", "damage": 1.0, "type": "fire", "description": "持续火焰伤害"},
            {"name": "魅惑", "damage": 0, "type": "debuff", "description": "迷惑敌人", "effect": {"dodge_rate": -0.1}}
        ],
        loot=[
            ("火狐皮", 0.7),
            ("火狐内丹", 0.3),
            ("下品灵石", 0.4),
            ("火灵草", 0.2)
        ],
        description="掌握火系法术的妖狐，速度极快且擅长法术攻击。火狐内丹是炼制火系丹药的材料。"
    ),
    
    "毒蝎": Beast(
        name="毒蝎",
        level=6,
        realm_level=1,
        beast_type=BeastType.NORMAL,
        health=180,
        mana=60,
        attack=40,
        defense=20,
        speed=10,
        crit_rate=0.1,
        dodge_rate=0.05,
        skills=[
            {"name": "毒刺", "damage": 1.0, "type": "poison", "description": "带毒的尾刺攻击", "effect": {"poison_damage": 5}},
            {"name": "剧毒喷射", "damage": 0.8, "type": "poison", "description": "喷射毒液", "effect": {"poison_damage": 8}},
            {"name": "钳击", "damage": 1.3, "type": "physical", "description": "用巨钳夹住敌人"}
        ],
        loot=[
            ("毒蝎尾", 0.6),
            ("毒囊", 0.5),
            ("蝎壳", 0.7),
            ("下品灵石", 0.5),
            ("解毒丹材料", 0.3)
        ],
        description="剧毒妖兽，尾刺含有致命毒素。毒囊是炼制毒药或解毒丹的材料。"
    ),
    
    # ===== 筑基期妖兽 =====
    "风鹰": Beast(
        name="风鹰",
        level=7,
        realm_level=2,
        beast_type=BeastType.NORMAL,
        health=220,
        mana=100,
        attack=55,
        defense=18,
        speed=35,
        crit_rate=0.2,
        dodge_rate=0.2,
        skills=[
            {"name": "风刃", "damage": 1.4, "type": "wind", "description": "发射锋利的风刃"},
            {"name": "俯冲", "damage": 1.8, "type": "wind", "description": "从高空俯冲攻击"},
            {"name": "疾风步", "damage": 0, "type": "buff", "description": "速度大幅提升", "effect": {"speed": 15}}
        ],
        loot=[
            ("风鹰羽", 0.8),
            ("风鹰爪", 0.6),
            ("中品灵石", 0.4),
            ("风灵珠", 0.15)
        ],
        description="掌握风系法术的妖禽，速度极快，难以捕捉。风鹰羽是炼制飞行法器的材料。"
    ),
    
    "岩龟": Beast(
        name="岩龟",
        level=8,
        realm_level=2,
        beast_type=BeastType.NORMAL,
        health=500,
        mana=80,
        attack=30,
        defense=60,
        speed=5,
        crit_rate=0.02,
        dodge_rate=0.02,
        skills=[
            {"name": "岩甲", "damage": 0, "type": "buff", "description": "岩石护甲，大幅提升防御", "effect": {"defense": 30}},
            {"name": "地刺", "damage": 1.2, "type": "earth", "description": "召唤地刺攻击"},
            {"name": "缩壳", "damage": 0, "type": "buff", "description": "缩入壳中，免疫部分伤害", "effect": {"damage_reduction": 0.5}}
        ],
        loot=[
            ("岩龟壳", 0.9),
            ("岩龟甲", 0.7),
            ("中品灵石", 0.5),
            ("土灵珠", 0.1)
        ],
        description="拥有岩石般坚硬外壳的妖兽，防御力惊人但速度缓慢。龟壳是炼制防御法宝的上好材料。"
    ),
    
    "雷豹": Beast(
        name="雷豹",
        level=10,
        realm_level=2,
        beast_type=BeastType.ELITE,
        health=350,
        mana=150,
        attack=70,
        defense=30,
        speed=40,
        crit_rate=0.25,
        dodge_rate=0.18,
        skills=[
            {"name": "雷击", "damage": 1.6, "type": "thunder", "description": "召唤雷电攻击"},
            {"name": "闪电突袭", "damage": 2.0, "type": "thunder", "description": "如闪电般快速攻击"},
            {"name": "雷光护体", "damage": 0, "type": "buff", "description": "雷电护体，反击攻击者", "effect": {"reflect_damage": 0.3}},
            {"name": "豹啸", "damage": 1.1, "type": "thunder", "description": "附带雷电的咆哮"}
        ],
        loot=[
            ("雷豹皮", 0.8),
            ("雷豹内丹", 0.5),
            ("中品灵石", 0.6),
            ("雷灵珠", 0.2),
            ("雷豹爪", 0.7)
        ],
        description="掌握雷电之力的精英妖兽，速度与攻击力兼备，是筑基期修士的劲敌。"
    ),
    
    # ===== 首领级妖兽 =====
    "金翅大鹏": Beast(
        name="金翅大鹏",
        level=15,
        realm_level=3,
        beast_type=BeastType.BOSS,
        health=800,
        mana=300,
        attack=120,
        defense=50,
        speed=50,
        crit_rate=0.3,
        dodge_rate=0.25,
        skills=[
            {"name": "金羽风暴", "damage": 2.0, "type": "wind", "description": "发射无数金色羽毛"},
            {"name": "大鹏展翅", "damage": 1.5, "type": "wind", "description": "扇动翅膀造成狂风"},
            {"name": "俯冲猎杀", "damage": 2.5, "type": "physical", "description": "致命的俯冲攻击"},
            {"name": "金身护体", "damage": 0, "type": "buff", "description": "金色光芒护体", "effect": {"defense": 40, "damage_reduction": 0.3}},
            {"name": "鹏啸九天", "damage": 1.8, "type": "wind", "description": "震耳欲聋的啸声攻击"}
        ],
        loot=[
            ("金翅大鹏羽", 1.0),
            ("大鹏内丹", 0.8),
            ("上品灵石", 0.7),
            ("风灵珠", 0.4),
            ("大鹏爪", 0.9),
            ("大鹏喙", 0.6),
            ("飞行法器材料", 0.5)
        ],
        description="传说中的神鸟后裔，拥有金色的翅膀和强大的风系能力。是结丹期修士都不敢轻易招惹的存在。"
    ),
    
    # ===== 神话级妖兽 =====
    "九尾妖狐": Beast(
        name="九尾妖狐",
        level=20,
        realm_level=4,
        beast_type=BeastType.MYTHIC,
        health=1200,
        mana=500,
        attack=150,
        defense=80,
        speed=60,
        crit_rate=0.35,
        dodge_rate=0.3,
        skills=[
            {"name": "九尾天火", "damage": 2.5, "type": "fire", "description": "九条尾巴同时释放天火"},
            {"name": "幻术", "damage": 0, "type": "debuff", "description": "让敌人陷入幻境", "effect": {"confusion": True}},
            {"name": "魅惑众生", "damage": 1.5, "type": "spirit", "description": "精神攻击，控制敌人"},
            {"name": "妖狐真身", "damage": 0, "type": "buff", "description": "现出真身，全属性提升", "effect": {"attack": 50, "defense": 30, "speed": 20}},
            {"name": "九尾护盾", "damage": 0, "type": "buff", "description": "九尾形成护盾", "effect": {"shield": 300}},
            {"name": "灵魂冲击", "damage": 2.0, "type": "spirit", "description": "直接攻击灵魂"}
        ],
        loot=[
            ("九尾狐皮", 1.0),
            ("九尾妖丹", 0.9),
            ("上品灵石", 1.0),
            ("极品灵石", 0.5),
            ("火灵珠", 0.6),
            ("幻术秘籍", 0.3),
            ("狐仙之泪", 0.4),
            ("九尾精华", 0.7)
        ],
        description="修炼千年的九尾妖狐，拥有毁天灭地的力量。传说其内丹可让人获得九条性命，是无数修士梦寐以求的至宝。"
    ),
}


def get_beast(name: str) -> Optional[Beast]:
    """
    获取妖兽信息
    
    Args:
        name: 妖兽名称
        
    Returns:
        妖兽信息，不存在则返回None
    """
    return BEASTS_DB.get(name)


def get_beasts_by_realm(realm_level: int) -> List[Beast]:
    """
    获取指定境界的妖兽列表
    
    Args:
        realm_level: 境界等级 0-9
        
    Returns:
        妖兽列表
    """
    return [beast for beast in BEASTS_DB.values() if beast.realm_level == realm_level]


def get_beasts_by_type(beast_type: BeastType) -> List[Beast]:
    """
    获取指定类型的妖兽列表
    
    Args:
        beast_type: 妖兽类型
        
    Returns:
        妖兽列表
    """
    return [beast for beast in BEASTS_DB.values() if beast.beast_type == beast_type]


def generate_beast_by_realm(realm_level: int, beast_type: Optional[BeastType] = None) -> Optional[Beast]:
    """
    根据境界随机生成妖兽
    
    Args:
        realm_level: 境界等级 0-9
        beast_type: 指定妖兽类型（可选）
        
    Returns:
        随机生成的妖兽，如果没有符合条件的则返回None
    """
    # 获取该境界的妖兽
    candidates = get_beasts_by_realm(realm_level)
    
    # 如果指定了类型，进一步筛选
    if beast_type:
        candidates = [b for b in candidates if b.beast_type == beast_type]
    
    if not candidates:
        # 如果没有找到精确匹配的，尝试找相近境界的
        for offset in range(1, 3):
            candidates = get_beasts_by_realm(realm_level + offset)
            if beast_type:
                candidates = [b for b in candidates if b.beast_type == beast_type]
            if candidates:
                break
            
            if realm_level - offset >= 0:
                candidates = get_beasts_by_realm(realm_level - offset)
                if beast_type:
                    candidates = [b for b in candidates if b.beast_type == beast_type]
                if candidates:
                    break
    
    if not candidates:
        return None
    
    # 随机选择一个
    selected = random.choice(candidates)
    
    # 创建副本并随机化属性（±10%波动）
    scale = random.uniform(0.9, 1.1)
    scaled_stats = selected.get_scaled_stats(scale)
    
    # 创建新的妖兽实例
    return Beast(
        name=selected.name,
        level=selected.level,
        realm_level=selected.realm_level,
        beast_type=selected.beast_type,
        health=scaled_stats["health"],
        mana=scaled_stats["mana"],
        attack=scaled_stats["attack"],
        defense=scaled_stats["defense"],
        speed=scaled_stats["speed"],
        crit_rate=min(selected.crit_rate * random.uniform(0.9, 1.1), 1.0),
        dodge_rate=min(selected.dodge_rate * random.uniform(0.9, 1.1), 1.0),
        skills=selected.skills.copy(),
        loot=selected.loot.copy(),
        description=selected.description
    )


def generate_beast_loot(beast: Beast, luck_bonus: float = 0.0) -> List[str]:
    """
    根据概率生成妖兽掉落
    
    Args:
        beast: 妖兽实例
        luck_bonus: 幸运值加成 (0-1)
        
    Returns:
        掉落的物品列表
    """
    loot_items = []
    
    for item_name, drop_rate in beast.loot:
        # 应用幸运加成
        adjusted_rate = min(drop_rate + luck_bonus, 1.0)
        
        if random.random() < adjusted_rate:
            # 根据妖兽类型增加掉落数量
            if beast.beast_type == BeastType.ELITE:
                count = random.randint(1, 2)
            elif beast.beast_type == BeastType.BOSS:
                count = random.randint(2, 3)
            elif beast.beast_type == BeastType.MYTHIC:
                count = random.randint(3, 5)
            else:
                count = 1
            
            loot_items.append(f"{item_name} x{count}")
    
    return loot_items


def calculate_beast_power(beast: Beast) -> int:
    """
    计算妖兽战斗力
    
    Args:
        beast: 妖兽实例
        
    Returns:
        战斗力数值
    """
    # 基础属性战力
    base_power = (
        beast.health * 0.5 +
        beast.mana * 0.3 +
        beast.attack * 2 +
        beast.defense * 1.5 +
        beast.speed * 1.2
    )
    
    # 类型加成
    type_multiplier = {
        BeastType.NORMAL: 1.0,
        BeastType.ELITE: 1.5,
        BeastType.BOSS: 2.5,
        BeastType.MYTHIC: 4.0
    }
    
    # 技能加成
    skill_bonus = len(beast.skills) * 10
    
    return int(base_power * type_multiplier[beast.beast_type] + skill_bonus)


def get_beast_difficulty_rating(beast: Beast) -> str:
    """
    获取妖兽难度评级
    
    Args:
        beast: 妖兽实例
        
    Returns:
        难度评级字符串
    """
    power = calculate_beast_power(beast)
    
    if power < 100:
        return "★☆☆☆☆ (极易)"
    elif power < 300:
        return "★★☆☆☆ (简单)"
    elif power < 600:
        return "★★★☆☆ (普通)"
    elif power < 1200:
        return "★★★★☆ (困难)"
    elif power < 2500:
        return "★★★★★ (极难)"
    else:
        return "★★★★★+ (神话)"


if __name__ == "__main__":
    # 测试妖兽系统
    print("=" * 70)
    print("妖兽系统测试")
    print("=" * 70)
    
    print("\n【所有妖兽列表】")
    for name, beast in BEASTS_DB.items():
        power = calculate_beast_power(beast)
        difficulty = get_beast_difficulty_rating(beast)
        print(f"  {name} - Lv.{beast.level} {beast.beast_type.value} (境界: {beast.realm_level})")
        print(f"    HP:{beast.health} MP:{beast.mana} ATK:{beast.attack} DEF:{beast.defense} SPD:{beast.speed}")
        print(f"    战力: {power} | 难度: {difficulty}")
        print(f"    技能: {', '.join([s['name'] for s in beast.skills])}")
        print()
    
    print("\n【按境界查询】")
    for realm in range(5):
        beasts = get_beasts_by_realm(realm)
        print(f"  境界 {realm}: {', '.join([b.name for b in beasts]) if beasts else '无'}")
    
    print("\n【按类型查询】")
    for btype in BeastType:
        beasts = get_beasts_by_type(btype)
        print(f"  {btype.value}: {', '.join([b.name for b in beasts])}")
    
    print("\n【随机生成测试】")
    for realm in range(5):
        beast = generate_beast_by_realm(realm)
        if beast:
            print(f"  境界 {realm}: 生成 {beast.name} (属性波动: {beast.health}HP)")
    
    print("\n【掉落测试 - 九尾妖狐】")
    jiuwei = get_beast("九尾妖狐")
    if jiuwei:
        print(f"  基础掉落概率:")
        for item, rate in jiuwei.loot:
            print(f"    {item}: {rate*100:.0f}%")
        
        print(f"\n  模拟击杀10次掉落:")
        for i in range(10):
            loot = generate_beast_loot(jiuwei)
            print(f"    第{i+1}次: {', '.join(loot) if loot else '无掉落'}")
        
        print(f"\n  幸运加成测试 (+20%):")
        for i in range(3):
            loot = generate_beast_loot(jiuwei, luck_bonus=0.2)
            print(f"    第{i+1}次: {', '.join(loot) if loot else '无掉落'}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
