"""
NPC目标系统模块
管理NPC的目标生成、进度追踪和完成处理
"""

import random
import time
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from .npc import NPC


class GoalType(Enum):
    """目标类型枚举"""
    BREAKTHROUGH = "突破境界"      # 突破到更高境界
    EARN_SPIRIT_STONES = "赚取灵石"  # 赚取灵石
    BUILD_RELATIONSHIP = "建立关系"  # 与其他NPC建立关系
    EXPLORE_LOCATION = "探索地点"    # 探索新地点
    ALCHEMY = "炼丹炼器"            # 炼丹或炼器


@dataclass
class Goal:
    """
    目标数据类
    
    Attributes:
        goal_type: 目标类型
        description: 目标描述
        target_value: 目标值
        current_value: 当前进度
        priority: 优先级 (1-10)
        is_completed: 是否完成
        created_at: 创建时间戳
        deadline: 截止时间戳（可选）
        npc_id: 所属NPC的ID
        reward_emotion: 完成时的情感奖励
        penalty_emotion: 失败时的情感惩罚
    """
    goal_type: GoalType
    description: str
    target_value: float
    current_value: float = 0.0
    priority: int = 5
    is_completed: bool = False
    is_failed: bool = False
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    npc_id: str = ""
    reward_emotion: str = "满足"
    penalty_emotion: str = "沮丧"
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保优先级在有效范围内
        self.priority = max(1, min(10, self.priority))
    
    @property
    def progress(self) -> float:
        """获取当前进度百分比"""
        if self.target_value <= 0:
            return 1.0 if self.current_value > 0 else 0.0
        return min(1.0, self.current_value / self.target_value)
    
    @property
    def is_expired(self) -> bool:
        """检查目标是否过期"""
        if self.deadline is None:
            return False
        return time.time() > self.deadline
    
    @property
    def remaining_time(self) -> Optional[float]:
        """获取剩余时间（秒）"""
        if self.deadline is None:
            return None
        remaining = self.deadline - time.time()
        return max(0.0, remaining)
    
    def get_priority_score(self) -> float:
        """
        获取优先级分数（考虑进度）
        用于目标排序，分数越高优先级越高
        
        Returns:
            优先级分数
        """
        if self.is_completed or self.is_failed:
            return 0.0
        # 优先级越高、进度越低，分数越高
        return self.priority * (1 - self.progress)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "goal_type": self.goal_type.value,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "priority": self.priority,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "created_at": self.created_at,
            "deadline": self.deadline,
            "npc_id": self.npc_id,
            "reward_emotion": self.reward_emotion,
            "penalty_emotion": self.penalty_emotion,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """从字典创建目标"""
        return cls(
            goal_type=GoalType(data.get("goal_type", "突破境界")),
            description=data.get("description", ""),
            target_value=data.get("target_value", 0.0),
            current_value=data.get("current_value", 0.0),
            priority=data.get("priority", 5),
            is_completed=data.get("is_completed", False),
            is_failed=data.get("is_failed", False),
            created_at=data.get("created_at", time.time()),
            deadline=data.get("deadline"),
            npc_id=data.get("npc_id", ""),
            reward_emotion=data.get("reward_emotion", "满足"),
            penalty_emotion=data.get("penalty_emotion", "沮丧"),
        )


