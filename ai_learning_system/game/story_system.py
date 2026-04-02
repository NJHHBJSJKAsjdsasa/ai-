"""
剧情系统模块
管理剧情流程、选择、回放等功能
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from config.story_config import (
    StoryChapter, StoryScene, StoryDialogue, StoryChoice,
    MAIN_STORY_CHAPTERS, SIDE_STORY_CHAPTERS, STORY_TRIGGERS,
    get_chapter_by_id, get_available_chapters, generate_random_side_story
)


@dataclass
class StoryState:
    """剧情状态数据类"""
    chapter_id: str
    current_scene_id: Optional[str] = None
    completed_scenes: List[str] = field(default_factory=list)
    choices_made: List[str] = field(default_factory=list)
    status: str = "active"  # active, completed, locked
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    replay_count: int = 0


@dataclass
class ChoiceEffect:
    """选择效果数据类"""
    effect_type: str
    target: Optional[str] = None
    value: Any = None
    is_applied: bool = False


class StoryManager:
    """剧情管理器"""
    
    def __init__(self, player_id: str, db: Database = None):
        """
        初始化剧情管理器
        
        Args:
            player_id: 玩家ID
            db: 数据库实例
        """
        self.player_id = player_id
        self.db = db or Database()
        self.active_story: Optional[StoryChapter] = None
        self.current_state: Optional[StoryState] = None
        self.current_scene: Optional[StoryScene] = None
        self.dialogue_index: int = 0
        
        # 初始化数据库表
        self.db.init_story_tables()
        
        # 加载配置到数据库
        self._init_story_data()
    
    def _init_story_data(self):
        """初始化剧情数据到数据库"""
        # 保存主线剧情
        for chapter in MAIN_STORY_CHAPTERS:
            self._save_chapter_to_db(chapter)
        
        # 保存支线剧情
        for chapter in SIDE_STORY_CHAPTERS:
            self._save_chapter_to_db(chapter)
    
    def _save_chapter_to_db(self, chapter: StoryChapter):
        """将剧情章节保存到数据库"""
        # 保存章节
        chapter_data = {
            'id': chapter.id,
            'chapter_number': chapter.chapter_number,
            'title': chapter.title,
            'description': chapter.description,
            'story_type': chapter.story_type,
            'realm_required': chapter.realm_required,
            'location_required': chapter.location_required,
            'pre_chapter_id': chapter.pre_chapter_id,
            'is_repeatable': chapter.is_repeatable
        }
        self.db.save_story_chapter(chapter_data)
        
        # 保存场景
        for scene in chapter.scenes:
            scene_data = {
                'id': scene.id,
                'chapter_id': chapter.id,
                'scene_number': scene.scene_number,
                'title': scene.title,
                'background': scene.background,
                'location': scene.location,
                'npcs': scene.npcs
            }
            self.db.save_story_scene(scene_data)
            
            # 保存对话
            for dialogue in scene.dialogues:
                dialogue_data = {
                    'id': dialogue.id,
                    'scene_id': scene.id,
                    'dialogue_order': dialogue.dialogue_order if hasattr(dialogue, 'dialogue_order') else 0,
                    'speaker_type': dialogue.speaker_type,
                    'speaker_id': dialogue.speaker_id,
                    'speaker_name': dialogue.speaker_name,
                    'content': dialogue.content,
                    'emotion': dialogue.emotion,
                    'animation': dialogue.animation
                }
                self.db.save_story_dialogue(dialogue_data)
            
            # 保存选择
            for i, choice in enumerate(scene.choices):
                choice_data = {
                    'id': choice.id,
                    'scene_id': scene.id,
                    'choice_order': i + 1,
                    'choice_text': choice.text,
                    'next_scene_id': choice.next_scene_id,
                    'effects': choice.effects,
                    'condition_type': choice.condition_type,
                    'condition_value': choice.condition_value
                }
                self.db.save_story_choice(choice_data)
        
        # 保存奖励
        for reward in chapter.rewards:
            reward_data = {
                'id': f"{chapter.id}_reward_{random.randint(1000, 9999)}",
                'chapter_id': chapter.id,
                'reward_type': reward.get('type', 'item'),
                'reward_item': reward.get('item', ''),
                'quantity': reward.get('quantity', 1),
                'condition_type': reward.get('condition', 'complete'),
                'condition_value': ''
            }
            self.db.save_story_reward(reward_data)
    
    def get_available_stories(self, realm_level: int, location: str) -> List[Dict[str, Any]]:
        """
        获取可用的剧情列表
        
        Args:
            realm_level: 当前境界等级
            location: 当前位置
            
        Returns:
            可用剧情列表
        """
        # 获取已完成的章节
        completed = self.db.get_player_completed_stories(self.player_id)
        completed_ids = [c['chapter_id'] for c in completed]
        
        # 从数据库获取可用章节
        available_chapters = []
        
        # 获取主线剧情
        main_chapters = self.db.get_story_chapters_by_type('main', realm_level)
        for chapter in main_chapters:
            if chapter['id'] not in completed_ids or chapter['is_repeatable']:
                # 检查前置条件
                if chapter['pre_chapter_id'] and chapter['pre_chapter_id'] not in completed_ids:
                    continue
                # 检查位置
                if chapter['location_required'] and chapter['location_required'] != location:
                    continue
                available_chapters.append(chapter)
        
        # 获取支线剧情
        side_chapters = self.db.get_story_chapters_by_type('side', realm_level)
        for chapter in side_chapters:
            if chapter['id'] not in completed_ids or chapter['is_repeatable']:
                if chapter['location_required'] and chapter['location_required'] != location:
                    continue
                available_chapters.append(chapter)
        
        return available_chapters
    
    def start_story(self, chapter_id: str) -> Tuple[bool, str]:
        """
        开始一个剧情
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取章节数据
        chapter_data = self.db.get_story_chapter(chapter_id)
        if not chapter_data:
            return False, "剧情不存在"
        
        # 检查是否已有进行中的剧情
        existing_record = self.db.get_player_story_record(self.player_id, chapter_id)
        if existing_record and existing_record['status'] == 'active':
            # 恢复进行中的剧情
            self._load_story_state(chapter_id, existing_record)
            return True, "恢复剧情进度"
        
        # 检查是否已完成且不可重复
        if existing_record and existing_record['status'] == 'completed' and not chapter_data['is_repeatable']:
            return False, "该剧情已完成且不可重复"
        
        # 创建新的剧情记录
        if not existing_record:
            self.db.create_player_story_record(self.player_id, chapter_id)
        else:
            # 重置剧情用于回放
            self.db.replay_player_story(self.player_id, chapter_id)
        
        # 加载剧情
        self._load_story_state(chapter_id)
        
        return True, f"开始剧情：{chapter_data['title']}"
    
    def _load_story_state(self, chapter_id: str, record: Dict = None):
        """加载剧情状态"""
        if record is None:
            record = self.db.get_player_story_record(self.player_id, chapter_id)
        
        self.current_state = StoryState(
            chapter_id=chapter_id,
            current_scene_id=record.get('current_scene_id'),
            completed_scenes=record.get('completed_scenes', []),
            choices_made=record.get('choices_made', []),
            status=record.get('status', 'active'),
            started_at=record.get('started_at'),
            completed_at=record.get('completed_at'),
            replay_count=record.get('replay_count', 0)
        )
        
        # 加载章节数据
        chapter_data = self.db.get_story_chapter(chapter_id)
        if chapter_data:
            self.active_story = self._build_chapter_from_db(chapter_id)
            
            # 确定当前场景
            if self.current_state.current_scene_id:
                self.current_scene = self._get_scene_by_id(self.current_state.current_scene_id)
            else:
                # 从第一个场景开始
                scenes = self.db.get_story_scenes(chapter_id)
                if scenes:
                    self.current_scene = self._build_scene_from_db(scenes[0]['id'])
                    self.current_state.current_scene_id = self.current_scene.id
            
            self.dialogue_index = 0
    
    def _build_chapter_from_db(self, chapter_id: str) -> StoryChapter:
        """从数据库构建章节对象"""
        chapter_data = self.db.get_story_chapter(chapter_id)
        if not chapter_data:
            return None
        
        return StoryChapter(
            id=chapter_data['id'],
            chapter_number=chapter_data['chapter_number'],
            title=chapter_data['title'],
            description=chapter_data['description'],
            story_type=chapter_data['story_type'],
            realm_required=chapter_data['realm_required'],
            location_required=chapter_data['location_required'],
            pre_chapter_id=chapter_data['pre_chapter_id'],
            is_repeatable=chapter_data['is_repeatable']
        )
    
    def _build_scene_from_db(self, scene_id: str) -> StoryScene:
        """从数据库构建场景对象"""
        # 获取场景数据
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_scenes WHERE id = ?", (scene_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # 获取对话
        dialogues = self.db.get_scene_dialogues(scene_id)
        dialogue_objects = [
            StoryDialogue(
                id=d['id'],
                speaker_type=d['speaker_type'],
                speaker_id=d['speaker_id'],
                speaker_name=d['speaker_name'],
                content=d['content'],
                emotion=d['emotion'],
                animation=d['animation']
            )
            for d in dialogues
        ]
        
        # 获取选择
        choices = self.db.get_scene_choices(scene_id)
        choice_objects = [
            StoryChoice(
                id=c['id'],
                text=c['choice_text'],
                next_scene_id=c['next_scene_id'],
                effects=c['effects'],
                condition_type=c['condition_type'],
                condition_value=c['condition_value']
            )
            for c in choices
        ]
        
        return StoryScene(
            id=row['id'],
            scene_number=row['scene_number'],
            title=row['title'],
            background=row['background'],
            location=row['location'],
            npcs=row['npcs'] if row['npcs'] else [],
            dialogues=dialogue_objects,
            choices=choice_objects
        )
    
    def _get_scene_by_id(self, scene_id: str) -> Optional[StoryScene]:
        """根据ID获取场景"""
        return self._build_scene_from_db(scene_id)
    
    def get_current_dialogue(self) -> Optional[Dict[str, Any]]:
        """
        获取当前对话
        
        Returns:
            对话数据，如果没有则返回None
        """
        if not self.current_scene:
            return None
        
        dialogues = self.current_scene.dialogues
        if self.dialogue_index < len(dialogues):
            dialogue = dialogues[self.dialogue_index]
            return {
                'id': dialogue.id,
                'speaker_type': dialogue.speaker_type,
                'speaker_name': dialogue.speaker_name,
                'content': dialogue.content,
                'emotion': dialogue.emotion,
                'animation': dialogue.animation,
                'is_last': self.dialogue_index == len(dialogues) - 1
            }
        return None
    
    def advance_dialogue(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        推进到下一段对话
        
        Returns:
            (是否有下一段, 对话数据)
        """
        self.dialogue_index += 1
        dialogue = self.get_current_dialogue()
        
        if dialogue:
            return True, dialogue
        else:
            # 对话结束，显示选择
            return False, None
    
    def get_current_choices(self) -> List[Dict[str, Any]]:
        """
        获取当前场景的选择选项
        
        Returns:
            选择列表
        """
        if not self.current_scene:
            return []
        
        choices = []
        for choice in self.current_scene.choices:
            choice_data = {
                'id': choice.id,
                'text': choice.text,
                'effects': choice.effects,
                'has_condition': choice.condition_type is not None
            }
            choices.append(choice_data)
        
        return choices
    
    def make_choice(self, choice_id: str) -> Tuple[bool, str, List[ChoiceEffect]]:
        """
        做出选择
        
        Args:
            choice_id: 选择ID
            
        Returns:
            (是否成功, 消息, 效果列表)
        """
        if not self.current_scene:
            return False, "没有进行中的剧情", []
        
        # 找到选择
        choice = None
        for c in self.current_scene.choices:
            if c.id == choice_id:
                choice = c
                break
        
        if not choice:
            return False, "无效的选择", []
        
        # 记录选择
        self.db.record_player_choice(self.player_id, self.current_state.chapter_id, choice_id)
        self.current_state.choices_made.append(choice_id)
        
        # 处理效果
        effects = self._process_choice_effects(choice.effects)
        
        # 保存选择效果到数据库
        for effect in effects:
            self.db.save_choice_effect(
                self.player_id,
                self.current_state.chapter_id,
                choice_id,
                effect.effect_type,
                effect.target,
                str(effect.value)
            )
        
        # 检查是否有下一场景
        if choice.next_scene_id:
            # 保存当前场景进度
            self.db.update_player_story_progress(
                self.player_id,
                self.current_state.chapter_id,
                self.current_scene.id
            )
            
            # 切换场景
            self.current_scene = self._get_scene_by_id(choice.next_scene_id)
            self.current_state.current_scene_id = choice.next_scene_id
            self.dialogue_index = 0
            
            return True, "进入下一场景", effects
        else:
            # 检查是否剧情完成
            if choice.effects.get('story_complete') or choice.effects.get('story_end'):
                self._complete_story()
                return True, "剧情完成", effects
            
            return True, "选择已记录", effects
    
    def _process_choice_effects(self, effects_dict: Dict[str, Any]) -> List[ChoiceEffect]:
        """处理选择效果"""
        effects = []
        
        for key, value in effects_dict.items():
            if key == 'npc_favor' and isinstance(value, dict):
                for npc_id, favor_change in value.items():
                    effects.append(ChoiceEffect(
                        effect_type='npc_favor',
                        target=npc_id,
                        value=favor_change
                    ))
            elif key in ['exp', 'spirit_stones', 'health', 'karma']:
                effects.append(ChoiceEffect(
                    effect_type=key,
                    value=value
                ))
            elif key == 'item':
                effects.append(ChoiceEffect(
                    effect_type='item',
                    value=value
                ))
            elif key == 'technique':
                effects.append(ChoiceEffect(
                    effect_type='technique',
                    value=value
                ))
            elif key == 'reputation':
                effects.append(ChoiceEffect(
                    effect_type='reputation',
                    value=value
                ))
        
        return effects
    
    def _complete_story(self):
        """完成剧情"""
        if self.current_state:
            self.db.complete_player_story(self.player_id, self.current_state.chapter_id)
            self.current_state.status = 'completed'
            self.current_state.completed_at = datetime.now().isoformat()
    
    def get_story_rewards(self) -> List[Dict[str, Any]]:
        """
        获取当前剧情的奖励
        
        Returns:
            奖励列表
        """
        if not self.current_state:
            return []
        
        rewards = self.db.get_story_rewards(self.current_state.chapter_id)
        
        # 检查是否已领取
        for reward in rewards:
            reward['claimed'] = self.db.has_claimed_reward(self.player_id, reward['id'])
        
        return rewards
    
    def claim_reward(self, reward_id: str) -> Tuple[bool, str]:
        """
        领取奖励
        
        Args:
            reward_id: 奖励ID
            
        Returns:
            (是否成功, 消息)
        """
        if not self.current_state:
            return False, "没有进行中的剧情"
        
        if self.db.has_claimed_reward(self.player_id, reward_id):
            return False, "奖励已领取"
        
        success = self.db.claim_story_reward(
            self.player_id,
            self.current_state.chapter_id,
            reward_id
        )
        
        if success:
            return True, "奖励领取成功"
        return False, "领取失败"
    
    def get_completed_stories(self, story_type: str = None) -> List[Dict[str, Any]]:
        """
        获取已完成的剧情
        
        Args:
            story_type: 剧情类型筛选
            
        Returns:
            已完成剧情列表
        """
        return self.db.get_player_completed_stories(self.player_id, story_type)
    
    def can_replay(self, chapter_id: str) -> bool:
        """
        检查剧情是否可以回放
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            是否可以回放
        """
        chapter_data = self.db.get_story_chapter(chapter_id)
        if not chapter_data:
            return False
        
        record = self.db.get_player_story_record(self.player_id, chapter_id)
        if not record:
            return False
        
        return record['status'] == 'completed' and chapter_data['is_repeatable']
    
    def replay_story(self, chapter_id: str) -> Tuple[bool, str]:
        """
        回放剧情
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            (是否成功, 消息)
        """
        if not self.can_replay(chapter_id):
            return False, "该剧情不可回放"
        
        success = self.db.replay_player_story(self.player_id, chapter_id)
        if success:
            self._load_story_state(chapter_id)
            return True, "开始剧情回放"
        return False, "回放失败"
    
    def check_story_trigger(self, trigger_type: str, condition: Any, 
                           realm_level: int, location: str) -> Optional[str]:
        """
        检查剧情触发条件
        
        Args:
            trigger_type: 触发类型
            condition: 触发条件
            realm_level: 当前境界
            location: 当前位置
            
        Returns:
            触发的剧情ID，如果没有触发返回None
        """
        for chapter_id, trigger in STORY_TRIGGERS.items():
            if trigger['type'] != trigger_type:
                continue
            
            # 检查自动触发
            if not trigger.get('auto_trigger', False):
                continue
            
            # 检查条件
            if trigger_type == 'location' and trigger['condition'] == location:
                # 检查境界要求
                chapter_data = self.db.get_story_chapter(chapter_id)
                if chapter_data and chapter_data['realm_required'] <= realm_level:
                    # 检查前置章节
                    if trigger.get('pre_chapter'):
                        pre_record = self.db.get_player_story_record(self.player_id, trigger['pre_chapter'])
                        if not pre_record or pre_record['status'] != 'completed':
                            continue
                    return chapter_id
            
            elif trigger_type == 'realm' and trigger['condition'] == realm_level:
                if trigger.get('location') == location:
                    return chapter_id
            
            elif trigger_type == 'random':
                if trigger.get('location') == location:
                    probability = trigger.get('probability', 0.1)
                    if random.random() < probability:
                        return chapter_id
        
        return None
    
    def skip_to_scene(self, scene_id: str) -> Tuple[bool, str]:
        """
        跳转到指定场景（用于回放或调试）
        
        Args:
            scene_id: 场景ID
            
        Returns:
            (是否成功, 消息)
        """
        if not self.active_story:
            return False, "没有进行中的剧情"
        
        scene = self._get_scene_by_id(scene_id)
        if not scene:
            return False, "场景不存在"
        
        self.current_scene = scene
        self.current_state.current_scene_id = scene_id
        self.dialogue_index = 0
        
        return True, f"跳转到场景：{scene.title}"
    
    def get_story_summary(self) -> Optional[Dict[str, Any]]:
        """
        获取当前剧情摘要
        
        Returns:
            剧情摘要数据
        """
        if not self.active_story or not self.current_state:
            return None
        
        return {
            'chapter_id': self.active_story.id,
            'title': self.active_story.title,
            'description': self.active_story.description,
            'story_type': self.active_story.story_type,
            'current_scene': self.current_scene.title if self.current_scene else None,
            'completed_scenes_count': len(self.current_state.completed_scenes),
            'choices_made_count': len(self.current_state.choices_made),
            'status': self.current_state.status,
            'replay_count': self.current_state.replay_count
        }


class StoryEffectApplier:
    """剧情效果应用器"""
    
    def __init__(self, player, db: Database = None):
        """
        初始化效果应用器
        
        Args:
            player: 玩家对象
            db: 数据库实例
        """
        self.player = player
        self.db = db or Database()
    
    def apply_pending_effects(self) -> List[Dict[str, Any]]:
        """
        应用待处理的效果
        
        Returns:
            已应用的效果列表
        """
        effects = self.db.get_player_choice_effects(self.player_id, None)
        applied = []
        
        for effect_data in effects:
            success = self._apply_effect(effect_data)
            if success:
                self.db.mark_choice_effect_applied(effect_data['id'])
                applied.append(effect_data)
        
        return applied
    
    def _apply_effect(self, effect_data: Dict[str, Any]) -> bool:
        """应用单个效果"""
        effect_type = effect_data['effect_type']
        target = effect_data.get('effect_target')
        value = effect_data.get('effect_value')
        
        try:
            if effect_type == 'exp':
                if hasattr(self.player, 'gain_exp'):
                    self.player.gain_exp(int(value))
                return True
            
            elif effect_type == 'spirit_stones':
                if hasattr(self.player, 'stats'):
                    self.player.stats.spirit_stones += int(value)
                return True
            
            elif effect_type == 'health':
                if hasattr(self.player, 'stats'):
                    self.player.stats.health = max(0, min(
                        self.player.stats.max_health,
                        self.player.stats.health + int(value)
                    ))
                return True
            
            elif effect_type == 'karma':
                if hasattr(self.player, 'stats'):
                    self.player.stats.karma += int(value)
                return True
            
            elif effect_type == 'npc_favor' and target:
                # NPC好感度处理
                if hasattr(self.player, 'game') and self.player.game:
                    npc_manager = self.player.game.npc_manager
                    if npc_manager:
                        npc_manager.update_favor(target, int(value))
                return True
            
            elif effect_type == 'item':
                # 物品奖励处理
                if hasattr(self.player, 'inventory'):
                    self.player.inventory.add_item(value, 1)
                return True
            
            elif effect_type == 'technique':
                # 功法学习处理
                if hasattr(self.player, 'techniques'):
                    self.player.techniques.learn(value)
                return True
            
            elif effect_type == 'reputation':
                # 声望处理
                if hasattr(self.player, 'add_reputation'):
                    self.player.add_reputation(value)
                return True
            
            return False
        
        except Exception as e:
            print(f"应用效果失败: {e}")
            return False
