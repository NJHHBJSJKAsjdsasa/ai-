"""战斗领域模型测试"""
import unittest
from domain.entities.combat import CombatUnit
from domain.services.combat_service import CombatService
from domain.value_objects.combat import CombatMode, CombatStatus, CombatSkill, DamageType


class TestCombatDomain(unittest.TestCase):
    """战斗领域模型测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.combat_service = CombatService()
        
        # 创建测试用的战斗单位
        self.player = CombatUnit(
            id="player_1",
            name="测试玩家",
            unit_type="player",
            level=1,
            health=100,
            max_health=100,
            mana=50,
            max_mana=50,
            attack=20,
            defense=10,
            speed=15,
            crit_rate=0.1,
            dodge_rate=0.05
        )
        
        self.enemy = CombatUnit(
            id="enemy_1",
            name="测试敌人",
            unit_type="npc",
            level=1,
            health=80,
            max_health=80,
            mana=40,
            max_mana=40,
            attack=15,
            defense=5,
            speed=10,
            crit_rate=0.05,
            dodge_rate=0.03
        )
        
        # 添加测试技能
        self.sword_skill = CombatSkill(
            name="剑气斩",
            damage=30,
            damage_type=DamageType.PHYSICAL,
            mana_cost=15,
            cooldown=2
        )
        self.fire_skill = CombatSkill(
            name="火球术",
            damage=25,
            damage_type=DamageType.MAGIC,
            mana_cost=10,
            cooldown=1
        )
        
        self.player.skills.append(self.sword_skill)
        self.enemy.skills.append(self.fire_skill)
    
    def test_combat_unit_creation(self):
        """测试战斗单位创建"""
        unit = CombatUnit(
            id="test_unit",
            name="测试单位",
            unit_type="beast",
            level=2,
            health=150,
            max_health=150,
            mana=60,
            max_mana=60,
            attack=25,
            defense=12,
            speed=18
        )
        
        self.assertEqual(unit.id, "test_unit")
        self.assertEqual(unit.name, "测试单位")
        self.assertEqual(unit.unit_type, "beast")
        self.assertEqual(unit.level, 2)
        self.assertEqual(unit.health, 150)
        self.assertEqual(unit.max_health, 150)
        self.assertEqual(unit.mana, 60)
        self.assertEqual(unit.max_mana, 60)
        self.assertEqual(unit.attack, 25)
        self.assertEqual(unit.defense, 12)
        self.assertEqual(unit.speed, 18)
        self.assertTrue(unit.is_alive())
    
    def test_skill_usage(self):
        """测试技能使用"""
        # 检查初始状态
        self.assertEqual(len(self.player.skills), 1)
        self.assertEqual(self.player.skills[0].name, "剑气斩")
        
        # 测试技能冷却
        self.assertTrue(self.player.can_use_skill(self.sword_skill))
        
        # 使用技能
        result = self.player.use_skill(self.sword_skill)
        self.assertTrue(result)
        self.assertEqual(self.player.mana, 35)  # 50 - 15
        self.assertEqual(self.player.skill_cooldowns.get("剑气斩"), 2)
        
        # 检查技能冷却中
        self.assertFalse(self.player.can_use_skill(self.sword_skill))
        
        # 更新冷却
        self.player.update_cooldowns()
        self.assertEqual(self.player.skill_cooldowns.get("剑气斩"), 1)
        
        self.player.update_cooldowns()
        self.assertIsNone(self.player.skill_cooldowns.get("剑气斩"))
        self.assertTrue(self.player.can_use_skill(self.sword_skill))
    
    def test_damage_calculation(self):
        """测试伤害计算"""
        # 测试普通攻击
        damage, is_crit, log = self.player.deal_damage(self.enemy)
        self.assertGreater(damage, 0)
        self.assertLess(self.enemy.health, 80)
        
        # 测试技能攻击
        self.player.use_skill(self.sword_skill)
        damage, is_crit, log = self.player.deal_damage(self.enemy, self.sword_skill)
        self.assertGreater(damage, 0)
        self.assertLess(self.enemy.health, 80 - damage)
    
    def test_combat_service_start(self):
        """测试战斗服务开始战斗"""
        result, player, enemy = self.combat_service.start_combat(
            self.player, self.enemy, CombatMode.SPAR
        )
        
        self.assertEqual(result.status, CombatStatus.ONGOING)
        self.assertEqual(len(result.combat_log), 5)  # 战斗开始日志
    
    def test_combat_service_execute_turn(self):
        """测试战斗服务执行回合"""
        # 开始战斗
        _, player, enemy = self.combat_service.start_combat(
            self.player, self.enemy, CombatMode.SPAR
        )
        
        # 执行一个回合
        result, player, enemy = self.combat_service.execute_turn(
            player, enemy, "attack", mode=CombatMode.SPAR
        )
        
        self.assertEqual(result.status, CombatStatus.ONGOING)
        self.assertGreater(len(result.combat_log), 0)
    
    def test_combat_service_win_condition(self):
        """测试战斗胜利条件"""
        # 创建一个低生命值的敌人
        weak_enemy = CombatUnit(
            id="weak_enemy",
            name="虚弱敌人",
            unit_type="npc",
            level=1,
            health=5,
            max_health=5,
            attack=5,
            defense=0
        )
        
        # 开始战斗
        _, player, enemy = self.combat_service.start_combat(
            self.player, weak_enemy, CombatMode.DEATHMATCH
        )
        
        # 执行攻击
        result, player, enemy = self.combat_service.execute_turn(
            player, enemy, "attack", mode=CombatMode.DEATHMATCH
        )
        
        self.assertEqual(result.status, CombatStatus.PLAYER_WIN)
        self.assertEqual(result.winner_id, "player_1")
        self.assertEqual(result.loser_id, "weak_enemy")
    
    def test_combat_rewards(self):
        """测试战斗奖励"""
        # 开始战斗
        _, player, enemy = self.combat_service.start_combat(
            self.player, self.enemy, CombatMode.DEATHMATCH
        )
        
        # 执行攻击直到胜利
        while True:
            result, player, enemy = self.combat_service.execute_turn(
                player, enemy, "attack", mode=CombatMode.DEATHMATCH
            )
            if result.status != CombatStatus.ONGOING:
                break
        
        if result.status == CombatStatus.PLAYER_WIN:
            self.assertGreater(result.exp_reward, 0)
            self.assertGreaterEqual(result.spirit_stones_reward, 0)
    
    def test_skill_effects(self):
        """测试技能效果"""
        # 创建一个带治疗效果的技能
        heal_skill = CombatSkill(
            name="治疗术",
            damage=0,
            mana_cost=20,
            effects=[{"type": "heal", "value": 30}]
        )
        
        self.player.skills.append(heal_skill)
        
        # 先让玩家受到伤害
        self.player.take_damage(50)
        initial_health = self.player.health
        
        # 使用治疗技能
        self.player.use_skill(heal_skill)
        
        # 检查生命值恢复
        self.assertGreater(self.player.health, initial_health)
    
    def test_defense_buff(self):
        """测试防御增益"""
        # 添加防御增益
        self.player.buffs["defend"] = 0.5  # 减少50%伤害
        
        # 记录初始生命值
        initial_health = self.player.health
        
        # 受到伤害
        damage, is_crit = self.player.take_damage(50)
        
        # 检查伤害是否减少
        self.assertLess(damage, 50)
        self.assertGreater(self.player.health, initial_health - 50)


if __name__ == "__main__":
    unittest.main()
