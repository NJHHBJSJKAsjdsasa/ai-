"""
背包处理器类

处理与背包、物品使用、法宝装备相关的命令。
"""

from .base_handler import BaseHandler
from utils.colors import Color


class InventoryHandler(BaseHandler):
    """
    背包处理器
    
    处理背包查看、物品使用、法宝装备等功能。
    """
    
    def handle_inventory(self):
        """处理背包命令"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        print(f"\n{self.colorize('🎒 背包', Color.BOLD_CYAN)}")
        print(self.colorize("─" * 50, Color.BOLD_BLUE))
        print(self.player.get_inventory_info())
    
    def handle_use_item(self, item_name: str):
        """处理使用道具命令"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not item_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要使用的道具")
            print(f"  可用命令: /使用 <道具名>")
            return
        
        success, message = self.player.use_item(item_name)
        if success:
            print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} {message}")
    
    def handle_equip_treasure(self, treasure_name: str):
        """处理装备法宝命令"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not treasure_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要装备的法宝")
            print(f"  可用命令: /装备 <法宝名>")
            return
        
        success, message = self.player.equip_treasure(treasure_name)
        if success:
            print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} {message}")
