"""
炼丹/炼器系统模块
实现材料采集、炼丹、炼器功能
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.alchemy_config import (
    MaterialType, PillType, EquipmentType, ItemQuality, ItemRarity,
    Material, Recipe, Blueprint, MATERIALS_DB, RECIPES_DB, BLUEPRINTS_DB,
    get_material, get_recipe, get_blueprint, calculate_quality,
    get_quality_multiplier, check_materials_available, get_random_gathering_result,
    get_recipes_by_type, get_blueprints_by_type, get_materials_by_type,
    QUALITY_SUCCESS_BONUS
)
from storage.database import Database


@dataclass
class AlchemyResult:
    """炼丹结果数据类"""
    success: bool
    message: str
    pill_name: str = ""
    quality: ItemQuality = ItemQuality.COMMON
    effects: Dict[str, Any] = field(default_factory=dict)
    exp_gained: int = 0


@dataclass
class ForgingResult:
    """炼器结果数据类"""
    success: bool
    message: str
    equipment_name: str = ""
    quality: ItemQuality = ItemQuality.COMMON
    attributes: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    exp_gained: int = 0


@dataclass
class GatheringResult:
    """采集结果数据类"""
    success: bool
    message: str
    materials: List[Tuple[str, int]] = field(default_factory=list)
    exp_gained: int = 0


class AlchemySystem:
    """
    炼丹/炼器系统管理器
    管理材料采集、炼丹、炼器功能
    """

    def __init__(self, db: Database = None):
        """
        初始化炼丹/炼器系统

        Args:
            db: 数据库实例
        """
        self.db = db or Database()
        self._init_database()
        self._init_default_data()

    def _init_database(self):
        """初始化数据库表"""
        try:
            self.db.init_generated_tables()
        except Exception as e:
            print(f"初始化炼丹/炼器数据库表时出错: {e}")

    def _init_default_data(self):
        """初始化默认丹方和图纸数据到数据库"""
        try:
            # 保存默认丹方
            for recipe in RECIPES_DB.values():
                if isinstance(recipe, Recipe):
                    self.db.save_alchemy_recipe({
                        'id': recipe.id,
                        'name': recipe.name,
                        'description': recipe.description,
                        'pill_type': recipe.pill_type.value,
                        'rarity': recipe.rarity.value,
                        'realm_required': recipe.realm_required,
                        'materials': recipe.materials,
                        'effects': recipe.effects,
                        'base_success_rate': recipe.base_success_rate,
                        'quality_multipliers': recipe.quality_multipliers
                    })

            # 保存默认图纸
            for blueprint in BLUEPRINTS_DB.values():
                if isinstance(blueprint, Blueprint):
                    self.db.save_forging_blueprint({
                        'id': blueprint.id,
                        'name': blueprint.name,
                        'description': blueprint.description,
                        'equipment_type': blueprint.equipment_type.value,
                        'rarity': blueprint.rarity.value,
                        'realm_required': blueprint.realm_required,
                        'materials': blueprint.materials,
                        'base_attributes': blueprint.base_attributes,
                        'special_effects': blueprint.special_effects,
                        'base_success_rate': blueprint.base_success_rate
                    })
        except Exception as e:
            print(f"初始化默认数据时出错: {e}")

    # ==================== 材料采集功能 ====================

    def gather_materials(self, player, location_level: int = 1,
                         location_type: str = "general") -> GatheringResult:
        """
        采集材料

        Args:
            player: 玩家对象
            location_level: 地点等级
            location_type: 地点类型

        Returns:
            采集结果
        """
        result = GatheringResult(success=False, message="")

        # 检查玩家状态
        if player.stats.spiritual_power < 10:
            result.message = "灵力不足，无法采集"
            return result

        # 消耗灵力
        player.stats.spiritual_power -= 10

        # 计算采集成功率（受福缘影响）
        base_success_rate = 0.7
        fortune_bonus = player.stats.fortune / 200  # 福缘0-100，加成0-0.5
        success_rate = min(0.95, base_success_rate + fortune_bonus)

        if random.random() > success_rate:
            result.message = "采集失败，一无所获"
            return result

        # 获取采集结果
        materials_found = get_random_gathering_result(location_level, location_type)

        if not materials_found:
            result.message = "此处似乎没有什么可采集的"
            return result

        # 添加到玩家背包
        added_materials = []
        for material_name, quantity in materials_found:
            material = get_material(material_name)
            if material:
                # 创建材料数据
                material_data = {
                    'name': material.name,
                    'description': material.description,
                    'material_type': material.material_type.value,
                    'rarity': material.rarity.value,
                    'level': material.level,
                    'effects': material.effects,
                    'value': material.value,
                    'source': material.source
                }

                # 保存到数据库并添加到玩家材料
                self.db.save_material(material_data, player.stats.name)

                # 添加到玩家背包（如果背包系统支持材料）
                if hasattr(player, 'inventory'):
                    player.inventory.add_item(material_name, quantity, material_data)

                added_materials.append(f"{material_name} x{quantity}")

        result.success = True
        result.materials = materials_found
        result.exp_gained = 5 * len(materials_found)
        result.message = f"采集成功！获得: {', '.join(added_materials)}"

        # 增加玩家修为
        player.stats.exp += result.exp_gained

        return result

    def get_player_materials(self, player_name: str) -> Dict[str, Dict]:
        """
        获取玩家拥有的材料

        Args:
            player_name: 玩家名称

        Returns:
            材料字典 {材料名: 材料数据}
        """
        materials = self.db.load_materials(player_name)
        return {m['name']: m for m in materials}

    # ==================== 炼丹功能 ====================

    def get_available_recipes(self, player_realm: int = 0) -> List[Recipe]:
        """
        获取玩家可使用的丹方

        Args:
            player_realm: 玩家境界等级

        Returns:
            丹方列表
        """
        return [r for r in RECIPES_DB.values()
                if isinstance(r, Recipe) and r.realm_required <= player_realm]

    def calculate_alchemy_success_rate(self, recipe: Recipe, player,
                                       material_quality_bonus: float = 0.0) -> float:
        """
        计算炼丹成功率

        Args:
            recipe: 丹方
            player: 玩家对象
            material_quality_bonus: 材料品质加成

        Returns:
            最终成功率
        """
        base_rate = recipe.base_success_rate

        # 境界加成（每高一个境界+5%）
        realm_bonus = max(0, (player.stats.realm_level - recipe.realm_required) * 0.05)

        # 福缘加成
        fortune_bonus = player.stats.fortune / 500  # 0-0.2

        # 计算最终成功率
        final_rate = base_rate + realm_bonus + fortune_bonus + material_quality_bonus

        # 限制在合理范围内
        return max(0.1, min(0.95, final_rate))

    def perform_alchemy(self, player, recipe_id: str) -> AlchemyResult:
        """
        执行炼丹

        Args:
            player: 玩家对象
            recipe_id: 丹方ID

        Returns:
            炼丹结果
        """
        result = AlchemyResult(success=False, message="")

        # 获取丹方
        recipe = get_recipe(recipe_id)
        if not recipe:
            result.message = "丹方不存在"
            return result

        # 检查境界要求
        if player.stats.realm_level < recipe.realm_required:
            result.message = f"境界不足，需要{recipe.realm_required}级境界"
            return result

        # 获取玩家材料
        player_materials = self.get_player_materials(player.stats.name)

        # 检查材料是否充足
        inventory = {name: 1 for name in player_materials.keys()}  # 简化处理
        if hasattr(player, 'inventory'):
            inventory = {name: data.get('count', 1)
                        for name, data in player.inventory.items.items()}

        if not check_materials_available(inventory, recipe.materials):
            result.message = "材料不足"
            return result

        # 计算材料品质加成
        material_quality_bonus = 0.0
        for material_name in recipe.materials.keys():
            material = get_material(material_name)
            if material:
                material_quality_bonus += QUALITY_SUCCESS_BONUS.get(material.rarity, 0.0)
        material_quality_bonus /= len(recipe.materials)  # 平均加成

        # 计算成功率
        success_rate = self.calculate_alchemy_success_rate(
            recipe, player, material_quality_bonus
        )

        # 消耗材料
        for material_name, count in recipe.materials.items():
            if hasattr(player, 'inventory'):
                player.inventory.remove_item(material_name, count)

        # 消耗灵力
        spirit_cost = 20 + recipe.realm_required * 5
        if player.stats.spiritual_power < spirit_cost:
            result.message = "灵力不足"
            return result
        player.stats.spiritual_power -= spirit_cost

        # 判定是否成功
        roll = random.random()
        if roll > success_rate:
            # 炼丹失败
            result.message = f"炼丹失败！炉火失控，材料尽毁"
            result.exp_gained = 2

            # 记录失败
            self.db.save_alchemy_record(player.stats.name, {
                'recipe_id': recipe.id,
                'recipe_name': recipe.name,
                'success': False,
                'quality': '',
                'materials_used': recipe.materials,
                'result_item': {}
            })
        else:
            # 炼丹成功
            quality = calculate_quality(success_rate)
            quality_multiplier = get_quality_multiplier(quality)

            # 计算丹药效果
            effects = {}
            for effect_name, effect_value in recipe.effects.items():
                if isinstance(effect_value, (int, float)):
                    effects[effect_name] = effect_value * quality_multiplier
                else:
                    effects[effect_name] = effect_value

            # 创建丹药数据
            pill_data = {
                'name': recipe.name,
                'description': f"{recipe.description} (品质: {quality.value})",
                'type': '丹药',
                'rarity': recipe.rarity.value,
                'quality': quality.value,
                'effects': effects,
                'value': int(100 * quality_multiplier),
                'usable': True
            }

            # 添加到玩家背包
            if hasattr(player, 'inventory'):
                player.inventory.add_generated_item(recipe.name, pill_data, 1)

            result.success = True
            result.pill_name = recipe.name
            result.quality = quality
            result.effects = effects
            result.exp_gained = int(10 * quality_multiplier)
            result.message = f"炼丹成功！获得【{quality.value}】{recipe.name}"

            # 记录成功
            self.db.save_alchemy_record(player.stats.name, {
                'recipe_id': recipe.id,
                'recipe_name': recipe.name,
                'success': True,
                'quality': quality.value,
                'materials_used': recipe.materials,
                'result_item': pill_data
            })

        # 增加玩家修为
        player.stats.exp += result.exp_gained

        return result

    def get_alchemy_history(self, player_name: str, limit: int = 20) -> List[Dict]:
        """
        获取炼丹历史

        Args:
            player_name: 玩家名称
            limit: 返回记录数

        Returns:
            炼丹记录列表
        """
        return self.db.get_alchemy_records(player_name, limit)

    # ==================== 炼器功能 ====================

    def get_available_blueprints(self, player_realm: int = 0) -> List[Blueprint]:
        """
        获取玩家可使用的炼器图纸

        Args:
            player_realm: 玩家境界等级

        Returns:
            图纸列表
        """
        return [b for b in BLUEPRINTS_DB.values()
                if isinstance(b, Blueprint) and b.realm_required <= player_realm]

    def calculate_forging_success_rate(self, blueprint: Blueprint, player,
                                       material_quality_bonus: float = 0.0) -> float:
        """
        计算炼器成功率

        Args:
            blueprint: 炼器图纸
            player: 玩家对象
            material_quality_bonus: 材料品质加成

        Returns:
            最终成功率
        """
        base_rate = blueprint.base_success_rate

        # 境界加成
        realm_bonus = max(0, (player.stats.realm_level - blueprint.realm_required) * 0.05)

        # 福缘加成
        fortune_bonus = player.stats.fortune / 500

        # 计算最终成功率
        final_rate = base_rate + realm_bonus + fortune_bonus + material_quality_bonus

        return max(0.1, min(0.95, final_rate))

    def perform_forging(self, player, blueprint_id: str) -> ForgingResult:
        """
        执行炼器

        Args:
            player: 玩家对象
            blueprint_id: 图纸ID

        Returns:
            炼器结果
        """
        result = ForgingResult(success=False, message="")

        # 获取图纸
        blueprint = get_blueprint(blueprint_id)
        if not blueprint:
            result.message = "图纸不存在"
            return result

        # 检查境界要求
        if player.stats.realm_level < blueprint.realm_required:
            result.message = f"境界不足，需要{blueprint.realm_required}级境界"
            return result

        # 获取玩家材料
        player_materials = self.get_player_materials(player.stats.name)

        # 检查材料是否充足
        inventory = {name: 1 for name in player_materials.keys()}
        if hasattr(player, 'inventory'):
            inventory = {name: data.get('count', 1)
                        for name, data in player.inventory.items.items()}

        if not check_materials_available(inventory, blueprint.materials):
            result.message = "材料不足"
            return result

        # 计算材料品质加成
        material_quality_bonus = 0.0
        for material_name in blueprint.materials.keys():
            material = get_material(material_name)
            if material:
                material_quality_bonus += QUALITY_SUCCESS_BONUS.get(material.rarity, 0.0)
        material_quality_bonus /= len(blueprint.materials)

        # 计算成功率
        success_rate = self.calculate_forging_success_rate(
            blueprint, player, material_quality_bonus
        )

        # 消耗材料
        for material_name, count in blueprint.materials.items():
            if hasattr(player, 'inventory'):
                player.inventory.remove_item(material_name, count)

        # 消耗灵力
        spirit_cost = 30 + blueprint.realm_required * 8
        if player.stats.spiritual_power < spirit_cost:
            result.message = "灵力不足"
            return result
        player.stats.spiritual_power -= spirit_cost

        # 判定是否成功
        roll = random.random()
        if roll > success_rate:
            # 炼器失败
            result.message = f"炼器失败！炉火失控，材料尽毁"
            result.exp_gained = 3

            # 记录失败
            self.db.save_forging_record(player.stats.name, {
                'blueprint_id': blueprint.id,
                'blueprint_name': blueprint.name,
                'success': False,
                'quality': '',
                'materials_used': blueprint.materials,
                'result_item': {}
            })
        else:
            # 炼器成功
            quality = calculate_quality(success_rate)
            quality_multiplier = get_quality_multiplier(quality)

            # 计算装备属性
            attributes = {}
            for attr_name, attr_value in blueprint.base_attributes.items():
                # 添加随机波动
                variance = random.uniform(0.9, 1.1)
                final_value = int(attr_value * quality_multiplier * variance)
                attributes[attr_name] = final_value

            # 根据品质决定是否获得特殊效果
            special_effects = []
            if quality in [ItemQuality.RARE, ItemQuality.EPIC, ItemQuality.LEGENDARY, ItemQuality.MYTHIC]:
                # 高品质有几率获得特殊效果
                num_effects = min(len(blueprint.special_effects),
                                  {ItemQuality.RARE: 1, ItemQuality.EPIC: 2,
                                   ItemQuality.LEGENDARY: 3, ItemQuality.MYTHIC: 4}.get(quality, 0))
                if num_effects > 0:
                    special_effects = random.sample(blueprint.special_effects,
                                                    min(num_effects, len(blueprint.special_effects)))

            # 创建装备数据
            equipment_data = {
                'name': blueprint.name,
                'description': f"{blueprint.description} (品质: {quality.value})",
                'type': '法宝' if blueprint.equipment_type == EquipmentType.TREASURE else '装备',
                'equipment_type': blueprint.equipment_type.value,
                'rarity': blueprint.rarity.value,
                'quality': quality.value,
                'attributes': attributes,
                'special_effects': special_effects,
                'value': int(200 * quality_multiplier),
                'usable': True
            }

            # 添加到玩家背包
            if hasattr(player, 'inventory'):
                player.inventory.add_generated_item(blueprint.name, equipment_data, 1)

            result.success = True
            result.equipment_name = blueprint.name
            result.quality = quality
            result.attributes = attributes
            result.special_effects = special_effects
            result.exp_gained = int(15 * quality_multiplier)
            result.message = f"炼器成功！获得【{quality.value}】{blueprint.name}"

            # 记录成功
            self.db.save_forging_record(player.stats.name, {
                'blueprint_id': blueprint.id,
                'blueprint_name': blueprint.name,
                'success': True,
                'quality': quality.value,
                'materials_used': blueprint.materials,
                'result_item': equipment_data
            })

        # 增加玩家修为
        player.stats.exp += result.exp_gained

        return result

    def get_forging_history(self, player_name: str, limit: int = 20) -> List[Dict]:
        """
        获取炼器历史

        Args:
            player_name: 玩家名称
            limit: 返回记录数

        Returns:
            炼器记录列表
        """
        return self.db.get_forging_records(player_name, limit)

    # ==================== 便捷方法 ====================

    def get_materials_by_category(self, category: str) -> List[Material]:
        """
        按类别获取材料

        Args:
            category: 类别 (herb:草药, ore:矿石, beast:妖兽材料, spiritual:灵物)

        Returns:
            材料列表
        """
        category_map = {
            'herb': MaterialType.HERB,
            'ore': MaterialType.ORE,
            'beast': MaterialType.BEAST_MATERIAL,
            'spiritual': MaterialType.SPIRITUAL_ITEM
        }
        material_type = category_map.get(category)
        if material_type:
            return get_materials_by_type(material_type)
        return []

    def get_recipes_by_category(self, category: str) -> List[Recipe]:
        """
        按类别获取丹方

        Args:
            category: 类别 (recovery:恢复, breakthrough:突破, buff:增益, permanent:永久)

        Returns:
            丹方列表
        """
        category_map = {
            'recovery': PillType.RECOVERY,
            'breakthrough': PillType.BREAKTHROUGH,
            'buff': PillType.BUFF,
            'permanent': PillType.PERMANENT
        }
        pill_type = category_map.get(category)
        if pill_type:
            return get_recipes_by_type(pill_type)
        return []

    def get_blueprints_by_category(self, category: str) -> List[Blueprint]:
        """
        按类别获取炼器图纸

        Args:
            category: 类别 (weapon:武器, armor:护甲, accessory:饰品, treasure:法宝)

        Returns:
            图纸列表
        """
        category_map = {
            'weapon': EquipmentType.WEAPON,
            'armor': EquipmentType.ARMOR,
            'accessory': EquipmentType.ACCESSORY,
            'treasure': EquipmentType.TREASURE
        }
        equipment_type = category_map.get(category)
        if equipment_type:
            return get_blueprints_by_type(equipment_type)
        return []


# 全局炼丹系统实例
_default_alchemy_system: Optional[AlchemySystem] = None


def get_alchemy_system(db: Database = None) -> AlchemySystem:
    """
    获取默认的炼丹系统实例

    Args:
        db: 数据库实例

    Returns:
        AlchemySystem实例
    """
    global _default_alchemy_system
    if _default_alchemy_system is None:
        _default_alchemy_system = AlchemySystem(db)
    return _default_alchemy_system
