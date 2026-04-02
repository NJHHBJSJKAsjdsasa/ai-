"""
天劫系统模块
管理天劫的触发、准备、战斗、奖励等核心玩法
"""

import random
import json
from typing import Dict, Optional, List, Any, Tuple
from enum import Enum
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.tribulation_config import (
    TribulationType, TribulationStatus, ThunderType, ThunderStrike,
    TribulationStage, get_tribulation_stage, generate_thunder_sequence,
    get_preparation_items, calculate_tribulation_success_rate,
    generate_tribulation_rewards, get_tribulation_type_by_karma,
    calculate_failure_penalty, TRIBULATION_PREPARATION_ITEMS
)
from storage.database import Database


class TribulationResult(Enum):
    """天劫结果枚举"""
    SUCCESS = "success"           # 成功
    FAILURE = "failure"           # 失败
    DEATH = "death"               # 死亡
    IN_PROGRESS = "in_progress"   # 进行中
    NOT_READY = "not_ready"       # 未准备好
    CANCELLED = "cancelled"       # 取消


class TribulationManager:
    """天劫管理器类"""

    def __init__(self, player=None, db: Database = None):
        """
        初始化天劫管理器

        Args:
            player: 玩家对象
            db: 数据库实例
        """
        self.player = player
        self.db = db or Database()
        self.current_tribulation: Optional[Dict[str, Any]] = None
        self.thunder_sequence: List[ThunderStrike] = []
        self.preparation_items: Dict[str, List[Dict]] = {
            "treasure": [],
            "pill": [],
            "formation": []
        }

    def check_tribulation_trigger(self, realm_level: int) -> Tuple[bool, str]:
        """
        检查是否应该触发天劫

        Args:
            realm_level: 当前境界等级

        Returns:
            (是否触发, 消息)
        """
        # 检查是否有天劫配置
        stage = get_tribulation_stage(realm_level)
        if not stage:
            return False, f"境界 {realm_level} 没有对应的天劫配置"

        # 检查玩家状态
        if not self.player:
            return False, "玩家对象未设置"

        if self.player.stats.is_dead:
            return False, "玩家已死亡"

        if self.player.stats.is_injured:
            return False, "玩家受伤中，无法渡劫"

        # 检查是否已经有进行中的天劫
        if self.current_tribulation and self.current_tribulation.get("status") == TribulationStatus.IN_PROGRESS.value:
            return False, "已有进行中的天劫"

        return True, f"可以触发{stage.tribulation_name}"

    def start_tribulation(self, realm_level: int) -> Dict[str, Any]:
        """
        开始天劫

        Args:
            realm_level: 境界等级

        Returns:
            天劫开始结果
        """
        # 检查是否可以触发
        can_trigger, message = self.check_tribulation_trigger(realm_level)
        if not can_trigger:
            return {
                "success": False,
                "result": TribulationResult.NOT_READY,
                "message": message
            }

        stage = get_tribulation_stage(realm_level)

        # 根据业力确定天劫类型
        tribulation_type = get_tribulation_type_by_karma(self.player.stats.karma)

        # 生成雷劫序列
        self.thunder_sequence = generate_thunder_sequence(stage)

        # 创建天劫记录
        self.current_tribulation = {
            "player_id": getattr(self.player, 'id', 'unknown'),
            "realm_level": realm_level,
            "realm_name": stage.realm_name,
            "tribulation_type": tribulation_type.value,
            "status": TribulationStatus.PREPARING.value,
            "total_thunder": stage.total_thunder,
            "current_thunder": 0,
            "thunder_power": stage.base_power,
            "player_health": self.player.stats.health,
            "player_max_health": self.player.stats.max_health,
            "player_spiritual_power": self.player.stats.spiritual_power,
            "player_max_spiritual_power": self.player.stats.max_spiritual_power,
            "player_defense": self.player.stats.defense,
            "player_resistance": 0.0,  # 基础雷抗
            "used_treasures": [],
            "used_pills": [],
            "used_formations": [],
            "thunder_history": [],
            "final_result": None,
            "reward_attributes": {},
            "created_at": datetime.now().isoformat()
        }

        # 保存到数据库
        self._save_tribulation_record()

        return {
            "success": True,
            "result": TribulationResult.IN_PROGRESS,
            "tribulation_id": self.current_tribulation.get("id"),
            "stage": stage,
            "thunder_sequence": self.thunder_sequence,
            "message": f"⚡ {stage.tribulation_name}降临！共{stage.total_thunder}道雷劫，请做好准备！"
        }

    def add_preparation_item(self, item_type: str, item_name: str) -> Dict[str, Any]:
        """
        添加天劫准备物品

        Args:
            item_type: 物品类型（treasure/pill/formation）
            item_name: 物品名称

        Returns:
            添加结果
        """
        if not self.current_tribulation:
            return {"success": False, "message": "没有进行中的天劫"}

        if self.current_tribulation["status"] != TribulationStatus.PREPARING.value:
            return {"success": False, "message": "天劫已开始，无法添加准备物品"}

        # 获取物品配置
        items = TRIBULATION_PREPARATION_ITEMS.get(item_type, [])
        item_config = None
        for item in items:
            if item.name == item_name:
                item_config = item
                break

        if not item_config:
            return {"success": False, "message": f"未找到{item_name}的配置"}

        # 检查境界要求
        if item_config.required_realm > self.current_tribulation["realm_level"]:
            return {"success": False, "message": f"境界不足，需要{item_config.required_realm}重境界"}

        # 添加到准备列表
        preparation = {
            "item_type": item_type,
            "name": item_name,
            "description": item_config.description,
            "effect_type": item_config.effect_type,
            "effect_value": item_config.effect_value,
            "rarity": item_config.rarity
        }

        self.preparation_items[item_type].append(preparation)

        # 更新天劫记录
        if item_type == "treasure":
            self.current_tribulation["used_treasures"].append(item_name)
        elif item_type == "pill":
            self.current_tribulation["used_pills"].append(item_name)
        elif item_type == "formation":
            self.current_tribulation["used_formations"].append(item_name)

        # 应用效果
        self._apply_preparation_effect(item_config.effect_type, item_config.effect_value)

        # 保存准备记录到数据库
        self._save_preparation_record(item_type, item_name, item_config)

        return {
            "success": True,
            "message": f"成功准备{item_name}，{item_config.description}",
            "preparation": preparation
        }

    def _apply_preparation_effect(self, effect_type: str, effect_value: float):
        """应用准备物品效果"""
        if effect_type == "thunder_resistance":
            self.current_tribulation["player_resistance"] += effect_value
        elif effect_type == "damage_reduction":
            self.current_tribulation["player_defense"] += int(effect_value * 100)
        elif effect_type == "thunder_absorb":
            self.current_tribulation["player_resistance"] += effect_value
        elif effect_type == "defense_boost":
            self.current_tribulation["player_defense"] += int(effect_value)
        elif effect_type == "health_regen":
            # 战斗中恢复，暂不应用
            pass
        elif effect_type == "spirit_regen":
            # 战斗中恢复，暂不应用
            pass
        elif effect_type == "tribulation_boost":
            self.current_tribulation["player_resistance"] += effect_value
        elif effect_type == "tribulation_great_boost":
            self.current_tribulation["player_resistance"] += effect_value

    def begin_tribulation_battle(self) -> Dict[str, Any]:
        """
        开始天劫战斗

        Returns:
            战斗开始结果
        """
        if not self.current_tribulation:
            return {"success": False, "message": "没有进行中的天劫"}

        if self.current_tribulation["status"] != TribulationStatus.PREPARING.value:
            return {"success": False, "message": "天劫状态错误"}

        # 更新状态为进行中
        self.current_tribulation["status"] = TribulationStatus.IN_PROGRESS.value

        # 保存到数据库
        self._save_tribulation_record()

        return {
            "success": True,
            "message": "天劫战斗开始！",
            "total_thunder": self.current_tribulation["total_thunder"],
            "first_thunder": self.thunder_sequence[0] if self.thunder_sequence else None
        }

    def process_thunder_strike(self, use_defense: bool = False, use_treasure: bool = False) -> Dict[str, Any]:
        """
        处理一道雷劫

        Args:
            use_defense: 是否使用防御
            use_treasure: 是否使用法宝

        Returns:
            雷劫处理结果
        """
        if not self.current_tribulation:
            return {"success": False, "message": "没有进行中的天劫", "finished": True}

        if self.current_tribulation["status"] != TribulationStatus.IN_PROGRESS.value:
            return {"success": False, "message": "天劫未在战斗中", "finished": True}

        current = self.current_tribulation["current_thunder"]
        total = self.current_tribulation["total_thunder"]

        if current >= total:
            # 所有雷劫完成，渡劫成功
            return self._tribulation_success()

        # 获取当前雷劫
        thunder = self.thunder_sequence[current]

        # 计算伤害
        damage = self._calculate_thunder_damage(thunder, use_defense, use_treasure)

        # 记录战斗前状态
        health_before = self.current_tribulation["player_health"]

        # 应用伤害
        self.current_tribulation["player_health"] -= damage
        health_after = max(0, self.current_tribulation["player_health"])
        self.current_tribulation["player_health"] = health_after

        # 更新当前雷劫数
        self.current_tribulation["current_thunder"] = current + 1

        # 记录雷劫历史
        thunder_record = {
            "thunder_number": thunder.number,
            "thunder_name": thunder.name,
            "thunder_power": thunder.base_power,
            "damage_dealt": damage,
            "health_before": health_before,
            "health_after": health_after,
            "use_defense": use_defense,
            "use_treasure": use_treasure
        }
        self.current_tribulation["thunder_history"].append(thunder_record)

        # 保存雷劫记录到数据库
        self._save_thunder_record(thunder, damage, health_before, health_after, use_defense, use_treasure)

        # 检查是否死亡
        if health_after <= 0:
            return self._tribulation_death()

        # 检查是否完成所有雷劫
        if current + 1 >= total:
            return self._tribulation_success()

        # 保存状态
        self._save_tribulation_record()

        # 获取下一道雷劫
        next_thunder = self.thunder_sequence[current + 1] if current + 1 < len(self.thunder_sequence) else None

        return {
            "success": True,
            "finished": False,
            "thunder": thunder,
            "damage": damage,
            "health_before": health_before,
            "health_after": health_after,
            "current": current + 1,
            "total": total,
            "next_thunder": next_thunder,
            "message": f"承受了{thunder.name}，受到{damage}点伤害，剩余{health_after}点生命"
        }

    def _calculate_thunder_damage(self, thunder: ThunderStrike, use_defense: bool, use_treasure: bool) -> int:
        """计算雷劫伤害"""
        base_damage = thunder.base_power

        # 应用玩家防御
        defense = self.current_tribulation["player_defense"]
        if use_defense:
            defense *= 1.5  # 主动防御增加50%效果

        # 雷抗减免
        resistance = self.current_tribulation["player_resistance"]

        # 法宝减免
        treasure_reduction = 0
        if use_treasure and self.preparation_items["treasure"]:
            # 使用第一个法宝
            treasure = self.preparation_items["treasure"][0]
            if treasure["effect_type"] in ["thunder_absorb", "damage_reduction", "thunder_resistance"]:
                treasure_reduction = treasure["effect_value"]

        # 计算最终伤害
        damage_reduction = defense * 0.5 + base_damage * resistance + base_damage * treasure_reduction
        final_damage = max(1, int(base_damage - damage_reduction))

        # 添加随机波动
        final_damage = int(final_damage * random.uniform(0.9, 1.1))

        return final_damage

    def _tribulation_success(self) -> Dict[str, Any]:
        """天劫成功处理"""
        self.current_tribulation["status"] = TribulationStatus.SUCCESS.value
        self.current_tribulation["final_result"] = "success"

        # 获取阶段配置
        stage = get_tribulation_stage(self.current_tribulation["realm_level"])

        # 生成奖励
        rewards = generate_tribulation_rewards(
            self.current_tribulation["realm_level"],
            True,
            stage.rewards.get("special_reward_probability", 0.5)
        )

        # 应用基础奖励
        base_rewards = {
            "max_health": stage.rewards.get("max_health", 0),
            "max_spiritual_power": stage.rewards.get("max_spiritual_power", 0),
            "defense": stage.rewards.get("defense", 0),
            "attack": stage.rewards.get("attack", 0),
            "crit_rate": stage.rewards.get("crit_rate", 0),
            "dodge_rate": stage.rewards.get("dodge_rate", 0)
        }

        # 保存奖励到数据库
        self._save_tribulation_rewards(True, rewards, base_rewards)

        # 更新玩家属性
        if self.player:
            self.player.stats.max_health += base_rewards["max_health"]
            self.player.stats.max_spiritual_power += base_rewards["max_spiritual_power"]
            self.player.stats.defense += base_rewards["defense"]
            self.player.stats.attack += base_rewards["attack"]
            self.player.stats.crit_rate += base_rewards["crit_rate"]
            self.player.stats.dodge_rate += base_rewards["dodge_rate"]

        # 保存最终记录
        self._save_tribulation_record()

        return {
            "success": True,
            "finished": True,
            "result": TribulationResult.SUCCESS,
            "message": f"🎉 恭喜！成功渡过{stage.tribulation_name}！",
            "base_rewards": base_rewards,
            "special_rewards": rewards
        }

    def _tribulation_failure(self) -> Dict[str, Any]:
        """天劫失败处理"""
        self.current_tribulation["status"] = TribulationStatus.FAILURE.value
        self.current_tribulation["final_result"] = "failure"

        # 获取阶段配置
        stage = get_tribulation_stage(self.current_tribulation["realm_level"])

        # 计算惩罚
        current_thunder = self.current_tribulation["current_thunder"]
        total_thunder = self.current_tribulation["total_thunder"]
        penalty = calculate_failure_penalty(stage, current_thunder, total_thunder)

        # 应用惩罚到玩家
        if self.player:
            # 损失气血
            health_loss = int(self.player.stats.max_health * penalty["health_loss"])
            self.player.stats.health = max(1, self.player.stats.health - health_loss)

            # 损失经验
            exp_loss = int(self.player.stats.exp * penalty["exp_loss"])
            self.player.stats.exp = max(0, self.player.stats.exp - exp_loss)

            # 受伤
            self.player.injure(penalty["injury_days"])

            # 境界跌落判定
            if random.random() < penalty.get("realm_fall_probability", 0):
                if self.player.stats.realm_layer > 1:
                    self.player.stats.realm_layer -= 1
                    realm_fall = True
                else:
                    realm_fall = False
            else:
                realm_fall = False

        # 保存记录
        self._save_tribulation_record()

        return {
            "success": False,
            "finished": True,
            "result": TribulationResult.FAILURE,
            "message": f"💔 渡劫失败！受到天劫反噬！",
            "penalty": penalty,
            "realm_fall": realm_fall if 'realm_fall' in dir() else False
        }

    def _tribulation_death(self) -> Dict[str, Any]:
        """天劫死亡处理"""
        self.current_tribulation["status"] = TribulationStatus.DEATH.value
        self.current_tribulation["final_result"] = "death"

        # 保存记录
        self._save_tribulation_record()

        # 玩家死亡处理
        if self.player:
            death_info = self.player.die("渡劫失败，身死道消")

            return {
                "success": False,
                "finished": True,
                "result": TribulationResult.DEATH,
                "message": "💀 渡劫失败，身死道消...",
                "death_info": death_info
            }

        return {
            "success": False,
            "finished": True,
            "result": TribulationResult.DEATH,
            "message": "💀 渡劫失败，身死道消..."
        }

    def flee_tribulation(self) -> Dict[str, Any]:
        """逃离天劫（放弃）"""
        if not self.current_tribulation:
            return {"success": False, "message": "没有进行中的天劫"}

        # 逃离视为失败，但惩罚减半
        self.current_tribulation["status"] = TribulationStatus.FAILURE.value
        self.current_tribulation["final_result"] = "fled"

        # 应用减半惩罚
        if self.player:
            health_loss = int(self.player.stats.max_health * 0.2)
            self.player.stats.health = max(1, self.player.stats.health - health_loss)
            exp_loss = int(self.player.stats.exp * 0.1)
            self.player.stats.exp = max(0, self.player.stats.exp - exp_loss)
            self.player.injure(30)

        self._save_tribulation_record()

        return {
            "success": False,
            "finished": True,
            "result": TribulationResult.CANCELLED,
            "message": "你逃离了天劫，但受到了一定的反噬"
        }

    def get_tribulation_info(self) -> Dict[str, Any]:
        """获取当前天劫信息"""
        if not self.current_tribulation:
            return {"has_tribulation": False}

        stage = get_tribulation_stage(self.current_tribulation["realm_level"])

        return {
            "has_tribulation": True,
            "tribulation_id": self.current_tribulation.get("id"),
            "status": self.current_tribulation["status"],
            "realm_name": self.current_tribulation["realm_name"],
            "tribulation_name": stage.tribulation_name if stage else "未知天劫",
            "current_thunder": self.current_tribulation["current_thunder"],
            "total_thunder": self.current_tribulation["total_thunder"],
            "player_health": self.current_tribulation["player_health"],
            "player_max_health": self.current_tribulation["player_max_health"],
            "player_resistance": self.current_tribulation["player_resistance"],
            "preparation_items": self.preparation_items,
            "thunder_history": self.current_tribulation["thunder_history"]
        }

    def get_available_preparations(self, realm_level: int) -> Dict[str, List[Dict]]:
        """获取可用的准备物品"""
        available = {}
        for item_type in ["treasure", "pill", "formation"]:
            items = get_preparation_items(item_type, realm_level)
            available[item_type] = [
                {
                    "name": item.name,
                    "description": item.description,
                    "effect_type": item.effect_type,
                    "effect_value": item.effect_value,
                    "rarity": item.rarity,
                    "required_realm": item.required_realm
                }
                for item in items
            ]
        return available

    def _save_tribulation_record(self):
        """保存天劫记录到数据库"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            data = self.current_tribulation.copy()
            data["used_treasures"] = json.dumps(data.get("used_treasures", []))
            data["used_pills"] = json.dumps(data.get("used_pills", []))
            data["used_formations"] = json.dumps(data.get("used_formations", []))
            data["thunder_history"] = json.dumps(data.get("thunder_history", []))
            data["reward_attributes"] = json.dumps(data.get("reward_attributes", {}))

            if "id" in data:
                # 更新记录
                cursor.execute("""
                    UPDATE tribulation_records SET
                        status = ?, current_thunder = ?, player_health = ?,
                        player_spiritual_power = ?, player_defense = ?, player_resistance = ?,
                        used_treasures = ?, used_pills = ?, used_formations = ?,
                        thunder_history = ?, final_result = ?, reward_attributes = ?,
                        completed_at = ?
                    WHERE id = ?
                """, (
                    data["status"], data["current_thunder"], data["player_health"],
                    data["player_spiritual_power"], data["player_defense"], data["player_resistance"],
                    data["used_treasures"], data["used_pills"], data["used_formations"],
                    data["thunder_history"], data["final_result"], data["reward_attributes"],
                    datetime.now().isoformat() if data.get("final_result") else None,
                    data["id"]
                ))
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO tribulation_records (
                        player_id, realm_level, realm_name, tribulation_type, status,
                        total_thunder, current_thunder, thunder_power,
                        player_health, player_max_health, player_spiritual_power, player_max_spiritual_power,
                        player_defense, player_resistance,
                        used_treasures, used_pills, used_formations,
                        thunder_history, final_result, reward_attributes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["player_id"], data["realm_level"], data["realm_name"],
                    data["tribulation_type"], data["status"],
                    data["total_thunder"], data["current_thunder"], data["thunder_power"],
                    data["player_health"], data["player_max_health"],
                    data["player_spiritual_power"], data["player_max_spiritual_power"],
                    data["player_defense"], data["player_resistance"],
                    data["used_treasures"], data["used_pills"], data["used_formations"],
                    data["thunder_history"], data["final_result"],
                    data["reward_attributes"], data["created_at"]
                ))
                data["id"] = cursor.lastrowid
                self.current_tribulation["id"] = data["id"]

            conn.commit()
        except Exception as e:
            print(f"保存天劫记录失败: {e}")

    def _save_preparation_record(self, item_type: str, item_name: str, item_config):
        """保存准备记录到数据库"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tribulation_preparations (
                    player_id, tribulation_id, item_type, item_name,
                    effect_type, effect_value, is_consumed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_tribulation["player_id"],
                self.current_tribulation.get("id"),
                item_type,
                item_name,
                item_config.effect_type,
                item_config.effect_value,
                0,
                datetime.now().isoformat()
            ))

            conn.commit()
        except Exception as e:
            print(f"保存准备记录失败: {e}")

    def _save_thunder_record(self, thunder: ThunderStrike, damage: int,
                             health_before: int, health_after: int,
                             use_defense: bool, use_treasure: bool):
        """保存雷劫记录到数据库"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tribulation_thunder_records (
                    tribulation_id, thunder_number, thunder_name, thunder_power,
                    damage_dealt, player_health_before, player_health_after,
                    defense_used, is_resisted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_tribulation.get("id"),
                thunder.number,
                thunder.name,
                thunder.base_power,
                damage,
                health_before,
                health_after,
                json.dumps({"use_defense": use_defense, "use_treasure": use_treasure}),
                0,
                datetime.now().isoformat()
            ))

            conn.commit()
        except Exception as e:
            print(f"保存雷劫记录失败: {e}")

    def _save_tribulation_rewards(self, success: bool, rewards: List[Dict], base_rewards: Dict):
        """保存天劫奖励到数据库"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            # 保存特殊奖励
            for reward in rewards:
                cursor.execute("""
                    INSERT INTO tribulation_rewards (
                        player_id, tribulation_id, realm_level, realm_name,
                        success, reward_type, reward_name, reward_value, description, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_tribulation["player_id"],
                    self.current_tribulation.get("id"),
                    self.current_tribulation["realm_level"],
                    self.current_tribulation["realm_name"],
                    1 if success else 0,
                    reward["type"],
                    reward["name"],
                    str(reward["value"]),
                    reward["description"],
                    datetime.now().isoformat()
                ))

            # 保存基础奖励
            for attr_name, attr_value in base_rewards.items():
                if attr_value > 0:
                    cursor.execute("""
                        INSERT INTO tribulation_rewards (
                            player_id, tribulation_id, realm_level, realm_name,
                            success, reward_type, reward_name, reward_value, description, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.current_tribulation["player_id"],
                        self.current_tribulation.get("id"),
                        self.current_tribulation["realm_level"],
                        self.current_tribulation["realm_name"],
                        1 if success else 0,
                        "base_attribute",
                        attr_name,
                        str(attr_value),
                        f"基础属性提升: {attr_name}",
                        datetime.now().isoformat()
                    ))

            conn.commit()
        except Exception as e:
            print(f"保存天劫奖励失败: {e}")

    def get_tribulation_history(self, player_id: str = None, limit: int = 10) -> List[Dict]:
        """获取天劫历史记录"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            player_id = player_id or getattr(self.player, 'id', None) or 'unknown'

            cursor.execute("""
                SELECT * FROM tribulation_records
                WHERE player_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (player_id, limit))

            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "realm_name": row["realm_name"],
                    "status": row["status"],
                    "total_thunder": row["total_thunder"],
                    "current_thunder": row["current_thunder"],
                    "final_result": row["final_result"],
                    "created_at": row["created_at"],
                    "completed_at": row["completed_at"]
                })

            return history
        except Exception as e:
            print(f"获取天劫历史失败: {e}")
            return []
