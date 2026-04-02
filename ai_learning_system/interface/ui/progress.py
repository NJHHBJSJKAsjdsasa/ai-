"""
UI进度条组件

提供带颜色的进度条显示，用于修为、血量等数值展示。
"""

from typing import Optional
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color, colorize
from .theme import UITheme
from .formatter import UIFormatter


class UIProgress:
    """
    UI进度条组件类
    
    提供格式化的进度条显示，支持自定义颜色、宽度和样式。
    """
    
    # 进度条字符
    FILLED_CHAR = '█'
    EMPTY_CHAR = '░'
    
    # 渐变颜色映射（从低到高）
    GRADIENT_COLORS = [
        Color.BOLD_RED,      # 0-20%
        Color.BOLD_YELLOW,   # 20-40%
        Color.BOLD_GREEN,    # 40-60%
        Color.BOLD_CYAN,     # 60-80%
        Color.BOLD_BLUE,     # 80-100%
    ]
    
    def __init__(self,
                 current: float = 0,
                 maximum: float = 100,
                 width: int = 30,
                 show_percentage: bool = True,
                 show_value: bool = True,
                 color: str = None,
                 label: str = None):
        """
        初始化进度条
        
        Args:
            current: 当前值
            maximum: 最大值
            width: 进度条宽度（字符数）
            show_percentage: 是否显示百分比
            show_value: 是否显示数值
            color: 进度条颜色，None则使用渐变色
            label: 标签文本
        """
        self.current = current
        self.maximum = maximum
        self.width = width
        self.show_percentage = show_percentage
        self.show_value = show_value
        self.color = color
        self.label = label
    
    def _get_gradient_color(self, percentage: float) -> str:
        """
        根据百分比获取渐变色
        
        Args:
            percentage: 百分比 (0-100)
            
        Returns:
            颜色代码
        """
        index = min(int(percentage / 20), len(self.GRADIENT_COLORS) - 1)
        return self.GRADIENT_COLORS[index]
    
    def render(self) -> str:
        """
        渲染进度条
        
        Returns:
            格式化后的进度条字符串
        """
        # 计算百分比
        if self.maximum <= 0:
            percentage = 0
        else:
            percentage = min(100, max(0, (self.current / self.maximum) * 100))
        
        # 计算填充长度
        filled_length = int(self.width * percentage / 100)
        empty_length = self.width - filled_length
        
        # 确定颜色
        bar_color = self.color or self._get_gradient_color(percentage)
        
        # 创建进度条
        filled_part = self.FILLED_CHAR * filled_length
        empty_part = self.EMPTY_CHAR * empty_length
        
        bar = colorize(filled_part, bar_color) + colorize(empty_part, Color.DIM)
        
        # 构建结果
        parts = []
        
        # 添加标签
        if self.label:
            parts.append(f"{self.label}:")
        
        # 添加进度条
        parts.append(f"[{bar}]")
        
        # 添加数值
        if self.show_value:
            parts.append(f"{int(self.current)}/{int(self.maximum)}")
        
        # 添加百分比
        if self.show_percentage:
            parts.append(f"{percentage:.1f}%")
        
        return ' '.join(parts)
    
    def __str__(self) -> str:
        return self.render()
    
    @classmethod
    def cultivation_bar(cls,
                       current_exp: float,
                       max_exp: float,
                       realm_name: str = "",
                       width: int = 30) -> 'UIProgress':
        """
        创建修为进度条
        
        Args:
            current_exp: 当前修为
            max_exp: 修为上限
            realm_name: 境界名称
            width: 进度条宽度
            
        Returns:
            配置好的修为进度条
        """
        label = f"☯️ {realm_name}" if realm_name else "☯️ 修为"
        return cls(
            current=current_exp,
            maximum=max_exp,
            width=width,
            show_percentage=True,
            show_value=True,
            color=Color.BOLD_CYAN,
            label=label
        )
    
    @classmethod
    def health_bar(cls,
                  current_hp: float,
                  max_hp: float,
                  label: str = "❤️ 生命",
                  width: int = 25) -> 'UIProgress':
        """
        创建血量/生命值进度条
        
        Args:
            current_hp: 当前生命值
            max_hp: 最大生命值
            label: 标签
            width: 进度条宽度
            
        Returns:
            配置好的生命值进度条
        """
        # 根据血量百分比确定颜色
        percentage = (current_hp / max_hp * 100) if max_hp > 0 else 0
        if percentage > 60:
            color = Color.BOLD_GREEN
        elif percentage > 30:
            color = Color.BOLD_YELLOW
        else:
            color = Color.BOLD_RED
        
        return cls(
            current=current_hp,
            maximum=max_hp,
            width=width,
            show_percentage=True,
            show_value=True,
            color=color,
            label=label
        )
    
    @classmethod
    def mana_bar(cls,
                current_mana: float,
                max_mana: float,
                label: str = "💧 法力",
                width: int = 25) -> 'UIProgress':
        """
        创建法力值进度条
        
        Args:
            current_mana: 当前法力值
            max_mana: 最大法力值
            label: 标签
            width: 进度条宽度
            
        Returns:
            配置好的法力值进度条
        """
        return cls(
            current=current_mana,
            maximum=max_mana,
            width=width,
            show_percentage=True,
            show_value=True,
            color=Color.BOLD_BLUE,
            label=label
        )
    
    @classmethod
    def stamina_bar(cls,
                   current_stamina: float,
                   max_stamina: float,
                   label: str = "⚡ 体力",
                   width: int = 25) -> 'UIProgress':
        """
        创建体力值进度条
        
        Args:
            current_stamina: 当前体力值
            max_stamina: 最大体力值
            label: 标签
            width: 进度条宽度
            
        Returns:
            配置好的体力值进度条
        """
        return cls(
            current=current_stamina,
            maximum=max_stamina,
            width=width,
            show_percentage=True,
            show_value=True,
            color=Color.BOLD_YELLOW,
            label=label
        )
    
    @classmethod
    def karma_bar(cls,
                 karma: float,
                 label: str = "☸️ 因果",
                 width: int = 25) -> 'UIProgress':
        """
        创建因果值进度条（双向）
        
        Args:
            karma: 因果值（正为善，负为恶）
            label: 标签
            width: 进度条宽度
            
        Returns:
            配置好的因果值进度条
        """
        # 将因果值映射到0-100范围
        max_karma = 1000
        normalized_karma = min(max_karma, max(-max_karma, karma))
        
        # 确定颜色
        if karma > 0:
            color = Color.BOLD_GREEN  # 善
        elif karma < 0:
            color = Color.BOLD_RED    # 恶
        else:
            color = Color.DIM         # 中性
        
        # 显示为0-100%的进度
        display_value = (normalized_karma + max_karma) / 2
        
        return cls(
            current=display_value,
            maximum=max_karma,
            width=width,
            show_percentage=False,
            show_value=True,
            color=color,
            label=label
        )
