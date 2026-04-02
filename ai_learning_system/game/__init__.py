"""
修仙游戏核心模块
包含玩家系统、修炼系统、NPC系统、世界系统等
"""

from .player import Player
from .cultivation import CultivationSystem
from .npc import NPC, NPCManager
from .world import World, GameTime
from .events import EventSystem
from .ai_judge import AIJudgeSystem, JudgeResult, ReplyCategory, judge_ai_reply
from .time_system import RealTimeSystem, GameTime as RealGameTime, get_time_system
from .npc_life import NPCLifeSystem, NPCActivity, NPCGoal, ActivityType, GoalType
from .world_evolution import WorldEvolution, WorldEvent, Faction, EventType
from .response_filter import ResponseFilter, filter_ai_response, check_xiuxian_keywords
from .generator import (
    InfiniteGenerator, GeneratedMap, GeneratedNPC, GeneratedItem, GeneratedMonster,
    MapType, NPCOccupation, NPCPersonality, ItemType, ItemRarity, MonsterType,
    generate_map, generate_npc, generate_item, generate_monster, get_generator
)
from .exploration_manager import ExplorationManager, ExplorationResult, explore, get_exploration_manager

__all__ = [
    'Player',
    'CultivationSystem',
    'NPC',
    'NPCManager',
    'World',
    'GameTime',
    'EventSystem',
    'AIJudgeSystem',
    'JudgeResult',
    'ReplyCategory',
    'judge_ai_reply',
    'RealTimeSystem',
    'RealGameTime',
    'get_time_system',
    'NPCLifeSystem',
    'NPCActivity',
    'NPCGoal',
    'ActivityType',
    'GoalType',
    'WorldEvolution',
    'WorldEvent',
    'Faction',
    'EventType',
    'ResponseFilter',
    'filter_ai_response',
    'check_xiuxian_keywords',
    # 无限生成系统
    'InfiniteGenerator',
    'GeneratedMap',
    'GeneratedNPC',
    'GeneratedItem',
    'GeneratedMonster',
    'MapType',
    'NPCOccupation',
    'NPCPersonality',
    'ItemType',
    'ItemRarity',
    'MonsterType',
    'generate_map',
    'generate_npc',
    'generate_item',
    'generate_monster',
    'get_generator',
    # 探索管理器
    'ExplorationManager',
    'ExplorationResult',
    'explore',
    'get_exploration_manager',
]
