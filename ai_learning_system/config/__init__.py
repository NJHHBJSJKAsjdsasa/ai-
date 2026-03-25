"""
修仙游戏配置模块
包含提示词配置、术语映射、境界配置等
"""

from .xiuxian_terms import modern_to_xiuxian, xiuxian_to_modern, XIUXIAN_TERMS, get_phrase, XIUXIAN_PHRASES
from .cultivation_realms import (
    REALMS, get_realm_info, get_realm_title, get_realm_icon,
    get_breakthrough_success_rate, can_breakthrough, get_realm_progress
)
from .prompts import (
    get_system_prompt, get_npc_prompt, XIUXIAN_PROMPTS, 
    PERSONALITIES, SECTS, SECT_DETAILS, SECT_RELATIONSHIPS,
    DAO_NAME_PREFIX, DAO_NAME_SUFFIX, FANREN_CHARACTERS
)
from .game_config import GAME_CONFIG, SPIRIT_ROOTS, generate_spirit_root, get_spirit_root_info, calculate_cultivation_speed
from .techniques import (
    Technique, TechniqueType, ElementType, TECHNIQUES_DB,
    get_technique, get_techniques_by_realm, get_techniques_by_element,
    get_techniques_by_type, can_learn_technique, calculate_learning_success_rate,
    get_all_techniques, TechniqueLearningRecord
)
from .items import (
    Item, ItemType, ItemRarity, ITEMS_DB,
    get_item, get_items_by_type, get_items_by_rarity,
    get_items_by_level, search_items, get_all_items,
    calculate_item_value, Inventory
)

__all__ = [
    # 术语和短语
    'modern_to_xiuxian',
    'xiuxian_to_modern',
    'XIUXIAN_TERMS',
    'get_phrase',
    'XIUXIAN_PHRASES',
    # 境界
    'REALMS',
    'get_realm_info',
    'get_realm_title',
    'get_realm_icon',
    'get_breakthrough_success_rate',
    'can_breakthrough',
    'get_realm_progress',
    # 提示词和门派
    'get_system_prompt',
    'get_npc_prompt',
    'XIUXIAN_PROMPTS',
    'PERSONALITIES',
    'SECTS',
    'SECT_DETAILS',
    'SECT_RELATIONSHIPS',
    'DAO_NAME_PREFIX',
    'DAO_NAME_SUFFIX',
    'FANREN_CHARACTERS',
    # 游戏配置
    'GAME_CONFIG',
    'SPIRIT_ROOTS',
    'generate_spirit_root',
    'get_spirit_root_info',
    'calculate_cultivation_speed',
    # 功法系统
    'Technique',
    'TechniqueType',
    'ElementType',
    'TECHNIQUES_DB',
    'get_technique',
    'get_techniques_by_realm',
    'get_techniques_by_element',
    'get_techniques_by_type',
    'can_learn_technique',
    'calculate_learning_success_rate',
    'get_all_techniques',
    'TechniqueLearningRecord',
    # 道具系统
    'Item',
    'ItemType',
    'ItemRarity',
    'ITEMS_DB',
    'get_item',
    'get_items_by_type',
    'get_items_by_rarity',
    'get_items_by_level',
    'search_items',
    'get_all_items',
    'calculate_item_value',
    'Inventory',
]
