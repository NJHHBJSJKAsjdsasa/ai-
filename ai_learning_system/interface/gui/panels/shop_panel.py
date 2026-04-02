"""
商店面板 - 实现NPC商店、拍卖行、玩家交易功能
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from .base_panel import BasePanel
from ..theme import Theme
from game.trade_system import trade_manager, TradeResult
from config.shop_config import ItemType, get_item_type_icon


class ShopPanel(BasePanel):
    """商店面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.current_shop = None
        self.current_items = []
        self.current_auctions = []
        self.shop_listbox = None
        self.item_listbox = None
        self.auction_listbox = None
        self.category_var = None
        self.quantity_var = None
        self.notebook = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🏪 商店与交易",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 创建标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置标签页样式
        style = ttk.Style()
        style.configure("TNotebook", background=Theme.BG_SECONDARY)
        style.configure("TNotebook.Tab", background=Theme.BG_TERTIARY, foreground=Theme.TEXT_PRIMARY)
        style.map("TNotebook.Tab", background=[("selected", Theme.ACCENT_CYAN)])

        # NPC商店标签页
        self.shop_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.shop_frame, text="🏪 NPC商店")
        self._setup_shop_tab()

        # 拍卖行标签页
        self.auction_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.auction_frame, text="🔨 拍卖行")
        self._setup_auction_tab()

        # 玩家交易标签页
        self.trade_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.trade_frame, text="🤝 玩家交易")
        self._setup_trade_tab()

        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _setup_shop_tab(self):
        """设置商店标签页"""
        # 左栏 - 商店列表
        left_frame = tk.Frame(self.shop_frame, bg=Theme.BG_SECONDARY, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # 当前位置
        location_label = tk.Label(
            left_frame,
            text="当前位置",
            **Theme.get_label_style("subtitle")
        )
        location_label.pack(anchor=tk.W, pady=(0, 5))

        self.location_var = tk.StringVar(value="新手村")
        location_display = tk.Label(
            left_frame,
            textvariable=self.location_var,
            **Theme.get_label_style("normal")
        )
        location_display.pack(anchor=tk.W, pady=(0, 10))

        # 商店列表
        shop_label = tk.Label(
            left_frame,
            text="商店列表",
            **Theme.get_label_style("subtitle")
        )
        shop_label.pack(anchor=tk.W, pady=(10, 5))

        self.shop_listbox = tk.Listbox(
            left_frame,
            **Theme.get_listbox_style(),
            height=10
        )
        self.shop_listbox.pack(fill=tk.BOTH, expand=True)
        self.shop_listbox.bind("<<ListboxSelect>>", self._on_shop_select)

        # 右栏 - 商品列表
        right_frame = tk.Frame(self.shop_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 商品筛选
        filter_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        filter_label = tk.Label(
            filter_frame,
            text="筛选:",
            **Theme.get_label_style("normal")
        )
        filter_label.pack(side=tk.LEFT)

        self.category_var = tk.StringVar(value="全部")
        categories = ["全部", "丹药", "材料", "法宝", "功法"]
        category_menu = tk.OptionMenu(
            filter_frame,
            self.category_var,
            *categories,
            command=self._on_category_change
        )
        category_menu.config(
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_CYAN,
            relief=tk.FLAT
        )
        category_menu.pack(side=tk.LEFT, padx=5)

        # 刷新按钮
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 刷新",
            command=self._refresh_shops,
            font=Theme.get_font(9),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT
        )
        refresh_btn.pack(side=tk.RIGHT)

        # 商品列表
        list_frame = tk.Frame(right_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 表头
        headers = ["物品", "类型", "价格", "库存", "需求"]
        header_frame = tk.Frame(list_frame, bg=Theme.BG_TERTIARY)
        header_frame.pack(fill=tk.X)
        for i, header in enumerate(headers):
            lbl = tk.Label(
                header_frame,
                text=header,
                width=12 if i == 0 else 10,
                **Theme.get_label_style("subtitle")
            )
            lbl.pack(side=tk.LEFT)

        self.item_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style(),
            height=15
        )
        self.item_listbox.pack(fill=tk.BOTH, expand=True)
        self.item_listbox.bind("<<ListboxSelect>>", self._on_item_select)
        self.item_listbox.bind("<Double-Button-1>", self._on_item_double_click)

        # 商品信息
        info_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, pady=10)

        self.item_info_var = tk.StringVar(value="选择一个商品查看详情")
        info_label = tk.Label(
            info_frame,
            textvariable=self.item_info_var,
            wraplength=400,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W)

        # 操作按钮
        btn_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=10)

        # 数量选择
        qty_label = tk.Label(
            btn_frame,
            text="数量:",
            **Theme.get_label_style("normal")
        )
        qty_label.pack(side=tk.LEFT)

        self.quantity_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(
            btn_frame,
            textvariable=self.quantity_var,
            width=5,
            **Theme.get_entry_style()
        )
        qty_entry.pack(side=tk.LEFT, padx=5)

        buy_btn = tk.Button(
            btn_frame,
            text="💰 购买",
            command=self._on_buy,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        buy_btn.pack(side=tk.LEFT, padx=10)

        sell_btn = tk.Button(
            btn_frame,
            text="💎 出售物品",
            command=self._on_sell,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        sell_btn.pack(side=tk.LEFT)

    def _setup_auction_tab(self):
        """设置拍卖行标签页"""
        # 顶部工具栏
        toolbar = tk.Frame(self.auction_frame, bg=Theme.BG_SECONDARY)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        filter_label = tk.Label(
            toolbar,
            text="筛选:",
            **Theme.get_label_style("normal")
        )
        filter_label.pack(side=tk.LEFT)

        self.auction_filter_var = tk.StringVar(value="全部")
        categories = ["全部", "丹药", "材料", "法宝", "功法"]
        filter_menu = tk.OptionMenu(
            toolbar,
            self.auction_filter_var,
            *categories,
            command=self._on_auction_filter_change
        )
        filter_menu.config(
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_CYAN,
            relief=tk.FLAT
        )
        filter_menu.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(
            toolbar,
            text="🔄 刷新",
            command=self._refresh_auctions,
            font=Theme.get_font(9),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)

        create_btn = tk.Button(
            toolbar,
            text="➕ 创建拍卖",
            command=self._on_create_auction,
            font=Theme.get_font(9),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT
        )
        create_btn.pack(side=tk.RIGHT)

        # 拍卖列表
        list_frame = tk.Frame(self.auction_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 表头
        headers = ["物品", "当前价", "一口价", "剩余时间", "出价次数"]
        header_frame = tk.Frame(list_frame, bg=Theme.BG_TERTIARY)
        header_frame.pack(fill=tk.X)
        for i, header in enumerate(headers):
            lbl = tk.Label(
                header_frame,
                text=header,
                width=15 if i == 0 else 12,
                **Theme.get_label_style("subtitle")
            )
            lbl.pack(side=tk.LEFT)

        self.auction_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style(),
            height=15
        )
        self.auction_listbox.pack(fill=tk.BOTH, expand=True)
        self.auction_listbox.bind("<<ListboxSelect>>", self._on_auction_select)

        # 拍卖信息
        info_frame = tk.Frame(self.auction_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, pady=10)

        self.auction_info_var = tk.StringVar(value="选择一个拍卖查看详情")
        info_label = tk.Label(
            info_frame,
            textvariable=self.auction_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W)

        # 操作按钮
        btn_frame = tk.Frame(self.auction_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=10)

        bid_btn = tk.Button(
            btn_frame,
            text="💰 出价",
            command=self._on_place_bid,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        bid_btn.pack(side=tk.LEFT, padx=5)

        buyout_btn = tk.Button(
            btn_frame,
            text="⚡ 一口价",
            command=self._on_buyout,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        buyout_btn.pack(side=tk.LEFT, padx=5)

    def _setup_trade_tab(self):
        """设置玩家交易标签页"""
        # 待处理请求
        pending_frame = tk.LabelFrame(
            self.trade_frame,
            text="待处理的交易请求",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.offer_listbox = tk.Listbox(
            pending_frame,
            **Theme.get_listbox_style(),
            height=10
        )
        self.offer_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.offer_listbox.bind("<<ListboxSelect>>", self._on_offer_select)

        # 请求详情
        info_frame = tk.Frame(self.trade_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.offer_info_var = tk.StringVar(value="选择一个请求查看详情")
        info_label = tk.Label(
            info_frame,
            textvariable=self.offer_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W)

        # 操作按钮
        btn_frame = tk.Frame(self.trade_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        accept_btn = tk.Button(
            btn_frame,
            text="✅ 接受",
            command=self._on_accept_offer,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        accept_btn.pack(side=tk.LEFT, padx=5)

        reject_btn = tk.Button(
            btn_frame,
            text="❌ 拒绝",
            command=self._on_reject_offer,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        reject_btn.pack(side=tk.LEFT, padx=5)

        create_offer_btn = tk.Button(
            btn_frame,
            text="➕ 发起交易",
            command=self._on_create_offer,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        create_offer_btn.pack(side=tk.RIGHT, padx=5)

    def refresh(self):
        """刷新面板"""
        # 初始化交易系统
        trade_manager.initialize()

        # 更新当前位置
        player = self.get_player()
        if player and hasattr(player.stats, 'location'):
            self.location_var.set(player.stats.location)
            self._refresh_shops()

        # 刷新拍卖行
        self._refresh_auctions()

        # 刷新交易请求
        self._refresh_offers()

    def _refresh_shops(self):
        """刷新商店列表"""
        self.shop_listbox.delete(0, tk.END)

        location = self.location_var.get()
        shops = trade_manager.get_shops_by_location(location)

        for shop in shops:
            display = f"{shop['name']} ({shop['shop_type']})"
            self.shop_listbox.insert(tk.END, display)
            # 存储商店ID
            self.shop_listbox.itemconfig(tk.END, {'bg': Theme.BG_PRIMARY})

        # 保存商店数据
        self._shops_data = shops

    def _refresh_shop_items(self):
        """刷新商品列表"""
        self.item_listbox.delete(0, tk.END)
        self.current_items = []

        if not self.current_shop:
            return

        items = trade_manager.get_shop_items(self.current_shop['id'])

        # 筛选
        category = self.category_var.get()
        if category != "全部":
            items = [item for item in items if item['item_type'] == category]

        for item in items:
            icon = trade_manager.get_item_icon(item['item_type'])
            display = (
                f"{icon} {item['item_name']:<12} "
                f"{item['item_type']:<8} "
                f"{item['current_price']:<8} "
                f"{item['stock']:<6} "
                f"{item['level_required']}层"
            )
            self.item_listbox.insert(tk.END, display)

            # 根据稀有度设置颜色
            color = trade_manager.get_rarity_color_code(item['rarity'])
            self.item_listbox.itemconfig(tk.END, {'fg': color})

        self.current_items = items

    def _refresh_auctions(self):
        """刷新拍卖列表"""
        self.auction_listbox.delete(0, tk.END)
        self.current_auctions = []

        # 筛选
        category = self.auction_filter_var.get() if hasattr(self, 'auction_filter_var') else "全部"
        item_type = None if category == "全部" else category

        auctions = trade_manager.get_active_auctions(item_type)

        for auction in auctions:
            buyout = str(auction.buyout_price) if auction.buyout_price else "无"
            display = (
                f"{auction.item_name:<15} "
                f"{auction.current_price:<12} "
                f"{buyout:<12} "
                f"{auction.time_remaining:<12} "
                f"{auction.bid_count}次"
            )
            self.auction_listbox.insert(tk.END, display)

            # 根据稀有度设置颜色
            color = trade_manager.get_rarity_color_code(auction.rarity)
            self.auction_listbox.itemconfig(tk.END, {'fg': color})

        self.current_auctions = auctions

    def _refresh_offers(self):
        """刷新交易请求"""
        if not hasattr(self, 'offer_listbox'):
            return

        self.offer_listbox.delete(0, tk.END)

        player = self.get_player()
        if not player:
            return

        offers = trade_manager.get_pending_offers(player.stats.name)

        for offer in offers:
            if offer['offer_type'] == 'sell':
                display = f"📤 {offer['sender_name']} 出售 {offer['item_name']} x{offer['quantity']} ({offer['price']}灵石/个)"
            else:
                display = f"📥 {offer['sender_name']} 求购 {offer['item_name']} x{offer['quantity']} ({offer['price']}灵石/个)"
            self.offer_listbox.insert(tk.END, display)

        self._offers_data = offers

    def _on_tab_changed(self, event=None):
        """标签页切换事件"""
        current = self.notebook.index(self.notebook.select())
        if current == 0:  # 商店
            self._refresh_shops()
        elif current == 1:  # 拍卖行
            self._refresh_auctions()
        elif current == 2:  # 玩家交易
            self._refresh_offers()

    def _on_shop_select(self, event=None):
        """商店选择事件"""
        selection = self.shop_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if 0 <= index < len(self._shops_data):
            self.current_shop = self._shops_data[index]
            self._refresh_shop_items()

    def _on_category_change(self, *args):
        """分类改变事件"""
        self._refresh_shop_items()

    def _on_auction_filter_change(self, *args):
        """拍卖筛选改变事件"""
        self._refresh_auctions()

    def _on_item_select(self, event=None):
        """商品选择事件"""
        selection = self.item_listbox.curselection()
        if not selection or not self.current_items:
            return

        index = selection[0]
        if 0 <= index < len(self.current_items):
            item = self.current_items[index]
            info = f"【{item['item_name']}】\n"
            info += f"类型: {item['item_type']} | 稀有度: {item['rarity']}\n"
            info += f"价格: {item['current_price']} 灵石\n"
            info += f"库存: {item['stock']}\n"
            info += f"需求境界: {item['level_required']}层\n"
            info += f"描述: {item['description']}"
            self.item_info_var.set(info)

    def _on_item_double_click(self, event=None):
        """商品双击事件"""
        self._on_buy()

    def _on_buy(self):
        """购买按钮"""
        selection = self.item_listbox.curselection()
        if not selection or not self.current_items:
            messagebox.showinfo("提示", "请先选择一个商品")
            return

        index = selection[0]
        if index >= len(self.current_items):
            return

        item = self.current_items[index]
        player = self.get_player()

        if not player:
            messagebox.showerror("错误", "无法获取玩家信息")
            return

        # 获取数量
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 1:
                quantity = 1
        except:
            quantity = 1

        # 确认购买
        total = item['current_price'] * quantity
        if not messagebox.askyesno(
            "确认购买",
            f"购买 {item['item_name']} x{quantity}\n"
            f"单价: {item['current_price']} 灵石\n"
            f"总计: {total} 灵石\n\n"
            f"确认购买吗？"
        ):
            return

        # 执行购买
        result = trade_manager.buy_item(
            player,
            self.current_shop['id'],
            item['id'],
            quantity
        )

        if result.success:
            messagebox.showinfo("成功", result.message)
            self._refresh_shop_items()
            self.log(result.message, "success")
        else:
            messagebox.showerror("失败", result.message)
            self.log(result.message, "error")

    def _on_sell(self):
        """出售按钮"""
        player = self.get_player()
        if not player:
            return

        # 获取背包物品
        items = list(player.inventory.items.keys())
        if not items:
            messagebox.showinfo("提示", "背包为空")
            return

        # 创建出售对话框
        dialog = tk.Toplevel(self)
        dialog.title("出售物品")
        dialog.geometry("300x400")
        dialog.config(bg=Theme.BG_SECONDARY)

        # 物品列表
        tk.Label(
            dialog,
            text="选择要出售的物品:",
            **Theme.get_label_style("subtitle")
        ).pack(pady=10)

        item_listbox = tk.Listbox(
            dialog,
            **Theme.get_listbox_style(),
            height=10
        )
        item_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for item_name in items:
            count = player.inventory.get_item_count(item_name)
            item_listbox.insert(tk.END, f"{item_name} x{count}")

        # 数量
        qty_frame = tk.Frame(dialog, bg=Theme.BG_SECONDARY)
        qty_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            qty_frame,
            text="数量:",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)

        qty_var = tk.StringVar(value="1")
        qty_entry = tk.Entry(
            qty_frame,
            textvariable=qty_var,
            width=5,
            **Theme.get_entry_style()
        )
        qty_entry.pack(side=tk.LEFT, padx=5)

        def do_sell():
            selection = item_listbox.curselection()
            if not selection:
                return

            item_name = items[selection[0]]
            try:
                quantity = int(qty_var.get())
            except:
                quantity = 1

            result = trade_manager.sell_item(
                player,
                self.current_shop['id'] if self.current_shop else "",
                item_name,
                quantity
            )

            if result.success:
                messagebox.showinfo("成功", result.message)
                self.log(result.message, "success")
                dialog.destroy()
            else:
                messagebox.showerror("失败", result.message)

        tk.Button(
            dialog,
            text="出售",
            command=do_sell,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT
        ).pack(pady=10)

    def _on_auction_select(self, event=None):
        """拍卖选择事件"""
        selection = self.auction_listbox.curselection()
        if not selection or not self.current_auctions:
            return

        index = selection[0]
        if 0 <= index < len(self.current_auctions):
            auction = self.current_auctions[index]
            info = f"【{auction.item_name}】\n"
            info += f"类型: {auction.item_type} | 稀有度: {auction.rarity}\n"
            info += f"起拍价: {auction.start_price} 灵石\n"
            info += f"当前价: {auction.current_price} 灵石\n"
            if auction.buyout_price:
                info += f"一口价: {auction.buyout_price} 灵石\n"
            info += f"加价幅度: {auction.bid_increment} 灵石\n"
            info += f"剩余时间: {auction.time_remaining}\n"
            info += f"出价次数: {auction.bid_count}\n"
            if auction.highest_bidder_name:
                info += f"最高出价者: {auction.highest_bidder_name}\n"
            info += f"描述: {auction.description}"
            self.auction_info_var.set(info)

    def _on_place_bid(self):
        """出价按钮"""
        selection = self.auction_listbox.curselection()
        if not selection or not self.current_auctions:
            messagebox.showinfo("提示", "请先选择一个拍卖")
            return

        index = selection[0]
        auction = self.current_auctions[index]
        player = self.get_player()

        if not player:
            return

        # 输入出价
        min_bid = auction.current_price + auction.bid_increment
        bid = simpledialog.askinteger(
            "出价",
            f"当前价格: {auction.current_price}\n"
            f"最低出价: {min_bid}\n"
            f"请输入出价金额:",
            minvalue=min_bid,
            initialvalue=min_bid
        )

        if not bid:
            return

        result = trade_manager.place_bid(player, auction.id, bid)

        if result.success:
            messagebox.showinfo("成功", result.message)
            self._refresh_auctions()
            self.log(result.message, "success")
        else:
            messagebox.showerror("失败", result.message)

    def _on_buyout(self):
        """一口价按钮"""
        selection = self.auction_listbox.curselection()
        if not selection or not self.current_auctions:
            messagebox.showinfo("提示", "请先选择一个拍卖")
            return

        index = selection[0]
        auction = self.current_auctions[index]

        if not auction.buyout_price:
            messagebox.showinfo("提示", "该拍卖不支持一口价")
            return

        player = self.get_player()
        if not player:
            return

        if not messagebox.askyesno(
            "确认购买",
            f"以 {auction.buyout_price} 灵石购买 {auction.item_name}？"
        ):
            return

        result = trade_manager.buyout_auction(player, auction.id)

        if result.success:
            messagebox.showinfo("成功", result.message)
            self._refresh_auctions()
            self.log(result.message, "success")
        else:
            messagebox.showerror("失败", result.message)

    def _on_create_auction(self):
        """创建拍卖"""
        player = self.get_player()
        if not player:
            return

        items = list(player.inventory.items.keys())
        if not items:
            messagebox.showinfo("提示", "背包为空")
            return

        # 创建拍卖对话框
        dialog = tk.Toplevel(self)
        dialog.title("创建拍卖")
        dialog.geometry("350x500")
        dialog.config(bg=Theme.BG_SECONDARY)

        # 物品选择
        tk.Label(
            dialog,
            text="选择物品:",
            **Theme.get_label_style("subtitle")
        ).pack(pady=5)

        item_listbox = tk.Listbox(
            dialog,
            **Theme.get_listbox_style(),
            height=8
        )
        item_listbox.pack(fill=tk.X, padx=10, pady=5)

        for item_name in items:
            count = player.inventory.get_item_count(item_name)
            item_listbox.insert(tk.END, f"{item_name} x{count}")

        # 价格设置
        price_frame = tk.Frame(dialog, bg=Theme.BG_SECONDARY)
        price_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            price_frame,
            text="起拍价:",
            **Theme.get_label_style("normal")
        ).pack(anchor=tk.W)

        start_price_var = tk.StringVar(value="100")
        tk.Entry(
            price_frame,
            textvariable=start_price_var,
            **Theme.get_entry_style()
        ).pack(fill=tk.X)

        tk.Label(
            price_frame,
            text="一口价 (可选):",
            **Theme.get_label_style("normal")
        ).pack(anchor=tk.W, pady=(10, 0))

        buyout_var = tk.StringVar(value="")
        tk.Entry(
            price_frame,
            textvariable=buyout_var,
            **Theme.get_entry_style()
        ).pack(fill=tk.X)

        tk.Label(
            price_frame,
            text="时长 (小时):",
            **Theme.get_label_style("normal")
        ).pack(anchor=tk.W, pady=(10, 0))

        duration_var = tk.StringVar(value="24")
        tk.Entry(
            price_frame,
            textvariable=duration_var,
            **Theme.get_entry_style()
        ).pack(fill=tk.X)

        def do_create():
            selection = item_listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请选择物品")
                return

            item_name = items[selection[0]]

            try:
                start_price = int(start_price_var.get())
                buyout = int(buyout_var.get()) if buyout_var.get() else None
                duration = int(duration_var.get())
            except:
                messagebox.showerror("错误", "请输入有效的数字")
                return

            # 获取物品类型
            from config.items import get_item
            db_item = get_item(item_name)
            item_type = db_item.item_type.value if db_item else "其他"
            rarity = db_item.rarity.value if db_item else "普通"

            # 创建拍卖
            success, msg, auction_id = trade_manager.create_auction(
                seller_id=player.stats.name,
                seller_name=player.stats.name,
                item_name=item_name,
                item_type=item_type,
                start_price=start_price,
                buyout_price=buyout,
                duration_hours=duration,
                rarity=rarity
            )

            if success:
                # 从背包移除物品
                player.inventory.remove_item(item_name, 1)
                messagebox.showinfo("成功", msg)
                self.log(msg, "success")
                dialog.destroy()
                self._refresh_auctions()
            else:
                messagebox.showerror("失败", msg)

        tk.Button(
            dialog,
            text="创建拍卖",
            command=do_create,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT
        ).pack(pady=20)

    def _on_offer_select(self, event=None):
        """交易请求选择事件"""
        selection = self.offer_listbox.curselection()
        if not selection or not hasattr(self, '_offers_data'):
            return

        index = selection[0]
        if 0 <= index < len(self._offers_data):
            offer = self._offers_data[index]
            info = f"【交易请求 #{offer['id']}】\n"
            info += f"来自: {offer['sender_name']}\n"
            info += f"类型: {'出售' if offer['offer_type'] == 'sell' else '求购'}\n"
            info += f"物品: {offer['item_name']} x{offer['quantity']}\n"
            info += f"单价: {offer['price']} 灵石\n"
            info += f"总价: {offer['price'] * offer['quantity']} 灵石\n"
            if offer['message']:
                info += f"留言: {offer['message']}\n"
            info += f"过期时间: {offer['expires_at'][:16]}"
            self.offer_info_var.set(info)

    def _on_accept_offer(self):
        """接受交易请求"""
        selection = self.offer_listbox.curselection()
        if not selection or not hasattr(self, '_offers_data'):
            messagebox.showinfo("提示", "请先选择一个交易请求")
            return

        index = selection[0]
        offer = self._offers_data[index]
        player = self.get_player()

        if not player:
            return

        result = trade_manager.accept_trade_offer(player, offer['id'])

        if result.success:
            messagebox.showinfo("成功", result.message)
            self._refresh_offers()
            self.log(result.message, "success")
        else:
            messagebox.showerror("失败", result.message)

    def _on_reject_offer(self):
        """拒绝交易请求"""
        selection = self.offer_listbox.curselection()
        if not selection or not hasattr(self, '_offers_data'):
            messagebox.showinfo("提示", "请先选择一个交易请求")
            return

        index = selection[0]
        offer = self._offers_data[index]
        player = self.get_player()

        if not player:
            return

        if trade_manager.reject_trade_offer(player, offer['id']):
            messagebox.showinfo("成功", "已拒绝交易请求")
            self._refresh_offers()
        else:
            messagebox.showerror("失败", "操作失败")

    def _on_create_offer(self):
        """发起交易"""
        messagebox.showinfo("提示", "玩家交易功能需要指定交易对象\n请在游戏中与其他玩家互动时发起交易")

    def on_show(self):
        """当面板显示时"""
        self.refresh()
