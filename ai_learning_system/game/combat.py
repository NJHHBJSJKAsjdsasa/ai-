"""
战斗系统核心模块
提供完整的回合制战斗机制，支持切磋和死斗两种模式
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CombatMode(Enum):
    """战斗模式枚举"""
    SPAR = "切磋"           # 切磋模式：不会死亡，结束后恢复
    DEATHMATCH = "死斗"     # 死斗模式：可能死亡，掉落物品


class DamageType(Enum):
    """伤害类型枚举"""
    PHYSICAL = "物理"       # 物理伤害
    MAGIC = "法术"          # 法术伤害
    TRUE = "真实"           # 真实伤害（无视防御）


class CombatStatus(Enum):
    """战斗状态枚举"""
    ONGOING = "进行中"
    PLAYER_WIN = "玩家胜利"
    ENEMY_WIN = "敌人胜利"
    FLED = "逃跑"
    DRAW = "平局"


@dataclass
class CombatSkill:
    """战斗技能数据类"""
    name: str                           # 技能名称
    description: str = ""               # 技能描述
    damage: int = 0                     # 基础伤害
    damage_type: DamageType = DamageType.PHYSICAL  # 伤害类型
    mana_cost: int = 0                  # 灵力消耗
    cooldown: int = 0                   # 冷却回合
    current_cooldown: int = 0           # 当前冷却
    is_aoe: bool = False                # 是否范围攻击
    effects: List[Dict[str, Any]] = field(default_factory=list)  # 附加效果


@dataclass
class CombatUnit:
    """战斗单位数据类"""
    # 基础信息
    name: str
    unit_type: str  # "player", "npc", "beast"
    
    # 战斗属性
    level: int = 1
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    attack: int = 10
    defense: int = 5
    speed: int = 10
    crit_rate: float = 0.05  # 暴击率
    dodge_rate: float = 0.05  # 闪避率
    
    # 技能
    skills: List[CombatSkill] = field(default_factory=list)
    
    # 状态
    is_stunned: bool = False        # 是否眩晕
    is_buffed: bool = False         # 是否有增益
    buffs: Dict[str, Any] = field(default_factory=dict)
    
    # 战斗记录
    damage_dealt: int = 0
    damage_taken: int = 0
    
    def __post_init__(self):
        if not self.skills:
            self.skills = []
        if not self.buffs:
            self.buffs = {}
    
    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.health > 0
    
    def take_damage(self, damage: int, damage_type: DamageType = DamageType.PHYSICAL) -> Tuple[int, bool]:
        """
        受到伤害
        
        Returns:
            (实际伤害, 是否暴击)
        """
        # 闪避判定
        if random.random() < self.dodge_rate:
            return 0, False
        
        # 计算实际伤害
        actual_damage = damage
        if damage_type != DamageType.TRUE:
            # 物理/法术伤害受防御影响
            reduction = self.defense / (self.defense + 50)
            actual_damage = int(damage * (1 - reduction))
        
        actual_damage = max(1, actual_damage)  # 最低造成1点伤害
        self.health = max(0, self.health - actual_damage)
        self.damage_taken += actual_damage
        
        return actual_damage, False
    
    def deal_damage(self, target: 'CombatUnit', skill: Optional[CombatSkill] = None) -> Tuple[int, bool, str]:
        """
        对目标造成伤害
        
        Returns:
            (伤害值, 是否暴击, 日志信息)
        """
        if skill:
            base_damage = skill.damage + self.attack
            damage_type = skill.damage_type
        else:
            base_damage = self.attack
            damage_type = DamageType.PHYSICAL
        
        # 暴击判定
        is_crit = random.random() < self.crit_rate
        if is_crit:
            base_damage = int(base_damage * 1.5)
        
        actual_damage, _ = target.take_damage(base_damage, damage_type)
        self.damage_dealt += actual_damage
        
        # 构建日志
        log = f"{self.name} 对 {target.name} 造成 {actual_damage} 点伤害"
        if is_crit:
            log += " (暴击!)"
        if damage_type == DamageType.MAGIC:
            log += " [法术]"
        elif damage_type == DamageType.TRUE:
            log += " [真实]"
        
        return actual_damage, is_crit, log
    
    def use_mana(self, amount: int) -> bool:
        """消耗灵力"""
        if self.mana < amount:
            return False
        self.mana -= amount
        return True
    
    def restore_mana(self, amount: int):
        """恢复灵力"""
        self.mana = min(self.max_mana, self.mana + amount)
    
    def heal(self, amount: int):
        """恢复生命值"""
        self.health = min(self.max_health, self.health + amount)
    
    def can_use_skill(self, skill: CombatSkill) -> bool:
        """检查是否可以使用技能"""
        return self.mana >= skill.mana_cost and skill.current_cooldown == 0
    
    def update_cooldowns(self):
        """更新技能冷却"""
        for skill in self.skills:
            if skill.current_cooldown > 0:
                skill.current_cooldown -= 1
    
    def get_available_skills(self) -> List[CombatSkill]:
        """获取可用的技能列表"""
        return [s for s in self.skills if self.can_use_skill(s)]


@dataclass
class CombatResult:
    """战斗结果数据类"""
    status: CombatStatus
    winner: Optional[CombatUnit] = None
    loser: Optional[CombatUnit] = None
    exp_reward: int = 0
    spirit_stones_reward: int = 0
    loot: List[str] = field(default_factory=list)
    combat_log: List[str] = field(default_factory=list)
    turns: int = 0
    mode: CombatMode = CombatMode.SPAR
    # 处决相关字段（死斗模式专用）
    execution_pending: bool = False  # 是否等待处决选择
    can_execute: bool = False  # 是否可以处决
    enemy_npc: Any = None  # 敌人NPC对象，用于处决


class CombatSystem:
    """战斗系统类"""
    
    def __init__(self):
        """初始化战斗系统"""
        self.player: Optional[CombatUnit] = None
        self.enemy: Optional[CombatUnit] = None
        self.mode: CombatMode = CombatMode.SPAR
        self.status: CombatStatus = CombatStatus.ONGOING
        self.turn: int = 0
        self.combat_log: List[str] = []
        self.current_turn_unit: Optional[CombatUnit] = None

        # 保存初始状态（用于切磋恢复）
        self._initial_player_health: int = 0
        self._initial_player_mana: int = 0
        self._initial_enemy_health: int = 0
        self._initial_enemy_mana: int = 0

        # 保存原始敌人NPC对象（用于死斗模式的处决功能）
        self._enemy_npc: Any = None
    
    def start_combat(self, player: CombatUnit, enemy: CombatUnit,
                     mode: CombatMode = CombatMode.SPAR, enemy_npc: Any = None) -> CombatResult:
        """
        开始战斗

        Args:
            player: 玩家战斗单位
            enemy: 敌人战斗单位
            mode: 战斗模式
            enemy_npc: 原始敌人NPC对象（用于死斗模式的处决功能）

        Returns:
            战斗结果
        """
        self.player = player
        self.enemy = enemy
        self.mode = mode
        self.status = CombatStatus.ONGOING
        self.turn = 0
        self.combat_log = []

        # 保存原始敌人NPC对象（用于死斗模式的处决功能）
        self._enemy_npc = enemy_npc

        # 保存初始状态
        self._initial_player_health = player.health
        self._initial_player_mana = player.mana
        self._initial_enemy_health = enemy.health
        self._initial_enemy_mana = enemy.mana
        
        # 记录战斗开始
        mode_str = "切磋" if mode == CombatMode.SPAR else "死斗"
        self._log(f"=== {mode_str}开始 ===")
        self._log(f"{player.name} VS {enemy.name}")
        self._log(f"{player.name}: {player.health}/{player.max_health} HP")
        self._log(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")
        
        # 确定先手（速度高的先出手，相同则随机）
        if player.speed > enemy.speed:
            self.current_turn_unit = player
        elif enemy.speed > player.speed:
            self.current_turn_unit = enemy
        else:
            self.current_turn_unit = random.choice([player, enemy])
        
        self._log(f"{self.current_turn_unit.name} 速度更快，率先出手！")
        
        return self._create_result()
    
    def execute_turn(self, action: str, skill_name: Optional[str] = None) -> CombatResult:
        """
        执行一个战斗回合
        
        Args:
            action: 行动类型 ("attack", "skill", "flee", "defend")
            skill_name: 技能名称（如果使用技能）
            
        Returns:
            战斗结果
        """
        if self.status != CombatStatus.ONGOING:
            return self._create_result()
        
        self.turn += 1
        self._log(f"\n--- 第 {self.turn} 回合 ---")
        
        # 玩家回合
        if self.current_turn_unit == self.player:
            self._execute_player_turn(action, skill_name)
            if self._check_combat_end():
                return self.end_combat()
            # 切换到敌人回合
            self.current_turn_unit = self.enemy
            # 执行敌人AI
            self._execute_enemy_turn()
        else:
            # 敌人先出手
            self._execute_enemy_turn()
            if self._check_combat_end():
                return self.end_combat()
            # 切换到玩家回合
            self.current_turn_unit = self.player
            self._execute_player_turn(action, skill_name)
        
        # 更新冷却
        self.player.update_cooldowns()
        self.enemy.update_cooldowns()
        
        # 检查战斗结束
        if self._check_combat_end():
            return self.end_combat()
        
        return self._create_result()
    
    def _execute_player_turn(self, action: str, skill_name: Optional[str] = None):
        """执行玩家回合"""
        if action == "attack":
            damage, is_crit, log = self.player.deal_damage(self.enemy)
            self._log(log)
        elif action == "skill" and skill_name:
            skill = self._find_skill(self.player, skill_name)
            if skill and self.player.can_use_skill(skill):
                self._use_skill(self.player, self.enemy, skill)
            else:
                self._log(f"{self.player.name} 无法使用 {skill_name}，改为普通攻击")
                damage, is_crit, log = self.player.deal_damage(self.enemy)
                self._log(log)
        elif action == "flee":
            if self._attempt_flee():
                self.status = CombatStatus.FLED
                self._log(f"{self.player.name} 成功逃跑！")
                return
            else:
                self._log(f"{self.player.name} 逃跑失败！")
        elif action == "defend":
            self._log(f"{self.player.name} 进入防御姿态，受到伤害减少")
            self.player.buffs["defend"] = 0.5  # 减少50%伤害
        else:
            # 默认普通攻击
            damage, is_crit, log = self.player.deal_damage(self.enemy)
            self._log(log)
    
    def _execute_enemy_turn(self):
        """执行敌人回合（AI）"""
        # 简单的AI逻辑
        available_skills = self.enemy.get_available_skills()
        
        # 如果生命值低且可以逃跑（非死斗模式），尝试逃跑
        if self.enemy.health < self.enemy.max_health * 0.2 and self.mode == CombatMode.SPAR:
            if random.random() < 0.3:
                if self._attempt_flee():
                    self.status = CombatStatus.FLED
                    self._log(f"{self.enemy.name} 逃跑了！")
                    return
        
        # 优先使用强力技能
        if available_skills:
            # 选择伤害最高的技能
            best_skill = max(available_skills, key=lambda s: s.damage)
            if self.enemy.mana >= best_skill.mana_cost:
                self._use_skill(self.enemy, self.player, best_skill)
                return
        
        # 普通攻击
        damage, is_crit, log = self.enemy.deal_damage(self.player)
        self._log(log)
    
    def _use_skill(self, user: CombatUnit, target: CombatUnit, skill: CombatSkill):
        """使用技能"""
        if not user.use_mana(skill.mana_cost):
            self._log(f"{user.name} 灵力不足，无法使用 {skill.name}")
            return
        
        skill.current_cooldown = skill.cooldown
        
        self._log(f"{user.name} 使用 {skill.name}！")
        
        if skill.damage > 0:
            damage, is_crit, log = user.deal_damage(target, skill)
            self._log(log)
        
        # 处理附加效果
        for effect in skill.effects:
            effect_type = effect.get("type")
            if effect_type == "heal":
                heal_amount = effect.get("value", 0)
                user.heal(heal_amount)
                self._log(f"{user.name} 恢复 {heal_amount} 点生命")
            elif effect_type == "buff":
                buff_name = effect.get("name", "buff")
                user.buffs[buff_name] = effect.get("value", 0)
                self._log(f"{user.name} 获得增益效果: {buff_name}")
            elif effect_type == "debuff":
                debuff_name = effect.get("name", "debuff")
                target.buffs[debuff_name] = effect.get("value", 0)
                self._log(f"{target.name} 受到减益效果: {debuff_name}")
            elif effect_type == "stun":
                target.is_stunned = True
                self._log(f"{target.name} 被眩晕！")
    
    def _find_skill(self, unit: CombatUnit, skill_name: str) -> Optional[CombatSkill]:
        """查找技能"""
        for skill in unit.skills:
            if skill.name == skill_name:
                return skill
        return None
    
    def _attempt_flee(self) -> bool:
        """尝试逃跑"""
        # 基础逃跑成功率
        base_chance = 0.5
        # 速度差影响
        if self.player and self.enemy:
            speed_diff = self.player.speed - self.enemy.speed
            base_chance += speed_diff * 0.02
        return random.random() < max(0.1, min(0.9, base_chance))
    
    def _check_combat_end(self) -> bool:
        """检查战斗是否结束"""
        if self.mode == CombatMode.SPAR:
            # 切磋模式：生命值降到1即结束
            if self.player.health <= 1:
                self.status = CombatStatus.ENEMY_WIN
                return True
            if self.enemy.health <= 1:
                self.status = CombatStatus.PLAYER_WIN
                return True
        else:
            # 死斗模式：生命值归零
            if self.player.health <= 0:
                self.status = CombatStatus.ENEMY_WIN
                return True
            if self.enemy.health <= 0:
                self.status = CombatStatus.PLAYER_WIN
                return True
        
        return False
    
    def end_combat(self) -> CombatResult:
        """结束战斗"""
        if self.status == CombatStatus.ONGOING:
            self._check_combat_end()

        self._log(f"\n=== 战斗结束 ===")

        if self.status == CombatStatus.PLAYER_WIN:
            self._log(f"{self.player.name} 获得胜利！")
        elif self.status == CombatStatus.ENEMY_WIN:
            self._log(f"{self.enemy.name} 获得胜利！")
        elif self.status == CombatStatus.FLED:
            self._log("战斗以逃跑结束")
        elif self.status == CombatStatus.DRAW:
            self._log("战斗平局")

        # 计算奖励
        result = self._create_result()

        # 切磋模式：恢复状态
        if self.mode == CombatMode.SPAR:
            self._restore_initial_state()
            self._log("切磋结束，双方状态已恢复")

        # 死斗模式且玩家胜利：检查是否触发处决流程
        # 只有击败NPC敌人时才触发处决选择
        if (self.mode == CombatMode.DEATHMATCH and
            self.status == CombatStatus.PLAYER_WIN and
            self.enemy and
            self.enemy.unit_type == "npc"):
            result.execution_pending = True  # 标记等待处决选择
            result.can_execute = True  # 标记可以处决
            result.enemy_npc = self._enemy_npc  # 保存原始NPC对象引用
            self._log(f"{self.enemy.name} 已战败，等待处决决定...")

        return result
    
    def _restore_initial_state(self):
        """恢复初始状态（切磋模式）"""
        if self.player:
            self.player.health = self._initial_player_health
            self.player.mana = self._initial_player_mana
        if self.enemy:
            self.enemy.health = self._initial_enemy_health
            self.enemy.mana = self._initial_enemy_mana
    
    def _create_result(self) -> CombatResult:
        """创建战斗结果"""
        winner = None
        loser = None
        
        if self.status == CombatStatus.PLAYER_WIN:
            winner = self.player
            loser = self.enemy
        elif self.status == CombatStatus.ENEMY_WIN:
            winner = self.enemy
            loser = self.player
        
        # 计算奖励
        exp_reward = 0
        spirit_stones_reward = 0
        loot = []
        
        if winner and loser:
            if self.mode == CombatMode.SPAR:
                exp_reward = self._calculate_spar_exp(winner, loser)
            else:
                exp_reward, spirit_stones_reward, loot = self._calculate_deathmatch_rewards(winner, loser)
        
        return CombatResult(
            status=self.status,
            winner=winner,
            loser=loser,
            exp_reward=exp_reward,
            spirit_stones_reward=spirit_stones_reward,
            loot=loot,
            combat_log=self.combat_log.copy(),
            turns=self.turn,
            mode=self.mode,
            # 处决相关字段默认值（在end_combat中会根据条件更新）
            execution_pending=False,  # 默认不等待处决选择
            can_execute=False,  # 默认可处决状态为否
            enemy_npc=None  # 默认无NPC对象引用
        )
    
    def _calculate_spar_exp(self, winner: CombatUnit, loser: CombatUnit) -> int:
        """计算切磋经验奖励"""
        base_exp = 10
        level_diff = loser.level - winner.level
        
        if level_diff > 0:
            base_exp += level_diff * 5
        else:
            base_exp = max(5, base_exp + level_diff * 2)
        
        # 胜者获得更多
        if winner == self.player:
            return base_exp
        else:
            return max(5, base_exp // 2)
    
    def _calculate_deathmatch_rewards(self, winner: CombatUnit, loser: CombatUnit) -> Tuple[int, int, List[str]]:
        """计算死斗奖励"""
        # 基础奖励
        base_exp = 50
        base_spirit_stones = 20
        
        # 根据等级差调整
        level_diff = loser.level - winner.level
        if level_diff > 0:
            multiplier = 1 + level_diff * 0.2
        else:
            multiplier = max(0.5, 1 + level_diff * 0.1)
        
        exp = int(base_exp * multiplier)
        spirit_stones = int(base_spirit_stones * multiplier)
        
        # 掉落物品
        loot = []
        if loser.unit_type == "beast":
            # 妖兽掉落材料
            loot = self._generate_beast_loot(loser)
        elif loser.unit_type == "npc":
            # NPC可能掉落物品
            if random.random() < 0.3:
                loot = self._generate_npc_loot(loser)
        
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
    
    def _log(self, message: str):
        """记录战斗日志"""
        self.combat_log.append(message)
    
    def get_combat_status_text(self) -> str:
        """获取战斗状态文本"""
        lines = [
            f"=== 战斗状态 ===",
            f"",
            f"{self.player.name}: {self.player.health}/{self.player.max_health} HP | {self.player.mana}/{self.player.max_mana} MP",
            f"{self.enemy.name}: {self.enemy.health}/{self.enemy.max_health} HP | {self.enemy.mana}/{self.enemy.mana} MP",
            f"",
            f"当前回合: {self.turn}",
            f"当前行动: {self.current_turn_unit.name if self.current_turn_unit else '无'}",
        ]
        return "\n".join(lines)
    
    def get_available_actions(self) -> List[str]:
        """获取可用行动列表"""
        actions = ["attack", "defend", "flee"]
        
        # 检查是否有可用技能
        if self.player and self.player.get_available_skills():
            actions.insert(1, "skill")
        
        return actions


def create_player_combat_unit(player) -> CombatUnit:
    """
    从玩家对象创建战斗单位
    
    Args:
        player: Player对象
        
    Returns:
        CombatUnit
    """
    # 计算战斗属性（确保是整数）
    from config import REALM_NAME_TO_LEVEL
    
    if isinstance(player.stats.realm_level, str):
        realm_level = REALM_NAME_TO_LEVEL.get(player.stats.realm_level, 0)
        if realm_level == 0 and player.stats.realm_level.isdigit():
            realm_level = int(player.stats.realm_level)
    else:
        realm_level = int(player.stats.realm_level)
    
    realm_layer = int(player.stats.realm_layer) if isinstance(player.stats.realm_layer, str) else player.stats.realm_layer
    realm_bonus = realm_level * 10
    
    unit = CombatUnit(
        name=player.stats.name,
        unit_type="player",
        level=realm_level * 9 + realm_layer,
        health=player.stats.health,
        max_health=player.stats.max_health,
        mana=player.stats.spiritual_power,
        max_mana=player.stats.max_spiritual_power,
        attack=20 + realm_bonus + getattr(player.stats, 'attack', 0),
        defense=10 + realm_bonus // 2 + getattr(player.stats, 'defense', 0),
        speed=10 + getattr(player.stats, 'speed', 0),
        crit_rate=getattr(player.stats, 'crit_rate', 0.05),
        dodge_rate=getattr(player.stats, 'dodge_rate', 0.05),
    )
    
    # 添加功法技能
    for tech_name in player.techniques.learned_techniques.keys():
        from config.techniques import get_technique
        technique = get_technique(tech_name)
        if technique and getattr(technique, 'is_combat_skill', False):
            skill = CombatSkill(
                name=technique.name,
                description=technique.description,
                damage=int(technique.combat_power_bonus * 50),
                damage_type=getattr(technique, 'damage_type', DamageType.PHYSICAL),
                mana_cost=getattr(technique, 'mana_cost', 10),
                cooldown=getattr(technique, 'cooldown', 0),
            )
            unit.skills.append(skill)
    
    return unit


def create_npc_combat_unit(npc) -> CombatUnit:
    """
    从NPC对象创建战斗单位
    
    Args:
        npc: NPC对象
        
    Returns:
        CombatUnit
    """
    # 处理realm_level，可能是数字或境界名称
    from config import REALM_NAME_TO_LEVEL
    if isinstance(npc.data.realm_level, str):
        # 尝试从境界名称获取等级
        realm_level = REALM_NAME_TO_LEVEL.get(npc.data.realm_level, 0)
        if realm_level == 0 and npc.data.realm_level.isdigit():
            realm_level = int(npc.data.realm_level)
    else:
        realm_level = int(npc.data.realm_level)
    
    realm_bonus = realm_level * 10
    
    unit = CombatUnit(
        name=npc.data.dao_name,
        unit_type="npc",
        level=realm_level * 9 + random.randint(1, 9),
        health=100 + realm_bonus * 10,
        max_health=100 + realm_bonus * 10,
        mana=50 + realm_bonus * 5,
        max_mana=50 + realm_bonus * 5,
        attack=15 + realm_bonus,
        defense=8 + realm_bonus // 2,
        speed=8 + random.randint(0, 10),
        crit_rate=0.03 + realm_level * 0.01,
        dodge_rate=0.03 + realm_level * 0.01,
    )
    
    # NPC根据门派添加技能
    if npc.data.sect_specialty == "剑道":
        unit.skills.append(CombatSkill(
            name="剑气斩",
            damage=30 + realm_bonus,
            damage_type=DamageType.PHYSICAL,
            mana_cost=15,
            cooldown=2,
        ))
    elif npc.data.sect_specialty == "炼丹术":
        unit.skills.append(CombatSkill(
            name="毒雾",
            damage=20 + realm_bonus,
            damage_type=DamageType.MAGIC,
            mana_cost=10,
            cooldown=1,
        ))
    
    return unit


def create_beast_combat_unit(beast_data: Dict[str, Any]) -> CombatUnit:
    """
    从妖兽数据创建战斗单位
    
    Args:
        beast_data: 妖兽数据字典
        
    Returns:
        CombatUnit
    """
    level = beast_data.get("level", 1)
    realm_level = beast_data.get("realm_level", 0)
    
    unit = CombatUnit(
        name=beast_data.get("name", "未知妖兽"),
        unit_type="beast",
        level=level,
        health=beast_data.get("health", 80 + level * 20),
        max_health=beast_data.get("health", 80 + level * 20),
        mana=beast_data.get("mana", 30 + level * 5),
        max_mana=beast_data.get("mana", 30 + level * 5),
        attack=beast_data.get("attack", 12 + level * 3),
        defense=beast_data.get("defense", 5 + level * 2),
        speed=beast_data.get("speed", 5 + level * 2),
        crit_rate=beast_data.get("crit_rate", 0.05),
        dodge_rate=beast_data.get("dodge_rate", 0.03),
    )
    
    # 添加妖兽技能
    skills_data = beast_data.get("skills", [])
    for skill_data in skills_data:
        skill = CombatSkill(
            name=skill_data.get("name", "攻击"),
            damage=skill_data.get("damage", 20),
            damage_type=DamageType(skill_data.get("damage_type", "PHYSICAL")),
            mana_cost=skill_data.get("mana_cost", 0),
            cooldown=skill_data.get("cooldown", 0),
        )
        unit.skills.append(skill)
    
    return unit
