"""
时间系统模块
实现游戏时间与现实时间的同步
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class GameTime:
    """游戏时间数据类"""
    year: int = 1
    month: int = 1
    day: int = 1
    hour: int = 8  # 默认早上8点
    
    def to_dict(self) -> Dict[str, int]:
        return asdict(self)
    
    def to_string(self) -> str:
        """转换为字符串显示"""
        time_of_day = ""
        if 5 <= self.hour < 11:
            time_of_day = "清晨"
        elif 11 <= self.hour < 14:
            time_of_day = "正午"
        elif 14 <= self.hour < 18:
            time_of_day = "下午"
        elif 18 <= self.hour < 21:
            time_of_day = "傍晚"
        else:
            time_of_day = "深夜"
        
        return f"第{self.year}年{self.month}月{self.day}日 {time_of_day}"
    
    def advance(self, hours: int = 1):
        """推进时间"""
        self.hour += hours
        
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
            
            if self.day > 30:
                self.day = 1
                self.month += 1
                
                if self.month > 12:
                    self.month = 1
                    self.year += 1


class RealTimeSystem:
    """真实时间系统"""
    
    # 默认时间流速：1现实秒 = 10游戏分钟
    DEFAULT_TIME_SCALE = 600  # 10分钟 = 600秒
    
    def __init__(self, time_scale: float = None):
        """
        初始化真实时间系统
        
        Args:
            time_scale: 时间流速（1现实秒 = X游戏秒），默认600（10分钟）
        """
        self.time_scale = time_scale or self.DEFAULT_TIME_SCALE
        self.game_time = GameTime()
        self.last_update_time = time.time()
        self.is_paused = False
        
        # 玩家时间记录（用于离线计算）
        self.player_last_online: Dict[str, float] = {}
    
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
            self.game_time.advance(game_hours)
        
        return game_hours
    
    def get_game_time(self) -> GameTime:
        """获取当前游戏时间"""
        return self.game_time
    
    def set_game_time(self, year: int = None, month: int = None, 
                      day: int = None, hour: int = None):
        """设置游戏时间"""
        if year is not None:
            self.game_time.year = year
        if month is not None:
            self.game_time.month = max(1, min(12, month))
        if day is not None:
            self.game_time.day = max(1, min(30, day))
        if hour is not None:
            self.game_time.hour = max(0, min(23, hour))
    
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
        
        self.game_time.advance(hours_to_advance)
        
        return hours_to_advance
    
    def get_time_of_day(self) -> str:
        """获取当前时段"""
        hour = self.game_time.hour
        if 5 <= hour < 11:
            return "morning"  # 清晨
        elif 11 <= hour < 14:
            return "noon"     # 正午
        elif 14 <= hour < 18:
            return "afternoon" # 下午
        elif 18 <= hour < 21:
            return "evening"   # 傍晚
        else:
            return "night"     # 深夜
    
    def get_season(self) -> str:
        """获取当前季节"""
        month = self.game_time.month
        if month in [3, 4, 5]:
            return "spring"   # 春
        elif month in [6, 7, 8]:
            return "summer"   # 夏
        elif month in [9, 10, 11]:
            return "autumn"   # 秋
        else:
            return "winter"   # 冬
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "game_time": self.game_time.to_dict(),
            "time_scale": self.time_scale,
            "is_paused": self.is_paused,
            "last_update_time": self.last_update_time,
            "player_last_online": self.player_last_online,
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        if "game_time" in data:
            gt = data["game_time"]
            self.game_time = GameTime(
                year=gt.get("year", 1),
                month=gt.get("month", 1),
                day=gt.get("day", 1),
                hour=gt.get("hour", 8),
            )
        self.time_scale = data.get("time_scale", self.DEFAULT_TIME_SCALE)
        self.is_paused = data.get("is_paused", False)
        self.player_last_online = data.get("player_last_online", {})
        self.last_update_time = time.time()


# 全局时间系统实例
time_system = RealTimeSystem()


def get_time_system() -> RealTimeSystem:
    """获取全局时间系统实例"""
    return time_system
