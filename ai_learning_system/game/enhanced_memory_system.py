"""
增强记忆系统模块
实现NPC的复杂记忆管理，包括记忆分类、情感色彩、创伤处理和决策影响
"""

import random
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MemoryCategory(Enum):
    """记忆分类"""
    COMBAT = auto()       # 战斗记忆
    SOCIAL = auto()       # 社交记忆
    EXPLORATION = auto()  # 探索记忆
    DECISION = auto()     # 决策记忆
    ACHIEVEMENT = auto()  # 成就记忆
    FAILURE = auto()      # 失败记忆


class MemoryEmotion(Enum):
    """记忆情感色彩"""
    POSITIVE = "positive"    # 积极
    NEGATIVE = "negative"    # 消极
    NEUTRAL = "neutral"      # 中性
    TRAUMA = "trauma"        # 创伤


class MemorySource(Enum):
    """记忆来源"""
    SELF = "self"        # 自己经历
    HEARD = "heard"      # 听说
    WITNESSED = "witnessed"  # 亲眼所见


@dataclass
class EnhancedMemory:
    """
    增强记忆数据类
    
    扩展原有Memory类，包含更丰富的记忆属性和关系
    """
    content: str                          # 记忆内容
    importance: int = 5                   # 重要性 (0-10)
    timestamp: float = field(default_factory=time.time)  # 创建时间
    emotion: MemoryEmotion = MemoryEmotion.NEUTRAL  # 情感色彩
    category: MemoryCategory = MemoryCategory.DECISION  # 记忆分类
    related_memories: List[str] = field(default_factory=list)  # 相关记忆ID列表
    source: MemorySource = MemorySource.SELF  # 记忆来源
    credibility: float = 1.0              # 可信度 (0-1)
    access_count: int = 0                 # 被访问次数
    last_accessed: float = field(default_factory=time.time)  # 最后访问时间
    trauma_score: float = 0.0             # 创伤分数 (0-10)
    
    # 记忆ID（由系统生成）
    memory_id: str = field(default="")
    
    def __post_init__(self):
        """验证字段值的有效性"""
        if not 0 <= self.importance <= 10:
            raise ValueError(f"importance 必须在 0-10 之间，当前值: {self.importance}")
        if not 0 <= self.credibility <= 1:
            raise ValueError(f"credibility 必须在 0-1 之间，当前值: {self.credibility}")
        if not 0 <= self.trauma_score <= 10:
            raise ValueError(f"trauma_score 必须在 0-10 之间，当前值: {self.trauma_score}")
        if self.access_count < 0:
            raise ValueError(f"access_count 不能为负数，当前值: {self.access_count}")
    
    def is_traumatic(self) -> bool:
        """检查是否为创伤记忆"""
        return self.trauma_score > 7 or self.emotion == MemoryEmotion.TRAUMA
    
    def get_age(self, current_time: float = None) -> float:
        """
        获取记忆年龄（天数）
        
        Args:
            current_time: 当前时间戳，默认为None表示使用当前时间
            
        Returns:
            记忆年龄（天数）
        """
        if current_time is None:
            current_time = time.time()
        return (current_time - self.timestamp) / 86400
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "importance": self.importance,
            "timestamp": self.timestamp,
            "emotion": self.emotion.value,
            "category": self.category.name,
            "related_memories": self.related_memories,
            "source": self.source.value,
            "credibility": self.credibility,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "trauma_score": self.trauma_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedMemory':
        """从字典创建EnhancedMemory对象"""
        return cls(
            memory_id=data.get("memory_id", ""),
            content=data["content"],
            importance=data["importance"],
            timestamp=data["timestamp"],
            emotion=MemoryEmotion(data.get("emotion", "neutral")),
            category=MemoryCategory[data.get("category", "DECISION")],
            related_memories=data.get("related_memories", []),
            source=MemorySource(data.get("source", "self")),
            credibility=data.get("credibility", 1.0),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", data["timestamp"]),
            trauma_score=data.get("trauma_score", 0.0),
        )


@dataclass
class DecisionContext:
    """决策上下文"""
    situation: str                    # 情境描述
    available_options: List[str]      # 可用选项
    risk_level: float = 0.5           # 风险等级 (0-1)
    urgency: float = 0.5              # 紧急程度 (0-1)
    involved_npcs: List[str] = field(default_factory=list)  # 涉及的NPC


