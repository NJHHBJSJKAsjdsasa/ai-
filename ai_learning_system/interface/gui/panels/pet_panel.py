"""
灵兽面板 - 实现灵兽管理、捕捉、培养、进化等功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, List, Dict, Any

from .base_panel import BasePanel
from ..theme import Theme
from config.pet_config import (
    PetType, PetRarity, get_pet_template, get_type_name, get_rarity_color,
    get_pets_by_location, PET_TEMPLATES_DB
)
from game.pet_system import PetSystem, SpiritPet, get_pet_system


class PetPanel(BasePanel):
    """灵兽面板"""
    
    def __init__(self, parent, main_window, **kwargs):
        self.pet_system: Optional[PetSystem] = None
        self.current_pet: Optional[SpiritPet] = None
        self.pet_list: List[SpiritPet] = []
        self.notebook = None
        super().__init__(parent, main_window, **kwargs)
    
    def _setup_ui(self):
        """设置界面"""
        # 初始化灵兽系统
        self.pet_system = get_pet_system()
        
        # 标题
        title = tk.Label(
            self,
            text="🐾 灵兽系统",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 设置标签页样式
        style = ttk.Style()
        style.configure("TNotebook", background=Theme.BG_SECONDARY)
        style.configure("TNotebook.Tab", background=Theme.BG_TERTIARY, foreground=Theme.TEXT_PRIMARY)
        style.map("TNotebook.Tab", background=[("selected", Theme.ACCENT_CYAN)])
        
        # 我的灵兽标签页
        self.my_pets_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.my_pets_frame, text="🐾 我的灵兽")
        self._setup_my_pets_tab()
        
        # 灵兽捕捉标签页
        self.catch_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.catch_frame, text="🎯 捕捉")
        self._setup_catch_tab()
        
        # 灵兽培养标签页
        self.train_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.train_frame, text="💪 培养")
        self._setup_train_tab()
        
        # 灵兽进化标签页
        self.evolve_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.evolve_frame, text="✨ 进化")
        self._setup_evolve_tab()
        
        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_my_pets_tab(self):
        """设置我的灵兽标签页"""
        # 左栏 - 灵兽列表
        left_frame = tk.Frame(self.my_pets_frame, bg=Theme.BG_SECONDARY, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 灵兽列表标题
        list_label = tk.Label(
            left_frame,
            text="灵兽列表",
            **Theme.get_label_style("subtitle")
        )
        list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 灵兽列表框
        self.pet_listbox = tk.Listbox(
            left_frame,
            **Theme.get_listbox_style(),
            height=20
        )
        self.pet_listbox.pack(fill=tk.BOTH, expand=True)
        self.pet_listbox.bind("<<ListboxSelect>>", self._on_pet_select)
        
        # 右栏 - 灵兽详情
        right_frame = tk.Frame(self.my_pets_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 灵兽详情框架
        self.detail_frame = tk.LabelFrame(
            right_frame,
            text="灵兽详情",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        self.detail_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 详情内容
        self.detail_text = tk.Text(
            self.detail_frame,
            **Theme.get_text_style(),
            height=15,
            state=tk.DISABLED
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 操作按钮框架
        btn_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 出战按钮
        self.battle_btn = tk.Button(
            btn_frame,
            text="⚔️ 出战",
            command=self._on_set_battle,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.battle_btn.pack(side=tk.LEFT, padx=5)
        
        # 休息按钮
        self.rest_btn = tk.Button(
            btn_frame,
            text="😴 休息",
            command=self._on_rest,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.rest_btn.pack(side=tk.LEFT, padx=5)
        
        # 恢复按钮
        self.heal_btn = tk.Button(
            btn_frame,
            text="💚 恢复",
            command=self._on_heal,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.heal_btn.pack(side=tk.LEFT, padx=5)
        
        # 放生按钮
        self.release_btn = tk.Button(
            btn_frame,
            text="🕊️ 放生",
            command=self._on_release,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.release_btn.pack(side=tk.LEFT, padx=5)
    
    def _setup_catch_tab(self):
        """设置捕捉标签页"""
        # 地点选择
        location_frame = tk.LabelFrame(
            self.catch_frame,
            text="选择捕捉地点",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        location_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.location_var = tk.StringVar(value="森林")
        locations = ["森林", "火山", "深潭", "悬崖", "草原", "雷霆峡谷", "暗影森林"]
        
        for loc in locations:
            rb = tk.Radiobutton(
                location_frame,
                text=loc,
                variable=self.location_var,
                value=loc,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_TERTIARY,
                font=Theme.get_font(10)
            )
            rb.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 探索按钮
        explore_btn = tk.Button(
            self.catch_frame,
            text="🔍 探索",
            command=self._on_explore,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        explore_btn.pack(pady=10)
        
        # 探索结果区域
        self.explore_result_frame = tk.LabelFrame(
            self.catch_frame,
            text="探索结果",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        self.explore_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.explore_result_var = tk.StringVar(value='点击"探索"按钮开始寻找灵兽...')
        result_label = tk.Label(
            self.explore_result_frame,
            textvariable=self.explore_result_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        result_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # 捕捉按钮（初始隐藏）
        self.catch_btn = tk.Button(
            self.catch_frame,
            text="🎯 捕捉",
            command=self._on_catch,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.catch_btn.pack(pady=10)
        
        # 当前遇到的灵兽
        self.encountered_pet = None
    
    def _setup_train_tab(self):
        """设置培养标签页"""
        # 选择灵兽
        select_frame = tk.Frame(self.train_frame, bg=Theme.BG_SECONDARY)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            select_frame,
            text="选择灵兽: ",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)
        
        self.train_pet_var = tk.StringVar()
        self.train_pet_combo = ttk.Combobox(
            select_frame,
            textvariable=self.train_pet_var,
            state="readonly",
            width=30
        )
        self.train_pet_combo.pack(side=tk.LEFT, padx=5)
        self.train_pet_combo.bind("<<ComboboxSelected>>", self._on_train_pet_select)
        
        # 灵兽信息
        self.train_info_frame = tk.LabelFrame(
            self.train_frame,
            text="灵兽信息",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        self.train_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.train_info_var = tk.StringVar(value="请选择一只灵兽")
        train_info_label = tk.Label(
            self.train_info_frame,
            textvariable=self.train_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        train_info_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # 培养操作
        train_ops_frame = tk.LabelFrame(
            self.train_frame,
            text="培养操作",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        train_ops_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 资质培养按钮
        potential_frame = tk.Frame(train_ops_frame, bg=Theme.BG_SECONDARY)
        potential_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            potential_frame,
            text="资质培养 (消耗灵石): ",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)
        
        potentials = [
            ("攻击", "attack"),
            ("防御", "defense"),
            ("生命", "health"),
            ("速度", "speed")
        ]
        
        for name, attr in potentials:
            btn = tk.Button(
                potential_frame,
                text=name,
                command=lambda a=attr: self._on_train_potential(a),
                font=Theme.get_font(10),
                bg=Theme.BG_TERTIARY,
                fg=Theme.TEXT_PRIMARY,
                relief=tk.FLAT,
                padx=10,
                pady=3
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # 亲密度培养
        intimacy_frame = tk.Frame(train_ops_frame, bg=Theme.BG_SECONDARY)
        intimacy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            intimacy_frame,
            text="亲密度: ",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)
        
        self.intimacy_btn = tk.Button(
            intimacy_frame,
            text="❤️ 互动 (+5亲密度)",
            command=self._on_increase_intimacy,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        self.intimacy_btn.pack(side=tk.LEFT, padx=5)
        
        # 经验获取
        exp_frame = tk.Frame(train_ops_frame, bg=Theme.BG_SECONDARY)
        exp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            exp_frame,
            text="经验: ",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)
        
        self.exp_btn = tk.Button(
            exp_frame,
            text="📈 训练 (+50经验)",
            command=self._on_gain_exp,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        self.exp_btn.pack(side=tk.LEFT, padx=5)
        
        # 培养结果
        self.train_result_var = tk.StringVar(value="")
        train_result_label = tk.Label(
            train_ops_frame,
            textvariable=self.train_result_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("subtitle")
        )
        train_result_label.pack(anchor=tk.W, padx=10, pady=10)
    
    def _setup_evolve_tab(self):
        """设置进化标签页"""
        # 选择灵兽
        select_frame = tk.Frame(self.evolve_frame, bg=Theme.BG_SECONDARY)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            select_frame,
            text="选择灵兽: ",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)
        
        self.evolve_pet_var = tk.StringVar()
        self.evolve_pet_combo = ttk.Combobox(
            select_frame,
            textvariable=self.evolve_pet_var,
            state="readonly",
            width=30
        )
        self.evolve_pet_combo.pack(side=tk.LEFT, padx=5)
        self.evolve_pet_combo.bind("<<ComboboxSelected>>", self._on_evolve_pet_select)
        
        # 进化信息
        self.evolve_info_frame = tk.LabelFrame(
            self.evolve_frame,
            text="进化信息",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        self.evolve_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.evolve_info_var = tk.StringVar(value="请选择一只灵兽查看进化信息")
        evolve_info_label = tk.Label(
            self.evolve_info_frame,
            textvariable=self.evolve_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        evolve_info_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # 进化按钮
        self.evolve_btn = tk.Button(
            self.evolve_frame,
            text="✨ 进化",
            command=self._on_evolve,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_PURPLE,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.evolve_btn.pack(pady=20)
    
    def _on_tab_changed(self, event=None):
        """标签页切换事件"""
        current = self.notebook.index(self.notebook.select())
        if current == 0:  # 我的灵兽
            self._refresh_pet_list()
        elif current == 2:  # 培养
            self._refresh_train_pet_combo()
        elif current == 3:  # 进化
            self._refresh_evolve_pet_combo()
    
    def refresh(self):
        """刷新面板"""
        self._refresh_pet_list()
    
    def _refresh_pet_list(self):
        """刷新灵兽列表"""
        self.pet_listbox.delete(0, tk.END)
        self.pet_list = []
        
        player = self.get_player()
        if not player:
            return
        
        # 获取玩家的灵兽
        self.pet_list = self.pet_system.get_player_pets(player.stats.name)
        
        for pet in self.pet_list:
            template = get_pet_template(pet.pet_template_id)
            rarity_str = template.rarity.value if template else "未知"
            battle_mark = "⚔️ " if pet.is_battle else ""
            display = f"{battle_mark}[{rarity_str}] {pet.name} (Lv.{pet.level})"
            self.pet_listbox.insert(tk.END, display)
    
    def _refresh_train_pet_combo(self):
        """刷新培养页面的灵兽选择"""
        player = self.get_player()
        if not player:
            return
        
        pets = self.pet_system.get_player_pets(player.stats.name)
        pet_names = [f"{p.name} (Lv.{p.level})" for p in pets]
        pet_ids = [p.id for p in pets]
        
        self.train_pet_combo['values'] = pet_names
        self._train_pet_ids = pet_ids  # 保存ID映射
    
    def _refresh_evolve_pet_combo(self):
        """刷新进化页面的灵兽选择"""
        player = self.get_player()
        if not player:
            return
        
        pets = self.pet_system.get_player_pets(player.stats.name)
        pet_names = [f"{p.name} (Lv.{p.level})" for p in pets]
        pet_ids = [p.id for p in pets]
        
        self.evolve_pet_combo['values'] = pet_names
        self._evolve_pet_ids = pet_ids  # 保存ID映射
    
    def _on_pet_select(self, event=None):
        """灵兽选择事件"""
        selection = self.pet_listbox.curselection()
        if not selection or not self.pet_list:
            return
        
        index = selection[0]
        if index < len(self.pet_list):
            self.current_pet = self.pet_list[index]
            self._show_pet_detail(self.current_pet)
    
    def _show_pet_detail(self, pet: SpiritPet):
        """显示灵兽详情"""
        template = get_pet_template(pet.pet_template_id)
        
        detail_text = f"""
