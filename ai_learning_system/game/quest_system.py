"""
任务系统模块
管理任务的接受、进度追踪、完成和奖励发放
"""

import random
import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from config.quest_config import (
    QuestType, ObjectiveType, QuestReward, QuestTemplate,
    MAIN_QUESTS, SIDE_QUEST_TEMPLATES, DAILY_QUEST_TEMPLATES,
    SIDE_QUEST_LOCATIONS, SIDE_QUEST_ENEMIES, SIDE_QUEST_MATERIALS, SIDE_QUEST_PLACES,
    DAILY_QUEST_COUNT, get_available_main_quests, get_main_quest_by_id,
    get_main_quest_chapter, get_chapter_name
)


class Quest:
    """玩家任务实例"""

    def __init__(self, quest_id: str, player_id: str, quest_data: Dict[str, Any],
                 current_progress: int = 0, status: str = "active"):
        self.id = quest_id
        self.player_id = player_id
        self.name = quest_data.get("name", "")
        self.description = quest_data.get("description", "")
        self.quest_type = quest_data.get("quest_type", "side")
        self.objective_type = quest_data.get("objective_type", "cultivation")
        self.objective_target = quest_data.get("objective_target", "")
        self.objective_count = quest_data.get("objective_count", 1)
        self.rewards = quest_data.get("rewards", {})
        self.current_progress = current_progress
        self.status = status  # active, completed, claimed
        self.accepted_at = quest_data.get("accepted_at", datetime.now().isoformat())
        self.expires_at = quest_data.get("expires_at")

    @property
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        return self.current_progress >= self.objective_count

    @property
    def progress_percent(self) -> float:
        """获取进度百分比"""
        if self.objective_count <= 0:
            return 100.0
        return min(100.0, (self.current_progress / self.objective_count) * 100)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type,
            "objective_type": self.objective_type,
            "objective_target": self.objective_target,
            "objective_count": self.objective_count,
            "current_progress": self.current_progress,
            "status": self.status,
            "rewards": self.rewards,
            "progress_percent": self.progress_percent,
            "is_completed": self.is_completed,
            "accepted_at": self.accepted_at,
            "expires_at": self.expires_at
        }


