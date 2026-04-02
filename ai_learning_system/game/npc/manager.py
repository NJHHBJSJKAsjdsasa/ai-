"""
NPC管理器模块
管理多个NPC的生成、更新和交互
"""

import time
from typing import Dict, List, Optional, Any

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import GAME_CONFIG
from game.npc_independent import NPCIndependentManager
from game.npc_relationship_network import RelationType, relationship_network
from game.social_event_system import SocialEventType, get_social_event_manager

from .models import NPCData
from .core import NPC


class NPCManager:
    """NPC管理器 - 集成独立系统和关系网络"""

    def __init__(self):
        """初始化NPC管理器"""
        self.npcs: Dict[str, NPC] = {}
        self.independent_manager = NPCIndependentManager()
        self.player_location: str = "新手村"
        self.social_event_manager = get_social_event_manager()

    def generate_npcs_for_location(self, location: str, count: int = None, db=None, show_progress: bool = False) -> List[NPC]:
        """
        为地点生成NPC（如果该地点已有足够NPC则跳过）

        Args:
            location: 地点名称
            count: 数量，默认使用配置
            db: 数据库实例，如果为None则创建新实例
            show_progress: 是否显示进度条，默认为False（由上层统一显示总进度）

        Returns:
            NPC列表
        """
        if count is None:
            count = GAME_CONFIG["npc"]["npc_count_per_location"]

        # 导入数据库
        from storage.database import Database
        if db is None:
            db = Database()

        # 检查该地点是否已有足够NPC
        existing_npcs = self.get_npcs_in_location(location)
        if len(existing_npcs) >= count:
            if show_progress:
                print(f"\n[生成NPC] {location} 已有 {len(existing_npcs)} 个NPC，跳过生成\n")
            return existing_npcs
        
        # 计算需要生成的数量
        need_to_generate = count - len(existing_npcs)
        
        npcs = []
        if show_progress:
            print(f"\n[生成NPC] 正在为 {location} 生成 {need_to_generate} 个NPC...")
        
        for i in range(need_to_generate):
            npc = NPC()
            npc.data.location = location

            # 初始化所有系统数据
            npc._init_new_systems()

            # 保存到数据库
            try:
                npc.save_to_database(db)
            except Exception as e:
                if show_progress:
                    print(f"保存NPC到数据库失败: {e}")

            self.npcs[npc.data.id] = npc
            # 同时添加到独立系统管理器
            self.independent_manager.add_npc(npc.independent, location)
            npcs.append(npc)
            
            # 显示总进度条
            if show_progress:
                progress = (i + 1) / need_to_generate * 100
                filled = int((i + 1) / need_to_generate * 20)
                empty = 20 - filled
                bar = "█" * filled + "░" * empty
                print(f"\r  进度: [{bar}] {progress:.0f}% ({i+1}/{need_to_generate})", end="", flush=True)
        
        if show_progress:
            print(f"\n  ✓ 完成！共生成 {len(npcs)} 个NPC\n")

        return npcs

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """
        获取NPC

        Args:
            npc_id: NPC ID

        Returns:
            NPC对象
        """
        return self.npcs.get(npc_id)

    def get_npcs_in_location(self, location: str) -> List[NPC]:
        """
        获取地点的所有NPC

        Args:
            location: 地点名称

        Returns:
            NPC列表
        """
        return [npc for npc in self.npcs.values() if npc.data.location == location and npc.data.is_alive]

    def get_npc_by_name(self, name: str) -> Optional[NPC]:
        """
        根据名字获取NPC

        Args:
            name: NPC名字

        Returns:
            NPC对象（只返回存活的NPC）
        """
        for npc in self.npcs.values():
            if npc.data.name == name or npc.data.dao_name == name:
                # 只返回存活的NPC
                if npc.data.is_alive:
                    return npc
        return None

    def advance_time_for_all(self, days: int = 1):
        """
        为所有NPC推进时间

        Args:
            days: 天数
        """
        for npc in self.npcs.values():
            npc.advance_time(days)

    def update_all(self, current_time: float = None, player_location: str = None):
        """
        更新所有NPC（独立系统）

        Args:
            current_time: 当前时间戳
            player_location: 玩家当前位置
        """
        if current_time is None:
            current_time = time.time()
        if player_location:
            self.player_location = player_location

        # 使用独立系统管理器批量更新
        self.independent_manager.update_all(current_time, self.player_location)

        # 同时更新NPC的基础状态
        for npc in self.npcs.values():
            if npc.data.location == self.player_location:
                npc.update(current_time, player_nearby=True)

    def socialize_npcs(self, npc_id1: str, npc_id2: str):
        """
        两个NPC之间进行社交

        Args:
            npc_id1: 第一个NPC的ID
            npc_id2: 第二个NPC的ID
        """
        npc1 = self.npcs.get(npc_id1)
        npc2 = self.npcs.get(npc_id2)

        if npc1 and npc2:
            npc1.socialize_with(npc2)
            self.independent_manager.socialize_between(npc_id1, npc_id2)

            # 更新关系网络
            affinity_change = random.randint(1, 5)
            npc1.update_relationship_with(
                npc_id2,
                {"affinity": affinity_change, "intimacy": random.randint(1, 3)},
                reason="社交互动"
            )

    def get_independent_stats(self) -> Dict[str, Any]:
        """获取独立系统统计信息"""
        return self.independent_manager.get_stats()

    def pause_npc(self, npc_id: str):
        """暂停指定NPC的独立更新"""
        self.independent_manager.pause_npc(npc_id)

    def resume_npc(self, npc_id: str):
        """恢复指定NPC的独立更新"""
        self.independent_manager.resume_npc(npc_id)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            npc_id: npc.to_dict()
            for npc_id, npc in self.npcs.items()
        }

    # ==================== NPC关系管理 ====================

    def initialize_relationships(self, db=None) -> bool:
        """
        初始化所有NPC之间的关系
        基于门派、位置、性格等因素自动建立关系

        Args:
            db: 数据库实例

        Returns:
            是否成功初始化
        """
        try:
            from storage.database import Database
            if db is None:
                db = Database()

            # 确保社交表已初始化
            db.init_social_tables()

            # 加载已存在的关系
            relationship_network.load_from_database()

            # 获取所有NPC列表
            npc_list = list(self.npcs.values())
            total_pairs = 0
            created_relations = 0

            # 遍历所有NPC对
            for i, npc1 in enumerate(npc_list):
                for npc2 in npc_list[i+1:]:
                    total_pairs += 1

                    # 检查是否已有关系
                    existing_relation = relationship_network.get_relationship(npc1.data.id, npc2.data.id)
                    if existing_relation:
                        continue

                    # 计算初始关系值
                    affinity, intimacy, hatred, relation_type = self._calculate_initial_relationship(
                        npc1, npc2
                    )

                    # 如果关系值有意义，创建关系
                    if abs(affinity) > 5 or intimacy > 5 or hatred > 5:
                        relationship_network.add_relationship(
                            npc1_id=npc1.data.id,
                            npc2_id=npc2.data.id,
                            relation_type=relation_type,
                            initial_affinity=affinity,
                            initial_intimacy=intimacy,
                            initial_hatred=hatred
                        )
                        created_relations += 1

            print(f"NPC关系初始化完成：共{total_pairs}对NPC，新建{created_relations}个关系")
            return True

        except Exception as e:
            print(f"初始化NPC关系失败: {e}")
            return False

    def _calculate_initial_relationship(self, npc1: NPC, npc2: NPC) -> tuple:
        """
        计算两个NPC的初始关系值

        Args:
            npc1: 第一个NPC
            npc2: 第二个NPC

        Returns:
            (affinity, intimacy, hatred, relation_type)
        """
        affinity = 0
        intimacy = 0
        hatred = 0

        # 1. 同门派加成
        if npc1.data.sect == npc2.data.sect and npc1.data.sect:
            affinity += random.randint(10, 30)
            intimacy += random.randint(5, 15)

        # 2. 同位置加成
        if npc1.data.location == npc2.data.location and npc1.data.location:
            affinity += random.randint(5, 15)
            intimacy += random.randint(3, 10)

        # 3. 职业相关
        if npc1.data.occupation == npc2.data.occupation and npc1.data.occupation:
            affinity += random.randint(5, 20)

        # 4. 性格匹配
        personality_bonus = self._calculate_personality_compatibility(
            npc1.data.personality, npc2.data.personality
        )
        affinity += personality_bonus

        # 5. 善恶值差异
        morality_diff = abs(npc1.data.morality - npc2.data.morality)
        if morality_diff > 50:
            # 善恶差异大，可能产生敌意
            hatred += random.randint(5, 20)
            affinity -= random.randint(5, 15)
        elif morality_diff < 20:
            # 善恶相近，增加好感
            affinity += random.randint(5, 15)

        # 6. 境界差异
        realm_diff = abs(npc1.data.realm_level - npc2.data.realm_level)
        if realm_diff > 3:
            # 境界差距大，可能产生敬畏或轻视
            if npc1.data.realm_level > npc2.data.realm_level:
                affinity -= random.randint(0, 10)  # 低境界对高境界的敬畏
            else:
                affinity -= random.randint(0, 5)   # 高境界对低境界的轻视

        # 确保数值在合理范围内
        affinity = max(-50, min(50, affinity))
        intimacy = max(0, min(30, intimacy))
        hatred = max(0, min(30, hatred))

        # 确定关系类型
        if hatred >= 20:
            relation_type = RelationType.HOSTILITY
        elif affinity >= 20 and intimacy >= 10:
            relation_type = RelationType.FRIENDSHIP
        elif npc1.data.sect == npc2.data.sect and npc1.data.sect:
            relation_type = RelationType.FACTION
        elif affinity < -10:
            relation_type = RelationType.UNFRIENDLY
        else:
            relation_type = RelationType.ACQUAINTANCE

        return affinity, intimacy, hatred, relation_type

    def _calculate_personality_compatibility(self, personality1: str, personality2: str) -> int:
        """
        计算性格相容度

        Args:
            personality1: 第一个NPC的性格
            personality2: 第二个NPC的性格

        Returns:
            相容度加成值
        """
        # 性格相容性映射
        compatibility_map = {
            "豪爽": ["豪爽", "正直", "开朗", "勇敢"],
            "谨慎": ["谨慎", "稳重", "细心", "内向"],
            "正直": ["正直", "豪爽", "善良", "公正"],
            "阴险": ["阴险", "狡猾", "多疑", "冷酷"],
            "善良": ["善良", "正直", "温和", "仁慈"],
            "冷酷": ["冷酷", "阴险", "无情", "孤傲"],
            "开朗": ["开朗", "豪爽", "活泼", "乐观"],
            "内向": ["内向", "谨慎", "文静", "害羞"],
            "勇敢": ["勇敢", "豪爽", "果断", "坚毅"],
            "多疑": ["多疑", "谨慎", "阴险", "狡猾"],
        }

        # 冲突性格映射
        conflict_map = {
            "豪爽": ["阴险", "多疑", "冷酷"],
            "谨慎": ["鲁莽", "冲动", "豪爽"],
            "正直": ["阴险", "狡猾", "邪恶"],
            "阴险": ["正直", "豪爽", "善良"],
            "善良": ["冷酷", "邪恶", "残忍"],
            "冷酷": ["善良", "热情", "开朗"],
            "开朗": ["阴沉", "忧郁", "冷酷"],
            "内向": ["张扬", "跋扈", "强势"],
        }

        bonus = 0

        # 检查相容性
        if personality1 in compatibility_map:
            if personality2 in compatibility_map[personality1]:
                bonus += random.randint(5, 15)

        # 检查冲突
        if personality1 in conflict_map:
            if personality2 in conflict_map[personality1]:
                bonus -= random.randint(10, 25)

        return bonus

    def update_relationship_after_combat(self, npc_id1: str, npc_id2: str, winner_id: str):
        """
        战斗后更新NPC关系

        Args:
            npc_id1: 第一个NPC的ID
            npc_id2: 第二个NPC的ID
            winner_id: 获胜者ID
        """
        npc1 = self.npcs.get(npc_id1)
        npc2 = self.npcs.get(npc_id2)

        if not npc1 or not npc2:
            return

        # 根据战斗结果更新关系
        if winner_id == npc_id1:
            # NPC1获胜
            npc1.update_relationship_with(
                npc_id2,
                {"affinity": random.randint(-5, 3), "hatred": random.randint(0, 5)},
                reason="战斗中获胜"
            )
            npc2.update_relationship_with(
                npc_id1,
                {"affinity": random.randint(-10, 0), "hatred": random.randint(3, 10)},
                reason="战斗中落败"
            )
        elif winner_id == npc_id2:
            # NPC2获胜
            npc2.update_relationship_with(
                npc_id1,
                {"affinity": random.randint(-5, 3), "hatred": random.randint(0, 5)},
                reason="战斗中获胜"
            )
            npc1.update_relationship_with(
                npc_id2,
                {"affinity": random.randint(-10, 0), "hatred": random.randint(3, 10)},
                reason="战斗中落败"
            )
        else:
            # 平局
            npc1.update_relationship_with(
                npc_id2,
                {"affinity": random.randint(0, 5), "intimacy": random.randint(1, 3)},
                reason="战斗平局，惺惺相惜"
            )
            npc2.update_relationship_with(
                npc_id1,
                {"affinity": random.randint(0, 5), "intimacy": random.randint(1, 3)},
                reason="战斗平局，惺惺相惜"
            )

    def get_npc_relationships(self, npc_id: str) -> Dict[str, Any]:
        """
        获取NPC的关系信息

        Args:
            npc_id: NPC ID

        Returns:
            关系信息字典
        """
        npc = self.npcs.get(npc_id)
        if not npc:
            return {}

        friends = npc.get_friends()
        enemies = npc.get_enemies()
        all_relations = npc.get_all_relationships()

        return {
            "npc_id": npc_id,
            "npc_name": npc.data.dao_name,
            "total_relations": len(all_relations),
            "friends": [(fid, rel.to_dict()) for fid, rel in friends],
            "enemies": [(eid, rel.to_dict()) for eid, rel in enemies],
            "all_relations": {oid: rel.to_dict() for oid, rel in all_relations.items()}
        }

    def get_relationship_network_stats(self) -> Dict[str, Any]:
        """
        获取关系网络统计信息

        Returns:
            统计信息字典
        """
        total_npcs = len(self.npcs)
        total_relations = 0
        total_friends = 0
        total_enemies = 0

        for npc in self.npcs.values():
            relations = npc.get_all_relationships()
            total_relations += len(relations)
            total_friends += len(npc.get_friends())
            total_enemies += len(npc.get_enemies())

        # 每对关系被计算了两次（双向），所以除以2
        total_relations //= 2
        total_friends //= 2
        total_enemies //= 2

        return {
            "total_npcs": total_npcs,
            "total_relations": total_relations,
            "total_friends": total_friends,
            "total_enemies": total_enemies,
            "avg_relations_per_npc": total_relations / total_npcs if total_npcs > 0 else 0
        }

    def process_npc_social_relationships(self, current_time: float = None):
        """
        处理NPC之间的社交关系发展
        包括道侣关系、师徒关系的自动建立

        Args:
            current_time: 当前时间戳
        """
        if current_time is None:
            current_time = time.time()

        # 处理道侣关系
        self._process_dao_lv_relationships(current_time)

        # 处理师徒关系
        self._process_master_apprentice_relationships(current_time)

        # 处理关系衰减
        relationship_network.process_all_relationship_decay(current_time)

    def _process_dao_lv_relationships(self, current_time: float):
        """
        处理NPC之间的道侣关系建立

        Args:
            current_time: 当前时间戳
        """
        import random

        # 获取所有可能成为道侣的NPC对
        potential_pairs = []

        for npc_id, npc in self.npcs.items():
            # 检查是否已有道侣
            if relationship_network.get_npc_dao_lv(npc_id):
                continue

            # 获取好友列表
            friends = relationship_network.get_friends(npc_id, min_affinity=70)

            for friend_id, relation in friends:
                # 检查对方是否已有道侣
                if relationship_network.get_npc_dao_lv(friend_id):
                    continue

                # 检查亲密度条件
                if relation.intimacy >= 80 and relation.hatred == 0:
                    # 检查性别（如果数据中有性别信息）
                    friend_npc = self.npcs.get(friend_id)
                    if friend_npc:
                        # 添加候选对
                        pair = tuple(sorted([npc_id, friend_id]))
                        if pair not in potential_pairs:
                            potential_pairs.append(pair)

        # 随机选择部分NPC对建立道侣关系
        random.shuffle(potential_pairs)
        for npc1_id, npc2_id in potential_pairs[:3]:  # 每轮最多建立3对道侣
            npc1 = self.npcs.get(npc1_id)
            npc2 = self.npcs.get(npc2_id)

            if npc1 and npc2:
                success, message = relationship_network.propose_dao_lv_between_npcs(
                    npc1_id, npc2_id,
                    {'realm_level': npc1.data.realm_level},
                    {'realm_level': npc2.data.realm_level}
                )

                if success:
                    # 创建社交事件
                    self.social_event_manager.create_event(
                        event_type=SocialEventType.DAO_LV_ESTABLISHED,
                        npc1_id=npc1_id,
                        npc2_id=npc2_id,
                        npc1_name=npc1.data.dao_name,
                        npc2_name=npc2.data.dao_name,
                        description=f"{npc1.data.dao_name} 与 {npc2.data.dao_name} 在 {npc1.data.location} 结为道侣，共赴修仙之路",
                        location=npc1.data.location,
                        is_public=True,
                        importance=8
                    )

    def _process_master_apprentice_relationships(self, current_time: float):
        """
        处理NPC之间的师徒关系建立

        Args:
            current_time: 当前时间戳
        """
        import random

        # 找出可能的师父（境界>=筑基期）
        potential_masters = []
        for npc_id, npc in self.npcs.items():
            if npc.data.realm_level >= 2:  # 筑基期及以上
                # 检查徒弟数量
                apprentices = relationship_network.get_npc_apprentices(npc_id)
                if len(apprentices) < 3:  # 最多3个徒弟
                    potential_masters.append(npc)

        # 为每个可能的师父寻找徒弟
        random.shuffle(potential_masters)

        for master in potential_masters[:5]:  # 每轮最多处理5个师父
            # 寻找可能的徒弟
            potential_apprentices = []

            for npc_id, npc in self.npcs.items():
                if npc_id == master.data.id:
                    continue

                # 检查徒弟条件
                if npc.data.realm_level >= master.data.realm_level:
                    continue

                # 检查是否已有师父
                if relationship_network.get_npc_master(npc_id):
                    continue

                # 获取关系
                relation = relationship_network.get_relationship(master.data.id, npc_id)
                if relation and relation.intimacy >= 30 and relation.affinity >= 40:
                    potential_apprentices.append(npc)

            # 随机选择一个徒弟
            if potential_apprentices:
                apprentice = random.choice(potential_apprentices)

                success, message = relationship_network.establish_master_apprentice_between_npcs(
                    master.data.id, apprentice.data.id,
                    {'realm_level': master.data.realm_level},
                    {'realm_level': apprentice.data.realm_level}
                )

                if success:
                    # 创建社交事件
                    self.social_event_manager.create_event(
                        event_type=SocialEventType.MASTER_APPRENTICE_ESTABLISHED,
                        npc1_id=master.data.id,
                        npc2_id=apprentice.data.id,
                        npc1_name=master.data.dao_name,
                        npc2_name=apprentice.data.dao_name,
                        description=f"{master.data.dao_name} 收 {apprentice.data.dao_name} 为徒，传承修仙之道",
                        location=master.data.location,
                        is_public=True,
                        importance=6
                    )

    def get_recent_social_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的社交事件

        Args:
            limit: 返回数量限制

        Returns:
            社交事件列表
        """
        events = self.social_event_manager.get_recent_events(limit)
        return [event.to_dict() for event in events]

    def get_player_social_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        获取玩家社交通知

        Args:
            unread_only: 是否只返回未读通知

        Returns:
            通知列表
        """
        return self.social_event_manager.get_player_notifications(unread_only)
