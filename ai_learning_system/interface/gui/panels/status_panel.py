"""
角色状态面板 - 重构版
使用真实游戏数据
"""
import tkinter as tk
from tkinter import messagebox
from .base_panel import BasePanel
from ..theme import Theme


class StatusPanel(BasePanel):
    """角色状态面板 - 重构版"""

    def __init__(self, parent, main_window, **kwargs):
        self.cultivation_var = None
        self.realm_var = None
        self.name_var = None
        self.age_var = None
        self.location_var = None
        self.exp_var = None
        self.exp_max_var = None
        self.hp_var = None
        self.hp_max_var = None
        self.attack_var = None
        self.defense_var = None
        self.speed_var = None
        self.spirit_root_var = None
        self.lifespan_var = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面 - 重构版"""
        # 标题
        title_frame = self.create_section_title(self, "☯ 角色状态")
        title_frame.pack(fill=tk.X, pady=(0, Theme.SPACING_LG))

        # 创建左右分栏
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左栏 - 基本信息
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, Theme.SPACING_LG))

        self._setup_basic_info(left_frame)
        self._setup_cultivation_info(left_frame)
        self._setup_attributes(left_frame)

        # 右栏 - 操作按钮
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(Theme.SPACING_LG, 0))
        right_frame.pack_propagate(False)

        self._setup_action_buttons(right_frame)

    def _setup_basic_info(self, parent):
        """设置基本信息区域"""
        # 信息卡片
        card = self.create_card(parent, "👤 基本信息")
        card.pack(fill=tk.X, pady=(0, Theme.SPACING_MD))

        # 名字
        self.name_var = tk.StringVar(value="未知道友")
        name_frame, _ = self.create_info_row(
            card, "道号", "未知道友", Theme.ACCENT_GOLD
        )
        name_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 绑定变量更新
        name_label = name_frame.winfo_children()[1]
        name_label.config(textvariable=self.name_var)

        # 境界
        self.realm_var = tk.StringVar(value="凡人")
        realm_frame, _ = self.create_info_row(
            card, "境界", "凡人", Theme.ACCENT_CYAN
        )
        realm_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)
        realm_label = realm_frame.winfo_children()[1]
        realm_label.config(textvariable=self.realm_var)

        # 灵根
        self.spirit_root_var = tk.StringVar(value="未知")
        spirit_frame, _ = self.create_info_row(
            card, "灵根", "未知", Theme.ACCENT_PURPLE
        )
        spirit_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)
        spirit_label = spirit_frame.winfo_children()[1]
        spirit_label.config(textvariable=self.spirit_root_var)

        # 年龄和寿元
        age_lifespan_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        age_lifespan_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 年龄
        self.age_var = tk.StringVar(value="16岁")
        age_frame = tk.Frame(age_lifespan_frame, bg=Theme.BG_TERTIARY)
        age_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(age_frame, text="年龄: ", **Theme.get_label_style("normal")).pack(side=tk.LEFT)
        tk.Label(
            age_frame, textvariable=self.age_var,
            font=Theme.get_font(Theme.FONT_SIZE_MD, bold=True),
            bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        # 寿元
        self.lifespan_var = tk.StringVar(value="80年")
        lifespan_frame = tk.Frame(age_lifespan_frame, bg=Theme.BG_TERTIARY)
        lifespan_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(lifespan_frame, text="寿元: ", **Theme.get_label_style("normal")).pack(side=tk.LEFT)
        tk.Label(
            lifespan_frame, textvariable=self.lifespan_var,
            font=Theme.get_font(Theme.FONT_SIZE_MD, bold=True),
            bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_GREEN
        ).pack(side=tk.LEFT)

        # 位置
        self.location_var = tk.StringVar(value="新手村")
        location_frame, _ = self.create_info_row(
            card, "位置", "新手村", Theme.TEXT_SECONDARY
        )
        location_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)
        location_label = location_frame.winfo_children()[1]
        location_label.config(textvariable=self.location_var)

    def _setup_cultivation_info(self, parent):
        """设置修为信息区域"""
        # 修为卡片
        card = self.create_card(parent, "🧘 修为状态")
        card.pack(fill=tk.X, pady=Theme.SPACING_MD)

        # 修为值和进度条
        self.exp_var = tk.IntVar(value=0)
        self.exp_max_var = tk.IntVar(value=100)

        exp_header_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        exp_header_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)

        tk.Label(
            exp_header_frame, text="修为",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)

        self.exp_value_label = tk.Label(
            exp_header_frame,
            text="0 / 100",
            font=Theme.get_font(Theme.FONT_SIZE_SM, bold=True),
            bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_GOLD
        )
        self.exp_value_label.pack(side=tk.RIGHT)

        # 修为进度条
        self.exp_progress = tk.Canvas(
            card, height=20, bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.exp_progress.pack(fill=tk.X, pady=Theme.SPACING_SM)

        # 生命值
        self.hp_var = tk.IntVar(value=100)
        self.hp_max_var = tk.IntVar(value=100)

        hp_header_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        hp_header_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)

        tk.Label(
            hp_header_frame, text="生命值",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)

        self.hp_value_label = tk.Label(
            hp_header_frame,
            text="100 / 100",
            font=Theme.get_font(Theme.FONT_SIZE_SM, bold=True),
            bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_RED
        )
        self.hp_value_label.pack(side=tk.RIGHT)

        # 生命进度条
        self.hp_progress = tk.Canvas(
            card, height=15, bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.hp_progress.pack(fill=tk.X, pady=Theme.SPACING_SM)

        # 灵力值
        self.sp_var = tk.IntVar(value=50)
        self.sp_max_var = tk.IntVar(value=50)

        sp_header_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        sp_header_frame.pack(fill=tk.X, pady=Theme.SPACING_XS)

        tk.Label(
            sp_header_frame, text="灵力值",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)

        self.sp_value_label = tk.Label(
            sp_header_frame,
            text="50 / 50",
            font=Theme.get_font(Theme.FONT_SIZE_SM, bold=True),
            bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_CYAN
        )
        self.sp_value_label.pack(side=tk.RIGHT)

        # 灵力进度条
        self.sp_progress = tk.Canvas(
            card, height=15, bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.sp_progress.pack(fill=tk.X, pady=Theme.SPACING_SM)

    def _setup_attributes(self, parent):
        """设置属性区域"""
        # 属性卡片
        card = self.create_card(parent, "⚔️ 战斗属性")
        card.pack(fill=tk.X, pady=Theme.SPACING_MD)

        # 属性网格
        attrs_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        attrs_frame.pack(fill=tk.X, pady=Theme.SPACING_SM)

        self.attack_var = tk.StringVar(value="0")
        self.defense_var = tk.StringVar(value="0")
        self.speed_var = tk.StringVar(value="10")
        self.crit_var = tk.StringVar(value="5%")
        self.dodge_var = tk.StringVar(value="5%")

        attributes = [
            ("⚔️", "攻击力", self.attack_var, Theme.ACCENT_RED),
            ("🛡️", "防御力", self.defense_var, Theme.ACCENT_CYAN),
            ("💨", "速度", self.speed_var, Theme.ACCENT_GREEN),
            ("💥", "暴击率", self.crit_var, Theme.ACCENT_GOLD),
            ("💫", "闪避率", self.dodge_var, Theme.ACCENT_PURPLE),
        ]

        for i, (icon, name, var, color) in enumerate(attributes):
            row = i // 2
            col = i % 2

            attr_frame = tk.Frame(attrs_frame, bg=Theme.BG_TERTIARY)
            attr_frame.grid(row=row, column=col, padx=Theme.SPACING_MD, pady=Theme.SPACING_XS, sticky="ew")

            # 图标
            tk.Label(
                attr_frame, text=icon,
                font=Theme.get_font(Theme.FONT_SIZE_MD),
                bg=Theme.BG_TERTIARY, fg=color
            ).pack(side=tk.LEFT, padx=(0, Theme.SPACING_XS))

            # 名称
            tk.Label(
                attr_frame, text=name,
                **Theme.get_label_style("normal")
            ).pack(side=tk.LEFT)

            # 值
            tk.Label(
                attr_frame, textvariable=var,
                font=Theme.get_font(Theme.FONT_SIZE_MD, bold=True),
                bg=Theme.BG_TERTIARY, fg=color
            ).pack(side=tk.RIGHT)

        # 配置网格权重
        attrs_frame.columnconfigure(0, weight=1)
        attrs_frame.columnconfigure(1, weight=1)

    def _setup_action_buttons(self, parent):
        """设置操作按钮"""
        # 操作标题
        title = tk.Label(
            parent,
            text="🎯 修炼操作",
            **Theme.get_label_style("heading")
        )
        title.pack(pady=(0, Theme.SPACING_LG))

        # 修炼按钮
        cultivate_btn = self.create_button(
            parent, "🧘 修炼", self._on_cultivate, "primary"
        )
        cultivate_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 突破按钮
        breakthrough_btn = self.create_button(
            parent, "⚡ 突破", self._on_breakthrough, "success"
        )
        breakthrough_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 休息按钮
        rest_btn = self.create_button(
            parent, "😴 休息", self._on_rest, "secondary"
        )
        rest_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 分隔线
        separator = tk.Frame(parent, bg=Theme.BORDER_DEFAULT, height=1)
        separator.pack(fill=tk.X, pady=Theme.SPACING_MD)

        # 快捷操作
        quick_title = tk.Label(
            parent,
            text="⚡ 快捷操作",
            **Theme.get_label_style("subheading")
        )
        quick_title.pack(pady=(0, Theme.SPACING_SM))

        # 查看背包按钮
        inventory_btn = self.create_button(
            parent, "🎒 查看背包",
            lambda: self.main_window.show_panel("inventory") if self.main_window else None,
            "ghost"
        )
        inventory_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

        # 查看功法按钮
        technique_btn = self.create_button(
            parent, "📜 查看功法",
            lambda: self.main_window.show_panel("technique") if self.main_window else None,
            "ghost"
        )
        technique_btn.pack(fill=tk.X, pady=Theme.SPACING_XS)

    def _draw_progress_bar(self, canvas, current, maximum, color):
        """绘制进度条"""
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1:  # 尚未渲染
            canvas.after(100, lambda: self._draw_progress_bar(canvas, current, maximum, color))
            return

        # 背景
        canvas.create_rectangle(0, 0, width, height, fill=Theme.BG_PRIMARY, outline="")

        # 进度
        if maximum > 0:
            progress = min(current / maximum, 1.0)
            fill_width = int(width * progress)
            canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def refresh(self):
        """刷新面板数据 - 使用真实游戏数据"""
        player = self.get_player()
        world = self.get_world()

        if player:
            # 获取玩家统计数据
            stats = player.stats

            # 基本信息
            self.name_var.set(stats.name)
            self.realm_var.set(player.get_realm_name())
            self.spirit_root_var.set(player.get_spirit_root_name())
            self.age_var.set(f"{stats.age}岁")
            self.lifespan_var.set(f"{stats.lifespan}年")

            # 修为 - 计算到下一级所需经验
            exp = stats.exp
            exp_required = self._get_exp_required(stats.realm_level, stats.realm_layer)
            self.exp_var.set(exp)
            self.exp_max_var.set(exp_required)

            # 更新修为显示
            self.exp_value_label.config(text=f"{exp} / {exp_required}")

            # 生命值
            hp = stats.health
            hp_max = stats.max_health
            self.hp_var.set(hp)
            self.hp_max_var.set(hp_max)
            self.hp_value_label.config(text=f"{hp} / {hp_max}")

            # 灵力值
            sp = stats.spiritual_power
            sp_max = stats.max_spiritual_power
            self.sp_var.set(sp)
            self.sp_max_var.set(sp_max)
            self.sp_value_label.config(text=f"{sp} / {sp_max}")

            # 属性
            self.attack_var.set(str(stats.attack))
            self.defense_var.set(str(stats.defense))
            self.speed_var.set(str(stats.speed))
            self.crit_var.set(f"{int(stats.crit_rate * 100)}%")
            self.dodge_var.set(f"{int(stats.dodge_rate * 100)}%")

            # 绘制进度条
            self._draw_progress_bar(self.exp_progress, exp, exp_required, Theme.ACCENT_GOLD)
            self._draw_progress_bar(self.hp_progress, hp, hp_max, Theme.ACCENT_RED)
            self._draw_progress_bar(self.sp_progress, sp, sp_max, Theme.ACCENT_CYAN)

        # 位置
        if player:
            location = stats.location if player else "未知"
            self.location_var.set(location)

    def _get_exp_required(self, realm_level, realm_layer):
        """获取突破所需经验"""
        # 基础经验需求
        base_exp = 100
        # 境界加成
        realm_multiplier = 1 + realm_level * 0.5
        # 层数加成
        layer_multiplier = 1 + (realm_layer - 1) * 0.1
        return int(base_exp * realm_multiplier * layer_multiplier)

    def _on_cultivate(self):
        """修炼按钮回调 - 使用真实修炼系统"""
        player = self.get_player()
        if player:
            try:
                # 获取修炼速度
                speed = player.get_cultivation_speed()
                import random
                gain = random.randint(5, 15) * speed
                player.stats.exp += int(gain)
                player.stats.total_practices += 1

                self.log(f"修炼成功，修为增加 {int(gain)} 点 (修炼速度: {speed:.2f}x)", "cultivation")
                self.refresh()
            except Exception as e:
                messagebox.showerror("错误", f"修炼失败: {e}")
        else:
            self.log("你打坐修炼，感觉修为有所提升...", "cultivation")
            self.refresh()

    def _on_breakthrough(self):
        """突破按钮回调 - 使用真实突破系统"""
        player = self.get_player()
        if player:
            try:
                # 检查是否可以突破
                stats = player.stats
                exp_required = self._get_exp_required(stats.realm_level, stats.realm_layer)

                if stats.exp >= exp_required:
                    # 执行突破
                    stats.exp -= exp_required
                    stats.realm_layer += 1

                    # 如果达到10层，提升境界
                    if stats.realm_layer > 9:
                        stats.realm_layer = 1
                        stats.realm_level += 1
                        player._update_max_stats()
                        player._update_lifespan()
                        self.log(f"突破成功！境界提升至 {player.get_realm_name()}！", "cultivation")
                    else:
                        self.log(f"突破成功！当前境界层数: {stats.realm_layer}", "cultivation")

                    stats.total_breakthroughs += 1
                    self.refresh()
                else:
                    self.log(f"修为不足，需要 {exp_required} 点修为才能突破", "cultivation")
            except Exception as e:
                messagebox.showerror("错误", f"突破失败: {e}")
        else:
            self.log("你尝试突破境界...", "cultivation")
            self.refresh()

    def _on_rest(self):
        """休息按钮回调 - 使用真实恢复系统"""
        player = self.get_player()
        if player:
            try:
                stats = player.stats
                # 恢复生命值和灵力
                heal_amount = 20
                sp_recover = 10

                old_hp = stats.health
                old_sp = stats.spiritual_power

                stats.health = min(stats.health + heal_amount, stats.max_health)
                stats.spiritual_power = min(stats.spiritual_power + sp_recover, stats.max_spiritual_power)

                actual_heal = stats.health - old_hp
                actual_sp = stats.spiritual_power - old_sp

                self.log(f"你休息了一会儿，生命值恢复 {actual_heal} 点，灵力恢复 {actual_sp} 点", "system")
                self.refresh()
            except Exception as e:
                messagebox.showerror("错误", f"休息失败: {e}")
        else:
            self.log("你休息了一会儿，感觉精神焕发", "system")
