"""
处决系统模块
管理战斗后对NPC的处决或饶恕选择，影响玩家业力值和NPC关系
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ExecutionChoice(Enum):
    """
    处决选择枚举
    定义玩家在战斗胜利后可做的选择
    """
    EXECUTE = "处决"  # 处决NPC，彻底击杀
    SPARE = "饶恕"    # 饶恕NPC，保留其性命


@dataclass
class ExecutionResult:
    """
    处决结果数据类
    记录处决或饶恕操作的结果信息
    
    Attributes:
        success: 操作是否成功执行
        choice: 玩家做出的选择（处决/饶恕）
        karma_change: 业力值变化（正数为善业，负数为恶业）
        message: 结果描述信息
        timestamp: 操作发生的时间戳
    """
    success: bool
    choice: ExecutionChoice
    karma_change: int
    message: str
    timestamp: datetime


class ExecutionSystem:
    """
    处决系统类
    
    负责处理战斗结束后对NPC的处决或饶恕逻辑，包括：
    - 计算业力值变化（根据NPC善恶属性和玩家选择）
    - 处理NPC生死状态
    - 更新NPC对玩家的好感度
    - 给予玩家相应奖励
    
    业力系统规则：
    - 处决邪恶NPC（morality < 0）：+善业（替天行道）
    - 处决善良NPC（morality > 0）：-善业/+恶业（滥杀无辜）
    - 饶恕邪恶NPC：+大量善业（慈悲为怀，感化恶人）
    - 饶恕善良NPC：+少量善业（善待善人）
    """
    
    def __init__(self):
        """
        初始化处决系统
        """
        pass
    
    def prompt_execution_choice(self, npc_name: str) -> str:
        """
        生成处决选择提示文本
        
        在战斗胜利后调用，向玩家展示处决或饶恕的选择提示
        
        Args:
            npc_name: NPC的道号或名称
            
        Returns:
            格式化的提示文本字符串
        """
        prompt = f"""
