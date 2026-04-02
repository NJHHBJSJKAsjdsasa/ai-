"""
动态材料生成系统
战斗中动态生成材料并保存到数据库
"""

import random
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MaterialRarity(Enum):
    """材料稀有度"""
    COMMON = "普通"
    UNCOMMON = "优秀"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"


@dataclass
class GeneratedMaterial:
    """生成的材料数据类"""
    id: str                            # 唯一ID
    name: str                          # 材料名称
    description: str                   # 描述
    material_type: str                 # 材料类型
    rarity: MaterialRarity             # 稀有度
    level: int                         # 等级
    effects: Dict[str, Any]            # 效果属性
    value: int                         # 价值
    source: str                        # 来源（击败的敌人）
    created_at: datetime               # 创建时间
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "material_type": self.material_type,
            "rarity": self.rarity.value,
            "level": self.level,
            "effects": self.effects,
            "value": self.value,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GeneratedMaterial':
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            material_type=data["material_type"],
            rarity=MaterialRarity(data["rarity"]),
            level=data["level"],
            effects=data["effects"],
            value=data["value"],
            source=data["source"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )


# 材料类型定义
MATERIAL_TYPES = {
    "妖兽材料": {
        "prefixes": ["粗糙的", "普通的", "优质的", "完美的", "传奇的"],
        "bases": ["兽皮", "兽骨", "兽牙", "兽爪", "兽筋", "兽血", "兽核"],
        "effects": ["坚韧", "锋利", "毒性", "火焰", "冰霜", "雷电"],
    },
    "灵草": {
        "prefixes": ["枯萎的", "幼嫩的", "成熟的", "千年的", "万年的"],
        "bases": ["灵芝", "人参", "何首乌", "雪莲", "朱果", "龙血草"],
        "effects": ["回血", "回蓝", "解毒", "增强", "突破", "延寿"],
    },
    "矿石": {
        "prefixes": ["劣质的", "普通的", "精纯的", "极品的", "神品的"],
        "bases": ["铁矿石", "铜矿石", "银矿石", "金矿石", "灵石矿", "玄铁矿"],
        "effects": ["坚硬", "轻盈", "导灵", "耐热", "耐寒", "抗震"],
    },
    "灵材": {
        "prefixes": ["残缺的", "完整的", "充盈的", "圆满的", "大道的"],
        "bases": ["灵木", "灵竹", "灵藤", "灵花", "灵叶", "灵根"],
        "effects": ["生机", "治愈", "净化", "增幅", "守护", "复苏"],
    },
}


