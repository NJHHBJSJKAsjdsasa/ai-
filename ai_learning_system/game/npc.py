"""
NPC系统模块
管理NPC生成、记忆、交互等
集成NPC独立系统
"""

import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    get_realm_info, get_realm_title, PERSONALITIES, SECTS, SECT_DETAILS,
    DAO_NAME_PREFIX, DAO_NAME_SUFFIX, GAME_CONFIG
)

# 导入NPC独立系统
from game.npc_independent import NPCIndependent, NPCIndependentManager


@dataclass
class NPCMemory:
    """NPC记忆数据类"""
    content: str
    importance: int = 5  # 重要性（0-10）
    timestamp: int = 0  # 游戏时间戳
    emotion: str = "neutral"  # 情感（positive/negative/neutral）


@dataclass
class NPCData:
    """NPC数据类"""
    id: str
    name: str
    dao_name: str
    age: int
    lifespan: int
    realm_level: int
    sect: str
    personality: str
    occupation: str
    location: str
    
    # 门派相关信息
    sect_type: str = ""  # 门派类型（正道/邪道/中立）
    sect_specialty: str = ""  # 门派专长
    
    # 关系
    favor: Dict[str, int] = field(default_factory=dict)  # 对玩家的好感度
    
    # 记忆
    memories: List[NPCMemory] = field(default_factory=list)
    
    # 状态
    is_alive: bool = True
    
    def __post_init__(self):
        if not self.memories:
            self.memories = []


