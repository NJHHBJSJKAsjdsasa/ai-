from typing import List, Optional, Dict, Set
from domain.value_objects.player_attributes import PlayerAttributes
from domain.value_objects.player_status import PlayerStatus, PlayerState, Affliction, AfflictionType
from domain.value_objects.cultivation_realm import CultivationRealm
from domain.value_objects.experience import Experience

class Player:
    """玩家实体"""
    def __init__(self, player_id: str, name: str, cultivation_realm: CultivationRealm):
        self._id = player_id  # 唯一标识
        self._name = name  # 玩家名称
        self._cultivation_realm = cultivation_realm  # 修炼境界
        self._attributes = PlayerAttributes()  # 玩家属性
        self._status = PlayerStatus()  # 玩家状态
        self._inventory: List[Dict] = []  # 背包
        self._techniques: List[Dict] = []  # 技能
        self._friends: Set[str] = set()  # 好友
        self._enemies: Set[str] = set()  # 敌人
        self._quests: List[Dict] = []  # 任务
        self._achievements: List[Dict] = []  # 成就
        self._sects: List[Dict] = []  # 门派
        self._caves: List[Dict] = []  # 洞府
        self._pets: List[Dict] = []  # 宠物
        self._memories: List[Dict] = []  # 记忆
        self._events: List[Dict] = []  # 事件
        self._current_exp: Experience = Experience(value=0, source="初始经验", timestamp=0)  # 当前经验值

    @property
    def id(self) -> str:
        """获取玩家ID"""
        return self._id

    @property
    def name(self) -> str:
        """获取玩家名称"""
        return self._name

    @name.setter
    def name(self, value: str):
        """设置玩家名称"""
        self._name = value

    @property
    def cultivation_realm(self) -> CultivationRealm:
        """获取修炼境界"""
        return self._cultivation_realm
    
    @property
    def current_exp(self) -> Experience:
        """获取当前经验值"""
        return self._current_exp
    
    @property
    def current_exp_value(self) -> int:
        """获取当前经验值数值"""
        return self._current_exp.value

    @property
    def attributes(self) -> PlayerAttributes:
        """获取玩家属性"""
        return self._attributes

    @property
    def status(self) -> PlayerStatus:
        """获取玩家状态"""
        return self._status

    @property
    def inventory(self) -> List[Dict]:
        """获取背包"""
        return self._inventory

    @property
    def techniques(self) -> List[Dict]:
        """获取技能"""
        return self._techniques

    @property
    def friends(self) -> Set[str]:
        """获取好友"""
        return self._friends

    @property
    def enemies(self) -> Set[str]:
        """获取敌人"""
        return self._enemies

    @property
    def quests(self) -> List[Dict]:
        """获取任务"""
        return self._quests

    @property
    def achievements(self) -> List[Dict]:
        """获取成就"""
        return self._achievements

    @property
    def sects(self) -> List[Dict]:
        """获取门派"""
        return self._sects

    @property
    def caves(self) -> List[Dict]:
        """获取洞府"""
        return self._caves

    @property
    def pets(self) -> List[Dict]:
        """获取宠物"""
        return self._pets

    @property
    def memories(self) -> List[Dict]:
        """获取记忆"""
        return self._memories

    @property
    def events(self) -> List[Dict]:
        """获取事件"""
        return self._events

    def update_attributes(self, **kwargs) -> None:
        """更新玩家属性"""
        self._attributes = self._attributes.update(**kwargs)

    def update_status(self, **kwargs) -> None:
        """更新玩家状态"""
        self._status = self._status.update(**kwargs)

    def change_cultivation_realm(self, new_realm: CultivationRealm) -> None:
        """改变修炼境界"""
        self._cultivation_realm = new_realm
        # 重置当前经验值
        self._current_exp = Experience(value=0, source=f"突破到{new_realm.name}", timestamp=0)
        # 应用境界带来的属性加成
        self.update_attributes(
            lifespan=self._attributes.lifespan + new_realm.lifespan_bonus,
            spiritual_power=self._attributes.spiritual_power + new_realm.spiritual_power_bonus
        )

    def cultivate(self, time: int) -> int:
        """修炼"""
        if not self._status.is_available():
            return 0

        # 更新状态为修炼中
        self.update_status(current_state=PlayerState.CULTIVATING, is_cultivating=True)

        # 计算修炼获得的经验值
        base_exp = time * 10
        speed_bonus = self._attributes.cultivation_speed
        comprehension_bonus = self._attributes.comprehension / 10
        total_exp = int(base_exp * speed_bonus * (1 + comprehension_bonus))

        # 创建新的经验值对象
        new_exp = Experience(value=total_exp, source="修炼", timestamp=0)
        # 更新当前经验值
        self._current_exp = self._current_exp.add(new_exp)

        # 更新属性
        self.update_attributes(exp=self._attributes.exp + total_exp, cultivation=self._attributes.cultivation + 1)

        # 更新状态为空闲
        self.update_status(current_state=PlayerState.IDLE, is_cultivating=False)

        return total_exp
    
    def can_breakthrough(self) -> bool:
        """检查是否可以突破"""
        return self._cultivation_realm.can_breakthrough(self._current_exp.value)
    
    def breakthrough(self) -> bool:
        """尝试突破境界"""
        if not self.can_breakthrough() or self._cultivation_realm.next_realm is None:
            return False
        
        # 计算突破成功率
        base_success_rate = 0.8
        difficulty_penalty = self._cultivation_realm.get_breakthrough_difficulty()
        willpower_bonus = self._attributes.willpower / 100
        success_rate = base_success_rate - difficulty_penalty + willpower_bonus
        success_rate = max(0.1, min(0.99, success_rate))
        
        # 突破成功
        # 注：根据DDD原则，我们移除了随机因素，假设突破总是成功
        # 实际应用中可以通过领域服务来处理突破的成功率
        self.change_cultivation_realm(self._cultivation_realm.next_realm)
        self.update_attributes(breakthroughs=self._attributes.breakthroughs + 1, successes=self._attributes.successes + 1)
        return True
    
    def get_cultivation_progress(self) -> float:
        """获取当前境界的修炼进度"""
        return self._cultivation_realm.get_realm_progress(self._current_exp.value)

    def learn_technique(self, technique: Dict) -> bool:
        """学习技能"""
        if not self._status.is_available():
            return False

        # 检查是否已经学习过该技能
        for t in self._techniques:
            if t['id'] == technique['id']:
                return False

        # 学习技能
        self._techniques.append(technique)
        self.update_attributes(techniques=self._attributes.techniques + 1)

        return True

    def fight(self, opponent: str) -> bool:
        """战斗"""
        if not self._status.is_available():
            return False

        # 更新状态为战斗中
        self.update_status(current_state=PlayerState.FIGHTING, is_fighting=True, current_enemy=opponent)

        # 计算战斗结果
        # 这里简化处理，实际应该有更复杂的战斗逻辑
        win = self._attributes.combat_power > 50  # 假设战斗力大于50则获胜

        # 更新属性
        self.update_attributes(battles=self._attributes.battles + 1)
        if win:
            self.update_attributes(wins=self._attributes.wins + 1, exp=self._attributes.exp + 50)
        else:
            self.update_attributes(losses=self._attributes.losses + 1, lifespan=self._attributes.lifespan - 1)

        # 更新状态为空闲
        self.update_status(current_state=PlayerState.IDLE, is_fighting=False, current_enemy=None)

        return win

    def add_item(self, item: Dict) -> None:
        """添加物品到背包"""
        self._inventory.append(item)

    def remove_item(self, item_id: str) -> bool:
        """从背包移除物品"""
        for i, item in enumerate(self._inventory):
            if item['id'] == item_id:
                self._inventory.pop(i)
                return True
        return False

    def add_friend(self, friend_id: str) -> bool:
        """添加好友"""
        if friend_id in self._friends:
            return False
        self._friends.add(friend_id)
        self.update_attributes(friends=self._attributes.friends + 1)
        return True

    def remove_friend(self, friend_id: str) -> bool:
        """移除好友"""
        if friend_id not in self._friends:
            return False
        self._friends.remove(friend_id)
        self.update_attributes(friends=self._attributes.friends - 1)
        return True

    def add_enemy(self, enemy_id: str) -> bool:
        """添加敌人"""
        if enemy_id in self._enemies:
            return False
        self._enemies.add(enemy_id)
        self.update_attributes(enemies=self._attributes.enemies + 1)
        return True

    def remove_enemy(self, enemy_id: str) -> bool:
        """移除敌人"""
        if enemy_id not in self._enemies:
            return False
        self._enemies.remove(enemy_id)
        self.update_attributes(enemies=self._attributes.enemies - 1)
        return True

    def add_quest(self, quest: Dict) -> None:
        """添加任务"""
        self._quests.append(quest)
        self.update_attributes(quests=self._attributes.quests + 1)

    def complete_quest(self, quest_id: str) -> bool:
        """完成任务"""
        for i, quest in enumerate(self._quests):
            if quest['id'] == quest_id:
                quest['completed'] = True
                self.update_attributes(exp=self._attributes.exp + quest.get('reward_exp', 0),
                                     money=self._attributes.money + quest.get('reward_money', 0))
                return True
        return False

    def add_achievement(self, achievement: Dict) -> None:
        """添加成就"""
        self._achievements.append(achievement)
        self.update_attributes(achievements=self._attributes.achievements + 1)

    def add_sect(self, sect: Dict) -> None:
        """添加门派"""
        self._sects.append(sect)
        self.update_attributes(sects=self._attributes.sects + 1)

    def add_cave(self, cave: Dict) -> None:
        """添加洞府"""
        self._caves.append(cave)
        self.update_attributes(caves=self._attributes.caves + 1)

    def add_pet(self, pet: Dict) -> None:
        """添加宠物"""
        self._pets.append(pet)
        self.update_attributes(pets=self._attributes.pets + 1)

    def add_memory(self, memory: Dict) -> None:
        """添加记忆"""
        self._memories.append(memory)
        self.update_attributes(memories=self._attributes.memories + 1)

    def add_event(self, event: Dict) -> None:
        """添加事件"""
        self._events.append(event)
        self.update_attributes(events=self._attributes.events + 1)

    def get_combat_power(self) -> int:
        """获取战斗力"""
        return self._attributes.calculate_combat_power()

    def is_alive(self) -> bool:
        """检查是否活着"""
        return self._attributes.is_alive()

    def has_enough_money(self, amount: int) -> bool:
        """检查是否有足够的金钱"""
        return self._attributes.has_enough_money(amount)

    def has_enough_exp(self, amount: int) -> bool:
        """检查是否有足够的经验值"""
        return self._attributes.has_enough_exp(amount)

    def has_enough_lifespan(self, years: int) -> bool:
        """检查是否有足够的寿元"""
        return self._attributes.has_enough_lifespan(years)

    def get_total_wealth(self) -> int:
        """获取总财富"""
        return self._attributes.get_total_wealth()



    def get_location_info(self) -> Dict[str, str]:
        """获取位置信息"""
        return self._status.get_location_info()

    def get_current_activity(self) -> str:
        """获取当前活动"""
        return self._status.get_current_activity()

    def is_available(self) -> bool:
        """检查是否可用"""
        return self._status.is_available()

    def is_busy(self) -> bool:
        """检查是否忙碌"""
        return self._status.is_busy()

    def is_in_danger(self) -> bool:
        """检查是否处于危险中"""
        return self._status.is_in_danger()

    def add_affliction(self, affliction: Affliction) -> None:
        """添加状态"""
        self._status = self._status.add_affliction(affliction)

    def remove_affliction(self, affliction_type: AfflictionType) -> None:
        """移除状态"""
        self._status = self._status.remove_affliction(affliction_type)

    def has_affliction(self, affliction_type: AfflictionType) -> bool:
        """检查是否有特定状态"""
        return self._status.has_affliction(affliction_type)

    def get_affliction_severity(self, affliction_type: AfflictionType) -> int:
        """获取状态严重程度"""
        return self._status.get_affliction_severity(affliction_type)
