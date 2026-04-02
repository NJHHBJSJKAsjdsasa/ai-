"""
UI排版格式化工具

提供文本对齐、换行、截断等排版功能。
"""

import re
import shutil
from typing import List, Optional, Tuple
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color, colorize, strip_colors
from .theme import UITheme


class UIFormatter:
    """
    UI排版格式化类
    
    提供统一的文本排版功能，包括对齐、换行、截断等。
    """
    
    # 默认终端宽度
    DEFAULT_WIDTH = 80
    
    # 最小宽度
    MIN_WIDTH = 40
    
    @classmethod
    def get_terminal_width(cls) -> int:
        """
        获取终端宽度
        
        Returns:
            终端宽度（字符数）
        """
        try:
            width = shutil.get_terminal_size().columns
            return max(width, cls.MIN_WIDTH)
        except:
            return cls.DEFAULT_WIDTH
    
    @classmethod
    def align_left(cls, text: str, width: int, fill_char: str = ' ') -> str:
        """
        左对齐文本
        
        Args:
            text: 要对齐的文本
            width: 目标宽度
            fill_char: 填充字符
            
        Returns:
            对齐后的文本
        """
        text_width = cls.get_display_width(text)
        if text_width >= width:
            return text
        padding = fill_char * (width - text_width)
        return text + padding
    
    @classmethod
    def align_right(cls, text: str, width: int, fill_char: str = ' ') -> str:
        """
        右对齐文本
        
        Args:
            text: 要对齐的文本
            width: 目标宽度
            fill_char: 填充字符
            
        Returns:
            对齐后的文本
        """
        text_width = cls.get_display_width(text)
        if text_width >= width:
            return text
        padding = fill_char * (width - text_width)
        return padding + text
    
    @classmethod
    def align_center(cls, text: str, width: int, fill_char: str = ' ') -> str:
        """
        居中对齐文本
        
        Args:
            text: 要对齐的文本
            width: 目标宽度
            fill_char: 填充字符
            
        Returns:
            对齐后的文本
        """
        text_width = cls.get_display_width(text)
        if text_width >= width:
            return text
        total_padding = width - text_width
        left_padding = fill_char * (total_padding // 2)
        right_padding = fill_char * (total_padding - total_padding // 2)
        return left_padding + text + right_padding
    
    @classmethod
    def get_display_width(cls, text: str) -> int:
        """
        获取文本的显示宽度（处理ANSI颜色代码和宽字符）
        
        Args:
            text: 输入文本
            
        Returns:
            显示宽度
        """
        # 移除ANSI颜色代码
        clean_text = strip_colors(text)
        
        width = 0
        for char in clean_text:
            # 中文字符和宽字符占2个宽度
            if ord(char) > 127:
                width += 2
            else:
                width += 1
        return width
    
    @classmethod
    def truncate(cls, text: str, max_width: int, suffix: str = '...') -> str:
        """
        截断文本到指定宽度
        
        Args:
            text: 要截断的文本
            max_width: 最大宽度
            suffix: 截断后缀
            
        Returns:
            截断后的文本
        """
        text_width = cls.get_display_width(text)
        if text_width <= max_width:
            return text
        
        suffix_width = cls.get_display_width(suffix)
        target_width = max_width - suffix_width
        
        result = []
        current_width = 0
        for char in strip_colors(text):
            char_width = 2 if ord(char) > 127 else 1
            if current_width + char_width > target_width:
                break
            result.append(char)
            current_width += char_width
        
        return ''.join(result) + suffix
    
    @classmethod
    def wrap_text(cls, text: str, max_width: int) -> List[str]:
        """
        自动换行文本
        
        Args:
            text: 要换行的文本
            max_width: 每行最大宽度
            
        Returns:
            换行后的文本列表
        """
        if not text:
            return ['']
        
        lines = []
        current_line = []
        current_width = 0
        
        # 移除颜色代码进行计算
        clean_text = strip_colors(text)
        
        for word in clean_text.split(' '):
            word_width = cls.get_display_width(word)
            
            # 单词本身超过最大宽度，需要截断
            if word_width > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_width = 0
                
                # 逐字符截断长单词
                partial = []
                partial_width = 0
                for char in word:
                    char_width = 2 if ord(char) > 127 else 1
                    if partial_width + char_width > max_width:
                        lines.append(''.join(partial))
                        partial = [char]
                        partial_width = char_width
                    else:
                        partial.append(char)
                        partial_width += char_width
                
                if partial:
                    current_line = [''.join(partial)]
                    current_width = partial_width
                continue
            
            # 检查是否需要换行
            space_width = 1 if current_line else 0
            if current_width + space_width + word_width > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += space_width + word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else ['']
    
    @classmethod
    def create_separator(cls, width: Optional[int] = None, 
                        char: str = '─',
                        color: str = None) -> str:
        """
        创建分隔线
        
        Args:
            width: 分隔线宽度，默认为终端宽度
            char: 分隔线字符
            color: 颜色代码
            
        Returns:
            分隔线字符串
        """
        if width is None:
            width = cls.get_terminal_width()
        
        separator = char * width
        
        if color:
            return colorize(separator, color)
        return separator
    
    @classmethod
    def create_header(cls, title: str, 
                     width: Optional[int] = None,
                     border_style: str = 'single',
                     border_color: str = None) -> str:
        """
        创建带标题的头部
        
        Args:
            title: 标题文本
            width: 宽度
            border_style: 边框样式
            border_color: 边框颜色
            
        Returns:
            格式化后的头部字符串
        """
        if width is None:
            width = cls.get_terminal_width()
        
        border = UITheme.get_border(border_style)
        
        if border_color is None:
            border_color = UITheme.BORDER_PRIMARY
        
        # 计算标题显示宽度
        title_width = cls.get_display_width(title)
        
        # 创建顶部边框
        top_border = (colorize(border['top_left'], border_color) +
                     colorize(border['horizontal'] * (width - 2), border_color) +
                     colorize(border['top_right'], border_color))
        
        # 创建标题行
        content_width = width - 4  # 减去边框和空格
        if title_width > content_width:
            title = cls.truncate(title, content_width)
        
        title_line = (colorize(border['vertical'], border_color) + ' ' +
                     cls.align_center(title, content_width) + ' ' +
                     colorize(border['vertical'], border_color))
        
        return f"{top_border}\n{title_line}"
    
    @classmethod
    def indent(cls, text: str, spaces: int = 2) -> str:
        """
        缩进文本
        
        Args:
            text: 要缩进的文本
            spaces: 缩进空格数
            
        Returns:
            缩进后的文本
        """
        indent_str = ' ' * spaces
        lines = text.split('\n')
        return '\n'.join(indent_str + line for line in lines)
