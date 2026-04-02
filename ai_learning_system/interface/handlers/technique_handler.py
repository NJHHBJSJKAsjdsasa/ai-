"""
功法处理器类

处理与功法相关的命令，包括查看已学功法、学习新功法和查看可学功法。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI

from .base_handler import BaseHandler
from utils.colors import Color, colorize


class TechniqueHandler(BaseHandler):
    """
    功法处理器类
    
    处理所有与功法相关的命令：
    - /功法 - 查看已学功法
    - /学习 <功法名> - 学习新功法
    - /可学功法 - 查看当前可学习的功法
    """
    
    def __init__(self, cli: 'CLI'):
        """
        初始化功法处理器
        
        Args:
            cli: CLI 实例
        """
        super().__init__(cli)
    
    def handle_techniques(self):
        """处理功法命令 - 查看已学功法"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        techniques = self.player.get_learned_techniques()
        
        if not techniques:
            print(f"\n{self.colorize('📖', Color.BOLD_CYAN)} 你还没有学习任何功法")
            print(f"  使用 /学习 <功法名> 学习功法")
            return
        
        print(f"\n{self.colorize('📖 已学功法', Color.BOLD_CYAN)}")
        print(self.colorize("─" * 50, Color.BOLD_BLUE))
        
        from config import get_technique
        for tech_name, tech_data in techniques.items():
            technique = get_technique(tech_name)
            if technique:
                level = tech_data.get("level", 1)
                print(f"  {technique.name} (Lv.{level}) - {technique.description[:30]}...")
    
    def handle_learn_technique(self, technique_name: str):
        """
        处理学习功法命令
        
        Args:
            technique_name: 要学习的功法名称
        """
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not technique_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要学习的功法")
            print(f"  可用命令: /学习 <功法名>")
            return
        
        success, message = self.player.learn_technique(technique_name)
        if success:
            print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} {message}")
    
    def handle_available_techniques(self):
        """处理可学功法命令 - 查看当前可学习的功法"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        from config import get_techniques_by_realm, can_learn_technique
        
        available = get_techniques_by_realm(self.player.stats.realm_level)
        learned = self.player.get_learned_techniques()
        
        print(f"\n{self.colorize('📚 可学功法', Color.BOLD_CYAN)} (当前境界: {self.player.get_realm_name()})")
        print(self.colorize("─" * 50, Color.BOLD_BLUE))
        
        for technique in available:
            if technique.name not in learned:
                can_learn = can_learn_technique(
                    technique.name, 
                    self.player.stats.realm_level,
                    self.player.stats.spirit_root
                )
                status = "✅" if can_learn else "❌"
                print(f"  {status} {technique.name} - {technique.description[:25]}...")
