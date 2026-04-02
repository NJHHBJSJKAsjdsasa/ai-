"""
世界演化面板
展示世界事件、时间线、天材地宝、势力变迁等信息
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional, Callable
import random

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from interface.gui.panels.base_panel import BasePanel
from game.world_evolution_system import WorldEvolutionManager, WorldEvent, TimelineEvent, Treasure, Faction
from config.world_config import RARITY_LEVELS, FACTION_TYPES


class WorldPanel(BasePanel):
    """世界演化面板"""

    def __init__(self, parent, main_window, **kwargs):
        """初始化世界演化面板"""
        self.world_manager: Optional[WorldEvolutionManager] = None
        self.current_tab = "events"

        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面 - 重写基类方法"""
        # 初始化世界管理器
        if self.game and hasattr(self.game, 'world_evolution_manager'):
            self.world_manager = self.game.world_evolution_manager
        else:
            from storage.database import Database
            self.world_manager = WorldEvolutionManager(Database())

        self._create_ui()
        self.refresh_data()

    def _create_ui(self):
        """创建UI组件"""
        # 标题
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            title_frame,
            text="世界演化",
            font=("Microsoft YaHei", 16, "bold")
        ).pack(side=tk.LEFT)

        # 刷新按钮
        ttk.Button(
            title_frame,
            text="刷新",
            command=self.refresh_data
        ).pack(side=tk.RIGHT)

        # 统计信息
        self.stats_frame = ttk.LabelFrame(self, text="世界概况", padding=10)
        self.stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_labels = {}
        stats_items = [
            ("active_events", "活跃事件", "0"),
            ("active_treasures", "未获取宝物", "0"),
            ("active_factions", "活跃势力", "0"),
            ("current_date", "当前日期", "第1年1月1日")
        ]

        for i, (key, label, default) in enumerate(stats_items):
            ttk.Label(self.stats_frame, text=f"{label}:").grid(row=0, column=i*2, padx=5)
            self.stats_labels[key] = ttk.Label(self.stats_frame, text=default)
            self.stats_labels[key].grid(row=0, column=i*2+1, padx=5)

        # 标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个标签页
        self._create_events_tab()
        self._create_timeline_tab()
        self._create_treasures_tab()
        self._create_factions_tab()
        self._create_economy_tab()

        # 绑定标签切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _create_events_tab(self):
        """创建事件标签页"""
        events_frame = ttk.Frame(self.notebook)
        self.notebook.add(events_frame, text="世界事件")

        # 筛选框架
        filter_frame = ttk.Frame(events_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="范围:").pack(side=tk.LEFT, padx=5)
        self.event_scope_var = tk.StringVar(value="all")
        scope_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.event_scope_var,
            values=["all", "local", "regional", "global"],
            width=10,
            state="readonly"
        )
        scope_combo.pack(side=tk.LEFT, padx=5)
        scope_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_events())

        # 事件列表
        columns = ("title", "type", "location", "importance", "status")
        self.events_tree = ttk.Treeview(
            events_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.events_tree.heading("title", text="事件")
        self.events_tree.heading("type", text="类型")
        self.events_tree.heading("location", text="地点")
        self.events_tree.heading("importance", text="重要度")
        self.events_tree.heading("status", text="状态")

        self.events_tree.column("title", width=200)
        self.events_tree.column("type", width=100)
        self.events_tree.column("location", width=100)
        self.events_tree.column("importance", width=60)
        self.events_tree.column("status", width=80)

        # 滚动条
        scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)

        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 双击查看详情
        self.events_tree.bind("<Double-1>", self._on_event_double_click)

        # 参与按钮
        btn_frame = ttk.Frame(events_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="参与事件",
            command=self._participate_event
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="查看详情",
            command=self._show_event_detail
        ).pack(side=tk.LEFT, padx=5)

    def _create_timeline_tab(self):
        """创建时间线标签页"""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="历史时间线")

        # 筛选框架
        filter_frame = ttk.Frame(timeline_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="年份:").pack(side=tk.LEFT, padx=5)
        self.timeline_year_var = tk.StringVar()
        year_entry = ttk.Entry(filter_frame, textvariable=self.timeline_year_var, width=10)
        year_entry.pack(side=tk.LEFT, padx=5)

        self.historic_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="仅显示历史事件",
            variable=self.historic_only_var,
            command=self._refresh_timeline
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            filter_frame,
            text="筛选",
            command=self._refresh_timeline
        ).pack(side=tk.LEFT, padx=5)

        # 时间线列表
        columns = ("date", "title", "type", "location", "importance")
        self.timeline_tree = ttk.Treeview(
            timeline_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.timeline_tree.heading("date", text="日期")
        self.timeline_tree.heading("title", text="事件")
        self.timeline_tree.heading("type", text="类型")
        self.timeline_tree.heading("location", text="地点")
        self.timeline_tree.heading("importance", text="重要度")

        self.timeline_tree.column("date", width=100)
        self.timeline_tree.column("title", width=250)
        self.timeline_tree.column("type", width=100)
        self.timeline_tree.column("location", width=100)
        self.timeline_tree.column("importance", width=60)

        scrollbar = ttk.Scrollbar(timeline_frame, orient=tk.VERTICAL, command=self.timeline_tree.yview)
        self.timeline_tree.configure(yscrollcommand=scrollbar.set)

        self.timeline_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.timeline_tree.bind("<Double-1>", self._on_timeline_double_click)

    def _create_treasures_tab(self):
        """创建天材地宝标签页"""
        treasures_frame = ttk.Frame(self.notebook)
        self.notebook.add(treasures_frame, text="天材地宝")

        # 筛选框架
        filter_frame = ttk.Frame(treasures_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="地点:").pack(side=tk.LEFT, padx=5)
        self.treasure_location_var = tk.StringVar(value="all")
        location_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.treasure_location_var,
            values=["all"],
            width=15,
            state="readonly"
        )
        location_combo.pack(side=tk.LEFT, padx=5)
        location_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_treasures())

        # 宝物列表
        columns = ("name", "type", "rarity", "location", "guardian")
        self.treasures_tree = ttk.Treeview(
            treasures_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.treasures_tree.heading("name", text="名称")
        self.treasures_tree.heading("type", text="类型")
        self.treasures_tree.heading("rarity", text="稀有度")
        self.treasures_tree.heading("location", text="地点")
        self.treasures_tree.heading("guardian", text="守护兽")

        self.treasures_tree.column("name", width=150)
        self.treasures_tree.column("type", width=80)
        self.treasures_tree.column("rarity", width=80)
        self.treasures_tree.column("location", width=100)
        self.treasures_tree.column("guardian", width=150)

        scrollbar = ttk.Scrollbar(treasures_frame, orient=tk.VERTICAL, command=self.treasures_tree.yview)
        self.treasures_tree.configure(yscrollcommand=scrollbar.set)

        self.treasures_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.treasures_tree.bind("<Double-1>", self._on_treasure_double_click)

        # 按钮框架
        btn_frame = ttk.Frame(treasures_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="获取宝物",
            command=self._claim_treasure
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="查看详情",
            command=self._show_treasure_detail
        ).pack(side=tk.LEFT, padx=5)

    def _create_factions_tab(self):
        """创建势力标签页"""
        factions_frame = ttk.Frame(self.notebook)
        self.notebook.add(factions_frame, text="势力分布")

        # 势力列表
        columns = ("rank", "name", "type", "leader", "power", "reputation", "influence")
        self.factions_tree = ttk.Treeview(
            factions_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.factions_tree.heading("rank", text="排名")
        self.factions_tree.heading("name", text="势力名称")
        self.factions_tree.heading("type", text="类型")
        self.factions_tree.heading("leader", text="领袖")
        self.factions_tree.heading("power", text="实力")
        self.factions_tree.heading("reputation", text="声望")
        self.factions_tree.heading("influence", text="影响力")

        self.factions_tree.column("rank", width=50)
        self.factions_tree.column("name", width=150)
        self.factions_tree.column("type", width=80)
        self.factions_tree.column("leader", width=100)
        self.factions_tree.column("power", width=60)
        self.factions_tree.column("reputation", width=60)
        self.factions_tree.column("influence", width=60)

        scrollbar = ttk.Scrollbar(factions_frame, orient=tk.VERTICAL, command=self.factions_tree.yview)
        self.factions_tree.configure(yscrollcommand=scrollbar.set)

        self.factions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.factions_tree.bind("<Double-1>", self._on_faction_double_click)

        # 按钮框架
        btn_frame = ttk.Frame(factions_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="查看详情",
            command=self._show_faction_detail
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="势力变迁历史",
            command=self._show_faction_history
        ).pack(side=tk.LEFT, padx=5)

    def _create_economy_tab(self):
        """创建经济标签页"""
        economy_frame = ttk.Frame(self.notebook)
        self.notebook.add(economy_frame, text="世界经济")

        # 资源价格列表
        columns = ("resource", "price", "supply", "demand", "trend")
        self.economy_tree = ttk.Treeview(
            economy_frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.economy_tree.heading("resource", text="资源")
        self.economy_tree.heading("price", text="价格")
        self.economy_tree.heading("supply", text="供应量")
        self.economy_tree.heading("demand", text="需求量")
        self.economy_tree.heading("trend", text="趋势")

        self.economy_tree.column("resource", width=100)
        self.economy_tree.column("price", width=80)
        self.economy_tree.column("supply", width=80)
        self.economy_tree.column("demand", width=80)
        self.economy_tree.column("trend", width=80)

        scrollbar = ttk.Scrollbar(economy_frame, orient=tk.VERTICAL, command=self.economy_tree.yview)
        self.economy_tree.configure(yscrollcommand=scrollbar.set)

        self.economy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def _on_tab_changed(self, event):
        """标签切换事件"""
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text")

        if tab_text == "世界事件":
            self._refresh_events()
        elif tab_text == "历史时间线":
            self._refresh_timeline()
        elif tab_text == "天材地宝":
            self._refresh_treasures()
        elif tab_text == "势力分布":
            self._refresh_factions()
        elif tab_text == "世界经济":
            self._refresh_economy()

    def refresh_data(self):
        """刷新所有数据"""
        self._update_stats()

        # 根据当前标签页刷新对应数据
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text")

        if tab_text == "世界事件":
            self._refresh_events()
        elif tab_text == "历史时间线":
            self._refresh_timeline()
        elif tab_text == "天材地宝":
            self._refresh_treasures()
        elif tab_text == "势力分布":
            self._refresh_factions()
        elif tab_text == "世界经济":
            self._refresh_economy()

    def _update_stats(self):
        """更新统计信息"""
        stats = self.world_manager.get_world_stats()

        self.stats_labels["active_events"].config(text=str(stats["active_events_count"]))
        self.stats_labels["active_treasures"].config(text=str(stats["active_treasures_count"]))
        self.stats_labels["active_factions"].config(text=str(stats["factions_count"]))

        # 获取当前游戏时间
        if self.game and hasattr(self.game, 'game_time'):
            game_time = self.game.game_time
            date_str = f"第{game_time.get('year', 1)}年{game_time.get('month', 1)}月{game_time.get('day', 1)}日"
            self.stats_labels["current_date"].config(text=date_str)

    def _refresh_events(self):
        """刷新事件列表"""
        # 清空列表
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)

        # 获取筛选条件
        scope = self.event_scope_var.get()
        if scope == "all":
            scope = None

        # 获取事件
        events = self.world_manager.get_active_events(scope=scope)

        # 添加到列表
        for event in events:
            self.events_tree.insert("", tk.END, values=(
                event.title,
                event.event_type,
                event.location,
                "★" * event.importance,
                "进行中" if event.status.value == "active" else "已结束"
            ), tags=(event.event_id,))

    def _refresh_timeline(self):
        """刷新时间线"""
        # 清空列表
        for item in self.timeline_tree.get_children():
            self.timeline_tree.delete(item)

        # 获取筛选条件
        year = None
        if self.timeline_year_var.get():
            try:
                year = int(self.timeline_year_var.get())
            except ValueError:
                pass

        is_historic = self.historic_only_var.get() if self.historic_only_var.get() else None

        # 获取时间线事件
        events = self.world_manager.get_timeline(year=year, is_historic=is_historic, limit=100)

        # 添加到列表
        for event in events:
            date_str = f"第{event.year}年{event.month}月{event.day}日"
            self.timeline_tree.insert("", tk.END, values=(
                date_str,
                event.title,
                event.event_type,
                event.location,
                "★" * event.importance
            ), tags=(event.event_id,))

    def _refresh_treasures(self):
        """刷新宝物列表"""
        # 清空列表
        for item in self.treasures_tree.get_children():
            self.treasures_tree.delete(item)

        # 获取筛选条件
        location = self.treasure_location_var.get()
        if location == "all":
            location = None

        # 获取宝物
        treasures = self.world_manager.get_active_treasures(location=location)

        # 添加到列表
        for treasure in treasures:
            rarity_info = RARITY_LEVELS.get(treasure.rarity, {})
            rarity_name = rarity_info.get("name", treasure.rarity)

            self.treasures_tree.insert("", tk.END, values=(
                treasure.name,
                treasure.treasure_type,
                rarity_name,
                treasure.spawn_location,
                f"{treasure.guardian_monster}(Lv.{treasure.guardian_level})"
            ), tags=(treasure.id,))

    def _refresh_factions(self):
        """刷新势力列表"""
        # 清空列表
        for item in self.factions_tree.get_children():
            self.factions_tree.delete(item)

        # 获取势力排名
        factions = self.world_manager.get_faction_ranking()

        # 添加到列表
        for i, faction in enumerate(factions, 1):
            faction_type_info = FACTION_TYPES.get(faction.faction_type, {})
            faction_type_name = faction_type_info.get("name", faction.faction_type)

            self.factions_tree.insert("", tk.END, values=(
                i,
                faction.name,
                faction_type_name,
                faction.leader,
                faction.power,
                faction.reputation,
                faction.get_influence()
            ), tags=(faction.id,))

    def _refresh_economy(self):
        """刷新经济信息"""
        # 清空列表
        for item in self.economy_tree.get_children():
            self.economy_tree.delete(item)

        # 获取经济信息
        economy = self.world_manager.get_economy_info()

        # 资源名称映射
        resource_names = {
            "spirit_stones": "灵石",
            "herbs": "草药",
            "ores": "矿石",
            "pellets": "丹药",
            "materials": "材料"
        }

        # 添加到列表
        for resource, price in economy.get("prices", {}).items():
            supply = economy.get("supply", {}).get(resource, 50)
            demand = economy.get("demand", {}).get(resource, 50)

            if supply > demand:
                trend = "↓ 下跌"
            elif supply < demand:
                trend = "↑ 上涨"
            else:
                trend = "→ 平稳"

            self.economy_tree.insert("", tk.END, values=(
                resource_names.get(resource, resource),
                f"{price:.2f}",
                supply,
                demand,
                trend
            ))

    def _on_event_double_click(self, event):
        """事件双击事件"""
        self._show_event_detail()

    def _on_timeline_double_click(self, event):
        """时间线双击事件"""
        selected = self.timeline_tree.selection()
        if not selected:
            return

        item = self.timeline_tree.item(selected[0])
        event_id = item["tags"][0] if item["tags"] else None

        if event_id:
            self._show_timeline_event_detail(event_id)

    def _on_treasure_double_click(self, event):
        """宝物双击事件"""
        self._show_treasure_detail()

    def _on_faction_double_click(self, event):
        """势力双击事件"""
        self._show_faction_detail()

    def _show_event_detail(self):
        """显示事件详情"""
        selected = self.events_tree.selection()
        if not selected:
            return

        item = self.events_tree.item(selected[0])
        event_id = item["tags"][0] if item["tags"] else None

        if event_id and event_id in self.world_manager.active_events:
            event = self.world_manager.active_events[event_id]
            self._show_detail_dialog("事件详情", self._format_event_detail(event))

    def _show_timeline_event_detail(self, event_id: str):
        """显示时间线事件详情"""
        # 从数据库获取事件详情
        events = self.world_manager.db.get_world_timeline(limit=1000)
        for event_data in events:
            if event_data["event_id"] == event_id:
                detail = f"""
事件: {event_data['title']}
类型: {event_data['event_type']}
日期: 第{event_data['year']}年{event_data['month']}月{event_data['day']}日
地点: {event_data.get('location', '未知')}
重要度: {'★' * event_data.get('importance', 5)}
历史事件: {'是' if event_data.get('is_historic') else '否'}

描述:
{event_data['description']}
                """
                self._show_detail_dialog("历史事件详情", detail)
                break

    def _show_treasure_detail(self):
        """显示宝物详情"""
        selected = self.treasures_tree.selection()
        if not selected:
            return

        item = self.treasures_tree.item(selected[0])
        treasure_id = item["tags"][0] if item["tags"] else None

        if treasure_id and treasure_id in self.world_manager.treasures:
            treasure = self.world_manager.treasures[treasure_id]
            self._show_detail_dialog("宝物详情", self._format_treasure_detail(treasure))

    def _show_faction_detail(self):
        """显示势力详情"""
        selected = self.factions_tree.selection()
        if not selected:
            return

        item = self.factions_tree.item(selected[0])
        faction_id = item["tags"][0] if item["tags"] else None

        if faction_id and faction_id in self.world_manager.factions:
            faction = self.world_manager.factions[faction_id]
            self._show_detail_dialog("势力详情", self._format_faction_detail(faction))

    def _show_faction_history(self):
        """显示势力变迁历史"""
        selected = self.factions_tree.selection()
        if not selected:
            return

        item = self.factions_tree.item(selected[0])
        faction_id = item["tags"][0] if item["tags"] else None

        if faction_id:
            changes = self.world_manager.db.get_faction_changes(faction_id=faction_id, limit=50)
            if changes:
                history_text = "势力变迁历史:\n\n"
                for change in changes:
                    date_str = f"第{change['year']}年{change['month']}月{change['day']}日"
                    history_text += f"[{date_str}] {change['change_type']}: {change['change_description']}\n"
                self._show_detail_dialog("势力变迁历史", history_text)
            else:
                self._show_detail_dialog("势力变迁历史", "暂无变迁记录")

    def _participate_event(self):
        """参与事件"""
        selected = self.events_tree.selection()
        if not selected:
            return

        item = self.events_tree.item(selected[0])
        event_id = item["tags"][0] if item["tags"] else None

        if not event_id:
            return

        # 创建参与对话框
        dialog = tk.Toplevel(self)
        dialog.title("参与世界事件")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="参与方式:").pack(pady=5)
        participation_type_var = tk.StringVar(value="观察")
        type_combo = ttk.Combobox(
            dialog,
            textvariable=participation_type_var,
            values=["观察", "协助", "主导", "对抗"],
            state="readonly"
        )
        type_combo.pack(pady=5)

        ttk.Label(dialog, text="参与描述:").pack(pady=5)
        description_text = tk.Text(dialog, height=5, width=40)
        description_text.pack(pady=5)

        def confirm():
            if self.game and hasattr(self.game, 'player'):
                player = self.game.player
                game_time = self.game.game_time if hasattr(self.game, 'game_time') else {"year": 1, "month": 1, "day": 1}

                self.world_manager.player_participate_event(
                    event_id=event_id,
                    player_id=player.id,
                    participation_type=participation_type_var.get(),
                    description=description_text.get("1.0", tk.END).strip(),
                    year=game_time.get("year", 1),
                    month=game_time.get("month", 1),
                    day=game_time.get("day", 1),
                    contribution_score=random.randint(10, 100)
                )

                dialog.destroy()
                self.refresh_data()

        ttk.Button(dialog, text="确认参与", command=confirm).pack(pady=10)

    def _claim_treasure(self):
        """获取宝物"""
        selected = self.treasures_tree.selection()
        if not selected:
            return

        item = self.treasures_tree.item(selected[0])
        treasure_id = item["tags"][0] if item["tags"] else None

        if not treasure_id:
            return

        if self.game and hasattr(self.game, 'player'):
            player = self.game.player
            success = self.world_manager.claim_treasure(treasure_id, player.id, player.name)

            if success:
                self.show_info("获取成功", "你成功获取了这件天材地宝！")
                self.refresh_data()
            else:
                self.show_error("获取失败", "无法获取这件宝物，可能已被他人取走。")

    def _format_event_detail(self, event: WorldEvent) -> str:
        """格式化事件详情"""
        return f"""
事件: {event.title}
类型: {event.event_type}
状态: {"进行中" if event.status.value == "active" else "已结束"}
日期: 第{event.start_year}年{event.start_month}月{event.start_day}日
地点: {event.location}
范围: {event.scope}
重要度: {'★' * event.importance}
玩家参与: {'是' if event.player_participated else '否'}

描述:
{event.description}
        """

    def _format_treasure_detail(self, treasure: Treasure) -> str:
        """格式化宝物详情"""
        rarity_info = RARITY_LEVELS.get(treasure.rarity, {})
        rarity_name = rarity_info.get("name", treasure.rarity)

        return f"""
名称: {treasure.name}
类型: {treasure.treasure_type}
稀有度: {rarity_name}
发现地点: {treasure.spawn_location}
发现时间: 第{treasure.spawn_year}年{treasure.spawn_month}月{treasure.spawn_day}日
守护兽: {treasure.guardian_monster} (等级: {treasure.guardian_level})
状态: {"已被获取" if treasure.is_claimed else "可获取"}

描述:
{treasure.description}

效果:
{self._format_effects(treasure.effects)}
        """

    def _format_faction_detail(self, faction: Faction) -> str:
        """格式化势力详情"""
        faction_type_info = FACTION_TYPES.get(faction.faction_type, {})
        faction_type_name = faction_type_info.get("name", faction.faction_type)

        return f"""
势力名称: {faction.name}
势力类型: {faction_type_name}
领袖: {faction.leader}
成立年份: 第{faction.founded_year}年
状态: {"活跃" if faction.is_active else "已解散"}

实力: {faction.power}/100
声望: {faction.reputation}/100
财富: {faction.wealth}/100
影响力: {faction.get_influence()}
成员数: {len(faction.members)}
领地数: {len(faction.territory)}

描述:
{faction.description}
        """

    def _format_effects(self, effects: Dict[str, Any]) -> str:
        """格式化效果"""
        if not effects:
            return "无特殊效果"

        effect_texts = []
        for key, value in effects.items():
            if key == "spirit_stones":
                effect_texts.append(f"  - 灵石: {value}")
            elif key == "exp_boost":
                effect_texts.append(f"  - 修为提升: +{value}")
            elif key == "lifespan_increase":
                effect_texts.append(f"  - 寿命增加: +{value}年")
            elif key == "attribute_bonus":
                effect_texts.append(f"  - 属性加成: +{value}")
            elif key == "herbs":
                effect_texts.append(f"  - 包含草药: {', '.join(value)}")
            else:
                effect_texts.append(f"  - {key}: {value}")

        return "\n".join(effect_texts)

    def _show_detail_dialog(self, title: str, content: str):
        """显示详情对话框"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x400")
        dialog.transient(self)

        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", content)
        text_widget.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(text_widget, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)

    def update(self, dt: float):
        """更新面板"""
        pass

    def on_show(self):
        """显示面板时调用"""
        self.refresh_data()

    def on_hide(self):
        """隐藏面板时调用"""
        pass
