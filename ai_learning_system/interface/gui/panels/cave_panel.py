"""
洞府面板 - 实现洞府管理、灵田种植、聚灵阵、护山大阵等功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from .base_panel import BasePanel
from ..theme import Theme

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from game.cave_system import CaveSystem, get_cave_system
from config.cave_config import (
    get_available_crops, get_cave_location, get_cave_level_config,
    get_spirit_array_config, get_defense_array_config,
    CAVE_LOCATIONS, CROPS_DB
)


class CavePanel(BasePanel):
    """洞府面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.cave_system: Optional[CaveSystem] = None
        self.current_cave_info = None
        self.notebook = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🏔️ 洞府系统",
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

        # 洞府信息标签页
        self.info_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.info_frame, text="🏔️ 洞府信息")
        self._setup_info_tab()

        # 灵田标签页
        self.fields_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.fields_frame, text="🌱 灵田")
        self._setup_fields_tab()

        # 升级标签页
        self.upgrade_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.upgrade_frame, text="⬆️ 升级")
        self._setup_upgrade_tab()

        # 创建洞府标签页
        self.create_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.create_frame, text="🏗️ 创建洞府")
        self._setup_create_tab()

        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _setup_info_tab(self):
        """设置洞府信息标签页"""
        # 洞府信息框架
        info_frame = tk.LabelFrame(
            self.info_frame,
            text="洞府信息",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11, bold=True)
        )
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.cave_info_var = tk.StringVar(value="暂无洞府信息")
        info_label = tk.Label(
            info_frame,
            textvariable=self.cave_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 属性框架
        stats_frame = tk.LabelFrame(
            self.info_frame,
            text="洞府属性",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11, bold=True)
        )
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.cave_stats_var = tk.StringVar(value="")
        stats_label = tk.Label(
            stats_frame,
            textvariable=self.cave_stats_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        stats_label.pack(anchor=tk.W, padx=10, pady=10)

        # 刷新按钮
        refresh_btn = tk.Button(
            self.info_frame,
            text="🔄 刷新信息",
            command=self._refresh_cave_info,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        refresh_btn.pack(pady=10)

    def _setup_fields_tab(self):
        """设置灵田标签页"""
        # 灵田列表框架
        fields_list_frame = tk.LabelFrame(
            self.fields_frame,
            text="灵田列表",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11, bold=True)
        )
        fields_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建灵田显示区域
        self.fields_canvas = tk.Canvas(fields_list_frame, bg=Theme.BG_SECONDARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(fields_list_frame, orient="vertical", command=self.fields_canvas.yview)
        self.fields_container = tk.Frame(self.fields_canvas, bg=Theme.BG_SECONDARY)

        self.fields_container.bind(
            "<Configure>",
            lambda e: self.fields_canvas.configure(scrollregion=self.fields_canvas.bbox("all"))
        )

        self.fields_canvas.create_window((0, 0), window=self.fields_container, anchor="nw")
        self.fields_canvas.configure(yscrollcommand=scrollbar.set)

        self.fields_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 操作框架
        action_frame = tk.Frame(self.fields_frame, bg=Theme.BG_SECONDARY)
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        # 作物选择
        crop_label = tk.Label(
            action_frame,
            text="选择作物:",
            **Theme.get_label_style("normal")
        )
        crop_label.pack(side=tk.LEFT, padx=5)

        self.crop_var = tk.StringVar()
        self.crop_combo = ttk.Combobox(
            action_frame,
            textvariable=self.crop_var,
            state="readonly",
            width=15
        )
        self.crop_combo.pack(side=tk.LEFT, padx=5)

        # 种植按钮
        plant_btn = tk.Button(
            action_frame,
            text="🌱 种植",
            command=self._on_plant,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        plant_btn.pack(side=tk.LEFT, padx=5)

        # 收获按钮
        harvest_btn = tk.Button(
            action_frame,
            text="🌾 收获",
            command=self._on_harvest,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        harvest_btn.pack(side=tk.LEFT, padx=5)

        # 施肥按钮
        fertilize_btn = tk.Button(
            action_frame,
            text="💩 施肥",
            command=self._on_fertilize,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_PURPLE,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        fertilize_btn.pack(side=tk.LEFT, padx=5)

        # 结果文本
        self.field_result_var = tk.StringVar(value="选择灵田进行操作")
        result_label = tk.Label(
            self.fields_frame,
            textvariable=self.field_result_var,
            wraplength=500,
            **Theme.get_label_style("normal")
        )
        result_label.pack(pady=10)

    def _setup_upgrade_tab(self):
        """设置升级标签页"""
        # 升级信息框架
        upgrade_info_frame = tk.LabelFrame(
            self.upgrade_frame,
            text="升级信息",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11, bold=True)
        )
        upgrade_info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.upgrade_info_var = tk.StringVar(value="暂无升级信息")
        upgrade_label = tk.Label(
            upgrade_info_frame,
            textvariable=self.upgrade_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        upgrade_label.pack(anchor=tk.W, padx=10, pady=10)

        # 升级按钮框架
        btn_frame = tk.Frame(self.upgrade_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 升级洞府按钮
        self.upgrade_cave_btn = tk.Button(
            btn_frame,
            text="⬆️ 升级洞府",
            command=self._on_upgrade_cave,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.upgrade_cave_btn.pack(side=tk.LEFT, padx=5)

        # 升级聚灵阵按钮
        self.upgrade_spirit_btn = tk.Button(
            btn_frame,
            text="✨ 升级聚灵阵",
            command=self._on_upgrade_spirit,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.upgrade_spirit_btn.pack(side=tk.LEFT, padx=5)

        # 升级护山大阵按钮
        self.upgrade_defense_btn = tk.Button(
            btn_frame,
            text="🛡️ 升级护山大阵",
            command=self._on_upgrade_defense,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.upgrade_defense_btn.pack(side=tk.LEFT, padx=5)

        # 升级结果文本
        self.upgrade_result_var = tk.StringVar(value="")
        upgrade_result_label = tk.Label(
            self.upgrade_frame,
            textvariable=self.upgrade_result_var,
            wraplength=500,
            **Theme.get_label_style("normal")
        )
        upgrade_result_label.pack(pady=10)

    def _setup_create_tab(self):
        """设置创建洞府标签页"""
        # 地点选择框架
        location_frame = tk.LabelFrame(
            self.create_frame,
            text="选择地点",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11, bold=True)
        )
        location_frame.pack(fill=tk.X, padx=10, pady=10)

        # 地点列表
        self.location_var = tk.StringVar()
        self.location_buttons = []

        locations_frame = tk.Frame(location_frame, bg=Theme.BG_SECONDARY)
        locations_frame.pack(fill=tk.X, padx=10, pady=10)

        for i, (loc_id, location) in enumerate(CAVE_LOCATIONS.items()):
            rb = tk.Radiobutton(
                locations_frame,
                text=f"{location.name}\n({location.description[:20]}...)",
                variable=self.location_var,
                value=loc_id,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_TERTIARY,
                font=Theme.get_font(9),
                wraplength=150,
                justify=tk.CENTER
            )
            rb.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="w")
            self.location_buttons.append(rb)

        # 洞府名称
        name_frame = tk.Frame(self.create_frame, bg=Theme.BG_SECONDARY)
        name_frame.pack(fill=tk.X, padx=10, pady=10)

        name_label = tk.Label(
            name_frame,
            text="洞府名称:",
            **Theme.get_label_style("normal")
        )
        name_label.pack(side=tk.LEFT, padx=5)

        self.cave_name_var = tk.StringVar()
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.cave_name_var,
            font=Theme.get_font(10),
            width=30
        )
        name_entry.pack(side=tk.LEFT, padx=5)

        # 创建按钮
        create_btn = tk.Button(
            self.create_frame,
            text="🏗️ 创建洞府",
            command=self._on_create_cave,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        create_btn.pack(pady=20)

        # 创建结果文本
        self.create_result_var = tk.StringVar(value="选择地点并输入名称创建洞府")
        create_result_label = tk.Label(
            self.create_frame,
            textvariable=self.create_result_var,
            wraplength=500,
            **Theme.get_label_style("normal")
        )
        create_result_label.pack(pady=10)

    def _on_tab_changed(self, event=None):
        """标签页切换事件"""
        current = self.notebook.index(self.notebook.select())
        if current == 0:  # 洞府信息
            self._refresh_cave_info()
        elif current == 1:  # 灵田
            self._refresh_fields()
        elif current == 2:  # 升级
            self._refresh_upgrade_info()
        elif current == 3:  # 创建洞府
            self._refresh_create_tab()

    def refresh(self):
        """刷新面板"""
        self._init_cave_system()
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self._refresh_cave_info()
        elif current == 1:
            self._refresh_fields()
        elif current == 2:
            self._refresh_upgrade_info()

    def _init_cave_system(self):
        """初始化洞府系统"""
        if self.cave_system is None:
            self.cave_system = get_cave_system()

    def _refresh_cave_info(self):
        """刷新洞府信息"""
        self._init_cave_system()
        player = self.get_player()
        if not player:
            self.cave_info_var.set("请先登录游戏")
            return

        cave_info = self.cave_system.get_cave_info(player.stats.name)
        if not cave_info:
            self.cave_info_var.set("你还没有洞府，请先在\"创建洞府\"标签页创建洞府")
            self.cave_stats_var.set("")
            return

        self.current_cave_info = cave_info

        # 显示洞府信息
        info_text = f"""
洞府名称: {cave_info['name']}
所在地点: {cave_info['location']}
洞府等级: {cave_info['level']}
聚灵阵: {cave_info['spirit_array']}
护山大阵: {cave_info['defense_array']}
灵田数量: {cave_info['max_fields']}块
        """
        self.cave_info_var.set(info_text)

        # 显示属性
        stats_text = f"""
修炼速度加成: +{cave_info['cultivation_bonus']*100:.0f}%
防御力: {cave_info['defense_power']}
灵力恢复: {cave_info['spirit_recovery']}/天
        """
        self.cave_stats_var.set(stats_text)

    def _refresh_fields(self):
        """刷新灵田列表"""
        self._init_cave_system()
        player = self.get_player()
        if not player:
            return

        # 清空现有显示
        for widget in self.fields_container.winfo_children():
            widget.destroy()

        cave_info = self.cave_system.get_cave_info(player.stats.name)
        if not cave_info:
            no_cave_label = tk.Label(
                self.fields_container,
                text="你还没有洞府",
                **Theme.get_label_style("normal")
            )
            no_cave_label.pack(pady=20)
            return

        # 更新作物选择
        crops = get_available_crops(player.stats.realm_level)
        crop_list = [f"{crop.name}({crop.seed_price}灵石)" for crop in crops]
        self.crop_combo['values'] = crop_list
        if crop_list:
            self.crop_combo.set(crop_list[0])

        # 显示灵田
        self.field_buttons = []
        for field in cave_info['fields']:
            field_frame = tk.Frame(
                self.fields_container,
                bg=Theme.BG_TERTIARY,
                padx=10,
                pady=5
            )
            field_frame.pack(fill=tk.X, padx=5, pady=2)

            # 灵田信息
            field_text = f"灵田 {field['index']+1}: {field['crop']} - {field['stage']}"
            if field['progress']:
                field_text += f" ({field['progress']})"
            if field['is_fertilized']:
                field_text += " [已施肥]"

            field_btn = tk.Button(
                field_frame,
                text=field_text,
                command=lambda idx=field['index']: self._on_field_select(idx),
                font=Theme.get_font(10),
                bg=Theme.BG_TERTIARY,
                fg=Theme.TEXT_PRIMARY,
                activebackground=Theme.ACCENT_CYAN,
                activeforeground=Theme.BG_PRIMARY,
                relief=tk.FLAT,
                anchor=tk.W,
                padx=10,
                pady=5
            )
            field_btn.pack(fill=tk.X)
            self.field_buttons.append((field_btn, field))

        self.selected_field_index = None

    def _refresh_upgrade_info(self):
        """刷新升级信息"""
        self._init_cave_system()
        player = self.get_player()
        if not player:
            self.upgrade_info_var.set("请先登录游戏")
            return

        upgrade_info = self.cave_system.get_upgrade_info(player.stats.name)
        if not upgrade_info:
            self.upgrade_info_var.set("你还没有洞府")
            return

        info_text = ""
        if upgrade_info['cave']:
            cave = upgrade_info['cave']
            info_text += f"【洞府升级】\n"
            info_text += f"当前: {cave['current']} -> {cave['next']}\n"
            info_text += f"消耗: {cave['cost']}灵石\n"
            info_text += f"新增灵田: {cave['new_fields']}块\n"
            info_text += f"修炼加成: +{cave['new_cultivation_bonus']*100:.0f}%\n\n"
            self.upgrade_cave_btn.config(state=tk.NORMAL)
        else:
            info_text += "【洞府升级】\n已达到最高等级\n\n"
            self.upgrade_cave_btn.config(state=tk.DISABLED)

        if upgrade_info['spirit_array']:
            spirit = upgrade_info['spirit_array']
            info_text += f"【聚灵阵升级】\n"
            info_text += f"当前: {spirit['current']} -> {spirit['next']}\n"
            info_text += f"消耗: {spirit['cost']}灵石\n"
            info_text += f"修炼加成: +{spirit['new_cultivation_bonus']*100:.0f}%\n\n"
            self.upgrade_spirit_btn.config(state=tk.NORMAL)
        else:
            info_text += "【聚灵阵升级】\n已达到当前洞府等级上限\n\n"
            self.upgrade_spirit_btn.config(state=tk.DISABLED)

        if upgrade_info['defense_array']:
            defense = upgrade_info['defense_array']
            info_text += f"【护山大阵升级】\n"
            info_text += f"当前: {defense['current']} -> {defense['next']}\n"
            info_text += f"消耗: {defense['cost']}灵石\n"
            info_text += f"防御力: {defense['new_defense_power']}\n"
            info_text += f"驱散概率: {defense['enemy_repel']*100:.0f}%\n"
            self.upgrade_defense_btn.config(state=tk.NORMAL)
        else:
            info_text += "【护山大阵升级】\n已达到当前洞府等级上限\n"
            self.upgrade_defense_btn.config(state=tk.DISABLED)

        self.upgrade_info_var.set(info_text)

    def _refresh_create_tab(self):
        """刷新创建洞府标签页"""
        player = self.get_player()
        if not player:
            return

        # 检查是否已有洞府
        cave_info = self.cave_system.get_cave_info(player.stats.name)
        if cave_info:
            self.create_result_var.set("你已经拥有洞府了，无法再次创建")
            for btn in self.location_buttons:
                btn.config(state=tk.DISABLED)
            return

        # 根据境界启用/禁用地点
        for btn in self.location_buttons:
            btn.config(state=tk.NORMAL)

        # 设置默认地点
        if not self.location_var.get():
            self.location_var.set("newbie_village")

    def _on_field_select(self, field_index):
        """选择灵田"""
        self.selected_field_index = field_index
        self.field_result_var.set(f"已选择灵田 {field_index+1}")

        # 更新按钮样式
        for btn, field in self.field_buttons:
            if field['index'] == field_index:
                btn.config(bg=Theme.ACCENT_CYAN, fg=Theme.BG_PRIMARY)
            else:
                btn.config(bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY)

    def _on_plant(self):
        """种植按钮"""
        if self.selected_field_index is None:
            messagebox.showinfo("提示", "请先选择一块灵田")
            return

        player = self.get_player()
        if not player:
            return

        crop_selection = self.crop_var.get()
        if not crop_selection:
            messagebox.showinfo("提示", "请选择要种植的作物")
            return

        # 解析作物名称
        crop_name = crop_selection.split("(")[0]

        # 查找作物ID
        crop_id = None
        for cid, crop in CROPS_DB.items():
            if crop.name == crop_name:
                crop_id = cid
                break

        if not crop_id:
            messagebox.showerror("错误", "作物数据错误")
            return

        result = self.cave_system.plant_crop(player, self.selected_field_index, crop_id)

        if result.success:
            self.field_result_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_fields()
        else:
            messagebox.showinfo("提示", result.message)

    def _on_harvest(self):
        """收获按钮"""
        if self.selected_field_index is None:
            messagebox.showinfo("提示", "请先选择一块灵田")
            return

        player = self.get_player()
        if not player:
            return

        result = self.cave_system.harvest_crop(player, self.selected_field_index)

        if result.success:
            self.field_result_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_fields()
        else:
            messagebox.showinfo("提示", result.message)

    def _on_fertilize(self):
        """施肥按钮"""
        if self.selected_field_index is None:
            messagebox.showinfo("提示", "请先选择一块灵田")
            return

        player = self.get_player()
        if not player:
            return

        success, message = self.cave_system.fertilize_field(player, self.selected_field_index)

        if success:
            self.field_result_var.set(message)
            self.log(message, "success")
            self._refresh_fields()
        else:
            messagebox.showinfo("提示", message)

    def _on_upgrade_cave(self):
        """升级洞府按钮"""
        player = self.get_player()
        if not player:
            return

        if not messagebox.askyesno("确认", "确定要升级洞府吗？"):
            return

        result = self.cave_system.upgrade_cave(player)

        if result.success:
            self.upgrade_result_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_upgrade_info()
        else:
            messagebox.showinfo("提示", result.message)

    def _on_upgrade_spirit(self):
        """升级聚灵阵按钮"""
        player = self.get_player()
        if not player:
            return

        if not messagebox.askyesno("确认", "确定要升级聚灵阵吗？"):
            return

        result = self.cave_system.upgrade_spirit_array(player)

        if result.success:
            self.upgrade_result_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_upgrade_info()
        else:
            messagebox.showinfo("提示", result.message)

    def _on_upgrade_defense(self):
        """升级护山大阵按钮"""
        player = self.get_player()
        if not player:
            return

        if not messagebox.askyesno("确认", "确定要升级护山大阵吗？"):
            return

        result = self.cave_system.upgrade_defense_array(player)

        if result.success:
            self.upgrade_result_var.set(result.message)
            self.log(result.message, "success")
            self._refresh_upgrade_info()
        else:
            messagebox.showinfo("提示", result.message)

    def _on_create_cave(self):
        """创建洞府按钮"""
        player = self.get_player()
        if not player:
            return

        location_id = self.location_var.get()
        if not location_id:
            messagebox.showinfo("提示", "请选择洞府地点")
            return

        cave_name = self.cave_name_var.get().strip()

        success, message = self.cave_system.create_cave(player, location_id, cave_name)

        if success:
            self.create_result_var.set(message)
            self.log(message, "success")
            messagebox.showinfo("成功", message)
        else:
            messagebox.showinfo("提示", message)

    def on_show(self):
        """当面板显示时"""
        self._init_cave_system()
        self.refresh()
