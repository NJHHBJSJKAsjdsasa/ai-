"""
NPC核心模块
包含NPC主类，集成独立系统和新系统
"""

import random
import time
from typing import Dict, List, Optional, Any

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import (
    get_realm_info, get_realm_title, PERSONALITIES, SECTS, SECT_DETAILS,
    DAO_NAME_PREFIX, DAO_NAME_SUFFIX, GAME_CONFIG
)

# 导入NPC独立系统
from game.npc_independent import NPCIndependent, NPCIndependentManager

# 导入新系统模块
from game.npc_goal_system import Goal, NPCGoalSystem, npc_goal_system
from game.npc_schedule_system import Activity, NPCScheduleSystem, schedule_system as npc_schedule_system
from game.npc_relationship_network import Relationship, NPCRelationshipNetwork, relationship_network
from game.npc_proactive_behavior import ProactiveBehavior, proactive_behavior
from game.world_event_system import WorldEvent, world_event_manager, npc_event_handler
from game.npc_life_record import LifeEvent, NPCLifeRecord, NPCStoryGenerator, get_life_record
from game.npc_personality_expression import SpeakingStyle, ValuesSystem, PersonalityExpression, personality_expression
from game.enhanced_memory_system import EnhancedMemory, EnhancedMemorySystem

from .models import NPCMemory, NPCData


