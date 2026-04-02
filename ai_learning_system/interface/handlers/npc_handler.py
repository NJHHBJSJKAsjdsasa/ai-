"""
NPC 处理器类

处理与 NPC 相关的所有命令，包括交谈、列表、详情和统计。
"""

from typing import Optional
from .base_handler import BaseHandler
from utils.colors import Color, colorize, green, bold, dim
from interface.ui import UIPanel, UITable, UIProgress, UIInfoCard, UITheme


# 翻译字典
NEED_TRANSLATIONS = {
    'HUNGER': '饥饿',
    'ENERGY': '精力',
    'SOCIAL': '社交',
    'CULTIVATION': '修炼',
    # 兼容旧数据
    'health': '健康',
    'safety': '安全',
    'achievement': '成就',
    'rest': '休息',
}

PERSONALITY_TRANSLATIONS = {
    'bravery': '勇敢',
    'caution': '谨慎',
    'aggression': '攻击性',
    'friendliness': '友善',
    'curiosity': '好奇心',
    'discipline': '自律',
    'greed': '贪婪',
    'loyalty': '忠诚',
}

GOAL_TYPE_TRANSLATIONS = {
    'CULTIVATION': '修炼',
    'SOCIAL': '社交',
    'EXPLORATION': '探索',
    'COMBAT': '战斗',
    'QUEST': '任务',
    'GATHERING': '采集',
    'CRAFTING': ' crafting',
}

ACTIVITY_TYPE_TRANSLATIONS = {
    'SLEEP': '睡眠',
    'CULTIVATION': '修炼',
    'WORK': '工作',
    'SOCIAL': '社交',
    'LEISURE': '休闲',
    'TRAVEL': '旅行',
    'COMBAT': '战斗',
    'SHOPPING': '购物',
    'REST': '休息',
}

EVENT_TYPE_TRANSLATIONS = {
    'BIRTH': '出生',
    'CULTIVATION': '修炼',
    'BREAKTHROUGH': '突破',
    'COMBAT': '战斗',
    'SOCIAL': '社交',
    'TRAVEL': '旅行',
    'QUEST': '任务',
    'ITEM_OBTAINED': '获得物品',
    'ITEM_LOST': '失去物品',
    'RELATIONSHIP': '关系',
    'DEATH': '死亡',
}

RELATION_TYPE_TRANSLATIONS = {
    'FRIEND': '朋友',
    'ENEMY': '敌人',
    'NEUTRAL': '中立',
    'MASTER': '师父',
    'DISCIPLE': '弟子',
    'FAMILY': '家人',
    'RIVAL': '竞争对手',
}


def translate_need(need_name: str) -> str:
    """翻译需求状态"""
    return NEED_TRANSLATIONS.get(need_name, need_name)


def translate_personality(trait: str) -> str:
    """翻译性格属性"""
    return PERSONALITY_TRANSLATIONS.get(trait, trait)


def translate_goal_type(goal_type) -> str:
    """翻译目标类型"""
    if hasattr(goal_type, 'value'):
        goal_type = goal_type.value
    if hasattr(goal_type, 'name'):
        goal_type = goal_type.name
    goal_type_str = str(goal_type).upper()
    return GOAL_TYPE_TRANSLATIONS.get(goal_type_str, str(goal_type))


def translate_activity_type(activity_type) -> str:
    """翻译活动类型"""
    if hasattr(activity_type, 'value'):
        activity_type = activity_type.value
    if hasattr(activity_type, 'name'):
        activity_type = activity_type.name
    activity_type_str = str(activity_type).upper()
    return ACTIVITY_TYPE_TRANSLATIONS.get(activity_type_str, str(activity_type))


def translate_event_type(event_type) -> str:
    """翻译事件类型"""
    if hasattr(event_type, 'value'):
        event_type = event_type.value
    if hasattr(event_type, 'name'):
        event_type = event_type.name
    event_type_str = str(event_type).upper()
    return EVENT_TYPE_TRANSLATIONS.get(event_type_str, str(event_type))


def translate_relation_type(relation_type) -> str:
    """翻译关系类型"""
    if hasattr(relation_type, 'value'):
        relation_type = relation_type.value
    if hasattr(relation_type, 'name'):
        relation_type = relation_type.name
    relation_type_str = str(relation_type).upper()
    return RELATION_TYPE_TRANSLATIONS.get(relation_type_str, str(relation_type))


