"""
NPC关系网络系统模块
管理NPC之间的复杂关系网络，包括友谊、敌对、师徒、家族、势力等关系
支持记忆传播和社交圈分析
"""

import random
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RelationType(Enum):
    """关系类型枚举"""
    FRIENDSHIP = "friendship"       # 友谊关系
    HOSTILITY = "hostility"         # 敌对关系
    MASTER_APPRENTICE = "master_apprentice"  # 师徒关系
    FAMILY = "family"               # 家族关系
    FACTION = "faction"             # 势力关系
    ACQUAINTANCE = "acquaintance"   # 熟人关系
    UNFRIENDLY = "unfriendly"       # 不友好关系
    DAO_LV = "dao_lv"               # 道侣关系


@dataclass
class RelationHistoryEntry:
    """关系历史记录条目"""
    timestamp: float                # 时间戳
    event: str                      # 事件描述
    delta_affinity: int = 0         # 好感度变化
    delta_intimacy: int = 0         # 亲密度变化
    delta_hatred: int = 0           # 仇恨度变化


@dataclass
class Relationship:
    """
    NPC关系数据类

    表示两个NPC之间的关系状态，包含好感度、亲密度、仇恨度等多维度指标
    """
    npc_id: str                     # 对方NPC的ID
    relation_type: RelationType     # 关系类型
    affinity: int = 0               # 好感度 (-100 to 100)
    intimacy: int = 0               # 亲密度 (0-100)
    hatred: int = 0                 # 仇恨度 (0-100)
    history: List[RelationHistoryEntry] = field(default_factory=list)  # 关系历史记录
    last_interaction: float = 0     # 上次互动时间戳

    def __post_init__(self):
        """初始化后处理"""
        if not self.history:
            self.history = []
        # 确保数值在有效范围内
        self.affinity = max(-100, min(100, self.affinity))
        self.intimacy = max(0, min(100, self.intimacy))
        self.hatred = max(0, min(100, self.hatred))

    def add_history_entry(
        self,
        event: str,
        delta_affinity: int = 0,
        delta_intimacy: int = 0,
        delta_hatred: int = 0
    ) -> None:
        """
        添加关系历史记录

        Args:
            event: 事件描述
            delta_affinity: 好感度变化
            delta_intimacy: 亲密度变化
            delta_hatred: 仇恨度变化
        """
        entry = RelationHistoryEntry(
            timestamp=time.time(),
            event=event,
            delta_affinity=delta_affinity,
            delta_intimacy=delta_intimacy,
            delta_hatred=delta_hatred
        )
        self.history.append(entry)

        # 限制历史记录数量
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def update_last_interaction(self) -> None:
        """更新上次互动时间"""
        self.last_interaction = time.time()

    def get_relation_strength(self) -> int:
        """
        获取关系强度

        Returns:
            关系强度值 (0-100)，综合考虑好感度、亲密度和仇恨度
        """
        if self.hatred > 50:
            # 高仇恨度时，关系强度主要由仇恨度决定
            return self.hatred
        elif self.affinity > 0:
            # 好感度为正时，综合考虑好感和亲密
            return min(100, (self.affinity + self.intimacy) // 2)
        else:
            # 冷淡关系
            return max(0, self.intimacy // 2)

    def get_relation_description(self) -> str:
        """
        获取关系描述

        Returns:
            关系描述字符串
        """
        if self.relation_type == RelationType.MASTER_APPRENTICE:
            return "师徒"
        elif self.relation_type == RelationType.FAMILY:
            return "家族"
        elif self.relation_type == RelationType.FACTION:
            return "同门"
        elif self.hatred >= 80:
            return "死敌"
        elif self.hatred >= 50:
            return "仇敌"
        elif self.hatred >= 20:
            return "厌恶"
        elif self.affinity >= 80:
            return "至交"
        elif self.affinity >= 50:
            return "好友"
        elif self.affinity >= 20:
            return "友善"
        elif self.affinity >= -20:
            return "普通"
        else:
            return "冷淡"

    def is_friend(self) -> bool:
        """
        是否为朋友关系

        Returns:
            好感度 > 0 且仇恨度较低
        """
        return self.affinity > 0 and self.hatred < 30

    def is_enemy(self) -> bool:
        """
        是否为敌人关系

        Returns:
            仇恨度 > 0
        """
        return self.hatred > 0

    def can_share_memory(self) -> bool:
        """
        是否可以分享记忆

        Returns:
            友谊关系且好感度 > 20
        """
        return (
            self.relation_type == RelationType.FRIENDSHIP
            and self.affinity > 20
            and self.hatred < 20
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            包含关系数据的字典
        """
        return {
            "npc_id": self.npc_id,
            "relation_type": self.relation_type.value,
            "affinity": self.affinity,
            "intimacy": self.intimacy,
            "hatred": self.hatred,
            "history": [
                {
                    "timestamp": entry.timestamp,
                    "event": entry.event,
                    "delta_affinity": entry.delta_affinity,
                    "delta_intimacy": entry.delta_intimacy,
                    "delta_hatred": entry.delta_hatred,
                }
                for entry in self.history
            ],
            "last_interaction": self.last_interaction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """
        从字典创建关系对象

        Args:
            data: 包含关系数据的字典

        Returns:
            Relationship对象
        """
        relation = cls(
            npc_id=data.get("npc_id", ""),
            relation_type=RelationType(data.get("relation_type", "acquaintance")),
            affinity=data.get("affinity", 0),
            intimacy=data.get("intimacy", 0),
            hatred=data.get("hatred", 0),
            last_interaction=data.get("last_interaction", 0),
        )

        # 恢复历史记录
        history_data = data.get("history", [])
        for entry_data in history_data:
            entry = RelationHistoryEntry(
                timestamp=entry_data.get("timestamp", time.time()),
                event=entry_data.get("event", ""),
                delta_affinity=entry_data.get("delta_affinity", 0),
                delta_intimacy=entry_data.get("delta_intimacy", 0),
                delta_hatred=entry_data.get("delta_hatred", 0),
            )
            relation.history.append(entry)

        return relation


@dataclass
class MemoryPropagationResult:
    """记忆传播结果"""
    target_id: str                  # 目标NPC ID
    success: bool                   # 是否成功传播
    credibility: float              # 传播后的可信度 (0-1)
    relationship_effect: int        # 对关系的影响


class NPCRelationshipNetwork:
    """
    NPC关系网络类

    管理所有NPC之间的关系网络，提供关系查询、更新、记忆传播等功能
    集成数据库持久化
    """

    def __init__(self, db=None):
        """初始化关系网络

        Args:
            db: 数据库实例，如果为None则延迟加载
        """
        # 关系网络: {npc_id: {other_npc_id: Relationship}}
        self._relationships: Dict[str, Dict[str, Relationship]] = {}

        # 数据库实例
        self._db = db

        # 记忆传播配置
        self._propagation_config = {
            "base_decay": 0.2,          # 基础可信度衰减
            "max_propagation_depth": 3,  # 最大传播深度
            "friend_bonus": 0.1,        # 朋友关系传播加成
            "enemy_penalty": 0.3,       # 敌人关系传播惩罚
        }

    def _get_db(self):
        """获取数据库实例（延迟加载）"""
        if self._db is None:
            from storage.database import Database
            self._db = Database()
            # 确保社交表已初始化
            self._db.init_social_tables()
        return self._db

    def _ensure_npc_exists(self, npc_id: str) -> None:
        """
        确保NPC在关系网络中存在

        Args:
            npc_id: NPC ID
        """
        if npc_id not in self._relationships:
            self._relationships[npc_id] = {}

    def _get_ordered_pair(self, npc1_id: str, npc2_id: str) -> Tuple[str, str]:
        """
        获取排序后的NPC对（用于统一存储）

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            排序后的NPC ID元组
        """
        return (npc1_id, npc2_id) if npc1_id < npc2_id else (npc2_id, npc1_id)

    def load_from_database(self) -> bool:
        """
        从数据库加载所有NPC关系

        Returns:
            是否成功加载
        """
        try:
            db = self._get_db()
            all_relations = db.get_all_npc_relations()

            self._relationships = {}
            for npc_id, relations in all_relations.items():
                self._relationships[npc_id] = {}
                for rel_data in relations:
                    # 确定关系类型
                    try:
                        rel_type = RelationType(rel_data.get('relation_type', 'acquaintance'))
                    except ValueError:
                        rel_type = RelationType.ACQUAINTANCE

                    relationship = Relationship(
                        npc_id=rel_data.get('npc_id', ''),
                        relation_type=rel_type,
                        affinity=rel_data.get('affinity', 0),
                        intimacy=rel_data.get('intimacy', 0),
                        hatred=rel_data.get('hatred', 0),
                        last_interaction=rel_data.get('last_interaction', 0) or time.time()
                    )
                    self._relationships[npc_id][rel_data.get('npc_id', '')] = relationship

            return True
        except Exception as e:
            print(f"从数据库加载NPC关系失败: {e}")
            return False

    def save_to_database(self) -> bool:
        """
        保存所有NPC关系到数据库

        Returns:
            是否成功保存
        """
        try:
            db = self.get_db()
            for npc_id, relations in self._relationships.items():
                for other_id, relationship in relations.items():
                    # 避免重复保存（只保存一次双向关系）
                    if npc_id < other_id:
                        db.add_npc_relation(
                            npc1_id=npc_id,
                            npc2_id=other_id,
                            relation_type=relationship.relation_type.value,
                            affinity=relationship.affinity,
                            intimacy=relationship.intimacy,
                            hatred=relationship.hatred
                        )
            return True
        except Exception as e:
            print(f"保存NPC关系到数据库失败: {e}")
            return False

    def sync_to_database(self, npc1_id: str, npc2_id: str) -> bool:
        """
        同步特定关系到数据库

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            是否成功同步
        """
        try:
            relationship = self.get_relationship(npc1_id, npc2_id)
            if relationship:
                db = self._get_db()
                return db.add_npc_relation(
                    npc1_id=npc1_id,
                    npc2_id=npc2_id,
                    relation_type=relationship.relation_type.value,
                    affinity=relationship.affinity,
                    intimacy=relationship.intimacy,
                    hatred=relationship.hatred
                )
            return False
        except Exception as e:
            print(f"同步NPC关系到数据库失败: {e}")
            return False

    def add_relationship(
        self,
        npc1_id: str,
        npc2_id: str,
        relation_type: RelationType,
        initial_affinity: int = 0,
        initial_intimacy: int = 0,
        initial_hatred: int = 0
    ) -> bool:
        """
        添加两个NPC之间的关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            relation_type: 关系类型
            initial_affinity: 初始好感度
            initial_intimacy: 初始亲密度
            initial_hatred: 初始仇恨度

        Returns:
            是否成功添加
        """
        if npc1_id == npc2_id:
            return False

        self._ensure_npc_exists(npc1_id)
        self._ensure_npc_exists(npc2_id)

        # 创建双向关系
        relationship1 = Relationship(
            npc_id=npc2_id,
            relation_type=relation_type,
            affinity=initial_affinity,
            intimacy=initial_intimacy,
            hatred=initial_hatred,
        )
        relationship1.add_history_entry(f"与{npc2_id}建立{relation_type.value}关系")

        relationship2 = Relationship(
            npc_id=npc1_id,
            relation_type=relation_type,
            affinity=initial_affinity,
            intimacy=initial_intimacy,
            hatred=initial_hatred,
        )
        relationship2.add_history_entry(f"与{npc1_id}建立{relation_type.value}关系")

        self._relationships[npc1_id][npc2_id] = relationship1
        self._relationships[npc2_id][npc1_id] = relationship2

        # 同步到数据库
        self.sync_to_database(npc1_id, npc2_id)

        return True

    def remove_relationship(self, npc1_id: str, npc2_id: str) -> bool:
        """
        移除两个NPC之间的关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            是否成功移除
        """
        removed = False

        if npc1_id in self._relationships and npc2_id in self._relationships[npc1_id]:
            del self._relationships[npc1_id][npc2_id]
            removed = True

        if npc2_id in self._relationships and npc1_id in self._relationships[npc2_id]:
            del self._relationships[npc2_id][npc1_id]
            removed = True

        # 从数据库中移除
        if removed:
            try:
                db = self._get_db()
                db.remove_npc_relation(npc1_id, npc2_id)
            except Exception as e:
                print(f"从数据库移除NPC关系失败: {e}")

        return removed

    def update_relationship(
        self,
        npc1_id: str,
        npc2_id: str,
        delta: Dict[str, int],
        reason: str = ""
    ) -> bool:
        """
        更新两个NPC之间的关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            delta: 变化值字典，可包含 affinity, intimacy, hatred
            reason: 更新原因

        Returns:
            是否成功更新
        """
        if npc1_id not in self._relationships or npc2_id not in self._relationships[npc1_id]:
            # 如果没有现有关系，创建新关系
            relation_type = RelationType.ACQUAINTANCE
            if delta.get("hatred", 0) > 0:
                relation_type = RelationType.HOSTILITY
            elif delta.get("affinity", 0) > 0:
                relation_type = RelationType.FRIENDSHIP

            return self.add_relationship(
                npc1_id, npc2_id, relation_type,
                delta.get("affinity", 0),
                delta.get("intimacy", 0),
                delta.get("hatred", 0)
            )

        # 获取双向关系
        rel1 = self._relationships[npc1_id][npc2_id]
        rel2 = self._relationships[npc2_id][npc1_id]

        # 应用变化
        delta_affinity = delta.get("affinity", 0)
        delta_intimacy = delta.get("intimacy", 0)
        delta_hatred = delta.get("hatred", 0)

        rel1.affinity = max(-100, min(100, rel1.affinity + delta_affinity))
        rel1.intimacy = max(0, min(100, rel1.intimacy + delta_intimacy))
        rel1.hatred = max(0, min(100, rel1.hatred + delta_hatred))
        rel1.update_last_interaction()

        rel2.affinity = max(-100, min(100, rel2.affinity + delta_affinity))
        rel2.intimacy = max(0, min(100, rel2.intimacy + delta_intimacy))
        rel2.hatred = max(0, min(100, rel2.hatred + delta_hatred))
        rel2.update_last_interaction()

        # 添加历史记录
        event_desc = reason if reason else "关系发生变化"
        rel1.add_history_entry(event_desc, delta_affinity, delta_intimacy, delta_hatred)
        rel2.add_history_entry(event_desc, delta_affinity, delta_intimacy, delta_hatred)

        # 记录关系数值变化到数据库
        try:
            db = self._get_db()
            if delta_affinity != 0:
                db.record_relationship_change(
                    npc1_id, npc2_id, 'affinity',
                    rel1.affinity - delta_affinity, rel1.affinity,
                    reason, 'interaction'
                )
            if delta_intimacy != 0:
                db.record_relationship_change(
                    npc1_id, npc2_id, 'intimacy',
                    rel1.intimacy - delta_intimacy, rel1.intimacy,
                    reason, 'interaction'
                )
            if delta_hatred != 0:
                db.record_relationship_change(
                    npc1_id, npc2_id, 'hatred',
                    rel1.hatred - delta_hatred, rel1.hatred,
                    reason, 'interaction'
                )
        except Exception as e:
            print(f"记录关系变化失败: {e}")

        # 自动更新关系类型
        self._auto_update_relation_type(npc1_id, npc2_id)

        # 同步到数据库
        self.sync_to_database(npc1_id, npc2_id)

        return True

    def _auto_update_relation_type(self, npc1_id: str, npc2_id: str) -> None:
        """
        根据关系数值自动更新关系类型

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
        """
        if npc1_id not in self._relationships or npc2_id not in self._relationships[npc1_id]:
            return

        rel = self._relationships[npc1_id][npc2_id]

        # 如果当前是特殊关系类型，保持不变
        if rel.relation_type in [RelationType.MASTER_APPRENTICE, RelationType.FAMILY]:
            return

        # 根据数值自动判断关系类型
        if rel.hatred >= 30:
            new_type = RelationType.HOSTILITY
        elif rel.affinity >= 20 and rel.intimacy >= 20:
            new_type = RelationType.FRIENDSHIP
        elif rel.affinity < -20:
            new_type = RelationType.UNFRIENDLY
        else:
            new_type = RelationType.ACQUAINTANCE

        # 更新关系类型
        if new_type != rel.relation_type:
            rel.relation_type = new_type
            self._relationships[npc2_id][npc1_id].relation_type = new_type

    def get_relationship(self, npc1_id: str, npc2_id: str) -> Optional[Relationship]:
        """
        获取两个NPC之间的关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            Relationship对象，如果不存在则返回None
        """
        if npc1_id in self._relationships:
            return self._relationships[npc1_id].get(npc2_id)
        return None

    def get_relationships(self, npc_id: str) -> Dict[str, Relationship]:
        """
        获取NPC的所有关系

        Args:
            npc_id: NPC ID

        Returns:
            关系字典 {other_npc_id: Relationship}
        """
        return self._relationships.get(npc_id, {}).copy()

    def get_friends(self, npc_id: str, min_affinity: int = 20) -> List[Tuple[str, Relationship]]:
        """
        获取NPC的朋友列表

        Args:
            npc_id: NPC ID
            min_affinity: 最小好感度阈值

        Returns:
            [(friend_id, relationship), ...]
        """
        friends = []
        relationships = self.get_relationships(npc_id)

        for other_id, rel in relationships.items():
            if rel.is_friend() and rel.affinity >= min_affinity:
                friends.append((other_id, rel))

        # 按好感度排序
        friends.sort(key=lambda x: x[1].affinity, reverse=True)
        return friends

    def get_enemies(self, npc_id: str, min_hatred: int = 20) -> List[Tuple[str, Relationship]]:
        """
        获取NPC的敌人列表

        Args:
            npc_id: NPC ID
            min_hatred: 最小仇恨度阈值

        Returns:
            [(enemy_id, relationship), ...]
        """
        enemies = []
        relationships = self.get_relationships(npc_id)

        for other_id, rel in relationships.items():
            if rel.is_enemy() and rel.hatred >= min_hatred:
                enemies.append((other_id, rel))

        # 按仇恨度排序
        enemies.sort(key=lambda x: x[1].hatred, reverse=True)
        return enemies

    def get_relations_by_type(
        self,
        npc_id: str,
        relation_type: RelationType
    ) -> List[Tuple[str, Relationship]]:
        """
        获取指定类型的关系

        Args:
            npc_id: NPC ID
            relation_type: 关系类型

        Returns:
            [(other_id, relationship), ...]
        """
        relations = []
        relationships = self.get_relationships(npc_id)

        for other_id, rel in relationships.items():
            if rel.relation_type == relation_type:
                relations.append((other_id, rel))

        return relations

    def propagate_memory(
        self,
        memory: Dict[str, Any],
        source_id: str,
        initial_credibility: float = 1.0,
        max_depth: int = None
    ) -> List[MemoryPropagationResult]:
        """
        将记忆传播给关系网中的其他NPC

        Args:
            memory: 记忆内容字典，需包含 content, importance 等字段
            source_id: 记忆来源NPC的ID
            initial_credibility: 初始可信度 (0-1)
            max_depth: 最大传播深度

        Returns:
            传播结果列表
        """
        if max_depth is None:
            max_depth = self._propagation_config["max_propagation_depth"]

        results = []
        visited = {source_id}
        current_layer = [(source_id, initial_credibility)]
        current_depth = 0

        while current_layer and current_depth < max_depth:
            next_layer = []

            for current_id, current_credibility in current_layer:
                # 获取当前NPC的朋友
                friends = self.get_friends(current_id, min_affinity=0)

                for friend_id, relationship in friends:
                    if friend_id in visited:
                        continue

                    visited.add(friend_id)

                    # 计算传播后的可信度
                    decay = self._propagation_config["base_decay"]

                    # 朋友关系加成
                    if relationship.relation_type == RelationType.FRIENDSHIP:
                        decay -= self._propagation_config["friend_bonus"]

                    # 亲密度影响
                    intimacy_factor = relationship.intimacy / 200  # 0-0.5
                    decay -= intimacy_factor

                    new_credibility = max(0.0, current_credibility - decay)

                    # 关系影响
                    rel_effect = 0
                    if new_credibility > 0.5:
                        # 高可信度传播可能增进友谊
                        rel_effect = random.randint(1, 3)
                        self.update_relationship(
                            current_id,
                            friend_id,
                            {"affinity": rel_effect, "intimacy": 1},
                            f"分享了关于{memory.get('content', '某事')}的信息"
                        )

                    result = MemoryPropagationResult(
                        target_id=friend_id,
                        success=new_credibility > 0.3,
                        credibility=new_credibility,
                        relationship_effect=rel_effect
                    )
                    results.append(result)

                    # 如果可信度足够高，继续传播
                    if new_credibility > 0.3:
                        next_layer.append((friend_id, new_credibility))

            current_layer = next_layer
            current_depth += 1

        return results

    def get_social_circle(
        self,
        npc_id: str,
        depth: int = 2,
        min_relation_strength: int = 20
    ) -> Dict[str, Any]:
        """
        获取NPC的社交圈子

        Args:
            npc_id: NPC ID
            depth: 搜索深度
            min_relation_strength: 最小关系强度

        Returns:
            社交圈信息字典
        """
        if npc_id not in self._relationships:
            return {"center": npc_id, "members": [], "connections": []}

        visited = {npc_id}
        current_layer = {npc_id}
        all_members = set()
        connections = []

        for _ in range(depth):
            next_layer = set()

            for current_id in current_layer:
                relationships = self.get_relationships(current_id)

                for other_id, rel in relationships.items():
                    if rel.get_relation_strength() >= min_relation_strength:
                        if other_id not in visited:
                            visited.add(other_id)
                            next_layer.add(other_id)
                            all_members.add(other_id)

                        # 记录连接
                        connection = {
                            "from": current_id,
                            "to": other_id,
                            "strength": rel.get_relation_strength(),
                            "type": rel.relation_type.value,
                        }
                        if connection not in connections:
                            connections.append(connection)

            current_layer = next_layer

        return {
            "center": npc_id,
            "members": list(all_members),
            "connections": connections,
            "total_members": len(all_members),
        }

    def get_network_stats(self, npc_id: str) -> Dict[str, Any]:
        """
        获取NPC的关系网络统计信息

        Args:
            npc_id: NPC ID

        Returns:
            统计信息字典
        """
        relationships = self.get_relationships(npc_id)

        if not relationships:
            return {
                "total_relations": 0,
                "friends_count": 0,
                "enemies_count": 0,
                "avg_affinity": 0,
                "avg_intimacy": 0,
                "avg_hatred": 0,
            }

        friends = [r for r in relationships.values() if r.is_friend()]
        enemies = [r for r in relationships.values() if r.is_enemy()]

        avg_affinity = sum(r.affinity for r in relationships.values()) / len(relationships)
        avg_intimacy = sum(r.intimacy for r in relationships.values()) / len(relationships)
        avg_hatred = sum(r.hatred for r in relationships.values()) / len(relationships)

        # 按类型统计
        type_counts = {}
        for rel in relationships.values():
            type_name = rel.relation_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_relations": len(relationships),
            "friends_count": len(friends),
            "enemies_count": len(enemies),
            "avg_affinity": round(avg_affinity, 2),
            "avg_intimacy": round(avg_intimacy, 2),
            "avg_hatred": round(avg_hatred, 2),
            "type_distribution": type_counts,
        }

    def find_path(
        self,
        npc1_id: str,
        npc2_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        查找两个NPC之间的关系路径

        Args:
            npc1_id: 起始NPC ID
            npc2_id: 目标NPC ID
            max_depth: 最大搜索深度

        Returns:
            NPC ID路径列表，如果没有路径则返回None
        """
        if npc1_id not in self._relationships or npc2_id not in self._relationships:
            return None

        # BFS搜索
        from collections import deque

        queue = deque([(npc1_id, [npc1_id])])
        visited = {npc1_id}

        while queue:
            current_id, path = queue.popleft()

            if len(path) > max_depth:
                continue

            if current_id == npc2_id:
                return path

            relationships = self.get_relationships(current_id)
            for next_id in relationships.keys():
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))

        return None

    def get_mutual_friends(self, npc1_id: str, npc2_id: str) -> List[str]:
        """
        获取两个NPC的共同朋友

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            共同朋友ID列表
        """
        friends1 = set(id for id, rel in self.get_friends(npc1_id))
        friends2 = set(id for id, rel in self.get_friends(npc2_id))
        return list(friends1 & friends2)

    def get_recommended_friends(self, npc_id: str, limit: int = 5) -> List[Tuple[str, int]]:
        """
        获取推荐给NPC的潜在朋友（朋友的朋友）

        Args:
            npc_id: NPC ID
            limit: 返回数量限制

        Returns:
            [(potential_friend_id, mutual_count), ...]
        """
        # 获取当前朋友
        current_friends = set(id for id, _ in self.get_friends(npc_id))
        current_friends.add(npc_id)

        # 统计朋友的朋友
        potential_friends: Dict[str, int] = {}

        for friend_id in current_friends:
            if friend_id == npc_id:
                continue

            friend_friends = self.get_friends(friend_id)
            for potential_id, _ in friend_friends:
                if potential_id not in current_friends:
                    potential_friends[potential_id] = potential_friends.get(potential_id, 0) + 1

        # 按共同朋友数量排序
        sorted_potentials = sorted(
            potential_friends.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_potentials[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            包含所有关系数据的字典
        """
        return {
            npc_id: {
                other_id: rel.to_dict()
                for other_id, rel in relations.items()
            }
            for npc_id, relations in self._relationships.items()
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典加载关系数据

        Args:
            data: 包含关系数据的字典
        """
        self._relationships = {}

        for npc_id, relations_data in data.items():
            self._relationships[npc_id] = {}
            for other_id, rel_data in relations_data.items():
                self._relationships[npc_id][other_id] = Relationship.from_dict(rel_data)

    def clear(self) -> None:
        """清空所有关系数据"""
        self._relationships = {}

    def get_all_npc_ids(self) -> Set[str]:
        """
        获取所有有关系的NPC ID

        Returns:
            NPC ID集合
        """
        return set(self._relationships.keys())

    def propose_dao_lv_between_npcs(self, npc1_id: str, npc2_id: str,
                                    npc1_data: Dict = None, npc2_data: Dict = None) -> Tuple[bool, str]:
        """
        提议两个NPC结为道侣

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            npc1_data: 第一个NPC的数据（包含realm_level等）
            npc2_data: 第二个NPC的数据（包含realm_level等）

        Returns:
            (是否成功, 消息)
        """
        if npc1_id == npc2_id:
            return False, "NPC不能与自己结为道侣"

        # 检查是否已有道侣
        existing1 = self.get_npc_dao_lv(npc1_id)
        if existing1:
            return False, f"NPC {npc1_id} 已有道侣"

        existing2 = self.get_npc_dao_lv(npc2_id)
        if existing2:
            return False, f"NPC {npc2_id} 已有道侣"

        # 获取当前关系
        relation = self.get_relationship(npc1_id, npc2_id)

        # 检查条件
        if not relation:
            return False, "两个NPC还不够熟悉，无法结为道侣"

        # 检查亲密度和信任度条件
        if relation.intimacy < 80:
            return False, f"亲密度不足（需要≥80，当前{relation.intimacy}）"

        if relation.affinity < 70:
            return False, f"好感度不足（需要≥70，当前{relation.affinity}）"

        if relation.hatred > 0:
            return False, "双方存在仇恨，无法结为道侣"

        # 建立道侣关系
        success = self._establish_dao_lv(npc1_id, npc2_id, relation)

        if success:
            # 记录社交事件
            db = self._get_db()
            db.record_npc_social_event(
                event_type='dao_lv_established',
                npc1_id=npc1_id,
                npc2_id=npc2_id,
                description=f"{npc1_id} 与 {npc2_id} 结为道侣",
                is_public=True
            )
            return True, "道侣关系建立成功"

        return False, "建立道侣关系失败"

    def _establish_dao_lv(self, npc1_id: str, npc2_id: str, base_relation: Relationship) -> bool:
        """
        建立道侣关系的核心逻辑

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            base_relation: 基础关系对象

        Returns:
            是否成功
        """
        try:
            # 更新关系类型为道侣
            base_relation.relation_type = RelationType.DAO_LV
            base_relation.intimacy = 100
            base_relation.affinity = min(100, base_relation.affinity + 20)
            base_relation.add_history_entry("结为道侣", 20, 20, 0)

            # 确保双向关系都存在
            self._ensure_npc_exists(npc1_id)
            self._ensure_npc_exists(npc2_id)

            # 更新双向关系
            self._relationships[npc1_id][npc2_id] = base_relation

            # 创建反向关系
            reverse_relation = Relationship(
                npc_id=npc1_id,
                relation_type=RelationType.DAO_LV,
                affinity=base_relation.affinity,
                intimacy=base_relation.intimacy,
                hatred=0
            )
            reverse_relation.add_history_entry("结为道侣", 20, 20, 0)
            self._relationships[npc2_id][npc1_id] = reverse_relation

            # 同步到数据库
            self.sync_to_database(npc1_id, npc2_id)

            return True
        except Exception as e:
            print(f"建立道侣关系失败: {e}")
            return False

    def break_dao_lv(self, npc1_id: str, npc2_id: str, reason: str = "") -> Tuple[bool, str]:
        """
        解除道侣关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            reason: 解除原因

        Returns:
            (是否成功, 消息)
        """
        relation = self.get_relationship(npc1_id, npc2_id)

        if not relation or relation.relation_type != RelationType.DAO_LV:
            return False, "双方没有道侣关系"

        # 更新关系类型为旧识
        relation.relation_type = RelationType.ACQUAINTANCE
        relation.intimacy = max(20, relation.intimacy - 50)
        relation.affinity = max(0, relation.affinity - 30)
        relation.add_history_entry(f"解除道侣关系: {reason}", -30, -50, 0)

        # 更新双向关系
        self._relationships[npc2_id][npc1_id].relation_type = RelationType.ACQUAINTANCE
        self._relationships[npc2_id][npc1_id].intimacy = relation.intimacy
        self._relationships[npc2_id][npc1_id].affinity = relation.affinity

        # 同步到数据库
        self.sync_to_database(npc1_id, npc2_id)

        # 记录社交事件
        db = self._get_db()
        db.record_npc_social_event(
            event_type='dao_lv_broken',
            npc1_id=npc1_id,
            npc2_id=npc2_id,
            description=f"{npc1_id} 与 {npc2_id} 解除道侣关系: {reason}",
            result="关系解除",
            is_public=True
        )

        return True, "道侣关系已解除"

    def get_npc_dao_lv(self, npc_id: str) -> Optional[Tuple[str, Relationship]]:
        """
        获取NPC的道侣

        Args:
            npc_id: NPC ID

        Returns:
            (道侣ID, 关系对象)，如果没有则返回None
        """
        relationships = self.get_relationships(npc_id)

        for other_id, rel in relationships.items():
            if rel.relation_type == RelationType.DAO_LV:
                return (other_id, rel)

        return None

    def establish_master_apprentice_between_npcs(self, master_id: str, apprentice_id: str,
                                                 master_data: Dict = None, apprentice_data: Dict = None) -> Tuple[bool, str]:
        """
        建立NPC之间的师徒关系

        Args:
            master_id: 师父NPC的ID
            apprentice_id: 徒弟NPC的ID
            master_data: 师父的数据（包含realm_level等）
            apprentice_data: 徒弟的数据（包含realm_level等）

        Returns:
            (是否成功, 消息)
        """
        if master_id == apprentice_id:
            return False, "NPC不能收自己为徒"

        # 检查师父境界（筑基期=2）
        if master_data and master_data.get('realm_level', 0) < 2:
            return False, "师父境界不足，需要达到筑基期"

        # 检查徒弟是否已有师父
        existing_master = self.get_npc_master(apprentice_id)
        if existing_master:
            return False, f"该NPC已有师父"

        # 检查境界差距
        if master_data and apprentice_data:
            if master_data.get('realm_level', 0) <= apprentice_data.get('realm_level', 0):
                return False, "师父境界必须高于徒弟"

        # 获取当前关系
        relation = self.get_relationship(master_id, apprentice_id)

        if not relation:
            return False, "双方还不够熟悉，无法建立师徒关系"

        # 检查亲密度和信任度条件
        if relation.intimacy < 30:
            return False, f"亲密度不足（需要≥30，当前{relation.intimacy}）"

        if relation.affinity < 40:
            return False, f"好感度不足（需要≥40，当前{relation.affinity}）"

        # 建立师徒关系
        success = self._establish_master_apprentice(master_id, apprentice_id, relation)

        if success:
            # 记录社交事件
            db = self._get_db()
            db.record_npc_social_event(
                event_type='master_apprentice_established',
                npc1_id=master_id,
                npc2_id=apprentice_id,
                description=f"{master_id} 收 {apprentice_id} 为徒",
                is_public=True
            )
            return True, "师徒关系建立成功"

        return False, "建立师徒关系失败"

    def _establish_master_apprentice(self, master_id: str, apprentice_id: str, base_relation: Relationship) -> bool:
        """
        建立师徒关系的核心逻辑

        Args:
            master_id: 师父NPC的ID
            apprentice_id: 徒弟NPC的ID
            base_relation: 基础关系对象

        Returns:
            是否成功
        """
        try:
            # 更新关系类型为师徒
            base_relation.relation_type = RelationType.MASTER_APPRENTICE
            base_relation.intimacy = min(100, base_relation.intimacy + 20)
            base_relation.affinity = min(100, base_relation.affinity + 15)
            base_relation.add_history_entry("建立师徒关系", 15, 20, 0)

            # 确保双向关系都存在
            self._ensure_npc_exists(master_id)
            self._ensure_npc_exists(apprentice_id)

            # 更新双向关系
            self._relationships[master_id][apprentice_id] = base_relation

            # 创建反向关系
            reverse_relation = Relationship(
                npc_id=master_id,
                relation_type=RelationType.MASTER_APPRENTICE,
                affinity=base_relation.affinity,
                intimacy=base_relation.intimacy,
                hatred=0
            )
            reverse_relation.add_history_entry("拜入师门", 15, 20, 0)
            self._relationships[apprentice_id][master_id] = reverse_relation

            # 同步到数据库
            self.sync_to_database(master_id, apprentice_id)

            return True
        except Exception as e:
            print(f"建立师徒关系失败: {e}")
            return False

    def end_master_apprentice_between_npcs(self, master_id: str, apprentice_id: str,
                                           reason: str = "") -> Tuple[bool, str]:
        """
        解除NPC之间的师徒关系

        Args:
            master_id: 师父NPC的ID
            apprentice_id: 徒弟NPC的ID
            reason: 解除原因

        Returns:
            (是否成功, 消息)
        """
        relation = self.get_relationship(master_id, apprentice_id)

        if not relation or relation.relation_type != RelationType.MASTER_APPRENTICE:
            return False, "双方没有师徒关系"

        # 更新关系类型为旧识
        relation.relation_type = RelationType.ACQUAINTANCE
        relation.intimacy = max(30, relation.intimacy - 30)
        relation.affinity = max(20, relation.affinity - 20)
        relation.add_history_entry(f"解除师徒关系: {reason}", -20, -30, 0)

        # 更新双向关系
        self._relationships[apprentice_id][master_id].relation_type = RelationType.ACQUAINTANCE
        self._relationships[apprentice_id][master_id].intimacy = relation.intimacy
        self._relationships[apprentice_id][master_id].affinity = relation.affinity

        # 同步到数据库
        self.sync_to_database(master_id, apprentice_id)

        # 记录社交事件
        db = self._get_db()
        db.record_npc_social_event(
            event_type='master_apprentice_ended',
            npc1_id=master_id,
            npc2_id=apprentice_id,
            description=f"{master_id} 与 {apprentice_id} 解除师徒关系: {reason}",
            result="关系解除",
            is_public=True
        )

        return True, "师徒关系已解除"

    def get_npc_master(self, apprentice_id: str) -> Optional[Tuple[str, Relationship]]:
        """
        获取NPC的师父

        Args:
            apprentice_id: 徒弟NPC的ID

        Returns:
            (师父ID, 关系对象)，如果没有则返回None
        """
        relationships = self.get_relationships(apprentice_id)

        for other_id, rel in relationships.items():
            if rel.relation_type == RelationType.MASTER_APPRENTICE:
                return (other_id, rel)

        return None

    def get_npc_apprentices(self, master_id: str) -> List[Tuple[str, Relationship]]:
        """
        获取NPC的徒弟列表

        Args:
            master_id: 师父NPC的ID

        Returns:
            [(徒弟ID, 关系对象), ...]
        """
        apprentices = []
        relationships = self.get_relationships(master_id)

        for other_id, rel in relationships.items():
            if rel.relation_type == RelationType.MASTER_APPRENTICE:
                apprentices.append((other_id, rel))

        return apprentices

    def apply_relationship_decay(self, npc_id: str, current_time: float = None) -> List[Dict[str, Any]]:
        """
        应用关系衰减机制
        长时间不互动会导致亲密度下降

        Args:
            npc_id: NPC ID
            current_time: 当前时间戳

        Returns:
            衰减记录列表
        """
        if current_time is None:
            current_time = time.time()

        decay_records = []
        relationships = self.get_relationships(npc_id)

        for other_id, rel in relationships.items():
            # 计算距离上次互动的时间（天）
            days_since_interaction = (current_time - rel.last_interaction) / (24 * 3600)

            # 如果超过7天没有互动，开始衰减
            if days_since_interaction > 7:
                # 计算衰减值（每7天衰减1点，最多衰减5点）
                decay_periods = int(days_since_interaction / 7)
                intimacy_decay = min(5, decay_periods)

                # 特殊关系类型衰减更慢
                if rel.relation_type == RelationType.DAO_LV:
                    intimacy_decay = max(0, intimacy_decay - 2)  # 道侣关系衰减更慢
                elif rel.relation_type == RelationType.MASTER_APPRENTICE:
                    intimacy_decay = max(0, intimacy_decay - 1)  # 师徒关系衰减较慢

                if intimacy_decay > 0 and rel.intimacy > 0:
                    old_intimacy = rel.intimacy
                    new_intimacy = max(0, rel.intimacy - intimacy_decay)

                    # 更新关系
                    rel.intimacy = new_intimacy
                    rel.add_history_entry(
                        f"长时间未互动，亲密度衰减",
                        0, -intimacy_decay, 0
                    )

                    # 更新反向关系
                    if other_id in self._relationships and npc_id in self._relationships[other_id]:
                        self._relationships[other_id][npc_id].intimacy = new_intimacy

                    # 同步到数据库
                    self.sync_to_database(npc_id, other_id)

                    # 记录衰减
                    decay_records.append({
                        'npc_id': npc_id,
                        'other_id': other_id,
                        'old_intimacy': old_intimacy,
                        'new_intimacy': new_intimacy,
                        'decay': intimacy_decay,
                        'days_inactive': days_since_interaction
                    })

        return decay_records

    def process_all_relationship_decay(self, current_time: float = None) -> Dict[str, List[Dict]]:
        """
        处理所有NPC的关系衰减

        Args:
            current_time: 当前时间戳

        Returns:
            所有NPC的衰减记录 {npc_id: [decay_records]}
        """
        if current_time is None:
            current_time = time.time()

        all_decay = {}
        for npc_id in self._relationships.keys():
            decay_records = self.apply_relationship_decay(npc_id, current_time)
            if decay_records:
                all_decay[npc_id] = decay_records

        return all_decay


# 全局关系网络实例
relationship_network = NPCRelationshipNetwork()
