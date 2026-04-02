"""
玩家系统模块
管理玩家属性、状态、存档等
"""

import random
import json
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    get_realm_info, get_realm_title, get_realm_icon,
    generate_spirit_root, get_spirit_root_info,
    calculate_cultivation_speed, GAME_CONFIG,
    TechniqueLearningRecord, Inventory
)


@dataclass
class PlayerStats:
    """玩家属性数据类"""
    # 基础属性
    name: str = "无名修士"
    age: int = 16
    lifespan: int = 80  # 寿元上限
    
    # 修为属性
    realm_level: int = 0  # 境界等级（0-7）
    realm_layer: int = 1  # 当前境界层数（1-9）
    exp: int = 0  # 经验值
    
    # 战斗属性
    health: int = 100  # 生命值
    max_health: int = 100
    spiritual_power: int = 50  # 灵力
    max_spiritual_power: int = 50
    
    # 资源属性
    spirit_stones: int = 100  # 灵石
    
    # 特殊属性
    fortune: int = 50  # 福缘（0-100）
    karma: int = 0  # 业力（-1000到1000）
    
    # 资质
    spirit_root: str = "wu"  # 灵根类型
    
    # 状态
    is_injured: bool = False  # 是否受伤
    injury_days: int = 0  # 受伤剩余天数
    is_dead: bool = False  # 是否死亡
    
    # 位置
    location: str = "新手村"  # 当前位置
    
    # 时间
    game_year: int = 1
    game_month: int = 1
    game_day: int = 1
    
    # 统计
    total_practices: int = 0  # 总修炼次数
    total_breakthroughs: int = 0  # 总突破次数
    death_count: int = 0  # 死亡次数
    
    # 战斗属性
    attack: int = 0  # 攻击力
    defense: int = 0  # 防御力
    speed: int = 10  # 速度
    crit_rate: float = 0.05  # 暴击率（默认5%）
    dodge_rate: float = 0.05  # 闪避率（默认5%）
    
    # 战斗记录
    combat_wins: int = 0  # 胜利次数
    combat_losses: int = 0  # 失败次数


