"""
灵兽系统模块
实现灵兽捕捉、培养、进化、技能等功能
"""

import random
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

from config.pet_config import (
    PetType, PetRarity, SkillType, PetTemplate, PetSkill, EvolutionStage,
    PET_TEMPLATES_DB, PET_SKILLS_DB,
    get_pet_template, get_pet_skill, get_random_pet_by_location,
    calculate_catch_success_rate, calculate_exp_to_next_level,
    calculate_level_up_attributes, get_random_potential,
    get_type_name, get_rarity_color
)
from storage.database import Database


@dataclass
class SpiritPet:
    """灵兽数据类"""
    id: str
    player_id: str
    pet_template_id: str
    name: str
    pet_type: PetType
    level: int = 1
    exp: int = 0
    exp_to_next: int = 100
    stage: int = 1
    is_active: bool = True
    is_battle: bool = False
    
    # 基础属性
    attack: int = 10
    defense: int = 10
    health: int = 100
    max_health: int = 100
    speed: int = 10
    
    # 资质属性
    attack_potential: int = 50
    defense_potential: int = 50
    health_potential: int = 50
    speed_potential: int = 50
    
    # 成长值
    growth_rate: float = 1.0
    
    # 亲密度
    intimacy: int = 0
    max_intimacy: int = 100
    
    # 状态
    status: str = "normal"
    
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class CatchResult:
    """捕捉结果数据类"""
    success: bool
    message: str
    pet: Optional[SpiritPet] = None
    catch_rate: float = 0.0


@dataclass
class LevelUpResult:
    """升级结果数据类"""
    success: bool
    message: str
    level_gained: int = 0
    attribute_growth: Dict[str, int] = field(default_factory=dict)
    new_skills: List[str] = field(default_factory=list)


@dataclass
class EvolutionResult:
    """进化结果数据类"""
    success: bool
    message: str
    new_stage: int = 1
    new_name: str = ""
    attribute_bonus: Dict[str, int] = field(default_factory=dict)
    new_skills: List[str] = field(default_factory=list)


@dataclass
class TrainingResult:
    """培养结果数据类"""
    success: bool
    message: str
    attribute_changed: str = ""
    old_value: int = 0
    new_value: int = 0
    cost: Dict[str, Any] = field(default_factory=dict)


