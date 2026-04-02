"""
战斗面板 - 与CLI功能完全一致
使用真实的CombatSystem进行战斗
"""
import tkinter as tk
from tkinter import messagebox, ttk
from .base_panel import BasePanel
from ..theme import Theme
from ..widgets import AnimatedProgressBar


class CombatPanel(BasePanel):
    """战斗面板 - 完整实现CLI的所有战斗功能"""

    def __init__(self, parent, main_window, **kwargs):
        self.combat_system = None
        self.current_target = None
        self.current_mode = None
        self.in_combat = False
        self.combat_log = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="⚔️ 战斗",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 战斗场景区域
        self._setup_combat_scene(content_frame)

        # 战斗日志
        self._setup_combat_log(content_frame)

        # 操作按钮
        self._setup_action_buttons(content_frame)

    def _setup_combat_scene(self, parent):
        """设置战斗场景"""
        scene_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=20, pady=20)
        scene_frame.pack(fill=tk.X, pady=(0, 10))

        # 玩家信息
        player_frame = tk.Frame(scene_frame, bg=Theme.BG_TERTIARY)
        player_frame.pack(side=tk.LEFT, fill=tk.Y)

        player_title = tk.Label(
            player_frame,
            text="🧑 玩家",
            **Theme.get_label_style("subtitle")
        )
        player_title.pack()

        self.player_hp_var = tk.StringVar(value="HP: 100/100")
        player_hp = tk.Label(
            player_frame,
            textvariable=self.player_hp_var,
            fg=Theme.ACCENT_GREEN,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(11, bold=True)
        )
        player_hp.pack(pady=(5, 0))

        # 玩家血条
        self.player_hp_bar = AnimatedProgressBar(
            player_frame,
            height=15,
            bg_color=Theme.BG_PRIMARY,
            fill_color=Theme.ACCENT_GREEN,
            animation_duration=Theme.ANIMATION_DURATION_FAST
        )
        self.player_hp_bar.pack(pady=(5, 0), fill=tk.X, padx=10)

        # 玩家灵力
        self.player_mp_var = tk.StringVar(value="MP: 50/50")
        player_mp = tk.Label(
            player_frame,
            textvariable=self.player_mp_var,
            fg=Theme.ACCENT_CYAN,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(10)
        )
        player_mp.pack(pady=(5, 0))

        # 玩家灵力条
        self.player_mp_bar = AnimatedProgressBar(
            player_frame,
            height=10,
            bg_color=Theme.BG_PRIMARY,
            fill_color=Theme.ACCENT_CYAN,
            animation_duration=Theme.ANIMATION_DURATION_FAST
        )
        self.player_mp_bar.pack(pady=(5, 0), fill=tk.X, padx=10)

        # VS 标志
        self.vs_label = tk.Label(
            scene_frame,
            text="VS",
            fg=Theme.ACCENT_GOLD,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_title_font(20)
        )
        self.vs_label.pack(side=tk.LEFT, expand=True)

        # 敌人信息
        enemy_frame = tk.Frame(scene_frame, bg=Theme.BG_TERTIARY)
        enemy_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.enemy_name_var = tk.StringVar(value="👹 敌人")
        enemy_title = tk.Label(
            enemy_frame,
            textvariable=self.enemy_name_var,
            **Theme.get_label_style("subtitle")
        )
        enemy_title.pack()

        self.enemy_hp_var = tk.StringVar(value="HP: ???/???")
        enemy_hp = tk.Label(
            enemy_frame,
            textvariable=self.enemy_hp_var,
            fg=Theme.ACCENT_RED,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(11, bold=True)
        )
        enemy_hp.pack(pady=(5, 0))

        # 敌人血条
        self.enemy_hp_bar = AnimatedProgressBar(
            enemy_frame,
            height=15,
            bg_color=Theme.BG_PRIMARY,
            fill_color=Theme.ACCENT_RED,
            animation_duration=Theme.ANIMATION_DURATION_FAST
        )
        self.enemy_hp_bar.pack(pady=(5, 0), fill=tk.X, padx=10)

        # 敌人灵力
        self.enemy_mp_var = tk.StringVar(value="MP: ???/???")
        enemy_mp = tk.Label(
            enemy_frame,
            textvariable=self.enemy_mp_var,
            fg=Theme.ACCENT_CYAN,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(10)
        )
        enemy_mp.pack(pady=(5, 0))

        # 敌人灵力条
        self.enemy_mp_bar = AnimatedProgressBar(
            enemy_frame,
            height=10,
            bg_color=Theme.BG_PRIMARY,
            fill_color=Theme.ACCENT_CYAN,
            animation_duration=Theme.ANIMATION_DURATION_FAST
        )
        self.enemy_mp_bar.pack(pady=(5, 0), fill=tk.X, padx=10)

        # 回合信息
        self.turn_var = tk.StringVar(value="准备战斗")
        turn_label = tk.Label(
            scene_frame,
            textvariable=self.turn_var,
            fg=Theme.ACCENT_GOLD,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(10, bold=True)
        )
        turn_label.pack(side=tk.BOTTOM, pady=(10, 0))

    def _setup_combat_log(self, parent):
        """设置战斗日志"""
        log_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        log_title = tk.Label(
            log_frame,
            text="战斗记录",
            **Theme.get_label_style("subtitle")
        )
        log_title.pack(anchor=tk.W, padx=10, pady=(10, 5))

        # 日志文本框
        text_frame = tk.Frame(log_frame, bg=Theme.BG_TERTIARY)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.combat_log = tk.Text(
            text_frame,
            state=tk.DISABLED,
            height=8,
            **Theme.get_text_style()
        )
        self.combat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.combat_log.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.combat_log.yview)

        # 配置标签样式
        self.combat_log.tag_config("player", foreground=Theme.ACCENT_CYAN, font=Theme.get_font(10, bold=True))
        self.combat_log.tag_config("enemy", foreground=Theme.ACCENT_RED, font=Theme.get_font(10, bold=True))
        self.combat_log.tag_config("system", foreground=Theme.ACCENT_GOLD, font=Theme.get_font(10, bold=True))
        self.combat_log.tag_config("damage", foreground=Theme.ACCENT_RED, font=Theme.get_font(10))
        self.combat_log.tag_config("heal", foreground=Theme.ACCENT_GREEN, font=Theme.get_font(10))
        self.combat_log.tag_config("normal", foreground=Theme.TEXT_PRIMARY, font=Theme.get_font(10))
        self.combat_log.tag_config("skill", foreground=Theme.ACCENT_PURPLE, font=Theme.get_font(10))
        self.combat_log.tag_config("critical", foreground="#ff6b6b", font=Theme.get_font(10, bold=True))

    def _setup_action_buttons(self, parent):
        """设置操作按钮"""
        btn_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X)

        # 发起战斗按钮
        self.combat_btn = tk.Button(
            btn_frame,
            text="⚔️ 发起战斗",
            command=self._on_initiate_combat,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.combat_btn.pack(side=tk.LEFT, padx=5)

        # 切磋按钮
        self.spar_btn = tk.Button(
            btn_frame,
            text="🤝 切磋",
            command=self._on_spar,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            activebackground="#7ee8c7",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.spar_btn.pack(side=tk.LEFT, padx=5)

        # 攻击按钮
        self.attack_btn = tk.Button(
            btn_frame,
            text="⚔️ 攻击",
            command=self._on_attack,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.attack_btn.pack(side=tk.LEFT, padx=5)

        # 技能按钮
        self.skill_btn = tk.Button(
            btn_frame,
            text="✨ 技能",
            command=self._on_skill,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.skill_btn.pack(side=tk.LEFT, padx=5)

        # 逃跑按钮
        self.flee_btn = tk.Button(
            btn_frame,
            text="🏃 逃跑",
            command=self._on_flee,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.TEXT_SECONDARY,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.flee_btn.pack(side=tk.LEFT, padx=5)

        # 处决按钮（战斗胜利后显示）
        self.execute_btn = tk.Button(
            btn_frame,
            text="⚔️ 处决",
            command=self._on_execute,
            font=Theme.get_font(11),
            bg="#8b0000",
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff0000",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.execute_btn.pack(side=tk.LEFT, padx=5)

        # 饶恕按钮（战斗胜利后显示）
        self.spare_btn = tk.Button(
            btn_frame,
            text="🕊️ 饶恕",
            command=self._on_spare,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            activebackground="#7ee8c7",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.spare_btn.pack(side=tk.LEFT, padx=5)

    def _draw_hp_bar(self, canvas, current, maximum, color):
        """绘制血条 - 使用AnimatedProgressBar"""
        if hasattr(canvas, 'set_progress'):
            canvas.set_progress(current, maximum, animate=True)
            if hasattr(canvas, 'set_color'):
                canvas.set_color(color)
        else:
            # 兼容旧代码
            canvas.delete("all")
            width = canvas.winfo_width()
            height = canvas.winfo_height()

            if width <= 1:
                canvas.after(100, lambda: self._draw_hp_bar(canvas, current, maximum, color))
                return

            # 背景
            canvas.create_rectangle(0, 0, width, height, fill=Theme.BG_PRIMARY, outline="")

            # 血量
            if maximum > 0:
                hp_percent = min(current / maximum, 1.0)
                fill_width = int(width * hp_percent)
                canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def _draw_mp_bar(self, canvas, current, maximum, color):
        """绘制灵力条 - 使用AnimatedProgressBar"""
        if hasattr(canvas, 'set_progress'):
            canvas.set_progress(current, maximum, animate=True)
            if hasattr(canvas, 'set_color'):
                canvas.set_color(color)
        else:
            # 兼容旧代码
            canvas.delete("all")
            width = canvas.winfo_width()
            height = canvas.winfo_height()

            if width <= 1:
                canvas.after(100, lambda: self._draw_mp_bar(canvas, current, maximum, color))
                return

            # 背景
            canvas.create_rectangle(0, 0, width, height, fill=Theme.BG_PRIMARY, outline="")

            # 灵力
            if maximum > 0:
                mp_percent = min(current / maximum, 1.0)
                fill_width = int(width * mp_percent)
                canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def _add_combat_log(self, message, msg_type="normal"):
        """添加战斗日志"""
        self.combat_log.config(state=tk.NORMAL)
        self.combat_log.insert(tk.END, f"{message}\n", msg_type)
        self.combat_log.see(tk.END)
        self.combat_log.config(state=tk.DISABLED)

    def _get_target_list(self):
        """获取可战斗目标列表"""
        targets = []

        # 从NPC管理器获取当前地点的NPC
        world = self.get_world()
        player = self.get_player()

        if world and hasattr(world, 'npc_manager') and player:
            location = player.stats.location if hasattr(player, 'stats') else "新手村"
            npcs = world.npc_manager.get_npcs_in_location(location)
            for npc in npcs:
                if hasattr(npc, 'data') and hasattr(npc.data, 'dao_name'):
                    targets.append((npc.data.dao_name, npc))
                elif hasattr(npc, 'name'):
                    targets.append((npc.name, npc))

        return targets

    def _on_initiate_combat(self):
        """发起战斗 - 选择目标和模式"""
        targets = self._get_target_list()

        if not targets:
            messagebox.showinfo("提示", "当前地点没有可战斗的目标")
            return

        # 创建战斗选择对话框
        dialog = tk.Toplevel(self)
        dialog.title("发起战斗")
        dialog.geometry("300x250")
        dialog.config(bg=Theme.BG_SECONDARY)
        dialog.transient(self)
        dialog.grab_set()

        # 目标选择
        tk.Label(
            dialog,
            text="选择目标:",
            **Theme.get_label_style("subtitle")
        ).pack(pady=(10, 5))

        target_var = tk.StringVar()
        target_combo = ttk.Combobox(
            dialog,
            textvariable=target_var,
            values=[t[0] for t in targets],
            state="readonly"
        )
        target_combo.pack(fill=tk.X, padx=20, pady=5)
        if targets:
            target_combo.current(0)

        # 战斗模式选择
        tk.Label(
            dialog,
            text="选择模式:",
            **Theme.get_label_style("subtitle")
        ).pack(pady=(10, 5))

        mode_var = tk.StringVar(value="spar")

        tk.Radiobutton(
            dialog,
            text="🤝 切磋 - 友好比试，不会死亡",
            variable=mode_var,
            value="spar",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            selectcolor=Theme.BG_TERTIARY
        ).pack(anchor=tk.W, padx=20)

        tk.Radiobutton(
            dialog,
            text="⚔️ 死斗 - 生死之战，可能死亡",
            variable=mode_var,
            value="deathmatch",
            bg=Theme.BG_SECONDARY,
            fg=Theme.ACCENT_RED,
            selectcolor=Theme.BG_TERTIARY
        ).pack(anchor=tk.W, padx=20)

        def start_combat():
            target_name = target_var.get()
            mode = mode_var.get()

            # 查找目标对象
            target = None
            for name, obj in targets:
                if name == target_name:
                    target = obj
                    break

            if target:
                dialog.destroy()
                self._start_combat(target, mode)

        # 开始战斗按钮
        tk.Button(
            dialog,
            text="开始战斗",
            command=start_combat,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(pady=20)

    def _on_spar(self):
        """快速切磋 - 使用第一个可用目标"""
        targets = self._get_target_list()
        if not targets:
            messagebox.showinfo("提示", "当前地点没有可切磋的目标")
            return

        # 使用第一个目标进行切磋
        target_name, target = targets[0]
        self._start_combat(target, "spar")

    def _start_combat(self, target, mode):
        """开始战斗 - 使用真实CombatSystem"""
        try:
            from game.combat import CombatSystem, CombatMode, create_player_combat_unit, create_npc_combat_unit

            # 创建战斗系统
            self.combat_system = CombatSystem()
            self.current_target = target
            self.current_mode = mode

            # 创建战斗单位
            player = self.get_player()
            if not player:
                messagebox.showerror("错误", "玩家未初始化")
                return

            player_unit = create_player_combat_unit(player)

            # 创建敌人单位
            if hasattr(target, 'data'):
                enemy_unit = create_npc_combat_unit(target)
                enemy_name = target.data.dao_name if hasattr(target.data, 'dao_name') else "未知敌人"
            else:
                messagebox.showerror("错误", "无效的战斗目标")
                return

            # 确定战斗模式
            combat_mode = CombatMode.SPAR if mode == "spar" else CombatMode.DEATHMATCH

            # 开始战斗
            result = self.combat_system.start_combat(player_unit, enemy_unit, combat_mode)
            self.in_combat = True

            # 更新UI
            mode_text = "【切磋】" if mode == "spar" else "【死斗】"
            mode_color = Theme.ACCENT_GREEN if mode == "spar" else Theme.ACCENT_RED
            self.vs_label.config(text=mode_text, fg=mode_color)
            self.enemy_name_var.set(f"👹 {enemy_name}")

            # 清空日志
            self.combat_log.config(state=tk.NORMAL)
            self.combat_log.delete(1.0, tk.END)
            self.combat_log.config(state=tk.DISABLED)

            self._add_combat_log(f"战斗开始！{'友好切磋' if mode == 'spar' else '生死之战'}", "system")
            self._add_combat_log(f"你对阵 {enemy_name}", "normal")

            # 更新按钮状态
            self._update_button_state("combat")

            # 刷新显示
            self._refresh_combat_ui()

            # 检查谁先手
            if self.combat_system.current_turn_unit != player_unit:
                self._add_combat_log("敌方先手！", "enemy")
                self.after(1000, self._enemy_turn)

        except Exception as e:
            messagebox.showerror("错误", f"战斗初始化失败: {e}")
            self.log(f"战斗初始化失败: {e}", "error")

    def _on_attack(self):
        """执行普通攻击"""
        if not self.combat_system or not self.in_combat:
            return

        try:
            result = self.combat_system.execute_turn("attack")
            self._process_combat_result(result)
        except Exception as e:
            self.log(f"攻击失败: {e}", "error")

    def _on_skill(self):
        """使用技能"""
        if not self.combat_system or not self.in_combat:
            return

        # 获取可用技能
        available_skills = self.combat_system.player.get_available_skills()

        if not available_skills:
            messagebox.showinfo("提示", "没有可用的技能")
            return

        # 创建技能选择对话框
        dialog = tk.Toplevel(self)
        dialog.title("选择技能")
        dialog.geometry("250x200")
        dialog.config(bg=Theme.BG_SECONDARY)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="选择要使用的技能:",
            **Theme.get_label_style("subtitle")
        ).pack(pady=10)

        skill_var = tk.StringVar()
        skill_list = tk.Listbox(dialog, **Theme.get_listbox_style())
        skill_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        for skill in available_skills:
            skill_list.insert(tk.END, f"{skill.name} (消耗{skill.mana_cost}灵力)")

        def use_skill():
            selection = skill_list.curselection()
            if selection:
                skill = available_skills[selection[0]]
                dialog.destroy()

                # 检查灵力
                if not self.combat_system.player.can_use_skill(skill):
                    messagebox.showinfo("提示", "灵力不足或技能冷却中")
                    return

                try:
                    result = self.combat_system.execute_turn("skill", skill.name)
                    self._process_combat_result(result)
                except Exception as e:
                    self.log(f"技能使用失败: {e}", "error")

        tk.Button(
            dialog,
            text="使用",
            command=use_skill,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(pady=10)

    def _on_flee(self):
        """尝试逃跑"""
        if not self.combat_system or not self.in_combat:
            return

        try:
            result = self.combat_system.execute_turn("flee")
            self._process_combat_result(result)
        except Exception as e:
            self.log(f"逃跑失败: {e}", "error")

    def _enemy_turn(self):
        """敌人回合"""
        if not self.combat_system or not self.in_combat:
            return

        try:
            # 敌人自动执行攻击
            result = self.combat_system.execute_turn("attack")
            self._process_combat_result(result)
        except Exception as e:
            self.log(f"敌人回合出错: {e}", "error")

    def _process_combat_result(self, result):
        """处理战斗结果"""
        # 显示战斗日志
        for log in result.combat_log:
            if "暴击" in log:
                self._add_combat_log(log, "critical")
            elif "使用" in log:
                self._add_combat_log(log, "skill")
            elif "恢复" in log or "治疗" in log:
                self._add_combat_log(log, "heal")
            elif "逃跑" in log:
                self._add_combat_log(log, "system")
            elif "造成" in log and "伤害" in log:
                self._add_combat_log(log, "damage")
            else:
                self._add_combat_log(log, "normal")

        # 清空已显示的日志
        self.combat_system.combat_log.clear()

        # 刷新UI
        self._refresh_combat_ui()

        # 检查战斗是否结束
        from game.combat import CombatStatus

        if result.status != CombatStatus.ONGOING:
            self._handle_combat_end(result)
        else:
            # 继续战斗
            self.turn_var.set(f"第 {self.combat_system.turn} 回合")

            # 检查是否是玩家回合
            if self.combat_system.current_turn_unit == self.combat_system.player:
                self._add_combat_log("→ 你的回合", "player")
            else:
                self._add_combat_log("→ 敌方回合", "enemy")
                self.after(1000, self._enemy_turn)

    def _refresh_combat_ui(self):
        """刷新战斗UI"""
        if not self.combat_system:
            return

        player = self.combat_system.player
        enemy = self.combat_system.enemy

        # 更新玩家信息
        self.player_hp_var.set(f"HP: {player.health}/{player.max_health}")
        self.player_mp_var.set(f"MP: {player.mana}/{player.max_mana}")
        self._draw_hp_bar(self.player_hp_bar, player.health, player.max_health, Theme.ACCENT_GREEN)
        self._draw_mp_bar(self.player_mp_bar, player.mana, player.max_mana, Theme.ACCENT_CYAN)

        # 更新敌人信息
        self.enemy_hp_var.set(f"HP: {enemy.health}/{enemy.max_health}")
        self.enemy_mp_var.set(f"MP: {enemy.mana}/{enemy.max_mana}")
        self._draw_hp_bar(self.enemy_hp_bar, enemy.health, enemy.max_health, Theme.ACCENT_RED)
        self._draw_mp_bar(self.enemy_mp_bar, enemy.mana, enemy.max_mana, Theme.ACCENT_CYAN)

    def _handle_combat_end(self, result):
        """处理战斗结束"""
        from game.combat import CombatStatus, CombatMode

        self.in_combat = False

        if result.status == CombatStatus.PLAYER_WIN:
            self._add_combat_log("🎉 你获得了胜利！", "system")

            if result.mode == CombatMode.DEATHMATCH:
                # 死斗胜利，显示处决/饶恕选项
                self._add_combat_log("敌人已败，请选择处决或饶恕", "system")
                self._update_button_state("execution")

                # 显示奖励
                self._add_combat_log(f"获得经验: +{result.exp_reward}", "heal")
                self._add_combat_log(f"获得灵石: +{result.spirit_stones_reward}", "system")

                # 应用奖励
                player = self.get_player()
                if player:
                    if hasattr(player, 'gain_exp'):
                        player.gain_exp(result.exp_reward)
                    if hasattr(player, 'add_spirit_stones'):
                        player.add_spirit_stones(result.spirit_stones_reward)
            else:
                # 切磋结束
                self._add_combat_log(f"获得经验: +{result.exp_reward}", "heal")
                self._update_button_state("end")

                player = self.get_player()
                if player and hasattr(player, 'gain_exp'):
                    player.gain_exp(result.exp_reward)

        elif result.status == CombatStatus.ENEMY_WIN:
            self._add_combat_log("💀 你战败了...", "damage")

            if result.mode == CombatMode.DEATHMATCH:
                self._add_combat_log("死斗失败，角色死亡！", "critical")
                messagebox.showinfo("战斗结束", "你在死斗中阵亡！")

                # 恢复部分生命值
                player = self.get_player()
                if player and hasattr(player, 'stats'):
                    player.stats.health = player.stats.max_health // 2
            else:
                messagebox.showinfo("战斗结束", "切磋失败！")

            self._update_button_state("end")

        elif result.status == CombatStatus.FLED:
            self._add_combat_log("🏃 你成功逃离了战斗！", "system")
            self._update_button_state("end")

        self.turn_var.set("战斗结束")
        self.vs_label.config(text="战斗结束", fg=Theme.TEXT_SECONDARY)

    def _on_execute(self):
        """处决敌人"""
        if not self.current_target:
            return

        try:
            from game.execution_system import execution_system

            result = execution_system.execute_npc(self.current_target, self.get_player())

            if result.success:
                self._add_combat_log(f"✓ {result.message}", "system")

                if result.karma_change > 0:
                    self._add_combat_log(f"☯ 业力值 +{result.karma_change}（替天行道）", "heal")
                elif result.karma_change < 0:
                    self._add_combat_log(f"☯ 业力值 {result.karma_change}（滥杀无辜）", "damage")
            else:
                self._add_combat_log(f"处决失败: {result.message}", "damage")

            self._update_button_state("end")

        except Exception as e:
            self.log(f"处决失败: {e}", "error")

    def _on_spare(self):
        """饶恕敌人"""
        if not self.current_target:
            return

        try:
            from game.execution_system import execution_system

            result = execution_system.spare_npc(self.current_target, self.get_player())

            if result.success:
                self._add_combat_log(f"✓ {result.message}", "system")

                if result.karma_change > 20:
                    self._add_combat_log(f"☯ 业力值 +{result.karma_change}（慈悲为怀）", "heal")
                elif result.karma_change > 0:
                    self._add_combat_log(f"☯ 业力值 +{result.karma_change}（心存善念）", "heal")
            else:
                self._add_combat_log(f"饶恕失败: {result.message}", "damage")

            self._update_button_state("end")

        except Exception as e:
            self.log(f"饶恕失败: {e}", "error")

    def _update_button_state(self, state):
        """更新按钮状态"""
        if state == "combat":
            # 战斗中
            self.combat_btn.config(state=tk.DISABLED)
            self.spar_btn.config(state=tk.DISABLED)
            self.attack_btn.config(state=tk.NORMAL)
            self.skill_btn.config(state=tk.NORMAL)
            self.flee_btn.config(state=tk.NORMAL)
            self.execute_btn.config(state=tk.DISABLED)
            self.spare_btn.config(state=tk.DISABLED)
        elif state == "execution":
            # 等待处决/饶恕选择
            self.combat_btn.config(state=tk.DISABLED)
            self.spar_btn.config(state=tk.DISABLED)
            self.attack_btn.config(state=tk.DISABLED)
            self.skill_btn.config(state=tk.DISABLED)
            self.flee_btn.config(state=tk.DISABLED)
            self.execute_btn.config(state=tk.NORMAL)
            self.spare_btn.config(state=tk.NORMAL)
        else:
            # 战斗结束/初始状态
            self.combat_btn.config(state=tk.NORMAL)
            self.spar_btn.config(state=tk.NORMAL)
            self.attack_btn.config(state=tk.DISABLED)
            self.skill_btn.config(state=tk.DISABLED)
            self.flee_btn.config(state=tk.DISABLED)
            self.execute_btn.config(state=tk.DISABLED)
            self.spare_btn.config(state=tk.DISABLED)

    def refresh(self):
        """刷新面板"""
        if self.in_combat and self.combat_system:
            self._refresh_combat_ui()

    def on_show(self):
        """当面板显示时"""
        super().on_show()
        # 如果没有在战斗中，重置状态
        if not self.in_combat:
            self._update_button_state("end")
            self.vs_label.config(text="VS", fg=Theme.ACCENT_GOLD)
            self.enemy_name_var.set("👹 敌人")
            self.turn_var.set("准备战斗")
