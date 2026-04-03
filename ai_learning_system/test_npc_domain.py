"""NPC领域模型测试"""

import pytest
from domain.entities.npc import NPC
from domain.value_objects.npc import (
    NPCMemory, Relationship, Dialogue, EmotionType, 
    MemoryCategory, RelationshipType, ScheduleActivity, 
    Personality, PersonalityTrait, CultivationInfo, NPCStats
)
from domain.services.npc_service import NPCService
from domain.services.npc_behavior_service import NPCBehaviorService
from domain.services.npc_dialogue_service import NPCDialogueService


class TestNPCDomain:
    """NPC领域模型测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.npc_service = NPCService()
        self.behavior_service = NPCBehaviorService()
        self.dialogue_service = NPCDialogueService()
    
    def test_npc_creation(self):
        """测试NPC创建"""
        npc_data = {
            "id": "npc_001",
            "name": "测试NPC",
            "dao_name": "测试道人",
            "age": 50,
            "realm_level": 2,
            "realm_name": "练气期",
            "lifespan": 200,
            "sect": "测试门派",
            "sect_type": "正道",
            "sect_specialty": "剑道",
            "occupation": "剑修",
            "location": "新手村",
            "morality": 50,
            "attack": 20,
            "defense": 10,
            "speed": 15,
            "crit_rate": 0.05,
            "dodge_rate": 0.05,
            "personality": {
                "traits": {
                    "diligence": 0.8,
                    "bravery": 0.7,
                    "wisdom": 0.6,
                    "kindness": 0.9,
                    "ambition": 0.5,
                    "patience": 0.7,
                    "temper": 0.3
                },
                "personality_type": "friendly"
            }
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        assert npc.id == "npc_001"
        assert npc.name == "测试NPC"
        assert npc.dao_name == "测试道人"
        assert npc.age == 50
        assert npc.cultivation_info.realm_level == 2
        assert npc.cultivation_info.realm_name == "练气期"
        assert npc.cultivation_info.lifespan == 200
        assert npc.sect == "测试门派"
        assert npc.occupation == "剑修"
        assert npc.location == "新手村"
        assert npc.morality == 50
        assert npc.get_stats().attack == 20
        assert npc.get_stats().defense == 10
        assert npc.get_stats().speed == 15
        assert npc.get_stats().crit_rate == 0.05
        assert npc.get_stats().dodge_rate == 0.05
        assert npc.get_personality().personality_type == "friendly"
    
    def test_memory_management(self):
        """测试记忆管理"""
        npc_data = {
            "id": "npc_002",
            "name": "记忆测试NPC",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        # 添加记忆
        memory1 = NPCMemory(
            content="测试记忆1",
            importance=8,
            timestamp=1000,
            emotion=EmotionType.POSITIVE,
            category=MemoryCategory.ACHIEVEMENT
        )
        
        memory2 = NPCMemory(
            content="测试记忆2",
            importance=5,
            timestamp=2000,
            emotion=EmotionType.NEUTRAL,
            category=MemoryCategory.DAILY
        )
        
        npc.add_memory(memory1)
        npc.add_memory(memory2)
        
        # 测试获取记忆
        memories = npc.get_memories()
        assert len(memories) == 2
        assert memories[0].content == "测试记忆1"
        assert memories[1].content == "测试记忆2"
        
        # 测试按类别获取记忆
        achievement_memories = npc.get_memories(MemoryCategory.ACHIEVEMENT)
        assert len(achievement_memories) == 1
        assert achievement_memories[0].content == "测试记忆1"
        
        # 测试获取最近记忆
        recent_memories = npc.get_recent_memories(1)
        assert len(recent_memories) == 1
        assert recent_memories[0].content == "测试记忆2"
    
    def test_relationship_management(self):
        """测试关系管理"""
        npc_data1 = {
            "id": "npc_003",
            "name": "关系测试NPC1",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc_data2 = {
            "id": "npc_004",
            "name": "关系测试NPC2",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc1 = self.npc_service.create_npc(npc_data1)
        npc2 = self.npc_service.create_npc(npc_data2)
        
        # 添加关系
        relationship = Relationship(
            npc_id="npc_004",
            relationship_type=RelationshipType.FRIEND,
            affinity=50,
            intimacy=30,
            hatred=0,
            last_interaction=1000
        )
        
        npc1.add_relationship(relationship)
        
        # 测试获取关系
        retrieved_relationship = npc1.get_relationship("npc_004")
        assert retrieved_relationship is not None
        assert retrieved_relationship.relationship_type == RelationshipType.FRIEND
        assert retrieved_relationship.affinity == 50
        
        # 测试更新关系
        npc1.update_relationship("npc_004", affinity=60, intimacy=40)
        updated_relationship = npc1.get_relationship("npc_004")
        assert updated_relationship.affinity == 60
        assert updated_relationship.intimacy == 40
        
        # 测试获取所有关系
        relationships = npc1.get_all_relationships()
        assert len(relationships) == 1
        assert "npc_004" in relationships
    
    def test_favor_management(self):
        """测试好感度管理"""
        npc_data = {
            "id": "npc_005",
            "name": "好感度测试NPC",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        # 测试初始好感度
        assert npc.get_favor("玩家1") == 0
        
        # 测试更新好感度
        npc.update_favor("玩家1", 20)
        assert npc.get_favor("玩家1") == 20
        
        # 测试好感度上限
        npc.update_favor("玩家1", 100)
        assert npc.get_favor("玩家1") == 100
        
        # 测试好感度下限
        npc.update_favor("玩家1", -200)
        assert npc.get_favor("玩家1") == -100
    
    def test_behavior_system(self):
        """测试行为系统"""
        npc_data = {
            "id": "npc_006",
            "name": "行为测试NPC",
            "age": 30,
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100,
            "occupation": "铁匠"
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        # 测试决策
        context = {"current_hour": 12}
        decision = self.behavior_service.make_decision(npc, context)
        assert decision in ["cultivate", "socialize", "explore", "rest", "work"]
        
        # 测试执行活动
        activity_result = self.behavior_service.execute_activity(npc, "cultivate", context)
        assert activity_result["success"] == True
        assert "cultivation" in activity_result["effects"]
        
        # 测试与玩家互动
        dialogue = self.behavior_service.interact_with_player(npc, "玩家1", "greet", context)
        assert isinstance(dialogue, Dialogue)
        assert "道友" in dialogue.content
    
    def test_dialogue_system(self):
        """测试对话系统"""
        npc_data = {
            "id": "npc_007",
            "name": "对话测试NPC",
            "dao_name": "对话道人",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100,
            "personality": {
                "traits": {
                    "kindness": 0.8
                },
                "personality_type": "friendly"
            }
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        # 测试生成问候语
        greeting = self.dialogue_service.generate_greeting(npc, "玩家1")
        assert "玩家1" in greeting
        # 检查问候语是否包含问候相关的词语
        assert any(word in greeting for word in ["你好", "道友", "见到你", "好久不见", "安好"])
        
        # 测试生成告别语
        farewell = self.dialogue_service.generate_farewell(npc, "玩家1")
        assert "再见" in farewell or "慢走" in farewell or "后会有期" in farewell or "有缘再会" in farewell
        
        # 测试生成回应
        context = {"player_name": "玩家1"}
        response = self.dialogue_service.generate_response(npc, "你好", context)
        assert isinstance(response, Dialogue)
        assert "玩家1" in response.content
    
    def test_npc_service(self):
        """测试NPC服务"""
        npc_data = {
            "id": "npc_008",
            "name": "服务测试NPC",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        # 测试创建NPC
        npc = self.npc_service.create_npc(npc_data)
        assert npc.id == "npc_008"
        
        # 测试获取NPC
        retrieved_npc = self.npc_service.get_npc("npc_008")
        assert retrieved_npc is not None
        assert retrieved_npc.id == "npc_008"
        
        # 测试获取所有NPC
        npcs = self.npc_service.get_all_npcs()
        assert len(npcs) >= 1
        
        # 测试处理NPC回合
        context = {"current_hour": 12, "timestamp": 1000}
        result = self.npc_service.process_npc_turn(npc, context)
        assert "npc_id" in result
        assert "decision" in result
        assert "effects" in result
        
        # 测试获取NPC状态
        status = self.npc_service.get_npc_status(npc)
        assert "id" in status
        assert "name" in status
        assert "realm" in status
        assert "combat_power" in status
    
    def test_combat_power_calculation(self):
        """测试战斗力计算"""
        npc_data = {
            "id": "npc_009",
            "name": "战斗力测试NPC",
            "realm_level": 3,
            "realm_name": "筑基期",
            "lifespan": 300,
            "attack": 50,
            "defense": 30,
            "speed": 20,
            "crit_rate": 0.1,
            "dodge_rate": 0.1
        }
        
        npc = self.npc_service.create_npc(npc_data)
        combat_power = npc.get_combat_power()
        assert combat_power > 0
        
        # 测试领域服务的战斗力计算
        service_combat_power = self.npc_service.calculate_combat_power(npc)
        assert service_combat_power == combat_power
    
    def test_time_advancement(self):
        """测试时间推进"""
        npc_data = {
            "id": "npc_010",
            "name": "时间测试NPC",
            "age": 50,
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc = self.npc_service.create_npc(npc_data)
        assert npc.age == 50
        
        # 推进时间
        self.npc_service.advance_time(npc, 365)  # 1年
        assert npc.age == 51
        
        # 测试寿元耗尽
        self.npc_service.advance_time(npc, 50 * 365)  # 50年
        assert npc.age == 101
        assert not npc.is_alive
    
    def test_schedule_management(self):
        """测试日程管理"""
        npc_data = {
            "id": "npc_011",
            "name": "日程测试NPC",
            "realm_level": 1,
            "realm_name": "凡人",
            "lifespan": 100
        }
        
        npc = self.npc_service.create_npc(npc_data)
        
        # 添加日程活动
        activity = ScheduleActivity(
            activity_type="cultivate",
            start_time=8,
            duration=4,
            location="修炼室",
            priority=8
        )
        
        self.npc_service.add_schedule_activity(npc, activity)
        
        # 测试获取日程
        schedule = npc.get_schedule()
        assert 8 in schedule
        assert schedule[8].activity_type == "cultivate"
        
        # 测试获取当前活动
        current_activity = npc.get_current_activity(8)
        assert current_activity is not None
        assert current_activity.activity_type == "cultivate"


if __name__ == "__main__":
    pytest.main([__file__])
