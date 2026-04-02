"""
商店系统配置 - 包含各地点的商店配置和商品数据
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ShopType(Enum):
    """商店类型"""
    GENERAL = "杂货店"          # 杂货店 - 卖基础物品
    PILL = "丹药店"             # 丹药店 - 卖丹药
    MATERIAL = "材料店"         # 材料店 - 卖材料
    TREASURE = "法宝店"         # 法宝店 - 卖法宝
    BOOK = "功法店"             # 功法店 - 卖功法秘籍
    AUCTION = "拍卖行"          # 拍卖行
    BLACK_MARKET = "黑市"       # 黑市 - 卖稀有物品


class ItemType(Enum):
    """商品类型"""
    PILL = "丹药"
    MATERIAL = "材料"
    TREASURE = "法宝"
    BOOK = "功法"
    SPIRIT_STONE = "灵石"
    CONSUMABLE = "消耗品"


class ItemRarity(Enum):
    """商品稀有度"""
    COMMON = "普通"
    UNCOMMON = "优秀"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"


@dataclass
class ShopItemConfig:
    """商店商品配置"""
    item_name: str                      # 商品名称
    item_type: ItemType                 # 商品类型
    base_price: int                     # 基础价格
    stock: int = 10                     # 库存数量
    max_stock: int = 10                 # 最大库存
    rarity: ItemRarity = ItemRarity.COMMON  # 稀有度
    level_required: int = 0             # 所需等级
    description: str = ""               # 描述
    effects: Dict = field(default_factory=dict)  # 效果
    restock_rate: float = 1.0           # 补货速率


@dataclass
class ShopConfig:
    """商店配置"""
    id: str                             # 商店ID
    name: str                           # 商店名称
    shop_type: ShopType                 # 商店类型
    location: str                       # 所在地点
    description: str                    # 描述
    owner_name: str                     # 店主名称
    reputation_required: int = 0        # 所需声望
    tax_rate: float = 0.05              # 税率
    refresh_interval: int = 24          # 刷新间隔（小时）
    items: List[ShopItemConfig] = field(default_factory=list)  # 商品列表


# ==================== 各地点商店配置 ====================

# 新手村商店
NEWBIE_VILLAGE_SHOPS: List[ShopConfig] = [
    ShopConfig(
        id="newbie_general",
        name="新手杂货铺",
        shop_type=ShopType.GENERAL,
        location="新手村",
        description="新手村的杂货铺，出售各种基础物品",
        owner_name="王掌柜",
        items=[
            ShopItemConfig(
                item_name="回气丹",
                item_type=ItemType.PILL,
                base_price=50,
                stock=20,
                max_stock=20,
                rarity=ItemRarity.COMMON,
                description="恢复法力的基础丹药",
                effects={"restore_mana": 30}
            ),
            ShopItemConfig(
                item_name="疗伤丹",
                item_type=ItemType.PILL,
                base_price=50,
                stock=20,
                max_stock=20,
                rarity=ItemRarity.COMMON,
                description="治疗伤势的基础丹药",
                effects={"restore_health": 30}
            ),
            ShopItemConfig(
                item_name="百年灵草",
                item_type=ItemType.MATERIAL,
                base_price=500,
                stock=5,
                max_stock=10,
                rarity=ItemRarity.UNCOMMON,
                description="生长百年的灵草，炼丹材料",
            ),
            ShopItemConfig(
                item_name="灵矿石",
                item_type=ItemType.MATERIAL,
                base_price=100,
                stock=15,
                max_stock=20,
                rarity=ItemRarity.COMMON,
                description="蕴含灵气的矿石",
            ),
            ShopItemConfig(
                item_name="储物袋",
                item_type=ItemType.TREASURE,
                base_price=1000,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.COMMON,
                description="低级修士常用的储物法宝",
            ),
        ]
    ),
    ShopConfig(
        id="newbie_pill",
        name="回春堂",
        shop_type=ShopType.PILL,
        location="新手村",
        description="专门出售各种丹药的店铺",
        owner_name="李药师",
        items=[
            ShopItemConfig(
                item_name="增元丹",
                item_type=ItemType.PILL,
                base_price=200,
                stock=10,
                max_stock=15,
                rarity=ItemRarity.UNCOMMON,
                description="增加修为的丹药",
                effects={"exp_bonus": 100}
            ),
            ShopItemConfig(
                item_name="筑基丹",
                item_type=ItemType.PILL,
                base_price=5000,
                stock=2,
                max_stock=5,
                rarity=ItemRarity.RARE,
                level_required=1,
                description="练气期突破筑基期必备丹药",
                effects={"breakthrough": "筑基期"}
            ),
            ShopItemConfig(
                item_name="回气丹",
                item_type=ItemType.PILL,
                base_price=45,
                stock=30,
                max_stock=30,
                rarity=ItemRarity.COMMON,
                description="恢复法力的基础丹药",
                effects={"restore_mana": 30}
            ),
        ]
    ),
]

# 青云城商店
QINGYUN_CITY_SHOPS: List[ShopConfig] = [
    ShopConfig(
        id="qingyun_general",
        name="万宝阁",
        shop_type=ShopType.GENERAL,
        location="青云城",
        description="青云城最大的杂货店，应有尽有",
        owner_name="赵老板",
        reputation_required=100,
        items=[
            ShopItemConfig(
                item_name="回气丹",
                item_type=ItemType.PILL,
                base_price=45,
                stock=50,
                max_stock=50,
                rarity=ItemRarity.COMMON,
                description="恢复法力的基础丹药",
            ),
            ShopItemConfig(
                item_name="疗伤丹",
                item_type=ItemType.PILL,
                base_price=45,
                stock=50,
                max_stock=50,
                rarity=ItemRarity.COMMON,
                description="治疗伤势的基础丹药",
            ),
            ShopItemConfig(
                item_name="百年灵草",
                item_type=ItemType.MATERIAL,
                base_price=450,
                stock=20,
                max_stock=30,
                rarity=ItemRarity.UNCOMMON,
                description="生长百年的灵草",
            ),
            ShopItemConfig(
                item_name="千年灵草",
                item_type=ItemType.MATERIAL,
                base_price=4500,
                stock=5,
                max_stock=10,
                rarity=ItemRarity.RARE,
                level_required=2,
                description="生长千年的灵草，药效强大",
            ),
        ]
    ),
    ShopConfig(
        id="qingyun_pill",
        name="百草轩",
        shop_type=ShopType.PILL,
        location="青云城",
        description="青云城最著名的丹药店",
        owner_name="孙丹师",
        reputation_required=200,
        items=[
            ShopItemConfig(
                item_name="筑基丹",
                item_type=ItemType.PILL,
                base_price=4500,
                stock=5,
                max_stock=10,
                rarity=ItemRarity.RARE,
                level_required=1,
                description="练气期突破筑基期必备丹药",
            ),
            ShopItemConfig(
                item_name="结丹期丹药",
                item_type=ItemType.PILL,
                base_price=18000,
                stock=2,
                max_stock=5,
                rarity=ItemRarity.EPIC,
                level_required=2,
                description="辅助结丹的珍贵丹药",
            ),
            ShopItemConfig(
                item_name="增元丹",
                item_type=ItemType.PILL,
                base_price=180,
                stock=30,
                max_stock=40,
                rarity=ItemRarity.UNCOMMON,
                description="增加修为的丹药",
            ),
            ShopItemConfig(
                item_name="万年灵乳",
                item_type=ItemType.MATERIAL,
                base_price=45000,
                stock=2,
                max_stock=5,
                rarity=ItemRarity.LEGENDARY,
                level_required=3,
                description="天地灵物，可瞬间恢复全部法力",
            ),
        ]
    ),
    ShopConfig(
        id="qingyun_treasure",
        name="神兵阁",
        shop_type=ShopType.TREASURE,
        location="青云城",
        description="出售各种法宝的店铺",
        owner_name="钱炼器师",
        reputation_required=300,
        items=[
            ShopItemConfig(
                item_name="储物袋",
                item_type=ItemType.TREASURE,
                base_price=900,
                stock=10,
                max_stock=15,
                rarity=ItemRarity.COMMON,
                description="低级修士常用的储物法宝",
            ),
            ShopItemConfig(
                item_name="下品飞剑",
                item_type=ItemType.TREASURE,
                base_price=5000,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.UNCOMMON,
                level_required=1,
                description="基础飞行法宝",
                effects={"speed": 10}
            ),
            ShopItemConfig(
                item_name="护身符",
                item_type=ItemType.TREASURE,
                base_price=2000,
                stock=5,
                max_stock=8,
                rarity=ItemRarity.UNCOMMON,
                description="可抵挡一次致命攻击",
                effects={"defense": 20}
            ),
        ]
    ),
    ShopConfig(
        id="qingyun_book",
        name="藏经阁",
        shop_type=ShopType.BOOK,
        location="青云城",
        description="出售各种功法秘籍",
        owner_name="周长老",
        reputation_required=500,
        items=[
            ShopItemConfig(
                item_name="长春功秘籍",
                item_type=ItemType.BOOK,
                base_price=1000,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.UNCOMMON,
                level_required=1,
                description="木属性基础功法",
            ),
            ShopItemConfig(
                item_name="眨眼剑法秘籍",
                item_type=ItemType.BOOK,
                base_price=500,
                stock=5,
                max_stock=8,
                rarity=ItemRarity.COMMON,
                description="以快制胜的凡俗剑法",
            ),
            ShopItemConfig(
                item_name="火球术秘籍",
                item_type=ItemType.BOOK,
                base_price=800,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.UNCOMMON,
                level_required=1,
                description="基础火属性法术",
            ),
        ]
    ),
]

# 天星城商店（高级城市）
TIANXING_CITY_SHOPS: List[ShopConfig] = [
    ShopConfig(
        id="tianxing_pill",
        name="太玄丹阁",
        shop_type=ShopType.PILL,
        location="天星城",
        description="天星城最顶级的丹药店",
        owner_name="玄丹子",
        reputation_required=1000,
        items=[
            ShopItemConfig(
                item_name="结丹期丹药",
                item_type=ItemType.PILL,
                base_price=15000,
                stock=5,
                max_stock=10,
                rarity=ItemRarity.EPIC,
                level_required=2,
                description="辅助结丹的珍贵丹药",
            ),
            ShopItemConfig(
                item_name="元婴期丹药",
                item_type=ItemType.PILL,
                base_price=80000,
                stock=2,
                max_stock=5,
                rarity=ItemRarity.LEGENDARY,
                level_required=3,
                description="辅助凝结元婴的珍贵丹药",
            ),
            ShopItemConfig(
                item_name="万年灵乳",
                item_type=ItemType.MATERIAL,
                base_price=40000,
                stock=5,
                max_stock=10,
                rarity=ItemRarity.LEGENDARY,
                level_required=3,
                description="天地灵物，可瞬间恢复全部法力",
            ),
        ]
    ),
    ShopConfig(
        id="tianxing_treasure",
        name="天机阁",
        shop_type=ShopType.TREASURE,
        location="天星城",
        description="出售高级法宝的店铺",
        owner_name="天机老人",
        reputation_required=1500,
        items=[
            ShopItemConfig(
                item_name="中品飞剑",
                item_type=ItemType.TREASURE,
                base_price=20000,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.RARE,
                level_required=2,
                description="中级飞行法宝",
                effects={"speed": 20, "attack": 15}
            ),
            ShopItemConfig(
                item_name="防御法器",
                item_type=ItemType.TREASURE,
                base_price=15000,
                stock=3,
                max_stock=5,
                rarity=ItemRarity.RARE,
                level_required=2,
                description="防御型法宝",
                effects={"defense": 30}
            ),
            ShopItemConfig(
                item_name="金雷竹",
                item_type=ItemType.MATERIAL,
                base_price=80000,
                stock=2,
                max_stock=5,
                rarity=ItemRarity.EPIC,
                level_required=3,
                description="可释放辟邪神雷的珍稀灵竹",
            ),
        ]
    ),
    ShopConfig(
        id="tianxing_black_market",
        name="黑市",
        shop_type=ShopType.BLACK_MARKET,
        location="天星城",
        description="地下黑市，出售各种来路不明的稀有物品",
        owner_name="神秘人",
        reputation_required=0,
        tax_rate=0.15,
        items=[
            ShopItemConfig(
                item_name="妖兽内丹",
                item_type=ItemType.MATERIAL,
                base_price=400,
                stock=10,
                max_stock=20,
                rarity=ItemRarity.RARE,
                level_required=2,
                description="妖兽体内凝结的内丹",
            ),
            ShopItemConfig(
                item_name="高级妖丹",
                item_type=ItemType.MATERIAL,
                base_price=1600,
                stock=3,
                max_stock=8,
                rarity=ItemRarity.EPIC,
                level_required=4,
                description="高阶妖兽凝结的内丹",
            ),
            ShopItemConfig(
                item_name="功法残页",
                item_type=ItemType.BOOK,
                base_price=150,
                stock=20,
                max_stock=30,
                rarity=ItemRarity.RARE,
                level_required=1,
                description="破损的功法残页",
            ),
        ]
    ),
]

# 所有商店配置字典
ALL_SHOPS: Dict[str, List[ShopConfig]] = {
    "新手村": NEWBIE_VILLAGE_SHOPS,
    "青云城": QINGYUN_CITY_SHOPS,
    "天星城": TIANXING_CITY_SHOPS,
}

# ==================== 拍卖行配置 ====================

AUCTION_CONFIG = {
    "min_start_price": 100,           # 最低起拍价
    "max_duration_hours": 72,         # 最大拍卖时长
    "default_duration_hours": 24,     # 默认拍卖时长
    "bid_increment_min": 100,         # 最小加价幅度
    "tax_rate": 0.05,                 # 拍卖税率
    "deposit_rate": 0.1,              # 保证金比例
}

# ==================== 动态价格配置 ====================

PRICE_DYNAMIC_CONFIG = {
    "price_fluctuation_range": 0.3,   # 价格波动范围（±30%）
    "demand_increase_rate": 0.05,     # 需求增加时的价格上涨率
    "supply_increase_rate": 0.03,     # 供应增加时的价格下降率
    "restock_threshold": 0.2,         # 补货阈值（库存低于20%时补货）
    "price_update_interval": 6,       # 价格更新间隔（小时）
}


# ==================== 辅助函数 ====================

def get_shops_by_location(location: str) -> List[ShopConfig]:
    """
    获取指定地点的所有商店

    Args:
        location: 地点名称

    Returns:
        商店配置列表
    """
    return ALL_SHOPS.get(location, [])


def get_shop_by_id(shop_id: str) -> Optional[ShopConfig]:
    """
    根据ID获取商店配置

    Args:
        shop_id: 商店ID

    Returns:
        商店配置，不存在返回None
    """
    for shops in ALL_SHOPS.values():
        for shop in shops:
            if shop.id == shop_id:
                return shop
    return None


def get_all_locations() -> List[str]:
    """获取所有有商店的地点列表"""
    return list(ALL_SHOPS.keys())


def calculate_dynamic_price(base_price: int, demand_factor: float, supply_factor: float) -> int:
    """
    计算动态价格

    Args:
        base_price: 基础价格
        demand_factor: 需求因子
        supply_factor: 供应因子

    Returns:
        计算后的价格
    """
    # 价格 = 基础价格 * 需求因子 / 供应因子
    price = base_price * (demand_factor / supply_factor)

    # 限制价格波动范围
    min_price = int(base_price * (1 - PRICE_DYNAMIC_CONFIG["price_fluctuation_range"]))
    max_price = int(base_price * (1 + PRICE_DYNAMIC_CONFIG["price_fluctuation_range"]))

    return max(min_price, min(max_price, int(price)))


def get_item_rarity_multiplier(rarity: ItemRarity) -> float:
    """
    获取稀有度价格倍率

    Args:
        rarity: 稀有度

    Returns:
        价格倍率
    """
    multipliers = {
        ItemRarity.COMMON: 1.0,
        ItemRarity.UNCOMMON: 1.5,
        ItemRarity.RARE: 3.0,
        ItemRarity.EPIC: 6.0,
        ItemRarity.LEGENDARY: 12.0,
        ItemRarity.MYTHIC: 25.0,
    }
    return multipliers.get(rarity, 1.0)


def get_item_type_icon(item_type: ItemType) -> str:
    """
    获取物品类型图标

    Args:
        item_type: 物品类型

    Returns:
        图标字符串
    """
    icons = {
        ItemType.PILL: "💊",
        ItemType.MATERIAL: "🪨",
        ItemType.TREASURE: "⚔️",
        ItemType.BOOK: "📜",
        ItemType.SPIRIT_STONE: "💎",
        ItemType.CONSUMABLE: "🧪",
    }
    return icons.get(item_type, "📦")


def get_rarity_color(rarity: ItemRarity) -> str:
    """
    获取稀有度颜色

    Args:
        rarity: 稀有度

    Returns:
        颜色代码
    """
    colors = {
        ItemRarity.COMMON: "#808080",      # 灰色
        ItemRarity.UNCOMMON: "#32CD32",    # 绿色
        ItemRarity.RARE: "#4169E1",        # 蓝色
        ItemRarity.EPIC: "#9932CC",        # 紫色
        ItemRarity.LEGENDARY: "#FFD700",   # 金色
        ItemRarity.MYTHIC: "#FF4500",      # 橙红色
    }
    return colors.get(rarity, "#FFFFFF")


# ==================== 初始化商店数据 ====================

def init_shops_to_database(db):
    """
    初始化商店数据到数据库

    Args:
        db: 数据库实例
    """
    from datetime import datetime, timedelta

    # 初始化交易表
    db.init_trade_tables()

    now = datetime.now().isoformat()
    next_refresh = (datetime.now() + timedelta(hours=24)).isoformat()

    for location, shops in ALL_SHOPS.items():
        for shop_config in shops:
            # 保存商店信息
            shop_data = {
                'id': shop_config.id,
                'name': shop_config.name,
                'shop_type': shop_config.shop_type.value,
                'location': shop_config.location,
                'description': shop_config.description,
                'owner_id': '',
                'owner_name': shop_config.owner_name,
                'reputation': shop_config.reputation_required,
                'tax_rate': shop_config.tax_rate,
                'is_active': True,
                'refresh_interval': shop_config.refresh_interval,
                'last_refresh': now,
            }
            db.save_shop(shop_data)

            # 保存商品
            for item in shop_config.items:
                item_data = {
                    'item_name': item.item_name,
                    'item_type': item.item_type.value,
                    'base_price': item.base_price,
                    'current_price': item.base_price,
                    'stock': item.stock,
                    'max_stock': item.max_stock,
                    'rarity': item.rarity.value,
                    'level_required': item.level_required,
                    'description': item.description,
                    'effects': item.effects,
                    'demand_factor': 1.0,
                    'supply_factor': 1.0,
                }
                db.add_shop_item(shop_config.id, item_data)

    print(f"已初始化 {sum(len(shops) for shops in ALL_SHOPS.values())} 个商店")


if __name__ == "__main__":
    # 测试商店配置
    print("=" * 60)
    print("商店系统配置测试")
    print("=" * 60)

    print("\n【各地点商店】")
    for location, shops in ALL_SHOPS.items():
        print(f"\n{location}:")
        for shop in shops:
            print(f"  - {shop.name} ({shop.shop_type.value}) - {shop.owner_name}")
            print(f"    商品数量: {len(shop.items)}")

    print("\n【动态价格测试】")
    base_price = 1000
    test_cases = [
        (1.0, 1.0),
        (1.5, 1.0),
        (1.0, 1.5),
        (2.0, 0.8),
        (0.8, 2.0),
    ]
    for demand, supply in test_cases:
        price = calculate_dynamic_price(base_price, demand, supply)
        print(f"  基础价: {base_price}, 需求: {demand}, 供应: {supply} -> 价格: {price}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
