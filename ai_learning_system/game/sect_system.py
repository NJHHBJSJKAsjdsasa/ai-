"""
门派系统模块
管理门派、成员、贡献、任务、功法、战争等
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class SectType(Enum):
    """门派类型"""
    RIGHTEOUS = "正道"
    DEMON = "魔道"
    NEUTRAL = "中立"
    IMMORTAL = "仙门"
    BUDDHIST = "佛门"


class Position(Enum):
    """门派职位"""
    OUTER = "外门弟子"
    INNER = "内门弟子"
    CORE = "核心弟子"
    ELDER = "长老"
    LEADER = "掌门"


# 职位等级映射
POSITION_LEVELS = {
    "外门弟子": 0,
    "内门弟子": 1,
    "核心弟子": 2,
    "长老": 3,
    "掌门": 4
}


# 职位晋升要求
POSITION_REQUIREMENTS = {
    "外门弟子": {"contribution": 0, "realm": 1},
    "内门弟子": {"contribution": 100, "realm": 2},
    "核心弟子": {"contribution": 500, "realm": 3},
    "长老": {"contribution": 2000, "realm": 4},
    "掌门": {"contribution": 10000, "realm": 6}
}


@dataclass
class Sect:
    """门派数据类"""
    id: str
    name: str
    description: str
    sect_type: SectType
    location: str
    founder: str
    established_date: str
    total_members: int = 0
    sect_level: int = 1
    reputation: int = 0
    resources: int = 0
    main_element: str = ""
    sect_leader: str = ""
    created_at: str = ""


@dataclass
class SectMember:
    """门派成员数据类"""
    id: int
    sect_id: str
    player_name: str
    position: str
    contribution: int = 0
    joined_at: str = ""
    last_active: str = ""


@dataclass
class SectTask:
    """门派任务数据类"""
    id: str
    sect_id: str
    task_name: str
    task_type: str
    description: str
    difficulty: int = 1
    contribution_reward: int = 0
    spirit_stone_reward: int = 0
    item_reward: List[str] = field(default_factory=list)
    required_realm: int = 0
    required_position: str = ""
    is_active: bool = True
    created_at: str = ""
    expires_at: str = ""


@dataclass
class SectTechnique:
    """门派专属功法数据类"""
    id: str
    sect_id: str
    technique_name: str
    description: str
    technique_type: str
    required_position: str
    required_contribution: int = 0
    required_realm: int = 0
    is_active: bool = True
    created_at: str = ""


# 预设门派数据 - 凡人修仙传风格
DEFAULT_SECTS = [
    {
        "id": "qixuan",
        "name": "七玄门",
        "description": "越国七大派之一，以剑修闻名，门内藏经阁藏有无数剑诀。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "七玄真人",
        "main_element": "金",
        "sect_level": 5
    },
    {
        "id": "huangfeng",
        "name": "黄枫谷",
        "description": "越国七大派之一，以炼丹术著称，谷内灵药遍地。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "黄枫老祖",
        "main_element": "木",
        "sect_level": 5
    },
    {
        "id": "yanyue",
        "name": "掩月宗",
        "description": "越国七大派之一，擅长幻术和隐匿之术，神秘莫测。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "掩月仙子",
        "main_element": "水",
        "sect_level": 5
    },
    {
        "id": "lingyunding",
        "name": "灵云顶",
        "description": "越国七大派之一，主修雷法，威势惊人。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "灵云尊者",
        "main_element": "雷",
        "sect_level": 5
    },
    {
        "id": "tianque",
        "name": "天阙堡",
        "description": "越国七大派之一，以防御功法闻名，堡内固若金汤。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "天阙上人",
        "main_element": "土",
        "sect_level": 5
    },
    {
        "id": "huoyun",
        "name": "火云宗",
        "description": "越国七大派之一，主修火属性功法，攻击力极强。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "火云老祖",
        "main_element": "火",
        "sect_level": 5
    },
    {
        "id": "baixiong",
        "name": "百巧院",
        "description": "越国七大派之一，擅长炼器和机关术。",
        "sect_type": "正道",
        "location": "越国",
        "founder": "百巧老人",
        "main_element": "金",
        "sect_level": 5
    }
]


# 门派专属功法
SECT_TECHNIQUES = {
    "qixuan": [
        {
            "technique_name": "七玄剑诀",
            "description": "七玄门镇派剑诀，剑气纵横，威力无穷",
            "technique_type": "剑法",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "玄天剑阵",
            "description": "七玄门绝学，可布下剑阵困敌",
            "technique_type": "阵法",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "huangfeng": [
        {
            "technique_name": "黄枫炼丹术",
            "description": "黄枫谷独门炼丹秘术，可炼制上品丹药",
            "technique_type": "炼丹",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "百草心经",
            "description": "黄枫谷心法，修炼后对各种灵药有天然感应",
            "technique_type": "功法",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "yanyue": [
        {
            "technique_name": "掩月幻术",
            "description": "掩月宗秘传幻术，可制造逼真幻象",
            "technique_type": "幻术",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "月影遁",
            "description": "掩月宗顶级身法，可在月光下瞬移",
            "technique_type": "身法",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "lingyunding": [
        {
            "technique_name": "灵云雷法",
            "description": "灵云顶基础雷法，可召唤雷电攻击",
            "technique_type": "雷法",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "九霄神雷",
            "description": "灵云顶绝学，可引动九天神雷",
            "technique_type": "雷法",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "tianque": [
        {
            "technique_name": "天阙护体功",
            "description": "天阙堡防御功法，可形成坚固护盾",
            "technique_type": "防御",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "不动如山",
            "description": "天阙堡绝学，防御力惊人",
            "technique_type": "防御",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "huoyun": [
        {
            "technique_name": "火云掌",
            "description": "火云宗基础掌法，掌中带火",
            "technique_type": "掌法",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "焚天诀",
            "description": "火云宗绝学，可焚尽万物",
            "technique_type": "功法",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ],
    "baixiong": [
        {
            "technique_name": "百巧炼器术",
            "description": "百巧院炼器秘术，可炼制精良法器",
            "technique_type": "炼器",
            "required_position": "内门弟子",
            "required_contribution": 200,
            "required_realm": 2
        },
        {
            "technique_name": "机关傀儡术",
            "description": "百巧院绝学，可制作强力傀儡",
            "technique_type": "傀儡",
            "required_position": "核心弟子",
            "required_contribution": 800,
            "required_realm": 3
        }
    ]
}


# 门派任务模板
SECT_TASK_TEMPLATES = [
    {
        "task_name": "采集灵草",
        "task_type": "采集",
        "description": "为门派采集指定数量的灵草",
        "difficulty": 1,
        "contribution_reward": 10,
        "spirit_stone_reward": 5,
        "required_realm": 1
    },
    {
        "task_name": "猎杀妖兽",
        "task_type": "战斗",
        "description": "清除门派领地内的妖兽威胁",
        "difficulty": 2,
        "contribution_reward": 20,
        "spirit_stone_reward": 10,
        "required_realm": 1
    },
    {
        "task_name": "护送弟子",
        "task_type": "护送",
        "description": "护送门派弟子前往指定地点",
        "difficulty": 2,
        "contribution_reward": 15,
        "spirit_stone_reward": 8,
        "required_realm": 2
    },
    {
        "task_name": "探索秘境",
        "task_type": "探索",
        "description": "探索门派发现的秘境",
        "difficulty": 3,
        "contribution_reward": 30,
        "spirit_stone_reward": 15,
        "required_realm": 2
    },
    {
        "task_name": "炼制丹药",
        "task_type": "炼丹",
        "description": "为门派炼制指定丹药",
        "difficulty": 3,
        "contribution_reward": 25,
        "spirit_stone_reward": 12,
        "required_realm": 2,
        "required_position": "内门弟子"
    },
    {
        "task_name": "守卫山门",
        "task_type": "守卫",
        "description": "守卫门派山门，抵御外敌",
        "difficulty": 4,
        "contribution_reward": 40,
        "spirit_stone_reward": 20,
        "required_realm": 3,
        "required_position": "内门弟子"
    },
    {
        "task_name": "追查叛徒",
        "task_type": "追查",
        "description": "追查并处置门派叛徒",
        "difficulty": 4,
        "contribution_reward": 50,
        "spirit_stone_reward": 25,
        "required_realm": 3,
        "required_position": "核心弟子"
    },
    {
        "task_name": "争夺灵矿",
        "task_type": "争夺",
        "description": "代表门派争夺灵矿资源",
        "difficulty": 5,
        "contribution_reward": 80,
        "spirit_stone_reward": 40,
        "required_realm": 4,
        "required_position": "核心弟子"
    }
]


class SectManager:
    """门派管理器"""

    def __init__(self):
        self._db = None

    def _get_db(self):
        """获取数据库实例"""
        if self._db is None:
            from storage.database import Database
            self._db = Database()
        return self._db

    def initialize_sects(self):
        """初始化预设门派"""
        db = self._get_db()
        db.init_sect_tables()

        now = datetime.now().isoformat()

        for sect_data in DEFAULT_SECTS:
            existing = db.get_sect(sect_data["id"])
            if not existing:
                sect_data["established_date"] = now
                sect_data["created_at"] = now
                db.save_sect(sect_data)

                # 添加门派专属功法
                if sect_data["id"] in SECT_TECHNIQUES:
                    for tech in SECT_TECHNIQUES[sect_data["id"]]:
                        tech_data = {
                            "id": str(uuid.uuid4()),
                            "sect_id": sect_data["id"],
                            **tech
                        }
                        db.save_sect_technique(tech_data)

                # 添加门派任务
                for task_template in SECT_TASK_TEMPLATES:
                    task_data = {
                        "id": str(uuid.uuid4()),
                        "sect_id": sect_data["id"],
                        **task_template
                    }
                    db.save_sect_task(task_data)

    def get_all_sects(self) -> List[Dict]:
        """获取所有门派"""
        db = self._get_db()
        return db.get_all_sects()

    def get_sect(self, sect_id: str) -> Optional[Dict]:
        """获取门派信息"""
        db = self._get_db()
        return db.get_sect(sect_id)

    def join_sect(self, sect_id: str, player_name: str) -> Tuple[bool, str]:
        """
        加入门派

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        # 检查是否已在其他门派
        existing = db.get_player_sect(player_name)
        if existing:
            return False, f"你已经是{existing['sect_name']}的弟子了"

        # 加入门派
        if db.join_sect(sect_id, player_name, "外门弟子"):
            sect = db.get_sect(sect_id)
            return True, f"成功加入{sect['name']}，成为外门弟子"
        return False, "加入门派失败"

    def leave_sect(self, player_name: str) -> Tuple[bool, str]:
        """
        离开门派

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        existing = db.get_player_sect(player_name)
        if not existing:
            return False, "你不属于任何门派"

        if existing['position'] == '掌门':
            return False, "掌门无法退出门派"

        sect_name = existing['sect_name']
        if db.leave_sect(player_name):
            return True, f"你已退出{sect_name}"
        return False, "退出门派失败"

    def get_player_sect(self, player_name: str) -> Optional[Dict]:
        """获取玩家所属门派信息"""
        db = self._get_db()
        return db.get_player_sect(player_name)

    def add_contribution(self, sect_id: str, player_name: str, amount: int,
                         contribution_type: str = '任务', description: str = '') -> bool:
        """添加贡献值"""
        db = self._get_db()
        return db.add_contribution(sect_id, player_name, amount, contribution_type, description)

    def get_sect_members(self, sect_id: str, limit: int = None) -> List[Dict]:
        """获取门派成员"""
        db = self._get_db()
        return db.get_sect_members(sect_id, limit)

    def get_sect_tasks(self, sect_id: str, player_position: str = None) -> List[Dict]:
        """获取门派任务"""
        db = self._get_db()
        return db.get_sect_tasks(sect_id, player_position)

    def accept_task(self, task_id: str, player_name: str) -> Tuple[bool, str]:
        """
        接受任务

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        # 检查是否已接受
        # TODO: 检查任务状态

        if db.accept_sect_task(task_id, player_name):
            return True, "任务接受成功"
        return False, "任务接受失败"

    def complete_task(self, task_id: str, player_name: str,
                      sect_id: str, contribution_reward: int,
                      spirit_stone_reward: int) -> Tuple[bool, str]:
        """
        完成任务

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        if db.complete_sect_task(task_id, player_name):
            # 添加贡献
            db.add_contribution(
                sect_id, player_name, contribution_reward,
                '任务', f'完成任务获得{contribution_reward}贡献'
            )

            # 检查是否可以晋升
            self._check_promotion(sect_id, player_name)

            return True, f"任务完成！获得{contribution_reward}贡献，{spirit_stone_reward}灵石"
        return False, "任务完成失败"

    def get_sect_techniques(self, sect_id: str, player_position: str = None,
                           player_contribution: int = 0) -> List[Dict]:
        """获取门派专属功法"""
        db = self._get_db()
        return db.get_sect_techniques(sect_id, player_position, player_contribution)

    def can_learn_technique(self, technique: Dict, player_position: str,
                           player_contribution: int, player_realm: int) -> Tuple[bool, str]:
        """
        检查是否可以学习功法

        Returns:
            (是否可以, 原因)
        """
        # 检查职位
        if technique.get('required_position'):
            position_order = {'外门弟子': 0, '内门弟子': 1, '核心弟子': 2, '长老': 3, '掌门': 4}
            player_rank = position_order.get(player_position, 0)
            required_rank = position_order.get(technique['required_position'], 0)
            if player_rank < required_rank:
                return False, f"需要职位：{technique['required_position']}"

        # 检查贡献
        if player_contribution < technique.get('required_contribution', 0):
            return False, f"需要贡献：{technique['required_contribution']}"

        # 检查境界
        if player_realm < technique.get('required_realm', 0):
            from config import get_realm_info
            realm_info = get_realm_info(technique['required_realm'])
            realm_name = realm_info.name if realm_info else f"境界{technique['required_realm']}"
            return False, f"需要境界：{realm_name}"

        return True, "可以学习"

    def _check_promotion(self, sect_id: str, player_name: str):
        """检查并执行晋升"""
        db = self._get_db()

        member_info = db.get_player_sect(player_name)
        if not member_info:
            return

        current_position = member_info['position']
        contribution = member_info['contribution']

        # 获取下一级职位
        position_order = ['外门弟子', '内门弟子', '核心弟子', '长老', '掌门']
        current_index = position_order.index(current_position) if current_position in position_order else -1

        if current_index >= len(position_order) - 1:
            return  # 已是最高职位

        next_position = position_order[current_index + 1]
        requirements = POSITION_REQUIREMENTS.get(next_position, {})

        if contribution >= requirements.get('contribution', 999999):
            # 可以晋升
            db.update_position(sect_id, player_name, next_position)
            return next_position

        return None

    def get_position_requirements(self, position: str) -> Dict:
        """获取职位要求"""
        return POSITION_REQUIREMENTS.get(position, {"contribution": 0, "realm": 0})

    def get_next_promotion_info(self, player_name: str) -> Optional[Dict]:
        """获取下次晋升信息"""
        db = self._get_db()

        member_info = db.get_player_sect(player_name)
        if not member_info:
            return None

        current_position = member_info['position']
        contribution = member_info['contribution']

        position_order = ['外门弟子', '内门弟子', '核心弟子', '长老', '掌门']
        current_index = position_order.index(current_position) if current_position in position_order else -1

        if current_index >= len(position_order) - 1:
            return None  # 已是最高职位

        next_position = position_order[current_index + 1]
        requirements = POSITION_REQUIREMENTS.get(next_position, {})

        return {
            'current_position': current_position,
            'next_position': next_position,
            'current_contribution': contribution,
            'required_contribution': requirements.get('contribution', 0),
            'required_realm': requirements.get('realm', 0),
            'progress': min(1.0, contribution / max(1, requirements.get('contribution', 1)))
        }

    def start_sect_war(self, attacker_sect_id: str, defender_sect_id: str,
                      war_type: str = "资源争夺") -> Tuple[bool, str]:
        """
        发起门派战争

        Returns:
            (是否成功, 消息)
        """
        db = self._get_db()

        if attacker_sect_id == defender_sect_id:
            return False, "不能向自己的门派宣战"

        now = datetime.now().isoformat()
        war_id = str(uuid.uuid4())

        # TODO: 实现战争创建

        return True, "宣战成功"

    def get_sect_rankings(self) -> List[Dict]:
        """获取门派排名"""
        db = self._get_db()
        sects = db.get_all_sects()

        # 按声望排序
        sorted_sects = sorted(sects, key=lambda x: x.get('reputation', 0), reverse=True)

        rankings = []
        for i, sect in enumerate(sorted_sects, 1):
            rankings.append({
                'rank': i,
                'sect_id': sect['id'],
                'name': sect['name'],
                'reputation': sect.get('reputation', 0),
                'total_members': sect.get('total_members', 0),
                'sect_level': sect.get('sect_level', 1)
            })

        return rankings


# 全局门派管理器实例
sect_manager = SectManager()


def get_sect_manager() -> SectManager:
    """获取门派管理器实例"""
    return sect_manager


if __name__ == "__main__":
    # 测试门派系统
    print("=" * 60)
    print("门派系统测试")
    print("=" * 60)

    manager = SectManager()
    manager.initialize_sects()

    print("\n【所有门派】")
    for sect in manager.get_all_sects():
        print(f"  {sect['name']} - {sect['description'][:30]}...")
        print(f"    类型: {sect['sect_type']}  主属性: {sect['main_element']}")

    print("\n【门派排名】")
    for rank in manager.get_sect_rankings():
        print(f"  第{rank['rank']}名: {rank['name']} (声望: {rank['reputation']})")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
