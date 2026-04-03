"""
战斗系统核心模块
提供完整的回合制战斗机制，支持切磋和死斗两种模式
"""

from typing import Dict, List, Optional, Any, Tuple
from domain.entities.combat import CombatUnit
from domain.services.combat_service import CombatService
from domain.value_objects.combat import CombatMode, CombatStatus, CombatResult as DomainCombatResult, CombatSkill, DamageType


class CombatSystem:
    """战斗系统类"""
    
    def __init__(self):
        """初始化战斗系统"""
        self.combat_service = CombatService()
        self.player: Optional[CombatUnit] = None
        self.enemy: Optional[CombatUnit] = None
        self.mode: CombatMode = CombatMode.SPAR
        self.status: CombatStatus = CombatStatus.ONGOING
        self.turn: int = 0
        self.combat_log: List[str] = []
        self.current_turn_unit: Optional[CombatUnit] = None

        # 保存初始状态（用于切磋恢复）
        self._initial_player_health: int = 0
        self._initial_player_mana: int = 0
        self._initial_enemy_health: int = 0
        self._initial_enemy_mana: int = 0

        # 保存原始敌人NPC对象（用于死斗模式的处决功能）
        self._enemy_npc: Any = None
    
    def start_combat(self, player: CombatUnit, enemy: CombatUnit,
                     mode: CombatMode = CombatMode.SPAR, enemy_npc: Any = None) -> Any:
        """
        开始战斗

        Args:
            player: 玩家战斗单位
            enemy: 敌人战斗单位
            mode: 战斗模式
            enemy_npc: 原始敌人NPC对象（用于死斗模式的处决功能）

        Returns:
            战斗结果
        """
        self.player = player
        self.enemy = enemy
        self.mode = mode
        self.status = CombatStatus.ONGOING
        self.turn = 0
        self.combat_log = []

        # 保存原始敌人NPC对象（用于死斗模式的处决功能）
        self._enemy_npc = enemy_npc

        # 保存初始状态
        self._initial_player_health = player.health
        self._initial_player_mana = player.mana
        self._initial_enemy_health = enemy.health
        self._initial_enemy_mana = enemy.mana
        
        # 调用领域服务开始战斗
        domain_result, self.player, self.enemy = self.combat_service.start_combat(
            player, enemy, mode, getattr(enemy_npc, 'id', None)
        )
        
        # 更新战斗日志
        self.combat_log = domain_result.combat_log
        
        # 确定先手
        if player.speed > enemy.speed:
            self.current_turn_unit = player
        elif enemy.speed > player.speed:
            self.current_turn_unit = enemy
        else:
            import random
            self.current_turn_unit = random.choice([player, enemy])
        
        # 转换为兼容的战斗结果
        return self._convert_to_compatible_result(domain_result)
    
    def execute_turn(self, action: str, skill_name: Optional[str] = None) -> Any:
        """
        执行一个战斗回合
        
        Args:
            action: 行动类型 ("attack", "skill", "flee", "defend")
            skill_name: 技能名称（如果使用技能）
            
        Returns:
            战斗结果
        """
        if self.status != CombatStatus.ONGOING:
            return self._create_compatible_result()
        
        self.turn += 1
        
        # 调用领域服务执行回合
        domain_result, self.player, self.enemy = self.combat_service.execute_turn(
            self.player, self.enemy, action, skill_name, self.mode
        )
        
        # 更新战斗日志
        self.combat_log.extend(domain_result.combat_log)
        
        # 更新状态
        self.status = domain_result.status
        
        # 检查战斗结束
        if self.status != CombatStatus.ONGOING:
            return self.end_combat()
        
        return self._convert_to_compatible_result(domain_result)
    
    def end_combat(self) -> Any:
        """结束战斗"""
        if self.status == CombatStatus.ONGOING:
            # 检查战斗状态
            if self.mode == CombatMode.SPAR:
                if self.player.health <= 1:
                    self.status = CombatStatus.ENEMY_WIN
                elif self.enemy.health <= 1:
                    self.status = CombatStatus.PLAYER_WIN
            else:
                if self.player.health <= 0:
                    self.status = CombatStatus.ENEMY_WIN
                elif self.enemy.health <= 0:
                    self.status = CombatStatus.PLAYER_WIN

        self.combat_log.append("\n=== 战斗结束 ===")

        if self.status == CombatStatus.PLAYER_WIN:
            self.combat_log.append(f"{self.player.name} 获得胜利！")
        elif self.status == CombatStatus.ENEMY_WIN:
            self.combat_log.append(f"{self.enemy.name} 获得胜利！")
        elif self.status == CombatStatus.FLED:
            self.combat_log.append("战斗以逃跑结束")
        elif self.status == CombatStatus.DRAW:
            self.combat_log.append("战斗平局")

        # 计算奖励
        result = self._create_compatible_result()

        # 切磋模式：恢复状态
        if self.mode == CombatMode.SPAR:
            self._restore_initial_state()
            self.combat_log.append("切磋结束，双方状态已恢复")

        # 死斗模式且玩家胜利：检查是否触发处决流程
        if (self.mode == CombatMode.DEATHMATCH and
            self.status == CombatStatus.PLAYER_WIN and
            self.enemy and
            self.enemy.unit_type == "npc"):
            result.execution_pending = True
            result.can_execute = True
            result.enemy_npc = self._enemy_npc
            self.combat_log.append(f"{self.enemy.name} 已战败，等待处决决定...")

        return result
    
    def _restore_initial_state(self):
        """恢复初始状态（切磋模式）"""
        if self.player:
            self.player.health = self._initial_player_health
            self.player.mana = self._initial_player_mana
        if self.enemy:
            self.enemy.health = self._initial_enemy_health
            self.enemy.mana = self._initial_enemy_mana
    
    def _create_compatible_result(self) -> Any:
        """创建兼容的战斗结果"""
        # 模拟旧的CombatResult结构
        class CompatibleCombatResult:
            def __init__(self):
                self.status = self.status
                self.winner = self.player if self.status == CombatStatus.PLAYER_WIN else self.enemy
                self.loser = self.enemy if self.status == CombatStatus.PLAYER_WIN else self.player
                self.exp_reward = 0
                self.spirit_stones_reward = 0
                self.loot = []
                self.combat_log = self.combat_log.copy()
                self.turns = self.turn
                self.mode = self.mode
                self.execution_pending = False
                self.can_execute = False
                self.enemy_npc = None
        
        return CompatibleCombatResult()
    
    def _convert_to_compatible_result(self, domain_result: DomainCombatResult) -> Any:
        """将领域战斗结果转换为兼容格式"""
        # 模拟旧的CombatResult结构
        class CompatibleCombatResult:
            def __init__(self):
                self.status = domain_result.status
                self.winner = self.player if domain_result.status == CombatStatus.PLAYER_WIN else self.enemy
                self.loser = self.enemy if domain_result.status == CombatStatus.PLAYER_WIN else self.player
                self.exp_reward = domain_result.exp_reward
                self.spirit_stones_reward = domain_result.spirit_stones_reward
                self.loot = domain_result.loot
                self.combat_log = domain_result.combat_log
                self.turns = domain_result.turns
                self.mode = domain_result.mode
                self.execution_pending = domain_result.execution_pending
                self.can_execute = domain_result.can_execute
                self.enemy_npc = self._enemy_npc
        
        return CompatibleCombatResult()
    
    def get_combat_status_text(self) -> str:
        """获取战斗状态文本"""
        if not self.player or not self.enemy:
            return "战斗未开始"
        
        return self.combat_service.get_combat_status_text(self.player, self.enemy, self.turn)
    
    def get_available_actions(self) -> List[str]:
        """获取可用行动列表"""
        if not self.player:
            return []
        return self.combat_service.get_available_actions(self.player)