class Player:
    """玩家类"""
    
    def __init__(self, name: str = "无名修士", load_from_db: bool = True, player_id: str = None):
        """
        初始化玩家
        
        Args:
            name: 玩家名字
            load_from_db: 是否从数据库加载
            player_id: 玩家ID（如果为None则自动生成）
        """
        import uuid
        self.id = player_id or f"player_{uuid.uuid4().hex[:8]}"
        self.stats = PlayerStats(name=name)
        
        # 功法系统
        self.techniques = TechniqueLearningRecord()
        
        # 背包系统
        self.inventory = Inventory(max_slots=50)
        
        # 装备栏
        self.equipped_treasures: Dict[str, str] = {}  # 部位 -> 法宝名称
        
        # 如果是新玩家，随机生成资质
        if not load_from_db:
            self._init_new_player()
        
        # 更新属性上限
        self._update_max_stats()
    
    def _init_new_player(self):
        """初始化新玩家"""
        # 随机生成灵根
        spirit_root_key, spirit_root = generate_spirit_root()
        self.stats.spirit_root = spirit_root_key
        
        # 根据灵根调整初始属性
        if spirit_root_key == "tian":
            self.stats.fortune = random.randint(70, 100)
        elif spirit_root_key == "wu":
            self.stats.fortune = random.randint(20, 60)
        else:
            self.stats.fortune = random.randint(40, 80)
        
        # 随机年龄（16-30岁）
        self.stats.age = random.randint(16, 30)
        
        # 初始化寿元
        self._update_lifespan()
    
    def _update_max_stats(self):
        """更新属性上限"""
        realm_info = get_realm_info(self.stats.realm_level)
        if realm_info:
            # 生命值上限 = 基础值 + 境界加成
            self.stats.max_health = 100 + self.stats.realm_level * 100
            # 灵力上限 = 基础值 + 境界加成
            self.stats.max_spiritual_power = 50 + self.stats.realm_level * 50
    
    def _update_lifespan(self):
        """更新寿元上限"""
        realm_info = get_realm_info(self.stats.realm_level)
        if realm_info:
            self.stats.lifespan = realm_info.lifespan
    
    def get_spirit_root_name(self) -> str:
        """获取灵根名称"""
        spirit_root = get_spirit_root_info(self.stats.spirit_root)
        return spirit_root.name
    
    def get_spirit_root_description(self) -> str:
        """获取灵根描述"""
        spirit_root = get_spirit_root_info(self.stats.spirit_root)
        return spirit_root.description
    
    def get_realm_name(self) -> str:
        """获取境界名称"""
        realm_info = get_realm_info(self.stats.realm_level)
        return realm_info.name if realm_info else "凡人"
    
    def get_realm_icon(self) -> str:
        """获取境界图标"""
        return get_realm_icon(self.stats.realm_level)
    
    def get_title(self, for_self: bool = True) -> str:
        """获取称谓"""
        return get_realm_title(self.stats.realm_level, for_self)
    
    def get_cultivation_speed(self) -> float:
        """获取修炼速度"""
        # 基础速度由灵根决定
        base_speed = calculate_cultivation_speed(self.stats.spirit_root)

        # 受伤时修炼速度减半
        if self.stats.is_injured:
            base_speed *= 0.5

        # 功法加成
        technique_bonus = self._calculate_technique_cultivation_bonus()
        base_speed *= (1 + technique_bonus)

        # 社交加成
        social_bonus = self._calculate_social_cultivation_bonus()
        base_speed *= (1 + social_bonus)

        return base_speed

    def _calculate_social_cultivation_bonus(self) -> float:
        """计算社交关系修炼速度加成"""
        bonus = 0.0

        try:
            from storage.database import Database
            db = Database()

            # 检查是否有道侣
            marriage = db.get_marriage(self.stats.name)
            if marriage:
                # 道侣加成：15%基础 + 亲密度额外加成
                intimacy = marriage.get('intimacy', 100)
                bonus += 0.15 + (intimacy / 1000)  # 15% + 最高10%

            # 检查师徒关系
            master_info = db.get_master(self.stats.name)
            if master_info:
                # 有师父加成：10%
                bonus += 0.10

            # 检查徒弟数量
            apprentices = db.get_apprentices(self.stats.name)
            if apprentices:
                # 每个徒弟提供2%加成，最多10%
                bonus += min(0.10, len(apprentices) * 0.02)

        except Exception as e:
            # 如果数据库查询失败，不应用加成
            pass

        return bonus
    
    def _calculate_technique_cultivation_bonus(self) -> float:
        """计算功法修炼速度加成"""
        bonus = 0.0
        for technique_name in self.techniques.learned_techniques.keys():
            from config import get_technique
            technique = get_technique(technique_name)
            if technique:
                level = self.techniques.get_technique_level(technique_name)
                bonus += technique.cultivation_speed_bonus * (1 + (level - 1) * 0.1)
        return bonus
    
    def get_combat_power_bonus(self) -> float:
        """获取战斗力加成"""
        bonus = 0.0
        # 功法加成
        for technique_name in self.techniques.learned_techniques.keys():
            from config import get_technique
            technique = get_technique(technique_name)
            if technique:
                level = self.techniques.get_technique_level(technique_name)
                bonus += technique.combat_power_bonus * (1 + (level - 1) * 0.1)

        # 社交加成
        social_bonus = self._calculate_social_combat_bonus()
        bonus += social_bonus

        # 法宝加成
        for treasure_name in self.equipped_treasures.values():
            from config import get_item
            item = get_item(treasure_name)
            if item and item.item_type.value == "法宝":
                # 法宝效果加成
                pass

        return bonus

    def _calculate_social_combat_bonus(self) -> float:
        """计算社交关系战斗加成"""
        bonus = 0.0

        try:
            from storage.database import Database
            db = Database()

            # 道侣战斗加成
            marriage = db.get_marriage(self.stats.name)
            if marriage:
                bonus += 0.10  # 10%战斗加成

            # 师父战斗加成（师父的指点）
            master_info = db.get_master(self.stats.name)
            if master_info:
                bonus += 0.05  # 5%战斗加成

        except Exception as e:
            pass

        return bonus

    def get_social_bonuses(self) -> Dict[str, Any]:
        """
        获取所有社交加成

        Returns:
            社交加成信息字典
        """
        bonuses = {
            'cultivation_speed': 0.0,
            'exp_bonus': 0.0,
            'combat_bonus': 0.0,
            'breakthrough_bonus': 0.0,
            'details': {}
        }

        try:
            from storage.database import Database
            db = Database()

            # 道侣加成
            marriage = db.get_marriage(self.stats.name)
            if marriage:
                intimacy = marriage.get('intimacy', 100)
                bonuses['cultivation_speed'] += 0.15 + (intimacy / 1000)
                bonuses['exp_bonus'] += 0.20
                bonuses['breakthrough_bonus'] += 0.10
                bonuses['combat_bonus'] += 0.10
                bonuses['details']['dao_lv'] = {
                    'partner_name': marriage.get('partner_name'),
                    'cultivation_speed_bonus': 0.15 + (intimacy / 1000),
                    'exp_bonus': 0.20,
                    'breakthrough_bonus': 0.10,
                    'combat_bonus': 0.10
                }

            # 师徒加成
            master_info = db.get_master(self.stats.name)
            if master_info:
                bonuses['cultivation_speed'] += 0.10
                bonuses['exp_bonus'] += 0.15
                bonuses['combat_bonus'] += 0.05
                bonuses['details']['master'] = {
                    'master_name': master_info.get('master_name'),
                    'cultivation_speed_bonus': 0.10,
                    'exp_bonus': 0.15,
                    'combat_bonus': 0.05
                }

            # 徒弟加成
            apprentices = db.get_apprentices(self.stats.name)
            if apprentices:
                apprentice_bonus = min(0.10, len(apprentices) * 0.02)
                bonuses['cultivation_speed'] += apprentice_bonus
                bonuses['details']['apprentices'] = {
                    'count': len(apprentices),
                    'cultivation_speed_bonus': apprentice_bonus
                }

        except Exception as e:
            pass

        return bonuses
    
    def get_attack_power(self) -> int:
        """
        获取攻击威力
        
        Returns:
            攻击威力 = 基础攻击力 + 境界加成
        """
        # 境界加成：每级境界增加10点攻击力
        realm_bonus = self.stats.realm_level * 10
        return self.stats.attack + realm_bonus
    
    def get_defense_power(self) -> int:
        """
        获取防御威力
        
        Returns:
            防御威力 = 基础防御力 + 境界加成
        """
        # 境界加成：每级境界增加5点防御力
        realm_bonus = self.stats.realm_level * 5
        return self.stats.defense + realm_bonus
    
    def get_combat_stats(self) -> Dict[str, Any]:
        """
        获取战斗属性字典
        
        Returns:
            包含所有战斗属性的字典
        """
        return {
            "attack": self.stats.attack,
            "defense": self.stats.defense,
            "speed": self.stats.speed,
            "crit_rate": self.stats.crit_rate,
            "dodge_rate": self.stats.dodge_rate,
            "attack_power": self.get_attack_power(),
            "defense_power": self.get_defense_power(),
            "health": self.stats.health,
            "max_health": self.stats.max_health,
            "spiritual_power": self.stats.spiritual_power,
            "max_spiritual_power": self.stats.max_spiritual_power,
            "combat_wins": self.stats.combat_wins,
            "combat_losses": self.stats.combat_losses,
            "win_rate": self._calculate_win_rate()
        }
    
    def _calculate_win_rate(self) -> float:
        """计算胜率"""
        total = self.stats.combat_wins + self.stats.combat_losses
        if total == 0:
            return 0.0
        return self.stats.combat_wins / total
    
    def record_combat_win(self):
        """记录战斗胜利"""
        self.stats.combat_wins += 1
    
    def record_combat_loss(self):
        """记录战斗失败"""
        self.stats.combat_losses += 1
    
    def learn_technique(self, technique_name: str) -> Tuple[bool, str]:
        """
        学习功法
        
        Args:
            technique_name: 功法名称
            
        Returns:
            (是否成功, 消息)
        """
        from config import get_technique, can_learn_technique, calculate_learning_success_rate
        
        technique = get_technique(technique_name)
        if not technique:
            return False, f"功法《{technique_name}》不存在"
        
        # 检查是否已学习
        if technique_name in self.techniques.learned_techniques:
            return False, f"你已经学过《{technique_name}》了"
        
        # 检查学习条件
        if not can_learn_technique(technique_name, self.stats.realm_level, self.stats.spirit_root):
            return False, f"你的境界不足以学习《{technique_name}》"
        
        # 计算成功率
        success_rate = calculate_learning_success_rate(
            technique_name, 
            self.stats.realm_level,
            self.stats.fortune
        )
        
        # 判定是否成功
        import random
        if random.random() <= success_rate:
            self.techniques.learn_technique(technique_name)
            return True, f"成功习得《{technique_name}》！"
        else:
            return False, f"学习《{technique_name}》失败，需要更多悟性"
    
    def practice_technique(self, technique_name: str) -> Tuple[bool, str]:
        """
        练习功法
        
        Args:
            technique_name: 功法名称
            
        Returns:
            (是否成功, 消息)
        """
        if technique_name not in self.techniques.learned_techniques:
            return False, f"你还没有学习《{technique_name}》"
        
        self.techniques.practice_technique(technique_name, 0.1)
        mastery = self.techniques.get_mastery(technique_name)
        level = self.techniques.get_technique_level(technique_name)
        
        return True, f"练习《{technique_name}》，熟练度提升至{mastery:.1%}，等级{level}级"
    
    def get_learned_techniques(self) -> Dict[str, Dict]:
        """获取已学功法列表"""
        return self.techniques.learned_techniques
    
    def add_item(self, item_name: str, count: int = 1) -> Tuple[bool, str]:
        """
        添加道具到背包
        
        Args:
            item_name: 道具名称
            count: 数量
            
        Returns:
            (是否成功, 消息)
        """
        from config import get_item
        item = get_item(item_name)
        if not item:
            return False, f"道具《{item_name}》不存在"
        
        if self.inventory.add_item(item_name, count):
            return True, f"获得 {item_name} x{count}"
        else:
            return False, "背包已满"
    
    def use_item(self, item_name: str) -> Tuple[bool, str]:
        """
        使用道具
        
        Args:
            item_name: 道具名称
            
        Returns:
            (是否成功, 消息)
        """
        from config import get_item, ItemType
        
        # 先检查是否是数据库中的道具
        item = get_item(item_name)
        
        # 检查背包中是否有这个道具
        if self.inventory.get_item_count(item_name) <= 0:
            return False, f"你没有{item_name}"
        
        # 如果是数据库道具，使用原有逻辑
        if item:
            # 根据道具类型处理效果
            if item.item_type == ItemType.PILL:
                # 丹药效果
                if "恢复法力" in item.effects:
                    self.stats.spiritual_power = min(
                        self.stats.max_spiritual_power,
                        self.stats.spiritual_power + 50
                    )
                if "恢复伤势" in item.effects:
                    self.heal()
                if "突破筑基" in item.effects:
                    # 突破辅助效果
                    pass
                
                # 使用背包中的道具
                success, msg = self.inventory.use_item(item_name, 1)
                if success:
                    return True, f"使用{item.name}，{', '.join(item.effects)}"
                return False, msg
            
            elif item.item_type == ItemType.TREASURE:
                # 装备法宝
                return self.equip_treasure(item_name)
            
            else:
                return False, f"无法使用{item.name}"
        
        # 如果不是数据库道具，检查是否是生成道具
        elif item_name in self.inventory.generated_items:
            item_data = self.inventory.generated_items[item_name]
            item_type = item_data.get("type", "未知")
            effects = item_data.get("effects", [])
            
            # 处理生成道具的效果
            if item_type == "丹药" or item_type == "PILL":
                # 丹药效果 - 根据稀有度恢复不同量
                rarity = item_data.get("rarity", "普通")
                restore_amount = {
                    "普通": 30,
                    "稀有": 50,
                    "史诗": 80,
                    "传说": 120,
                    "神话": 200
                }.get(rarity, 30)
                
                self.stats.spiritual_power = min(
                    self.stats.max_spiritual_power,
                    self.stats.spiritual_power + restore_amount
                )
                
                # 使用背包中的道具
                success, msg = self.inventory.use_item(item_name, 1)
                if success:
                    return True, f"使用{item_name}，恢复了{restore_amount}点法力"
                return False, msg
            
            elif item_type == "法宝" or item_type == "MAGIC_TREASURE":
                # 装备生成的法宝
                return self.equip_generated_treasure(item_name, item_data)
            
            else:
                # 其他类型的生成道具
                success, msg = self.inventory.use_item(item_name, 1)
                if success:
                    return True, f"使用{item_name}"
                return False, msg
        
        else:
            return False, f"道具《{item_name}》不存在"
    
    def equip_treasure(self, treasure_name: str) -> Tuple[bool, str]:
        """
        装备法宝
        
        Args:
            treasure_name: 法宝名称
            
        Returns:
            (是否成功, 消息)
        """
        from config import get_item, ItemType
        
        item = get_item(treasure_name)
        if not item or item.item_type != ItemType.TREASURE:
            return False, f"{treasure_name}不是法宝"
        
        if self.inventory.get_item_count(treasure_name) <= 0:
            return False, f"你没有{treasure_name}"
        
        # 装备到对应部位（简化处理，所有法宝都装备到主手）
        slot = "main_hand"
        self.equipped_treasures[slot] = treasure_name
        
        return True, f"装备{treasure_name}"
    
    def equip_generated_treasure(self, treasure_name: str, item_data: Dict) -> Tuple[bool, str]:
        """
        装备生成的法宝
        
        Args:
            treasure_name: 法宝名称
            item_data: 法宝数据
            
        Returns:
            (是否成功, 消息)
        """
        if self.inventory.get_item_count(treasure_name) <= 0:
            return False, f"你没有{treasure_name}"
        
        # 装备到对应部位（简化处理，所有法宝都装备到主手）
        slot = "main_hand"
        self.equipped_treasures[slot] = treasure_name
        
        # 根据稀有度提供属性加成
        rarity = item_data.get("rarity", "普通")
        power_bonus = {
            "普通": 5,
            "稀有": 10,
            "史诗": 20,
            "传说": 35,
            "神话": 50
        }.get(rarity, 5)
        
        return True, f"装备{treasure_name}，攻击力+{power_bonus}"
    
    def get_inventory_info(self) -> str:
        """获取背包信息"""
        info = ["背包内容："]
        for item_name, data in self.inventory.items.items():
            info.append(f"  {item_name} x{data['count']}")
        
        if not self.inventory.items:
            info.append("  （空）")
        
        info.append(f"\n总价值：{self.inventory.get_total_value()} 灵石")
        return "\n".join(info)
    
    def get_exp_needed(self) -> int:
        """获取突破所需经验"""
        realm_info = get_realm_info(self.stats.realm_level)
        if realm_info:
            return realm_info.exp_to_next
        return 999999
    
    def get_exp_progress(self) -> Tuple[int, int, float]:
        """
        获取经验进度
        
        Returns:
            (当前境界内经验, 需要经验, 进度百分比)
        """
        realm_info = get_realm_info(self.stats.realm_level)
        if not realm_info:
            return (0, 1, 0.0)
        
        # 计算当前境界内的经验（确保不为负数）
        exp_in_realm = max(0, self.stats.exp - realm_info.exp_required)
        exp_needed = realm_info.exp_to_next
        progress = min(1.0, max(0.0, exp_in_realm / exp_needed))
        
        return (exp_in_realm, exp_needed, progress)
    
    def can_breakthrough(self) -> bool:
        """检查是否可以突破"""
        realm_info = get_realm_info(self.stats.realm_level)
        if not realm_info:
            return False
        
        return self.stats.exp >= realm_info.exp_required + realm_info.exp_to_next
    
    def add_exp(self, amount: int) -> int:
        """
        增加经验
        
        Args:
            amount: 经验值
            
        Returns:
            实际增加的经验值
        """
        self.stats.exp += amount
        return amount
    
    def advance_time(self, days: int = 1):
        """
        推进时间
        
        Args:
            days: 天数
        """
        for _ in range(days):
            self.stats.game_day += 1
            
            # 月份进位
            if self.stats.game_day > 30:
                self.stats.game_day = 1
                self.stats.game_month += 1
                
                # 年份进位
                if self.stats.game_month > 12:
                    self.stats.game_month = 1
                    self.stats.game_year += 1
                    
                    # 每年增加年龄
                    self.stats.age += 1
            
            # 受伤恢复
            if self.stats.is_injured:
                self.stats.injury_days -= 1
                if self.stats.injury_days <= 0:
                    self.stats.is_injured = False
                    self.stats.injury_days = 0
        
        # 检查寿元
        if self.stats.age >= self.stats.lifespan:
            self.stats.is_dead = True
    
    def injure(self, days: int = 180):
        """
        受伤
        
        Args:
            days: 受伤天数
        """
        self.stats.is_injured = True
        self.stats.injury_days = days
        # 生命值减半
        self.stats.health = self.stats.max_health // 2
    
    def heal(self):
        """恢复"""
        self.stats.is_injured = False
        self.stats.injury_days = 0
        self.stats.health = self.stats.max_health
        self.stats.spiritual_power = self.stats.max_spiritual_power
    
    def die(self, cause: str = "寿元耗尽") -> Dict[str, Any]:
        """
        死亡处理
        
        Args:
            cause: 死亡原因
            
        Returns:
            死亡信息
        """
        self.stats.is_dead = True
        self.stats.death_count += 1
        
        # 计算转世继承
        inheritance = {
            "exp": int(self.stats.exp * 0.3),
            "spirit_stones": int(self.stats.spirit_stones * 0.5),
            "fortune_bonus": min(10, self.stats.death_count * 2),
        }
        
        return {
            "name": self.stats.name,
            "age": self.stats.age,
            "realm": self.get_realm_name(),
            "cause": cause,
            "inheritance": inheritance,
        }
    
    def reincarnate(self, inheritance: Dict[str, Any]):
        """
        转世重生
        
        Args:
            inheritance: 继承的属性
        """
        # 保留部分属性
        old_name = self.stats.name
        old_death_count = self.stats.death_count
        
        # 重置属性
        self.stats = PlayerStats(name=old_name)
        self.stats.death_count = old_death_count
        
        # 继承经验
        self.stats.exp = inheritance.get("exp", 0)
        
        # 继承灵石
        self.stats.spirit_stones = inheritance.get("spirit_stones", 100)
        
        # 福缘加成
        fortune_bonus = inheritance.get("fortune_bonus", 0)
        self.stats.fortune = min(100, 50 + fortune_bonus)
        
        # 重新初始化
        self._init_new_player()
        self._update_max_stats()
        self._update_lifespan()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（完整序列化）"""
        return {
            "stats": asdict(self.stats),
            "techniques": {
                "learned": self.techniques.learned_techniques,
                "progress": self.techniques.learning_progress
            },
            "inventory": {
                "items": self.inventory.items,
                "generated_items": self.inventory.generated_items,
                "max_slots": self.inventory.max_slots
            },
            "equipped": self.equipped_treasures
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载（完整反序列化）"""
        if not isinstance(data, dict):
            print(f"警告: 玩家数据格式错误，期望字典但得到 {type(data)}")
            return
        
        # 加载基础属性
        stats_data = data.get("stats", {})
        
        # 如果没有stats键或stats为空，尝试从data中直接提取已知属性（兼容旧格式）
        if not stats_data:
            known_stats = ["name", "age", "lifespan", "realm_level", "realm_layer", "exp",
                          "health", "max_health", "spiritual_power", "max_spiritual_power",
                          "spirit_stones", "fortune", "karma", "spirit_root",
                          "is_injured", "injury_days", "is_dead", "location",
                          "game_year", "game_month", "game_day", "total_practices",
                          "total_breakthroughs", "death_count", "attack", "defense",
                          "speed", "crit_rate", "dodge_rate", "combat_wins", "combat_losses"]
            # 尝试从data的一级键中提取统计属性
            stats_data = {k: v for k, v in data.items() if k in known_stats}
            
            # 如果还是没有找到，可能数据格式有问题
            if not stats_data:
                print(f"警告: 无法从数据中提取玩家属性，数据键: {list(data.keys())}")
        
        # 加载stats数据
        for key, value in stats_data.items():
            if hasattr(self.stats, key):
                # 类型转换确保数据一致性
                if key in ["age", "lifespan", "realm_level", "realm_layer", "exp", 
                          "health", "max_health", "spiritual_power", "max_spiritual_power",
                          "spirit_stones", "fortune", "karma", "injury_days",
                          "game_year", "game_month", "game_day", "total_practices",
                          "total_breakthroughs", "death_count", "attack", "defense",
                          "speed", "combat_wins", "combat_losses"]:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        print(f"警告: 属性 {key} 的值 '{value}' 无法转换为整数，跳过")
                        continue
                elif key in ["is_injured", "is_dead"]:
                    value = bool(value)
                elif key in ["crit_rate", "dodge_rate"]:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        print(f"警告: 属性 {key} 的值 '{value}' 无法转换为浮点数，跳过")
                        continue
                elif key == "spirit_root":
                    value = str(value) if value else "wu"
                elif key == "name":
                    value = str(value) if value else "无名修士"
                elif key == "location":
                    value = str(value) if value else "新手村"
                setattr(self.stats, key, value)
        
        # 加载功法数据
        if "techniques" in data:
            tech_data = data["techniques"]
            self.techniques.learned_techniques = tech_data.get("learned", {})
            self.techniques.learning_progress = tech_data.get("progress", {})
        
        # 加载背包数据
        if "inventory" in data:
            inv_data = data["inventory"]
            # 处理新旧格式兼容
            if isinstance(inv_data, dict):
                if "items" in inv_data:
                    self.inventory.items = inv_data.get("items", {})
                    self.inventory.generated_items = inv_data.get("generated_items", {})
                    self.inventory.max_slots = inv_data.get("max_slots", 50)
                else:
                    # 旧格式直接是items字典
                    self.inventory.items = inv_data
        
        # 加载装备数据
        if "equipped" in data:
            self.equipped_treasures = data["equipped"]
        
        # 确保属性在有效范围内
        self._sanitize_stats()
        self._update_max_stats()
    
    def _sanitize_stats(self):
        """清理和验证属性值"""
        # 确保数值在合理范围内
        self.stats.health = max(0, min(self.stats.health, self.stats.max_health))
        self.stats.spiritual_power = max(0, min(self.stats.spiritual_power, self.stats.max_spiritual_power))
        self.stats.spirit_stones = max(0, self.stats.spirit_stones)
        self.stats.fortune = max(0, min(100, self.stats.fortune))
        self.stats.karma = max(-1000, min(1000, self.stats.karma))
        self.stats.age = max(1, self.stats.age)
        self.stats.realm_level = max(0, min(7, self.stats.realm_level))
        self.stats.realm_layer = max(1, min(9, self.stats.realm_layer))
    
    def add_karma(self, amount: int) -> int:
        """
        添加业力值
        
        Args:
            amount: 要添加的业力值（正数为善业，负数为恶业）
            
        Returns:
            实际变化的业力值
        """
        old_karma = self.stats.karma
        new_karma = old_karma + amount
        
        # 限制业力值在 -1000 到 1000 范围内
        new_karma = max(-1000, min(1000, new_karma))
        
        self.stats.karma = new_karma
        actual_change = new_karma - old_karma
        
        return actual_change
    
    def get_karma_level(self) -> str:
        """
        获取业力等级
        
        Returns:
            业力等级描述字符串
        """
        karma = self.stats.karma
        
        if karma < -500:
            return "魔头"
        elif karma < -200:
            return "恶人"
        elif karma < 0:
            return "偏恶"
        elif karma == 0:
            return "中立"
        elif karma < 200:
            return "偏善"
        elif karma < 500:
            return "善人"
        else:
            return "圣人"
    
    def get_karma_description(self) -> str:
        """
        获取业力描述（带emoji）
        
        Returns:
            带emoji的业力描述字符串
        """
        karma = self.stats.karma
        level = self.get_karma_level()
        
        if karma < -500:
            return f"☠️ {level} ({karma}) - 罪孽深重，天地不容"
        elif karma < -200:
            return f"😈 {level} ({karma}) - 作恶多端，人人得而诛之"
        elif karma < 0:
            return f"😒 {level} ({karma}) - 略有恶行，尚需反省"
        elif karma == 0:
            return f"😐 {level} ({karma}) - 不偏不倚，心如止水"
        elif karma < 200:
            return f"🙂 {level} ({karma}) - 心存善念，乐于助人"
        elif karma < 500:
            return f"😇 {level} ({karma}) - 广积善缘，德行高尚"
        else:
            return f"✨ {level} ({karma}) - 功德圆满，超凡入圣"
    
    def get_karma_color(self) -> str:
        """
        获取业力颜色（用于UI显示）
        
        Returns:
            颜色代码字符串
            - 负数：红色系（深红到浅红）
            - 正数：绿色系（浅绿到深绿）
            - 零：灰色
        """
        karma = self.stats.karma
        
        if karma < -500:
            return "#8B0000"  # 深红色 - 魔头
        elif karma < -200:
            return "#DC143C"  # 猩红色 - 恶人
        elif karma < 0:
            return "#F08080"  # 浅珊瑚色 - 偏恶
        elif karma == 0:
            return "#808080"  # 灰色 - 中立
        elif karma < 200:
            return "#90EE90"  # 浅绿色 - 偏善
        elif karma < 500:
            return "#32CD32"  # 酸橙绿 - 善人
        else:
            return "#228B22"  # 森林绿 - 圣人
    
    def get_status_text(self) -> str:
        """获取状态文本（用于显示）"""
        exp_current, exp_needed, exp_progress = self.get_exp_progress()
        
        status = f"""
╔══════════════════════════════════════════════════════════╗
║  {self.get_realm_icon()} {self.stats.name} 的状态                              ║
╠══════════════════════════════════════════════════════════╣
║  境界: {self.get_realm_name()} {self.stats.realm_layer}层                           ║
║  灵根: {self.get_spirit_root_name()}                                        ║
║  年龄: {self.stats.age}岁 / {self.stats.lifespan}岁寿元                        ║
║  位置: {self.stats.location}                                        ║
╠══════════════════════════════════════════════════════════╣
║  修为: {exp_current}/{exp_needed} ({exp_progress*100:.1f}%)                      ║
║  气血: {self.stats.health}/{self.stats.max_health}                              ║
║  灵力: {self.stats.spiritual_power}/{self.stats.max_spiritual_power}                              ║
║  灵石: {self.stats.spirit_stones}                                      ║
╠══════════════════════════════════════════════════════════╣
║  福缘: {self.stats.fortune}  业力: {self.stats.karma} [{self.get_karma_level()}]              ║
║  时间: 第{self.stats.game_year}年{self.stats.game_month}月{self.stats.game_day}日                          ║
╚══════════════════════════════════════════════════════════╝
"""
        if self.stats.is_injured:
            status += f"\n⚠️ 受伤状态，剩余{self.stats.injury_days}天恢复，修炼速度减半"
        
        return status
    
    def __str__(self) -> str:
        return f"{self.stats.name} ({self.get_realm_name()})"
