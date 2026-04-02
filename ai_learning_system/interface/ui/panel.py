"""
UI面板组件

提供带边框的面板容器，用于组织界面内容。
"""

from typing import List, Optional, Union
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color, colorize, strip_colors
from .theme import UITheme
from .formatter import UIFormatter


class UIPanel:
    """
    UI面板组件类
    
    提供带边框的内容容器，支持标题、自定义宽度和样式。
    """
    
    def __init__(self, 
                 title: Optional[str] = None,
                 width: Optional[int] = None,
                 border_style: str = 'single',
                 border_color: str = None,
                 title_color: str = None,
                 padding: int = 1):
        """
        初始化面板
        
        Args:
            title: 面板标题
            width: 面板宽度，默认为终端宽度
            border_style: 边框样式 ('single', 'double', 'rounded')
            border_color: 边框颜色
            title_color: 标题颜色
            padding: 内边距（空格数）
        """
        self.title = title
        self.width = width or UIFormatter.get_terminal_width()
        self.border_style = border_style
        self.border_color = border_color or UITheme.BORDER_PRIMARY
        self.title_color = title_color or UITheme.TITLE_PRIMARY
        self.padding = padding
        self.content_lines: List[str] = []
        
        self.border = UITheme.get_border(border_style)
    
    def add_line(self, text: str = '', align: str = 'left'):
        """
        添加单行内容
        
        Args:
            text: 文本内容
            align: 对齐方式 ('left', 'center', 'right')
        """
        content_width = self.width - 2 - (self.padding * 2)  # 减去边框和内边距
        
        # 处理换行
        lines = UIFormatter.wrap_text(text, content_width)
        
        for line in lines:
            if align == 'center':
                line = UIFormatter.align_center(line, content_width)
            elif align == 'right':
                line = UIFormatter.align_right(line, content_width)
            else:
                line = UIFormatter.align_left(line, content_width)
            
            self.content_lines.append(line)
    
    def add_separator(self, char: str = '─'):
        """
        添加内部分隔线
        
        Args:
            char: 分隔线字符
        """
        content_width = self.width - 2 - (self.padding * 2)
        separator = char * content_width
        self.content_lines.append(separator)
    
    def add_empty_line(self):
        """添加空行"""
        self.content_lines.append('')
    
    def render(self) -> str:
        """
        渲染面板
        
        Returns:
            格式化后的面板字符串
        """
        lines = []
        
        # 顶部边框
        if self.title:
            # 带标题的顶部边框
            title_display = f" {self.title} "
            title_width = UIFormatter.get_display_width(strip_colors(self.title))
            total_title_width = title_width + 2  # 加上两侧空格
            
            side_width = (self.width - 2 - total_title_width) // 2
            right_width = self.width - 2 - total_title_width - side_width
            
            top = (colorize(self.border['top_left'], self.border_color) +
                  colorize(self.border['horizontal'] * side_width, self.border_color) +
                  colorize(title_display, self.title_color) +
                  colorize(self.border['horizontal'] * right_width, self.border_color) +
                  colorize(self.border['top_right'], self.border_color))
        else:
            top = (colorize(self.border['top_left'], self.border_color) +
                  colorize(self.border['horizontal'] * (self.width - 2), self.border_color) +
                  colorize(self.border['top_right'], self.border_color))
        
        lines.append(top)
        
        # 内容行
        padding_str = ' ' * self.padding
        for content in self.content_lines:
            line = (colorize(self.border['vertical'], self.border_color) +
                   padding_str + content + padding_str)
            
            # 填充剩余宽度
            content_display_width = UIFormatter.get_display_width(content)
            remaining = self.width - 2 - (self.padding * 2) - content_display_width
            if remaining > 0:
                line += ' ' * remaining
            
            line += colorize(self.border['vertical'], self.border_color)
            lines.append(line)
        
        # 底部边框
        bottom = (colorize(self.border['bottom_left'], self.border_color) +
                 colorize(self.border['horizontal'] * (self.width - 2), self.border_color) +
                 colorize(self.border['bottom_right'], self.border_color))
        lines.append(bottom)
        
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        return self.render()
    
    @classmethod
    def welcome_panel(cls, 
                     title: str = "☯️ 修仙世界 - AI驱动文字修仙游戏",
                     subtitle: str = "欢迎来到修仙世界！",
                     width: int = 62) -> 'UIPanel':
        """
        创建欢迎面板
        
        Args:
            title: 主标题
            subtitle: 副标题
            width: 面板宽度
            
        Returns:
            配置好的欢迎面板
        """
        panel = cls(
            title=title,
            width=width,
            border_style='double',
            border_color=UITheme.BORDER_PRIMARY,
            title_color=UITheme.TITLE_PRIMARY
        )
        
        panel.add_empty_line()
        panel.add_line(subtitle, align='center')
        panel.add_line("这是一个由AI驱动的真实修仙体验。", align='center')
        panel.add_empty_line()
        panel.add_line("资质平庸、突破艰难、寿元有限、因果报应...", align='center')
        panel.add_line("每个选择都会影响你的修仙之路。", align='center')
        panel.add_empty_line()
        panel.add_line("输入 /help 查看可用命令", align='center')
        
        return panel
    
    @classmethod
    def help_panel(cls,
                   title: str = "📖 修仙指令大全",
                   width: int = 62) -> 'UIPanel':
        """
        创建帮助面板
        
        Args:
            title: 面板标题
            width: 面板宽度
            
        Returns:
            配置好的帮助面板框架
        """
        return cls(
            title=title,
            width=width,
            border_style='single',
            border_color=UITheme.BORDER_SECONDARY,
            title_color=UITheme.TITLE_SECONDARY
        )
    
    @classmethod
    def info_panel(cls,
                   title: str,
                   width: int = 60,
                   border_color: str = None) -> 'UIPanel':
        """
        创建信息面板
        
        Args:
            title: 面板标题
            width: 面板宽度
            border_color: 边框颜色
            
        Returns:
            配置好的信息面板
        """
        return cls(
            title=title,
            width=width,
            border_style='rounded',
            border_color=border_color or UITheme.BORDER_ACCENT,
            title_color=UITheme.TITLE_SECONDARY
        )
    
    @classmethod
    def success_panel(cls,
                     title: str = "✅ 成功",
                     message: str = "",
                     width: int = 50) -> 'UIPanel':
        """
        创建成功提示面板
        
        Args:
            title: 面板标题
            message: 成功消息
            width: 面板宽度
            
        Returns:
            配置好的成功面板
        """
        panel = cls(
            title=title,
            width=width,
            border_style='rounded',
            border_color=UITheme.SUCCESS,
            title_color=UITheme.SUCCESS
        )
        
        if message:
            panel.add_empty_line()
            panel.add_line(message, align='center')
        
        return panel
    
    @classmethod
    def error_panel(cls,
                   title: str = "❌ 错误",
                   message: str = "",
                   width: int = 50) -> 'UIPanel':
        """
        创建错误提示面板
        
        Args:
            title: 面板标题
            message: 错误消息
            width: 面板宽度
            
        Returns:
            配置好的错误面板
        """
        panel = cls(
            title=title,
            width=width,
            border_style='rounded',
            border_color=UITheme.ERROR,
            title_color=UITheme.ERROR
        )
        
        if message:
            panel.add_empty_line()
            panel.add_line(message, align='center')
        
        return panel
