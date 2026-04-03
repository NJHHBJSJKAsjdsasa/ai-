"""
NPC之间战斗系统模块
管理NPC之间的切磋、死斗以及NPC与妖兽的战斗
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.combat import (
    CombatSystem, CombatMode, CombatUnit,
    create_npc_combat_unit, create_beast_combat_unit
)
from domain.value_objects.combat import CombatResult
from game.execution_system import ExecutionChoice, execution_system
from game.death_manager import death_manager


@dataclass
class NPCCombatRecord:
    """NPC战斗记录"""
    opponent_id: str
    opponent_name: str
    mode: CombatMode
    result: str  # "win", "loss", "draw"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NPCCombatStats:
    """NPC战斗统计"""
    wins: int = 0
    losses: int = 0
    draws: int = 0
    spar_count: int = 0
    deathmatch_count: int = 0
    history: List[NPCCombatRecord] = field(default_factory=list)


class NPCCombatManager:
    """NPC战斗管理器"""
    
    # 门派关系表（影响死斗概率）
    SECT_RELATIONS = {
        ("青云门", "魔教"): "hostile",
        ("魔教", "青云门"): "hostile",
        ("天音寺", "魔教"): "hostile",
        ("魔教", "天音寺"): "hostile",
        ("青云门", "天音寺"): "friendly",
        ("天音寺", "青云门"): "friendly",
    }
    
    def __init__(self):
        """初始化NPC战斗管理器"""
        self.npc_stats: Dict[str, NPCCombatStats] = {}
        self.active_combats: Dict[str, CombatSystem] = {}
        self.combat_logs: List[Dict[str, Any]] = []
    
    def get_npc_combat_stats(self, npc_id: str) -> NPCCombatStats:
        """获取NPC战斗统计"""
        if npc_id not in self.npc_stats:
            self.npc_stats[npc_id] = NPCCombatStats()
        return self.npc_stats[npc_id]
    
    def _should_execute_npc(self, npc_winner, npc_loser) -> bool:
        """
        判断NPC是否应该处决战败的对手
        
        根据NPC的性格、道德值以及与对方的关系来决定是否处决
        
        Args:
            npc_winner: 胜利的NPC
            npc_loser: 战败的NPC
            
        Returns:
            bool: 是否处决
        """
        # 基础处决概率
        base_chance = 0.3
        
        # 获取胜者性格
        winner_personality = getattr(npc_winner.data, 'personality', '中立')
        winner_morality = getattr(npc_winner.data, 'morality', 0)
        
        # 根据性格调整处决概率
        # 邪恶性格更容易处决
        evil_personalities = ['阴险', '冷酷', '残忍', '嗜血', '狡诈', '恶毒']
        # 善良性格不容易处决
        good_personalities = ['善良', '仁慈', '慈悲', '宽厚', '温和', '正直']
        # 暴躁性格容易处决
        aggressive_personalities = ['暴躁', '凶狠', '霸道', '傲慢']
        
        if winner_personality in evil_personalities:
            base_chance += 0.4  # 邪恶NPC高概率处决
        elif winner_personality in aggressive_personalities:
            base_chance += 0.2  # 暴躁NPC较高概率处决
        elif winner_personality in good_personalities:
            base_chance -= 0.25  # 善良NPC低概率处决
        
        # 根据道德值调整（-100到100）
        if winner_morality < 0:
            # 道德值越低，处决概率越高
            morality_modifier = abs(winner_morality) / 200  # 最高增加0.5
            base_chance += morality_modifier
        else:
            # 道德值越高，处决概率越低
            morality_modifier = winner_morality / 200  # 最高减少0.5
            base_chance -= morality_modifier
        
        # 考虑双方关系（好感度）
        relationship = npc_winner.independent.get_relationship(npc_loser.data.id)
        affinity = relationship.get('affinity', 0)
        
        # 关系越好越不容易处决
        if affinity > 50:
            base_chance -= 0.3  # 好友关系大幅降低处决概率
        elif affinity > 20:
            base_chance -= 0.15  # 友好关系降低处决概率
        elif affinity < -50:
            base_chance += 0.2  # 仇敌关系增加处决概率
        elif affinity < -20:
            base_chance += 0.1  # 恶劣关系略微增加处决概率
        
        # 考虑败者的道德值
        loser_morality = getattr(npc_loser.data, 'morality', 0)
        if loser_morality < -50:
            # 处决大恶之人，正义NPC可能更倾向于处决
            if winner_morality > 0:
                base_chance += 0.15  # 正义NPC更可能处决恶人
        elif loser_morality > 50:
            # 处决大善之人，降低处决概率（除非胜者极恶）
            base_chance -= 0.2
        
        # 确保概率在合理范围内
        final_chance = max(0.05, min(0.95, base_chance))
        
        return random.random() < final_chance
    
    def execute_npc_vs_npc(self, winner, loser) -> bool:
        """
        执行NPC之间的处决
        
        胜者处决败者，获得败者全部物品，并添加相关记忆
        
        Args:
            winner: 胜利的NPC
            loser: 战败的NPC（将被处决）
            
        Returns:
            bool: 处决是否成功执行
        """
        try:
            # 使用death_manager标记NPC死亡
            death_record = death_manager.mark_npc_dead(
                npc=loser,
                killer_name=winner.data.dao_name,
                reason=f"被{winner.data.dao_name}在死斗中处决"
            )
            
            # 胜者获得败者的全部物品
            loot_items = []
            if hasattr(loser.data, 'inventory') and loser.data.inventory:
                for item in loser.data.inventory:
                    if hasattr(winner.data, 'inventory'):
                        winner.data.inventory.append(item)
                    loot_items.append(str(item))
            
            # 胜者获得败者的灵石
            if hasattr(loser.data, 'spirit_stones') and hasattr(winner.data, 'spirit_stones'):
                stolen_stones = loser.data.spirit_stones
                winner.data.spirit_stones += stolen_stones
                if stolen_stones > 0:
                    loot_items.append(f"{stolen_stones}灵石")
                loser.data.spirit_stones = 0
            
            # 添加胜者的记忆（处决对手）
            winner.independent.add_memory(
                f"在死斗中处决了{loser.data.dao_name}，获得了对方的全部物品",
                importance=10,
                emotion="negative" if getattr(winner.data, 'morality', 0) > 0 else "positive"
            )
            
            # 添加败者的记忆（被处决）
            loser.independent.add_memory(
                f"被{winner.data.dao_name}在死斗中处决",
                importance=10,
                emotion="negative"
            )
            
            return True
            
        except Exception as e:
            # 处决过程出错，记录错误
            print(f"NPC处决过程出错: {e}")
            return False
    
    def execute_npc_vs_player(self, npc, player, combat_result) -> bool:
        """
        NPC处决战败的玩家
        
        当NPC战胜玩家后，根据NPC性格决定是否处决玩家
        
        Args:
            npc: 胜利的NPC
            player: 战败的玩家
            combat_result: 战斗结果
            
        Returns:
            bool: 是否执行了处决
        """
        # 获取NPC性格
        npc_personality = getattr(npc.data, 'personality', '中立')
        npc_morality = getattr(npc.data, 'morality', 0)
        
        # 基础处决概率
        base_chance = 0.2
        
        # 邪恶NPC高概率处决玩家
        evil_personalities = ['阴险', '冷酷', '残忍', '嗜血', '狡诈', '恶毒']
        aggressive_personalities = ['暴躁', '凶狠', '霸道', '傲慢']
        good_personalities = ['善良', '仁慈', '慈悲', '宽厚', '温和', '正直']
        
        if npc_personality in evil_personalities:
            base_chance += 0.5  # 邪恶NPC极高概率处决玩家
        elif npc_personality in aggressive_personalities:
            base_chance += 0.3  # 暴躁NPC较高概率处决玩家
        elif npc_personality in good_personalities:
            base_chance -= 0.3  # 善良NPC低概率处决玩家
        
        # 根据道德值调整
        if npc_morality < 0:
            base_chance += abs(npc_morality) / 150  # 最高增加约0.67
        else:
            base_chance -= npc_morality / 150  # 最高减少约0.67
        
        # 考虑玩家与NPC的关系
        relationship = npc.independent.get_relationship(player.stats.id if hasattr(player.stats, 'id') else 'player')
        affinity = relationship.get('affinity', 0)
        
        if affinity > 30:
            base_chance -= 0.25  # 友好关系降低处决概率
        elif affinity < -30:
            base_chance += 0.2  # 敌对关系增加处决概率
        
        # 确保概率在合理范围内
        final_chance = max(0.05, min(0.95, base_chance))
        
        # 决定是否处决
        should_execute = random.random() < final_chance
        
        if should_execute:
            # 调用execution_system执行NPC处决玩家
            # 注意：这里使用execution_system.execute_npc的逻辑，但角色互换
            # 实际上应该有一个专门处理NPC处决玩家的方法
            # 这里我们手动处理玩家死亡逻辑
            
            # 标记玩家死亡（如果游戏支持玩家死亡机制）
            if hasattr(player, 'is_alive'):
                player.is_alive = False
            
            # 添加NPC记忆（处决玩家）
            npc.independent.add_memory(
                f"处决了玩家{player.stats.name}",
                importance=9,
                emotion="positive" if npc_morality < 0 else "negative"
            )
            
            # NPC获得玩家的物品
            if hasattr(player, 'inventory') and player.inventory:
                for item in player.inventory:
                    if hasattr(npc.data, 'inventory'):
                        npc.data.inventory.append(item)
            
            # NPC获得玩家的灵石
            if hasattr(player.stats, 'spirit_stones') and hasattr(npc.data, 'spirit_stones'):
                stolen_stones = player.stats.spirit_stones
                npc.data.spirit_stones += stolen_stones
                player.stats.spirit_stones = 0
            
            return True
        
        return False
    
    def _should_execute_player(self, npc) -> bool:
        """
        判断NPC是否应该处决玩家（辅助方法）
        
        用于NPC战胜玩家后的处决决策
        
        Args:
            npc: 胜利的NPC
            
        Returns:
            bool: 是否处决
        """
        npc_personality = getattr(npc.data, 'personality', '中立')
        npc_morality = getattr(npc.data, 'morality', 0)
        
        # 基础处决概率
        base_chance = 0.2
        
        # 邪恶NPC高概率处决
        evil_personalities = ['阴险', '冷酷', '残忍', '嗜血', '狡诈', '恶毒']
        aggressive_personalities = ['暴躁', '凶狠', '霸道', '傲慢']
        good_personalities = ['善良', '仁慈', '慈悲', '宽厚', '温和', '正直']
        
        if npc_personality in evil_personalities:
            base_chance += 0.5
        elif npc_personality in aggressive_personalities:
            base_chance += 0.3
        elif npc_personality in good_personalities:
            base_chance -= 0.3
        
        # 道德值影响
        if npc_morality < 0:
            base_chance += abs(npc_morality) / 150
        else:
            base_chance -= npc_morality / 150
        
        return random.random() < max(0.05, min(0.95, base_chance))
    
    def check_spar_opportunity(self, npc1, npc2) -> bool:
        """
        检查是否有切磋机会
        
        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC
            
        Returns:
            是否触发切磋
        """
        # 必须在同一地点
        if npc1.data.location != npc2.data.location:
            return False
        
        # 检查关系
        relationship = npc1.independent.get_relationship(npc2.data.id)
        affinity = relationship.get("affinity", 0)
        
        # 关系良好才切磋
        if affinity < 20:
            return False
        
        # 基础概率
        base_chance = 0.1
        
        # 性格影响
        friendly_personalities = ["开朗", "豪爽", "热心", "正直"]
        if npc1.data.personality in friendly_personalities:
            base_chance += 0.1
        if npc2.data.personality in friendly_personalities:
            base_chance += 0.1
        
        # 境界相近更容易切磋
        realm_diff = abs(npc1.data.realm_level - npc2.data.realm_level)
        if realm_diff == 0:
            base_chance += 0.1
        elif realm_diff > 2:
            base_chance -= 0.1
        
        return random.random() < max(0.05, min(0.5, base_chance))
    
    def check_deathmatch_opportunity(self, npc1, npc2) -> bool:
        """
        检查是否有死斗机会
        
        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC
            
        Returns:
            是否触发死斗
        """
        # 必须在同一地点
        if npc1.data.location != npc2.data.location:
            return False
        
        # 检查关系
        relationship = npc1.independent.get_relationship(npc2.data.id)
        affinity = relationship.get("affinity", 0)
        
        # 关系极差才会死斗
        if affinity > -50:
            return False
        
        # 基础概率
        base_chance = 0.05
        
        # 性格影响
        aggressive_personalities = ["暴躁", "阴险", "冷酷", "傲慢"]
        if npc1.data.personality in aggressive_personalities:
            base_chance += 0.1
        if npc2.data.personality in aggressive_personalities:
            base_chance += 0.1
        
        # 门派敌对关系
        sect_relation = self.SECT_RELATIONS.get((npc1.data.sect, npc2.data.sect))
        if sect_relation == "hostile":
            base_chance += 0.2
        
        return random.random() < max(0.02, min(0.5, base_chance))
    
    def execute_npc_spar(self, npc1, npc2) -> Optional[CombatResult]:
        """
        执行NPC之间的切磋
        
        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC
            
        Returns:
            战斗结果
        """
        # 创建战斗单位
        unit1 = create_npc_combat_unit(npc1)
        unit2 = create_npc_combat_unit(npc2)
        
        # 创建战斗系统
        combat = CombatSystem()
        combat.start_combat(unit1, unit2, CombatMode.SPAR)
        
        # 自动执行战斗（最多50回合）
        max_turns = 50
        for _ in range(max_turns):
            if combat.status != combat.status.ONGOING:
                break
            
            # NPC AI自动选择行动
            current_unit = combat.current_turn_unit
            if current_unit == unit1:
                action = self._choose_npc_action(unit1, unit2, CombatMode.SPAR)
                skill_name = None
                if action == "skill" and unit1.get_available_skills():
                    skill = random.choice(unit1.get_available_skills())
                    skill_name = skill.name
                combat.execute_turn(action, skill_name)
            else:
                action = self._choose_npc_action(unit2, unit1, CombatMode.SPAR)
                skill_name = None
                if action == "skill" and unit2.get_available_skills():
                    skill = random.choice(unit2.get_available_skills())
                    skill_name = skill.name
                combat.execute_turn(action, skill_name)
        
        # 获取结果
        result = combat.end_combat()
        
        # 记录战斗
        self._record_combat(npc1, npc2, result)
        
        # 更新统计
        self._update_stats(npc1, npc2, result)
        
        # 添加记忆
        self._add_combat_memories(npc1, npc2, result, CombatMode.SPAR)
        
        return result
    
    def execute_npc_deathmatch(self, npc1, npc2) -> Optional[CombatResult]:
        """
        执行NPC之间的死斗
        
        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC
            
        Returns:
            战斗结果
        """
        # 创建战斗单位
        unit1 = create_npc_combat_unit(npc1)
        unit2 = create_npc_combat_unit(npc2)
        
        # 创建战斗系统
        combat = CombatSystem()
        combat.start_combat(unit1, unit2, CombatMode.DEATHMATCH)
        
        # 自动执行战斗（最多100回合）
        max_turns = 100
        for _ in range(max_turns):
            if combat.status != combat.status.ONGOING:
                break
            
            # NPC AI自动选择行动（死斗模式下更激进）
            current_unit = combat.current_turn_unit
            if current_unit == unit1:
                action = self._choose_npc_action(unit1, unit2, CombatMode.DEATHMATCH)
                skill_name = None
                if action == "skill" and unit1.get_available_skills():
                    # 死斗模式下优先使用高伤害技能
                    best_skill = max(unit1.get_available_skills(), key=lambda s: s.damage)
                    skill_name = best_skill.name
                combat.execute_turn(action, skill_name)
            else:
                action = self._choose_npc_action(unit2, unit1, CombatMode.DEATHMATCH)
                skill_name = None
                if action == "skill" and unit2.get_available_skills():
                    best_skill = max(unit2.get_available_skills(), key=lambda s: s.damage)
                    skill_name = best_skill.name
                combat.execute_turn(action, skill_name)
        
        # 获取结果
        result = combat.end_combat()
        
        # 记录战斗
        self._record_combat(npc1, npc2, result)
        
        # 更新统计
        self._update_stats(npc1, npc2, result)
        
        # 处理死斗后果（包含处决逻辑）
        self._handle_deathmatch_consequences(npc1, npc2, result)
        
        # 添加记忆
        self._add_combat_memories(npc1, npc2, result, CombatMode.DEATHMATCH)
        
        return result
    
    def execute_npc_vs_beast(self, npc, beast_data: Dict[str, Any]) -> Optional[CombatResult]:
        """
        执行NPC与妖兽的战斗
        
        Args:
            npc: NPC对象
            beast_data: 妖兽数据
            
        Returns:
            战斗结果
        """
        # 创建战斗单位
        npc_unit = create_npc_combat_unit(npc)
        beast_unit = create_beast_combat_unit(beast_data)
        
        # 创建战斗系统
        combat = CombatSystem()
        combat.start_combat(npc_unit, beast_unit, CombatMode.DEATHMATCH)
        
        # 自动执行战斗
        max_turns = 100
        for _ in range(max_turns):
            if combat.status != combat.status.ONGOING:
                break
            
            current_unit = combat.current_turn_unit
            if current_unit == npc_unit:
                action = self._choose_npc_action(npc_unit, beast_unit, CombatMode.DEATHMATCH)
                skill_name = None
                if action == "skill" and npc_unit.get_available_skills():
                    best_skill = max(npc_unit.get_available_skills(), key=lambda s: s.damage)
                    skill_name = best_skill.name
                combat.execute_turn(action, skill_name)
            else:
                # 妖兽AI
                action = self._choose_beast_action(beast_unit, npc_unit)
                combat.execute_turn(action)
        
        # 获取结果
        result = combat.end_combat()
        
        # 记录战斗
        self._record_npc_beast_combat(npc, beast_data, result)
        
        # 如果NPC胜利，获得奖励
        if result.status.value == "玩家胜利":  # NPC作为"玩家"
            self._grant_npc_rewards(npc, result)
        
        return result
    
    def _choose_npc_action(self, npc_unit: CombatUnit, 
                          target: CombatUnit, 
                          mode: CombatMode) -> str:
        """
        NPC选择行动
        
        Args:
            npc_unit: NPC战斗单位
            target: 目标
            mode: 战斗模式
            
        Returns:
            行动类型
        """
        # 生命值低时的策略
        health_percent = npc_unit.health / npc_unit.max_health
        
        # 死斗模式下不逃跑
        if mode == CombatMode.SPAR and health_percent < 0.2:
            if random.random() < 0.3:
                return "flee"
        
        # 有可用技能时优先使用
        available_skills = npc_unit.get_available_skills()
        if available_skills and random.random() < 0.6:
            return "skill"
        
        # 生命值低时可能防御
        if health_percent < 0.3 and random.random() < 0.3:
            return "defend"
        
        # 默认攻击
        return "attack"
    
    def _choose_beast_action(self, beast_unit: CombatUnit, target: CombatUnit) -> str:
        """妖兽选择行动"""
        # 妖兽更简单，主要攻击
        available_skills = beast_unit.get_available_skills()
        if available_skills and random.random() < 0.5:
            return "skill"
        return "attack"
    
    def _record_combat(self, npc1, npc2, result: CombatResult):
        """记录NPC之间的战斗"""
        log_entry = {
            "type": "npc_vs_npc",
            "npc1_id": npc1.data.id,
            "npc1_name": npc1.data.dao_name,
            "npc2_id": npc2.data.id,
            "npc2_name": npc2.data.dao_name,
            "mode": result.mode.value,
            "winner": result.winner.name if result.winner else None,
            "turns": result.turns,
            "timestamp": datetime.now(),
        }
        self.combat_logs.append(log_entry)
    
    def _record_npc_beast_combat(self, npc, beast_data: Dict[str, Any], result: CombatResult):
        """记录NPC与妖兽的战斗"""
        log_entry = {
            "type": "npc_vs_beast",
            "npc_id": npc.data.id,
            "npc_name": npc.data.dao_name,
            "beast_name": beast_data.get("name", "未知妖兽"),
            "winner": result.winner.name if result.winner else None,
            "turns": result.turns,
            "timestamp": datetime.now(),
        }
        self.combat_logs.append(log_entry)
    
    def _update_stats(self, npc1, npc2, result: CombatResult):
        """更新NPC战斗统计"""
        stats1 = self.get_npc_combat_stats(npc1.data.id)
        stats2 = self.get_npc_combat_stats(npc2.data.id)
        
        if result.mode == CombatMode.SPAR:
            stats1.spar_count += 1
            stats2.spar_count += 1
        else:
            stats1.deathmatch_count += 1
            stats2.deathmatch_count += 1
        
        # 确定胜负
        if result.winner:
            if result.winner.name == npc1.data.dao_name:
                stats1.wins += 1
                stats2.losses += 1
                
                record1 = NPCCombatRecord(
                    opponent_id=npc2.data.id,
                    opponent_name=npc2.data.dao_name,
                    mode=result.mode,
                    result="win"
                )
                record2 = NPCCombatRecord(
                    opponent_id=npc1.data.id,
                    opponent_name=npc1.data.dao_name,
                    mode=result.mode,
                    result="loss"
                )
            else:
                stats2.wins += 1
                stats1.losses += 1
                
                record1 = NPCCombatRecord(
                    opponent_id=npc2.data.id,
                    opponent_name=npc2.data.dao_name,
                    mode=result.mode,
                    result="loss"
                )
                record2 = NPCCombatRecord(
                    opponent_id=npc1.data.id,
                    opponent_name=npc1.data.dao_name,
                    mode=result.mode,
                    result="win"
                )
            
            stats1.history.append(record1)
            stats2.history.append(record2)
        else:
            # 平局或逃跑
            stats1.draws += 1
            stats2.draws += 1
    
    def _handle_deathmatch_consequences(self, npc1, npc2, result: CombatResult):
        """
        处理死斗后果
        
        根据战斗结果处理胜者和败者的后果，包括处决判断、物品获取等
        """
        if result.status.value == "玩家胜利":
            winner = npc1 if result.winner.name == npc1.data.dao_name else npc2
            loser = npc2 if winner == npc1 else npc1
            
            # 判断是否处决战败者
            should_execute = self._should_execute_npc(winner, loser)
            
            if should_execute:
                # 执行处决
                execution_success = self.execute_npc_vs_npc(winner, loser)
                
                if execution_success:
                    # 处决成功，记录战斗日志
                    log_entry = {
                        "type": "npc_execution",
                        "winner_id": winner.data.id,
                        "winner_name": winner.data.dao_name,
                        "loser_id": loser.data.id,
                        "loser_name": loser.data.dao_name,
                        "reason": "死斗胜利后处决",
                        "timestamp": datetime.now(),
                    }
                    self.combat_logs.append(log_entry)
            else:
                # 胜者选择饶恕败者
                winner.independent.add_memory(
                    f"在死斗中战胜了{loser.data.dao_name}，但选择饶恕对方一命",
                    importance=8,
                    emotion="positive" if getattr(winner.data, 'morality', 0) > 0 else "neutral"
                )
                loser.independent.add_memory(
                    f"被{winner.data.dao_name}在死斗中击败，但对方饶恕了自己",
                    importance=8,
                    emotion="positive"
                )
                
                # 饶恕后，败者对胜者好感度略有提升
                if hasattr(loser.independent, 'update_relationship'):
                    loser.independent.update_relationship(winner.data.id, affinity=10)
            
            # 胜者获得败者的物品（无论是否处决，胜者都能获得战利品）
            if result.loot:
                for item in result.loot:
                    winner.independent.add_memory(
                        f"从{loser.data.dao_name}处获得了{item}",
                        importance=5
                    )
    
    def _add_combat_memories(self, npc1, npc2, result: CombatResult, mode: CombatMode):
        """添加战斗记忆"""
        mode_str = "切磋" if mode == CombatMode.SPAR else "死斗"
        
        if result.winner:
            if result.winner.name == npc1.data.dao_name:
                npc1.independent.add_memory(
                    f"与{npc2.data.dao_name}进行{mode_str}并获胜",
                    importance=6 if mode == CombatMode.SPAR else 9
                )
                npc2.independent.add_memory(
                    f"与{npc1.data.dao_name}进行{mode_str}并落败",
                    importance=5 if mode == CombatMode.SPAR else 8
                )
            else:
                npc2.independent.add_memory(
                    f"与{npc1.data.dao_name}进行{mode_str}并获胜",
                    importance=6 if mode == CombatMode.SPAR else 9
                )
                npc1.independent.add_memory(
                    f"与{npc2.data.dao_name}进行{mode_str}并落败",
                    importance=5 if mode == CombatMode.SPAR else 8
                )
        else:
            # 平局
            npc1.independent.add_memory(
                f"与{npc2.data.dao_name}进行{mode_str}，结果平局",
                importance=5
            )
            npc2.independent.add_memory(
                f"与{npc1.data.dao_name}进行{mode_str}，结果平局",
                importance=5
            )
    
    def _grant_npc_rewards(self, npc, result: CombatResult):
        """给予NPC战斗奖励"""
        # 增加经验（简化处理，实际应该修改NPC数据结构）
        exp_gain = result.exp_reward
        
        # 记录获得奖励
        if result.loot:
            for item in result.loot:
                npc.independent.add_memory(
                    f"从妖兽身上获得了{item}",
                    importance=4
                )
    
    def process_npc_interaction(self, npc1, npc2):
        """
        处理NPC互动，可能触发战斗
        
        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC
            
        Returns:
            触发的战斗结果，如果没有触发则返回None
        """
        # 检查死斗
        if self.check_deathmatch_opportunity(npc1, npc2):
            return self.execute_npc_deathmatch(npc1, npc2)
        
        # 检查切磋
        if self.check_spar_opportunity(npc1, npc2):
            return self.execute_npc_spar(npc1, npc2)
        
        return None
    
    def process_npc_vs_player_combat(self, npc, player, combat_result: CombatResult) -> bool:
        """
        处理NPC与玩家战斗后的逻辑
        
        当NPC战胜玩家后，根据NPC性格决定是否处决玩家
        
        Args:
            npc: 与玩家战斗的NPC
            player: 玩家对象
            combat_result: 战斗结果
            
        Returns:
            bool: NPC是否处决了玩家
        """
        # 只有NPC胜利时才考虑处决
        if combat_result.winner and combat_result.winner.name == npc.data.dao_name:
            # NPC战胜玩家，判断是否处决
            executed = self.execute_npc_vs_player(npc, player, combat_result)
            
            if executed:
                # 记录处决事件
                log_entry = {
                    "type": "npc_execute_player",
                    "npc_id": npc.data.id,
                    "npc_name": npc.data.dao_name,
                    "player_name": player.stats.name,
                    "timestamp": datetime.now(),
                }
                self.combat_logs.append(log_entry)
                
                # 添加NPC记忆
                npc.independent.add_memory(
                    f"战胜并处决了玩家{player.stats.name}，获得了对方的全部物品",
                    importance=10,
                    emotion="positive" if getattr(npc.data, 'morality', 0) < 0 else "negative"
                )
            else:
                # NPC选择饶恕玩家
                npc.independent.add_memory(
                    f"战胜了玩家{player.stats.name}，但选择饶恕对方",
                    importance=7,
                    emotion="positive"
                )
                
                # 玩家对NPC的好感度提升（被饶恕）
                if hasattr(npc.independent, 'update_favor'):
                    npc.independent.update_favor(player.stats.name, 20)
            
            return executed
        
        return False
    
    def check_npc_execute_player_opportunity(self, npc, player) -> bool:
        """
        检查NPC是否有机会处决玩家
        
        用于在特定情况下（如玩家重伤、被俘虏等）判断NPC是否会处决玩家
        
        Args:
            npc: NPC对象
            player: 玩家对象
            
        Returns:
            bool: NPC是否会处决玩家
        """
        # 使用_should_execute_player辅助方法判断
        return self._should_execute_player(npc)
    
    def get_combat_summary(self, npc_id: str) -> Dict[str, Any]:
        """获取NPC战斗摘要"""
        stats = self.get_npc_combat_stats(npc_id)
        total = stats.wins + stats.losses + stats.draws
        
        return {
            "wins": stats.wins,
            "losses": stats.losses,
            "draws": stats.draws,
            "total": total,
            "win_rate": stats.wins / total if total > 0 else 0,
            "spar_count": stats.spar_count,
            "deathmatch_count": stats.deathmatch_count,
            "recent_history": stats.history[-5:] if stats.history else [],
        }


# 全局NPC战斗管理器实例
npc_combat_manager = NPCCombatManager()
