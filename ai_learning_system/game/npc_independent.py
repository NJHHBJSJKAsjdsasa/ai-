"""
NPC独立系统模块
实现NPC的自主行为、需求、目标、性格、记忆和社交系统
采用单线程轮询+时间片架构
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

from config import GAME_CONFIG


class NeedType(Enum):
    """需求类型"""
    HUNGER = auto()      # 饥饿度
    ENERGY = auto()      # 精力值
    SOCIAL = auto()      # 社交需求
    CULTIVATION = auto() # 修炼欲望


class GoalType(Enum):
    """目标类型"""
    BREAKTHROUGH = auto()   # 突破境界
    WEALTH = auto()         # 赚取灵石
    RELATIONSHIP = auto()   # 建立关系
    EXPLORATION = auto()    # 探索新地点
    CRAFTING = auto()       # 炼丹/炼器


class ActivityType(Enum):
    """活动类型"""
    EAT = auto()           # 进食
    REST = auto()          # 休息
    SOCIALIZE = auto()     # 社交
    CULTIVATE = auto()     # 修炼
    WORK = auto()          # 工作
    EXPLORE = auto()       # 探索
    IDLE = auto()          # 闲逛


@dataclass
class NPCNeed:
    """NPC需求"""
    need_type: NeedType
    value: float = 50.0      # 当前值 (0-100)
    decay_rate: float = 1.0  # 每秒衰减率
    
    def update(self, seconds: float):
        """更新需求值"""
        self.value = max(0.0, min(100.0, self.value + self.decay_rate * seconds))
    
    def is_urgent(self) -> bool:
        """检查是否为紧急需求"""
        if self.need_type == NeedType.HUNGER:
            return self.value > 80
        elif self.need_type == NeedType.ENERGY:
            return self.value < 20
        elif self.need_type == NeedType.SOCIAL:
            return self.value > 70
        elif self.need_type == NeedType.CULTIVATION:
            return self.value > 60
        return False
    
    def get_priority(self) -> float:
        """获取需求优先级（越高越需要满足）"""
        if self.need_type == NeedType.HUNGER:
            return self.value / 100.0
        elif self.need_type == NeedType.ENERGY:
            return (100 - self.value) / 100.0
        elif self.need_type == NeedType.SOCIAL:
            return self.value / 100.0
        elif self.need_type == NeedType.CULTIVATION:
            return self.value / 100.0
        return 0.0


@dataclass
class NPCGoal:
    """NPC目标"""
    goal_type: GoalType
    description: str
    target_value: float
    current_value: float = 0.0
    priority: int = 5        # 优先级 (1-10)
    is_completed: bool = False
    created_at: float = field(default_factory=time.time)
    
    def update_progress(self, value: float):
        """更新进度"""
        self.current_value = min(self.target_value, self.current_value + value)
        if self.current_value >= self.target_value:
            self.is_completed = True
    
    def get_progress(self) -> float:
        """获取进度百分比"""
        if self.target_value <= 0:
            return 1.0
        return self.current_value / self.target_value
    
    def get_priority_score(self) -> float:
        """获取优先级分数（考虑进度）"""
        if self.is_completed:
            return 0.0
        return self.priority * (1 - self.get_progress())


@dataclass
class Personality:
    """性格属性"""
    bravery: float = 0.5      # 勇敢 (0-1)
    greed: float = 0.5        # 贪婪 (0-1)
    kindness: float = 0.5     # 善良 (0-1)
    diligence: float = 0.5    # 勤奋 (0-1)
    curiosity: float = 0.5    # 好奇 (0-1)
    
    @classmethod
    def random(cls) -> 'Personality':
        """生成随机性格"""
        return cls(
            bravery=random.uniform(0.1, 0.9),
            greed=random.uniform(0.1, 0.9),
            kindness=random.uniform(0.1, 0.9),
            diligence=random.uniform(0.1, 0.9),
            curiosity=random.uniform(0.1, 0.9)
        )


@dataclass
class Memory:
    """NPC记忆"""
    content: str
    importance: int = 5       # 重要性 (0-10)
    timestamp: float = field(default_factory=time.time)
    emotion: str = "neutral"  # 情感 (positive/negative/neutral)
    fade_rate: float = 0.1    # 淡化速率
    
    def get_current_importance(self, current_time: float) -> float:
        """获取当前重要性（考虑时间淡化）"""
        age = current_time - self.timestamp
        faded = self.importance * (1 - self.fade_rate * age / 86400)  # 按天淡化
        return max(0, faded)


@dataclass
class Relationship:
    """NPC关系"""
    npc_id: str
    affinity: float = 0.0     # 好感度 (-100 to 100)
    familiarity: float = 0.0  # 熟悉度 (0-100)
    last_interaction: float = 0.0
    
    def update_affinity(self, delta: float):
        """更新好感度"""
        self.affinity = max(-100, min(100, self.affinity + delta))


class NPCIndependent:
    """NPC独立系统核心类"""
    
    def __init__(self, npc_id: str, npc_data: Dict[str, Any] = None):
        """
        初始化NPC独立系统
        
        Args:
            npc_id: NPC唯一标识
            npc_data: NPC基础数据
        """
        self.npc_id = npc_id
        self.npc_data = npc_data or {}
        
        # 时间片更新机制
        self.last_update = 0.0
        self.update_interval = random.uniform(5, 30)  # 5-30秒随机间隔
        self.is_paused = False
        
        # 需求系统
        self.needs: Dict[NeedType, NPCNeed] = {
            NeedType.HUNGER: NPCNeed(NeedType.HUNGER, random.uniform(20, 50), 0.5),
            NeedType.ENERGY: NPCNeed(NeedType.ENERGY, random.uniform(60, 100), -0.3),
            NeedType.SOCIAL: NPCNeed(NeedType.SOCIAL, random.uniform(30, 60), 0.4),
            NeedType.CULTIVATION: NPCNeed(NeedType.CULTIVATION, random.uniform(10, 40), 0.2)
        }
        
        # 性格系统（必须在目标系统之前初始化）
        self.personality = Personality.random()
        
        # 目标系统
        self.goals: List[NPCGoal] = []
        self._generate_goals()
        
        # 记忆系统
        self.memories: List[Memory] = []
        
        # 社交系统
        self.relationships: Dict[str, Relationship] = {}
        
        # 当前状态
        self.current_activity: ActivityType = ActivityType.IDLE
        self.current_location: str = npc_data.get("location", "新手村") if npc_data else "新手村"
        self.last_action_result: str = ""
        
        # 统计
        self.total_actions = 0
        self.total_interactions = 0
    
    def _generate_goals(self):
        """生成初始目标"""
        # 主要目标：突破境界
        self.goals.append(NPCGoal(
            goal_type=GoalType.BREAKTHROUGH,
            description="突破到下一境界",
            target_value=1000,
            priority=10
        ))
        
        # 根据职业添加目标
        occupation = self.npc_data.get("occupation", "散修") if self.npc_data else "散修"
        if "商" in occupation:
            self.goals.append(NPCGoal(
                goal_type=GoalType.WEALTH,
                description="赚取1000灵石",
                target_value=1000,
                priority=7
            ))
        elif "炼丹" in occupation or "炼器" in occupation:
            self.goals.append(NPCGoal(
                goal_type=GoalType.CRAFTING,
                description="炼制100件物品",
                target_value=100,
                priority=8
            ))
        
        # 社交目标
        self.goals.append(NPCGoal(
            goal_type=GoalType.RELATIONSHIP,
            description="结交5位好友",
            target_value=5,
            priority=5
        ))
        
        # 探索目标（好奇性格）
        if self.personality.curiosity > 0.6:
            self.goals.append(NPCGoal(
                goal_type=GoalType.EXPLORATION,
                description="探索3个新地点",
                target_value=3,
                priority=6
            ))
    
    def update(self, current_time: float, player_nearby: bool = False) -> bool:
        """
        更新NPC状态（时间片更新机制）
        
        Args:
            current_time: 当前时间戳
            player_nearby: 玩家是否在附近
            
        Returns:
            是否执行了更新
        """
        if self.is_paused:
            return False
        
        # 检查是否到达更新时间
        interval = self.get_update_interval(player_nearby)
        if current_time - self.last_update < interval:
            return False
        
        self.last_update = current_time
        
        # 更新需求
        self._update_needs(interval)
        
        # 做决定
        decision = self.make_decision()
        
        # 执行动作
        result = self.execute_action(decision)
        self.last_action_result = result
        
        # 记录记忆
        self.add_memory(f"{decision}: {result}", importance=3)
        
        # 社交互动（30%概率）
        if random.random() < 0.3:
            self.socialize()
        
        self.total_actions += 1
        return True
    
    def get_update_interval(self, player_nearby: bool) -> float:
        """
        获取更新间隔（根据与玩家距离调整）
        
        Args:
            player_nearby: 玩家是否在附近
            
        Returns:
            更新间隔（秒）
        """
        if player_nearby:
            return self.update_interval * 0.5  # 玩家在附近时更新更快
        return self.update_interval
    
    def _update_needs(self, seconds: float):
        """更新需求值"""
        for need in self.needs.values():
            need.update(seconds)
    
    def make_decision(self) -> str:
        """
        做决定（优先级：紧急需求 > 目标 > 日程 > 性格）
        
        Returns:
            决策描述
        """
        # 1. 检查紧急需求
        urgent_need = self._get_urgent_need()
        if urgent_need:
            return self._need_to_action(urgent_need)
        
        # 2. 检查目标
        active_goal = self._get_active_goal()
        if active_goal:
            return self._goal_to_action(active_goal)
        
        # 3. 根据性格选择
        return self._personality_to_action()
    
    def _get_urgent_need(self) -> Optional[NeedType]:
        """获取最紧急的需求"""
        urgent_needs = [
            (need_type, need.get_priority())
            for need_type, need in self.needs.items()
            if need.is_urgent()
        ]
        if urgent_needs:
            urgent_needs.sort(key=lambda x: x[1], reverse=True)
            return urgent_needs[0][0]
        return None
    
    def _need_to_action(self, need_type: NeedType) -> str:
        """将需求转换为行动"""
        if need_type == NeedType.HUNGER:
            return "找食物"
        elif need_type == NeedType.ENERGY:
            return "休息"
        elif need_type == NeedType.SOCIAL:
            return "找人聊天"
        elif need_type == NeedType.CULTIVATION:
            return "修炼"
        return "闲逛"
    
    def _get_active_goal(self) -> Optional[NPCGoal]:
        """获取当前最优先的活跃目标"""
        active_goals = [g for g in self.goals if not g.is_completed]
        if not active_goals:
            return None
        active_goals.sort(key=lambda g: g.get_priority_score(), reverse=True)
        return active_goals[0]
    
    def _goal_to_action(self, goal: NPCGoal) -> str:
        """将目标转换为行动"""
        if goal.goal_type == GoalType.BREAKTHROUGH:
            return "努力修炼"
        elif goal.goal_type == GoalType.WEALTH:
            return "寻找赚钱机会"
        elif goal.goal_type == GoalType.RELATIONSHIP:
            return "结交新朋友"
        elif goal.goal_type == GoalType.EXPLORATION:
            return "探索新地点"
        elif goal.goal_type == GoalType.CRAFTING:
            return "炼制物品"
        return "闲逛"
    
    def _personality_to_action(self) -> str:
        """根据性格选择行动"""
        choices = []
        
        if self.personality.diligence > 0.6:
            choices.append("修炼")
        if self.personality.greed > 0.5:
            choices.append("工作赚钱")
        if self.personality.bravery > 0.5:
            choices.append("探索秘境")
        if self.personality.curiosity > 0.6:
            choices.append("探索")
        if self.personality.kindness > 0.6:
            choices.append("帮助他人")
        
        if choices:
            return random.choice(choices)
        return "闲逛"
    
    def execute_action(self, action: str) -> str:
        """
        执行动作
        
        Args:
            action: 动作描述
            
        Returns:
            动作结果
        """
        # 更新当前活动类型
        if "修炼" in action:
            self.current_activity = ActivityType.CULTIVATE
            self.needs[NeedType.CULTIVATION].value = max(0, self.needs[NeedType.CULTIVATION].value - 20)
            self.needs[NeedType.ENERGY].value -= 10
            return "修为有所提升"
        
        elif "食物" in action or "吃" in action:
            self.current_activity = ActivityType.EAT
            self.needs[NeedType.HUNGER].value = max(0, self.needs[NeedType.HUNGER].value - 50)
            return "吃饱了"
        
        elif "休息" in action or "睡" in action:
            self.current_activity = ActivityType.REST
            self.needs[NeedType.ENERGY].value = min(100, self.needs[NeedType.ENERGY].value + 30)
            return "精力充沛"
        
        elif "聊天" in action or "社交" in action or "结交" in action:
            self.current_activity = ActivityType.SOCIALIZE
            self.needs[NeedType.SOCIAL].value = max(0, self.needs[NeedType.SOCIAL].value - 30)
            return "心情愉快"
        
        elif "工作" in action or "赚钱" in action:
            self.current_activity = ActivityType.WORK
            self.needs[NeedType.ENERGY].value -= 15
            # 更新财富目标
            for goal in self.goals:
                if goal.goal_type == GoalType.WEALTH:
                    goal.update_progress(random.randint(10, 50))
            return "赚了一些灵石"
        
        elif "探索" in action:
            self.current_activity = ActivityType.EXPLORE
            self.needs[NeedType.ENERGY].value -= 10
            # 更新探索目标
            for goal in self.goals:
                if goal.goal_type == GoalType.EXPLORATION:
                    goal.update_progress(0.1)
            return "发现了一些有趣的东西"
        
        elif "炼制" in action:
            self.current_activity = ActivityType.WORK
            self.needs[NeedType.ENERGY].value -= 20
            # 更新制造目标
            for goal in self.goals:
                if goal.goal_type == GoalType.CRAFTING:
                    goal.update_progress(1)
            return "成功炼制了一件物品"
        
        else:
            self.current_activity = ActivityType.IDLE
            return "悠闲地度过了一段时间"
    
    def socialize(self):
        """社交互动"""
        # 这里会在NPCIndependentManager中实现
        # 因为需要访问其他NPC
        pass
    
    def add_memory(self, content: str, importance: int = 5, emotion: str = "neutral"):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            importance: 重要性 (0-10)
            emotion: 情感
        """
        memory = Memory(content, importance, emotion=emotion)
        self.memories.append(memory)
        
        # 限制记忆数量
        max_memories = 50
        if len(self.memories) > max_memories:
            # 删除重要性最低的记忆
            self.memories.sort(key=lambda m: m.importance)
            self.memories = self.memories[-max_memories:]
    
    def get_memories(self, limit: int = 10) -> List[Memory]:
        """获取最近的记忆"""
        return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:limit]
    
    def get_relationship(self, other_npc_id: str) -> Relationship:
        """获取与另一个NPC的关系"""
        if other_npc_id not in self.relationships:
            self.relationships[other_npc_id] = Relationship(other_npc_id)
        return self.relationships[other_npc_id]
    
    def update_relationship(self, other_npc_id: str, delta: float):
        """更新与另一个NPC的关系"""
        rel = self.get_relationship(other_npc_id)
        rel.update_affinity(delta)
        rel.last_interaction = time.time()
        rel.familiarity = min(100, rel.familiarity + 1)
    
    def pause(self):
        """暂停更新"""
        self.is_paused = True
    
    def resume(self):
        """恢复更新"""
        self.is_paused = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            "npc_id": self.npc_id,
            "location": self.current_location,
            "current_activity": self.current_activity.name,
            "last_action": self.last_action_result,
            "needs": {
                need_type.name: round(need.value, 1)
                for need_type, need in self.needs.items()
            },
            "goals": [
                {
                    "type": goal.goal_type.name,
                    "description": goal.description,
                    "progress": f"{goal.get_progress()*100:.0f}%",
                    "completed": goal.is_completed
                }
                for goal in self.goals
            ],
            "personality": {
                "勇敢": round(self.personality.bravery, 2),
                "贪婪": round(self.personality.greed, 2),
                "善良": round(self.personality.kindness, 2),
                "勤奋": round(self.personality.diligence, 2),
                "好奇": round(self.personality.curiosity, 2)
            },
            "memory_count": len(self.memories),
            "relationship_count": len(self.relationships),
            "total_actions": self.total_actions
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "npc_id": self.npc_id,
            "last_update": self.last_update,
            "update_interval": self.update_interval,
            "is_paused": self.is_paused,
            "needs": {
                need_type.name: {"value": need.value, "decay_rate": need.decay_rate}
                for need_type, need in self.needs.items()
            },
            "goals": [
                {
                    "goal_type": goal.goal_type.name,
                    "description": goal.description,
                    "target_value": goal.target_value,
                    "current_value": goal.current_value,
                    "priority": goal.priority,
                    "is_completed": goal.is_completed
                }
                for goal in self.goals
            ],
            "personality": {
                "bravery": self.personality.bravery,
                "greed": self.personality.greed,
                "kindness": self.personality.kindness,
                "diligence": self.personality.diligence,
                "curiosity": self.personality.curiosity
            },
            "memories": [
                {
                    "content": m.content,
                    "importance": m.importance,
                    "timestamp": m.timestamp,
                    "emotion": m.emotion
                }
                for m in self.memories
            ],
            "relationships": {
                npc_id: {
                    "affinity": rel.affinity,
                    "familiarity": rel.familiarity,
                    "last_interaction": rel.last_interaction
                }
                for npc_id, rel in self.relationships.items()
            },
            "current_location": self.current_location,
            "total_actions": self.total_actions,
            "total_interactions": self.total_interactions
        }


