"""
社交面板 - 管理社交关系相关功能
包括好友、道侣、师徒、仇敌等
"""
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from .base_panel import BasePanel
from ..theme import Theme


class SocialPanel(BasePanel):
    """社交面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.social_manager = None
        self.current_dao_lv = None
        self.current_master = None
        self.current_apprentices = []
        self.current_friends = []
        self.current_enemies = []
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self,
            text="💕 社交",
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
        self._create_friends_tab()
        self._create_dao_lv_tab()
        self._create_master_apprentice_tab()
        self._create_enemies_tab()

    def _create_overview_tab(self):
        """创建概览标签页"""
        self.overview_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.overview_frame, text="概览")

        # 社交信息区域
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

        # 加成信息区域
        self.bonus_frame = tk.LabelFrame(
            self.overview_frame,
            text="社交加成",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11)
        )
        self.bonus_frame.pack(fill=tk.X, padx=10, pady=10)

        self.bonus_text = tk.Text(
            self.bonus_frame,
            wrap=tk.WORD,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=6
        )
        self.bonus_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.bonus_text.config(state=tk.DISABLED)

    def _create_friends_tab(self):
        """创建好友标签页"""
        self.friends_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.friends_frame, text="好友")

        # 好友列表
        list_frame = tk.Frame(self.friends_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.friend_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.friend_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.friend_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.friend_listbox.yview)

        self.friend_listbox.bind("<<ListboxSelect>>", self._on_friend_select)

        # 好友信息
        self.friend_info_var = tk.StringVar(value="选择一个好友查看详情")
        info_label = tk.Label(
            self.friends_frame,
            textvariable=self.friend_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 操作按钮
        btn_frame = tk.Frame(self.friends_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.add_friend_btn = tk.Button(
            btn_frame,
            text="➕ 添加好友",
            command=self._on_add_friend,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.add_friend_btn.pack(side=tk.LEFT, padx=5)

        self.chat_btn = tk.Button(
            btn_frame,
            text="💬 交谈",
            command=self._on_chat_friend,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.chat_btn.pack(side=tk.LEFT, padx=5)

        self.gift_btn = tk.Button(
            btn_frame,
            text="🎁 赠送礼物",
            command=self._on_gift_friend,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.gift_btn.pack(side=tk.LEFT, padx=5)

        self.remove_friend_btn = tk.Button(
            btn_frame,
            text="❌ 删除好友",
            command=self._on_remove_friend,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.remove_friend_btn.pack(side=tk.LEFT, padx=5)

        # 第二行按钮
        btn_frame2 = tk.Frame(self.friends_frame, bg=Theme.BG_SECONDARY)
        btn_frame2.pack(fill=tk.X, padx=10, pady=5)

        self.duel_btn = tk.Button(
            btn_frame2,
            text="⚔️ 切磋",
            command=self._on_duel_friend,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_ORANGE,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.duel_btn.pack(side=tk.LEFT, padx=5)

        self.discuss_btn = tk.Button(
            btn_frame2,
            text="📖 论道",
            command=self._on_discuss_dao,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_PURPLE,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.discuss_btn.pack(side=tk.LEFT, padx=5)

        self.cultivate_btn = tk.Button(
            btn_frame2,
            text="🧘 共修",
            command=self._on_cultivate_together,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_CYAN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.cultivate_btn.pack(side=tk.LEFT, padx=5)

    def _create_dao_lv_tab(self):
        """创建道侣标签页"""
        self.dao_lv_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.dao_lv_frame, text="道侣")

        # 道侣信息区域
        self.dao_lv_info_frame = tk.LabelFrame(
            self.dao_lv_frame,
            text="道侣信息",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11)
        )
        self.dao_lv_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dao_lv_info_text = tk.Text(
            self.dao_lv_info_frame,
            wrap=tk.WORD,
            font=Theme.get_font(11),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            height=12
        )
        self.dao_lv_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.dao_lv_info_text.config(state=tk.DISABLED)

        # 操作按钮
        btn_frame = tk.Frame(self.dao_lv_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.propose_btn = tk.Button(
            btn_frame,
            text="💍 结为道侣",
            command=self._on_propose_dao_lv,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_PINK,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.propose_btn.pack(side=tk.LEFT, padx=5)

        self.dual_cultivation_btn = tk.Button(
            btn_frame,
            text="☯️ 双修",
            command=self._on_dual_cultivation,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_PURPLE,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.dual_cultivation_btn.pack(side=tk.LEFT, padx=5)

        self.divorce_btn = tk.Button(
            btn_frame,
            text="💔 解除道侣",
            command=self._on_divorce,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.divorce_btn.pack(side=tk.LEFT, padx=5)

        # 加成说明
        bonus_frame = tk.LabelFrame(
            self.dao_lv_frame,
            text="道侣加成",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10)
        )
        bonus_frame.pack(fill=tk.X, padx=10, pady=10)

        bonus_text = """
