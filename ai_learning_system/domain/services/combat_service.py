"""战斗领域服务"""
import random
from typing import Optional, List, Tuple, Dict, Any
from domain.entities.combat import CombatUnit
from domain.value_objects.combat import CombatMode, CombatStatus, CombatResult, CombatSkill, DamageType


class CombatService:
    """战斗领域服务"""
    
    def start_combat(self, player: CombatUnit, enemy: CombatUnit, 
                     mode: CombatMode = CombatMode.SPAR, enemy_npc_id: Optional[str] = None) -> Tuple[CombatResult, CombatUnit, CombatUnit]:
        """
        开始战斗
        
        Args:
            player: 玩家战斗单位
            enemy: 敌人战斗单位
            mode: 战斗模式
            enemy_npc_id: 敌人NPC ID（用于死斗模式的处决功能）
            
        Returns:
            (战斗结果, 玩家单位, 敌人单位)
        """
        # 保存初始状态
        initial_player_health = player.health
        initial_player_mana = player.mana
        initial_enemy_health = enemy.health
        initial_enemy_mana = enemy.mana
        
        # 战斗日志
        combat_log = []
        
        # 记录战斗开始
        mode_str = "切磋" if mode == CombatMode.SPAR else "死斗"
        combat_log.append(f"=== {mode_str}开始 ===")
        combat_log.append(f"{player.name} VS {enemy.name}")
        combat_log.append(f"{player.name}: {player.health}/{player.max_health} HP")
        combat_log.append(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")
        
        # 确定先手（速度高的先出手，相同则随机）
        if player.speed > enemy.speed:
            current_turn_unit = player
        elif enemy.speed > player.speed:
            current_turn_unit = enemy
        else:
            current_turn_unit = random.choice([player, enemy])
        
        combat_log.append(f"{current_turn_unit.name} 速度更快，率先出手！")
        
        # 创建初始战斗结果
        result = CombatResult(
            status=CombatStatus.ONGOING,
            combat_log=combat_log,
            mode=mode
        )
        
        return result, player, enemy
    
    def execute_turn(self, player: CombatUnit, enemy: CombatUnit, action: str, 
                     skill_name: Optional[str] = None, mode: CombatMode = CombatMode.SPAR) -> Tuple[CombatResult, CombatUnit, CombatUnit]:
        """
        执行一个战斗回合
        
        Args:
            player: 玩家战斗单位
            enemy: 敌人战斗单位
            action: 行动类型 ("attack", "skill", "flee", "defend")
            skill_name: 技能名称（如果使用技能）
            mode: 战斗模式
            
        Returns:
            (战斗结果, 玩家单位, 敌人单位)
        """
        combat_log = []
        status = CombatStatus.ONGOING
        turn = 1
        
        combat_log.append(f"\n--- 第 {turn} 回合 ---")
        
        # 玩家回合
        if player.speed >= enemy.speed:
            self._execute_player_turn(player, enemy, action, skill_name, combat_log)
            if not player.is_alive() or not enemy.is_alive():
                status = self._check_combat_end(player, enemy, mode)
                if status != CombatStatus.ONGOING:
                    result = self._create_result(status, player, enemy, combat_log, turn, mode)
                    return result, player, enemy
            
            # 敌人回合
            self._execute_enemy_turn(enemy, player, combat_log)
        else:
            # 敌人先出手
            self._execute_enemy_turn(enemy, player, combat_log)
            if not player.is_alive() or not enemy.is_alive():
                status = self._check_combat_end(player, enemy, mode)
                if status != CombatStatus.ONGOING:
                    result = self._create_result(status, player, enemy, combat_log, turn, mode)
                    return result, player, enemy
            
            # 玩家回合
            self._execute_player_turn(player, enemy, action, skill_name, combat_log)
        
        # 更新冷却
        player.update_cooldowns()
        enemy.update_cooldowns()
        
        # 检查战斗结束
        status = self._check_combat_end(player, enemy, mode)
        
        result = self._create_result(status, player, enemy, combat_log, turn, mode)
        return result, player, enemy
    
    def _execute_player_turn(self, player: CombatUnit, enemy: CombatUnit, 
                            action: str, skill_name: Optional[str], combat_log: List[str]):
        """执行玩家回合"""
        if action == "attack":
            damage, is_crit, log = player.deal_damage(enemy)
            combat_log.append(log)
        elif action == "skill" and skill_name:
            skill = self._find_skill(player, skill_name)
            if skill and player.can_use_skill(skill):
                self._use_skill(player, enemy, skill, combat_log)
            else:
                combat_log.append(f"{player.name} 无法使用 {skill_name}，改为普通攻击")
                damage, is_crit, log = player.deal_damage(enemy)
                combat_log.append(log)
        elif action == "flee":
            if self._attempt_flee(player, enemy):
                combat_log.append(f"{player.name} 成功逃跑！")
            else:
                combat_log.append(f"{player.name} 逃跑失败！")
        elif action == "defend":
            combat_log.append(f"{player.name} 进入防御姿态，受到伤害减少")
            player.buffs["defend"] = 0.5  # 减少50%伤害
        else:
            # 默认普通攻击
            damage, is_crit, log = player.deal_damage(enemy)
            combat_log.append(log)
    
    def _execute_enemy_turn(self, enemy: CombatUnit, player: CombatUnit, combat_log: List[str]):
        """执行敌人回合（AI）"""
        # 简单的AI逻辑
        available_skills = enemy.get_available_skills()
        
        # 优先使用强力技能
        if available_skills:
            # 选择伤害最高的技能
            best_skill = max(available_skills, key=lambda s: s.damage)
            if enemy.mana >= best_skill.mana_cost:
                self._use_skill(enemy, player, best_skill, combat_log)
                return
        
        # 普通攻击
        damage, is_crit, log = enemy.deal_damage(player)
        combat_log.append(log)
    
    def _use_skill(self, user: CombatUnit, target: CombatUnit, skill: CombatSkill, combat_log: List[str]):
        """使用技能"""
        if not user.use_skill(skill):
            combat_log.append(f"{user.name} 无法使用 {skill.name}")
            return
        
        combat_log.append(f"{user.name} 使用 {skill.name}！")
        
        if skill.damage > 0:
            damage, is_crit, log = user.deal_damage(target, skill)
            combat_log.append(log)
        
        # 处理附加效果
        for effect in skill.effects:
            effect_type = effect.get("type")
            if effect_type == "heal":
                heal_amount = effect.get("value", 0)
                user.heal(heal_amount)
                combat_log.append(f"{user.name} 恢复 {heal_amount} 点生命")
            elif effect_type == "buff":
                buff_name = effect.get("name", "buff")
                user.buffs[buff_name] = effect.get("value", 0)
                combat_log.append(f"{user.name} 获得增益效果: {buff_name}")
            elif effect_type == "debuff":
                debuff_name = effect.get("name", "debuff")
                target.buffs[debuff_name] = effect.get("value", 0)
                combat_log.append(f"{target.name} 受到减益效果: {debuff_name}")
            elif effect_type == "stun":
                target.is_stunned = True
                combat_log.append(f"{target.name} 被眩晕！")
    
    def _find_skill(self, unit: CombatUnit, skill_name: str) -> Optional[CombatSkill]:
        """查找技能"""
        for skill in unit.skills:
            if skill.name == skill_name:
                return skill
        return None
    
    def _attempt_flee(self, player: CombatUnit, enemy: CombatUnit) -> bool:
        """尝试逃跑"""
        # 基础逃跑成功率
        base_chance = 0.5
        # 速度差影响
        speed_diff = player.speed - enemy.speed
        base_chance += speed_diff * 0.02
        return random.random() < max(0.1, min(0.9, base_chance))
    
    def _check_combat_end(self, player: CombatUnit, enemy: CombatUnit, mode: CombatMode) -> CombatStatus:
        """检查战斗是否结束"""
        if mode == CombatMode.SPAR:
            # 切磋模式：生命值降到1即结束
            if player.health <= 1:
                return CombatStatus.ENEMY_WIN
            if enemy.health <= 1:
                return CombatStatus.PLAYER_WIN
        else:
            # 死斗模式：生命值归零
            if player.health <= 0:
                return CombatStatus.ENEMY_WIN
            if enemy.health <= 0:
                return CombatStatus.PLAYER_WIN
        
        return CombatStatus.ONGOING
    
    def _create_result(self, status: CombatStatus, player: CombatUnit, enemy: CombatUnit, 
                      combat_log: List[str], turns: int, mode: CombatMode) -> CombatResult:
        """创建战斗结果"""
        winner_id = None
        loser_id = None
        
        if status == CombatStatus.PLAYER_WIN:
            winner_id = player.id
            loser_id = enemy.id
        elif status == CombatStatus.ENEMY_WIN:
            winner_id = enemy.id
            loser_id = player.id
        
        # 计算奖励
        exp_reward = 0
        spirit_stones_reward = 0
        loot = []
        
        if winner_id and loser_id:
            if mode == CombatMode.SPAR:
                exp_reward = self._calculate_spar_exp(player, enemy)
            else:
                exp_reward, spirit_stones_reward, loot = self._calculate_deathmatch_rewards(player, enemy)
        
        # 死斗模式且玩家胜利：检查是否触发处决流程
        execution_pending = False
        can_execute = False
        enemy_npc_id = None
        
        if (mode == CombatMode.DEATHMATCH and
            status == CombatStatus.PLAYER_WIN and
            enemy.unit_type == "npc"):
            execution_pending = True
            can_execute = True
            enemy_npc_id = enemy.id
        
        return CombatResult(
            status=status,
            winner_id=winner_id,
            loser_id=loser_id,
            exp_reward=exp_reward,
            spirit_stones_reward=spirit_stones_reward,
            loot=loot,
            combat_log=combat_log,
            turns=turns,
            mode=mode,
            execution_pending=execution_pending,
            can_execute=can_execute,
            enemy_npc_id=enemy_npc_id
        )
    
    def _calculate_spar_exp(self, player: CombatUnit, enemy: CombatUnit) -> int:
        """计算切磋经验奖励"""
        base_exp = 10
        level_diff = enemy.level - player.level
        
        if level_diff > 0:
            base_exp += level_diff * 5
        else:
            base_exp = max(5, base_exp + level_diff * 2)
        
        return base_exp
    
    def _calculate_deathmatch_rewards(self, player: CombatUnit, enemy: CombatUnit) -> Tuple[int, int, List[str]]:
        """计算死斗奖励"""
        # 基础奖励
        base_exp = 50
        base_spirit_stones = 20
        
        # 根据等级差调整
        level_diff = enemy.level - player.level
        if level_diff > 0:
            multiplier = 1 + level_diff * 0.2
        else:
            multiplier = max(0.5, 1 + level_diff * 0.1)
        
        exp = int(base_exp * multiplier)
        spirit_stones = int(base_spirit_stones * multiplier)
        
        # 掉落物品
        loot = []
        if enemy.unit_type == "beast":
            # 妖兽掉落材料
            loot = self._generate_beast_loot(enemy)
        elif enemy.unit_type == "npc":
            # NPC可能掉落物品
            if random.random() < 0.3:
                loot = self._generate_npc_loot(enemy)
        
        return exp, spirit_stones, loot
    
    def _generate_beast_loot(self, beast: CombatUnit) -> List[str]:
        """生成妖兽掉落"""
        loot = []
        loot_table = {
            "普通": [("妖兽皮毛", 0.8), ("妖兽骨", 0.5)],
            "稀有": [("妖兽内丹", 0.3), ("妖兽精血", 0.4)],
            "史诗": [("高级妖丹", 0.2), ("妖兽灵核", 0.3)],
        }
        
        # 根据等级确定稀有度
        if beast.level <= 3:
            rarity = "普通"
        elif beast.level <= 6:
            rarity = "稀有"
        else:
            rarity = "史诗"
        
        for item, chance in loot_table.get(rarity, []):
            if random.random() < chance:
                loot.append(item)
        
        return loot
    
    def _generate_npc_loot(self, npc: CombatUnit) -> List[str]:
        """生成NPC掉落"""
        loot = []
        possible_loot = ["灵石袋", "丹药", "功法残页", "材料包"]
        if random.random() < 0.5:
            loot.append(random.choice(possible_loot))
        return loot
    
    def get_combat_status_text(self, player: CombatUnit, enemy: CombatUnit, turn: int) -> str:
        """获取战斗状态文本"""
        lines = [
            f"=== 战斗状态 ===",
            f"",
            f"{player.name}: {player.health}/{player.max_health} HP | {player.mana}/{player.max_mana} MP",
            f"{enemy.name}: {enemy.health}/{enemy.max_health} HP | {enemy.mana}/{enemy.max_mana} MP",
            f"",
            f"当前回合: {turn}",
        ]
        return "\n".join(lines)
    
    def get_available_actions(self, player: CombatUnit) -> List[str]:
        """获取可用行动列表"""
        actions = ["attack", "defend", "flee"]
        
        # 检查是否有可用技能
        if player.get_available_skills():
            actions.insert(1, "skill")
        
        return actions
