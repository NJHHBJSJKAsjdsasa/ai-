"""
功法修炼面板 - 使用真实游戏数据
"""
import tkinter as tk
from tkinter import messagebox
from .base_panel import BasePanel
from ..theme import Theme


class TechniquePanel(BasePanel):
    """功法修炼面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.learned_listbox = None
        self.available_listbox = None
        self.tech_info_var = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="📜 功法",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左栏 - 已学功法
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._setup_learned_list(left_frame)

        # 右栏 - 可学习功法和信息
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self._setup_available_list(right_frame)
        self._setup_tech_info(right_frame)

    def _setup_learned_list(self, parent):
        """设置已学功法列表"""
        # 标题
        title_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title = tk.Label(
            title_frame,
            text="✨ 已学功法",
            **Theme.get_label_style("subtitle")
        )
        title.pack(side=tk.LEFT)

        # 功法列表框
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.learned_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.learned_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.learned_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.learned_listbox.yview)

        # 绑定选择事件
        self.learned_listbox.bind("<<ListboxSelect>>", self._on_learned_select)
        self.learned_listbox.bind("<Double-Button-1>", self._on_learned_double_click)

        # 操作按钮
        btn_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        practice_btn = tk.Button(
            btn_frame,
            text="🧘 修炼",
            command=self._on_practice,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        practice_btn.pack(side=tk.LEFT, padx=5)

        detail_btn = tk.Button(
            btn_frame,
            text="📋 详情",
            command=self._on_view_learned_detail,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        detail_btn.pack(side=tk.LEFT, padx=5)

    def _setup_available_list(self, parent):
        """设置可学习功法列表"""
        # 标题
        title_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title = tk.Label(
            title_frame,
            text="📚 可学习功法",
            **Theme.get_label_style("subtitle")
        )
        title.pack(side=tk.LEFT)

        # 功法列表框
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.available_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.available_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.available_listbox.yview)

        # 绑定选择事件
        self.available_listbox.bind("<<ListboxSelect>>", self._on_available_select)
        self.available_listbox.bind("<Double-Button-1>", self._on_available_double_click)

        # 操作按钮
        btn_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        learn_btn = tk.Button(
            btn_frame,
            text="📖 学习",
            command=self._on_learn,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            activebackground="#7ee8c7",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        learn_btn.pack(side=tk.LEFT, padx=5)

        detail_btn = tk.Button(
            btn_frame,
            text="📋 详情",
            command=self._on_view_available_detail,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        detail_btn.pack(side=tk.LEFT, padx=5)

    def _setup_tech_info(self, parent):
        """设置功法信息区域"""
        # 信息标题
        info_title = tk.Label(
            parent,
            text="功法信息",
            **Theme.get_label_style("subtitle")
        )
        info_title.pack(anchor=tk.W, pady=(10, 5))

        # 功法描述
        self.tech_info_var = tk.StringVar(value="选择一个功法查看详情")
        info_label = tk.Label(
            parent,
            textvariable=self.tech_info_var,
            wraplength=300,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))

    def _get_player_techniques(self):
        """获取玩家已学功法 - 使用真实数据"""
        player = self.get_player()
        if player and hasattr(player, 'techniques'):
            tech_record = player.techniques
            # TechniqueLearningRecord 对象，使用 learned_techniques 字典
            if hasattr(tech_record, 'learned_techniques'):
                return tech_record.learned_techniques
        return {}

    def _get_available_techniques(self):
        """获取可学习功法 - 包括配置中的功法和生成的功法"""
        available = []
        player_techs = self._get_player_techniques()
        player_tech_names = set(player_techs.keys())

        # 从配置中读取可学习功法
        try:
            from config.techniques import TECHNIQUES_DB
            for tech_name, tech_data in TECHNIQUES_DB.items():
                if tech_name not in player_tech_names:
                    available.append(tech_data)
        except ImportError:
            pass

        # 从数据库加载生成的功法
        try:
            from storage.database import Database
            db = Database()
            generated_techs = db.get_generated_techniques(is_learned=False)
            db.close()

            for tech_data in generated_techs:
                # 转换为与配置功法相同的格式
                tech_obj = type('GeneratedTechnique', (), {
                    'name': tech_data['name'],
                    'technique_type': tech_data['technique_type'],
                    'realm_required': tech_data['realm_required'],
                    'description': tech_data['description'],
                    'effects': tech_data.get('effects', {}),
                    'rarity': tech_data.get('rarity', '凡阶'),
                    'cultivation_method': tech_data.get('cultivation_method', ''),
                    'origin': tech_data.get('origin', ''),
                    '_is_generated': True,
                    '_generated_id': tech_data['id'],
                })()
                if tech_data['name'] not in player_tech_names:
                    available.append(tech_obj)
        except Exception as e:
            print(f"加载生成功法失败: {e}")

        return available

    def refresh(self):
        """刷新面板 - 使用真实数据"""
        # 刷新已学功法
        self.learned_listbox.delete(0, tk.END)
        learned = self._get_player_techniques()

        for tech_name, tech_data in learned.items():
            name = tech_data.get('name', tech_name)
            level = tech_data.get('level', 1)
            mastery = tech_data.get('mastery', 0.0)

            self.learned_listbox.insert(
                tk.END,
                f"{name} (Lv.{level}) - {int(mastery * 100)}%"
            )

        # 刷新可学习功法
        self.available_listbox.delete(0, tk.END)
        available = self._get_available_techniques()

        for tech in available:
            name = getattr(tech, 'name', '未知')
            realm_req = getattr(tech, 'realm_required', 0)
            tech_type = getattr(tech, 'technique_type', '其他')
            
            # 获取境界名称
            try:
                from config import get_realm_info
                realm_info = get_realm_info(realm_req)
                realm_name = realm_info.name if realm_info else "凡人"
            except:
                realm_name = f"境界{realm_req}"

            self.available_listbox.insert(
                tk.END,
                f"{name} [{tech_type}] - 需要: {realm_name}"
            )

        # 清空功法信息
        self.tech_info_var.set("选择一个功法查看详情")

    def _on_learned_select(self, event=None):
        """已学功法选择事件"""
        selection = self.learned_listbox.curselection()
        if selection:
            index = selection[0]
            techniques = list(self._get_player_techniques().items())
            if 0 <= index < len(techniques):
                tech_name, tech_data = techniques[index]
                self._update_learned_tech_info(tech_name, tech_data)

    def _on_available_select(self, event=None):
        """可学习功法选择事件"""
        selection = self.available_listbox.curselection()
        if selection:
            index = selection[0]
            techniques = self._get_available_techniques()
            if 0 <= index < len(techniques):
                tech = techniques[index]
                self._update_available_tech_info(tech)

    def _update_learned_tech_info(self, tech_name, tech_data):
        """更新已学功法信息显示"""
        info = f"名称: {tech_data.get('name', tech_name)}\n"
        info += f"等级: {tech_data.get('level', 1)}\n"
        info += f"熟练度: {int(tech_data.get('mastery', 0.0) * 100)}%\n"
        
        # 尝试获取功法详细信息
        try:
            from config.techniques import get_technique
            tech_detail = get_technique(tech_name)
            if tech_detail:
                info += f"类型: {getattr(tech_detail, 'technique_type', '未知')}\n"
                info += f"描述: {getattr(tech_detail, 'description', '暂无描述')}\n"
        except:
            pass
        
        self.tech_info_var.set(info)

    def _update_available_tech_info(self, tech):
        """更新可学习功法信息显示"""
        info = f"名称: {getattr(tech, 'name', '未知')}\n"
        info += f"类型: {getattr(tech, 'technique_type', '其他')}\n"
        
        realm_req = getattr(tech, 'realm_required', 0)
        try:
            from config import get_realm_info
            realm_info = get_realm_info(realm_req)
            realm_name = realm_info.name if realm_info else "凡人"
        except:
            realm_name = f"境界{realm_req}"
        
        info += f"学习要求: {realm_name}\n"
        info += f"描述: {getattr(tech, 'description', '暂无描述')}"

        self.tech_info_var.set(info)

    def _get_selected_learned(self):
        """获取选中的已学功法"""
        selection = self.learned_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个已学功法")
            return None

        index = selection[0]
        techniques = list(self._get_player_techniques().items())
        if 0 <= index < len(techniques):
            return techniques[index]
        return None

    def _get_selected_available(self):
        """获取选中的可学习功法"""
        selection = self.available_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个可学习功法")
            return None

        index = selection[0]
        techniques = self._get_available_techniques()
        if 0 <= index < len(techniques):
            return techniques[index]
        return None

    def _on_learned_double_click(self, event=None):
        """已学功法双击事件"""
        self._on_practice()

    def _on_available_double_click(self, event=None):
        """可学习功法双击事件"""
        self._on_learn()

    def _on_practice(self):
        """修炼按钮回调 - 使用真实功法系统"""
        result = self._get_selected_learned()
        if not result:
            return

        tech_name, tech_data = result
        name = tech_data.get('name', tech_name)

        # 获取 TechniqueLearningRecord 并练习
        player = self.get_player()
        if player and hasattr(player, 'techniques'):
            tech_record = player.techniques
            if hasattr(tech_record, 'practice_technique'):
                if tech_record.practice_technique(tech_name, 0.1):
                    level = tech_record.get_technique_level(tech_name)
                    mastery = tech_record.get_mastery(tech_name)
                    self.log(f"你修炼了 {name}，当前等级 Lv.{level}，熟练度 {int(mastery * 100)}%", "cultivation")
                else:
                    self.log(f"修炼 {name} 失败", "system")
            else:
                # 直接修改数据
                old_mastery = tech_data.get('mastery', 0.0)
                tech_data['mastery'] = min(1.0, old_mastery + 0.1)
                
                # 检查升级
                if tech_data['mastery'] >= 1.0:
                    tech_data['mastery'] = 0.0
                    tech_data['level'] = tech_data.get('level', 1) + 1
                    self.log(f"你修炼了 {name}，熟练度已满，功法升级到 Lv.{tech_data['level']}！", "cultivation")
                else:
                    self.log(f"你修炼了 {name}，熟练度增加 (当前: {int(tech_data['mastery'] * 100)}%)", "cultivation")
        
        self.refresh()

    def _on_view_learned_detail(self):
        """查看已学功法详情"""
        result = self._get_selected_learned()
        if not result:
            return

        tech_name, tech_data = result
        
        info = f"名称: {tech_data.get('name', tech_name)}\n"
        info += f"等级: {tech_data.get('level', 1)}\n"
        info += f"熟练度: {int(tech_data.get('mastery', 0.0) * 100)}%\n"
        
        # 尝试获取功法详细信息
        try:
            from config.techniques import get_technique
            tech_detail = get_technique(tech_name)
            if tech_detail:
                info += f"类型: {getattr(tech_detail, 'technique_type', '未知')}\n"
                info += f"属性: {getattr(tech_detail, 'element', '未知')}\n"
                info += f"描述: {getattr(tech_detail, 'description', '暂无描述')}\n"
                
                effects = getattr(tech_detail, 'effects', None)
                if effects:
                    info += "\n效果:\n"
                    for effect in effects:
                        info += f"  - {effect}\n"
        except:
            pass

        messagebox.showinfo("功法详情", info)

    def _on_learn(self):
        """学习按钮回调"""
        tech = self._get_selected_available()
        if not tech:
            return

        name = getattr(tech, 'name', '未知')
        realm_req = getattr(tech, 'realm_required', 0)

        # 检查是否满足学习条件
        player = self.get_player()
        if player:
            current_realm = getattr(player.stats, 'realm_level', 0)
            if current_realm < realm_req:
                try:
                    from config import get_realm_info
                    realm_info = get_realm_info(realm_req)
                    realm_name = realm_info.name if realm_info else f"境界{realm_req}"
                except:
                    realm_name = f"境界{realm_req}"
                messagebox.showinfo("提示", f"你的境界不足，无法学习 {name}\n需要: {realm_name}")
                return

        if messagebox.askyesno("确认", f"确定要学习 {name} 吗？"):
            # 学习功法
            if player and hasattr(player, 'techniques'):
                tech_record = player.techniques
                if hasattr(tech_record, 'learn_technique'):
                    # 准备功法数据
                    technique_data = None
                    if getattr(tech, '_is_generated', False):
                        technique_data = {
                            "technique_type": getattr(tech, 'technique_type', '未知'),
                            "rarity": getattr(tech, 'rarity', '凡阶'),
                            "realm_required": getattr(tech, 'realm_required', 0),
                        }

                    if tech_record.learn_technique(name, technique_data):
                        # 如果是生成的功法，标记为已学习
                        if getattr(tech, '_is_generated', False):
                            try:
                                from storage.database import Database
                                db = Database()
                                db.learn_technique(getattr(tech, '_generated_id', ''))
                                db.close()
                            except Exception as e:
                                print(f"标记功法已学习失败: {e}")

                        self.log(f"你学会了 {name}！", "cultivation")
                        self.refresh()
                    else:
                        self.log(f"学习 {name} 失败，可能已学习过", "system")
                else:
                    self.log(f"开始学习 {name}", "cultivation")

    def _on_view_available_detail(self):
        """查看可学习功法详情"""
        tech = self._get_selected_available()
        if not tech:
            return

        name = getattr(tech, 'name', '未知')
        tech_type = getattr(tech, 'technique_type', '其他')
        realm_req = getattr(tech, 'realm_required', 0)
        description = getattr(tech, 'description', '暂无描述')
        
        try:
            from config import get_realm_info
            realm_info = get_realm_info(realm_req)
            realm_name = realm_info.name if realm_info else f"境界{realm_req}"
        except:
            realm_name = f"境界{realm_req}"

        info = f"名称: {name}\n"
        info += f"类型: {tech_type}\n"
        info += f"属性: {getattr(tech, 'element', '未知')}\n"
        info += f"学习要求: {realm_name}\n"
        info += f"描述: {description}\n"
        
        effects = getattr(tech, 'effects', None)
        if effects:
            info += "\n效果:\n"
            # 效果名称中英文映射
            effect_translations = {
                'power': '威力',
                'attack_bonus': '攻击力加成',
                'crit_rate': '暴击率',
                'spiritual_power_bonus': '灵力加成',
                'recovery_rate': '恢复速度',
                'defense_bonus': '防御加成',
                'health_bonus': '生命值加成',
                'speed_bonus': '速度加成',
                'dodge_rate': '闪避率',
                'mental_strength': '神识强度',
                'resistance': '抗性加成',
                'palm_power_bonus': '掌力加成',
                'armor_break': '破甲',
                'fist_power_bonus': '拳劲加成',
                'penetration': '穿透',
                'finger_power_bonus': '指力加成',
                'accuracy': '精准',
                'leg_power_bonus': '腿劲加成',
                'combo': '连击',
                'special_effect': '特殊效果',
            }
            if isinstance(effects, dict):
                for key, value in effects.items():
                    cn_key = effect_translations.get(key, key)
                    info += f"  - {cn_key}: {value}\n"
            else:
                for effect in effects:
                    info += f"  - {effect}\n"

        messagebox.showinfo("功法详情", info)
