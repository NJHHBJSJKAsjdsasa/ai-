"""
GUI 面板模块
"""

from .base_panel import BasePanel
from .status_panel import StatusPanel
from .map_panel import MapPanel
from .npc_panel import NPCPanel
from .inventory_panel import InventoryPanel
from .technique_panel import TechniquePanel
from .combat_panel import CombatPanel
from .quest_panel import QuestPanel

__all__ = [
    'BasePanel',
    'StatusPanel',
    'MapPanel',
    'NPCPanel',
    'InventoryPanel',
    'TechniquePanel',
    'CombatPanel',
    'QuestPanel',
]
