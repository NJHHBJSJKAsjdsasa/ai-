"""
CLI 命令处理器模块

将 CLI 的功能拆分为多个独立的处理器模块，每个模块负责特定功能领域。
"""

from .base_handler import BaseHandler
from .cultivation_handler import CultivationHandler
from .npc_handler import NPCHandler
from .inventory_handler import InventoryHandler
from .map_handler import MapHandler
from .technique_handler import TechniqueHandler
from .exploration_handler import ExplorationHandler
from .character_handler import CharacterHandler
from .admin_handler import AdminHandler
from .combat_handler import CombatHandler

__all__ = [
    'BaseHandler',
    'CultivationHandler',
    'NPCHandler',
    'InventoryHandler',
    'MapHandler',
    'TechniqueHandler',
    'ExplorationHandler',
    'CharacterHandler',
    'AdminHandler',
    'CombatHandler',
]