结为道侣后可获得以下加成：
• 修炼速度 +15%
• 经验获取 +20%
• 突破成功率 +10%
• 双修可获得大量修为
        """
        bonus_label = tk.Label(
            bonus_frame,
            text=bonus_text,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        bonus_label.pack(anchor=tk.W, padx=10, pady=5)

    def _create_master_apprentice_tab(self):
        """创建师徒标签页"""
        self.ma_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.ma_frame, text="师徒")

        # 师父信息区域
        master_frame = tk.LabelFrame(
            self.ma_frame,
            text="我的师父",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11)
        )
        master_frame.pack(fill=tk.X, padx=10, pady=5)

        self.master_info_text = tk.Text(
            master_frame,
            wrap=tk.WORD,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=6
        )
        self.master_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.master_info_text.config(state=tk.DISABLED)

        # 徒弟列表区域
        apprentice_frame = tk.LabelFrame(
            self.ma_frame,
            text="我的徒弟",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(11)
        )
        apprentice_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        list_frame = tk.Frame(apprentice_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.apprentice_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.apprentice_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.apprentice_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.apprentice_listbox.yview)

        self.apprentice_listbox.bind("<<ListboxSelect>>", self._on_apprentice_select)

        # 操作按钮
        btn_frame = tk.Frame(self.ma_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.accept_apprentice_btn = tk.Button(
            btn_frame,
            text="📜 收徒",
            command=self._on_accept_apprentice,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.accept_apprentice_btn.pack(side=tk.LEFT, padx=5)

        self.teach_btn = tk.Button(
            btn_frame,
            text="📖 传授功法",
            command=self._on_teach_technique,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GOLD,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.teach_btn.pack(side=tk.LEFT, padx=5)

        self.leave_master_btn = tk.Button(
            btn_frame,
            text="🚪 离开师门",
            command=self._on_leave_master,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.leave_master_btn.pack(side=tk.LEFT, padx=5)

        # 加成说明
        bonus_frame = tk.LabelFrame(
            self.ma_frame,
            text="师徒加成",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10)
        )
        bonus_frame.pack(fill=tk.X, padx=10, pady=5)

        bonus_text = """
