"""
NPC系统模块 - 向后兼容重定向文件
管理NPC生成、记忆、交互等
集成NPC独立系统

注意：此文件仅为向后兼容保留，请使用新的模块化导入方式：
- from game.npc import NPC, NPCManager, NPCMemory, NPCData
- from game.npc.models import NPCMemory, NPCData
- from game.npc.core import NPC
- from game.npc.manager import NPCManager
"""

# 从新的模块化结构重新导出所有公共接口
from .npc.models import NPCMemory, NPCData
from .npc.core import NPC
from .npc.manager import NPCManager

__all__ = ['NPCMemory', 'NPCData', 'NPC', 'NPCManager']