class MaterialGenerator:
    """材料生成器"""
    
    # 稀有度概率分布
    RARITY_CHANCES = {
        0: {MaterialRarity.COMMON: 0.7, MaterialRarity.UNCOMMON: 0.25, MaterialRarity.RARE: 0.05},
        1: {MaterialRarity.COMMON: 0.5, MaterialRarity.UNCOMMON: 0.35, MaterialRarity.RARE: 0.14, MaterialRarity.EPIC: 0.01},
        2: {MaterialRarity.COMMON: 0.3, MaterialRarity.UNCOMMON: 0.4, MaterialRarity.RARE: 0.25, MaterialRarity.EPIC: 0.05},
        3: {MaterialRarity.UNCOMMON: 0.4, MaterialRarity.RARE: 0.4, MaterialRarity.EPIC: 0.18, MaterialRarity.LEGENDARY: 0.02},
        4: {MaterialRarity.RARE: 0.5, MaterialRarity.EPIC: 0.35, MaterialRarity.LEGENDARY: 0.15},
    }
    
    # 基础价值表
    BASE_VALUES = {
        MaterialRarity.COMMON: 10,
        MaterialRarity.UNCOMMON: 30,
        MaterialRarity.RARE: 100,
        MaterialRarity.EPIC: 500,
        MaterialRarity.LEGENDARY: 2000,
    }
    
    @staticmethod
    def generate_material(enemy_name: str, enemy_level: int, enemy_type: str = "npc") -> GeneratedMaterial:
        """
        生成材料
        
        Args:
            enemy_name: 敌人名称
            enemy_level: 敌人等级
            enemy_type: 敌人类型 (npc/beast)
            
        Returns:
            生成的材料
        """
        # 确定材料类型
        if enemy_type == "beast":
            material_type = "妖兽材料"
        else:
            material_type = random.choice(["灵草", "矿石", "灵材"])
        
        # 确定稀有度
        rarity = MaterialGenerator._determine_rarity(enemy_level)
        
        # 生成名称
        name = MaterialGenerator._generate_material_name(material_type, rarity)
        
        # 计算属性
        effects = MaterialGenerator._calculate_material_stats(material_type, rarity, enemy_level)
        
        # 计算价值
        value = MaterialGenerator._calculate_value(rarity, enemy_level)
        
        # 生成描述
        description = MaterialGenerator._generate_description(name, material_type, rarity, effects)
        
        return GeneratedMaterial(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            material_type=material_type,
            rarity=rarity,
            level=enemy_level,
            effects=effects,
            value=value,
            source=enemy_name,
            created_at=datetime.now(),
        )
    
    @staticmethod
    def _determine_rarity(enemy_level: int) -> MaterialRarity:
        """根据敌人等级确定稀有度"""
        # 根据等级确定概率分布
        if enemy_level <= 9:
            chances = MaterialGenerator.RARITY_CHANCES[0]
        elif enemy_level <= 18:
            chances = MaterialGenerator.RARITY_CHANCES[1]
        elif enemy_level <= 27:
            chances = MaterialGenerator.RARITY_CHANCES[2]
        elif enemy_level <= 54:
            chances = MaterialGenerator.RARITY_CHANCES[3]
        else:
            chances = MaterialGenerator.RARITY_CHANCES[4]
        
        # 根据概率选择稀有度
        rand = random.random()
        cumulative = 0
        for rarity, chance in chances.items():
            cumulative += chance
            if rand <= cumulative:
                return rarity
        
        return MaterialRarity.COMMON
    
    @staticmethod
    def _generate_material_name(material_type: str, rarity: MaterialRarity) -> str:
        """生成材料名称"""
        type_info = MATERIAL_TYPES.get(material_type, MATERIAL_TYPES["灵材"])
        
        # 根据稀有度选择前缀
        prefix_index = min(list(MaterialRarity).index(rarity), len(type_info["prefixes"]) - 1)
        prefix = type_info["prefixes"][prefix_index]
        
        # 随机选择基础名称
        base = random.choice(type_info["bases"])
        
        return f"{prefix}{base}"
    
    @staticmethod
    def _calculate_material_stats(material_type: str, rarity: MaterialRarity, level: int) -> Dict[str, Any]:
        """计算材料属性"""
        type_info = MATERIAL_TYPES.get(material_type, MATERIAL_TYPES["灵材"])
        
        # 基础效果
        base_effect = random.choice(type_info["effects"])
        
        # 稀有度倍数
        rarity_multiplier = {
            MaterialRarity.COMMON: 1.0,
            MaterialRarity.UNCOMMON: 1.5,
            MaterialRarity.RARE: 2.5,
            MaterialRarity.EPIC: 5.0,
            MaterialRarity.LEGENDARY: 10.0,
        }[rarity]
        
        # 等级加成
        level_bonus = level * 0.1
        
        effects = {
            "primary_effect": base_effect,
            "power": int(10 * rarity_multiplier * (1 + level_bonus)),
            "purity": int(50 * rarity_multiplier),
            "durability": int(100 * rarity_multiplier),
        }
        
        # 稀有度以上添加额外效果
        if rarity in [MaterialRarity.RARE, MaterialRarity.EPIC, MaterialRarity.LEGENDARY]:
            effects["secondary_effect"] = random.choice([e for e in type_info["effects"] if e != base_effect])
        
        # 传说级添加特殊效果
        if rarity == MaterialRarity.LEGENDARY:
            effects["special_trait"] = random.choice(["灵性", "成长性", "不灭", "大道亲和"])
        
        return effects
    
    @staticmethod
    def _calculate_value(rarity: MaterialRarity, level: int) -> int:
        """计算材料价值"""
        base_value = MaterialGenerator.BASE_VALUES[rarity]
        level_bonus = int(level * 0.5)
        variance = random.randint(-int(base_value * 0.1), int(base_value * 0.1))
        return max(1, base_value + level_bonus + variance)
    
    @staticmethod
    def _generate_description(name: str, material_type: str, rarity: MaterialRarity, effects: Dict) -> str:
        """生成材料描述"""
        descriptions = []
        
        # 基础描述
        rarity_desc = {
            MaterialRarity.COMMON: "随处可见的普通材料",
            MaterialRarity.UNCOMMON: "品质较好的材料",
            MaterialRarity.RARE: "难得一见的珍稀材料",
            MaterialRarity.EPIC: "蕴含强大力量的史诗材料",
            MaterialRarity.LEGENDARY: "传说中的神级材料",
        }[rarity]
        
        descriptions.append(f"{rarity_desc}。")
        
        # 效果描述
        if "primary_effect" in effects:
            descriptions.append(f"主要效果：{effects['primary_effect']}。")
        if "secondary_effect" in effects:
            descriptions.append(f"附带效果：{effects['secondary_effect']}。")
        if "special_trait" in effects:
            descriptions.append(f"特殊属性：{effects['special_trait']}。")
        
        return " ".join(descriptions)
    
    @staticmethod
    def get_material_quality_text(rarity: MaterialRarity) -> str:
        """获取材料品质文本"""
        quality_colors = {
            MaterialRarity.COMMON: "⚪",
            MaterialRarity.UNCOMMON: "🟢",
            MaterialRarity.RARE: "🔵",
            MaterialRarity.EPIC: "🟣",
            MaterialRarity.LEGENDARY: "🟡",
        }
        return f"{quality_colors.get(rarity, '⚪')} {rarity.value}"
    
    @staticmethod
    def generate_multiple_materials(enemy_name: str, enemy_level: int, enemy_type: str = "npc", count: int = 1) -> List[GeneratedMaterial]:
        """
        生成多个材料
        
        Args:
            enemy_name: 敌人名称
            enemy_level: 敌人等级
            enemy_type: 敌人类型
            count: 生成数量
            
        Returns:
            材料列表
        """
        materials = []
        for _ in range(count):
            material = MaterialGenerator.generate_material(enemy_name, enemy_level, enemy_type)
            materials.append(material)
        return materials


# 全局材料生成器实例
material_generator = MaterialGenerator()