class PetSystem:
    """
    灵兽系统管理器
    管理灵兽捕捉、培养、进化、技能等功能
    """
    
    def __init__(self, db: Database = None):
        """
        初始化灵兽系统
        
        Args:
            db: 数据库实例
        """
        self.db = db or Database()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            self.db.init_pet_tables()
        except Exception as e:
            print(f"初始化灵兽数据库表时出错: {e}")
    
    # ==================== 灵兽捕捉功能 ====================
    
    def encounter_pet(self, location: str, player_level: int = 1) -> Optional[PetTemplate]:
        """
        在指定地点遇到灵兽
        
        Args:
            location: 地点名称
            player_level: 玩家等级
            
        Returns:
            遇到的灵兽模板，如果没有则返回None
        """
        # 30%概率遇到灵兽
        if random.random() > 0.3:
            return None
        
        return get_random_pet_by_location(location, player_level)
    
    def attempt_catch(
        self,
        player_id: str,
        pet_template: PetTemplate,
        pet_health_percent: float,
        player_level: int,
        player_spiritual_power: int,
        location: str,
        catch_item_bonus: float = 0.0
    ) -> CatchResult:
        """
        尝试捕捉灵兽
        
        Args:
            player_id: 玩家ID
            pet_template: 灵兽模板
            pet_health_percent: 灵兽剩余血量百分比
            player_level: 玩家等级
            player_spiritual_power: 玩家灵力
            location: 捕捉地点
            catch_item_bonus: 捕捉道具加成
            
        Returns:
            捕捉结果
        """
        # 计算成功率
        catch_rate = calculate_catch_success_rate(
            pet_template, pet_health_percent, player_level,
            player_spiritual_power, catch_item_bonus
        )
        
        # 记录捕捉尝试
        self.db.save_catch_record({
            'player_id': player_id,
            'pet_template_id': pet_template.template_id,
            'pet_name': pet_template.name,
            'location': location,
            'success': False  # 先记录为失败，成功后再更新
        })
        
        # 判定是否成功
        if random.random() <= catch_rate:
            # 捕捉成功，创建灵兽
            pet = self._create_pet_from_template(player_id, pet_template)
            
            # 保存到数据库
            self._save_pet_to_db(pet)
            
            # 学习初始技能
            for skill_id in pet_template.initial_skills:
                self._learn_skill(pet.id, skill_id)
            
            return CatchResult(
                success=True,
                message=f"恭喜！成功捕捉到【{pet_template.rarity.value}】{pet_template.name}！",
                pet=pet,
                catch_rate=catch_rate
            )
        else:
            return CatchResult(
                success=False,
                message=f"捕捉失败...{pet_template.name}逃走了",
                catch_rate=catch_rate
            )
    
    def _create_pet_from_template(self, player_id: str, template: PetTemplate) -> SpiritPet:
        """从模板创建灵兽"""
        now = datetime.now().isoformat()
        
        # 随机生成资质
        attack_potential = get_random_potential(template.min_attack_potential, template.max_attack_potential)
        defense_potential = get_random_potential(template.min_defense_potential, template.max_defense_potential)
        health_potential = get_random_potential(template.min_health_potential, template.max_health_potential)
        speed_potential = get_random_potential(template.min_speed_potential, template.max_speed_potential)
        
        # 随机生成成长率
        growth_rate = round(random.uniform(template.min_growth_rate, template.max_growth_rate), 2)
        
        # 计算初始属性（根据资质调整）
        attack = int(template.base_attack * (attack_potential / 50))
        defense = int(template.base_defense * (defense_potential / 50))
        health = int(template.base_health * (health_potential / 50))
        speed = int(template.base_speed * (speed_potential / 50))
        
        return SpiritPet(
            id=str(uuid.uuid4()),
            player_id=player_id,
            pet_template_id=template.template_id,
            name=template.name,
            pet_type=template.pet_type,
            level=1,
            exp=0,
            exp_to_next=calculate_exp_to_next_level(1, growth_rate),
            stage=1,
            is_active=True,
            is_battle=False,
            attack=attack,
            defense=defense,
            health=health,
            max_health=health,
            speed=speed,
            attack_potential=attack_potential,
            defense_potential=defense_potential,
            health_potential=health_potential,
            speed_potential=speed_potential,
            growth_rate=growth_rate,
            intimacy=0,
            max_intimacy=100,
            status="normal",
            created_at=now,
            updated_at=now
        )
    
    # ==================== 灵兽培养功能 ====================
    
    def gain_exp(self, pet_id: str, exp_amount: int) -> LevelUpResult:
        """
        灵兽获得经验
        
        Args:
            pet_id: 灵兽ID
            exp_amount: 获得的经验值
            
        Returns:
            升级结果
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return LevelUpResult(success=False, message="灵兽不存在")
        
        pet = self._dict_to_pet(pet_data)
        template = get_pet_template(pet.pet_template_id)
        
        if not template:
            return LevelUpResult(success=False, message="灵兽模板不存在")
        
        old_level = pet.level
        pet.exp += exp_amount
        
        level_gained = 0
        new_skills = []
        total_growth = {"attack": 0, "defense": 0, "health": 0, "speed": 0}
        
        # 检查是否升级
        while pet.exp >= pet.exp_to_next and pet.level < 100:
            pet.exp -= pet.exp_to_next
            pet.level += 1
            level_gained += 1
            
            # 计算属性增长
            potentials = {
                "attack_potential": pet.attack_potential,
                "defense_potential": pet.defense_potential,
                "health_potential": pet.health_potential,
                "speed_potential": pet.speed_potential
            }
            growth = calculate_level_up_attributes(pet.pet_type, pet.level, potentials, pet.growth_rate)
            
            pet.attack += growth["attack"]
            pet.defense += growth["defense"]
            pet.health += growth["health"]
            pet.max_health += growth["health"]
            pet.speed += growth["speed"]
            
            for key, value in growth.items():
                total_growth[key] += value
            
            # 更新下一级所需经验
            pet.exp_to_next = calculate_exp_to_next_level(pet.level, pet.growth_rate)
            
            # 检查是否有新技能可学习
            for skill_id in template.initial_skills:
                skill = get_pet_skill(skill_id)
                if skill and skill.learn_level == pet.level and skill.learn_stage <= pet.stage:
                    if skill_id not in [s['skill_id'] for s in self.db.get_pet_skills(pet_id)]:
                        self._learn_skill(pet_id, skill_id)
                        new_skills.append(skill.name)
        
        # 保存更新
        self._save_pet_to_db(pet)
        
        if level_gained > 0:
            message = f"{pet.name} 升到了 {pet.level} 级！"
            if new_skills:
                message += f" 学会了新技能：{', '.join(new_skills)}"
        else:
            message = f"{pet.name} 获得了 {exp_amount} 点经验"
        
        return LevelUpResult(
            success=True,
            message=message,
            level_gained=level_gained,
            attribute_growth=total_growth,
            new_skills=new_skills
        )
    
    def increase_intimacy(self, pet_id: str, amount: int = 5) -> bool:
        """
        增加亲密度
        
        Args:
            pet_id: 灵兽ID
            amount: 增加量
            
        Returns:
            是否成功
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False
        
        pet = self._dict_to_pet(pet_data)
        pet.intimacy = min(pet.max_intimacy, pet.intimacy + amount)
        
        self._save_pet_to_db(pet)
        return True
    
    def train_potential(
        self,
        pet_id: str,
        attribute: str,
        player_spirit_stones: int
    ) -> TrainingResult:
        """
        培养资质
        
        Args:
            pet_id: 灵兽ID
            attribute: 要培养的属性 (attack/defense/health/speed)
            player_spirit_stones: 玩家拥有的灵石数量
            
        Returns:
            培养结果
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return TrainingResult(success=False, message="灵兽不存在")
        
        pet = self._dict_to_pet(pet_data)
        
        # 检查属性名
        potential_attr = f"{attribute}_potential"
        if not hasattr(pet, potential_attr):
            return TrainingResult(success=False, message="无效的属性")
        
        current_value = getattr(pet, potential_attr)
        
        # 检查是否已达上限
        if current_value >= 100:
            return TrainingResult(success=False, message="该资质已达到上限")
        
        # 计算培养成本
        cost = current_value * 10  # 每点资质需要10灵石
        
        if player_spirit_stones < cost:
            return TrainingResult(
                success=False,
                message=f"灵石不足，需要 {cost} 灵石"
            )
        
        # 计算培养效果（随机增加1-3点）
        increase = random.randint(1, 3)
        new_value = min(100, current_value + increase)
        actual_increase = new_value - current_value
        
        # 更新资质
        setattr(pet, potential_attr, new_value)
        
        # 保存
        self._save_pet_to_db(pet)
        
        # 记录培养
        self.db.save_training_record({
            'pet_id': pet_id,
            'training_type': 'potential',
            'attribute_changed': attribute,
            'old_value': current_value,
            'new_value': new_value,
            'cost': {'spirit_stones': cost}
        })
        
        attr_names = {
            'attack': '攻击资质',
            'defense': '防御资质',
            'health': '生命资质',
            'speed': '速度资质'
        }
        
        return TrainingResult(
            success=True,
            message=f"培养成功！{attr_names.get(attribute, attribute)} 提升了 {actual_increase} 点",
            attribute_changed=attribute,
            old_value=current_value,
            new_value=new_value,
            cost={'spirit_stones': cost}
        )
    
    def rest_pet(self, pet_id: str) -> bool:
        """
        让灵兽休息恢复
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            是否成功
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False
        
        pet = self._dict_to_pet(pet_data)
        pet.health = pet.max_health
        pet.status = "normal"
        
        self._save_pet_to_db(pet)
        return True
    
    # ==================== 灵兽进化功能 ====================
    
    def can_evolve(self, pet_id: str) -> Tuple[bool, str, Optional[EvolutionStage]]:
        """
        检查灵兽是否可以进化
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            (是否可以进化, 提示信息, 下一进化阶段)
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False, "灵兽不存在", None
        
        pet = self._dict_to_pet(pet_data)
        template = get_pet_template(pet.pet_template_id)
        
        if not template:
            return False, "灵兽模板不存在", None
        
        # 检查是否还有下一阶段
        if pet.stage >= len(template.evolution_stages):
            return False, "该灵兽已达到最终形态", None
        
        next_stage = template.evolution_stages[pet.stage]  # stage是1-based索引
        
        # 检查等级要求
        if pet.level < next_stage.required_level:
            return False, f"需要达到 {next_stage.required_level} 级才能进化", None
        
        # 检查亲密度要求
        if pet.intimacy < next_stage.required_intimacy:
            return False, f"需要亲密度达到 {next_stage.required_intimacy} 才能进化", None
        
        return True, "可以进化", next_stage
    
    def evolve_pet(self, pet_id: str, player_inventory: Dict[str, int]) -> EvolutionResult:
        """
        进化灵兽
        
        Args:
            pet_id: 灵兽ID
            player_inventory: 玩家背包物品
            
        Returns:
            进化结果
        """
        can_evo, message, next_stage = self.can_evolve(pet_id)
        
        if not can_evo:
            return EvolutionResult(success=False, message=message)
        
        pet_data = self.db.get_spirit_pet(pet_id)
        pet = self._dict_to_pet(pet_data)
        template = get_pet_template(pet.pet_template_id)
        
        # 检查所需物品
        if next_stage.required_items:
            for item_name, count in next_stage.required_items.items():
                if player_inventory.get(item_name, 0) < count:
                    return EvolutionResult(
                        success=False,
                        message=f"进化材料不足，需要 {item_name} x{count}"
                    )
        
        # 记录进化前状态
        old_stage = pet.stage
        old_name = pet.name
        
        # 执行进化
        pet.stage = next_stage.stage
        pet.name = next_stage.name
        
        # 应用属性加成
        for attr, bonus in next_stage.attribute_bonus.items():
            current_val = getattr(pet, attr, 0)
            setattr(pet, attr, current_val + bonus)
        
        # 更新最大生命值
        pet.max_health = pet.health
        
        # 学习新技能
        new_skills = []
        for skill_id in next_stage.new_skills:
            skill = get_pet_skill(skill_id)
            if skill:
                self._learn_skill(pet_id, skill_id)
                new_skills.append(skill.name)
        
        # 保存
        self._save_pet_to_db(pet)
        
        # 记录进化
        self.db.save_pet_evolution({
            'pet_id': pet_id,
            'from_stage': old_stage,
            'to_stage': pet.stage,
            'from_name': old_name,
            'to_name': pet.name
        })
        
        return EvolutionResult(
            success=True,
            message=f"恭喜！{old_name} 成功进化为 {pet.name}！",
            new_stage=pet.stage,
            new_name=pet.name,
            attribute_bonus=next_stage.attribute_bonus,
            new_skills=new_skills
        )
    
    # ==================== 灵兽技能功能 ====================
    
    def _learn_skill(self, pet_id: str, skill_id: str) -> bool:
        """
        让灵兽学习技能
        
        Args:
            pet_id: 灵兽ID
            skill_id: 技能ID
            
        Returns:
            是否成功
        """
        skill = get_pet_skill(skill_id)
        if not skill:
            return False
        
        # 检查是否已学习
        existing_skills = self.db.get_pet_skills(pet_id)
        if any(s['skill_id'] == skill_id for s in existing_skills):
            return False
        
        # 保存技能
        self.db.save_pet_skill({
            'pet_id': pet_id,
            'skill_id': skill_id,
            'skill_name': skill.name,
            'skill_type': skill.skill_type.value,
            'level': 1,
            'max_level': skill.max_level,
            'damage': skill.damage,
            'effect_type': skill.effect_type,
            'effect_value': skill.effect_value,
            'cooldown': skill.cooldown,
            'mana_cost': skill.mana_cost,
            'description': skill.description,
            'is_active': True
        })
        
        return True
    
    def upgrade_skill(self, pet_id: str, skill_id: str, player_spirit_stones: int) -> Tuple[bool, str]:
        """
        升级技能
        
        Args:
            pet_id: 灵兽ID
            skill_id: 技能ID
            player_spirit_stones: 玩家拥有的灵石数量
            
        Returns:
            (是否成功, 提示信息)
        """
        skills = self.db.get_pet_skills(pet_id)
        skill_data = next((s for s in skills if s['skill_id'] == skill_id), None)
        
        if not skill_data:
            return False, "技能不存在"
        
        if skill_data['level'] >= skill_data['max_level']:
            return False, "技能已达到最高等级"
        
        # 计算升级成本
        cost = skill_data['level'] * 50
        
        if player_spirit_stones < cost:
            return False, f"灵石不足，需要 {cost} 灵石"
        
        # 升级技能
        new_level = skill_data['level'] + 1
        self.db.update_pet_skill_level(skill_data['id'], new_level)
        
        return True, f"{skill_data['skill_name']} 升级到 {new_level} 级！"
    
    def get_pet_skills(self, pet_id: str) -> List[Dict[str, Any]]:
        """
        获取灵兽的所有技能
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            技能列表
        """
        return self.db.get_pet_skills(pet_id)
    
    # ==================== 出战功能 ====================
    
    def set_battle_pet(self, player_id: str, pet_id: str) -> Tuple[bool, str]:
        """
        设置出战灵兽
        
        Args:
            player_id: 玩家ID
            pet_id: 灵兽ID
            
        Returns:
            (是否成功, 提示信息)
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False, "灵兽不存在"
        
        if pet_data['player_id'] != player_id:
            return False, "这不是你的灵兽"
        
        if pet_data['health'] <= 0:
            return False, "灵兽生命值不足，无法出战"
        
        # 先清除当前出战灵兽
        self.db.clear_battle_pet(player_id)
        
        # 设置新的出战灵兽
        self.db.update_pet_battle_status(pet_id, True)
        
        return True, f"{pet_data['name']} 已设置为出战状态"
    
    def unset_battle_pet(self, player_id: str, pet_id: str) -> Tuple[bool, str]:
        """
        取消灵兽出战
        
        Args:
            player_id: 玩家ID
            pet_id: 灵兽ID
            
        Returns:
            (是否成功, 提示信息)
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False, "灵兽不存在"
        
        if pet_data['player_id'] != player_id:
            return False, "这不是你的灵兽"
        
        self.db.update_pet_battle_status(pet_id, False)
        
        return True, f"{pet_data['name']} 已休息"
    
    def get_battle_pet(self, player_id: str) -> Optional[SpiritPet]:
        """
        获取玩家当前出战的灵兽
        
        Args:
            player_id: 玩家ID
            
        Returns:
            出战灵兽，如果没有则返回None
        """
        pet_data = self.db.get_battle_pet(player_id)
        if pet_data:
            return self._dict_to_pet(pet_data)
        return None
    
    # ==================== 查询功能 ====================
    
    def get_player_pets(self, player_id: str) -> List[SpiritPet]:
        """
        获取玩家的所有灵兽
        
        Args:
            player_id: 玩家ID
            
        Returns:
            灵兽列表
        """
        pets_data = self.db.get_player_spirit_pets(player_id)
        return [self._dict_to_pet(p) for p in pets_data]
    
    def get_pet(self, pet_id: str) -> Optional[SpiritPet]:
        """
        获取灵兽信息
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            灵兽信息
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if pet_data:
            return self._dict_to_pet(pet_data)
        return None
    
    def get_pet_evolution_history(self, pet_id: str) -> List[Dict[str, Any]]:
        """
        获取灵兽的进化历史
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            进化历史列表
        """
        return self.db.get_pet_evolutions(pet_id)
    
    def get_catch_history(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取捕捉历史
        
        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制
            
        Returns:
            捕捉历史列表
        """
        return self.db.get_catch_records(player_id, limit)
    
    def get_training_history(self, pet_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取培养历史
        
        Args:
            pet_id: 灵兽ID
            limit: 返回记录数量限制
            
        Returns:
            培养历史列表
        """
        return self.db.get_training_records(pet_id, limit)
    
    # ==================== 辅助方法 ====================
    
    def _save_pet_to_db(self, pet: SpiritPet):
        """保存灵兽到数据库"""
        pet.updated_at = datetime.now().isoformat()
        self.db.save_spirit_pet({
            'id': pet.id,
            'player_id': pet.player_id,
            'pet_template_id': pet.pet_template_id,
            'name': pet.name,
            'pet_type': pet.pet_type.value,
            'level': pet.level,
            'exp': pet.exp,
            'exp_to_next': pet.exp_to_next,
            'stage': pet.stage,
            'is_active': pet.is_active,
            'is_battle': pet.is_battle,
            'attack': pet.attack,
            'defense': pet.defense,
            'health': pet.health,
            'max_health': pet.max_health,
            'speed': pet.speed,
            'attack_potential': pet.attack_potential,
            'defense_potential': pet.defense_potential,
            'health_potential': pet.health_potential,
            'speed_potential': pet.speed_potential,
            'growth_rate': pet.growth_rate,
            'intimacy': pet.intimacy,
            'max_intimacy': pet.max_intimacy,
            'status': pet.status,
            'created_at': pet.created_at,
            'updated_at': pet.updated_at
        })
    
    def _dict_to_pet(self, data: Dict[str, Any]) -> SpiritPet:
        """将字典转换为SpiritPet对象"""
        return SpiritPet(
            id=data['id'],
            player_id=data['player_id'],
            pet_template_id=data['pet_template_id'],
            name=data['name'],
            pet_type=PetType(data['pet_type']),
            level=data['level'],
            exp=data['exp'],
            exp_to_next=data['exp_to_next'],
            stage=data['stage'],
            is_active=data['is_active'],
            is_battle=data['is_battle'],
            attack=data['attack'],
            defense=data['defense'],
            health=data['health'],
            max_health=data['max_health'],
            speed=data['speed'],
            attack_potential=data['attack_potential'],
            defense_potential=data['defense_potential'],
            health_potential=data['health_potential'],
            speed_potential=data['speed_potential'],
            growth_rate=data['growth_rate'],
            intimacy=data['intimacy'],
            max_intimacy=data['max_intimacy'],
            status=data['status'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
    
    def release_pet(self, pet_id: str) -> Tuple[bool, str]:
        """
        放生灵兽
        
        Args:
            pet_id: 灵兽ID
            
        Returns:
            (是否成功, 提示信息)
        """
        pet_data = self.db.get_spirit_pet(pet_id)
        if not pet_data:
            return False, "灵兽不存在"
        
        pet_name = pet_data['name']
        
        # 删除灵兽（关联的技能、记录等会通过外键级联删除）
        if self.db.delete_spirit_pet(pet_id):
            return True, f"{pet_name} 已被放生"
        else:
            return False, "放生失败"


# 全局灵兽系统实例
_default_pet_system: Optional[PetSystem] = None


def get_pet_system(db: Database = None) -> PetSystem:
    """
    获取默认的灵兽系统实例
    
    Args:
        db: 数据库实例
        
    Returns:
        PetSystem实例
    """
    global _default_pet_system
    if _default_pet_system is None:
        _default_pet_system = PetSystem(db)
    return _default_pet_system
