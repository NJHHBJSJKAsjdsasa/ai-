"""
炼丹面板 - 实现炼丹、丹方学习、材料采集等功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from .base_panel import BasePanel
from ..theme import Theme


class AlchemyPanel(BasePanel):
    """炼丹面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.current_recipe = None
        self.notebook = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="⚗️ 炼丹系统",
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

        # 炼丹标签页
        self.alchemy_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.alchemy_frame, text="⚗️ 炼丹")
        self._setup_alchemy_tab()

        # 丹方标签页
        self.recipe_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.recipe_frame, text="📜 丹方")
        self._setup_recipe_tab()

        # 材料采集标签页
        self.gather_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.gather_frame, text="🌿 采集")
        self._setup_gather_tab()

        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _setup_alchemy_tab(self):
        """设置炼丹标签页"""
        # 左栏 - 丹方列表
        left_frame = tk.Frame(self.alchemy_frame, bg=Theme.BG_SECONDARY, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # 丹方列表
        recipe_label = tk.Label(
            left_frame,
            text="已学丹方",
            **Theme.get_label_style("subtitle")
        )
        recipe_label.pack(anchor=tk.W, pady=(0, 5))

        self.recipe_listbox = tk.Listbox(
            left_frame,
            **Theme.get_listbox_style(),
            height=15
        )
        self.recipe_listbox.pack(fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind("<<ListboxSelect>>", self._on_recipe_select)

        # 右栏 - 炼丹操作
        right_frame = tk.Frame(self.alchemy_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 丹方详情
        detail_frame = tk.LabelFrame(
            right_frame,
            text="丹方详情",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        detail_frame.pack(fill=tk.X, pady=(0, 10))

        self.recipe_detail_var = tk.StringVar(value="选择一个丹方查看详情")
        detail_label = tk.Label(
            detail_frame,
            textvariable=self.recipe_detail_var,
            wraplength=400,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        detail_label.pack(anchor=tk.W, padx=10, pady=10)

        # 材料需求
        material_frame = tk.LabelFrame(
            right_frame,
            text="所需材料",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        material_frame.pack(fill=tk.X, pady=(0, 10))

        self.material_var = tk.StringVar(value="")
        material_label = tk.Label(
            material_frame,
            textvariable=self.material_var,
            wraplength=400,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        material_label.pack(anchor=tk.W, padx=10, pady=10)

        # 炼丹按钮
        btn_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=10)

        alchemy_btn = tk.Button(
            btn_frame,
            text="⚗️ 开始炼丹",
            command=self._on_alchemy,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        alchemy_btn.pack(side=tk.LEFT, padx=5)

        # 炼丹结果
        result_frame = tk.LabelFrame(
            right_frame,
            text="炼丹结果",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.alchemy_result_var = tk.StringVar(value='点击"开始炼丹"按钮开始炼制')
        result_label = tk.Label(
            result_frame,
            textvariable=self.alchemy_result_var,
            wraplength=400,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        result_label.pack(anchor=tk.W, padx=10, pady=10)

    def _setup_recipe_tab(self):
        """设置丹方标签页"""
        # 丹方列表
        list_frame = tk.Frame(self.recipe_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 表头
        headers = ["丹方名称", "类型", "成功率", "境界要求"]
        header_frame = tk.Frame(list_frame, bg=Theme.BG_TERTIARY)
        header_frame.pack(fill=tk.X)
        for i, header in enumerate(headers):
            lbl = tk.Label(
                header_frame,
                text=header,
                width=15 if i == 0 else 12,
                **Theme.get_label_style("subtitle")
            )
            lbl.pack(side=tk.LEFT)

        self.all_recipe_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style(),
            height=15
        )
        self.all_recipe_listbox.pack(fill=tk.BOTH, expand=True)
        self.all_recipe_listbox.bind("<<ListboxSelect>>", self._on_all_recipe_select)

        # 丹方详情
        info_frame = tk.Frame(self.recipe_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.all_recipe_info_var = tk.StringVar(value="选择一个丹方查看详情")
        info_label = tk.Label(
            info_frame,
            textvariable=self.all_recipe_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W)

        # 学习按钮
        btn_frame = tk.Frame(self.recipe_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        learn_btn = tk.Button(
            btn_frame,
            text="📖 学习丹方",
            command=self._on_learn_recipe,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        learn_btn.pack(side=tk.LEFT, padx=5)

    def _setup_gather_tab(self):
        """设置采集标签页"""
        # 采集区域选择
        area_frame = tk.LabelFrame(
            self.gather_frame,
            text="采集区域",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        area_frame.pack(fill=tk.X, padx=10, pady=10)

        self.gather_area_var = tk.StringVar(value="灵草园")
        areas = ["灵草园", "灵矿山", "妖兽森林", "秘境"]
        for area in areas:
            rb = tk.Radiobutton(
                area_frame,
                text=area,
                variable=self.gather_area_var,
                value=area,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_TERTIARY,
                font=Theme.get_font(10)
            )
            rb.pack(side=tk.LEFT, padx=10, pady=5)

        # 采集按钮
        btn_frame = tk.Frame(self.gather_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        gather_btn = tk.Button(
            btn_frame,
            text="🌿 开始采集",
            command=self._on_gather,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        gather_btn.pack(side=tk.LEFT, padx=5)

        # 采集结果
        self.content_area = tk.Frame(self.gather_frame, bg=Theme.BG_SECONDARY)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_label = tk.Label(
            self.content_area,
            text="采集可以获得炼丹材料",
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W)

        # 结果区域
        self.gather_result_var = tk.StringVar(value='点击"开始采集"按钮采集材料')
        result_label = tk.Label(
            self.content_area,
            textvariable=self.gather_result_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        result_label.pack(anchor=tk.W, pady=10)

    def _on_gather(self):
        """采集按钮回调"""
        player = self.get_player()
        if not player:
            return

        area = self.gather_area_var.get()

        # 模拟采集结果
        import random
        materials = {
            "灵草园": ["百年灵草", "千年灵草", "万年灵乳"],
            "灵矿山": ["灵矿石", "金雷竹", "玄铁矿"],
            "妖兽森林": ["妖兽内丹", "妖兽皮毛", "妖兽骨"],
            "秘境": ["万年灵乳", "金雷竹", "高级妖丹"]
        }

        area_materials = materials.get(area, ["普通材料"])
        found = random.choice(area_materials)
        count = random.randint(1, 3)

        # 添加到背包
        player.inventory.add_item(found, count)

        result = f"在{area}采集到 {found} x{count}"
        self.gather_result_var.set(result)
        self.log(result, "success")

    def _on_tab_changed(self, event=None):
        """标签页切换事件"""
        current = self.notebook.index(self.notebook.select())
        if current == 0:  # 炼丹
            self._refresh_recipes()
        elif current == 1:  # 丹方
            self._refresh_all_recipes()

    def refresh(self):
        """刷新面板"""
        self._refresh_recipes()

    def _refresh_recipes(self):
        """刷新已学丹方列表"""
        self.recipe_listbox.delete(0, tk.END)

        # 模拟已学丹方
        recipes = [
            ("回气丹", "恢复类", "80%", "练气期"),
            ("疗伤丹", "恢复类", "75%", "练气期"),
            ("增元丹", "修为类", "60%", "筑基期"),
            ("筑基丹", "突破类", "40%", "练气期"),
        ]

        for recipe in recipes:
            display = f"{recipe[0]:<12} {recipe[1]:<8} {recipe[2]:<8} {recipe[3]}"
            self.recipe_listbox.insert(tk.END, display)

    def _refresh_all_recipes(self):
        """刷新所有丹方列表"""
        self.all_recipe_listbox.delete(0, tk.END)

        # 模拟所有丹方
        recipes = [
            ("回气丹", "恢复类", "80%", "练气期"),
            ("疗伤丹", "恢复类", "75%", "练气期"),
            ("增元丹", "修为类", "60%", "筑基期"),
            ("筑基丹", "突破类", "40%", "练气期"),
            ("结丹期丹药", "突破类", "30%", "筑基期"),
            ("元婴期丹药", "突破类", "20%", "结丹期"),
        ]

        for recipe in recipes:
            display = f"{recipe[0]:<15} {recipe[1]:<10} {recipe[2]:<10} {recipe[3]}"
            self.all_recipe_listbox.insert(tk.END, display)

    def _on_recipe_select(self, event=None):
        """丹方选择事件"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        # 模拟丹方详情
        recipes_info = {
            "回气丹": {
                "desc": "恢复法力的基础丹药",
                "materials": "百年灵草 x1, 灵泉水 x1",
                "effect": "恢复30点法力"
            },
            "疗伤丹": {
                "desc": "治疗伤势的基础丹药",
                "materials": "百年灵草 x1, 妖兽血 x1",
                "effect": "恢复30点生命值"
            },
            "增元丹": {
                "desc": "增加修为的丹药",
                "materials": "千年灵草 x1, 妖兽内丹 x1",
                "effect": "增加100点修为"
            },
            "筑基丹": {
                "desc": "练气期突破筑基期必备丹药",
                "materials": "千年灵草 x3, 妖兽内丹 x2, 灵泉水 x2",
                "effect": "提升突破成功率"
            }
        }

        recipe_names = ["回气丹", "疗伤丹", "增元丹", "筑基丹"]
        if selection[0] < len(recipe_names):
            name = recipe_names[selection[0]]
            info = recipes_info.get(name, {})
            detail = f"【{name}】\n"
            detail += f"描述: {info.get('desc', '')}\n"
            detail += f"效果: {info.get('effect', '')}"
            self.recipe_detail_var.set(detail)
            self.material_var.set(info.get('materials', ''))

    def _on_all_recipe_select(self, event=None):
        """所有丹方选择事件"""
        selection = self.all_recipe_listbox.curselection()
        if not selection:
            return

        # 模拟丹方详情
        self.all_recipe_info_var.set("丹方详情...")

    def _on_alchemy(self):
        """炼丹按钮"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个丹方")
            return

        import random
        success = random.random() < 0.7

        if success:
            self.alchemy_result_var.set("炼丹成功！获得丹药")
            self.log("炼丹成功！", "success")
        else:
            self.alchemy_result_var.set("炼丹失败...材料浪费了")
            self.log("炼丹失败...", "error")

    def _on_learn_recipe(self):
        """学习丹方按钮"""
        messagebox.showinfo("提示", "丹方学习功能需要找到炼丹师NPC学习")

    def on_show(self):
        """当面板显示时"""
        self.refresh()
