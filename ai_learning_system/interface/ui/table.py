"""
UI表格组件

提供格式化的表格显示，支持列宽自适应和对齐。
"""

from typing import List, Dict, Any, Optional, Union
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color, colorize, strip_colors
from .theme import UITheme
from .formatter import UIFormatter


class UITable:
    """
    UI表格组件类
    
    提供格式化的表格显示，支持表头、数据行、列宽自适应。
    """
    
    def __init__(self,
                 headers: Optional[List[str]] = None,
                 rows: Optional[List[List[str]]] = None,
                 width: Optional[int] = None,
                 border_style: str = 'single',
                 border_color: str = None,
                 header_color: str = None):
        """
        初始化表格
        
        Args:
            headers: 表头列表
            rows: 数据行列表
            width: 表格宽度，默认为终端宽度
            border_style: 边框样式
            border_color: 边框颜色
            header_color: 表头颜色
        """
        self.headers = headers or []
        self.rows = rows or []
        self.width = width or UIFormatter.get_terminal_width()
        self.border_style = border_style
        self.border_color = border_color or UITheme.BORDER_SECONDARY
        self.header_color = header_color or UITheme.TITLE_SECONDARY
        
        self.border = UITheme.get_border(border_style)
        self._column_widths: List[int] = []
    
    def add_row(self, row: List[str]):
        """
        添加数据行
        
        Args:
            row: 行数据列表
        """
        self.rows.append(row)
    
    def set_headers(self, headers: List[str]):
        """
        设置表头
        
        Args:
            headers: 表头列表
        """
        self.headers = headers
    
    def _calculate_column_widths(self) -> List[int]:
        """
        计算每列的宽度
        
        Returns:
            每列宽度的列表
        """
        if not self.headers and not self.rows:
            return []
        
        # 确定列数
        col_count = 0
        if self.headers:
            col_count = len(self.headers)
        elif self.rows:
            col_count = max(len(row) for row in self.rows)
        
        # 初始化每列宽度
        col_widths = [0] * col_count
        
        # 考虑表头宽度
        if self.headers:
            for i, header in enumerate(self.headers):
                if i < col_count:
                    col_widths[i] = max(col_widths[i], 
                                       UIFormatter.get_display_width(strip_colors(header)))
        
        # 考虑数据行宽度
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < col_count:
                    cell_width = UIFormatter.get_display_width(strip_colors(str(cell)))
                    col_widths[i] = max(col_widths[i], cell_width)
        
        # 添加最小内边距
        col_widths = [w + 2 for w in col_widths]  # 每侧1个空格
        
        # 如果总宽度超过限制，按比例缩小
        total_width = sum(col_widths) + (len(col_widths) + 1)  # 加上边框
        if total_width > self.width:
            # 计算可用内容宽度
            available_width = self.width - (len(col_widths) + 1) - (len(col_widths) * 2)
            total_content = sum(w - 2 for w in col_widths)
            
            if total_content > 0:
                # 按比例分配
                new_widths = []
                for w in col_widths:
                    content_w = w - 2
                    new_content_w = max(3, int(content_w * available_width / total_content))
                    new_widths.append(new_content_w + 2)
                col_widths = new_widths
        
        return col_widths
    
    def _render_cell(self, content: str, width: int, align: str = 'left') -> str:
        """
        渲染单元格
        
        Args:
            content: 单元格内容
            width: 单元格宽度
            align: 对齐方式
            
        Returns:
            格式化后的单元格字符串
        """
        content = str(content)
        content_width = UIFormatter.get_display_width(strip_colors(content))
        
        # 截断过长的内容
        if content_width > width - 2:
            content = UIFormatter.truncate(content, width - 2)
            content_width = UIFormatter.get_display_width(strip_colors(content))
        
        # 对齐
        if align == 'center':
            aligned = UIFormatter.align_center(content, width - 2)
        elif align == 'right':
            aligned = UIFormatter.align_right(content, width - 2)
        else:
            aligned = UIFormatter.align_left(content, width - 2)
        
        return f" {aligned} "
    
    def _render_separator(self, col_widths: List[int], 
                         left: str, mid: str, right: str) -> str:
        """
        渲染分隔线
        
        Args:
            col_widths: 列宽度列表
            left: 左边框字符
            mid: 中间连接字符
            right: 右边框字符
            
        Returns:
            分隔线字符串
        """
        parts = [colorize(left, self.border_color)]
        
        for i, width in enumerate(col_widths):
            parts.append(colorize(self.border['horizontal'] * width, self.border_color))
            if i < len(col_widths) - 1:
                parts.append(colorize(mid, self.border_color))
        
        parts.append(colorize(right, self.border_color))
        return ''.join(parts)
    
    def render(self) -> str:
        """
        渲染表格
        
        Returns:
            格式化后的表格字符串
        """
        if not self.headers and not self.rows:
            return ""
        
        col_widths = self._calculate_column_widths()
        lines = []
        
        # 顶部边框
        lines.append(self._render_separator(col_widths, 
                                           self.border['top_left'],
                                           self.border['top_t'],
                                           self.border['top_right']))
        
        # 表头
        if self.headers:
            header_cells = []
            for i, header in enumerate(self.headers):
                if i < len(col_widths):
                    cell = self._render_cell(header, col_widths[i], 'center')
                    # 应用表头颜色
                    colored_cell = colorize(cell, self.header_color)
                    header_cells.append(colored_cell)
            
            header_line = (colorize(self.border['vertical'], self.border_color) +
                          colorize(self.border['vertical'], self.border_color).join(header_cells) +
                          colorize(self.border['vertical'], self.border_color))
            lines.append(header_line)
            
            # 表头下方分隔线
            lines.append(self._render_separator(col_widths,
                                               self.border['left_t'],
                                               self.border['cross'],
                                               self.border['right_t']))
        
        # 数据行
        for row in self.rows:
            row_cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    rendered_cell = self._render_cell(cell, col_widths[i], 'left')
                    row_cells.append(rendered_cell)
            
            # 填充空单元格
            while len(row_cells) < len(col_widths):
                idx = len(row_cells)
                row_cells.append(self._render_cell('', col_widths[idx], 'left'))
            
            row_line = (colorize(self.border['vertical'], self.border_color) +
                       colorize(self.border['vertical'], self.border_color).join(row_cells) +
                       colorize(self.border['vertical'], self.border_color))
            lines.append(row_line)
        
        # 底部边框
        lines.append(self._render_separator(col_widths,
                                           self.border['bottom_left'],
                                           self.border['bottom_t'],
                                           self.border['bottom_right']))
        
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        return self.render()
    
    @classmethod
    def from_dict_list(cls,
                      data: List[Dict[str, Any]],
                      columns: Optional[List[str]] = None,
                      width: Optional[int] = None) -> 'UITable':
        """
        从字典列表创建表格
        
        Args:
            data: 字典列表
            columns: 要显示的列，None则显示所有列
            width: 表格宽度
            
        Returns:
            配置好的表格
        """
        if not data:
            return cls(width=width)
        
        # 确定列
        if columns is None:
            columns = list(data[0].keys())
        
        # 创建表头
        headers = [str(col) for col in columns]
        
        # 创建行
        rows = []
        for item in data:
            row = [str(item.get(col, '')) for col in columns]
            rows.append(row)
        
        return cls(headers=headers, rows=rows, width=width)
    
    @classmethod
    def simple_list(cls,
                   items: List[str],
                   title: Optional[str] = None,
                   width: int = 60,
                   numbered: bool = True) -> 'UITable':
        """
        创建简单列表表格
        
        Args:
            items: 项目列表
            title: 标题（可选）
            width: 表格宽度
            numbered: 是否显示序号
            
        Returns:
            配置好的列表表格
        """
        if numbered:
            headers = ['#', '项目']
            rows = [[str(i+1), item] for i, item in enumerate(items)]
        else:
            headers = ['项目']
            rows = [[item] for item in items]
        
        table = cls(headers=headers, rows=rows, width=width)
        return table
