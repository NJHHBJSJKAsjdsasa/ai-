import unittest
from domain.entities.player import Player
from domain.value_objects.player_attributes import PlayerAttributes
from domain.value_objects.player_status import PlayerStatus, PlayerState, Affliction, AfflictionType
from domain.value_objects.cultivation_realm import CultivationRealm

class TestPlayerDomain(unittest.TestCase):
    """玩家领域模型测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.realm = CultivationRealm(name="凡人", level=0, description="未入仙道的普通人")
        self.player = Player(player_id="1", name="测试玩家", cultivation_realm=self.realm)
    
    def test_player_creation(self):
        """测试玩家创建"""
        self.assertEqual(self.player.id, "1")
        self.assertEqual(self.player.name, "测试玩家")
        self.assertEqual(self.player.cultivation_realm.name, "凡人")
        self.assertEqual(self.player.cultivation_realm.level, 0)
    
    def test_update_attributes(self):
        """测试更新属性"""
        initial_money = self.player.attributes.money
        self.player.update_attributes(money=initial_money + 100)
        self.assertEqual(self.player.attributes.money, initial_money + 100)
    
    def test_update_status(self):
        """测试更新状态"""
        self.player.update_status(current_state=PlayerState.CULTIVATING)
        self.assertEqual(self.player.status.current_state, PlayerState.CULTIVATING)
    
    def test_cultivate(self):
        """测试修炼"""
        initial_exp = self.player.attributes.exp
        exp_gained = self.player.cultivate(10)
        self.assertGreater(self.player.attributes.exp, initial_exp)
        self.assertGreater(exp_gained, 0)
        self.assertEqual(self.player.status.current_state, PlayerState.IDLE)
    
    def test_learn_technique(self):
        """测试学习技能"""
        technique = {"id": "1", "name": "基础剑法"}
        result = self.player.learn_technique(technique)
        self.assertTrue(result)
        self.assertEqual(len(self.player.techniques), 1)
        self.assertEqual(self.player.techniques[0]["id"], "1")
    
    def test_fight(self):
        """测试战斗"""
        result = self.player.fight("敌人1")
        self.assertIsInstance(result, bool)
        self.assertEqual(self.player.status.current_state, PlayerState.IDLE)
    
    def test_add_item(self):
        """测试添加物品"""
        item = {"id": "1", "name": "金疮药"}
        self.player.add_item(item)
        self.assertEqual(len(self.player.inventory), 1)
        self.assertEqual(self.player.inventory[0]["id"], "1")
    
    def test_remove_item(self):
        """测试移除物品"""
        item = {"id": "1", "name": "金疮药"}
        self.player.add_item(item)
        result = self.player.remove_item("1")
        self.assertTrue(result)
        self.assertEqual(len(self.player.inventory), 0)
    
    def test_add_friend(self):
        """测试添加好友"""
        result = self.player.add_friend("friend1")
        self.assertTrue(result)
        self.assertIn("friend1", self.player.friends)
    
    def test_remove_friend(self):
        """测试移除好友"""
        self.player.add_friend("friend1")
        result = self.player.remove_friend("friend1")
        self.assertTrue(result)
        self.assertNotIn("friend1", self.player.friends)
    
    def test_add_enemy(self):
        """测试添加敌人"""
        result = self.player.add_enemy("enemy1")
        self.assertTrue(result)
        self.assertIn("enemy1", self.player.enemies)
    
    def test_remove_enemy(self):
        """测试移除敌人"""
        self.player.add_enemy("enemy1")
        result = self.player.remove_enemy("enemy1")
        self.assertTrue(result)
        self.assertNotIn("enemy1", self.player.enemies)
    
    def test_add_quest(self):
        """测试添加任务"""
        quest = {"id": "1", "name": "新手任务"}
        self.player.add_quest(quest)
        self.assertEqual(len(self.player.quests), 1)
        self.assertEqual(self.player.quests[0]["id"], "1")
    
    def test_complete_quest(self):
        """测试完成任务"""
        quest = {"id": "1", "name": "新手任务", "reward_exp": 100, "reward_money": 50}
        self.player.add_quest(quest)
        initial_exp = self.player.attributes.exp
        initial_money = self.player.attributes.money
        result = self.player.complete_quest("1")
        self.assertTrue(result)
        self.assertEqual(self.player.quests[0]["completed"], True)
        self.assertEqual(self.player.attributes.exp, initial_exp + 100)
        self.assertEqual(self.player.attributes.money, initial_money + 50)
    
    def test_add_achievement(self):
        """测试添加成就"""
        achievement = {"id": "1", "name": "初入仙道"}
        self.player.add_achievement(achievement)
        self.assertEqual(len(self.player.achievements), 1)
        self.assertEqual(self.player.achievements[0]["id"], "1")
    
    def test_add_sect(self):
        """测试添加门派"""
        sect = {"id": "1", "name": "武当派"}
        self.player.add_sect(sect)
        self.assertEqual(len(self.player.sects), 1)
        self.assertEqual(self.player.sects[0]["id"], "1")
    
    def test_add_cave(self):
        """测试添加洞府"""
        cave = {"id": "1", "name": "水帘洞"}
        self.player.add_cave(cave)
        self.assertEqual(len(self.player.caves), 1)
        self.assertEqual(self.player.caves[0]["id"], "1")
    
    def test_add_pet(self):
        """测试添加宠物"""
        pet = {"id": "1", "name": "灵猫"}
        self.player.add_pet(pet)
        self.assertEqual(len(self.player.pets), 1)
        self.assertEqual(self.player.pets[0]["id"], "1")
    
    def test_add_memory(self):
        """测试添加记忆"""
        memory = {"id": "1", "content": "初次修炼"}
        self.player.add_memory(memory)
        self.assertEqual(len(self.player.memories), 1)
        self.assertEqual(self.player.memories[0]["id"], "1")
    
    def test_add_event(self):
        """测试添加事件"""
        event = {"id": "1", "name": "第一次战斗"}
        self.player.add_event(event)
        self.assertEqual(len(self.player.events), 1)
        self.assertEqual(self.player.events[0]["id"], "1")
    
    def test_get_combat_power(self):
        """测试获取战斗力"""
        combat_power = self.player.get_combat_power()
        self.assertGreater(combat_power, 0)
    
    def test_is_alive(self):
        """测试是否活着"""
        self.assertTrue(self.player.is_alive())
    
    def test_has_enough_money(self):
        """测试是否有足够的金钱"""
        self.assertTrue(self.player.has_enough_money(50))
        self.assertFalse(self.player.has_enough_money(1000))
    
    def test_has_enough_exp(self):
        """测试是否有足够的经验值"""
        self.assertTrue(self.player.has_enough_exp(0))
        self.assertFalse(self.player.has_enough_exp(100))
    
    def test_has_enough_lifespan(self):
        """测试是否有足够的寿元"""
        self.assertTrue(self.player.has_enough_lifespan(10))
        self.assertFalse(self.player.has_enough_lifespan(100))
    
    def test_get_total_wealth(self):
        """测试获取总财富"""
        wealth = self.player.get_total_wealth()
        self.assertGreater(wealth, 0)
    
    def test_get_cultivation_progress(self):
        """测试获取修炼进度"""
        progress = self.player.get_cultivation_progress(100)
        self.assertGreaterEqual(progress, 0.0)
        self.assertLessEqual(progress, 1.0)
    
    def test_get_location_info(self):
        """测试获取位置信息"""
        location_info = self.player.get_location_info()
        self.assertIn("world", location_info)
        self.assertIn("location", location_info)
        self.assertIn("sect", location_info)
        self.assertIn("cave", location_info)
    
    def test_get_current_activity(self):
        """测试获取当前活动"""
        activity = self.player.get_current_activity()
        self.assertEqual(activity, "idle")
    
    def test_is_available(self):
        """测试是否可用"""
        self.assertTrue(self.player.is_available())
    
    def test_is_busy(self):
        """测试是否忙碌"""
        self.assertFalse(self.player.is_busy())
    
    def test_is_in_danger(self):
        """测试是否处于危险中"""
        self.assertFalse(self.player.is_in_danger())
    
    def test_add_affliction(self):
        """测试添加状态"""
        affliction = Affliction(type=AfflictionType.POISON, severity=5, duration=10, description="中毒")
        self.player.add_affliction(affliction)
        self.assertTrue(self.player.has_affliction(AfflictionType.POISON))
    
    def test_remove_affliction(self):
        """测试移除状态"""
        affliction = Affliction(type=AfflictionType.POISON, severity=5, duration=10, description="中毒")
        self.player.add_affliction(affliction)
        self.player.remove_affliction(AfflictionType.POISON)
        self.assertFalse(self.player.has_affliction(AfflictionType.POISON))
    
    def test_has_affliction(self):
        """测试是否有特定状态"""
        self.assertFalse(self.player.has_affliction(AfflictionType.POISON))
        affliction = Affliction(type=AfflictionType.POISON, severity=5, duration=10, description="中毒")
        self.player.add_affliction(affliction)
        self.assertTrue(self.player.has_affliction(AfflictionType.POISON))
    
    def test_get_affliction_severity(self):
        """测试获取状态严重程度"""
        self.assertEqual(self.player.get_affliction_severity(AfflictionType.POISON), 0)
        affliction = Affliction(type=AfflictionType.POISON, severity=5, duration=10, description="中毒")
        self.player.add_affliction(affliction)
        self.assertEqual(self.player.get_affliction_severity(AfflictionType.POISON), 5)

if __name__ == '__main__':
    unittest.main()
