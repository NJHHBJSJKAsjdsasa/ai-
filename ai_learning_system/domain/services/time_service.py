"""
时间系统领域服务
"""

import time
from typing import Dict, Tuple
from dataclasses import dataclass

from domain.value_objects.time import GameTime


@dataclass
class RealTimeSystem:
    """真实时间系统服务"""
    
    # 默认时间流速：1现实秒 = 10游戏分钟
    DEFAULT_TIME_SCALE = 600  # 10分钟 = 600秒
    
    time_scale: float = None
    game_time: GameTime = None
    last_update_time: float = None
    is_paused: bool = False
    
    # 玩家时间记录（用于离线计算）
    player_last_online: Dict[str, float] = None
    
    def __post_init__(self):
        """初始化"""
        self.time_scale = self.time_scale or self.DEFAULT_TIME_SCALE
        self.game_time = self.game_time or GameTime()
        self.last_update_time = self.last_update_time or time.time()
        self.player_last_online = self.player_last_online or {}
    
    def update(self) -> int:
        """
        更新游戏时间
        
        Returns:
            推进的游戏小时数
        """
        if self.is_paused:
            return 0
        
        current_time = time.time()
        real_elapsed = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 计算游戏时间流逝
        game_elapsed_seconds = real_elapsed * self.time_scale
        game_hours = int(game_elapsed_seconds / 3600)
        
        if game_hours > 0:
            self.game_time = self.game_time.advance(game_hours)
        
        return game_hours
    
    def get_game_time(self) -> GameTime:
        """获取当前游戏时间"""
        return self.game_time
    
    def set_game_time(self, year: int = None, month: int = None, 
                      day: int = None, hour: int = None):
        """设置游戏时间"""
        current_time = self.game_time
        self.game_time = GameTime(
            year=year if year is not None else current_time.year,
            month=month if month is not None else current_time.month,
            day=day if day is not None else current_time.day,
            hour=hour if hour is not None else current_time.hour
        )
    
    def set_time_scale(self, scale: float):
        """
        设置时间流速
        
        Args:
            scale: 1现实秒 = X游戏秒
        """
        self.time_scale = max(1, scale)  # 最小1秒
    
    def pause(self):
        """暂停时间"""
        self.is_paused = True
    
    def resume(self):
        """恢复时间"""
        self.is_paused = False
        self.last_update_time = time.time()
    
    def record_player_online(self, player_id: str):
        """
        记录玩家上线时间
        
        Args:
            player_id: 玩家ID
        """
        self.player_last_online[player_id] = time.time()
    
    def record_player_offline(self, player_id: str):
        """
        记录玩家离线时间
        
        Args:
            player_id: 玩家ID
        """
        self.player_last_online[player_id] = time.time()
    
    def calculate_offline_time(self, player_id: str) -> Tuple[int, float]:
        """
        计算玩家离线时间
        
        Args:
            player_id: 玩家ID
            
        Returns:
            (游戏小时数, 现实秒数)
        """
        if player_id not in self.player_last_online:
            return (0, 0)
        
        last_online = self.player_last_online[player_id]
        real_elapsed = time.time() - last_online
        
        # 计算游戏时间
        game_elapsed_seconds = real_elapsed * self.time_scale
        game_hours = int(game_elapsed_seconds / 3600)
        
        return (game_hours, real_elapsed)
    
    def advance_offline(self, game_hours: int):
        """
        批量推进离线时间
        
        Args:
            game_hours: 游戏小时数
        """
        # 限制最大离线时间（避免一次推进太多）
        max_hours = 24 * 30  # 最多推进30天
        hours_to_advance = min(game_hours, max_hours)
        
        self.game_time = self.game_time.advance(hours_to_advance)
        
        return hours_to_advance
    
    def get_time_of_day(self) -> str:
        """获取当前时段"""
        return self.game_time.get_time_of_day()
    
    def get_season(self) -> str:
        """获取当前季节"""
        return self.game_time.get_season()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "game_time": self.game_time.to_dict(),
            "time_scale": self.time_scale,
            "is_paused": self.is_paused,
            "last_update_time": self.last_update_time,
            "player_last_online": self.player_last_online,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RealTimeSystem':
        """从字典加载"""
        game_time = GameTime.from_dict(data.get("game_time", {}))
        return cls(
            game_time=game_time,
            time_scale=data.get("time_scale", cls.DEFAULT_TIME_SCALE),
            is_paused=data.get("is_paused", False),
            player_last_online=data.get("player_last_online", {})
        )