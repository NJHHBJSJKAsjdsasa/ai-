"""
探索面板 - 与CLI的/探索、/生成、/妖兽命令功能一致
"""
import tkinter as tk
from tkinter import messagebox, ttk
from .base_panel import BasePanel
from ..theme import Theme


class ExplorationPanel(BasePanel):
    """探索面板 - 完整实现CLI的探索功能"""

    def __init__(self, parent, main_window, **kwargs):
        self.exploration_manager = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="🔍 探索",
            **Theme.get_label_style("title")
        )
        title.pack(pady=10)

        # 主内容区
        content_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左栏 - 探索操作
        left_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._setup_exploration_controls(left_frame)
        self._setup_generation_controls(left_frame)

        # 右栏 - 探索结果和妖兽列表
        right_frame = tk.Frame(content_frame, bg=Theme.BG_SECONDARY, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        self._setup_results_area(right_frame)
        self._setup_monsters_list(right_frame)

    def _setup_exploration_controls(self, parent):
        """设置探索控制区"""
        # 探索卡片
        card = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=15, pady=15)
        card.pack(fill=tk.X, pady=10)

        # 标题
        title = tk.Label(
            card,
            text="🌍 区域探索",
            **Theme.get_label_style("subtitle")
        )
        title.pack(anchor=tk.W)

        # 描述
        desc = tk.Label(
            card,
            text="在当前地点进行探索，可能发现物品、NPC、妖兽或新地点",
            wraplength=350,
            **Theme.get_label_style("normal")
        )
        desc.pack(anchor=tk.W, pady=(5, 10))

        # 探索按钮
        explore_btn = tk.Button(
            card,
            text="🔍 开始探索",
            command=self._on_explore,
            font=Theme.get_font(12),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            activebackground="#ffec8b",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        explore_btn.pack(fill=tk.X)

    def _setup_generation_controls(self, parent):
        """设置生成控制区"""
        # 生成卡片
        card = tk.Frame(parent, bg=Theme.BG_TERTIARY, padx=15, pady=15)
        card.pack(fill=tk.X, pady=10)

        # 标题
        title = tk.Label(
            card,
            text="✨ 无限生成",
            **Theme.get_label_style("subtitle")
        )
        title.pack(anchor=tk.W)

        # 描述
        desc = tk.Label(
            card,
            text="手动生成地图、NPC、物品或妖兽",
            wraplength=350,
            **Theme.get_label_style("normal")
        )
        desc.pack(anchor=tk.W, pady=(5, 10))

        # 生成类型选择
        type_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            type_frame,
            text="生成类型:",
            **Theme.get_label_style("normal")
        ).pack(side=tk.LEFT)

        self.gen_type_var = tk.StringVar(value="npc")
        gen_types = [
            ("NPC", "npc"),
            ("物品", "item"),
            ("妖兽", "monster"),
            ("地图", "map"),
            ("功法", "technique"),
        ]

        for text, value in gen_types:
            tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.gen_type_var,
                value=value,
                bg=Theme.BG_TERTIARY,
                fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_SECONDARY
            ).pack(side=tk.LEFT, padx=5)

        # 生成按钮
        generate_btn = tk.Button(
            card,
            text="✨ 生成",
            command=self._on_generate,
            font=Theme.get_font(11),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            activebackground="#80e5ff",
            activeforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        generate_btn.pack(fill=tk.X)

    def _setup_results_area(self, parent):
        """设置探索结果区域"""
        # 结果标题
        title = tk.Label(
            parent,
            text="📜 探索记录",
            **Theme.get_label_style("subtitle")
        )
        title.pack(anchor=tk.W, pady=(0, 10))

        # 结果文本框
        result_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.result_text = tk.Text(
            result_frame,
            state=tk.DISABLED,
            height=10,
            **Theme.get_text_style()
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

        # 配置标签样式
        self.result_text.tag_config("title", foreground=Theme.ACCENT_GOLD, font=Theme.get_font(11, bold=True))
        self.result_text.tag_config("success", foreground=Theme.ACCENT_GREEN, font=Theme.get_font(10))
        self.result_text.tag_config("item", foreground=Theme.ACCENT_CYAN, font=Theme.get_font(10))
        self.result_text.tag_config("npc", foreground=Theme.ACCENT_PURPLE, font=Theme.get_font(10))
        self.result_text.tag_config("monster", foreground=Theme.ACCENT_RED, font=Theme.get_font(10))
        self.result_text.tag_config("normal", foreground=Theme.TEXT_PRIMARY, font=Theme.get_font(10))

    def _setup_monsters_list(self, parent):
        """设置妖兽列表"""
        # 妖兽标题
        title_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        title_frame.pack(fill=tk.X, pady=(10, 5))

        title = tk.Label(
            title_frame,
            text="👹 当前区域妖兽",
            **Theme.get_label_style("subtitle")
        )
        title.pack(side=tk.LEFT)

        # 刷新按钮
        refresh_btn = tk.Button(
            title_frame,
            text="🔄",
            command=self._refresh_monsters,
            font=Theme.get_font(9),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=3,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT)

        # 妖兽列表框
        list_frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.monster_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.monster_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.monster_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.monster_listbox.yview)

        # 绑定双击事件
        self.monster_listbox.bind("<Double-Button-1>", self._on_monster_double_click)

    def _get_exploration_manager(self):
        """获取探索管理器 - 每次创建新的实例以避免线程问题"""
        try:
            from game.exploration_manager import ExplorationManager
            from storage.database import Database
            world = self.get_world()
            if world:
                # 创建新的数据库连接
                db = Database()
                return ExplorationManager(world, db=db, use_llm=False)
        except Exception as e:
            self.log(f"探索管理器初始化失败: {e}", "error")
        return None

    def _add_result(self, message, msg_type="normal"):
        """添加探索结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, f"{message}\n", msg_type)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def _on_explore(self):
        """探索按钮回调 - 使用真实探索系统"""
        player = self.get_player()

        if not player:
            messagebox.showinfo("提示", "玩家未初始化")
            return

        try:
            import random
            from game.generator import InfiniteGenerator
            from storage.database import Database

            generator = InfiniteGenerator(use_llm=False)
            db = Database()

            # 显示结果
            self._add_result(f"\n{'='*40}", "normal")
            self._add_result(f"🌍 探索结果", "title")
            self._add_result(f"{'='*40}", "normal")

            # 探索事件概率
            exploration_events = [
                ("发现新区域", 0.25),
                ("遇到NPC", 0.2),
                ("发现物品", 0.15),
                ("发现功法", 0.15),
                ("遭遇妖兽", 0.15),
                ("一无所获", 0.1),
            ]

            event = random.choices(
                [e[0] for e in exploration_events],
                weights=[e[1] for e in exploration_events]
            )[0]

            if event == "发现新区域":
                # 生成新地图
                new_map = generator.generate_map(target_level=player.stats.realm_level)
                try:
                    db.save_generated_map(new_map.to_dict())
                    self._add_result(f"✓ 发现新区域: {new_map.name}", "success")
                    self._add_result(f"  类型: {new_map.map_type.value}", "normal")
                    self._add_result(f"  描述: {new_map.description[:50]}...", "normal")
                    self.log(f"探索发现新区域: {new_map.name}", "exploration")
                except Exception as e:
                    self._add_result(f"发现新区域但保存失败: {e}", "normal")

            elif event == "遇到NPC":
                # 生成NPC
                npc = generator.generate_npc(location=player.stats.location)
                try:
                    db.save_generated_npc(npc.to_dict())
                    self._add_result(f"✓ 遇到NPC: {npc.full_name}", "npc")
                    self._add_result(f"  性别: {npc.gender}", "normal")
                    self._add_result(f"  职业: {npc.occupation.value}", "normal")
                    self._add_result(f"  性格: {npc.personality.value}", "normal")
                    self.log(f"探索遇到NPC: {npc.full_name}", "exploration")
                except Exception as e:
                    self._add_result(f"遇到NPC但保存失败: {e}", "normal")

            elif event == "发现物品":
                # 生成物品
                item = generator.generate_item()
                try:
                    db.save_generated_item(item.to_dict())
                    self._add_result(f"✓ 发现物品: {item.name}", "item")
                    self._add_result(f"  类型: {item.item_type.value}", "normal")
                    self._add_result(f"  稀有度: {item.rarity.value}", "item")

                    # 添加到背包
                    item_data = {
                        "name": item.name,
                        "description": getattr(item, 'description', f'这是一件{item.rarity.value}的{item.item_type.value}'),
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "value": getattr(item, 'attributes', {}).get('power', 100) * 10,
                        "usable": True,
                    }
                    if hasattr(player, 'inventory') and player.inventory.add_generated_item(item.name, item_data, 1):
                        self._add_result(f"  ✓ 已添加到背包", "success")

                    self.log(f"探索发现物品: {item.name}", "exploration")
                except Exception as e:
                    self._add_result(f"发现物品但保存失败: {e}", "normal")

            elif event == "发现功法":
                # 生成功法
                technique = generator.generate_technique(realm_level=player.stats.realm_level)
                try:
                    # 保存到数据库
                    player_name = getattr(player, 'name', '未知')
                    db.save_generated_technique(technique.to_dict(), discovered_by=player_name)

                    self._add_result(f"✓ 发现功法秘籍: {technique.name}", "item")
                    self._add_result(f"  类型: {technique.technique_type.value}", "normal")
                    self._add_result(f"  稀有度: {technique.rarity.value}", "item")
                    self._add_result(f"  境界要求: {technique.realm_required}", "normal")
                    self._add_result(f"  描述: {technique.description[:50]}...", "normal")

                    # 显示功法效果
                    effects = technique.effects
                    if effects:
                        self._add_result(f"  功法效果:", "success")
                        effect_translations = {
                            'power': '威力', 'attack_bonus': '攻击力加成', 'crit_rate': '暴击率',
                            'spiritual_power_bonus': '灵力加成', 'recovery_rate': '恢复速度',
                            'defense_bonus': '防御加成', 'health_bonus': '生命值加成',
                            'speed_bonus': '速度加成', 'dodge_rate': '闪避率',
                            'mental_strength': '神识强度', 'resistance': '抗性加成',
                            'palm_power_bonus': '掌力加成', 'armor_break': '破甲',
                            'fist_power_bonus': '拳劲加成', 'penetration': '穿透',
                            'finger_power_bonus': '指力加成', 'accuracy': '精准',
                            'leg_power_bonus': '腿劲加成', 'combo': '连击',
                            'special_effect': '特殊效果',
                        }
                        for key, value in list(effects.items())[:3]:  # 只显示前3个效果
                            cn_key = effect_translations.get(key, key)
                            self._add_result(f"    • {cn_key}: {value}", "normal")

                    self._add_result(f"  ✓ 已记录到功法图鉴", "success")

                    self.log(f"探索发现功法: {technique.name}", "exploration")
                except Exception as e:
                    self._add_result(f"发现功法但记录失败: {e}", "normal")

            elif event == "遭遇妖兽":
                # 生成妖兽
                monster_level = max(1, player.stats.realm_level + random.randint(-1, 2))
                monster = generator.generate_monster(level=monster_level, location=player.stats.location)
                try:
                    db.save_generated_monster(monster.to_dict())
                    self._add_result(f"✓ 遭遇妖兽: {monster.name}", "monster")
                    self._add_result(f"  类型: {monster.monster_type.value}", "normal")
                    self._add_result(f"  等级: {monster.level}", "normal")
                    self._add_result(f"  弱点: {monster.weakness}", "normal")
                    self.log(f"探索遭遇妖兽: {monster.name}", "exploration")
                except Exception as e:
                    self._add_result(f"遭遇妖兽但保存失败: {e}", "normal")

            else:  # 一无所获
                self._add_result(f"探索没有发现什么特别的...", "normal")
                self.log("探索完成，但没有发现", "exploration")

            db.close()

            # 刷新妖兽列表
            self._refresh_monsters()

            # 刷新其他面板
            if self.main_window:
                self.main_window.refresh_all_panels()

        except Exception as e:
            messagebox.showerror("错误", f"探索失败: {e}")
            self.log(f"探索失败: {e}", "error")

    def _on_generate(self):
        """生成按钮回调 - 使用真实生成系统"""
        gen_type = self.gen_type_var.get()
        player = self.get_player()

        if not player:
            messagebox.showinfo("提示", "玩家未初始化")
            return

        try:
            from game.generator import InfiniteGenerator
            from storage.database import Database

            generator = InfiniteGenerator(use_llm=False)
            db = Database()

            self._add_result(f"\n{'='*40}", "normal")

            if gen_type == "map":
                # 生成地图
                new_map = generator.generate_map(target_level=player.stats.realm_level)
                db.save_generated_map(new_map.to_dict())

                self._add_result(f"✨ 生成新地图", "title")
                self._add_result(f"名称: {new_map.name}", "normal")
                self._add_result(f"类型: {new_map.map_type.value}", "normal")
                self._add_result(f"等级: {new_map.level}", "normal")
                self._add_result(f"描述: {new_map.description[:50]}...", "normal")
                self.log(f"生成新地图: {new_map.name}", "system")

            elif gen_type == "npc":
                # 生成NPC
                location = player.stats.location
                npc = generator.generate_npc(
                    location=location,
                    target_realm=generator.generate_realm_level(player.stats.realm_level)
                )
                db.save_generated_npc(npc.to_dict())

                self._add_result(f"✨ 生成新NPC", "title")
                self._add_result(f"姓名: {npc.full_name}", "npc")
                self._add_result(f"性别: {npc.gender}", "normal")
                self._add_result(f"年龄: {npc.age}岁", "normal")
                self._add_result(f"职业: {npc.occupation.value}", "normal")
                self._add_result(f"性格: {npc.personality.value}", "normal")
                self.log(f"生成新NPC: {npc.full_name}", "system")

            elif gen_type == "item":
                # 生成物品
                item = generator.generate_item()
                db.save_generated_item(item.to_dict())

                self._add_result(f"✨ 生成新物品", "title")
                self._add_result(f"名称: {item.name}", "item")
                self._add_result(f"类型: {item.item_type.value}", "normal")
                self._add_result(f"稀有度: {item.rarity.value}", "item")
                self._add_result(f"描述: {item.description[:50]}...", "normal")
                self.log(f"生成新物品: {item.name}", "system")

            elif gen_type == "monster":
                # 生成妖兽
                location = player.stats.location
                monster = generator.generate_monster(
                    level=player.stats.realm_level + 1,
                    location=location
                )
                db.save_generated_monster(monster.to_dict())

                self._add_result(f"✨ 生成新妖兽", "title")
                self._add_result(f"名称: {monster.name}", "monster")
                self._add_result(f"类型: {monster.monster_type.value}", "normal")
                self._add_result(f"等级: {monster.level}", "normal")
                self._add_result(f"描述: {monster.description[:50]}...", "normal")
                self._add_result(f"弱点: {monster.weakness}", "normal")
                self.log(f"生成新妖兽: {monster.name}", "system")

            elif gen_type == "technique":
                # 生成功法
                technique = generator.generate_technique(
                    realm_level=player.stats.realm_level
                )

                # 保存到数据库
                player_name = getattr(player, 'name', '未知')
                db.save_generated_technique(technique.to_dict(), discovered_by=player_name)

                self._add_result(f"✨ 生成新功法", "title")
                self._add_result(f"名称: {technique.name}", "item")
                self._add_result(f"类型: {technique.technique_type.value}", "normal")
                self._add_result(f"稀有度: {technique.rarity.value}", "item")
                self._add_result(f"境界要求: {technique.realm_required}", "normal")
                self._add_result(f"描述: {technique.description[:50]}...", "normal")
                self._add_result(f"修炼方法: {technique.cultivation_method}", "normal")
                self._add_result(f"来源: {technique.origin}", "normal")

                # 显示功法效果 - 支持中英文映射
                effects = technique.effects
                if effects:
                    self._add_result(f"功法效果:", "success")
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
                    for key, value in effects.items():
                        cn_key = effect_translations.get(key, key)
                        self._add_result(f"  • {cn_key}: {value}", "normal")

                self._add_result(f"✓ 已保存到功法图鉴", "success")
                self.log(f"生成新功法: {technique.name}", "system")

            db.close()

            # 刷新妖兽列表
            if gen_type == "monster":
                self._refresh_monsters()

        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {e}")
            self.log(f"生成失败: {e}", "error")

    def _refresh_monsters(self):
        """刷新妖兽列表"""
        self.monster_listbox.delete(0, tk.END)

        player = self.get_player()
        if not player:
            return

        try:
            from storage.database import Database
            from config import get_realm_info

            location = player.stats.location
            db = Database()
            monsters = db.get_generated_monsters_by_location(location)
            db.close()

            if monsters:
                for monster in monsters:
                    name = monster.get('name', '未知')
                    realm_level = monster.get('realm_level', 0)
                    realm_info = get_realm_info(realm_level)
                    realm_name = realm_info.name if realm_info else "凡人"
                    monster_type = monster.get('monster_type', '未知')

                    display_text = f"{name} [{realm_name}] - {monster_type}"
                    self.monster_listbox.insert(tk.END, display_text)
            else:
                self.monster_listbox.insert(tk.END, "暂无妖兽")

        except Exception as e:
            self.monster_listbox.insert(tk.END, f"加载失败: {e}")

    def _on_monster_double_click(self, event=None):
        """妖兽双击事件 - 查看详情"""
        selection = self.monster_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        monster_text = self.monster_listbox.get(index)

        if monster_text == "暂无妖兽" or monster_text.startswith("加载失败"):
            return

        # 提取妖兽名称
        monster_name = monster_text.split(" [")[0]

        try:
            from storage.database import Database

            location = self.get_player().stats.location
            db = Database()
            monsters = db.get_generated_monsters_by_location(location)
            db.close()

            # 查找选中的妖兽
            for monster in monsters:
                if monster.get('name') == monster_name:
                    # 显示详情
                    info = f"名称: {monster.get('name', '未知')}\n"
                    info += f"类型: {monster.get('monster_type', '未知')}\n"
                    info += f"等级: {monster.get('level', 0)}\n"
                    info += f"描述: {monster.get('description', '无')}\n"
                    info += f"弱点: {monster.get('weakness', '未知')}\n"
                    info += f"能力: {', '.join(monster.get('abilities', []))}"

                    messagebox.showinfo("妖兽详情", info)
                    break

        except Exception as e:
            messagebox.showerror("错误", f"获取详情失败: {e}")

    def refresh(self):
        """刷新面板"""
        self._refresh_monsters()

    def on_show(self):
        """当面板显示时"""
        super().on_show()
        self._refresh_monsters()
