"""
任务面板 - 管理任务接取、追踪和奖励领取
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .base_panel import BasePanel
from ..theme import Theme


class QuestPanel(BasePanel):
    """任务面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.quest_manager = None
        self.current_tab = "active"  # active, available, daily
        self.quest_listbox = None
        self.quest_detail_text = None
        self.selected_quest = None
        self._active_quests = []
        self._available_quests = []
        self._daily_quests = []
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="📜 任务系统",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区域
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧面板 - 任务列表
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        self._setup_quest_list(left_frame)

        # 右侧面板 - 任务详情
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._setup_quest_detail(right_frame)

    def _setup_quest_list(self, parent):
        """设置任务列表区域"""
        # 标签页按钮
        tab_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        tab_frame.pack(fill=tk.X, pady=(0, 5))

        self.tab_buttons = {}
        tabs = [
            ("active", "进行中"),
            ("available", "可接取"),
            ("daily", "日常")
        ]

        for tab_id, tab_name in tabs:
            btn = tk.Button(
                tab_frame,
                text=tab_name,
                command=lambda t=tab_id: self._switch_tab(t),
                font=Theme.get_font(10),
                bg=Theme.BG_TERTIARY,
                fg=Theme.TEXT_PRIMARY,
                activebackground=Theme.ACCENT_CYAN,
                activeforeground=Theme.BG_PRIMARY,
                relief=tk.FLAT,
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[tab_id] = btn

        # 章节信息（仅主线显示）
        self.chapter_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=10, pady=5)
        self.chapter_frame.pack(fill=tk.X, pady=(0, 5))

        self.chapter_label = tk.Label(
            self.chapter_frame,
            text="当前章节：-",
            **Theme.get_label_style("subtitle")
        )
        self.chapter_label.pack(anchor=tk.W)

        # 任务列表
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.quest_listbox = tk.Listbox(
            list_frame,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10),
            selectbackground=Theme.ACCENT_CYAN,
            selectforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.quest_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.quest_listbox.yview)

        # 绑定选择事件
        self.quest_listbox.bind('<<ListboxSelect>>', self._on_quest_select)

        # 刷新按钮
        refresh_btn = tk.Button(
            parent,
            text="🔄 刷新列表",
            command=self._refresh_current_tab,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        refresh_btn.pack(fill=tk.X, pady=(5, 0))

    def _setup_quest_detail(self, parent):
        """设置任务详情区域"""
        # 详情卡片
        detail_card = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=15, pady=15)
        detail_card.pack(fill=tk.BOTH, expand=True)

        # 任务名称
        self.detail_name_label = tk.Label(
            detail_card,
            text="请选择任务",
            **Theme.get_label_style("title")
        )
        self.detail_name_label.pack(anchor=tk.W)

        # 分隔线
        separator = tk.Frame(detail_card, bg=Theme.BORDER_LIGHT, height=2)
        separator.pack(fill=tk.X, pady=10)

        # 任务类型标签
        self.detail_type_label = tk.Label(
            detail_card,
            text="",
            font=Theme.get_font(9),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_DIM
        )
        self.detail_type_label.pack(anchor=tk.W)

        # 任务描述
        desc_frame = tk.Frame(detail_card, bg=Theme.BG_TERTIARY)
        desc_frame.pack(fill=tk.X, pady=10)

        desc_title = tk.Label(
            desc_frame,
            text="任务描述：",
            **Theme.get_label_style("subtitle")
        )
        desc_title.pack(anchor=tk.W)

        self.detail_desc_text = tk.Text(
            desc_frame,
            height=4,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        self.detail_desc_text.pack(fill=tk.X, pady=(5, 0))
        self.detail_desc_text.config(state=tk.DISABLED)

        # 任务目标
        objective_frame = tk.Frame(detail_card, bg=Theme.BG_TERTIARY)
        objective_frame.pack(fill=tk.X, pady=10)

        objective_title = tk.Label(
            objective_frame,
            text="任务目标：",
            **Theme.get_label_style("subtitle")
        )
        objective_title.pack(anchor=tk.W)

        self.detail_objective_label = tk.Label(
            objective_frame,
            text="",
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY
        )
        self.detail_objective_label.pack(anchor=tk.W, pady=(5, 0))

        # 进度条
        self.progress_frame = tk.Frame(detail_card, bg=Theme.BG_TERTIARY)
        self.progress_frame.pack(fill=tk.X, pady=10)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="进度：0/0",
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY
        )
        self.progress_label.pack(anchor=tk.W)

        self.progress_canvas = tk.Canvas(
            self.progress_frame,
            height=20,
            bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=(5, 0))

        # 奖励信息
        reward_frame = tk.Frame(detail_card, bg=Theme.BG_TERTIARY)
        reward_frame.pack(fill=tk.X, pady=10)

        reward_title = tk.Label(
            reward_frame,
            text="任务奖励：",
            **Theme.get_label_style("subtitle")
        )
        reward_title.pack(anchor=tk.W)

        self.detail_reward_text = tk.Text(
            reward_frame,
            height=4,
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT_GOLD,
            font=Theme.get_font(10),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        self.detail_reward_text.pack(fill=tk.X, pady=(5, 0))
        self.detail_reward_text.config(state=tk.DISABLED)

        # 操作按钮
        self.action_frame = tk.Frame(detail_card, bg=Theme.BG_TERTIARY)
        self.action_frame.pack(fill=tk.X, pady=(15, 0))

        self.accept_btn = tk.Button(
            self.action_frame,
            text="接受任务",
            command=self._on_accept_quest,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            activebackground="#66ff66",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.accept_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.claim_btn = tk.Button(
            self.action_frame,
            text="领取奖励",
            command=self._on_claim_reward,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.claim_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.abandon_btn = tk.Button(
            self.action_frame,
            text="放弃任务",
            command=self._on_abandon_quest,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.abandon_btn.pack(side=tk.LEFT)

    def _switch_tab(self, tab_id):
        """切换标签页"""
        self.current_tab = tab_id

        # 更新按钮样式
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(bg=Theme.ACCENT_CYAN, fg=Theme.BG_PRIMARY)
            else:
                btn.config(bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY)

        # 显示/隐藏章节信息
        if tab_id == "active":
            self.chapter_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.chapter_frame.pack_forget()

        self._refresh_current_tab()

    def _refresh_current_tab(self):
        """刷新当前标签页"""
        self.quest_listbox.delete(0, tk.END)
        self.selected_quest = None
        self._clear_detail()

        if not self.quest_manager:
            self.quest_listbox.insert(tk.END, "任务系统未初始化")
            return

        if self.current_tab == "active":
            self._load_active_quests()
        elif self.current_tab == "available":
            self._load_available_quests()
        elif self.current_tab == "daily":
            self._load_daily_quests()

    def _load_active_quests(self):
        """加载进行中的任务"""
        quests = self.quest_manager.get_active_quests()

        if not quests:
            self.quest_listbox.insert(tk.END, "暂无进行中的任务")
            return

        # 按类型分组
        main_quests = [q for q in quests if q.quest_type == "main"]
        side_quests = [q for q in quests if q.quest_type == "side"]
        daily_quests = [q for q in quests if q.quest_type == "daily"]

        # 显示章节进度
        chapter_progress = self.quest_manager.get_chapter_progress()
        self.chapter_label.config(
            text=f"当前章节：第{chapter_progress['chapter']}章 {chapter_progress['chapter_name']}"
        )

        # 插入主线任务
        if main_quests:
            self.quest_listbox.insert(tk.END, "【主线任务】")
            for quest in main_quests:
                status_icon = "✅" if quest.is_completed else "📌"
                self.quest_listbox.insert(tk.END, f"{status_icon} {quest.name}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_GOLD)

        # 插入支线任务
        if side_quests:
            self.quest_listbox.insert(tk.END, "【支线任务】")
            for quest in side_quests:
                status_icon = "✅" if quest.is_completed else "📋"
                self.quest_listbox.insert(tk.END, f"{status_icon} {quest.name}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_CYAN)

        # 插入日常任务
        if daily_quests:
            self.quest_listbox.insert(tk.END, "【日常任务】")
            for quest in daily_quests:
                status_icon = "✅" if quest.is_completed else "📅"
                self.quest_listbox.insert(tk.END, f"{status_icon} {quest.name}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_GREEN)

        # 存储任务引用
        self._current_quests = quests

    def _load_available_quests(self):
        """加载可接取的任务"""
        # 主线任务
        main_quests = self.quest_manager.get_available_main_quests()

        # 支线任务
        side_quests = self.quest_manager.get_available_side_quests(3)

        self._available_quests = []

        if main_quests:
            self.quest_listbox.insert(tk.END, "【主线任务】")
            for quest in main_quests:
                self.quest_listbox.insert(tk.END, f"📜 {quest.name}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_GOLD)
                self._available_quests.append(quest.to_dict())

        if side_quests:
            self.quest_listbox.insert(tk.END, "【支线任务】")
            for quest in side_quests:
                self.quest_listbox.insert(tk.END, f"📋 {quest['name']}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_CYAN)
                self._available_quests.append(quest)

        if not main_quests and not side_quests:
            self.quest_listbox.insert(tk.END, "暂无可接取的任务")

    def _load_daily_quests(self):
        """加载日常任务"""
        daily_quests = self.quest_manager.get_available_daily_quests()

        if not daily_quests:
            self.quest_listbox.insert(tk.END, "今日日常任务已接完")
            return

        self.quest_listbox.insert(tk.END, "【今日日常】")
        for quest in daily_quests:
            # 检查是否已接取
            if self.quest_manager.has_active_quest(quest['id']):
                self.quest_listbox.insert(tk.END, f"✓ {quest['name']} (已接取)")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.TEXT_DIM)
            else:
                self.quest_listbox.insert(tk.END, f"📅 {quest['name']}")
                self.quest_listbox.itemconfig(tk.END, foreground=Theme.ACCENT_GREEN)

        self._daily_quests = daily_quests

    def _on_quest_select(self, event):
        """任务选择事件"""
        selection = self.quest_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        text = self.quest_listbox.get(index)

        # 跳过分组标题
        if text.startswith("【"):
            self.selected_quest = None
            self._clear_detail()
            return

        # 获取对应的任务
        quest = self._get_quest_by_index(index, text)
        if quest:
            self.selected_quest = quest
            self._show_quest_detail(quest)

    def _get_quest_by_index(self, index, text):
        """根据索引获取任务"""
        if self.current_tab == "active":
            # 计算实际的任务索引（跳过标题）
            quest_index = 0
            for i in range(index + 1):
                item_text = self.quest_listbox.get(i)
                if not item_text.startswith("【"):
                    if i == index:
                        if quest_index < len(self._current_quests):
                            return self._current_quests[quest_index]
                    quest_index += 1

        elif self.current_tab == "available":
            quest_index = 0
            for i in range(index + 1):
                item_text = self.quest_listbox.get(i)
                if not item_text.startswith("【"):
                    if i == index:
                        if quest_index < len(self._available_quests):
                            return self._available_quests[quest_index]
                    quest_index += 1

        elif self.current_tab == "daily":
            quest_index = 0
            for i in range(index + 1):
                item_text = self.quest_listbox.get(i)
                if not item_text.startswith("【"):
                    if i == index:
                        if quest_index < len(self._daily_quests):
                            return self._daily_quests[quest_index]
                    quest_index += 1

        return None

    def _show_quest_detail(self, quest):
        """显示任务详情"""
        # 获取任务数据
        if isinstance(quest, dict):
            quest_id = quest.get('id')
            quest_name = quest.get('name')
            quest_desc = quest.get('description')
            quest_type = quest.get('quest_type')
            objective_type = quest.get('objective_type')
            objective_target = quest.get('objective_target')
            objective_count = quest.get('objective_count')
            current_progress = quest.get('current_progress', 0)
            rewards = quest.get('rewards', {})
            is_completed = quest.get('is_completed', False)
            status = quest.get('status', 'available')
        else:
            quest_id = quest.id
            quest_name = quest.name
            quest_desc = quest.description
            quest_type = quest.quest_type
            objective_type = quest.objective_type
            objective_target = quest.objective_target
            objective_count = quest.objective_count
            current_progress = quest.current_progress
            rewards = quest.rewards
            is_completed = quest.is_completed
            status = quest.status

        # 任务名称
        self.detail_name_label.config(text=quest_name)

        # 任务类型
        type_names = {
            'main': '主线任务',
            'side': '支线任务',
            'daily': '日常任务'
        }
        type_colors = {
            'main': Theme.ACCENT_GOLD,
            'side': Theme.ACCENT_CYAN,
            'daily': Theme.ACCENT_GREEN
        }
        self.detail_type_label.config(
            text=f"类型：{type_names.get(quest_type, '未知')}",
            fg=type_colors.get(quest_type, Theme.TEXT_DIM)
        )

        # 任务描述
        self.detail_desc_text.config(state=tk.NORMAL)
        self.detail_desc_text.delete('1.0', tk.END)
        self.detail_desc_text.insert(tk.END, quest_desc)
        self.detail_desc_text.config(state=tk.DISABLED)

        # 任务目标
        objective_names = {
            'cultivation': '修炼',
            'combat': '战斗',
            'collection': '收集',
            'exploration': '探索'
        }
        objective_text = f"{objective_names.get(objective_type, objective_type)}: {objective_target} x{objective_count}"
        self.detail_objective_label.config(text=objective_text)

        # 进度
        if self.current_tab == "active":
            self.progress_frame.pack(fill=tk.X, pady=10)
            self.progress_label.config(text=f"进度：{current_progress}/{objective_count}")
            self._draw_progress_bar(current_progress, objective_count)
        else:
            self.progress_frame.pack_forget()

        # 奖励
        self.detail_reward_text.config(state=tk.NORMAL)
        self.detail_reward_text.delete('1.0', tk.END)

        reward_texts = []
        if rewards.get('exp'):
            reward_texts.append(f"经验：{rewards['exp']}")
        if rewards.get('spirit_stones'):
            reward_texts.append(f"灵石：{rewards['spirit_stones']}")
        if rewards.get('reputation'):
            reward_texts.append(f"声望：{rewards['reputation']}")
        if rewards.get('karma'):
            karma = rewards['karma']
            reward_texts.append(f"业力：{'+' if karma > 0 else ''}{karma}")
        if rewards.get('items'):
            items = rewards['items']
            item_text = "道具：" + ", ".join([f"{item['name']}x{item['count']}" for item in items])
            reward_texts.append(item_text)
        if rewards.get('techniques'):
            techs = rewards['techniques']
            reward_texts.append(f"功法：{', '.join(techs)}")

        self.detail_reward_text.insert(tk.END, "\n".join(reward_texts) if reward_texts else "无")
        self.detail_reward_text.config(state=tk.DISABLED)

        # 更新按钮状态
        self._update_action_buttons(status, is_completed)

    def _draw_progress_bar(self, current, maximum):
        """绘制进度条"""
        self.progress_canvas.delete("all")
        width = self.progress_canvas.winfo_width()
        height = self.progress_canvas.winfo_height()

        if width <= 1:
            self.progress_canvas.after(100, lambda: self._draw_progress_bar(current, maximum))
            return

        # 背景
        self.progress_canvas.create_rectangle(0, 0, width, height, fill=Theme.BG_PRIMARY, outline="")

        # 进度
        if maximum > 0:
            progress = min(current / maximum, 1.0)
            fill_width = int(width * progress)
            color = Theme.ACCENT_GREEN if progress >= 1.0 else Theme.ACCENT_CYAN
            self.progress_canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def _update_action_buttons(self, status, is_completed):
        """更新操作按钮状态"""
        if self.current_tab == "available" or self.current_tab == "daily":
            # 可接取任务
            self.accept_btn.config(state=tk.NORMAL)
            self.claim_btn.config(state=tk.DISABLED)
            self.abandon_btn.config(state=tk.DISABLED)

            # 检查是否已接取
            if self.selected_quest:
                quest_id = self.selected_quest.get('id') if isinstance(self.selected_quest, dict) else self.selected_quest.id
                if self.quest_manager and self.quest_manager.has_active_quest(quest_id):
                    self.accept_btn.config(state=tk.DISABLED, text="已接取")
                else:
                    self.accept_btn.config(state=tk.NORMAL, text="接受任务")

        elif self.current_tab == "active":
            # 进行中任务
            self.accept_btn.config(state=tk.DISABLED)

            if is_completed:
                self.claim_btn.config(state=tk.NORMAL)
                self.abandon_btn.config(state=tk.DISABLED)
            else:
                self.claim_btn.config(state=tk.DISABLED)
                self.abandon_btn.config(state=tk.NORMAL)

    def _clear_detail(self):
        """清空详情显示"""
        self.detail_name_label.config(text="请选择任务")
        self.detail_type_label.config(text="")
        self.detail_desc_text.config(state=tk.NORMAL)
        self.detail_desc_text.delete('1.0', tk.END)
        self.detail_desc_text.config(state=tk.DISABLED)
        self.detail_objective_label.config(text="")
        self.progress_label.config(text="进度：0/0")
        self.progress_canvas.delete("all")
        self.detail_reward_text.config(state=tk.NORMAL)
        self.detail_reward_text.delete('1.0', tk.END)
        self.detail_reward_text.config(state=tk.DISABLED)

        self.accept_btn.config(state=tk.DISABLED)
        self.claim_btn.config(state=tk.DISABLED)
        self.abandon_btn.config(state=tk.DISABLED)

    def _on_accept_quest(self):
        """接受任务"""
        if not self.selected_quest or not self.quest_manager:
            return

        quest_id = self.selected_quest.get('id') if isinstance(self.selected_quest, dict) else self.selected_quest.id
        quest_type = self.selected_quest.get('quest_type') if isinstance(self.selected_quest, dict) else self.selected_quest.quest_type

        success, msg = self.quest_manager.accept_quest(quest_id, quest_type)

        if success:
            self.log(msg, "quest")
            self._refresh_current_tab()
        else:
            messagebox.showwarning("提示", msg)

    def _on_claim_reward(self):
        """领取奖励"""
        if not self.selected_quest or not self.quest_manager:
            return

        quest_id = self.selected_quest.id
        success, msg, rewards = self.quest_manager.claim_reward(quest_id)

        if success:
            # 构建奖励信息
            reward_msgs = [msg]
            if rewards.get('exp'):
                reward_msgs.append(f"获得 {rewards['exp']} 点经验")
            if rewards.get('spirit_stones'):
                reward_msgs.append(f"获得 {rewards['spirit_stones']} 灵石")
            if rewards.get('items'):
                for item in rewards['items']:
                    reward_msgs.append(f"获得 {item['name']} x{item['count']}")
            if rewards.get('techniques'):
                for tech in rewards['techniques']:
                    reward_msgs.append(f"习得功法《{tech}》")

            self.log("\n".join(reward_msgs), "quest")
            self._refresh_current_tab()

            # 刷新主窗口其他面板（状态面板）
            if self.main_window:
                self.main_window.refresh_all_panels()
        else:
            messagebox.showwarning("提示", msg)

    def _on_abandon_quest(self):
        """放弃任务"""
        if not self.selected_quest or not self.quest_manager:
            return

        quest_name = self.selected_quest.name
        if messagebox.askyesno("确认", f"确定要放弃任务「{quest_name}」吗？"):
            quest_id = self.selected_quest.id
            success, msg = self.quest_manager.abandon_quest(quest_id)

            if success:
                self.log(msg, "quest")
                self._refresh_current_tab()
            else:
                messagebox.showwarning("提示", msg)

    def on_show(self):
        """面板显示时调用"""
        self.refresh()

    def refresh(self):
        """刷新面板"""
        player = self.get_player()
        if player:
            # 初始化任务管理器
            if not self.quest_manager:
                from game.quest_system import QuestManager
                self.quest_manager = QuestManager(player.stats.name, player)

        self._switch_tab(self.current_tab)
