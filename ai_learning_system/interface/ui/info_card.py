"""
UI信息卡片组件

提供格式化的信息卡片显示，用于展示实体详情。
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import Color, colorize, strip_colors
from .theme import UITheme
from .formatter import UIFormatter
from .panel import UIPanel


class UIInfoCard:
    """
    UI信息卡片组件类
    
    提供格式化的键值对信息展示，支持分组和图标。
    """
    
    def __init__(self,
                 title: Optional[str] = None,
                 width: int = 60,
                 border_style: str = 'rounded',
                 border_color: str = None,
                 title_color: str = None):
        """
        初始化信息卡片
        
        Args:
            title: 卡片标题
            width: 卡片宽度
            border_style: 边框样式
            border_color: 边框颜色
            title_color: 标题颜色
        """
        self.title = title
        self.width = width
        self.border_style = border_style
        self.border_color = border_color or UITheme.BORDER_PRIMARY
        self.title_color = title_color or UITheme.TITLE_PRIMARY
        
        self.sections: List[Dict[str, Any]] = []
        self.key_value_pairs: List[Tuple[str, str, str]] = []  # (key, value, icon)
    
    def add_section(self, name: str, icon: str = ""):
        """
        添加分组
        
        Args:
            name: 分组名称
            icon: 分组图标
        """
        self.sections.append({
            'name': name,
            'icon': icon,
            'items': []
        })
    
    def add_item(self, key: str, value: Any, icon: str = "", section: int = -1):
        """
        添加键值对
        
        Args:
            key: 键名
            value: 值
            icon: 图标
            section: 所属分组索引，-1表示当前分组或无分组
        """
        value_str = str(value)
        
        if section >= 0 and section < len(self.sections):
            self.sections[section]['items'].append((key, value_str, icon))
        else:
            self.key_value_pairs.append((key, value_str, icon))
    
    def add_key_value(self, key: str, value: Any, icon: str = ""):
        """
        添加键值对（简化版）
        
        Args:
            key: 键名
            value: 值
            icon: 图标
        """
        self.add_item(key, value, icon)
    
    def _format_key_value(self, key: str, value: str, icon: str, 
                         max_key_width: int) -> str:
        """
        格式化键值对行
        
        Args:
            key: 键名
            value: 值
            icon: 图标
            max_key_width: 最大键名宽度
            
        Returns:
            格式化后的行
        """
        # 图标
        icon_str = f"{icon} " if icon else "  "
        
        # 键名（右对齐）
        key_colored = colorize(f"{key}:", UITheme.TEXT_DIM)
        key_padded = UIFormatter.align_right(key_colored, max_key_width)
        
        # 值
        value_colored = colorize(value, UITheme.TEXT_NORMAL)
        
        return f"{icon_str}{key_padded} {value_colored}"
    
    def render(self) -> str:
        """
        渲染信息卡片
        
        Returns:
            格式化后的卡片字符串
        """
        panel = UIPanel(
            title=self.title,
            width=self.width,
            border_style=self.border_style,
            border_color=self.border_color,
            title_color=self.title_color,
            padding=1
        )
        
        # 计算最大键名宽度
        all_keys = []
        for key, _, _ in self.key_value_pairs:
            all_keys.append(key)
        for section in self.sections:
            for key, _, _ in section['items']:
                all_keys.append(key)
        
        max_key_width = max((UIFormatter.get_display_width(k) for k in all_keys), default=0)
        max_key_width = min(max_key_width, self.width // 3)  # 限制最大宽度
        
        content_width = self.width - 4  # 减去边框和内边距
        
        # 渲染无分组的键值对
        if self.key_value_pairs:
            for key, value, icon in self.key_value_pairs:
                line = self._format_key_value(key, value, icon, max_key_width)
                panel.add_line(line)
        
        # 渲染分组
        for i, section in enumerate(self.sections):
            # 分组间隔
            if i > 0 or self.key_value_pairs:
                panel.add_empty_line()
            
            # 分组标题
            section_icon = section.get('icon', '')
            section_name = section.get('name', '')
            if section_name:
                section_title = f"{section_icon} {section_name}" if section_icon else section_name
                panel.add_line(colorize(section_title, UITheme.TITLE_SECONDARY))
                panel.add_separator('─')
            
            # 分组内容
            for key, value, icon in section['items']:
                line = self._format_key_value(key, value, icon, max_key_width)
                panel.add_line(line)
        
        return panel.render()
    
    def __str__(self) -> str:
        return self.render()
    
    @classmethod
    def from_dict(cls,
                 data: Dict[str, Any],
                 title: Optional[str] = None,
                 width: int = 60,
                 icon_map: Optional[Dict[str, str]] = None) -> 'UIInfoCard':
        """
        从字典创建信息卡片
        
        Args:
            data: 数据字典
            title: 卡片标题
            width: 卡片宽度
            icon_map: 键到图标的映射
            
        Returns:
            配置好的信息卡片
        """
        card = cls(title=title, width=width)
        icon_map = icon_map or {}
        
        for key, value in data.items():
            icon = icon_map.get(key, "")
            card.add_key_value(key, value, icon)
        
        return card
    
    @classmethod
    def player_status_card(cls,
                          player_data: Dict[str, Any],
                          width: int = 60) -> 'UIInfoCard':
        """
        创建玩家状态卡片
        
        Args:
            player_data: 玩家数据字典
            width: 卡片宽度
            
        Returns:
            配置好的玩家状态卡片
        """
        card = cls(title="📊 角色状态", width=width)
        
        # 基本信息分组
        card.add_section("基本信息", "👤")
        card.add_item("姓名", player_data.get('name', '未知'), "", 0)
        card.add_item("境界", player_data.get('realm', '未知'), "", 0)
        card.add_item("年龄", f"{player_data.get('age', 0)}岁", "", 0)
        card.add_item("寿命", f"{player_data.get('lifespan', 0)}年", "", 0)
        
        # 修为分组
        card.add_section("修为", "☯️")
        card.add_item("当前修为", player_data.get('exp', 0), "", 1)
        card.add_item("修为上限", player_data.get('max_exp', 0), "", 1)
        card.add_item("修炼速度", f"{player_data.get('cultivation_speed', 1.0)}倍", "", 1)
        
        # 属性分组
        card.add_section("属性", "⚔️")
        card.add_item("攻击力", player_data.get('attack', 0), "", 2)
        card.add_item("防御力", player_data.get('defense', 0), "", 2)
        card.add_item("速度", player_data.get('speed', 0), "", 2)
        
        # 其他分组
        card.add_section("其他", "📋")
        card.add_item("灵石", player_data.get('spirit_stones', 0), "💎", 3)
        card.add_item("气运", player_data.get('fortune', 0), "🍀", 3)
        card.add_item("因果", player_data.get('karma', 0), "☸️", 3)
        
        return card
    
    @classmethod
    def npc_info_card(cls,
                     npc_data: Dict[str, Any],
                     width: int = 60) -> 'UIInfoCard':
        """
        创建NPC信息卡片
        
        Args:
            npc_data: NPC数据字典
            width: 卡片宽度
            
        Returns:
            配置好的NPC信息卡片
        """
        name = npc_data.get('name', '未知')
        card = cls(title=f"👤 {name}", width=width)
        
        # 基本信息
        card.add_key_value("境界", npc_data.get('realm', '未知'), "☯️")
        card.add_key_value("门派", npc_data.get('sect', '散修'), "🏯")
        card.add_key_value("位置", npc_data.get('location', '未知'), "📍")
        
        # 关系
        relationship = npc_data.get('relationship', 0)
        rel_icon = "❤️" if relationship > 50 else "😐" if relationship > -50 else "💢"
        card.add_key_value("关系值", relationship, rel_icon)
        
        # 状态
        status = npc_data.get('status', '正常')
        status_icon = "😊" if status == '正常' else "😴" if status == '休息' else "⚔️"
        card.add_key_value("状态", status, status_icon)
        
        return card
    
    @classmethod
    def item_card(cls,
                 item_data: Dict[str, Any],
                 width: int = 50) -> 'UIInfoCard':
        """
        创建物品信息卡片
        
        Args:
            item_data: 物品数据字典
            width: 卡片宽度
            
        Returns:
            配置好的物品信息卡片
        """
        name = item_data.get('name', '未知物品')
        rarity = item_data.get('rarity', '普通')
        
        # 根据稀有度确定颜色
        rarity_colors = {
            '普通': UITheme.TEXT_DIM,
            '稀有': Color.GREEN,
            '史诗': Color.MAGENTA,
            '传说': Color.YELLOW,
            '神话': Color.RED,
        }
        rarity_color = rarity_colors.get(rarity, UITheme.TEXT_DIM)
        
        card = cls(title=f"📦 {name}", width=width)
        
        card.add_key_value("类型", item_data.get('type', '未知'), "🏷️")
        card.add_key_value("稀有度", colorize(rarity, rarity_color), "⭐")
        card.add_key_value("数量", item_data.get('quantity', 1), "🔢")
        
        description = item_data.get('description', '')
        if description:
            card.add_empty_line()
            card.add_line(colorize(description, UITheme.TEXT_DIM))
        
        return card
