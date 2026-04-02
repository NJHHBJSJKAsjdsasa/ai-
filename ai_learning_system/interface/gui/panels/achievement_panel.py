"""
成就面板模块
显示成就列表、进度、奖励等信息
"""

from typing import Dict, List, Any, Optional, Callable
import tkinter as tk
from tkinter import ttk, messagebox

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from interface.gui.panels.base_panel import BasePanel
from interface.gui.theme import Theme
from interface.gui.widgets.scrollable_frame import ScrollableFrame
from interface.gui.widgets.tooltip import ToolTip
from game.achievement_system import AchievementManager
from config.achievement_config import get_category_name, get_tier_name, get_tier_color


class AchievementPanel(BasePanel):
    """成就面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.achievement_manager: Optional[AchievementManager] = None
        self.current_category: str = "all"
        self.current_status: str = "all"
        self.achievement_cards: List[Dict[str, Any]] = []
        self.on_claim_callback: Optional[Callable] = None

        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面 - 重写基类方法"""
        # 获取成就管理器
        if self.game and hasattr(self.game, 'achievement_manager'):
            self.achievement_manager = self.game.achievement_manager

        self.create_ui()

    def create_ui(self):
        """创建UI界面"""
        self.config(padx=10, pady=10)

        # 标题区域
        self._create_header()

        # 统计区域
        self._create_stats_section()

        # 筛选区域
        self._create_filter_section()

        # 成就列表区域
        self._create_achievement_list()

        # 加载成就数据
        self.refresh_achievements()

    def _create_header(self):
        """创建标题区域"""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # 标题
        title_label = ttk.Label(
            header_frame,
            text="🏆 成就系统",
            font=Theme.FONTS['title']
        )
        title_label.pack(side=tk.LEFT)

        # 一键领取按钮
        self.claim_all_btn = ttk.Button(
            header_frame,
            text="🎁 一键领取",
            command=self._claim_all_rewards
        )
        self.claim_all_btn.pack(side=tk.RIGHT)

    def _create_stats_section(self):
        """创建统计区域"""
        self.stats_frame = ttk.LabelFrame(self, text="成就统计", padding=10)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))

        # 统计信息
        self.stats_labels = {}

        stats_items = [
            ('total_points', '总积分', '#ffffff'),
            ('completion_rate', '完成度', '#4CAF50'),
            ('bronze_count', '铜', '#cd7f32'),
            ('silver_count', '银', '#c0c0c0'),
            ('gold_count', '金', '#ffd700'),
            ('diamond_count', '钻石', '#b9f2ff')
        ]

        for i, (key, label, color) in enumerate(stats_items):
            frame = ttk.Frame(self.stats_frame)
            frame.grid(row=0, column=i, padx=10, pady=5)

            value_label = tk.Label(
                frame,
                text="0",
                font=Theme.FONTS['heading'],
                fg=color,
                bg=Theme.COLORS['bg_secondary']
            )
            value_label.pack()

            name_label = ttk.Label(frame, text=label, font=Theme.FONTS['small'])
            name_label.pack()

            self.stats_labels[key] = value_label

    def _create_filter_section(self):
        """创建筛选区域"""
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # 分类筛选
        ttk.Label(filter_frame, text="分类:").pack(side=tk.LEFT, padx=(0, 5))

        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["all", "cultivation", "combat", "exploration", "social", "collection", "special"],
            state="readonly",
            width=12
        )
        self.category_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.category_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 状态筛选
        ttk.Label(filter_frame, text="状态:").pack(side=tk.LEFT, padx=(0, 5))

        self.status_var = tk.StringVar(value="all")
        self.status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["all", "locked", "unlocked", "claimed"],
            state="readonly",
            width=12
        )
        self.status_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.status_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 刷新按钮
        refresh_btn = ttk.Button(
            filter_frame,
            text="🔄 刷新",
            command=self.refresh_achievements
        )
        refresh_btn.pack(side=tk.RIGHT)

    def _create_achievement_list(self):
        """创建成就列表"""
        # 创建滚动区域
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.achievements_container = self.scroll_frame.scrollable_frame

    def _create_achievement_card(self, achievement: Dict[str, Any]) -> ttk.Frame:
        """
        创建成就卡片

        Args:
            achievement: 成就数据

        Returns:
            成就卡片框架
        """
        # 根据状态确定边框颜色
        status_colors = {
            'locked': '#666666',
            'unlocked': '#4CAF50',
            'claimed': '#FFD700'
        }
        border_color = status_colors.get(achievement['status'], '#666666')

        # 创建卡片框架
        card = tk.Frame(
            self.achievements_container,
            bg=Theme.COLORS['bg_secondary'],
            highlightbackground=border_color,
            highlightthickness=2,
            padx=10,
            pady=10
        )
        card.pack(fill=tk.X, pady=5, padx=5)

        # 左侧：图标和等级
        left_frame = tk.Frame(card, bg=Theme.COLORS['bg_secondary'])
        left_frame.pack(side=tk.LEFT, padx=(0, 10))

        # 成就图标
        icon_label = tk.Label(
            left_frame,
            text=achievement.get('icon', '🏆'),
            font=('Arial', 32),
            bg=Theme.COLORS['bg_secondary']
        )
        icon_label.pack()

        # 等级标签
        tier = achievement.get('tier', 'bronze')
        tier_color = get_tier_color(tier)
        tier_name = get_tier_name(tier)

        tier_label = tk.Label(
            left_frame,
            text=tier_name,
            font=Theme.FONTS['small'],
            fg=tier_color,
            bg=Theme.COLORS['bg_secondary']
        )
        tier_label.pack()

        # 中间：成就信息
        center_frame = tk.Frame(card, bg=Theme.COLORS['bg_secondary'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 成就名称
        name_label = tk.Label(
            center_frame,
            text=achievement.get('name', '未知成就'),
            font=Theme.FONTS['heading'],
            fg=Theme.COLORS['text_primary'],
            bg=Theme.COLORS['bg_secondary']
        )
        name_label.pack(anchor=tk.W)

        # 成就描述
        desc_label = tk.Label(
            center_frame,
            text=achievement.get('description', ''),
            font=Theme.FONTS['normal'],
            fg=Theme.COLORS['text_secondary'],
            bg=Theme.COLORS['bg_secondary'],
            wraplength=400,
            justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(5, 0))

        # 进度条
        progress = achievement.get('progress', 0)
        target = achievement.get('target_value', 1)
        progress_pct = min(100, (progress / target * 100)) if target > 0 else 0

        progress_frame = tk.Frame(center_frame, bg=Theme.COLORS['bg_secondary'])
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        progress_bar = ttk.Progressbar(
            progress_frame,
            value=progress_pct,
            maximum=100,
            length=200,
            mode='determinate'
        )
        progress_bar.pack(side=tk.LEFT)

        progress_label = tk.Label(
            progress_frame,
            text=f"{progress}/{target}",
            font=Theme.FONTS['small'],
            fg=Theme.COLORS['text_secondary'],
            bg=Theme.COLORS['bg_secondary']
        )
        progress_label.pack(side=tk.LEFT, padx=(10, 0))

        # 分类标签
        category = achievement.get('category', 'special')
        category_name = get_category_name(category)

        cat_label = tk.Label(
            center_frame,
            text=f"分类: {category_name}",
            font=Theme.FONTS['small'],
            fg=Theme.COLORS['text_secondary'],
            bg=Theme.COLORS['bg_secondary']
        )
        cat_label.pack(anchor=tk.W, pady=(5, 0))

        # 右侧：奖励和操作
        right_frame = tk.Frame(card, bg=Theme.COLORS['bg_secondary'])
        right_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # 奖励信息
        rewards = achievement.get('rewards', {})
        reward_texts = []

        if rewards.get('exp', 0) > 0:
            reward_texts.append(f"经验: {rewards['exp']}")
        if rewards.get('spirit_stones', 0) > 0:
            reward_texts.append(f"灵石: {rewards['spirit_stones']}")
        if rewards.get('title'):
            reward_texts.append(f"称号: {rewards['title']}")

        if reward_texts:
            rewards_label = tk.Label(
                right_frame,
                text="奖励:\n" + "\n".join(reward_texts),
                font=Theme.FONTS['small'],
                fg='#FFD700',
                bg=Theme.COLORS['bg_secondary'],
                justify=tk.LEFT
            )
            rewards_label.pack(pady=(0, 10))

        # 状态标签和操作按钮
        status = achievement.get('status', 'locked')

        if status == 'locked':
            status_label = tk.Label(
                right_frame,
                text="🔒 未解锁",
                font=Theme.FONTS['normal'],
                fg='#666666',
                bg=Theme.COLORS['bg_secondary']
            )
            status_label.pack()
        elif status == 'unlocked':
            status_label = tk.Label(
                right_frame,
                text="✨ 可领取",
                font=Theme.FONTS['normal'],
                fg='#4CAF50',
                bg=Theme.COLORS['bg_secondary']
            )
            status_label.pack()

            # 领取按钮
            claim_btn = ttk.Button(
                right_frame,
                text="领取奖励",
                command=lambda aid=achievement['id']: self._claim_reward(aid)
            )
            claim_btn.pack(pady=(5, 0))
        else:  # claimed
            status_label = tk.Label(
                right_frame,
                text="✅ 已领取",
                font=Theme.FONTS['normal'],
                fg='#FFD700',
                bg=Theme.COLORS['bg_secondary']
            )
            status_label.pack()

        # 添加提示
        tooltip_text = f"{achievement.get('name', '')}\n{achievement.get('description', '')}"
        ToolTip(card, tooltip_text)

        return card

    def _on_filter_changed(self, event=None):
        """筛选条件改变时刷新列表"""
        self.current_category = self.category_var.get()
        self.current_status = self.status_var.get()
        self.refresh_achievements()

    def refresh_achievements(self):
        """刷新成就列表"""
        if not self.achievement_manager:
            return

        # 清除现有卡片
        for widget in self.achievements_container.winfo_children():
            widget.destroy()

        # 获取成就数据
        player_id = self._get_player_id()
        if not player_id:
            return

        # 应用筛选
        status_filter = None if self.current_status == "all" else self.current_status
        category_filter = None if self.current_category == "all" else self.current_category

        achievements = self.achievement_manager.get_player_achievements(
            player_id,
            status=status_filter,
            category=category_filter
        )

        # 创建成就卡片
        self.achievement_cards = []
        for achievement in achievements:
            card = self._create_achievement_card(achievement)
            self.achievement_cards.append({
                'card': card,
                'achievement': achievement
            })

        # 更新统计
        self._update_stats()

    def _update_stats(self):
        """更新统计信息"""
        if not self.achievement_manager:
            return

        player_id = self._get_player_id()
        if not player_id:
            return

        stats = self.achievement_manager.get_player_achievement_stats(player_id)

        # 更新统计标签
        self.stats_labels['total_points'].config(text=str(stats.get('total_points', 0)))
        self.stats_labels['completion_rate'].config(text=f"{stats.get('completion_rate', 0):.1f}%")
        self.stats_labels['bronze_count'].config(text=str(stats.get('bronze_count', 0)))
        self.stats_labels['silver_count'].config(text=str(stats.get('silver_count', 0)))
        self.stats_labels['gold_count'].config(text=str(stats.get('gold_count', 0)))
        self.stats_labels['diamond_count'].config(text=str(stats.get('diamond_count', 0)))

    def _claim_reward(self, achievement_id: str):
        """
        领取单个成就奖励

        Args:
            achievement_id: 成就ID
        """
        if not self.achievement_manager:
            return

        player_id = self._get_player_id()
        if not player_id:
            return

        result = self.achievement_manager.claim_reward(player_id, achievement_id)

        if result.get('success'):
            rewards = result.get('rewards', {})
            reward_msgs = []

            if rewards.get('exp', 0) > 0:
                reward_msgs.append(f"经验: {rewards['exp']}")
            if rewards.get('spirit_stones', 0) > 0:
                reward_msgs.append(f"灵石: {rewards['spirit_stones']}")
            if rewards.get('title'):
                reward_msgs.append(f"称号: {rewards['title']}")

            messagebox.showinfo(
                "领取成功",
                f"成功领取奖励！\n\n" + "\n".join(reward_msgs)
            )

            # 刷新显示
            self.refresh_achievements()

            # 调用回调
            if self.on_claim_callback:
                self.on_claim_callback(rewards)
        else:
            messagebox.showerror(
                "领取失败",
                result.get('message', '未知错误')
            )

    def _claim_all_rewards(self):
        """一键领取所有奖励"""
        if not self.achievement_manager:
            return

        player_id = self._get_player_id()
        if not player_id:
            return

        # 检查是否有可领取的奖励
        if not self.achievement_manager.has_unclaimed_achievements(player_id):
            messagebox.showinfo("提示", "没有可领取的奖励")
            return

        result = self.achievement_manager.claim_all_rewards(player_id)

        if result['success_count'] > 0:
            reward_msgs = []
            total_rewards = result['total_rewards']

            if total_rewards['exp'] > 0:
                reward_msgs.append(f"经验: {total_rewards['exp']}")
            if total_rewards['spirit_stones'] > 0:
                reward_msgs.append(f"灵石: {total_rewards['spirit_stones']}")
            if total_rewards['karma'] != 0:
                reward_msgs.append(f"业力: {total_rewards['karma']}")
            if total_rewards['reputation'] > 0:
                reward_msgs.append(f"声望: {total_rewards['reputation']}")
            if total_rewards['titles']:
                reward_msgs.append(f"称号: {', '.join(total_rewards['titles'])}")

            messagebox.showinfo(
                "领取成功",
                f"成功领取 {result['success_count']} 个成就奖励！\n\n" + "\n".join(reward_msgs)
            )

            # 刷新显示
            self.refresh_achievements()

            # 调用回调
            if self.on_claim_callback:
                self.on_claim_callback(total_rewards)
        else:
            messagebox.showinfo("提示", "没有可领取的奖励")

    def _get_player_id(self) -> Optional[str]:
        """获取当前玩家ID"""
        if self.game and hasattr(self.game, 'player') and self.game.player:
            return self.game.player.id
        return None

    def set_claim_callback(self, callback: Callable):
        """
        设置领取奖励回调

        Args:
            callback: 回调函数，接收奖励数据作为参数
        """
        self.on_claim_callback = callback

    def show_achievement_unlocked(self, achievement: Dict[str, Any]):
        """
        显示成就解锁提示

        Args:
            achievement: 成就数据
        """
        # 创建弹出窗口
        popup = tk.Toplevel(self)
        popup.title("成就解锁！")
        popup.geometry("300x200")
        popup.transient(self)
        popup.grab_set()

        # 设置窗口居中
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (300 // 2)
        y = (popup.winfo_screenheight() // 2) - (200 // 2)
        popup.geometry(f"+{x}+{y}")

        # 成就图标
        icon_label = tk.Label(
            popup,
            text=achievement.get('icon', '🏆'),
            font=('Arial', 48)
        )
        icon_label.pack(pady=10)

        # 成就名称
        name_label = tk.Label(
            popup,
            text=f"解锁成就: {achievement.get('name', '')}",
            font=Theme.FONTS['heading']
        )
        name_label.pack()

        # 成就描述
        desc_label = tk.Label(
            popup,
            text=achievement.get('description', ''),
            font=Theme.FONTS['normal'],
            wraplength=250
        )
        desc_label.pack(pady=5)

        # 确定按钮
        ttk.Button(
            popup,
            text="确定",
            command=popup.destroy
        ).pack(pady=10)

        # 自动关闭
        popup.after(5000, popup.destroy)

    def update(self):
        """更新面板"""
        super().update()
        self.refresh_achievements()

    def on_show(self):
        """面板显示时调用"""
        super().on_show()
        self.refresh_achievements()