def create_player_combat_unit(player) -> CombatUnit:
    """
    从玩家对象创建战斗单位
    
    Args:
        player: Player对象
        
    Returns:
        CombatUnit
    """
    # 计算战斗属性（确保是整数）
    from config import REALM_NAME_TO_LEVEL
    
    if isinstance(player.stats.realm_level, str):
        realm_level = REALM_NAME_TO_LEVEL.get(player.stats.realm_level, 0)
        if realm_level == 0 and player.stats.realm_level.isdigit():
            realm_level = int(player.stats.realm_level)
    else:
        realm_level = int(player.stats.realm_level)
    
    realm_layer = int(player.stats.realm_layer) if isinstance(player.stats.realm_layer, str) else player.stats.realm_layer
    realm_bonus = realm_level * 10
    
    unit = CombatUnit(
        id=getattr(player, 'id', 'player_1'),
        name=player.stats.name,
        unit_type="player",
        level=realm_level * 9 + realm_layer,
        health=player.stats.health,
        max_health=player.stats.max_health,
        mana=player.stats.spiritual_power,
        max_mana=player.stats.max_spiritual_power,
        attack=20 + realm_bonus + getattr(player.stats, 'attack', 0),
        defense=10 + realm_bonus // 2 + getattr(player.stats, 'defense', 0),
        speed=10 + getattr(player.stats, 'speed', 0),
        crit_rate=getattr(player.stats, 'crit_rate', 0.05),
        dodge_rate=getattr(player.stats, 'dodge_rate', 0.05),
    )
    
    # 添加功法技能
    for tech_name in player.techniques.learned_techniques.keys():
        from config.techniques import get_technique
        technique = get_technique(tech_name)
        if technique and getattr(technique, 'is_combat_skill', False):
            skill = CombatSkill(
                name=technique.name,
                description=technique.description,
                damage=int(technique.combat_power_bonus * 50),
                damage_type=getattr(technique, 'damage_type', DamageType.PHYSICAL),
                mana_cost=getattr(technique, 'mana_cost', 10),
                cooldown=getattr(technique, 'cooldown', 0),
            )
            unit.skills.append(skill)
    
    return unit


