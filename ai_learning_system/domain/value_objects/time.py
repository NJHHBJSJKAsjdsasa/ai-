"""
时间系统值对象模块
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class GameTime:
    """游戏时间值对象"""
    year: int = 1
    month: int = 1
    day: int = 1
    hour: int = 8  # 默认早上8点
    
    def __post_init__(self):
        """初始化后验证"""
        if self.year < 1:
            raise ValueError("年份必须大于0")
        if self.month < 1 or self.month > 12:
            raise ValueError("月份必须在1-12之间")
        if self.day < 1 or self.day > 30:
            raise ValueError("日期必须在1-30之间")
        if self.hour < 0 or self.hour > 23:
            raise ValueError("小时必须在0-23之间")
    
    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour
        }
    
    def to_string(self) -> str:
        """转换为字符串显示"""
        time_of_day = self.get_time_of_day()
        return f"第{self.year}年{self.month}月{self.day}日 {time_of_day}"
    
    def advance(self, hours: int = 1) -> 'GameTime':
        """推进时间，返回新的GameTime对象"""
        new_hour = self.hour + hours
        new_day = self.day
        new_month = self.month
        new_year = self.year
        
        while new_hour >= 24:
            new_hour -= 24
            new_day += 1
            
            if new_day > 30:
                new_day = 1
                new_month += 1
                
                if new_month > 12:
                    new_month = 1
                    new_year += 1
        
        return GameTime(
            year=new_year,
            month=new_month,
            day=new_day,
            hour=new_hour
        )
    
    def get_time_of_day(self) -> str:
        """获取当前时段"""
        if 5 <= self.hour < 11:
            return "清晨"
        elif 11 <= self.hour < 14:
            return "正午"
        elif 14 <= self.hour < 18:
            return "下午"
        elif 18 <= self.hour < 21:
            return "傍晚"
        else:
            return "深夜"
    
    def get_season(self) -> str:
        """获取当前季节"""
        if self.month in [3, 4, 5]:
            return "春"
        elif self.month in [6, 7, 8]:
            return "夏"
        elif self.month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'GameTime':
        """从字典创建GameTime对象"""
        return cls(
            year=data.get("year", 1),
            month=data.get("month", 1),
            day=data.get("day", 1),
            hour=data.get("hour", 8)
        )