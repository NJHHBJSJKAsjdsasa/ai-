"""NPC领域服务"""

from typing import Dict, List, Optional, Tuple
from domain.entities.npc import NPC
from domain.value_objects.npc import (
    NPCMemory, Relationship, Dialogue, EmotionType, 
    MemoryCategory, RelationshipType, ScheduleActivity, 
    Personality, PersonalityTrait, CultivationInfo, NPCStats
)
from domain.services.npc_behavior_service import NPCBehaviorService
from domain.services.npc_dialogue_service import NPCDialogueService


class NPCService:
    """NPC领域服务"""
    
    def __init__(self):
        """初始化NPC服务"""
        self.behavior_service = NPCBehaviorService()
        self.dialogue_service = NPCDialogueService()
        self.npcs: Dict[str, NPC] = {}  # NPC缓存
    
    def create_npc(self, npc_data: Dict) -> NPC:
        """
        创建NPC
        
        Args:
            npc_data: NPC数据
            
        Returns:
            NPC实体
        """
        # 创建修炼信息
        cultivation_info = CultivationInfo(
            realm_level=npc_data['realm_level'],
            realm_name=npc_data['realm_name'],
            lifespan=npc_data['lifespan'],
            cultivation_speed=npc_data.get('cultivation_speed', 1.0)
        )
        
        # 创建属性
        stats = NPCStats(
            attack=npc_data.get('attack', 10),
            defense=npc_data.get('defense', 5),
            speed=npc_data.get('speed', 8),
            crit_rate=npc_data.get('crit_rate', 0.03),
            dodge_rate=npc_data.get('dodge_rate', 0.03)
        )
        
        # 创建NPC
        npc = NPC(
            id=npc_data['id'],
            name=npc_data['name'],
            dao_name=npc_data.get('dao_name', npc_data['name']),
            age=npc_data.get('age', 20),
            cultivation_info=cultivation_info,
            sect=npc_data.get('sect', ''),
            sect_type=npc_data.get('sect_type', ''),
            sect_specialty=npc_data.get('sect_specialty', ''),
            occupation=npc_data.get('occupation', ''),
            location=npc_data.get('location', ''),
            morality=npc_data.get('morality', 0),
            is_alive=npc_data.get('is_alive', True),
            can_resurrect=npc_data.get('can_resurrect', True),
            death_info=npc_data.get('death_info', {})
        )
        
        # 设置属性
        npc.update_stats(stats)
        
        # 设置个性（如果提供）
        if 'personality' in npc_data:
            personality_data = npc_data['personality']
            traits = {}
            for trait_name, value in personality_data.get('traits', {}).items():
                try:
                    # 转换为大写并处理下划线
                    trait_key = trait_name.upper().replace('_', '')
                    trait = PersonalityTrait[trait_key]
                    traits[trait] = value
                except (ValueError, KeyError):
                    pass
            
            # 即使没有 traits 也创建个性对象
            personality = Personality(
                traits=traits,
                personality_type=personality_data.get('personality_type', 'calm')
            )
            npc.set_personality(personality)
        
        # 缓存NPC
        self.npcs[npc.id] = npc
        
        return npc
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """
        获取NPC
        
        Args:
            npc_id: NPC ID
            
        Returns:
            NPC实体
        """
        return self.npcs.get(npc_id)
    
    def get_all_npcs(self) -> List[NPC]:
        """
        获取所有NPC
        
        Returns:
            NPC列表
        """
        return list(self.npcs.values())
    
    def update_npc(self, npc: NPC):
        """
        更新NPC
        
        Args:
            npc: NPC实体
        """
        self.npcs[npc.id] = npc
    
    def remove_npc(self, npc_id: str):
        """
        移除NPC
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.npcs:
            del self.npcs[npc_id]
    
    def process_npc_turn(self, npc: NPC, context: Dict) -> Dict:
        """
        处理NPC回合
        
        Args:
            npc: NPC实体
            context: 上下文
            
        Returns:
            处理结果
        """
        # 做出决策
        decision = self.behavior_service.make_decision(npc, context)
        
        # 执行决策
        result = {
            "npc_id": npc.id,
            "decision": decision,
            "effects": {}
        }
        
        if decision == "dead":
            result["effects"]["status"] = "dead"
        elif decision.startswith("execute_activity:"):
            activity_type = decision.split(":")[1]
            activity_result = self.behavior_service.execute_activity(npc, activity_type, context)
            result["effects"]["activity"] = activity_result
        else:
            # 执行其他行为
            if decision == "cultivate":
                activity_result = self.behavior_service.execute_activity(npc, "cultivate", context)
                result["effects"]["activity"] = activity_result
            elif decision == "socialize":
                # 寻找附近的NPC进行社交
                nearby_npcs = [n for n in self.npcs.values() if n.id != npc.id and n.is_alive]
                if nearby_npcs:
                    target_npc = nearby_npcs[0]  # 简单选择第一个
                    dialogue1, dialogue2 = self.behavior_service.interact_with_npc(npc, target_npc, context)
                    result["effects"]["dialogue"] = {
                        "npc1": dialogue1.content,
                        "npc2": dialogue2.content
                    }
            elif decision == "explore":
                activity_result = self.behavior_service.execute_activity(npc, "explore", context)
                result["effects"]["activity"] = activity_result
            elif decision == "rest":
                activity_result = self.behavior_service.execute_activity(npc, "rest", context)
                result["effects"]["activity"] = activity_result
            elif decision == "work":
                activity_result = self.behavior_service.execute_activity(npc, "work", context)
                result["effects"]["activity"] = activity_result
        
        # 更新NPC状态
        self.update_npc(npc)
        
        return result
    
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
        if action == "greet":
            # 使用对话服务生成问候语
            return self.dialogue_service.generate_dialogue(npc, player_name, "greeting", context)
        elif action == "farewell":
            # 使用对话服务生成告别语
            return self.dialogue_service.generate_dialogue(npc, player_name, "farewell", context)
        elif action == "ask_about_cultivation":
            # 使用对话服务生成修炼建议
            return self.dialogue_service.generate_dialogue(npc, player_name, "advice", context)
        else:
            # 使用行为服务处理其他互动
            return self.behavior_service.interact_with_player(npc, player_name, action, context)
    
    def interact_between_npcs(self, npc1: NPC, npc2: NPC, context: Dict) -> Tuple[Dialogue, Dialogue]:
        """
        NPC之间的互动
        
        Args:
            npc1: 发起互动的NPC
            npc2: 被互动的NPC
            context: 互动上下文
            
        Returns:
            两个NPC的对话
        """
        # 使用行为服务处理NPC之间的互动
        return self.behavior_service.interact_with_npc(npc1, npc2, context)
    
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
        return self.dialogue_service.generate_dialogue(npc, player_name, dialogue_type, context)
    
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
        return self.dialogue_service.generate_response(npc, player_input, context)
    
    def add_schedule_activity(self, npc: NPC, activity: ScheduleActivity):
        """
        添加日程活动
        
        Args:
            npc: NPC实体
            activity: 日程活动
        """
        npc.add_schedule_activity(activity)
        self.update_npc(npc)
    
    def update_relationship(self, npc: NPC, target_npc_id: str, **kwargs):
        """
        更新关系
        
        Args:
            npc: NPC实体
            target_npc_id: 目标NPC ID
            **kwargs: 关系更新参数
        """
        npc.update_relationship(target_npc_id, **kwargs)
        self.update_npc(npc)
    
    def add_memory(self, npc: NPC, memory: NPCMemory):
        """
        添加记忆
        
        Args:
            npc: NPC实体
            memory: 记忆对象
        """
        npc.add_memory(memory)
        self.update_npc(npc)
    
    def advance_time(self, npc: NPC, days: int = 1):
        """
        推进时间
        
        Args:
            npc: NPC实体
            days: 天数
        """
        npc.advance_age(days)
        self.update_npc(npc)
    
    def calculate_combat_power(self, npc: NPC) -> int:
        """
        计算战斗力
        
        Args:
            npc: NPC实体
            
        Returns:
            战斗力
        """
        return npc.get_combat_power()
    
    def get_npc_status(self, npc: NPC) -> Dict:
        """
        获取NPC状态
        
        Args:
            npc: NPC实体
            
        Returns:
            NPC状态
        """
        return {
            "id": npc.id,
            "name": npc.name,
            "dao_name": npc.dao_name,
            "age": npc.age,
            "realm": npc.cultivation_info.realm_name,
            "realm_level": npc.cultivation_info.realm_level,
            "sect": npc.sect,
            "occupation": npc.occupation,
            "location": npc.location,
            "morality": npc.morality,
            "morality_description": npc.get_morality_description(),
            "is_alive": npc.is_alive,
            "combat_power": npc.get_combat_power(),
            "stats": {
                "attack": npc.get_stats().attack,
                "defense": npc.get_stats().defense,
                "speed": npc.get_stats().speed,
                "crit_rate": npc.get_stats().crit_rate,
                "dodge_rate": npc.get_stats().dodge_rate
            },
            "memories_count": len(npc.get_memories()),
            "relationships_count": len(npc.get_all_relationships()),
            "goals_count": len(npc.get_goals())
        }
    
    def save_npc(self, npc: NPC) -> Dict:
        """
        保存NPC
        
        Args:
            npc: NPC实体
            
        Returns:
            保存的数据
        """
        return npc.to_dict()
    
    def load_npc(self, data: Dict) -> NPC:
        """
        加载NPC
        
        Args:
            data: NPC数据
            
        Returns:
            NPC实体
        """
        npc = NPC.from_dict(data)
        self.npcs[npc.id] = npc
        return npc
