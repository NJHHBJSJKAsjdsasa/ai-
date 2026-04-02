"""
角色管理处理器

处理角色相关的命令，包括新建、加载和列出角色。
"""

from typing import TYPE_CHECKING

from .base_handler import BaseHandler
from utils.colors import Color

if TYPE_CHECKING:
    from ..cli import CLI


class CharacterHandler(BaseHandler):
    """
    角色管理处理器
    
    处理角色相关的命令，包括新建、加载和列出角色。
    """
    
    def __init__(self, cli: 'CLI'):
        """
        初始化角色管理处理器
        
        Args:
            cli: CLI 实例
        """
        super().__init__(cli)
    
    def handle_new_character(self):
        """处理新建角色命令"""
        # 保存当前角色
        if self.player and self.cli.game_mode:
            if self.save_player():
                print(f"\n{self.colorize('💾', Color.BOLD_CYAN)} 已保存当前角色：{self.player.stats.name}")
        
        # 创建新角色
        print(f"\n{self.colorize('🎮', Color.BOLD_GREEN)} 创建新角色！")
        
        # 输入角色名称
        name = input(f"{self.colorize('请输入角色名称:', Color.BOLD_CYAN)} ").strip()
        if not name:
            name = "道友"
        
        # 创建新玩家
        from game import Player, CultivationSystem
        self.cli.player = Player(name=name, load_from_db=False)
        
        # 重新初始化游戏系统
        self.cli.cultivation_system = CultivationSystem(self.player)
        
        print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 新角色创建成功！")
        print(f"  名称: {self.player.stats.name}")
        print(f"  灵根: {self.player.stats.spirit_root}")
        print(f"  寿元: {self.player.stats.lifespan}年")
    
    def handle_load_character(self, character_name: str):
        """处理加载角色命令"""
        if not character_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要加载的角色名称")
            print(f"  可用命令: /加载 <角色名>")
            print(f"  使用 /角色列表 查看所有角色")
            return
        
        # 保存当前角色
        if self.player and self.cli.game_mode:
            if self.save_player():
                print(f"\n{self.colorize('💾', Color.BOLD_CYAN)} 已保存当前角色")
        
        # 加载指定角色
        try:
            from storage.database import Database
            from game import Player, CultivationSystem
            
            db = Database()
            data = db.load_player(character_name)
            db.close()
            
            if data:
                self.cli.player = Player(name="道友", load_from_db=False)
                self.player.from_dict(data)
                self.cli.cultivation_system = CultivationSystem(self.player)
                
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 成功加载角色：{self.player.stats.name}")
                print(f"  当前境界: {self.player.get_realm_name()}")
                print(f"  当前年龄: {self.player.stats.age}岁")
            else:
                print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 未找到角色：{character_name}")
                print(f"  使用 /角色列表 查看所有角色")
                
        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 加载角色失败：{e}")
    
    def handle_list_characters(self):
        """处理角色列表命令"""
        try:
            from storage.database import Database
            
            db = Database()
            players = db.list_players()
            db.close()
            
            if not players:
                print(f"\n{self.colorize('📋', Color.BOLD_CYAN)} 暂无角色")
                print(f"  使用 /新建角色 创建新角色")
                return
            
            print(f"\n{self.colorize('📋 角色列表', Color.BOLD_CYAN)}")
            print(self.colorize("─" * 50, Color.BOLD_BLUE))
            
            for i, p in enumerate(players, 1):
                current = " 👈 当前" if self.player and p['name'] == self.player.stats.name else ""
                print(f"  {i}. {p['name']}{current}")
                print(f"     创建时间: {p['created_at'][:10]}")
                print(f"     最后更新: {p['updated_at'][:10]}")
            
            print(self.colorize("─" * 50, Color.BOLD_BLUE))
            print(f"{self.colorize('💡', Color.BOLD_YELLOW)} 使用 /加载 <角色名> 切换角色")
            
        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 获取角色列表失败：{e}")
