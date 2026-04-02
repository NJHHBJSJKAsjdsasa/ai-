"""
修仙游戏配置模块
包含提示词配置、术语映射、境界配置等
"""

from .xiuxian_terms import modern_to_xiuxian, xiuxian_to_modern, XIUXIAN_TERMS, get_phrase, XIUXIAN_PHRASES
from .cultivation_realms import (
    REALMS, REALM_NAME_TO_LEVEL, get_realm_info, get_realm_title, get_realm_icon,
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
    get_all_techniques, TechniqueLearningRecord, get_technique_combos, calculate_combo_bonuses
)
from .items import (
    Item, ItemType, ItemRarity, ITEMS_DB,
    get_item, get_items_by_type, get_items_by_rarity,
    get_items_by_level, search_items, get_all_items,
    calculate_item_value, Inventory
)
from .enemies import (
    Beast, BeastType, BEASTS_DB,
    get_beast, get_beasts_by_realm, get_beasts_by_type,
    generate_beast_by_realm, generate_beast_loot,
    calculate_beast_power, get_beast_difficulty_rating
)
from .quest_config import (
    QuestType, ObjectiveType, QuestReward, QuestTemplate,
    MAIN_QUESTS, SIDE_QUEST_TEMPLATES, DAILY_QUEST_TEMPLATES,
    DAILY_QUEST_COUNT, get_main_quest_by_id, get_next_main_quest,
    get_available_main_quests, get_main_quest_chapter, get_chapter_name
)
from .tribulation_config import (
    TribulationType, TribulationStatus, ThunderType, ThunderStrike,
    TribulationStage, TribulationReward, PreparationItem,
    TRIBULATION_STAGES, TRIBULATION_REWARDS, TRIBULATION_PREPARATION_ITEMS,
    get_tribulation_stage, get_all_tribulation_stages, generate_thunder_sequence,
    get_preparation_items, calculate_tribulation_success_rate,
    generate_tribulation_rewards, get_tribulation_type_by_karma,
    calculate_failure_penalty
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
    'REALM_NAME_TO_LEVEL',
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
    'get_technique_combos',
    'calculate_combo_bonuses',
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
    # 妖兽系统
    'Beast',
    'BeastType',
    'BEASTS_DB',
    'get_beast',
    'get_beasts_by_realm',
    'get_beasts_by_type',
    'generate_beast_by_realm',
    'generate_beast_loot',
    'calculate_beast_power',
    'get_beast_difficulty_rating',
    # 任务系统
    'QuestType',
    'ObjectiveType',
    'QuestReward',
    'QuestTemplate',
    'MAIN_QUESTS',
    'SIDE_QUEST_TEMPLATES',
    'DAILY_QUEST_TEMPLATES',
    'DAILY_QUEST_COUNT',
    'get_main_quest_by_id',
    'get_next_main_quest',
    'get_available_main_quests',
    'get_main_quest_chapter',
    'get_chapter_name',
    # 天劫系统
    'TribulationType',
    'TribulationStatus',
    'ThunderType',
    'ThunderStrike',
    'TribulationStage',
    'TribulationReward',
    'PreparationItem',
    'TRIBULATION_STAGES',
    'TRIBULATION_REWARDS',
    'TRIBULATION_PREPARATION_ITEMS',
    'get_tribulation_stage',
    'get_all_tribulation_stages',
    'generate_thunder_sequence',
    'get_preparation_items',
    'calculate_tribulation_success_rate',
    'generate_tribulation_rewards',
    'get_tribulation_type_by_karma',
    'calculate_failure_penalty',
]
