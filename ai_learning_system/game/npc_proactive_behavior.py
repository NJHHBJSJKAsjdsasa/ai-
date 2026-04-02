"""
NPC主动行为系统模块
实现NPC的主动对话、挑战、交易、探索等行为
"""

import random
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG, PERSONALITIES


class ProactiveActionType(Enum):
    """主动行为类型"""
    DIALOGUE = auto()       # 主动对话
    COMBAT = auto()         # 主动挑战
    TRADE = auto()          # 主动交易
    EXPLORATION = auto()    # 主动探索
    NONE = auto()           # 无行为


@dataclass
class DialogueRequest:
    """对话请求"""
    initiator_id: str
    initiator_name: str
    target_id: str
    target_name: str
    dialogue_type: str  # "friendly", "help_request", "greeting"
    content: str
    importance: int = 5


@dataclass
class CombatChallenge:
    """战斗挑战"""
    challenger_id: str
    challenger_name: str
    target_id: str
    target_name: str
    combat_type: str  # "spar", "deathmatch"
    reason: str
    challenge_strength: int = 0  # 挑战强度评估


@dataclass
class TradeRequest:
    """交易请求"""
    trader_id: str
    trader_name: str
    target_id: str
    target_name: str
    offered_items: List[Dict[str, Any]] = field(default_factory=list)
    requested_items: List[Dict[str, Any]] = field(default_factory=list)
    offered_gold: int = 0
    requested_gold: int = 0
    reason: str = ""


@dataclass
class ExplorationResult:
    """探索结果"""
    explorer_id: str
    explorer_name: str
    location: str
    discoveries: List[str] = field(default_factory=list)
    found_items: List[Dict[str, Any]] = field(default_factory=list)
    encountered_npcs: List[str] = field(default_factory=list)
    danger_level: int = 0  # 0-10


@dataclass
class ProactiveAction:
    """主动行为"""
    action_type: ProactiveActionType
    action_data: Any
    priority: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CooldownEntry:
    """冷却记录"""
    action_type: ProactiveActionType
    last_used: float
    cooldown_duration: float


