"""
成就系统模块
管理成就的检测、解锁、奖励发放等功能
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from config.achievement_config import (
    AchievementCategory, AchievementTier, AchievementConditionType,
    AchievementTemplate, AchievementReward, ALL_ACHIEVEMENTS,
    get_achievement_by_id, get_achievements_by_category,
    get_category_name, get_tier_name, get_tier_color, get_tier_point_value
)


@dataclass
class AchievementUnlockEvent:
    """成就解锁事件"""
    achievement_id: str
    achievement_name: str
    tier: str
    icon: str
    description: str
    rewards: Dict[str, Any]
    unlocked_at: str


class AchievementManager:
    """成就管理器"""

    def __init__(self, db: Database):
        self.db = db
        self._achievement_templates: Dict[str, AchievementTemplate] = {}
        self._initialized = False
        self._event_handlers: List[Callable] = []

    def initialize(self):
        """初始化成就系统"""
        if self._initialized:
            return

        # 创建数据库表
        self.db.init_achievement_tables()

        # 加载成就模板到数据库
        self._load_achievement_templates()

        self._initialized = True

    def _load_achievement_templates(self):
        """加载成就模板到数据库"""
        for template in ALL_ACHIEVEMENTS:
            self._achievement_templates[template.id] = template
            self.db.save_achievement_template(template.to_dict())

    def initialize_player_achievements(self, player_id: str) -> bool:
        """
        初始化玩家的成就数据

        Args:
            player_id: 玩家ID

        Returns:
            是否成功
        """
        if not self._initialized:
            self.initialize()

        # 获取所有成就模板
        templates = [t.to_dict() for t in ALL_ACHIEVEMENTS]

        # 初始化玩家成就进度
        return self.db.init_player_achievements(player_id, templates)

    def register_event_handler(self, handler: Callable):
        """
        注册成就解锁事件处理器

        Args:
            handler: 事件处理函数，接收 AchievementUnlockEvent 参数
        """
        self._event_handlers.append(handler)

    def _notify_unlock(self, event: AchievementUnlockEvent):
        """通知所有监听器成就解锁事件"""
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"成就解锁事件处理器错误: {e}")

    # ==================== 成就检测方法 ====================

    def check_realm_breakthrough(self, player_id: str, realm_id: str) -> List[AchievementUnlockEvent]:
        """
        检测突破境界成就

        Args:
            player_id: 玩家ID
            realm_id: 境界ID

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.REALM_BREAKTHROUGH,
            f"realm_{realm_id}",
            1
        )

    def check_practice_count(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测修炼次数成就

        Args:
            player_id: 玩家ID
            count: 当前修炼次数

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.PRACTICE_COUNT,
            "practice",
            count
        )

    def check_tribulation_success(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测渡劫成功成就

        Args:
            player_id: 玩家ID
            count: 当前渡劫成功次数

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.TRIBULATION_SUCCESS,
            "tribulation",
            count
        )

    def check_defeat_enemy(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测击败敌人成就

        Args:
            player_id: 玩家ID
            count: 当前击败敌人数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.DEFEAT_ENEMY,
            "enemy",
            count
        )

    def check_defeat_boss(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测击败BOSS成就

        Args:
            player_id: 玩家ID
            count: 当前击败BOSS数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.DEFEAT_BOSS,
            "boss",
            count
        )

    def check_win_streak(self, player_id: str, streak: int) -> List[AchievementUnlockEvent]:
        """
        检测连胜成就

        Args:
            player_id: 玩家ID
            streak: 当前连胜次数

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.WIN_STREAK,
            "streak",
            streak
        )

    def check_discover_location(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测发现地点成就

        Args:
            player_id: 玩家ID
            count: 当前发现地点数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.DISCOVER_LOCATION,
            "location",
            count
        )

    def check_explore_count(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测探索次数成就

        Args:
            player_id: 玩家ID
            count: 当前探索次数

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.EXPLORE_COUNT,
            "explore",
            count
        )

    def check_discover_secret(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测发现秘境成就

        Args:
            player_id: 玩家ID
            count: 当前发现秘境数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.DISCOVER_SECRET,
            "secret",
            count
        )

    def check_make_friend(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测结交朋友成就

        Args:
            player_id: 玩家ID
            count: 当前好友数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.MAKE_FRIEND,
            "friend",
            count
        )

    def check_find_partner(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测结交道侣成就

        Args:
            player_id: 玩家ID
            count: 当前道侣数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.FIND_PARTNER,
            "partner",
            count
        )

    def check_accept_apprentice(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测收徒成就

        Args:
            player_id: 玩家ID
            count: 当前徒弟数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.ACCEPT_APPRENTICE,
            "apprentice",
            count
        )

    def check_join_sect(self, player_id: str) -> List[AchievementUnlockEvent]:
        """
        检测加入门派成就

        Args:
            player_id: 玩家ID

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.JOIN_SECT,
            "sect",
            1
        )

    def check_sect_contribution(self, player_id: str, contribution: int) -> List[AchievementUnlockEvent]:
        """
        检测门派贡献成就

        Args:
            player_id: 玩家ID
            contribution: 当前门派贡献值

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.SECT_CONTRIBUTION,
            "contribution",
            contribution
        )

    def check_collect_item(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测收集物品成就

        Args:
            player_id: 玩家ID
            count: 当前收集物品种类数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.COLLECT_ITEM,
            "item",
            count
        )

    def check_collect_technique(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测收集功法成就

        Args:
            player_id: 玩家ID
            count: 当前学习功法数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.COLLECT_TECHNIQUE,
            "technique",
            count
        )

    def check_collect_pet(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测收集灵兽成就

        Args:
            player_id: 玩家ID
            count: 当前拥有灵兽数量

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.COLLECT_PET,
            "pet",
            count
        )

    def check_reach_level(self, player_id: str, level: int) -> List[AchievementUnlockEvent]:
        """
        检测达到等级成就

        Args:
            player_id: 玩家ID
            level: 当前等级

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.REACH_LEVEL,
            "level",
            level
        )

    def check_first_death(self, player_id: str) -> List[AchievementUnlockEvent]:
        """
        检测首次死亡成就

        Args:
            player_id: 玩家ID

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.FIRST_DEATH,
            "death",
            1
        )

    def check_rebirth(self, player_id: str, count: int) -> List[AchievementUnlockEvent]:
        """
        检测转世重生成就

        Args:
            player_id: 玩家ID
            count: 当前转世次数

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.REBIRTH,
            "rebirth",
            count
        )

    def check_special_event(self, player_id: str) -> List[AchievementUnlockEvent]:
        """
        检测特殊事件成就

        Args:
            player_id: 玩家ID

        Returns:
            解锁的成就事件列表
        """
        return self._check_and_update_progress(
            player_id,
            AchievementConditionType.SPECIAL_EVENT,
            "event",
            1
        )

    # ==================== 核心检测逻辑 ====================

    def _check_and_update_progress(self, player_id: str,
                                   condition_type: AchievementConditionType,
                                   condition_target: str,
                                   progress: int) -> List[AchievementUnlockEvent]:
        """
        检查并更新成就进度

        Args:
            player_id: 玩家ID
            condition_type: 条件类型
            condition_target: 条件目标
            progress: 当前进度

        Returns:
            解锁的成就事件列表
        """
        unlocked_events = []

        # 查找匹配的成就模板
        matching_achievements = [
            template for template in ALL_ACHIEVEMENTS
            if template.condition_type == condition_type
            and template.condition_target == condition_target
        ]

        for template in matching_achievements:
            # 更新进度
            result = self.db.update_achievement_progress(
                player_id, template.id, progress, auto_unlock=True
            )

            if result['unlocked']:
                # 创建解锁事件
                event = AchievementUnlockEvent(
                    achievement_id=template.id,
                    achievement_name=template.name,
                    tier=template.tier.value,
                    icon=template.icon,
                    description=template.description,
                    rewards=template.rewards.to_dict(),
                    unlocked_at=datetime.now().isoformat()
                )
                unlocked_events.append(event)
                self._notify_unlock(event)

        return unlocked_events

    # ==================== 成就查询方法 ====================

    def get_player_achievements(self, player_id: str, status: str = None,
                                category: str = None) -> List[Dict[str, Any]]:
        """
        获取玩家成就列表

        Args:
            player_id: 玩家ID
            status: 状态筛选
            category: 分类筛选

        Returns:
            成就列表
        """
        achievements = self.db.get_player_achievements(player_id, status)

        if category:
            achievements = [a for a in achievements if a['category'] == category]

        return achievements

    def get_player_achievement_stats(self, player_id: str) -> Dict[str, Any]:
        """
        获取玩家成就统计

        Args:
            player_id: 玩家ID

        Returns:
            成就统计数据
        """
        stats = self.db.get_player_achievement_stats(player_id)

        # 计算总成就数
        total_count = len(ALL_ACHIEVEMENTS)
        claimed_count = stats.get('total_achievements', 0)

        stats['total_available'] = total_count
        stats['completion_rate'] = (claimed_count / total_count * 100) if total_count > 0 else 0

        return stats

    def get_achievement_categories(self) -> List[Dict[str, Any]]:
        """
        获取成就分类信息

        Returns:
            分类列表
        """
        categories = []
        for category in AchievementCategory:
            achievements = get_achievements_by_category(category)
            categories.append({
                'id': category.value,
                'name': get_category_name(category),
                'count': len(achievements),
                'icon': self._get_category_icon(category)
            })
        return categories

    def _get_category_icon(self, category: AchievementCategory) -> str:
        """获取分类图标"""
        icons = {
            AchievementCategory.CULTIVATION: "🧘",
            AchievementCategory.COMBAT: "⚔️",
            AchievementCategory.EXPLORATION: "🗺️",
            AchievementCategory.SOCIAL: "👥",
            AchievementCategory.COLLECTION: "📦",
            AchievementCategory.SPECIAL: "✨"
        }
        return icons.get(category, "🏆")

    def get_tier_info(self, tier: str) -> Dict[str, Any]:
        """
        获取等级信息

        Args:
            tier: 等级代码

        Returns:
            等级信息
        """
        tier_map = {
            'bronze': AchievementTier.BRONZE,
            'silver': AchievementTier.SILVER,
            'gold': AchievementTier.GOLD,
            'diamond': AchievementTier.DIAMOND
        }

        tier_enum = tier_map.get(tier, AchievementTier.BRONZE)

        return {
            'id': tier,
            'name': get_tier_name(tier_enum),
            'color': get_tier_color(tier_enum),
            'points': get_tier_point_value(tier_enum)
        }

    def has_unclaimed_achievements(self, player_id: str) -> bool:
        """
        检查是否有未领取奖励的成就

        Args:
            player_id: 玩家ID

        Returns:
            是否有未领取的成就
        """
        return self.db.has_unclaimed_achievements(player_id)

    def get_recent_unlocked(self, player_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取最近解锁的成就

        Args:
            player_id: 玩家ID
            limit: 数量限制

        Returns:
            最近解锁的成就列表
        """
        return self.db.get_recent_unlocked_achievements(player_id, limit)

    # ==================== 奖励领取 ====================

    def claim_reward(self, player_id: str, achievement_id: str) -> Dict[str, Any]:
        """
        领取成就奖励

        Args:
            player_id: 玩家ID
            achievement_id: 成就ID

        Returns:
            领取结果
        """
        return self.db.claim_achievement_reward(player_id, achievement_id)

    def claim_all_rewards(self, player_id: str) -> Dict[str, Any]:
        """
        领取所有未领取的奖励

        Args:
            player_id: 玩家ID

        Returns:
            领取结果
        """
        # 获取所有已解锁但未领取的成就
        unlocked_achievements = self.db.get_player_achievements(player_id, status='unlocked')

        results = {
            'success_count': 0,
            'failed_count': 0,
            'total_rewards': {
                'exp': 0,
                'spirit_stones': 0,
                'karma': 0,
                'reputation': 0,
                'titles': [],
                'items': []
            }
        }

        for achievement in unlocked_achievements:
            result = self.db.claim_achievement_reward(player_id, achievement['id'])

            if result['success']:
                results['success_count'] += 1
                rewards = result['rewards']

                # 累加奖励
                results['total_rewards']['exp'] += rewards.get('exp', 0)
                results['total_rewards']['spirit_stones'] += rewards.get('spirit_stones', 0)
                results['total_rewards']['karma'] += rewards.get('karma', 0)
                results['total_rewards']['reputation'] += rewards.get('reputation', 0)

                if rewards.get('title'):
                    results['total_rewards']['titles'].append(rewards['title'])

                if rewards.get('items'):
                    results['total_rewards']['items'].extend(rewards['items'])
            else:
                results['failed_count'] += 1

        return results


# ==================== 便捷函数 ====================

def create_achievement_manager(db: Database) -> AchievementManager:
    """
    创建成就管理器实例

    Args:
        db: 数据库实例

    Returns:
        成就管理器实例
    """
    manager = AchievementManager(db)
    manager.initialize()
    return manager
