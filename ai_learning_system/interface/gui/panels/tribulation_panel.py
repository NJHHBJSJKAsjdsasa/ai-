"""
天劫面板 - 实现天劫系统的UI界面
"""
import tkinter as tk
from tkinter import messagebox, ttk
from .base_panel import BasePanel
from ..theme import Theme

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from game.tribulation_system import TribulationManager, TribulationResult
from config.tribulation_config import (
    get_tribulation_stage, get_all_tribulation_stages,
    get_preparation_items, TribulationStatus
)


class TribulationPanel(BasePanel):
    """天劫面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.tribulation_manager = None
        self.current_stage = None
        self.preparation_vars = {}
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="⚡ 天劫系统",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 创建主内容区域（左右分栏）
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左栏 - 天劫信息和准备
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_frame.pack_propagate(False)

        self._setup_tribulation_info(left_frame)
        self._setup_preparation_area(left_frame)

        # 右栏 - 战斗区域和历史
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self._setup_battle_area(right_frame)
        self._setup_history_area(right_frame)

    def _setup_tribulation_info(self, parent):
        """设置天劫信息区域"""
        # 信息卡片
        self.info_card = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=15, pady=15)
        self.info_card.pack(fill=tk.X, pady=5)

        # 当前境界
        self.realm_var = tk.StringVar(value="当前境界: 凡人")
        realm_label = tk.Label(
            self.info_card,
            textvariable=self.realm_var,
            **Theme.get_label_style("subtitle")
        )
        realm_label.pack(anchor=tk.W)

        # 天劫状态
        self.status_var = tk.StringVar(value="状态: 未触发")
        status_label = tk.Label(
            self.info_card,
            textvariable=self.status_var,
            **Theme.get_label_style("normal")
        )
        status_label.pack(anchor=tk.W, pady=(5, 0))

        # 下一重天劫信息
        self.next_tribulation_var = tk.StringVar(value="下一重天劫: 小雷劫 (3道)")
        next_label = tk.Label(
            self.info_card,
            textvariable=self.next_tribulation_var,
            **Theme.get_label_style("normal")
        )
        next_label.pack(anchor=tk.W, pady=(5, 0))

        # 触发条件
        self.condition_var = tk.StringVar(value="触发条件: 突破至练气期")
        condition_label = tk.Label(
            self.info_card,
            textvariable=self.condition_var,
            **Theme.get_label_style("dim")
        )
        condition_label.pack(anchor=tk.W, pady=(5, 0))

        # 操作按钮区域
        btn_frame = tk.Frame(self.info_card, bg=Theme.BG_TERTIARY)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # 触发天劫按钮
        self.trigger_btn = tk.Button(
            btn_frame,
            text="⚡ 触发天劫",
            command=self._on_trigger_tribulation,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.trigger_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 查看天劫详情按钮
        self.detail_btn = tk.Button(
            btn_frame,
            text="📜 天劫详情",
            command=self._on_show_tribulation_details,
            font=Theme.get_font(11),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_CYAN,
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.detail_btn.pack(side=tk.LEFT)

    def _setup_preparation_area(self, parent):
        """设置准备区域"""
        # 准备区域框架
        prep_frame = tk.LabelFrame(
            parent,
            text=" 渡劫准备 ",
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11),
            padx=10,
            pady=10
        )
        prep_frame.pack(fill=tk.X, pady=5)

        # 创建标签页
        self.prep_notebook = ttk.Notebook(prep_frame)
        self.prep_notebook.pack(fill=tk.BOTH, expand=True)

        # 法宝页
        self.treasure_frame = tk.Frame(self.prep_notebook, bg=Theme.BG_TERTIARY)
        self.prep_notebook.add(self.treasure_frame, text="法宝")
        self._setup_preparation_list(self.treasure_frame, "treasure")

        # 丹药页
        self.pill_frame = tk.Frame(self.prep_notebook, bg=Theme.BG_TERTIARY)
        self.prep_notebook.add(self.pill_frame, text="丹药")
        self._setup_preparation_list(self.pill_frame, "pill")

        # 阵法页
        self.formation_frame = tk.Frame(self.prep_notebook, bg=Theme.BG_TERTIARY)
        self.prep_notebook.add(self.formation_frame, text="阵法")
        self._setup_preparation_list(self.formation_frame, "formation")

        # 已准备物品显示
        self.prepared_items_var = tk.StringVar(value="已准备: 无")
        prepared_label = tk.Label(
            prep_frame,
            textvariable=self.prepared_items_var,
            **Theme.get_label_style("normal")
        )
        prepared_label.pack(anchor=tk.W, pady=(10, 0))

        # 雷抗显示
        self.resistance_var = tk.StringVar(value="当前雷抗: 0%")
        resistance_label = tk.Label(
            prep_frame,
            textvariable=self.resistance_var,
            fg=Theme.ACCENT_CYAN,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(10, bold=True)
        )
        resistance_label.pack(anchor=tk.W, pady=(5, 0))

    def _setup_preparation_list(self, parent, item_type):
        """设置准备物品列表"""
        # 创建滚动区域
        canvas = tk.Canvas(parent, bg=Theme.BG_TERTIARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Theme.BG_TERTIARY)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=350)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 存储引用以便刷新
        if item_type == "treasure":
            self.treasure_scroll_frame = scroll_frame
        elif item_type == "pill":
            self.pill_scroll_frame = scroll_frame
        elif item_type == "formation":
            self.formation_scroll_frame = scroll_frame

    def _setup_battle_area(self, parent):
        """设置战斗区域"""
        # 战斗框架
        battle_frame = tk.LabelFrame(
            parent,
            text=" 天劫战斗 ",
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11),
            padx=10,
            pady=10
        )
        battle_frame.pack(fill=tk.X, pady=5)

        # 战斗状态
        self.battle_status_var = tk.StringVar(value="等待天劫触发...")
        battle_status = tk.Label(
            battle_frame,
            textvariable=self.battle_status_var,
            **Theme.get_label_style("subtitle")
        )
        battle_status.pack(anchor=tk.W)

        # 当前雷劫信息
        self.current_thunder_var = tk.StringVar(value="当前雷劫: -")
        current_thunder_label = tk.Label(
            battle_frame,
            textvariable=self.current_thunder_var,
            **Theme.get_label_style("normal")
        )
        current_thunder_label.pack(anchor=tk.W, pady=(5, 0))

        # 进度显示
        progress_frame = tk.Frame(battle_frame, bg=Theme.BG_TERTIARY)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        self.thunder_progress_var = tk.StringVar(value="进度: 0/0")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.thunder_progress_var,
            **Theme.get_label_style("normal")
        )
        progress_label.pack(side=tk.LEFT)

        # 生命值显示
        self.battle_health_var = tk.StringVar(value="生命: 0/0")
        health_label = tk.Label(
            progress_frame,
            textvariable=self.battle_health_var,
            fg=Theme.ACCENT_RED,
            bg=Theme.BG_TERTIARY,
            font=Theme.get_font(10, bold=True)
        )
        health_label.pack(side=tk.RIGHT)

        # 进度条
        self.battle_progress = tk.Canvas(
            battle_frame,
            height=20,
            bg=Theme.BG_PRIMARY,
            highlightthickness=0
        )
        self.battle_progress.pack(fill=tk.X, pady=(5, 0))

        # 战斗日志
        self.battle_log = tk.Text(
            battle_frame,
            height=8,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.battle_log.pack(fill=tk.X, pady=(10, 0))

        # 战斗按钮区域
        battle_btn_frame = tk.Frame(battle_frame, bg=Theme.BG_TERTIARY)
        battle_btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.defense_btn = tk.Button(
            battle_btn_frame,
            text="🛡️ 防御",
            command=self._on_defense,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.defense_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.treasure_btn = tk.Button(
            battle_btn_frame,
            text="⚔️ 使用法宝",
            command=self._on_use_treasure,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.treasure_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.begin_battle_btn = tk.Button(
            battle_btn_frame,
            text="⚡ 开始渡劫",
            command=self._on_begin_battle,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            activebackground="#ff6b6b",
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.begin_battle_btn.pack(side=tk.LEFT)

    def _setup_history_area(self, parent):
        """设置历史记录区域"""
        # 历史框架
        history_frame = tk.LabelFrame(
            parent,
            text=" 渡劫历史 ",
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11),
            padx=10,
            pady=10
        )
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 历史列表
        self.history_listbox = tk.Listbox(
            history_frame,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10),
            selectmode=tk.SINGLE,
            height=8
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)

        # 绑定选择事件
        self.history_listbox.bind('<<ListboxSelect>>', self._on_history_select)

    def refresh(self):
        """刷新面板数据"""
        player = self.get_player()
        if not player:
            return

        # 初始化天劫管理器
        if not self.tribulation_manager:
            self.tribulation_manager = TribulationManager(player)

        # 更新境界信息
        realm_level = player.stats.realm_level
        realm_name = player.get_realm_name()
        self.realm_var.set(f"当前境界: {realm_name}")

        # 获取下一重天劫信息
        next_stage = get_tribulation_stage(realm_level)
        if next_stage:
            self.next_tribulation_var.set(
                f"下一重天劫: {next_stage.tribulation_name} ({next_stage.total_thunder}道)"
            )
            self.condition_var.set(f"触发条件: 突破至{next_stage.realm_name}")
        else:
            self.next_tribulation_var.set("下一重天劫: 无")
            self.condition_var.set("触发条件: 已到达最高境界")

        # 检查天劫状态
        tribulation_info = self.tribulation_manager.get_tribulation_info()
        if tribulation_info.get("has_tribulation"):
            status = tribulation_info["status"]
            self.status_var.set(f"状态: {self._get_status_text(status)}")

            # 更新战斗信息
            if status == TribulationStatus.IN_PROGRESS.value:
                self._update_battle_info(tribulation_info)
                self._enable_battle_buttons()
            elif status == TribulationStatus.PREPARING.value:
                self.battle_status_var.set("准备阶段 - 请选择准备物品")
                self.begin_battle_btn.config(state=tk.NORMAL)
                self._disable_battle_buttons()
            else:
                self._disable_all_battle_buttons()
        else:
            self.status_var.set("状态: 未触发")
            self._disable_all_battle_buttons()

        # 刷新准备物品列表
        self._refresh_preparation_lists(realm_level)

        # 刷新历史记录
        self._refresh_history()

        # 更新已准备物品显示
        self._update_prepared_items()

    def _get_status_text(self, status: str) -> str:
        """获取状态文本"""
        status_map = {
            TribulationStatus.PENDING.value: "待触发",
            TribulationStatus.PREPARING.value: "准备中",
            TribulationStatus.IN_PROGRESS.value: "进行中",
            TribulationStatus.SUCCESS.value: "成功",
            TribulationStatus.FAILURE.value: "失败",
            TribulationStatus.DEATH.value: "死亡"
        }
        return status_map.get(status, status)

    def _refresh_preparation_lists(self, realm_level: int):
        """刷新准备物品列表"""
        preparations = self.tribulation_manager.get_available_preparations(realm_level)

        # 刷新法宝列表
        self._clear_frame(self.treasure_scroll_frame)
        for item in preparations.get("treasure", []):
            self._create_preparation_item(self.treasure_scroll_frame, item, "treasure")

        # 刷新丹药列表
        self._clear_frame(self.pill_scroll_frame)
        for item in preparations.get("pill", []):
            self._create_preparation_item(self.pill_scroll_frame, item, "pill")

        # 刷新阵法列表
        self._clear_frame(self.formation_scroll_frame)
        for item in preparations.get("formation", []):
            self._create_preparation_item(self.formation_scroll_frame, item, "formation")

    def _create_preparation_item(self, parent, item, item_type):
        """创建准备物品项"""
        frame = tk.Frame(parent, bg=Theme.BG_TERTIARY, pady=5)
        frame.pack(fill=tk.X)

        # 复选框
        var = tk.BooleanVar(value=False)
        self.preparation_vars[f"{item_type}_{item['name']}"] = var

        cb = tk.Checkbutton(
            frame,
            text=f"{item['name']} ({item['rarity']})",
            variable=var,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            selectcolor=Theme.BG_PRIMARY,
            activebackground=Theme.BG_TERTIARY,
            activeforeground=Theme.TEXT_PRIMARY,
            command=lambda t=item_type, n=item['name']: self._on_preparation_toggle(t, n)
        )
        cb.pack(side=tk.LEFT)

        # 效果描述
        desc = tk.Label(
            frame,
            text=item['description'],
            **Theme.get_label_style("dim")
        )
        desc.pack(side=tk.RIGHT)

    def _on_preparation_toggle(self, item_type: str, item_name: str):
        """准备物品切换事件"""
        var = self.preparation_vars.get(f"{item_type}_{item_name}")
        if var and var.get():
            # 添加准备物品
            result = self.tribulation_manager.add_preparation_item(item_type, item_name)
            if result["success"]:
                self.log(result["message"], "success")
            else:
                self.log(result["message"], "error")
                var.set(False)
        self._update_prepared_items()

    def _update_prepared_items(self):
        """更新已准备物品显示"""
        if not self.tribulation_manager:
            return

        info = self.tribulation_manager.get_tribulation_info()
        if not info.get("has_tribulation"):
            self.prepared_items_var.set("已准备: 无")
            self.resistance_var.set("当前雷抗: 0%")
            return

        preparations = info.get("preparation_items", {})
        items_text = []
        for item_type, items in preparations.items():
            for item in items:
                items_text.append(item['name'])

        if items_text:
            self.prepared_items_var.set(f"已准备: {', '.join(items_text)}")
        else:
            self.prepared_items_var.set("已准备: 无")

        # 更新雷抗
        resistance = info.get("player_resistance", 0)
        self.resistance_var.set(f"当前雷抗: {resistance*100:.1f}%")

    def _update_battle_info(self, info: dict):
        """更新战斗信息"""
        current = info.get("current_thunder", 0)
        total = info.get("total_thunder", 0)
        health = info.get("player_health", 0)
        max_health = info.get("player_max_health", 100)

        self.thunder_progress_var.set(f"进度: {current}/{total}")
        self.battle_health_var.set(f"生命: {health}/{max_health}")

        # 更新进度条
        self._draw_progress_bar(self.battle_progress, current, total, Theme.ACCENT_GOLD)

        # 更新当前雷劫
        history = info.get("thunder_history", [])
        if history:
            last_thunder = history[-1]
            self.current_thunder_var.set(f"当前雷劫: {last_thunder.get('thunder_name', '-')}")
            self._add_battle_log(f"承受了{last_thunder.get('thunder_name')}，"
                                f"受到{last_thunder.get('damage_dealt', 0)}点伤害")

    def _draw_progress_bar(self, canvas, current, maximum, color):
        """绘制进度条"""
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1:
            canvas.after(100, lambda: self._draw_progress_bar(canvas, current, maximum, color))
            return

        # 背景
        canvas.create_rectangle(0, 0, width, height, fill=Theme.BG_PRIMARY, outline="")

        # 进度
        if maximum > 0:
            progress = min(current / maximum, 1.0)
            fill_width = int(width * progress)
            canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def _add_battle_log(self, message: str):
        """添加战斗日志"""
        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.insert(tk.END, f"{message}\n")
        self.battle_log.see(tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def _clear_battle_log(self):
        """清空战斗日志"""
        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.delete(1.0, tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def _enable_battle_buttons(self):
        """启用战斗按钮"""
        self.defense_btn.config(state=tk.NORMAL)
        self.treasure_btn.config(state=tk.NORMAL)
        self.begin_battle_btn.config(state=tk.DISABLED)

    def _disable_battle_buttons(self):
        """禁用战斗按钮"""
        self.defense_btn.config(state=tk.DISABLED)
        self.treasure_btn.config(state=tk.DISABLED)

    def _disable_all_battle_buttons(self):
        """禁用所有战斗按钮"""
        self.defense_btn.config(state=tk.DISABLED)
        self.treasure_btn.config(state=tk.DISABLED)
        self.begin_battle_btn.config(state=tk.DISABLED)

    def _on_trigger_tribulation(self):
        """触发天劫按钮事件"""
        player = self.get_player()
        if not player:
            messagebox.showwarning("警告", "请先创建角色")
            return

        if not self.tribulation_manager:
            self.tribulation_manager = TribulationManager(player)

        realm_level = player.stats.realm_level
        result = self.tribulation_manager.start_tribulation(realm_level)

        if result["success"]:
            self.log(result["message"], "success")
            self._clear_battle_log()
            self._add_battle_log("天劫已触发，请准备渡劫物品")
            self.refresh()
        else:
            messagebox.showinfo("提示", result["message"])

    def _on_begin_battle(self):
        """开始渡劫按钮事件"""
        if not self.tribulation_manager:
            return

        result = self.tribulation_manager.begin_tribulation_battle()
        if result["success"]:
            self.log("天劫战斗开始！", "success")
            self.battle_status_var.set("天劫进行中！")
            self._enable_battle_buttons()
            self._process_next_thunder()
        else:
            messagebox.showwarning("警告", result["message"])

    def _process_next_thunder(self):
        """处理下一道雷劫"""
        if not self.tribulation_manager:
            return

        result = self.tribulation_manager.process_thunder_strike(
            use_defense=False,
            use_treasure=False
        )

        if result.get("finished"):
            self._handle_tribulation_end(result)
        else:
            self.refresh()

    def _on_defense(self):
        """防御按钮事件"""
        if not self.tribulation_manager:
            return

        result = self.tribulation_manager.process_thunder_strike(
            use_defense=True,
            use_treasure=False
        )

        if result.get("finished"):
            self._handle_tribulation_end(result)
        else:
            self.refresh()

    def _on_use_treasure(self):
        """使用法宝按钮事件"""
        if not self.tribulation_manager:
            return

        result = self.tribulation_manager.process_thunder_strike(
            use_defense=False,
            use_treasure=True
        )

        if result.get("finished"):
            self._handle_tribulation_end(result)
        else:
            self.refresh()

    def _handle_tribulation_end(self, result: dict):
        """处理天劫结束"""
        self._disable_all_battle_buttons()

        if result["result"] == TribulationResult.SUCCESS:
            messagebox.showinfo("恭喜", result["message"])
            # 显示奖励
            rewards_text = "基础奖励:\n"
            for attr, value in result.get("base_rewards", {}).items():
                if value > 0:
                    rewards_text += f"  {attr}: +{value}\n"

            special_rewards = result.get("special_rewards", [])
            if special_rewards:
                rewards_text += "\n特殊奖励:\n"
                for reward in special_rewards:
                    rewards_text += f"  {reward['name']}: {reward['description']}\n"

            self._add_battle_log(rewards_text)
            self.log("渡劫成功！获得丰厚奖励！", "success")

        elif result["result"] == TribulationResult.FAILURE:
            messagebox.showerror("失败", result["message"])
            self.log("渡劫失败，受到天劫反噬", "error")

        elif result["result"] == TribulationResult.DEATH:
            messagebox.showerror("死亡", result["message"])
            self.log("渡劫失败，身死道消...", "error")

        self.refresh()

    def _on_show_tribulation_details(self):
        """显示天劫详情"""
        stages = get_all_tribulation_stages()

        detail_window = tk.Toplevel(self)
        detail_window.title("天劫详情")
        detail_window.geometry("500x600")
        detail_window.config(bg=Theme.BG_SECONDARY)

        # 标题
        title = tk.Label(
            detail_window,
            text="⚡ 天劫详情",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 创建滚动区域
        canvas = tk.Canvas(detail_window, bg=Theme.BG_SECONDARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Theme.BG_SECONDARY)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 显示每个阶段
        for level, stage in stages:
            stage_frame = tk.Frame(scroll_frame, bg=Theme.BG_TERTIARY, padx=10, pady=10)
            stage_frame.pack(fill=tk.X, pady=5)

            name_label = tk.Label(
                stage_frame,
                text=f"{stage.tribulation_name} ({stage.realm_name})",
                **Theme.get_label_style("subtitle")
            )
            name_label.pack(anchor=tk.W)

            desc_label = tk.Label(
                stage_frame,
                text=stage.description,
                **Theme.get_label_style("normal")
            )
            desc_label.pack(anchor=tk.W, pady=(5, 0))

            info_text = f"雷劫数: {stage.total_thunder} | 基础威力: {stage.base_power} | 所需雷抗: {stage.required_resistance*100:.0f}%"
            info_label = tk.Label(
                stage_frame,
                text=info_text,
                **Theme.get_label_style("dim")
            )
            info_label.pack(anchor=tk.W, pady=(5, 0))

    def _refresh_history(self):
        """刷新历史记录"""
        if not self.tribulation_manager:
            return

        history = self.tribulation_manager.get_tribulation_history(limit=10)

        self.history_listbox.delete(0, tk.END)
        for record in history:
            status_icon = "✓" if record["final_result"] == "success" else "✗"
            text = f"{status_icon} {record['realm_name']} - {self._get_status_text(record['status'])} " \
                   f"({record['current_thunder']}/{record['total_thunder']})"
            self.history_listbox.insert(tk.END, text)

    def _on_history_select(self, event):
        """历史记录选择事件"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            # 可以在这里显示详细信息

    def _clear_frame(self, frame):
        """清空框架"""
        for widget in frame.winfo_children():
            widget.destroy()

    def on_show(self):
        """当面板显示时调用"""
        self.refresh()
