from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CultivationRealm:
    """修炼境界值对象"""
    name: str  # 境界名称
    level: int  # 境界等级
    description: str  # 境界描述
    required_exp: int  # 突破所需经验值
    lifespan_bonus: int  # 寿元加成
    spiritual_power_bonus: int  # 灵力加成
    next_realm: Optional['CultivationRealm'] = None  # 下一境界
    
    def __eq__(self, other):
        if not isinstance(other, CultivationRealm):
            return False
        return self.level == other.level
    
    def __lt__(self, other):
        if not isinstance(other, CultivationRealm):
            raise TypeError("Can only compare with CultivationRealm")
        return self.level < other.level
    
    def __gt__(self, other):
        if not isinstance(other, CultivationRealm):
            raise TypeError("Can only compare with CultivationRealm")
        return self.level > other.level
    
    def is_higher_than(self, other: 'CultivationRealm') -> bool:
        """检查是否高于另一个境界"""
        return self.level > other.level
    
    def is_lower_than(self, other: 'CultivationRealm') -> bool:
        """检查是否低于另一个境界"""
        return self.level < other.level
    
    def can_breakthrough(self, current_exp: int) -> bool:
        """检查是否可以突破到下一境界"""
        return current_exp >= self.required_exp
    
    def get_breakthrough_difficulty(self) -> float:
        """获取突破难度"""
        return self.level * 0.1
    
    def get_realm_progress(self, current_exp: int) -> float:
        """获取当前境界的进度"""
        if self.required_exp <= 0:
            return 0.0
        return min(1.0, current_exp / self.required_exp)
