from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Memory:
    """记忆数据类"""
    content: str
    importance: int  # 重要性评分 0-10
    category: str  # 分类标签
    is_encrypted: bool  # 是否加密
    retention_days: int  # 保留天数
    source: str = "user"  # 记忆来源 (user/ai)
    id: int = None  # 记忆ID，数据库自动生成
    created_at: datetime = None  # 创建时间
    last_accessed: datetime = None  # 最后访问时间
    access_count: int = 0  # 访问次数
    privacy_level: int = 0  # 隐私级别 0-100

    def __post_init__(self):
        """验证字段值的有效性，并为 None 的字段设置默认值"""
        # 设置默认时间
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = datetime.now()
        
        # 验证字段值
        if not 0 <= self.importance <= 10:
            raise ValueError(f"importance 必须在 0-10 之间，当前值: {self.importance}")
        if not 0 <= self.privacy_level <= 100:
            raise ValueError(f"privacy_level 必须在 0-100 之间，当前值: {self.privacy_level}")
        if self.access_count < 0:
            raise ValueError(f"access_count 不能为负数，当前值: {self.access_count}")
        if self.retention_days < 0:
            raise ValueError(f"retention_days 不能为负数，当前值: {self.retention_days}")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'importance': self.importance,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'privacy_level': self.privacy_level,
            'is_encrypted': self.is_encrypted,
            'retention_days': self.retention_days,
            'source': self.source
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Memory':
        """从字典创建 Memory 对象"""
        return cls(
            id=data['id'],
            content=data['content'],
            importance=data['importance'],
            category=data['category'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            access_count=data['access_count'],
            privacy_level=data['privacy_level'],
            is_encrypted=data['is_encrypted'],
            retention_days=data['retention_days'],
            source=data.get('source', 'user')
        )

    @classmethod
    def from_row(cls, row: tuple) -> 'Memory':
        """从数据库行创建 Memory 对象"""
        return cls(
            id=row[0],
            content=row[1],
            importance=row[2],
            category=row[3],
            created_at=datetime.fromisoformat(row[4]),
            last_accessed=datetime.fromisoformat(row[5]),
            access_count=row[6],
            privacy_level=row[7],
            is_encrypted=bool(row[8]),
            retention_days=row[9],
            source=row[10] if len(row) > 10 else 'user'
        )