徒弟加成：修炼速度 +10%，经验获取 +15%，功法学习成功率 +20%
师父加成：声望获取 +5%，业力获取 +10%，每次传授获得修为 +50
        """
        bonus_label = tk.Label(
            bonus_frame,
            text=bonus_text,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        bonus_label.pack(anchor=tk.W, padx=10, pady=5)

    def _create_enemies_tab(self):
        """创建仇敌标签页"""
        self.enemies_frame = tk.Frame(self.notebook, bg=Theme.BG_SECONDARY)
        self.notebook.add(self.enemies_frame, text="仇敌")

        # 仇敌列表
        list_frame = tk.Frame(self.enemies_frame, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.enemy_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style()
        )
        self.enemy_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.enemy_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.enemy_listbox.yview)

        self.enemy_listbox.bind("<<ListboxSelect>>", self._on_enemy_select)

        # 仇敌信息
        self.enemy_info_var = tk.StringVar(value="选择一个仇敌查看详情")
        info_label = tk.Label(
            self.enemies_frame,
            textvariable=self.enemy_info_var,
            wraplength=500,
            justify=tk.LEFT,
            **Theme.get_label_style("normal")
        )
        info_label.pack(anchor=tk.W, padx=10, pady=10)

        # 操作按钮
        btn_frame = tk.Frame(self.enemies_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.add_enemy_btn = tk.Button(
            btn_frame,
            text="➕ 添加仇敌",
            command=self._on_add_enemy,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_RED,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.add_enemy_btn.pack(side=tk.LEFT, padx=5)

        self.revenge_btn = tk.Button(
            btn_frame,
            text="⚔️ 复仇任务",
            command=self._on_revenge_quest,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_ORANGE,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.revenge_btn.pack(side=tk.LEFT, padx=5)

        self.forgive_btn = tk.Button(
            btn_frame,
            text="🕊️ 原谅",
            command=self._on_forgive_enemy,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.forgive_btn.pack(side=tk.LEFT, padx=5)

    def _get_social_manager(self):
        """获取社交管理器"""
        if self.social_manager is None:
            from game.social_system import get_social_manager
            self.social_manager = get_social_manager()
            self.social_manager.initialize_social_system()
        return self.social_manager

    def refresh(self):
        """刷新面板"""
        self._refresh_overview()
        self._refresh_friends()
        self._refresh_dao_lv()
        self._refresh_master_apprentice()
        self._refresh_enemies()

    def _refresh_overview(self):
        """刷新概览"""
        player = self.get_player()
        if not player:
            self._set_overview_text("请先创建角色")
            self._set_bonus_text("无加成")
            return

        manager = self._get_social_manager()
        relations = manager.get_all_relations(player.stats.name)

        text = f"""
╔══════════════════════════════════════════════════════════╗
║  💕 社交关系概览                                          ║
╠══════════════════════════════════════════════════════════╣
║  好友数量: {len(relations['friends'])}人                                          ║
║  道侣: {'✓ 有' if relations['dao_lv'] else '✗ 无'}                                      ║
║  师父: {'✓ 有' if relations['master'] else '✗ 无'}                                      ║
║  徒弟数量: {len(relations['apprentices'])}人                                          ║
║  仇敌数量: {len(relations['enemies'])}人                                          ║
╚══════════════════════════════════════════════════════════╝
"""
        self._set_overview_text(text)

        # 刷新加成信息
        bonuses = manager.get_social_bonuses(player.stats.name)
        bonus_text = f"""
修炼速度加成: +{bonuses['cultivation_speed']*100:.0f}%
经验获取加成: +{bonuses['exp_bonus']*100:.0f}%
战斗加成: +{bonuses['combat_bonus']*100:.0f}%
突破成功率加成: +{bonuses['breakthrough_bonus']*100:.0f}%
"""
        self._set_bonus_text(bonus_text)

    def _set_overview_text(self, text):
        """设置概览文本"""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(1.0, text)
        self.overview_text.config(state=tk.DISABLED)

    def _set_bonus_text(self, text):
        """设置加成文本"""
        self.bonus_text.config(state=tk.NORMAL)
        self.bonus_text.delete(1.0, tk.END)
        self.bonus_text.insert(1.0, text)
        self.bonus_text.config(state=tk.DISABLED)

    def _refresh_friends(self):
        """刷新好友列表"""
        self.friend_listbox.delete(0, tk.END)
        self.current_friends = []

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        friends = manager.get_friends(player.stats.name)
        self.current_friends = friends

        for friend in friends:
            self.friend_listbox.insert(
                tk.END,
                f"{friend['target_name']} [亲密度:{friend['intimacy']} 信任度:{friend['trust']}]"
            )

    def _refresh_dao_lv(self):
        """刷新道侣信息"""
        player = self.get_player()
        if not player:
            self._set_dao_lv_info_text("请先创建角色")
            self.current_dao_lv = None
            return

        manager = self._get_social_manager()
        dao_lv_info = manager.get_dao_lv_info(player.stats.name)
        self.current_dao_lv = dao_lv_info

        if dao_lv_info:
            text = f"""
