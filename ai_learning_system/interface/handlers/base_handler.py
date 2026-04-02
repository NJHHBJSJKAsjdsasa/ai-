"""
基础处理器类

所有 CLI 命令处理器的基类，提供公共功能和接口。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI


class BaseHandler:
    """
    基础处理器类
    
    所有 CLI 命令处理器的基类，提供对 CLI 实例的访问和公共工具方法。
    """
    
    def __init__(self, cli: 'CLI'):
        """
        初始化处理器
        
        Args:
            cli: CLI 实例，用于访问玩家、世界等游戏状态
        """
        self.cli = cli
    
    @property
    def player(self):
        """获取当前玩家"""
        return self.cli.player
    
    @property
    def world(self):
        """获取游戏世界"""
        return self.cli.world
    
    @property
    def cultivation_system(self):
        """获取修炼系统"""
        return self.cli.cultivation_system
    
    @property
    def npc_manager(self):
        """获取NPC管理器"""
        return self.cli.npc_manager
    
    @property
    def exploration_manager(self):
        """获取探索管理器"""
        return self.cli.exploration_manager
    
    @property
    def logger(self):
        """获取日志记录器"""
        return self.cli.logger
    
    def save_player(self) -> bool:
        """
        保存玩家数据
        
        Returns:
            是否保存成功
        """
        return self.cli.save_player()
    
    def print(self, message: str):
        """
        打印消息
        
        Args:
            message: 要打印的消息
        """
        print(message)
    
    def colorize(self, text: str, color) -> str:
        """
        为文本添加颜色
        
        Args:
            text: 要着色的文本
            color: 颜色代码
            
        Returns:
            着色后的文本
        """
        from utils.colors import colorize as cz
        return cz(text, color)
