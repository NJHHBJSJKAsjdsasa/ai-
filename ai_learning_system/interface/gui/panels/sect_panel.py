"""
门派面板 - 管理门派相关功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from .base_panel import BasePanel
from ..theme import Theme


class SectPanel(BasePanel):
    """门派面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.sect_manager = None
        self.current_sect = None
        self.sect_listbox = None
        self.member_listbox = None
        self.task_listbox = None
        self.technique_listbox = None
        self.info_text = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🏛️ 门派",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区 - 使用Notebook实现标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置Notebook样式
        style = ttk.Style()
        style.configure("TNotebook", background=Theme.BG_SECONDARY)
        style.configure("TNotebook.Tab", background=Theme.BG_TERTIARY, foreground=Theme.TEXT_PRIMARY)
        style.map("TNotebook.Tab", background=[("selected", Theme.ACCENT_CYAN)])

        # 创建各个标签页
        self._create_overview_tab()
        self._create_sects_tab()
        self._create_members_tab()
        self._create_tasks_tab()
        self._create_techniques_tab()

    def _create_overview_tab(self):
        """创建概览标签页"""
        self.overview_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.overview_frame, text="概览")

        # 门派信息区域
        self.overview_text = tk.Text(
            self.overview_frame,
            wrap=tk.WORD,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            height=20
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.overview_text.config(state=tk.DISABLED)

        # 操作按钮区域
        btn_frame = tk.Frame(self.overview_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.join_btn = tk.Button(
            btn_frame,
            text="🚪 加入门派",
            command=self._on_join_sect,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.join_btn.pack(side=tk.LEFT, padx=5)

        self.leave_btn = tk.Button(
            btn_frame,
            text="🚶 退出门派",
            command=self._on_leave_sect,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.leave_btn.pack(side=tk.LEFT, padx=5)

        self.promotion_btn = tk.Button(
            btn_frame,
            text="📈 晋升信息",
            command=self._on_check_promotion,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.promotion_btn.pack(side=tk.LEFT, padx=5)

    def _create_sects_tab(self):
        """创建门派列表标签页"""
        self.sects_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.sects_frame, text="所有门派")

        # 门派列表
        list_frame = tk.Frame(self.sects_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sect_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.sect_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sect_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.sect_listbox.yview)

        self.sect_listbox.bind("<<ListboxSelect>>", self._on_sect_select)
        self.sect_listbox.bind("<Double-Button-1>", self._on_sect_double_click)

        # 门派信息
        self.sect_info_var = tk.StringVar(value="选择一个门派查看详情")
        info_label = tk.Label(
            self.sects_frame,
            textvariable=self.sect_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 加入按钮
        self.join_sect_btn = tk.Button(
            self.sects_frame,
            text="➕ 加入该门派",
            command=self._on_join_selected_sect,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.join_sect_btn.pack(pady=10)

    def _create_members_tab(self):
        """创建成员列表标签页"""
        self.members_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.members_frame, text="门派成员")

        # 成员列表
        list_frame = tk.Frame(self.members_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.member_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.member_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.member_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.member_listbox.yview)

        # 提示标签
        self.members_hint = tk.Label(
            self.members_frame,
            text="加入门派后可查看成员列表",
            **Theme.get_label_style("dim")
        )
        self.members_hint.pack(pady=10)

    def _create_tasks_tab(self):
        """创建任务标签页"""
        self.tasks_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.tasks_frame, text="门派任务")

        # 任务列表
        list_frame = tk.Frame(self.tasks_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.task_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

        self.task_listbox.bind("<<ListboxSelect>>", self._on_task_select)

        # 任务信息
        self.task_info_var = tk.StringVar(value="选择一个任务查看详情")
        info_label = tk.Label(
            self.tasks_frame,
            textvariable=self.task_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 操作按钮
        btn_frame = tk.Frame(self.tasks_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.accept_task_btn = tk.Button(
            btn_frame,
            text="📋 接受任务",
            command=self._on_accept_task,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.accept_task_btn.pack(side=tk.LEFT, padx=5)

        self.complete_task_btn = tk.Button(
            btn_frame,
            text="✅ 完成任务",
            command=self._on_complete_task,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.complete_task_btn.pack(side=tk.LEFT, padx=5)

        # 提示标签
        self.tasks_hint = tk.Label(
            self.tasks_frame,
            text="加入门派后可接取任务",
            **Theme.get_label_style("dim")
        )
        self.tasks_hint.pack(pady=10)

    def _create_techniques_tab(self):
        """创建功法标签页"""
        self.techniques_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.techniques_frame, text="门派功法")

        # 功法列表
        list_frame = tk.Frame(self.techniques_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.technique_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.technique_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.technique_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.technique_listbox.yview)

        self.technique_listbox.bind("<<ListboxSelect>>", self._on_technique_select)

        # 功法信息
        self.technique_info_var = tk.StringVar(value="选择一个功法查看详情")
        info_label = tk.Label(
            self.techniques_frame,
            textvariable=self.technique_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 学习按钮
        self.learn_tech_btn = tk.Button(
            self.techniques_frame,
            text="📖 学习功法",
            command=self._on_learn_technique,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.learn_tech_btn.pack(pady=10)

        # 提示标签
        self.techniques_hint = tk.Label(
            self.techniques_frame,
            text="加入门派后可学习门派功法",
            **Theme.get_label_style("dim")
        )
        self.techniques_hint.pack(pady=10)

    def _get_sect_manager(self):
        """获取门派管理器"""
        if self.sect_manager is None:
            from game.sect_system import get_sect_manager
            self.sect_manager = get_sect_manager()
            self.sect_manager.initialize_sects()
        return self.sect_manager

    def refresh(self):
        """刷新面板"""
        self._refresh_overview()
        self._refresh_sect_list()
        self._refresh_members()
        self._refresh_tasks()
        self._refresh_techniques()

    def _refresh_overview(self):
        """刷新概览"""
        player = self.get_player()
        if not player:
            self._set_overview_text("请先创建角色")
            return

        manager = self._get_sect_manager()
        sect_info = manager.get_player_sect(player.stats.name)

        if sect_info:
            self.current_sect = sect_info

            # 获取晋升信息
            promotion_info = manager.get_next_promotion_info(player.stats.name)

            text = f"""
╔══════════════════════════════════════════════════════════╗
║  🏛️ {sect_info['sect_name']}                                    ║
╠══════════════════════════════════════════════════════════╣
║  职位: {sect_info['position']}                                      ║
║  贡献: {sect_info['contribution']}                                          ║
║  门派类型: {sect_info['sect_type']}                                    ║
║  主属性: {sect_info['main_element']}                                        ║
╠══════════════════════════════════════════════════════════╣
"""
            if promotion_info:
                text += f"""║  晋升进度: {promotion_info['current_position']} → {promotion_info['next_position']}              ║
║  贡献: {promotion_info['current_contribution']}/{promotion_info['required_contribution']} ({int(promotion_info['progress']*100)}%)                          ║
╚══════════════════════════════════════════════════════════╝"""
            else:
                text += "║  你已达到最高职位！                                      ║\n"
                text += "╚══════════════════════════════════════════════════════════╝"

            self._set_overview_text(text)

            # 更新按钮状态
            self.join_btn.config(state=tk.DISABLED)
            self.leave_btn.config(state=tk.NORMAL)
            if promotion_info:
                self.promotion_btn.config(state=tk.NORMAL)
            else:
                self.promotion_btn.config(state=tk.DISABLED)
        else:
            self.current_sect = None
            self._set_overview_text("""
╔══════════════════════════════════════════════════════════╗
║  🏛️ 无门无派                                              ║
╠══════════════════════════════════════════════════════════╣
║  你还没有加入任何门派                                      ║
║  加入门派可以获得：                                        ║
║    • 门派专属功法                                          ║
║    • 门派任务奖励                                          ║
║    • 职位晋升体系                                          ║
║    • 门派庇护                                              ║
╚══════════════════════════════════════════════════════════╝

💡 提示：切换到"所有门派"标签页选择门派加入
""")
            self.join_btn.config(state=tk.NORMAL)
            self.leave_btn.config(state=tk.DISABLED)
            self.promotion_btn.config(state=tk.DISABLED)

    def _set_overview_text(self, text):
        """设置概览文本"""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(1.0, text)
        self.overview_text.config(state=tk.DISABLED)

    def _refresh_sect_list(self):
        """刷新门派列表"""
        self.sect_listbox.delete(0, tk.END)

        manager = self._get_sect_manager()
        sects = manager.get_all_sects()

        for sect in sects:
            self.sect_listbox.insert(
                tk.END,
                f"{sect['name']} [{sect['sect_type']}] - {sect['main_element']}属性"
            )

    def _refresh_members(self):
        """刷新成员列表"""
        self.member_listbox.delete(0, tk.END)

        if not self.current_sect:
            self.members_hint.config(text="加入门派后可查看成员列表")
            return

        self.members_hint.config(text="")

        manager = self._get_sect_manager()
        members = manager.get_sect_members(self.current_sect['sect_id'], limit=50)

        for i, member in enumerate(members, 1):
            self.member_listbox.insert(
                tk.END,
                f"{i}. {member['player_name']} - {member['position']} (贡献: {member['contribution']})"
            )

    def _refresh_tasks(self):
        """刷新任务列表"""
        self.task_listbox.delete(0, tk.END)
        self.tasks = []

        if not self.current_sect:
            self.tasks_hint.config(text="加入门派后可接取任务")
            return

        self.tasks_hint.config(text="")

        manager = self._get_sect_manager()
        tasks = manager.get_sect_tasks(
            self.current_sect['sect_id'],
            self.current_sect['position']
        )
        self.tasks = tasks

        for task in tasks:
            self.task_listbox.insert(
                tk.END,
                f"{task['task_name']} [{task['task_type']}] - 难度{task['difficulty']}"
            )

    def _refresh_techniques(self):
        """刷新功法列表"""
        self.technique_listbox.delete(0, tk.END)
        self.techniques = []

        if not self.current_sect:
            self.techniques_hint.config(text="加入门派后可学习门派功法")
            return

        self.techniques_hint.config(text="")

        manager = self._get_sect_manager()
        techniques = manager.get_sect_techniques(
            self.current_sect['sect_id'],
            self.current_sect['position'],
            self.current_sect['contribution']
        )
        self.techniques = techniques

        for tech in techniques:
            status = "✓" if tech.get('can_learn') else "✗"
            self.technique_listbox.insert(
                tk.END,
                f"{status} {tech['technique_name']} [{tech['technique_type']}]"
            )

    def _on_sect_select(self, event=None):
        """门派选择事件"""
        selection = self.sect_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        manager = self._get_sect_manager()
        sects = manager.get_all_sects()

        if 0 <= index < len(sects):
            sect = sects[index]
            info = f"""
名称: {sect['name']}
类型: {sect['sect_type']}
主属性: {sect['main_element']}
位置: {sect['location']}
创始人: {sect['founder']}
成员数: {sect['total_members']}
门派等级: {sect['sect_level']}
声望: {sect['reputation']}

描述: {sect['description']}
"""
            self.sect_info_var.set(info)
            self.selected_sect = sect

    def _on_sect_double_click(self, event=None):
        """门派双击事件"""
        self._on_join_selected_sect()

    def _on_join_sect(self):
        """加入门派按钮"""
        self.notebook.select(self.sects_frame)

    def _on_join_selected_sect(self):
        """加入选中门派"""
        if not hasattr(self, 'selected_sect'):
            messagebox.showinfo("提示", "请先选择一个门派")
            return

        player = self.get_player()
        if not player:
            messagebox.showinfo("提示", "请先创建角色")
            return

        manager = self._get_sect_manager()
        success, msg = manager.join_sect(self.selected_sect['id'], player.stats.name)

        if success:
            self.log(msg, "system")
            self.refresh()
        else:
            messagebox.showinfo("提示", msg)

    def _on_leave_sect(self):
        """退出门派"""
        player = self.get_player()
        if not player:
            return

        if messagebox.askyesno("确认", "确定要退出门派吗？贡献值将保留但职位会丢失。"):
            manager = self._get_sect_manager()
            success, msg = manager.leave_sect(player.stats.name)

            if success:
                self.log(msg, "system")
                self.refresh()
            else:
                messagebox.showinfo("提示", msg)

    def _on_check_promotion(self):
        """查看晋升信息"""
        player = self.get_player()
        if not player:
            return

        manager = self._get_sect_manager()
        info = manager.get_next_promotion_info(player.stats.name)

        if info:
            msg = f"""
当前职位: {info['current_position']}
下一职位: {info['next_position']}

当前贡献: {info['current_contribution']}
需要贡献: {info['required_contribution']}
进度: {int(info['progress']*100)}%

需要境界: 境界{info['required_realm']}
"""
            messagebox.showinfo("晋升信息", msg)
        else:
            messagebox.showinfo("晋升信息", "你已达到最高职位！")

    def _on_task_select(self, event=None):
        """任务选择事件"""
        selection = self.task_listbox.curselection()
        if not selection or not self.tasks:
            return

        index = selection[0]
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            info = f"""
任务: {task['task_name']}
类型: {task['task_type']}
难度: {task['difficulty']}
描述: {task['description']}

奖励:
  贡献: {task['contribution_reward']}
  灵石: {task['spirit_stone_reward']}

要求:
  境界: 境界{task['required_realm']}
  职位: {task['required_position'] or '无要求'}
"""
            self.task_info_var.set(info)
            self.selected_task = task

    def _on_accept_task(self):
        """接受任务"""
        if not hasattr(self, 'selected_task'):
            messagebox.showinfo("提示", "请先选择一个任务")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_sect_manager()
        success, msg = manager.accept_task(self.selected_task['id'], player.stats.name)

        if success:
            self.log(f"接受任务: {self.selected_task['task_name']}", "system")
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showinfo("提示", msg)

    def _on_complete_task(self):
        """完成任务"""
        if not hasattr(self, 'selected_task'):
            messagebox.showinfo("提示", "请先选择一个任务")
            return

        player = self.get_player()
        if not player or not self.current_sect:
            return

        manager = self._get_sect_manager()
        success, msg = manager.complete_task(
            self.selected_task['id'],
            player.stats.name,
            self.current_sect['sect_id'],
            self.selected_task['contribution_reward'],
            self.selected_task['spirit_stone_reward']
        )

        if success:
            self.log(msg, "system")
            messagebox.showinfo("成功", msg)
            self.refresh()
        else:
            messagebox.showinfo("提示", msg)

    def _on_technique_select(self, event=None):
        """功法选择事件"""
        selection = self.technique_listbox.curselection()
        if not selection or not self.techniques:
            return

        index = selection[0]
        if 0 <= index < len(self.techniques):
            tech = self.techniques[index]
            info = f"""
功法: {tech['technique_name']}
类型: {tech['technique_type']}
描述: {tech['description']}

学习要求:
  职位: {tech['required_position'] or '无要求'}
  贡献: {tech['required_contribution']}
  境界: 境界{tech['required_realm']}

状态: {'可学习' if tech.get('can_learn') else '未满足条件'}
"""
            self.technique_info_var.set(info)
            self.selected_technique = tech

    def _on_learn_technique(self):
        """学习功法"""
        if not hasattr(self, 'selected_technique'):
            messagebox.showinfo("提示", "请先选择一个功法")
            return

        player = self.get_player()
        if not player or not self.current_sect:
            return

        tech = self.selected_technique

        # 检查是否可以学习
        manager = self._get_sect_manager()
        can_learn, reason = manager.can_learn_technique(
            tech,
            self.current_sect['position'],
            self.current_sect['contribution'],
            player.stats.realm_level
        )

        if not can_learn:
            messagebox.showinfo("提示", f"无法学习: {reason}")
            return

        # 学习功法
        if messagebox.askyesno("确认", f"确定要学习 {tech['technique_name']} 吗？"):
            success, msg = player.learn_technique(tech['technique_name'])
            if success:
                self.log(f"学会了门派功法: {tech['technique_name']}", "cultivation")
                messagebox.showinfo("成功", f"成功习得 {tech['technique_name']}！")
            else:
                messagebox.showinfo("提示", msg)
