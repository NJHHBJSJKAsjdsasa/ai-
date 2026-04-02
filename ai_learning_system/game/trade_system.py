"""
交易系统模块
管理商店、拍卖行、玩家交易等功能
"""

import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from config.shop_config import (
    ShopType, ItemType, ItemRarity,
    calculate_dynamic_price, get_item_type_icon, get_rarity_color,
    AUCTION_CONFIG, PRICE_DYNAMIC_CONFIG, init_shops_to_database
)


@dataclass
class TradeResult:
    """交易结果"""
    success: bool
    message: str
    item_name: str = ""
    quantity: int = 0
    total_price: int = 0
    remaining_spirit_stones: int = 0


@dataclass
class AuctionItem:
    """拍卖物品"""
    id: int
    item_name: str
    item_type: str
    seller_id: str
    seller_name: str
    start_price: int
    current_price: int
    buyout_price: Optional[int]
    bid_increment: int
    rarity: str
    level_required: int
    description: str
    effects: Dict
    status: str
    start_time: str
    end_time: str
    highest_bidder_id: Optional[str]
    highest_bidder_name: Optional[str]
    bid_count: int

    @property
    def time_remaining(self) -> str:
        """获取剩余时间"""
        try:
            end = datetime.fromisoformat(self.end_time)
            now = datetime.now()
            if end <= now:
                return "已结束"
            diff = end - now
            hours = int(diff.total_seconds() / 3600)
            minutes = int((diff.total_seconds() % 3600) / 60)
            if hours > 0:
                return f"{hours}小时{minutes}分钟"
            return f"{minutes}分钟"
        except:
            return "未知"


