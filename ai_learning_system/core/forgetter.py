"""
遗忘机制模块

实现记忆的过期检查、强度计算、自动遗忘和归档功能
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class Forgetter:
    """遗忘管理器，负责记忆的过期检查、强度计算和自动清理"""

    def __init__(self, database):
        """
        初始化遗忘管理器

        Args:
            database: 数据库实例，用于操作记忆数据
        """
        self.database = database

    def is_expired(self, memory: Dict[str, Any]) -> bool:
        """
        检查记忆是否过期

        Args:
            memory: 记忆字典，包含 created_at 和 retention_days

        Returns:
            如果记忆已过期返回 True，否则返回 False
        """
        created_at = memory.get('created_at')
        retention_days = memory.get('retention_days', 30)

        if not created_at:
            return False

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        expiration_time = created_at + timedelta(days=retention_days)
        return datetime.now() > expiration_time

    def calculate_memory_strength(self, memory: Dict[str, Any]) -> float:
        """
        计算记忆强度

        基于重要性、访问次数、最后访问时间计算记忆强度
        返回 0-1 之间的强度值

        Args:
            memory: 记忆字典

        Returns:
            0-1 之间的强度值
        """
        importance = memory.get('importance', 5)
        access_count = memory.get('access_count', 0)
        last_accessed = memory.get('last_accessed')

        importance_factor = min(importance / 10.0, 1.0)

        access_factor = min(access_count / 20.0, 1.0)

        recency_factor = 0.5
        if last_accessed:
            if isinstance(last_accessed, str):
                last_accessed = datetime.fromisoformat(last_accessed)
            days_since_access = (datetime.now() - last_accessed).days
            recency_factor = max(0, 1.0 - (days_since_access / 30.0))

        strength = (importance_factor * 0.4 +
                   access_factor * 0.3 +
                   recency_factor * 0.3)

        return min(max(strength, 0.0), 1.0)

    def should_forget(self, memory: Dict[str, Any]) -> bool:
        """
        判断是否该遗忘该记忆

        - 如果过期且强度低，返回 True
        - 如果重要性 >= 10，永不遗忘

        Args:
            memory: 记忆字典

        Returns:
            是否应该遗忘
        """
        importance = memory.get('importance', 5)
        if importance >= 10:
            return False

        if not self.is_expired(memory):
            return False

        strength = self.calculate_memory_strength(memory)
        return strength < 0.3

    def forget_expired_memories(self) -> List[Dict[str, Any]]:
        """
        遗忘所有过期记忆

        遍历所有记忆，删除过期且应该遗忘的记忆

        Returns:
            被删除的记忆列表
        """
        deleted_memories = []
        all_memories = self.database.get_all_memories()

        for memory in all_memories:
            if self.should_forget(memory):
                memory_id = memory.get('id')
                if memory_id:
                    self.database.delete_memory(memory_id)
                    deleted_memories.append(memory)

        return deleted_memories

    def archive_old_memories(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        归档旧记忆

        将超过指定天数未访问的记忆标记为归档

        Args:
            days: 未访问天数阈值，默认 30 天

        Returns:
            被归档的记忆列表
        """
        archived_memories = []
        all_memories = self.database.get_all_memories()
        cutoff_date = datetime.now() - timedelta(days=days)

        for memory in all_memories:
            last_accessed = memory.get('last_accessed')
            if not last_accessed:
                continue

            if isinstance(last_accessed, str):
                last_accessed = datetime.fromisoformat(last_accessed)

            if last_accessed < cutoff_date:
                memory_id = memory.get('id')
                if memory_id:
                    self.database.update_memory(memory_id, {'status': 'archived'})
                    archived_memories.append(memory)

        return archived_memories

    def strengthen_memory(self, memory_id: str) -> bool:
        """
        强化记忆（延长保留期）

        增加访问次数，更新最后访问时间，延长保留天数

        Args:
            memory_id: 记忆 ID

        Returns:
            是否成功强化
        """
        memory = self.database.get_memory(memory_id)
        if not memory:
            return False

        current_access_count = memory.get('access_count', 0)
        importance = memory.get('importance', 5)

        additional_days = min(importance * 2, 30)
        current_retention = memory.get('retention_days', 30)
        new_retention = current_retention + additional_days

        updates = {
            'access_count': current_access_count + 1,
            'last_accessed': datetime.now().isoformat(),
            'retention_days': new_retention
        }

        self.database.update_memory(memory_id, updates)
        return True

    def get_forgetting_stats(self) -> Dict[str, Any]:
        """
        获取遗忘统计

        Returns:
            包含各种统计信息的字典
        """
        all_memories = self.database.get_all_memories()

        total_memories = len(all_memories)
        expired_count = 0
        archived_count = 0
        high_importance_count = 0
        total_strength = 0.0

        for memory in all_memories:
            if self.is_expired(memory):
                expired_count += 1

            if memory.get('status') == 'archived':
                archived_count += 1

            if memory.get('importance', 5) >= 10:
                high_importance_count += 1

            total_strength += self.calculate_memory_strength(memory)

        avg_strength = total_strength / total_memories if total_memories > 0 else 0.0

        return {
            'total_memories': total_memories,
            'expired_memories': expired_count,
            'archived_memories': archived_count,
            'high_importance_memories': high_importance_count,
            'average_strength': round(avg_strength, 4),
            'forgettable_memories': sum(1 for m in all_memories if self.should_forget(m))
        }