@dataclass
class DecisionInfluence:
    """记忆对决策的影响"""
    option_index: int                 # 影响的选项索引
    influence_score: float            # 影响分数 (-1到1)
    reason: str                       # 影响原因
    source_memory_id: str             # 来源记忆ID


class EnhancedMemorySystem:
    """
    增强记忆系统核心类
    
    负责管理记忆的增删改查、记忆淡化、创伤处理和决策影响
    """
    
    # 创伤阈值
    TRAUMA_THRESHOLD = 7.0
    
    # 记忆淡化参数
    FADE_RATE = 0.1           # 基础淡化速率
    IMPORTANCE_FADE_FACTOR = 0.05  # 重要性对淡化的影响因子
    
    # 访问对记忆强度的影响
    ACCESS_BOOST = 0.1        # 每次访问提升的强度
    
    def __init__(self, owner_id: str):
        """
        初始化增强记忆系统
        
        Args:
            owner_id: 记忆所有者ID（通常是NPC ID）
        """
        self.owner_id = owner_id
        self.memories: Dict[str, EnhancedMemory] = {}
        self._memory_counter = 0
        
        # 记忆网络（用于快速查找相关记忆）
        self._category_index: Dict[MemoryCategory, Set[str]] = {
            cat: set() for cat in MemoryCategory
        }
        self._emotion_index: Dict[MemoryEmotion, Set[str]] = {
            emo: set() for emo in MemoryEmotion
        }
        
        # 创伤状态
        self._trauma_active = False
        self._trauma_triggers: Set[str] = set()  # 创伤触发关键词
        
        # 决策修正缓存
        self._decision_cache: Dict[str, List[DecisionInfluence]] = {}
    
    def _generate_memory_id(self) -> str:
        """生成唯一记忆ID"""
        self._memory_counter += 1
        return f"{self.owner_id}_mem_{self._memory_counter}_{int(time.time())}"
    
    def add_memory(self, memory: EnhancedMemory) -> str:
        """
        添加记忆
        
        Args:
            memory: 要添加的记忆对象
            
        Returns:
            记忆ID
        """
        # 生成记忆ID
        memory_id = self._generate_memory_id()
        memory.memory_id = memory_id
        
        # 存储记忆
        self.memories[memory_id] = memory
        
        # 更新索引
        self._category_index[memory.category].add(memory_id)
        self._emotion_index[memory.emotion].add(memory_id)
        
        # 检查是否为创伤记忆
        if memory.is_traumatic():
            self._trauma_active = True
            self._extract_trauma_triggers(memory)
        
        return memory_id
    
    def _extract_trauma_triggers(self, memory: EnhancedMemory):
        """从创伤记忆中提取触发关键词"""
        # 简单的关键词提取（可以根据需要扩展）
        keywords = memory.content.split()
        # 提取长度大于2的词作为触发词
        for word in keywords:
            if len(word) > 2:
                self._trauma_triggers.add(word)
    
    def recall(self, query: str, limit: int = 10, 
               category: MemoryCategory = None,
               emotion: MemoryEmotion = None) -> List[EnhancedMemory]:
        """
        根据查询召回相关记忆
        
        Args:
            query: 查询关键词
            limit: 返回记忆数量限制
            category: 可选的分类过滤
            emotion: 可选的情感过滤
            
        Returns:
            相关记忆列表，按相关性排序
        """
        results = []
        query_lower = query.lower()
        
        # 获取候选记忆
        candidate_ids = set(self.memories.keys())
        
        # 应用分类过滤
        if category:
            candidate_ids &= self._category_index[category]
        
        # 应用情感过滤
        if emotion:
            candidate_ids &= self._emotion_index[emotion]
        
        # 计算相关性分数
        for memory_id in candidate_ids:
            memory = self.memories[memory_id]
            relevance = self._calculate_relevance(memory, query_lower)
            
            if relevance > 0:
                # 更新访问信息
                memory.access_count += 1
                memory.last_accessed = time.time()
                results.append((memory, relevance))
        
        # 按相关性排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前limit个
        return [mem for mem, _ in results[:limit]]
    
    def _calculate_relevance(self, memory: EnhancedMemory, query: str) -> float:
        """
        计算记忆与查询的相关性
        
        Args:
            memory: 记忆对象
            query: 查询字符串（小写）
            
        Returns:
            相关性分数 (0-1)
        """
        content_lower = memory.content.lower()
        
        # 基础匹配分数
        if query in content_lower:
            base_score = 0.5
            # 完全匹配加分
            if query == content_lower:
                base_score = 1.0
        else:
            # 部分匹配
            query_words = query.split()
            match_count = sum(1 for word in query_words if word in content_lower)
            if match_count == 0:
                return 0.0
            base_score = 0.3 * (match_count / len(query_words))
        
        # 考虑重要性
        importance_factor = memory.importance / 10.0
        
        # 考虑访问频率（经常访问的记忆更相关）
        access_factor = min(memory.access_count * 0.05, 0.2)
        
        # 考虑时间衰减
        age_days = memory.get_age()
        time_factor = max(0, 1 - age_days * 0.01)
        
        # 创伤记忆权重更高
        trauma_factor = 1.5 if memory.is_traumatic() else 1.0
        
        # 综合计算
        relevance = base_score * (0.4 + 0.3 * importance_factor + 
                                  0.2 * access_factor + 0.1 * time_factor)
        relevance *= trauma_factor
        
        return min(1.0, relevance)
    
    def get_related_memories(self, memory_id: str, 
                            include_indirect: bool = False) -> List[EnhancedMemory]:
        """
        获取相关记忆
        
        Args:
            memory_id: 记忆ID
            include_indirect: 是否包含间接相关记忆
            
        Returns:
            相关记忆列表
        """
        if memory_id not in self.memories:
            return []
        
        memory = self.memories[memory_id]
        related = []
        
        # 直接相关记忆
        for related_id in memory.related_memories:
            if related_id in self.memories:
                related.append(self.memories[related_id])
        
        # 间接相关记忆
        if include_indirect:
            indirect_ids = set()
            for related_memory in related:
                for indirect_id in related_memory.related_memories:
                    if indirect_id != memory_id and indirect_id in self.memories:
                        indirect_ids.add(indirect_id)
            
            for indirect_id in indirect_ids:
                if indirect_id not in memory.related_memories:
                    related.append(self.memories[indirect_id])
        
        return related
    
    def link_memories(self, memory_id1: str, memory_id2: str) -> bool:
        """
        链接两个记忆
        
        Args:
            memory_id1: 第一个记忆ID
            memory_id2: 第二个记忆ID
            
        Returns:
            是否成功链接
        """
        if memory_id1 not in self.memories or memory_id2 not in self.memories:
            return False
        
        # 双向链接
        if memory_id2 not in self.memories[memory_id1].related_memories:
            self.memories[memory_id1].related_memories.append(memory_id2)
        
        if memory_id1 not in self.memories[memory_id2].related_memories:
            self.memories[memory_id2].related_memories.append(memory_id1)
        
        return True
    
    def update_memory_emotion(self, memory_id: str, 
                              emotion: MemoryEmotion) -> bool:
        """
        更新记忆情感
        
        Args:
            memory_id: 记忆ID
            emotion: 新情感
            
        Returns:
            是否成功更新
        """
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        
        # 从旧情感索引中移除
        if memory_id in self._emotion_index[memory.emotion]:
            self._emotion_index[memory.emotion].remove(memory_id)
        
        # 更新情感
        memory.emotion = emotion
        
        # 添加到新情感索引
        self._emotion_index[emotion].add(memory_id)
        
        # 如果更新为创伤情感，更新创伤状态
        if emotion == MemoryEmotion.TRAUMA:
            self._trauma_active = True
            self._extract_trauma_triggers(memory)
        
        return True
    
    def fade_memories(self, current_time: float = None):
        """
        记忆淡化处理
        
        非创伤记忆会随时间淡化，重要性降低
        
        Args:
            current_time: 当前时间戳，默认为None表示使用当前时间
        """
        if current_time is None:
            current_time = time.time()
        
        memories_to_remove = []
        
        for memory_id, memory in self.memories.items():
            # 创伤记忆不会淡化
            if memory.is_traumatic():
                continue
            
            # 计算淡化程度
            age_days = memory.get_age(current_time)
            fade_amount = (self.FADE_RATE * age_days * 
                          (1 - memory.importance * self.IMPORTANCE_FADE_FACTOR))
            
            # 访问可以减缓淡化
            access_protection = min(memory.access_count * self.ACCESS_BOOST, 0.5)
            fade_amount *= (1 - access_protection)
            
            # 应用淡化
            memory.importance = max(0, memory.importance - fade_amount)
            
            # 如果重要性降到0，标记为删除
            if memory.importance <= 0:
                memories_to_remove.append(memory_id)
        
        # 删除淡化的记忆
        for memory_id in memories_to_remove:
            self._remove_memory(memory_id)
    
    def _remove_memory(self, memory_id: str):
        """删除记忆及其索引"""
        if memory_id not in self.memories:
            return
        
        memory = self.memories[memory_id]
        
        # 从索引中移除
        self._category_index[memory.category].discard(memory_id)
        self._emotion_index[memory.emotion].discard(memory_id)
        
        # 从其他记忆的相关列表中移除
        for other_memory in self.memories.values():
            if memory_id in other_memory.related_memories:
                other_memory.related_memories.remove(memory_id)
        
        # 删除记忆
        del self.memories[memory_id]
    
    def get_traumatic_memories(self) -> List[EnhancedMemory]:
        """
        获取所有创伤记忆
        
        Returns:
            创伤记忆列表
        """
        return [
            memory for memory in self.memories.values()
            if memory.is_traumatic()
        ]
    
    def calculate_memory_weight(self, memory: EnhancedMemory) -> float:
        """
        计算记忆权重
        
        权重用于决策时评估记忆的影响力
        
        Args:
            memory: 记忆对象
            
        Returns:
            记忆权重 (0-1)
        """
        # 基础权重来自重要性
        weight = memory.importance / 10.0
        
        # 可信度修正
        weight *= memory.credibility
        
        # 来源修正（亲身经历权重更高）
        source_multiplier = {
            MemorySource.SELF: 1.0,
            MemorySource.WITNESSED: 0.8,
            MemorySource.HEARD: 0.5,
        }
        weight *= source_multiplier.get(memory.source, 0.5)
        
        # 访问频率加成
        weight += min(memory.access_count * 0.02, 0.2)
        
        # 创伤记忆权重加成
        if memory.is_traumatic():
            weight *= 1.5
            weight += memory.trauma_score / 20.0
        
        return min(1.0, weight)
    
    def get_decision_influence(self, context: DecisionContext) -> List[DecisionInfluence]:
        """
        获取记忆对决策的影响
        
        Args:
            context: 决策上下文
            
        Returns:
            决策影响列表
        """
        influences = []
        
        # 召回相关记忆
        relevant_memories = self.recall(
            context.situation, 
            limit=20
        )
        
        # 分析每个选项
        for option_idx, option in enumerate(context.available_options):
            option_memories = self.recall(option, limit=10)
            
            for memory in option_memories + relevant_memories:
                influence = self._analyze_influence(memory, context, option_idx)
                if influence:
                    influences.append(influence)
        
        # 按影响分数排序
        influences.sort(key=lambda x: abs(x.influence_score), reverse=True)
        
        return influences
    
    def _analyze_influence(self, memory: EnhancedMemory, 
                          context: DecisionContext,
                          option_index: int) -> Optional[DecisionInfluence]:
        """
        分析单个记忆对决策的影响
        
        Args:
            memory: 记忆对象
            context: 决策上下文
            option_index: 选项索引
            
        Returns:
            决策影响对象，如果无影响则返回None
        """
        weight = self.calculate_memory_weight(memory)
        
        # 情感影响
        emotion_score = 0.0
        if memory.emotion == MemoryEmotion.POSITIVE:
            emotion_score = 0.3 * weight
        elif memory.emotion == MemoryEmotion.NEGATIVE:
            emotion_score = -0.3 * weight
        elif memory.emotion == MemoryEmotion.TRAUMA:
            emotion_score = -0.8 * weight
        
        # 分类影响
        category_score = 0.0
        if memory.category == MemoryCategory.FAILURE:
            category_score = -0.4 * weight
        elif memory.category == MemoryCategory.ACHIEVEMENT:
            category_score = 0.4 * weight
        elif memory.category == MemoryCategory.COMBAT and context.risk_level > 0.5:
            # 高风险情境下，战斗记忆影响更大
            if memory.emotion == MemoryEmotion.NEGATIVE:
                category_score = -0.5 * weight
            elif memory.emotion == MemoryEmotion.POSITIVE:
                category_score = 0.3 * weight
        
        # 综合影响分数
        total_score = emotion_score + category_score
        
        # 如果影响太小，忽略
        if abs(total_score) < 0.1:
            return None
        
        # 生成影响原因
        reason = self._generate_influence_reason(memory, total_score)
        
        return DecisionInfluence(
            option_index=option_index,
            influence_score=max(-1.0, min(1.0, total_score)),
            reason=reason,
            source_memory_id=memory.memory_id
        )
    
    def _generate_influence_reason(self, memory: EnhancedMemory, 
                                   score: float) -> str:
        """生成影响原因描述"""
        if score > 0.5:
            return f"记得{memory.content[:20]}...（积极经验）"
        elif score > 0:
            return f"想起{memory.content[:20]}...（略有信心）"
        elif score > -0.5:
            return f"担心{memory.content[:20]}...（有些顾虑）"
        else:
            return f"恐惧{memory.content[:20]}...（创伤阴影）"
    
    def apply_memory_to_decision(self, decision: str, 
                                 relevant_memories: List[EnhancedMemory]) -> Tuple[str, float]:
        """
        应用记忆修正决策
        
        Args:
            decision: 原始决策
            relevant_memories: 相关记忆列表
            
        Returns:
            (修正后的决策, 修正强度)
        """
        if not relevant_memories:
            return decision, 0.0
        
        total_modifier = 0.0
        total_weight = 0.0
        
        for memory in relevant_memories:
            weight = self.calculate_memory_weight(memory)
            
            # 根据情感计算修正值
            if memory.emotion == MemoryEmotion.POSITIVE:
                modifier = 0.2
            elif memory.emotion == MemoryEmotion.NEGATIVE:
                modifier = -0.2
            elif memory.emotion == MemoryEmotion.TRAUMA:
                modifier = -0.5
            else:
                modifier = 0.0
            
            # 根据分类调整
            if memory.category == MemoryCategory.FAILURE:
                modifier -= 0.1
            elif memory.category == MemoryCategory.ACHIEVEMENT:
                modifier += 0.1
            
            total_modifier += modifier * weight
            total_weight += weight
        
        if total_weight == 0:
            return decision, 0.0
        
        # 计算平均修正
        avg_modifier = total_modifier / total_weight
        
        # 根据修正强度调整决策描述
        if avg_modifier > 0.3:
            modified_decision = f"充满信心地{decision}"
        elif avg_modifier > 0.1:
            modified_decision = f"谨慎但乐观地{decision}"
        elif avg_modifier < -0.3:
            modified_decision = f"犹豫不决地{decision}"
        elif avg_modifier < -0.1:
            modified_decision = f"带着顾虑{decision}"
        else:
            modified_decision = decision
        
        return modified_decision, avg_modifier
    
    def trauma_response_check(self, situation: str) -> Tuple[bool, float, str]:
        """
        检查创伤反应
        
        Args:
            situation: 当前情境描述
            
        Returns:
            (是否触发创伤反应, 反应强度, 反应描述)
        """
        if not self._trauma_active:
            return False, 0.0, ""
        
        # 检查是否触发创伤关键词
        trigger_count = 0
        situation_lower = situation.lower()
        
        for trigger in self._trauma_triggers:
            if trigger.lower() in situation_lower:
                trigger_count += 1
        
        if trigger_count == 0:
            return False, 0.0, ""
        
        # 计算触发强度
        trigger_strength = min(trigger_count / len(self._trauma_triggers), 1.0)
        
        # 获取创伤记忆的平均创伤分数
        traumatic_memories = self.get_traumatic_memories()
        avg_trauma_score = sum(m.trauma_score for m in traumatic_memories) / len(traumatic_memories)
        
        # 计算反应强度
        response_intensity = trigger_strength * (avg_trauma_score / 10.0)
        
        # 生成反应描述
        if response_intensity > 0.7:
            reaction = "强烈的创伤反应：恐慌、逃避、无法思考"
        elif response_intensity > 0.4:
            reaction = "明显的创伤反应：焦虑、警惕、犹豫"
        elif response_intensity > 0.2:
            reaction = "轻微的创伤反应：不安、警觉"
        else:
            reaction = "隐约的不适感"
        
        return True, response_intensity, reaction
    
    def get_memories_by_category(self, category: MemoryCategory, 
                                 limit: int = None) -> List[EnhancedMemory]:
        """
        按分类获取记忆
        
        Args:
            category: 记忆分类
            limit: 数量限制
            
        Returns:
            记忆列表
        """
        memory_ids = self._category_index[category]
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        
        # 按重要性排序
        memories.sort(key=lambda m: m.importance, reverse=True)
        
        if limit:
            return memories[:limit]
        return memories
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        total_memories = len(self.memories)
        
        if total_memories == 0:
            return {
                "total_memories": 0,
                "traumatic_memories": 0,
                "category_distribution": {},
                "emotion_distribution": {},
                "average_importance": 0.0,
                "trauma_active": False,
            }
        
        # 分类统计
        category_dist = {
            cat.name: len(ids) for cat, ids in self._category_index.items()
        }
        
        # 情感统计
        emotion_dist = {
            emo.value: len(ids) for emo, ids in self._emotion_index.items()
        }
        
        # 平均重要性
        avg_importance = sum(m.importance for m in self.memories.values()) / total_memories
        
        # 创伤记忆统计
        traumatic_count = len(self.get_traumatic_memories())
        
        return {
            "total_memories": total_memories,
            "traumatic_memories": traumatic_count,
            "category_distribution": category_dist,
            "emotion_distribution": emotion_dist,
            "average_importance": round(avg_importance, 2),
            "trauma_active": self._trauma_active,
            "trauma_triggers": list(self._trauma_triggers)[:10],  # 只显示前10个
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "owner_id": self.owner_id,
            "memories": {
                mid: mem.to_dict() for mid, mem in self.memories.items()
            },
            "trauma_active": self._trauma_active,
            "trauma_triggers": list(self._trauma_triggers),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedMemorySystem':
        """从字典创建EnhancedMemorySystem对象"""
        system = cls(data["owner_id"])
        
        # 恢复记忆
        for memory_id, memory_data in data.get("memories", {}).items():
            memory = EnhancedMemory.from_dict(memory_data)
            memory.memory_id = memory_id
            system.memories[memory_id] = memory
            
            # 更新索引
            system._category_index[memory.category].add(memory_id)
            system._emotion_index[memory.emotion].add(memory_id)
            
            # 更新计数器
            counter = int(memory_id.split("_")[2]) if "_" in memory_id else 0
            system._memory_counter = max(system._memory_counter, counter)
        
        # 恢复创伤状态
        system._trauma_active = data.get("trauma_active", False)
        system._trauma_triggers = set(data.get("trauma_triggers", []))
        
        return system


class EnhancedMemoryManager:
    """
    增强记忆系统管理器
    
    管理多个NPC的增强记忆系统
    """
    
    def __init__(self):
        """初始化管理器"""
        self.systems: Dict[str, EnhancedMemorySystem] = {}
    
    def get_or_create_system(self, owner_id: str) -> EnhancedMemorySystem:
        """
        获取或创建记忆系统
        
        Args:
            owner_id: 所有者ID
            
        Returns:
            增强记忆系统实例
        """
        if owner_id not in self.systems:
            self.systems[owner_id] = EnhancedMemorySystem(owner_id)
        return self.systems[owner_id]
    
    def remove_system(self, owner_id: str):
        """
        移除记忆系统
        
        Args:
            owner_id: 所有者ID
        """
        if owner_id in self.systems:
            del self.systems[owner_id]
    
    def fade_all_memories(self, current_time: float = None):
        """
        对所有记忆系统进行淡化处理
        
        Args:
            current_time: 当前时间戳
        """
        for system in self.systems.values():
            system.fade_memories(current_time)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有记忆系统的统计信息
        
        Returns:
            统计信息字典
        """
        return {
            owner_id: system.get_memory_stats()
            for owner_id, system in self.systems.items()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            owner_id: system.to_dict()
            for owner_id, system in self.systems.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedMemoryManager':
        """从字典创建EnhancedMemoryManager对象"""
        manager = cls()
        
        for owner_id, system_data in data.items():
            manager.systems[owner_id] = EnhancedMemorySystem.from_dict(system_data)
        
        return manager


# 全局管理器实例
enhanced_memory_manager = EnhancedMemoryManager()