class NPCHandler(BaseHandler):
    """
    NPC 处理器类
    
    处理所有与 NPC 交互相关的命令。
    """
    
    def handle_talk(self, npc_name: str):
        """
        处理交谈命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.npc_manager or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要交谈的NPC")
            warning_panel.add_line("可用命令: /交谈 <NPC名字>")
            print(warning_panel.render())
            return
        
        # 查找NPC
        npc = self.npc_manager.get_npc_by_name(npc_name)
        if not npc or npc.data.location != self.player.stats.location:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line(f"{npc_name}不在此处")
            print(warning_panel.render())
            return
        
        # 使用UIInfoCard显示NPC信息
        npc_data = {
            'name': npc.data.dao_name,
            'realm': npc.get_realm_name(),
            'sect': npc.data.sect,
            'occupation': npc.data.occupation,
            'personality': npc.data.personality,
            'location': npc.data.location,
        }
        
        card = UIInfoCard.npc_info_card(npc_data, width=60)
        print(card.render())
        
        # 显示问候
        greeting_panel = UIPanel.info_panel("💬 问候", width=60, border_color=UITheme.BORDER_SECONDARY)
        greeting = npc.get_greeting(self.player.stats.name)
        greeting_panel.add_line(greeting)
        print(greeting_panel.render())
        
        # 更新好感度
        npc.update_favor(self.player.stats.name, 1)
        
        # 添加记忆
        npc.add_memory(f"与{self.player.stats.name}交谈", importance=3)
    
    def handle_npc_list(self):
        """处理NPC列表命令 - 显示独立NPC系统信息"""
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        npcs = self.world.get_npcs_in_location(self.player.stats.location)
        
        if not npcs:
            empty_panel = UIPanel.info_panel("👥 当前地点的修士", width=60)
            empty_panel.add_line(colorize("此处暂无其他修士", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return
        
        # 使用UITable显示NPC列表
        headers = ['关系', '道号', '境界', '职业', '活动']
        rows = []
        
        for npc in npcs:
            favor = npc.get_favor(self.player.stats.name)
            favor_icon = "😊" if favor > 30 else "😐" if favor > -30 else "😠"
            status = npc.get_independent_status()
            activity = status.get('current_activity', '闲逛')
            rows.append([
                favor_icon,
                npc.data.dao_name,
                npc.get_realm_name(),
                npc.data.occupation,
                activity
            ])
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"👥 当前地点的修士 ({self.player.stats.location})", width=62)
        print(title_panel.render())
        
        # 创建表格
        table = UITable(headers=headers, rows=rows, width=62)
        print(table.render())
        
        # 底部信息
        footer_panel = UIPanel(width=62, border_style='none')
        footer_panel.add_line(f"共{len(npcs)}位修士在此地活动")
        footer_panel.add_line(f"使用 {green('/npc <名字>')} 查看详细信息")
        print(footer_panel.render())
    
    def handle_npc_detail(self, npc_name: str):
        """
        处理NPC详情命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        if not npc_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
            print(f"  可用命令: /npc <名字>")
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 未找到名为'{npc_name}'的修士")
            return
        
        # 获取独立系统状态
        status = npc.get_independent_status()
        
        print(f"\n{self.colorize('📋 NPC详情', Color.BOLD_CYAN)}")
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
        print(f"  道号: {bold(npc.data.dao_name)}")
        print(f"  境界: {npc.get_realm_name()}")
        print(f"  年龄: {npc.data.age}岁 / {npc.data.lifespan}岁")
        print(f"  门派: {npc.data.sect}")
        print(f"  职业: {npc.data.occupation}")
        print(f"  位置: {npc.data.location}")
        print(f"  性格: {npc.data.personality}")
        print(self.colorize("─" * 60, Color.BOLD_BLUE))
        
        # 显示独立系统信息
        print(f"  {bold('当前活动:')} {status.get('current_activity', '未知')}")
        print(f"  {bold('最后行动:')} {status.get('last_action', '无')}")
        
        # 显示需求
        print(f"\n  {bold('需求状态:')}")
        needs = status.get('needs', {})
        for need_name, value in needs.items():
            bar = self._render_bar(value, 100, 20)
            cn_name = translate_need(need_name)
            print(f"    {cn_name:<12} [{bar}] {value:.1f}")

        # 显示目标
        print(f"\n  {bold('当前目标:')}")
        goals = status.get('goals', [])
        for goal in goals[:3]:  # 最多显示3个
            progress = goal.get('progress', '0%')
            completed = "✓" if goal.get('completed') else "○"
            print(f"    {completed} {goal.get('description', '未知')} ({progress})")

        # 显示性格
        print(f"\n  {bold('性格属性:')}")
        personality = status.get('personality', {})
        for trait, value in personality.items():
            bar = self._render_bar(value * 100, 100, 20)
            cn_trait = translate_personality(trait)
            print(f"    {cn_trait:<8} [{bar}] {value:.2f}")
        
        # 显示记忆和关系
        print(f"\n  {bold('记忆数量:')} {status.get('memory_count', 0)}")
        print(f"  {bold('关系数量:')} {status.get('relationship_count', 0)}")
        print(f"  {bold('总行动数:')} {status.get('total_actions', 0)}")
        
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
    
    def handle_npc_stats(self):
        """处理NPC统计命令"""
        if not self.world:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        stats = self.world.get_npc_stats()
        
        print(f"\n{self.colorize('📊 NPC独立系统统计', Color.BOLD_CYAN)}")
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
        print(f"  总NPC数: {stats.get('total_npcs', 0)}")
        print(f"  活跃NPC数: {stats.get('active_npcs', 0)}")
        print(f"  总记忆数: {stats.get('total_memories', 0)}")
        print(f"  总关系数: {stats.get('total_relationships', 0)}")
        print(f"  总行动数: {stats.get('total_actions', 0)}")
        
        # 显示区域分布
        zones = stats.get('zones', {})
        if zones:
            print(f"\n  {bold('区域分布:')}")
            for zone, count in zones.items():
                print(f"    {zone}: {count}个NPC")
        
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
    
    def _render_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """
        渲染进度条
        
        Args:
            value: 当前值
            max_value: 最大值
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        ratio = min(1.0, value / max_value) if max_value > 0 else 0
        filled = int(width * ratio)
        empty = width - filled
        return "█" * filled + "░" * empty

    def handle_npc_goals(self, npc_name: str):
        """
        处理NPC目标命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_goals <NPC名字>")
            print(warning_panel.render())
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"🎯 {npc.data.dao_name} 的目标", width=70)
        print(title_panel.render())
        
        # 获取目标列表
        goals = getattr(npc, 'goals', [])
        
        if not goals:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("暂无目标", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return
        
        # 分类目标
        active_goals = [g for g in goals if not getattr(g, 'is_completed', False) and not getattr(g, 'is_failed', False)]
        completed_goals = [g for g in goals if getattr(g, 'is_completed', False)]
        failed_goals = [g for g in goals if getattr(g, 'is_failed', False)]
        
        # 显示进行中的目标
        if active_goals:
            active_panel = UIPanel(
                title="📌 进行中",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(active_panel.render())
            
            headers = ['优先级', '类型', '描述', '进度']
            rows = []
            for goal in sorted(active_goals, key=lambda g: getattr(g, 'priority', 5), reverse=True):
                goal_type = getattr(goal, 'goal_type', '未知')
                goal_type_str = translate_goal_type(goal_type)

                priority = getattr(goal, 'priority', 5)
                priority_str = "★" * (priority // 2) + "☆" * (5 - priority // 2)

                current = getattr(goal, 'current_value', 0)
                target = getattr(goal, 'target_value', 1)
                progress = min(100, int(current / target * 100)) if target > 0 else 0
                progress_bar = self._render_bar(progress, 100, 10)
                progress_str = f"[{progress_bar}] {progress}%"

                rows.append([
                    priority_str,
                    goal_type_str[:6],
                    getattr(goal, 'description', '未知')[:20],
                    progress_str
                ])
            
            table = UITable(headers=headers, rows=rows, width=70)
            print(table.render())
        
        # 显示已完成的目标
        if completed_goals:
            completed_panel = UIPanel(
                title=f"✅ 已完成 ({len(completed_goals)}个)",
                width=70,
                border_style='rounded',
                border_color=UITheme.SUCCESS
            )
            print(completed_panel.render())
            
            for goal in completed_goals[:3]:  # 最多显示3个
                goal_type = getattr(goal, 'goal_type', '未知')
                goal_type_str = translate_goal_type(goal_type)
                desc = UIPanel(width=70, border_style='none')
                desc.add_line(f"  ✓ {getattr(goal, 'description', '未知')} [{goal_type_str}]")
                print(desc.render())
        
        # 显示失败的目标
        if failed_goals:
            failed_panel = UIPanel(
                title=f"❌ 已失败 ({len(failed_goals)}个)",
                width=70,
                border_style='rounded',
                border_color=UITheme.ERROR
            )
            print(failed_panel.render())
            
            for goal in failed_goals[:2]:  # 最多显示2个
                goal_type = getattr(goal, 'goal_type', '未知')
                goal_type_str = translate_goal_type(goal_type)
                desc = UIPanel(width=70, border_style='none')
                desc.add_line(f"  ✗ {getattr(goal, 'description', '未知')} [{goal_type_str}]")
                print(desc.render())
        
        # 统计信息
        stats_panel = UIPanel(width=70, border_style='none')
        total = len(goals)
        completion_rate = len(completed_goals) / total * 100 if total > 0 else 0
        stats_panel.add_line(f"\n总计: {total}个目标 | 完成率: {completion_rate:.1f}%")
        print(stats_panel.render())

    def handle_npc_schedule(self, npc_name: str):
        """
        处理NPC日程命令

        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return

        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_schedule <NPC名字>")
            print(warning_panel.render())
            return

        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return

        # 创建标题面板
        title_panel = UIPanel.info_panel(f"📅 {npc.data.dao_name} 的日程", width=70)
        print(title_panel.render())

        # 获取日程
        schedule = getattr(npc, 'schedule', {})

        if not schedule:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("暂无日程安排", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return

        # 获取当前时间
        import time
        current_hour = int((time.time() // 3600) % 24)

        # 查找当前活动（考虑活动持续时间）
        current_activity = None
        for hour, activity in schedule.items():
            if activity and activity.contains_hour(current_hour):
                current_activity = activity
                break

        # 显示当前活动
        if current_activity:
            current_panel = UIPanel(
                title="🔔 当前活动",
                width=70,
                border_style='rounded',
                border_color=UITheme.SUCCESS
            )

            # 使用 description 获取活动描述
            activity_desc = getattr(current_activity, 'description', '')
            if not activity_desc:
                activity_desc = getattr(current_activity, 'activity_type', None)
                if activity_desc and hasattr(activity_desc, 'value'):
                    activity_desc = activity_desc.value
                else:
                    activity_desc = '未知活动'

            # 获取活动类型的中文显示
            activity_type = getattr(current_activity, 'activity_type', None)
            activity_type_str = translate_activity_type(activity_type)

            # 获取活动时间
            start_time = getattr(current_activity, 'start_time', current_hour)
            end_time = getattr(current_activity, 'end_time', start_time + 1)

            # 获取优先级
            priority = getattr(current_activity, 'priority', 5)
            priority_str = "★" * priority + "☆" * (10 - priority)

            # 检查是否为临时活动
            is_temporary = getattr(current_activity, 'is_temporary', False)
            temp_marker = " [临时]" if is_temporary else ""

            current_panel.add_line(f"时间: {start_time:02d}:00 - {end_time:02d}:00")
            current_panel.add_line(f"活动: {colorize(activity_desc, UITheme.SUCCESS)}{colorize(temp_marker, UITheme.WARNING)}")
            current_panel.add_line(f"类型: {activity_type_str}")
            current_panel.add_line(f"优先级: {priority_str} ({priority}/10)")

            # 获取活动地点
            location = getattr(current_activity, 'location', '')
            if location:
                current_panel.add_line(f"地点: {location}")

            print(current_panel.render())

        # 显示全天日程 - 时间线样式
        schedule_panel = UIPanel(
            title="📋 今日日程时间线",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        print(schedule_panel.render())

        # 按开始时间排序的活动列表
        activities = []
        seen_activities = set()

        for hour, activity in schedule.items():
            if activity and id(activity) not in seen_activities:
                activities.append(activity)
                seen_activities.add(id(activity))

        # 按开始时间排序
        activities.sort(key=lambda x: getattr(x, 'start_time', 0))

        if activities:
            for activity in activities:
                start_time = getattr(activity, 'start_time', 0)
                end_time = getattr(activity, 'end_time', start_time + 1)
                duration = getattr(activity, 'duration', 1)

                # 判断是否为当前活动
                is_current = activity.contains_hour(current_hour)

                # 时间线符号
                if is_current:
                    timeline_icon = colorize("▶", UITheme.SUCCESS)
                    time_color = UITheme.SUCCESS
                else:
                    timeline_icon = "○"
                    time_color = UITheme.TEXT

                # 获取活动描述
                activity_desc = getattr(activity, 'description', '')
                if not activity_desc:
                    activity_type = getattr(activity, 'activity_type', None)
                    if activity_type and hasattr(activity_type, 'value'):
                        activity_desc = activity_type.value
                    else:
                        activity_desc = '未知活动'

                # 获取活动类型
                activity_type = getattr(activity, 'activity_type', None)
                activity_type_str = translate_activity_type(activity_type)

                # 获取优先级
                priority = getattr(activity, 'priority', 5)

                # 检查是否为临时活动
                is_temporary = getattr(activity, 'is_temporary', False)
                temp_marker = colorize("[临]", UITheme.WARNING) if is_temporary else "   "

                # 获取地点
                location = getattr(activity, 'location', '')
                location_str = f"📍{location}" if location else ""

                # 创建时间线条目
                time_str = f"{start_time:02d}:00-{end_time:02d}:00"

                # 构建时间线行
                activity_line = f"{timeline_icon} {colorize(time_str, time_color)} {temp_marker} {activity_desc}"
                if location_str:
                    activity_line += f" {colorize(location_str, UITheme.TEXT_DIM)}"

                # 添加优先级指示
                priority_indicator = "▲" * min(priority // 2, 5)
                if priority_indicator:
                    activity_line += f" {colorize(priority_indicator, UITheme.WARNING if priority >= 8 else UITheme.INFO)}"

                line_panel = UIPanel(width=70, border_style='none')
                line_panel.add_line(activity_line)
                print(line_panel.render())
        else:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("今日无日程安排", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())

        # 显示临时事件
        temp_events = getattr(npc, 'temp_events', [])
        if temp_events:
            events_panel = UIPanel(
                title="⚡ 临时事件",
                width=70,
                border_style='rounded',
                border_color=UITheme.WARNING
            )
            print(events_panel.render())

            for event in temp_events[:5]:  # 最多显示5个
                event_panel = UIPanel(width=70, border_style='none')
                event_desc = getattr(event, 'description', '未知事件')
                event_time = getattr(event, 'time', '未知时间')
                event_priority = getattr(event, 'priority', 5)
                priority_str = "★" * event_priority
                event_panel.add_line(f"  • {event_time}: {event_desc} {colorize(priority_str, UITheme.WARNING)}")
                print(event_panel.render())

    def handle_npc_relations(self, npc_name: str):
        """
        处理NPC关系命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_relations <NPC名字>")
            print(warning_panel.render())
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"🤝 {npc.data.dao_name} 的关系网络", width=70)
        print(title_panel.render())
        
        # 获取关系数据
        relationships = getattr(npc, 'relationships', {})
        
        if not relationships:
            # 尝试从独立系统获取
            status = npc.get_independent_status() if hasattr(npc, 'get_independent_status') else {}
            relationships = status.get('relationships', {})
        
        if not relationships:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("暂无关系数据", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return
        
        # 分类关系
        friends = []
        enemies = []
        others = []
        
        for rel_id, rel_data in relationships.items():
            if isinstance(rel_data, dict):
                affinity = rel_data.get('affinity', 0)
                hatred = rel_data.get('hatred', 0)
                rel_type = rel_data.get('relation_type', '未知')
            else:
                affinity = getattr(rel_data, 'affinity', 0)
                hatred = getattr(rel_data, 'hatred', 0)
                rel_type = getattr(rel_data, 'relation_type', '未知')
            
            rel_info = {
                'id': rel_id,
                'affinity': affinity,
                'hatred': hatred,
                'type': rel_type
            }
            
            if hatred > 20:
                enemies.append(rel_info)
            elif affinity > 0:
                friends.append(rel_info)
            else:
                others.append(rel_info)
        
        # 显示朋友列表
        if friends:
            friends_panel = UIPanel(
                title=f"😊 朋友 ({len(friends)}位)",
                width=70,
                border_style='rounded',
                border_color=UITheme.SUCCESS
            )
            print(friends_panel.render())
            
            headers = ['道友', '好感度', '关系类型', '关系度']
            rows = []
            for friend in sorted(friends, key=lambda x: x['affinity'], reverse=True)[:5]:
                affinity = friend['affinity']
                affinity_bar = self._render_bar(affinity + 100, 200, 8)
                rel_strength = "至交" if affinity >= 80 else "好友" if affinity >= 50 else "友善"
                rel_type_str = translate_relation_type(friend['type'])

                rows.append([
                    friend['id'][:8],
                    f"[{affinity_bar}]",
                    rel_type_str[:6],
                    rel_strength
                ])
            
            table = UITable(headers=headers, rows=rows, width=70)
            print(table.render())
        
        # 显示敌人列表
        if enemies:
            enemies_panel = UIPanel(
                title=f"😠 敌人 ({len(enemies)}位)",
                width=70,
                border_style='rounded',
                border_color=UITheme.ERROR
            )
            print(enemies_panel.render())
            
            headers = ['对手', '仇恨度', '关系类型', '敌意等级']
            rows = []
            for enemy in sorted(enemies, key=lambda x: x['hatred'], reverse=True)[:5]:
                hatred = enemy['hatred']
                hatred_bar = self._render_bar(hatred, 100, 8)
                hostility = "死敌" if hatred >= 80 else "仇敌" if hatred >= 50 else "厌恶"
                rel_type_str = translate_relation_type(enemy['type'])

                rows.append([
                    enemy['id'][:8],
                    f"[{hatred_bar}]",
                    rel_type_str[:6],
                    hostility
                ])
            
            table = UITable(headers=headers, rows=rows, width=70)
            print(table.render())
        
        # 显示其他关系
        if others:
            others_panel = UIPanel(
                title=f"😐 其他关系 ({len(others)}位)",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(others_panel.render())
            
            for other in others[:3]:
                other_panel = UIPanel(width=70, border_style='none')
                affinity = other['affinity']
                rel_desc = "普通" if affinity >= -20 else "冷淡"
                other_panel.add_line(f"  • {other['id'][:8]}: {rel_desc} (好感度: {affinity})")
                print(other_panel.render())
        
        # 统计信息
        stats_panel = UIPanel(width=70, border_style='none')
        total = len(friends) + len(enemies) + len(others)
        stats_panel.add_line(f"\n总计: {total}位关系人 | 朋友: {len(friends)} | 敌人: {len(enemies)}")
        print(stats_panel.render())

    def handle_npc_story(self, npc_name: str):
        """
        处理NPC故事命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_story <NPC名字>")
            print(warning_panel.render())
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"📖 {npc.data.dao_name} 的人生故事", width=70)
        print(title_panel.render())
        
        # 基本信息
        info_panel = UIPanel(
            title="👤 基本信息",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        info_panel.add_line(f"姓名: {npc.data.name}")
        info_panel.add_line(f"道号: {npc.data.dao_name}")
        info_panel.add_line(f"年龄: {npc.data.age}岁 / 寿元: {npc.data.lifespan}岁")
        info_panel.add_line(f"门派: {npc.data.sect}")
        info_panel.add_line(f"职业: {npc.data.occupation}")
        info_panel.add_line(f"当前境界: {npc.get_realm_name()}")
        print(info_panel.render())
        
        # 获取人生记录
        life_record = getattr(npc, 'life_record', None)
        
        if life_record:
            # 显示关键事件
            events = getattr(life_record, 'records', {}).get(npc.data.id, [])
            
            if events:
                events_panel = UIPanel(
                    title=f"📜 关键事件 ({len(events)}件)",
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.INFO
                )
                print(events_panel.render())
                
                # 按重要性排序，显示重要事件
                important_events = sorted(
                    events, 
                    key=lambda e: getattr(e, 'importance', 5), 
                    reverse=True
                )[:5]
                
                headers = ['时间', '类型', '事件', '重要性']
                rows = []
                for event in important_events:
                    event_type = getattr(event, 'event_type', '未知')
                    event_type_str = translate_event_type(event_type)

                    timestamp = getattr(event, 'timestamp', 0)
                    import time
                    time_str = time.strftime("%m-%d", time.localtime(timestamp)) if timestamp else "未知"

                    description = getattr(event, 'description', '未知')[:20]
                    importance = getattr(event, 'importance', 5)
                    importance_str = "★" * importance + "☆" * (10 - importance)

                    rows.append([time_str, event_type_str[:6], description, importance_str])
                
                table = UITable(headers=headers, rows=rows, width=70)
                print(table.render())
            
            # 显示修炼历程
            cultivation_events = [e for e in events if 'CULTIVATION' in str(type(e)).upper() or 
                                 (hasattr(e, 'event_type') and 'CULTIVATION' in str(e.event_type).upper())]
            
            if cultivation_events:
                cult_panel = UIPanel(
                    title="🧘 修炼历程",
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.SUCCESS
                )
                print(cult_panel.render())
                
                for event in cultivation_events[-3:]:  # 显示最近3个
                    desc = getattr(event, 'description', '未知')
                    outcome = getattr(event, 'outcome', '')
                    cult_desc = UIPanel(width=70, border_style='none')
                    cult_desc.add_line(f"  • {desc}")
                    if outcome:
                        cult_desc.add_line(f"    结果: {outcome}")
                    print(cult_desc.render())
        
        # 生成人生简介
        story_panel = UIPanel(
            title="📚 人生简介",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        
        # 根据NPC数据生成简介
        personality = npc.data.personality
        occupation = npc.data.occupation
        sect = npc.data.sect
        realm = npc.get_realm_name()
        
        story_parts = []
        story_parts.append(f"{npc.data.name}，道号{npc.data.dao_name}，")
        story_parts.append(f"{npc.data.age}岁，出身于{sect}。")
        story_parts.append(f"性格{personality}，以{occupation}为业。")
        story_parts.append(f"目前修为已达{realm}。")
        
        if life_record and events:
            story_parts.append(f"\n一生经历{len(events)}件大事，")
            if cultivation_events:
                story_parts.append(f"修炼突破{cultivation_events}次。")
        
        story_text = "".join(story_parts)
        story_panel.add_line(story_text)
        print(story_panel.render())

    def handle_npc_schedule_history(self, npc_name: str):
        """
        处理NPC日程历史命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_schedule_history <NPC名字>")
            print(warning_panel.render())
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"📜 {npc.data.dao_name} 的日程历史", width=70)
        print(title_panel.render())
        
        # 获取日程历史
        history = npc.get_schedule_history() if hasattr(npc, 'get_schedule_history') else []
        
        if not history:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("暂无日程历史记录", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return
        
        # 统计过去7天的活动
        activity_stats = {}
        daily_stats = []
        
        for schedule in history[-7:]:  # 只统计最近7天
            date = schedule.get('date', '未知日期')
            activities = schedule.get('activities', [])
            
            day_stat = {
                'date': date,
                'total_activities': len(activities),
                'total_hours': 0,
                'activity_types': {}
            }
            
            for activity in activities:
                activity_type = activity.get('activity_type', '未知')
                duration = activity.get('duration', 1)
                
                # 统计活动类型
                if activity_type not in activity_stats:
                    activity_stats[activity_type] = {'count': 0, 'hours': 0}
                activity_stats[activity_type]['count'] += 1
                activity_stats[activity_type]['hours'] += duration
                
                # 统计每日活动类型
                if activity_type not in day_stat['activity_types']:
                    day_stat['activity_types'][activity_type] = 0
                day_stat['activity_types'][activity_type] += duration
                
                day_stat['total_hours'] += duration
            
            daily_stats.append(day_stat)
        
        # 显示每日统计
        daily_panel = UIPanel(
            title=f"📅 过去{len(daily_stats)}天日程统计",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        print(daily_panel.render())
        
        headers = ['日期', '活动数', '总时长', '主要活动']
        rows = []
        for day in daily_stats:
            # 找出主要活动
            main_activity = max(day['activity_types'].items(), key=lambda x: x[1])[0] if day['activity_types'] else '无'
            main_activity_str = translate_activity_type(main_activity)
            rows.append([
                day['date'][-5:] if len(day['date']) > 5 else day['date'],
                str(day['total_activities']),
                f"{day['total_hours']}h",
                main_activity_str[:8]
            ])
        
        table = UITable(headers=headers, rows=rows, width=70)
        print(table.render())
        
        # 显示活动类型分布
        if activity_stats:
            dist_panel = UIPanel(
                title="📊 活动类型分布",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(dist_panel.render())
            
            # 按总时长排序
            sorted_activities = sorted(activity_stats.items(), key=lambda x: x[1]['hours'], reverse=True)
            
            headers = ['活动类型', '次数', '总时长', '占比']
            rows = []
            total_hours = sum(stat['hours'] for stat in activity_stats.values())
            
            for activity_type, stat in sorted_activities[:8]:  # 最多显示8种
                percentage = (stat['hours'] / total_hours * 100) if total_hours > 0 else 0
                bar = self._render_bar(percentage, 100, 8)
                activity_type_str = translate_activity_type(activity_type)
                rows.append([
                    activity_type_str[:8],
                    str(stat['count']),
                    f"{stat['hours']}h",
                    f"[{bar}] {percentage:.1f}%"
                ])
            
            table = UITable(headers=headers, rows=rows, width=70)
            print(table.render())
        
        # 显示历史详情
        history_panel = UIPanel(
            title="📋 历史日程详情",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        print(history_panel.render())
        
        # 显示最近3天的详细日程
        for day in daily_stats[-3:]:
            day_panel = UIPanel(
                title=f"📅 {day['date']}",
                width=70,
                border_style='rounded',
                border_color=UITheme.BORDER_SECONDARY
            )
            
            # 获取该日的日程
            day_schedule = None
            for schedule in history:
                if schedule.get('date') == day['date']:
                    day_schedule = schedule
                    break
            
            if day_schedule:
                activities = day_schedule.get('activities', [])
                # 按开始时间排序
                activities.sort(key=lambda x: x.get('start_time', 0))
                
                for activity in activities[:6]:  # 最多显示6个活动
                    start_time = activity.get('start_time', 0)
                    duration = activity.get('duration', 1)
                    end_time = activity.get('end_time', start_time + duration)
                    activity_type = activity.get('activity_type', '未知')
                    description = activity.get('description', activity_type)
                    location = activity.get('location', '')
                    
                    time_str = f"{start_time:02d}:00-{end_time:02d}:00"
                    location_str = f" @{location}" if location else ""
                    day_panel.add_line(f"  {time_str} {description}{location_str}")
                
                if len(activities) > 6:
                    day_panel.add_line(f"  ... 还有 {len(activities) - 6} 个活动")
            
            print(day_panel.render())
        
        # 统计摘要
        summary_panel = UIPanel(width=70, border_style='none')
        total_days = len(daily_stats)
        total_activities = sum(day['total_activities'] for day in daily_stats)
        avg_activities = total_activities / total_days if total_days > 0 else 0
        summary_panel.add_line(f"\n统计摘要: 共{total_days}天 | 总计{total_activities}个活动 | 日均{avg_activities:.1f}个")
        print(summary_panel.render())

    def handle_npc_personality(self, npc_name: str):
        """
        处理NPC个性命令
        
        Args:
            npc_name: NPC 的名字
        """
        if not self.world or not self.player:
            error_panel = UIPanel.error_panel("错误", "系统未初始化")
            print(error_panel.render())
            return
        
        if not npc_name:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line("请指定要查看的NPC")
            warning_panel.add_line("可用命令: /npc_personality <NPC名字>")
            print(warning_panel.render())
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            error_panel = UIPanel.error_panel("错误", f"未找到名为'{npc_name}'的修士")
            print(error_panel.render())
            return
        
        # 创建标题面板
        title_panel = UIPanel.info_panel(f"🎭 {npc.data.dao_name} 的个性", width=70)
        print(title_panel.render())
        
        # 显示个性描述
        personality_panel = UIPanel(
            title="📝 个性描述",
            width=70,
            border_style='rounded',
            border_color=UITheme.INFO
        )
        personality_panel.add_line(f"性格: {npc.data.personality}")
        personality_panel.add_line(f"职业: {npc.data.occupation}")
        personality_panel.add_line(f"门派: {npc.data.sect}")
        
        # 从独立系统获取性格属性
        status = npc.get_independent_status() if hasattr(npc, 'get_independent_status') else {}
        personality_traits = status.get('personality', {})
        
        if personality_traits:
            personality_panel.add_line("\n性格属性:")
            for trait, value in personality_traits.items():
                bar = self._render_bar(value * 100, 100, 15)
                cn_trait = translate_personality(trait)
                personality_panel.add_line(f"  {cn_trait:<8} [{bar}] {value:.2f}")
        
        print(personality_panel.render())
        
        # 显示价值观
        values_system = getattr(npc, 'values', None)
        if values_system:
            values_panel = UIPanel(
                title="💎 价值观",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            
            values = getattr(values_system, 'values', None)
            if values:
                values_dict = {}
                if hasattr(values, 'to_dict'):
                    values_dict = values.to_dict()
                else:
                    values_dict = {
                        'justice': getattr(values, 'justice', 50),
                        'interest': getattr(values, 'interest', 50),
                        'loyalty': getattr(values, 'loyalty', 50),
                        'freedom': getattr(values, 'freedom', 50),
                        'power': getattr(values, 'power', 50),
                    }
                
                name_map = {
                    'justice': '正义',
                    'interest': '利益',
                    'loyalty': '忠诚',
                    'freedom': '自由',
                    'power': '权力',
                }
                
                for key, name in name_map.items():
                    value = values_dict.get(key, 50)
                    bar = self._render_bar(value, 100, 15)
                    values_panel.add_line(f"  {name:<6} [{bar}] {value}")
                
                # 显示主导价值观
                if hasattr(values_system, 'get_dominant_value'):
                    dominant_name, dominant_value = values_system.get_dominant_value()
                    values_panel.add_line(f"\n主导价值观: {dominant_name} ({dominant_value})")
                
                if hasattr(values_system, 'get_value_description'):
                    value_desc = values_system.get_value_description()
                    values_panel.add_line(f"性格倾向: {value_desc}")
            
            print(values_panel.render())
        
        # 显示说话风格
        speaking_style = getattr(npc, 'speaking_style', None)
        if speaking_style:
            style_panel = UIPanel(
                title="💬 说话风格",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            
            # 获取风格信息
            style_name = getattr(speaking_style, 'name', '未知')
            style_desc = getattr(speaking_style, 'description', '')
            
            style_panel.add_line(f"风格类型: {style_name}")
            if style_desc:
                style_panel.add_line(f"风格描述: {style_desc}")
            
            # 显示风格特征
            if hasattr(speaking_style, 'style'):
                style_enum = speaking_style.style
                if hasattr(style_enum, 'value'):
                    style_panel.add_line(f"风格枚举: {style_enum.value}")
            
            # 显示常用词汇示例
            if hasattr(speaking_style, 'common_words'):
                common_words = speaking_style.common_words
                if common_words:
                    words_str = ", ".join(common_words[:6])
                    style_panel.add_line(f"\n常用词汇: {words_str}")
            
            # 显示开场白示例
            if hasattr(speaking_style, 'openings'):
                openings = speaking_style.openings
                if openings:
                    style_panel.add_line(f"开场示例: {openings[0]}")
            
            print(style_panel.render())
        
        # 如果没有详细数据，显示提示
        if not values_system and not speaking_style and not personality_traits:
            hint_panel = UIPanel(width=70, border_style='none')
            hint_panel.add_line(colorize("\n该NPC暂无详细的个性数据", UITheme.TEXT_DIM))
            hint_panel.add_line(colorize("基础性格: " + npc.data.personality, UITheme.TEXT_DIM))
            print(hint_panel.render())

    def handle_sects(self):
        """
        处理门派列表命令
        显示游戏中所有可用的门派信息，包含真实的位置和关系数据
        """
        from config import SECT_DETAILS, SECT_RELATIONSHIPS
        
        # 创建标题面板
        title_panel = UIPanel.info_panel("🏛️ 修仙门派", width=70)
        print(title_panel.render())
        
        if not SECT_DETAILS:
            empty_panel = UIPanel(width=70, border_style='none')
            empty_panel.add_line(colorize("暂无门派数据", UITheme.TEXT_DIM), align='center')
            print(empty_panel.render())
            return
        
        # 获取世界中的真实地点数据
        world_locations = {}
        if self.world:
            for loc_name, location in self.world.locations.items():
                if location.sects:
                    for sect in location.sects:
                        world_locations[sect] = {
                            'location_name': loc_name,
                            'location_desc': location.description,
                            'connections': location.connections,
                            'realm_required': location.realm_required
                        }
        
        # 按类型分类门派
        righteous_sects = []  # 正道
        evil_sects = []       # 邪道
        neutral_sects = []    # 中立
        
        for sect_name, sect_info in SECT_DETAILS.items():
            sect_type = sect_info.get('type', '中立')
            # 合并配置数据和世界数据
            merged_info = sect_info.copy()
            if sect_name in world_locations:
                merged_info['world_location'] = world_locations[sect_name]
            
            if sect_type == '正道':
                righteous_sects.append((sect_name, merged_info))
            elif sect_type == '邪道':
                evil_sects.append((sect_name, merged_info))
            else:
                neutral_sects.append((sect_name, merged_info))
        
        # 显示正道门派
        if righteous_sects:
            righteous_panel = UIPanel(
                title=f"✨ 正道门派 ({len(righteous_sects)}个)",
                width=70,
                border_style='rounded',
                border_color=UITheme.SUCCESS
            )
            print(righteous_panel.render())
            
            for sect_name, sect_info in righteous_sects:
                sect_panel = UIPanel(
                    title=sect_name,
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.INFO
                )
                
                # 显示真实位置数据
                world_loc = sect_info.get('world_location')
                if world_loc:
                    from config import get_realm_info
                    realm_info = get_realm_info(world_loc['realm_required'])
                    realm_name = realm_info.name if realm_info else "凡人"
                    sect_panel.add_line(f"📍 位置: {world_loc['location_name']}")
                    sect_panel.add_line(f"   {colorize(world_loc['location_desc'][:40], UITheme.TEXT_DIM)}")
                    sect_panel.add_line(f"   进入要求: {realm_name}")
                    if world_loc['connections']:
                        sect_panel.add_line(f"   可通往: {', '.join(world_loc['connections'][:3])}")
                else:
                    sect_panel.add_line(f"� 位置: {sect_info.get('location', '未知')}")
                
                sect_panel.add_line(f"⚔️ 实力: {sect_info.get('strength', '未知')}")
                sect_panel.add_line(f"🎯 专长: {sect_info.get('specialty', '无')}")
                sect_panel.add_line(f"📊 境界范围: {sect_info.get('realm_range', '未知')}")
                print(sect_panel.render())
        
        # 显示邪道门派
        if evil_sects:
            evil_panel = UIPanel(
                title=f"🩸 邪道门派 ({len(evil_sects)}个)",
                width=70,
                border_style='rounded',
                border_color=UITheme.ERROR
            )
            print(evil_panel.render())
            
            for sect_name, sect_info in evil_sects:
                sect_panel = UIPanel(
                    title=sect_name,
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.WARNING
                )
                
                # 显示真实位置数据
                world_loc = sect_info.get('world_location')
                if world_loc:
                    from config import get_realm_info
                    realm_info = get_realm_info(world_loc['realm_required'])
                    realm_name = realm_info.name if realm_info else "凡人"
                    sect_panel.add_line(f"📍 位置: {world_loc['location_name']}")
                    sect_panel.add_line(f"   {colorize(world_loc['location_desc'][:40], UITheme.TEXT_DIM)}")
                    sect_panel.add_line(f"   进入要求: {realm_name}")
                    if world_loc['connections']:
                        sect_panel.add_line(f"   可通往: {', '.join(world_loc['connections'][:3])}")
                else:
                    sect_panel.add_line(f"� 位置: {sect_info.get('location', '未知')}")
                
                sect_panel.add_line(f"⚔️ 实力: {sect_info.get('strength', '未知')}")
                sect_panel.add_line(f"🎯 专长: {sect_info.get('specialty', '无')}")
                sect_panel.add_line(f"📊 境界范围: {sect_info.get('realm_range', '未知')}")
                print(sect_panel.render())
        
        # 显示中立门派
        if neutral_sects:
            neutral_panel = UIPanel(
                title=f"⚖️ 中立门派 ({len(neutral_sects)}个)",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(neutral_panel.render())
            
            for sect_name, sect_info in neutral_sects:
                sect_panel = UIPanel(
                    title=sect_name,
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.BORDER_SECONDARY
                )
                
                # 显示真实位置数据
                world_loc = sect_info.get('world_location')
                if world_loc:
                    from config import get_realm_info
                    realm_info = get_realm_info(world_loc['realm_required'])
                    realm_name = realm_info.name if realm_info else "凡人"
                    sect_panel.add_line(f"📍 位置: {world_loc['location_name']}")
                    sect_panel.add_line(f"   {colorize(world_loc['location_desc'][:40], UITheme.TEXT_DIM)}")
                    sect_panel.add_line(f"   进入要求: {realm_name}")
                    if world_loc['connections']:
                        sect_panel.add_line(f"   可通往: {', '.join(world_loc['connections'][:3])}")
                else:
                    sect_panel.add_line(f"� 位置: {sect_info.get('location', '未知')}")
                
                sect_panel.add_line(f"⚔️ 实力: {sect_info.get('strength', '未知')}")
                sect_panel.add_line(f"🎯 专长: {sect_info.get('specialty', '无')}")
                sect_panel.add_line(f"📊 境界范围: {sect_info.get('realm_range', '未知')}")
                print(sect_panel.render())
        
        # 显示门派关系网络（基于真实数据）
        relations_data = []
        
        # 从配置获取关系
        if SECT_RELATIONSHIPS:
            relations_data.extend(SECT_RELATIONSHIPS)
        
        # 从世界数据推断关系（同地点的门派可能有联系）
        if self.world:
            location_sects = {}
            for loc_name, location in self.world.locations.items():
                if len(location.sects) > 1:
                    # 同一地点的多个门派标记为邻近关系
                    for i, sect1 in enumerate(location.sects):
                        for sect2 in location.sects[i+1:]:
                            if sect1 in SECT_DETAILS and sect2 in SECT_DETAILS:
                                relations_data.append({
                                    'sect1': sect1,
                                    'sect2': sect2,
                                    'relation': '邻近',
                                    'source': f'同位于{loc_name}'
                                })
        
        if relations_data:
            relations_panel = UIPanel(
                title=f"🌐 门派关系网络 ({len(relations_data)}个关系)",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(relations_panel.render())
            
            # 按关系类型分组
            friendly_relations = [r for r in relations_data if r.get('relation') in ['友好', '同盟', '合作']]
            hostile_relations = [r for r in relations_data if r.get('relation') in ['敌对', '竞争', '死敌']]
            other_relations = [r for r in relations_data if r not in friendly_relations and r not in hostile_relations]
            
            if friendly_relations:
                friendly_panel = UIPanel(
                    title=f"🤝 友好关系 ({len(friendly_relations)}个)",
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.SUCCESS
                )
                print(friendly_panel.render())
                for relation in friendly_relations[:5]:
                    rel_panel = UIPanel(width=70, border_style='none')
                    sect1 = relation.get('sect1', '未知')
                    sect2 = relation.get('sect2', '未知')
                    rel_type = relation.get('relation', '友好')
                    source = relation.get('source', '')
                    if source:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type} ({source})")
                    else:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type}")
                    print(rel_panel.render())
            
            if hostile_relations:
                hostile_panel = UIPanel(
                    title=f"⚔️ 敌对关系 ({len(hostile_relations)}个)",
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.ERROR
                )
                print(hostile_panel.render())
                for relation in hostile_relations[:5]:
                    rel_panel = UIPanel(width=70, border_style='none')
                    sect1 = relation.get('sect1', '未知')
                    sect2 = relation.get('sect2', '未知')
                    rel_type = relation.get('relation', '敌对')
                    source = relation.get('source', '')
                    if source:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type} ({source})")
                    else:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type}")
                    print(rel_panel.render())
            
            if other_relations:
                other_panel = UIPanel(
                    title=f"⚖️ 其他关系 ({len(other_relations)}个)",
                    width=70,
                    border_style='rounded',
                    border_color=UITheme.INFO
                )
                print(other_panel.render())
                for relation in other_relations[:5]:
                    rel_panel = UIPanel(width=70, border_style='none')
                    sect1 = relation.get('sect1', '未知')
                    sect2 = relation.get('sect2', '未知')
                    rel_type = relation.get('relation', '中立')
                    source = relation.get('source', '')
                    if source:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type} ({source})")
                    else:
                        rel_panel.add_line(f"  • {sect1} - {sect2}: {rel_type}")
                    print(rel_panel.render())
        
        # 显示地点-门派映射表
        if world_locations:
            map_panel = UIPanel(
                title="🗺️ 门派分布地图",
                width=70,
                border_style='rounded',
                border_color=UITheme.INFO
            )
            print(map_panel.render())
            
            # 按地点分组显示
            location_groups = {}
            for sect_name, loc_data in world_locations.items():
                loc_name = loc_data['location_name']
                if loc_name not in location_groups:
                    location_groups[loc_name] = []
                location_groups[loc_name].append(sect_name)
            
            for loc_name, sects in location_groups.items():
                loc_detail_panel = UIPanel(width=70, border_style='none')
                sects_str = ', '.join(sects)
                loc_detail_panel.add_line(f"  📍 {loc_name}: {sects_str}")
                print(loc_detail_panel.render())
        
        # 统计信息
        stats_panel = UIPanel(width=70, border_style='none')
        total = len(SECT_DETAILS)
        located_sects = len(world_locations)
        stats_panel.add_line(f"\n总计: {total}个门派 | 正道: {len(righteous_sects)} | 邪道: {len(evil_sects)} | 中立: {len(neutral_sects)}")
        stats_panel.add_line(f"已建立据点: {located_sects}个 | 分布地点: {len(location_groups) if world_locations else 0}处")
        print(stats_panel.render())