class TradeManager:
    """交易管理器"""

    def __init__(self):
        self.db = Database()
        self._initialized = False

    def initialize(self):
        """初始化交易系统"""
        if not self._initialized:
            # 初始化数据库表
            self.db.init_trade_tables()
            # 初始化商店数据
            init_shops_to_database(self.db)
            self._initialized = True
            print("交易系统初始化完成")

    # ==================== 商店系统 ====================

    def get_shops_by_location(self, location: str) -> List[Dict]:
        """
        获取指定地点的所有商店

        Args:
            location: 地点名称

        Returns:
            商店列表
        """
        return self.db.get_shop_by_location(location)

    def get_shop_items(self, shop_id: str) -> List[Dict]:
        """
        获取商店的商品列表

        Args:
            shop_id: 商店ID

        Returns:
            商品列表
        """
        items = self.db.get_shop_items(shop_id)
        # 更新动态价格
        for item in items:
            item['current_price'] = calculate_dynamic_price(
                item['base_price'],
                item['demand_factor'],
                item['supply_factor']
            )
        return items

    def buy_item(self, player, shop_id: str, item_id: int, quantity: int = 1) -> TradeResult:
        """
        购买商品

        Args:
            player: 玩家对象
            shop_id: 商店ID
            item_id: 商品ID
            quantity: 购买数量

        Returns:
            交易结果
        """
        # 获取商品信息
        items = self.db.get_shop_items(shop_id)
        item = None
        for i in items:
            if i['id'] == item_id:
                item = i
                break

        if not item:
            return TradeResult(False, "商品不存在")

        # 检查库存
        if item['stock'] < quantity:
            return TradeResult(False, f"库存不足，当前库存: {item['stock']}")

        # 检查等级要求
        if hasattr(player.stats, 'realm_level') and item['level_required'] > player.stats.realm_level:
            return TradeResult(False, f"境界不足，需要: {item['level_required']}层")

        # 计算总价
        unit_price = calculate_dynamic_price(
            item['base_price'],
            item['demand_factor'],
            item['supply_factor']
        )
        total_price = unit_price * quantity

        # 检查灵石
        if player.stats.spirit_stones < total_price:
            return TradeResult(
                False,
                f"灵石不足，需要: {total_price}，拥有: {player.stats.spirit_stones}"
            )

        # 扣除灵石
        player.stats.spirit_stones -= total_price

        # 减少库存
        self.db.update_shop_item_stock(item_id, -quantity)

        # 增加需求因子（购买导致价格上涨）
        new_demand = min(2.0, item['demand_factor'] + PRICE_DYNAMIC_CONFIG['demand_increase_rate'] * quantity)
        self._update_demand_factor(item_id, new_demand)

        # 添加物品到背包
        from config.items import get_item
        db_item = get_item(item['item_name'])
        if db_item:
            player.inventory.add_item(item['item_name'], quantity)
        else:
            # 动态生成的物品
            item_data = {
                'name': item['item_name'],
                'type': item['item_type'],
                'rarity': item['rarity'],
                'description': item['description'],
                'effects': item['effects'],
                'value': unit_price,
            }
            player.inventory.add_generated_item(item['item_name'], item_data, quantity)

        # 记录交易
        self.db.record_trade({
            'trade_type': 'buy',
            'item_name': item['item_name'],
            'item_type': item['item_type'],
            'quantity': quantity,
            'price': unit_price,
            'total_amount': total_price,
            'buyer_id': player.stats.name,
            'buyer_name': player.stats.name,
            'shop_id': shop_id,
        })

        # 记录价格历史
        self.db.record_price_history({
            'item_name': item['item_name'],
            'item_type': item['item_type'],
            'shop_id': shop_id,
            'price': unit_price,
            'trade_type': 'buy',
            'location': player.stats.location if hasattr(player.stats, 'location') else ''
        })

        return TradeResult(
            True,
            f"成功购买 {item['item_name']} x{quantity}",
            item['item_name'],
            quantity,
            total_price,
            player.stats.spirit_stones
        )

    def sell_item(self, player, shop_id: str, item_name: str, quantity: int = 1) -> TradeResult:
        """
        出售物品给商店

        Args:
            player: 玩家对象
            shop_id: 商店ID
            item_name: 物品名称
            quantity: 出售数量

        Returns:
            交易结果
        """
        # 检查背包
        item_count = player.inventory.get_item_count(item_name)
        if item_count < quantity:
            return TradeResult(False, f"物品数量不足，拥有: {item_count}")

        # 获取物品价值
        from config.items import get_item, calculate_item_value
        item = get_item(item_name)
        if item:
            unit_price = int(item.value * 0.7)  # 商店收购价为70%
        else:
            # 动态生成的物品
            if item_name in player.inventory.generated_items:
                item_data = player.inventory.generated_items[item_name]
                unit_price = int(item_data.get('value', 100) * 0.7)
            else:
                unit_price = 50  # 默认价格

        total_price = unit_price * quantity

        # 移除物品
        player.inventory.remove_item(item_name, quantity)

        # 增加灵石
        player.stats.spirit_stones += total_price

        # 记录交易
        self.db.record_trade({
            'trade_type': 'sell',
            'item_name': item_name,
            'item_type': item.item_type.value if item else '其他',
            'quantity': quantity,
            'price': unit_price,
            'total_amount': total_price,
            'seller_id': player.stats.name,
            'seller_name': player.stats.name,
            'shop_id': shop_id,
        })

        return TradeResult(
            True,
            f"成功出售 {item_name} x{quantity}",
            item_name,
            quantity,
            total_price,
            player.stats.spirit_stones
        )

    def _update_demand_factor(self, item_id: int, new_demand: float):
        """更新需求因子"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE shop_items SET demand_factor = ? WHERE id = ?",
                (new_demand, item_id)
            )
            conn.commit()
        except Exception as e:
            print(f"更新需求因子失败: {e}")

    def restock_items(self, shop_id: str):
        """
        补货

        Args:
            shop_id: 商店ID
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            # 获取需要补货的商品
            cursor.execute("""
                SELECT id, stock, max_stock FROM shop_items 
                WHERE shop_id = ? AND stock < max_stock * ?
            """, (shop_id, PRICE_DYNAMIC_CONFIG['restock_threshold']))

            rows = cursor.fetchall()
            for row in rows:
                item_id = row['id']
                max_stock = row['max_stock']
                # 补货到最大库存
                cursor.execute("""
                    UPDATE shop_items 
                    SET stock = max_stock, supply_factor = MIN(supply_factor + ?, 2.0)
                    WHERE id = ?
                """, (PRICE_DYNAMIC_CONFIG['supply_increase_rate'], item_id))

            conn.commit()
        except Exception as e:
            print(f"补货失败: {e}")

    # ==================== 拍卖行系统 ====================

    def create_auction(
        self,
        seller_id: str,
        seller_name: str,
        item_name: str,
        item_type: str,
        start_price: int,
        buyout_price: Optional[int] = None,
        duration_hours: int = 24,
        rarity: str = "普通",
        level_required: int = 0,
        description: str = "",
        effects: Dict = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        创建拍卖

        Args:
            seller_id: 卖家ID
            seller_name: 卖家名称
            item_name: 物品名称
            item_type: 物品类型
            start_price: 起拍价
            buyout_price: 一口价（可选）
            duration_hours: 拍卖时长（小时）
            rarity: 稀有度
            level_required: 所需等级
            description: 描述
            effects: 效果

        Returns:
            (是否成功, 消息, 拍卖ID)
        """
        # 验证价格
        if start_price < AUCTION_CONFIG['min_start_price']:
            return False, f"起拍价不能低于 {AUCTION_CONFIG['min_start_price']}", None

        if buyout_price and buyout_price <= start_price:
            return False, "一口价必须高于起拍价", None

        if duration_hours > AUCTION_CONFIG['max_duration_hours']:
            return False, f"拍卖时长不能超过 {AUCTION_CONFIG['max_duration_hours']} 小时", None

        # 计算结束时间
        end_time = (datetime.now() + timedelta(hours=duration_hours)).isoformat()

        # 创建拍卖
        auction_data = {
            'item_name': item_name,
            'item_type': item_type,
            'seller_id': seller_id,
            'seller_name': seller_name,
            'start_price': start_price,
            'buyout_price': buyout_price,
            'bid_increment': max(AUCTION_CONFIG['bid_increment_min'], start_price // 10),
            'rarity': rarity,
            'level_required': level_required,
            'description': description,
            'effects': effects or {},
            'end_time': end_time,
        }

        auction_id = self.db.create_auction_item(auction_data)

        return True, f"成功创建拍卖，ID: {auction_id}", auction_id

    def get_active_auctions(self, item_type: str = None) -> List[AuctionItem]:
        """
        获取活跃的拍卖

        Args:
            item_type: 物品类型筛选

        Returns:
            拍卖物品列表
        """
        auctions = self.db.get_active_auctions(item_type)
        return [AuctionItem(**auction) for auction in auctions]

    def place_bid(self, player, auction_id: int, bid_amount: int) -> TradeResult:
        """
        竞拍

        Args:
            player: 玩家对象
            auction_id: 拍卖ID
            bid_amount: 出价金额

        Returns:
            交易结果
        """
        # 获取拍卖信息
        auctions = self.db.get_active_auctions()
        auction = None
        for a in auctions:
            if a['id'] == auction_id:
                auction = a
                break

        if not auction:
            return TradeResult(False, "拍卖不存在或已结束")

        # 检查是否是自己的拍卖
        if auction['seller_id'] == player.stats.name:
            return TradeResult(False, "不能竞拍自己的物品")

        # 检查出价
        min_bid = auction['current_price'] + auction['bid_increment']
        if bid_amount < min_bid:
            return TradeResult(False, f"出价过低，最低出价: {min_bid}")

        # 检查灵石
        if player.stats.spirit_stones < bid_amount:
            return TradeResult(False, f"灵石不足，需要: {bid_amount}")

        # 如果是当前最高出价者，先退还之前的出价
        if auction['highest_bidder_id'] == player.stats.name:
            # 增加之前的出价金额
            player.stats.spirit_stones += auction['current_price']

        # 扣除灵石
        player.stats.spirit_stones -= bid_amount

        # 更新拍卖
        success = self.db.place_bid(
            auction_id,
            player.stats.name,
            player.stats.name,
            bid_amount
        )

        if success:
            return TradeResult(
                True,
                f"成功出价 {bid_amount} 灵石",
                auction['item_name'],
                1,
                bid_amount,
                player.stats.spirit_stones
            )
        else:
            # 退还灵石
            player.stats.spirit_stones += bid_amount
            return TradeResult(False, "出价失败")

    def buyout_auction(self, player, auction_id: int) -> TradeResult:
        """
        一口价购买

        Args:
            player: 玩家对象
            auction_id: 拍卖ID

        Returns:
            交易结果
        """
        # 获取拍卖信息
        auctions = self.db.get_active_auctions()
        auction = None
        for a in auctions:
            if a['id'] == auction_id:
                auction = a
                break

        if not auction:
            return TradeResult(False, "拍卖不存在或已结束")

        if not auction['buyout_price']:
            return TradeResult(False, "该拍卖不支持一口价")

        # 检查是否是自己的拍卖
        if auction['seller_id'] == player.stats.name:
            return TradeResult(False, "不能购买自己的物品")

        # 检查灵石
        price = auction['buyout_price']
        if player.stats.spirit_stones < price:
            return TradeResult(False, f"灵石不足，需要: {price}")

        # 扣除灵石
        player.stats.spirit_stones -= price

        # 结束拍卖
        success, final_price = self.db.buyout_auction(
            auction_id,
            player.stats.name,
            player.stats.name
        )

        if success:
            # 添加物品到背包
            from config.items import get_item
            db_item = get_item(auction['item_name'])
            if db_item:
                player.inventory.add_item(auction['item_name'], 1)
            else:
                item_data = {
                    'name': auction['item_name'],
                    'type': auction['item_type'],
                    'rarity': auction['rarity'],
                    'description': auction['description'],
                    'effects': auction['effects'],
                    'value': final_price,
                }
                player.inventory.add_generated_item(auction['item_name'], item_data, 1)

            # 给卖家转账（扣除税率）
            seller_receive = int(final_price * (1 - AUCTION_CONFIG['tax_rate']))
            # TODO: 给卖家增加灵石

            return TradeResult(
                True,
                f"成功以 {final_price} 灵石购买 {auction['item_name']}",
                auction['item_name'],
                1,
                final_price,
                player.stats.spirit_stones
            )
        else:
            # 退还灵石
            player.stats.spirit_stones += price
            return TradeResult(False, "购买失败")

    def finalize_auctions(self):
        """结束到期的拍卖"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 获取到期的拍卖
            cursor.execute("""
                SELECT * FROM auction_items 
                WHERE status = 'active' AND end_time <= ?
            """, (now,))

            rows = cursor.fetchall()
            for row in rows:
                auction_id = row['id']
                highest_bidder = row['highest_bidder_id']

                if highest_bidder:
                    # 有人竞拍，成交
                    cursor.execute("""
                        UPDATE auction_items 
                        SET status = 'sold' 
                        WHERE id = ?
                    """, (auction_id,))
                else:
                    # 无人竞拍，流拍
                    cursor.execute("""
                        UPDATE auction_items 
                        SET status = 'expired' 
                        WHERE id = ?
                    """, (auction_id,))

            conn.commit()
        except Exception as e:
            print(f"结束拍卖失败: {e}")

    # ==================== 玩家交易系统 ====================

    def create_trade_offer(
        self,
        sender_id: str,
        sender_name: str,
        receiver_id: str,
        receiver_name: str,
        item_name: str,
        item_type: str,
        quantity: int,
        price: int,
        offer_type: str = 'sell',
        message: str = "",
        expires_hours: int = 24
    ) -> Tuple[bool, str, Optional[int]]:
        """
        创建交易请求

        Args:
            sender_id: 发送者ID
            sender_name: 发送者名称
            receiver_id: 接收者ID
            receiver_name: 接收者名称
            item_name: 物品名称
            item_type: 物品类型
            quantity: 数量
            price: 价格
            offer_type: 请求类型（sell/buy）
            message: 留言
            expires_hours: 过期时间（小时）

        Returns:
            (是否成功, 消息, 请求ID)
        """
        expires_at = (datetime.now() + timedelta(hours=expires_hours)).isoformat()

        offer_data = {
            'sender_id': sender_id,
            'sender_name': sender_name,
            'receiver_id': receiver_id,
            'receiver_name': receiver_name,
            'item_name': item_name,
            'item_type': item_type,
            'quantity': quantity,
            'price': price,
            'offer_type': offer_type,
            'message': message,
            'expires_at': expires_at,
        }

        offer_id = self.db.create_trade_offer(offer_data)

        return True, f"成功创建交易请求，ID: {offer_id}", offer_id

    def get_pending_offers(self, player_id: str) -> List[Dict]:
        """
        获取待处理的交易请求

        Args:
            player_id: 玩家ID

        Returns:
            交易请求列表
        """
        return self.db.get_pending_offers(player_id)

    def accept_trade_offer(self, player, offer_id: int) -> TradeResult:
        """
        接受交易请求

        Args:
            player: 玩家对象
            offer_id: 请求ID

        Returns:
            交易结果
        """
        offers = self.db.get_pending_offers(player.stats.name)
        offer = None
        for o in offers:
            if o['id'] == offer_id:
                offer = o
                break

        if not offer:
            return TradeResult(False, "交易请求不存在或已过期")

        # 根据请求类型处理
        if offer['offer_type'] == 'sell':
            # 对方出售物品给我
            total_price = offer['price'] * offer['quantity']

            # 检查灵石
            if player.stats.spirit_stones < total_price:
                return TradeResult(False, f"灵石不足，需要: {total_price}")

            # 扣除灵石
            player.stats.spirit_stones -= total_price

            # 添加物品到背包
            from config.items import get_item
            db_item = get_item(offer['item_name'])
            if db_item:
                player.inventory.add_item(offer['item_name'], offer['quantity'])
            else:
                item_data = {
                    'name': offer['item_name'],
                    'type': offer['item_type'],
                    'value': offer['price'],
                }
                player.inventory.add_generated_item(offer['item_name'], item_data, offer['quantity'])

        else:
            # 对方购买我的物品
            # 检查背包
            item_count = player.inventory.get_item_count(offer['item_name'])
            if item_count < offer['quantity']:
                return TradeResult(False, f"物品数量不足，拥有: {item_count}")

            # 移除物品
            player.inventory.remove_item(offer['item_name'], offer['quantity'])

            # 增加灵石
            total_price = offer['price'] * offer['quantity']
            player.stats.spirit_stones += total_price

        # 更新请求状态
        self.db.respond_to_offer(offer_id, True, player.stats.name)

        return TradeResult(
            True,
            f"成功完成交易: {offer['item_name']} x{offer['quantity']}",
            offer['item_name'],
            offer['quantity'],
            offer['price'] * offer['quantity'],
            player.stats.spirit_stones
        )

    def reject_trade_offer(self, player, offer_id: int) -> bool:
        """
        拒绝交易请求

        Args:
            player: 玩家对象
            offer_id: 请求ID

        Returns:
            是否成功
        """
        return self.db.respond_to_offer(offer_id, False, player.stats.name)

    # ==================== 价格查询 ====================

    def get_price_history(self, item_name: str, limit: int = 30) -> List[Dict]:
        """
        获取物品价格历史

        Args:
            item_name: 物品名称
            limit: 返回记录数限制

        Returns:
            价格历史列表
        """
        return self.db.get_price_history(item_name, limit)

    def get_average_price(self, item_name: str) -> int:
        """
        获取物品平均价格

        Args:
            item_name: 物品名称

        Returns:
            平均价格
        """
        history = self.db.get_price_history(item_name, 30)
        if not history:
            return 0
        return sum(h['price'] for h in history) // len(history)

    # ==================== 工具方法 ====================

    def get_item_icon(self, item_type: str) -> str:
        """获取物品图标"""
        try:
            item_type_enum = ItemType(item_type)
            return get_item_type_icon(item_type_enum)
        except:
            return "📦"

    def get_rarity_color_code(self, rarity: str) -> str:
        """获取稀有度颜色代码"""
        try:
            rarity_enum = ItemRarity(rarity)
            return get_rarity_color(rarity_enum)
        except:
            return "#FFFFFF"


# 全局交易管理器实例
trade_manager = TradeManager()


if __name__ == "__main__":
    # 测试交易系统
    print("=" * 60)
    print("交易系统测试")
    print("=" * 60)

    # 初始化
    trade_manager.initialize()

    # 测试获取商店
    print("\n【新手村商店】")
    shops = trade_manager.get_shops_by_location("新手村")
    for shop in shops:
        print(f"  - {shop['name']} ({shop['shop_type']})")

    # 测试获取商品
    if shops:
        print(f"\n【{shops[0]['name']} 商品】")
        items = trade_manager.get_shop_items(shops[0]['id'])
        for item in items[:3]:
            print(f"  - {item['item_name']}: {item['current_price']} 灵石 (库存: {item['stock']})")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