class NPC:
    """NPC类 - 集成独立系统和新系统"""
    
    def __init__(self, npc_data: Optional[NPCData] = None):
        """
        初始化NPC
        
        Args:
            npc_data: NPC数据
        """
        if npc_data:
            self.data = npc_data
        else:
            self.data = self._generate_random_npc()
        
        # ========== 新系统属性（必须在独立系统之前初始化）==========
        # 目标系统
        self.goals: List[Goal] = []
        
        # 日程系统
        self.schedule: Dict[int, Activity] = {}
        
        # 价值观系统
        self.values: ValuesSystem = None
        
        # 说话风格
        self.speaking_style: SpeakingStyle = None
        
        # 成长记录系统
        self.life_record: NPCLifeRecord = None
        
        # 增强记忆系统
        self.enhanced_memory: EnhancedMemorySystem = None
        
        # 主动行为冷却
        self.proactive_cooldowns: Dict[str, float] = {}
        
        # 日程执行跟踪
        self.last_executed_hour: int = -1
        self.last_execution_result: Optional[Dict[str, Any]] = None
        
        # 初始化新系统（在独立系统之前，因为独立系统需要访问目标）
        self._init_new_systems()
        
        # 初始化NPC独立系统（传入self引用以访问真实目标）
        npc_data_dict = {
            "occupation": self.data.occupation,
            "location": self.data.location,
            "personality": self.data.personality,
        }
        self.independent = NPCIndependent(self.data.id, npc_data_dict, parent_npc=self)
        
        # 战斗AI配置
        self.combat_ai_config: Dict[str, Any] = {
            "aggressive": 0.5,  # 侵略性 (0-1)
            "defensive": 0.5,  # 防御性 (0-1)
            "tactical": 0.5,  # 战术性 (0-1)
            "retreat_threshold": 0.2,  # 撤退生命值阈值
            "skill_usage_rate": 0.7,  # 技能使用频率
        }
        
        # 战斗记录
        self.combat_record: List[Dict[str, Any]] = []
    
    def _init_new_systems(self):
        """初始化所有新系统"""
        # 1. 生成初始目标
        self._generate_initial_goals()
        
        # 2. 生成每日日程
        self._generate_daily_schedule()
        
        # 3. 生成价值观和说话风格
        self._generate_personality_expression()
        
        # 4. 初始化成长记录
        self.life_record = get_life_record()
        self._record_birth_event()
        
        # 5. 初始化增强记忆系统
        self.enhanced_memory = EnhancedMemorySystem(self.data.id)
        
        # 6. 注册世界事件监听
        self._register_event_handlers()
    
    def _generate_initial_goals(self, verbose: bool = False):
        """
        生成初始目标（基于NPC真实属性）
        
        使用npc_goal_system.generate_goals，它会基于NPC的真实职业、性格、境界生成目标
        
        Args:
            verbose: 是否显示详细日志（批量生成时建议设为False）
        """
        # 使用目标系统生成目标（基于真实属性）
        generated_goals = npc_goal_system.generate_goals(self, count=random.randint(2, 4))
        self.goals.extend(generated_goals)
        
        # 仅在详细模式下记录目标生成日志
        if verbose:
            print(f"[NPC目标] {self.data.dao_name}({self.data.id}) 生成了 {len(generated_goals)} 个目标")
            for goal in generated_goals:
                goal_type = goal.goal_type.value if hasattr(goal.goal_type, 'value') else str(goal.goal_type)
                # 创建优先级进度条
                priority_bar = "█" * goal.priority + "░" * (10 - goal.priority)
                print(f"  - {goal_type}: {goal.description}")
                print(f"    优先级: [{priority_bar}] {goal.priority}/10")
    
    def _get_goal_target(self, goal_type: str) -> str:
        """根据目标类型获取目标对象"""
        targets = {
            "cultivation": f"突破到{get_realm_info(min(self.data.realm_level + 1, 7)).name if get_realm_info(min(self.data.realm_level + 1, 7)) else '更高境界'}",
            "exploration": random.choice(["神秘洞穴", "古老遗迹", "禁地", "秘境"]),
            "social": "结交志同道合的道友",
            "combat": "提升战斗技巧",
            "crafting": f"成为优秀的{self.data.occupation}" if self.data.occupation else "精通技艺"
        }
        return targets.get(goal_type, "未知目标")
    
    def _generate_daily_schedule(self):
        """生成每日日程"""
        # 保存当前日程到历史（如果存在）
        self.save_schedule_history()
        
        schedule = npc_schedule_system.generate_daily_schedule(self)
        # 将活动列表转换为以小时为键的字典
        self.schedule = {}
        if schedule and hasattr(schedule, 'activities'):
            for activity in schedule.activities:
                if hasattr(activity, 'start_time'):
                    self.schedule[activity.start_time] = activity
    
    def save_schedule_history(self):
        """
        保存当前日程到历史记录
        将当前日程保存到日程系统的历史记录中
        """
        if not self.schedule:
            return
        
        # 从当前schedule字典创建DailySchedule对象
        from game.npc_schedule_system import DailySchedule, Activity
        daily_schedule = DailySchedule(npc_id=self.data.id)
        
        # 添加活动到日程
        for hour, activity in self.schedule.items():
            if activity and isinstance(activity, Activity):
                daily_schedule.add_activity(activity)
        
        # 保存到日程系统的历史记录
        npc_schedule_system._add_to_history(self.data.id, daily_schedule)
    
    def get_schedule_history(self) -> List[Dict[str, Any]]:
        """
        获取日程历史记录
        
        Returns:
            过去7天的日程历史列表
        """
        history = npc_schedule_system.get_schedule_history(self.data.id)
        
        # 转换为可序列化的字典列表
        history_list = []
        for schedule in history:
            if schedule and hasattr(schedule, 'to_dict'):
                history_list.append(schedule.to_dict())
        
        return history_list
    
    def _generate_personality_expression(self):
        """生成个性表达系统"""
        # 生成价值观
        self.values = ValuesSystem()
        self.values.generate_random_values()
        
        # 根据道德值调整价值观
        if self.data.morality > 30:
            self.values.values.justice = max(self.values.values.justice, 70)
        elif self.data.morality < -30:
            self.values.values.justice = min(self.values.values.justice, 30)
        
        # 生成说话风格
        self.speaking_style = personality_expression.get_style_for_personality(self.data.personality)
    
    def _record_birth_event(self):
        """记录出生/初始事件"""
        if self.life_record:
            from game.npc_life_record import EventType, EmotionType
            self.life_record.record_event(
                npc_id=self.data.id,
                event_type=EventType.ACHIEVEMENT,
                description=f"{self.data.name}出生于{self.data.sect}，成为{self.data.occupation}",
                importance=8,
                emotion=EmotionType.POSITIVE,
                location=self.data.sect,
                outcome=f"成为{self.data.sect}的{self.data.occupation}",
                details={
                    "sect": self.data.sect,
                    "occupation": self.data.occupation,
                    "realm_level": self.data.realm_level,
                    "realm_name": self.get_realm_name(),
                    "age": self.data.age
                }
            )
    
    def _register_event_handlers(self):
        """注册世界事件处理器"""
        # 注册NPC事件监听器
        from game.world_event_system import WorldEventType
        world_event_manager.register_npc_listener(
            self.data.id, 
            [WorldEventType.PLAYER_BREAKTHROUGH, WorldEventType.SECRET_REALM_OPEN]
        )
    
    def update(self, current_time: float = None, player_nearby: bool = False) -> bool:
        """
        更新NPC状态（独立系统 + 新系统）
        
        Args:
            current_time: 当前时间戳
            player_nearby: 玩家是否在附近
            
        Returns:
            是否执行了更新
        """
        if current_time is None:
            current_time = time.time()
        
        # 更新独立系统
        updated = self.independent.update(current_time, player_nearby)
        
        # ========== 新系统更新 ==========
        # 1. 获取当前小时
        current_hour = int((current_time // 3600) % 24)
        
        # 2. 执行当前日程活动（每小时只执行一次）
        if current_hour != self.last_executed_hour:
            self.execute_current_activity(current_hour)
            self.last_executed_hour = current_hour
        
        # 3. 获取当前活动（日程系统）
        current_activity = self.schedule.get(current_hour)
        
        # 4. 检查主动行为
        if player_nearby:
            self._check_proactive_behaviors(current_time)
        
        # 5. 更新目标进度
        self._update_goal_progress(current_activity)
        
        # 6. 记录生活事件（根据活动）
        if current_activity and random.random() < 0.1:  # 10%概率记录
            self._record_activity_event(current_activity)
        
        return updated
    
    def execute_current_activity(self, hour: int = None) -> Dict[str, Any]:
        """
        执行当前小时的活动并应用效果
        
        Args:
            hour: 当前小时（0-23），如果为None则使用当前时间
            
        Returns:
            执行结果字典
        """
        if hour is None:
            hour = time.localtime().tm_hour
        
        # 调用NPCScheduleSystem.execute_schedule_with_effects执行日程
        result = npc_schedule_system.execute_schedule_with_effects(self, hour)
        
        # 保存执行结果
        self.last_execution_result = result
        
        # 如果执行成功，记录到记忆系统
        if result.get("success"):
            activity = result.get("activity")
            effects = result.get("effects", {})
            
            # 构建记忆内容
            if activity:
                activity_desc = activity.get("description", "未知活动")
                effects_msg = effects.get("message", "")
                memory_content = f"{activity_desc}"
                if effects_msg:
                    memory_content += f"，{effects_msg}"
                
                # 添加到独立系统记忆
                self.independent._add_memory(memory_content, importance=3)
                
                # 添加到增强记忆系统
                if self.enhanced_memory:
                    from game.enhanced_memory_system import EnhancedMemory, MemoryCategory, MemoryEmotion
                    memory = EnhancedMemory(
                        content=memory_content,
                        category=MemoryCategory.ACHIEVEMENT,
                        importance=3,
                        emotion=MemoryEmotion.NEUTRAL
                    )
                    self.enhanced_memory.add_memory(memory)
                
                # 记录到生活记录系统
                if self.life_record:
                    from game.npc_life_record import EventType, EmotionType
                    
                    # 根据活动类型确定事件类型和情感
                    activity_type = activity.get("activity_type", "")
                    event_type = EventType.DECISION
                    emotion = EmotionType.NEUTRAL
                    
                    if activity_type == "修炼":
                        event_type = EventType.ACHIEVEMENT
                        emotion = EmotionType.POSITIVE
                    elif activity_type == "社交":
                        event_type = EventType.SOCIAL
                        emotion = EmotionType.POSITIVE
                    elif activity_type == "探索":
                        event_type = EventType.EXPLORATION
                        emotion = EmotionType.EXCITED
                    elif activity_type == "睡觉":
                        event_type = EventType.CULTIVATION
                        emotion = EmotionType.NEUTRAL
                    
                    self.life_record.record_event(
                        npc_id=self.data.id,
                        event_type=event_type,
                        description=memory_content,
                        importance=random.randint(2, 4),
                        emotion=emotion,
                        location=self.data.location,
                        outcome=effects_msg if effects_msg else "完成日常活动",
                        details={
                            "activity_type": activity_type,
                            "hour": hour,
                            "effects": effects.get("changes", {})
                        }
                    )
        
        return result
    
    def _check_proactive_behaviors(self, current_time: float):
        """检查主动行为"""
        # 检查各种主动行为的冷却
        behavior_types = ["dialogue", "combat", "trade", "exploration"]
        
        for behavior_type in behavior_types:
            cooldown_key = f"proactive_{behavior_type}"
            last_time = self.proactive_cooldowns.get(cooldown_key, 0)
            
            # 检查冷却时间（至少5分钟）
            if current_time - last_time < 300:
                continue
            
            # 检查冷却是否过期（可以触发新行为）
            if not proactive_behavior.is_on_cooldown(self.data.id, behavior_type):
                self.proactive_cooldowns[cooldown_key] = current_time
                # 实际触发逻辑由调用方处理
                break
    
    def _update_goal_progress(self, current_activity: Optional[Activity]):
        """
        更新目标进度（使用npc_goal_system统一处理）
        
        Args:
            current_activity: 当前活动
        """
        if not current_activity:
            return
        
        # 使用npc_goal_system.update_goal_from_activity统一处理目标进度更新
        results = npc_goal_system.update_goal_from_activity(self, current_activity)
        
        # 处理完成的目标
        for result in results:
            if result.get('just_achieved'):
                goal = result.get('goal')
                if goal:
                    self._complete_goal(goal)
        
        # 如果有目标被更新，保存到数据库
        if results:
            self.save_to_database()
    
    def _calculate_goal_progress(self, goal: Goal, activity: Activity) -> float:
        """计算目标进度增量"""
        from game.npc_goal_system import GoalType
        from game.npc_schedule_system import ScheduleActivityType
        
        # 活动类型与目标类型的映射关系
        activity_to_goal_map = {
            ScheduleActivityType.CULTIVATE: GoalType.BREAKTHROUGH,
            ScheduleActivityType.WORK: GoalType.EARN_SPIRIT_STONES,
            ScheduleActivityType.SOCIALIZE: GoalType.BUILD_RELATIONSHIP,
            ScheduleActivityType.EXPLORE: GoalType.EXPLORE_LOCATION,
            ScheduleActivityType.CRAFT: GoalType.ALCHEMY,
        }
        
        # 获取活动类型和目标类型
        activity_type = activity.activity_type
        goal_type = goal.goal_type
        
        # 检查活动类型是否与目标类型匹配
        mapped_goal_type = activity_to_goal_map.get(activity_type)
        if mapped_goal_type != goal_type:
            return 0.0
        
        # 基础进度增量（根据活动时长）
        base_progress = activity.duration * random.uniform(1.0, 2.0)
        
        # 根据NPC性格调整进度（勤奋性格加成）
        diligence_bonus = 1.0
        if hasattr(self.independent, 'personality') and hasattr(self.independent.personality, 'diligence'):
            diligence = self.independent.personality.diligence
            # 勤奋度0.5为基准，每增加0.1增加5%进度
            diligence_bonus = 1.0 + (diligence - 0.5) * 0.5
        
        # 计算最终进度增量
        progress_increment = base_progress * diligence_bonus
        
        return progress_increment
    
    def _complete_goal(self, goal: Goal):
        """完成目标处理"""
        # 标记目标完成
        goal.is_completed = True
        
        # 记录完成事件到NPC人生记录
        if self.life_record:
            from game.npc_life_record import EventType, EmotionType
            
            # 根据目标类型确定事件描述
            goal_descriptions = {
                "突破境界": f"成功突破境界，达到新的修为层次",
                "赚取灵石": f"赚取了足够的灵石，财富目标达成",
                "建立关系": f"建立了深厚的关系，社交目标达成",
                "探索地点": f"完成了地点探索，发现了新的区域",
                "炼丹炼器": f"成功炼制了目标物品，炼制技艺提升",
            }
            
            goal_type_value = goal.goal_type.value if hasattr(goal.goal_type, 'value') else str(goal.goal_type)
            description = goal_descriptions.get(goal_type_value, f"完成了目标：{goal.description}")
            
            self.life_record.record_event(
                npc_id=self.data.id,
                event_type=EventType.ACHIEVEMENT,
                description=description,
                importance=random.randint(6, 9),
                emotion=EmotionType.POSITIVE,
                location=self.data.location
            )
        
        # 触发完成奖励（添加到记忆系统）
        reward_message = f"目标达成：{goal.description}，感到{goal.reward_emotion}"
        self.independent.add_memory(reward_message, importance=7)
        
        # 添加到增强记忆系统
        if self.enhanced_memory:
            self.enhanced_memory.add_memory(
                content=reward_message,
                memory_type="achievement",
                importance=7,
                emotional_tag="positive"
            )
    
    def _record_activity_event(self, activity: Activity):
        """记录活动事件"""
        if not self.life_record:
            return
        
        from game.npc_life_record import EventType, EmotionType
        
        event_descriptions = {
            "cultivation": f"专心修炼，感悟{get_realm_info(self.data.realm_level).name if get_realm_info(self.data.realm_level) else '境界'}之道",
            "work": f"从事{self.data.occupation}工作",
            "rest": "休息恢复精力",
            "social": "与其他修士交流",
            "exploration": "探索周边区域",
            "combat": "进行战斗训练"
        }
        
        activity_type_value = activity.activity_type.value if hasattr(activity.activity_type, 'value') else str(activity.activity_type)
        description = event_descriptions.get(
            activity_type_value, 
            f"进行{activity.description if activity.description else '活动'}"
        )
        
        self.life_record.record_event(
            npc_id=self.data.id,
            event_type=EventType.EXPLORATION if activity_type_value == "exploration" else EventType.DECISION,
            description=description,
            importance=random.randint(2, 4),
            emotion=EmotionType.NEUTRAL,
            location=self.data.location
        )
    
    def get_independent_status(self) -> Dict[str, Any]:
        """获取独立系统状态"""
        return self.independent.get_status()
    
    # ========== 新系统公共方法 ==========
    def set_goal(self, goal_type: str, target: str, priority: int = 5) -> Optional[Goal]:
        """
        设置目标
        
        Args:
            goal_type: 目标类型
            target: 目标对象
            priority: 优先级 (1-10)
            
        Returns:
            创建的目标对象
        """
        from game.npc_goal_system import GoalType
        
        try:
            # 将字符串目标类型转换为枚举
            goal_type_map = {
                "cultivation": GoalType.BREAKTHROUGH,
                "exploration": GoalType.EXPLORE_LOCATION,
                "social": GoalType.BUILD_RELATIONSHIP,
                "combat": GoalType.EARN_SPIRIT_STONES,
                "crafting": GoalType.ALCHEMY,
            }
            gt = goal_type_map.get(goal_type, GoalType.BREAKTHROUGH)
            
            goal = Goal(
                goal_type=gt,
                description=target,
                target_value=100.0,
                current_value=0.0,
                priority=priority,
                npc_id=self.data.id,
            )
            self.goals.append(goal)
            
            # 记录目标设定事件
            if self.life_record:
                self.life_record.add_event(
                    event_type="goal_set",
                    description=f"设定了新目标：{target}",
                    importance=5,
                    tags=["目标", goal_type]
                )
            return goal
        except Exception:
            return None
    
    def get_daily_schedule(self) -> Dict[int, Activity]:
        """
        获取每日日程
        
        Returns:
            日程字典 {小时: 活动}
        """
        return self.schedule
    
    def get_current_activity(self) -> Optional[Activity]:
        """
        获取当前活动
        
        Returns:
            当前活动对象
        """
        import time
        current_hour = time.localtime().tm_hour
        return npc_schedule_system.get_current_activity(self, current_hour)
    
    def initiate_interaction(self, target: 'NPC') -> bool:
        """
        主动发起交互
        
        Args:
            target: 目标NPC
            
        Returns:
            是否成功发起
        """
        if not target:
            return False
        
        # 使用主动行为系统
        behavior_type = proactive_behavior.determine_behavior_type(self.data.id, target.data.id)
        
        if behavior_type == "socialize":
            # 社交交互
            self.socialize_with(target)
            return True
        elif behavior_type == "combat":
            # 战斗交互
            self._check_combat_trigger(target)
            return True
        elif behavior_type == "trade":
            # 交易交互（记录事件）
            if self.life_record:
                self.life_record.add_event(
                    event_type="trade",
                    description=f"向{target.data.name}发起交易",
                    importance=4,
                    tags=["交易", "社交"]
                )
            return True
        
        return False
    
    def perceive_world_event(self, event: WorldEvent):
        """
        感知世界事件
        
        Args:
            event: 世界事件
        """
        # 记录事件感知
        if self.life_record:
            self.life_record.add_event(
                event_type="world_event",
                description=f"感知到世界事件：{event.name}",
                importance=event.importance,
                tags=["世界事件"] + event.tags
            )
        
        # 添加到增强记忆
        if self.enhanced_memory:
            self.enhanced_memory.add_memory(
                content=f"经历了世界事件：{event.description}",
                memory_type="world_event",
                importance=event.importance,
                emotional_tag=event.emotional_impact
            )
        
        # 根据事件类型调整目标
        self._adjust_goals_by_event(event)
    
    def _adjust_goals_by_event(self, event: WorldEvent):
        """根据世界事件调整目标"""
        # 根据事件影响调整目标优先级
        for goal in self.goals:
            if goal.is_completed or goal.is_failed:
                continue
            
            # 根据事件类型和目标类型的关联调整
            if event.event_type == "cultivation_opportunity" and goal.goal_type.value == "突破境界":
                goal.priority = min(10, goal.priority + 1)
            elif event.event_type == "conflict" and goal.goal_type.value == "赚取灵石":
                goal.priority = min(10, goal.priority + 2)
            elif event.event_type == "resource_discovery" and goal.goal_type.value == "探索地点":
                goal.priority = min(10, goal.priority + 1)
    
    def get_life_story(self) -> str:
        """
        获取人生故事
        
        Returns:
            人生故事文本
        """
        if not self.life_record:
            return f"{self.data.name}的故事尚未开始..."
        
        story_generator = NPCStoryGenerator(self.life_record)
        return story_generator.generate_life_story()
    
    def get_personality_description(self) -> str:
        """
        获取个性描述
        
        Returns:
            个性描述文本
        """
        descriptions = []
        
        # 基础性格
        descriptions.append(f"性格：{self.data.personality}")
        
        # 价值观描述
        if self.values:
            descriptions.append(f"价值观：{self.values.get_dominant_value()}")
        
        # 说话风格
        if self.speaking_style:
            style_desc = f"说话风格：{self.speaking_style.formality_level}"
            if self.speaking_style.use_classical:
                style_desc += "，善用古文"
            descriptions.append(style_desc)
        
        # 当前目标
        active_goals = [g for g in self.goals if not g.is_completed and not g.is_failed]
        if active_goals:
            top_goal = max(active_goals, key=lambda g: g.priority)
            descriptions.append(f"当前目标：{top_goal.description}")
        
        return "；".join(descriptions)
    
    def update_relationship_with(self, target_id: str, delta: Dict[str, int], reason: str = "") -> bool:
        """
        更新与特定NPC的关系

        Args:
            target_id: 目标NPC ID
            delta: 关系变化值字典，可包含 affinity, intimacy, hatred
            reason: 变化原因

        Returns:
            是否成功更新
        """
        # 更新关系网络
        success = relationship_network.update_relationship(
            npc1_id=self.data.id,
            npc2_id=target_id,
            delta=delta,
            reason=reason
        )

        # 记录关系变化事件
        if success and self.life_record:
            total_change = abs(delta.get("affinity", 0)) + abs(delta.get("intimacy", 0)) + abs(delta.get("hatred", 0))
            if total_change >= 5:
                event_type = "relationship_improve" if delta.get("affinity", 0) > 0 else "relationship_deteriorate"
                self.life_record.add_event(
                    event_type=event_type,
                    description=f"与{target_id}的关系发生变化：{reason}" if reason else f"与{target_id}的关系发生变化",
                    importance=min(10, int(total_change / 10) + 3),
                    tags=["关系变化"]
                )

        return success

    def get_relationship_with(self, target_id: str) -> Optional[Relationship]:
        """
        获取与特定NPC的关系

        Args:
            target_id: 目标NPC ID

        Returns:
            关系对象
        """
        return relationship_network.get_relationship(self.data.id, target_id)

    def get_all_relationships(self) -> Dict[str, Relationship]:
        """
        获取NPC的所有关系

        Returns:
            关系字典 {other_npc_id: Relationship}
        """
        return relationship_network.get_relationships(self.data.id)

    def get_friends(self, min_affinity: int = 20) -> List[Tuple[str, Relationship]]:
        """
        获取朋友列表

        Args:
            min_affinity: 最小好感度阈值

        Returns:
            [(friend_id, relationship), ...]
        """
        return relationship_network.get_friends(self.data.id, min_affinity)

    def get_enemies(self, min_hatred: int = 20) -> List[Tuple[str, Relationship]]:
        """
        获取敌人列表

        Args:
            min_hatred: 最小仇恨度阈值

        Returns:
            [(enemy_id, relationship), ...]
        """
        return relationship_network.get_enemies(self.data.id, min_hatred)

    def add_relationship_with(self, target_id: str, relation_type,
                             initial_affinity: int = 0, initial_intimacy: int = 0,
                             initial_hatred: int = 0) -> bool:
        """
        添加与特定NPC的关系

        Args:
            target_id: 目标NPC ID
            relation_type: 关系类型
            initial_affinity: 初始好感度
            initial_intimacy: 初始亲密度
            initial_hatred: 初始仇恨度

        Returns:
            是否成功添加
        """
        from game.npc_relationship_network import RelationType
        if isinstance(relation_type, str):
            try:
                relation_type = RelationType(relation_type)
            except ValueError:
                relation_type = RelationType.ACQUAINTANCE

        return relationship_network.add_relationship(
            npc1_id=self.data.id,
            npc2_id=target_id,
            relation_type=relation_type,
            initial_affinity=initial_affinity,
            initial_intimacy=initial_intimacy,
            initial_hatred=initial_hatred
        )
    
    def speak(self, content: str, context: str = "") -> str:
        """
        生成个性化对话
        
        Args:
            content: 原始内容
            context: 对话上下文
            
        Returns:
            个性化表达的内容
        """
        if not self.speaking_style:
            return content
        
        return self.speaking_style.express(content, context)
    
    def add_enhanced_memory(self, content: str, memory_type: str = "general", 
                           importance: int = 5, emotional_tag: str = "neutral"):
        """
        添加增强记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            emotional_tag: 情感标签
        """
        if self.enhanced_memory:
            self.enhanced_memory.add_memory(
                content=content,
                memory_type=memory_type,
                importance=importance,
                emotional_tag=emotional_tag
            )
    
    def get_combat_power(self) -> int:
        """
        计算战斗力
        
        Returns:
            战斗力数值
        """
        # 基础战斗力 = 攻击 + 防御 * 2 + 速度
        base_power = self.data.attack + self.data.defense * 2 + self.data.speed
        
        # 境界加成
        realm_multiplier = 1 + self.data.realm_level * 0.2
        
        # 暴击和闪避加成
        crit_bonus = self.data.crit_rate * 100
        dodge_bonus = self.data.dodge_rate * 100
        
        # 计算总战斗力
        combat_power = int((base_power + crit_bonus + dodge_bonus) * realm_multiplier)
        
        return combat_power
    
    def socialize_with(self, other_npc: 'NPC'):
        """
        与另一个NPC社交
        
        Args:
            other_npc: 另一个NPC
        """
        # 更新关系
        affinity_change = random.uniform(-2, 5)
        self.independent.update_relationship(other_npc.data.id, affinity_change)
        other_npc.independent.update_relationship(self.data.id, affinity_change)
        
        # 分享记忆
        if self.independent.memories and random.random() < 0.3:
            memory = random.choice(self.independent.memories)
            other_npc.independent.add_memory(
                f"听{self.data.dao_name}说: {memory.content}", 
                importance=memory.importance//2
            )
        
        if other_npc.independent.memories and random.random() < 0.3:
            memory = random.choice(other_npc.independent.memories)
            self.independent.add_memory(
                f"听{other_npc.data.dao_name}说: {memory.content}", 
                importance=memory.importance//2
            )
        
        # 记录互动记忆
        self.independent.add_memory(f"与{other_npc.data.dao_name}交流了一番", importance=3)
        other_npc.independent.add_memory(f"与{self.data.dao_name}交流了一番", importance=3)
        
        # 检查战斗机会
        self._check_combat_trigger(other_npc)
    
    def _check_combat_trigger(self, other_npc: 'NPC'):
        """
        检查是否触发战斗
        
        Args:
            other_npc: 另一个NPC
        """
        from game.npc_combat import npc_combat_manager
        
        # 检查战斗机会
        combat_type = self.independent._check_combat_opportunity(other_npc)
        
        if combat_type:
            # 双方做出战斗决策
            self_accept = self.independent._make_combat_decision(other_npc, combat_type)
            other_accept = other_npc.independent._make_combat_decision(self, combat_type)
            
            if self_accept and other_accept:
                # 执行战斗
                if combat_type == "spar":
                    result = npc_combat_manager.execute_npc_spar(self, other_npc)
                    if result:
                        # 记录战斗
                        self._record_combat(other_npc, combat_type, result)
                        other_npc._record_combat(self, combat_type, result)
                elif combat_type == "deathmatch":
                    result = npc_combat_manager.execute_npc_deathmatch(self, other_npc)
                    if result:
                        self._record_combat(other_npc, combat_type, result)
                        other_npc._record_combat(self, combat_type, result)
    
    def _record_combat(self, opponent: 'NPC', combat_type: str, result):
        """
        记录战斗结果
        
        Args:
            opponent: 对手NPC
            combat_type: 战斗类型
            result: 战斗结果
        """
        import time
        
        # 确定胜负
        if result.winner_id == self.data.id:
            outcome = "win"
            self.data.combat_wins += 1
        elif result.winner_id == opponent.data.id:
            outcome = "loss"
            self.data.combat_losses += 1
        else:
            outcome = "draw"
        
        # 添加到战斗记录
        combat_entry = {
            "opponent_id": opponent.data.id,
            "opponent_name": opponent.data.dao_name,
            "type": combat_type,
            "outcome": outcome,
            "timestamp": time.time(),
            "turns": getattr(result, 'total_turns', 0),
        }
        self.combat_record.append(combat_entry)
        
        # 限制记录数量
        if len(self.combat_record) > 20:
            self.combat_record = self.combat_record[-20:]
    
    def _generate_random_npc(self) -> NPCData:
        """生成随机NPC"""
        # 生成道号
        dao_name = random.choice(DAO_NAME_PREFIX) + random.choice(DAO_NAME_SUFFIX)

        # 随机境界（根据概率分布）
        realm_weights = [30, 25, 20, 15, 8, 2, 0, 0]  # 凡人到大乘的概率
        realm_level = random.choices(range(8), weights=realm_weights)[0]

        # 获取境界信息
        realm_info = get_realm_info(realm_level)

        # 随机年龄
        if realm_level == 0:
            age = random.randint(16, 60)
            lifespan = 80
        else:
            min_age = 16 + realm_level * 10
            max_age = realm_info.lifespan if realm_info else 100
            age = random.randint(min_age, min(max_age - 10, max_age))
            lifespan = realm_info.lifespan if realm_info else 100

        # 随机门派（优先使用有详细信息的门派）
        if SECT_DETAILS and random.random() < 0.7:  # 70%概率使用有详细信息的门派
            sect = random.choice(list(SECT_DETAILS.keys()))
            sect_info = SECT_DETAILS.get(sect, {})
            sect_type = sect_info.get("type", "中立")
            sect_specialty = sect_info.get("specialty", "")

            # 根据门派类型调整职业
            if sect_specialty == "炼丹术":
                occupations = ["炼丹师", "药商", "门派弟子", "散修"]
            elif sect_specialty == "驭兽术":
                occupations = ["驭兽师", "猎人", "门派弟子", "散修"]
            elif sect_specialty == "剑道" or sect_specialty == "巨剑术":
                occupations = ["剑修", "门派弟子", "散修", "猎人"]
            elif sect_specialty == "炼体术":
                occupations = ["体修", "门派弟子", "散修", "铁匠"]
            elif sect_specialty == "符箓之道":
                occupations = ["符师", "门派弟子", "散修", "药商"]
            else:
                occupations = ["药商", "铁匠", "散修", "门派弟子", "炼丹师", "炼器师", "猎人", "渔夫"]
        else:
            sect = random.choice(SECTS)
            sect_type = ""
            sect_specialty = ""
            occupations = ["药商", "铁匠", "散修", "门派弟子", "炼丹师", "炼器师", "猎人", "渔夫"]

        occupation = random.choice(occupations)

        # 随机性格
        personality = random.choice(PERSONALITIES)

        # 生成ID
        npc_id = f"npc_{random.randint(10000, 99999)}"

        # 随机生成善恶值 (-80到80之间)
        morality = random.randint(-80, 80)

        # 根据门派类型调整善恶值 (正道+20, 邪道-20)
        if sect_type == "正道":
            morality += 20
        elif sect_type == "邪道":
            morality -= 20

        # 确保善恶值在-100到100范围内
        morality = max(-100, min(100, morality))

        # 根据境界生成战斗属性
        base_attack = 10 + realm_level * 5
        base_defense = 5 + realm_level * 3
        base_speed = 8 + realm_level * 2
        base_crit = min(0.03 + realm_level * 0.01, 0.3)
        base_dodge = min(0.03 + realm_level * 0.01, 0.3)

        # 根据职业调整战斗属性
        if occupation in ["剑修", "体修"]:
            base_attack = int(base_attack * 1.2)
            base_crit = min(base_crit * 1.5, 0.5)
        elif occupation in ["炼丹师", "炼器师"]:
            base_defense = int(base_defense * 1.2)
        elif occupation == "驭兽师":
            base_speed = int(base_speed * 1.3)

        # 添加随机波动
        attack = int(base_attack * random.uniform(0.8, 1.2))
        defense = int(base_defense * random.uniform(0.8, 1.2))
        speed = int(base_speed * random.uniform(0.8, 1.2))
        crit_rate = round(base_crit * random.uniform(0.8, 1.2), 3)
        dodge_rate = round(base_dodge * random.uniform(0.8, 1.2), 3)

        return NPCData(
            id=npc_id,
            name=dao_name,
            dao_name=dao_name,
            age=age,
            lifespan=lifespan,
            realm_level=realm_level,
            sect=sect,
            sect_type=sect_type,
            sect_specialty=sect_specialty,
            personality=personality,
            occupation=occupation,
            location="新手村",
            morality=morality,
            attack=attack,
            defense=defense,
            speed=speed,
            crit_rate=crit_rate,
            dodge_rate=dodge_rate,
        )
    
    def get_realm_name(self) -> str:
        """获取境界名称"""
        realm_info = get_realm_info(self.data.realm_level)
        return realm_info.name if realm_info else "凡人"
    
    def get_sect_description(self) -> str:
        """获取门派描述"""
        if self.data.sect in SECT_DETAILS:
            sect_info = SECT_DETAILS[self.data.sect]
            return f"{self.data.sect}（{sect_info.get('type', '未知')}）- {sect_info.get('description', '')[:50]}..."
        return self.data.sect
    
    def get_sect_info(self) -> Dict[str, str]:
        """获取门派详细信息"""
        if self.data.sect in SECT_DETAILS:
            return SECT_DETAILS[self.data.sect]
        return {}
    
    def get_title(self, for_self: bool = False) -> str:
        """获取称谓"""
        return get_realm_title(self.data.realm_level, for_self)
    
    def add_memory(self, content: str, importance: int = 5, emotion: str = "neutral"):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            importance: 重要性
            emotion: 情感
        """
        memory = NPCMemory(
            content=content,
            importance=importance,
            emotion=emotion,
        )
        self.data.memories.append(memory)
        
        # 限制记忆数量
        max_memories = GAME_CONFIG["npc"]["npc_interaction_memory_limit"]
        if len(self.data.memories) > max_memories:
            # 删除重要性最低的记忆
            self.data.memories.sort(key=lambda m: m.importance)
            self.data.memories = self.data.memories[-max_memories:]
    
    def update_favor(self, player_name: str, delta: int):
        """
        更新好感度
        
        Args:
            player_name: 玩家名字
            delta: 变化值
        """
        # 确保favor是字典
        if not isinstance(self.data.favor, dict):
            self.data.favor = {}
        current = self.data.favor.get(player_name, 0)
        self.data.favor[player_name] = max(-100, min(100, current + delta))
    
    def get_favor(self, player_name: str) -> int:
        """
        获取好感度
        
        Args:
            player_name: 玩家名字
            
        Returns:
            好感度值
        """
        # 确保favor是字典
        if not isinstance(self.data.favor, dict):
            self.data.favor = {}
        return self.data.favor.get(player_name, 0)
    
    def get_greeting(self, player_name: str) -> str:
        """
        获取问候语
        
        Args:
            player_name: 玩家名字
            
        Returns:
            问候语
        """
        favor = self.get_favor(player_name)
        
        if favor >= 50:
            greetings = [
                f"{player_name}道友！好久不见，别来无恙？",
                f"哈哈，{player_name}道友来了，快请进！",
                f"{player_name}道友，今日可要多叙叙旧。",
            ]
        elif favor >= 0:
            greetings = [
                f"{player_name}道友，有礼了。",
                f"见过{player_name}道友。",
                f"{player_name}道友安好。",
            ]
        elif favor >= -50:
            greetings = [
                f"...（冷淡地看着{player_name}）",
                f"{player_name}道友，有何贵干？",
                f"哼，{player_name}...",
            ]
        else:
            greetings = [
                f"{player_name}！你还敢出现在我面前？",
                f"滚！我不想见到你！",
                f"（怒目而视）{player_name}...",
            ]
        
        return random.choice(greetings)
    
    def advance_time(self, days: int = 1):
        """
        推进时间

        Args:
            days: 天数
        """
        self.data.age += days // 365

        # 检查寿元
        if self.data.age >= self.data.lifespan:
            self.data.is_alive = False

    def mark_as_dead(self, killer_name: str, reason: str, location: str):
        """
        标记NPC死亡

        Args:
            killer_name: 凶手名称
            reason: 死亡原因
            location: 死亡地点
        """
        import time
        from game.death_manager import death_manager

        # 更新死亡地点
        self.data.location = location

        # 调用death_manager保存记录并设置死亡状态
        death_record = death_manager.mark_npc_dead(self, killer_name, reason)

        # 填充死亡信息
        self.data.death_info = {
            "killer_name": killer_name,
            "reason": reason,
            "location": location,
            "timestamp": time.time(),
            "realm_at_death": self.get_realm_name(),
            "age_at_death": self.data.age,
            "death_time": death_record.death_time.isoformat(),
            "can_resurrect": death_record.can_resurrect,
        }

        # 根据death_manager的判断更新can_resurrect
        self.data.can_resurrect = death_record.can_resurrect

        # 添加死亡记忆到独立系统
        self.independent._add_memory(
            f"在{location}被{killer_name}击杀，死因：{reason}",
            importance=10
        )

    def resurrect(self) -> bool:
        """
        复活NPC

        Returns:
            是否成功复活
        """
        # 检查是否可复活
        if not self.data.can_resurrect:
            return False

        # 检查是否已死亡
        if self.data.is_alive:
            return False

        # 设置存活状态
        self.data.is_alive = True

        # 清除死亡信息
        self.data.death_info = {}

        # 添加复活记忆
        self.independent._add_memory(
            "奇迹般地复活了，重获新生",
            importance=10
        )

        return True

    def get_morality_description(self) -> str:
        """
        获取善恶值描述

        Returns:
            善恶描述字符串
        """
        morality = self.data.morality

        if morality < -50:
            return "极恶"
        elif morality < -20:
            return "邪恶"
        elif morality < 0:
            return "偏恶"
        elif morality == 0:
            return "中立"
        elif morality <= 20:
            return "偏善"
        elif morality <= 50:
            return "善良"
        else:
            return "大善"

    def is_evil(self) -> bool:
        """
        是否邪恶

        Returns:
            善恶值是否为负
        """
        return self.data.morality < 0

    def is_good(self) -> bool:
        """
        是否善良

        Returns:
            善恶值是否为正
        """
        return self.data.morality > 0

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            包含NPC数据的字典
        """
        data = {
            "id": self.data.id,
            "name": self.data.name,
            "dao_name": self.data.dao_name,
            "age": self.data.age,
            "lifespan": self.data.lifespan,
            "realm_level": self.data.realm_level,
            "sect": self.data.sect,
            "personality": self.data.personality,
            "occupation": self.data.occupation,
            "location": self.data.location,
            "favor": self.data.favor,
            "is_alive": self.data.is_alive,
            "death_info": self.data.death_info,
            "can_resurrect": self.data.can_resurrect,
            "morality": self.data.morality,
            "sect_type": self.data.sect_type,
            "sect_specialty": self.data.sect_specialty,
            "attack": self.data.attack,
            "defense": self.data.defense,
            "speed": self.data.speed,
            "crit_rate": self.data.crit_rate,
            "dodge_rate": self.data.dodge_rate,
            "combat_wins": self.data.combat_wins,
            "combat_losses": self.data.combat_losses,
            "combat_record": self.combat_record,
        }
        
        # ========== 新系统数据序列化 ==========
        # 目标系统
        if self.goals:
            data["goals"] = [
                {
                    "goal_type": g.goal_type.value if hasattr(g.goal_type, 'value') else str(g.goal_type),
                    "description": g.description,
                    "target_value": g.target_value,
                    "current_value": g.current_value,
                    "priority": g.priority,
                    "is_completed": g.is_completed,
                    "is_failed": g.is_failed,
                    "created_at": g.created_at,
                    "deadline": g.deadline,
                    "npc_id": g.npc_id,
                    "reward_emotion": g.reward_emotion,
                    "penalty_emotion": g.penalty_emotion,
                }
                for g in self.goals
            ]
        
        # 日程系统
        if self.schedule:
            data["schedule"] = {
                str(hour): {
                    "activity_type": activity.activity_type.value if hasattr(activity.activity_type, 'value') else str(activity.activity_type),
                    "start_time": activity.start_time,
                    "duration": activity.duration,
                    "location": activity.location,
                    "priority": activity.priority,
                    "is_temporary": activity.is_temporary,
                    "description": activity.description,
                }
                for hour, activity in self.schedule.items()
            }
        
        # 价值观系统
        if self.values:
            data["values"] = self.values.to_dict() if hasattr(self.values, 'to_dict') else {}
        
        # 说话风格
        if self.speaking_style:
            data["speaking_style"] = self.speaking_style.to_dict() if hasattr(self.speaking_style, 'to_dict') else {}
        
        # 成长记录
        if self.life_record:
            data["life_record"] = self.life_record.to_dict() if hasattr(self.life_record, 'to_dict') else {}
        
        # 增强记忆系统
        if self.enhanced_memory:
            data["enhanced_memory"] = self.enhanced_memory.to_dict() if hasattr(self.enhanced_memory, 'to_dict') else {}
        
        # 主动行为冷却
        if self.proactive_cooldowns:
            data["proactive_cooldowns"] = self.proactive_cooldowns
        
        # 独立系统数据
        if self.independent:
            data["independent"] = self.independent.to_dict() if hasattr(self.independent, 'to_dict') else {}
        
        return data
    
    def save_to_database(self, db=None) -> bool:
        """
        保存NPC到数据库
        
        Args:
            db: 数据库实例，如果为None则创建新实例
            
        Returns:
            是否保存成功
        """
        try:
            from storage.database import Database
            if db is None:
                db = Database()
            
            # 获取NPC数据字典
            npc_data = self.to_dict()
            
            # 保存到数据库
            db.save_npc_full(npc_data)
            return True
        except Exception as e:
            print(f"保存NPC到数据库失败: {e}")
            return False
    
    @classmethod
    def load_from_database(cls, npc_id: str, db=None) -> Optional['NPC']:
        """
        从数据库加载NPC
        
        Args:
            npc_id: NPC ID
            db: 数据库实例，如果为None则创建新实例
            
        Returns:
            NPC对象，如果不存在则返回None
        """
        try:
            from storage.database import Database
            if db is None:
                db = Database()
            
            # 从数据库加载完整数据
            npc_data = db.load_npc_full(npc_id)
            if npc_data is None:
                return None
            
            # 从字典创建NPC
            return cls.from_dict(npc_data)
        except Exception as e:
            print(f"从数据库加载NPC失败: {e}")
            return None
    
    def update_in_database(self, db=None) -> bool:
        """
        更新NPC在数据库中的数据
        
        Args:
            db: 数据库实例，如果为None则创建新实例
            
        Returns:
            是否更新成功
        """
        return self.save_to_database(db)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPC':
        """
        从字典创建NPC

        Args:
            data: 包含NPC数据的字典

        Returns:
            NPC对象
        """
        # 确保数据是字典类型
        if not isinstance(data, dict):
            raise ValueError(f"from_dict期望接收字典类型，但收到了 {type(data).__name__}")
        
        # 创建NPCData对象，使用默认值确保向后兼容
        # 处理realm_level可能是字符串的情况
        realm_level_raw = data.get("realm_level", 0)
        if isinstance(realm_level_raw, str):
            from config import REALM_NAME_TO_LEVEL
            # 先尝试从境界名称映射
            realm_level = REALM_NAME_TO_LEVEL.get(realm_level_raw, None)
            if realm_level is None:
                # 如果不是境界名称，尝试作为数字解析
                if realm_level_raw.isdigit():
                    realm_level = int(realm_level_raw)
                else:
                    realm_level = 0
        else:
            realm_level = int(realm_level_raw) if realm_level_raw is not None else 0
        
        # 获取name和dao_name，确保dao_name有值
        name = data.get("name", "")
        dao_name = data.get("dao_name", "")
        # 如果dao_name为空，使用name作为后备
        if not dao_name:
            dao_name = name
        # 如果name为空，使用dao_name作为后备
        if not name:
            name = dao_name
        
        npc_data = NPCData(
            id=data.get("id", f"npc_{random.randint(10000, 99999)}"),
            name=name,
            dao_name=dao_name,
            age=data.get("age", 20),
            lifespan=data.get("lifespan", 100),
            realm_level=realm_level,
            sect=data.get("sect", "散修"),
            personality=data.get("personality", "普通"),
            occupation=data.get("occupation", "散修"),
            location=data.get("location", "新手村"),
            sect_type=data.get("sect_type", ""),
            sect_specialty=data.get("sect_specialty", ""),
            favor=data.get("favor", {}),
            is_alive=data.get("is_alive", True),
            death_info=data.get("death_info", {}),
            can_resurrect=data.get("can_resurrect", True),
            morality=data.get("morality", 0),
            attack=data.get("attack", 10),
            defense=data.get("defense", 5),
            speed=data.get("speed", 8),
            crit_rate=data.get("crit_rate", 0.03),
            dodge_rate=data.get("dodge_rate", 0.03),
            combat_wins=data.get("combat_wins", 0),
            combat_losses=data.get("combat_losses", 0),
        )

        # 创建NPC对象
        npc = cls(npc_data)

        # 恢复战斗记录（如果存在）
        if "combat_record" in data:
            npc.combat_record = data["combat_record"]
        
        # ========== 恢复新系统数据 ==========
        # 恢复目标系统
        if "goals" in data:
            npc.goals = []
            for goal_data in data["goals"]:
                try:
                    from game.npc_goal_system import GoalType
                    goal_type_str = goal_data.get("goal_type", "突破境界")
                    # 处理可能是枚举或字符串的情况
                    if isinstance(goal_type_str, str):
                        goal_type = GoalType(goal_type_str)
                    else:
                        goal_type = goal_type_str
                    
                    goal = Goal(
                        goal_type=goal_type,
                        description=goal_data.get("description", ""),
                        target_value=goal_data.get("target_value", 100.0),
                        current_value=goal_data.get("current_value", 0.0),
                        priority=goal_data.get("priority", 5),
                        is_completed=goal_data.get("is_completed", False),
                        is_failed=goal_data.get("is_failed", False),
                        created_at=goal_data.get("created_at", 0),
                        deadline=goal_data.get("deadline"),
                        npc_id=npc.data.id,
                        reward_emotion=goal_data.get("reward_emotion", "满足"),
                        penalty_emotion=goal_data.get("penalty_emotion", "沮丧"),
                    )
                    npc.goals.append(goal)
                except (ValueError, KeyError) as e:
                    # 如果目标类型无效，跳过这个目标
                    continue
        
        # 恢复日程系统
        if "schedule" in data:
            npc.schedule = {}
            schedule_load_failed = False
            for hour_str, activity_data in data["schedule"].items():
                try:
                    # 确保小时键正确转换为整数
                    hour = int(hour_str)
                    # 使用Activity.from_dict()方法正确还原Activity对象
                    activity = Activity.from_dict(activity_data)
                    npc.schedule[hour] = activity
                except (ValueError, KeyError, TypeError) as e:
                    # 如果活动数据无效，标记加载失败
                    schedule_load_failed = True
                    continue
            
            # 如果日程加载失败或为空，生成新的日程作为回退
            if schedule_load_failed or not npc.schedule:
                npc._generate_daily_schedule()
        
        # 恢复价值观系统
        if "values" in data and data["values"]:
            npc.values = ValuesSystem()
            if hasattr(npc.values, 'from_dict'):
                npc.values.from_dict(data["values"])
        
        # 恢复说话风格
        if "speaking_style" in data and data["speaking_style"]:
            npc.speaking_style = SpeakingStyle()
            if hasattr(npc.speaking_style, 'from_dict'):
                npc.speaking_style.from_dict(data["speaking_style"])
        
        # 恢复成长记录
        if "life_record" in data and data["life_record"]:
            npc.life_record = NPCLifeRecord(npc.data.id, npc.data.name)
            if hasattr(npc.life_record, 'from_dict'):
                npc.life_record.from_dict(data["life_record"])
        
        # 恢复增强记忆系统
        if "enhanced_memory" in data and data["enhanced_memory"]:
            npc.enhanced_memory = EnhancedMemorySystem(npc.data.id)
            if hasattr(npc.enhanced_memory, 'from_dict'):
                npc.enhanced_memory.from_dict(data["enhanced_memory"])
        
        # 恢复主动行为冷却
        if "proactive_cooldowns" in data:
            npc.proactive_cooldowns = data["proactive_cooldowns"]
        
        # 恢复独立系统数据
        if "independent" in data and data["independent"]:
            independent_data = data["independent"]
            # 恢复需求
            if "needs" in independent_data and hasattr(npc.independent, 'needs'):
                for need_type_name, need_data in independent_data["needs"].items():
                    try:
                        from game.npc_independent import NeedType
                        need_type = NeedType[need_type_name]
                        if need_type in npc.independent.needs:
                            npc.independent.needs[need_type].value = need_data.get("value", 50.0)
                            npc.independent.needs[need_type].decay_rate = need_data.get("decay_rate", 1.0)
                    except (KeyError, ValueError):
                        continue
            
            # 恢复性格
            if "personality" in independent_data and hasattr(npc.independent, 'personality'):
                personality_data = independent_data["personality"]
                # 处理 personality_data 可能是字符串（旧数据格式）的情况
                if isinstance(personality_data, dict):
                    npc.independent.personality.bravery = personality_data.get("bravery", 0.5)
                    npc.independent.personality.greed = personality_data.get("greed", 0.5)
                    npc.independent.personality.kindness = personality_data.get("kindness", 0.5)
                    npc.independent.personality.diligence = personality_data.get("diligence", 0.5)
                    npc.independent.personality.curiosity = personality_data.get("curiosity", 0.5)
                elif isinstance(personality_data, str):
                    # 如果是字符串（性格描述），保持默认性格值
                    # 可以根据性格描述调整默认值
                    pass
            
            # 恢复记忆
            if "memories" in independent_data and hasattr(npc.independent, 'memories'):
                from game.npc_independent import Memory
                npc.independent.memories = []
                for mem_data in independent_data["memories"]:
                    try:
                        memory = Memory(
                            content=mem_data.get("content", ""),
                            importance=mem_data.get("importance", 5),
                            timestamp=mem_data.get("timestamp", 0),
                            emotion=mem_data.get("emotion", "neutral"),
                            fade_rate=mem_data.get("fade_rate", 0.1)
                        )
                        npc.independent.memories.append(memory)
                    except Exception:
                        continue
            
            # 恢复关系
            if "relationships" in independent_data and hasattr(npc.independent, 'relationships'):
                from game.npc_independent import Relationship
                npc.independent.relationships = {}
                for rel_id, rel_data in independent_data["relationships"].items():
                    try:
                        relationship = Relationship(
                            npc_id=rel_id,
                            affinity=rel_data.get("affinity", 0.0),
                            familiarity=rel_data.get("familiarity", 0.0),
                            last_interaction=rel_data.get("last_interaction", 0.0)
                        )
                        npc.independent.relationships[rel_id] = relationship
                    except Exception:
                        continue
            
            # 恢复独立系统目标
            if "goals" in independent_data and hasattr(npc.independent, 'goals'):
                from game.npc_independent import NPCGoal, GoalType
                npc.independent.goals = []
                for goal_data in independent_data["goals"]:
                    try:
                        goal_type_str = goal_data.get("goal_type", "BREAKTHROUGH")
                        if isinstance(goal_type_str, str):
                            goal_type = GoalType[goal_type_str]
                        else:
                            goal_type = goal_type_str
                        
                        goal = NPCGoal(
                            goal_type=goal_type,
                            description=goal_data.get("description", ""),
                            target_value=goal_data.get("target_value", 100.0),
                            current_value=goal_data.get("current_value", 0.0),
                            priority=goal_data.get("priority", 5),
                            is_completed=goal_data.get("is_completed", False),
                            created_at=goal_data.get("created_at", 0)
                        )
                        npc.independent.goals.append(goal)
                    except (ValueError, KeyError):
                        continue
            
            # 恢复统计数据
            if "total_actions" in independent_data:
                npc.independent.total_actions = independent_data["total_actions"]
            if "total_interactions" in independent_data:
                npc.independent.total_interactions = independent_data["total_interactions"]

        return npc

    def __str__(self) -> str:
        return f"{self.data.dao_name} ({self.get_realm_name()})"
