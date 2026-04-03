"""战斗相关的实体"""
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from domain.value_objects.combat import CombatSkill, DamageType


@dataclass
class CombatUnit:
    """战斗单位实体"""
    # 唯一标识符
    id: str
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
    skill_cooldowns: Dict[str, int] = field(default_factory=dict)  # 技能冷却
    
    # 状态
    is_stunned: bool = False        # 是否眩晕
    buffs: Dict[str, float] = field(default_factory=dict)
    
    # 战斗记录
    damage_dealt: int = 0
    damage_taken: int = 0
    
    def __post_init__(self):
        if not self.skills:
            self.skills = []
        if not self.skill_cooldowns:
            self.skill_cooldowns = {}
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
        
        # 应用防御增益
        if "defend" in self.buffs:
            actual_damage = int(actual_damage * (1 - self.buffs["defend"]))
        
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
        return self.mana >= skill.mana_cost and self.skill_cooldowns.get(skill.name, 0) == 0
    
    def update_cooldowns(self):
        """更新技能冷却"""
        for skill_name in list(self.skill_cooldowns.keys()):
            if self.skill_cooldowns[skill_name] > 0:
                self.skill_cooldowns[skill_name] -= 1
            if self.skill_cooldowns[skill_name] <= 0:
                del self.skill_cooldowns[skill_name]
    
    def get_available_skills(self) -> List[CombatSkill]:
        """获取可用的技能列表"""
        return [s for s in self.skills if self.can_use_skill(s)]
    
    def use_skill(self, skill: CombatSkill) -> bool:
        """使用技能"""
        if not self.can_use_skill(skill):
            return False
        
        if not self.use_mana(skill.mana_cost):
            return False
        
        # 设置冷却
        if skill.cooldown > 0:
            self.skill_cooldowns[skill.name] = skill.cooldown
        
        # 处理技能效果
        for effect in skill.effects:
            effect_type = effect.get("type")
            if effect_type == "heal":
                heal_amount = effect.get("value", 0)
                self.heal(heal_amount)
            elif effect_type == "buff":
                buff_name = effect.get("name", "buff")
                self.buffs[buff_name] = effect.get("value", 0)
            elif effect_type == "stun":
                self.is_stunned = True
        
        return True