╔══════════════════════════════════════════════════════════╗
║  战斗胜利！                                                ║
╠══════════════════════════════════════════════════════════╣
║  {npc_name}已败于你手，生死皆在你一念之间                    ║
╠══════════════════════════════════════════════════════════╣
║  请选择你的行动：                                          ║
║                                                           ║
║  [1] 处决 - 彻底击杀，斩草除根                              ║
║      · 获得额外战斗奖励                                     ║
║      · 根据对方善恶影响业力                                 ║
║                                                           ║
║  [2] 饶恕 - 放其一条生路，结个善缘                          ║
║      · 对方好感度大幅提升                                   ║
║      · 根据对方善恶获得业力                                 ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
"""
        return prompt
    
    def execute_npc(self, npc, player) -> ExecutionResult:
        """
        执行处决NPC操作
        
        彻底击杀NPC，玩家获得额外奖励，并根据NPC善恶值计算业力变化
        
        Args:
            npc: NPC对象，需包含 data.is_alive、data.morality 等属性
            player: 玩家对象，需包含 stats.karma 等属性
            
        Returns:
            ExecutionResult: 处决结果对象
        """
        timestamp = datetime.now()
        
        # 检查NPC是否已经被击败或死亡
        if not npc.data.is_alive:
            return ExecutionResult(
                success=False,
                choice=ExecutionChoice.EXECUTE,
                karma_change=0,
                message=f"{npc.data.dao_name}已经死亡，无需再次处决",
                timestamp=timestamp
            )
        
        # 标记NPC死亡
        npc.data.is_alive = False
        
        # 计算业力变化
        karma_change = self.calculate_karma_change(npc, ExecutionChoice.EXECUTE)
        
        # 更新玩家业力值
        player.stats.karma += karma_change
        player.stats.karma = max(-1000, min(1000, player.stats.karma))  # 限制业力范围
        
        # 玩家获得额外奖励
        reward_message = self._give_execution_rewards(player, npc)
        
        # 构建结果消息
        if karma_change > 0:
            karma_desc = f"业力 +{karma_change}（替天行道，善业增长）"
        elif karma_change < 0:
            karma_desc = f"业力 {karma_change}（滥杀无辜，恶业增长）"
        else:
            karma_desc = "业力无变化"
        
        message = f"你处决了{npc.data.dao_name}！{karma_desc}。{reward_message}"
        
        return ExecutionResult(
            success=True,
            choice=ExecutionChoice.EXECUTE,
            karma_change=karma_change,
            message=message,
            timestamp=timestamp
        )
    
    def spare_npc(self, npc, player) -> ExecutionResult:
        """
        执行饶恕NPC操作
        
        保留NPC性命，恢复其少量生命值，大幅提升好感度，并根据NPC善恶值计算业力变化
        
        Args:
            npc: NPC对象，需包含 data.is_alive、data.morality、data.favor 等属性
            player: 玩家对象，需包含 stats.name、stats.karma 等属性
            
        Returns:
            ExecutionResult: 饶恕结果对象
        """
        timestamp = datetime.now()
        
        # 检查NPC是否已经被击败
        if not npc.data.is_alive:
            return ExecutionResult(
                success=False,
                choice=ExecutionChoice.SPARE,
                karma_change=0,
                message=f"{npc.data.dao_name}已经死亡，无法饶恕",
                timestamp=timestamp
            )
        
        # NPC保留1点生命值（重伤状态）
        # 注意：这里假设NPC有health属性，如果没有则跳过
        if hasattr(npc.data, 'health'):
            npc.data.health = 1
        
        # NPC对玩家好感度大幅提升
        favor_boost = 30  # 饶恕带来的好感度提升
        npc.update_favor(player.stats.name, favor_boost)
        
        # 添加NPC记忆（被饶恕）
        npc.add_memory(
            f"被{player.stats.name}饶恕一命，感激不尽",
            importance=8,
            emotion="positive"
        )
        
        # 计算业力变化
        karma_change = self.calculate_karma_change(npc, ExecutionChoice.SPARE)
        
        # 更新玩家业力值
        player.stats.karma += karma_change
        player.stats.karma = max(-1000, min(1000, player.stats.karma))  # 限制业力范围
        
        # 构建结果消息
        if karma_change > 20:
            karma_desc = f"业力 +{karma_change}（慈悲为怀，大善之举）"
        elif karma_change > 0:
            karma_desc = f"业力 +{karma_change}（心存善念）"
        else:
            karma_desc = "业力无变化"
        
        current_favor = npc.get_favor(player.stats.name)
        message = f"你饶恕了{npc.data.dao_name}！{karma_desc}。对方好感度+{favor_boost}（当前：{current_favor}）"
        
        return ExecutionResult(
            success=True,
            choice=ExecutionChoice.SPARE,
            karma_change=karma_change,
            message=message,
            timestamp=timestamp
        )
    
    def calculate_karma_change(self, npc, choice: ExecutionChoice) -> int:
        """
        计算业力值变化
        
        根据NPC的善恶值（morality）和玩家的选择计算业力变化：
        - morality范围：-100到100，负数表示邪恶，正数表示善良
        - 处决邪恶NPC：+善业（替天行道）
        - 处决善良NPC：-善业/+恶业（滥杀无辜）
        - 饶恕邪恶NPC：+大量善业（慈悲为怀，感化恶人）
        - 饶恕善良NPC：+少量善业（善待善人）
        
        Args:
            npc: NPC对象，需包含 data.morality 属性
            choice: 玩家的选择（处决/饶恕）
            
        Returns:
            业力变化值（范围-50到+50）
        """
        # 获取NPC善恶值，默认为0（中立）
        morality = getattr(npc.data, 'morality', 0)
        
        if choice == ExecutionChoice.EXECUTE:
            # 处决选择
            if morality < 0:
                # 处决邪恶NPC：替天行道，善业增长
                # 邪恶程度越高，善业越多（范围+5到+25）
                karma_change = min(25, max(5, abs(morality) // 4))
            elif morality > 0:
                # 处决善良NPC：滥杀无辜，恶业增长
                # 善良程度越高，恶业越多（范围-25到-5）
                karma_change = max(-25, min(-5, -morality // 4))
            else:
                # 处决中立NPC：业力变化较小
                karma_change = -5
                
        elif choice == ExecutionChoice.SPARE:
            # 饶恕选择
            if morality < 0:
                # 饶恕邪恶NPC：慈悲为怀，大善之举
                # 饶恕恶人比处决恶人获得更大量善业（范围+15到+40）
                karma_change = min(40, max(15, abs(morality) // 2 + 10))
            elif morality > 0:
                # 饶恕善良NPC：善待善人，善业增长
                # 善业较少（范围+5到+15）
                karma_change = min(15, max(5, morality // 8))
            else:
                # 饶恕中立NPC：心存善念
                karma_change = 10
        else:
            # 未知选择
            karma_change = 0
        
        # 确保业力变化在合理范围内（-50到+50）
        return max(-50, min(50, karma_change))
    
    def _give_execution_rewards(self, player, npc) -> str:
        """
        给予玩家处决奖励
        
        处决NPC后，玩家获得额外的灵石和经验奖励
        
        Args:
            player: 玩家对象
            npc: 被处决的NPC对象
            
        Returns:
            奖励描述字符串
        """
        # 基础奖励
        base_spirit_stones = 50
        base_exp = 20
        
        # 根据NPC境界调整奖励
        # 处理realm_level可能是字符串的情况
        from config import REALM_NAME_TO_LEVEL
        realm_level = npc.data.realm_level
        if isinstance(realm_level, str):
            realm_level_num = REALM_NAME_TO_LEVEL.get(realm_level, 0)
            if realm_level_num == 0 and realm_level.isdigit():
                realm_level_num = int(realm_level)
        else:
            realm_level_num = int(realm_level)
        realm_bonus = realm_level_num * 20
        
        # 总奖励
        spirit_stones = base_spirit_stones + realm_bonus
        exp = base_exp + realm_bonus // 2
        
        # 发放奖励
        player.stats.spirit_stones += spirit_stones
        player.add_exp(exp)
        
        return f"获得 {spirit_stones} 灵石，{exp} 经验值"
    
    def get_npc_morality_description(self, npc) -> str:
        """
        获取NPC善恶值描述
        
        根据NPC的morality属性返回对应的描述文本
        
        Args:
            npc: NPC对象
            
        Returns:
            善恶值描述字符串
        """
        morality = getattr(npc.data, 'morality', 0)
        
        if morality <= -80:
            return "极恶（罪大恶极）"
        elif morality <= -50:
            return "邪恶（恶贯满盈）"
        elif morality <= -20:
            return "偏恶（为非作歹）"
        elif morality < 0:
            return "小恶（略有劣迹）"
        elif morality == 0:
            return "中立（亦正亦邪）"
        elif morality < 20:
            return "小善（心地善良）"
        elif morality < 50:
            return "偏善（乐善好施）"
        elif morality < 80:
            return "善良（德高望重）"
        else:
            return "极善（圣人君子）"


# 全局处决系统实例
execution_system = ExecutionSystem()