【{pet.name}】

基本信息:
  类型: {get_type_name(pet.pet_type)}
  稀有度: {template.rarity.value if template else '未知'}
  等级: {pet.level}
  阶段: {pet.stage}
  经验: {pet.exp}/{pet.exp_to_next}

属性:
  攻击: {pet.attack}
  防御: {pet.defense}
  生命: {pet.health}/{pet.max_health}
  速度: {pet.speed}

资质:
  攻击资质: {pet.attack_potential}/100
  防御资质: {pet.defense_potential}/100
  生命资质: {pet.health_potential}/100
  速度资质: {pet.speed_potential}/100

其他:
  成长率: {pet.growth_rate}
  亲密度: {pet.intimacy}/{pet.max_intimacy}
  状态: {'出战' if pet.is_battle else '休息'}
"""
        
        # 获取技能
        skills = self.pet_system.get_pet_skills(pet.id)
        if skills:
            detail_text += "\n技能:\n"
            for skill in skills:
                detail_text += f"  • {skill['skill_name']} (Lv.{skill['level']})\n"
        
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, detail_text)
        self.detail_text.config(state=tk.DISABLED)
    
    def _on_set_battle(self):
        """设置出战"""
        if not self.current_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        player = self.get_player()
        if not player:
            return
        
        success, message = self.pet_system.set_battle_pet(
            player.stats.name, self.current_pet.id
        )
        
        if success:
            self.log(message, "success")
            self._refresh_pet_list()
        else:
            messagebox.showinfo("提示", message)
    
    def _on_rest(self):
        """休息"""
        if not self.current_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        player = self.get_player()
        if not player:
            return
        
        success, message = self.pet_system.unset_battle_pet(
            player.stats.name, self.current_pet.id
        )
        
        if success:
            self.log(message, "system")
            self._refresh_pet_list()
        else:
            messagebox.showinfo("提示", message)
    
    def _on_heal(self):
        """恢复"""
        if not self.current_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        if self.pet_system.rest_pet(self.current_pet.id):
            self.log(f"{self.current_pet.name} 已恢复", "success")
            self._refresh_pet_list()
            if self.current_pet:
                self._show_pet_detail(self.current_pet)
    
    def _on_release(self):
        """放生"""
        if not self.current_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        if messagebox.askyesno(
            "确认",
            f"确定要放生 {self.current_pet.name} 吗？\n(此操作不可恢复)"
        ):
            success, message = self.pet_system.release_pet(self.current_pet.id)
            if success:
                self.log(message, "system")
                self.current_pet = None
                self._refresh_pet_list()
                self.detail_text.config(state=tk.NORMAL)
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("提示", message)
    
    def _on_explore(self):
        """探索"""
        player = self.get_player()
        if not player:
            return
        
        location = self.location_var.get()
        
        # 模拟遇到灵兽
        from config.pet_config import get_random_pet_by_location
        pet_template = get_random_pet_by_location(location, player.stats.realm_level)
        
        if pet_template:
            self.encountered_pet = pet_template
            self.explore_result_var.set(
                f"在{location}发现了一只灵兽！\n\n"
                f"【{pet_template.rarity.value}】{pet_template.name}\n"
                f"类型: {get_type_name(pet_template.pet_type)}\n"
                f"描述: {pet_template.description}\n\n"
                f"捕捉难度: {'⭐' * int(pet_template.catch_difficulty * 5)}"
            )
            self.catch_btn.config(state=tk.NORMAL)
        else:
            self.encountered_pet = None
            self.explore_result_var.set(f"在{location}探索了一番，但没有发现灵兽...")
            self.catch_btn.config(state=tk.DISABLED)
    
    def _on_catch(self):
        """捕捉"""
        if not self.encountered_pet:
            return
        
        player = self.get_player()
        if not player:
            return
        
        # 模拟战斗后捕捉（假设灵兽血量50%）
        result = self.pet_system.attempt_catch(
            player_id=player.stats.name,
            pet_template=self.encountered_pet,
            pet_health_percent=0.5,
            player_level=player.stats.realm_level,
            player_spiritual_power=player.stats.spiritual_power,
            location=self.location_var.get()
        )
        
        self.explore_result_var.set(
            f"{result.message}\n"
            f"(捕捉成功率: {result.catch_rate*100:.1f}%)"
        )
        
        if result.success:
            self.catch_btn.config(state=tk.DISABLED)
            self.encountered_pet = None
            self.log(result.message, "success")
        else:
            self.log(result.message, "error")
    
    def _on_train_pet_select(self, event=None):
        """培养页面灵兽选择"""
        selection = self.train_pet_combo.current()
        if selection < 0 or not hasattr(self, '_train_pet_ids'):
            return
        
        pet_id = self._train_pet_ids[selection]
        pet = self.pet_system.get_pet(pet_id)
        
        if pet:
            info = f"""
{pet.name} (Lv.{pet.level})
类型: {get_type_name(pet.pet_type)}