class ProactiveBehavior:
    """NPC主动行为系统
    
    管理NPC的主动行为，包括对话、挑战、交易和探索。
    实现冷却机制防止NPC过于频繁地主动行为。
    """
    
    # 冷却时间配置（秒）
    DEFAULT_COOLDOWNS = {
        ProactiveActionType.DIALOGUE: 60.0,      # 对话冷却1分钟
        ProactiveActionType.COMBAT: 300.0,       # 挑战冷却5分钟
        ProactiveActionType.TRADE: 180.0,        # 交易冷却3分钟
        ProactiveActionType.EXPLORATION: 600.0,  # 探索冷却10分钟
    }
    
    # 性格对行为的影响系数
    PERSONALITY_MODIFIERS = {
        "勇敢": {"combat_bonus": 0.3, "exploration_bonus": 0.2, "dialogue_penalty": -0.1},
        "贪婪": {"trade_bonus": 0.4, "combat_bonus": 0.1},
        "好奇": {"exploration_bonus": 0.5, "dialogue_bonus": 0.2},
        "善良": {"dialogue_bonus": 0.3, "combat_penalty": -0.2},
        "开朗": {"dialogue_bonus": 0.4, "trade_bonus": 0.1},
        "阴险": {"combat_bonus": 0.2, "trade_penalty": -0.1},
        "冷酷": {"combat_bonus": 0.3, "dialogue_penalty": -0.2},
        "暴躁": {"combat_bonus": 0.4, "dialogue_penalty": -0.1},
    }
    
    def __init__(self):
        """初始化主动行为系统"""
        self.cooldowns: Dict[str, Dict[ProactiveActionType, CooldownEntry]] = {}
        self.action_history: Dict[str, List[ProactiveAction]] = {}
        self.max_history_size = 50
    
    def _get_personality_modifiers(self, personality: str) -> Dict[str, float]:
        """
        获取性格修饰符
        
        Args:
            personality: NPC性格
            
        Returns:
            修饰符字典
        """
        modifiers = {}
        for trait, mods in self.PERSONALITY_MODIFIERS.items():
            if trait in personality:
                for key, value in mods.items():
                    modifiers[key] = modifiers.get(key, 0) + value
        return modifiers
    
    def _is_on_cooldown(self, npc_id: str, action_type: ProactiveActionType) -> bool:
        """
        检查行为是否在冷却中
        
        Args:
            npc_id: NPC ID
            action_type: 行为类型
            
        Returns:
            是否在冷却中
        """
        if npc_id not in self.cooldowns:
            return False
        
        if action_type not in self.cooldowns[npc_id]:
            return False
        
        entry = self.cooldowns[npc_id][action_type]
        elapsed = time.time() - entry.last_used
        return elapsed < entry.cooldown_duration
    
    def _get_remaining_cooldown(self, npc_id: str, action_type: ProactiveActionType) -> float:
        """
        获取剩余冷却时间
        
        Args:
            npc_id: NPC ID
            action_type: 行为类型
            
        Returns:
            剩余冷却时间（秒），0表示不在冷却中
        """
        if not self._is_on_cooldown(npc_id, action_type):
            return 0.0
        
        entry = self.cooldowns[npc_id][action_type]
        elapsed = time.time() - entry.last_used
        return max(0.0, entry.cooldown_duration - elapsed)
    
    def _set_cooldown(self, npc_id: str, action_type: ProactiveActionType, 
                      duration: Optional[float] = None):
        """
        设置行为冷却
        
        Args:
            npc_id: NPC ID
            action_type: 行为类型
            duration: 冷却时间，None则使用默认值
        """
        if npc_id not in self.cooldowns:
            self.cooldowns[npc_id] = {}
        
        if duration is None:
            duration = self.DEFAULT_COOLDOWNS.get(action_type, 60.0)
        
        self.cooldowns[npc_id][action_type] = CooldownEntry(
            action_type=action_type,
            last_used=time.time(),
            cooldown_duration=duration
        )
    
    def _record_action(self, npc_id: str, action: ProactiveAction):
        """
        记录NPC行为
        
        Args:
            npc_id: NPC ID
            action: 行为记录
        """
        if npc_id not in self.action_history:
            self.action_history[npc_id] = []
        
        self.action_history[npc_id].append(action)
        
        # 限制历史记录大小
        if len(self.action_history[npc_id]) > self.max_history_size:
            self.action_history[npc_id] = self.action_history[npc_id][-self.max_history_size:]
    
    def _get_relationship_score(self, npc, target) -> float:
        """
        获取与目标的关系分数
        
        Args:
            npc: NPC对象
            target: 目标对象
            
        Returns:
            关系分数（-100到100）
        """
        if hasattr(npc, 'independent') and hasattr(target.data, 'id'):
            rel = npc.independent.get_relationship(target.data.id)
            return rel.affinity if hasattr(rel, 'affinity') else 0.0
        return 0.0
    
    def _calculate_power_difference(self, npc, target) -> float:
        """
        计算与目标的实力差距
        
        Args:
            npc: NPC对象
            target: 目标对象
            
        Returns:
            实力差距比例（正数表示NPC更强）
        """
        npc_power = npc.get_combat_power() if hasattr(npc, 'get_combat_power') else 100
        target_power = target.get_combat_power() if hasattr(target, 'get_combat_power') else 100
        
        if target_power == 0:
            return 1.0
        
        return (npc_power - target_power) / target_power
    
    def initiate_dialogue(self, npc, target) -> Optional[DialogueRequest]:
        """
        主动对话逻辑
        
        根据关系度决定是否主动对话：
        - 好感度高时主动友好交流
        - 有需求时主动求助
        
        Args:
            npc: 发起对话的NPC
            target: 对话目标
            
        Returns:
            对话请求对象，如果不发起对话则返回None
        """
        npc_id = npc.data.id if hasattr(npc, 'data') else str(id(npc))
        
        # 检查冷却
        if self._is_on_cooldown(npc_id, ProactiveActionType.DIALOGUE):
            return None
        
        # 获取关系分数
        relationship = self._get_relationship_score(npc, target)
        
        # 获取性格修饰符
        personality = npc.data.personality if hasattr(npc.data, 'personality') else ""
        modifiers = self._get_personality_modifiers(personality)
        dialogue_bonus = modifiers.get("dialogue_bonus", 0)
        
        # 基础对话概率
        base_chance = 0.3 + dialogue_bonus
        
        # 根据关系调整概率
        if relationship >= 50:
            chance = base_chance + 0.3
            dialogue_type = "friendly"
        elif relationship >= 0:
            chance = base_chance + 0.1
            dialogue_type = "greeting"
        elif relationship >= -30:
            chance = base_chance - 0.1
            dialogue_type = "neutral"
        else:
            # 关系差时通常不主动对话
            return None
        
        # 检查是否有需求
        needs_help = False
        if hasattr(npc, 'independent') and hasattr(npc.independent, 'needs'):
            for need_type, need in npc.independent.needs.items():
                if need.is_urgent():
                    needs_help = True
                    break
        
        if needs_help and relationship >= 0:
            chance += 0.2
            dialogue_type = "help_request"
        
        # 判断是否发起对话
        if random.random() > max(0.0, min(1.0, chance)):
            return None
        
        # 生成对话内容
        npc_name = npc.data.dao_name if hasattr(npc.data, 'dao_name') else "NPC"
        target_name = target.data.dao_name if hasattr(target.data, 'dao_name') else "目标"
        
        if dialogue_type == "friendly":
            contents = [
                f"{target_name}道友，今日天气不错，不如我们聊聊？",
                f"哈哈，{target_name}道友，好久不见，近来可好？",
                f"{target_name}道友，我近日有些修炼心得，想与你分享。",
            ]
        elif dialogue_type == "help_request":
            contents = [
                f"{target_name}道友，我近日修炼遇到瓶颈，不知可否请教一二？",
                f"{target_name}道友，我急需一些材料，不知你手上可有？",
                f"{target_name}道友，能否帮我一个忙？必有重谢。",
            ]
        elif dialogue_type == "greeting":
            contents = [
                f"{target_name}道友，有礼了。",
                f"见过{target_name}道友。",
                f"{target_name}道友安好。",
            ]
        else:
            contents = [
                f"（看了{target_name}一眼）",
                f"{target_name}道友...",
            ]
        
        content = random.choice(contents)
        
        # 设置冷却
        self._set_cooldown(npc_id, ProactiveActionType.DIALOGUE)
        
        # 记录行为
        request = DialogueRequest(
            initiator_id=npc_id,
            initiator_name=npc_name,
            target_id=target.data.id if hasattr(target.data, 'id') else str(id(target)),
            target_name=target_name,
            dialogue_type=dialogue_type,
            content=content,
            importance=6 if dialogue_type == "friendly" else 4
        )
        
        self._record_action(npc_id, ProactiveAction(
            action_type=ProactiveActionType.DIALOGUE,
            action_data=request,
            priority=chance
        ))
        
        return request
    
    def initiate_combat(self, npc, target) -> Optional[CombatChallenge]:
        """
        主动挑战逻辑
        
        - 对仇人主动发起挑战
        - 根据实力差距决定是否挑战
        - 勇敢性格的NPC更可能挑战
        
        Args:
            npc: 发起挑战的NPC
            target: 挑战目标
            
        Returns:
            战斗挑战对象，如果不发起挑战则返回None
        """
        npc_id = npc.data.id if hasattr(npc, 'data') else str(id(npc))
        
        # 检查冷却
        if self._is_on_cooldown(npc_id, ProactiveActionType.COMBAT):
            return None
        
        # 获取关系分数
        relationship = self._get_relationship_score(npc, target)
        
        # 获取性格修饰符
        personality = npc.data.personality if hasattr(npc.data, 'personality') else ""
        modifiers = self._get_personality_modifiers(personality)
        combat_bonus = modifiers.get("combat_bonus", 0)
        
        # 计算实力差距
        power_diff = self._calculate_power_difference(npc, target)
        
        # 基础挑战概率
        base_chance = 0.1 + combat_bonus
        
        # 根据关系决定挑战类型
        if relationship <= -50:
            # 仇敌关系，可能发起死斗
            combat_type = "deathmatch"
            chance = base_chance + 0.3
            reason = "仇敌相见"
        elif relationship <= -20:
            # 关系差，可能切磋
            combat_type = "spar"
            chance = base_chance + 0.15
            reason = "关系不和"
        elif relationship >= 30:
            # 关系好，可能友好切磋
            combat_type = "spar"
            chance = base_chance + 0.1
            reason = "互相切磋"
        else:
            # 普通关系，低概率切磋
            combat_type = "spar"
            chance = base_chance
            reason = "试探实力"
        
        # 根据实力差距调整
        if power_diff > 0.3:
            # NPC明显更强，更可能挑战
            chance += 0.15
        elif power_diff < -0.3:
            # NPC明显更弱，降低挑战概率（除非勇敢性格）
            if combat_bonus > 0.2:
                chance += 0.05  # 勇敢NPC仍可能挑战
            else:
                chance -= 0.2
        
        # 判断是否发起挑战
        if random.random() > max(0.0, min(1.0, chance)):
            return None
        
        # 生成挑战
        npc_name = npc.data.dao_name if hasattr(npc.data, 'dao_name') else "NPC"
        target_name = target.data.dao_name if hasattr(target.data, 'dao_name') else "目标"
        
        # 设置冷却
        cooldown_duration = 600.0 if combat_type == "deathmatch" else 300.0
        self._set_cooldown(npc_id, ProactiveActionType.COMBAT, cooldown_duration)
        
        # 记录行为
        challenge = CombatChallenge(
            challenger_id=npc_id,
            challenger_name=npc_name,
            target_id=target.data.id if hasattr(target.data, 'id') else str(id(target)),
            target_name=target_name,
            combat_type=combat_type,
            reason=reason,
            challenge_strength=int(abs(power_diff) * 100)
        )
        
        self._record_action(npc_id, ProactiveAction(
            action_type=ProactiveActionType.COMBAT,
            action_data=challenge,
            priority=chance
        ))
        
        return challenge
    
    def initiate_trade(self, npc, target) -> Optional[TradeRequest]:
        """
        主动交易逻辑
        
        - 需要物品时主动寻求交易
        - 贪婪性格的NPC更可能主动交易
        
        Args:
            npc: 发起交易的NPC
            target: 交易目标
            
        Returns:
            交易请求对象，如果不发起交易则返回None
        """
        npc_id = npc.data.id if hasattr(npc, 'data') else str(id(npc))
        
        # 检查冷却
        if self._is_on_cooldown(npc_id, ProactiveActionType.TRADE):
            return None
        
        # 获取关系分数
        relationship = self._get_relationship_score(npc, target)
        
        # 获取性格修饰符
        personality = npc.data.personality if hasattr(npc.data, 'personality') else ""
        modifiers = self._get_personality_modifiers(personality)
        trade_bonus = modifiers.get("trade_bonus", 0)
        
        # 基础交易概率
        base_chance = 0.2 + trade_bonus
        
        # 根据关系调整
        if relationship >= 30:
            chance = base_chance + 0.2
        elif relationship >= 0:
            chance = base_chance + 0.1
        elif relationship >= -20:
            chance = base_chance - 0.1
        else:
            # 关系差时不交易
            return None
        
        # 检查NPC是否有交易需求
        has_need = False
        reason = ""
        
        # 检查是否需要物品
        occupation = npc.data.occupation if hasattr(npc.data, 'occupation') else ""
        if "炼丹" in occupation or "炼器" in occupation:
            has_need = True
            reason = "需要炼丹/炼器材料"
        elif "商" in occupation:
            has_need = True
            reason = "寻找商机"
            chance += 0.2
        
        # 贪婪性格更可能交易
        if "贪婪" in personality:
            has_need = True
            reason = "想要赚取更多灵石"
            chance += 0.15
        
        if not has_need and random.random() > 0.3:
            return None
        
        # 判断是否发起交易
        if random.random() > max(0.0, min(1.0, chance)):
            return None
        
        # 生成交易请求
        npc_name = npc.data.dao_name if hasattr(npc.data, 'dao_name') else "NPC"
        target_name = target.data.dao_name if hasattr(target.data, 'dao_name') else "目标"
        
        # 生成交易内容
        offered_gold = random.randint(10, 100) if random.random() < 0.5 else 0
        requested_gold = random.randint(10, 100) if offered_gold == 0 else 0
        
        # 设置冷却
        self._set_cooldown(npc_id, ProactiveActionType.TRADE)
        
        # 记录行为
        request = TradeRequest(
            trader_id=npc_id,
            trader_name=npc_name,
            target_id=target.data.id if hasattr(target.data, 'id') else str(id(target)),
            target_name=target_name,
            offered_gold=offered_gold,
            requested_gold=requested_gold,
            reason=reason
        )
        
        self._record_action(npc_id, ProactiveAction(
            action_type=ProactiveActionType.TRADE,
            action_data=request,
            priority=chance
        ))
        
        return request
    
    def initiate_exploration(self, npc, world_state: Optional[Dict[str, Any]] = None) -> Optional[ExplorationResult]:
        """
        主动探索逻辑
        
        - 好奇性格的NPC主动探索
        - 根据当前目标决定是否探索
        
        Args:
            npc: 探索的NPC
            world_state: 世界状态信息
            
        Returns:
            探索结果对象，如果不探索则返回None
        """
        npc_id = npc.data.id if hasattr(npc, 'data') else str(id(npc))
        
        # 检查冷却
        if self._is_on_cooldown(npc_id, ProactiveActionType.EXPLORATION):
            return None
        
        # 获取性格修饰符
        personality = npc.data.personality if hasattr(npc.data, 'personality') else ""
        modifiers = self._get_personality_modifiers(personality)
        exploration_bonus = modifiers.get("exploration_bonus", 0)
        
        # 基础探索概率
        base_chance = 0.15 + exploration_bonus
        
        # 检查是否有探索目标
        has_exploration_goal = False
        if hasattr(npc, 'independent') and hasattr(npc.independent, 'goals'):
            for goal in npc.independent.goals:
                if hasattr(goal, 'goal_type') and goal.goal_type.name == "EXPLORATION":
                    if not goal.is_completed:
                        has_exploration_goal = True
                        base_chance += 0.2
                        break
        
        # 好奇性格更可能探索
        if "好奇" in personality or "求知" in personality:
            base_chance += 0.25
        
        # 猎人职业更可能探索
        occupation = npc.data.occupation if hasattr(npc.data, 'occupation') else ""
        if "猎" in occupation or "渔" in occupation:
            base_chance += 0.15
        
        # 判断是否探索
        if random.random() > max(0.0, min(1.0, base_chance)):
            return None
        
        # 生成探索结果
        npc_name = npc.data.dao_name if hasattr(npc.data, 'dao_name') else "NPC"
        location = npc.data.location if hasattr(npc.data, 'location') else "未知地点"
        
        # 生成发现
        discoveries = []
        found_items = []
        encountered_npcs = []
        danger_level = random.randint(0, 5)
        
        # 根据地点生成不同的发现
        if "山" in location or "林" in location:
            discoveries = ["发现了一处灵气充沛的洞穴", "找到了几株珍稀草药"]
            found_items = [{"name": "灵芝", "type": "herb", "value": 50}]
        elif "城" in location or "镇" in location:
            discoveries = ["发现了一家隐秘的店铺", "听到了一些有趣的消息"]
            encountered_npcs = ["神秘商人", "流浪修士"]
        else:
            discoveries = ["发现了一些有趣的事物", "探索了周边区域"]
        
        # 随机增加危险
        if random.random() < 0.2:
            danger_level += random.randint(3, 5)
            discoveries.append("遭遇了危险！")
        
        # 设置冷却
        self._set_cooldown(npc_id, ProactiveActionType.EXPLORATION)
        
        # 记录行为
        result = ExplorationResult(
            explorer_id=npc_id,
            explorer_name=npc_name,
            location=location,
            discoveries=discoveries,
            found_items=found_items,
            encountered_npcs=encountered_npcs,
            danger_level=danger_level
        )
        
        self._record_action(npc_id, ProactiveAction(
            action_type=ProactiveActionType.EXPLORATION,
            action_data=result,
            priority=base_chance
        ))
        
        # 添加记忆
        if hasattr(npc, 'independent'):
            discovery_text = "，".join(discoveries[:2])
            npc.independent.add_memory(
                f"在{location}探索，{discovery_text}",
                importance=4 + danger_level // 3
            )
        
        return result
    
    def decide_proactive_action(self, npc, world_state: Dict[str, Any]) -> Optional[ProactiveAction]:
        """
        主动行为决策逻辑
        
        计算各种主动行为的优先级，检查触发条件，考虑冷却时间，
        返回决定采取的行动。
        
        Args:
            npc: NPC对象
            world_state: 世界状态信息，包含：
                - nearby_npcs: 附近的NPC列表
                - player_nearby: 玩家是否在附近
                - location: 当前地点
                - time_of_day: 当前时间（0-23）
                
        Returns:
            决定采取的主动行为，如果无行为则返回None
        """
        npc_id = npc.data.id if hasattr(npc, 'data') else str(id(npc))
        
        # 获取附近的NPC
        nearby_npcs = world_state.get("nearby_npcs", [])
        player_nearby = world_state.get("player_nearby", False)
        time_of_day = world_state.get("time_of_day", 12)
        
        # 如果没有附近的NPC，只能探索
        if not nearby_npcs:
            if random.random() < 0.3:
                result = self.initiate_exploration(npc, world_state)
                if result:
                    return ProactiveAction(
                        action_type=ProactiveActionType.EXPLORATION,
                        action_data=result,
                        priority=0.3
                    )
            return None
        
        # 计算各种行为的优先级
        action_priorities: List[Tuple[ProactiveActionType, float, Any, Callable]] = []
        
        # 获取性格修饰符
        personality = npc.data.personality if hasattr(npc.data, 'personality') else ""
        modifiers = self._get_personality_modifiers(personality)
        
        for target in nearby_npcs:
            # 对话优先级
            if not self._is_on_cooldown(npc_id, ProactiveActionType.DIALOGUE):
                dialogue_bonus = modifiers.get("dialogue_bonus", 0)
                relationship = self._get_relationship_score(npc, target)
                
                if relationship >= 30:
                    dialogue_priority = 0.6 + dialogue_bonus
                elif relationship >= 0:
                    dialogue_priority = 0.4 + dialogue_bonus
                elif relationship >= -20:
                    dialogue_priority = 0.2 + dialogue_bonus
                else:
                    dialogue_priority = 0.0
                
                if dialogue_priority > 0:
                    action_priorities.append((
                        ProactiveActionType.DIALOGUE,
                        dialogue_priority,
                        target,
                        lambda n=npc, t=target: self.initiate_dialogue(n, t)
                    ))
            
            # 挑战优先级
            if not self._is_on_cooldown(npc_id, ProactiveActionType.COMBAT):
                combat_bonus = modifiers.get("combat_bonus", 0)
                relationship = self._get_relationship_score(npc, target)
                power_diff = self._calculate_power_difference(npc, target)
                
                if relationship <= -50:
                    combat_priority = 0.7 + combat_bonus
                elif relationship <= -20:
                    combat_priority = 0.4 + combat_bonus
                elif relationship >= 30 and power_diff > -0.2:
                    # 友好切磋
                    combat_priority = 0.3 + combat_bonus
                else:
                    combat_priority = 0.1 + combat_bonus
                
                # 实力差距影响
                if power_diff > 0.2:
                    combat_priority += 0.1
                elif power_diff < -0.4:
                    combat_priority -= 0.2
                
                if combat_priority > 0:
                    action_priorities.append((
                        ProactiveActionType.COMBAT,
                        combat_priority,
                        target,
                        lambda n=npc, t=target: self.initiate_combat(n, t)
                    ))
            
            # 交易优先级
            if not self._is_on_cooldown(npc_id, ProactiveActionType.TRADE):
                trade_bonus = modifiers.get("trade_bonus", 0)
                relationship = self._get_relationship_score(npc, target)
                
                if relationship >= 20:
                    trade_priority = 0.4 + trade_bonus
                elif relationship >= 0:
                    trade_priority = 0.25 + trade_bonus
                else:
                    trade_priority = 0.0
                
                # 商人职业增加交易概率
                occupation = npc.data.occupation if hasattr(npc.data, 'occupation') else ""
                if "商" in occupation:
                    trade_priority += 0.2
                
                if trade_priority > 0:
                    action_priorities.append((
                        ProactiveActionType.TRADE,
                        trade_priority,
                        target,
                        lambda n=npc, t=target: self.initiate_trade(n, t)
                    ))
        
        # 探索优先级（不需要目标）
        if not self._is_on_cooldown(npc_id, ProactiveActionType.EXPLORATION):
            exploration_bonus = modifiers.get("exploration_bonus", 0)
            exploration_priority = 0.2 + exploration_bonus
            
            # 夜晚降低探索概率
            if time_of_day < 6 or time_of_day > 20:
                exploration_priority -= 0.1
            
            # 好奇性格增加探索概率
            if "好奇" in personality:
                exploration_priority += 0.15
            
            if exploration_priority > 0:
                action_priorities.append((
                    ProactiveActionType.EXPLORATION,
                    exploration_priority,
                    None,
                    lambda n=npc: self.initiate_exploration(n, world_state)
                ))
        
        # 如果没有可行的行为
        if not action_priorities:
            return None
        
        # 按优先级排序
        action_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # 尝试执行最高优先级的行为
        for action_type, priority, target, action_func in action_priorities:
            result = action_func()
            if result:
                return ProactiveAction(
                    action_type=action_type,
                    action_data=result,
                    priority=priority
                )
        
        return None
    
    def get_npc_cooldowns(self, npc_id: str) -> Dict[str, float]:
        """
        获取NPC的所有冷却状态
        
        Args:
            npc_id: NPC ID
            
        Returns:
            冷却状态字典，键为行为类型名称，值为剩余冷却时间
        """
        cooldowns = {}
        for action_type in ProactiveActionType:
            if action_type != ProactiveActionType.NONE:
                remaining = self._get_remaining_cooldown(npc_id, action_type)
                cooldowns[action_type.name] = remaining
        return cooldowns
    
    def get_action_history(self, npc_id: str, limit: int = 10) -> List[ProactiveAction]:
        """
        获取NPC的行为历史
        
        Args:
            npc_id: NPC ID
            limit: 返回的最大记录数
            
        Returns:
            行为历史列表
        """
        history = self.action_history.get(npc_id, [])
        return history[-limit:] if history else []
    
    def clear_cooldown(self, npc_id: str, action_type: Optional[ProactiveActionType] = None):
        """
        清除NPC的冷却
        
        Args:
            npc_id: NPC ID
            action_type: 行为类型，None则清除所有冷却
        """
        if npc_id not in self.cooldowns:
            return
        
        if action_type is None:
            self.cooldowns[npc_id] = {}
        elif action_type in self.cooldowns[npc_id]:
            del self.cooldowns[npc_id][action_type]
    
    def reset_all_cooldowns(self, npc_id: str):
        """
        重置NPC的所有冷却时间
        
        Args:
            npc_id: NPC ID
        """
        self.clear_cooldown(npc_id)
    
    def is_on_cooldown(self, npc_id: str, action_type_str: str) -> bool:
        """
        检查行为是否在冷却中（公共接口）
        
        Args:
            npc_id: NPC ID
            action_type_str: 行为类型字符串 (dialogue/combat/trade/exploration)
            
        Returns:
            是否在冷却中
        """
        type_map = {
            "dialogue": ProactiveActionType.DIALOGUE,
            "combat": ProactiveActionType.COMBAT,
            "trade": ProactiveActionType.TRADE,
            "exploration": ProactiveActionType.EXPLORATION,
        }
        action_type = type_map.get(action_type_str.lower())
        if not action_type:
            return False
        return self._is_on_cooldown(npc_id, action_type)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Returns:
            统计信息字典
        """
        total_npcs = len(self.action_history)
        total_actions = sum(len(history) for history in self.action_history.values())
        
        action_counts = {action_type.name: 0 for action_type in ProactiveActionType}
        for history in self.action_history.values():
            for action in history:
                action_counts[action.action_type.name] += 1
        
        return {
            "total_npcs_tracked": total_npcs,
            "total_actions_recorded": total_actions,
            "action_counts": action_counts,
            "npcs_on_cooldown": len(self.cooldowns),
        }


# 全局主动行为系统实例
proactive_behavior = ProactiveBehavior()
