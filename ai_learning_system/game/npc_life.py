"""
NPC生活系统模块
实现NPC的日程、目标和决策逻辑
"""

import random
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG


class ActivityType(Enum):
    """NPC活动类型"""
    CULTIVATION = auto()    # 修炼
    WORK = auto()           # 工作
    REST = auto()           # 休息
    SOCIAL = auto()         # 社交
    EXPLORE = auto()        # 探索
    TRAVEL = auto()         # 旅行
    SHOP = auto()           # 购物
    EAT = auto()            # 进食


class GoalType(Enum):
    """NPC目标类型"""
    CULTIVATION = auto()    # 修炼目标（突破境界）
    WEALTH = auto()         # 财富目标（赚取灵石）
    SOCIAL = auto()         # 社交目标（建立关系）
    EXPLORATION = auto()    # 探索目标（发现新地点）
    CRAFTING = auto()       # 制造目标（炼丹、炼器）


@dataclass
class NPCActivity:
    """NPC活动"""
    activity_type: ActivityType
    start_hour: int         # 开始时间（0-23）
    duration: int           # 持续时间（小时）
    location: str           # 活动地点
    description: str        # 活动描述
    
    def is_active(self, current_hour: int) -> bool:
        """检查活动是否在进行中"""
        end_hour = (self.start_hour + self.duration) % 24
        if self.start_hour + self.duration < 24:
            return self.start_hour <= current_hour < end_hour
        else:
            return current_hour >= self.start_hour or current_hour < end_hour


@dataclass
class NPCGoal:
    """NPC目标"""
    goal_type: GoalType
    description: str
    target_value: int
    current_value: int = 0
    deadline_days: int = -1  # -1表示无期限
    priority: int = 5        # 优先级（1-10）
    is_completed: bool = False
    
    def update_progress(self, value: int):
        """更新进度"""
        self.current_value += value
        if self.current_value >= self.target_value:
            self.current_value = self.target_value
            self.is_completed = True
    
    def get_progress(self) -> float:
        """获取进度百分比"""
        if self.target_value <= 0:
            return 1.0
        return min(1.0, self.current_value / self.target_value)


@dataclass
class NPCState:
    """NPC状态"""
    mood: int = 50          # 心情（0-100）
    health: int = 100       # 健康（0-100）
    energy: int = 100       # 精力（0-100）
    hunger: int = 0         # 饥饿（0-100）
    
    def update(self, activity: ActivityType, hours: int = 1):
        """根据活动更新状态"""
        if activity == ActivityType.CULTIVATION:
            self.energy -= 5 * hours
            self.hunger += 3 * hours
            if self.energy < 30:
                self.mood -= 2 * hours
        elif activity == ActivityType.WORK:
            self.energy -= 8 * hours
            self.hunger += 5 * hours
            self.mood -= 1 * hours
        elif activity == ActivityType.REST:
            self.energy = min(100, self.energy + 15 * hours)
            self.hunger += 2 * hours
            self.mood = min(100, self.mood + 2 * hours)
        elif activity == ActivityType.SOCIAL:
            self.energy -= 3 * hours
            self.hunger += 4 * hours
            self.mood = min(100, self.mood + 5 * hours)
        elif activity == ActivityType.EAT:
            self.hunger = max(0, self.hunger - 30 * hours)
            self.energy = min(100, self.energy + 5 * hours)
            self.mood = min(100, self.mood + 3 * hours)
        
        # 限制范围
        self.mood = max(0, min(100, self.mood))
        self.health = max(0, min(100, self.health))
        self.energy = max(0, min(100, self.energy))
        self.hunger = max(0, min(100, self.hunger))
    
    def needs_rest(self) -> bool:
        """是否需要休息"""
        return self.energy < 20 or self.health < 30
    
    def needs_food(self) -> bool:
        """是否需要进食"""
        return self.hunger > 70


