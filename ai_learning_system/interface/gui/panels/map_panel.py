"""
地图探索面板 - 树形结构显示，支持境界限制和筛选
"""
import tkinter as tk
from tkinter import messagebox, ttk
from .base_panel import BasePanel
from ..theme import Theme


class MapPanel(BasePanel):
    """地图探索面板 - 树形结构"""

    def __init__(self, parent, main_window, **kwargs):
        self.location_tree = None
        self.map_canvas = None
        self.current_location_var = None
        self.location_info_var = None
        self.filter_var = None
        self.show_accessible_only_var = None
        self.expanded_nodes = set()  # 记录展开的节点
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🗺️ 世界地图",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左栏 - 地图可视化
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._setup_map_canvas(left_frame)

        # 右栏 - 地点树和操作
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        self._setup_filters(right_frame)
        self._setup_location_tree(right_frame)
        self._setup_location_info(right_frame)
        self._setup_action_buttons(right_frame)

    def _setup_filters(self, parent):
        """设置筛选控件"""
        filter_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=10, pady=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # 标题
        title = tk.Label(
            filter_frame,
            text="🔍 筛选",
            **Theme.get_label_style("subtitle")
        )
        title.pack(anchor=tk.W)

        # 只显示可前往
        self.show_accessible_only_var = tk.BooleanVar(value=False)
        accessible_check = tk.Checkbutton(
            filter_frame,
            text="只显示可前往",
            variable=self.show_accessible_only_var,
            command=self._on_filter_change,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            selectcolor=Theme.BG_SECONDARY,
            font=Theme.get_font(10)
        )
        accessible_check.pack(anchor=tk.W, pady=(5, 0))

        # 境界筛选
        filter_row = tk.Frame(filter_frame, bg=Theme.BG_TERTIARY)
        filter_row.pack(fill=tk.X, pady=(5, 0))

        tk.Label(
            filter_row,
            text="境界:",
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10)
        ).pack(side=tk.LEFT)

        self.filter_var = tk.StringVar(value="all")
        realm_values = ["all", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        realm_names = ["全部", "凡人", "炼气", "筑基", "结丹", "元婴", "化神", "炼虚", "合体", "大乘", "真仙"]

        self.realm_combo = ttk.Combobox(
            filter_row,
            textvariable=self.filter_var,
            values=realm_names,
            state="readonly",
            width=12
        )
        self.realm_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.realm_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 保存realm值到名称的映射
        self.realm_value_map = dict(zip(realm_names, realm_values))

    def _setup_map_canvas(self, parent):
        """设置地图画布"""
        # 当前位置显示
        self.current_location_var = tk.StringVar(value="当前位置: 新手村")
        location_label = tk.Label(
            parent,
            textvariable=self.current_location_var,
            **Theme.get_label_style("subtitle")
        )
        location_label.pack(anchor=tk.W, pady=(0, 10))

        # 地图画布
        map_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=2, pady=2)
        map_frame.pack(fill=tk.BOTH, expand=True)

        self.map_canvas = tk.Canvas(
            map_frame,
            bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.map_canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定画布大小变化事件
        self.map_canvas.bind("<Configure>", self._on_canvas_resize)

    def _setup_location_tree(self, parent):
        """设置地点树形列表"""
        # 列表标题
        list_title = tk.Label(
            parent,
            text="📍 地点列表",
            **Theme.get_label_style("subtitle")
        )
        list_title.pack(anchor=tk.W, pady=(0, 10))

        # 树形列表框
        tree_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建Treeview
        columns = ("name", "realm", "danger")
        self.location_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            height=12
        )

        # 定义列
        self.location_tree.heading("#0", text="地点")
        self.location_tree.heading("name", text="名称")
        self.location_tree.heading("realm", text="境界要求")
        self.location_tree.heading("danger", text="危险度")

        self.location_tree.column("#0", width=80, minwidth=80)
        self.location_tree.column("name", width=80, minwidth=80)
        self.location_tree.column("realm", width=60, minwidth=60)
        self.location_tree.column("danger", width=50, minwidth=50)

        self.location_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.location_tree.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.location_tree.yview)

        # 绑定选择事件
        self.location_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.location_tree.bind("<Double-Button-1>", self._on_tree_double_click)

    def _setup_location_info(self, parent):
        """设置地点信息区域"""
        # 信息标题
        info_title = tk.Label(
            parent,
            text="📋 地点信息",
            **Theme.get_label_style("subtitle")
        )
        info_title.pack(anchor=tk.W, pady=(10, 5))

        # 地点信息
        self.location_info_var = tk.StringVar(value="选择一个地点查看详情")
        info_label = tk.Label(
            parent,
            textvariable=self.location_info_var,
            wraplength=290,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))

    def _setup_action_buttons(self, parent):
        """设置操作按钮"""
        # 操作标题
        action_title = tk.Label(
            parent,
            text="🎮 操作",
            **Theme.get_label_style("subtitle")
        )
        action_title.pack(anchor=tk.W, pady=(10, 10))

        # 前往按钮
        self.go_btn = tk.Button(
            parent,
            text="🚶 前往",
            command=self._on_go,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.go_btn.pack(fill=tk.X, pady=5)

        # 展开/折叠按钮
        btn_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=5)

        expand_btn = tk.Button(
            btn_frame,
            text="📂 展开全部",
            command=self._expand_all,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        expand_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        collapse_btn = tk.Button(
            btn_frame,
            text="📁 折叠全部",
            command=self._collapse_all,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        collapse_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

    def _on_canvas_resize(self, event=None):
        """画布大小变化时重绘"""
        self._draw_tree_map()

    def _draw_tree_map(self):
        """绘制树形地图"""
        if not self.map_canvas:
            return

        self.map_canvas.delete("all")

        width = self.map_canvas.winfo_width()
        height = self.map_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # 获取地点数据
        locations = self._get_filtered_locations()
        current_location = self._get_current_location()
        player_realm = self._get_player_realm()

        if not locations:
            self._draw_empty_map(width, height)
            return

        # 计算树形布局
        node_positions = self._calculate_tree_positions(locations, width, height)

        # 绘制连接线
        self._draw_connections(node_positions, locations)

        # 绘制节点
        for location_id, (x, y) in node_positions.items():
            location = locations.get(location_id)
            if location is None:
                continue

            name = getattr(location, 'name', location_id)
            is_current = location_id == current_location
            is_accessible = location.is_accessible(player_realm) if hasattr(location, 'is_accessible') else True

            # 节点颜色根据危险等级
            danger_colors = {
                "安全": Theme.ACCENT_GREEN,
                "普通": Theme.ACCENT_CYAN,
                "危险": Theme.ACCENT_GOLD,
                "绝境": Theme.ACCENT_RED,
            }
            base_color = danger_colors.get(getattr(location, 'danger_level', '普通'), Theme.ACCENT_CYAN)

            # 如果不可进入，颜色变暗
            if not is_accessible:
                base_color = "#555555"

            # 当前位置高亮
            if is_current:
                radius = 20
                outline_color = Theme.ACCENT_GOLD
                outline_width = 3
            else:
                radius = 15
                outline_color = ""
                outline_width = 0

            # 绘制节点圆形
            self.map_canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=base_color,
                outline=outline_color,
                width=outline_width,
                tags=(f"node_{location_id}", "node")
            )

            # 绑定点击事件
            self.map_canvas.tag_bind(f"node_{location_id}", "<Button-1>",
                                     lambda e, lid=location_id: self._on_node_click(lid))

            # 绘制地点名称
            self.map_canvas.create_text(
                x, y + radius + 12,
                text=name,
                fill=Theme.TEXT_PRIMARY if is_accessible else Theme.TEXT_SECONDARY,
                font=Theme.get_font(9, bold=is_current)
            )

            # 如果是当前位置，添加标记
            if is_current:
                self.map_canvas.create_text(
                    x, y - radius - 10,
                    text="★",
                    fill=Theme.ACCENT_GOLD,
                    font=Theme.get_font(14)
                )

            # 绘制境界要求（小字）
            realm_name = location.get_realm_name() if hasattr(location, 'get_realm_name') else "凡人"
            self.map_canvas.create_text(
                x, y + radius + 25,
                text=f"({realm_name})",
                fill=Theme.TEXT_SECONDARY,
                font=Theme.get_font(8)
            )

    def _draw_connections(self, node_positions, locations):
        """绘制节点之间的连接线"""
        for location_id, (x, y) in node_positions.items():
            location = locations.get(location_id)
            if not location:
                continue

            # 连接到父节点
            parent_name = getattr(location, 'parent_location', '')
            if parent_name and parent_name in node_positions:
                px, py = node_positions[parent_name]
                self.map_canvas.create_line(
                    x, y - 15, px, py + 15,
                    fill=Theme.BORDER_LIGHT,
                    width=2
                )

            # 连接到兄弟节点（可选，避免线条过多）
            # for conn_id in getattr(location, 'connections', []):
            #     if conn_id in node_positions and conn_id != parent_name:
            #         cx, cy = node_positions[conn_id]
            #         self.map_canvas.create_line(
            #             x, y, cx, cy,
            #             fill=Theme.BORDER_DARK,
            #             width=1,
            #             dash=(4, 4)
            #         )

    def _calculate_tree_positions(self, locations, width, height):
        """计算树形布局的节点位置"""
        positions = {}

        # 找出根节点（没有父节点的）
        root_locations = [
            loc_id for loc_id, loc in locations.items()
            if not getattr(loc, 'parent_location', '')
        ]

        if not root_locations:
            return positions

        # 按层级组织节点
        levels = {}

        def get_level(loc_id, visited=None):
            if visited is None:
                visited = set()
            if loc_id in visited:
                return 0
            visited.add(loc_id)

            loc = locations.get(loc_id)
            if not loc:
                return 0
            parent = getattr(loc, 'parent_location', '')
            if not parent or parent not in locations:
                return 0
            return 1 + get_level(parent, visited)

        for loc_id in locations:
            level = get_level(loc_id)
            if level not in levels:
                levels[level] = []
            levels[level].append(loc_id)

        # 计算位置
        level_height = height / (max(levels.keys()) + 2) if levels else height / 2

        for level, loc_ids in levels.items():
            y = (level + 1) * level_height
            count = len(loc_ids)
            if count == 1:
                positions[loc_ids[0]] = (width / 2, y)
            else:
                spacing = width / (count + 1)
                for i, loc_id in enumerate(loc_ids):
                    x = (i + 1) * spacing
                    positions[loc_id] = (x, y)

        return positions

    def _draw_empty_map(self, width, height):
        """绘制空地图提示"""
        self.map_canvas.create_text(
            width / 2, height / 2,
            text="暂无地图数据",
            fill=Theme.TEXT_SECONDARY,
            font=Theme.get_font(14)
        )

    def _on_node_click(self, location_id):
        """节点点击事件"""
        # 在树形列表中选中对应项
        self._select_tree_item(location_id)

    def _get_filtered_locations(self):
        """获取筛选后的地点"""
        locations = self._get_locations()
        if not locations:
            return {}

        player_realm = self._get_player_realm()

        # 只显示可前往的地点
        if self.show_accessible_only_var and self.show_accessible_only_var.get():
            locations = {
                k: v for k, v in locations.items()
                if (v.is_accessible(player_realm) if hasattr(v, 'is_accessible') else True)
            }

        # 按境界筛选
        if self.filter_var:
            filter_value = self.filter_var.get()
            if filter_value != "all" and filter_value != "全部":
                # 获取对应的realm值
                realm_value = self.realm_value_map.get(filter_value, filter_value)
                try:
                    realm_level = int(realm_value)
                    locations = {
                        k: v for k, v in locations.items()
                        if getattr(v, 'realm_required', 0) == realm_level
                    }
                except ValueError:
                    pass

        return locations

    def _get_locations(self):
        """获取地点数据 - 使用真实世界数据"""
        world = self.get_world()
        if world and hasattr(world, 'locations'):
            return world.locations
        return {}

    def _get_current_location(self):
        """获取当前位置 - 使用真实玩家数据"""
        player = self.get_player()
        if player and hasattr(player, 'stats'):
            return player.stats.location
        return "新手村"

    def _get_player_realm(self):
        """获取玩家境界等级"""
        player = self.get_player()
        if player and hasattr(player, 'stats'):
            return player.stats.realm_level
        return 0

    def _on_filter_change(self, event=None):
        """筛选条件变化"""
        self.refresh()

    def _select_tree_item(self, location_id):
        """在树形列表中选中指定项"""
        # 查找对应的tree item
        for item in self.location_tree.get_children():
            if self._find_and_select_item(item, location_id):
                return

    def _find_and_select_item(self, item, location_id):
        """递归查找并选中树节点"""
        # 检查当前项
        values = self.location_tree.item(item, 'values')
        if values and values[0] == location_id:
            self.location_tree.selection_set(item)
            self.location_tree.see(item)
            self._on_tree_select()
            return True

        # 递归检查子项
        for child in self.location_tree.get_children(item):
            if self._find_and_select_item(child, location_id):
                return True

        return False

    def _on_tree_select(self, event=None):
        """树节点选择事件"""
        selection = self.location_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.location_tree.item(item, 'values')
        if not values:
            return

        location_name = values[0]
        location = self._get_locations().get(location_name)

        if location:
            # 显示地点详情
            realm_name = location.get_realm_name() if hasattr(location, 'get_realm_name') else "凡人"
            danger = getattr(location, 'danger_level', '普通')
            loc_type = getattr(location, 'location_type', '普通')
            desc = getattr(location, 'description', '暂无描述')

            player_realm = self._get_player_realm()
            is_accessible = location.is_accessible(player_realm) if hasattr(location, 'is_accessible') else True

            status_icon = "✓" if is_accessible else "✗"
            status_color = "可进入" if is_accessible else "境界不足"

            info = f"【{location_name}】\n"
            info += f"类型: {loc_type}\n"
            info += f"境界要求: {realm_name} {status_icon}\n"
            info += f"危险等级: {danger}\n"
            info += f"状态: {status_color}\n\n"
            info += f"描述: {desc}"

            self.location_info_var.set(info)

            # 更新前往按钮状态
            if is_accessible:
                self.go_btn.config(state=tk.NORMAL, bg=Theme.ACCENT_GOLD)
            else:
                self.go_btn.config(state=tk.DISABLED, bg=Theme.BG_TERTIARY)

    def _on_tree_double_click(self, event=None):
        """树节点双击事件"""
        self._on_go()

    def _on_go(self):
        """前往按钮回调 - 检查境界限制"""
        selection = self.location_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个地点")
            return

        item = selection[0]
        values = self.location_tree.item(item, 'values')
        if not values:
            return

        location_name = values[0]

        # 执行移动
        player = self.get_player()
        world = self.get_world()

        if player and world:
            try:
                # 检查境界限制
                location = world.locations.get(location_name)
                if location and hasattr(location, 'is_accessible'):
                    if not location.is_accessible(player.stats.realm_level):
                        realm_name = location.get_realm_name()
                        current_realm_name = player.stats.get_realm_name() if hasattr(player.stats, 'get_realm_name') else "凡人"
                        messagebox.showwarning(
                            "境界不足",
                            f"你的修为不足以进入此地\n\n"
                            f"需要: {realm_name}\n"
                            f"当前: {current_realm_name}\n\n"
                            f"请先提升境界或寻找其他路径。"
                        )
                        return

                current_loc = player.stats.location
                if location_name == current_loc:
                    self.log("你已经在该地点了", "system")
                    return

                # 更新玩家位置
                player.stats.location = location_name

                # 为新位置生成NPC
                if hasattr(world, 'npc_manager'):
                    world.npc_manager.generate_npcs_for_location(location_name, count=3)

                self.log(f"你来到了 {location_name}", "exploration")
                self.refresh()

                # 刷新其他面板
                if self.main_window:
                    self.main_window.refresh_all_panels()
            except Exception as e:
                messagebox.showerror("错误", f"移动失败: {e}")
        else:
            self.log(f"你前往了 {location_name}", "exploration")
            self.refresh()

    def _expand_all(self):
        """展开所有节点"""
        def expand_children(item):
            self.location_tree.item(item, open=True)
            for child in self.location_tree.get_children(item):
                expand_children(child)

        for item in self.location_tree.get_children():
            expand_children(item)

    def _collapse_all(self):
        """折叠所有节点"""
        def collapse_children(item):
            self.location_tree.item(item, open=False)
            for child in self.location_tree.get_children(item):
                collapse_children(child)

        for item in self.location_tree.get_children():
            collapse_children(item)

    def refresh(self):
        """刷新面板 - 使用真实数据"""
        # 更新当前位置显示
        current = self._get_current_location()
        self.current_location_var.set(f"当前位置: {current}")

        # 清空树形列表
        for item in self.location_tree.get_children():
            self.location_tree.delete(item)

        # 获取地点数据
        locations = self._get_filtered_locations()

        if locations:
            # 构建树形结构
            self._build_location_tree(locations)

        # 重绘地图
        self._draw_tree_map()

        # 清空地点信息
        self.location_info_var.set("选择一个地点查看详情")
        self.go_btn.config(state=tk.NORMAL, bg=Theme.ACCENT_GOLD)

    def _build_location_tree(self, locations):
        """构建地点树形结构"""
        # 找出根节点
        root_locations = [
            (loc_id, loc) for loc_id, loc in locations.items()
            if not getattr(loc, 'parent_location', '')
        ]

        # 递归添加节点
        def add_node(parent_item, location_id, location):
            realm_name = location.get_realm_name() if hasattr(location, 'get_realm_name') else "凡人"
            danger = getattr(location, 'danger_level', '普通')

            # 图标根据类型
            loc_type = getattr(location, 'location_type', '普通')
            icon_map = {
                '区域': '🌍',
                '城镇': '🏘️',
                '门派': '⛩️',
                '野外': '🌲',
                '秘境': '💎',
                '洞府': '🏔️',
            }
            icon = icon_map.get(loc_type, '📍')

            # 检查是否可进入
            player_realm = self._get_player_realm()
            is_accessible = location.is_accessible(player_realm) if hasattr(location, 'is_accessible') else True

            # 不可进入的显示为灰色
            tags = ()
            if not is_accessible:
                tags = ('inaccessible',)

            item = self.location_tree.insert(
                parent_item,
                'end',
                text=f"{icon}",
                values=(location_id, realm_name, danger),
                tags=tags
            )

            # 如果是当前位置，高亮显示
            if location_id == self._get_current_location():
                self.location_tree.item(item, text=f"{icon} ★")

            # 递归添加子节点
            for sub_loc_id in getattr(location, 'sub_locations', []):
                if sub_loc_id in locations:
                    add_node(item, sub_loc_id, locations[sub_loc_id])

        # 添加根节点
        for loc_id, loc in root_locations:
            add_node('', loc_id, loc)

        # 配置标签样式
        self.location_tree.tag_configure('inaccessible', foreground='#666666')

    def on_show(self):
        """当面板显示时"""
        super().on_show()
        self.refresh()