╔══════════════════════════════════════════════════════════╗
║  💕 道侣: {dao_lv_info['partner_name']}                                    ║
╠══════════════════════════════════════════════════════════╣
║  关系类型: {dao_lv_info['marriage_type']}                                          ║
║  结缘日期: {dao_lv_info['marriage_date'][:10] if dao_lv_info['marriage_date'] else '未知'}                              ║
║  亲密度: {dao_lv_info['intimacy']}                                          ║
║  双修次数: {dao_lv_info['dual_cultivation_count']}                                          ║
╚══════════════════════════════════════════════════════════╝
"""
            self._set_dao_lv_info_text(text)

            # 更新按钮状态
            self.propose_btn.config(state=tk.DISABLED)
            self.dual_cultivation_btn.config(state=tk.NORMAL)
            self.divorce_btn.config(state=tk.NORMAL)
        else:
            self._set_dao_lv_info_text("""
╔══════════════════════════════════════════════════════════╗
║  💕 暂无道侣                                              ║
╠══════════════════════════════════════════════════════════╣
║  结为道侣可获得：                                          ║
║    • 修炼速度 +15%                                        ║
║    • 经验获取 +20%                                        ║
║    • 突破成功率 +10%                                      ║
║    • 双修获得大量修为                                     ║
╚══════════════════════════════════════════════════════════╝

💡 提示：需要与目标亲密度≥80且信任度≥70才能结为道侣
""")
            # 更新按钮状态
            self.propose_btn.config(state=tk.NORMAL)
            self.dual_cultivation_btn.config(state=tk.DISABLED)
            self.divorce_btn.config(state=tk.DISABLED)

    def _set_dao_lv_info_text(self, text):
        """设置道侣信息文本"""
        self.dao_lv_info_text.config(state=tk.NORMAL)
        self.dao_lv_info_text.delete(1.0, tk.END)
        self.dao_lv_info_text.insert(1.0, text)
        self.dao_lv_info_text.config(state=tk.DISABLED)

    def _refresh_master_apprentice(self):
        """刷新师徒信息"""
        player = self.get_player()
        if not player:
            self._set_master_info_text("请先创建角色")
            self.apprentice_listbox.delete(0, tk.END)
            return

        manager = self._get_social_manager()

        # 刷新师父信息
        master_info = manager.get_master(player.stats.name)
        self.current_master = master_info

        if master_info:
            text = f"""
师父: {master_info['master_name']}
关系: {master_info['relation_type']}
拜师日期: {master_info['established_date'][:10] if master_info['established_date'] else '未知'}
尊敬度: {master_info['respect']}
已传授功法: {', '.join(master_info['techniques_taught']) if master_info['techniques_taught'] else '无'}
"""
            self._set_master_info_text(text)
        else:
            self._set_master_info_text("你还没有师父\n\n💡 提示：需要达到筑基期才能收徒")

        # 刷新徒弟列表
        self.apprentice_listbox.delete(0, tk.END)
        apprentices = manager.get_apprentices(player.stats.name)
        self.current_apprentices = apprentices

        for apprentice in apprentices:
            self.apprentice_listbox.insert(
                tk.END,
                f"{apprentice['apprentice_name']} [尊敬度:{apprentice['respect']} 传授次数:{apprentice['teaching_count']}]"
            )

    def _set_master_info_text(self, text):
        """设置师父信息文本"""
        self.master_info_text.config(state=tk.NORMAL)
        self.master_info_text.delete(1.0, tk.END)
        self.master_info_text.insert(1.0, text)
        self.master_info_text.config(state=tk.DISABLED)

    def _refresh_enemies(self):
        """刷新仇敌列表"""
        self.enemy_listbox.delete(0, tk.END)
        self.current_enemies = []

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        enemies = manager.get_enemies(player.stats.name, is_completed=False)
        self.current_enemies = enemies

        for enemy in enemies:
            hatred_level = enemy['hatred_level']
            level_name = "轻微" if hatred_level < 30 else "憎恨" if hatred_level < 60 else "深仇"
            self.enemy_listbox.insert(
                tk.END,
                f"{enemy['enemy_name']} [仇恨:{level_name}]"
            )

    # ==================== 事件处理 ====================

    def _on_friend_select(self, event=None):
        """好友选择事件"""
        selection = self.friend_listbox.curselection()
        if not selection or not self.current_friends:
            return

        index = selection[0]
        if 0 <= index < len(self.current_friends):
            friend = self.current_friends[index]

            # 获取关系等级信息
            manager = self._get_social_manager()
            level_info = manager.get_friendship_level_info(friend['intimacy'])

            # 构建进度条
            progress_bar = self._create_progress_bar(level_info['progress_percent'], 20)

            info = f"""好友: {friend['target_name']}
