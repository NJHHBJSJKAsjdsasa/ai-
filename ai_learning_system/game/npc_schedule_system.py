"""
NPC日程系统模块
管理NPC的日常活动安排，包括日程生成、调整、冲突解决和执行
"""

import random
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG, PERSONALITIES
from game.npc_independent import NPCIndependent, NeedType, ActivityType, NPCNeed
from game.npc_goal_system import Goal, GoalType


class ScheduleActivityType(Enum):
    """日程活动类型枚举"""
    WAKE_UP = "起床"
    CULTIVATE = "修炼"
    EAT = "吃饭"
    WORK = "工作"
    SOCIALIZE = "社交"
    EXPLORE = "探索"
    SLEEP = "睡觉"
    REST = "休息"
    CRAFT = "炼制"
    TRAVEL = "移动"


@dataclass
class Activity:
    """
    活动数据类
    
    Attributes:
        activity_type: 活动类型
        start_time: 开始时间（小时，0-23）
        duration: 持续时间（小时）
        location: 活动地点
        priority: 优先级（1-10，数字越大优先级越高）
        is_temporary: 是否为临时活动
        description: 活动描述
        related_goal: 关联目标类型（可选）
    """
    activity_type: ScheduleActivityType
    start_time: int
    duration: int
    location: str
    priority: int = 5
    is_temporary: bool = False
    description: str = ""
    related_goal: Optional[GoalType] = None
    
    def __post_init__(self):
        if not self.description:
            self.description = self.activity_type.value
        # 确保时间在有效范围内
        self.start_time = max(0, min(23, self.start_time))
        self.duration = max(1, min(24, self.duration))
        self.priority = max(1, min(10, self.priority))
    
    @property
    def end_time(self) -> int:
        """计算结束时间"""
        end = self.start_time + self.duration
        if end >= 24:
            return end - 24
        return end
    
    def overlaps_with(self, other: 'Activity') -> bool:
        """
        检查是否与另一个活动时间重叠
        
        Args:
            other: 另一个活动
            
        Returns:
            是否重叠
        """
        self_start = self.start_time
        self_end = self.end_time
        other_start = other.start_time
        other_end = other.end_time
        
        # 处理跨天的情况
        if self_start > self_end:  # 跨天
            if other_start > other_end:  # 双方都跨天
                return True
            return other_start >= self_start or other_end <= self_end
        
        if other_start > other_end:  # 对方跨天
            return self_start >= other_start or self_end <= other_end
        
        # 正常情况
        return not (self_end <= other_start or self_start >= other_end)
    
    def contains_hour(self, hour: int) -> bool:
        """
        检查指定小时是否包含在活动时间内
        
        Args:
            hour: 小时（0-23）
            
        Returns:
            是否包含
        """
        if self.start_time <= self.end_time:
            return self.start_time <= hour < self.end_time
        else:  # 跨天
            return hour >= self.start_time or hour < self.end_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "activity_type": self.activity_type.value,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_time": self.end_time,
            "location": self.location,
            "priority": self.priority,
            "is_temporary": self.is_temporary,
            "description": self.description,
            "related_goal": self.related_goal.name if self.related_goal else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """
        从字典还原Activity对象
        
        Args:
            data: 字典数据
            
        Returns:
            Activity对象
        """
        # 将activity_type字符串转换为ScheduleActivityType枚举
        activity_type_value = data.get("activity_type", "")
        activity_type = None
        for act_type in ScheduleActivityType:
            if act_type.value == activity_type_value:
                activity_type = act_type
                break
        if activity_type is None:
            activity_type = ScheduleActivityType.REST

        # 将related_goal字符串转换为GoalType枚举
        related_goal_name = data.get("related_goal")
        related_goal = None
        if related_goal_name:
            for goal_type in GoalType:
                if goal_type.name == related_goal_name:
                    related_goal = goal_type
                    break

        return cls(
            activity_type=activity_type,
            start_time=data.get("start_time", 0),
            duration=data.get("duration", 1),
            location=data.get("location", ""),
            priority=data.get("priority", 5),
            is_temporary=data.get("is_temporary", False),
            description=data.get("description", ""),
            related_goal=related_goal,
        )


