"""
道具系统配置 - 包含《凡人修仙传》等小说中的法宝、丹药、材料
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ItemType(Enum):
    """道具类型"""
    TREASURE = "法宝"         # 法宝
    PILL = "丹药"             # 丹药
    MATERIAL = "材料"         # 材料
    SPIRIT_STONE = "灵石"     # 灵石
    BOOK = "秘籍"             # 秘籍
    CONSUMABLE = "消耗品"     # 消耗品


class ItemRarity(Enum):
    """道具稀有度"""
    COMMON = "普通"           # 普通
    UNCOMMON = "优秀"         # 优秀
    RARE = "稀有"             # 稀有
    EPIC = "史诗"             # 史诗
    LEGENDARY = "传说"        # 传说
    MYTHIC = "神话"           # 神话


@dataclass
class Item:
    """道具数据类"""
    name: str                           # 道具名称
    description: str                    # 道具描述
    item_type: ItemType                 # 道具类型
    rarity: ItemRarity                  # 稀有度
    effects: List[str] = field(default_factory=list)  # 道具效果
    value: int = 100                    # 价值（灵石）
    stackable: bool = True              # 是否可堆叠
    max_stack: int = 99                 # 最大堆叠数量
    usable: bool = True                 # 是否可使用
    level_required: int = 0             # 所需等级
    origin: str = ""                    # 来源
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.item_type.value,
            "rarity": self.rarity.value,
            "effects": self.effects,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
            "usable": self.usable,
            "level_required": self.level_required,
            "origin": self.origin
        }


# 道具数据库 - 来自《凡人修仙传》等小说
ITEMS_DB: Dict[str, Item] = {
    # ===== 法宝 =====
    "掌天瓶": Item(
        name="掌天瓶",
        description="可催熟灵药的神秘宝瓶，韩立最大的机缘。瓶内可凝聚绿液，一滴可让灵药瞬间成熟。",
        item_type=ItemType.TREASURE,
        rarity=ItemRarity.MYTHIC,
        effects=["催熟灵药", "凝聚绿液", "时间加速"],
        value=9999999,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=0,
        origin="《凡人修仙传》- 韩立机缘所得"
    ),
    
    "青竹蜂云剑": Item(
        name="青竹蜂云剑",
        description="韩立本命法宝，由万年金雷竹炼制而成。可释放辟邪神雷，克制邪魔。",
        item_type=ItemType.TREASURE,
        rarity=ItemRarity.LEGENDARY,
        effects=["辟邪神雷", "剑阵威力", "克制邪魔"],
        value=500000,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=4,  # 元婴期
        origin="《凡人修仙传》- 韩立本命法宝"
    ),
    
    "风雷翅": Item(
        name="风雷翅",
        description="由雷鹏翅膀炼制而成，飞行速度极快。可施展风雷遁术，瞬息千里。",
        item_type=ItemType.TREASURE,
        rarity=ItemRarity.LEGENDARY,
        effects=["风雷遁术", "速度无双", "飞行加速"],
        value=300000,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=4,  # 元婴期
        origin="《凡人修仙传》- 韩立法宝"
    ),
    
    "虚天鼎": Item(
        name="虚天鼎",
        description="虚天殿至宝，可炼丹炼器。鼎内空间巨大，可容纳万物。",
        item_type=ItemType.TREASURE,
        rarity=ItemRarity.LEGENDARY,
        effects=["炼丹增效", "炼器加成", "储物"],
        value=800000,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=5,  # 化神期
        origin="《凡人修仙传》- 虚天殿至宝"
    ),
    
    "储物袋": Item(
        name="储物袋",
        description="低级修士常用的储物法宝，内有数尺空间。",
        item_type=ItemType.TREASURE,
        rarity=ItemRarity.COMMON,
        effects=["储物"],
        value=100,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=1,
        origin="通用法宝"
    ),
    
    # ===== 丹药 =====
    "筑基丹": Item(
        name="筑基丹",
        description="练气期突破筑基期必备丹药。服用后可大大增加突破成功率。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.RARE,
        effects=["突破筑基", "固本培元", "提升成功率"],
        value=5000,
        stackable=True,
        max_stack=10,
        usable=True,
        level_required=1,
        origin="《凡人修仙传》- 突破丹药"
    ),
    
    "结丹期丹药": Item(
        name="结丹期丹药",
        description="辅助结丹的珍贵丹药。可提升结丹成功率，稳固金丹品质。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.EPIC,
        effects=["辅助结丹", "提升成功率", "稳固金丹"],
        value=20000,
        stackable=True,
        max_stack=5,
        usable=True,
        level_required=2,
        origin="《凡人修仙传》- 突破丹药"
    ),
    
    "元婴期丹药": Item(
        name="元婴期丹药",
        description="辅助凝结元婴的珍贵丹药。可提升元婴品质，增强神识。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.LEGENDARY,
        effects=["辅助凝婴", "提升品质", "增强神识"],
        value=100000,
        stackable=True,
        max_stack=3,
        usable=True,
        level_required=3,
        origin="《凡人修仙传》- 突破丹药"
    ),
    
    "回气丹": Item(
        name="回气丹",
        description="恢复法力的基础丹药。服用后可快速恢复部分法力。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.COMMON,
        effects=["恢复法力", "快速回蓝"],
        value=50,
        stackable=True,
        max_stack=99,
        usable=True,
        level_required=1,
        origin="通用丹药"
    ),
    
    "疗伤丹": Item(
        name="疗伤丹",
        description="治疗伤势的基础丹药。服用后可恢复伤势，治疗内伤。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.COMMON,
        effects=["恢复伤势", "治疗内伤"],
        value=50,
        stackable=True,
        max_stack=99,
        usable=True,
        level_required=1,
        origin="通用丹药"
    ),
    
    "增元丹": Item(
        name="增元丹",
        description="增加修为的丹药。服用后可获得大量修为经验。",
        item_type=ItemType.PILL,
        rarity=ItemRarity.UNCOMMON,
        effects=["增加修为", "经验加成"],
        value=200,
        stackable=True,
        max_stack=50,
        usable=True,
        level_required=1,
        origin="通用丹药"
    ),
    
    # ===== 材料 =====
    "万年灵乳": Item(
        name="万年灵乳",
        description="天地灵物，可瞬间恢复全部法力。极为珍贵，有价无市。",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.LEGENDARY,
        effects=["瞬间回蓝", "恢复全部法力", "疗伤"],
        value=50000,
        stackable=True,
        max_stack=10,
        usable=True,
        level_required=1,
        origin="《凡人修仙传》- 天地灵物"
    ),
    
    "金雷竹": Item(
        name="金雷竹",
        description="可释放辟邪神雷的珍稀灵竹。是炼制雷属性法宝的顶级材料。",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.EPIC,
        effects=["辟邪神雷", "炼制法宝", "克制邪魔"],
        value=100000,
        stackable=True,
        max_stack=10,
        usable=False,
        level_required=3,
        origin="《凡人修仙传》- 珍稀材料"
    ),
    
    "千年灵草": Item(
        name="千年灵草",
        description="生长千年的灵草，药效强大。是炼制高级丹药的主药。",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.RARE,
        effects=["炼丹材料", "药效强大"],
        value=5000,
        stackable=True,
        max_stack=20,
        usable=False,
        level_required=2,
        origin="通用材料"
    ),
    
    "百年灵草": Item(
        name="百年灵草",
        description="生长百年的灵草，药效中等。是炼制中级丹药的常用药材。",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.UNCOMMON,
        effects=["炼丹材料", "药效中等"],
        value=500,
        stackable=True,
        max_stack=50,
        usable=False,
        level_required=1,
        origin="通用材料"
    ),
    
    "灵矿石": Item(
        name="灵矿石",
        description="蕴含灵气的矿石，可提炼灵石或炼制法宝。",
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        effects=["提炼灵石", "炼器材料"],
        value=100,
        stackable=True,
        max_stack=99,
        usable=False,
        level_required=1,
        origin="通用材料"
    ),
    
    # ===== 灵石 =====
    "下品灵石": Item(
        name="下品灵石",
        description="最基础的灵石，蕴含少量灵气。是修仙界的通用货币。",
        item_type=ItemType.SPIRIT_STONE,
        rarity=ItemRarity.COMMON,
        effects=["货币", "恢复微量法力"],
        value=1,
        stackable=True,
        max_stack=9999,
        usable=True,
        level_required=0,
        origin="通用货币"
    ),
    
    "中品灵石": Item(
        name="中品灵石",
        description="品质较好的灵石，蕴含中等灵气。一颗中品灵石可兑换一百颗下品灵石。",
        item_type=ItemType.SPIRIT_STONE,
        rarity=ItemRarity.UNCOMMON,
        effects=["货币", "恢复少量法力"],
        value=100,
        stackable=True,
        max_stack=999,
        usable=True,
        level_required=0,
        origin="通用货币"
    ),
    
    "上品灵石": Item(
        name="上品灵石",
        description="高品质的灵石，蕴含大量灵气。一颗上品灵石可兑换一百颗中品灵石。",
        item_type=ItemType.SPIRIT_STONE,
        rarity=ItemRarity.RARE,
        effects=["货币", "恢复大量法力"],
        value=10000,
        stackable=True,
        max_stack=99,
        usable=True,
        level_required=0,
        origin="通用货币"
    ),
    
    "极品灵石": Item(
        name="极品灵石",
        description="极品灵石，蕴含海量灵气。极为稀有，有价无市。",
        item_type=ItemType.SPIRIT_STONE,
        rarity=ItemRarity.EPIC,
        effects=["货币", "恢复海量法力", "突破辅助"],
        value=1000000,
        stackable=True,
        max_stack=10,
        usable=True,
        level_required=0,
        origin="珍稀货币"
    ),
    
    # ===== 秘籍 =====
    "长春功秘籍": Item(
        name="长春功秘籍",
        description="记载长春功修炼之法的秘籍。木属性基础功法。",
        item_type=ItemType.BOOK,
        rarity=ItemRarity.UNCOMMON,
        effects=["学习长春功"],
        value=1000,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=1,
        origin="《凡人修仙传》- 基础功法"
    ),
    
    "眨眼剑法秘籍": Item(
        name="眨眼剑法秘籍",
        description="记载眨眼剑法的秘籍。以快制胜的凡俗剑法。",
        item_type=ItemType.BOOK,
        rarity=ItemRarity.COMMON,
        effects=["学习眨眼剑法"],
        value=500,
        stackable=False,
        max_stack=1,
        usable=True,
        level_required=0,
        origin="《凡人修仙传》- 凡俗武技"
    ),
}


def get_item(name: str) -> Optional[Item]:
    """
    获取道具信息
    
    Args:
        name: 道具名称
        
    Returns:
        道具信息，不存在则返回None
    """
    return ITEMS_DB.get(name)


def get_items_by_type(item_type: ItemType) -> List[Item]:
    """
    获取指定类型的道具
    
    Args:
        item_type: 道具类型
        
    Returns:
        道具列表
    """
    return [item for item in ITEMS_DB.values() if item.item_type == item_type]


def get_items_by_rarity(rarity: ItemRarity) -> List[Item]:
    """
    获取指定稀有度的道具
    
    Args:
        rarity: 稀有度
        
    Returns:
        道具列表
    """
    return [item for item in ITEMS_DB.values() if item.rarity == rarity]


def get_items_by_level(level: int) -> List[Item]:
    """
    获取指定等级可使用的道具
    
    Args:
        level: 等级
        
    Returns:
        道具列表
    """
    return [item for item in ITEMS_DB.values() if item.level_required <= level]


def search_items(keyword: str) -> List[Item]:
    """
    搜索道具
    
    Args:
        keyword: 关键词
        
    Returns:
        道具列表
    """
    results = []
    keyword_lower = keyword.lower()
    for item in ITEMS_DB.values():
        if (keyword_lower in item.name.lower() or 
            keyword_lower in item.description.lower() or
            any(keyword_lower in effect.lower() for effect in item.effects)):
            results.append(item)
    return results


def get_all_items() -> Dict[str, Item]:
    """获取所有道具"""
    return ITEMS_DB.copy()


def calculate_item_value(item_name: str, quantity: int = 1) -> int:
    """
    计算道具价值
    
    Args:
        item_name: 道具名称
        quantity: 数量
        
    Returns:
        总价值
    """
    item = get_item(item_name)
    if not item:
        return 0
    return item.value * quantity


# 玩家背包类
class Inventory:
    """玩家背包"""
    
    def __init__(self, max_slots: int = 50):
        self.max_slots = max_slots
        self.items: Dict[str, Dict] = {}  # {item_name: {"count": int, "data": Dict}}
        self.generated_items: Dict[str, Dict] = {}  # 存储动态生成的道具 {item_name: item_data}
    
    def add_item(self, item_name: str, count: int = 1, item_data: Dict = None) -> bool:
        """
        添加道具
        
        Args:
            item_name: 道具名称
            count: 数量
            item_data: 动态生成的道具数据（可选）
        """
        # 先检查是否是数据库中的道具
        item = get_item(item_name)
        
        # 如果不是数据库道具，检查是否是已记录的生成道具
        if not item and item_name in self.generated_items:
            item_data = self.generated_items[item_name]
        
        # 如果是全新的生成道具，使用传入的数据创建
        if not item and item_data:
            self.generated_items[item_name] = item_data
            item = item_data
        
        # 如果还是找不到，无法添加
        if not item:
            return False
        
        # 检查背包空间
        if len(self.items) >= self.max_slots and item_name not in self.items:
            return False
        
        # 判断是否可堆叠
        stackable = item.get("stackable", True) if isinstance(item, dict) else item.stackable
        max_stack = item.get("max_stack", 99) if isinstance(item, dict) else item.max_stack
        
        if item_name in self.items:
            # 检查堆叠上限
            current_count = self.items[item_name]["count"]
            if stackable and current_count + count <= max_stack:
                self.items[item_name]["count"] += count
            elif stackable:
                return False
            else:
                return False
        else:
            # 存储道具数据
            if isinstance(item, dict):
                data = item
            else:
                data = item.to_dict()
            
            self.items[item_name] = {
                "count": count,
                "data": data
            }
        
        return True
    
    def add_generated_item(self, item_name: str, item_data: Dict, count: int = 1) -> bool:
        """
        添加动态生成的道具
        
        Args:
            item_name: 道具名称
            item_data: 道具数据字典
            count: 数量
        """
        # 存储生成道具的定义
        self.generated_items[item_name] = item_data
        
        # 添加到背包
        return self.add_item(item_name, count, item_data)
    
    def remove_item(self, item_name: str, count: int = 1) -> bool:
        """移除道具"""
        if item_name not in self.items:
            return False
        
        if self.items[item_name]["count"] < count:
            return False
        
        self.items[item_name]["count"] -= count
        if self.items[item_name]["count"] <= 0:
            del self.items[item_name]
        
        return True
    
    def use_item(self, item_name: str) -> bool:
        """使用道具"""
        if item_name not in self.items:
            return False
        
        # 先检查是否是数据库道具
        item = get_item(item_name)
        
        # 如果不是，检查是否是生成道具
        if not item and item_name in self.generated_items:
            item_data = self.generated_items[item_name]
            usable = item_data.get("usable", True)
            if not usable:
                return False
            # 使用生成道具
            self.remove_item(item_name, 1)
            return True
        
        if not item or not item.usable:
            return False
        
        # 这里可以添加使用效果逻辑
        self.remove_item(item_name, 1)
        return True
    
    def get_item_count(self, item_name: str) -> int:
        """获取道具数量"""
        return self.items.get(item_name, {}).get("count", 0)
    
    def get_total_value(self) -> int:
        """获取背包总价值"""
        total = 0
        for item_name, data in self.items.items():
            # 先检查是否是数据库道具
            item = get_item(item_name)
            if item:
                total += item.value * data["count"]
            else:
                # 检查是否是生成道具
                if item_name in self.generated_items:
                    item_data = self.generated_items[item_name]
                    value = item_data.get("value", 100)
                    total += value * data["count"]
                else:
                    # 从存储的数据中获取价值
                    item_data = data.get("data", {})
                    value = item_data.get("value", 100)
                    total += value * data["count"]
        return total
    
    def is_full(self) -> bool:
        """检查背包是否已满"""
        return len(self.items) >= self.max_slots


if __name__ == "__main__":
    # 测试道具系统
    print("=" * 60)
    print("道具系统测试")
    print("=" * 60)
    
    print("\n【所有法宝】")
    treasures = get_items_by_type(ItemType.TREASURE)
    for item in treasures:
        print(f"  {item.name} ({item.rarity.value}) - {item.description[:30]}...")
    
    print("\n【所有丹药】")
    pills = get_items_by_type(ItemType.PILL)
    for item in pills:
        print(f"  {item.name} ({item.rarity.value}) - {item.description[:30]}...")
    
    print("\n【传说级道具】")
    legendary_items = get_items_by_rarity(ItemRarity.LEGENDARY)
    for item in legendary_items:
        print(f"  {item.name} ({item.item_type.value})")
    
    print("\n【背包测试】")
    inventory = Inventory(max_slots=20)
    print(f"添加筑基丹 x5: {inventory.add_item('筑基丹', 5)}")
    print(f"添加掌天瓶: {inventory.add_item('掌天瓶', 1)}")
    print(f"添加下品灵石 x100: {inventory.add_item('下品灵石', 100)}")
    print(f"筑基丹数量: {inventory.get_item_count('筑基丹')}")
    print(f"背包总价值: {inventory.get_total_value()} 灵石")
    print(f"使用筑基丹: {inventory.use_item('筑基丹')}")
    print(f"筑基丹剩余: {inventory.get_item_count('筑基丹')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
