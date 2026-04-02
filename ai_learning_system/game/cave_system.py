"""
洞府系统模块
实现洞府购买、升级、灵田种植、聚灵阵、护山大阵等功能
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.cave_config import (
    CaveLevel, CropType, CropStage,
    CaveLevelConfig, CropConfig, SpiritArrayConfig, DefenseArrayConfig, CaveLocation,
    CAVE_LEVELS, CROPS_DB, SPIRIT_ARRAY_LEVELS, DEFENSE_ARRAY_LEVELS, CAVE_LOCATIONS,
    get_cave_level_config, get_crop_config, get_spirit_array_config, get_defense_array_config,
    get_cave_location, get_available_crops, get_crops_by_type,
    calculate_cave_price, get_next_cave_level, calculate_total_cultivation_bonus
)
from storage.database import Database


@dataclass
class CaveField:
    """灵田数据类"""
    id: int = 0
    cave_id: str = ""
    field_index: int = 0
    crop_id: Optional[str] = None
    crop_name: str = ""
    planted_at: Optional[datetime] = None
    growth_days: int = 0
    total_growth_days: int = 0
    stage: str = "empty"  # empty, seed, sprout, growth, mature, withered
    yield_amount: int = 0
    is_fertilized: bool = False
    fertilizer_bonus: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'cave_id': self.cave_id,
            'field_index': self.field_index,
            'crop_id': self.crop_id,
            'crop_name': self.crop_name,
            'planted_at': self.planted_at.isoformat() if self.planted_at else '',
            'growth_days': self.growth_days,
            'total_growth_days': self.total_growth_days,
            'stage': self.stage,
            'yield_amount': self.yield_amount,
            'is_fertilized': self.is_fertilized,
            'fertilizer_bonus': self.fertilizer_bonus
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaveField':
        """从字典创建"""
        field = cls()
        field.id = data.get('id', 0)
        field.cave_id = data.get('cave_id', '')
        field.field_index = data.get('field_index', 0)
        field.crop_id = data.get('crop_id')
        field.crop_name = data.get('crop_name', '')
        planted_at_str = data.get('planted_at', '')
        if planted_at_str:
            try:
                field.planted_at = datetime.fromisoformat(planted_at_str)
            except:
                field.planted_at = None
        field.growth_days = data.get('growth_days', 0)
        field.total_growth_days = data.get('total_growth_days', 0)
        field.stage = data.get('stage', 'empty')
        field.yield_amount = data.get('yield_amount', 0)
        field.is_fertilized = data.get('is_fertilized', False)
        field.fertilizer_bonus = data.get('fertilizer_bonus', 0.0)
        return field


@dataclass
class PlayerCave:
    """玩家洞府数据类"""
    id: str = ""
    player_name: str = ""
    cave_name: str = "无名洞府"
    location_id: str = "newbie_village"
    cave_level: CaveLevel = CaveLevel.SIMPLE
    spirit_array_level: int = 0
    defense_array_level: int = 0
    max_fields: int = 2
    created_at: Optional[datetime] = None
    last_visit: Optional[datetime] = None
    cultivation_bonus: float = 0.0
    defense_power: int = 0
    spirit_recovery: int = 0
    fields: List[CaveField] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'player_name': self.player_name,
            'cave_name': self.cave_name,
            'location_id': self.location_id,
            'cave_level': self.cave_level.value,
            'spirit_array_level': self.spirit_array_level,
            'defense_array_level': self.defense_array_level,
            'max_fields': self.max_fields,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'last_visit': self.last_visit.isoformat() if self.last_visit else '',
            'cultivation_bonus': self.cultivation_bonus,
            'defense_power': self.defense_power,
            'spirit_recovery': self.spirit_recovery
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerCave':
        """从字典创建"""
        cave = cls()
        cave.id = data.get('id', '')
        cave.player_name = data.get('player_name', '')
        cave.cave_name = data.get('cave_name', '无名洞府')
        cave.location_id = data.get('location_id', 'newbie_village')
        cave.cave_level = CaveLevel(data.get('cave_level', 0))
        cave.spirit_array_level = data.get('spirit_array_level', 0)
        cave.defense_array_level = data.get('defense_array_level', 0)
        cave.max_fields = data.get('max_fields', 2)
        created_at_str = data.get('created_at', '')
        if created_at_str:
            try:
                cave.created_at = datetime.fromisoformat(created_at_str)
            except:
                cave.created_at = datetime.now()
        last_visit_str = data.get('last_visit', '')
        if last_visit_str:
            try:
                cave.last_visit = datetime.fromisoformat(last_visit_str)
            except:
                cave.last_visit = datetime.now()
        cave.cultivation_bonus = data.get('cultivation_bonus', 0.0)
        cave.defense_power = data.get('defense_power', 0)
        cave.spirit_recovery = data.get('spirit_recovery', 0)
        return cave


@dataclass
class PlantResult:
    """种植结果"""
    success: bool
    message: str
    field_index: int = -1


@dataclass
class HarvestResult:
    """收获结果"""
    success: bool
    message: str
    crop_name: str = ""
    quantity: int = 0
    quality: str = "普通"


@dataclass
class UpgradeResult:
    """升级结果"""
    success: bool
    message: str
    new_level: int = 0
    cost: int = 0


@dataclass
class DefenseResult:
    """防御结果"""
    success: bool
    message: str
    enemy_name: str = ""
    damage_dealt: int = 0
    damage_taken: int = 0
    enemy_repelled: bool = False


class CaveSystem:
    """
    洞府系统管理器
    管理洞府购买、升级、灵田种植、聚灵阵、护山大阵等功能
    """

    def __init__(self, db: Database = None):
        """
        初始化洞府系统

        Args:
            db: 数据库实例
        """
        self.db = db or Database()
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        try:
            self.db.init_cave_tables()
        except Exception as e:
            print(f"初始化洞府数据库表时出错: {e}")

    # ==================== 洞府基础功能 ====================

    def create_cave(self, player, location_id: str, cave_name: str = None) -> Tuple[bool, str]:
        """
        创建洞府

        Args:
            player: 玩家对象
            location_id: 地点ID
            cave_name: 洞府名称

        Returns:
            (是否成功, 消息)
        """
        # 检查玩家是否已有洞府
        existing_cave = self.get_player_cave(player.stats.name)
        if existing_cave:
            return False, "你已经拥有洞府了"

        # 获取地点配置
        location = get_cave_location(location_id)
        if not location:
            return False, "地点不存在"

        # 检查境界要求
        if player.stats.realm_level < location.min_realm:
            return False, f"境界不足，需要{location.min_realm}级境界"

        # 计算价格
        cave_config = get_cave_level_config(CaveLevel.SIMPLE)
        price = calculate_cave_price(
            cave_config.base_price,
            location.price_multiplier,
            CaveLevel.SIMPLE
        )

        # 检查灵石
        if player.stats.spirit_stones < price:
            return False, f"灵石不足，需要{price}灵石"

        # 扣除灵石
        player.stats.spirit_stones -= price

        # 创建洞府
        now = datetime.now()
        cave = PlayerCave(
            player_name=player.stats.name,
            cave_name=cave_name or f"{player.stats.name}的洞府",
            location_id=location_id,
            cave_level=CaveLevel.SIMPLE,
            max_fields=cave_config.max_fields,
            created_at=now,
            last_visit=now
        )

        # 计算属性
        self._update_cave_stats(cave)

        # 保存到数据库
        cave_data = cave.to_dict()
        cave_data['id'] = self.db.save_player_cave(cave_data)
        cave.id = cave_data['id']

        # 初始化灵田
        self._init_fields(cave)

        return True, f"成功创建洞府【{cave.cave_name}】，消耗{price}灵石"

    def get_player_cave(self, player_name: str) -> Optional[PlayerCave]:
        """
        获取玩家洞府

        Args:
            player_name: 玩家名称

        Returns:
            洞府对象，如果不存在则返回None
        """
        cave_data = self.db.get_player_cave(player_name)
        if not cave_data:
            return None

        cave = PlayerCave.from_dict(cave_data)

        # 加载灵田
        fields_data = self.db.get_cave_fields(cave.id)
        cave.fields = [CaveField.from_dict(f) for f in fields_data]

        return cave

    def _init_fields(self, cave: PlayerCave):
        """初始化灵田"""
        for i in range(cave.max_fields):
            field = CaveField(
                cave_id=cave.id,
                field_index=i,
                stage="empty"
            )
            field_id = self.db.save_cave_field(field.to_dict())
            field.id = field_id
            cave.fields.append(field)

    def _update_cave_stats(self, cave: PlayerCave):
        """更新洞府属性"""
        cave_config = get_cave_level_config(cave.cave_level)
        spirit_config = get_spirit_array_config(cave.spirit_array_level)
        defense_config = get_defense_array_config(cave.defense_array_level)
        location = get_cave_location(cave.location_id)

        # 计算修炼加成
        cave.cultivation_bonus = calculate_total_cultivation_bonus(
            cave.cave_level,
            cave.spirit_array_level,
            cave.location_id
        )

        # 计算防御力
        cave.defense_power = cave_config.defense_power
        if defense_config:
            cave.defense_power += defense_config.defense_power

        # 计算灵力恢复
        cave.spirit_recovery = cave_config.spirit_recovery
        if spirit_config:
            cave.spirit_recovery += spirit_config.spirit_gathering // 10

    def update_cave(self, cave: PlayerCave) -> bool:
        """
        更新洞府信息

        Args:
            cave: 洞府对象

        Returns:
            是否成功
        """
        try:
            self._update_cave_stats(cave)
            self.db.save_player_cave(cave.to_dict())
            return True
        except Exception as e:
            print(f"更新洞府失败: {e}")
            return False

    # ==================== 洞府升级功能 ====================

    def upgrade_cave(self, player) -> UpgradeResult:
        """
        升级洞府

        Args:
            player: 玩家对象

        Returns:
            升级结果
        """
        result = UpgradeResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 获取下一个等级
        next_level = get_next_cave_level(cave.cave_level)
        if not next_level:
            result.message = "洞府已经达到最高等级"
            return result

        # 获取配置
        current_config = get_cave_level_config(cave.cave_level)
        next_config = get_cave_level_config(next_level)
        location = get_cave_location(cave.location_id)

        # 检查地点等级限制
        if next_level.value > location.max_cave_level.value:
            result.message = f"该地点无法建造{next_config.name}"
            return result

        # 计算升级价格
        upgrade_price = int(next_config.upgrade_price * location.price_multiplier)

        # 检查灵石
        if player.stats.spirit_stones < upgrade_price:
            result.message = f"灵石不足，需要{upgrade_price}灵石"
            return result

        # 扣除灵石
        player.stats.spirit_stones -= upgrade_price

        # 升级洞府
        old_level = cave.cave_level
        cave.cave_level = next_level
        cave.max_fields = next_config.max_fields

        # 更新属性
        self._update_cave_stats(cave)

        # 保存到数据库
        self.db.save_player_cave(cave.to_dict())

        # 记录升级
        self.db.record_cave_upgrade(
            cave.id, 'cave',
            old_level.value, next_level.value,
            {'spirit_stones': upgrade_price}
        )

        # 添加新灵田
        current_fields_count = len(cave.fields)
        for i in range(current_fields_count, cave.max_fields):
            field = CaveField(
                cave_id=cave.id,
                field_index=i,
                stage="empty"
            )
            field_id = self.db.save_cave_field(field.to_dict())
            field.id = field_id
            cave.fields.append(field)

        result.success = True
        result.message = f"洞府升级成功！当前等级：{next_config.name}"
        result.new_level = next_level.value
        result.cost = upgrade_price

        return result

    def upgrade_spirit_array(self, player) -> UpgradeResult:
        """
        升级聚灵阵

        Args:
            player: 玩家对象

        Returns:
            升级结果
        """
        result = UpgradeResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 获取当前配置
        cave_config = get_cave_level_config(cave.cave_level)

        # 检查是否达到等级上限
        if cave.spirit_array_level >= cave_config.max_spirit_array_level:
            result.message = "聚灵阵已达到当前洞府等级上限"
            return result

        # 获取下一级配置
        next_level = cave.spirit_array_level + 1
        next_config = get_spirit_array_config(next_level)

        if not next_config:
            result.message = "聚灵阵已经达到最高等级"
            return result

        # 检查灵石
        if player.stats.spirit_stones < next_config.upgrade_cost:
            result.message = f"灵石不足，需要{next_config.upgrade_cost}灵石"
            return result

        # 扣除灵石
        player.stats.spirit_stones -= next_config.upgrade_cost

        # 升级聚灵阵
        old_level = cave.spirit_array_level
        cave.spirit_array_level = next_level

        # 更新属性
        self._update_cave_stats(cave)

        # 保存到数据库
        self.db.save_player_cave(cave.to_dict())

        # 记录升级
        self.db.record_cave_upgrade(
            cave.id, 'spirit_array',
            old_level, next_level,
            {'spirit_stones': next_config.upgrade_cost}
        )

        result.success = True
        result.message = f"聚灵阵升级成功！当前等级：{next_config.name}"
        result.new_level = next_level
        result.cost = next_config.upgrade_cost

        return result

    def upgrade_defense_array(self, player) -> UpgradeResult:
        """
        升级护山大阵

        Args:
            player: 玩家对象

        Returns:
            升级结果
        """
        result = UpgradeResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 获取当前配置
        cave_config = get_cave_level_config(cave.cave_level)

        # 检查是否达到等级上限
        if cave.defense_array_level >= cave_config.max_defense_level:
            result.message = "护山大阵已达到当前洞府等级上限"
            return result

        # 获取下一级配置
        next_level = cave.defense_array_level + 1
        next_config = get_defense_array_config(next_level)

        if not next_config:
            result.message = "护山大阵已经达到最高等级"
            return result

        # 检查灵石
        if player.stats.spirit_stones < next_config.upgrade_cost:
            result.message = f"灵石不足，需要{next_config.upgrade_cost}灵石"
            return result

        # 扣除灵石
        player.stats.spirit_stones -= next_config.upgrade_cost

        # 升级护山大阵
        old_level = cave.defense_array_level
        cave.defense_array_level = next_level

        # 更新属性
        self._update_cave_stats(cave)

        # 保存到数据库
        self.db.save_player_cave(cave.to_dict())

        # 记录升级
        self.db.record_cave_upgrade(
            cave.id, 'defense_array',
            old_level, next_level,
            {'spirit_stones': next_config.upgrade_cost}
        )

        result.success = True
        result.message = f"护山大阵升级成功！当前等级：{next_config.name}"
        result.new_level = next_level
        result.cost = next_config.upgrade_cost

        return result

    # ==================== 灵田种植功能 ====================

    def plant_crop(self, player, field_index: int, crop_id: str) -> PlantResult:
        """
        种植作物

        Args:
            player: 玩家对象
            field_index: 灵田索引
            crop_id: 作物ID

        Returns:
            种植结果
        """
        result = PlantResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 检查灵田索引
        if field_index < 0 or field_index >= len(cave.fields):
            result.message = "灵田索引无效"
            return result

        field = cave.fields[field_index]

        # 检查灵田是否为空
        if field.stage != "empty":
            result.message = "该灵田已有作物"
            return result

        # 获取作物配置
        crop_config = get_crop_config(crop_id)
        if not crop_config:
            result.message = "作物不存在"
            return result

        # 检查境界要求
        if player.stats.realm_level < crop_config.required_realm:
            result.message = f"境界不足，需要{crop_config.required_realm}级境界"
            return result

        # 检查种子价格
        if player.stats.spirit_stones < crop_config.seed_price:
            result.message = f"灵石不足，需要{crop_config.seed_price}灵石购买种子"
            return result

        # 扣除灵石
        player.stats.spirit_stones -= crop_config.seed_price

        # 种植作物
        field.crop_id = crop_id
        field.crop_name = crop_config.name
        field.planted_at = datetime.now()
        field.growth_days = 0
        field.total_growth_days = crop_config.growth_days
        field.stage = "seed"
        field.yield_amount = crop_config.yield_amount
        field.is_fertilized = False
        field.fertilizer_bonus = 0.0

        # 保存到数据库
        self.db.save_cave_field(field.to_dict())

        result.success = True
        result.message = f"成功种植{crop_config.name}"
        result.field_index = field_index

        return result

    def harvest_crop(self, player, field_index: int) -> HarvestResult:
        """
        收获作物

        Args:
            player: 玩家对象
            field_index: 灵田索引

        Returns:
            收获结果
        """
        result = HarvestResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 检查灵田索引
        if field_index < 0 or field_index >= len(cave.fields):
            result.message = "灵田索引无效"
            return result

        field = cave.fields[field_index]

        # 检查是否有作物可收获
        if field.stage != "mature":
            result.message = "该灵田没有成熟的作物"
            return result

        # 获取作物配置
        crop_config = get_crop_config(field.crop_id)
        if not crop_config:
            result.message = "作物数据错误"
            return result

        # 计算产量
        base_yield = field.yield_amount
        if field.is_fertilized:
            base_yield = int(base_yield * (1 + field.fertilizer_bonus))

        # 随机波动
        quantity = int(base_yield * random.uniform(0.8, 1.2))
        quantity = max(1, quantity)

        # 计算品质
        quality_roll = random.random()
        if quality_roll > 0.95:
            quality = "传说"
            quantity = int(quantity * 1.5)
        elif quality_roll > 0.85:
            quality = "史诗"
            quantity = int(quantity * 1.3)
        elif quality_roll > 0.70:
            quality = "稀有"
            quantity = int(quantity * 1.1)
        elif quality_roll > 0.40:
            quality = "优秀"
        else:
            quality = "普通"

        # 添加到玩家背包
        if hasattr(player, 'inventory'):
            item_data = {
                'name': crop_config.name,
                'description': crop_config.description,
                'type': '材料',
                'rarity': quality,
                'effects': crop_config.effects,
                'value': crop_config.sell_price,
                'usable': True
            }
            player.inventory.add_generated_item(crop_config.name, item_data, quantity)

        # 记录收获
        self.db.record_cave_harvest(
            cave.id, field.id,
            field.crop_id, crop_config.name,
            quantity, quality
        )

        # 清空灵田
        self.db.clear_cave_field(field.id)
        field.crop_id = None
        field.crop_name = ""
        field.planted_at = None
        field.growth_days = 0
        field.total_growth_days = 0
        field.stage = "empty"
        field.yield_amount = 0
        field.is_fertilized = False
        field.fertilizer_bonus = 0.0

        result.success = True
        result.message = f"收获成功！获得【{quality}】{crop_config.name} x{quantity}"
        result.crop_name = crop_config.name
        result.quantity = quantity
        result.quality = quality

        return result

    def update_fields_growth(self, player):
        """
        更新所有灵田的生长状态

        Args:
            player: 玩家对象
        """
        cave = self.get_player_cave(player.stats.name)
        if not cave:
            return

        now = datetime.now()

        for field in cave.fields:
            if field.stage == "empty" or field.stage == "withered":
                continue

            if not field.planted_at:
                continue

            # 计算生长天数
            days_passed = (now - field.planted_at).days
            field.growth_days = days_passed

            # 更新生长阶段
            if field.growth_days >= field.total_growth_days:
                field.stage = "mature"
            elif field.growth_days >= field.total_growth_days * 0.6:
                field.stage = "growth"
            elif field.growth_days >= field.total_growth_days * 0.2:
                field.stage = "sprout"
            else:
                field.stage = "seed"

            # 检查枯萎（超过成熟期的50%）
            if field.growth_days > field.total_growth_days * 1.5:
                field.stage = "withered"

            # 保存到数据库
            self.db.save_cave_field(field.to_dict())

    def fertilize_field(self, player, field_index: int) -> Tuple[bool, str]:
        """
        施肥

        Args:
            player: 玩家对象
            field_index: 灵田索引

        Returns:
            (是否成功, 消息)
        """
        cave = self.get_player_cave(player.stats.name)
        if not cave:
            return False, "你还没有洞府"

        if field_index < 0 or field_index >= len(cave.fields):
            return False, "灵田索引无效"

        field = cave.fields[field_index]

        if field.stage == "empty":
            return False, "该灵田没有作物"

        if field.is_fertilized:
            return False, "该灵田已经施过肥了"

        # 肥料价格
        fertilizer_price = 50

        if player.stats.spirit_stones < fertilizer_price:
            return False, f"灵石不足，需要{fertilizer_price}灵石购买肥料"

        # 扣除灵石
        player.stats.spirit_stones -= fertilizer_price

        # 施肥
        field.is_fertilized = True
        field.fertilizer_bonus = 0.3  # 30%产量加成

        # 保存到数据库
        self.db.save_cave_field(field.to_dict())

        return True, "施肥成功，产量将提升30%"

    # ==================== 护山大阵功能 ====================

    def defend_against_enemy(self, player, enemy_name: str, enemy_level: int) -> DefenseResult:
        """
        护山大阵防御敌人

        Args:
            player: 玩家对象
            enemy_name: 敌人名称
            enemy_level: 敌人等级

        Returns:
            防御结果
        """
        result = DefenseResult(success=False, message="")

        cave = self.get_player_cave(player.stats.name)
        if not cave:
            result.message = "你还没有洞府"
            return result

        # 获取护山大阵配置
        defense_config = get_defense_array_config(cave.defense_array_level)

        if cave.defense_array_level == 0:
            result.message = "没有护山大阵，无法防御"
            return result

        # 计算防御成功率
        defense_power = cave.defense_power
        enemy_power = enemy_level * 100

        success_rate = min(0.9, defense_power / (defense_power + enemy_power))

        # 添加福缘影响
        if hasattr(player.stats, 'fortune'):
            success_rate += player.stats.fortune / 1000

        success_rate = min(0.95, success_rate)

        # 判定是否成功
        if random.random() < success_rate:
            # 防御成功
            damage_dealt = defense_config.attack_power if defense_config else 0
            damage_taken = 0

            # 检查是否驱散敌人
            enemy_repelled = random.random() < (defense_config.enemy_repel if defense_config else 0)

            result.success = True
            result.damage_dealt = damage_dealt
            result.damage_taken = damage_taken
            result.enemy_repelled = enemy_repelled

            if enemy_repelled:
                result.message = f"护山大阵成功驱散{enemy_name}！"
            else:
                result.message = f"护山大阵成功抵御{enemy_name}的攻击！"
        else:
            # 防御失败
            damage_dealt = defense_config.attack_power // 2 if defense_config else 0
            damage_taken = enemy_level * 10

            result.success = False
            result.damage_dealt = damage_dealt
            result.damage_taken = damage_taken
            result.message = f"护山大阵被{enemy_name}攻破！"

        result.enemy_name = enemy_name

        # 记录防御日志
        self.db.record_defense_log(
            cave.id, enemy_name, enemy_level,
            'success' if result.success else 'failed',
            result.damage_dealt, result.damage_taken
        )

        return result

    # ==================== 获取信息功能 ====================

    def get_cultivation_bonus(self, player_name: str) -> float:
        """
        获取洞府修炼加成

        Args:
            player_name: 玩家名称

        Returns:
            修炼加成倍率
        """
        cave = self.get_player_cave(player_name)
        if not cave:
            return 0.0

        return cave.cultivation_bonus

    def get_available_locations(self, player_realm: int) -> List[CaveLocation]:
        """
        获取玩家可购买洞府的地点

        Args:
            player_realm: 玩家境界

        Returns:
            地点列表
        """
        return [loc for loc in CAVE_LOCATIONS.values() if loc.min_realm <= player_realm]

    def get_cave_info(self, player_name: str) -> Dict[str, Any]:
        """
        获取洞府详细信息

        Args:
            player_name: 玩家名称

        Returns:
            洞府信息字典
        """
        cave = self.get_player_cave(player_name)
        if not cave:
            return None

        cave_config = get_cave_level_config(cave.cave_level)
        spirit_config = get_spirit_array_config(cave.spirit_array_level)
        defense_config = get_defense_array_config(cave.defense_array_level)
        location = get_cave_location(cave.location_id)

        # 更新灵田生长状态
        self.update_fields_growth(type('Player', (), {'stats': type('Stats', (), {'name': player_name})})())

        return {
            'id': cave.id,
            'name': cave.cave_name,
            'location': location.name if location else "未知",
            'level': cave_config.name if cave_config else "未知",
            'level_value': cave.cave_level.value,
            'spirit_array': spirit_config.name if spirit_config else "无",
            'defense_array': defense_config.name if defense_config else "无",
            'cultivation_bonus': cave.cultivation_bonus,
            'defense_power': cave.defense_power,
            'spirit_recovery': cave.spirit_recovery,
            'max_fields': cave.max_fields,
            'fields': [
                {
                    'index': f.field_index,
                    'crop': f.crop_name if f.crop_name else "空闲",
                    'stage': self._get_stage_display(f.stage),
                    'progress': f"{f.growth_days}/{f.total_growth_days}" if f.total_growth_days > 0 else "",
                    'is_fertilized': f.is_fertilized
                }
                for f in cave.fields
            ]
        }

    def _get_stage_display(self, stage: str) -> str:
        """获取生长阶段显示文本"""
        stage_map = {
            'empty': '空闲',
            'seed': '种子期',
            'sprout': '发芽期',
            'growth': '生长期',
            'mature': '可收获',
            'withered': '已枯萎'
        }
        return stage_map.get(stage, stage)

    def get_upgrade_info(self, player_name: str) -> Dict[str, Any]:
        """
        获取升级信息

        Args:
            player_name: 玩家名称

        Returns:
            升级信息字典
        """
        cave = self.get_player_cave(player_name)
        if not cave:
            return None

        cave_config = get_cave_level_config(cave.cave_level)
        location = get_cave_location(cave.location_id)

        result = {
            'cave': None,
            'spirit_array': None,
            'defense_array': None
        }

        # 洞府升级信息
        next_cave_level = get_next_cave_level(cave.cave_level)
        if next_cave_level:
            next_config = get_cave_level_config(next_cave_level)
            if next_cave_level.value <= location.max_cave_level.value:
                result['cave'] = {
                    'current': cave_config.name if cave_config else "未知",
                    'next': next_config.name,
                    'cost': int(next_config.upgrade_price * location.price_multiplier),
                    'new_fields': next_config.max_fields - cave_config.max_fields,
                    'new_cultivation_bonus': next_config.cultivation_bonus
                }

        # 聚灵阵升级信息
        if cave.spirit_array_level < cave_config.max_spirit_array_level:
            next_spirit = get_spirit_array_config(cave.spirit_array_level + 1)
            current_spirit = get_spirit_array_config(cave.spirit_array_level)
            if next_spirit:
                result['spirit_array'] = {
                    'current': current_spirit.name if current_spirit else "无",
                    'next': next_spirit.name,
                    'cost': next_spirit.upgrade_cost,
                    'new_cultivation_bonus': next_spirit.cultivation_bonus
                }

        # 护山大阵升级信息
        if cave.defense_array_level < cave_config.max_defense_level:
            next_defense = get_defense_array_config(cave.defense_array_level + 1)
            current_defense = get_defense_array_config(cave.defense_array_level)
            if next_defense:
                result['defense_array'] = {
                    'current': current_defense.name if current_defense else "无",
                    'next': next_defense.name,
                    'cost': next_defense.upgrade_cost,
                    'new_defense_power': next_defense.defense_power,
                    'enemy_repel': next_defense.enemy_repel
                }

        return result


# 全局洞府系统实例
_default_cave_system: Optional[CaveSystem] = None


def get_cave_system(db: Database = None) -> CaveSystem:
    """
    获取默认的洞府系统实例

    Args:
        db: 数据库实例

    Returns:
        CaveSystem实例
    """
    global _default_cave_system
    if _default_cave_system is None:
        _default_cave_system = CaveSystem(db)
    return _default_cave_system
