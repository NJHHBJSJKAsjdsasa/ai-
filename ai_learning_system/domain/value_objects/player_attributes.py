from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class PlayerAttributes:
    """玩家属性值对象"""
    strength: int = 10  # 力量
    agility: int = 10   # 敏捷
    intelligence: int = 10  # 智力
    vitality: int = 10  # 体力
    spiritual_power: int = 0  # 灵力
    fortune: int = 0    # 福缘
    karma: int = 0      # 业力
    luck: int = 0       # 运气
    comprehension: int = 10  # 悟性
    willpower: int = 10  # 意志力
    charisma: int = 10  # 魅力
    reputation: int = 0  # 声望
    cultivation_speed: float = 1.0  # 修炼速度倍率
    breakthrough_rate: float = 1.0  # 突破成功率倍率
    pill_effect: float = 1.0  # 丹药效果倍率
    treasure_discovery: float = 1.0  # 寻宝倍率
    combat_power: int = 0  # 战斗力
    lifespan: int = 80  # 寿元
    exp: int = 0  # 经验值
    money: int = 100  # 金钱
    pills: int = 0  # 丹药数量
    materials: int = 0  # 材料数量
    weapons: int = 0  # 武器数量
    armor: int = 0  # 防具数量
    treasures: int = 0  # 珍宝数量
    techniques: int = 0  # 技能数量
    pets: int = 0  # 宠物数量
    friends: int = 0  # 好友数量
    enemies: int = 0  # 敌人数量
    quests: int = 0  # 任务数量
    achievements: int = 0  # 成就数量
    sects: int = 0  # 门派数量
    caves: int = 0  # 洞府数量
    worlds: int = 0  # 世界数量
    memories: int = 0  # 记忆数量
    events: int = 0  # 事件数量
    deaths: int = 0  # 死亡次数
    rebirths: int = 0  # 转世次数
    breakthroughs: int = 0  # 突破次数
    failures: int = 0  # 失败次数
    successes: int = 0  # 成功次数
    battles: int = 0  # 战斗次数
    wins: int = 0  # 胜利次数
    losses: int = 0  # 失败次数
    draws: int = 0  # 平局次数
    exploration: int = 0  # 探索次数
    discoveries: int = 0  # 发现次数
    alchemy: int = 0  # 炼丹次数
    refining: int = 0  # 炼器次数
    trading: int = 0  # 交易次数
    social: int = 0  # 社交次数
    meditation: int = 0  # 冥想次数
    cultivation: int = 0  # 修炼次数
    tribulation: int = 0  # 渡劫次数
    transcendence: int = 0  # 超越次数
    ascension: int = 0  # 飞升次数
    immortality: int = 0  # 成仙次数

    def update(self, **kwargs) -> 'PlayerAttributes':
        """更新属性并返回新的属性对象"""
        new_attributes = self.__dict__.copy()
        new_attributes.update(kwargs)
        return PlayerAttributes(**new_attributes)

    def calculate_combat_power(self) -> int:
        """计算战斗力"""
        base_power = self.strength * 2 + self.agility * 1.5 + self.intelligence * 1.8 + self.vitality * 1.2
        spiritual_bonus = self.spiritual_power * 3
        total_power = int(base_power + spiritual_bonus)
        return max(1, total_power)

    def has_enough_money(self, amount: int) -> bool:
        """检查是否有足够的金钱"""
        return self.money >= amount

    def has_enough_exp(self, amount: int) -> bool:
        """检查是否有足够的经验值"""
        return self.exp >= amount

    def has_enough_lifespan(self, years: int) -> bool:
        """检查是否有足够的寿元"""
        return self.lifespan >= years

    def is_alive(self) -> bool:
        """检查是否活着"""
        return self.lifespan > 0

    def get_total_achievements(self) -> int:
        """获取总成就数"""
        return self.achievements

    def get_total_wealth(self) -> int:
        """获取总财富"""
        return self.money + self.pills * 10 + self.materials * 5 + self.treasures * 100

    def get_cultivation_progress(self, realm_exp: int) -> float:
        """获取修炼进度"""
        if realm_exp <= 0:
            return 0.0
        return min(1.0, self.exp / realm_exp)
