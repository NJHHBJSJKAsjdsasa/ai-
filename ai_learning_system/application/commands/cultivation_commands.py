from dataclasses import dataclass
from typing import Optional

@dataclass
class CultivateCommand:
    """修炼命令"""
    player_id: str
    time_spent: int

@dataclass
class AttemptBreakthroughCommand:
    """尝试突破命令"""
    player_id: str
