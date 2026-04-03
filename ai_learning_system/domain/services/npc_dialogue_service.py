"""NPC对话服务"""

from typing import Dict, List, Optional
from domain.entities.npc import NPC
from domain.value_objects.npc import (
    Dialogue, EmotionType, Personality, PersonalityTrait
)
import random


class NPCDialogueService:
    """NPC对话服务"""
    
    def __init__(self):
        """初始化对话服务"""
        # 不同个性类型的对话模板
        self.personality_templates = {
            "calm": {
                "greeting": ["{player_name}道友，有礼了。", "见过{player_name}道友。", "{player_name}道友安好。"],
                "question": ["请问有什么事吗？", "不知道友有何指教？", "何事相询？"],
                "advice": ["修炼之道，在于持之以恒。", "心境平和是突破的关键。", "循序渐进，不可急躁。"],
                "farewell": ["道友慢走。", "有缘再会。", "后会有期。"]
            },
            "enthusiastic": {
                "greeting": ["{player_name}道友！好久不见，别来无恙？", "哈哈，{player_name}道友来了，快请进！", "{player_name}道友，今日可要多叙叙旧！"],
                "question": ["道友有什么事尽管说！", "有什么能帮忙的吗？", "快告诉我发生了什么！"],
                "advice": ["修炼就要充满激情！", "突破境界需要一股冲劲！", "放手去做，不要害怕失败！"],
                "farewell": ["道友慢走，有空常来！", "下次再来找我玩啊！", "期待与道友再次相见！"]
            },
            "arrogant": {
                "greeting": ["哼，{player_name}来了。", "{player_name}，你也配和我说话？", "...（傲慢地看着{player_name}）"],
                "question": ["有话快说，有屁快放！", "别浪费我的时间！", "说吧，什么事？"],
                "advice": ["以你的资质，能修炼到这一步已经不错了。", "跟着我学，或许还有点希望。", "记住，实力才是硬道理。"],
                "farewell": ["滚吧，别再打扰我。", "赶紧走，别让我再看到你。", "哼，浪费时间。"]
            },
            "wise": {
                "greeting": ["{player_name}道友，欢迎。", "见过{player_name}小友。", "{player_name}，来了。"],
                "question": ["你心中有什么疑惑？", "请问有什么问题需要解答？", "我能帮你什么？"],
                "advice": ["道可道，非常道。", "万物皆有定数，不必强求。", "内修其心，外练其体。"],
                "farewell": ["愿你早日得道。", "修行之路，任重道远。", "去吧，记住我的话。"]
            },
            "friendly": {
                "greeting": ["{player_name}道友，你好！", "嗨，{player_name}，最近怎么样？", "{player_name}，见到你真高兴！"],
                "question": ["有什么事吗，朋友？", "需要帮忙吗？", "怎么了，{player_name}？"],
                "advice": ["我们一起努力吧！", "有困难随时找我。", "相信自己，你能做到的！"],
                "farewell": ["再见啦，{player_name}！", "回头见！", "下次再聊！"]
            }
        }
        
        # 通用对话模板
        self.generic_templates = {
            "greeting": ["{player_name}道友，有礼了。", "见过{player_name}道友。", "{player_name}道友安好。"],
            "question": ["请问有什么事吗？", "不知道友有何指教？", "何事相询？"],
            "advice": ["修炼之道，在于持之以恒。", "心境平和是突破的关键。", "循序渐进，不可急躁。"],
            "farewell": ["道友慢走。", "有缘再会。", "后会有期。"]
        }
    
    def generate_dialogue(self, npc: NPC, player_name: str, dialogue_type: str, context: Dict) -> Dialogue:
        """
        生成NPC对话
        
        Args:
            npc: NPC实体
            player_name: 玩家名字
            dialogue_type: 对话类型
            context: 对话上下文
            
        Returns:
            对话对象
        """
        # 获取NPC个性
        personality = npc.get_personality()
        personality_type = personality.personality_type if personality else "calm"
        
        # 获取玩家好感度
        favor = npc.get_favor(player_name)
        
        # 生成对话内容
        content = self._generate_dialogue_content(
            npc=npc,
            player_name=player_name,
            dialogue_type=dialogue_type,
            personality_type=personality_type,
            favor=favor,
            context=context
        )
        
        # 确定情感
        emotion = self._determine_emotion(favor, personality_type)
        
        # 创建对话对象
        dialogue = Dialogue(
            content=content,
            speaker_id=npc.id,
            speaker_name=npc.dao_name,
            context=str(context),
            emotion=emotion,
            timestamp=context.get('timestamp', 0)
        )
        
        return dialogue
    
    def _generate_dialogue_content(self, npc: NPC, player_name: str, dialogue_type: str, 
                                  personality_type: str, favor: int, context: Dict) -> str:
        """
        生成对话内容
        
        Args:
            npc: NPC实体
            player_name: 玩家名字
            dialogue_type: 对话类型
            personality_type: 个性类型
            favor: 好感度
            context: 对话上下文
            
        Returns:
            对话内容
        """
        # 根据个性类型选择模板
        templates = self.personality_templates.get(personality_type, self.generic_templates)
        
        # 根据对话类型选择模板
        type_templates = templates.get(dialogue_type, self.generic_templates.get(dialogue_type, []))
        
        if not type_templates:
            return f"{player_name}道友，你想做什么？"
        
        # 根据好感度调整对话
        if favor >= 50:
            # 高好感度，使用更友好的对话
            if dialogue_type == "greeting":
                type_templates = [t for t in type_templates if "！" in t or "快请进" in t]
                if not type_templates:
                    type_templates = templates.get(dialogue_type, self.generic_templates.get(dialogue_type, []))
        elif favor <= -30:
            # 低好感度，使用更冷漠的对话
            if dialogue_type == "greeting":
                type_templates = [t for t in type_templates if "哼" in t or "..." in t]
                if not type_templates:
                    type_templates = templates.get(dialogue_type, self.generic_templates.get(dialogue_type, []))
        
        # 随机选择一个模板
        template = random.choice(type_templates)
        
        # 替换模板中的变量
        content = template.format(player_name=player_name)
        
        # 根据上下文添加额外内容
        content = self._enrich_dialogue(content, npc, context)
        
        return content
    
    def _enrich_dialogue(self, content: str, npc: NPC, context: Dict) -> str:
        """
        根据上下文丰富对话内容
        
        Args:
            content: 基础对话内容
            npc: NPC实体
            context: 对话上下文
            
        Returns:
            丰富后的对话内容
        """
        # 检查是否有特殊上下文
        if context.get('recent_activity'):
            recent_activity = context['recent_activity']
            if recent_activity == "cultivate":
                content += " 最近我一直在潜心修炼，感觉有所突破。"
            elif recent_activity == "explore":
                content += " 前几日我在附近发现了一处有趣的地方。"
            elif recent_activity == "socialize":
                content += " 最近认识了一些新朋友，收获颇丰。"
        
        # 根据NPC状态添加内容
        if npc.cultivation_info.realm_level >= 5:
            content += " 修行之路，任重道远啊。"
        
        return content
    
    def _determine_emotion(self, favor: int, personality_type: str) -> EmotionType:
        """
        根据好感度和个性确定情感
        
        Args:
            favor: 好感度
            personality_type: 个性类型
            
        Returns:
            情感类型
        """
        if favor >= 30:
            return EmotionType.POSITIVE
        elif favor <= -30:
            return EmotionType.NEGATIVE
        else:
            # 根据个性类型调整中性情感
            if personality_type in ["enthusiastic", "friendly"]:
                return EmotionType.POSITIVE
            elif personality_type in ["arrogant"]:
                return EmotionType.NEGATIVE
            else:
                return EmotionType.NEUTRAL
    
    def generate_response(self, npc: NPC, player_input: str, context: Dict) -> Dialogue:
        """
        生成NPC对玩家输入的回应
        
        Args:
            npc: NPC实体
            player_input: 玩家输入
            context: 对话上下文
            
        Returns:
            对话对象
        """
        # 分析玩家输入
        player_name = context.get('player_name', '道友')
        input_lower = player_input.lower()
        
        # 确定对话类型
        if any(word in input_lower for word in ['你好', 'hello', 'hi', '嗨', '问候']):
            dialogue_type = "greeting"
        elif any(word in input_lower for word in ['再见', 'bye', '拜拜', ' farewell']):
            dialogue_type = "farewell"
        elif any(word in input_lower for word in ['修炼', '突破', '境界', '修为']):
            dialogue_type = "advice"
        else:
            dialogue_type = "question"
        
        # 生成对话
        return self.generate_dialogue(npc, player_name, dialogue_type, context)
    
    def generate_npc_to_npc_dialogue(self, npc1: NPC, npc2: NPC, context: Dict) -> tuple[Dialogue, Dialogue]:
        """
        生成NPC之间的对话
        
        Args:
            npc1: 发起对话的NPC
            npc2: 回应的NPC
            context: 对话上下文
            
        Returns:
            两个NPC的对话
        """
        # 获取NPC个性
        personality1 = npc1.get_personality()
        personality_type1 = personality1.personality_type if personality1 else "calm"
        
        personality2 = npc2.get_personality()
        personality_type2 = personality2.personality_type if personality2 else "calm"
        
        # 获取关系
        relationship = npc1.get_relationship(npc2.id)
        affinity = relationship.affinity if relationship else 0
        
        # 生成NPC1的对话
        content1 = self._generate_npc_initiative_dialogue(
            npc1, npc2, personality_type1, affinity, context
        )
        
        # 生成NPC2的回应
        content2 = self._generate_npc_response_dialogue(
            npc2, npc1, personality_type2, affinity, context
        )
        
        # 创建对话对象
        dialogue1 = Dialogue(
            content=content1,
            speaker_id=npc1.id,
            speaker_name=npc1.dao_name,
            context=str(context),
            emotion=self._determine_emotion(affinity, personality_type1),
            timestamp=context.get('timestamp', 0)
        )
        
        dialogue2 = Dialogue(
            content=content2,
            speaker_id=npc2.id,
            speaker_name=npc2.dao_name,
            context=str(context),
            emotion=self._determine_emotion(affinity, personality_type2),
            timestamp=context.get('timestamp', 0)
        )
        
        return dialogue1, dialogue2
    
    def _generate_npc_initiative_dialogue(self, npc1: NPC, npc2: NPC, 
                                         personality_type: str, affinity: int, context: Dict) -> str:
        """
        生成NPC主动对话
        
        Args:
            npc1: 发起对话的NPC
            npc2: 回应的NPC
            personality_type: 个性类型
            affinity: 好感度
            context: 对话上下文
            
        Returns:
            对话内容
        """
        # 基于个性和关系生成对话
        if affinity >= 30:
            # 友好关系
            dialogues = [
                f"{npc2.dao_name}道友，近来可好？",
                f"{npc2.dao_name}，最近修炼可有突破？",
                f"{npc2.dao_name}，有空一起探讨修炼之道如何？",
                f"{npc2.dao_name}，我最近发现了一处不错的修炼场所，一起去看看？"
            ]
        elif affinity >= -20:
            # 一般关系
            dialogues = [
                f"{npc2.dao_name}道友，有礼了。",
                f"见过{npc2.dao_name}道友。",
                f"{npc2.dao_name}，今日天气不错。",
                f"{npc2.dao_name}，最近可有什么新鲜事？"
            ]
        else:
            # 敌对关系
            dialogues = [
                f"{npc2.dao_name}，我们之间没什么好说的。",
                f"哼，{npc2.dao_name}...",
                f"离我远点，{npc2.dao_name}。",
                f"{npc2.dao_name}，别挡我的路！"
            ]
        
        # 根据个性调整对话
        if personality_type == "enthusiastic":
            dialogues = [d + "！" for d in dialogues]
        elif personality_type == "arrogant":
            dialogues = [d.replace("道友", "") for d in dialogues]
        elif personality_type == "wise":
            dialogues = [d + " 道可道，非常道。" for d in dialogues]
        
        return random.choice(dialogues)
    
    def _generate_npc_response_dialogue(self, npc2: NPC, npc1: NPC, 
                                       personality_type: str, affinity: int, context: Dict) -> str:
        """
        生成NPC回应对话
        
        Args:
            npc2: 回应的NPC
            npc1: 发起对话的NPC
            personality_type: 个性类型
            affinity: 好感度
            context: 对话上下文
            
        Returns:
            对话内容
        """
        # 基于个性和关系生成回应
        if affinity >= 30:
            # 友好关系
            responses = [
                f"{npc1.dao_name}道友，托你的福，一切安好。",
                f"{npc1.dao_name}，修炼路上还需努力啊。",
                f"好啊，{npc1.dao_name}，我们找个地方详谈。",
                f"{npc1.dao_name}，你的提议不错，我们一起去吧。"
            ]
        elif affinity >= -20:
            # 一般关系
            responses = [
                f"{npc1.dao_name}道友，安好。",
                f"见过{npc1.dao_name}。",
                f"是啊，{npc1.dao_name}，天气不错。",
                f"{npc1.dao_name}，最近还算平静。"
            ]
        else:
            # 敌对关系
            responses = [
                f"{npc1.dao_name}，我们没什么好说的。",
                f"哼，{npc1.dao_name}...",
                f"我不想和你说话，{npc1.dao_name}。",
                f"{npc1.dao_name}，离我远点！"
            ]
        
        # 根据个性调整回应
        if personality_type == "enthusiastic":
            responses = [r + "！" for r in responses]
        elif personality_type == "arrogant":
            responses = [r.replace("道友", "") for r in responses]
        elif personality_type == "wise":
            responses = [r + " 万物皆有定数。" for r in responses]
        
        return random.choice(responses)
    
    def generate_greeting(self, npc: NPC, player_name: str) -> str:
        """
        生成问候语
        
        Args:
            npc: NPC实体
            player_name: 玩家名字
            
        Returns:
            问候语
        """
        context = {}
        dialogue = self.generate_dialogue(npc, player_name, "greeting", context)
        return dialogue.content
    
    def generate_farewell(self, npc: NPC, player_name: str) -> str:
        """
        生成告别语
        
        Args:
            npc: NPC实体
            player_name: 玩家名字
            
        Returns:
            告别语
        """
        context = {}
        dialogue = self.generate_dialogue(npc, player_name, "farewell", context)
        return dialogue.content