当前资质:
  攻击: {pet.attack_potential}/100
  防御: {pet.defense_potential}/100
  生命: {pet.health_potential}/100
  速度: {pet.speed_potential}/100

亲密度: {pet.intimacy}/100
经验: {pet.exp}/{pet.exp_to_next}
"""
            self.train_info_var.set(info)
            self._selected_train_pet = pet
    
    def _on_train_potential(self, attribute: str):
        """培养资质"""
        if not hasattr(self, '_selected_train_pet') or not self._selected_train_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        player = self.get_player()
        if not player:
            return
        
        # 假设玩家有1000灵石
        spirit_stones = getattr(player.stats, 'spirit_stones', 1000)
        
        result = self.pet_system.train_potential(
            self._selected_train_pet.id,
            attribute,
            spirit_stones
        )
        
        if result.success:
            self.train_result_var.set(result.message)
            self.log(result.message, "success")
            # 扣除灵石
            if hasattr(player.stats, 'spirit_stones'):
                player.stats.spirit_stones -= result.cost.get('spirit_stones', 0)
            self._on_train_pet_select()  # 刷新显示
        else:
            messagebox.showinfo("提示", result.message)
    
    def _on_increase_intimacy(self):
        """增加亲密度"""
        if not hasattr(self, '_selected_train_pet') or not self._selected_train_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        if self.pet_system.increase_intimacy(self._selected_train_pet.id, 5):
            self.train_result_var.set("互动成功！亲密度 +5")
            self.log(f"与 {self._selected_train_pet.name} 互动，亲密度 +5", "success")
            self._on_train_pet_select()  # 刷新显示
    
    def _on_gain_exp(self):
        """获得经验"""
        if not hasattr(self, '_selected_train_pet') or not self._selected_train_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        result = self.pet_system.gain_exp(self._selected_train_pet.id, 50)
        
        self.train_result_var.set(result.message)
        if result.level_gained > 0:
            self.log(result.message, "success")
        else:
            self.log(result.message, "system")
        
        self._on_train_pet_select()  # 刷新显示
    
    def _on_evolve_pet_select(self, event=None):
        """进化页面灵兽选择"""
        selection = self.evolve_pet_combo.current()
        if selection < 0 or not hasattr(self, '_evolve_pet_ids'):
            return
        
        pet_id = self._evolve_pet_ids[selection]
        pet = self.pet_system.get_pet(pet_id)
        
        if not pet:
            return
        
        self._selected_evolve_pet = pet
        
        # 检查是否可以进化
        can_evolve, message, next_stage = self.pet_system.can_evolve(pet.id)
        
        if can_evolve and next_stage:
            info = f"""
{pet.name} (Lv.{pet.level}) - 当前阶段: {pet.stage}

