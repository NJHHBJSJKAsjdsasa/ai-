"""
世界演化系统管理器
实现世界时间线、NPC演化、势力变迁、天材地宝生成、世界事件等核心功能
"""

import random
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.world_config import (
    WORLD_EVENT_TEMPLATES, TREASURE_TYPES, RARITY_LEVELS,
    FACTION_TYPES, NPC_EVOLUTION_CONFIG, WORLD_ECONOMY_CONFIG,
    WORLD_TIME_CONFIG, WorldEventScope, get_event_template,
    get_random_treasure_type, calculate_treasure_value
)
from config import GAME_CONFIG
from storage.database import Database


class WorldEventStatus(Enum):
    """世界事件状态"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class WorldEvent:
    """世界事件数据类"""
    event_id: str
    event_type: str
    title: str
    description: str
    status: WorldEventStatus
    start_year: int
    start_month: int
    start_day: int
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    end_day: Optional[int] = None
    location: str = ""
    scope: str = "local"
    importance: int = 5
    involved_npcs: List[str] = field(default_factory=list)
    involved_factions: List[str] = field(default_factory=list)
    event_data: Dict[str, Any] = field(default_factory=dict)
    player_participated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "start_year": self.start_year,
            "start_month": self.start_month,
            "start_day": self.start_day,
            "end_year": self.end_year,
            "end_month": self.end_month,
            "end_day": self.end_day,
            "location": self.location,
            "scope": self.scope,
            "importance": self.importance,
            "involved_npcs": self.involved_npcs,
            "involved_factions": self.involved_factions,
            "event_data": self.event_data,
            "player_participated": self.player_participated
        }


@dataclass
class TimelineEvent:
    """时间线事件"""
    event_id: str
    event_type: str
    title: str
    description: str
    year: int
    month: int
    day: int
    location: str = ""
    importance: int = 5
    is_historic: bool = False
    involved_npcs: List[str] = field(default_factory=list)
    involved_factions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "location": self.location,
            "importance": self.importance,
            "is_historic": self.is_historic,
            "involved_npcs": self.involved_npcs,
            "involved_factions": self.involved_factions
        }


@dataclass
class Treasure:
    """天材地宝"""
    id: str
    name: str
    treasure_type: str
    rarity: str
    description: str
    effects: Dict[str, Any]
    spawn_location: str
    spawn_year: int
    spawn_month: int
    spawn_day: int
    discoverer_id: str = ""
    discoverer_name: str = ""
    is_discovered: bool = False
    is_claimed: bool = False
    guardian_monster: str = ""
    guardian_level: int = 1
    expire_year: Optional[int] = None
    expire_month: Optional[int] = None
    expire_day: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "treasure_type": self.treasure_type,
            "rarity": self.rarity,
            "description": self.description,
            "effects": self.effects,
            "spawn_location": self.spawn_location,
            "spawn_year": self.spawn_year,
            "spawn_month": self.spawn_month,
            "spawn_day": self.spawn_day,
            "discoverer_id": self.discoverer_id,
            "discoverer_name": self.discoverer_name,
            "is_discovered": self.is_discovered,
            "is_claimed": self.is_claimed,
            "guardian_monster": self.guardian_monster,
            "guardian_level": self.guardian_level,
            "expire_year": self.expire_year,
            "expire_month": self.expire_month,
            "expire_day": self.expire_day
        }


@dataclass
class Faction:
    """势力"""
    id: str
    name: str
    faction_type: str
    description: str
    leader: str
    members: List[str] = field(default_factory=list)
    territory: List[str] = field(default_factory=list)
    reputation: int = 50
    power: int = 50
    wealth: int = 50
    founded_year: int = 1
    is_active: bool = True

    def get_influence(self) -> int:
        """获取影响力"""
        return (self.reputation + self.power + len(self.members) * 2) // 3

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "faction_type": self.faction_type,
            "description": self.description,
            "leader": self.leader,
            "members": self.members,
            "territory": self.territory,
            "reputation": self.reputation,
            "power": self.power,
            "wealth": self.wealth,
            "founded_year": self.founded_year,
            "is_active": self.is_active,
            "influence": self.get_influence()
        }


class WorldEvolutionManager:
    """世界演化管理器"""

    def __init__(self, db: Database = None):
        """初始化世界演化管理器"""
        self.db = db or Database()
        self.active_events: Dict[str, WorldEvent] = {}
        self.factions: Dict[str, Faction] = {}
        self.treasures: Dict[str, Treasure] = {}
        self.economy: Dict[str, Any] = {
            "prices": {},
            "supply": {},
            "demand": {}
        }
        self._init_tables()
        self._load_data()
        self._init_world_data()

    def _init_world_data(self):
        """初始化世界数据（如果没有数据则生成初始内容）"""
        # 如果没有活跃事件，生成一些初始事件
        if not self.active_events:
            self._generate_initial_events()

        # 如果没有宝物，生成一些初始宝物
        if not self.treasures:
            self._generate_initial_treasures()

        # 初始化经济系统
        if not self.economy["prices"]:
            self._init_economy()

        # 初始化势力
        self._init_factions()

    def _generate_initial_events(self, count: int = 3):
        """生成初始世界事件"""
        from datetime import datetime
        now = datetime.now()
        year, month, day = 1, 1, 1

        for _ in range(count):
            self._generate_random_event(year, month, day)

    def _generate_initial_treasures(self, count: int = 5):
        """生成初始天材地宝"""
        year, month, day = 1, 1, 1

        for _ in range(count):
            self._spawn_treasure(year, month, day)

    def _init_economy(self):
        """初始化经济系统"""
        # 设置初始资源价格
        resources = ["spirit_stones", "herbs", "ores", "pellets", "materials"]
        base_prices = {
            "spirit_stones": 100,
            "herbs": 50,
            "ores": 80,
            "pellets": 200,
            "materials": 60
        }

        for resource in resources:
            self.economy["prices"][resource] = base_prices.get(resource, 100)
            self.economy["supply"][resource] = random.randint(40, 80)
            self.economy["demand"][resource] = random.randint(40, 80)

    def _init_factions(self):
        """初始化势力"""
        if not self.factions:
            self._generate_initial_factions()

    def _generate_initial_factions(self, count: int = 5):
        """生成初始势力"""
        faction_names = [
            "青云门", "玄天宗", "万剑阁", "丹鼎派", "灵兽山",
            "天机阁", "血魔宗", "合欢派", "白骨门", "金阳宗"
        ]

        for i in range(min(count, len(faction_names))):
            self._create_faction(faction_names[i])

    def _create_faction(self, name: str) -> Faction:
        """创建势力"""
        faction_type = random.choice(list(FACTION_TYPES.keys()))

        faction = Faction(
            id=str(uuid.uuid4()),
            name=name,
            faction_type=faction_type,
            leader=random.choice(["掌门", "宗主", "阁主", "长老"]),
            founded_year=random.randint(1, 100),
            description=f"{name}是一个{FACTION_TYPES[faction_type]['name']}势力。"
        )

        # 设置初始属性
        faction.power = random.randint(30, 80)
        faction.reputation = random.randint(20, 90)
        faction.wealth = random.randint(20, 80)

        self.factions[faction.id] = faction
        return faction

    def _init_tables(self):
        """初始化数据库表"""
        self.db.init_world_evolution_tables()

    def _load_data(self):
        """从数据库加载数据"""
        # 加载活跃事件
        events_data = self.db.get_active_world_events()
        for event_data in events_data:
            event = WorldEvent(
                event_id=event_data["event_id"],
                event_type=event_data["event_type"],
                title=event_data["title"],
                description=event_data["description"],
                status=WorldEventStatus(event_data["status"]),
                start_year=event_data["start_year"],
                start_month=event_data["start_month"],
                start_day=event_data["start_day"],
                end_year=event_data.get("end_year"),
                end_month=event_data.get("end_month"),
                end_day=event_data.get("end_day"),
                location=event_data.get("location", ""),
                scope=event_data.get("scope", "local"),
                importance=event_data.get("importance", 5),
                involved_npcs=event_data.get("involved_npcs", []),
                involved_factions=event_data.get("involved_factions", []),
                event_data=event_data.get("event_data", {}),
                player_participated=event_data.get("player_participated", False)
            )
            self.active_events[event.event_id] = event

        # 加载活跃宝物
        treasures_data = self.db.get_active_treasures()
        for treasure_data in treasures_data:
            treasure = Treasure(
                id=treasure_data["id"],
                name=treasure_data["name"],
                treasure_type=treasure_data["treasure_type"],
                rarity=treasure_data["rarity"],
                description=treasure_data["description"],
                effects=treasure_data.get("effects", {}),
                spawn_location=treasure_data["spawn_location"],
                spawn_year=treasure_data["spawn_year"],
                spawn_month=treasure_data["spawn_month"],
                spawn_day=treasure_data["spawn_day"],
                discoverer_id=treasure_data.get("discoverer_id", ""),
                discoverer_name=treasure_data.get("discoverer_name", ""),
                is_discovered=treasure_data.get("is_discovered", False),
                is_claimed=treasure_data.get("is_claimed", False),
                guardian_monster=treasure_data.get("guardian_monster", ""),
                guardian_level=treasure_data.get("guardian_level", 1),
                expire_year=treasure_data.get("expire_year"),
                expire_month=treasure_data.get("expire_month"),
                expire_day=treasure_data.get("expire_day")
            )
            self.treasures[treasure.id] = treasure

    def update(self, game_time: Dict[str, int], npc_manager=None, player=None):
        """
        更新世界演化

        Args:
            game_time: 游戏时间字典
            npc_manager: NPC管理器
            player: 玩家对象
        """
        year = game_time.get("year", 1)
        month = game_time.get("month", 1)
        day = game_time.get("day", 1)

        # 检查事件
        self._check_events(year, month, day)

        # 检查宝物生成
        self._check_treasure_spawn(year, month, day)

        # 更新NPC演化
        if npc_manager and day % WORLD_TIME_CONFIG["npc_evolution_interval_days"] == 0:
            self._update_npc_evolution(year, month, day, npc_manager)

        # 更新势力
        if day % WORLD_TIME_CONFIG["faction_update_interval_days"] == 0:
            self._update_factions(year, month, day)

        # 更新经济
        if day % WORLD_TIME_CONFIG["economy_update_interval_days"] == 0:
            self._update_economy(year, month, day)

        # 检查事件结束
        self._check_event_end(year, month, day)

    def _check_events(self, year: int, month: int, day: int):
        """检查并生成新事件"""
        # 随机事件生成概率
        if random.random() < WORLD_TIME_CONFIG["treasure_spawn_chance"]:
            self._generate_random_event(year, month, day)

    def _generate_random_event(self, year: int, month: int, day: int):
        """生成随机事件"""
        # 随机选择事件模板
        template = random.choice(WORLD_EVENT_TEMPLATES)

        # 检查是否可以重复
        if not template.can_repeat:
            # 检查是否已有同类型活跃事件
            for event in self.active_events.values():
                if event.event_type == template.event_type:
                    return

        # 生成事件数据
        event_id = str(uuid.uuid4())
        title = random.choice(template.title_templates)
        description = random.choice(template.description_templates)

        # 填充变量
        locations = [loc["name"] for loc in GAME_CONFIG["world"]["locations"]]
        location = random.choice(locations) if locations else "未知地点"

        # 随机选择一个势力名称（如果有势力）
        faction_name = "某势力"
        if self.factions:
            faction_name = random.choice(list(self.factions.values())).name

        # 格式化标题和描述，处理可能的占位符
        try:
            title = title.format(location=location, faction=faction_name)
        except KeyError:
            pass  # 如果还有其他占位符，忽略

        try:
            description = description.format(location=location, faction=faction_name)
        except KeyError:
            pass

        # 创建事件
        event = WorldEvent(
            event_id=event_id,
            event_type=template.event_type,
            title=title,
            description=description,
            status=WorldEventStatus.ACTIVE,
            start_year=year,
            start_month=month,
            start_day=day,
            location=location,
            scope=template.scope.value,
            importance=random.randint(template.min_importance, template.max_importance),
            event_data=template.effects
        )

        # 保存到内存和数据库
        self.active_events[event_id] = event
        self.db.save_world_event(event.to_dict())

        # 记录到时间线
        self._record_timeline_event(
            event_type=template.event_type,
            title=title,
            description=description,
            year=year, month=month, day=day,
            location=location,
            importance=event.importance,
            is_historic=event.importance >= 8
        )

        return event

    def _record_timeline_event(self, event_type: str, title: str, description: str,
                               year: int, month: int, day: int, location: str = "",
                               importance: int = 5, is_historic: bool = False,
                               involved_npcs: List[str] = None,
                               involved_factions: List[str] = None):
        """记录时间线事件"""
        timeline_data = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "title": title,
            "description": description,
            "year": year,
            "month": month,
            "day": day,
            "location": location,
            "importance": importance,
            "is_historic": is_historic,
            "involved_npcs": involved_npcs or [],
            "involved_factions": involved_factions or []
        }
        self.db.save_world_timeline_event(timeline_data)

    def _check_treasure_spawn(self, year: int, month: int, day: int):
        """检查天材地宝生成"""
        if random.random() < WORLD_TIME_CONFIG["treasure_spawn_chance"]:
            self._spawn_treasure(year, month, day)

    def _spawn_treasure(self, year: int, month: int, day: int) -> Optional[Treasure]:
        """生成天材地宝"""
        treasure_type_key = get_random_treasure_type()
        treasure_type = TREASURE_TYPES[treasure_type_key]

        # 选择生成地点
        locations = [loc["name"] for loc in GAME_CONFIG["world"]["locations"]
                     if loc.get("danger_level") in ["危险", "绝境"]]
        if not locations:
            locations = [loc["name"] for loc in GAME_CONFIG["world"]["locations"]]

        location = random.choice(locations)

        # 创建宝物
        treasure_id = str(uuid.uuid4())
        treasure = Treasure(
            id=treasure_id,
            name=treasure_type["name"],
            treasure_type=treasure_type["type"],
            rarity=treasure_type["rarity"],
            description=treasure_type["description"],
            effects=treasure_type["effects"],
            spawn_location=location,
            spawn_year=year,
            spawn_month=month,
            spawn_day=day,
            guardian_monster=self._generate_guardian(treasure_type["rarity"]),
            guardian_level=self._calculate_guardian_level(treasure_type["rarity"]),
            expire_year=year + random.randint(1, 3),
            expire_month=month,
            expire_day=day
        )

        # 保存
        self.treasures[treasure_id] = treasure
        self.db.save_treasure(treasure.to_dict())

        # 记录事件
        self._record_timeline_event(
            event_type="天材地宝出世",
            title=f"{treasure.name}现世",
            description=f"{treasure.name}在{location}出现，引起各方关注。",
            year=year, month=month, day=day,
            location=location,
            importance=RARITY_LEVELS[treasure.rarity]["spawn_weight"] // 10 + 3
        )

        return treasure

    def _generate_guardian(self, rarity: str) -> str:
        """生成守护兽"""
        guardians = {
            "common": ["野狼", "山猪", "毒蛇"],
            "uncommon": ["妖狼", "铁背熊", "双头蛇"],
            "rare": ["金丹期妖兽", "筑基期妖兽", "三头蛇"],
            "epic": ["元婴期妖兽", "化形妖兽", "上古异兽"],
            "legendary": ["化神期妖兽", "真龙后裔", "凤凰后裔"],
            "mythic": ["渡劫期妖兽", "真龙", "凤凰"]
        }
        return random.choice(guardians.get(rarity, ["妖兽"]))

    def _calculate_guardian_level(self, rarity: str) -> int:
        """计算守护兽等级"""
        level_map = {
            "common": random.randint(1, 3),
            "uncommon": random.randint(3, 6),
            "rare": random.randint(6, 10),
            "epic": random.randint(10, 15),
            "legendary": random.randint(15, 20),
            "mythic": random.randint(20, 30)
        }
        return level_map.get(rarity, 1)

    def _update_npc_evolution(self, year: int, month: int, day: int, npc_manager):
        """更新NPC演化"""
        if not npc_manager or not hasattr(npc_manager, 'npcs'):
            return

        for npc in npc_manager.npcs.values():
            if not npc.data.is_alive:
                continue

            # 突破尝试
            if random.random() < NPC_EVOLUTION_CONFIG["breakthrough_chance"]:
                self._try_npc_breakthrough(npc, year, month, day)

            # 探索行为
            if random.random() < NPC_EVOLUTION_CONFIG["exploration_chance"]:
                self._try_npc_exploration(npc, year, month, day)

            # 社交行为
            if random.random() < NPC_EVOLUTION_CONFIG["social_chance"]:
                self._try_npc_social(npc, year, month, day)

            # 战斗行为
            if random.random() < NPC_EVOLUTION_CONFIG["combat_chance"]:
                self._try_npc_combat(npc, year, month, day)

            # 检查死亡
            self._check_npc_death(npc, year, month, day)

    def _try_npc_breakthrough(self, npc, year: int, month: int, day: int):
        """NPC尝试突破"""
        old_realm = npc.data.realm_level

        # 突破成功率
        success_rate = 0.3 + (npc.data.talent or 0.5) * 0.3

        if random.random() < success_rate and old_realm < 9:
            npc.data.realm_level += 1

            # 记录演化
            evolution_data = {
                "npc_id": npc.data.id,
                "npc_name": npc.data.name,
                "evolution_type": "突破",
                "year": year,
                "month": month,
                "day": day,
                "old_realm": old_realm,
                "new_realm": npc.data.realm_level,
                "action_taken": "闭关突破",
                "action_result": "成功"
            }
            self.db.save_npc_evolution(evolution_data)

            # 记录重要突破到时间线
            if npc.data.realm_level >= 4:
                self._record_timeline_event(
                    event_type="NPC突破",
                    title=f"{npc.data.name}突破至新境界",
                    description=f"{npc.data.name}成功突破，实力大增。",
                    year=year, month=month, day=day,
                    location=npc.data.location,
                    importance=5 + npc.data.realm_level,
                    is_historic=npc.data.realm_level >= 6,
                    involved_npcs=[npc.data.id]
                )

    def _try_npc_exploration(self, npc, year: int, month: int, day: int):
        """NPC尝试探索"""
        locations = [loc["name"] for loc in GAME_CONFIG["world"]["locations"]]
        if not locations:
            return

        old_location = npc.data.location
        new_location = random.choice(locations)

        if new_location != old_location:
            npc.data.location = new_location

            # 记录演化
            evolution_data = {
                "npc_id": npc.data.id,
                "npc_name": npc.data.name,
                "evolution_type": "迁移",
                "year": year,
                "month": month,
                "day": day,
                "old_location": old_location,
                "new_location": new_location,
                "action_taken": "探索",
                "action_result": f"前往{new_location}"
            }
            self.db.save_npc_evolution(evolution_data)

    def _try_npc_social(self, npc, year: int, month: int, day: int):
        """NPC尝试社交"""
        # 简化的社交逻辑
        pass

    def _try_npc_combat(self, npc, year: int, month: int, day: int):
        """NPC尝试战斗"""
        # 简化的战斗逻辑
        pass

    def _check_npc_death(self, npc, year: int, month: int, day: int):
        """检查NPC死亡"""
        # 基于年龄的死亡概率
        base_lifespan = NPC_EVOLUTION_CONFIG["realm_lifespan_bonus"].get(
            npc.data.realm_level, 100
        )
        max_lifespan = int(base_lifespan * NPC_EVOLUTION_CONFIG["max_age_multiplier"])

        if npc.data.age >= max_lifespan:
            death_chance = 0.5
        elif npc.data.age >= base_lifespan:
            death_chance = 0.1
        else:
            death_chance = NPC_EVOLUTION_CONFIG["death_chance_base"]

        if random.random() < death_chance:
            npc.data.is_alive = False

            # 记录演化
            evolution_data = {
                "npc_id": npc.data.id,
                "npc_name": npc.data.name,
                "evolution_type": "死亡",
                "year": year,
                "month": month,
                "day": day,
                "action_taken": "寿终正寝",
                "action_result": f"享年{npc.data.age}岁"
            }
            self.db.save_npc_evolution(evolution_data)

            # 记录到时间线
            self._record_timeline_event(
                event_type="NPC死亡",
                title=f"{npc.data.name}陨落",
                description=f"{npc.data.name}寿终正寝，享年{npc.data.age}岁。",
                year=year, month=month, day=day,
                location=npc.data.location,
                importance=3,
                involved_npcs=[npc.data.id]
            )

    def _update_factions(self, year: int, month: int, day: int):
        """更新势力"""
        for faction in self.factions.values():
            if not faction.is_active:
                continue

            # 势力自然变化
            power_change = random.randint(-5, 5)
            reputation_change = random.randint(-3, 3)
            wealth_change = random.randint(-5, 5)

            old_power = faction.power
            old_reputation = faction.reputation

            faction.power = max(10, min(100, faction.power + power_change))
            faction.reputation = max(10, min(100, faction.reputation + reputation_change))
            faction.wealth = max(10, min(100, faction.wealth + wealth_change))

            # 记录重大变化
            if abs(power_change) >= 5:
                change_data = {
                    "faction_id": faction.id,
                    "faction_name": faction.name,
                    "change_type": "实力变化",
                    "change_description": f"势力实力从{old_power}变为{faction.power}",
                    "year": year,
                    "month": month,
                    "day": day,
                    "old_value": old_power,
                    "new_value": faction.power
                }
                self.db.save_faction_change(change_data)

            # 检查势力衰落
            if faction.power < 20 and faction.reputation < 20:
                if random.random() < 0.3:
                    faction.is_active = False
                    change_data = {
                        "faction_id": faction.id,
                        "faction_name": faction.name,
                        "change_type": "势力解散",
                        "change_description": f"{faction.name}因实力衰退而解散",
                        "year": year,
                        "month": month,
                        "day": day,
                        "old_value": "活跃",
                        "new_value": "解散"
                    }
                    self.db.save_faction_change(change_data)

                    self._record_timeline_event(
                        event_type="势力衰落",
                        title=f"{faction.name}解散",
                        description=f"{faction.name}因实力衰退而解散。",
                        year=year, month=month, day=day,
                        importance=6,
                        is_historic=True,
                        involved_factions=[faction.id]
                    )

    def _update_economy(self, year: int, month: int, day: int):
        """更新经济"""
        for resource, config in WORLD_ECONOMY_CONFIG["resources"].items():
            # 价格波动
            volatility = config["volatility"]
            change = random.uniform(-volatility, volatility)

            current_price = self.economy["prices"].get(resource, config["base_price"])
            new_price = max(0.5, current_price * (1 + change))

            self.economy["prices"][resource] = new_price

            # 供需变化
            supply_change = random.randint(-10, 10)
            demand_change = random.randint(-10, 10)

            self.economy["supply"][resource] = max(0, min(100,
                self.economy["supply"].get(resource, 50) + supply_change))
            self.economy["demand"][resource] = max(0, min(100,
                self.economy["demand"].get(resource, 50) + demand_change))

            # 记录到数据库
            economy_data = {
                "year": year,
                "month": month,
                "day": day,
                "resource_type": resource,
                "price": new_price,
                "supply_level": self.economy["supply"][resource],
                "demand_level": self.economy["demand"][resource]
            }
            self.db.save_economy_record(economy_data)

    def _check_event_end(self, year: int, month: int, day: int):
        """检查事件是否结束"""
        for event in list(self.active_events.values()):
            if event.status != WorldEventStatus.ACTIVE:
                continue

            # 检查事件是否到期
            template = get_event_template(event.event_type)
            if template:
                # 计算事件持续时间
                days_passed = (year - event.start_year) * 360 + \
                             (month - event.start_month) * 30 + \
                             (day - event.start_day)

                if days_passed >= template.duration_days:
                    self._end_event(event, year, month, day)

    def _end_event(self, event: WorldEvent, year: int, month: int, day: int):
        """结束事件"""
        event.status = WorldEventStatus.COMPLETED
        event.end_year = year
        event.end_month = month
        event.end_day = day

        # 更新数据库
        self.db.update_world_event_status(
            event.event_id, "completed", year, month, day
        )

        # 从活跃事件移除
        if event.event_id in self.active_events:
            del self.active_events[event.event_id]

    def create_faction(self, name: str, faction_type: str, description: str,
                       leader: str, year: int = 1) -> Faction:
        """
        创建新势力

        Args:
            name: 势力名称
            faction_type: 势力类型
            description: 势力描述
            leader: 领袖
            year: 创建年份

        Returns:
            新势力
        """
        faction_id = f"faction_{len(self.factions)}"
        faction = Faction(
            id=faction_id,
            name=name,
            faction_type=faction_type,
            description=description,
            leader=leader,
            founded_year=year
        )
        self.factions[faction_id] = faction

        # 记录到时间线
        self._record_timeline_event(
            event_type="势力崛起",
            title=f"{name}成立",
            description=f"{name}成立，{leader}担任领袖。",
            year=year, month=1, day=1,
            importance=6,
            is_historic=True,
            involved_factions=[faction_id]
        )

        return faction

    def player_participate_event(self, event_id: str, player_id: str,
                                 participation_type: str, description: str,
                                 year: int, month: int, day: int,
                                 contribution_score: int = 0) -> bool:
        """
        记录玩家参与世界事件

        Args:
            event_id: 事件ID
            player_id: 玩家ID
            participation_type: 参与类型
            description: 参与描述
            year: 年份
            month: 月份
            day: 日期
            contribution_score: 贡献分数

        Returns:
            是否成功
        """
        # 更新事件
        if event_id in self.active_events:
            self.active_events[event_id].player_participated = True
            self.db.save_world_event(self.active_events[event_id].to_dict())

        # 记录参与
        participation_data = {
            "player_id": player_id,
            "event_id": event_id,
            "participation_type": participation_type,
            "participation_description": description,
            "year": year,
            "month": month,
            "day": day,
            "contribution_score": contribution_score
        }
        self.db.record_player_participation(participation_data)
        return True

    def claim_treasure(self, treasure_id: str, player_id: str, player_name: str) -> bool:
        """
        玩家获取天材地宝

        Args:
            treasure_id: 宝物ID
            player_id: 玩家ID
            player_name: 玩家名称

        Returns:
            是否成功
        """
        if treasure_id not in self.treasures:
            return False

        treasure = self.treasures[treasure_id]
        if treasure.is_claimed:
            return False

        # 更新宝物状态
        treasure.is_claimed = True
        treasure.discoverer_id = player_id
        treasure.discoverer_name = player_name
        treasure.is_discovered = True

        # 更新数据库
        success = self.db.claim_treasure(treasure_id, player_id, player_name)

        if success:
            # 从活跃宝物移除
            del self.treasures[treasure_id]

        return success

    def get_active_events(self, scope: str = None, location: str = None) -> List[WorldEvent]:
        """
        获取活跃事件

        Args:
            scope: 范围筛选
            location: 地点筛选

        Returns:
            活跃事件列表
        """
        events = list(self.active_events.values())

        if scope:
            events = [e for e in events if e.scope == scope]

        if location:
            events = [e for e in events if e.location == location]

        return sorted(events, key=lambda e: e.importance, reverse=True)

    def get_timeline(self, year: int = None, is_historic: bool = None,
                     limit: int = 50) -> List[TimelineEvent]:
        """
        获取时间线

        Args:
            year: 年份筛选
            is_historic: 是否历史事件
            limit: 返回数量限制

        Returns:
            时间线事件列表
        """
        events_data = self.db.get_world_timeline(year=year, is_historic=is_historic, limit=limit)
        return [
            TimelineEvent(
                event_id=e["event_id"],
                event_type=e["event_type"],
                title=e["title"],
                description=e["description"],
                year=e["year"],
                month=e["month"],
                day=e["day"],
                location=e.get("location", ""),
                importance=e.get("importance", 5),
                is_historic=e.get("is_historic", False),
                involved_npcs=e.get("involved_npcs", []),
                involved_factions=e.get("involved_factions", [])
            )
            for e in events_data
        ]

    def get_active_treasures(self, location: str = None) -> List[Treasure]:
        """
        获取活跃宝物

        Args:
            location: 地点筛选

        Returns:
            活跃宝物列表
        """
        treasures = list(self.treasures.values())

        if location:
            treasures = [t for t in treasures if t.spawn_location == location]

        return treasures

    def get_faction_ranking(self) -> List[Faction]:
        """
        获取势力排名

        Returns:
            按影响力排序的势力列表
        """
        active_factions = [f for f in self.factions.values() if f.is_active]
        return sorted(active_factions, key=lambda f: f.get_influence(), reverse=True)

    def get_economy_info(self) -> Dict[str, Any]:
        """
        获取经济信息

        Returns:
            经济信息字典
        """
        return {
            "prices": self.economy["prices"],
            "supply": self.economy["supply"],
            "demand": self.economy["demand"]
        }

    def get_world_stats(self) -> Dict[str, Any]:
        """
        获取世界统计信息

        Returns:
            统计信息字典
        """
        return {
            "active_events_count": len(self.active_events),
            "active_treasures_count": len(self.treasures),
            "factions_count": len([f for f in self.factions.values() if f.is_active]),
            "total_factions": len(self.factions),
            "economy": self.get_economy_info()
        }
