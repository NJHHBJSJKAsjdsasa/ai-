from dataclasses import dataclass

@dataclass(frozen=True)
class Experience:
    """经验值值对象"""
    value: int  # 经验值数值
    source: str  # 经验值来源
    timestamp: int  # 获得经验值的时间戳
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("经验值不能为负数")
        if not self.source:
            raise ValueError("经验值来源不能为空")
        if self.timestamp < 0:
            raise ValueError("时间戳不能为负数")
    
    def add(self, other: 'Experience') -> 'Experience':
        """添加经验值"""
        return Experience(
            value=self.value + other.value,
            source=f"{self.source}, {other.source}",
            timestamp=max(self.timestamp, other.timestamp)
        )
    
    def subtract(self, amount: int) -> 'Experience':
        """减少经验值"""
        if amount < 0:
            raise ValueError("减少的经验值不能为负数")
        if amount > self.value:
            raise ValueError("减少的经验值不能超过当前经验值")
        return Experience(
            value=self.value - amount,
            source=f"{self.source} (减少{amount})",
            timestamp=self.timestamp
        )