@dataclass
class DailySchedule:
    """
    每日日程数据类
    
    Attributes:
        activities: 活动列表
        date: 日期标识
        npc_id: NPC ID
        is_locked: 是否锁定（防止自动调整）
    """
    activities: List[Activity] = field(default_factory=list)
    date: str = ""
    npc_id: str = ""
    is_locked: bool = False
    
    def __post_init__(self):
        if not self.date:
            self.date = time.strftime("%Y-%m-%d")
    
    def add_activity(self, activity: Activity) -> bool:
        """
        添加活动（自动检查冲突）
        
        Args:
            activity: 要添加的活动
            
        Returns:
            是否添加成功
        """
        # 检查冲突
        for existing in self.activities:
            if activity.overlaps_with(existing):
                if activity.priority <= existing.priority:
                    return False
                # 高优先级可以替换低优先级
                self.activities.remove(existing)
        
        self.activities.append(activity)
        self._sort_activities()
        return True
    
    def remove_activity(self, activity_type: ScheduleActivityType, start_time: int) -> bool:
        """
        移除指定活动
        
        Args:
            activity_type: 活动类型
            start_time: 开始时间
            
        Returns:
            是否移除成功
        """
        for activity in self.activities:
            if activity.activity_type == activity_type and activity.start_time == start_time:
                self.activities.remove(activity)
                return True
        return False
    
    def get_activity_at(self, hour: int) -> Optional[Activity]:
        """
        获取指定时间的活动
        
        Args:
            hour: 小时（0-23）
            
        Returns:
            当前活动，如果没有则返回None
        """
        for activity in self.activities:
            if activity.contains_hour(hour):
                return activity
        return None
    
    def get_activities_by_type(self, activity_type: ScheduleActivityType) -> List[Activity]:
        """
        获取指定类型的所有活动
        
        Args:
            activity_type: 活动类型
            
        Returns:
            活动列表
        """
        return [a for a in self.activities if a.activity_type == activity_type]
    
    def get_total_duration_by_type(self, activity_type: ScheduleActivityType) -> int:
        """
        获取指定类型的总时长
        
        Args:
            activity_type: 活动类型
            
        Returns:
            总时长（小时）
        """
        return sum(a.duration for a in self.activities if a.activity_type == activity_type)
    
    def has_conflicts(self) -> List[Tuple[Activity, Activity]]:
        """
        检查日程冲突
        
        Returns:
            冲突的活动对列表
        """
        conflicts = []
        for i, a1 in enumerate(self.activities):
            for a2 in self.activities[i+1:]:
                if a1.overlaps_with(a2):
                    conflicts.append((a1, a2))
        return conflicts
    
    def _sort_activities(self):
        """按开始时间排序活动"""
        self.activities.sort(key=lambda a: a.start_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "npc_id": self.npc_id,
            "date": self.date,
            "is_locked": self.is_locked,
            "activities": [a.to_dict() for a in self.activities],
        }