class NPCIndependentManager:
    """NPC独立系统管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.npcs: Dict[str, NPCIndependent] = {}
        self.player_location: str = "新手村"
        self.zones: Dict[str, Set[str]] = {}  # 区域 -> NPC ID集合
        self.update_count = 0
        self.last_stats_time = time.time()
    
    def add_npc(self, npc: NPCIndependent, zone: str = None):
        """
        添加NPC
        
        Args:
            npc: NPC独立系统实例
            zone: 所在区域
        """
        self.npcs[npc.npc_id] = npc
        
        # 添加到区域
        zone = zone or npc.current_location
        if zone not in self.zones:
            self.zones[zone] = set()
        self.zones[zone].add(npc.npc_id)
    
    def remove_npc(self, npc_id: str):
        """移除NPC"""
        if npc_id in self.npcs:
            npc = self.npcs[npc_id]
            # 从区域中移除
            for zone, npc_ids in self.zones.items():
                if npc_id in npc_ids:
                    npc_ids.remove(npc_id)
                    break
            del self.npcs[npc_id]
    
    def get_npc(self, npc_id: str) -> Optional[NPCIndependent]:
        """获取NPC"""
        return self.npcs.get(npc_id)
    
    def update_all(self, current_time: float, player_location: str = None):
        """
        更新所有NPC（单线程轮询）
        
        Args:
            current_time: 当前时间戳
            player_location: 玩家当前位置
        """
        if player_location:
            self.player_location = player_location
        
        # 只更新玩家所在区域的NPC（分区更新）
        npc_ids_to_update = self.zones.get(self.player_location, set())
        
        updated_count = 0
        for npc_id in npc_ids_to_update:
            npc = self.npcs.get(npc_id)
            if npc:
                # 检查是否在玩家附近（简化：同区域视为附近）
                player_nearby = (npc.current_location == self.player_location)
                if npc.update(current_time, player_nearby):
                    updated_count += 1
        
        self.update_count += updated_count
        
        # 每秒输出一次统计
        if current_time - self.last_stats_time >= 10:
            self._print_stats()
            self.last_stats_time = current_time
    
    def _print_stats(self):
        """打印统计信息"""
        total_npcs = len(self.npcs)
        active_npcs = sum(1 for npc in self.npcs.values() if not npc.is_paused)
        print(f"[NPC独立系统] 总计: {total_npcs}, 活跃: {active_npcs}, 本轮更新: {self.update_count}")
        self.update_count = 0
    
    def pause_npc(self, npc_id: str):
        """暂停指定NPC"""
        npc = self.npcs.get(npc_id)
        if npc:
            npc.pause()
    
    def resume_npc(self, npc_id: str):
        """恢复指定NPC"""
        npc = self.npcs.get(npc_id)
        if npc:
            npc.resume()
    
    def pause_all(self):
        """暂停所有NPC"""
        for npc in self.npcs.values():
            npc.pause()
    
    def resume_all(self):
        """恢复所有NPC"""
        for npc in self.npcs.values():
            npc.resume()
    
    def get_npcs_in_zone(self, zone: str) -> List[NPCIndependent]:
        """获取区域内的所有NPC"""
        npc_ids = self.zones.get(zone, set())
        return [self.npcs[npc_id] for npc_id in npc_ids if npc_id in self.npcs]
    
    def move_npc_to_zone(self, npc_id: str, new_zone: str):
        """移动NPC到新区域"""
        npc = self.npcs.get(npc_id)
        if not npc:
            return
        
        # 从旧区域移除
        for zone, npc_ids in self.zones.items():
            if npc_id in npc_ids:
                npc_ids.remove(npc_id)
                break
        
        # 添加到新区域
        if new_zone not in self.zones:
            self.zones[new_zone] = set()
        self.zones[new_zone].add(npc_id)
        npc.current_location = new_zone
    
    def socialize_between(self, npc_id1: str, npc_id2: str):
        """
        两个NPC之间进行社交
        
        Args:
            npc_id1: 第一个NPC的ID
            npc_id2: 第二个NPC的ID
        """
        npc1 = self.npcs.get(npc_id1)
        npc2 = self.npcs.get(npc_id2)
        
        if not npc1 or not npc2:
            return
        
        # 更新关系
        affinity_change = random.uniform(-2, 5)
        if npc1.personality.kindness > 0.6:
            affinity_change += 1
        if npc2.personality.kindness > 0.6:
            affinity_change += 1
        
        npc1.update_relationship(npc_id2, affinity_change)
        npc2.update_relationship(npc_id1, affinity_change)
        
        # 分享记忆
        if npc1.memories and random.random() < 0.3:
            memory = random.choice(npc1.memories)
            npc2.add_memory(f"听{npc_id1}说: {memory.content}", importance=memory.importance//2)
        
        if npc2.memories and random.random() < 0.3:
            memory = random.choice(npc2.memories)
            npc1.add_memory(f"听{npc_id2}说: {memory.content}", importance=memory.importance//2)
        
        npc1.total_interactions += 1
        npc2.total_interactions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_npcs": len(self.npcs),
            "active_npcs": sum(1 for npc in self.npcs.values() if not npc.is_paused),
            "zones": {zone: len(npc_ids) for zone, npc_ids in self.zones.items()},
            "total_memories": sum(len(npc.memories) for npc in self.npcs.values()),
            "total_relationships": sum(len(npc.relationships) for npc in self.npcs.values()),
            "total_actions": sum(npc.total_actions for npc in self.npcs.values())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "player_location": self.player_location,
            "zones": {zone: list(npc_ids) for zone, npc_ids in self.zones.items()}
        }