class QuestManager:
    """任务管理器"""

    def __init__(self, player_id: str, player=None):
        self.player_id = player_id
        self.player = player
        self.db = Database()
        self._active_quests: Dict[str, Quest] = {}
        self._completed_quests: List[str] = []
        self._daily_quests_generated_today = False

        # 初始化数据库表
        self.db.init_quest_tables()

        # 初始化主线任务模板到数据库
        self._init_main_quests()

        # 加载玩家任务数据
        self._load_player_quests()

    def _init_main_quests(self):
        """初始化主线任务模板到数据库"""
        for quest_template in MAIN_QUESTS:
            self.db.save_quest_template(quest_template.to_dict())

    def _load_player_quests(self):
        """加载玩家任务数据"""
        # 加载进行中的任务
        active_quests_data = self.db.get_player_quests(self.player_id, status="active")
        for quest_data in active_quests_data:
            template = self.db.get_quest_template(quest_data["quest_id"])
            if template:
                template["accepted_at"] = quest_data["accepted_at"]
                template["expires_at"] = quest_data["expires_at"]
                quest = Quest(
                    quest_id=quest_data["quest_id"],
                    player_id=self.player_id,
                    quest_data=template,
                    current_progress=quest_data["current_progress"],
                    status=quest_data["status"]
                )
                self._active_quests[quest_data["quest_id"]] = quest

        # 加载已完成的任务历史
        completed_data = self.db.get_player_quests(self.player_id, status="claimed")
        for quest_data in completed_data:
            if quest_data["quest_id"] not in self._completed_quests:
                self._completed_quests.append(quest_data["quest_id"])

        # 检查日常任务是否需要刷新
        self._check_daily_refresh()

    def _check_daily_refresh(self):
        """检查日常任务是否需要刷新"""
        last_refresh = self.db.get_last_daily_refresh(self.player_id)
        if last_refresh:
            last_date = datetime.fromisoformat(last_refresh).date()
            today = datetime.now().date()
            if last_date < today:
                self._daily_quests_generated_today = False
            else:
                self._daily_quests_generated_today = True
        else:
            self._daily_quests_generated_today = False

    # ==================== 任务查询 ====================

    def get_active_quests(self, quest_type: str = None) -> List[Quest]:
        """
        获取进行中的任务

        Args:
            quest_type: 任务类型筛选（main/side/daily）

        Returns:
            任务列表
        """
        if quest_type:
            return [q for q in self._active_quests.values() if q.quest_type == quest_type]
        return list(self._active_quests.values())

    def get_available_main_quests(self) -> List[QuestTemplate]:
        """获取可接取的主线任务"""
        player_level = self.player.stats.realm_level if self.player else 0
        return get_available_main_quests(player_level, self._completed_quests)

    def get_available_side_quests(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        获取可接取的支线任务列表

        Args:
            count: 返回数量

        Returns:
            支线任务列表
        """
        quests = []
        for _ in range(count):
            quest = self._generate_side_quest()
            if quest:
                quests.append(quest)
        return quests

    def get_available_daily_quests(self) -> List[Dict[str, Any]]:
        """获取可接取的日常任务"""
        if not self._daily_quests_generated_today:
            # 生成新的日常任务
            quests = self._generate_daily_quests()
            self._daily_quests_generated_today = True
            self.db.update_daily_refresh(self.player_id)
            return quests

        # 返回已生成的日常任务
        daily_quests = self.get_active_quests("daily")
        return [q.to_dict() for q in daily_quests]

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """获取指定任务"""
        return self._active_quests.get(quest_id)

    def has_active_quest(self, quest_id: str) -> bool:
        """检查是否有进行中的指定任务"""
        return quest_id in self._active_quests

    def has_completed_quest(self, quest_id: str) -> bool:
        """检查是否已完成指定任务"""
        return quest_id in self._completed_quests

    # ==================== 任务操作 ====================

    def accept_quest(self, quest_id: str, quest_type: str = None) -> Tuple[bool, str]:
        """
        接受任务

        Args:
            quest_id: 任务ID
            quest_type: 任务类型

        Returns:
            (是否成功, 消息)
        """
        # 检查是否已接取
        if self.has_active_quest(quest_id):
            return False, "你已经接取了该任务"

        # 检查是否已完成（非重复任务）
        if self.has_completed_quest(quest_id):
            template = self.db.get_quest_template(quest_id)
            if template and not template.get("is_repeatable", False):
                return False, "该任务已完成，无法重复接取"

        # 获取任务模板
        template = self.db.get_quest_template(quest_id)
        if not template:
            return False, "任务不存在"

        # 检查等级要求
        player_level = self.player.stats.realm_level if self.player else 0
        if template.get("min_level", 0) > player_level:
            return False, f"境界不足，需要{template['min_level']}级境界"

        # 检查前置任务
        pre_quest_id = template.get("pre_quest_id")
        if pre_quest_id and not self.has_completed_quest(pre_quest_id):
            return False, "需要先完成前置任务"

        # 计算过期时间（日常任务）
        expires_at = None
        if quest_type == "daily" or template.get("quest_type") == "daily":
            tomorrow = datetime.now() + timedelta(days=1)
            expires_at = tomorrow.replace(hour=0, minute=0, second=0).isoformat()

        # 保存到数据库
        success = self.db.accept_quest(
            self.player_id,
            quest_id,
            quest_type or template.get("quest_type", "side"),
            template.get("objective_count", 1),
            expires_at
        )

        if success:
            # 创建任务实例
            quest = Quest(
                quest_id=quest_id,
                player_id=self.player_id,
                quest_data=template,
                status="active"
            )
            self._active_quests[quest_id] = quest
            return True, f"接受任务：{template['name']}"

        return False, "接受任务失败"

    def abandon_quest(self, quest_id: str) -> Tuple[bool, str]:
        """
        放弃任务

        Args:
            quest_id: 任务ID

        Returns:
            (是否成功, 消息)
        """
        if not self.has_active_quest(quest_id):
            return False, "你没有进行中的该任务"

        success = self.db.abandon_quest(self.player_id, quest_id)
        if success:
            quest = self._active_quests.pop(quest_id)
            return True, f"放弃任务：{quest.name}"

        return False, "放弃任务失败"

    def update_progress(self, objective_type: str, objective_target: str, amount: int = 1) -> List[str]:
        """
        更新任务进度

        Args:
            objective_type: 目标类型
            objective_target: 目标对象
            amount: 增加的数量

        Returns:
            完成的任务名称列表
        """
        completed_quests = []

        for quest in self._active_quests.values():
            if quest.status != "active":
                continue

            # 检查目标类型和对象是否匹配
            if quest.objective_type == objective_type:
                # 如果是通用目标或匹配特定目标
                if quest.objective_target == objective_target or quest.objective_target in ["practice", "defeat_monster", "collect_material", "explore"]:
                    # 更新进度
                    new_progress = min(quest.objective_count, quest.current_progress + amount)

                    if new_progress != quest.current_progress:
                        quest.current_progress = new_progress
                        self.db.update_quest_progress(self.player_id, quest.id, new_progress)

                        # 检查是否完成
                        if quest.is_completed and quest.status == "active":
                            self._complete_quest(quest)
                            completed_quests.append(quest.name)

        return completed_quests

    def _complete_quest(self, quest: Quest):
        """完成任务"""
        quest.status = "completed"
        self.db.complete_quest(self.player_id, quest.id)

        # 如果是主线任务，记录到已完成列表
        if quest.quest_type == "main":
            if quest.id not in self._completed_quests:
                self._completed_quests.append(quest.id)

    def claim_reward(self, quest_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        领取任务奖励

        Args:
            quest_id: 任务ID

        Returns:
            (是否成功, 消息, 奖励详情)
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return False, "任务不存在", {}

        if quest.status != "completed":
            return False, "任务尚未完成", {}

        # 发放奖励
        rewards = quest.rewards
        reward_details = {
            "exp": 0,
            "spirit_stones": 0,
            "items": [],
            "techniques": [],
            "reputation": 0,
            "karma": 0
        }

        if self.player:
            # 经验奖励
            exp = rewards.get("exp", 0)
            if exp > 0:
                self.player.add_exp(exp)
                reward_details["exp"] = exp

            # 灵石奖励
            spirit_stones = rewards.get("spirit_stones", 0)
            if spirit_stones > 0:
                self.player.stats.spirit_stones += spirit_stones
                reward_details["spirit_stones"] = spirit_stones

            # 道具奖励
            items = rewards.get("items", [])
            for item in items:
                item_name = item.get("name", "")
                item_count = item.get("count", 1)
                self.player.add_item(item_name, item_count)
                reward_details["items"].append({"name": item_name, "count": item_count})

            # 功法奖励
            techniques = rewards.get("techniques", [])
            for tech_name in techniques:
                success, msg = self.player.learn_technique(tech_name)
                if success:
                    reward_details["techniques"].append(tech_name)

            # 声望奖励
            reputation = rewards.get("reputation", 0)
            if reputation > 0:
                # 这里可以添加到玩家的声望系统
                reward_details["reputation"] = reputation

            # 业力奖励
            karma = rewards.get("karma", 0)
            if karma != 0:
                self.player.add_karma(karma)
                reward_details["karma"] = karma

        # 标记为已领取
        self.db.claim_quest_reward(self.player_id, quest_id)
        quest.status = "claimed"

        # 从活跃任务中移除
        if quest_id in self._active_quests:
            del self._active_quests[quest_id]

        return True, f"领取奖励：{quest.name}", reward_details

    # ==================== 任务生成 ====================

    def _generate_side_quest(self) -> Optional[Dict[str, Any]]:
        """生成随机支线任务"""
        if not SIDE_QUEST_TEMPLATES:
            return None

        # 随机选择模板
        template = random.choice(SIDE_QUEST_TEMPLATES)

        # 生成任务名称
        name_prefix = random.choice(template.get("name_prefix", [""]))
        name_suffix = random.choice(template.get("name_suffix", [""]))
        quest_name = f"{name_prefix}{name_suffix}"

        # 生成任务描述
        desc_template = random.choice(template.get("description_templates", [""]))
        location = random.choice(SIDE_QUEST_LOCATIONS)
        enemy = random.choice(SIDE_QUEST_ENEMIES)
        material = random.choice(SIDE_QUEST_MATERIALS)
        place = random.choice(SIDE_QUEST_PLACES)
        count = random.randint(template.get("min_count", 1), template.get("max_count", 5))

        description = desc_template.format(
            location=location,
            enemy=enemy,
            material=material,
            place=place,
            count=count
        )

        # 生成奖励
        rewards_config = template.get("rewards", {})
        player_level = self.player.stats.realm_level if self.player else 1
        level_multiplier = 1 + player_level * 0.2

        exp = int(count * rewards_config.get("exp_multiplier", 10) * level_multiplier)
        spirit_stones = int(count * rewards_config.get("spirit_stones_multiplier", 5) * level_multiplier)
        reputation_range = rewards_config.get("reputation_range", [5, 10])
        reputation = random.randint(reputation_range[0], reputation_range[1])

        rewards = {
            "exp": exp,
            "spirit_stones": spirit_stones,
            "reputation": reputation,
            "items": []
        }

        # 业力奖励（如果有）
        karma_range = rewards_config.get("karma_range")
        if karma_range:
            rewards["karma"] = random.randint(karma_range[0], karma_range[1])

        # 生成任务ID
        quest_id = f"side_{uuid.uuid4().hex[:8]}"

        return {
            "id": quest_id,
            "name": quest_name,
            "description": description,
            "quest_type": "side",
            "objective_type": template["objective_type"].value,
            "objective_target": template["objective_target"],
            "objective_count": count,
            "rewards": rewards,
            "location": location
        }

    def _generate_daily_quests(self) -> List[Dict[str, Any]]:
        """生成日常任务"""
        quests = []
        selected_templates = random.sample(DAILY_QUEST_TEMPLATES, min(DAILY_QUEST_COUNT, len(DAILY_QUEST_TEMPLATES)))

        for template in selected_templates:
            count = random.randint(template.get("min_count", 1), template.get("max_count", 3))

            # 生成描述
            description = template["description"].format(count=count)

            # 获取奖励
            rewards_config = template.get("rewards", {})

            quest_id = f"daily_{template['objective_target']}_{datetime.now().strftime('%Y%m%d')}"

            quest_data = {
                "id": quest_id,
                "name": template["name"],
                "description": description,
                "quest_type": "daily",
                "objective_type": template["objective_type"].value,
                "objective_target": template["objective_target"],
                "objective_count": count,
                "rewards": rewards_config
            }

            # 保存到数据库
            self.db.save_quest_template(quest_data)
            quests.append(quest_data)

        return quests

    # ==================== 快捷方法 ====================

    def on_practice(self, count: int = 1) -> List[str]:
        """修炼时调用，更新相关任务进度"""
        return self.update_progress("cultivation", "practice", count)

    def on_breakthrough(self) -> List[str]:
        """突破时调用，更新相关任务进度"""
        return self.update_progress("cultivation", "breakthrough", 1)

    def on_defeat_monster(self, count: int = 1) -> List[str]:
        """击败妖兽时调用，更新相关任务进度"""
        return self.update_progress("combat", "defeat_monster", count)

    def on_collect_material(self, count: int = 1) -> List[str]:
        """收集材料时调用，更新相关任务进度"""
        return self.update_progress("collection", "collect_material", count)

    def on_explore(self, location: str) -> List[str]:
        """探索时调用，更新相关任务进度"""
        completed = self.update_progress("exploration", "explore_location", 1)
        completed.extend(self.update_progress("exploration", location, 1))
        return completed

    def get_chapter_progress(self) -> Dict[str, Any]:
        """获取当前章节进度"""
        # 找到当前进行中的主线任务
        main_quests = self.get_active_quests("main")
        if main_quests:
            current_quest = main_quests[0]
            chapter = get_main_quest_chapter(current_quest.id)
            return {
                "chapter": chapter,
                "chapter_name": get_chapter_name(chapter),
                "current_quest": current_quest.name,
                "progress": current_quest.progress_percent
            }

        # 检查是否有可接取的主线任务
        available = self.get_available_main_quests()
        if available:
            next_quest = available[0]
            chapter = get_main_quest_chapter(next_quest.id)
            return {
                "chapter": chapter,
                "chapter_name": get_chapter_name(chapter),
                "current_quest": "无",
                "next_quest": next_quest.name,
                "progress": 0
            }

        # 所有主线任务已完成
        return {
            "chapter": 5,
            "chapter_name": get_chapter_name(5),
            "current_quest": "已完成所有主线任务",
            "progress": 100
        }

    def get_summary(self) -> Dict[str, Any]:
        """获取任务系统摘要"""
        active = self.get_active_quests()
        main_active = [q for q in active if q.quest_type == "main"]
        side_active = [q for q in active if q.quest_type == "side"]
        daily_active = [q for q in active if q.quest_type == "daily"]

        chapter_progress = self.get_chapter_progress()

        return {
            "active_count": len(active),
            "main_active": len(main_active),
            "side_active": len(side_active),
            "daily_active": len(daily_active),
            "completed_count": len(self._completed_quests),
            "chapter_progress": chapter_progress
        }
