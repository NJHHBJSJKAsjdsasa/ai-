"""
世界演化系统模块
实现世界的动态演化，包括势力兴衰、历史记录、新事物生成
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG, get_realm_info


class EventType(Enum):
    """世界事件类型"""
    BIRTH = auto()  # 出生
    DEATH = auto()  # 死亡
    BREAKTHROUGH = auto()  # 突破
    FACTION_RISE = auto()  # 势力崛起
    FACTION_FALL = auto()  # 势力衰落
    DISCOVERY = auto()  # 发现
    CONFLICT = auto()  # 冲突
    ALLIANCE = auto()  # 结盟
    TRADE = auto()  # 贸易
    NATURAL_DISASTER = auto()  # 天灾


@dataclass
class WorldEvent:
    """世界事件"""
    event_type: EventType
    year: int
    month: int
    day: int
    description: str
    involved_npcs: List[str] = field(default_factory=list)
    location: str = ""
    impact: int = 0  # 影响程度（0-100）
    is_historic: bool = False  # 是否为历史事件

    def to_string(self) -> str:
        """转换为字符串"""
        return f"第{self.year}年{self.month}月{self.day}日 - {self.description}"


@dataclass
class Faction:
    """势力"""
    id: str
    name: str
    faction_type: str  # 门派、家族、散修联盟
    leader: str
    members: List[str] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)
    territory: List[str] = field(default_factory=list)
    reputation: int = 50  # 声望（0-100）
    power: int = 50  # 实力（0-100）
    founded_year: int = 1
    is_active: bool = True

    def get_influence(self) -> int:
        """获取影响力"""
        return (self.reputation + self.power + len(self.members) * 2) // 3


class WorldEvolution:
    """世界演化系统"""

    def __init__(self):
        """初始化世界演化系统"""
        self.factions: Dict[str, Faction] = {}
        self.events: List[WorldEvent] = []
        self.economy = {
            "resources": {
                "spirit_stones": 10000,
                "herbs": 1000,
                "ores": 1000,
                "pellets": 500,
            },
            "prices": {
                "spirit_stones": 1.0,
                "herbs": 10.0,
                "ores": 15.0,
                "pellets": 50.0,
            },
            "price_history": [],
        }
        self.evolution_log: List[str] = []

    def update(self, game_time: Dict[str, int], npc_manager=None):
        """
        更新世界演化

        Args:
            game_time: 游戏时间字典
            npc_manager: NPC管理器
        """
        year = game_time.get("year", 1)
        month = game_time.get("month", 1)
        day = game_time.get("day", 1)

        # 每月更新一次经济
        if day == 1:
            self._update_economy()

        # 每季度检查势力变化
        if month % 3 == 0 and day == 1:
            self._update_factions()

        # 随机事件
        if random.random() < 0.1:  # 10%概率
            self._generate_random_event(year, month, day, npc_manager)

    def _update_economy(self):
        """更新经济系统"""
        # 物价波动
        for resource in self.economy["prices"]:
            current_price = self.economy["prices"][resource]
            # 随机波动 ±10%
            change = random.uniform(-0.1, 0.1)
            new_price = max(0.5, current_price * (1 + change))
            self.economy["prices"][resource] = round(new_price, 2)

        # 记录历史
        self.economy["price_history"].append({
            "prices": self.economy["prices"].copy(),
            "timestamp": datetime.now().isoformat(),
        })

        # 限制历史记录长度
        if len(self.economy["price_history"]) > 100:
            self.economy["price_history"] = self.economy["price_history"][-100:]

    def _update_factions(self):
        """更新势力"""
        for faction in self.factions.values():
            if not faction.is_active:
                continue

            # 势力自然变化
            change = random.randint(-5, 5)
            faction.power = max(0, min(100, faction.power + change))

            # 声望变化
            reputation_change = random.randint(-3, 3)
            faction.reputation = max(0, min(100, faction.reputation + reputation_change))

            # 检查势力衰落
            if faction.power < 20 and faction.reputation < 20:
                if random.random() < 0.3:
                    faction.is_active = False
                    self._record_event(
                        EventType.FACTION_FALL,
                        faction.founded_year, 1, 1,
                        f"{faction.name}因实力衰退而解散",
                        involved_npcs=[faction.leader],
                        impact=60,
                        is_historic=True
                    )

    def _generate_random_event(self, year: int, month: int, day: int, npc_manager=None):
        """生成随机事件"""
        event_types = [
            EventType.DISCOVERY,
            EventType.CONFLICT,
            EventType.TRADE,
        ]

        if npc_manager:
            event_types.extend([EventType.BIRTH, EventType.DEATH, EventType.BREAKTHROUGH])

        event_type = random.choice(event_types)

        if event_type == EventType.DISCOVERY:
            self._handle_discovery(year, month, day)
        elif event_type == EventType.CONFLICT:
            self._handle_conflict(year, month, day)
        elif event_type == EventType.TRADE:
            self._handle_trade(year, month, day)
        elif event_type == EventType.BIRTH and npc_manager:
            self._handle_birth(year, month, day, npc_manager)
        elif event_type == EventType.DEATH and npc_manager:
            self._handle_death(year, month, day, npc_manager)
        elif event_type == EventType.BREAKTHROUGH and npc_manager:
            self._handle_breakthrough(year, month, day, npc_manager)

    def _handle_discovery(self, year: int, month: int, day: int):
        """处理发现事件"""
        discoveries = [
            "一处上古遗迹",
            "一条灵石矿脉",
            "一片灵药园",
            "一个秘境入口",
            "一本失传功法",
        ]
        discovery = random.choice(discoveries)
        location = random.choice(["万兽山脉", "天元城", "海外", "新手村"])

        self._record_event(
            EventType.DISCOVERY,
            year, month, day,
            f"在{location}发现了{discovery}",
            location=location,
            impact=random.randint(30, 70)
        )

    def _handle_conflict(self, year: int, month: int, day: int):
        """处理冲突事件"""
        factions_list = [f for f in self.factions.values() if f.is_active]
        if len(factions_list) >= 2:
            f1, f2 = random.sample(factions_list, 2)
            self._record_event(
                EventType.CONFLICT,
                year, month, day,
                f"{f1.name}与{f2.name}发生冲突",
                involved_npcs=[f1.leader, f2.leader],
                impact=random.randint(40, 80)
            )

    def _handle_trade(self, year: int, month: int, day: int):
        """处理贸易事件"""
        resources = ["灵石", "药材", "矿石", "丹药"]
        resource = random.choice(resources)
        amount = random.randint(100, 1000)

        self._record_event(
            EventType.TRADE,
            year, month, day,
            f"市场上交易了{amount}{resource}",
            impact=random.randint(10, 30)
        )

    def _handle_birth(self, year: int, month: int, day: int, npc_manager):
        """处理出生事件"""
        # 生成新NPC
        from .npc import NPC
        new_npc = NPC()
        new_npc.data.age = 0
        new_npc.data.location = random.choice(["新手村", "天元城"])

        if npc_manager:
            npc_manager.npcs[new_npc.data.id] = new_npc

        self._record_event(
            EventType.BIRTH,
            year, month, day,
            f"{new_npc.data.dao_name}出生了",
            involved_npcs=[new_npc.data.id],
            location=new_npc.data.location,
            impact=20
        )

    def _handle_death(self, year: int, month: int, day: int, npc_manager):
        """处理死亡事件"""
        # 找一个年龄大的NPC
        if npc_manager and npc_manager.npcs:
            old_npcs = [npc for npc in npc_manager.npcs.values()
                        if npc.data.age > npc.data.lifespan * 0.8]
            if old_npcs:
                npc = random.choice(old_npcs)
                npc.data.is_alive = False

                self._record_event(
                    EventType.DEATH,
                    year, month, day,
                    f"{npc.data.dao_name}寿终正寝，享年{npc.data.age}岁",
                    involved_npcs=[npc.data.id],
                    location=npc.data.location,
                    impact=40
                )

    def _handle_breakthrough(self, year: int, month: int, day: int, npc_manager):
        """处理突破事件"""
        if npc_manager and npc_manager.npcs:
            npcs = [npc for npc in npc_manager.npcs.values()
                    if npc.data.is_alive and npc.data.realm_level < 6]
            if npcs:
                npc = random.choice(npcs)
                old_realm = npc.get_realm_name()
                npc.data.realm_level += 1
                new_realm = npc.get_realm_name()

                self._record_event(
                    EventType.BREAKTHROUGH,
                    year, month, day,
                    f"{npc.data.dao_name}突破成功，从{old_realm}晋升至{new_realm}",
                    involved_npcs=[npc.data.id],
                    location=npc.data.location,
                    impact=50,
                    is_historic=(npc.data.realm_level >= 4)
                )

    def _record_event(self, event_type: EventType, year: int, month: int, day: int,
                      description: str, involved_npcs: List[str] = None,
                      location: str = "", impact: int = 0, is_historic: bool = False):
        """记录事件"""
        event = WorldEvent(
            event_type=event_type,
            year=year,
            month=month,
            day=day,
            description=description,
            involved_npcs=involved_npcs or [],
            location=location,
            impact=impact,
            is_historic=is_historic
        )
        self.events.append(event)

        # 添加到日志
        self.evolution_log.append(event.to_string())

        # 限制日志长度
        if len(self.evolution_log) > 1000:
            self.evolution_log = self.evolution_log[-1000:]

    def create_faction(self, name: str, faction_type: str, leader: str,
                       year: int = 1) -> Faction:
        """
        创建新势力

        Args:
            name: 势力名称
            faction_type: 势力类型
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
            leader=leader,
            founded_year=year
        )
        self.factions[faction_id] = faction

        self._record_event(
            EventType.FACTION_RISE,
            year, 1, 1,
            f"{name}成立，{leader}担任领袖",
            involved_npcs=[leader],
            impact=60,
            is_historic=True
        )

        return faction

    def get_recent_events(self, count: int = 10) -> List[WorldEvent]:
        """获取最近事件"""
        return self.events[-count:]

    def get_historic_events(self) -> List[WorldEvent]:
        """获取历史事件"""
        return [e for e in self.events if e.is_historic]

    def get_faction_ranking(self) -> List[Faction]:
        """获取势力排名"""
        active_factions = [f for f in self.factions.values() if f.is_active]
        return sorted(active_factions, key=lambda f: f.get_influence(), reverse=True)

    def get_market_info(self) -> Dict[str, Any]:
        """获取市场信息"""
        return {
            "prices": self.economy["prices"],
            "resources": self.economy["resources"],
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "factions": {
                fid: {
                    "id": f.id,
                    "name": f.name,
                    "faction_type": f.faction_type,
                    "leader": f.leader,
                    "members": f.members,
                    "resources": f.resources,
                    "territory": f.territory,
                    "reputation": f.reputation,
                    "power": f.power,
                    "founded_year": f.founded_year,
                    "is_active": f.is_active,
                }
                for fid, f in self.factions.items()
            },
            "events": [
                {
                    "event_type": e.event_type.name,
                    "year": e.year,
                    "month": e.month,
                    "day": e.day,
                    "description": e.description,
                    "involved_npcs": e.involved_npcs,
                    "location": e.location,
                    "impact": e.impact,
                    "is_historic": e.is_historic,
                }
                for e in self.events
            ],
            "economy": self.economy,
        }
