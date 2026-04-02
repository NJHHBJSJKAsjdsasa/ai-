"""
死亡NPC管理系统
管理NPC的死亡记录、复活检查等功能
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import sys
from pathlib import Path

# 设置项目根目录导入路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database


@dataclass
class DeathRecord:
    """
    死亡记录数据类
    
    存储NPC死亡的相关信息
    """
    npc_id: str                      # NPC唯一标识符
    npc_name: str                    # NPC名称（道号）
    death_time: datetime             # 死亡时间
    killer_name: str                 # 击杀者名称
    death_reason: str                # 死亡原因
    location: str                    # 死亡地点
    can_resurrect: bool             # 是否可以复活
    is_resurrected: bool = False    # 是否已被复活
    resurrection_time: Optional[datetime] = None  # 复活时间

    def to_dict(self) -> Dict[str, Any]:
        """将死亡记录转换为字典"""
        return {
            'npc_id': self.npc_id,
            'npc_name': self.npc_name,
            'death_time': self.death_time.isoformat(),
            'killer_name': self.killer_name,
            'death_reason': self.death_reason,
            'location': self.location,
            'can_resurrect': self.can_resurrect,
            'is_resurrected': self.is_resurrected,
            'resurrection_time': self.resurrection_time.isoformat() if self.resurrection_time else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeathRecord':
        """从字典创建死亡记录"""
        return cls(
            npc_id=data['npc_id'],
            npc_name=data['npc_name'],
            death_time=datetime.fromisoformat(data['death_time']),
            killer_name=data['killer_name'],
            death_reason=data['death_reason'],
            location=data['location'],
            can_resurrect=data['can_resurrect'],
            is_resurrected=data.get('is_resurrected', False),
            resurrection_time=datetime.fromisoformat(data['resurrection_time']) if data.get('resurrection_time') else None
        )


class DeathManager:
    """
    死亡NPC管理器（单例模式）
    
    负责管理所有NPC的死亡记录、复活检查等功能
    确保全局只有一个管理器实例
    """
    
    _instance: Optional['DeathManager'] = None
    _initialized: bool = False
    
    # 复活时间限制（默认7天内可以复活）
    RESURRECTION_TIME_LIMIT_DAYS: int = 7
    
    def __new__(cls):
        """单例模式实现，确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化死亡管理器"""
        # 避免重复初始化
        if DeathManager._initialized:
            return
        
        # 内存中的死亡记录缓存
        self._death_records: Dict[str, DeathRecord] = {}
        
        # 数据库实例
        self._db: Optional[Database] = None
        
        # 标记已初始化
        DeathManager._initialized = True
    
    def _get_db(self) -> Database:
        """
        获取数据库实例（延迟初始化）
        
        Returns:
            Database: 数据库实例
        """
        if self._db is None:
            self._db = Database()
            self._init_death_tables()
        return self._db
    
    def _init_death_tables(self):
        """初始化死亡记录相关的数据库表"""
        db = self._db
        conn = db._get_connection()
        cursor = conn.cursor()
        
        # 创建死亡记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_death_records (
                npc_id TEXT PRIMARY KEY,
                npc_name TEXT NOT NULL,
                death_time TEXT NOT NULL,
                killer_name TEXT NOT NULL,
                death_reason TEXT NOT NULL,
                location TEXT NOT NULL,
                can_resurrect INTEGER NOT NULL DEFAULT 1,
                is_resurrected INTEGER NOT NULL DEFAULT 0,
                resurrection_time TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_death_time ON npc_death_records(death_time)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resurrected ON npc_death_records(is_resurrected)
        """)
        
        conn.commit()
    
    def _save_death_record_to_db(self, record: DeathRecord):
        """
        将死亡记录保存到数据库
        
        Args:
            record: 死亡记录对象
        """
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO npc_death_records (
                npc_id, npc_name, death_time, killer_name, death_reason,
                location, can_resurrect, is_resurrected, resurrection_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.npc_id,
            record.npc_name,
            record.death_time.isoformat(),
            record.killer_name,
            record.death_reason,
            record.location,
            1 if record.can_resurrect else 0,
            1 if record.is_resurrected else 0,
            record.resurrection_time.isoformat() if record.resurrection_time else None,
            now
        ))
        
        conn.commit()
    
    def _load_death_record_from_db(self, npc_id: str) -> Optional[DeathRecord]:
        """
        从数据库加载死亡记录
        
        Args:
            npc_id: NPC ID
            
        Returns:
            DeathRecord: 死亡记录，如果不存在则返回None
        """
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM npc_death_records WHERE npc_id = ?",
            (npc_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return DeathRecord(
            npc_id=row['npc_id'],
            npc_name=row['npc_name'],
            death_time=datetime.fromisoformat(row['death_time']),
            killer_name=row['killer_name'],
            death_reason=row['death_reason'],
            location=row['location'],
            can_resurrect=bool(row['can_resurrect']),
            is_resurrected=bool(row['is_resurrected']),
            resurrection_time=datetime.fromisoformat(row['resurrection_time']) if row['resurrection_time'] else None
        )
    
    def _update_resurrection_status_in_db(self, npc_id: str):
        """
        更新数据库中的复活状态
        
        Args:
            npc_id: NPC ID
        """
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE npc_death_records 
            SET is_resurrected = 1, resurrection_time = ?
            WHERE npc_id = ?
        """, (now, npc_id))
        
        conn.commit()
    
    def mark_npc_dead(self, npc, killer_name: str, reason: str) -> DeathRecord:
        """
        标记NPC死亡
        
        设置NPC的死亡状态，创建死亡记录并保存到数据库
        
        Args:
            npc: NPC对象（需要包含data属性）
            killer_name: 击杀者名称
            reason: 死亡原因
            
        Returns:
            DeathRecord: 创建的死亡记录
        """
        # 设置NPC死亡状态
        npc.data.is_alive = False
        
        # 确定是否可以复活（根据死亡原因判断）
        # 某些特殊死亡原因可能导致无法复活
        can_resurrect = self._determine_resurrect_eligibility(reason)
        
        # 创建死亡记录
        death_record = DeathRecord(
            npc_id=npc.data.id,
            npc_name=npc.data.dao_name,
            death_time=datetime.now(),
            killer_name=killer_name,
            death_reason=reason,
            location=npc.data.location,
            can_resurrect=can_resurrect
        )
        
        # 保存到内存缓存
        self._death_records[npc.data.id] = death_record
        
        # 保存到数据库
        self._save_death_record_to_db(death_record)
        
        # 记录死亡信息到NPC数据
        npc.data.death_info = {
            'death_time': death_record.death_time.isoformat(),
            'killer_name': killer_name,
            'death_reason': reason,
            'can_resurrect': can_resurrect
        }
        
        return death_record
    
    def _determine_resurrect_eligibility(self, reason: str) -> bool:
        """
        根据死亡原因判断是否可复活
        
        Args:
            reason: 死亡原因
            
        Returns:
            bool: 是否可以复活
        """
        # 某些特殊死亡原因导致无法复活
        permanent_death_reasons = [
            '魂飞魄散',
            '神魂俱灭',
            '被噬魂',
            '寿元耗尽',
            '天劫失败',
            '走火入魔',
        ]
        
        # 检查死亡原因是否包含永久死亡关键词
        for permanent_reason in permanent_death_reasons:
            if permanent_reason in reason:
                return False
        
        return True
    
    def get_dead_npcs(self) -> List[DeathRecord]:
        """
        获取所有死亡NPC记录
        
        Returns:
            List[DeathRecord]: 死亡记录列表
        """
        # 从数据库加载所有未复活的死亡记录
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM npc_death_records WHERE is_resurrected = 0 ORDER BY death_time DESC"
        )
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            record = DeathRecord(
                npc_id=row['npc_id'],
                npc_name=row['npc_name'],
                death_time=datetime.fromisoformat(row['death_time']),
                killer_name=row['killer_name'],
                death_reason=row['death_reason'],
                location=row['location'],
                can_resurrect=bool(row['can_resurrect']),
                is_resurrected=bool(row['is_resurrected']),
                resurrection_time=datetime.fromisoformat(row['resurrection_time']) if row['resurrection_time'] else None
            )
            records.append(record)
            # 更新内存缓存
            self._death_records[record.npc_id] = record
        
        return records
    
    def can_resurrect(self, npc_id: str) -> bool:
        """
        检查NPC是否可以复活
        
        检查条件：
        1. can_resurrect字段为True
        2. 死亡时间未超过复活时间限制
        
        Args:
            npc_id: NPC ID
            
        Returns:
            bool: 是否可以复活
        """
        # 先从内存缓存查找
        record = self._death_records.get(npc_id)
        
        # 如果内存中没有，从数据库加载
        if record is None:
            record = self._load_death_record_from_db(npc_id)
            if record:
                self._death_records[npc_id] = record
        
        # 如果没有死亡记录，说明NPC未死亡，不需要复活
        if record is None:
            return False
        
        # 如果已经复活，不能再次复活
        if record.is_resurrected:
            return False
        
        # 检查是否可以复活
        if not record.can_resurrect:
            return False
        
        # 检查死亡时间是否超过限制
        time_limit = timedelta(days=self.RESURRECTION_TIME_LIMIT_DAYS)
        if datetime.now() - record.death_time > time_limit:
            return False
        
        return True
    
    def resurrect_npc(self, npc_id: str, npc=None) -> bool:
        """
        复活NPC
        
        将NPC状态恢复为存活，清除死亡信息
        
        Args:
            npc_id: NPC ID
            npc: NPC对象（可选，如果提供则更新NPC状态）
            
        Returns:
            bool: 是否成功复活
        """
        # 检查是否可以复活
        if not self.can_resurrect(npc_id):
            return False
        
        # 获取死亡记录
        record = self._death_records.get(npc_id)
        if record is None:
            record = self._load_death_record_from_db(npc_id)
            if record is None:
                return False
        
        # 标记为已复活
        record.is_resurrected = True
        record.resurrection_time = datetime.now()
        
        # 更新内存缓存
        self._death_records[npc_id] = record
        
        # 更新数据库
        self._update_resurrection_status_in_db(npc_id)
        
        # 如果提供了NPC对象，更新其状态
        if npc is not None:
            npc.data.is_alive = True
            # 清除死亡信息
            if hasattr(npc.data, 'death_info'):
                delattr(npc.data, 'death_info')
        
        return True
    
    def filter_alive_npcs(self, npcs: List) -> List:
        """
        过滤存活的NPC
        
        Args:
            npcs: NPC对象列表
            
        Returns:
            List: 存活的NPC列表（is_alive = True）
        """
        return [npc for npc in npcs if hasattr(npc, 'data') and npc.data.is_alive]
    
    def get_death_record(self, npc_id: str) -> Optional[DeathRecord]:
        """
        获取NPC的死亡记录
        
        Args:
            npc_id: NPC ID
            
        Returns:
            Optional[DeathRecord]: 死亡记录，如果不存在则返回None
        """
        # 先从内存缓存查找
        record = self._death_records.get(npc_id)
        
        # 如果内存中没有，从数据库加载
        if record is None:
            record = self._load_death_record_from_db(npc_id)
            if record:
                self._death_records[npc_id] = record
        
        return record
    
    def get_death_statistics(self) -> Dict[str, Any]:
        """
        获取死亡统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        # 总死亡数
        cursor.execute("SELECT COUNT(*) FROM npc_death_records")
        total_deaths = cursor.fetchone()[0]
        
        # 已复活数
        cursor.execute("SELECT COUNT(*) FROM npc_death_records WHERE is_resurrected = 1")
        resurrected_count = cursor.fetchone()[0]
        
        # 未复活数
        cursor.execute("SELECT COUNT(*) FROM npc_death_records WHERE is_resurrected = 0")
        not_resurrected_count = cursor.fetchone()[0]
        
        # 不可复活数
        cursor.execute("SELECT COUNT(*) FROM npc_death_records WHERE can_resurrect = 0")
        permanent_deaths = cursor.fetchone()[0]
        
        # 最近死亡时间
        cursor.execute(
            "SELECT death_time FROM npc_death_records ORDER BY death_time DESC LIMIT 1"
        )
        row = cursor.fetchone()
        latest_death = row['death_time'] if row else None
        
        # 死亡原因统计
        cursor.execute("""
            SELECT death_reason, COUNT(*) as count 
            FROM npc_death_records 
            GROUP BY death_reason 
            ORDER BY count DESC
        """)
        reason_stats = {row['death_reason']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total_deaths': total_deaths,
            'resurrected_count': resurrected_count,
            'not_resurrected_count': not_resurrected_count,
            'permanent_deaths': permanent_deaths,
            'latest_death': latest_death,
            'death_reason_stats': reason_stats
        }
    
    def clean_old_records(self, days: int = 30) -> int:
        """
        清理过旧的死亡记录
        
        Args:
            days: 保留天数，超过此天数的记录将被删除
            
        Returns:
            int: 删除的记录数量
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        db = self._get_db()
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM npc_death_records WHERE death_time < ? AND is_resurrected = 1",
            (cutoff_date,)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        # 清理内存缓存
        npc_ids_to_remove = [
            npc_id for npc_id, record in self._death_records.items()
            if record.is_resurrected and record.death_time < datetime.fromisoformat(cutoff_date)
        ]
        for npc_id in npc_ids_to_remove:
            del self._death_records[npc_id]
        
        return deleted_count
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例（主要用于测试）"""
        if cls._instance:
            cls._instance = None
            cls._initialized = False


# 全局死亡管理器实例
death_manager = DeathManager()
