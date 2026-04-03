from abc import ABC, abstractmethod
from domain.entities.npc import NPC
from typing import List, Optional


class NPCRepository(ABC):
    """NPC仓库接口"""
    
    @abstractmethod
    def save(self, npc: NPC) -> None:
        """保存NPC
        
        Args:
            npc: NPC实体
        """
        pass
    
    @abstractmethod
    def find_by_id(self, npc_id: str) -> Optional[NPC]:
        """根据ID查找NPC
        
        Args:
            npc_id: NPC ID
            
        Returns:
            NPC实体，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def find_by_location(self, location: str) -> List[NPC]:
        """根据位置查找NPC
        
        Args:
            location: 位置名称
            
        Returns:
            NPC实体列表
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[NPC]:
        """根据名称查找NPC
        
        Args:
            name: NPC名称
            
        Returns:
            NPC实体，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def update(self, npc: NPC) -> None:
        """更新NPC
        
        Args:
            npc: NPC实体
        """
        pass
    
    @abstractmethod
    def delete(self, npc_id: str) -> None:
        """删除NPC
        
        Args:
            npc_id: NPC ID
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[NPC]:
        """查找所有NPC
        
        Returns:
            NPC实体列表
        """
        pass
    
    @abstractmethod
    def save_all(self, npcs: List[NPC]) -> None:
        """保存所有NPC
        
        Args:
            npcs: NPC实体列表
        """
        pass
    
    @abstractmethod
    def find_alive(self) -> List[NPC]:
        """查找所有存活的NPC
        
        Returns:
            存活的NPC实体列表
        """
        pass
    
    @abstractmethod
    def find_dead(self) -> List[NPC]:
        """查找所有死亡的NPC
        
        Returns:
            死亡的NPC实体列表
        """
        pass