下一进化阶段:
  名称: {next_stage.name}
  所需等级: {next_stage.required_level}
  所需亲密度: {next_stage.required_intimacy}
  
所需材料:
"""
            if next_stage.required_items:
                for item, count in next_stage.required_items.items():
                    info += f"    {item} x{count}\n"
            else:
                info += "    无\n"
            
            info += f"\n属性加成:\n"
            for attr, bonus in next_stage.attribute_bonus.items():
                info += f"    {attr}: +{bonus}\n"
            
            if next_stage.new_skills:
                info += f"\n新技能: {', '.join(next_stage.new_skills)}"
            
            self.evolve_info_var.set(info)
            self.evolve_btn.config(state=tk.NORMAL)
        else:
            self.evolve_info_var.set(f"{pet.name} (Lv.{pet.level})\n\n{message}")
            self.evolve_btn.config(state=tk.DISABLED)
    
    def _on_evolve(self):
        """进化"""
        if not hasattr(self, '_selected_evolve_pet') or not self._selected_evolve_pet:
            messagebox.showinfo("提示", "请先选择一只灵兽")
            return
        
        player = self.get_player()
        if not player:
            return
        
        # 模拟玩家背包
        inventory = getattr(player, 'inventory', {})
        inventory_items = {}
        if hasattr(inventory, 'items'):
            inventory_items = {k: v.get('count', 1) for k, v in inventory.items.items()}
        
        result = self.pet_system.evolve_pet(
            self._selected_evolve_pet.id,
            inventory_items
        )
        
        if result.success:
            self.evolve_info_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_evolve_pet_combo()
            self.evolve_btn.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("提示", result.message)
    
    def on_show(self):
        """当面板显示时"""
        self.refresh()
