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


class Player:
    """玩家类"""
    
    def __init__(self, name: str = "无名修士", load_from_db: bool = True):
        """
        初始化玩家
        
        Args:
            name: 玩家名字
            load_from_db: 是否从数据库加载
        """
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
        
        return base_speed
    
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
        
        # 法宝加成
        for treasure_name in self.equipped_treasures.values():
            from config import get_item
            item = get_item(treasure_name)
            if item and item.item_type.value == "法宝":
                # 法宝效果加成
                pass
        
        return bonus
    
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
                
                self.inventory.use_item(item_name)
                return True, f"使用{item.name}，{', '.join(item.effects)}"
            
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
                
                self.inventory.use_item(item_name)
                return True, f"使用{item_name}，恢复了{restore_amount}点法力"
            
            elif item_type == "法宝" or item_type == "MAGIC_TREASURE":
                # 装备生成的法宝
                return self.equip_generated_treasure(item_name, item_data)
            
            else:
                # 其他类型的生成道具
                self.inventory.use_item(item_name)
                return True, f"使用{item_name}"
        
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
            (当前经验, 需要经验, 进度百分比)
        """
        realm_info = get_realm_info(self.stats.realm_level)
        if not realm_info:
            return (0, 1, 0.0)
        
        exp_in_realm = self.stats.exp - realm_info.exp_required
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
        """转换为字典"""
        return {
            "stats": asdict(self.stats),
            "techniques": {
                "learned": self.techniques.learned_techniques,
                "progress": self.techniques.learning_progress
            },
            "inventory": self.inventory.items,
            "equipped": self.equipped_treasures
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        # 加载基础属性
        stats_data = data.get("stats", data)  # 兼容旧格式
        for key, value in stats_data.items():
            if hasattr(self.stats, key):
                setattr(self.stats, key, value)
        
        # 加载功法数据
        if "techniques" in data:
            tech_data = data["techniques"]
            self.techniques.learned_techniques = tech_data.get("learned", {})
            self.techniques.learning_progress = tech_data.get("progress", {})
        
        # 加载背包数据
        if "inventory" in data:
            self.inventory.items = data["inventory"]
        
        # 加载装备数据
        if "equipped" in data:
            self.equipped_treasures = data["equipped"]
        
        self._update_max_stats()
    
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
║  福缘: {self.stats.fortune}  业力: {self.stats.karma}                              ║
║  时间: 第{self.stats.game_year}年{self.stats.game_month}月{self.stats.game_day}日                          ║
╚══════════════════════════════════════════════════════════╝
"""
        if self.stats.is_injured:
            status += f"\n⚠️ 受伤状态，剩余{self.stats.injury_days}天恢复，修炼速度减半"
        
        return status
    
    def __str__(self) -> str:
        return f"{self.stats.name} ({self.get_realm_name()})"
