"""
GUI 主窗口 - 重构版
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from .theme import Theme
from .log_panel import LogPanel
from .animation_manager import animation_manager, EasingType

# 面板导入
from .panels.status_panel import StatusPanel
from .panels.map_panel import MapPanel
from .panels.npc_panel import NPCPanel
from .panels.inventory_panel import InventoryPanel
from .panels.technique_panel import TechniquePanel
from .panels.combat_panel import CombatPanel
from .panels.exploration_panel import ExplorationPanel
from .panels.alchemy_panel import AlchemyPanel
from .panels.quest_panel import QuestPanel
from .panels.sect_panel import SectPanel
from .panels.social_panel import SocialPanel
from .panels.tribulation_panel import TribulationPanel
from .panels.cave_panel import CavePanel
from .panels.pet_panel import PetPanel
from .panels.achievement_panel import AchievementPanel
from .panels.world_panel import WorldPanel
from .panels.story_panel import StoryPanel
from .panels.shop_panel import ShopPanel


class MainWindow:
    """修仙系统 GUI 主窗口 - 重构版"""

    def __init__(self, game_instance=None):
        self.root = tk.Tk()
        self.game = game_instance
        self.current_panel = None
        self.panels = {}
        self.nav_collapsed = False

        self._setup_window()
        self._setup_menu()
        self._setup_layout()
        self._setup_status_bar()

        # 启动状态栏更新
        self._update_status_bar()

    def _setup_window(self):
        """设置窗口属性"""
        self.root.title("☯ 修仙系统")
        self.root.geometry("1280x850")
        self.root.minsize(1000, 700)
        self.root.config(bg=Theme.BG_PRIMARY)

        # 设置窗口关闭协议
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                         activebackground=Theme.BG_ELEVATED, activeforeground=Theme.ACCENT_GOLD)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(
            menubar, tearoff=0,
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_ELEVATED, activeforeground=Theme.ACCENT_GOLD
        )
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="💾 保存游戏", command=self._save_game)
        file_menu.add_command(label="📂 加载游戏", command=self._load_game)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 退出", command=self._on_close)

        # 视图菜单
        view_menu = tk.Menu(
            menubar, tearoff=0,
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_ELEVATED, activeforeground=Theme.ACCENT_GOLD
        )
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="🗑️ 清空日志", command=self._clear_logs)
        view_menu.add_separator()
        view_menu.add_command(label="📐 折叠/展开导航", command=self._toggle_nav)

        # 帮助菜单
        help_menu = tk.Menu(
            menubar, tearoff=0,
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_ELEVATED, activeforeground=Theme.ACCENT_GOLD
        )
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="❓ 关于", command=self._show_about)

    def _setup_layout(self):
        """设置主布局"""
        # 主框架
        main_frame = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Theme.SPACING_MD, pady=Theme.SPACING_MD)

        # 左侧导航面板
        self.nav_container = tk.Frame(main_frame, bg=Theme.BG_SECONDARY, width=Theme.NAV_WIDTH)
        self.nav_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, Theme.SPACING_MD))
        self.nav_container.pack_propagate(False)

        # 创建Canvas用于滚动
        self.nav_canvas = tk.Canvas(
            self.nav_container, bg=Theme.BG_SECONDARY,
            highlightthickness=0, width=Theme.NAV_WIDTH - 12
        )
        self.nav_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.nav_scrollbar = tk.Scrollbar(
            self.nav_container, orient=tk.VERTICAL,
            command=self.nav_canvas.yview,
            bg=Theme.BG_TERTIARY, troughcolor=Theme.BG_SECONDARY,
            activebackground=Theme.BG_ELEVATED
        )
        self.nav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.nav_canvas.configure(yscrollcommand=self.nav_scrollbar.set)

        # 创建导航框架（放在Canvas中）
        self.nav_frame = tk.Frame(self.nav_canvas, bg=Theme.BG_SECONDARY, width=Theme.NAV_WIDTH - 20)
        self.nav_canvas_window = self.nav_canvas.create_window(
            (0, 0), window=self.nav_frame, anchor=tk.NW,
            width=Theme.NAV_WIDTH - 20
        )

        self._setup_navigation()

        # 绑定事件以更新滚动区域
        self.nav_frame.bind("<Configure>", self._on_nav_frame_configure)
        self.nav_canvas.bind("<Configure>", self._on_nav_canvas_configure)

        # 绑定鼠标滚轮事件
        self.nav_canvas.bind("<MouseWheel>", self._on_nav_mousewheel)
        self.nav_frame.bind("<MouseWheel>", self._on_nav_mousewheel)

        # 右侧内容区域
        right_frame = tk.Frame(main_frame, bg=Theme.BG_PRIMARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 中央内容面板
        self.content_frame = tk.Frame(
            right_frame, bg=Theme.BG_SECONDARY,
            highlightbackground=Theme.BORDER_DEFAULT,
            highlightthickness=1
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Theme.SPACING_MD))

        # 初始化各个面板
        self._init_panels()

        # 底部日志面板
        self.log_panel = LogPanel(right_frame, bg=Theme.BG_SECONDARY)
        self.log_panel.pack(fill=tk.X, side=tk.BOTTOM)

        # 默认显示状态面板
        self.show_panel("status")

    def _setup_navigation(self):
        """设置导航按钮"""
        # 标题区域 - 增强视觉效果
        title_frame = tk.Frame(self.nav_frame, bg=Theme.BG_SECONDARY)
        title_frame.pack(fill=tk.X, pady=Theme.SPACING_LG, padx=Theme.SPACING_MD)

        # 标题背景装饰
        title_decor = tk.Frame(title_frame, bg=Theme.ACCENT_GOLD, height=2)
        title_decor.pack(fill=tk.X, pady=(0, Theme.SPACING_SM))

        title_label = tk.Label(
            title_frame,
            text="☯ 修仙系统",
            font=Theme.get_font(Theme.FONT_SIZE_LG, bold=True),
            bg=Theme.BG_SECONDARY,
            fg=Theme.ACCENT_GOLD
        )
        title_label.pack()

        # 分隔线
        separator = tk.Frame(self.nav_frame, bg=Theme.BORDER_DEFAULT, height=1)
        separator.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_SM)

        # 导航按钮分组配置 - 增强视觉层次
        nav_groups = [
            ("基础", [
                ("status", "📊", "状态", self._on_status_click),
                ("map", "🗺️", "地图", self._on_map_click),
                ("story", "📖", "剧情", self._on_story_click),
            ]),
            ("交互", [
                ("npc", "👥", "NPC", self._on_npc_click),
                ("social", "💕", "社交", self._on_social_click),
                ("inventory", "🎒", "背包", self._on_inventory_click),
                ("shop", "🏪", "商店", self._on_shop_click),
            ]),
            ("修炼", [
                ("technique", "📜", "功法", self._on_technique_click),
                ("sect", "🏛️", "门派", self._on_sect_click),
                ("combat", "⚔️", "战斗", self._on_combat_click),
                ("tribulation", "⚡", "天劫", self._on_tribulation_click),
            ]),
            ("探索", [
                ("exploration", "🔍", "探索", self._on_exploration_click),
                ("alchemy", "⚗️", "炼丹", self._on_alchemy_click),
                ("pet", "🐾", "灵兽", self._on_pet_click),
                ("cave", "🏔️", "洞府", self._on_cave_click),
                ("quest", "📜", "任务", self._on_quest_click),
            ]),
            ("系统", [
                ("achievement", "🏆", "成就", self._on_achievement_click),
                ("world", "🌍", "世界", self._on_world_click),
            ])
        ]

        self.nav_buttons = {}
        for group_name, items in nav_groups:
            # 分组标签
            group_frame = tk.Frame(self.nav_frame, bg=Theme.BG_SECONDARY)
            group_frame.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=(Theme.SPACING_MD, Theme.SPACING_XS))
            
            group_label = tk.Label(
                group_frame,
                text=f"— {group_name} —",
                **Theme.get_button_style("nav_group")
            )
            group_label.pack(fill=tk.X, anchor="w")
            
            # 分组内按钮
            for nav_id, icon, text, command in items:
                btn = self._create_nav_button(self.nav_frame, icon, text, command, nav_id)
                btn.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_XS)
                self.nav_buttons[nav_id] = btn

        # 底部区域
        bottom_frame = tk.Frame(self.nav_frame, bg=Theme.BG_SECONDARY)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=Theme.SPACING_MD)

        # 分隔线
        separator2 = tk.Frame(bottom_frame, bg=Theme.BORDER_DEFAULT, height=1)
        separator2.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_SM)

        # 折叠按钮
        collapse_btn = self._create_nav_button(
            bottom_frame, "◀", "收起", self._toggle_nav, "collapse",
            bg=Theme.BG_TERTIARY
        )
        collapse_btn.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_XS)

        # 退出按钮
        quit_btn = self._create_nav_button(
            bottom_frame, "🚪", "退出", self._on_close, "quit",
            bg=Theme.ACCENT_RED
        )
        quit_btn.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_XS)

    def _init_panels(self):
        """初始化各个功能面板"""
        self.panels = {
            "status": StatusPanel(self.content_frame, self),
            "map": MapPanel(self.content_frame, self),
            "story": StoryPanel(self.content_frame, self),
            "npc": NPCPanel(self.content_frame, self),
            "social": SocialPanel(self.content_frame, self),
            "inventory": InventoryPanel(self.content_frame, self),
            "shop": ShopPanel(self.content_frame, self),
            "technique": TechniquePanel(self.content_frame, self),
            "sect": SectPanel(self.content_frame, self),
            "combat": CombatPanel(self.content_frame, self),
            "exploration": ExplorationPanel(self.content_frame, self),
            "alchemy": AlchemyPanel(self.content_frame, self),
            "pet": PetPanel(self.content_frame, self),
            "cave": CavePanel(self.content_frame, self),
            "quest": QuestPanel(self.content_frame, self),
            "tribulation": TribulationPanel(self.content_frame, self),
            "achievement": AchievementPanel(self.content_frame, self),
            "world": WorldPanel(self.content_frame, self),
        }

    def show_panel(self, panel_name):
        """显示指定面板"""
        if self.current_panel == panel_name:
            return

        # 更新按钮样式
        for nav_id, btn in self.nav_buttons.items():
            if nav_id == panel_name:
                btn.config(**Theme.get_button_style("nav_active"))
            else:
                btn.config(**Theme.get_button_style("nav"))

        # 切换面板
        if self.current_panel:
            self.panels[self.current_panel].on_hide()
            self.panels[self.current_panel].pack_forget()

        if panel_name in self.panels:
            self.panels[panel_name].pack(
                fill=tk.BOTH, expand=True,
                padx=Theme.SPACING_MD, pady=Theme.SPACING_MD
            )
            self.current_panel = panel_name
            self.panels[panel_name].on_show()

    def _toggle_nav(self):
        """切换导航栏折叠状态"""
        self.nav_collapsed = not self.nav_collapsed

        if self.nav_collapsed:
            # 折叠
            self.nav_container.config(width=Theme.NAV_COLLAPSED_WIDTH)
            self.nav_canvas.config(width=Theme.NAV_COLLAPSED_WIDTH - 12)
            self.nav_canvas.itemconfig(self.nav_canvas_window, width=Theme.NAV_COLLAPSED_WIDTH - 20)

            # 更新按钮只显示图标
            for btn in self.nav_buttons.values():
                original_text = btn.cget("text")
                if len(original_text) > 2:
                    btn.config(text=original_text[:2])
        else:
            # 展开
            self.nav_container.config(width=Theme.NAV_WIDTH)
            self.nav_canvas.config(width=Theme.NAV_WIDTH - 12)
            self.nav_canvas.itemconfig(self.nav_canvas_window, width=Theme.NAV_WIDTH - 20)

            # 恢复按钮文本
            nav_items = {
                "status": "📊 状态",
                "map": "🗺️ 地图",
                "story": "📖 剧情",
                "npc": "👥 NPC",
                "social": "💕 社交",
                "inventory": "🎒 背包",
                "shop": "🏪 商店",
                "technique": "📜 功法",
                "sect": "🏛️ 门派",
                "combat": "⚔️ 战斗",
                "exploration": "🔍 探索",
                "alchemy": "⚗️ 炼丹",
                "pet": "🐾 灵兽",
                "cave": "🏔️ 洞府",
                "quest": "📜 任务",
                "tribulation": "⚡ 天劫",
                "achievement": "🏆 成就",
                "world": "🌍 世界",
                "collapse": "◀ 收起" if not self.nav_collapsed else "▶ 展开",
                "quit": "🚪 退出",
            }
            for nav_id, btn in self.nav_buttons.items():
                if nav_id in nav_items:
                    btn.config(text=nav_items[nav_id])

    def _setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = tk.Frame(
            self.root, bg=Theme.BG_SECONDARY,
            height=Theme.STATUS_BAR_HEIGHT
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 游戏状态
        self.game_status_label = tk.Label(
            self.status_bar, text="就绪",
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY
        )
        self.game_status_label.pack(side=tk.LEFT, padx=Theme.SPACING_MD)

        # 分隔符
        separator = tk.Label(
            self.status_bar, text="|",
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_DIM
        )
        separator.pack(side=tk.LEFT)

        # 当前时间
        self.time_label = tk.Label(
            self.status_bar, text="",
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY
        )
        self.time_label.pack(side=tk.LEFT, padx=Theme.SPACING_MD)

        # 游戏时间（如果有）
        if self.game and hasattr(self.game, 'world'):
            separator2 = tk.Label(
                self.status_bar, text="|",
                font=Theme.get_font(Theme.FONT_SIZE_SM),
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_DIM
            )
            separator2.pack(side=tk.LEFT)

            self.world_time_label = tk.Label(
                self.status_bar, text="",
                font=Theme.get_font(Theme.FONT_SIZE_SM),
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_GOLD
            )
            self.world_time_label.pack(side=tk.LEFT, padx=Theme.SPACING_MD)

    def _update_status_bar(self):
        """更新状态栏"""
        # 更新时间
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"系统时间: {current_time}")

        # 更新游戏时间
        if hasattr(self, 'world_time_label') and self.game and hasattr(self.game, 'world'):
            world = self.game.world
            if hasattr(world, 'current_time'):
                self.world_time_label.config(text=f"游戏时间: {world.current_time}")

        # 每秒更新一次
        self.root.after(1000, self._update_status_bar)

    def _create_nav_button(self, parent, icon, text, command, nav_id, bg=None):
        """创建导航按钮"""
        is_active = nav_id == self.current_panel
        style = Theme.get_button_style("nav_active" if is_active else "nav")

        if bg:
            style = {**style, "bg": bg}

        btn = tk.Button(
            parent,
            text=f"{icon} {text}",
            command=command,
            **style
        )

        # 添加悬停效果
        original_bg = btn.cget("bg")
        hover_bg = Theme._lighten_color(original_bg, 1.1)

        btn.bind("<Enter>", lambda e, b=btn, hbg=hover_bg: b.config(bg=hbg))
        btn.bind("<Leave>", lambda e, b=btn, obg=original_bg: b.config(bg=obg))

        return btn

    # 导航按钮回调
    def _on_status_click(self):
        self.show_panel("status")

    def _on_map_click(self):
        self.show_panel("map")

    def _on_story_click(self):
        self.show_panel("story")

    def _on_npc_click(self):
        self.show_panel("npc")

    def _on_social_click(self):
        self.show_panel("social")

    def _on_inventory_click(self):
        self.show_panel("inventory")

    def _on_shop_click(self):
        self.show_panel("shop")

    def _on_technique_click(self):
        self.show_panel("technique")

    def _on_sect_click(self):
        self.show_panel("sect")

    def _on_combat_click(self):
        self.show_panel("combat")

    def _on_exploration_click(self):
        self.show_panel("exploration")

    def _on_alchemy_click(self):
        self.show_panel("alchemy")

    def _on_cave_click(self):
        self.show_panel("cave")

    def _on_quest_click(self):
        self.show_panel("quest")

    def _on_tribulation_click(self):
        self.show_panel("tribulation")

    def _on_pet_click(self):
        self.show_panel("pet")

    def _on_achievement_click(self):
        self.show_panel("achievement")

    def _on_world_click(self):
        self.show_panel("world")

    def _on_nav_frame_configure(self, event=None):
        """导航框架大小变化时更新滚动区域"""
        self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))

    def _on_nav_canvas_configure(self, event=None):
        """Canvas大小变化时调整内部框架宽度"""
        self.nav_canvas.itemconfig(self.nav_canvas_window, width=event.width)

    def _on_nav_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.nav_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # 菜单回调
    def _save_game(self):
        """保存游戏"""
        if self.game and hasattr(self.game, 'save'):
            try:
                self.game.save()
                self.log("游戏已保存", "system")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
        else:
            messagebox.showinfo("提示", "保存功能暂不可用")

    def _load_game(self):
        """加载游戏"""
        if self.game and hasattr(self.game, 'load'):
            try:
                self.game.load()
                self.log("游戏已加载", "system")
                self.refresh_all_panels()
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
        else:
            messagebox.showinfo("提示", "加载功能暂不可用")

    def _clear_logs(self):
        """清空日志"""
        self.log_panel.clear()

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "☯ 修仙系统 GUI v2.0\n\n"
            "基于 tkinter 开发的图形界面\n"
            "为修仙 AI 学习系统提供可视化操作\n\n"
            "重构版 - 全新视觉体验"
        )

    def _on_close(self):
        """关闭窗口"""
        if messagebox.askyesno("确认", "确定要退出游戏吗？"):
            self.root.destroy()

    # 公共方法
    def log(self, message, log_type="system"):
        """添加日志"""
        if hasattr(self, 'log_panel'):
            self.log_panel.log(message, log_type)

    def refresh_all_panels(self):
        """刷新所有面板"""
        for panel in self.panels.values():
            if hasattr(panel, 'refresh'):
                panel.refresh()

    def refresh_current_panel(self):
        """刷新当前面板"""
        if self.current_panel and hasattr(self.panels[self.current_panel], 'refresh'):
            self.panels[self.current_panel].refresh()

    def run(self):
        """运行主循环"""
        self.root.mainloop()