class NPCGoalSystem:
    """
    NPC目标系统类
    
    管理NPC的目标生成、进度评估和完成处理
    """
    
    def __init__(self):
        """初始化目标系统"""
        # NPC目标映射: npc_id -> List[Goal]
        self.npc_goals: Dict[str, List[Goal]] = {}
        
        # 职业与目标类型的关联权重
        self.occupation_goal_weights: Dict[str, Dict[GoalType, float]] = {
            "炼丹师": {
                GoalType.ALCHEMY: 0.4,
                GoalType.EARN_SPIRIT_STONES: 0.2,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.EXPLORE_LOCATION: 0.1,
            },
            "炼器师": {
                GoalType.ALCHEMY: 0.4,
                GoalType.EARN_SPIRIT_STONES: 0.2,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.EXPLORE_LOCATION: 0.1,
            },
            "药商": {
                GoalType.EARN_SPIRIT_STONES: 0.4,
                GoalType.BUILD_RELATIONSHIP: 0.3,
                GoalType.ALCHEMY: 0.1,
                GoalType.BREAKTHROUGH: 0.1,
                GoalType.EXPLORE_LOCATION: 0.1,
            },
            "剑修": {
                GoalType.BREAKTHROUGH: 0.3,
                GoalType.EXPLORE_LOCATION: 0.3,
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.EARN_SPIRIT_STONES: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
            "体修": {
                GoalType.BREAKTHROUGH: 0.4,
                GoalType.EXPLORE_LOCATION: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.EARN_SPIRIT_STONES: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
            "驭兽师": {
                GoalType.EXPLORE_LOCATION: 0.4,
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.EARN_SPIRIT_STONES: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
            "符师": {
                GoalType.ALCHEMY: 0.3,
                GoalType.EARN_SPIRIT_STONES: 0.3,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.EXPLORE_LOCATION: 0.1,
            },
            "猎人": {
                GoalType.EXPLORE_LOCATION: 0.4,
                GoalType.EARN_SPIRIT_STONES: 0.2,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
            "渔夫": {
                GoalType.EARN_SPIRIT_STONES: 0.3,
                GoalType.EXPLORE_LOCATION: 0.3,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
            "铁匠": {
                GoalType.ALCHEMY: 0.3,
                GoalType.EARN_SPIRIT_STONES: 0.3,
                GoalType.BREAKTHROUGH: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.1,
                GoalType.EXPLORE_LOCATION: 0.1,
            },
            "散修": {
                GoalType.BREAKTHROUGH: 0.3,
                GoalType.EARN_SPIRIT_STONES: 0.2,
                GoalType.EXPLORE_LOCATION: 0.2,
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.ALCHEMY: 0.1,
            },
            "门派弟子": {
                GoalType.BREAKTHROUGH: 0.3,
                GoalType.BUILD_RELATIONSHIP: 0.3,
                GoalType.EXPLORE_LOCATION: 0.2,
                GoalType.EARN_SPIRIT_STONES: 0.1,
                GoalType.ALCHEMY: 0.1,
            },
        }
        
        # 默认目标权重
        self.default_goal_weights: Dict[GoalType, float] = {
            GoalType.BREAKTHROUGH: 0.25,
            GoalType.EARN_SPIRIT_STONES: 0.25,
            GoalType.BUILD_RELATIONSHIP: 0.2,
            GoalType.EXPLORE_LOCATION: 0.2,
            GoalType.ALCHEMY: 0.1,
        }
        
        # 性格与目标类型的关联调整
        self.personality_goal_modifiers: Dict[str, Dict[GoalType, float]] = {
            "贪婪自私，唯利是图": {
                GoalType.EARN_SPIRIT_STONES: 0.3,
                GoalType.BUILD_RELATIONSHIP: -0.1,
            },
            "善良正直，嫉恶如仇": {
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.EARN_SPIRIT_STONES: -0.1,
            },
            "勇敢无畏，敢于冒险": {
                GoalType.EXPLORE_LOCATION: 0.3,
                GoalType.BREAKTHROUGH: 0.1,
            },
            "胆小谨慎，明哲保身": {
                GoalType.EXPLORE_LOCATION: -0.2,
                GoalType.BREAKTHROUGH: -0.1,
                GoalType.EARN_SPIRIT_STONES: 0.2,
            },
            "阴险狡诈，城府极深": {
                GoalType.BUILD_RELATIONSHIP: 0.2,
                GoalType.EARN_SPIRIT_STONES: 0.1,
            },
            "温和友善，乐于助人": {
                GoalType.BUILD_RELATIONSHIP: 0.3,
                GoalType.EARN_SPIRIT_STONES: -0.1,
            },
            "冷漠孤傲，独来独往": {
                GoalType.BUILD_RELATIONSHIP: -0.3,
                GoalType.BREAKTHROUGH: 0.2,
            },
            "好奇求知，博览群书": {
                GoalType.EXPLORE_LOCATION: 0.2,
                GoalType.ALCHEMY: 0.2,
            },
        }
    
    def generate_goals(self, npc: 'NPC', count: int = 3) -> List[Goal]:
        """
        根据NPC属性生成合适的目标
        
        Args:
            npc: NPC对象
            count: 生成目标数量
            
        Returns:
            生成的目标列表
        """
        goals = []
        npc_id = npc.data.id
        occupation = npc.data.occupation
        personality = npc.data.personality
        realm_level = npc.data.realm_level
        
        # 获取基础权重
        weights = self._calculate_goal_weights(occupation, personality, realm_level)
        
        # 生成目标
        for _ in range(count):
            goal = self._create_random_goal(npc, weights)
            if goal:
                goals.append(goal)
        
        # 存储目标
        if npc_id not in self.npc_goals:
            self.npc_goals[npc_id] = []
        self.npc_goals[npc_id].extend(goals)
        
        return goals
    
    def _calculate_goal_weights(
        self, 
        occupation: str, 
        personality: str, 
        realm_level: int
    ) -> Dict[GoalType, float]:
        """
        计算目标类型的权重
        
        Args:
            occupation: 职业
            personality: 性格
            realm_level: 境界等级
            
        Returns:
            目标类型权重字典
        """
        # 获取职业权重
        weights = self.occupation_goal_weights.get(
            occupation, 
            self.default_goal_weights.copy()
        ).copy()
        
        # 应用性格调整
        if personality in self.personality_goal_modifiers:
            modifiers = self.personality_goal_modifiers[personality]
            for goal_type, modifier in modifiers.items():
                weights[goal_type] = weights.get(goal_type, 0.1) + modifier
        
        # 根据境界调整权重
        if realm_level <= 2:  # 低境界更关注突破
            weights[GoalType.BREAKTHROUGH] = weights.get(GoalType.BREAKTHROUGH, 0.1) + 0.2
        elif realm_level >= 5:  # 高境界更关注关系和探索
            weights[GoalType.BUILD_RELATIONSHIP] = weights.get(GoalType.BUILD_RELATIONSHIP, 0.1) + 0.1
            weights[GoalType.EXPLORE_LOCATION] = weights.get(GoalType.EXPLORE_LOCATION, 0.1) + 0.1
        
        # 确保所有权重为正数
        for goal_type in GoalType:
            if goal_type not in weights:
                weights[goal_type] = 0.05
            weights[goal_type] = max(0.01, weights[goal_type])
        
        return weights
    
    def _create_random_goal(
        self, 
        npc: 'NPC', 
        weights: Dict[GoalType, float]
    ) -> Optional[Goal]:
        """
        根据权重创建随机目标
        
        Args:
            npc: NPC对象
            weights: 目标类型权重
            
        Returns:
            创建的目标，失败返回None
        """
        goal_types = list(weights.keys())
        weight_values = [weights[gt] for gt in goal_types]
        
        # 归一化权重
        total = sum(weight_values)
        if total <= 0:
            return None
        
        normalized_weights = [w / total for w in weight_values]
        
        # 随机选择目标类型
        goal_type = random.choices(goal_types, weights=normalized_weights)[0]
        
        # 根据目标类型创建具体目标
        return self._create_goal_by_type(npc, goal_type)
    
    def _create_goal_by_type(self, npc: 'NPC', goal_type: GoalType) -> Goal:
        """
        根据目标类型创建具体目标
        
        Args:
            npc: NPC对象
            goal_type: 目标类型
            
        Returns:
            创建的目标
        """
        npc_id = npc.data.id
        realm_level = npc.data.realm_level
        dao_name = npc.data.dao_name
        
        if goal_type == GoalType.BREAKTHROUGH:
            # 突破目标
            target_realm = realm_level + 1
            descriptions = [
                f"突破至第{target_realm}层境界",
                f"冲击更高境界，提升修为",
                f"感悟天道，寻求突破契机",
            ]
            return Goal(
                goal_type=goal_type,
                description=random.choice(descriptions),
                target_value=100.0,
                current_value=0.0,
                priority=random.randint(7, 10),
                npc_id=npc_id,
                reward_emotion="欣喜若狂",
                penalty_emotion="沮丧失望",
            )
        
        elif goal_type == GoalType.EARN_SPIRIT_STONES:
            # 赚取灵石目标
            amounts = [100, 500, 1000, 2000, 5000]
            target = random.choice(amounts)
            descriptions = [
                f"赚取{target}灵石",
                f"积累财富，收集{target}灵石",
                f"通过交易赚取{target}灵石",
            ]
            return Goal(
                goal_type=goal_type,
                description=random.choice(descriptions),
                target_value=float(target),
                current_value=0.0,
                priority=random.randint(4, 8),
                npc_id=npc_id,
                reward_emotion="心满意足",
                penalty_emotion="懊恼",
            )
        
        elif goal_type == GoalType.BUILD_RELATIONSHIP:
            # 建立关系目标
            target_count = random.randint(1, 3)
            descriptions = [
                f"结识{target_count}位志同道合的道友",
                f"与{target_count}位修士建立友好关系",
                f"扩展人脉，结交{target_count}位朋友",
            ]
            return Goal(
                goal_type=goal_type,
                description=random.choice(descriptions),
                target_value=float(target_count),
                current_value=0.0,
                priority=random.randint(3, 7),
                npc_id=npc_id,
                reward_emotion="欣慰",
                penalty_emotion="孤独",
            )
        
        elif goal_type == GoalType.EXPLORE_LOCATION:
            # 探索地点目标
            locations = ["秘境", "古迹", "洞府", "山脉", "森林", "湖泊"]
            target_location = random.choice(locations)
            descriptions = [
                f"探索一处{target_location}",
                f"寻找{target_location}中的机缘",
                f"前往{target_location}历练",
            ]
            return Goal(
                goal_type=goal_type,
                description=random.choice(descriptions),
                target_value=1.0,
                current_value=0.0,
                priority=random.randint(4, 8),
                npc_id=npc_id,
                reward_emotion="兴奋",
                penalty_emotion="遗憾",
            )
        
        elif goal_type == GoalType.ALCHEMY:
            # 炼丹炼器目标
            items = ["丹药", "法宝", "符箓", "阵盘"]
            target_item = random.choice(items)
            target_count = random.randint(1, 5)
            descriptions = [
                f"炼制{target_count}件{target_item}",
                f"精通{target_item}炼制之法",
                f"成功炼制{target_count}个{target_item}",
            ]
            return Goal(
                goal_type=goal_type,
                description=random.choice(descriptions),
                target_value=float(target_count),
                current_value=0.0,
                priority=random.randint(5, 9),
                npc_id=npc_id,
                reward_emotion="成就感",
                penalty_emotion="挫败",
            )
        
        # 默认返回突破目标
        return Goal(
            goal_type=GoalType.BREAKTHROUGH,
            description=f"{dao_name}寻求突破",
            target_value=100.0,
            current_value=0.0,
            priority=5,
            npc_id=npc_id,
        )
    
    def evaluate_goal_progress(self, goal: Goal) -> Dict[str, Any]:
        """
        评估目标进度
        
        Args:
            goal: 目标对象
            
        Returns:
            评估结果字典
        """
        progress = goal.progress
        
        # 评估状态
        if goal.is_completed:
            status = "completed"
            status_text = "已完成"
        elif goal.is_failed:
            status = "failed"
            status_text = "已失败"
        elif goal.is_expired:
            status = "expired"
            status_text = "已过期"
        elif progress >= 1.0:
            status = "ready"
            status_text = "可完成"
        elif progress >= 0.7:
            status = "almost"
            status_text = "即将完成"
        elif progress >= 0.3:
            status = "progressing"
            status_text = "进行中"
        else:
            status = "started"
            status_text = "刚开始"
        
        return {
            "goal": goal,
            "progress": progress,
            "progress_percent": f"{progress * 100:.1f}%",
            "status": status,
            "status_text": status_text,
            "is_expired": goal.is_expired,
            "remaining_time": goal.remaining_time,
        }
    
    def prioritize_goals(self, goals: List[Goal]) -> List[Goal]:
        """
        根据优先级和进度排序目标
        
        排序规则：
        1. 未完成的优先于已完成的
        2. 高优先级优先
        3. 进度高的优先（在优先级相同时）
        4. 快过期的优先
        
        Args:
            goals: 目标列表
            
        Returns:
            排序后的目标列表
        """
        def sort_key(goal: Goal) -> tuple:
            # 计算综合分数
            # 完成状态：未完成(0) < 已完成(1)
            completed_score = 1 if goal.is_completed else 0
            
            # 优先级分数：10 - priority（越高越好）
            priority_score = 10 - goal.priority
            
            # 进度分数：1 - progress（进度低的优先）
            progress_score = 1 - goal.progress
            
            # 过期紧迫性：快过期的优先
            urgency_score = 0
            if goal.deadline:
                remaining = goal.remaining_time or 0
                if remaining < 86400:  # 24小时内
                    urgency_score = 3
                elif remaining < 604800:  # 7天内
                    urgency_score = 2
                elif remaining < 2592000:  # 30天内
                    urgency_score = 1
            
            return (completed_score, priority_score, urgency_score, progress_score)
        
        return sorted(goals, key=sort_key)
    
    def on_goal_achieved(self, goal: Goal) -> Dict[str, Any]:
        """
        目标完成时的处理
        
        Args:
            goal: 完成的目标
            
        Returns:
            处理结果字典
        """
        if goal.is_completed:
            return {
                "success": False,
                "message": "目标已完成",
            }
        
        # 标记为完成
        goal.is_completed = True
        goal.current_value = goal.target_value
        
        # 计算满足感
        satisfaction = self._calculate_satisfaction(goal)
        
        # 生成奖励
        rewards = self._generate_rewards(goal)
        
        return {
            "success": True,
            "goal": goal,
            "emotion": goal.reward_emotion,
            "satisfaction": satisfaction,
            "rewards": rewards,
            "message": f"目标达成：{goal.description}\n"
                      f"感受：{goal.reward_emotion}\n"
                      f"满足感：{satisfaction:.1f}/10",
        }
    
    def _calculate_satisfaction(self, goal: Goal) -> float:
        """
        计算目标完成时的满足感
        
        Args:
            goal: 目标对象
            
        Returns:
            满足感数值 (0-10)
        """
        base_satisfaction = 5.0
        
        # 优先级加成
        priority_bonus = goal.priority * 0.3
        
        # 难度加成（目标值越大，满足感越高）
        difficulty_bonus = min(3.0, goal.target_value / 1000)
        
        # 随机波动
        random_bonus = random.uniform(-1.0, 1.0)
        
        satisfaction = base_satisfaction + priority_bonus + difficulty_bonus + random_bonus
        return max(0.0, min(10.0, satisfaction))
    
    def _generate_rewards(self, goal: Goal) -> Dict[str, Any]:
        """
        生成目标完成奖励
        
        Args:
            goal: 目标对象
            
        Returns:
            奖励字典
        """
        rewards = {
            "spirit_stones": 0,
            "exp": 0,
            "reputation": 0,
        }
        
        # 根据目标类型生成奖励
        if goal.goal_type == GoalType.BREAKTHROUGH:
            rewards["exp"] = int(goal.target_value * 0.5)
            rewards["reputation"] = random.randint(5, 15)
        elif goal.goal_type == GoalType.EARN_SPIRIT_STONES:
            rewards["spirit_stones"] = int(goal.target_value * 0.1)
            rewards["exp"] = int(goal.target_value * 0.01)
        elif goal.goal_type == GoalType.BUILD_RELATIONSHIP:
            rewards["reputation"] = int(goal.target_value * 10)
            rewards["exp"] = int(goal.target_value * 5)
        elif goal.goal_type == GoalType.EXPLORE_LOCATION:
            rewards["spirit_stones"] = random.randint(50, 200)
            rewards["exp"] = random.randint(20, 50)
        elif goal.goal_type == GoalType.ALCHEMY:
            rewards["exp"] = int(goal.target_value * 10)
            rewards["reputation"] = int(goal.target_value * 2)
        
        return rewards
    
    def on_goal_failed(self, goal: Goal, reason: str = "") -> Dict[str, Any]:
        """
        目标失败时的处理
        
        Args:
            goal: 失败的目标
            reason: 失败原因
            
        Returns:
            处理结果字典
        """
        if goal.is_failed:
            return {
                "success": False,
                "message": "目标已标记为失败",
            }
        
        # 标记为失败
        goal.is_failed = True
        
        # 计算负面情绪强度
        negative_intensity = self._calculate_negative_emotion(goal)
        
        return {
            "success": True,
            "goal": goal,
            "emotion": goal.penalty_emotion,
            "negative_intensity": negative_intensity,
            "reason": reason,
            "message": f"目标失败：{goal.description}\n"
                      f"原因：{reason or '未能完成'}\n"
                      f"感受：{goal.penalty_emotion}\n"
                      f"负面强度：{negative_intensity:.1f}/10",
        }
    
    def _calculate_negative_emotion(self, goal: Goal) -> float:
        """
        计算目标失败时的负面情绪强度
        
        Args:
            goal: 目标对象
            
        Returns:
            负面情绪强度 (0-10)
        """
        base_intensity = 3.0
        
        # 优先级越高，失败越难受
        priority_factor = goal.priority * 0.3
        
        # 进度越高，失败越难受（功亏一篑）
        progress_factor = goal.progress * 2.0
        
        # 随机波动
        random_factor = random.uniform(-0.5, 0.5)
        
        intensity = base_intensity + priority_factor + progress_factor + random_factor
        return max(0.0, min(10.0, intensity))
    
    def update_goal_progress(self, goal: Goal, value: float) -> Dict[str, Any]:
        """
        更新目标进度
        
        Args:
            goal: 目标对象
            value: 新的进度值（绝对值）或增量（相对值）
            
        Returns:
            更新结果字典
        """
        old_progress = goal.progress
        
        # 更新进度
        goal.current_value = value
        
        # 确保不超过目标值
        if goal.current_value > goal.target_value:
            goal.current_value = goal.target_value
        
        new_progress = goal.progress
        
        # 检查是否完成
        achieved = False
        if new_progress >= 1.0 and old_progress < 1.0:
            achieved = True
            achievement_result = self.on_goal_achieved(goal)
        else:
            achievement_result = None
        
        return {
            "success": True,
            "goal": goal,
            "old_progress": old_progress,
            "new_progress": new_progress,
            "progress_delta": new_progress - old_progress,
            "is_completed": goal.is_completed,
            "just_achieved": achieved,
            "achievement_result": achievement_result,
        }
    
    def add_goal_progress(self, goal: Goal, delta: float) -> Dict[str, Any]:
        """
        增加目标进度
        
        Args:
            goal: 目标对象
            delta: 进度增量
            
        Returns:
            更新结果字典
        """
        new_value = goal.current_value + delta
        return self.update_goal_progress(goal, new_value)
    
    def update_goal_from_activity(self, npc: 'NPC', activity: Any) -> List[Dict[str, Any]]:
        """
        根据活动更新NPC目标进度
        
        Args:
            npc: NPC对象
            activity: 活动对象
            
        Returns:
            更新的目标列表
        """
        results = []
        
        # 获取NPC的目标列表（优先使用npc.goals，否则使用npc_goal_system存储的）
        if hasattr(npc, 'goals') and npc.goals:
            goals = npc.goals
        else:
            goals = self.get_active_goals(npc)
        
        for goal in goals:
            if getattr(goal, 'is_completed', False) or getattr(goal, 'is_failed', False):
                continue
            
            # 计算进度增量
            progress = self._calculate_progress_from_activity(goal, activity, npc)
            if progress > 0:
                result = self.add_goal_progress(goal, progress)
                results.append(result)
                
                # 如果目标刚完成，触发保存
                if result.get('just_achieved'):
                    self._trigger_save(npc)
        
        return results
    
    def _calculate_progress_from_activity(self, goal: Goal, activity: Any, npc: 'NPC') -> float:
        """
        根据活动计算目标进度增量
        
        Args:
            goal: 目标对象
            activity: 活动对象
            npc: NPC对象
            
        Returns:
            进度增量
        """
        # 获取目标类型
        goal_type = getattr(goal, 'goal_type', None)
        if goal_type is None:
            return 0.0
        
        # 获取目标类型值
        if hasattr(goal_type, 'value'):
            goal_type_value = goal_type.value
        else:
            goal_type_value = str(goal_type)
        
        # 获取活动类型
        activity_type = getattr(activity, 'activity_type', None)
        if activity_type is None:
            return 0.0
        
        # 获取活动类型值
        if hasattr(activity_type, 'value'):
            activity_type_value = activity_type.value
        elif hasattr(activity_type, 'name'):
            activity_type_value = activity_type.name
        else:
            activity_type_value = str(activity_type)
        
        # 活动类型到目标类型的映射（支持枚举名称和中文值）
        activity_to_goal_map = {
            # 英文枚举名称
            'CULTIVATE': '突破境界',
            'CULTIVATION': '突破境界',
            'WORK': '赚取灵石',
            'SOCIALIZE': '建立关系',
            'SOCIAL': '建立关系',
            'EXPLORE': '探索地点',
            'EXPLORATION': '探索地点',
            'CRAFT': '炼丹炼器',
            'ALCHEMY': '炼丹炼器',
            # 中文值
            '修炼': '突破境界',
            '工作': '赚取灵石',
            '社交': '建立关系',
            '探索': '探索地点',
            '炼制': '炼丹炼器',
        }
        
        # 检查活动是否匹配目标类型
        mapped_goal_type = activity_to_goal_map.get(activity_type_value)
        if mapped_goal_type != goal_type_value:
            return 0.0
        
        # 基础进度增量（根据活动时长）
        duration = getattr(activity, 'duration', 1)
        base_progress = duration * random.uniform(1.0, 2.0)
        
        # 根据NPC性格调整进度（勤奋性格加成）
        diligence_bonus = 1.0
        if hasattr(npc, 'independent') and hasattr(npc.independent, 'personality'):
            diligence = getattr(npc.independent.personality, 'diligence', 0.5)
            # 勤奋度0.5为基准，每增加0.1增加5%进度
            diligence_bonus = 1.0 + (diligence - 0.5) * 0.5
        
        # 计算最终进度增量
        progress_increment = base_progress * diligence_bonus
        
        return progress_increment
    
    def _trigger_save(self, npc: 'NPC'):
        """
        触发NPC保存到数据库
        
        Args:
            npc: NPC对象
        """
        try:
            if hasattr(npc, 'save_to_database'):
                npc.save_to_database()
        except Exception as e:
            # 保存失败不中断流程
            print(f"保存NPC目标进度失败: {e}")
    
    def get_active_goals(self, npc: 'NPC') -> List[Goal]:
        """
        获取NPC的活跃目标
        
        活跃目标指未完成、未失败且未过期的目标
        
        Args:
            npc: NPC对象
            
        Returns:
            活跃目标列表
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return []
        
        active_goals = []
        for goal in self.npc_goals[npc_id]:
            if not goal.is_completed and not goal.is_failed and not goal.is_expired:
                active_goals.append(goal)
        
        # 按优先级排序
        return self.prioritize_goals(active_goals)
    
    def get_all_goals(self, npc: 'NPC') -> List[Goal]:
        """
        获取NPC的所有目标
        
        Args:
            npc: NPC对象
            
        Returns:
            所有目标列表
        """
        npc_id = npc.data.id
        return self.npc_goals.get(npc_id, [])
    
    def get_completed_goals(self, npc: 'NPC') -> List[Goal]:
        """
        获取NPC已完成的目标
        
        Args:
            npc: NPC对象
            
        Returns:
            已完成目标列表
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return []
        
        return [g for g in self.npc_goals[npc_id] if g.is_completed]
    
    def get_failed_goals(self, npc: 'NPC') -> List[Goal]:
        """
        获取NPC失败的目标
        
        Args:
            npc: NPC对象
            
        Returns:
            失败目标列表
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return []
        
        return [g for g in self.npc_goals[npc_id] if g.is_failed or g.is_expired]
    
    def remove_goal(self, npc: 'NPC', goal: Goal) -> bool:
        """
        移除NPC的目标
        
        Args:
            npc: NPC对象
            goal: 要移除的目标
            
        Returns:
            是否成功移除
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return False
        
        if goal in self.npc_goals[npc_id]:
            self.npc_goals[npc_id].remove(goal)
            return True
        
        return False
    
    def clear_goals(self, npc: 'NPC') -> int:
        """
        清除NPC的所有目标
        
        Args:
            npc: NPC对象
            
        Returns:
            清除的目标数量
        """
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return 0
        
        count = len(self.npc_goals[npc_id])
        self.npc_goals[npc_id] = []
        return count
    
    def update_all_goals(self, npc: 'NPC') -> List[Dict[str, Any]]:
        """
        更新NPC的所有目标状态
        
        检查过期目标并更新进度
        
        Args:
            npc: NPC对象
            
        Returns:
            更新结果列表
        """
        results = []
        npc_id = npc.data.id
        
        if npc_id not in self.npc_goals:
            return results
        
        for goal in self.npc_goals[npc_id]:
            # 检查是否过期
            if goal.is_expired and not goal.is_failed and not goal.is_completed:
                fail_result = self.on_goal_failed(goal, "目标超时未完成")
                results.append(fail_result)
            else:
                # 评估进度
                eval_result = self.evaluate_goal_progress(goal)
                results.append(eval_result)
        
        return results
    
    def get_goal_statistics(self, npc: 'NPC') -> Dict[str, Any]:
        """
        获取NPC的目标统计信息
        
        Args:
            npc: NPC对象
            
        Returns:
            统计信息字典
        """
        npc_id = npc.data.id
        all_goals = self.npc_goals.get(npc_id, [])
        
        total = len(all_goals)
        completed = len([g for g in all_goals if g.is_completed])
        failed = len([g for g in all_goals if g.is_failed])
        expired = len([g for g in all_goals if g.is_expired and not g.is_failed])
        active = total - completed - failed
        
        # 计算完成率
        completion_rate = completed / total if total > 0 else 0.0
        
        # 按类型统计
        type_stats = {}
        for goal_type in GoalType:
            type_count = len([g for g in all_goals if g.goal_type == goal_type])
            type_stats[goal_type.value] = type_count
        
        return {
            "npc_id": npc_id,
            "npc_name": npc.data.dao_name,
            "total_goals": total,
            "active_goals": active,
            "completed_goals": completed,
            "failed_goals": failed,
            "expired_goals": expired,
            "completion_rate": completion_rate,
            "completion_rate_percent": f"{completion_rate * 100:.1f}%",
            "type_statistics": type_stats,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将目标系统转换为字典
        
        Returns:
            包含所有NPC目标的字典
        """
        return {
            npc_id: [goal.to_dict() for goal in goals]
            for npc_id, goals in self.npc_goals.items()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典加载目标系统
        
        Args:
            data: 包含NPC目标数据的字典
        """
        self.npc_goals = {}
        for npc_id, goals_data in data.items():
            self.npc_goals[npc_id] = [
                Goal.from_dict(goal_data) for goal_data in goals_data
            ]


# 全局目标系统实例
npc_goal_system = NPCGoalSystem()
