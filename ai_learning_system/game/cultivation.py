"""
修炼系统模块
管理修炼、突破等核心玩法
"""

import random
from typing import Dict, Optional, Tuple, Any
from enum import Enum

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    get_realm_info, get_breakthrough_success_rate,
    GAME_CONFIG, get_phrase
)
from .player import Player


class BreakthroughResult(Enum):
    """突破结果枚举"""
    SUCCESS = "success"           # 成功
    FAILURE = "failure"           # 失败
    INJURY = "injury"             # 受伤
    DEATH = "death"               # 死亡
    NOT_READY = "not_ready"       # 未达到突破条件


class CultivationSystem:
    """修炼系统类"""
    
    def __init__(self, player: Player):
        """
        初始化修炼系统
        
        Args:
            player: 玩家对象
        """
        self.player = player
    
    def practice(self, times: int = 1) -> Dict[str, Any]:
        """
        修炼
        
        Args:
            times: 修炼次数
            
        Returns:
            修炼结果
        """
        if self.player.stats.is_dead:
            return {
                "success": False,
                "message": "道友已陨落，无法修炼...",
            }
        
        if self.player.stats.is_injured:
            return {
                "success": False,
                "message": f"道友身负重伤，需静养{self.player.stats.injury_days}天方可修炼。",
            }
        
        # 限制最大修炼次数
        max_times = GAME_CONFIG["cultivation"]["max_practice_per_session"]
        times = min(times, max_times)
        
        # 获取修炼速度
        speed = self.player.get_cultivation_speed()
        base_exp = GAME_CONFIG["cultivation"]["base_exp_per_practice"]
        
        total_exp = 0
        total_days = 0
        messages = []
        
        for i in range(times):
            # 计算获得经验
            exp_gain = int(base_exp * speed * (1 + random.uniform(-0.1, 0.1)))
            total_exp += exp_gain
            
            # 消耗时间
            days = GAME_CONFIG["cultivation"]["practice_time_days"]
            total_days += days
            
            # 消耗灵力
            self.player.stats.spiritual_power -= 5
            if self.player.stats.spiritual_power < 0:
                self.player.stats.spiritual_power = 0
                messages.append(f"第{i+1}次修炼：灵力不足，修炼效果减半")
                total_exp -= exp_gain // 2
            
            # 随机事件（小概率）
            if random.random() < 0.05:
                event = self._random_cultivation_event()
                messages.append(f"第{i+1}次修炼：{event}")
        
        # 增加经验
        self.player.add_exp(total_exp)
        self.player.stats.total_practices += times
        
        # 推进时间
        self.player.advance_time(total_days)
        
        # 恢复灵力
        self.player.stats.spiritual_power = min(
            self.player.stats.spiritual_power + times * 10,
            self.player.stats.max_spiritual_power
        )
        
        # 构建结果
        result = {
            "success": True,
            "times": times,
            "exp_gained": total_exp,
            "days_passed": total_days,
            "speed": speed,
            "messages": messages,
        }
        
        # 检查是否可以突破
        if self.player.can_breakthrough():
            result["can_breakthrough"] = True
            result["message"] = f"修炼完成！获得{total_exp}修为，已可尝试突破！"
        else:
            result["can_breakthrough"] = False
            exp_current, exp_needed, progress = self.player.get_exp_progress()
            result["message"] = f"修炼完成！获得{total_exp}修为，当前进度{progress*100:.1f}%"
        
        return result
    
    def _random_cultivation_event(self) -> str:
        """随机修炼事件"""
        events = [
            "心有所感，修为精进！",
            "灵气充沛，事半功倍！",
            "略有所悟，道心更坚。",
            "偶遇灵气漩涡，吸收了不少灵气。",
            "心境平和，修炼顺利。",
        ]
        return random.choice(events)
    
    def attempt_breakthrough(self) -> Dict[str, Any]:
        """
        尝试突破
        
        Returns:
            突破结果
        """
        if self.player.stats.is_dead:
            return {
                "result": BreakthroughResult.NOT_READY,
                "message": "道友已陨落，无法突破...",
            }
        
        if self.player.stats.is_injured:
            return {
                "result": BreakthroughResult.NOT_READY,
                "message": "道友身负重伤，无法突破。",
            }
        
        if not self.player.can_breakthrough():
            exp_current, exp_needed, progress = self.player.get_exp_progress()
            return {
                "result": BreakthroughResult.NOT_READY,
                "message": f"修为不足，还需{exp_needed - exp_current}修为方可突破。",
            }
        
        # 计算成功率
        player_stats = {
            "fortune": self.player.stats.fortune,
            "karma": self.player.stats.karma,
        }
        success_rate = get_breakthrough_success_rate(
            self.player.stats.realm_level,
            player_stats
        )
        
        # 消耗灵力
        self.player.stats.spiritual_power -= 20
        if self.player.stats.spiritual_power < 0:
            self.player.stats.spiritual_power = 0
            success_rate *= 0.8  # 灵力不足降低成功率
        
        # 判定结果
        roll = random.random()
        
        if roll < success_rate:
            # 突破成功
            return self._breakthrough_success()
        elif roll < success_rate + 0.1:  # 10%概率死亡
            # 死亡
            return self._breakthrough_death()
        elif roll < success_rate + 0.1 + GAME_CONFIG["breakthrough"]["injury_chance"]:
            # 受伤
            return self._breakthrough_injury()
        else:
            # 普通失败
            return self._breakthrough_failure()
    
    def _breakthrough_success(self) -> Dict[str, Any]:
        """突破成功"""
        old_realm = self.player.get_realm_name()
        old_level = self.player.stats.realm_level
        
        # 提升境界
        self.player.stats.realm_level += 1
        self.player.stats.realm_layer = 1
        self.player.stats.total_breakthroughs += 1
        
        # 更新属性
        self.player._update_max_stats()
        self.player._update_lifespan()
        
        # 恢复状态
        self.player.heal()
        
        new_realm = self.player.get_realm_name()
        
        # 获取突破奖励
        realm_info = get_realm_info(self.player.stats.realm_level)
        bonus = realm_info.breakthrough_bonus if realm_info else {}
        
        message = f"""
🎉 突破成功！🎉

{old_realm} → {new_realm}

天雷滚滚，灵气涌动！
道友成功突破瓶颈，修为更上一层楼！

突破奖励：
- 寿元提升至 {self.player.stats.lifespan} 年
- 气血上限提升至 {self.player.stats.max_health}
- 灵力上限提升至 {self.player.stats.max_spiritual_power}
"""
        
        if "spiritual_power" in bonus:
            message += f"- 获得 {bonus['spiritual_power']} 灵力\n"
        
        return {
            "result": BreakthroughResult.SUCCESS,
            "old_realm": old_realm,
            "new_realm": new_realm,
            "message": message,
        }
    
    def _breakthrough_failure(self) -> Dict[str, Any]:
        """突破失败"""
        # 损失部分经验
        exp_loss = int(self.player.stats.exp * GAME_CONFIG["breakthrough"]["exp_loss_on_failure"])
        self.player.stats.exp -= exp_loss
        
        # 消耗时间
        days = GAME_CONFIG["cultivation"]["practice_time_days"] * 3
        self.player.advance_time(days)
        
        message = f"""
💔 突破失败

道行不稳，突破未果。
损失 {exp_loss} 修为，需重新积累。

建议：
- 稳固当前境界后再尝试
- 寻找突破丹药辅助
- 寻找灵气充沛之地修炼
"""
        
        return {
            "result": BreakthroughResult.FAILURE,
            "exp_loss": exp_loss,
            "message": message,
        }
    
    def _breakthrough_injury(self) -> Dict[str, Any]:
        """突破受伤"""
        # 损失部分经验
        exp_loss = int(self.player.stats.exp * GAME_CONFIG["breakthrough"]["exp_loss_on_failure"] * 2)
        self.player.stats.exp -= exp_loss
        
        # 受伤
        injury_days = GAME_CONFIG["breakthrough"]["injury_duration_days"]
        self.player.injure(injury_days)
        
        # 消耗时间
        days = GAME_CONFIG["cultivation"]["practice_time_days"] * 5
        self.player.advance_time(days)
        
        message = f"""
⚠️ 突破失败，走火入魔！

气血逆行，经脉受损！
损失 {exp_loss} 修为，需静养 {injury_days} 天。

警告：
- 受伤期间修炼速度减半
- 需等待伤势恢复后方可再次尝试突破
- 建议寻找疗伤丹药
"""
        
        return {
            "result": BreakthroughResult.INJURY,
            "exp_loss": exp_loss,
            "injury_days": injury_days,
            "message": message,
        }
    
    def _breakthrough_death(self) -> Dict[str, Any]:
        """突破死亡"""
        cause = "突破失败，走火入魔，爆体而亡"
        death_info = self.player.die(cause)
        
        message = f"""
💀 突破失败，身死道消 💀

{self.player.stats.name} 在突破时走火入魔，爆体而亡...

陨落信息：
- 年龄：{death_info['age']} 岁
- 境界：{death_info['realm']}
- 死因：{death_info['cause']}

轮回转世：
- 继承修为：{death_info['inheritance']['exp']}
- 继承灵石：{death_info['inheritance']['spirit_stones']}
- 福缘加成：+{death_info['inheritance']['fortune_bonus']}

大道无情，愿道友来世再续仙缘...
"""
        
        return {
            "result": BreakthroughResult.DEATH,
            "death_info": death_info,
            "message": message,
        }
    
    def get_breakthrough_info(self) -> Dict[str, Any]:
        """
        获取突破信息
        
        Returns:
            突破相关信息
        """
        if not self.player.can_breakthrough():
            exp_current, exp_needed, progress = self.player.get_exp_progress()
            return {
                "can_breakthrough": False,
                "message": f"修为不足，还需 {exp_needed - exp_current} 修为方可突破。",
                "progress": progress,
            }
        
        player_stats = {
            "fortune": self.player.stats.fortune,
            "karma": self.player.stats.karma,
        }
        success_rate = get_breakthrough_success_rate(
            self.player.stats.realm_level,
            player_stats
        )
        
        current_realm = self.player.get_realm_name()
        next_realm_info = get_realm_info(self.player.stats.realm_level + 1)
        next_realm = next_realm_info.name if next_realm_info else "未知"
        
        return {
            "can_breakthrough": True,
            "current_realm": current_realm,
            "next_realm": next_realm,
            "success_rate": success_rate,
            "message": f"当前突破成功率：{success_rate*100:.1f}%\n{current_realm} → {next_realm}",
        }
