import unittest
from domain.entities.player import Player
from domain.value_objects.cultivation_realm import CultivationRealm
from domain.value_objects.experience import Experience
from domain.services.cultivation_service import CultivationService

class TestCultivationDomain(unittest.TestCase):
    """测试修炼领域模型"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建修炼服务
        self.cultivation_service = CultivationService()
        # 创建境界层次结构
        self.realms = self.cultivation_service.create_realm_hierarchy()
        # 创建玩家
        self.player = Player("test_player", "测试玩家", self.realms[0])
    
    def test_experience_creation(self):
        """测试经验值对象的创建"""
        exp = Experience(value=100, source="测试", timestamp=123456)
        self.assertEqual(exp.value, 100)
        self.assertEqual(exp.source, "测试")
        self.assertEqual(exp.timestamp, 123456)
    
    def test_experience_addition(self):
        """测试经验值的添加"""
        exp1 = Experience(value=100, source="测试1", timestamp=123456)
        exp2 = Experience(value=200, source="测试2", timestamp=123457)
        result = exp1.add(exp2)
        self.assertEqual(result.value, 300)
        self.assertIn("测试1", result.source)
        self.assertIn("测试2", result.source)
        self.assertEqual(result.timestamp, 123457)
    
    def test_experience_subtraction(self):
        """测试经验值的减少"""
        exp = Experience(value=300, source="测试", timestamp=123456)
        result = exp.subtract(100)
        self.assertEqual(result.value, 200)
        self.assertIn("减少100", result.source)
    
    def test_cultivation_gains_experience(self):
        """测试修炼获得经验值"""
        initial_exp = self.player.current_exp_value
        gained_exp = self.player.cultivate(10)
        self.assertGreater(self.player.current_exp_value, initial_exp)
        self.assertEqual(gained_exp, self.player.current_exp_value - initial_exp)
    
    def test_breakthrough_condition(self):
        """测试突破条件"""
        # 初始状态下不能突破
        self.assertFalse(self.player.can_breakthrough())
        
        # 手动设置经验值达到突破条件
        required_exp = self.player.cultivation_realm.required_exp
        # 由于Experience是不可变的，我们需要通过多次修炼来积累经验
        while self.player.current_exp_value < required_exp:
            self.player.cultivate(100)
        
        # 现在应该可以突破
        self.assertTrue(self.player.can_breakthrough())
    
    def test_breakthrough_success(self):
        """测试突破成功"""
        # 手动设置经验值达到突破条件
        required_exp = self.player.cultivation_realm.required_exp
        while self.player.current_exp_value < required_exp:
            self.player.cultivate(100)
        
        # 记录突破前的境界
        initial_realm = self.player.cultivation_realm
        # 执行突破
        success = self.player.breakthrough()
        # 突破应该成功
        self.assertTrue(success)
        # 境界应该提升
        self.assertNotEqual(self.player.cultivation_realm, initial_realm)
        # 经验值应该重置
        self.assertEqual(self.player.current_exp_value, 0)
    
    def test_cultivation_status(self):
        """测试获取修炼状态"""
        status = self.cultivation_service.get_cultivation_status(self.player)
        self.assertIn("current_realm", status)
        self.assertIn("current_exp", status)
        self.assertIn("required_exp", status)
        self.assertIn("progress", status)
        self.assertIn("next_realm", status)
    
    def test_realm_hierarchy_creation(self):
        """测试境界层次结构的创建"""
        realms = self.cultivation_service.create_realm_hierarchy()
        self.assertEqual(len(realms), 5)
        self.assertEqual(realms[0].name, "练气期")
        self.assertEqual(realms[1].name, "筑基期")
        self.assertEqual(realms[2].name, "金丹期")
        self.assertEqual(realms[3].name, "元婴期")
        self.assertEqual(realms[4].name, "化神期")

if __name__ == '__main__':
    unittest.main()