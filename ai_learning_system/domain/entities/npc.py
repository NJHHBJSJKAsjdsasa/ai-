"""NPC实体"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from domain.value_objects.npc import (
    NPCMemory, Relationship, Dialogue, Personality, 
    CultivationInfo, NPCStats, ScheduleActivity, 
    EmotionType, MemoryCategory, RelationshipType
)


@dataclass
class NPC:
    """NPC实体"""
    id: str
    name: str
    dao_name: str
    age: int
    cultivation_info: CultivationInfo
    sect: str
    sect_type: str = ""
    sect_specialty: str = ""
    occupation: str = ""
    location: str = ""
    morality: int = 0  # 善恶值 (-100 to 100)
    is_alive: bool = True
    can_resurrect: bool = True
    death_info: Dict = field(default_factory=dict)
    
    # 内部状态
    _memories: List[NPCMemory] = field(default_factory=list)
    _relationships: Dict[str, Relationship] = field(default_factory=dict)
    _favor: Dict[str, int] = field(default_factory=dict)  # 对玩家的好感度
    _stats: NPCStats = field(default_factory=lambda: NPCStats(10, 5, 8, 0.03, 0.03))
    _personality: Optional[Personality] = None
    _schedule: Dict[int, ScheduleActivity] = field(default_factory=dict)
    _combat_record: List[Dict] = field(default_factory=list)
    _goals: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        # 验证善恶值范围
        if not -100 <= self.morality <= 100:
            raise ValueError("善恶值必须在-100到100之间")
    
    # ========== 基本属性方法 ==========
    def get_stats(self) -> NPCStats:
        """获取NPC属性"""
        return self._stats
    
    def update_stats(self, stats: NPCStats):
        """更新NPC属性"""
        self._stats = stats
    
    def get_personality(self) -> Optional[Personality]:
        """获取个性"""
        return self._personality
    
    def set_personality(self, personality: Personality):
        """设置个性"""
        self._personality = personality
    
    # ========== 记忆管理 ==========
    def add_memory(self, memory: NPCMemory):
        """添加记忆"""
        self._memories.append(memory)
        # 限制记忆数量，保留重要性高的记忆
        if len(self._memories) > 50:
            self._memories.sort(key=lambda m: m.importance, reverse=True)
            self._memories = self._memories[:50]
    
    def get_memories(self, category: Optional[MemoryCategory] = None) -> List[NPCMemory]:
        """获取记忆"""
        if category:
            return [m for m in self._memories if m.category == category]
        return self._memories
    
    def get_recent_memories(self, limit: int = 10) -> List[NPCMemory]:
        """获取最近的记忆"""
        return sorted(self._memories, key=lambda m: m.timestamp, reverse=True)[:limit]
    
    # ========== 关系管理 ==========
    def add_relationship(self, relationship: Relationship):
        """添加关系"""
        self._relationships[relationship.npc_id] = relationship
    
    def update_relationship(self, npc_id: str, **kwargs):
        """更新关系"""
        if npc_id in self._relationships:
            current_relationship = self._relationships[npc_id]
            new_relationship = current_relationship.with_updates(**kwargs)
            self._relationships[npc_id] = new_relationship
    
    def get_relationship(self, npc_id: str) -> Optional[Relationship]:
        """获取与特定NPC的关系"""
        return self._relationships.get(npc_id)
    
    def get_all_relationships(self) -> Dict[str, Relationship]:
        """获取所有关系"""
        return self._relationships
    
    def get_friends(self, min_affinity: int = 20) -> List[Relationship]:
        """获取朋友列表"""
        return [r for r in self._relationships.values() if r.affinity >= min_affinity]
    
    def get_enemies(self, min_hatred: int = 20) -> List[Relationship]:
        """获取敌人列表"""
        return [r for r in self._relationships.values() if r.hatred >= min_hatred]
    
    # ========== 玩家好感度管理 ==========
    def update_favor(self, player_name: str, delta: int):
        """更新对玩家的好感度"""
        current = self._favor.get(player_name, 0)
        new_favor = max(-100, min(100, current + delta))
        self._favor[player_name] = new_favor
    
    def get_favor(self, player_name: str) -> int:
        """获取对玩家的好感度"""
        return self._favor.get(player_name, 0)
    
    # ========== 日程管理 ==========
    def add_schedule_activity(self, activity: ScheduleActivity):
        """添加日程活动"""
        self._schedule[activity.start_time] = activity
    
    def get_schedule(self) -> Dict[int, ScheduleActivity]:
        """获取日程"""
        return self._schedule
    
    def get_current_activity(self, hour: int) -> Optional[ScheduleActivity]:
        """获取当前活动"""
        return self._schedule.get(hour)
    
    # ========== 战斗记录管理 ==========
    def add_combat_record(self, record: Dict):
        """添加战斗记录"""
        self._combat_record.append(record)
        # 限制记录数量
        if len(self._combat_record) > 20:
            self._combat_record = self._combat_record[-20:]
    
    def get_combat_record(self) -> List[Dict]:
        """获取战斗记录"""
        return self._combat_record
    
    # ========== 目标管理 ==========
    def add_goal(self, goal: Dict):
        """添加目标"""
        self._goals.append(goal)
    
    def update_goal_progress(self, goal_index: int, progress: float):
        """更新目标进度"""
        if 0 <= goal_index < len(self._goals):
            self._goals[goal_index]['current_value'] = min(progress, self._goals[goal_index]['target_value'])
    
    def get_goals(self) -> List[Dict]:
        """获取目标列表"""
        return self._goals
    
    # ========== 状态管理 ==========
    def advance_age(self, days: int = 1):
        """增加年龄"""
        self.age += days // 365
        # 检查寿元
        if self.age >= self.cultivation_info.lifespan:
            self.is_alive = False
    
    def mark_as_dead(self, killer_name: str, reason: str, location: str, timestamp: int):
        """标记死亡"""
        self.is_alive = False
        self.location = location
        self.death_info = {
            "killer_name": killer_name,
            "reason": reason,
            "location": location,
            "timestamp": timestamp,
            "realm_at_death": self.cultivation_info.realm_name,
            "age_at_death": self.age
        }
    
    def resurrect(self) -> bool:
        """复活"""
        if not self.can_resurrect or self.is_alive:
            return False
        
        self.is_alive = True
        self.death_info = {}
        return True
    
    # ========== 善恶值相关 ==========
    def get_morality_description(self) -> str:
        """获取善恶值描述"""
        if self.morality < -50:
            return "极恶"
        elif self.morality < -20:
            return "邪恶"
        elif self.morality < 0:
            return "偏恶"
        elif self.morality == 0:
            return "中立"
        elif self.morality <= 20:
            return "偏善"
        elif self.morality <= 50:
            return "善良"
        else:
            return "大善"
    
    def is_evil(self) -> bool:
        """是否邪恶"""
        return self.morality < 0
    
    def is_good(self) -> bool:
        """是否善良"""
        return self.morality > 0
    
    # ========== 战斗力计算 ==========
    def get_combat_power(self) -> int:
        """计算战斗力"""
        # 基础战斗力 = 攻击 + 防御 * 2 + 速度
        base_power = self._stats.attack + self._stats.defense * 2 + self._stats.speed
        
        # 境界加成
        realm_multiplier = 1 + self.cultivation_info.realm_level * 0.2
        
        # 暴击和闪避加成
        crit_bonus = self._stats.crit_rate * 100
        dodge_bonus = self._stats.dodge_rate * 100
        
        # 计算总战斗力
        combat_power = int((base_power + crit_bonus + dodge_bonus) * realm_multiplier)
        
        return combat_power
    
    # ========== 序列化方法 ==========
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "dao_name": self.dao_name,
            "age": self.age,
            "cultivation_info": {
                "realm_level": self.cultivation_info.realm_level,
                "realm_name": self.cultivation_info.realm_name,
                "lifespan": self.cultivation_info.lifespan,
                "cultivation_speed": self.cultivation_info.cultivation_speed
            },
            "sect": self.sect,
            "sect_type": self.sect_type,
            "sect_specialty": self.sect_specialty,
            "occupation": self.occupation,
            "location": self.location,
            "morality": self.morality,
            "is_alive": self.is_alive,
            "can_resurrect": self.can_resurrect,
            "death_info": self.death_info,
            "stats": {
                "attack": self._stats.attack,
                "defense": self._stats.defense,
                "speed": self._stats.speed,
                "crit_rate": self._stats.crit_rate,
                "dodge_rate": self._stats.dodge_rate
            },
            "favor": self._favor,
            "combat_record": self._combat_record,
            "goals": self._goals
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """从字典创建NPC"""
        cultivation_info = CultivationInfo(
            realm_level=data['cultivation_info']['realm_level'],
            realm_name=data['cultivation_info']['realm_name'],
            lifespan=data['cultivation_info']['lifespan'],
            cultivation_speed=data['cultivation_info'].get('cultivation_speed', 1.0)
        )
        
        stats = NPCStats(
            attack=data['stats']['attack'],
            defense=data['stats']['defense'],
            speed=data['stats']['speed'],
            crit_rate=data['stats']['crit_rate'],
            dodge_rate=data['stats']['dodge_rate']
        )
        
        npc = cls(
            id=data['id'],
            name=data['name'],
            dao_name=data['dao_name'],
            age=data['age'],
            cultivation_info=cultivation_info,
            sect=data['sect'],
            sect_type=data.get('sect_type', ''),
            sect_specialty=data.get('sect_specialty', ''),
            occupation=data.get('occupation', ''),
            location=data.get('location', ''),
            morality=data.get('morality', 0),
            is_alive=data.get('is_alive', True),
            can_resurrect=data.get('can_resurrect', True),
            death_info=data.get('death_info', {})
        )
        
        npc._stats = stats
        npc._favor = data.get('favor', {})
        npc._combat_record = data.get('combat_record', [])
        npc._goals = data.get('goals', [])
        
        return npc
