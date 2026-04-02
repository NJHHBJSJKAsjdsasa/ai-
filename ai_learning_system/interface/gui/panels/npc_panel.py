"""
NPC 交互面板 - 使用真实游戏数据，与 CLI 功能一致
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from .base_panel import BasePanel
from ..theme import Theme


# 翻译字典
NEED_TRANSLATIONS = {
    'HUNGER': '饥饿',
    'ENERGY': '精力',
    'SOCIAL': '社交',
    'CULTIVATION': '修炼',
    # 兼容旧数据
    'health': '健康',
    'safety': '安全',
    'achievement': '成就',
    'rest': '休息',
}

PERSONALITY_TRANSLATIONS = {
    'bravery': '勇敢',
    'caution': '谨慎',
    'aggression': '攻击性',
    'friendliness': '友善',
    'curiosity': '好奇心',
    'discipline': '自律',
    'greed': '贪婪',
    'loyalty': '忠诚',
}

GOAL_TYPE_TRANSLATIONS = {
    'CULTIVATION': '修炼',
    'SOCIAL': '社交',
    'EXPLORATION': '探索',
    'COMBAT': '战斗',
    'QUEST': '任务',
    'GATHERING': '采集',
    'CRAFTING': ' crafting',
}

ACTIVITY_TYPE_TRANSLATIONS = {
    'SLEEP': '睡眠',
    'CULTIVATION': '修炼',
    'WORK': '工作',
    'SOCIAL': '社交',
    'LEISURE': '休闲',
    'TRAVEL': '旅行',
    'COMBAT': '战斗',
    'SHOPPING': '购物',
    'REST': '休息',
}

EVENT_TYPE_TRANSLATIONS = {
    'BIRTH': '出生',
    'CULTIVATION': '修炼',
    'BREAKTHROUGH': '突破',
    'COMBAT': '战斗',
    'SOCIAL': '社交',
    'TRAVEL': '旅行',
    'QUEST': '任务',
    'ITEM_OBTAINED': '获得物品',
    'ITEM_LOST': '失去物品',
    'RELATIONSHIP': '关系',
    'DEATH': '死亡',
}

RELATION_TYPE_TRANSLATIONS = {
    'FRIEND': '朋友',
    'ENEMY': '敌人',
    'NEUTRAL': '中立',
    'MASTER': '师父',
    'DISCIPLE': '弟子',
    'FAMILY': '家人',
    'RIVAL': '竞争对手',
}


def translate_need(need_name: str) -> str:
    """翻译需求状态"""
    return NEED_TRANSLATIONS.get(need_name, need_name)


def translate_personality(trait: str) -> str:
    """翻译性格属性"""
    return PERSONALITY_TRANSLATIONS.get(trait, trait)


def translate_goal_type(goal_type) -> str:
    """翻译目标类型"""
    if hasattr(goal_type, 'value'):
        goal_type = goal_type.value
    if hasattr(goal_type, 'name'):
        goal_type = goal_type.name
    goal_type_str = str(goal_type).upper()
    return GOAL_TYPE_TRANSLATIONS.get(goal_type_str, str(goal_type))


def translate_activity_type(activity_type) -> str:
    """翻译活动类型"""
    if hasattr(activity_type, 'value'):
        activity_type = activity_type.value
    if hasattr(activity_type, 'name'):
        activity_type = activity_type.name
    activity_type_str = str(activity_type).upper()
    return ACTIVITY_TYPE_TRANSLATIONS.get(activity_type_str, str(activity_type))


def translate_event_type(event_type) -> str:
    """翻译事件类型"""
    if hasattr(event_type, 'value'):
        event_type = event_type.value
    if hasattr(event_type, 'name'):
        event_type = event_type.name
    event_type_str = str(event_type).upper()
    return EVENT_TYPE_TRANSLATIONS.get(event_type_str, str(event_type))


def translate_relation_type(relation_type) -> str:
    """翻译关系类型"""
    if hasattr(relation_type, 'value'):
        relation_type = relation_type.value
    if hasattr(relation_type, 'name'):
        relation_type = relation_type.name
    relation_type_str = str(relation_type).upper()
    return RELATION_TYPE_TRANSLATIONS.get(relation_type_str, str(relation_type))


class NPCPanel(BasePanel):
    """NPC 交互面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.npc_listbox = None
        self.filter_var = None
        self.selected_npc = None
        self.npc_info_var = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="👥 NPC 交互",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左栏 - NPC 列表和信息
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._setup_npc_list(left_frame)
        self._setup_npc_info(left_frame)

        # 右栏 - 操作按钮
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        self._setup_action_buttons(right_frame)

    def _setup_npc_list(self, parent):
        """设置 NPC 列表"""
        # 筛选栏
        filter_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        filter_label = tk.Label(
            filter_frame,
            text="筛选:",
            **Theme.get_label_style("normal")
        )
        filter_label.pack(side=tk.LEFT)

        self.filter_var = tk.StringVar(value="all")
        filters = [
            ("全部", "all"),
            ("友好", "friendly"),
            ("敌对", "hostile"),
        ]

        for text, value in filters:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                command=self._on_filter_change,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_PRIMARY,
                activebackground=Theme.BG_SECONDARY,
                activeforeground=Theme.ACCENT_CYAN,
                font=Theme.get_font(9)
            )
            rb.pack(side=tk.LEFT, padx=5)

        # NPC 列表框
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.npc_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.npc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.npc_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.npc_listbox.yview)

        # 绑定选择事件
        self.npc_listbox.bind("<<ListboxSelect>>", self._on_npc_select)
        self.npc_listbox.bind("<Double-Button-1>", self._on_npc_double_click)

    def _setup_npc_info(self, parent):
        """设置 NPC 信息区域"""
        # 信息标题
        info_title = tk.Label(
            parent,
            text="NPC 信息",
            **Theme.get_label_style("subtitle")
        )
        info_title.pack(anchor=tk.W, pady=(10, 5))

        # NPC 描述
        self.npc_info_var = tk.StringVar(value="选择一个 NPC 查看详情")
        info_label = tk.Label(
            parent,
            textvariable=self.npc_info_var,
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
            **Theme.get_label_style("subtitle")
        )
        action_title.pack(anchor=tk.W, pady=(0, 15))

        # 交谈按钮
        talk_btn = tk.Button(
            parent,
            text="💬 交谈",
            command=self._on_talk,
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
        talk_btn.pack(fill=tk.X, pady=5)

        # 查看详情按钮
        detail_btn = tk.Button(
            parent,
            text="📋 详情",
            command=self._on_view_detail,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        detail_btn.pack(fill=tk.X, pady=5)

        # 查看目标按钮
        goals_btn = tk.Button(
            parent,
            text="🎯 目标",
            command=self._on_view_goals,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_GREEN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        goals_btn.pack(fill=tk.X, pady=5)

        # 查看关系按钮
        relations_btn = tk.Button(
            parent,
            text="🔗 关系",
            command=self._on_view_relations,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_PURPLE,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        relations_btn.pack(fill=tk.X, pady=5)

        # 查看日程按钮
        schedule_btn = tk.Button(
            parent,
            text="📅 日程",
            command=self._on_view_schedule,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_CYAN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        schedule_btn.pack(fill=tk.X, pady=5)

        # 查看故事按钮
        story_btn = tk.Button(
            parent,
            text="📖 故事",
            command=self._on_view_story,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_GOLD,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        story_btn.pack(fill=tk.X, pady=5)

        # 查看个性按钮
        personality_btn = tk.Button(
            parent,
            text="🎭 个性",
            command=self._on_view_personality,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_GREEN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        personality_btn.pack(fill=tk.X, pady=5)

        # 战斗按钮
        combat_btn = tk.Button(
            parent,
            text="⚔️ 切磋",
            command=self._on_combat,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        combat_btn.pack(fill=tk.X, pady=5)

    def _get_current_location(self):
        """获取当前位置"""
        player = self.get_player()
        if player and hasattr(player, 'stats'):
            return player.stats.location
        return "新手村"

    def _get_npcs(self):
        """获取 NPC 列表 - 使用真实 NPC 管理器"""
        world = self.get_world()
        if world:
            location = self._get_current_location()
            # 使用 world 的方法获取 NPC
            npcs = world.get_npcs_in_location(location)
            return npcs if npcs else []
        return []

    def _get_filtered_npcs(self):
        """获取筛选后的 NPC 列表"""
        npcs = self._get_npcs()
        filter_type = self.filter_var.get()

        if filter_type == "all":
            return npcs
        elif filter_type == "friendly":
            return [npc for npc in npcs if self._get_attitude(npc) == "friendly"]
        elif filter_type == "hostile":
            return [npc for npc in npcs if self._get_attitude(npc) == "hostile"]

        return npcs

    def _get_attitude(self, npc):
        """获取 NPC 对玩家的态度"""
        player = self.get_player()
        if not player:
            return "neutral"
        
        # 通过 favor 判断态度
        if hasattr(npc, 'get_favor'):
            favor = npc.get_favor(player.stats.name)
            if favor > 30:
                return "friendly"
            elif favor < -30:
                return "hostile"
        return "neutral"

    def refresh(self):
        """刷新面板 - 使用真实数据"""
        self.npc_listbox.delete(0, tk.END)
        npcs = self._get_filtered_npcs()

        for npc in npcs:
            # NPC 数据通过 data 属性访问
            name = npc.data.dao_name if hasattr(npc, 'data') else "未知"
            realm = npc.get_realm_name() if hasattr(npc, 'get_realm_name') else "凡人"
            attitude = self._get_attitude(npc)

            # 根据关系显示不同标记
            if attitude == "friendly":
                marker = "😊"
            elif attitude == "hostile":
                marker = "😠"
            else:
                marker = "😐"

            self.npc_listbox.insert(tk.END, f"{marker} {name} ({realm})")

        # 清空 NPC 信息
        self.npc_info_var.set("选择一个 NPC 查看详情")

    def _on_filter_change(self):
        """筛选改变回调"""
        self.refresh()

    def _on_npc_select(self, event=None):
        """NPC 选择回调"""
        selection = self.npc_listbox.curselection()
        if selection:
            index = selection[0]
            npcs = self._get_filtered_npcs()
            if 0 <= index < len(npcs):
                self.selected_npc = npcs[index]
                # 更新 NPC 信息显示
                self._update_npc_info(self.selected_npc)

    def _update_npc_info(self, npc):
        """更新 NPC 信息显示"""
        if not hasattr(npc, 'data'):
            self.npc_info_var.set("无法获取 NPC 信息")
            return

        data = npc.data
        info = f"道号: {data.dao_name}\n"
        info += f"境界: {npc.get_realm_name() if hasattr(npc, 'get_realm_name') else '凡人'}\n"
        info += f"门派: {data.sect}\n"
        info += f"职业: {data.occupation}\n"
        info += f"性格: {data.personality}\n"
        info += f"年龄: {data.age}岁 / 寿元: {data.lifespan}年\n"
        info += f"位置: {data.location}\n"
        info += f"态度: {self._get_attitude(npc)}"
        self.npc_info_var.set(info)

    def _on_npc_double_click(self, event=None):
        """NPC 双击回调"""
        self._on_view_detail()

    def _get_selected_npc(self):
        """获取选中的 NPC"""
        selection = self.npc_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个 NPC")
            return None

        index = selection[0]
        npcs = self._get_filtered_npcs()
        if 0 <= index < len(npcs):
            return npcs[index]
        return None

    def _on_talk(self):
        """交谈按钮回调"""
        npc = self._get_selected_npc()
        if not npc:
            return

        npc_name = npc.data.dao_name if hasattr(npc, 'data') else "未知"

        # 打开对话窗口
        dialog = NPCDialog(self, npc_name, npc)
        dialog.show()

    def _on_view_detail(self):
        """查看详情按钮回调 - 与 CLI 的 /npc 命令一致"""
        npc = self._get_selected_npc()
        if not npc:
            return

        if not hasattr(npc, 'data'):
            messagebox.showinfo("提示", "无法获取 NPC 详细信息")
            return

        # 使用 get_independent_status 获取完整状态
        status = npc.get_independent_status() if hasattr(npc, 'get_independent_status') else {}

        data = npc.data
        info = f"📋 {data.dao_name} 的详细信息\n"
        info += "═" * 50 + "\n\n"
        
        info += f"道号: {data.dao_name}\n"
        info += f"境界: {npc.get_realm_name()}\n"
        info += f"年龄: {data.age}岁 / {data.lifespan}岁\n"
        info += f"门派: {data.sect}\n"
        info += f"职业: {data.occupation}\n"
        info += f"位置: {data.location}\n"
        info += f"性格: {data.personality}\n"
        info += "─" * 50 + "\n\n"
        
        # 显示独立系统信息
        if status:
            info += f"当前活动: {status.get('current_activity', '未知')}\n"
            info += f"最后行动: {status.get('last_action', '无')}\n\n"
            
            # 显示需求状态
            info += "需求状态:\n"
            needs = status.get('needs', {})
            for need_name, value in needs.items():
                bar = self._render_bar(value, 100, 20)
                cn_name = translate_need(need_name)
                info += f"  {cn_name:<10} [{bar}] {value:.1f}\n"

            # 显示目标
            info += "\n当前目标:\n"
            goals = status.get('goals', [])
            for goal in goals[:3]:
                progress = goal.get('progress', '0%')
                completed = "✓" if goal.get('completed') else "○"
                info += f"  {completed} {goal.get('description', '未知')} ({progress})\n"

            # 显示性格属性
            info += "\n性格属性:\n"
            personality = status.get('personality', {})
            for trait, value in personality.items():
                bar = self._render_bar(value * 100, 100, 20)
                cn_trait = translate_personality(trait)
                info += f"  {cn_trait:<8} [{bar}] {value:.2f}\n"
            
            info += f"\n记忆数量: {status.get('memory_count', 0)}\n"
            info += f"关系数量: {status.get('relationship_count', 0)}\n"
            info += f"总行动数: {status.get('total_actions', 0)}\n"
        
        info += "\n" + "═" * 50

        messagebox.showinfo("NPC 详情", info)

    def _render_bar(self, value, max_value, width=20):
        """渲染进度条"""
        ratio = min(1.0, value / max_value) if max_value > 0 else 0
        filled = int(width * ratio)
        empty = width - filled
        return "█" * filled + "░" * empty

    def _on_view_goals(self):
        """查看目标按钮回调 - 与 CLI 的 /npc_goals 命令一致"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.dao_name if hasattr(npc, 'data') else "未知"
        
        info = f"🎯 {name} 的目标\n"
        info += "═" * 50 + "\n\n"

        # 获取目标列表
        goals = getattr(npc, 'goals', [])
        
        if not goals:
            info += "暂无目标\n"
        else:
            # 分类目标
            active_goals = [g for g in goals if not getattr(g, 'is_completed', False) and not getattr(g, 'is_failed', False)]
            completed_goals = [g for g in goals if getattr(g, 'is_completed', False)]
            failed_goals = [g for g in goals if getattr(g, 'is_failed', False)]
            
            # 显示进行中的目标
            if active_goals:
                info += "📌 进行中:\n"
                for goal in sorted(active_goals, key=lambda g: getattr(g, 'priority', 5), reverse=True):
                    goal_type = getattr(goal, 'goal_type', '未知')
                    goal_type_str = translate_goal_type(goal_type)

                    priority = getattr(goal, 'priority', 5)
                    priority_str = "★" * (priority // 2) + "☆" * (5 - priority // 2)

                    current = getattr(goal, 'current_value', 0)
                    target = getattr(goal, 'target_value', 1)
                    progress = min(100, int(current / target * 100)) if target > 0 else 0
                    progress_bar = self._render_bar(progress, 100, 10)

                    info += f"  {priority_str} [{goal_type_str[:6]}] {getattr(goal, 'description', '未知')[:20]}\n"
                    info += f"      [{progress_bar}] {progress}%\n"
                info += "\n"

            # 显示已完成的目标
            if completed_goals:
                info += f"✅ 已完成 ({len(completed_goals)}个):\n"
                for goal in completed_goals[:3]:
                    goal_type = getattr(goal, 'goal_type', '未知')
                    goal_type_str = translate_goal_type(goal_type)
                    info += f"  ✓ {getattr(goal, 'description', '未知')} [{goal_type_str}]\n"
                info += "\n"

            # 显示失败的目标
            if failed_goals:
                info += f"❌ 已失败 ({len(failed_goals)}个):\n"
                for goal in failed_goals[:2]:
                    goal_type = getattr(goal, 'goal_type', '未知')
                    goal_type_str = translate_goal_type(goal_type)
                    info += f"  ✗ {getattr(goal, 'description', '未知')} [{goal_type_str}]\n"
                info += "\n"
            
            total = len(goals)
            completion_rate = len(completed_goals) / total * 100 if total > 0 else 0
            info += f"总计: {total}个目标 | 完成率: {completion_rate:.1f}%\n"

        messagebox.showinfo("NPC 目标", info)

    def _on_view_relations(self):
        """查看关系按钮回调 - 使用真实关系数据"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.dao_name if hasattr(npc, 'data') else "未知"

        info = f"🤝 {name} 的关系网络\n"
        info += "═" * 50 + "\n\n"

        # 从关系网络获取真实关系数据
        friends = npc.get_friends(min_affinity=20) if hasattr(npc, 'get_friends') else []
        enemies = npc.get_enemies(min_hatred=20) if hasattr(npc, 'get_enemies') else []
        all_relations = npc.get_all_relationships() if hasattr(npc, 'get_all_relationships') else {}

        # 获取关系统计
        stats = None
        if hasattr(npc, 'get_relationship_with') and all_relations:
            from game.npc_relationship_network import relationship_network
            stats = relationship_network.get_network_stats(npc.data.id)

        if stats:
            info += f"📊 关系统计: 总计{stats.get('total_relations', 0)}位关系人\n"
            info += f"   朋友: {stats.get('friends_count', 0)} | 敌人: {stats.get('enemies_count', 0)}\n"
            info += f"   平均好感度: {stats.get('avg_affinity', 0):.1f}\n\n"

        # 显示朋友列表
        if friends:
            info += f"😊 朋友 ({len(friends)}位):\n"
            for friend_id, relationship in sorted(friends, key=lambda x: x[1].affinity, reverse=True)[:5]:
                affinity = relationship.affinity
                intimacy = relationship.intimacy
                affinity_bar = self._render_bar(affinity + 100, 200, 8)
                rel_strength = relationship.get_relation_description()
                info += f"  {friend_id[:8]:<10} [{affinity_bar}] {rel_strength} (亲密:{intimacy})\n"
            info += "\n"

        # 显示敌人列表
        if enemies:
            info += f"😠 敌人 ({len(enemies)}位):\n"
            for enemy_id, relationship in sorted(enemies, key=lambda x: x[1].hatred, reverse=True)[:5]:
                hatred = relationship.hatred
                hatred_bar = self._render_bar(hatred, 100, 8)
                hostility = relationship.get_relation_description()
                info += f"  {enemy_id[:8]:<10} [{hatred_bar}] {hostility}\n"
            info += "\n"

        # 显示其他关系（非朋友非敌人的关系）
        others = []
        for other_id, relationship in all_relations.items():
            if other_id not in [f[0] for f in friends] and other_id not in [e[0] for e in enemies]:
                others.append((other_id, relationship))

        if others:
            info += f"😐 其他关系 ({len(others)}位):\n"
            for other_id, relationship in sorted(others, key=lambda x: x[1].affinity, reverse=True)[:5]:
                affinity = relationship.affinity
                rel_desc = relationship.get_relation_description()
                info += f"  {other_id[:8]}: {rel_desc} (好感度: {affinity})\n"
            info += "\n"

        if not friends and not enemies and not others:
            info += "暂无关系数据\n"
            info += "\n提示：NPC关系会在游戏运行中自动建立和发展\n"

        info += "\n" + "═" * 50

        messagebox.showinfo("NPC 关系", info)

    def _on_view_schedule(self):
        """查看日程按钮回调 - 与 CLI 的 /npc_schedule 命令一致"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.dao_name if hasattr(npc, 'data') else "未知"
        
        info = f"📅 {name} 的日程\n"
        info += "═" * 50 + "\n\n"

        # 获取日程
        schedule = getattr(npc, 'schedule', {})
        
        if not schedule:
            info += "暂无日程安排\n"
        else:
            # 显示当前活动
            import time
            current_hour = int((time.time() // 3600) % 24)
            current_activity = schedule.get(current_hour)
            
            if current_activity:
                info += "🔔 当前活动:\n"
                activity_name = getattr(current_activity, 'name', '未知活动')
                activity_type = getattr(current_activity, 'activity_type', '未知')
                activity_type_str = translate_activity_type(activity_type)

                info += f"  时间: {current_hour}:00 - {current_hour + 1}:00\n"
                info += f"  活动: {activity_name}\n"
                info += f"  类型: {activity_type_str}\n"

                location = getattr(current_activity, 'location', '')
                if location:
                    info += f"  地点: {location}\n"
                info += "\n"

            # 显示全天日程
            info += "📋 今日日程:\n"
            for hour in range(24):
                activity = schedule.get(hour)
                if activity:
                    time_str = f"{hour:02d}:00"
                    name = getattr(activity, 'name', '未知')[:10]
                    act_type = getattr(activity, 'activity_type', '未知')
                    act_type_str = translate_activity_type(act_type)[:4]
                    location = getattr(activity, 'location', '')[:8]

                    # 高亮当前时间
                    if hour == current_hour:
                        time_str = f"▶ {time_str}"

                    info += f"  {time_str:<8} {name:<12} {act_type_str:<6} {location}\n"
            
            # 显示临时事件
            temp_events = getattr(npc, 'temp_events', [])
            if temp_events:
                info += "\n⚡ 临时事件:\n"
                for event in temp_events[:3]:
                    event_desc = getattr(event, 'description', '未知事件')
                    event_time = getattr(event, 'time', '未知时间')
                    info += f"  • {event_time}: {event_desc}\n"

        messagebox.showinfo("NPC 日程", info)

    def _on_view_story(self):
        """查看故事按钮回调 - 与 CLI 的 /npc_story 命令一致"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.name if hasattr(npc, 'data') else "未知"
        
        info = f"📖 {name} 的人生故事\n"
        info += "═" * 50 + "\n\n"

        # 基本信息
        info += "👤 基本信息:\n"
        info += f"  姓名: {npc.data.name}\n"
        info += f"  道号: {npc.data.dao_name}\n"
        info += f"  年龄: {npc.data.age}岁 / 寿元: {npc.data.lifespan}岁\n"
        info += f"  门派: {npc.data.sect}\n"
        info += f"  职业: {npc.data.occupation}\n"
        info += f"  当前境界: {npc.get_realm_name()}\n\n"

        # 获取人生记录
        life_record = getattr(npc, 'life_record', None)
        
        if life_record:
            # 显示关键事件
            events = getattr(life_record, 'records', {}).get(npc.data.id, [])
            
            if events:
                info += f"📜 关键事件 ({len(events)}件):\n"
                # 按重要性排序，显示重要事件
                important_events = sorted(
                    events, 
                    key=lambda e: getattr(e, 'importance', 5), 
                    reverse=True
                )[:5]
                
                for i, event in enumerate(important_events, 1):
                    event_type = getattr(event, 'event_type', '未知')
                    event_type_str = translate_event_type(event_type)

                    timestamp = getattr(event, 'timestamp', 0)
                    import time
                    time_str = time.strftime("%m-%d", time.localtime(timestamp)) if timestamp else "未知"

                    description = getattr(event, 'description', '未知')[:20]
                    importance = getattr(event, 'importance', 5)
                    importance_str = "★" * importance + "☆" * (10 - importance)

                    info += f"  {i}. [{time_str}] [{event_type_str[:6]}] {description} {importance_str}\n"
                info += "\n"
            
            # 显示修炼历程
            cultivation_events = [e for e in events if 'CULTIVATION' in str(type(e)).upper() or 
                                 (hasattr(e, 'event_type') and 'CULTIVATION' in str(e.event_type).upper())]
            
            if cultivation_events:
                info += "🧘 修炼历程:\n"
                for event in cultivation_events[-3:]:
                    desc = getattr(event, 'description', '未知')
                    outcome = getattr(event, 'outcome', '')
                    info += f"  • {desc}\n"
                    if outcome:
                        info += f"    结果: {outcome}\n"
                info += "\n"
        
        # 生成人生简介
        info += "📚 人生简介:\n"
        personality = npc.data.personality
        occupation = npc.data.occupation
        sect = npc.data.sect
        realm = npc.get_realm_name()
        
        story_parts = []
        story_parts.append(f"{npc.data.name}，道号{npc.data.dao_name}，")
        story_parts.append(f"{npc.data.age}岁，出身于{sect}。")
        story_parts.append(f"性格{personality}，以{occupation}为业。")
        story_parts.append(f"目前修为已达{realm}。")
        
        if life_record and events:
            story_parts.append(f"\n一生经历{len(events)}件大事，")
            if cultivation_events:
                story_parts.append(f"修炼突破{len(cultivation_events)}次。")
        
        story_text = "".join(story_parts)
        info += f"  {story_text}\n"

        messagebox.showinfo("NPC 故事", info)

    def _on_view_personality(self):
        """查看个性按钮回调 - 与 CLI 的 /npc_personality 命令一致"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.dao_name if hasattr(npc, 'data') else "未知"
        
        info = f"🎭 {name} 的个性\n"
        info += "═" * 50 + "\n\n"

        # 显示个性描述
        info += "📝 个性描述:\n"
        info += f"  性格: {npc.data.personality}\n"
        info += f"  职业: {npc.data.occupation}\n"
        info += f"  门派: {npc.data.sect}\n\n"
        
        # 从独立系统获取性格属性
        status = npc.get_independent_status() if hasattr(npc, 'get_independent_status') else {}
        personality_traits = status.get('personality', {})
        
        if personality_traits:
            info += "性格属性:\n"
            for trait, value in personality_traits.items():
                bar = self._render_bar(value * 100, 100, 15)
                cn_trait = translate_personality(trait)
                info += f"  {cn_trait:<8} [{bar}] {value:.2f}\n"
            info += "\n"
        
        # 显示价值观
        values_system = getattr(npc, 'values', None)
        if values_system:
            info += "💎 价值观:\n"
            
            values = getattr(values_system, 'values', None)
            if values:
                values_dict = {}
                if hasattr(values, 'to_dict'):
                    values_dict = values.to_dict()
                else:
                    values_dict = {
                        'justice': getattr(values, 'justice', 50),
                        'interest': getattr(values, 'interest', 50),
                        'loyalty': getattr(values, 'loyalty', 50),
                        'freedom': getattr(values, 'freedom', 50),
                        'power': getattr(values, 'power', 50),
                    }
                
                name_map = {
                    'justice': '正义',
                    'interest': '利益',
                    'loyalty': '忠诚',
                    'freedom': '自由',
                    'power': '权力',
                }
                
                for key, display_name in name_map.items():
                    value = values_dict.get(key, 50)
                    bar = self._render_bar(value, 100, 15)
                    info += f"  {display_name:<6} [{bar}] {value}\n"
                
                # 显示主导价值观
                if hasattr(values_system, 'get_dominant_value'):
                    dominant_name, dominant_value = values_system.get_dominant_value()
                    info += f"\n主导价值观: {dominant_name} ({dominant_value})\n"
                
                if hasattr(values_system, 'get_value_description'):
                    value_desc = values_system.get_value_description()
                    info += f"性格倾向: {value_desc}\n"

        messagebox.showinfo("NPC 个性", info)

    def _on_combat(self):
        """战斗按钮回调"""
        npc = self._get_selected_npc()
        if not npc:
            return

        name = npc.data.dao_name if hasattr(npc, 'data') else "未知"

        if messagebox.askyesno("确认", f"确定要与 {name} 切磋吗？"):
            self.log(f"你向 {name} 发起了切磋请求", "combat")
            # 切换到战斗面板
            if self.main_window:
                self.main_window.show_panel("combat")


class NPCDialog:
    """NPC 对话窗口"""

    def __init__(self, parent, npc_name, npc=None):
        self.parent = parent
        self.npc_name = npc_name
        self.npc = npc
        self.dialog = None
        self.chat_text = None
        self.input_entry = None

    def show(self):
        """显示对话框"""
        self.dialog = tk.Toplevel()
        self.dialog.title(f"与 {self.npc_name} 对话")
        self.dialog.geometry("500x400")
        self.dialog.config(bg=Theme.BG_SECONDARY)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 对话历史
        chat_frame = tk.Frame(self.dialog, bg=Theme.BG_TERTIARY)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_text = tk.Text(
            chat_frame,
            state=tk.DISABLED,
            **Theme.get_text_style()
        )
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chat_text.yview)

        # 配置标签
        self.chat_text.tag_config("npc", foreground=Theme.ACCENT_GOLD, font=Theme.get_font(10, bold=True))
        self.chat_text.tag_config("player", foreground=Theme.ACCENT_CYAN, font=Theme.get_font(10, bold=True))
        self.chat_text.tag_config("message", foreground=Theme.TEXT_PRIMARY, font=Theme.get_font(10))

        # 添加欢迎消息
        welcome_msg = "道友，有何贵干？"
        attitude = self._get_npc_attitude()
        if attitude == "friendly":
            welcome_msg = "道友来了，快请进！"
        elif attitude == "hostile":
            welcome_msg = "哼，你来做什么？"

        self._add_message(f"{self.npc_name}", welcome_msg, "npc")

        # 输入区域
        input_frame = tk.Frame(self.dialog, bg=Theme.BG_SECONDARY)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_entry = tk.Entry(
            input_frame,
            **Theme.get_entry_style()
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self._on_send)

        send_btn = tk.Button(
            input_frame,
            text="发送",
            command=self._on_send,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 关闭按钮
        close_btn = tk.Button(
            self.dialog,
            text="结束对话",
            command=self._on_close,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        close_btn.pack(pady=(0, 10))

        # 聚焦输入框
        self.input_entry.focus_set()

    def _get_npc_attitude(self):
        """获取 NPC 态度"""
        if self.npc and hasattr(self.npc, 'get_favor'):
            # 获取玩家名字
            player_name = "player"  # 默认玩家名
            favor = self.npc.get_favor(player_name)
            if favor > 30:
                return "friendly"
            elif favor < -30:
                return "hostile"
        return "neutral"

    def _add_message(self, speaker, message, speaker_type):
        """添加消息到对话历史"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{speaker}: ", speaker_type)
        self.chat_text.insert(tk.END, f"{message}\n\n", "message")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _on_send(self, event=None):
        """发送消息"""
        message = self.input_entry.get().strip()
        if not message:
            return

        # 添加玩家消息
        self._add_message("你", message, "player")
        self.input_entry.delete(0, tk.END)

        # 更新好感度
        if self.npc and hasattr(self.npc, 'update_favor'):
            self.npc.update_favor("player", 1)

        # 添加记忆
        if self.npc and hasattr(self.npc, 'add_memory'):
            self.npc.add_memory(f"与玩家交谈", importance=3)

        # NPC 回复
        self.dialog.after(500, self._npc_reply)

    def _npc_reply(self):
        """NPC 回复"""
        attitude = self._get_npc_attitude()

        if attitude == "friendly":
            replies = [
                "原来如此，道友果然见识不凡。",
                "此事说来话长，不如我们慢慢聊。",
                "我最近也在寻找这个问题的答案。",
                "道友可曾听说过那个传说？",
                "哈哈哈，有趣有趣！",
                "如果道友需要帮忙，尽管开口。",
            ]
        elif attitude == "hostile":
            replies = [
                "哼，少废话！",
                "我没兴趣跟你闲聊。",
                "有事快说，有屁快放！",
                "你这种人我见得多了。",
                "别来烦我！",
            ]
        else:
            replies = [
                "嗯，继续说。",
                "原来如此。",
                "我了解了。",
                "还有其他事吗？",
            ]

        import random
        reply = random.choice(replies)
        self._add_message(self.npc_name, reply, "npc")

    def _on_close(self):
        """关闭对话框"""
        self.dialog.destroy()
