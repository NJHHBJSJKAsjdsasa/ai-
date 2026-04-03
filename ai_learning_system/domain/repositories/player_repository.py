from abc import ABC, abstractmethod
from domain.entities.player import Player

class PlayerRepository(ABC):
    """玩家仓库接口"""
    
    @abstractmethod
    def save(self, player: Player) -> None:
        """保存玩家
        
        Args:
            player: 玩家实体
        """
        pass
    
    @abstractmethod
    def find_by_id(self, player_id: str) -> Player:
        """根据ID查找玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            玩家实体，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def update(self, player: Player) -> None:
        """更新玩家
        
        Args:
            player: 玩家实体
        """
        pass
    
    @abstractmethod
    def delete(self, player_id: str) -> None:
        """删除玩家
        
        Args:
            player_id: 玩家ID
        """
        pass
    
    @abstractmethod
    def find_all(self) -> list[Player]:
        """查找所有玩家
        
        Returns:
            玩家实体列表
        """
        pass
    
    @abstractmethod
    def save_all(self, players: list[Player]) -> None:
        """保存所有玩家
        
        Args:
            players: 玩家实体列表
        """
        pass