class NPC:
    """NPC类 - 集成独立系统"""
    
    def __init__(self, npc_data: Optional[NPCData] = None):
        """
        初始化NPC
        
        Args:
            npc_data: NPC数据
        """
        if npc_data:
            self.data = npc_data
        else:
            self.data = self._generate_random_npc()
        
        # 初始化NPC独立系统
        npc_data_dict = {
            "occupation": self.data.occupation,
            "location": self.data.location,
            "personality": self.data.personality,
        }
        self.independent = NPCIndependent(self.data.id, npc_data_dict)
    
    def update(self, current_time: float = None, player_nearby: bool = False) -> bool:
        """
        更新NPC状态（独立系统）
        
        Args:
            current_time: 当前时间戳
            player_nearby: 玩家是否在附近
            
        Returns:
            是否执行了更新
        """
        if current_time is None:
            current_time = time.time()
        return self.independent.update(current_time, player_nearby)
    
    def get_independent_status(self) -> Dict[str, Any]:
        """获取独立系统状态"""
        return self.independent.get_status()
    
    def socialize_with(self, other_npc: 'NPC'):
        """
        与另一个NPC社交
        
        Args:
            other_npc: 另一个NPC
        """
        # 更新关系
        affinity_change = random.uniform(-2, 5)
        self.independent.update_relationship(other_npc.data.id, affinity_change)
        other_npc.independent.update_relationship(self.data.id, affinity_change)
        
        # 分享记忆
        if self.independent.memories and random.random() < 0.3:
            memory = random.choice(self.independent.memories)
            other_npc.independent.add_memory(
                f"听{self.data.dao_name}说: {memory.content}", 
                importance=memory.importance//2
            )
        
        if other_npc.independent.memories and random.random() < 0.3:
            memory = random.choice(other_npc.independent.memories)
            self.independent.add_memory(
                f"听{other_npc.data.dao_name}说: {memory.content}", 
                importance=memory.importance//2
            )
        
        # 记录互动记忆
        self.independent.add_memory(f"与{other_npc.data.dao_name}交流了一番", importance=3)
        other_npc.independent.add_memory(f"与{self.data.dao_name}交流了一番", importance=3)
    
    def _generate_random_npc(self) -> NPCData:
        """生成随机NPC"""
        # 生成道号
        dao_name = random.choice(DAO_NAME_PREFIX) + random.choice(DAO_NAME_SUFFIX)
        
        # 随机境界（根据概率分布）
        realm_weights = [30, 25, 20, 15, 8, 2, 0, 0]  # 凡人到大乘的概率
        realm_level = random.choices(range(8), weights=realm_weights)[0]
        
        # 获取境界信息
        realm_info = get_realm_info(realm_level)
        
        # 随机年龄
        if realm_level == 0:
            age = random.randint(16, 60)
            lifespan = 80
        else:
            min_age = 16 + realm_level * 10
            max_age = realm_info.lifespan if realm_info else 100
            age = random.randint(min_age, min(max_age - 10, max_age))
            lifespan = realm_info.lifespan if realm_info else 100
        
        # 随机门派（优先使用有详细信息的门派）
        if SECT_DETAILS and random.random() < 0.7:  # 70%概率使用有详细信息的门派
            sect = random.choice(list(SECT_DETAILS.keys()))
            sect_info = SECT_DETAILS.get(sect, {})
            sect_type = sect_info.get("type", "中立")
            sect_specialty = sect_info.get("specialty", "")
            
            # 根据门派类型调整职业
            if sect_specialty == "炼丹术":
                occupations = ["炼丹师", "药商", "门派弟子", "散修"]
            elif sect_specialty == "驭兽术":
                occupations = ["驭兽师", "猎人", "门派弟子", "散修"]
            elif sect_specialty == "剑道" or sect_specialty == "巨剑术":
                occupations = ["剑修", "门派弟子", "散修", "猎人"]
            elif sect_specialty == "炼体术":
                occupations = ["体修", "门派弟子", "散修", "铁匠"]
            elif sect_specialty == "符箓之道":
                occupations = ["符师", "门派弟子", "散修", "药商"]
            else:
                occupations = ["药商", "铁匠", "散修", "门派弟子", "炼丹师", "炼器师", "猎人", "渔夫"]
        else:
            sect = random.choice(SECTS)
            sect_type = ""
            sect_specialty = ""
            occupations = ["药商", "铁匠", "散修", "门派弟子", "炼丹师", "炼器师", "猎人", "渔夫"]
        
        occupation = random.choice(occupations)
        
        # 随机性格
        personality = random.choice(PERSONALITIES)
        
        # 生成ID
        npc_id = f"npc_{random.randint(10000, 99999)}"
        
        return NPCData(
            id=npc_id,
            name=dao_name,
            dao_name=dao_name,
            age=age,
            lifespan=lifespan,
            realm_level=realm_level,
            sect=sect,
            sect_type=sect_type,
            sect_specialty=sect_specialty,
            personality=personality,
            occupation=occupation,
            location="新手村",
        )
    
    def get_realm_name(self) -> str:
        """获取境界名称"""
        realm_info = get_realm_info(self.data.realm_level)
        return realm_info.name if realm_info else "凡人"
    
    def get_sect_description(self) -> str:
        """获取门派描述"""
        if self.data.sect in SECT_DETAILS:
            sect_info = SECT_DETAILS[self.data.sect]
            return f"{self.data.sect}（{sect_info.get('type', '未知')}）- {sect_info.get('description', '')[:50]}..."
        return self.data.sect
    
    def get_sect_info(self) -> Dict[str, str]:
        """获取门派详细信息"""
        if self.data.sect in SECT_DETAILS:
            return SECT_DETAILS[self.data.sect]
        return {}
    
    def get_title(self, for_self: bool = False) -> str:
        """获取称谓"""
        return get_realm_title(self.data.realm_level, for_self)
    
    def add_memory(self, content: str, importance: int = 5, emotion: str = "neutral"):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            importance: 重要性
            emotion: 情感
        """
        memory = NPCMemory(
            content=content,
            importance=importance,
            emotion=emotion,
        )
        self.data.memories.append(memory)
        
        # 限制记忆数量
        max_memories = GAME_CONFIG["npc"]["npc_interaction_memory_limit"]
        if len(self.data.memories) > max_memories:
            # 删除重要性最低的记忆
            self.data.memories.sort(key=lambda m: m.importance)
            self.data.memories = self.data.memories[-max_memories:]
    
    def update_favor(self, player_name: str, delta: int):
        """
        更新好感度
        
        Args:
            player_name: 玩家名字
            delta: 变化值
        """
        current = self.data.favor.get(player_name, 0)
        self.data.favor[player_name] = max(-100, min(100, current + delta))
    
    def get_favor(self, player_name: str) -> int:
        """
        获取好感度
        
        Args:
            player_name: 玩家名字
            
        Returns:
            好感度值
        """
        return self.data.favor.get(player_name, 0)
    
    def get_greeting(self, player_name: str) -> str:
        """
        获取问候语
        
        Args:
            player_name: 玩家名字
            
        Returns:
            问候语
        """
        favor = self.get_favor(player_name)
        
        if favor >= 50:
            greetings = [
                f"{player_name}道友！好久不见，别来无恙？",
                f"哈哈，{player_name}道友来了，快请进！",
                f"{player_name}道友，今日可要多叙叙旧。",
            ]
        elif favor >= 0:
            greetings = [
                f"{player_name}道友，有礼了。",
                f"见过{player_name}道友。",
                f"{player_name}道友安好。",
            ]
        elif favor >= -50:
            greetings = [
                f"...（冷淡地看着{player_name}）",
                f"{player_name}道友，有何贵干？",
                f"哼，{player_name}...",
            ]
        else:
            greetings = [
                f"{player_name}！你还敢出现在我面前？",
                f"滚！我不想见到你！",
                f"（怒目而视）{player_name}...",
            ]
        
        return random.choice(greetings)
    
    def advance_time(self, days: int = 1):
        """
        推进时间
        
        Args:
            days: 天数
        """
        self.data.age += days // 365
        
        # 检查寿元
        if self.data.age >= self.data.lifespan:
            self.data.is_alive = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.data.id,
            "name": self.data.name,
            "dao_name": self.data.dao_name,
            "age": self.data.age,
            "lifespan": self.data.lifespan,
            "realm_level": self.data.realm_level,
            "sect": self.data.sect,
            "personality": self.data.personality,
            "occupation": self.data.occupation,
            "location": self.data.location,
            "favor": self.data.favor,
            "is_alive": self.data.is_alive,
        }
    
    def __str__(self) -> str:
        return f"{self.data.dao_name} ({self.get_realm_name()})"


class NPCManager:
    """NPC管理器 - 集成独立系统"""
    
    def __init__(self):
        """初始化NPC管理器"""
        self.npcs: Dict[str, NPC] = {}
        self.independent_manager = NPCIndependentManager()
        self.player_location: str = "新手村"
    
    def generate_npcs_for_location(self, location: str, count: int = None) -> List[NPC]:
        """
        为地点生成NPC
        
        Args:
            location: 地点名称
            count: 数量，默认使用配置
            
        Returns:
            NPC列表
        """
        if count is None:
            count = GAME_CONFIG["npc"]["npc_count_per_location"]
        
        npcs = []
        for _ in range(count):
            npc = NPC()
            npc.data.location = location
            self.npcs[npc.data.id] = npc
            # 同时添加到独立系统管理器
            self.independent_manager.add_npc(npc.independent, location)
            npcs.append(npc)
        
        return npcs
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """
        获取NPC
        
        Args:
            npc_id: NPC ID
            
        Returns:
            NPC对象
        """
        return self.npcs.get(npc_id)
    
    def get_npcs_in_location(self, location: str) -> List[NPC]:
        """
        获取地点的所有NPC
        
        Args:
            location: 地点名称
            
        Returns:
            NPC列表
        """
        return [npc for npc in self.npcs.values() if npc.data.location == location and npc.data.is_alive]
    
    def get_npc_by_name(self, name: str) -> Optional[NPC]:
        """
        根据名字获取NPC
        
        Args:
            name: NPC名字
            
        Returns:
            NPC对象
        """
        for npc in self.npcs.values():
            if npc.data.name == name or npc.data.dao_name == name:
                return npc
        return None
    
    def advance_time_for_all(self, days: int = 1):
        """
        为所有NPC推进时间
        
        Args:
            days: 天数
        """
        for npc in self.npcs.values():
            npc.advance_time(days)
    
    def update_all(self, current_time: float = None, player_location: str = None):
        """
        更新所有NPC（独立系统）
        
        Args:
            current_time: 当前时间戳
            player_location: 玩家当前位置
        """
        if current_time is None:
            current_time = time.time()
        if player_location:
            self.player_location = player_location
        
        # 使用独立系统管理器批量更新
        self.independent_manager.update_all(current_time, self.player_location)
        
        # 同时更新NPC的基础状态
        for npc in self.npcs.values():
            if npc.data.location == self.player_location:
                npc.update(current_time, player_nearby=True)
    
    def socialize_npcs(self, npc_id1: str, npc_id2: str):
        """
        两个NPC之间进行社交
        
        Args:
            npc_id1: 第一个NPC的ID
            npc_id2: 第二个NPC的ID
        """
        npc1 = self.npcs.get(npc_id1)
        npc2 = self.npcs.get(npc_id2)
        
        if npc1 and npc2:
            npc1.socialize_with(npc2)
            self.independent_manager.socialize_between(npc_id1, npc_id2)
    
    def get_independent_stats(self) -> Dict[str, Any]:
        """获取独立系统统计信息"""
        return self.independent_manager.get_stats()
    
    def pause_npc(self, npc_id: str):
        """暂停指定NPC的独立更新"""
        self.independent_manager.pause_npc(npc_id)
    
    def resume_npc(self, npc_id: str):
        """恢复指定NPC的独立更新"""
        self.independent_manager.resume_npc(npc_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            npc_id: npc.to_dict()
            for npc_id, npc in self.npcs.items()
        }