关系等级: {level_info['level_name']} ({friend['intimacy']}/100)
进度: [{progress_bar}] {level_info['progress_percent']:.1f}%
下一级: {level_info['next_level_name']} (还需{level_info['intimacy_to_next']}亲密度)
信任度: {friend['trust']}/100
仇恨度: {friend['hatred']}/100
备注: {friend['notes'] or '无'}"""
            self.friend_info_var.set(info)
            self.selected_friend = friend

    def _get_intimacy_level_name(self, intimacy: int) -> str:
        """获取亲密度等级名称"""
        if intimacy >= 81:
            return "至爱"
        elif intimacy >= 61:
            return "情深"
        elif intimacy >= 41:
            return "亲近"
        elif intimacy >= 21:
            return "熟悉"
        else:
            return "初识"

    def _create_progress_bar(self, percent: float, length: int = 20) -> str:
        """
        创建进度条字符串

        Args:
            percent: 进度百分比 (0-100)
            length: 进度条长度

        Returns:
            进度条字符串
        """
        filled = int(length * percent / 100)
        empty = length - filled
        return "█" * filled + "░" * empty

    def _on_add_friend(self):
        """添加好友"""
        player = self.get_player()
        if not player:
            messagebox.showinfo("提示", "请先创建角色")
            return

        # 获取可添加的NPC列表
        available_npcs = self._get_available_npcs(player.stats.name)

        if not available_npcs:
            messagebox.showinfo("提示", "当前地图没有可结交的NPC")
            return

        # 显示NPC选择对话框
        dialog = NPCSelectionDialog(self, available_npcs, title="添加好友")
        friend_name = dialog.show()

        if not friend_name:
            return

        manager = self._get_social_manager()
        success, msg = manager.add_friend(player.stats.name, friend_name)

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("提示", msg)

    def _on_chat_friend(self):
        """与好友交谈"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, changes = manager.interact_with_friend(
            player.stats.name,
            self.selected_friend['target_name'],
            'chat'
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("交谈", msg)

    def _on_gift_friend(self):
        """赠送礼物"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, changes = manager.interact_with_friend(
            player.stats.name,
            self.selected_friend['target_name'],
            'gift'
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("赠送礼物", msg)

    def _on_remove_friend(self):
        """移除好友"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        if messagebox.askyesno("确认", f"确定要删除好友 {self.selected_friend['target_name']} 吗？"):
            manager = self._get_social_manager()
            success, msg = manager.remove_friend(player.stats.name, self.selected_friend['target_name'])

            if success:
                self.log(msg, "system")
                self.refresh()
            messagebox.showinfo("提示", msg)

    def _on_duel_friend(self):
        """与好友切磋"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, changes = manager.interact_with_friend(
            player.stats.name,
            self.selected_friend['target_name'],
            'duel'
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("切磋", msg)

    def _on_discuss_dao(self):
        """与好友论道"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, changes = manager.interact_with_friend(
            player.stats.name,
            self.selected_friend['target_name'],
            'discuss_dao'
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("论道", msg)

    def _on_cultivate_together(self):
        """与好友共修"""
        if not hasattr(self, 'selected_friend'):
            messagebox.showinfo("提示", "请先选择一个好友")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, changes = manager.interact_with_friend(
            player.stats.name,
            self.selected_friend['target_name'],
            'cultivate_together'
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("共修", msg)

    def _on_propose_dao_lv(self):
        """提议结为道侣"""
        player = self.get_player()
        if not player:
            messagebox.showinfo("提示", "请先创建角色")
            return

        target_name = simpledialog.askstring("结为道侣", "请输入对方名称:")
        if not target_name:
            return

        manager = self._get_social_manager()
        success, msg = manager.propose_dao_lv(
            player.stats.name,
            target_name,
            player.stats.realm_level,
            player.stats.realm_level
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("结为道侣", msg)

    def _on_dual_cultivation(self):
        """进行双修"""
        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        success, msg, result = manager.dual_cultivation(
            player.stats.name,
            player.stats.realm_level
        )

        if success:
            self.log(msg, "cultivation")
            self.refresh()
        messagebox.showinfo("双修", msg)

    def _on_divorce(self):
        """解除道侣关系"""
        player = self.get_player()
        if not player:
            return

        if not self.current_dao_lv:
            messagebox.showinfo("提示", "你没有道侣")
            return

        reason = simpledialog.askstring("解除道侣", "请输入解除原因（可选）:") or ""

        if messagebox.askyesno("确认", f"确定要解除与 {self.current_dao_lv['partner_name']} 的道侣关系吗？"):
            manager = self._get_social_manager()
            success, msg = manager.divorce(player.stats.name, reason)

            if success:
                self.log(msg, "system")
                self.refresh()
            messagebox.showinfo("解除道侣", msg)

    def _on_apprentice_select(self, event=None):
        """徒弟选择事件"""
        selection = self.apprentice_listbox.curselection()
        if not selection or not self.current_apprentices:
            return

        index = selection[0]
        if 0 <= index < len(self.current_apprentices):
            self.selected_apprentice = self.current_apprentices[index]

    def _on_accept_apprentice(self):
        """收徒"""
        player = self.get_player()
        if not player:
            messagebox.showinfo("提示", "请先创建角色")
            return

        apprentice_name = simpledialog.askstring("收徒", "请输入徒弟名称:")
        if not apprentice_name:
            return

        manager = self._get_social_manager()
        success, msg = manager.accept_apprentice(
            player.stats.name,
            apprentice_name,
            player.stats.realm_level,
            player.stats.realm_level - 1  # 假设徒弟境界低一级
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("收徒", msg)

    def _on_teach_technique(self):
        """传授功法"""
        if not hasattr(self, 'selected_apprentice'):
            messagebox.showinfo("提示", "请先选择一个徒弟")
            return

        player = self.get_player()
        if not player:
            return

        technique_name = simpledialog.askstring("传授功法", "请输入要传授的功法名称:")
        if not technique_name:
            return

        manager = self._get_social_manager()
        success, msg = manager.teach_technique(
            player.stats.name,
            self.selected_apprentice['apprentice_name'],
            technique_name
        )

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("传授功法", msg)

    def _on_leave_master(self):
        """离开师门"""
        player = self.get_player()
        if not player:
            return

        if not self.current_master:
            messagebox.showinfo("提示", "你没有师父")
            return

        reason = simpledialog.askstring("离开师门", "请输入离开原因（可选）:") or ""

        if messagebox.askyesno("确认", "确定要离开师门吗？"):
            manager = self._get_social_manager()
            success, msg = manager.leave_master(player.stats.name, reason)

            if success:
                self.log(msg, "system")
                self.refresh()
            messagebox.showinfo("离开师门", msg)

    def _on_enemy_select(self, event=None):
        """仇敌选择事件"""
        selection = self.enemy_listbox.curselection()
        if not selection or not self.current_enemies:
            return

        index = selection[0]
        if 0 <= index < len(self.current_enemies):
            enemy = self.current_enemies[index]
            info = f"""
仇敌: {enemy['enemy_name']}
结仇原因: {enemy['conflict_reason']}
仇恨等级: {enemy['hatred_level']}/100
结仇时间: {enemy['created_at'][:10] if enemy['created_at'] else '未知'}
复仇目标: {enemy['revenge_target']}
"""
            self.enemy_info_var.set(info)
            self.selected_enemy = enemy

    def _on_add_enemy(self):
        """添加仇敌"""
        player = self.get_player()
        if not player:
            messagebox.showinfo("提示", "请先创建角色")
            return

        enemy_name = simpledialog.askstring("添加仇敌", "请输入仇敌名称:")
        if not enemy_name:
            return

        reason = simpledialog.askstring("添加仇敌", "请输入结仇原因:") or "未知"

        manager = self._get_social_manager()
        success, msg = manager.add_enemy(player.stats.name, enemy_name, reason)

        if success:
            self.log(msg, "system")
            self.refresh()
        messagebox.showinfo("添加仇敌", msg)

    def _on_revenge_quest(self):
        """复仇任务"""
        if not hasattr(self, 'selected_enemy'):
            messagebox.showinfo("提示", "请先选择一个仇敌")
            return

        player = self.get_player()
        if not player:
            return

        manager = self._get_social_manager()
        quest = manager.create_revenge_quest(player.stats.name, self.selected_enemy['enemy_name'])

        if quest:
            msg = f"""
复仇任务: {quest['name']}
描述: {quest['description']}
仇恨等级: {quest['hatred_level']}

奖励:
  经验: {quest['rewards']['exp']}
  业力: {quest['rewards']['karma']}
  声望: {quest['rewards']['reputation']}
"""
            if messagebox.askyesno("复仇任务", msg + "\n\n是否接受此复仇任务？"):
                self.log(f"接受复仇任务: {quest['name']}", "quest")
        else:
            messagebox.showinfo("提示", "无法创建复仇任务")

    def _on_forgive_enemy(self):
        """原谅仇敌"""
        if not hasattr(self, 'selected_enemy'):
            messagebox.showinfo("提示", "请先选择一个仇敌")
            return

        player = self.get_player()
        if not player:
            return

        if messagebox.askyesno("确认", f"确定要原谅 {self.selected_enemy['enemy_name']} 吗？"):
            manager = self._get_social_manager()
            success, msg = manager.forgive_enemy(player.stats.name, self.selected_enemy['enemy_name'])

            if success:
                self.log(msg, "system")
                self.refresh()
            messagebox.showinfo("原谅仇敌", msg)

    def _get_available_npcs(self, player_name: str) -> list:
        """
        获取可添加为好友的NPC列表

        Args:
            player_name: 玩家名称

        Returns:
            NPC列表，每个NPC包含名称、境界、门派等信息
        """
        from storage.database import Database
        db = Database()

        # 获取当前地图的NPC
        player = self.get_player()
        if not player:
            return []

        current_location = player.location if hasattr(player, 'location') else "新手村"
        npcs_in_location = db.get_npcs_by_location_full(current_location)

        # 获取已有的好友列表
        manager = self._get_social_manager()
        friends = manager.get_friends(player_name)
        friend_names = {f['target_name'] for f in friends}

        # 过滤掉已经是好友的NPC
        available_npcs = []
        for npc in npcs_in_location:
            npc_name = npc.get('name', '') or npc.get('full_name', '')
            if npc_name and npc_name not in friend_names and npc_name != player_name:
                available_npcs.append({
                    'name': npc_name,
                    'realm': npc.get('realm_level', '未知'),
                    'sect': npc.get('sect', '散修'),
                    'gender': npc.get('gender', '未知'),
                    'age': npc.get('age', 0)
                })

        return available_npcs


class NPCSelectionDialog(tk.Toplevel):
    """NPC选择对话框"""

    def __init__(self, parent, npcs, title="选择NPC"):
        """
        初始化NPC选择对话框

        Args:
            parent: 父窗口
            npcs: NPC列表
            title: 对话框标题
        """
        super().__init__(parent)
        self.title(title)
        self.npcs = npcs
        self.selected_npc = None
        self.result = None

        # 设置对话框样式
        self.configure(bg=Theme.BG_SECONDARY)
        self.geometry("500x400")
        self.resizable(False, False)

        # 模态对话框
        self.transient(parent)
        self.grab_set()

        self._setup_ui()
        self.center_window()

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(
            self,
            text="选择要添加为好友的NPC",
            font=Theme.get_font(12, bold=True),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY
        )
        title_label.pack(pady=10)

        # 说明文字
        info_label = tk.Label(
            self,
            text=f"当前地图共有 {len(self.npcs)} 位NPC可以结交",
            font=Theme.get_font(10),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY
        )
        info_label.pack(pady=5)

        # NPC列表框架
        list_frame = tk.Frame(self, bg=Theme.BG_TERTIARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 表头
        header_frame = tk.Frame(list_frame, bg=Theme.BG_TERTIARY)
        header_frame.pack(fill=tk.X, pady=5)

        tk.Label(header_frame, text="名称", width=15, font=Theme.get_font(10, bold=True),
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="境界", width=12, font=Theme.get_font(10, bold=True),
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="门派", width=12, font=Theme.get_font(10, bold=True),
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)

        # 列表框
        listbox_frame = tk.Frame(list_frame, bg=Theme.BG_TERTIARY)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox = tk.Listbox(
            listbox_frame,
            font=Theme.get_font(10),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            selectbackground=Theme.ACCENT_CYAN,
            selectforeground=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            height=10
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # 填充NPC数据
        for npc in self.npcs:
            display_text = f"{npc['name']:<15} {npc['realm']:<12} {npc['sect']:<12}"
            self.listbox.insert(tk.END, display_text)

        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", self._on_double_click)

        # NPC详情
        self.detail_var = tk.StringVar(value="选择一个NPC查看详情")
        detail_label = tk.Label(
            self,
            textvariable=self.detail_var,
            wraplength=450,
            justify=tk.LEFT,
            font=Theme.get_font(9),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY
        )
        detail_label.pack(anchor=tk.W, padx=15, pady=5)

        # 按钮框架
        btn_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=15, pady=15)

        # 确定按钮
        self.ok_btn = tk.Button(
            btn_frame,
            text="确定",
            command=self._on_ok,
            font=Theme.get_font(10),
            bg=Theme.ACCENT_GREEN,
            fg=Theme.BG_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.ok_btn.pack(side=tk.RIGHT, padx=5)

        # 取消按钮
        cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            command=self._on_cancel,
            font=Theme.get_font(10),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # 如果没有NPC，显示提示
        if not self.npcs:
            self.listbox.insert(tk.END, "当前地图没有可结交的NPC")
            self.listbox.config(state=tk.DISABLED)

    def center_window(self):
        """居中窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _on_select(self, event=None):
        """选择事件"""
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if 0 <= index < len(self.npcs):
            self.selected_npc = self.npcs[index]

            # 更新详情显示
            npc = self.selected_npc
            detail_text = f"名称: {npc['name']} | 境界: {npc['realm']} | 门派: {npc['sect']} | 性别: {npc['gender']} | 年龄: {npc['age']}岁"
            self.detail_var.set(detail_text)

            # 启用确定按钮
            self.ok_btn.config(state=tk.NORMAL)

    def _on_double_click(self, event=None):
        """双击事件"""
        self._on_select()
        if self.selected_npc:
            self._on_ok()

    def _on_ok(self):
        """确定按钮"""
        if self.selected_npc:
            self.result = self.selected_npc['name']
            self.destroy()

    def _on_cancel(self):
        """取消按钮"""
        self.result = None
        self.destroy()

    def show(self):
        """显示对话框并返回结果"""
        self.wait_window()
        return self.result