def create_npc_combat_unit(npc) -> CombatUnit:
    """
    从NPC对象创建战斗单位
    
    Args:
        npc: NPC对象
        
    Returns:
        CombatUnit
    """
    # 处理realm_level，可能是数字或境界名称
    from config import REALM_NAME_TO_LEVEL
    if isinstance(npc.data.realm_level, str):
        # 尝试从境界名称获取等级
        realm_level = REALM_NAME_TO_LEVEL.get(npc.data.realm_level, 0)
        if realm_level == 0 and npc.data.realm_level.isdigit():
            realm_level = int(npc.data.realm_level)
    else:
        realm_level = int(npc.data.realm_level)
    
    realm_bonus = realm_level * 10
    
    unit = CombatUnit(
        id=getattr(npc, 'id', f'npc_{hash(npc.data.dao_name)}'),
        name=npc.data.dao_name,
        unit_type="npc",
        level=realm_level * 9 + 5,
        health=100 + realm_bonus * 10,
        max_health=100 + realm_bonus * 10,
        mana=50 + realm_bonus * 5,
        max_mana=50 + realm_bonus * 5,
        attack=15 + realm_bonus,
        defense=8 + realm_bonus // 2,
        speed=15,
        crit_rate=0.03 + realm_level * 0.01,
        dodge_rate=0.03 + realm_level * 0.01,
    )
    
    # NPC根据门派添加技能
    if npc.data.sect_specialty == "剑道":
        unit.skills.append(CombatSkill(
            name="剑气斩",
            damage=30 + realm_bonus,
            damage_type=DamageType.PHYSICAL,
            mana_cost=15,
            cooldown=2,
        ))
    elif npc.data.sect_specialty == "炼丹术":
        unit.skills.append(CombatSkill(
            name="毒雾",
            damage=20 + realm_bonus,
            damage_type=DamageType.MAGIC,
            mana_cost=10,
            cooldown=1,
        ))
    
    return unit


def create_beast_combat_unit(beast_data: Dict[str, Any]) -> CombatUnit:
    """
    从妖兽数据创建战斗单位
    
    Args:
        beast_data: 妖兽数据字典
        
    Returns:
        CombatUnit
    """
    level = beast_data.get("level", 1)
    realm_level = beast_data.get("realm_level", 0)
    
    unit = CombatUnit(
        id=beast_data.get("id", f'beast_{hash(beast_data.get("name", "unknown"))}'),
        name=beast_data.get("name", "未知妖兽"),
        unit_type="beast",
        level=level,
        health=beast_data.get("health", 80 + level * 20),
        max_health=beast_data.get("health", 80 + level * 20),
        mana=beast_data.get("mana", 30 + level * 5),
        max_mana=beast_data.get("mana", 30 + level * 5),
        attack=beast_data.get("attack", 12 + level * 3),
        defense=beast_data.get("defense", 5 + level * 2),
        speed=beast_data.get("speed", 5 + level * 2),
        crit_rate=beast_data.get("crit_rate", 0.05),
        dodge_rate=beast_data.get("dodge_rate", 0.03),
    )
    
    # 添加妖兽技能
    skills_data = beast_data.get("skills", [])
    for skill_data in skills_data:
        skill = CombatSkill(
            name=skill_data.get("name", "攻击"),
            damage=skill_data.get("damage", 20),
            damage_type=DamageType(skill_data.get("damage_type", "PHYSICAL")),
            mana_cost=skill_data.get("mana_cost", 0),
            cooldown=skill_data.get("cooldown", 0),
        )
        unit.skills.append(skill)
    
    return unit
