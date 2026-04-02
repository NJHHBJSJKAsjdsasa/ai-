"""
UI主题管理模块

定义和管理UI颜色主题，确保界面风格统一。
"""

from enum import Enum
from typing import Dict, Optional
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color


class UITheme:
    """
    UI主题管理类
    
    提供统一的颜色主题配置，确保界面风格一致。
    """
    
    # 边框颜色
    BORDER_PRIMARY = Color.BOLD_CYAN      # 主边框
    BORDER_SECONDARY = Color.BOLD_BLUE    # 次边框
    BORDER_ACCENT = Color.BOLD_MAGENTA    # 强调边框
    
    # 标题颜色
    TITLE_PRIMARY = Color.BOLD_WHITE      # 主标题
    TITLE_SECONDARY = Color.BOLD_CYAN     # 次标题
    TITLE_SUCCESS = Color.BOLD_GREEN      # 成功标题
    TITLE_WARNING = Color.BOLD_YELLOW     # 警告标题
    TITLE_ERROR = Color.BOLD_RED          # 错误标题
    
    # 文本颜色
    TEXT_NORMAL = Color.RESET             # 普通文本
    TEXT_DIM = Color.DIM                  # 暗淡文本
    TEXT_EMPHASIS = Color.BOLD            # 强调文本
    
    # 状态颜色
    SUCCESS = Color.BOLD_GREEN            # 成功
    WARNING = Color.BOLD_YELLOW           # 警告
    ERROR = Color.BOLD_RED                # 错误
    INFO = Color.BOLD_BLUE                # 信息
    
    # 特殊元素颜色
    HIGHLIGHT = Color.BOLD_CYAN           # 高亮
    MUTED = Color.DIM                     # 淡化
    
    # 图标颜色映射
    ICON_COLORS = {
        'success': Color.BOLD_GREEN,
        'warning': Color.BOLD_YELLOW,
        'error': Color.BOLD_RED,
        'info': Color.BOLD_BLUE,
        'highlight': Color.BOLD_CYAN,
        'muted': Color.DIM,
    }
    
    # 边框样式
    BORDER_STYLES = {
        'single': {
            'horizontal': '─',
            'vertical': '│',
            'top_left': '┌',
            'top_right': '┐',
            'bottom_left': '└',
            'bottom_right': '┘',
            'left_t': '├',
            'right_t': '┤',
            'top_t': '┬',
            'bottom_t': '┴',
            'cross': '┼',
        },
        'double': {
            'horizontal': '═',
            'vertical': '║',
            'top_left': '╔',
            'top_right': '╗',
            'bottom_left': '╚',
            'bottom_right': '╝',
            'left_t': '╠',
            'right_t': '╣',
            'top_t': '╦',
            'bottom_t': '╩',
            'cross': '╬',
        },
        'rounded': {
            'horizontal': '─',
            'vertical': '│',
            'top_left': '╭',
            'top_right': '╮',
            'bottom_left': '╰',
            'bottom_right': '╯',
            'left_t': '├',
            'right_t': '┤',
            'top_t': '┬',
            'bottom_t': '┴',
            'cross': '┼',
        },
    }
    
    @classmethod
    def get_border(cls, style: str = 'single') -> Dict[str, str]:
        """
        获取边框样式
        
        Args:
            style: 边框样式名称 ('single', 'double', 'rounded')
            
        Returns:
            边框字符字典
        """
        return cls.BORDER_STYLES.get(style, cls.BORDER_STYLES['single'])
    
    @classmethod
    def get_icon_color(cls, icon_type: str) -> str:
        """
        获取图标颜色
        
        Args:
            icon_type: 图标类型
            
        Returns:
            颜色代码
        """
        return cls.ICON_COLORS.get(icon_type, Color.RESET)
