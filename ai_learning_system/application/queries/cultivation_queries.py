from dataclasses import dataclass
from typing import Optional

@dataclass
class GetCultivationStatusQuery:
    """获取修炼状态查询"""
    player_id: str
