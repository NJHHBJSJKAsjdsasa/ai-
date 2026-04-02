"""
NPC独立系统模块
实现NPC的自主行为、需求、目标、性格、记忆和社交系统
采用单线程轮询+时间片架构
"""

import random
import time
import threading
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG
from game.npc_combat import npc_combat_manager


# 需求类型中文映射
NEED_TYPE_TRANSLATIONS = {
    'HUNGER': '饥饿',
    'ENERGY': '精力',
    'SOCIAL': '社交',
    'CULTIVATION': '修炼',
}

# 活动类型中文映射
ACTIVITY_TYPE_TRANSLATIONS = {
    'EAT': '进食',
    'REST': '休息',
    'SOCIALIZE': '社交',
    'CULTIVATE': '修炼',
    'WORK': '工作',
    'EXPLORE': '探索',
    'IDLE': '闲逛',
}


class NeedType(Enum):
    """需求类型"""
    HUNGER = auto()      # 饥饿度
    ENERGY = auto()      # 精力值
    SOCIAL = auto()      # 社交需求
    CULTIVATION = auto() # 修炼欲望


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
    """NPC独立系统核心类
    
    线程安全设计：使用锁保护共享状态
    """
    
    def __init__(self, npc_id: str, npc_data: Dict[str, Any] = None, parent_npc=None):
        """
        初始化NPC独立系统
        
        Args:
            npc_id: NPC唯一标识
            npc_data: NPC基础数据
            parent_npc: 父NPC对象（用于访问真实目标系统）
        """
        self.npc_id = npc_id
        self.npc_data = npc_data or {}
        self.parent_npc = parent_npc  # 引用父NPC以访问真实目标
        
        # 线程锁保护共享状态
        self._lock = threading.Lock()
        
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
        
        # 性格系统
        self.personality = Personality.random()
        
        # 注意：目标系统现在通过 parent_npc.goals 访问，不再自建
        
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
    
    def get_goals(self) -> List[Any]:
        """
        获取真实目标列表（从父NPC）
        
        Returns:
            目标列表
        """
        if self.parent_npc and hasattr(self.parent_npc, 'goals'):
            return self.parent_npc.goals
        return []
    
    def _get_active_goal_from_parent(self) -> Optional[Any]:
        """
        从父NPC获取当前最优先的活跃目标
        
        Returns:
            活跃目标对象或None
        """
        goals = self.get_goals()
        if not goals:
            return None
        
        # 过滤未完成的目标
        active_goals = [g for g in goals if not getattr(g, 'is_completed', False) and not getattr(g, 'is_failed', False)]
        if not active_goals:
            return None
        
        # 按优先级排序（考虑进度）
        def get_priority_score(goal):
            if getattr(goal, 'is_completed', False):
                return 0.0
            priority = getattr(goal, 'priority', 5)
            progress = getattr(goal, 'progress', 0)
            return priority * (1 - progress)
        
        active_goals.sort(key=get_priority_score, reverse=True)
        return active_goals[0]
    
    def update(self, current_time: float, player_nearby: bool = False) -> bool:
        """
        更新NPC状态（时间片更新机制）
        
        线程安全：使用锁保护整个更新过程
        
        Args:
            current_time: 当前时间戳
            player_nearby: 玩家是否在附近
            
        Returns:
            是否执行了更新
        """
        with self._lock:
            if self.is_paused:
                return False
            
            # 检查是否到达更新时间
            interval = self._get_update_interval(player_nearby)
            if current_time - self.last_update < interval:
                return False
            
            self.last_update = current_time
            
            # 更新需求
            self._update_needs(interval)
            
            # 做决定
            decision = self._make_decision()
            
            # 执行动作
            result = self._execute_action(decision)
            self.last_action_result = result
            
            # 记录记忆
            self._add_memory(f"{decision}: {result}", importance=3)
            
            # 社交互动（30%概率）
            if random.random() < 0.3:
                self._socialize()
            
            self.total_actions += 1
            return True
    
    def _get_update_interval(self, player_nearby: bool) -> float:
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
    
    def _make_decision(self) -> str:
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
    
    def _get_active_goal(self) -> Optional[Any]:
        """获取当前最优先的活跃目标（从父NPC）"""
        return self._get_active_goal_from_parent()
    
    def _goal_to_action(self, goal: Any) -> str:
        """将目标转换为行动（使用父NPC的真实目标类型）"""
        # 获取目标类型（支持枚举和字符串）
        goal_type = getattr(goal, 'goal_type', None)
        if goal_type is None:
            return "闲逛"
        
        # 获取目标类型值（处理枚举和字符串）
        if hasattr(goal_type, 'value'):
            goal_type_value = goal_type.value
        else:
            goal_type_value = str(goal_type)
        
        # 映射到行动
        goal_type_map = {
            '突破境界': '努力修炼',
            '赚取灵石': '寻找赚钱机会',
            '建立关系': '结交新朋友',
            '探索地点': '探索新地点',
            '炼丹炼器': '炼制物品',
        }
        
        return goal_type_map.get(goal_type_value, "闲逛")
    
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
    
    def _execute_action(self, action: str) -> str:
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
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
            return "赚了一些灵石"
        
        elif "探索" in action:
            self.current_activity = ActivityType.EXPLORE
            self.needs[NeedType.ENERGY].value -= 10
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
            return "发现了一些有趣的东西"
        
        elif "炼制" in action:
            self.current_activity = ActivityType.WORK
            self.needs[NeedType.ENERGY].value -= 20
            # 注意：目标进度更新由父NPC的 _update_goal_progress 处理
            return "成功炼制了一件物品"
        
        else:
            self.current_activity = ActivityType.IDLE
            return "悠闲地度过了一段时间"
    
    def _socialize(self):
        """社交互动"""
        # 这里会在NPCIndependentManager中实现
        # 因为需要访问其他NPC
        pass
    
    def _check_combat_opportunity(self, other_npc) -> Optional[str]:
        """
        检查战斗机会
        
        Args:
            other_npc: 另一个NPC对象
            
        Returns:
            战斗类型: "spar"(切磋), "deathmatch"(死斗), 或 None
        """
        # 使用全局战斗管理器检查
        if npc_combat_manager.check_spar_opportunity(self, other_npc):
            return "spar"
        elif npc_combat_manager.check_deathmatch_opportunity(self, other_npc):
            return "deathmatch"
        return None
    
    def _make_combat_decision(self, other_npc, combat_type: str) -> bool:
        """
        自主战斗决策
        
        Args:
            other_npc: 另一个NPC对象
            combat_type: 战斗类型
            
        Returns:
            是否接受战斗
        """
        # 根据性格做出决策
        if combat_type == "spar":
            # 切磋：勇敢性格更可能接受
            if self.personality.bravery > 0.6:
                return True
            # 根据战斗力差距决定
            my_power = getattr(self.npc_data, 'attack', 10) + getattr(self.npc_data, 'defense', 5)
            other_power = getattr(other_npc.data, 'attack', 10) + getattr(other_npc.data, 'defense', 5)
            if my_power >= other_power * 0.8:  # 差距不大时接受
                return True
            return random.random() < 0.5
            
        elif combat_type == "deathmatch":
            # 死斗：非常危险，只有勇敢且贪婪的NPC可能接受
            if self.personality.bravery > 0.7 and self.personality.greed > 0.6:
                return True
            # 或者实力碾压
            my_power = getattr(self.npc_data, 'attack', 10) + getattr(self.npc_data, 'defense', 5)
            other_power = getattr(other_npc.data, 'attack', 10) + getattr(other_npc.data, 'defense', 5)
            if my_power > other_power * 1.5:  # 实力碾压时接受
                return True
            return False
            
        return False
    
    def _add_memory(self, content: str, importance: int = 5, emotion: str = "neutral"):
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
        """获取最近的记忆（线程安全）"""
        with self._lock:
            return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:limit]
    
    def get_relationship(self, other_npc_id: str) -> Relationship:
        """获取与另一个NPC的关系（线程安全）"""
        with self._lock:
            if other_npc_id not in self.relationships:
                self.relationships[other_npc_id] = Relationship(other_npc_id)
            return self.relationships[other_npc_id]
    
    def update_relationship(self, other_npc_id: str, delta: float):
        """更新与另一个NPC的关系（线程安全）"""
        with self._lock:
            rel = self.get_relationship(other_npc_id)
            rel.update_affinity(delta)
            rel.last_interaction = time.time()
            rel.familiarity = min(100, rel.familiarity + 1)
    
    def pause(self):
        """暂停更新（线程安全）"""
        with self._lock:
            self.is_paused = True
    
    def resume(self):
        """恢复更新（线程安全）"""
        with self._lock:
            self.is_paused = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息（线程安全）"""
        with self._lock:
            return {
                "npc_id": self.npc_id,
                "location": self.current_location,
                "current_activity": ACTIVITY_TYPE_TRANSLATIONS.get(self.current_activity.name, self.current_activity.name),
                "last_action": self.last_action_result,
                "needs": {
                    NEED_TYPE_TRANSLATIONS.get(need_type.name, need_type.name): round(need.value, 1)
                    for need_type, need in self.needs.items()
                },
                "goals": self._get_goals_status(),
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
    
    def _get_goals_status(self) -> List[Dict[str, Any]]:
        """
        获取目标状态（从父NPC的真实目标）
        
        Returns:
            目标状态列表
        """
        goals = self.get_goals()
        if not goals:
            return []
        
        result = []
        for goal in goals:
            # 获取目标类型名称
            goal_type = getattr(goal, 'goal_type', None)
            if hasattr(goal_type, 'name'):
                type_name = goal_type.name
            elif hasattr(goal_type, 'value'):
                type_name = goal_type.value
            else:
                type_name = str(goal_type)
            
            # 计算进度
            current = getattr(goal, 'current_value', 0)
            target = getattr(goal, 'target_value', 1)
            progress = (current / target * 100) if target > 0 else 0
            
            result.append({
                "type": type_name,
                "description": getattr(goal, 'description', '未知目标'),
                "progress": f"{progress:.0f}%",
                "completed": getattr(goal, 'is_completed', False)
            })
        
        return result
    
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
            # 注意：目标数据现在通过 parent_npc.goals 访问，不再在独立系统中序列化
            "goals": [],
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
    """NPC独立系统管理器
    
    线程安全设计：使用锁保护所有共享状态
    """
    
    def __init__(self):
        """初始化管理器"""
        self._lock = threading.Lock()
        self.npcs: Dict[str, NPCIndependent] = {}
        self.player_location: str = "新手村"
        self.zones: Dict[str, Set[str]] = {}  # 区域 -> NPC ID集合
        self.update_count = 0
        self.last_stats_time = time.time()
    
    def add_npc(self, npc: NPCIndependent, zone: str = None):
        """
        添加NPC（线程安全）
        
        Args:
            npc: NPC独立系统实例
            zone: 所在区域
        """
        with self._lock:
            self.npcs[npc.npc_id] = npc
            
            # 添加到区域
            zone = zone or npc.current_location
            if zone not in self.zones:
                self.zones[zone] = set()
            self.zones[zone].add(npc.npc_id)
    
    def remove_npc(self, npc_id: str):
        """移除NPC（线程安全）"""
        with self._lock:
            if npc_id in self.npcs:
                npc = self.npcs[npc_id]
                # 从区域中移除
                for zone, npc_ids in self.zones.items():
                    if npc_id in npc_ids:
                        npc_ids.remove(npc_id)
                        break
                del self.npcs[npc_id]
    
    def get_npc(self, npc_id: str) -> Optional[NPCIndependent]:
        """获取NPC（线程安全）"""
        with self._lock:
            return self.npcs.get(npc_id)
    
    def update_all(self, current_time: float, player_location: str = None):
        """
        更新所有NPC（单线程轮询，线程安全）
        
        Args:
            current_time: 当前时间戳
            player_location: 玩家当前位置
        """
        with self._lock:
            if player_location:
                self.player_location = player_location
            
            # 只更新玩家所在区域的NPC（分区更新）
            npc_ids_to_update = self.zones.get(self.player_location, set()).copy()
        
        updated_count = 0
        for npc_id in npc_ids_to_update:
            npc = self.get_npc(npc_id)
            if npc:
                # 检查是否在玩家附近（简化：同区域视为附近）
                player_nearby = (npc.current_location == self.player_location)
                if npc.update(current_time, player_nearby):
                    updated_count += 1
        
        with self._lock:
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
