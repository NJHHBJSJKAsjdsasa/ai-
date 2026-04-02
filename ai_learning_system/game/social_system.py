"""
社交系统模块
管理道侣、师徒、好友、仇敌等社交关系
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid

from config.social_config import (
    RelationType, InteractionType,
    can_become_dao_lv, can_become_apprentice,
    calculate_dual_cultivation_exp,
    get_dao_lv_bonuses, get_master_apprentice_bonuses,
    get_intimacy_level, get_trust_level, get_hatred_level,
    FRIEND_INTERACTIONS, ENEMY_INTERACTIONS,
    REVENGE_QUEST_TEMPLATES, INTIMACY_LEVELS
)


@dataclass
class SocialRelation:
    """社交关系数据类"""
    id: int
    player_name: str
    target_name: str
    relation_type: str
    intimacy: int = 0
    trust: int = 0
    hatred: int = 0
    created_at: str = ""
    updated_at: str = ""
    notes: str = ""


@dataclass
class MarriageInfo:
    """道侣关系数据类"""
    id: int
    partner_name: str
    marriage_type: str
    marriage_date: str
    intimacy: int = 100
    dual_cultivation_count: int = 0
    last_dual_cultivation: Optional[str] = None
    benefits: Dict = field(default_factory=dict)


@dataclass
class MasterApprenticeInfo:
    """师徒关系数据类"""
    id: int
    master_name: Optional[str] = None
    apprentice_name: Optional[str] = None
    relation_type: str = "师徒"
    established_date: str = ""
    respect: int = 50
    teaching_count: int = 0
    last_teaching: Optional[str] = None
    techniques_taught: List[str] = field(default_factory=list)


@dataclass
class RevengeQuest:
    """复仇任务数据类"""
    id: int
    enemy_name: str
    conflict_reason: str
    hatred_level: int
    created_at: str
    revenge_target: str
    is_completed: bool = False
    completed_at: Optional[str] = None
    revenge_result: Optional[str] = None


class SocialManager:
    """社交管理器"""

    def __init__(self):
        self._db = None
        self._dual_cultivation_cooldowns: Dict[str, datetime] = {}

    def _get_db(self):
        """获取数据库实例"""
        if self._db is None:
            from storage.database import Database
            self._db = Database()
            self._db.init_social_tables()
        return self._db

    def initialize_social_system(self):
        """初始化社交系统"""
        db = self._get_db()
        db.init_social_tables()

    # ==================== 好友系统 ====================

    def add_friend(self, player_name: str, friend_name: str,
                   intimacy: int = 30, trust: int = 40) -> Tuple[bool, str]:
        """
        添加好友

        Args:
            player_name: 玩家名称
            friend_name: 好友名称
            intimacy: 初始亲密度
            trust: 初始信任度

        Returns:
            (是否成功, 消息)
        """
        if player_name == friend_name:
            return False, "不能添加自己为好友"

        db = self._get_db()

        # 检查NPC是否存在
        npc = db.get_npc_by_name(friend_name)
        if not npc:
            return False, f"NPC '{friend_name}' 不存在，无法添加为好友。请先确保该NPC存在于游戏中。"

        # 检查是否已经是好友
        relations = db.get_social_relations(player_name, '好友')
        for r in relations:
            if r['target_name'] == friend_name:
                return False, f"{friend_name}已经是你的好友了"

        # 添加双向好友关系
        db.add_social_relation(player_name, friend_name, '好友', intimacy, trust, 0)
        db.add_social_relation(friend_name, player_name, '好友', intimacy, trust, 0)

        return True, f"成功添加{friend_name}为好友"

    def get_friends(self, player_name: str) -> List[Dict[str, Any]]:
        """
        获取好友列表

        Args:
            player_name: 玩家名称

        Returns:
            好友列表
        """
        db = self._get_db()
        return db.get_social_relations(player_name, '好友')

    def remove_friend(self, player_name: str, friend_name: str) -> Tuple[bool, str]:
        """
        移除好友

        Args:
            player_name: 玩家名称
            friend_name: 好友名称

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        # 移除双向关系
        db.remove_social_relation(player_name, friend_name, '好友')
        db.remove_social_relation(friend_name, player_name, '好友')

        return True, f"已将{friend_name}从好友列表中移除"

    def interact_with_friend(self, player_name: str, friend_name: str,
                            interaction_type: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        与好友互动

        Args:
            player_name: 玩家名称
            friend_name: 好友名称
            interaction_type: 互动类型 (chat/gift/help/duel/discuss_dao/cultivate_together)

        Returns:
            (是否成功, 消息, 变化数据)
        """
        db = self._get_db()

        # 获取互动配置
        config = FRIEND_INTERACTIONS.get(interaction_type)
        if not config:
            return False, "未知的互动类型", {}

        # 记录互动
        description = f"{player_name}与{friend_name}进行了{config.get('name', interaction_type)}"
        db.record_social_interaction(
            player_name, friend_name,
            interaction_type,
            description,
            config['intimacy_change'],
            config['trust_change'],
            0
        )

        # 构建变化数据
        changes = {
            'intimacy_change': config['intimacy_change'],
            'trust_change': config['trust_change'],
            'exp_bonus': config.get('exp_bonus', 0),
            'cultivation_bonus': config.get('cultivation_bonus', 0),
        }

        # 处理特殊互动类型的额外效果
        extra_effects = []

        if interaction_type == 'duel':
            # 切磋：获得战斗经验
            exp_gain = config.get('exp_bonus', 0)
            if exp_gain > 0:
                extra_effects.append(f"战斗经验+{exp_gain}")
                # TODO: 实际增加玩家战斗经验

        elif interaction_type == 'discuss_dao':
            # 论道：获得修炼感悟
            insight = config.get('insight_bonus', 0)
            if insight > 0:
                extra_effects.append(f"修炼感悟+{insight}")
                changes['insight_bonus'] = insight
            # 论道提供持续的修炼加成
            cult_bonus = config.get('cultivation_bonus', 0)
            if cult_bonus > 0:
                extra_effects.append(f"修炼效率提升{cult_bonus*100:.0f}%（持续）")

        elif interaction_type == 'cultivate_together':
            # 共修：双方获得修炼效率提升
            cult_bonus = config.get('cultivation_bonus', 0)
            if cult_bonus > 0:
                extra_effects.append(f"本次修炼效率提升{cult_bonus*100:.0f}%")
            exp_gain = config.get('exp_bonus', 0)
            if exp_gain > 0:
                extra_effects.append(f"经验+{exp_gain}")

        # 构建成功消息
        msg = f"{config.get('name', '互动')}成功！\n"
        msg += f"亲密度+{config['intimacy_change']}，信任度+{config['trust_change']}"

        if extra_effects:
            msg += "\n" + "，".join(extra_effects)

        return True, msg, changes

    # ==================== 道侣系统 ====================

    def propose_dao_lv(self, player_name: str, target_name: str,
                      player_realm: int, target_realm: int) -> Tuple[bool, str]:
        """
        提议结为道侣

        Args:
            player_name: 玩家名称
            target_name: 目标名称
            player_realm: 玩家境界
            target_realm: 目标境界

        Returns:
            (是否成功, 消息)
        """
        if player_name == target_name:
            return False, "不能与自己结为道侣"

        db = self._get_db()

        # 检查是否已经有道侣
        existing = db.get_marriage(player_name)
        if existing:
            return False, f"你已经有道侣了（{existing['partner_name']}）"

        target_existing = db.get_marriage(target_name)
        if target_existing:
            return False, f"{target_name}已经有道侣了"

        # 检查亲密度和信任度
        relations = db.get_social_relations(player_name)
        relation = None
        for r in relations:
            if r['target_name'] == target_name:
                relation = r
                break

        if not relation:
            return False, f"你与{target_name}还不够熟悉，请先建立友谊"

        if not can_become_dao_lv(relation['intimacy'], relation['trust'], relation['hatred']):
            return False, (f"条件不满足：需要亲密度≥80且信任度≥70\n"
                          f"当前：亲密度{relation['intimacy']}，信任度{relation['trust']}")

        # 创建道侣关系
        if db.create_marriage(player_name, target_name, '道侣'):
            return True, f"恭喜！你与{target_name}正式结为道侣！"
        return False, "结为道侣失败"

    def get_dao_lv_info(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        获取道侣信息

        Args:
            player_name: 玩家名称

        Returns:
            道侣信息
        """
        db = self._get_db()
        return db.get_marriage(player_name)

    def dual_cultivation(self, player_name: str, player_realm: int,
                        location: str = "洞府") -> Tuple[bool, str, Dict[str, Any]]:
        """
        进行双修

        Args:
            player_name: 玩家名称
            player_realm: 玩家境界
            location: 地点

        Returns:
            (是否成功, 消息, 收益数据)
        """
        db = self._get_db()

        # 检查是否有道侣
        marriage = db.get_marriage(player_name)
        if not marriage:
            return False, "你没有道侣，无法进行双修", {}

        # 检查冷却时间
        cooldown_key = f"{player_name}_{marriage['partner_name']}"
        last_time = self._dual_cultivation_cooldowns.get(cooldown_key)
        if last_time:
            cooldown_hours = 8
            if datetime.now() - last_time < timedelta(hours=cooldown_hours):
                remaining = cooldown_hours - (datetime.now() - last_time).total_seconds() / 3600
                return False, f"双修冷却中，还需等待{remaining:.1f}小时", {}

        # 计算收益
        base_exp = 100
        realm_diff = 0  # 假设道侣同境界
        exp_gained = calculate_dual_cultivation_exp(base_exp, marriage['intimacy'], realm_diff)
        intimacy_increase = 5

        # 记录双修
        benefits = {
            'cultivation_speed_bonus': 0.15,
            'exp_bonus': 0.20,
        }

        db.record_dual_cultivation(
            player_name, marriage['partner_name'],
            exp_gained, intimacy_increase, benefits, location
        )

        # 更新冷却时间
        self._dual_cultivation_cooldowns[cooldown_key] = datetime.now()

        result = {
            'exp_gained': exp_gained,
            'intimacy_increase': intimacy_increase,
            'new_intimacy': marriage['intimacy'] + intimacy_increase,
        }

        return True, f"双修成功！获得修为{exp_gained}，亲密度+{intimacy_increase}", result

    def divorce(self, player_name: str, reason: str = "") -> Tuple[bool, str]:
        """
        解除道侣关系

        Args:
            player_name: 玩家名称
            reason: 解除原因

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        marriage = db.get_marriage(player_name)
        if not marriage:
            return False, "你没有道侣"

        partner_name = marriage['partner_name']

        if db.divorce(player_name, partner_name, reason):
            return True, f"你与{partner_name}的道侣关系已解除"
        return False, "解除道侣关系失败"

    def get_dao_lv_bonuses(self) -> Dict[str, Any]:
        """获取道侣加成"""
        return get_dao_lv_bonuses()

    # ==================== 师徒系统 ====================

    def accept_apprentice(self, master_name: str, apprentice_name: str,
                         master_realm: int, apprentice_realm: int) -> Tuple[bool, str]:
        """
        收徒

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            master_realm: 师父境界
            apprentice_realm: 徒弟境界

        Returns:
            (是否成功, 消息)
        """
        if master_name == apprentice_name:
            return False, "不能收自己为徒"

        db = self._get_db()

        # 检查师父境界
        if master_realm < 2:  # 筑基期
            return False, "你的境界不足，需要达到筑基期才能收徒"

        # 检查徒弟是否已有师父
        existing_master = db.get_master(apprentice_name)
        if existing_master:
            return False, f"{apprentice_name}已经有师父了"

        # 检查亲密度和信任度
        relations = db.get_social_relations(master_name)
        relation = None
        for r in relations:
            if r['target_name'] == apprentice_name:
                relation = r
                break

        if not relation:
            return False, f"你与{apprentice_name}还不够熟悉"

        if not can_become_apprentice(relation['intimacy'], relation['trust'], master_realm, apprentice_realm):
            return False, (f"条件不满足：需要亲密度≥30，信任度≥40，且境界差距不超过2级\n"
                          f"当前：亲密度{relation['intimacy']}，信任度{relation['trust']}")

        # 建立师徒关系
        if db.establish_master_apprentice(master_name, apprentice_name, '师徒'):
            return True, f"成功收{apprentice_name}为徒"
        return False, "收徒失败"

    def get_master(self, apprentice_name: str) -> Optional[Dict[str, Any]]:
        """
        获取师父信息

        Args:
            apprentice_name: 徒弟名称

        Returns:
            师父信息
        """
        db = self._get_db()
        return db.get_master(apprentice_name)

    def get_apprentices(self, master_name: str) -> List[Dict[str, Any]]:
        """
        获取徒弟列表

        Args:
            master_name: 师父名称

        Returns:
            徒弟列表
        """
        db = self._get_db()
        return db.get_apprentices(master_name)

    def teach_technique(self, master_name: str, apprentice_name: str,
                       technique_name: str) -> Tuple[bool, str]:
        """
        传授功法

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            technique_name: 功法名称

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        # 检查师徒关系
        apprentices = db.get_apprentices(master_name)
        apprentice = None
        for a in apprentices:
            if a['apprentice_name'] == apprentice_name:
                apprentice = a
                break

        if not apprentice:
            return False, f"{apprentice_name}不是你的徒弟"

        # 传授功法
        if db.teach_technique(master_name, apprentice_name, technique_name):
            return True, f"成功将{technique_name}传授给{apprentice_name}"
        return False, "传授功法失败"

    def expel_apprentice(self, master_name: str, apprentice_name: str,
                        reason: str = "") -> Tuple[bool, str]:
        """
        逐出师门

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            reason: 原因

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        if db.end_master_apprentice(master_name, apprentice_name, reason):
            return True, f"已将{apprentice_name}逐出师门"
        return False, "操作失败"

    def leave_master(self, apprentice_name: str, reason: str = "") -> Tuple[bool, str]:
        """
        叛出师门

        Args:
            apprentice_name: 徒弟名称
            reason: 原因

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        master_info = db.get_master(apprentice_name)
        if not master_info:
            return False, "你没有师父"

        if db.end_master_apprentice(master_info['master_name'], apprentice_name, reason):
            return True, f"你已离开师门"
        return False, "操作失败"

    def get_master_apprentice_bonuses(self) -> Dict[str, Any]:
        """获取师徒加成"""
        return get_master_apprentice_bonuses()

    # ==================== 仇敌系统 ====================

    def add_enemy(self, player_name: str, enemy_name: str,
                  reason: str, hatred_level: int = 50) -> Tuple[bool, str]:
        """
        添加仇敌

        Args:
            player_name: 玩家名称
            enemy_name: 仇敌名称
            reason: 结仇原因
            hatred_level: 仇恨等级

        Returns:
            (是否成功, 消息)
        """
        if player_name == enemy_name:
            return False, "不能与自己为敌"

        db = self._get_db()

        # 创建复仇记录
        if db.create_revenge_record(player_name, enemy_name, reason, hatred_level):
            return True, f"已将{enemy_name}记为仇敌"
        return False, "添加仇敌失败"

    def get_enemies(self, player_name: str, is_completed: bool = None) -> List[Dict[str, Any]]:
        """
        获取仇敌列表

        Args:
            player_name: 玩家名称
            is_completed: 是否已完成复仇

        Returns:
            仇敌列表
        """
        db = self._get_db()
        return db.get_revenge_records(player_name, is_completed)

    def create_revenge_quest(self, player_name: str, enemy_name: str) -> Optional[Dict[str, Any]]:
        """
        创建复仇任务

        Args:
            player_name: 玩家名称
            enemy_name: 仇敌名称

        Returns:
            任务信息
        """
        enemies = self.get_enemies(player_name, is_completed=False)
        enemy = None
        for e in enemies:
            if e['enemy_name'] == enemy_name:
                enemy = e
                break

        if not enemy:
            return None

        # 选择复仇任务模板
        import random
        template = random.choice(REVENGE_QUEST_TEMPLATES)

        quest = {
            'id': enemy['id'],
            'name': template['name'],
            'description': template['description'].format(name=enemy_name),
            'enemy_name': enemy_name,
            'hatred_level': enemy['hatred_level'],
            'rewards': template['rewards'],
        }

        return quest

    def complete_revenge(self, player_name: str, enemy_name: str,
                        result: str = "") -> Tuple[bool, str]:
        """
        完成复仇

        Args:
            player_name: 玩家名称
            enemy_name: 仇敌名称
            result: 复仇结果

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        enemies = db.get_revenge_records(player_name, is_completed=False)
        enemy = None
        for e in enemies:
            if e['enemy_name'] == enemy_name:
                enemy = e
                break

        if not enemy:
            return False, "未找到该仇敌的复仇记录"

        if db.complete_revenge(enemy['id'], result):
            return True, f"复仇完成！{result}"
        return False, "完成复仇记录失败"

    def forgive_enemy(self, player_name: str, enemy_name: str) -> Tuple[bool, str]:
        """
        原谅仇敌

        Args:
            player_name: 玩家名称
            enemy_name: 仇敌名称

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        # 更新仇敌关系为旧识
        db.add_social_relation(player_name, enemy_name, '旧识', 20, 30, 10, "曾经的仇敌，现已和解")
        db.add_social_relation(enemy_name, player_name, '旧识', 20, 30, 10, "曾经的仇敌，现已和解")

        # 完成复仇记录
        enemies = db.get_revenge_records(player_name, is_completed=False)
        for e in enemies:
            if e['enemy_name'] == enemy_name:
                db.complete_revenge(e['id'], "双方和解")
                break

        return True, f"你已原谅{enemy_name}，恩怨一笔勾销"

    # ==================== 社交关系通用方法 ====================

    def get_all_relations(self, player_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有社交关系

        Args:
            player_name: 玩家名称

        Returns:
            分类的社交关系
        """
        db = self._get_db()

        all_relations = db.get_social_relations(player_name)

        result = {
            'friends': [],
            'dao_lv': None,
            'master': None,
            'apprentices': [],
            'enemies': [],
            'others': []
        }

        for relation in all_relations:
            relation_type = relation['relation_type']
            if relation_type == '好友':
                result['friends'].append(relation)
            elif relation_type == '道侣':
                result['dao_lv'] = relation
            elif relation_type == '师徒':
                if relation['player_name'] == player_name:
                    # 这是徒弟视角
                    result['master'] = relation
                else:
                    # 这是师父视角
                    result['apprentices'].append(relation)
            elif relation_type == '仇敌':
                result['enemies'].append(relation)
            else:
                result['others'].append(relation)

        return result

    def get_relation_level_name(self, intimacy: int, trust: int, hatred: int) -> str:
        """
        获取关系等级名称

        Args:
            intimacy: 亲密度
            trust: 信任度
            hatred: 仇恨度

        Returns:
            关系等级名称
        """
        if hatred > 50:
            return get_hatred_level(hatred)['name']
        elif intimacy > 50:
            return get_intimacy_level(intimacy)['name']
        else:
            return get_trust_level(trust)['name']

    def get_friendship_level_info(self, intimacy: int) -> Dict[str, Any]:
        """
        获取友谊等级信息

        Args:
            intimacy: 亲密度

        Returns:
            包含等级名称、进度、下一级所需亲密度等信息
        """
        # 确定当前等级
        current_level = None
        next_level = None

        for i, level in enumerate(INTIMACY_LEVELS):
            if level['min'] <= intimacy <= level['max']:
                current_level = level
                # 获取下一级
                if i < len(INTIMACY_LEVELS) - 1:
                    next_level = INTIMACY_LEVELS[i + 1]
                break

        if not current_level:
            current_level = INTIMACY_LEVELS[0]
            next_level = INTIMACY_LEVELS[1] if len(INTIMACY_LEVELS) > 1 else None

        # 计算进度
        level_range = current_level['max'] - current_level['min'] + 1
        progress_in_level = intimacy - current_level['min']
        progress_percent = (progress_in_level / level_range) * 100 if level_range > 0 else 0

        result = {
            'level_name': current_level['name'],
            'intimacy': intimacy,
            'min': current_level['min'],
            'max': current_level['max'],
            'progress_percent': min(100, max(0, progress_percent)),
            'bonus': current_level['bonus']
        }

        # 下一级信息
        if next_level:
            result['next_level_name'] = next_level['name']
            result['next_level_required'] = next_level['min']
            result['intimacy_to_next'] = next_level['min'] - intimacy
        else:
            result['next_level_name'] = '已满级'
            result['next_level_required'] = current_level['max']
            result['intimacy_to_next'] = 0

        return result

    def get_social_bonuses(self, player_name: str) -> Dict[str, Any]:
        """
        获取社交加成

        Args:
            player_name: 玩家名称

        Returns:
            加成信息
        """
        bonuses = {
            'cultivation_speed': 0.0,
            'exp_bonus': 0.0,
            'combat_bonus': 0.0,
            'breakthrough_bonus': 0.0,
        }

        db = self._get_db()

        # 道侣加成
        marriage = db.get_marriage(player_name)
        if marriage:
            dao_lv_bonuses = get_dao_lv_bonuses()
            bonuses['cultivation_speed'] += dao_lv_bonuses.get('cultivation_speed', 0)
            bonuses['exp_bonus'] += dao_lv_bonuses.get('exp_bonus', 0)
            bonuses['breakthrough_bonus'] += dao_lv_bonuses.get('breakthrough_bonus', 0)

        # 师徒加成
        master_info = db.get_master(player_name)
        if master_info:
            ma_bonuses = get_master_apprentice_bonuses()
            apprentice_bonus = ma_bonuses.get('apprentice', {})
            bonuses['cultivation_speed'] += apprentice_bonus.get('cultivation_speed', 0)
            bonuses['exp_bonus'] += apprentice_bonus.get('exp_bonus', 0)

        return bonuses


# 全局社交管理器实例
social_manager = SocialManager()


def get_social_manager() -> SocialManager:
    """获取社交管理器实例"""
    return social_manager


if __name__ == "__main__":
    # 测试社交系统
    print("=" * 60)
    print("社交系统测试")
    print("=" * 60)

    manager = SocialManager()
    manager.initialize_social_system()

    print("\n【测试好友系统】")
    success, msg = manager.add_friend("韩立", "南宫婉", 50, 60)
    print(f"  添加好友: {msg}")

    friends = manager.get_friends("韩立")
    print(f"  好友数量: {len(friends)}")

    print("\n【测试道侣系统】")
    success, msg = manager.propose_dao_lv("韩立", "南宫婉", 5, 5)
    print(f"  结为道侣: {msg}")

    dao_lv_info = manager.get_dao_lv_info("韩立")
    if dao_lv_info:
        print(f"  道侣: {dao_lv_info['partner_name']}")

    print("\n【测试师徒系统】")
    success, msg = manager.accept_apprentice("韩立", "厉飞雨", 6, 3)
    print(f"  收徒: {msg}")

    apprentices = manager.get_apprentices("韩立")
    print(f"  徒弟数量: {len(apprentices)}")

    print("\n【测试仇敌系统】")
    success, msg = manager.add_enemy("韩立", "王蝉", "争夺宝物", 70)
    print(f"  添加仇敌: {msg}")

    enemies = manager.get_enemies("韩立")
    print(f"  仇敌数量: {len(enemies)}")

    print("\n【测试加成】")
    bonuses = manager.get_social_bonuses("韩立")
    print(f"  修炼速度加成: {bonuses['cultivation_speed']*100:.0f}%")
    print(f"  经验加成: {bonuses['exp_bonus']*100:.0f}%")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
