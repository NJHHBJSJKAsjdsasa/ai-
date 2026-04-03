"""NPC行为服务"""

from typing import Dict, List, Optional, Tuple
from domain.entities.npc import NPC
from domain.value_objects.npc import (
    NPCMemory, Relationship, Dialogue, EmotionType, 
    MemoryCategory, RelationshipType, ScheduleActivity
)
import random


class NPCBehaviorService:
    """NPC行为服务"""
    
    def __init__(self):
        """初始化行为服务"""
        self.behavior_cooldowns: Dict[str, float] = {}  # NPC行为冷却
    
    def make_decision(self, npc: NPC, context: Dict) -> str:
        """
        NPC决策
        
        Args:
            npc: NPC实体
            context: 决策上下文
            
        Returns:
            决策结果
        """
        # 基于NPC状态和上下文做出决策
        if not npc.is_alive:
            return "dead"
        
        # 检查当前活动
        current_hour = context.get('current_hour', 0)
        current_activity = npc.get_current_activity(current_hour)
        
        if current_activity:
            # 执行当前日程活动
            return f"execute_activity:{current_activity.activity_type}"
        
        # 基于优先级的决策
        priorities = {
            "cultivate": self._calculate_cultivate_priority(npc),
            "socialize": self._calculate_socialize_priority(npc),
            "explore": self._calculate_explore_priority(npc),
            "rest": self._calculate_rest_priority(npc),
            "work": self._calculate_work_priority(npc)
        }
        
        # 选择优先级最高的行为
        best_behavior = max(priorities.items(), key=lambda x: x[1])[0]
        return best_behavior
    
    def _calculate_cultivate_priority(self, npc: NPC) -> float:
        """计算修炼优先级"""
        # 基于境界和年龄计算优先级
        priority = 5.0
        
        # 年轻NPC更倾向于修炼
        if npc.age < 100:
            priority += 2.0
        
        # 低境界NPC更倾向于修炼
        if npc.cultivation_info.realm_level < 3:
            priority += 3.0
        
        return priority
    
    def _calculate_socialize_priority(self, npc: NPC) -> float:
        """计算社交优先级"""
        priority = 3.0
        
        # 基于个性计算社交倾向
        personality = npc.get_personality()
        if personality:
            # 善良的NPC更倾向于社交
            if personality.traits.get('KINDNESS', 0) > 0.6:
                priority += 2.0
        
        return priority
    
    def _calculate_explore_priority(self, npc: NPC) -> float:
        """计算探索优先级"""
        priority = 2.0
        
        # 年轻且勇敢的NPC更倾向于探索
        if npc.age < 150:
            priority += 1.0
        
        personality = npc.get_personality()
        if personality:
            if personality.traits.get('BRAVERY', 0) > 0.7:
                priority += 2.0
        
        return priority
    
    def _calculate_rest_priority(self, npc: NPC) -> float:
        """计算休息优先级"""
        priority = 1.0
        
        # 年龄大的NPC需要更多休息
        if npc.age > 300:
            priority += 3.0
        
        return priority
    
    def _calculate_work_priority(self, npc: NPC) -> float:
        """计算工作优先级"""
        priority = 2.0
        
        # 有职业的NPC更倾向于工作
        if npc.occupation:
            priority += 2.0
        
        return priority
    
    def interact_with_player(self, npc: NPC, player_name: str, action: str, context: Dict) -> Dialogue:
        """
        NPC与玩家互动
        
        Args:
            npc: NPC实体
            player_name: 玩家名字
            action: 玩家动作
            context: 互动上下文
            
        Returns:
            对话对象
        """
        favor = npc.get_favor(player_name)
        
        # 根据好感度和动作生成对话
        if action == "greet":
            dialogue_content = self._generate_greeting(npc, player_name, favor)
        elif action == "ask_about_cultivation":
            dialogue_content = self._generate_cultivation_advice(npc, favor)
        elif action == "ask_about_sect":
            dialogue_content = self._generate_sect_info(npc, favor)
        elif action == "trade":
            dialogue_content = self._generate_trade_response(npc, favor)
        else:
            dialogue_content = f"{player_name}道友，你想做什么？"
        
        # 生成对话对象
        dialogue = Dialogue(
            content=dialogue_content,
            speaker_id=npc.id,
            speaker_name=npc.dao_name,
            context=str(context),
            emotion=self._determine_emotion(favor),
            timestamp=context.get('timestamp', 0)
        )
        
        # 更新好感度
        if action in ["greet", "ask_about_cultivation"]:
            npc.update_favor(player_name, 1)
        
        # 添加互动记忆
        memory_content = f"与{player_name}进行了{action}互动"
        memory = NPCMemory(
            content=memory_content,
            importance=3,
            timestamp=context.get('timestamp', 0),
            emotion=EmotionType.POSITIVE,
            category=MemoryCategory.SOCIAL
        )
        npc.add_memory(memory)
        
        return dialogue
    
    def interact_with_npc(self, npc1: NPC, npc2: NPC, context: Dict) -> Tuple[Dialogue, Dialogue]:
        """
        NPC之间的互动
        
        Args:
            npc1: 发起互动的NPC
            npc2: 被互动的NPC
            context: 互动上下文
            
        Returns:
            两个NPC的对话
        """
        # 检查关系
        relationship = npc1.get_relationship(npc2.id)
        if not relationship:
            # 创建初始关系
            relationship = Relationship(
                npc_id=npc2.id,
                relationship_type=RelationshipType.ACQUAINTANCE,
                affinity=0,
                intimacy=0,
                hatred=0,
                last_interaction=context.get('timestamp', 0)
            )
            npc1.add_relationship(relationship)
        
        # 基于关系生成互动
        affinity = relationship.affinity
        
        # NPC1的对话
        dialogue1_content = self._generate_npc_interaction(npc1, npc2, affinity, context)
        dialogue1 = Dialogue(
            content=dialogue1_content,
            speaker_id=npc1.id,
            speaker_name=npc1.dao_name,
            context=str(context),
            emotion=self._determine_emotion(affinity),
            timestamp=context.get('timestamp', 0)
        )
        
        # NPC2的回应
        dialogue2_content = self._generate_npc_response(npc2, npc1, affinity, context)
        dialogue2 = Dialogue(
            content=dialogue2_content,
            speaker_id=npc2.id,
            speaker_name=npc2.dao_name,
            context=str(context),
            emotion=self._determine_emotion(affinity),
            timestamp=context.get('timestamp', 0)
        )
        
        # 更新关系
        affinity_change = random.randint(-2, 5)
        new_affinity = min(100, max(-100, affinity + affinity_change))
        npc1.update_relationship(npc2.id, affinity=new_affinity, last_interaction=context.get('timestamp', 0))
        
        # 添加互动记忆
        memory_content1 = f"与{npc2.dao_name}交流了一番"
        memory1 = NPCMemory(
            content=memory_content1,
            importance=3,
            timestamp=context.get('timestamp', 0),
            emotion=EmotionType.POSITIVE if affinity_change > 0 else EmotionType.NEUTRAL,
            category=MemoryCategory.SOCIAL
        )
        npc1.add_memory(memory1)
        
        memory_content2 = f"与{npc1.dao_name}交流了一番"
        memory2 = NPCMemory(
            content=memory_content2,
            importance=3,
            timestamp=context.get('timestamp', 0),
            emotion=EmotionType.POSITIVE if affinity_change > 0 else EmotionType.NEUTRAL,
            category=MemoryCategory.SOCIAL
        )
        npc2.add_memory(memory2)
        
        return dialogue1, dialogue2
    
    def _generate_greeting(self, npc: NPC, player_name: str, favor: int) -> str:
        """生成问候语"""
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
    
    def _generate_cultivation_advice(self, npc: NPC, favor: int) -> str:
        """生成修炼建议"""
        if favor >= 0:
            advices = [
                "修炼之道，在于持之以恒，不可急躁。",
                "心境平和是突破境界的关键。",
                "多感悟天地灵气，与自然融为一体。",
                "修炼之余，也要注意休息，劳逸结合。",
            ]
        else:
            advices = [
                "修炼之事，与你何干？",
                "自己的路自己走，问别人作甚？",
                "哼，就你这样也想修炼有成？",
            ]
        
        return random.choice(advices)
    
    def _generate_sect_info(self, npc: NPC, favor: int) -> str:
        """生成门派信息"""
        if favor >= 0:
            if npc.sect:
                return f"我派{self._get_sect_description(npc)}，乃是一方名门正派。"
            else:
                return "我乃散修，无门无派。"
        else:
            return "门派之事，岂容外人知晓？"
    
    def _generate_trade_response(self, npc: NPC, favor: int) -> str:
        """生成交易回应"""
        if favor >= 0:
            return "你想交易什么？我这里有些宝贝，或许你会感兴趣。"
        else:
            return "我与你没什么好交易的。"
    
    def _generate_npc_interaction(self, npc1: NPC, npc2: NPC, affinity: int, context: Dict) -> str:
        """生成NPC互动内容"""
        if affinity >= 30:
            interactions = [
                f"{npc2.dao_name}道友，近来可好？",
                f"{npc2.dao_name}，最近修炼可有突破？",
                f"{npc2.dao_name}，有空一起探讨修炼之道如何？",
            ]
        elif affinity >= -20:
            interactions = [
                f"{npc2.dao_name}道友，有礼了。",
                f"见过{npc2.dao_name}道友。",
                f"{npc2.dao_name}，今日天气不错。",
            ]
        else:
            interactions = [
                f"{npc2.dao_name}，我们之间没什么好说的。",
                f"哼，{npc2.dao_name}...",
                f"离我远点，{npc2.dao_name}。",
            ]
        
        return random.choice(interactions)
    
    def _generate_npc_response(self, npc2: NPC, npc1: NPC, affinity: int, context: Dict) -> str:
        """生成NPC回应内容"""
        if affinity >= 30:
            responses = [
                f"{npc1.dao_name}道友，托你的福，一切安好。",
                f"{npc1.dao_name}，修炼路上还需努力啊。",
                f"好啊，{npc1.dao_name}，我们找个地方详谈。",
            ]
        elif affinity >= -20:
            responses = [
                f"{npc1.dao_name}道友，安好。",
                f"见过{npc1.dao_name}。",
                f"是啊，{npc1.dao_name}，天气不错。",
            ]
        else:
            responses = [
                f"{npc1.dao_name}，我们没什么好说的。",
                f"哼，{npc1.dao_name}...",
                f"我不想和你说话，{npc1.dao_name}。",
            ]
        
        return random.choice(responses)
    
    def _determine_emotion(self, affinity: int) -> EmotionType:
        """根据好感度确定情感"""
        if affinity >= 30:
            return EmotionType.POSITIVE
        elif affinity <= -30:
            return EmotionType.NEGATIVE
        else:
            return EmotionType.NEUTRAL
    
    def _get_sect_description(self, npc: NPC) -> str:
        """获取门派描述"""
        if npc.sect_type:
            return f"{npc.sect}（{npc.sect_type}）"
        return npc.sect
    
    def execute_activity(self, npc: NPC, activity_type: str, context: Dict) -> Dict:
        """
        执行活动
        
        Args:
            npc: NPC实体
            activity_type: 活动类型
            context: 活动上下文
            
        Returns:
            执行结果
        """
        results = {
            "success": True,
            "activity_type": activity_type,
            "effects": {}
        }
        
        if activity_type == "cultivate":
            # 修炼效果
            cultivation_gain = random.randint(1, 5)
            results["effects"]["cultivation"] = cultivation_gain
            
            # 添加修炼记忆
            memory_content = f"进行了修炼，获得了{cultivation_gain}点修为"
            memory = NPCMemory(
                content=memory_content,
                importance=4,
                timestamp=context.get('timestamp', 0),
                emotion=EmotionType.POSITIVE,
                category=MemoryCategory.ACHIEVEMENT
            )
            npc.add_memory(memory)
            
        elif activity_type == "socialize":
            # 社交效果
            results["effects"]["social"] = "与其他修士交流"
            
        elif activity_type == "explore":
            # 探索效果
            discovery = random.choice(["发现了一处灵脉", "找到了一些灵草", "遇到了一只妖兽", "一无所获"])
            results["effects"]["discovery"] = discovery
            
            # 添加探索记忆
            memory_content = f"探索时{discovery}"
            emotion = EmotionType.POSITIVE if "发现" in discovery or "找到" in discovery else EmotionType.NEUTRAL
            memory = NPCMemory(
                content=memory_content,
                importance=3,
                timestamp=context.get('timestamp', 0),
                emotion=emotion,
                category=MemoryCategory.EXPLORATION
            )
            npc.add_memory(memory)
            
        elif activity_type == "rest":
            # 休息效果
            results["effects"]["rest"] = "恢复了精力"
            
        elif activity_type == "work":
            # 工作效果
            if npc.occupation:
                earnings = random.randint(1, 10)
                results["effects"]["earnings"] = earnings
                results["effects"]["occupation"] = npc.occupation
                
                # 添加工作记忆
                memory_content = f"从事{npc.occupation}工作，赚取了{earnings}块灵石"
                memory = NPCMemory(
                    content=memory_content,
                    importance=3,
                    timestamp=context.get('timestamp', 0),
                    emotion=EmotionType.POSITIVE,
                    category=MemoryCategory.DAILY
                )
                npc.add_memory(memory)
        
        return results