class NPCLifeSystem:
    """NPC生活系统"""
    
    def __init__(self, npc_data: Dict[str, Any]):
        """
        初始化NPC生活系统
        
        Args:
            npc_data: NPC基础数据
        """
        self.npc_data = npc_data
        self.state = NPCState()
        self.schedule: List[NPCActivity] = []
        self.goals: List[NPCGoal] = []
        self.current_activity: Optional[NPCActivity] = None
        
        # 生成初始日程和目标
        self._generate_schedule()
        self._generate_goals()
    
    def _generate_schedule(self):
        """生成NPC日程"""
        occupation = self.npc_data.get("occupation", "散修")
        personality = self.npc_data.get("personality", "")
        
        # 根据职业生成日程
        if "炼丹" in occupation or "炼器" in occupation:
            self.schedule = self._generate_crafter_schedule()
        elif "商" in occupation:
            self.schedule = self._generate_merchant_schedule()
        elif "猎" in occupation or "渔" in occupation:
            self.schedule = self._generate_hunter_schedule()
        else:
            self.schedule = self._generate_cultivator_schedule()
        
        # 根据性格调整
        if "勤奋" in personality or "刻苦" in personality:
            # 增加修炼时间
            self._add_extra_cultivation()
        elif "懒惰" in personality or "懒散" in personality:
            # 增加休息时间
            self._add_extra_rest()
    
    def _generate_cultivator_schedule(self) -> List[NPCActivity]:
        """生成修炼者日程"""
        return [
            NPCActivity(ActivityType.REST, 0, 6, "居所", "睡眠休息"),
            NPCActivity(ActivityType.CULTIVATION, 6, 4, "修炼室", "晨间修炼"),
            NPCActivity(ActivityType.EAT, 10, 1, "食堂", "进食"),
            NPCActivity(ActivityType.WORK, 11, 3, "工作地点", "门派任务"),
            NPCActivity(ActivityType.EAT, 14, 1, "食堂", "进食"),
            NPCActivity(ActivityType.CULTIVATION, 15, 4, "修炼室", "下午修炼"),
            NPCActivity(ActivityType.SOCIAL, 19, 2, "公共区域", "与同门交流"),
            NPCActivity(ActivityType.EAT, 21, 1, "食堂", "进食"),
            NPCActivity(ActivityType.REST, 22, 2, "居所", "休息准备入睡"),
        ]
    
    def _generate_crafter_schedule(self) -> List[NPCActivity]:
        """生成工匠日程"""
        return [
            NPCActivity(ActivityType.REST, 0, 5, "居所", "睡眠休息"),
            NPCActivity(ActivityType.CULTIVATION, 5, 2, "修炼室", "晨间修炼"),
            NPCActivity(ActivityType.EAT, 7, 1, "食堂", "进食"),
            NPCActivity(ActivityType.WORK, 8, 6, "工坊", "炼丹/炼器"),
            NPCActivity(ActivityType.EAT, 14, 1, "食堂", "进食"),
            NPCActivity(ActivityType.WORK, 15, 4, "工坊", "继续工作"),
            NPCActivity(ActivityType.SHOP, 19, 2, "坊市", "出售商品"),
            NPCActivity(ActivityType.EAT, 21, 1, "食堂", "进食"),
            NPCActivity(ActivityType.REST, 22, 2, "居所", "休息"),
        ]
    
    def _generate_merchant_schedule(self) -> List[NPCActivity]:
        """生成商人日程"""
        return [
            NPCActivity(ActivityType.REST, 0, 5, "居所", "睡眠休息"),
            NPCActivity(ActivityType.EAT, 7, 1, "食堂", "进食"),
            NPCActivity(ActivityType.WORK, 8, 8, "店铺", "经营店铺"),
            NPCActivity(ActivityType.EAT, 16, 1, "食堂", "进食"),
            NPCActivity(ActivityType.SHOP, 17, 3, "坊市", "采购货物"),
            NPCActivity(ActivityType.SOCIAL, 20, 2, "酒馆", "与客户应酬"),
            NPCActivity(ActivityType.EAT, 22, 1, "食堂", "进食"),
            NPCActivity(ActivityType.REST, 23, 1, "居所", "休息"),
        ]
    
    def _generate_hunter_schedule(self) -> List[NPCActivity]:
        """生成猎人日程"""
        return [
            NPCActivity(ActivityType.REST, 0, 4, "居所", "睡眠休息"),
            NPCActivity(ActivityType.EXPLORE, 4, 6, "野外", "清晨狩猎"),
            NPCActivity(ActivityType.EAT, 10, 1, "野外", "进食"),
            NPCActivity(ActivityType.EXPLORE, 11, 4, "野外", "继续狩猎"),
            NPCActivity(ActivityType.EAT, 15, 1, "居所", "进食休息"),
            NPCActivity(ActivityType.WORK, 16, 3, "坊市", "出售猎物"),
            NPCActivity(ActivityType.CULTIVATION, 19, 3, "修炼室", "晚间修炼"),
            NPCActivity(ActivityType.EAT, 22, 1, "食堂", "进食"),
            NPCActivity(ActivityType.REST, 23, 1, "居所", "休息"),
        ]
    
    def _add_extra_cultivation(self):
        """增加额外修炼时间"""
        # 找到休息时段，减少休息增加修炼
        for activity in self.schedule:
            if activity.activity_type == ActivityType.REST and activity.duration > 2:
                activity.duration -= 1
                self.schedule.append(NPCActivity(
                    ActivityType.CULTIVATION,
                    (activity.start_hour + activity.duration) % 24,
                    1,
                    "修炼室",
                    "额外修炼"
                ))
                break
    
    def _add_extra_rest(self):
        """增加额外休息时间"""
        for activity in self.schedule:
            if activity.activity_type == ActivityType.CULTIVATION and activity.duration > 2:
                activity.duration -= 1
                break
    
    def _generate_goals(self):
        """生成NPC目标"""
        realm_level = self.npc_data.get("realm_level", 0)
        personality = self.npc_data.get("personality", "")
        occupation = self.npc_data.get("occupation", "散修")
        
        # 主要目标：突破境界
        self.goals.append(NPCGoal(
            GoalType.CULTIVATION,
            f"突破到下一境界",
            1000,
            0,
            priority=10
        ))
        
        # 根据职业添加目标
        if "商" in occupation:
            self.goals.append(NPCGoal(
                GoalType.WEALTH,
                f"赚取1000灵石",
                1000,
                self.npc_data.get("spirit_stones", 0),
                priority=7
            ))
        elif "炼丹" in occupation:
            self.goals.append(NPCGoal(
                GoalType.CRAFTING,
                f"炼制100颗丹药",
                100,
                0,
                priority=8
            ))
        
        # 根据性格添加目标
        if "好奇" in personality or "求知" in personality:
            self.goals.append(NPCGoal(
                GoalType.EXPLORATION,
                f"探索3个新地点",
                3,
                0,
                priority=6
            ))
        
        # 社交目标（大多数人都有）
        self.goals.append(NPCGoal(
            GoalType.SOCIAL,
            f"结交5位好友",
            5,
            0,
            priority=5
        ))
        
        # 按优先级排序
        self.goals.sort(key=lambda g: g.priority, reverse=True)
    
    def get_current_activity(self, current_hour: int) -> Optional[NPCActivity]:
        """
        获取当前活动
        
        Args:
            current_hour: 当前小时（0-23）
            
        Returns:
            当前活动，如果没有则返回None
        """
        for activity in self.schedule:
            if activity.is_active(current_hour):
                return activity
        return None
    
    def decide_next_action(self, current_hour: int, environment: Dict[str, Any]) -> str:
        """
        决定下一步行动
        
        Args:
            current_hour: 当前小时
            environment: 环境信息
            
        Returns:
            行动描述
        """
        # 检查基本需求
        if self.state.needs_rest():
            return "感到疲惫，决定休息恢复精力"
        
        if self.state.needs_food():
            return "感到饥饿，准备进食"
        
        # 获取当前活动
        activity = self.get_current_activity(current_hour)
        if activity:
            # 根据活动类型执行
            if activity.activity_type == ActivityType.CULTIVATION:
                return f"正在{activity.location}{activity.description}"
            elif activity.activity_type == ActivityType.WORK:
                return f"正在{activity.location}工作"
            elif activity.activity_type == ActivityType.SOCIAL:
                return f"正在{activity.location}与人交流"
            elif activity.activity_type == ActivityType.EXPLORE:
                return f"正在{activity.location}探索"
            else:
                return f"正在{activity.description}"
        
        # 没有安排活动时，根据目标决定
        active_goals = [g for g in self.goals if not g.is_completed]
        if active_goals:
            top_goal = active_goals[0]
            if top_goal.goal_type == GoalType.CULTIVATION:
                return "决定利用空闲时间修炼"
            elif top_goal.goal_type == GoalType.WEALTH:
                return "决定去寻找赚钱的机会"
            elif top_goal.goal_type == GoalType.SOCIAL:
                return "决定去找人交流增进关系"
        
        return "正在休息"
    
    def update(self, hours: int = 1, current_hour: int = 8):
        """
        更新NPC状态
        
        Args:
            hours: 经过的小时数
            current_hour: 当前小时
        """
        # 获取当前活动并更新状态
        activity = self.get_current_activity(current_hour)
        if activity:
            self.state.update(activity.activity_type, hours)
            self.current_activity = activity
            
            # 更新目标进度
            self._update_goal_progress(activity.activity_type, hours)
        else:
            # 默认休息
            self.state.update(ActivityType.REST, hours)
    
    def _update_goal_progress(self, activity_type: ActivityType, hours: int):
        """更新目标进度"""
        for goal in self.goals:
            if goal.is_completed:
                continue
            
            if goal.goal_type == GoalType.CULTIVATION and activity_type == ActivityType.CULTIVATION:
                goal.update_progress(10 * hours)
            elif goal.goal_type == GoalType.WEALTH and activity_type == ActivityType.WORK:
                goal.update_progress(5 * hours)
            elif goal.goal_type == GoalType.CRAFTING and activity_type == ActivityType.WORK:
                goal.update_progress(1 * hours)
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        lines = [
            f"状态：心情{self.state.mood}/健康{self.state.health}/精力{self.state.energy}/饥饿{self.state.hunger}",
        ]
        
        if self.current_activity:
            lines.append(f"当前活动：{self.current_activity.description}")
        
        # 显示主要目标
        active_goals = [g for g in self.goals if not g.is_completed][:2]
        if active_goals:
            lines.append("当前目标：")
            for goal in active_goals:
                progress = goal.get_progress() * 100
                lines.append(f"  - {goal.description} ({progress:.0f}%)")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "state": {
                "mood": self.state.mood,
                "health": self.state.health,
                "energy": self.state.energy,
                "hunger": self.state.hunger,
            },
            "goals": [
                {
                    "goal_type": g.goal_type.name,
                    "description": g.description,
                    "target_value": g.target_value,
                    "current_value": g.current_value,
                    "is_completed": g.is_completed,
                }
                for g in self.goals
            ],
        }