class NPCScheduleSystem:
    """
    NPC日程系统类
    
    管理NPC的日程生成、调整和执行
    """
    
    # 默认日程模板
    DEFAULT_SCHEDULE_TEMPLATE: List[Dict[str, Any]] = [
        {"type": ScheduleActivityType.WAKE_UP, "start": 6, "duration": 1, "priority": 10},
        {"type": ScheduleActivityType.CULTIVATE, "start": 8, "duration": 4, "priority": 7},
        {"type": ScheduleActivityType.EAT, "start": 12, "duration": 1, "priority": 9},
        {"type": ScheduleActivityType.WORK, "start": 14, "duration": 4, "priority": 6},
        {"type": ScheduleActivityType.SOCIALIZE, "start": 18, "duration": 2, "priority": 5},
        {"type": ScheduleActivityType.CULTIVATE, "start": 20, "duration": 2, "priority": 7},
        {"type": ScheduleActivityType.SLEEP, "start": 22, "duration": 8, "priority": 10},
    ]
    
    # 性格对日程的影响
    PERSONALITY_SCHEDULE_MODIFIERS = {
        "勤奋": {"cultivate_bonus": 2, "rest_penalty": 1, "work_bonus": 1},
        "懒惰": {"cultivate_penalty": 2, "rest_bonus": 2, "work_penalty": 1},
        "社交": {"social_bonus": 2, "social_priority": 1},
        "孤僻": {"social_penalty": 2, "cultivate_bonus": 1},
        "好奇": {"explore_bonus": 2, "explore_priority": 1},
        "谨慎": {"cultivate_bonus": 1, "explore_penalty": 1},
        "贪婪": {"work_bonus": 2, "wealth_focus": True},
        "善良": {"social_bonus": 1, "help_others": True},
    }
    
    def __init__(self):
        """初始化日程系统"""
        self.npc_schedules: Dict[str, DailySchedule] = {}
        self.schedule_history: Dict[str, List[DailySchedule]] = {}
        self.max_history_days = 7
    
    def generate_daily_schedule(self, npc) -> DailySchedule:
        """
        根据NPC属性生成每日日程
        
        Args:
            npc: NPC对象（需要包含independent属性）
            
        Returns:
            生成的日程
        """
        npc_id = npc.data.id
        
        # 保存旧日程到历史（如果存在）
        if npc_id in self.npc_schedules:
            old_schedule = self.npc_schedules[npc_id]
            self._add_to_history(npc_id, old_schedule)
        
        # 创建新日程
        schedule = DailySchedule(npc_id=npc_id)
        
        # 应用默认模板
        for template in self.DEFAULT_SCHEDULE_TEMPLATE:
            activity = Activity(
                activity_type=template["type"],
                start_time=template["start"],
                duration=template["duration"],
                location=npc.data.location,
                priority=template["priority"],
                description=template["type"].value
            )
            schedule.add_activity(activity)
        
        # 根据职业调整
        self._adjust_for_occupation(schedule, npc)
        
        # 根据性格调整
        self._adjust_for_personality(schedule, npc)
        
        # 根据目标调整（使用npc.goals）
        if hasattr(npc, 'goals') and npc.goals:
            self.adjust_schedule_for_goal(schedule, npc.goals)
        
        # 根据需求调整（使用npc.independent.needs，如果存在）
        if hasattr(npc, 'independent') and npc.independent:
            self.adjust_schedule_for_needs(schedule, npc.independent.needs)
        
        # 解决冲突
        self.resolve_schedule_conflicts(schedule)
        
        # 保存日程
        self.npc_schedules[npc_id] = schedule
        
        return schedule
    
    def _adjust_for_occupation(self, schedule: DailySchedule, npc):
        """
        根据职业调整日程
        
        Args:
            schedule: 日程对象
            npc: NPC对象
        """
        occupation = npc.data.occupation
        
        if "炼丹" in occupation or "炼器" in occupation:
            # 炼丹师/炼器师增加炼制时间
            self._replace_or_add_activity(schedule, Activity(
                activity_type=ScheduleActivityType.CRAFT,
                start_time=14,
                duration=3,
                location="炼丹房" if "炼丹" in occupation else "炼器室",
                priority=7,
                description=f"{occupation}工作"
            ))
        
        elif "剑修" in occupation or "体修" in occupation:
            # 战斗职业增加修炼时间
            cultivate_activities = schedule.get_activities_by_type(ScheduleActivityType.CULTIVATE)
            for activity in cultivate_activities:
                activity.duration += 1
                activity.priority = min(10, activity.priority + 1)
        
        elif "商" in occupation:
            # 商人增加工作时间
            work_activities = schedule.get_activities_by_type(ScheduleActivityType.WORK)
            for activity in work_activities:
                activity.duration += 2
                activity.priority = min(10, activity.priority + 1)
        
        elif "猎人" in occupation or "驭兽" in occupation:
            # 猎人/驭兽师增加探索时间
            self._replace_or_add_activity(schedule, Activity(
                activity_type=ScheduleActivityType.EXPLORE,
                start_time=14,
                duration=3,
                location="野外",
                priority=6,
                description="狩猎妖兽"
            ))
    
    def _adjust_for_personality(self, schedule: DailySchedule, npc):
        """
        根据性格调整日程
        
        Args:
            schedule: 日程对象
            npc: NPC对象
        """
        personality = npc.data.personality
        modifiers = self.PERSONALITY_SCHEDULE_MODIFIERS.get(personality, {})
        
        if not modifiers:
            return
        
        # 勤奋性格增加修炼时间
        if "cultivate_bonus" in modifiers:
            bonus = modifiers["cultivate_bonus"]
            cultivate_activities = schedule.get_activities_by_type(ScheduleActivityType.CULTIVATE)
            for activity in cultivate_activities:
                activity.duration = min(6, activity.duration + bonus)
                activity.priority = min(10, activity.priority + 1)
        
        # 懒惰性格减少工作时间
        if "work_penalty" in modifiers:
            work_activities = schedule.get_activities_by_type(ScheduleActivityType.WORK)
            for activity in work_activities:
                activity.duration = max(1, activity.duration - modifiers["work_penalty"])
        
        # 社交性格增加社交时间
        if "social_bonus" in modifiers:
            social_activities = schedule.get_activities_by_type(ScheduleActivityType.SOCIALIZE)
            for activity in social_activities:
                activity.duration = min(4, activity.duration + modifiers["social_bonus"])
                if "social_priority" in modifiers:
                    activity.priority = min(10, activity.priority + modifiers["social_priority"])
        
        # 孤僻性格减少社交时间
        if "social_penalty" in modifiers:
            social_activities = schedule.get_activities_by_type(ScheduleActivityType.SOCIALIZE)
            for activity in social_activities:
                activity.duration = max(0, activity.duration - modifiers["social_penalty"])
                if activity.duration == 0:
                    schedule.activities.remove(activity)
        
        # 好奇性格增加探索时间
        if "explore_bonus" in modifiers:
            self._replace_or_add_activity(schedule, Activity(
                activity_type=ScheduleActivityType.EXPLORE,
                start_time=15,
                duration=modifiers["explore_bonus"],
                location=npc.data.location,
                priority=5 + modifiers.get("explore_priority", 0),
                description="探索周围"
            ))
    
    def _replace_or_add_activity(self, schedule: DailySchedule, new_activity: Activity):
        """
        替换或添加活动
        
        Args:
            schedule: 日程对象
            new_activity: 新活动
        """
        # 尝试移除冲突的低优先级活动
        to_remove = []
        for activity in schedule.activities:
            if new_activity.overlaps_with(activity):
                if activity.priority < new_activity.priority:
                    to_remove.append(activity)
        
        for activity in to_remove:
            schedule.activities.remove(activity)
        
        schedule.add_activity(new_activity)
    
    def adjust_schedule_for_goal(self, schedule: DailySchedule, goals: List[Goal]):
        """
        根据目标调整日程
        
        Args:
            schedule: 日程对象
            goals: 目标列表
        """
        # 按优先级排序目标
        sorted_goals = sorted(goals, key=lambda g: g.get_priority_score(), reverse=True)
        
        for goal in sorted_goals:
            if goal.is_completed:
                continue
            
            # 获取目标类型值（支持枚举和字符串）
            goal_type_value = goal.goal_type.value if hasattr(goal.goal_type, 'value') else str(goal.goal_type)
            
            if goal_type_value == '突破境界':
                # 突破目标：增加修炼时间
                self._extend_activity_type(schedule, ScheduleActivityType.CULTIVATE, 2)
                # 提高修炼优先级
                for activity in schedule.get_activities_by_type(ScheduleActivityType.CULTIVATE):
                    activity.priority = min(10, activity.priority + 2)
                    activity.related_goal = GoalType.BREAKTHROUGH
            
            elif goal_type_value == '赚取灵石':
                # 财富目标：增加工作时间
                self._extend_activity_type(schedule, ScheduleActivityType.WORK, 2)
                for activity in schedule.get_activities_by_type(ScheduleActivityType.WORK):
                    activity.priority = min(10, activity.priority + 1)
                    activity.related_goal = GoalType.EARN_SPIRIT_STONES
            
            elif goal_type_value == '建立关系':
                # 关系目标：增加社交时间
                self._extend_activity_type(schedule, ScheduleActivityType.SOCIALIZE, 2)
                for activity in schedule.get_activities_by_type(ScheduleActivityType.SOCIALIZE):
                    activity.priority = min(10, activity.priority + 2)
                    activity.related_goal = GoalType.BUILD_RELATIONSHIP
            
            elif goal_type_value == '探索地点':
                # 探索目标：增加探索时间
                existing_explore = schedule.get_activities_by_type(ScheduleActivityType.EXPLORE)
                if existing_explore:
                    for activity in existing_explore:
                        activity.duration = min(4, activity.duration + 2)
                        activity.priority = min(10, activity.priority + 2)
                        activity.related_goal = GoalType.EXPLORE_LOCATION
                else:
                    # 添加探索活动
                    self._replace_or_add_activity(schedule, Activity(
                        activity_type=ScheduleActivityType.EXPLORE,
                        start_time=14,
                        duration=3,
                        location="未知区域",
                        priority=7,
                        description="探索新地点",
                        related_goal=GoalType.EXPLORE_LOCATION
                    ))
            
            elif goal_type_value == '炼丹炼器':
                # 制造目标：增加炼制时间
                existing_craft = schedule.get_activities_by_type(ScheduleActivityType.CRAFT)
                if existing_craft:
                    for activity in existing_craft:
                        activity.duration = min(5, activity.duration + 2)
                        activity.priority = min(10, activity.priority + 2)
                        activity.related_goal = GoalType.ALCHEMY
    
    def _extend_activity_type(self, schedule: DailySchedule, activity_type: ScheduleActivityType, hours: int):
        """
        延长指定类型活动的总时长
        
        Args:
            schedule: 日程对象
            activity_type: 活动类型
            hours: 要增加的小时数
        """
        activities = schedule.get_activities_by_type(activity_type)
        if activities:
            # 优先延长第一个活动
            activities[0].duration = min(8, activities[0].duration + hours)
    
    def adjust_schedule_for_needs(self, schedule: DailySchedule, needs: Dict[NeedType, NPCNeed]):
        """
        根据需求调整日程
        
        Args:
            schedule: 日程对象
            needs: 需求字典
        """
        for need_type, need in needs.items():
            if not need.is_urgent():
                continue
            
            if need_type == NeedType.HUNGER:
                # 饿了：优先安排吃饭
                eat_activities = schedule.get_activities_by_type(ScheduleActivityType.EAT)
                if eat_activities:
                    for activity in eat_activities:
                        activity.priority = 10
                else:
                    # 紧急添加吃饭时间
                    current_hour = time.localtime().tm_hour
                    meal_time = current_hour + 1 if current_hour < 23 else 12
                    self._replace_or_add_activity(schedule, Activity(
                        activity_type=ScheduleActivityType.EAT,
                        start_time=meal_time,
                        duration=1,
                        location=schedule.activities[0].location if schedule.activities else "居所",
                        priority=10,
                        is_temporary=True,
                        description="紧急用餐"
                    ))
            
            elif need_type == NeedType.ENERGY:
                # 累了：增加休息时间
                if need.value < 10:  # 非常累
                    # 立即休息
                    current_hour = time.localtime().tm_hour
                    self._replace_or_add_activity(schedule, Activity(
                        activity_type=ScheduleActivityType.REST,
                        start_time=current_hour,
                        duration=2,
                        location="居所",
                        priority=10,
                        is_temporary=True,
                        description="紧急休息"
                    ))
                else:
                    # 提前睡觉时间
                    sleep_activities = schedule.get_activities_by_type(ScheduleActivityType.SLEEP)
                    for activity in sleep_activities:
                        if activity.start_time > 18:  # 晚上才能提前
                            activity.start_time = max(18, activity.start_time - 1)
                            activity.priority = 9
            
            elif need_type == NeedType.SOCIAL:
                # 需要社交：增加社交时间
                social_activities = schedule.get_activities_by_type(ScheduleActivityType.SOCIALIZE)
                if social_activities:
                    for activity in social_activities:
                        activity.priority = 8
                        activity.duration = min(3, activity.duration + 1)
                else:
                    # 添加社交活动
                    self._replace_or_add_activity(schedule, Activity(
                        activity_type=ScheduleActivityType.SOCIALIZE,
                        start_time=19,
                        duration=2,
                        location="集市",
                        priority=8,
                        is_temporary=True,
                        description="满足社交需求"
                    ))
            
            elif need_type == NeedType.CULTIVATION:
                # 修炼欲望强烈
                cultivate_activities = schedule.get_activities_by_type(ScheduleActivityType.CULTIVATE)
                for activity in cultivate_activities:
                    activity.priority = min(10, activity.priority + 1)
    
    def get_current_activity(self, npc, hour: Optional[int] = None) -> Optional[Activity]:
        """
        获取当前时间应该进行的活动
        
        Args:
            npc: NPC对象
            hour: 指定小时（默认为当前时间）
            
        Returns:
            当前活动，如果没有则返回None
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_schedules:
            # 生成新日程
            schedule = self.generate_daily_schedule(npc)
        else:
            schedule = self.npc_schedules[npc_id]
        
        if hour is None:
            hour = time.localtime().tm_hour
        
        return schedule.get_activity_at(hour)
    
    def add_temporary_event(self, npc, event: Activity) -> bool:
        """
        添加临时日程事件
        
        Args:
            npc: NPC对象
            event: 临时事件
            
        Returns:
            是否添加成功
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_schedules:
            self.generate_daily_schedule(npc)
        
        schedule = self.npc_schedules[npc_id]
        event.is_temporary = True
        
        return schedule.add_activity(event)
    
    def resolve_schedule_conflicts(self, schedule: DailySchedule) -> List[Tuple[Activity, Activity]]:
        """
        解决日程冲突
        
        策略：
        1. 优先保留高优先级活动
        2. 临时活动优先于常规活动（同优先级时）
        3. 睡眠和吃饭优先于其他活动
        
        Args:
            schedule: 日程对象
            
        Returns:
            解决的冲突列表
        """
        conflicts = schedule.has_conflicts()
        resolved = []
        
        for a1, a2 in conflicts:
            # 确定保留哪个活动
            keep_a1 = False
            
            # 比较优先级
            if a1.priority > a2.priority:
                keep_a1 = True
            elif a1.priority == a2.priority:
                # 同优先级：临时活动优先
                if a1.is_temporary and not a2.is_temporary:
                    keep_a1 = True
                # 睡眠和吃饭优先
                elif a1.activity_type in [ScheduleActivityType.SLEEP, ScheduleActivityType.EAT]:
                    keep_a1 = True
            
            # 移除被放弃的活动
            if keep_a1:
                if a2 in schedule.activities:
                    schedule.activities.remove(a2)
                    resolved.append((a1, a2))
            else:
                if a1 in schedule.activities:
                    schedule.activities.remove(a1)
                    resolved.append((a2, a1))
        
        # 重新排序
        schedule._sort_activities()
        
        return resolved
    
    def execute_schedule(self, npc) -> Dict[str, Any]:
        """
        执行日程
        
        Args:
            npc: NPC对象
            
        Returns:
            执行结果
        """
        npc_id = npc.data.id
        independent = npc.independent
        
        # 获取当前活动
        current_hour = time.localtime().tm_hour
        activity = self.get_current_activity(npc, current_hour)
        
        if not activity:
            return {
                "success": False,
                "message": "当前没有安排活动",
                "activity": None,
                "effects": {}
            }
        
        # 执行活动效果
        effects = self._execute_activity_effect(npc, activity)
        
        # 更新独立系统状态
        self._update_independent_state(independent, activity)
        
        return {
            "success": True,
            "message": f"执行活动: {activity.description}",
            "activity": activity.to_dict(),
            "effects": effects
        }

    def execute_schedule_with_effects(self, npc, hour: Optional[int] = None) -> Dict[str, Any]:
        """
        执行日程并应用实际效果到NPC
        
        Args:
            npc: NPC对象
            hour: 指定小时（默认为当前时间）
            
        Returns:
            执行结果，包含应用的效果
        """
        npc_id = npc.data.id
        independent = npc.independent
        
        # 获取当前活动
        if hour is None:
            hour = time.localtime().tm_hour
        activity = self.get_current_activity(npc, hour)
        
        if not activity:
            return {
                "success": False,
                "message": "当前没有安排活动",
                "activity": None,
                "effects_applied": False,
                "effects": {}
            }
        
        # 应用活动效果到NPC
        effects = self.apply_activity_effects(npc, activity)
        
        # 更新独立系统状态
        self._update_independent_state(independent, activity)
        
        return {
            "success": True,
            "message": f"执行活动: {activity.description}",
            "activity": activity.to_dict(),
            "effects_applied": True,
            "effects": effects
        }

    def apply_activity_effects(self, npc, activity: Activity) -> Dict[str, Any]:
        """
        将活动效果应用到NPC状态
        
        效果包括：
        - 修炼：增加修为
        - 工作：赚取灵石
        - 吃饭：恢复饥饿
        - 睡觉：恢复精力
        - 社交：恢复社交需求
        - 探索：可能发现物品
        - 炼制：增加制造进度
        - 休息：恢复少量精力
        
        Args:
            npc: NPC对象
            activity: 活动对象
            
        Returns:
            应用的效果字典
        """
        effects = {
            "activity_type": activity.activity_type.value,
            "duration": activity.duration,
            "changes": {}
        }
        
        activity_type = activity.activity_type
        duration = activity.duration
        independent = npc.independent
        
        if activity_type == ScheduleActivityType.CULTIVATE:
            # 修炼：增加修为
            base_exp = 10 * duration
            # 勤奋性格加成
            if hasattr(npc.data, 'personality') and npc.data.personality == "勤奋":
                base_exp = int(base_exp * 1.2)
            
            # 应用到NPC修为
            if hasattr(npc.data, 'cultivation'):
                old_exp = getattr(npc.data.cultivation, 'exp', 0)
                if hasattr(npc.data.cultivation, 'exp'):
                    npc.data.cultivation.exp += base_exp
                effects["changes"]["exp_gain"] = base_exp
            else:
                effects["changes"]["exp_gain"] = base_exp
            
            # 减少修炼需求
            if NeedType.CULTIVATION in independent.needs:
                independent.needs[NeedType.CULTIVATION].value = max(0, independent.needs[NeedType.CULTIVATION].value - 20 * duration)
            
            # 消耗精力
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value = max(0, independent.needs[NeedType.ENERGY].value - 10 * duration)
            
            effects["message"] = f"修炼了{duration}小时，修为增加{base_exp}点"
        
        elif activity_type == ScheduleActivityType.WORK:
            # 工作：赚取灵石
            base_income = 5 * duration
            if hasattr(npc.data, 'occupation') and "商" in npc.data.occupation:
                base_income = int(base_income * 1.5)
            
            # 应用到NPC灵石
            if hasattr(npc.data, 'spirit_stones'):
                npc.data.spirit_stones += base_income
            elif hasattr(npc.data, 'inventory'):
                if hasattr(npc.data.inventory, 'spirit_stones'):
                    npc.data.inventory.spirit_stones += base_income
                elif isinstance(npc.data.inventory, dict):
                    npc.data.inventory["spirit_stones"] = npc.data.inventory.get("spirit_stones", 0) + base_income
            
            effects["changes"]["spirit_stones"] = base_income
            
            # 消耗精力
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value = max(0, independent.needs[NeedType.ENERGY].value - 15 * duration)
            
            effects["message"] = f"工作了{duration}小时，赚取{base_income}灵石"
        
        elif activity_type == ScheduleActivityType.EAT:
            # 吃饭：恢复饥饿
            hunger_recovery = 50
            
            # 应用到NPC饥饿状态
            if NeedType.HUNGER in independent.needs:
                old_hunger = independent.needs[NeedType.HUNGER].value
                independent.needs[NeedType.HUNGER].value = max(0, old_hunger - hunger_recovery)
                effects["changes"]["hunger_reduction"] = hunger_recovery
            
            effects["message"] = "饱餐一顿，饥饿感消失"
        
        elif activity_type == ScheduleActivityType.SLEEP:
            # 睡觉：恢复精力
            energy_recovery = 30 * duration
            
            # 应用到NPC精力
            if NeedType.ENERGY in independent.needs:
                old_energy = independent.needs[NeedType.ENERGY].value
                independent.needs[NeedType.ENERGY].value = min(100, old_energy + energy_recovery)
                effects["changes"]["energy_recovery"] = energy_recovery
            
            effects["message"] = f"睡眠{duration}小时，精力充沛"
        
        elif activity_type == ScheduleActivityType.SOCIALIZE:
            # 社交：恢复社交需求
            social_recovery = 40
            
            # 应用到NPC社交需求
            if NeedType.SOCIAL in independent.needs:
                old_social = independent.needs[NeedType.SOCIAL].value
                independent.needs[NeedType.SOCIAL].value = max(0, old_social - social_recovery)
                effects["changes"]["social_reduction"] = social_recovery
            
            effects["message"] = "与他人交流，心情愉悦，社交需求得到满足"
        
        elif activity_type == ScheduleActivityType.EXPLORE:
            # 探索：可能发现物品或事件
            effects["changes"]["explore_progress"] = duration
            
            # 消耗精力
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value = max(0, independent.needs[NeedType.ENERGY].value - 10 * duration)
            
            # 随机发现
            if random.random() < 0.3:
                discovery = "发现了一些有趣的东西"
                effects["changes"]["discovery"] = discovery
                effects["message"] = f"探索了{duration}小时，{discovery}"
            else:
                effects["message"] = f"探索了{duration}小时"
        
        elif activity_type == ScheduleActivityType.CRAFT:
            # 炼制：增加制造进度
            craft_progress = duration * 10
            effects["changes"]["craft_progress"] = craft_progress
            
            # 消耗精力
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value = max(0, independent.needs[NeedType.ENERGY].value - 20 * duration)
            
            effects["message"] = f"炼制了{duration}小时，进度增加{craft_progress}"
        
        elif activity_type == ScheduleActivityType.REST:
            # 休息：恢复少量精力
            energy_recovery = 20 * duration
            
            # 应用到NPC精力
            if NeedType.ENERGY in independent.needs:
                old_energy = independent.needs[NeedType.ENERGY].value
                independent.needs[NeedType.ENERGY].value = min(100, old_energy + energy_recovery)
                effects["changes"]["energy_recovery"] = energy_recovery
            
            effects["message"] = f"休息了{duration}小时，精力有所恢复"
        
        elif activity_type == ScheduleActivityType.WAKE_UP:
            effects["message"] = "起床开始新的一天"
        
        elif activity_type == ScheduleActivityType.TRAVEL:
            effects["message"] = f"移动中，耗时{duration}小时"
        
        else:
            effects["message"] = f"进行{activity.description}"
        
        return effects
    
    def _execute_activity_effect(self, npc, activity: Activity) -> Dict[str, Any]:
        """
        执行活动效果
        
        Args:
            npc: NPC对象
            activity: 活动
            
        Returns:
            效果字典
        """
        effects = {}
        activity_type = activity.activity_type
        
        if activity_type == ScheduleActivityType.CULTIVATE:
            # 修炼：增加修为
            base_exp = 10 * activity.duration
            # 勤奋性格加成
            if npc.data.personality == "勤奋":
                base_exp = int(base_exp * 1.2)
            effects["exp_gain"] = base_exp
            effects["message"] = f"修炼了{activity.duration}小时，修为增加{base_exp}点"
        
        elif activity_type == ScheduleActivityType.WORK:
            # 工作：赚取灵石
            base_income = 5 * activity.duration
            if "商" in npc.data.occupation:
                base_income = int(base_income * 1.5)
            effects["spirit_stones"] = base_income
            effects["message"] = f"工作了{activity.duration}小时，赚取{base_income}灵石"
        
        elif activity_type == ScheduleActivityType.EAT:
            # 吃饭：恢复饥饿度
            effects["hunger_reduction"] = 50
            effects["message"] = "饱餐一顿"
        
        elif activity_type == ScheduleActivityType.SLEEP:
            # 睡觉：恢复精力
            effects["energy_recovery"] = 30 * activity.duration
            effects["message"] = f"睡眠{activity.duration}小时，精力充沛"
        
        elif activity_type == ScheduleActivityType.SOCIALIZE:
            # 社交：满足社交需求
            effects["social_reduction"] = 40
            effects["message"] = "与他人交流，心情愉悦"
        
        elif activity_type == ScheduleActivityType.EXPLORE:
            # 探索：可能发现物品或事件
            effects["explore_progress"] = activity.duration
            if random.random() < 0.3:
                effects["discovery"] = "发现了一些有趣的东西"
            effects["message"] = f"探索了{activity.duration}小时"
        
        elif activity_type == ScheduleActivityType.CRAFT:
            # 炼制：增加制造进度
            effects["craft_progress"] = activity.duration * 10
            effects["message"] = f"炼制了{activity.duration}小时"
        
        elif activity_type == ScheduleActivityType.REST:
            # 休息：恢复少量精力
            effects["energy_recovery"] = 20 * activity.duration
            effects["message"] = f"休息了{activity.duration}小时"
        
        else:
            effects["message"] = f"进行{activity.description}"
        
        return effects
    
    def _update_independent_state(self, independent: NPCIndependent, activity: Activity):
        """
        更新独立系统状态
        
        Args:
            independent: NPC独立系统
            activity: 活动
        """
        activity_type = activity.activity_type
        
        # 更新当前活动
        if activity_type == ScheduleActivityType.CULTIVATE:
            independent.current_activity = ActivityType.CULTIVATE
            if NeedType.CULTIVATION in independent.needs:
                independent.needs[NeedType.CULTIVATION].value = max(0, independent.needs[NeedType.CULTIVATION].value - 20)
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value -= 10
        
        elif activity_type == ScheduleActivityType.EAT:
            independent.current_activity = ActivityType.EAT
            if NeedType.HUNGER in independent.needs:
                independent.needs[NeedType.HUNGER].value = max(0, independent.needs[NeedType.HUNGER].value - 50)
        
        elif activity_type == ScheduleActivityType.SLEEP:
            independent.current_activity = ActivityType.REST
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value = min(100, independent.needs[NeedType.ENERGY].value + 30)
        
        elif activity_type == ScheduleActivityType.SOCIALIZE:
            independent.current_activity = ActivityType.SOCIALIZE
            if NeedType.SOCIAL in independent.needs:
                independent.needs[NeedType.SOCIAL].value = max(0, independent.needs[NeedType.SOCIAL].value - 30)
        
        elif activity_type == ScheduleActivityType.WORK:
            independent.current_activity = ActivityType.WORK
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value -= 15
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
        
        elif activity_type == ScheduleActivityType.EXPLORE:
            independent.current_activity = ActivityType.EXPLORE
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value -= 10
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
        
        elif activity_type == ScheduleActivityType.CRAFT:
            independent.current_activity = ActivityType.WORK
            if NeedType.ENERGY in independent.needs:
                independent.needs[NeedType.ENERGY].value -= 20
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
        
        else:
            independent.current_activity = ActivityType.IDLE
    
    def _add_to_history(self, npc_id: str, schedule: DailySchedule):
        """
        添加日程到历史记录
        
        Args:
            npc_id: NPC ID
            schedule: 日程
        """
        if npc_id not in self.schedule_history:
            self.schedule_history[npc_id] = []
        
        self.schedule_history[npc_id].append(schedule)
        
        # 限制历史记录数量
        if len(self.schedule_history[npc_id]) > self.max_history_days:
            self.schedule_history[npc_id] = self.schedule_history[npc_id][-self.max_history_days:]
    
    @staticmethod
    def activity_from_dict(data: Dict[str, Any]) -> Activity:
        """
        从字典还原Activity对象的静态方法
        
        Args:
            data: 字典数据
            
        Returns:
            Activity对象
        """
        return Activity.from_dict(data)

    def get_schedule(self, npc_id: str) -> Optional[DailySchedule]:
        """
        获取NPC的当前日程
        
        Args:
            npc_id: NPC ID
            
        Returns:
            日程对象，如果没有则返回None
        """
        return self.npc_schedules.get(npc_id)
    
    def get_schedule_history(self, npc_id: str) -> List[DailySchedule]:
        """
        获取NPC的日程历史
        
        Args:
            npc_id: NPC ID
            
        Returns:
            日程历史列表
        """
        return self.schedule_history.get(npc_id, [])
    
    def clear_schedule(self, npc_id: str):
        """
        清除NPC的日程
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.npc_schedules:
            del self.npc_schedules[npc_id]
    
    def lock_schedule(self, npc_id: str) -> bool:
        """
        锁定NPC日程（防止自动调整）
        
        Args:
            npc_id: NPC ID
            
        Returns:
            是否成功锁定
        """
        if npc_id in self.npc_schedules:
            self.npc_schedules[npc_id].is_locked = True
            return True
        return False
    
    def unlock_schedule(self, npc_id: str) -> bool:
        """
        解锁NPC日程
        
        Args:
            npc_id: NPC ID
            
        Returns:
            是否成功解锁
        """
        if npc_id in self.npc_schedules:
            self.npc_schedules[npc_id].is_locked = False
            return True
        return False
    
    def get_daily_stats(self, npc_id: str) -> Dict[str, Any]:
        """
        获取NPC的每日活动统计
        
        Args:
            npc_id: NPC ID
            
        Returns:
            统计信息字典
        """
        schedule = self.npc_schedules.get(npc_id)
        if not schedule:
            return {}
        
        stats = {
            "total_activities": len(schedule.activities),
            "total_hours": sum(a.duration for a in schedule.activities),
            "activity_breakdown": {},
            "priority_distribution": {"high": 0, "medium": 0, "low": 0},
        }
        
        for activity in schedule.activities:
            # 活动类型统计
            type_name = activity.activity_type.value
            if type_name not in stats["activity_breakdown"]:
                stats["activity_breakdown"][type_name] = {"count": 0, "hours": 0}
            stats["activity_breakdown"][type_name]["count"] += 1
            stats["activity_breakdown"][type_name]["hours"] += activity.duration
            
            # 优先级分布
            if activity.priority >= 8:
                stats["priority_distribution"]["high"] += 1
            elif activity.priority >= 5:
                stats["priority_distribution"]["medium"] += 1
            else:
                stats["priority_distribution"]["low"] += 1
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "npc_schedules": {
                npc_id: schedule.to_dict()
                for npc_id, schedule in self.npc_schedules.items()
            },
            "schedule_history": {
                npc_id: [s.to_dict() for s in history]
                for npc_id, history in self.schedule_history.items()
            },
        }


# 全局日程系统实例
schedule_system = NPCScheduleSystem()


def get_schedule_system() -> NPCScheduleSystem:
    """获取全局日程系统实例"""
    return schedule_system
