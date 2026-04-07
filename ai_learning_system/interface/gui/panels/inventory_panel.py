"""
背包道具面板 - 使用真实游戏数据
"""
import tkinter as tk
from tkinter import messagebox
from .base_panel import BasePanel
from ..theme import Theme


class InventoryPanel(BasePanel):
    """背包道具面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.item_listbox = None
        self.category_var = None
        self.capacity_var = None
        self.item_info_var = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🎒 背包",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左栏 - 物品列表和信息
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._setup_item_list(left_frame)
        self._setup_item_info(left_frame)

        # 右栏 - 操作按钮
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        self._setup_action_buttons(right_frame)

    def _setup_item_list(self, parent):
        """设置物品列表"""
        # 分类筛选和容量显示
        top_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # 分类筛选
        filter_label = tk.Label(
            top_frame,
            text="分类:",
            **Theme.get_label_style("normal")
        )
        filter_label.pack(side=tk.LEFT)

        self.category_var = tk.StringVar(value="all")
        categories = [
            ("全部", "all"),
            ("丹药", "pill"),
            ("材料", "material"),
            ("功法", "technique"),
            ("装备", "equipment"),
        ]

        category_menu = tk.OptionMenu(
            top_frame,
            self.category_var,
            *([cat[1] for cat in categories]),
            command=self._on_category_change
        )
        category_menu.config(
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_CYAN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            font=Theme.get_font(9)
        )
        category_menu.pack(side=tk.LEFT, padx=5)

        # 容量显示
        self.capacity_var = tk.StringVar(value="容量: 0/50")
        capacity_label = tk.Label(
            top_frame,
            textvariable=self.capacity_var,
            **Theme.get_label_style("subtitle")
        )
        capacity_label.pack(side=tk.RIGHT)

        # 物品列表框
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.item_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.item_listbox.yview)

        # 绑定选择事件
        self.item_listbox.bind("<<ListboxSelect>>", self._on_item_select)
        self.item_listbox.bind("<Double-Button-1>", self._on_item_double_click)
        self.item_listbox.bind("<Button-3>", self._on_item_right_click)

    def _setup_item_info(self, parent):
        """设置物品信息区域"""
        # 信息标题
        info_title = tk.Label(
            parent,
            text="物品信息",
            **Theme.get_label_style("subtitle")
        )
        info_title.pack(anchor=tk.W, pady=(10, 5))

        # 物品描述
        self.item_info_var = tk.StringVar(value="选择一个物品查看详情")
        info_label = tk.Label(
            parent,
            textvariable=self.item_info_var,
            wraplength=400,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))

    def _setup_action_buttons(self, parent):
        """设置操作按钮"""
        # 操作标题
        action_title = tk.Label(
            parent,
            text="操作",
            **Theme.get_label_style("subheading")
        )
        action_title.pack(anchor=tk.W, pady=(0, Theme.SPACING_MD))

        # 使用按钮
        use_btn = tk.Button(
            parent,
            text="✨ 使用",
            command=self._on_use,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=Theme.SPACING_MD,
            pady=Theme.SPACING_SM,
            cursor="hand2"
        )
        use_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 查看详情按钮
        detail_btn = tk.Button(
            parent,
            text="📋 详情",
            command=self._on_view_detail,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=Theme.SPACING_MD,
            pady=Theme.SPACING_SM,
            cursor="hand2"
        )
        detail_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 丢弃按钮
        drop_btn = tk.Button(
            parent,
            text="🗑️ 丢弃",
            command=self._on_drop,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=Theme.SPACING_MD,
            pady=Theme.SPACING_SM,
            cursor="hand2"
        )
        drop_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 分隔线
        separator = tk.Frame(parent, bg=Theme.BORDER_DEFAULT, height=1)
        separator.pack(fill=tk.X, pady=Theme.SPACING_MD)

        # 整理背包按钮
        sort_btn = tk.Button(
            parent,
            text="🔄 整理",
            command=self._on_sort,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_GREEN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=Theme.SPACING_MD,
            pady=Theme.SPACING_SM,
            cursor="hand2"
        )
        sort_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

    def _get_inventory(self):
        """获取背包 - 使用真实 Inventory 类"""
        player = self.get_player()
        if player and hasattr(player, 'inventory'):
            return player.inventory
        return None

    def _get_items(self):
        """获取物品列表 - 使用真实数据"""
        inventory = self._get_inventory()
        if inventory and hasattr(inventory, 'items'):
            if isinstance(inventory.items, dict):
                # inventory.items 的格式是 {item_name: InventoryItem}
                items_list = []
                for item_name, item in inventory.items.items():
                    # 创建一个包含所有必要属性的对象
                    item_data = item.item_data
                    # 构造一个简单的对象包装器
                    item_obj = type('ItemWrapper', (), {})()
                    item_obj.name = item_name
                    item_obj.quantity = item.count
                    item_obj.item_type = item_data.get('type', 'other')
                    item_obj.description = item_data.get('description', '暂无描述')
                    item_obj.rarity = item_data.get('rarity', '普通')
                    item_obj.data = item_data
                    items_list.append(item_obj)
                return items_list
        return []

    def _get_filtered_items(self):
        """获取筛选后的物品列表"""
        items = self._get_items()
        category = self.category_var.get()

        if category == "all":
            return items
        else:
            # 根据物品类型筛选 - 支持中英文类型
            filtered = []
            category_map = {
                "pill": ["pill", "丹药"],
                "material": ["material", "材料", "灵石", "消耗品"],
                "technique": ["technique", "秘籍"],
                "equipment": ["equipment", "法宝"],
            }
            target_types = category_map.get(category, [category])
            
            for item in items:
                item_type = getattr(item, 'item_type', 'other')
                if item_type in target_types:
                    filtered.append(item)
            return filtered

    def _get_category_name(self, category):
        """获取分类名称"""
        names = {
            "pill": "丹药",
            "material": "材料",
            "technique": "功法",
            "equipment": "装备",
            "丹药": "丹药",
            "材料": "材料",
            "法宝": "装备",
            "秘籍": "功法",
            "灵石": "材料",
            "消耗品": "材料",
        }
        return names.get(category, "其他")

    def _get_category_icon(self, item):
        """获取分类图标"""
        item_type = getattr(item, 'item_type', 'other')
        icons = {
            "pill": "💊",
            "material": "🪨",
            "technique": "📜",
            "equipment": "⚔️",
            "丹药": "💊",
            "材料": "🪨",
            "法宝": "⚔️",
            "秘籍": "📜",
            "灵石": "💎",
            "消耗品": "📦",
        }
        return icons.get(item_type, "📦")

    def refresh(self):
        """刷新面板 - 使用真实数据"""
        self.item_listbox.delete(0, tk.END)
        items = self._get_filtered_items()

        for item in items:
            name = getattr(item, 'name', '未知')
            quantity = getattr(item, 'quantity', 1)
            icon = self._get_category_icon(item)

            if quantity > 1:
                display_text = f"{icon} {name} x{quantity}"
            else:
                display_text = f"{icon} {name}"

            self.item_listbox.insert(tk.END, display_text)

        # 更新容量显示
        inventory = self._get_inventory()
        if inventory:
            current = len(inventory.items)
            # Inventory 使用 max_slots 而不是 capacity
            max_capacity = getattr(inventory, 'max_slots', 50)
            self.capacity_var.set(f"容量: {current}/{max_capacity}")
        else:
            self.capacity_var.set(f"容量: {len(items)}/50")

        # 清空物品信息
        self.item_info_var.set("选择一个物品查看详情")

    def _on_category_change(self, *args):
        """分类改变回调"""
        self.refresh()

    def _on_item_select(self, event=None):
        """物品选择事件"""
        selection = self.item_listbox.curselection()
        if selection:
            index = selection[0]
            items = self._get_filtered_items()
            if 0 <= index < len(items):
                item = items[index]
                self._update_item_info(item)

    def _update_item_info(self, item):
        """更新物品信息显示"""
        info = f"名称: {getattr(item, 'name', '未知')}\n"
        info += f"类型: {self._get_category_name(getattr(item, 'item_type', 'other'))}\n"
        info += f"数量: {getattr(item, 'quantity', 1)}\n"
        info += f"描述: {getattr(item, 'description', '暂无描述')}\n"

        # 显示属性
        if hasattr(item, 'properties') and item.properties:
            info += "\n属性:\n"
            for prop, value in item.properties.items():
                info += f"  {prop}: {value}\n"

        self.item_info_var.set(info)

    def _get_selected_item(self):
        """获取选中的物品"""
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个物品")
            return None

        index = selection[0]
        items = self._get_filtered_items()
        if 0 <= index < len(items):
            return items[index]
        return None

    def _on_item_double_click(self, event=None):
        """物品双击事件"""
        self._on_use()

    def _on_item_right_click(self, event=None):
        """物品右键事件"""
        self._on_view_detail()

    def _on_use(self):
        """使用按钮回调 - 使用真实物品系统"""
        item = self._get_selected_item()
        if not item:
            return

        name = getattr(item, 'name', '未知')
        item_type = getattr(item, 'item_type', 'other')

        # 执行使用
        player = self.get_player()

        if player:
            try:
                # 使用物品 - 调用player的use_item方法
                success, message = player.use_item(name)
                if success:
                    self.log(message, "system")
                else:
                    self.log(message, "system")
                self.refresh()

                # 刷新状态面板
                if self.main_window:
                    self.main_window.refresh_current_panel()
            except Exception as e:
                messagebox.showerror("错误", f"使用失败: {e}")
        else:
            # 模拟使用
            if item_type == "pill" or item_type == "丹药":
                self.log(f"你服用了 {name}，感觉体内灵力涌动", "system")
            elif item_type == "equipment" or item_type == "法宝":
                self.log(f"你装备了 {name}", "system")
            else:
                self.log(f"你使用了 {name}", "system")
            self.refresh()

    def _on_view_detail(self):
        """查看详情按钮回调"""
        item = self._get_selected_item()
        if not item:
            return

        name = getattr(item, 'name', '未知')
        item_type = getattr(item, 'item_type', 'other')
        quantity = getattr(item, 'quantity', 1)
        description = getattr(item, 'description', '暂无描述')
        category_name = self._get_category_name(item_type)

        # 构建详细信息
        info = f"名称: {name}\n"
        info += f"分类: {category_name}\n"
        info += f"数量: {quantity}\n"
        info += f"描述: {description}\n"

        # 显示属性
        if hasattr(item, 'properties') and item.properties:
            info += "\n属性:\n"
            for prop, value in item.properties.items():
                info += f"  {prop}: {value}\n"

        # 显示使用效果
        if hasattr(item, 'use_effect') and item.use_effect:
            info += f"\n使用效果: {item.use_effect}\n"

        messagebox.showinfo("物品详情", info)

    def _on_drop(self):
        """丢弃按钮回调"""
        item = self._get_selected_item()
        if not item:
            return

        name = getattr(item, 'name', '未知')

        if messagebox.askyesno("确认", f"确定要丢弃 {name} 吗？"):
            inventory = self._get_inventory()
            if inventory:
                try:
                    success, msg = inventory.remove_item(name)
                    if success:
                        self.log(f"你丢弃了 {name}", "system")
                    else:
                        self.log(f"丢弃 {name} 失败: {msg}", "system")
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("错误", f"丢弃失败: {e}")
            else:
                self.log(f"你丢弃了 {name}", "system")
                self.refresh()

    def _on_sort(self):
        """整理背包按钮回调"""
        inventory = self._get_inventory()
        if inventory and hasattr(inventory, 'sort_items'):
            try:
                inventory.sort_items()
                self.log("背包已整理", "system")
                self.refresh()
            except Exception as e:
                self.log(f"整理背包失败: {e}", "system")
        else:
            self.log("背包已整理", "system")
            self.refresh()
