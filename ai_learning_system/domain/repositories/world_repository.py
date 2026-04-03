from abc import ABC, abstractmethod
from domain.entities.world import World
from typing import List, Optional


class WorldRepository(ABC):
    """世界仓库接口"""
    
    @abstractmethod
    def save(self, world: World) -> None:
        """保存世界
        
        Args:
            world: 世界实体
        """
        pass
    
    @abstractmethod
    def find_by_id(self, world_id: str) -> Optional[World]:
        """根据ID查找世界
        
        Args:
            world_id: 世界ID
            
        Returns:
            世界实体，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[World]:
        """根据名称查找世界
        
        Args:
            name: 世界名称
            
        Returns:
            世界实体，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def update(self, world: World) -> None:
        """更新世界
        
        Args:
            world: 世界实体
        """
        pass
    
    @abstractmethod
    def delete(self, world_id: str) -> None:
        """删除世界
        
        Args:
            world_id: 世界ID
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[World]:
        """查找所有世界
        
        Returns:
            世界实体列表
        """
        pass
    
    @abstractmethod
    def save_all(self, worlds: List[World]) -> None:
        """保存所有世界
        
        Args:
            worlds: 世界实体列表
        """
        pass