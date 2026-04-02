import sqlite3
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import Memory


class Database:
    """SQLite 数据库管理类
    
    使用单例模式确保全局只有一个数据库连接实例。
    支持上下文管理器自动管理资源。
    """
    
    _instance: Optional['Database'] = None
    _lock = False

    def __new__(cls, db_path: str = None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认为 data/memories.db
        """
        # 避免重复初始化
        if self._initialized:
            return
            
        if db_path is None:
            # 获取当前文件所在目录的上级目录，然后指向 data/memories.db
            current_dir = Path(__file__).parent
            db_path = current_dir / "data" / "memories.db"

        self.db_path = Path(db_path)
        # 确保数据目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection: Optional[sqlite3.Connection] = None
        self._connection_count = 0  # 连接引用计数
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(str(self.db_path))
                # 启用外键支持
                self._connection.execute("PRAGMA foreign_keys = ON")
                # 设置行工厂，使查询结果可以通过列名访问
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                raise RuntimeError(f"数据库连接失败: {e}")
        self._connection_count += 1
        return self._connection

    def close(self, force: bool = False):
        """关闭数据库连接
        
        Args:
            force: 是否强制关闭，忽略引用计数
        """
        if not force:
            self._connection_count = max(0, self._connection_count - 1)
            if self._connection_count > 0:
                return  # 还有引用，不关闭
                
        if self._connection:
            try:
                self._connection.close()
            except sqlite3.Error as e:
                print(f"警告: 关闭数据库连接时出错: {e}")
            finally:
                self._connection = None
                self._connection_count = 0

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False
        
    @classmethod
    def reset_instance(cls):
        """重置单例实例（主要用于测试）"""
        if cls._instance:
            cls._instance.close(force=True)
            cls._instance = None

    def init_tables(self):
        """创建数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 memories 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                importance INTEGER NOT NULL DEFAULT 5 CHECK(importance >= 0 AND importance <= 10),
                category TEXT NOT NULL DEFAULT 'general',
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0 CHECK(access_count >= 0),
                privacy_level INTEGER NOT NULL DEFAULT 50 CHECK(privacy_level >= 0 AND privacy_level <= 100),
                is_encrypted INTEGER NOT NULL DEFAULT 0,
                retention_days INTEGER NOT NULL DEFAULT 30 CHECK(retention_days >= 0),
                source TEXT NOT NULL DEFAULT 'user'
            )
        """)

        # 创建 players 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at)
        """)

        conn.commit()

    def init_generated_tables(self):
        """创建无限生成内容的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 generated_maps 表 - 存储生成的地图
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_maps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                map_type TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                size TEXT,
                description TEXT,
                history TEXT,
                environment TEXT,
                connections TEXT,
                npcs TEXT,
                monsters TEXT,
                items TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 generated_npcs 表 - 存储生成的NPC
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_npcs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT,
                full_name TEXT,
                gender TEXT,
                age INTEGER,
                realm_level TEXT,
                occupation TEXT,
                personality TEXT,
                appearance TEXT,
                catchphrase TEXT,
                story TEXT,
                location TEXT,
                favor INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 generated_items 表 - 存储生成的物品
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                rarity TEXT,
                attributes TEXT,
                effects TEXT,
                description TEXT,
                origin TEXT,
                legend TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 generated_monsters 表 - 存储生成的妖兽
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_monsters (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                monster_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                realm_level TEXT,
                attributes TEXT,
                drops TEXT,
                description TEXT,
                habits TEXT,
                weakness TEXT,
                location TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 materials 表 - 存储玩家收集的材料
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                material_type TEXT,
                rarity TEXT,
                level INTEGER DEFAULT 1,
                effects TEXT,
                value INTEGER DEFAULT 0,
                source TEXT,
                created_at TEXT NOT NULL,
                owner_id TEXT NOT NULL
            )
        """)

        # 创建 death_records 表 - 存储NPC死亡记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS death_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc_id TEXT NOT NULL,
                npc_name TEXT,
                killer_name TEXT,
                death_reason TEXT,
                location TEXT,
                death_time TEXT NOT NULL,
                can_resurrect INTEGER DEFAULT 1
            )
        """)

        # 创建 generated_techniques 表 - 存储生成的功法
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_techniques (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                technique_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                realm_required INTEGER DEFAULT 0,
                description TEXT,
                effects TEXT,
                cultivation_method TEXT,
                origin TEXT,
                created_at TEXT NOT NULL,
                discovered_by TEXT,
                is_learned INTEGER DEFAULT 0
            )
        """)

        # 创建 alchemy_recipes 表 - 存储丹方
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alchemy_recipes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                pill_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                realm_required INTEGER DEFAULT 0,
                materials TEXT NOT NULL,
                effects TEXT,
                base_success_rate REAL DEFAULT 0.5,
                quality_multipliers TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 forging_blueprints 表 - 存储炼器图纸
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forging_blueprints (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                equipment_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                realm_required INTEGER DEFAULT 0,
                materials TEXT NOT NULL,
                base_attributes TEXT,
                special_effects TEXT,
                base_success_rate REAL DEFAULT 0.5,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 player_alchemy_records 表 - 存储玩家炼丹记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_alchemy_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                recipe_id TEXT NOT NULL,
                recipe_name TEXT,
                success INTEGER DEFAULT 0,
                quality TEXT,
                materials_used TEXT,
                result_item TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 player_forging_records 表 - 存储玩家炼器记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_forging_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                blueprint_id TEXT NOT NULL,
                blueprint_name TEXT,
                success INTEGER DEFAULT 0,
                quality TEXT,
                materials_used TEXT,
                result_item TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 为 generated_npcs 表添加死亡相关字段（如果不存在）
        # 使用 try-except 确保向后兼容
        try:
            cursor.execute("ALTER TABLE generated_npcs ADD COLUMN is_alive INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE generated_npcs ADD COLUMN death_info TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE generated_npcs ADD COLUMN can_resurrect INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE generated_npcs ADD COLUMN morality INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # 字段已存在

        # 为 generated_npcs 表添加完整NPC数据存储字段（如果不存在）
        new_columns = [
            ("npc_data", "TEXT"),
            ("independent_data", "TEXT"),
            ("goals_data", "TEXT"),
            ("schedule_data", "TEXT"),
            ("values_data", "TEXT"),
            ("speaking_style_data", "TEXT"),
            ("life_record_data", "TEXT"),
            ("enhanced_memory_data", "TEXT"),
            ("combat_record_data", "TEXT"),
            ("updated_at", "TEXT"),
        ]
        
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE generated_npcs ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass  # 字段已存在

        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_maps_level ON generated_maps(level)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_maps_type ON generated_maps(map_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npcs_location ON generated_npcs(location)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monsters_location ON generated_monsters(location)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monsters_level ON generated_monsters(level)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_type ON generated_items(item_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_rarity ON generated_items(rarity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_owner ON materials(owner_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_type ON materials(material_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_death_records_npc ON death_records(npc_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npcs_alive ON generated_npcs(is_alive)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alchemy_recipes_type ON alchemy_recipes(pill_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alchemy_recipes_rarity ON alchemy_recipes(rarity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_forging_blueprints_type ON forging_blueprints(equipment_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_forging_blueprints_rarity ON forging_blueprints(rarity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alchemy_records_player ON player_alchemy_records(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_forging_records_player ON player_forging_records(player_id)
        """)

        # 创建天劫记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tribulation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                realm_level INTEGER NOT NULL,
                realm_name TEXT NOT NULL,
                tribulation_type TEXT NOT NULL DEFAULT 'normal',
                status TEXT NOT NULL DEFAULT 'pending',
                total_thunder INTEGER NOT NULL DEFAULT 9,
                current_thunder INTEGER NOT NULL DEFAULT 0,
                thunder_power INTEGER NOT NULL DEFAULT 100,
                player_health INTEGER NOT NULL DEFAULT 100,
                player_max_health INTEGER NOT NULL DEFAULT 100,
                player_spiritual_power INTEGER NOT NULL DEFAULT 100,
                player_max_spiritual_power INTEGER NOT NULL DEFAULT 100,
                player_defense INTEGER NOT NULL DEFAULT 0,
                player_resistance REAL NOT NULL DEFAULT 0.0,
                used_treasures TEXT,
                used_pills TEXT,
                used_formations TEXT,
                thunder_history TEXT,
                final_result TEXT,
                reward_attributes TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        # 创建天劫奖励记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tribulation_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                tribulation_id INTEGER NOT NULL,
                realm_level INTEGER NOT NULL,
                realm_name TEXT NOT NULL,
                success INTEGER NOT NULL DEFAULT 0,
                reward_type TEXT NOT NULL,
                reward_name TEXT NOT NULL,
                reward_value TEXT NOT NULL,
                description TEXT,
                is_claimed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tribulation_id) REFERENCES tribulation_records(id)
            )
        """)

        # 创建天劫准备物品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tribulation_preparations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                tribulation_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_id TEXT,
                effect_type TEXT NOT NULL,
                effect_value REAL NOT NULL DEFAULT 0.0,
                is_consumed INTEGER NOT NULL DEFAULT 0,
                used_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tribulation_id) REFERENCES tribulation_records(id)
            )
        """)

        # 创建天劫雷劫详细记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tribulation_thunder_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tribulation_id INTEGER NOT NULL,
                thunder_number INTEGER NOT NULL,
                thunder_name TEXT NOT NULL,
                thunder_power INTEGER NOT NULL DEFAULT 100,
                damage_dealt INTEGER NOT NULL DEFAULT 0,
                player_health_before INTEGER NOT NULL DEFAULT 0,
                player_health_after INTEGER NOT NULL DEFAULT 0,
                defense_used TEXT,
                resistance_applied REAL NOT NULL DEFAULT 0.0,
                is_resisted INTEGER NOT NULL DEFAULT 0,
                special_effect TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (tribulation_id) REFERENCES tribulation_records(id)
            )
        """)

        # 创建天劫相关索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tribulation_player ON tribulation_records(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tribulation_status ON tribulation_records(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tribulation_rewards_player ON tribulation_rewards(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tribulation_preparations ON tribulation_preparations(tribulation_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tribulation_thunder ON tribulation_thunder_records(tribulation_id)
        """)

        conn.commit()

    def create_memory(self, memory_data: Dict[str, Any]) -> Memory:
        """
        创建新记忆

        Args:
            memory_data: 记忆数据字典，包含 content, importance, category 等字段

        Returns:
            创建的 Memory 对象
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now()

        cursor.execute("""
            INSERT INTO memories (
                content, importance, category, created_at, last_accessed,
                access_count, privacy_level, is_encrypted, retention_days, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_data['content'],
            memory_data.get('importance', 5),
            memory_data.get('category', 'general'),
            now.isoformat(),
            now.isoformat(),
            memory_data.get('access_count', 0),
            memory_data.get('privacy_level', 50),
            1 if memory_data.get('is_encrypted', False) else 0,
            memory_data.get('retention_days', 30),
            memory_data.get('source', 'user')
        ))

        conn.commit()
        memory_id = cursor.lastrowid

        return self.get_memory(memory_id)

    def insert_memory(self, memory) -> int:
        """
        插入记忆对象（兼容接口）

        Args:
            memory: Memory 对象

        Returns:
            插入的记忆ID
        """
        memory_data = {
            'content': memory.content,
            'importance': memory.importance,
            'category': memory.category,
            'access_count': memory.access_count,
            'privacy_level': memory.privacy_level,
            'is_encrypted': memory.is_encrypted,
            'retention_days': memory.retention_days,
            'source': memory.source
        }
        result = self.create_memory(memory_data)
        return result.id if result else None

    def get_memory(self, memory_id: int) -> Optional[Memory]:
        """
        根据 ID 获取记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            Memory 对象，如果不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        # 更新访问次数和最后访问时间
        cursor.execute("""
            UPDATE memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), memory_id))
        conn.commit()

        return Memory.from_row(tuple(row))

    def get_all_memories(self, limit: int = None, offset: int = 0) -> List[Memory]:
        """
        获取所有记忆

        Args:
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            Memory 对象列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM memories ORDER BY created_at DESC"
        params = []

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset > 0:
                query += " OFFSET ?"
                params.append(offset)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Memory.from_row(tuple(row)) for row in rows]

    # ==================== 玩家数据操作 ====================

    def save_player(self, name: str, data: Dict[str, Any]) -> bool:
        """
        保存玩家数据

        Args:
            name: 玩家名称
            data: 玩家数据字典

        Returns:
            是否保存成功
        """
        import json
        from datetime import datetime

        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        data_json = json.dumps(data, ensure_ascii=False)

        # 检查是否已存在该玩家
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        existing = cursor.fetchone()

        if existing:
            # 更新现有记录
            cursor.execute(
                "UPDATE players SET data = ?, updated_at = ? WHERE name = ?",
                (data_json, now, name)
            )
        else:
            # 创建新记录
            cursor.execute(
                "INSERT INTO players (name, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, data_json, now, now)
            )

        conn.commit()
        return True

    def load_player(self, name: str = None) -> Optional[Dict[str, Any]]:
        """
        加载玩家数据

        Args:
            name: 玩家名称，如果为None则加载最新的玩家

        Returns:
            玩家数据字典，如果不存在则返回None
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        if name:
            cursor.execute(
                "SELECT data FROM players WHERE name = ? ORDER BY updated_at DESC LIMIT 1",
                (name,)
            )
        else:
            cursor.execute(
                "SELECT data FROM players ORDER BY updated_at DESC LIMIT 1"
            )

        row = cursor.fetchone()
        if row:
            return json.loads(row['data'])
        return None

    def delete_player(self, name: str) -> bool:
        """
        删除玩家数据

        Args:
            name: 玩家名称

        Returns:
            是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM players WHERE name = ?", (name,))
        conn.commit()

        return cursor.rowcount > 0

    def list_players(self) -> List[Dict[str, Any]]:
        """
        列出所有玩家

        Returns:
            玩家列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, created_at, updated_at FROM players ORDER BY updated_at DESC"
        )

        return [
            {
                'name': row['name'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            for row in cursor.fetchall()
        ]

    def update_memory(self, memory_id: int, updates: Dict[str, Any]) -> Optional[Memory]:
        """
        更新记忆

        Args:
            memory_id: 记忆 ID
            updates: 要更新的字段字典

        Returns:
            更新后的 Memory 对象，如果不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 检查记忆是否存在
        cursor.execute("SELECT id FROM memories WHERE id = ?", (memory_id,))
        if cursor.fetchone() is None:
            return None

        # 构建更新语句
        allowed_fields = {
            'content', 'importance', 'category', 'privacy_level',
            'is_encrypted', 'retention_days'
        }

        update_fields = []
        values = []

        for key, value in updates.items():
            if key in allowed_fields:
                update_fields.append(f"{key} = ?")
                # 转换布尔值为整数
                if key == 'is_encrypted':
                    value = 1 if value else 0
                values.append(value)

        if not update_fields:
            return self.get_memory(memory_id)

        values.append(memory_id)

        query = f"UPDATE memories SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()

        return self.get_memory(memory_id)

    def delete_memory(self, memory_id: int) -> bool:
        """
        删除记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            是否成功删除
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.commit()

        return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            包含统计信息的字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 总记忆数
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_count = cursor.fetchone()[0]

        # 分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM memories
            GROUP BY category
        """)
        category_stats = {row['category']: row['count'] for row in cursor.fetchall()}

        # 平均重要性
        cursor.execute("SELECT AVG(importance) FROM memories")
        avg_importance = cursor.fetchone()[0] or 0

        # 平均隐私级别
        cursor.execute("SELECT AVG(privacy_level) FROM memories")
        avg_privacy = cursor.fetchone()[0] or 0

        # 加密记忆数
        cursor.execute("SELECT COUNT(*) FROM memories WHERE is_encrypted = 1")
        encrypted_count = cursor.fetchone()[0]

        # 总访问次数
        cursor.execute("SELECT SUM(access_count) FROM memories")
        total_access_count = cursor.fetchone()[0] or 0

        # 最近创建的记忆
        cursor.execute("""
            SELECT created_at FROM memories
            ORDER BY created_at DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        latest_created = row['created_at'] if row else None

        return {
            'total_count': total_count,
            'category_stats': category_stats,
            'avg_importance': round(avg_importance, 2),
            'avg_privacy_level': round(avg_privacy, 2),
            'encrypted_count': encrypted_count,
            'total_access_count': total_access_count,
            'latest_created': latest_created
        }

    def search_memories(
        self,
        keyword: str = None,
        category: str = None,
        min_importance: int = None,
        max_importance: int = None
    ) -> List[Memory]:
        """
        搜索记忆

        Args:
            keyword: 关键词搜索（内容模糊匹配）
            category: 分类筛选
            min_importance: 最小重要性
            max_importance: 最大重要性

        Returns:
            匹配的 Memory 对象列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if keyword:
            conditions.append("content LIKE ?")
            params.append(f"%{keyword}%")

        if category:
            conditions.append("category = ?")
            params.append(category)

        if min_importance is not None:
            conditions.append("importance >= ?")
            params.append(min_importance)

        if max_importance is not None:
            conditions.append("importance <= ?")
            params.append(max_importance)

        query = "SELECT * FROM memories"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY importance DESC, created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Memory.from_row(tuple(row)) for row in rows]

    # ==================== 无限生成内容存储操作 ====================

    def save_generated_map(self, map_data: Dict[str, Any]) -> str:
        """
        保存生成的地图

        Args:
            map_data: 地图数据字典，包含 name, map_type, level, size, description 等字段

        Returns:
            保存的地图ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        map_id = map_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO generated_maps (
                id, name, map_type, level, size, description, history,
                environment, connections, npcs, monsters, items, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            map_id,
            map_data.get('name', ''),
            map_data.get('map_type', ''),
            map_data.get('level', 1),
            map_data.get('size', ''),
            map_data.get('description', ''),
            map_data.get('history', ''),
            map_data.get('environment', ''),
            json.dumps(map_data.get('connections', []), ensure_ascii=False),
            json.dumps(map_data.get('npcs', []), ensure_ascii=False),
            json.dumps(map_data.get('monsters', []), ensure_ascii=False),
            json.dumps(map_data.get('items', []), ensure_ascii=False),
            now
        ))

        conn.commit()
        return map_id

    def save_generated_npc(self, npc_data: Dict[str, Any]) -> str:
        """
        保存生成的NPC（基础方法，保持向后兼容）

        Args:
            npc_data: NPC数据字典，包含 name, surname, gender, age, realm_level 等字段

        Returns:
            保存的NPC ID
        """
        # 调用完整保存方法
        return self.save_npc_full(npc_data)

    def save_npc_full(self, npc_data: Dict[str, Any]) -> str:
        """
        保存完整NPC数据（包含所有系统数据）

        Args:
            npc_data: 完整NPC数据字典，包含所有系统数据

        Returns:
            保存的NPC ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        npc_id = npc_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        # 处理 favor 字段，如果是字典则转换为JSON字符串
        favor = npc_data.get('favor', 0)
        if isinstance(favor, dict):
            # 如果是字典，取第一个值或转换为JSON
            if favor:
                favor = list(favor.values())[0] if favor else 0
            else:
                favor = 0

        # 提取基础数据
        base_data = {
            'id': npc_id,
            'name': npc_data.get('name', ''),
            'dao_name': npc_data.get('dao_name', ''),
            'age': npc_data.get('age', 0),
            'lifespan': npc_data.get('lifespan', 100),
            'realm_level': npc_data.get('realm_level', 0),
            'sect': npc_data.get('sect', ''),
            'sect_type': npc_data.get('sect_type', ''),
            'sect_specialty': npc_data.get('sect_specialty', ''),
            'personality': npc_data.get('personality', ''),
            'occupation': npc_data.get('occupation', ''),
            'location': npc_data.get('location', ''),
            'favor': npc_data.get('favor', {}),
            'is_alive': npc_data.get('is_alive', True),
            'death_info': npc_data.get('death_info', {}),
            'can_resurrect': npc_data.get('can_resurrect', True),
            'morality': npc_data.get('morality', 0),
            'attack': npc_data.get('attack', 10),
            'defense': npc_data.get('defense', 5),
            'speed': npc_data.get('speed', 8),
            'crit_rate': npc_data.get('crit_rate', 0.03),
            'dodge_rate': npc_data.get('dodge_rate', 0.03),
            'combat_wins': npc_data.get('combat_wins', 0),
            'combat_losses': npc_data.get('combat_losses', 0),
            'combat_record': npc_data.get('combat_record', []),
        }

        # 提取各系统数据
        goals_data = npc_data.get('goals', [])
        schedule_data = npc_data.get('schedule', {})
        values_data = npc_data.get('values', {})
        speaking_style_data = npc_data.get('speaking_style', {})
        life_record_data = npc_data.get('life_record', {})
        enhanced_memory_data = npc_data.get('enhanced_memory', {})
        combat_record_data = npc_data.get('combat_record', [])

        # 提取独立系统数据（如果存在）
        independent_data = {}
        if 'independent' in npc_data:
            independent_data = npc_data['independent']
        elif 'needs' in npc_data or 'personality' in npc_data or 'memories' in npc_data:
            # 独立系统数据可能在顶层
            independent_data = {
                'needs': npc_data.get('needs', {}),
                'personality': npc_data.get('personality', {}),
                'memories': npc_data.get('memories', []),
                'relationships': npc_data.get('relationships', {}),
                'goals': npc_data.get('independent_goals', []),
            }

        cursor.execute("""
            INSERT OR REPLACE INTO generated_npcs (
                id, name, surname, full_name, gender, age, realm_level,
                occupation, personality, appearance, catchphrase, story,
                location, favor, created_at,
                is_alive, death_info, can_resurrect, morality,
                npc_data, independent_data, goals_data, schedule_data,
                values_data, speaking_style_data, life_record_data,
                enhanced_memory_data, combat_record_data, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            npc_id,
            npc_data.get('name', ''),
            npc_data.get('surname', ''),
            npc_data.get('full_name', ''),
            npc_data.get('gender', ''),
            npc_data.get('age', 0),
            str(npc_data.get('realm_level', '')),
            npc_data.get('occupation', ''),
            npc_data.get('personality', ''),
            npc_data.get('appearance', ''),
            npc_data.get('catchphrase', ''),
            npc_data.get('story', ''),
            npc_data.get('location', ''),
            favor,
            npc_data.get('created_at', now),
            1 if npc_data.get('is_alive', True) else 0,
            json.dumps(npc_data.get('death_info', {}), ensure_ascii=False),
            1 if npc_data.get('can_resurrect', True) else 0,
            npc_data.get('morality', 0),
            json.dumps(base_data, ensure_ascii=False),
            json.dumps(independent_data, ensure_ascii=False),
            json.dumps(goals_data, ensure_ascii=False),
            json.dumps(schedule_data, ensure_ascii=False),
            json.dumps(values_data, ensure_ascii=False),
            json.dumps(speaking_style_data, ensure_ascii=False),
            json.dumps(life_record_data, ensure_ascii=False),
            json.dumps(enhanced_memory_data, ensure_ascii=False),
            json.dumps(combat_record_data, ensure_ascii=False),
            now
        ))

        conn.commit()
        return npc_id

    def save_generated_item(self, item_data: Dict[str, Any]) -> str:
        """
        保存生成的物品

        Args:
            item_data: 物品数据字典，包含 name, item_type, rarity, attributes 等字段

        Returns:
            保存的物品ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        item_id = item_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO generated_items (
                id, name, item_type, rarity, attributes, effects,
                description, origin, legend, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            item_data.get('name', ''),
            item_data.get('item_type', ''),
            item_data.get('rarity', ''),
            json.dumps(item_data.get('attributes', {}), ensure_ascii=False),
            json.dumps(item_data.get('effects', {}), ensure_ascii=False),
            item_data.get('description', ''),
            item_data.get('origin', ''),
            item_data.get('legend', ''),
            now
        ))

        conn.commit()
        return item_id

    def save_generated_monster(self, monster_data: Dict[str, Any]) -> str:
        """
        保存生成的妖兽

        Args:
            monster_data: 妖兽数据字典，包含 name, monster_type, level, realm_level 等字段

        Returns:
            保存的妖兽ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        monster_id = monster_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO generated_monsters (
                id, name, monster_type, level, realm_level, attributes,
                drops, description, habits, weakness, location, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            monster_id,
            monster_data.get('name', ''),
            monster_data.get('monster_type', ''),
            monster_data.get('level', 1),
            monster_data.get('realm_level', ''),
            json.dumps(monster_data.get('attributes', {}), ensure_ascii=False),
            json.dumps(monster_data.get('drops', []), ensure_ascii=False),
            monster_data.get('description', ''),
            monster_data.get('habits', ''),
            monster_data.get('weakness', ''),
            monster_data.get('location', ''),
            now
        ))

        conn.commit()
        return monster_id

    def get_generated_map(self, map_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取地图

        Args:
            map_id: 地图ID

        Returns:
            地图数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM generated_maps WHERE id = ?", (map_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'map_type': row['map_type'],
            'level': row['level'],
            'size': row['size'],
            'description': row['description'],
            'history': row['history'],
            'environment': row['environment'],
            'connections': json.loads(row['connections']) if row['connections'] else [],
            'npcs': json.loads(row['npcs']) if row['npcs'] else [],
            'monsters': json.loads(row['monsters']) if row['monsters'] else [],
            'items': json.loads(row['items']) if row['items'] else [],
            'created_at': row['created_at']
        }

    def get_generated_npcs_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        获取某地图的NPC（基础方法，保持向后兼容）

        Args:
            location: 地图名称或ID

        Returns:
            NPC数据字典列表
        """
        return self.get_npcs_by_location_full(location)

    def load_npc_full(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        加载完整NPC数据（包含所有系统数据）

        Args:
            npc_id: NPC ID

        Returns:
            完整NPC数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM generated_npcs WHERE id = ?", (npc_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        # 构建完整NPC数据
        npc_data = self._parse_npc_row(row)
        return npc_data

    def get_npcs_by_location_full(self, location: str) -> List[Dict[str, Any]]:
        """
        获取某地图的所有完整NPC数据

        Args:
            location: 地图名称或ID

        Returns:
            完整NPC数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM generated_npcs WHERE location = ? ORDER BY created_at DESC
        """, (location,))

        rows = cursor.fetchall()
        return [self._parse_npc_row(row) for row in rows]

    def get_npc_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        通过名称查找NPC

        Args:
            name: NPC名称（name, full_name 或 id）

        Returns:
            NPC数据字典，如果不存在则返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 先尝试通过id查找
            cursor.execute("SELECT * FROM generated_npcs WHERE id = ?", (name,))
            row = cursor.fetchone()
            if row:
                return self._parse_npc_row(row)

            # 再通过name查找
            cursor.execute("SELECT * FROM generated_npcs WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return self._parse_npc_row(row)

            # 最后通过full_name查找
            cursor.execute("SELECT * FROM generated_npcs WHERE full_name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return self._parse_npc_row(row)

            return None
        except sqlite3.Error as e:
            print(f"查找NPC失败: {e}")
            return None

    def _parse_npc_row(self, row) -> Dict[str, Any]:
        """
        解析NPC数据库行数据为完整NPC字典

        Args:
            row: 数据库行

        Returns:
            完整NPC数据字典
        """
        # 基础数据
        npc_data = {
            'id': row['id'],
            'name': row['name'],
            'surname': row['surname'],
            'full_name': row['full_name'],
            'gender': row['gender'],
            'age': row['age'],
            'realm_level': row['realm_level'],
            'occupation': row['occupation'],
            'personality': row['personality'],
            'appearance': row['appearance'],
            'catchphrase': row['catchphrase'],
            'story': row['story'],
            'location': row['location'],
            'favor': row['favor'],
            'created_at': row['created_at'],
            'is_alive': bool(row['is_alive']) if row['is_alive'] is not None else True,
            'can_resurrect': bool(row['can_resurrect']) if row['can_resurrect'] is not None else True,
            'morality': row['morality'] if row['morality'] is not None else 0,
        }

        # 解析死亡信息
        if row['death_info']:
            try:
                npc_data['death_info'] = json.loads(row['death_info'])
            except (json.JSONDecodeError, TypeError):
                npc_data['death_info'] = {}
        else:
            npc_data['death_info'] = {}

        # 解析完整NPC数据（如果存在）
        if row['npc_data']:
            try:
                full_data = json.loads(row['npc_data'])
                # 确保解析后的数据是字典类型
                if isinstance(full_data, dict):
                    # 合并完整数据，以完整数据为准
                    npc_data.update(full_data)
                elif isinstance(full_data, str):
                    # 如果还是字符串，尝试再次解析（双重JSON编码的情况）
                    try:
                        full_data = json.loads(full_data)
                        if isinstance(full_data, dict):
                            npc_data.update(full_data)
                    except (json.JSONDecodeError, TypeError):
                        pass
            except (json.JSONDecodeError, TypeError):
                pass

        # 解析独立系统数据
        if row['independent_data']:
            try:
                npc_data['independent'] = json.loads(row['independent_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['independent'] = {}

        # 解析目标系统数据
        if row['goals_data']:
            try:
                npc_data['goals'] = json.loads(row['goals_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['goals'] = []

        # 解析日程系统数据
        if row['schedule_data']:
            try:
                npc_data['schedule'] = json.loads(row['schedule_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['schedule'] = {}

        # 解析价值观数据
        if row['values_data']:
            try:
                npc_data['values'] = json.loads(row['values_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['values'] = {}

        # 解析说话风格数据
        if row['speaking_style_data']:
            try:
                npc_data['speaking_style'] = json.loads(row['speaking_style_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['speaking_style'] = {}

        # 解析成长记录数据
        if row['life_record_data']:
            try:
                npc_data['life_record'] = json.loads(row['life_record_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['life_record'] = {}

        # 解析增强记忆数据
        if row['enhanced_memory_data']:
            try:
                npc_data['enhanced_memory'] = json.loads(row['enhanced_memory_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['enhanced_memory'] = {}

        # 解析战斗记录数据
        if row['combat_record_data']:
            try:
                npc_data['combat_record'] = json.loads(row['combat_record_data'])
            except (json.JSONDecodeError, TypeError):
                npc_data['combat_record'] = []

        return npc_data

    # ==================== 剧情系统操作 ====================

    def init_story_tables(self):
        """创建剧情系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 story_chapters 表 - 剧情章节定义
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_chapters (
                id TEXT PRIMARY KEY,
                chapter_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                story_type TEXT NOT NULL DEFAULT 'main',
                realm_required INTEGER DEFAULT 0,
                location_required TEXT,
                pre_chapter_id TEXT,
                is_repeatable INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 story_scenes 表 - 剧情场景
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_scenes (
                id TEXT PRIMARY KEY,
                chapter_id TEXT NOT NULL,
                scene_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                background TEXT,
                location TEXT,
                npcs TEXT,
                FOREIGN KEY (chapter_id) REFERENCES story_chapters(id) ON DELETE CASCADE
            )
        """)

        # 创建 story_dialogues 表 - 剧情对话
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_dialogues (
                id TEXT PRIMARY KEY,
                scene_id TEXT NOT NULL,
                dialogue_order INTEGER NOT NULL,
                speaker_type TEXT NOT NULL,
                speaker_id TEXT,
                speaker_name TEXT NOT NULL,
                content TEXT NOT NULL,
                emotion TEXT,
                animation TEXT,
                FOREIGN KEY (scene_id) REFERENCES story_scenes(id) ON DELETE CASCADE
            )
        """)

        # 创建 story_choices 表 - 剧情选择
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_choices (
                id TEXT PRIMARY KEY,
                scene_id TEXT NOT NULL,
                choice_order INTEGER NOT NULL,
                choice_text TEXT NOT NULL,
                next_scene_id TEXT,
                effects TEXT,
                condition_type TEXT,
                condition_value TEXT,
                FOREIGN KEY (scene_id) REFERENCES story_scenes(id) ON DELETE CASCADE
            )
        """)

        # 创建 player_story_records 表 - 玩家剧情记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_story_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                chapter_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'locked',
                current_scene_id TEXT,
                completed_scenes TEXT,
                choices_made TEXT,
                started_at TEXT,
                completed_at TEXT,
                replay_count INTEGER DEFAULT 0,
                UNIQUE(player_id, chapter_id)
            )
        """)

        # 创建 player_choice_effects 表 - 玩家选择影响记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_choice_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                chapter_id TEXT NOT NULL,
                choice_id TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                effect_target TEXT,
                effect_value TEXT,
                is_applied INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 story_rewards 表 - 剧情奖励
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_rewards (
                id TEXT PRIMARY KEY,
                chapter_id TEXT NOT NULL,
                reward_type TEXT NOT NULL,
                reward_item TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                condition_type TEXT,
                condition_value TEXT,
                FOREIGN KEY (chapter_id) REFERENCES story_chapters(id) ON DELETE CASCADE
            )
        """)

        # 创建 player_story_rewards 表 - 玩家已领取的剧情奖励
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_story_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                chapter_id TEXT NOT NULL,
                reward_id TEXT NOT NULL,
                claimed_at TEXT NOT NULL,
                UNIQUE(player_id, reward_id)
            )
        """)

        # 创建 story_branch_conditions 表 - 剧情分支条件
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_branch_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_key TEXT NOT NULL,
                condition_value TEXT NOT NULL,
                compare_operator TEXT DEFAULT 'eq',
                target_scene_id TEXT NOT NULL
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_chapters_type ON story_chapters(story_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_chapters_realm ON story_chapters(realm_required)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_scenes_chapter ON story_scenes(chapter_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_dialogues_scene ON story_dialogues(scene_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_choices_scene ON story_choices(scene_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_story_player ON player_story_records(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_story_chapter ON player_story_records(chapter_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_choice_effects_player ON player_choice_effects(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_story_rewards_chapter ON story_rewards(chapter_id)
        """)

        conn.commit()

    def save_story_chapter(self, chapter_data: Dict[str, Any]) -> str:
        """
        保存剧情章节

        Args:
            chapter_data: 章节数据字典

        Returns:
            章节ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        chapter_id = chapter_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO story_chapters (
                id, chapter_number, title, description, story_type,
                realm_required, location_required, pre_chapter_id, is_repeatable, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chapter_id,
            chapter_data.get('chapter_number', 1),
            chapter_data.get('title', ''),
            chapter_data.get('description', ''),
            chapter_data.get('story_type', 'main'),
            chapter_data.get('realm_required', 0),
            chapter_data.get('location_required', ''),
            chapter_data.get('pre_chapter_id', ''),
            1 if chapter_data.get('is_repeatable', False) else 0,
            now
        ))

        conn.commit()
        return chapter_id

    def get_story_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        获取剧情章节

        Args:
            chapter_id: 章节ID

        Returns:
            章节数据字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM story_chapters WHERE id = ?", (chapter_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'chapter_number': row['chapter_number'],
            'title': row['title'],
            'description': row['description'],
            'story_type': row['story_type'],
            'realm_required': row['realm_required'],
            'location_required': row['location_required'],
            'pre_chapter_id': row['pre_chapter_id'],
            'is_repeatable': bool(row['is_repeatable']),
            'created_at': row['created_at']
        }

    def get_story_chapters_by_type(self, story_type: str, realm_level: int = None) -> List[Dict[str, Any]]:
        """
        获取指定类型的剧情章节

        Args:
            story_type: 剧情类型（main/side）
            realm_level: 境界等级筛选

        Returns:
            章节列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if realm_level is not None:
            cursor.execute("""
                SELECT * FROM story_chapters 
                WHERE story_type = ? AND realm_required <= ?
                ORDER BY chapter_number ASC
            """, (story_type, realm_level))
        else:
            cursor.execute("""
                SELECT * FROM story_chapters WHERE story_type = ? ORDER BY chapter_number ASC
            """, (story_type,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'chapter_number': row['chapter_number'],
                'title': row['title'],
                'description': row['description'],
                'story_type': row['story_type'],
                'realm_required': row['realm_required'],
                'location_required': row['location_required'],
                'pre_chapter_id': row['pre_chapter_id'],
                'is_repeatable': bool(row['is_repeatable']),
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def save_story_scene(self, scene_data: Dict[str, Any]) -> str:
        """
        保存剧情场景

        Args:
            scene_data: 场景数据字典

        Returns:
            场景ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        scene_id = scene_data.get('id', str(uuid.uuid4()))

        cursor.execute("""
            INSERT OR REPLACE INTO story_scenes (
                id, chapter_id, scene_number, title, background, location, npcs
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            scene_id,
            scene_data.get('chapter_id', ''),
            scene_data.get('scene_number', 1),
            scene_data.get('title', ''),
            scene_data.get('background', ''),
            scene_data.get('location', ''),
            json.dumps(scene_data.get('npcs', []), ensure_ascii=False)
        ))

        conn.commit()
        return scene_id

    def get_story_scenes(self, chapter_id: str) -> List[Dict[str, Any]]:
        """
        获取章节的所有场景

        Args:
            chapter_id: 章节ID

        Returns:
            场景列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM story_scenes WHERE chapter_id = ? ORDER BY scene_number ASC
        """, (chapter_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'chapter_id': row['chapter_id'],
                'scene_number': row['scene_number'],
                'title': row['title'],
                'background': row['background'],
                'location': row['location'],
                'npcs': json.loads(row['npcs']) if row['npcs'] else []
            }
            for row in rows
        ]

    def save_story_dialogue(self, dialogue_data: Dict[str, Any]) -> str:
        """
        保存剧情对话

        Args:
            dialogue_data: 对话数据字典

        Returns:
            对话ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        dialogue_id = dialogue_data.get('id', str(uuid.uuid4()))

        cursor.execute("""
            INSERT OR REPLACE INTO story_dialogues (
                id, scene_id, dialogue_order, speaker_type, speaker_id, speaker_name, content, emotion, animation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dialogue_id,
            dialogue_data.get('scene_id', ''),
            dialogue_data.get('dialogue_order', 1),
            dialogue_data.get('speaker_type', 'npc'),
            dialogue_data.get('speaker_id', ''),
            dialogue_data.get('speaker_name', ''),
            dialogue_data.get('content', ''),
            dialogue_data.get('emotion', ''),
            dialogue_data.get('animation', '')
        ))

        conn.commit()
        return dialogue_id

    def get_scene_dialogues(self, scene_id: str) -> List[Dict[str, Any]]:
        """
        获取场景的所有对话

        Args:
            scene_id: 场景ID

        Returns:
            对话列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM story_dialogues WHERE scene_id = ? ORDER BY dialogue_order ASC
        """, (scene_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'scene_id': row['scene_id'],
                'dialogue_order': row['dialogue_order'],
                'speaker_type': row['speaker_type'],
                'speaker_id': row['speaker_id'],
                'speaker_name': row['speaker_name'],
                'content': row['content'],
                'emotion': row['emotion'],
                'animation': row['animation']
            }
            for row in rows
        ]

    def save_story_choice(self, choice_data: Dict[str, Any]) -> str:
        """
        保存剧情选择

        Args:
            choice_data: 选择数据字典

        Returns:
            选择ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        choice_id = choice_data.get('id', str(uuid.uuid4()))

        cursor.execute("""
            INSERT OR REPLACE INTO story_choices (
                id, scene_id, choice_order, choice_text, next_scene_id, effects, condition_type, condition_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            choice_id,
            choice_data.get('scene_id', ''),
            choice_data.get('choice_order', 1),
            choice_data.get('choice_text', ''),
            choice_data.get('next_scene_id', ''),
            json.dumps(choice_data.get('effects', {}), ensure_ascii=False),
            choice_data.get('condition_type', ''),
            choice_data.get('condition_value', '')
        ))

        conn.commit()
        return choice_id

    def get_scene_choices(self, scene_id: str) -> List[Dict[str, Any]]:
        """
        获取场景的所有选择

        Args:
            scene_id: 场景ID

        Returns:
            选择列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM story_choices WHERE scene_id = ? ORDER BY choice_order ASC
        """, (scene_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'scene_id': row['scene_id'],
                'choice_order': row['choice_order'],
                'choice_text': row['choice_text'],
                'next_scene_id': row['next_scene_id'],
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'condition_type': row['condition_type'],
                'condition_value': row['condition_value']
            }
            for row in rows
        ]

    def create_player_story_record(self, player_id: str, chapter_id: str) -> bool:
        """
        创建玩家剧情记录

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR IGNORE INTO player_story_records (
                    player_id, chapter_id, status, completed_scenes, choices_made, started_at
                ) VALUES (?, ?, 'active', '[]', '[]', ?)
            """, (player_id, chapter_id, now))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"创建剧情记录失败: {e}")
            return False

    def get_player_story_record(self, player_id: str, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家剧情记录

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID

        Returns:
            剧情记录数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM player_story_records WHERE player_id = ? AND chapter_id = ?
        """, (player_id, chapter_id))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'player_id': row['player_id'],
            'chapter_id': row['chapter_id'],
            'status': row['status'],
            'current_scene_id': row['current_scene_id'],
            'completed_scenes': json.loads(row['completed_scenes']) if row['completed_scenes'] else [],
            'choices_made': json.loads(row['choices_made']) if row['choices_made'] else [],
            'started_at': row['started_at'],
            'completed_at': row['completed_at'],
            'replay_count': row['replay_count']
        }

    def update_player_story_progress(self, player_id: str, chapter_id: str, scene_id: str) -> bool:
        """
        更新玩家剧情进度

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID
            scene_id: 当前场景ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取当前已完成的场景
            cursor.execute("""
                SELECT completed_scenes FROM player_story_records 
                WHERE player_id = ? AND chapter_id = ?
            """, (player_id, chapter_id))
            row = cursor.fetchone()

            completed_scenes = json.loads(row['completed_scenes']) if row and row['completed_scenes'] else []
            if scene_id not in completed_scenes:
                completed_scenes.append(scene_id)

            cursor.execute("""
                UPDATE player_story_records 
                SET current_scene_id = ?, completed_scenes = ?, status = 'active'
                WHERE player_id = ? AND chapter_id = ?
            """, (scene_id, json.dumps(completed_scenes, ensure_ascii=False), player_id, chapter_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新剧情进度失败: {e}")
            return False

    def record_player_choice(self, player_id: str, chapter_id: str, choice_id: str) -> bool:
        """
        记录玩家选择

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID
            choice_id: 选择ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取当前已做的选择
            cursor.execute("""
                SELECT choices_made FROM player_story_records 
                WHERE player_id = ? AND chapter_id = ?
            """, (player_id, chapter_id))
            row = cursor.fetchone()

            choices_made = json.loads(row['choices_made']) if row and row['choices_made'] else []
            if choice_id not in choices_made:
                choices_made.append(choice_id)

            cursor.execute("""
                UPDATE player_story_records 
                SET choices_made = ?
                WHERE player_id = ? AND chapter_id = ?
            """, (json.dumps(choices_made, ensure_ascii=False), player_id, chapter_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"记录玩家选择失败: {e}")
            return False

    def complete_player_story(self, player_id: str, chapter_id: str) -> bool:
        """
        完成玩家剧情

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE player_story_records 
                SET status = 'completed', completed_at = ?
                WHERE player_id = ? AND chapter_id = ?
            """, (now, player_id, chapter_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"完成剧情失败: {e}")
            return False

    def replay_player_story(self, player_id: str, chapter_id: str) -> bool:
        """
        重置玩家剧情（用于回放）

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE player_story_records 
                SET current_scene_id = NULL, completed_scenes = '[]', choices_made = '[]',
                    status = 'active', replay_count = replay_count + 1
                WHERE player_id = ? AND chapter_id = ?
            """, (player_id, chapter_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"重置剧情失败: {e}")
            return False

    def save_choice_effect(self, player_id: str, chapter_id: str, choice_id: str,
                          effect_type: str, effect_target: str, effect_value: str) -> bool:
        """
        保存选择影响

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID
            choice_id: 选择ID
            effect_type: 影响类型
            effect_target: 影响目标
            effect_value: 影响值

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO player_choice_effects 
                (player_id, chapter_id, choice_id, effect_type, effect_target, effect_value, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (player_id, chapter_id, choice_id, effect_type, effect_target, effect_value, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存选择影响失败: {e}")
            return False

    def get_player_choice_effects(self, player_id: str, effect_type: str = None) -> List[Dict[str, Any]]:
        """
        获取玩家的选择影响

        Args:
            player_id: 玩家ID
            effect_type: 影响类型筛选

        Returns:
            影响列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if effect_type:
            cursor.execute("""
                SELECT * FROM player_choice_effects 
                WHERE player_id = ? AND effect_type = ? AND is_applied = 0
                ORDER BY created_at DESC
            """, (player_id, effect_type))
        else:
            cursor.execute("""
                SELECT * FROM player_choice_effects 
                WHERE player_id = ? AND is_applied = 0
                ORDER BY created_at DESC
            """, (player_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'chapter_id': row['chapter_id'],
                'choice_id': row['choice_id'],
                'effect_type': row['effect_type'],
                'effect_target': row['effect_target'],
                'effect_value': row['effect_value'],
                'is_applied': bool(row['is_applied']),
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def mark_choice_effect_applied(self, effect_id: int) -> bool:
        """
        标记选择影响已应用

        Args:
            effect_id: 影响记录ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE player_choice_effects SET is_applied = 1 WHERE id = ?
            """, (effect_id,))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"标记选择影响失败: {e}")
            return False

    def save_story_reward(self, reward_data: Dict[str, Any]) -> str:
        """
        保存剧情奖励

        Args:
            reward_data: 奖励数据字典

        Returns:
            奖励ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        reward_id = reward_data.get('id', str(uuid.uuid4()))

        cursor.execute("""
            INSERT OR REPLACE INTO story_rewards (
                id, chapter_id, reward_type, reward_item, quantity, condition_type, condition_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            reward_id,
            reward_data.get('chapter_id', ''),
            reward_data.get('reward_type', 'item'),
            reward_data.get('reward_item', ''),
            reward_data.get('quantity', 1),
            reward_data.get('condition_type', ''),
            reward_data.get('condition_value', '')
        ))

        conn.commit()
        return reward_id

    def get_story_rewards(self, chapter_id: str) -> List[Dict[str, Any]]:
        """
        获取章节的所有奖励

        Args:
            chapter_id: 章节ID

        Returns:
            奖励列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM story_rewards WHERE chapter_id = ?
        """, (chapter_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'chapter_id': row['chapter_id'],
                'reward_type': row['reward_type'],
                'reward_item': row['reward_item'],
                'quantity': row['quantity'],
                'condition_type': row['condition_type'],
                'condition_value': row['condition_value']
            }
            for row in rows
        ]

    def claim_story_reward(self, player_id: str, chapter_id: str, reward_id: str) -> bool:
        """
        领取剧情奖励

        Args:
            player_id: 玩家ID
            chapter_id: 章节ID
            reward_id: 奖励ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR IGNORE INTO player_story_rewards (player_id, chapter_id, reward_id, claimed_at)
                VALUES (?, ?, ?, ?)
            """, (player_id, chapter_id, reward_id, now))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"领取剧情奖励失败: {e}")
            return False

    def has_claimed_reward(self, player_id: str, reward_id: str) -> bool:
        """
        检查玩家是否已领取奖励

        Args:
            player_id: 玩家ID
            reward_id: 奖励ID

        Returns:
            是否已领取
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM player_story_rewards WHERE player_id = ? AND reward_id = ?
        """, (player_id, reward_id))

        return cursor.fetchone() is not None

    def get_player_completed_stories(self, player_id: str, story_type: str = None) -> List[Dict[str, Any]]:
        """
        获取玩家已完成的剧情

        Args:
            player_id: 玩家ID
            story_type: 剧情类型筛选

        Returns:
            已完成剧情列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if story_type:
            cursor.execute("""
                SELECT psr.*, sc.title, sc.story_type, sc.chapter_number
                FROM player_story_records psr
                JOIN story_chapters sc ON psr.chapter_id = sc.id
                WHERE psr.player_id = ? AND psr.status = 'completed' AND sc.story_type = ?
                ORDER BY psr.completed_at DESC
            """, (player_id, story_type))
        else:
            cursor.execute("""
                SELECT psr.*, sc.title, sc.story_type, sc.chapter_number
                FROM player_story_records psr
                JOIN story_chapters sc ON psr.chapter_id = sc.id
                WHERE psr.player_id = ? AND psr.status = 'completed'
                ORDER BY psr.completed_at DESC
            """, (player_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'chapter_id': row['chapter_id'],
                'title': row['title'],
                'story_type': row['story_type'],
                'chapter_number': row['chapter_number'],
                'completed_at': row['completed_at'],
                'replay_count': row['replay_count']
            }
            for row in rows
        ]

    # ==================== 世界演化系统操作 ====================

    def init_world_evolution_tables(self):
        """创建世界演化系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 world_timeline 表 - 世界时间线（记录重要事件）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                location TEXT,
                importance INTEGER DEFAULT 5,
                is_historic INTEGER DEFAULT 0,
                involved_npcs TEXT,
                involved_factions TEXT,
                event_data TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 world_events 表 - 世界事件（当前活跃事件）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                start_year INTEGER NOT NULL,
                start_month INTEGER NOT NULL,
                start_day INTEGER NOT NULL,
                end_year INTEGER,
                end_month INTEGER,
                end_day INTEGER,
                location TEXT,
                scope TEXT DEFAULT 'local',
                importance INTEGER DEFAULT 5,
                involved_npcs TEXT,
                involved_factions TEXT,
                event_data TEXT,
                player_participated INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 创建 faction_changes 表 - 势力变迁记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faction_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faction_id TEXT NOT NULL,
                faction_name TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_description TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                old_value TEXT,
                new_value TEXT,
                related_npc TEXT,
                related_event TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 npc_evolution 表 - NPC演化记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc_id TEXT NOT NULL,
                npc_name TEXT NOT NULL,
                evolution_type TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                old_realm INTEGER,
                new_realm INTEGER,
                old_location TEXT,
                new_location TEXT,
                action_taken TEXT,
                action_result TEXT,
                related_event TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 treasures 表 - 天材地宝
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS treasures (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                treasure_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                description TEXT NOT NULL,
                effects TEXT NOT NULL,
                spawn_location TEXT,
                spawn_year INTEGER,
                spawn_month INTEGER,
                spawn_day INTEGER,
                discoverer_id TEXT,
                discoverer_name TEXT,
                is_discovered INTEGER DEFAULT 0,
                is_claimed INTEGER DEFAULT 0,
                guardian_monster TEXT,
                guardian_level INTEGER DEFAULT 1,
                expire_year INTEGER,
                expire_month INTEGER,
                expire_day INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 player_world_participation 表 - 玩家参与世界事件记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_world_participation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                participation_type TEXT NOT NULL,
                participation_description TEXT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                contribution_score INTEGER DEFAULT 0,
                rewards_received TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(player_id, event_id)
            )
        """)

        # 创建 world_economy 表 - 世界经济记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_economy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                price REAL NOT NULL,
                supply_level INTEGER DEFAULT 50,
                demand_level INTEGER DEFAULT 50,
                location TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timeline_year ON world_timeline(year, month, day)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timeline_type ON world_timeline(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_world_events_status ON world_events(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_world_events_type ON world_events(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_faction_changes_faction ON faction_changes(faction_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_evolution_npc ON npc_evolution(npc_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_treasures_location ON treasures(spawn_location)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_treasures_discovered ON treasures(is_discovered)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_participation_player ON player_world_participation(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_world_economy_date ON world_economy(year, month, day)
        """)

        conn.commit()

    def save_world_timeline_event(self, event_data: Dict[str, Any]) -> int:
        """
        保存世界时间线事件

        Args:
            event_data: 事件数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO world_timeline (
                event_id, event_type, title, description, year, month, day,
                location, importance, is_historic, involved_npcs, involved_factions,
                event_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_data.get('event_id', str(uuid.uuid4())),
            event_data.get('event_type', 'general'),
            event_data.get('title', ''),
            event_data.get('description', ''),
            event_data.get('year', 1),
            event_data.get('month', 1),
            event_data.get('day', 1),
            event_data.get('location', ''),
            event_data.get('importance', 5),
            1 if event_data.get('is_historic', False) else 0,
            json.dumps(event_data.get('involved_npcs', []), ensure_ascii=False),
            json.dumps(event_data.get('involved_factions', []), ensure_ascii=False),
            json.dumps(event_data.get('event_data', {}), ensure_ascii=False),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_world_timeline(self, year: int = None, event_type: str = None,
                          is_historic: bool = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取世界时间线事件

        Args:
            year: 筛选年份
            event_type: 事件类型
            is_historic: 是否历史事件
            limit: 返回数量限制

        Returns:
            事件列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if year is not None:
            conditions.append("year = ?")
            params.append(year)

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)

        if is_historic is not None:
            conditions.append("is_historic = ?")
            params.append(1 if is_historic else 0)

        query = "SELECT * FROM world_timeline"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY year DESC, month DESC, day DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'event_id': row['event_id'],
                'event_type': row['event_type'],
                'title': row['title'],
                'description': row['description'],
                'year': row['year'],
                'month': row['month'],
                'day': row['day'],
                'location': row['location'],
                'importance': row['importance'],
                'is_historic': bool(row['is_historic']),
                'involved_npcs': json.loads(row['involved_npcs']) if row['involved_npcs'] else [],
                'involved_factions': json.loads(row['involved_factions']) if row['involved_factions'] else [],
                'event_data': json.loads(row['event_data']) if row['event_data'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def save_world_event(self, event_data: Dict[str, Any]) -> int:
        """
        保存世界事件

        Args:
            event_data: 事件数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO world_events (
                event_id, event_type, title, description, status,
                start_year, start_month, start_day, end_year, end_month, end_day,
                location, scope, importance, involved_npcs, involved_factions,
                event_data, player_participated, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_data.get('event_id', str(uuid.uuid4())),
            event_data.get('event_type', 'general'),
            event_data.get('title', ''),
            event_data.get('description', ''),
            event_data.get('status', 'active'),
            event_data.get('start_year', 1),
            event_data.get('start_month', 1),
            event_data.get('start_day', 1),
            event_data.get('end_year'),
            event_data.get('end_month'),
            event_data.get('end_day'),
            event_data.get('location', ''),
            event_data.get('scope', 'local'),
            event_data.get('importance', 5),
            json.dumps(event_data.get('involved_npcs', []), ensure_ascii=False),
            json.dumps(event_data.get('involved_factions', []), ensure_ascii=False),
            json.dumps(event_data.get('event_data', {}), ensure_ascii=False),
            1 if event_data.get('player_participated', False) else 0,
            now,
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_active_world_events(self, scope: str = None, location: str = None) -> List[Dict[str, Any]]:
        """
        获取活跃的世界事件

        Args:
            scope: 事件范围筛选
            location: 地点筛选

        Returns:
            活跃事件列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = ["status = 'active'"]
        params = []

        if scope:
            conditions.append("scope = ?")
            params.append(scope)

        if location:
            conditions.append("location = ?")
            params.append(location)

        query = "SELECT * FROM world_events WHERE " + " AND ".join(conditions)
        query += " ORDER BY importance DESC, created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'event_id': row['event_id'],
                'event_type': row['event_type'],
                'title': row['title'],
                'description': row['description'],
                'status': row['status'],
                'start_year': row['start_year'],
                'start_month': row['start_month'],
                'start_day': row['start_day'],
                'end_year': row['end_year'],
                'end_month': row['end_month'],
                'end_day': row['end_day'],
                'location': row['location'],
                'scope': row['scope'],
                'importance': row['importance'],
                'involved_npcs': json.loads(row['involved_npcs']) if row['involved_npcs'] else [],
                'involved_factions': json.loads(row['involved_factions']) if row['involved_factions'] else [],
                'event_data': json.loads(row['event_data']) if row['event_data'] else {},
                'player_participated': bool(row['player_participated']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            for row in rows
        ]

    def update_world_event_status(self, event_id: str, status: str,
                                  end_year: int = None, end_month: int = None,
                                  end_day: int = None) -> bool:
        """
        更新世界事件状态

        Args:
            event_id: 事件ID
            status: 新状态
            end_year: 结束年份
            end_month: 结束月份
            end_day: 结束日期

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE world_events
                SET status = ?, end_year = ?, end_month = ?, end_day = ?, updated_at = ?
                WHERE event_id = ?
            """, (status, end_year, end_month, end_day, now, event_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新世界事件状态失败: {e}")
            return False

    def save_faction_change(self, change_data: Dict[str, Any]) -> int:
        """
        保存势力变迁记录

        Args:
            change_data: 变迁数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO faction_changes (
                faction_id, faction_name, change_type, change_description,
                year, month, day, old_value, new_value, related_npc, related_event, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            change_data.get('faction_id', ''),
            change_data.get('faction_name', ''),
            change_data.get('change_type', ''),
            change_data.get('change_description', ''),
            change_data.get('year', 1),
            change_data.get('month', 1),
            change_data.get('day', 1),
            json.dumps(change_data.get('old_value'), ensure_ascii=False),
            json.dumps(change_data.get('new_value'), ensure_ascii=False),
            change_data.get('related_npc', ''),
            change_data.get('related_event', ''),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_faction_changes(self, faction_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取势力变迁记录

        Args:
            faction_id: 势力ID筛选
            limit: 返回数量限制

        Returns:
            变迁记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if faction_id:
            cursor.execute("""
                SELECT * FROM faction_changes
                WHERE faction_id = ?
                ORDER BY year DESC, month DESC, day DESC
                LIMIT ?
            """, (faction_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM faction_changes
                ORDER BY year DESC, month DESC, day DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'faction_id': row['faction_id'],
                'faction_name': row['faction_name'],
                'change_type': row['change_type'],
                'change_description': row['change_description'],
                'year': row['year'],
                'month': row['month'],
                'day': row['day'],
                'old_value': json.loads(row['old_value']) if row['old_value'] else None,
                'new_value': json.loads(row['new_value']) if row['new_value'] else None,
                'related_npc': row['related_npc'],
                'related_event': row['related_event'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def save_npc_evolution(self, evolution_data: Dict[str, Any]) -> int:
        """
        保存NPC演化记录

        Args:
            evolution_data: 演化数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO npc_evolution (
                npc_id, npc_name, evolution_type, year, month, day,
                old_realm, new_realm, old_location, new_location,
                action_taken, action_result, related_event, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evolution_data.get('npc_id', ''),
            evolution_data.get('npc_name', ''),
            evolution_data.get('evolution_type', ''),
            evolution_data.get('year', 1),
            evolution_data.get('month', 1),
            evolution_data.get('day', 1),
            evolution_data.get('old_realm'),
            evolution_data.get('new_realm'),
            evolution_data.get('old_location', ''),
            evolution_data.get('new_location', ''),
            evolution_data.get('action_taken', ''),
            evolution_data.get('action_result', ''),
            evolution_data.get('related_event', ''),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_npc_evolution_history(self, npc_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取NPC演化历史

        Args:
            npc_id: NPC ID
            limit: 返回数量限制

        Returns:
            演化记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM npc_evolution
            WHERE npc_id = ?
            ORDER BY year DESC, month DESC, day DESC
            LIMIT ?
        """, (npc_id, limit))

        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'npc_id': row['npc_id'],
                'npc_name': row['npc_name'],
                'evolution_type': row['evolution_type'],
                'year': row['year'],
                'month': row['month'],
                'day': row['day'],
                'old_realm': row['old_realm'],
                'new_realm': row['new_realm'],
                'old_location': row['old_location'],
                'new_location': row['new_location'],
                'action_taken': row['action_taken'],
                'action_result': row['action_result'],
                'related_event': row['related_event'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def save_treasure(self, treasure_data: Dict[str, Any]) -> str:
        """
        保存天材地宝

        Args:
            treasure_data: 宝物数据字典

        Returns:
            宝物ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        treasure_id = treasure_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO treasures (
                id, name, treasure_type, rarity, description, effects,
                spawn_location, spawn_year, spawn_month, spawn_day,
                discoverer_id, discoverer_name, is_discovered, is_claimed,
                guardian_monster, guardian_level, expire_year, expire_month, expire_day, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            treasure_id,
            treasure_data.get('name', ''),
            treasure_data.get('treasure_type', ''),
            treasure_data.get('rarity', 'common'),
            treasure_data.get('description', ''),
            json.dumps(treasure_data.get('effects', {}), ensure_ascii=False),
            treasure_data.get('spawn_location', ''),
            treasure_data.get('spawn_year', 1),
            treasure_data.get('spawn_month', 1),
            treasure_data.get('spawn_day', 1),
            treasure_data.get('discoverer_id', ''),
            treasure_data.get('discoverer_name', ''),
            1 if treasure_data.get('is_discovered', False) else 0,
            1 if treasure_data.get('is_claimed', False) else 0,
            treasure_data.get('guardian_monster', ''),
            treasure_data.get('guardian_level', 1),
            treasure_data.get('expire_year'),
            treasure_data.get('expire_month'),
            treasure_data.get('expire_day'),
            now
        ))

        conn.commit()
        return treasure_id

    def get_active_treasures(self, location: str = None) -> List[Dict[str, Any]]:
        """
        获取活跃的天材地宝（未被发现或未过期的）

        Args:
            location: 地点筛选

        Returns:
            宝物列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = ["is_claimed = 0"]
        params = []

        if location:
            conditions.append("spawn_location = ?")
            params.append(location)

        query = "SELECT * FROM treasures WHERE " + " AND ".join(conditions)
        query += " ORDER BY rarity DESC, spawn_year DESC, spawn_month DESC, spawn_day DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'name': row['name'],
                'treasure_type': row['treasure_type'],
                'rarity': row['rarity'],
                'description': row['description'],
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'spawn_location': row['spawn_location'],
                'spawn_year': row['spawn_year'],
                'spawn_month': row['spawn_month'],
                'spawn_day': row['spawn_day'],
                'discoverer_id': row['discoverer_id'],
                'discoverer_name': row['discoverer_name'],
                'is_discovered': bool(row['is_discovered']),
                'is_claimed': bool(row['is_claimed']),
                'guardian_monster': row['guardian_monster'],
                'guardian_level': row['guardian_level'],
                'expire_year': row['expire_year'],
                'expire_month': row['expire_month'],
                'expire_day': row['expire_day'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def claim_treasure(self, treasure_id: str, player_id: str, player_name: str) -> bool:
        """
        玩家获取天材地宝

        Args:
            treasure_id: 宝物ID
            player_id: 玩家ID
            player_name: 玩家名称

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE treasures
                SET is_claimed = 1, discoverer_id = ?, discoverer_name = ?, is_discovered = 1
                WHERE id = ? AND is_claimed = 0
            """, (player_id, player_name, treasure_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"获取天材地宝失败: {e}")
            return False

    def record_player_participation(self, participation_data: Dict[str, Any]) -> int:
        """
        记录玩家参与世界事件

        Args:
            participation_data: 参与数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO player_world_participation (
                player_id, event_id, participation_type, participation_description,
                year, month, day, contribution_score, rewards_received, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            participation_data.get('player_id', ''),
            participation_data.get('event_id', ''),
            participation_data.get('participation_type', ''),
            participation_data.get('participation_description', ''),
            participation_data.get('year', 1),
            participation_data.get('month', 1),
            participation_data.get('day', 1),
            participation_data.get('contribution_score', 0),
            json.dumps(participation_data.get('rewards_received', {}), ensure_ascii=False),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_player_participation_history(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取玩家参与世界事件的历史

        Args:
            player_id: 玩家ID
            limit: 返回数量限制

        Returns:
            参与记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM player_world_participation
            WHERE player_id = ?
            ORDER BY year DESC, month DESC, day DESC
            LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'event_id': row['event_id'],
                'participation_type': row['participation_type'],
                'participation_description': row['participation_description'],
                'year': row['year'],
                'month': row['month'],
                'day': row['day'],
                'contribution_score': row['contribution_score'],
                'rewards_received': json.loads(row['rewards_received']) if row['rewards_received'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def save_economy_record(self, economy_data: Dict[str, Any]) -> int:
        """
        保存世界经济记录

        Args:
            economy_data: 经济数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO world_economy (
                year, month, day, resource_type, price, supply_level, demand_level, location, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            economy_data.get('year', 1),
            economy_data.get('month', 1),
            economy_data.get('day', 1),
            economy_data.get('resource_type', ''),
            economy_data.get('price', 0.0),
            economy_data.get('supply_level', 50),
            economy_data.get('demand_level', 50),
            economy_data.get('location', ''),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_economy_history(self, resource_type: str = None, location: str = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取经济历史记录

        Args:
            resource_type: 资源类型筛选
            location: 地点筛选
            limit: 返回数量限制

        Returns:
            经济记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)

        if location:
            conditions.append("location = ?")
            params.append(location)

        query = "SELECT * FROM world_economy"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY year DESC, month DESC, day DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'year': row['year'],
                'month': row['month'],
                'day': row['day'],
                'resource_type': row['resource_type'],
                'price': row['price'],
                'supply_level': row['supply_level'],
                'demand_level': row['demand_level'],
                'location': row['location'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_generated_monsters_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        获取某地图的妖兽

        Args:
            location: 地图名称或ID

        Returns:
            妖兽数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM generated_monsters WHERE location = ? ORDER BY level DESC
        """, (location,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'monster_type': row['monster_type'],
                'level': row['level'],
                'realm_level': row['realm_level'],
                'attributes': json.loads(row['attributes']) if row['attributes'] else {},
                'drops': json.loads(row['drops']) if row['drops'] else [],
                'description': row['description'],
                'habits': row['habits'],
                'weakness': row['weakness'],
                'location': row['location'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_all_generated_maps(self) -> List[Dict[str, Any]]:
        """
        获取所有生成的地图

        Returns:
            地图数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM generated_maps ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'map_type': row['map_type'],
                'level': row['level'],
                'size': row['size'],
                'description': row['description'],
                'history': row['history'],
                'environment': row['environment'],
                'connections': json.loads(row['connections']) if row['connections'] else [],
                'npcs': json.loads(row['npcs']) if row['npcs'] else [],
                'monsters': json.loads(row['monsters']) if row['monsters'] else [],
                'items': json.loads(row['items']) if row['items'] else [],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_generated_maps_by_level(self, level: int) -> List[Dict[str, Any]]:
        """
        获取某等级的地图

        Args:
            level: 地图等级

        Returns:
            地图数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM generated_maps WHERE level = ? ORDER BY created_at DESC
        """, (level,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'map_type': row['map_type'],
                'level': row['level'],
                'size': row['size'],
                'description': row['description'],
                'history': row['history'],
                'environment': row['environment'],
                'connections': json.loads(row['connections']) if row['connections'] else [],
                'npcs': json.loads(row['npcs']) if row['npcs'] else [],
                'monsters': json.loads(row['monsters']) if row['monsters'] else [],
                'items': json.loads(row['items']) if row['items'] else [],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    # ==================== 材料系统操作 ====================

    def save_material(self, material_data: dict, owner_id: str) -> bool:
        """
        保存材料到数据库

        Args:
            material_data: 材料数据字典，包含 name, description, material_type, rarity 等字段
            owner_id: 玩家ID（材料所有者）

        Returns:
            是否保存成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            material_id = material_data.get('id', str(uuid.uuid4()))
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO materials (
                    id, name, description, material_type, rarity, level,
                    effects, value, source, created_at, owner_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material_id,
                material_data.get('name', ''),
                material_data.get('description', ''),
                material_data.get('material_type', ''),
                material_data.get('rarity', 'common'),
                material_data.get('level', 1),
                json.dumps(material_data.get('effects', {}), ensure_ascii=False),
                material_data.get('value', 0),
                material_data.get('source', ''),
                now,
                owner_id
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存材料失败: {e}")
            return False

    def load_materials(self, owner_id: str) -> list:
        """
        加载指定玩家的所有材料

        Args:
            owner_id: 玩家ID

        Returns:
            材料数据字典列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM materials WHERE owner_id = ? ORDER BY created_at DESC
            """, (owner_id,))

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'material_type': row['material_type'],
                    'rarity': row['rarity'],
                    'level': row['level'],
                    'effects': json.loads(row['effects']) if row['effects'] else {},
                    'value': row['value'],
                    'source': row['source'],
                    'created_at': row['created_at'],
                    'owner_id': row['owner_id']
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"加载材料失败: {e}")
            return []

    def delete_material(self, material_id: str) -> bool:
        """
        删除指定材料

        Args:
            material_id: 材料ID

        Returns:
            是否删除成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
            conn.commit()

            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除材料失败: {e}")
            return False

    # ==================== 死亡记录系统操作 ====================

    def save_death_record(self, record: dict) -> bool:
        """
        保存NPC死亡记录

        Args:
            record: 死亡记录字典，包含 npc_id, npc_name, killer_name, death_reason 等字段

        Returns:
            是否保存成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO death_records (
                    npc_id, npc_name, killer_name, death_reason, location,
                    death_time, can_resurrect
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get('npc_id', ''),
                record.get('npc_name', ''),
                record.get('killer_name', ''),
                record.get('death_reason', ''),
                record.get('location', ''),
                now,
                1 if record.get('can_resurrect', True) else 0
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存死亡记录失败: {e}")
            return False

    def load_death_records(self) -> list:
        """
        加载所有死亡记录

        Returns:
            死亡记录字典列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM death_records ORDER BY death_time DESC
            """)

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'npc_id': row['npc_id'],
                    'npc_name': row['npc_name'],
                    'killer_name': row['killer_name'],
                    'death_reason': row['death_reason'],
                    'location': row['location'],
                    'death_time': row['death_time'],
                    'can_resurrect': bool(row['can_resurrect'])
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"加载死亡记录失败: {e}")
            return []

    def update_npc_death_status(self, npc_id: str, is_alive: bool, death_info: dict) -> bool:
        """
        更新NPC的死亡状态

        Args:
            npc_id: NPC的ID
            is_alive: 是否存活
            death_info: 死亡信息字典，包含 death_time, killer, reason 等

        Returns:
            是否更新成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE generated_npcs
                SET is_alive = ?, death_info = ?
                WHERE id = ?
            """, (
                1 if is_alive else 0,
                json.dumps(death_info, ensure_ascii=False),
                npc_id
            ))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新NPC死亡状态失败: {e}")
            return False

    def load_alive_npcs(self) -> list:
        """
        加载所有存活的NPC

        Returns:
            存活NPC数据字典列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM generated_npcs 
                WHERE is_alive = 1 OR is_alive IS NULL
                ORDER BY created_at DESC
            """)

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'surname': row['surname'],
                    'full_name': row['full_name'],
                    'gender': row['gender'],
                    'age': row['age'],
                    'realm_level': row['realm_level'],
                    'occupation': row['occupation'],
                    'personality': row['personality'],
                    'appearance': row['appearance'],
                    'catchphrase': row['catchphrase'],
                    'story': row['story'],
                    'location': row['location'],
                    'favor': row['favor'],
                    'is_alive': row['is_alive'] if row['is_alive'] is not None else 1,
                    'death_info': json.loads(row['death_info']) if row['death_info'] else None,
                    'can_resurrect': row['can_resurrect'] if row['can_resurrect'] is not None else 1,
                    'morality': row['morality'] if row['morality'] is not None else 0,
                    'created_at': row['created_at']
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"加载存活NPC失败: {e}")
            return []

    # ==================== 功法系统操作 ====================

    def save_generated_technique(self, technique_data: Dict[str, Any], discovered_by: str = None) -> str:
        """
        保存生成的功法

        Args:
            technique_data: 功法数据字典
            discovered_by: 发现者ID（玩家名称）

        Returns:
            功法ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        technique_id = technique_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO generated_techniques (
                id, name, technique_type, rarity, realm_required,
                description, effects, cultivation_method, origin,
                created_at, discovered_by, is_learned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            technique_id,
            technique_data.get('name', ''),
            technique_data.get('technique_type', ''),
            technique_data.get('rarity', ''),
            technique_data.get('realm_required', 0),
            technique_data.get('description', ''),
            json.dumps(technique_data.get('effects', {}), ensure_ascii=False),
            technique_data.get('cultivation_method', ''),
            technique_data.get('origin', ''),
            now,
            discovered_by,
            0  # 默认未学习
        ))

        conn.commit()
        return technique_id

    def get_generated_techniques(self, discovered_by: str = None, is_learned: bool = None) -> List[Dict[str, Any]]:
        """
        获取生成的功法列表

        Args:
            discovered_by: 发现者ID，如果为None则获取所有
            is_learned: 是否已学习，如果为None则不筛选

        Returns:
            功法数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if discovered_by:
            conditions.append("discovered_by = ?")
            params.append(discovered_by)

        if is_learned is not None:
            conditions.append("is_learned = ?")
            params.append(1 if is_learned else 0)

        query = "SELECT * FROM generated_techniques"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'name': row['name'],
                'technique_type': row['technique_type'],
                'rarity': row['rarity'],
                'realm_required': row['realm_required'],
                'description': row['description'],
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'cultivation_method': row['cultivation_method'],
                'origin': row['origin'],
                'created_at': row['created_at'],
                'discovered_by': row['discovered_by'],
                'is_learned': bool(row['is_learned'])
            }
            for row in rows
        ]

    def get_technique_by_id(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取功法

        Args:
            technique_id: 功法ID

        Returns:
            功法数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM generated_techniques WHERE id = ?", (technique_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'technique_type': row['technique_type'],
            'rarity': row['rarity'],
            'realm_required': row['realm_required'],
            'description': row['description'],
            'effects': json.loads(row['effects']) if row['effects'] else {},
            'cultivation_method': row['cultivation_method'],
            'origin': row['origin'],
            'created_at': row['created_at'],
            'discovered_by': row['discovered_by'],
            'is_learned': bool(row['is_learned'])
        }

    def learn_technique(self, technique_id: str) -> bool:
        """
        标记功法为已学习

        Args:
            technique_id: 功法ID

        Returns:
            是否更新成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE generated_techniques SET is_learned = 1 WHERE id = ?
            """, (technique_id,))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"学习功法失败: {e}")
            return False

    # ==================== 门派系统操作 ====================

    def init_sect_tables(self):
        """创建门派系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 sects 表 - 门派信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                sect_type TEXT NOT NULL DEFAULT '正道',
                location TEXT,
                founder TEXT,
                established_date TEXT,
                total_members INTEGER DEFAULT 0,
                sect_level INTEGER DEFAULT 1,
                reputation INTEGER DEFAULT 0,
                resources INTEGER DEFAULT 0,
                main_element TEXT,
                sect_leader TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 sect_members 表 - 门派成员
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sect_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                position TEXT NOT NULL DEFAULT '外门弟子',
                contribution INTEGER DEFAULT 0,
                joined_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (sect_id) REFERENCES sects(id)
            )
        """)

        # 创建 sect_contributions 表 - 贡献记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sect_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                contribution_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (sect_id) REFERENCES sects(id)
            )
        """)

        # 创建 sect_tasks 表 - 门派任务
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_tasks (
                id TEXT PRIMARY KEY,
                sect_id TEXT NOT NULL,
                task_name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                description TEXT,
                difficulty INTEGER DEFAULT 1,
                contribution_reward INTEGER DEFAULT 0,
                spirit_stone_reward INTEGER DEFAULT 0,
                item_reward TEXT,
                required_realm INTEGER DEFAULT 0,
                required_position TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                FOREIGN KEY (sect_id) REFERENCES sects(id)
            )
        """)

        # 创建 sect_task_records 表 - 任务完成记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_task_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'accepted',
                completed_at TEXT,
                FOREIGN KEY (task_id) REFERENCES sect_tasks(id)
            )
        """)

        # 创建 sect_techniques 表 - 门派专属功法
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_techniques (
                id TEXT PRIMARY KEY,
                sect_id TEXT NOT NULL,
                technique_name TEXT NOT NULL,
                description TEXT,
                technique_type TEXT,
                required_position TEXT,
                required_contribution INTEGER DEFAULT 0,
                required_realm INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (sect_id) REFERENCES sects(id)
            )
        """)

        # 创建 sect_wars 表 - 门派战争
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_wars (
                id TEXT PRIMARY KEY,
                attacker_sect_id TEXT NOT NULL,
                defender_sect_id TEXT NOT NULL,
                war_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ongoing',
                start_time TEXT NOT NULL,
                end_time TEXT,
                winner_sect_id TEXT,
                war_score_attacker INTEGER DEFAULT 0,
                war_score_defender INTEGER DEFAULT 0,
                description TEXT,
                FOREIGN KEY (attacker_sect_id) REFERENCES sects(id),
                FOREIGN KEY (defender_sect_id) REFERENCES sects(id)
            )
        """)

        # 创建 sect_war_participants 表 - 战争参与者
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sect_war_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                war_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                sect_id TEXT NOT NULL,
                contribution_score INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                joined_at TEXT NOT NULL,
                FOREIGN KEY (war_id) REFERENCES sect_wars(id),
                FOREIGN KEY (sect_id) REFERENCES sects(id)
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_members_sect ON sect_members(sect_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_members_player ON sect_members(player_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_contributions_sect ON sect_contributions(sect_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_tasks_sect ON sect_tasks(sect_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_techniques_sect ON sect_techniques(sect_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_wars_attacker ON sect_wars(attacker_sect_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sect_wars_defender ON sect_wars(defender_sect_id)
        """)

        conn.commit()

    def save_sect(self, sect_data: Dict[str, Any]) -> str:
        """
        保存门派信息

        Args:
            sect_data: 门派数据字典

        Returns:
            门派ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        sect_id = sect_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO sects (
                id, name, description, sect_type, location, founder,
                established_date, total_members, sect_level, reputation,
                resources, main_element, sect_leader, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sect_id,
            sect_data.get('name', ''),
            sect_data.get('description', ''),
            sect_data.get('sect_type', '正道'),
            sect_data.get('location', ''),
            sect_data.get('founder', ''),
            sect_data.get('established_date', ''),
            sect_data.get('total_members', 0),
            sect_data.get('sect_level', 1),
            sect_data.get('reputation', 0),
            sect_data.get('resources', 0),
            sect_data.get('main_element', ''),
            sect_data.get('sect_leader', ''),
            now
        ))

        conn.commit()
        return sect_id

    def get_sect(self, sect_id: str) -> Optional[Dict[str, Any]]:
        """
        获取门派信息

        Args:
            sect_id: 门派ID

        Returns:
            门派数据字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sects WHERE id = ?", (sect_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'sect_type': row['sect_type'],
            'location': row['location'],
            'founder': row['founder'],
            'established_date': row['established_date'],
            'total_members': row['total_members'],
            'sect_level': row['sect_level'],
            'reputation': row['reputation'],
            'resources': row['resources'],
            'main_element': row['main_element'],
            'sect_leader': row['sect_leader'],
            'created_at': row['created_at']
        }

    def get_all_sects(self) -> List[Dict[str, Any]]:
        """
        获取所有门派

        Returns:
            门派数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sects ORDER BY reputation DESC")
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'sect_type': row['sect_type'],
                'location': row['location'],
                'founder': row['founder'],
                'established_date': row['established_date'],
                'total_members': row['total_members'],
                'sect_level': row['sect_level'],
                'reputation': row['reputation'],
                'resources': row['resources'],
                'main_element': row['main_element'],
                'sect_leader': row['sect_leader'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def join_sect(self, sect_id: str, player_name: str, position: str = '外门弟子') -> bool:
        """
        加入门派

        Args:
            sect_id: 门派ID
            player_name: 玩家名称
            position: 初始职位

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 检查是否已在其他门派
            cursor.execute(
                "SELECT id FROM sect_members WHERE player_name = ? AND is_active = 1",
                (player_name,)
            )
            if cursor.fetchone():
                return False

            cursor.execute("""
                INSERT INTO sect_members (
                    sect_id, player_name, position, contribution, joined_at, last_active, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sect_id, player_name, position, 0, now, now, 1))

            # 更新门派成员数
            cursor.execute("""
                UPDATE sects SET total_members = total_members + 1 WHERE id = ?
            """, (sect_id,))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"加入门派失败: {e}")
            return False

    def leave_sect(self, player_name: str) -> bool:
        """
        离开门派

        Args:
            player_name: 玩家名称

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取当前门派
            cursor.execute(
                "SELECT sect_id FROM sect_members WHERE player_name = ? AND is_active = 1",
                (player_name,)
            )
            row = cursor.fetchone()
            if not row:
                return False

            sect_id = row['sect_id']

            # 标记为离开
            cursor.execute("""
                UPDATE sect_members SET is_active = 0 WHERE player_name = ? AND sect_id = ?
            """, (player_name, sect_id))

            # 更新门派成员数
            cursor.execute("""
                UPDATE sects SET total_members = total_members - 1 WHERE id = ?
            """, (sect_id,))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"离开门派失败: {e}")
            return False

    def get_player_sect(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家所属门派

        Args:
            player_name: 玩家名称

        Returns:
            门派成员信息
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sm.*, s.name as sect_name, s.description as sect_description,
                   s.sect_type, s.location, s.reputation, s.main_element
            FROM sect_members sm
            JOIN sects s ON sm.sect_id = s.id
            WHERE sm.player_name = ? AND sm.is_active = 1
        """, (player_name,))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'sect_id': row['sect_id'],
            'sect_name': row['sect_name'],
            'sect_description': row['sect_description'],
            'sect_type': row['sect_type'],
            'location': row['location'],
            'reputation': row['reputation'],
            'main_element': row['main_element'],
            'player_name': row['player_name'],
            'position': row['position'],
            'contribution': row['contribution'],
            'joined_at': row['joined_at'],
            'last_active': row['last_active']
        }

    def add_contribution(self, sect_id: str, player_name: str, amount: int,
                         contribution_type: str = '任务', description: str = '') -> bool:
        """
        添加贡献值

        Args:
            sect_id: 门派ID
            player_name: 玩家名称
            amount: 贡献值
            contribution_type: 贡献类型
            description: 描述

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 更新成员贡献
            cursor.execute("""
                UPDATE sect_members
                SET contribution = contribution + ?, last_active = ?
                WHERE sect_id = ? AND player_name = ? AND is_active = 1
            """, (amount, now, sect_id, player_name))

            # 记录贡献
            cursor.execute("""
                INSERT INTO sect_contributions
                (sect_id, player_name, contribution_type, amount, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sect_id, player_name, contribution_type, amount, description, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加贡献失败: {e}")
            return False

    def update_position(self, sect_id: str, player_name: str, new_position: str) -> bool:
        """
        更新职位

        Args:
            sect_id: 门派ID
            player_name: 玩家名称
            new_position: 新职位

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sect_members
                SET position = ?, last_active = ?
                WHERE sect_id = ? AND player_name = ? AND is_active = 1
            """, (new_position, datetime.now().isoformat(), sect_id, player_name))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新职位失败: {e}")
            return False

    def get_sect_members(self, sect_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取门派成员列表

        Args:
            sect_id: 门派ID
            limit: 限制数量

        Returns:
            成员列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM sect_members
            WHERE sect_id = ? AND is_active = 1
            ORDER BY contribution DESC
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (sect_id,))
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'player_name': row['player_name'],
                'position': row['position'],
                'contribution': row['contribution'],
                'joined_at': row['joined_at'],
                'last_active': row['last_active']
            }
            for row in rows
        ]

    def save_sect_task(self, task_data: Dict[str, Any]) -> str:
        """
        保存门派任务

        Args:
            task_data: 任务数据

        Returns:
            任务ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        task_id = task_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO sect_tasks (
                id, sect_id, task_name, task_type, description, difficulty,
                contribution_reward, spirit_stone_reward, item_reward,
                required_realm, required_position, is_active, created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            task_data.get('sect_id', ''),
            task_data.get('task_name', ''),
            task_data.get('task_type', ''),
            task_data.get('description', ''),
            task_data.get('difficulty', 1),
            task_data.get('contribution_reward', 0),
            task_data.get('spirit_stone_reward', 0),
            json.dumps(task_data.get('item_reward', []), ensure_ascii=False),
            task_data.get('required_realm', 0),
            task_data.get('required_position', ''),
            1 if task_data.get('is_active', True) else 0,
            now,
            task_data.get('expires_at', '')
        ))

        conn.commit()
        return task_id

    def get_sect_tasks(self, sect_id: str, player_position: str = None) -> List[Dict[str, Any]]:
        """
        获取门派任务

        Args:
            sect_id: 门派ID
            player_position: 玩家职位（用于筛选）

        Returns:
            任务列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM sect_tasks
            WHERE sect_id = ? AND is_active = 1
        """
        params = [sect_id]

        if player_position:
            query += " AND (required_position = '' OR required_position <= ?)"
            params.append(player_position)

        query += " ORDER BY difficulty ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'task_name': row['task_name'],
                'task_type': row['task_type'],
                'description': row['description'],
                'difficulty': row['difficulty'],
                'contribution_reward': row['contribution_reward'],
                'spirit_stone_reward': row['spirit_stone_reward'],
                'item_reward': json.loads(row['item_reward']) if row['item_reward'] else [],
                'required_realm': row['required_realm'],
                'required_position': row['required_position'],
                'created_at': row['created_at'],
                'expires_at': row['expires_at']
            }
            for row in rows
        ]

    def accept_sect_task(self, task_id: str, player_name: str) -> bool:
        """
        接受门派任务

        Args:
            task_id: 任务ID
            player_name: 玩家名称

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO sect_task_records (task_id, player_name, status, completed_at)
                VALUES (?, ?, 'accepted', ?)
            """, (task_id, player_name, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"接受任务失败: {e}")
            return False

    def complete_sect_task(self, task_id: str, player_name: str) -> bool:
        """
        完成任务

        Args:
            task_id: 任务ID
            player_name: 玩家名称

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE sect_task_records
                SET status = 'completed', completed_at = ?
                WHERE task_id = ? AND player_name = ? AND status = 'accepted'
            """, (now, task_id, player_name))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"完成任务失败: {e}")
            return False

    def save_sect_technique(self, technique_data: Dict[str, Any]) -> str:
        """
        保存门派专属功法

        Args:
            technique_data: 功法数据

        Returns:
            功法ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        tech_id = technique_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO sect_techniques (
                id, sect_id, technique_name, description, technique_type,
                required_position, required_contribution, required_realm, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tech_id,
            technique_data.get('sect_id', ''),
            technique_data.get('technique_name', ''),
            technique_data.get('description', ''),
            technique_data.get('technique_type', ''),
            technique_data.get('required_position', ''),
            technique_data.get('required_contribution', 0),
            technique_data.get('required_realm', 0),
            1 if technique_data.get('is_active', True) else 0,
            now
        ))

        conn.commit()
        return tech_id

    def get_sect_techniques(self, sect_id: str, player_position: str = None,
                           player_contribution: int = 0) -> List[Dict[str, Any]]:
        """
        获取门派专属功法

        Args:
            sect_id: 门派ID
            player_position: 玩家职位
            player_contribution: 玩家贡献值

        Returns:
            功法列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM sect_techniques
            WHERE sect_id = ? AND is_active = 1
        """
        params = [sect_id]

        cursor.execute(query, params)
        rows = cursor.fetchall()

        techniques = []
        for row in rows:
            tech = {
                'id': row['id'],
                'technique_name': row['technique_name'],
                'description': row['description'],
                'technique_type': row['technique_type'],
                'required_position': row['required_position'],
                'required_contribution': row['required_contribution'],
                'required_realm': row['required_realm'],
                'created_at': row['created_at']
            }

            # 检查是否可学习
            can_learn = True
            if player_position and row['required_position']:
                position_order = {'外门弟子': 0, '内门弟子': 1, '核心弟子': 2, '长老': 3, '掌门': 4}
                player_rank = position_order.get(player_position, 0)
                required_rank = position_order.get(row['required_position'], 0)
                if player_rank < required_rank:
                    can_learn = False

            if player_contribution < row['required_contribution']:
                can_learn = False

            tech['can_learn'] = can_learn
            techniques.append(tech)

        return techniques

    # ==================== 社交系统操作 ====================

    def init_social_tables(self):
        """创建社交系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 social_relations 表 - 社交关系（好友、仇敌）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                target_name TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                intimacy INTEGER DEFAULT 0,
                trust INTEGER DEFAULT 0,
                hatred INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                notes TEXT,
                UNIQUE(player_name, target_name, relation_type)
            )
        """)

        # 创建 marriage_records 表 - 道侣/婚姻记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marriage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_name TEXT NOT NULL,
                player2_name TEXT NOT NULL,
                marriage_type TEXT DEFAULT '道侣',
                marriage_date TEXT NOT NULL,
                intimacy INTEGER DEFAULT 100,
                dual_cultivation_count INTEGER DEFAULT 0,
                last_dual_cultivation TEXT,
                benefits TEXT,
                is_active INTEGER DEFAULT 1,
                divorced_at TEXT,
                divorce_reason TEXT
            )
        """)

        # 创建 master_apprentice 表 - 师徒关系
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_apprentice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_name TEXT NOT NULL,
                apprentice_name TEXT NOT NULL,
                relation_type TEXT DEFAULT '师徒',
                established_date TEXT NOT NULL,
                respect INTEGER DEFAULT 50,
                teaching_count INTEGER DEFAULT 0,
                last_teaching TEXT,
                techniques_taught TEXT,
                is_active INTEGER DEFAULT 1,
                ended_at TEXT,
                end_reason TEXT,
                UNIQUE(master_name, apprentice_name)
            )
        """)

        # 创建 dual_cultivation_records 表 - 双修记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dual_cultivation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_name TEXT NOT NULL,
                player2_name TEXT NOT NULL,
                cultivation_date TEXT NOT NULL,
                exp_gained INTEGER DEFAULT 0,
                intimacy_increase INTEGER DEFAULT 0,
                benefits TEXT,
                location TEXT
            )
        """)

        # 创建 revenge_records 表 - 复仇记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revenge_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                victim_name TEXT NOT NULL,
                enemy_name TEXT NOT NULL,
                conflict_reason TEXT,
                hatred_level INTEGER DEFAULT 50,
                created_at TEXT NOT NULL,
                revenge_target TEXT,
                is_completed INTEGER DEFAULT 0,
                completed_at TEXT,
                revenge_result TEXT
            )
        """)

        # 创建 social_interactions 表 - 社交互动记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initiator_name TEXT NOT NULL,
                target_name TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                interaction_date TEXT NOT NULL,
                description TEXT,
                intimacy_change INTEGER DEFAULT 0,
                trust_change INTEGER DEFAULT 0,
                hatred_change INTEGER DEFAULT 0,
                location TEXT
            )
        """)

        # 创建 npc_relations 表 - NPC之间的关系
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc1_id TEXT NOT NULL,
                npc2_id TEXT NOT NULL,
                relation_type TEXT NOT NULL DEFAULT 'acquaintance',
                relation_status TEXT DEFAULT 'active',
                affinity INTEGER DEFAULT 0,
                intimacy INTEGER DEFAULT 0,
                hatred INTEGER DEFAULT 0,
                history TEXT,
                last_interaction TEXT,
                established_date TEXT,
                ended_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(npc1_id, npc2_id)
            )
        """)

        # 创建 npc_relation_history 表 - NPC关系历史记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_relation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc1_id TEXT NOT NULL,
                npc2_id TEXT NOT NULL,
                event TEXT NOT NULL,
                delta_affinity INTEGER DEFAULT 0,
                delta_intimacy INTEGER DEFAULT 0,
                delta_hatred INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                reason TEXT
            )
        """)

        # 创建 npc_social_events 表 - NPC社交事件记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_social_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                npc1_id TEXT NOT NULL,
                npc2_id TEXT NOT NULL,
                event_date TEXT NOT NULL,
                description TEXT,
                location TEXT,
                result TEXT,
                is_public INTEGER DEFAULT 0
            )
        """)

        # 创建 npc_relationship_changes 表 - NPC关系数值变化历史
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npc_relationship_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc1_id TEXT NOT NULL,
                npc2_id TEXT NOT NULL,
                change_type TEXT NOT NULL,
                old_value INTEGER,
                new_value INTEGER,
                delta INTEGER,
                change_date TEXT NOT NULL,
                reason TEXT,
                trigger_event TEXT
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_social_relations_player ON social_relations(player_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_social_relations_target ON social_relations(target_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_social_relations_type ON social_relations(relation_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_marriage_player1 ON marriage_records(player1_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_marriage_player2 ON marriage_records(player2_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_marriage_active ON marriage_records(is_active)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_master_apprentice_master ON master_apprentice(master_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_master_apprentice_apprentice ON master_apprentice(apprentice_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_revenge_victim ON revenge_records(victim_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_revenge_enemy ON revenge_records(enemy_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_initiator ON social_interactions(initiator_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_target ON social_interactions(target_name)
        """)

        # NPC关系表索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relations_npc1 ON npc_relations(npc1_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relations_npc2 ON npc_relations(npc2_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relations_type ON npc_relations(relation_type)
        """)

        # 检查并添加缺失的列（表迁移）
        try:
            cursor.execute("SELECT relation_status FROM npc_relations LIMIT 1")
        except sqlite3.OperationalError:
            # 列不存在，添加新列
            cursor.execute("ALTER TABLE npc_relations ADD COLUMN relation_status TEXT DEFAULT 'active'")
            cursor.execute("ALTER TABLE npc_relations ADD COLUMN established_date TEXT")
            cursor.execute("ALTER TABLE npc_relations ADD COLUMN ended_date TEXT")

        # 创建新列的索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relations_status ON npc_relations(relation_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relation_history_npc1 ON npc_relation_history(npc1_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_relation_history_npc2 ON npc_relation_history(npc2_id)
        """)

        # NPC社交事件表索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_social_events_npc1 ON npc_social_events(npc1_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_social_events_npc2 ON npc_social_events(npc2_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_social_events_type ON npc_social_events(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_social_events_date ON npc_social_events(event_date)
        """)

        # NPC关系变化表索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_rel_changes_npc1 ON npc_relationship_changes(npc1_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_rel_changes_npc2 ON npc_relationship_changes(npc2_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_rel_changes_type ON npc_relationship_changes(change_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_npc_rel_changes_date ON npc_relationship_changes(change_date)
        """)

        conn.commit()

    def add_social_relation(self, player_name: str, target_name: str,
                           relation_type: str, intimacy: int = 0,
                           trust: int = 0, hatred: int = 0, notes: str = '') -> bool:
        """
        添加社交关系

        Args:
            player_name: 玩家名称
            target_name: 目标名称
            relation_type: 关系类型（好友/仇敌/熟人）
            intimacy: 亲密度
            trust: 信任度
            hatred: 仇恨度
            notes: 备注

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO social_relations
                (player_name, target_name, relation_type, intimacy, trust, hatred, created_at, updated_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (player_name, target_name, relation_type, intimacy, trust, hatred, now, now, notes))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加社交关系失败: {e}")
            return False

    def get_social_relations(self, player_name: str, relation_type: str = None) -> List[Dict[str, Any]]:
        """
        获取社交关系列表

        Args:
            player_name: 玩家名称
            relation_type: 关系类型筛选

        Returns:
            关系列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM social_relations
            WHERE player_name = ?
        """
        params = [player_name]

        if relation_type:
            query += " AND relation_type = ?"
            params.append(relation_type)

        query += " ORDER BY intimacy DESC, trust DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'player_name': row['player_name'],
                'target_name': row['target_name'],
                'relation_type': row['relation_type'],
                'intimacy': row['intimacy'],
                'trust': row['trust'],
                'hatred': row['hatred'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'notes': row['notes']
            }
            for row in rows
        ]

    def update_social_relation(self, player_name: str, target_name: str,
                               intimacy_delta: int = 0, trust_delta: int = 0,
                               hatred_delta: int = 0, notes: str = None) -> bool:
        """
        更新社交关系

        Args:
            player_name: 玩家名称
            target_name: 目标名称
            intimacy_delta: 亲密度变化
            trust_delta: 信任度变化
            hatred_delta: 仇恨度变化
            notes: 备注（可选）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 获取当前值
            cursor.execute("""
                SELECT intimacy, trust, hatred FROM social_relations
                WHERE player_name = ? AND target_name = ?
            """, (player_name, target_name))
            row = cursor.fetchone()

            if row:
                new_intimacy = max(0, min(100, row['intimacy'] + intimacy_delta))
                new_trust = max(0, min(100, row['trust'] + trust_delta))
                new_hatred = max(0, min(100, row['hatred'] + hatred_delta))

                if notes:
                    cursor.execute("""
                        UPDATE social_relations
                        SET intimacy = ?, trust = ?, hatred = ?, updated_at = ?, notes = ?
                        WHERE player_name = ? AND target_name = ?
                    """, (new_intimacy, new_trust, new_hatred, now, notes, player_name, target_name))
                else:
                    cursor.execute("""
                        UPDATE social_relations
                        SET intimacy = ?, trust = ?, hatred = ?, updated_at = ?
                        WHERE player_name = ? AND target_name = ?
                    """, (new_intimacy, new_trust, new_hatred, now, player_name, target_name))

                conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"更新社交关系失败: {e}")
            return False

    def remove_social_relation(self, player_name: str, target_name: str,
                               relation_type: str = None) -> bool:
        """
        移除社交关系

        Args:
            player_name: 玩家名称
            target_name: 目标名称
            relation_type: 关系类型（可选）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if relation_type:
                cursor.execute("""
                    DELETE FROM social_relations
                    WHERE player_name = ? AND target_name = ? AND relation_type = ?
                """, (player_name, target_name, relation_type))
            else:
                cursor.execute("""
                    DELETE FROM social_relations
                    WHERE player_name = ? AND target_name = ?
                """, (player_name, target_name))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"移除社交关系失败: {e}")
            return False

    def create_marriage(self, player1_name: str, player2_name: str,
                       marriage_type: str = '道侣') -> bool:
        """
        创建道侣关系

        Args:
            player1_name: 玩家1名称
            player2_name: 玩家2名称
            marriage_type: 关系类型（道侣/夫妻）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO marriage_records
                (player1_name, player2_name, marriage_type, marriage_date, intimacy, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (player1_name, player2_name, marriage_type, now, 100, 1))

            # 同时添加双向好友关系
            self.add_social_relation(player1_name, player2_name, '道侣', 100, 100, 0)
            self.add_social_relation(player2_name, player1_name, '道侣', 100, 100, 0)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建道侣关系失败: {e}")
            return False

    def get_marriage(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家的道侣关系

        Args:
            player_name: 玩家名称

        Returns:
            道侣关系信息
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM marriage_records
            WHERE (player1_name = ? OR player2_name = ?) AND is_active = 1
        """, (player_name, player_name))

        row = cursor.fetchone()
        if row is None:
            return None

        partner_name = row['player2_name'] if row['player1_name'] == player_name else row['player1_name']

        return {
            'id': row['id'],
            'partner_name': partner_name,
            'marriage_type': row['marriage_type'],
            'marriage_date': row['marriage_date'],
            'intimacy': row['intimacy'],
            'dual_cultivation_count': row['dual_cultivation_count'],
            'last_dual_cultivation': row['last_dual_cultivation'],
            'benefits': json.loads(row['benefits']) if row['benefits'] else {}
        }

    def record_dual_cultivation(self, player1_name: str, player2_name: str,
                                exp_gained: int, intimacy_increase: int,
                                benefits: Dict[str, Any], location: str = '') -> bool:
        """
        记录双修

        Args:
            player1_name: 玩家1名称
            player2_name: 玩家2名称
            exp_gained: 获得修为
            intimacy_increase: 亲密度增加
            benefits: 其他收益
            location: 地点

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 记录双修
            cursor.execute("""
                INSERT INTO dual_cultivation_records
                (player1_name, player2_name, cultivation_date, exp_gained, intimacy_increase, benefits, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (player1_name, player2_name, now, exp_gained, intimacy_increase,
                  json.dumps(benefits, ensure_ascii=False), location))

            # 更新道侣关系
            cursor.execute("""
                UPDATE marriage_records
                SET dual_cultivation_count = dual_cultivation_count + 1,
                    last_dual_cultivation = ?,
                    intimacy = intimacy + ?
                WHERE ((player1_name = ? AND player2_name = ?) OR (player1_name = ? AND player2_name = ?))
                AND is_active = 1
            """, (now, intimacy_increase, player1_name, player2_name, player2_name, player1_name))

            # 更新社交关系亲密度
            self.update_social_relation(player1_name, player2_name, intimacy_increase, 0, 0)
            self.update_social_relation(player2_name, player1_name, intimacy_increase, 0, 0)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录双修失败: {e}")
            return False

    def divorce(self, player1_name: str, player2_name: str, reason: str = '') -> bool:
        """
        解除道侣关系

        Args:
            player1_name: 玩家1名称
            player2_name: 玩家2名称
            reason: 解除原因

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE marriage_records
                SET is_active = 0, divorced_at = ?, divorce_reason = ?
                WHERE ((player1_name = ? AND player2_name = ?) OR (player1_name = ? AND player2_name = ?))
                AND is_active = 1
            """, (now, reason, player1_name, player2_name, player2_name, player1_name))

            # 更新社交关系
            self.add_social_relation(player1_name, player2_name, '旧识', 30, 30, 20, f"曾经的道侣，因{reason}分开")
            self.add_social_relation(player2_name, player1_name, '旧识', 30, 30, 20, f"曾经的道侣，因{reason}分开")

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"解除道侣关系失败: {e}")
            return False

    def establish_master_apprentice(self, master_name: str, apprentice_name: str,
                                   relation_type: str = '师徒') -> bool:
        """
        建立师徒关系

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            relation_type: 关系类型（师徒/记名师徒）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO master_apprentice
                (master_name, apprentice_name, relation_type, established_date, respect, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (master_name, apprentice_name, relation_type, now, 50, 1))

            # 添加社交关系
            self.add_social_relation(master_name, apprentice_name, '师徒', 70, 80, 0, '师徒关系')
            self.add_social_relation(apprentice_name, master_name, '师徒', 70, 80, 0, '师徒关系')

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"建立师徒关系失败: {e}")
            return False

    def get_master(self, apprentice_name: str) -> Optional[Dict[str, Any]]:
        """
        获取徒弟的师父

        Args:
            apprentice_name: 徒弟名称

        Returns:
            师父信息
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM master_apprentice
            WHERE apprentice_name = ? AND is_active = 1
        """, (apprentice_name,))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'master_name': row['master_name'],
            'relation_type': row['relation_type'],
            'established_date': row['established_date'],
            'respect': row['respect'],
            'teaching_count': row['teaching_count'],
            'techniques_taught': json.loads(row['techniques_taught']) if row['techniques_taught'] else []
        }

    def get_apprentices(self, master_name: str) -> List[Dict[str, Any]]:
        """
        获取师父的徒弟列表

        Args:
            master_name: 师父名称

        Returns:
            徒弟列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM master_apprentice
            WHERE master_name = ? AND is_active = 1
            ORDER BY established_date DESC
        """, (master_name,))

        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'apprentice_name': row['apprentice_name'],
                'relation_type': row['relation_type'],
                'established_date': row['established_date'],
                'respect': row['respect'],
                'teaching_count': row['teaching_count'],
                'techniques_taught': json.loads(row['techniques_taught']) if row['techniques_taught'] else []
            }
            for row in rows
        ]

    def teach_technique(self, master_name: str, apprentice_name: str,
                       technique_name: str) -> bool:
        """
        师父传授功法

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            technique_name: 功法名称

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取当前已传授功法
            cursor.execute("""
                SELECT techniques_taught FROM master_apprentice
                WHERE master_name = ? AND apprentice_name = ? AND is_active = 1
            """, (master_name, apprentice_name))

            row = cursor.fetchone()
            if row is None:
                return False

            techniques = json.loads(row['techniques_taught']) if row['techniques_taught'] else []
            if technique_name not in techniques:
                techniques.append(technique_name)

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE master_apprentice
                SET teaching_count = teaching_count + 1,
                    last_teaching = ?,
                    techniques_taught = ?,
                    respect = respect + 5
                WHERE master_name = ? AND apprentice_name = ? AND is_active = 1
            """, (now, json.dumps(techniques, ensure_ascii=False), master_name, apprentice_name))

            # 更新社交关系
            self.update_social_relation(master_name, apprentice_name, 5, 5, 0)
            self.update_social_relation(apprentice_name, master_name, 5, 5, 0)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"传授功法失败: {e}")
            return False

    def end_master_apprentice(self, master_name: str, apprentice_name: str,
                              reason: str = '') -> bool:
        """
        解除师徒关系

        Args:
            master_name: 师父名称
            apprentice_name: 徒弟名称
            reason: 解除原因

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE master_apprentice
                SET is_active = 0, ended_at = ?, end_reason = ?
                WHERE master_name = ? AND apprentice_name = ? AND is_active = 1
            """, (now, reason, master_name, apprentice_name))

            # 更新社交关系
            self.add_social_relation(master_name, apprentice_name, '旧识', 40, 40, 10, f"曾经的师徒，因{reason}分开")
            self.add_social_relation(apprentice_name, master_name, '旧识', 40, 40, 10, f"曾经的师徒，因{reason}分开")

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"解除师徒关系失败: {e}")
            return False

    def create_revenge_record(self, victim_name: str, enemy_name: str,
                             conflict_reason: str, hatred_level: int = 50) -> bool:
        """
        创建复仇记录

        Args:
            victim_name: 受害者名称
            enemy_name: 敌人名称
            conflict_reason: 结仇原因
            hatred_level: 仇恨等级

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO revenge_records
                (victim_name, enemy_name, conflict_reason, hatred_level, created_at, revenge_target)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (victim_name, enemy_name, conflict_reason, hatred_level, now, f"击败{enemy_name}"))

            # 添加仇敌关系
            self.add_social_relation(victim_name, enemy_name, '仇敌', 0, 0, hatred_level, conflict_reason)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建复仇记录失败: {e}")
            return False

    def get_revenge_records(self, victim_name: str, is_completed: bool = None) -> List[Dict[str, Any]]:
        """
        获取复仇记录

        Args:
            victim_name: 受害者名称
            is_completed: 是否已完成

        Returns:
            复仇记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM revenge_records
            WHERE victim_name = ?
        """
        params = [victim_name]

        if is_completed is not None:
            query += " AND is_completed = ?"
            params.append(1 if is_completed else 0)

        query += " ORDER BY hatred_level DESC, created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'enemy_name': row['enemy_name'],
                'conflict_reason': row['conflict_reason'],
                'hatred_level': row['hatred_level'],
                'created_at': row['created_at'],
                'revenge_target': row['revenge_target'],
                'is_completed': bool(row['is_completed']),
                'completed_at': row['completed_at'],
                'revenge_result': row['revenge_result']
            }
            for row in rows
        ]

    def complete_revenge(self, record_id: int, result: str = '') -> bool:
        """
        完成复仇

        Args:
            record_id: 记录ID
            result: 复仇结果

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE revenge_records
                SET is_completed = 1, completed_at = ?, revenge_result = ?
                WHERE id = ?
            """, (now, result, record_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"完成复仇记录失败: {e}")
            return False

    def record_social_interaction(self, initiator_name: str, target_name: str,
                                 interaction_type: str, description: str,
                                 intimacy_change: int = 0, trust_change: int = 0,
                                 hatred_change: int = 0, location: str = '') -> bool:
        """
        记录社交互动

        Args:
            initiator_name: 发起者名称
            target_name: 目标名称
            interaction_type: 互动类型
            description: 描述
            intimacy_change: 亲密度变化
            trust_change: 信任度变化
            hatred_change: 仇恨度变化
            location: 地点

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO social_interactions
                (initiator_name, target_name, interaction_type, interaction_date, description,
                 intimacy_change, trust_change, hatred_change, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (initiator_name, target_name, interaction_type, now, description,
                  intimacy_change, trust_change, hatred_change, location))

            # 更新社交关系
            self.update_social_relation(initiator_name, target_name,
                                       intimacy_change, trust_change, hatred_change)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录社交互动失败: {e}")
            return False

    # ==================== NPC关系系统操作 ====================

    def add_npc_relation(self, npc1_id: str, npc2_id: str, relation_type: str = 'acquaintance',
                         affinity: int = 0, intimacy: int = 0, hatred: int = 0,
                         history: str = '', relation_status: str = 'active',
                         established_date: str = None) -> bool:
        """
        添加或更新NPC关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            relation_type: 关系类型
            affinity: 好感度
            intimacy: 亲密度
            hatred: 仇恨度
            history: 历史记录JSON字符串
            relation_status: 关系状态 (active/inactive)
            established_date: 建立日期

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            if established_date is None:
                established_date = now

            # 确保npc1_id < npc2_id以保持一致性
            if npc1_id > npc2_id:
                npc1_id, npc2_id = npc2_id, npc1_id

            cursor.execute("""
                INSERT OR REPLACE INTO npc_relations
                (npc1_id, npc2_id, relation_type, relation_status, affinity, intimacy, hatred,
                 history, established_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (npc1_id, npc2_id, relation_type, relation_status, affinity, intimacy, hatred,
                  history, established_date, now, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加NPC关系失败: {e}")
            return False

    def get_npc_relation(self, npc1_id: str, npc2_id: str) -> Optional[Dict[str, Any]]:
        """
        获取两个NPC之间的关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            关系数据字典，如果不存在则返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 确保npc1_id < npc2_id以保持一致性
            if npc1_id > npc2_id:
                npc1_id, npc2_id = npc2_id, npc1_id

            cursor.execute("""
                SELECT * FROM npc_relations
                WHERE npc1_id = ? AND npc2_id = ?
            """, (npc1_id, npc2_id))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'npc1_id': row['npc1_id'],
                    'npc2_id': row['npc2_id'],
                    'relation_type': row['relation_type'],
                    'relation_status': row['relation_status'],
                    'affinity': row['affinity'],
                    'intimacy': row['intimacy'],
                    'hatred': row['hatred'],
                    'history': json.loads(row['history']) if row['history'] else [],
                    'last_interaction': row['last_interaction'],
                    'established_date': row['established_date'],
                    'ended_date': row['ended_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
        except sqlite3.Error as e:
            print(f"获取NPC关系失败: {e}")
            return None

    def get_npc_relations(self, npc_id: str, relation_type: str = None) -> List[Dict[str, Any]]:
        """
        获取NPC的所有关系

        Args:
            npc_id: NPC的ID
            relation_type: 关系类型筛选（可选）

        Returns:
            关系列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT * FROM npc_relations
                WHERE npc1_id = ? OR npc2_id = ?
            """
            params = [npc_id, npc_id]

            if relation_type:
                query += " AND relation_type = ?"
                params.append(relation_type)

            cursor.execute(query, params)

            relations = []
            for row in cursor.fetchall():
                # 确定对方NPC的ID
                other_id = row['npc2_id'] if row['npc1_id'] == npc_id else row['npc1_id']
                relations.append({
                    'id': row['id'],
                    'npc_id': other_id,
                    'relation_type': row['relation_type'],
                    'relation_status': row['relation_status'],
                    'affinity': row['affinity'],
                    'intimacy': row['intimacy'],
                    'hatred': row['hatred'],
                    'history': json.loads(row['history']) if row['history'] else [],
                    'last_interaction': row['last_interaction'],
                    'established_date': row['established_date'],
                    'ended_date': row['ended_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return relations
        except sqlite3.Error as e:
            print(f"获取NPC关系列表失败: {e}")
            return []

    def update_npc_relation(self, npc1_id: str, npc2_id: str,
                           delta_affinity: int = 0, delta_intimacy: int = 0,
                           delta_hatred: int = 0, reason: str = '') -> bool:
        """
        更新NPC关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            delta_affinity: 好感度变化
            delta_intimacy: 亲密度变化
            delta_hatred: 仇恨度变化
            reason: 变化原因

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 确保npc1_id < npc2_id以保持一致性
            original_npc1, original_npc2 = npc1_id, npc2_id
            if npc1_id > npc2_id:
                npc1_id, npc2_id = npc2_id, npc1_id

            # 获取当前关系
            cursor.execute("""
                SELECT * FROM npc_relations
                WHERE npc1_id = ? AND npc2_id = ?
            """, (npc1_id, npc2_id))

            row = cursor.fetchone()
            now = datetime.now().isoformat()

            if row:
                # 更新现有关系
                new_affinity = max(-100, min(100, row['affinity'] + delta_affinity))
                new_intimacy = max(0, min(100, row['intimacy'] + delta_intimacy))
                new_hatred = max(0, min(100, row['hatred'] + delta_hatred))

                # 根据数值自动更新关系类型
                new_type = row['relation_type']
                if new_hatred >= 30:
                    new_type = 'hostility'
                elif new_affinity >= 20 and new_intimacy >= 20:
                    new_type = 'friendship'
                elif new_affinity < -20:
                    new_type = 'unfriendly'

                cursor.execute("""
                    UPDATE npc_relations
                    SET affinity = ?, intimacy = ?, hatred = ?, relation_type = ?, updated_at = ?
                    WHERE npc1_id = ? AND npc2_id = ?
                """, (new_affinity, new_intimacy, new_hatred, new_type, now, npc1_id, npc2_id))
            else:
                # 创建新关系
                new_affinity = max(-100, min(100, delta_affinity))
                new_intimacy = max(0, min(100, delta_intimacy))
                new_hatred = max(0, min(100, delta_hatred))

                # 确定关系类型
                new_type = 'acquaintance'
                if new_hatred >= 30:
                    new_type = 'hostility'
                elif new_affinity >= 20:
                    new_type = 'friendship'
                elif new_affinity < -20:
                    new_type = 'unfriendly'

                cursor.execute("""
                    INSERT INTO npc_relations
                    (npc1_id, npc2_id, relation_type, affinity, intimacy, hatred, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (npc1_id, npc2_id, new_type, new_affinity, new_intimacy, new_hatred, now, now))

            # 记录历史
            cursor.execute("""
                INSERT INTO npc_relation_history
                (npc1_id, npc2_id, event, delta_affinity, delta_intimacy, delta_hatred, timestamp, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (original_npc1, original_npc2, 'relation_update', delta_affinity, delta_intimacy, delta_hatred, now, reason))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新NPC关系失败: {e}")
            return False

    def remove_npc_relation(self, npc1_id: str, npc2_id: str) -> bool:
        """
        移除NPC关系

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 确保npc1_id < npc2_id以保持一致性
            if npc1_id > npc2_id:
                npc1_id, npc2_id = npc2_id, npc1_id

            cursor.execute("""
                DELETE FROM npc_relations
                WHERE npc1_id = ? AND npc2_id = ?
            """, (npc1_id, npc2_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"移除NPC关系失败: {e}")
            return False

    def get_npc_relation_history(self, npc1_id: str, npc2_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取NPC关系历史

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            limit: 返回记录数量限制

        Returns:
            历史记录列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM npc_relation_history
                WHERE (npc1_id = ? AND npc2_id = ?) OR (npc1_id = ? AND npc2_id = ?)
                ORDER BY timestamp DESC
                LIMIT ?
            """, (npc1_id, npc2_id, npc2_id, npc1_id, limit))

            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row['id'],
                    'npc1_id': row['npc1_id'],
                    'npc2_id': row['npc2_id'],
                    'event': row['event'],
                    'delta_affinity': row['delta_affinity'],
                    'delta_intimacy': row['delta_intimacy'],
                    'delta_hatred': row['delta_hatred'],
                    'timestamp': row['timestamp'],
                    'reason': row['reason']
                })
            return history
        except sqlite3.Error as e:
            print(f"获取NPC关系历史失败: {e}")
            return []

    def get_all_npc_relations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有NPC关系

        Returns:
            以NPC ID为键的关系字典
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM npc_relations")

            relations = {}
            for row in cursor.fetchall():
                npc1_id = row['npc1_id']
                npc2_id = row['npc2_id']

                relation_data = {
                    'npc1_id': npc1_id,
                    'npc2_id': npc2_id,
                    'relation_type': row['relation_type'],
                    'relation_status': row['relation_status'],
                    'affinity': row['affinity'],
                    'intimacy': row['intimacy'],
                    'hatred': row['hatred'],
                    'history': json.loads(row['history']) if row['history'] else [],
                    'last_interaction': row['last_interaction'],
                    'established_date': row['established_date'],
                    'ended_date': row['ended_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }

                if npc1_id not in relations:
                    relations[npc1_id] = []
                if npc2_id not in relations:
                    relations[npc2_id] = []

                relations[npc1_id].append({**relation_data, 'npc_id': npc2_id})
                relations[npc2_id].append({**relation_data, 'npc_id': npc1_id})

            return relations
        except sqlite3.Error as e:
            print(f"获取所有NPC关系失败: {e}")
            return {}

    def record_npc_social_event(self, event_type: str, npc1_id: str, npc2_id: str,
                                description: str = '', location: str = '',
                                result: str = '', is_public: bool = False) -> bool:
        """
        记录NPC社交事件

        Args:
            event_type: 事件类型 (dao_lv_established, master_apprentice_established, etc.)
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            description: 事件描述
            location: 发生地点
            result: 事件结果
            is_public: 是否公开事件

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO npc_social_events
                (event_type, npc1_id, npc2_id, event_date, description, location, result, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_type, npc1_id, npc2_id, now, description, location, result, 1 if is_public else 0))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录NPC社交事件失败: {e}")
            return False

    def get_npc_social_events(self, npc_id: str, event_type: str = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取NPC的社交事件

        Args:
            npc_id: NPC的ID
            event_type: 事件类型筛选（可选）
            limit: 返回记录数量限制

        Returns:
            社交事件列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT * FROM npc_social_events
                WHERE npc1_id = ? OR npc2_id = ?
            """
            params = [npc_id, npc_id]

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            query += " ORDER BY event_date DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row['id'],
                    'event_type': row['event_type'],
                    'npc1_id': row['npc1_id'],
                    'npc2_id': row['npc2_id'],
                    'event_date': row['event_date'],
                    'description': row['description'],
                    'location': row['location'],
                    'result': row['result'],
                    'is_public': bool(row['is_public'])
                })
            return events
        except sqlite3.Error as e:
            print(f"获取NPC社交事件失败: {e}")
            return []

    def record_relationship_change(self, npc1_id: str, npc2_id: str,
                                   change_type: str, old_value: int,
                                   new_value: int, reason: str = '',
                                   trigger_event: str = '') -> bool:
        """
        记录NPC关系数值变化

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            change_type: 变化类型 (affinity, intimacy, hatred)
            old_value: 原值
            new_value: 新值
            reason: 变化原因
            trigger_event: 触发事件

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            delta = new_value - old_value

            cursor.execute("""
                INSERT INTO npc_relationship_changes
                (npc1_id, npc2_id, change_type, old_value, new_value, delta, change_date, reason, trigger_event)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (npc1_id, npc2_id, change_type, old_value, new_value, delta, now, reason, trigger_event))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录关系变化失败: {e}")
            return False

    def get_relationship_changes(self, npc1_id: str, npc2_id: str = None,
                                 change_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取关系数值变化历史

        Args:
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID（可选）
            change_type: 变化类型筛选（可选）
            limit: 返回记录数量限制

        Returns:
            关系变化列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT * FROM npc_relationship_changes
                WHERE (npc1_id = ? OR npc2_id = ?)
            """
            params = [npc1_id, npc1_id]

            if npc2_id:
                query += " AND (npc1_id = ? OR npc2_id = ?)"
                params.extend([npc2_id, npc2_id])

            if change_type:
                query += " AND change_type = ?"
                params.append(change_type)

            query += " ORDER BY change_date DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            changes = []
            for row in cursor.fetchall():
                changes.append({
                    'id': row['id'],
                    'npc1_id': row['npc1_id'],
                    'npc2_id': row['npc2_id'],
                    'change_type': row['change_type'],
                    'old_value': row['old_value'],
                    'new_value': row['new_value'],
                    'delta': row['delta'],
                    'change_date': row['change_date'],
                    'reason': row['reason'],
                    'trigger_event': row['trigger_event']
                })
            return changes
        except sqlite3.Error as e:
            print(f"获取关系变化历史失败: {e}")
            return []

    def get_npc_dao_lv(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取NPC的道侣关系

        Args:
            npc_id: NPC的ID

        Returns:
            道侣关系信息，如果没有则返回None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM npc_relations
                WHERE (npc1_id = ? OR npc2_id = ?)
                AND relation_type = 'dao_lv'
                AND relation_status = 'active'
            """, (npc_id, npc_id))

            row = cursor.fetchone()
            if row:
                partner_id = row['npc2_id'] if row['npc1_id'] == npc_id else row['npc1_id']
                return {
                    'id': row['id'],
                    'partner_id': partner_id,
                    'relation_type': row['relation_type'],
                    'affinity': row['affinity'],
                    'intimacy': row['intimacy'],
                    'established_date': row['established_date'],
                    'created_at': row['created_at']
                }
            return None
        except sqlite3.Error as e:
            print(f"获取NPC道侣关系失败: {e}")
            return None

    def get_npc_master_apprentice_relations(self, npc_id: str, as_master: bool = True) -> List[Dict[str, Any]]:
        """
        获取NPC的师徒关系

        Args:
            npc_id: NPC的ID
            as_master: True为获取徒弟列表，False为获取师父

        Returns:
            师徒关系列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if as_master:
                cursor.execute("""
                    SELECT * FROM npc_relations
                    WHERE npc1_id = ? AND relation_type = 'master_apprentice'
                    AND relation_status = 'active'
                    UNION
                    SELECT * FROM npc_relations
                    WHERE npc2_id = ? AND relation_type = 'master_apprentice'
                    AND relation_status = 'active'
                """, (npc_id, npc_id))
            else:
                # 获取师父（关系中的另一方）
                cursor.execute("""
                    SELECT * FROM npc_relations
                    WHERE (npc1_id = ? OR npc2_id = ?)
                    AND relation_type = 'master_apprentice'
                    AND relation_status = 'active'
                """, (npc_id, npc_id))

            relations = []
            for row in cursor.fetchall():
                other_id = row['npc2_id'] if row['npc1_id'] == npc_id else row['npc1_id']
                relations.append({
                    'id': row['id'],
                    'other_id': other_id,
                    'relation_type': row['relation_type'],
                    'affinity': row['affinity'],
                    'intimacy': row['intimacy'],
                    'established_date': row['established_date'],
                    'created_at': row['created_at']
                })
            return relations
        except sqlite3.Error as e:
            print(f"获取NPC师徒关系失败: {e}")
            return []

    # ==================== 商店系统操作 ====================

    def init_trade_tables(self):
        """创建交易系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 shops 表 - 商店信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                shop_type TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                owner_id TEXT,
                owner_name TEXT,
                reputation INTEGER DEFAULT 0,
                tax_rate REAL DEFAULT 0.05,
                is_active INTEGER DEFAULT 1,
                refresh_interval INTEGER DEFAULT 24,
                last_refresh TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 shop_items 表 - 商店商品
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                base_price INTEGER NOT NULL,
                current_price INTEGER NOT NULL,
                stock INTEGER DEFAULT 1,
                max_stock INTEGER DEFAULT 10,
                rarity TEXT,
                level_required INTEGER DEFAULT 0,
                description TEXT,
                effects TEXT,
                demand_factor REAL DEFAULT 1.0,
                supply_factor REAL DEFAULT 1.0,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
            )
        """)

        # 创建 auction_items 表 - 拍卖行物品
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auction_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                seller_name TEXT,
                start_price INTEGER NOT NULL,
                current_price INTEGER NOT NULL,
                buyout_price INTEGER,
                bid_increment INTEGER DEFAULT 100,
                rarity TEXT,
                level_required INTEGER DEFAULT 0,
                description TEXT,
                effects TEXT,
                status TEXT DEFAULT 'active',
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                highest_bidder_id TEXT,
                highest_bidder_name TEXT,
                bid_count INTEGER DEFAULT 0
            )
        """)

        # 创建 player_trades 表 - 玩家交易记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                price INTEGER NOT NULL,
                total_amount INTEGER NOT NULL,
                seller_id TEXT,
                seller_name TEXT,
                buyer_id TEXT,
                buyer_name TEXT,
                shop_id TEXT,
                shop_name TEXT,
                auction_id INTEGER,
                trade_time TEXT NOT NULL,
                location TEXT
            )
        """)

        # 创建 price_history 表 - 价格历史记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                shop_id TEXT,
                shop_name TEXT,
                price INTEGER NOT NULL,
                trade_type TEXT NOT NULL,
                trade_time TEXT NOT NULL,
                location TEXT
            )
        """)

        # 创建 player_trade_offers 表 - 玩家交易请求
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_trade_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT NOT NULL,
                sender_name TEXT,
                receiver_id TEXT NOT NULL,
                receiver_name TEXT,
                item_name TEXT,
                item_type TEXT,
                quantity INTEGER DEFAULT 1,
                price INTEGER,
                offer_type TEXT DEFAULT 'sell',
                status TEXT DEFAULT 'pending',
                message TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                responded_at TEXT
            )
        """)

        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_shops_location ON shops(location)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_shops_type ON shops(shop_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_shop_items_shop_id ON shop_items(shop_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_shop_items_type ON shop_items(item_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auction_status ON auction_items(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auction_end_time ON auction_items(end_time)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_seller ON player_trades(seller_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_buyer ON player_trades(buyer_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_item ON price_history(item_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_offers_sender ON player_trade_offers(sender_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_offers_receiver ON player_trade_offers(receiver_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_offers_status ON player_trade_offers(status)
        """)

        conn.commit()

    def save_shop(self, shop_data: Dict[str, Any]) -> str:
        """
        保存商店信息

        Args:
            shop_data: 商店数据字典

        Returns:
            商店ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        shop_id = shop_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO shops (
                id, name, shop_type, location, description, owner_id, owner_name,
                reputation, tax_rate, is_active, refresh_interval, last_refresh, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shop_id,
            shop_data.get('name', ''),
            shop_data.get('shop_type', 'general'),
            shop_data.get('location', ''),
            shop_data.get('description', ''),
            shop_data.get('owner_id', ''),
            shop_data.get('owner_name', ''),
            shop_data.get('reputation', 0),
            shop_data.get('tax_rate', 0.05),
            1 if shop_data.get('is_active', True) else 0,
            shop_data.get('refresh_interval', 24),
            shop_data.get('last_refresh', now),
            now
        ))

        conn.commit()
        return shop_id

    def get_shop_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        获取指定地点的所有商店

        Args:
            location: 地点名称

        Returns:
            商店列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM shops WHERE location = ? AND is_active = 1
        """, (location,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'shop_type': row['shop_type'],
                'location': row['location'],
                'description': row['description'],
                'owner_id': row['owner_id'],
                'owner_name': row['owner_name'],
                'reputation': row['reputation'],
                'tax_rate': row['tax_rate'],
                'is_active': bool(row['is_active']),
                'refresh_interval': row['refresh_interval'],
                'last_refresh': row['last_refresh'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_shop_items(self, shop_id: str) -> List[Dict[str, Any]]:
        """
        获取商店的商品列表

        Args:
            shop_id: 商店ID

        Returns:
            商品列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM shop_items WHERE shop_id = ? AND is_active = 1 AND stock > 0
        """, (shop_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'shop_id': row['shop_id'],
                'item_name': row['item_name'],
                'item_type': row['item_type'],
                'base_price': row['base_price'],
                'current_price': row['current_price'],
                'stock': row['stock'],
                'max_stock': row['max_stock'],
                'rarity': row['rarity'],
                'level_required': row['level_required'],
                'description': row['description'],
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'demand_factor': row['demand_factor'],
                'supply_factor': row['supply_factor'],
                'is_active': bool(row['is_active'])
            }
            for row in rows
        ]

    def add_shop_item(self, shop_id: str, item_data: Dict[str, Any]) -> int:
        """
        添加商品到商店

        Args:
            shop_id: 商店ID
            item_data: 商品数据

        Returns:
            商品ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        base_price = item_data.get('base_price', 100)

        cursor.execute("""
            INSERT INTO shop_items (
                shop_id, item_name, item_type, base_price, current_price,
                stock, max_stock, rarity, level_required, description, effects,
                demand_factor, supply_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shop_id,
            item_data.get('item_name', ''),
            item_data.get('item_type', ''),
            base_price,
            item_data.get('current_price', base_price),
            item_data.get('stock', 1),
            item_data.get('max_stock', 10),
            item_data.get('rarity', 'common'),
            item_data.get('level_required', 0),
            item_data.get('description', ''),
            json.dumps(item_data.get('effects', {}), ensure_ascii=False),
            item_data.get('demand_factor', 1.0),
            item_data.get('supply_factor', 1.0)
        ))

        conn.commit()
        return cursor.lastrowid

    def update_shop_item_price(self, item_id: int, new_price: int) -> bool:
        """
        更新商品价格

        Args:
            item_id: 商品ID
            new_price: 新价格

        Returns:
            是否更新成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE shop_items SET current_price = ? WHERE id = ?
            """, (new_price, item_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新商品价格失败: {e}")
            return False

    def update_shop_item_stock(self, item_id: int, quantity: int) -> bool:
        """
        更新商品库存

        Args:
            item_id: 商品ID
            quantity: 变化数量（正数为增加，负数为减少）

        Returns:
            是否更新成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE shop_items 
                SET stock = MAX(0, stock + ?) 
                WHERE id = ?
            """, (quantity, item_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新商品库存失败: {e}")
            return False

    def create_auction_item(self, auction_data: Dict[str, Any]) -> int:
        """
        创建拍卖物品

        Args:
            auction_data: 拍卖数据

        Returns:
            拍卖ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO auction_items (
                item_name, item_type, seller_id, seller_name, start_price,
                current_price, buyout_price, bid_increment, rarity, level_required,
                description, effects, status, start_time, end_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            auction_data.get('item_name', ''),
            auction_data.get('item_type', ''),
            auction_data.get('seller_id', ''),
            auction_data.get('seller_name', ''),
            auction_data.get('start_price', 100),
            auction_data.get('start_price', 100),
            auction_data.get('buyout_price', None),
            auction_data.get('bid_increment', 100),
            auction_data.get('rarity', 'common'),
            auction_data.get('level_required', 0),
            auction_data.get('description', ''),
            json.dumps(auction_data.get('effects', {}), ensure_ascii=False),
            'active',
            now,
            auction_data.get('end_time', now)
        ))

        conn.commit()
        return cursor.lastrowid

    def get_active_auctions(self, item_type: str = None) -> List[Dict[str, Any]]:
        """
        获取活跃的拍卖物品

        Args:
            item_type: 物品类型筛选

        Returns:
            拍卖列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if item_type:
            cursor.execute("""
                SELECT * FROM auction_items 
                WHERE status = 'active' AND end_time > ? AND item_type = ?
                ORDER BY end_time ASC
            """, (now, item_type))
        else:
            cursor.execute("""
                SELECT * FROM auction_items 
                WHERE status = 'active' AND end_time > ?
                ORDER BY end_time ASC
            """, (now,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'item_name': row['item_name'],
                'item_type': row['item_type'],
                'seller_id': row['seller_id'],
                'seller_name': row['seller_name'],
                'start_price': row['start_price'],
                'current_price': row['current_price'],
                'buyout_price': row['buyout_price'],
                'bid_increment': row['bid_increment'],
                'rarity': row['rarity'],
                'level_required': row['level_required'],
                'description': row['description'],
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'status': row['status'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'highest_bidder_id': row['highest_bidder_id'],
                'highest_bidder_name': row['highest_bidder_name'],
                'bid_count': row['bid_count']
            }
            for row in rows
        ]

    def place_bid(self, auction_id: int, bidder_id: str, bidder_name: str, bid_amount: int) -> bool:
        """
        竞拍物品

        Args:
            auction_id: 拍卖ID
            bidder_id: 竞拍者ID
            bidder_name: 竞拍者名称
            bid_amount: 出价金额

        Returns:
            是否竞拍成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 检查拍卖是否活跃
            cursor.execute("""
                SELECT current_price, bid_increment, end_time, status 
                FROM auction_items WHERE id = ?
            """, (auction_id,))
            row = cursor.fetchone()

            if not row:
                return False

            if row['status'] != 'active':
                return False

            if datetime.now().isoformat() > row['end_time']:
                return False

            min_bid = row['current_price'] + row['bid_increment']
            if bid_amount < min_bid:
                return False

            # 更新竞拍信息
            cursor.execute("""
                UPDATE auction_items 
                SET current_price = ?, highest_bidder_id = ?, highest_bidder_name = ?, bid_count = bid_count + 1
                WHERE id = ?
            """, (bid_amount, bidder_id, bidder_name, auction_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"竞拍失败: {e}")
            return False

    def buyout_auction(self, auction_id: int, buyer_id: str, buyer_name: str) -> Tuple[bool, int]:
        """
        一口价购买拍卖物品

        Args:
            auction_id: 拍卖ID
            buyer_id: 购买者ID
            buyer_name: 购买者名称

        Returns:
            (是否成功, 价格)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取拍卖信息
            cursor.execute("""
                SELECT buyout_price, status, end_time FROM auction_items WHERE id = ?
            """, (auction_id,))
            row = cursor.fetchone()

            if not row or row['status'] != 'active' or not row['buyout_price']:
                return False, 0

            if datetime.now().isoformat() > row['end_time']:
                return False, 0

            price = row['buyout_price']

            # 结束拍卖
            cursor.execute("""
                UPDATE auction_items 
                SET status = 'sold', highest_bidder_id = ?, highest_bidder_name = ?, current_price = ?
                WHERE id = ?
            """, (buyer_id, buyer_name, price, auction_id))

            conn.commit()
            return cursor.rowcount > 0, price
        except sqlite3.Error as e:
            print(f"一口价购买失败: {e}")
            return False, 0

    def record_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        记录交易

        Args:
            trade_data: 交易数据

        Returns:
            交易记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO player_trades (
                trade_type, item_name, item_type, quantity, price, total_amount,
                seller_id, seller_name, buyer_id, buyer_name, shop_id, shop_name,
                auction_id, trade_time, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data.get('trade_type', 'buy'),
            trade_data.get('item_name', ''),
            trade_data.get('item_type', ''),
            trade_data.get('quantity', 1),
            trade_data.get('price', 0),
            trade_data.get('total_amount', 0),
            trade_data.get('seller_id', ''),
            trade_data.get('seller_name', ''),
            trade_data.get('buyer_id', ''),
            trade_data.get('buyer_name', ''),
            trade_data.get('shop_id', ''),
            trade_data.get('shop_name', ''),
            trade_data.get('auction_id', None),
            now,
            trade_data.get('location', '')
        ))

        conn.commit()
        return cursor.lastrowid

    def record_price_history(self, price_data: Dict[str, Any]) -> bool:
        """
        记录价格历史

        Args:
            price_data: 价格数据

        Returns:
            是否记录成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO price_history (
                    item_name, item_type, shop_id, shop_name, price, trade_type, trade_time, location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                price_data.get('item_name', ''),
                price_data.get('item_type', ''),
                price_data.get('shop_id', ''),
                price_data.get('shop_name', ''),
                price_data.get('price', 0),
                price_data.get('trade_type', 'buy'),
                now,
                price_data.get('location', '')
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录价格历史失败: {e}")
            return False

    def get_price_history(self, item_name: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        获取物品价格历史

        Args:
            item_name: 物品名称
            limit: 返回记录数限制

        Returns:
            价格历史列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM price_history 
            WHERE item_name = ? 
            ORDER BY trade_time DESC 
            LIMIT ?
        """, (item_name, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'item_name': row['item_name'],
                'item_type': row['item_type'],
                'shop_id': row['shop_id'],
                'shop_name': row['shop_name'],
                'price': row['price'],
                'trade_type': row['trade_type'],
                'trade_time': row['trade_time'],
                'location': row['location']
            }
            for row in rows
        ]

    def create_trade_offer(self, offer_data: Dict[str, Any]) -> int:
        """
        创建玩家交易请求

        Args:
            offer_data: 交易请求数据

        Returns:
            请求ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO player_trade_offers (
                sender_id, sender_name, receiver_id, receiver_name, item_name,
                item_type, quantity, price, offer_type, status, message, created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            offer_data.get('sender_id', ''),
            offer_data.get('sender_name', ''),
            offer_data.get('receiver_id', ''),
            offer_data.get('receiver_name', ''),
            offer_data.get('item_name', ''),
            offer_data.get('item_type', ''),
            offer_data.get('quantity', 1),
            offer_data.get('price', 0),
            offer_data.get('offer_type', 'sell'),
            'pending',
            offer_data.get('message', ''),
            now,
            offer_data.get('expires_at', now)
        ))

        conn.commit()
        return cursor.lastrowid

    def get_pending_offers(self, player_id: str) -> List[Dict[str, Any]]:
        """
        获取玩家的待处理交易请求

        Args:
            player_id: 玩家ID

        Returns:
            交易请求列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            SELECT * FROM player_trade_offers 
            WHERE (receiver_id = ? OR sender_id = ?) AND status = 'pending' AND expires_at > ?
            ORDER BY created_at DESC
        """, (player_id, player_id, now))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'sender_id': row['sender_id'],
                'sender_name': row['sender_name'],
                'receiver_id': row['receiver_id'],
                'receiver_name': row['receiver_name'],
                'item_name': row['item_name'],
                'item_type': row['item_type'],
                'quantity': row['quantity'],
                'price': row['price'],
                'offer_type': row['offer_type'],
                'status': row['status'],
                'message': row['message'],
                'created_at': row['created_at'],
                'expires_at': row['expires_at']
            }
            for row in rows
        ]

    def respond_to_offer(self, offer_id: int, accept: bool, responder_id: str) -> bool:
        """
        响应交易请求

        Args:
            offer_id: 请求ID
            accept: 是否接受
            responder_id: 响应者ID

        Returns:
            是否响应成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            status = 'accepted' if accept else 'rejected'

            cursor.execute("""
                UPDATE player_trade_offers 
                SET status = ?, responded_at = ?
                WHERE id = ? AND (receiver_id = ? OR sender_id = ?) AND status = 'pending'
            """, (status, now, offer_id, responder_id, responder_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"响应交易请求失败: {e}")
            return False

    # ==================== 炼丹系统操作 ====================

    def save_alchemy_recipe(self, recipe_data: Dict[str, Any]) -> str:
        """
        保存丹方

        Args:
            recipe_data: 丹方数据字典

        Returns:
            丹方ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        recipe_id = recipe_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO alchemy_recipes (
                id, name, description, pill_type, rarity, realm_required,
                materials, effects, base_success_rate, quality_multipliers, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe_id,
            recipe_data.get('name', ''),
            recipe_data.get('description', ''),
            recipe_data.get('pill_type', ''),
            recipe_data.get('rarity', 'common'),
            recipe_data.get('realm_required', 0),
            json.dumps(recipe_data.get('materials', {}), ensure_ascii=False),
            json.dumps(recipe_data.get('effects', {}), ensure_ascii=False),
            recipe_data.get('base_success_rate', 0.5),
            json.dumps(recipe_data.get('quality_multipliers', {}), ensure_ascii=False),
            now
        ))

        conn.commit()
        return recipe_id

    def get_alchemy_recipes(self, pill_type: str = None, rarity: str = None) -> List[Dict[str, Any]]:
        """
        获取丹方列表

        Args:
            pill_type: 丹药类型筛选
            rarity: 稀有度筛选

        Returns:
            丹方数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if pill_type:
            conditions.append("pill_type = ?")
            params.append(pill_type)

        if rarity:
            conditions.append("rarity = ?")
            params.append(rarity)

        query = "SELECT * FROM alchemy_recipes"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY rarity DESC, realm_required ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'pill_type': row['pill_type'],
                'rarity': row['rarity'],
                'realm_required': row['realm_required'],
                'materials': json.loads(row['materials']) if row['materials'] else {},
                'effects': json.loads(row['effects']) if row['effects'] else {},
                'base_success_rate': row['base_success_rate'],
                'quality_multipliers': json.loads(row['quality_multipliers']) if row['quality_multipliers'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_alchemy_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取丹方

        Args:
            recipe_id: 丹方ID

        Returns:
            丹方数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alchemy_recipes WHERE id = ?", (recipe_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'pill_type': row['pill_type'],
            'rarity': row['rarity'],
            'realm_required': row['realm_required'],
            'materials': json.loads(row['materials']) if row['materials'] else {},
            'effects': json.loads(row['effects']) if row['effects'] else {},
            'base_success_rate': row['base_success_rate'],
            'quality_multipliers': json.loads(row['quality_multipliers']) if row['quality_multipliers'] else {},
            'created_at': row['created_at']
        }

    def save_alchemy_record(self, player_id: str, record_data: Dict[str, Any]) -> bool:
        """
        保存炼丹记录

        Args:
            player_id: 玩家ID
            record_data: 记录数据字典

        Returns:
            是否保存成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO player_alchemy_records (
                    player_id, recipe_id, recipe_name, success, quality,
                    materials_used, result_item, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                record_data.get('recipe_id', ''),
                record_data.get('recipe_name', ''),
                1 if record_data.get('success', False) else 0,
                record_data.get('quality', ''),
                json.dumps(record_data.get('materials_used', {}), ensure_ascii=False),
                json.dumps(record_data.get('result_item', {}), ensure_ascii=False),
                now
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存炼丹记录失败: {e}")
            return False

    def get_alchemy_records(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取玩家炼丹记录

        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制

        Returns:
            炼丹记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM player_alchemy_records
            WHERE player_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'recipe_id': row['recipe_id'],
                'recipe_name': row['recipe_name'],
                'success': bool(row['success']),
                'quality': row['quality'],
                'materials_used': json.loads(row['materials_used']) if row['materials_used'] else {},
                'result_item': json.loads(row['result_item']) if row['result_item'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    # ==================== 炼器系统操作 ====================

    def save_forging_blueprint(self, blueprint_data: Dict[str, Any]) -> str:
        """
        保存炼器图纸

        Args:
            blueprint_data: 图纸数据字典

        Returns:
            图纸ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        blueprint_id = blueprint_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO forging_blueprints (
                id, name, description, equipment_type, rarity, realm_required,
                materials, base_attributes, special_effects, base_success_rate, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            blueprint_id,
            blueprint_data.get('name', ''),
            blueprint_data.get('description', ''),
            blueprint_data.get('equipment_type', ''),
            blueprint_data.get('rarity', 'common'),
            blueprint_data.get('realm_required', 0),
            json.dumps(blueprint_data.get('materials', {}), ensure_ascii=False),
            json.dumps(blueprint_data.get('base_attributes', {}), ensure_ascii=False),
            json.dumps(blueprint_data.get('special_effects', []), ensure_ascii=False),
            blueprint_data.get('base_success_rate', 0.5),
            now
        ))

        conn.commit()
        return blueprint_id

    def get_forging_blueprints(self, equipment_type: str = None, rarity: str = None) -> List[Dict[str, Any]]:
        """
        获取炼器图纸列表

        Args:
            equipment_type: 装备类型筛选
            rarity: 稀有度筛选

        Returns:
            图纸数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []

        if equipment_type:
            conditions.append("equipment_type = ?")
            params.append(equipment_type)

        if rarity:
            conditions.append("rarity = ?")
            params.append(rarity)

        query = "SELECT * FROM forging_blueprints"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY rarity DESC, realm_required ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'equipment_type': row['equipment_type'],
                'rarity': row['rarity'],
                'realm_required': row['realm_required'],
                'materials': json.loads(row['materials']) if row['materials'] else {},
                'base_attributes': json.loads(row['base_attributes']) if row['base_attributes'] else {},
                'special_effects': json.loads(row['special_effects']) if row['special_effects'] else [],
                'base_success_rate': row['base_success_rate'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_forging_blueprint_by_id(self, blueprint_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取炼器图纸

        Args:
            blueprint_id: 图纸ID

        Returns:
            图纸数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM forging_blueprints WHERE id = ?", (blueprint_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'equipment_type': row['equipment_type'],
            'rarity': row['rarity'],
            'realm_required': row['realm_required'],
            'materials': json.loads(row['materials']) if row['materials'] else {},
            'base_attributes': json.loads(row['base_attributes']) if row['base_attributes'] else {},
            'special_effects': json.loads(row['special_effects']) if row['special_effects'] else [],
            'base_success_rate': row['base_success_rate'],
            'created_at': row['created_at']
        }

    def save_forging_record(self, player_id: str, record_data: Dict[str, Any]) -> bool:
        """
        保存炼器记录

        Args:
            player_id: 玩家ID
            record_data: 记录数据字典

        Returns:
            是否保存成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO player_forging_records (
                    player_id, blueprint_id, blueprint_name, success, quality,
                    materials_used, result_item, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                record_data.get('blueprint_id', ''),
                record_data.get('blueprint_name', ''),
                1 if record_data.get('success', False) else 0,
                record_data.get('quality', ''),
                json.dumps(record_data.get('materials_used', {}), ensure_ascii=False),
                json.dumps(record_data.get('result_item', {}), ensure_ascii=False),
                now
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存炼器记录失败: {e}")
            return False

    def get_forging_records(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取玩家炼器记录

        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制

        Returns:
            炼器记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM player_forging_records
            WHERE player_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'blueprint_id': row['blueprint_id'],
                'blueprint_name': row['blueprint_name'],
                'success': bool(row['success']),
                'quality': row['quality'],
                'materials_used': json.loads(row['materials_used']) if row['materials_used'] else {},
                'result_item': json.loads(row['result_item']) if row['result_item'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    # ==================== 任务系统操作 ====================

    def init_quest_tables(self):
        """创建任务系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建任务模板表 - 存储所有可用的任务定义
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                quest_type TEXT NOT NULL,  -- main:主线, side:支线, daily:日常
                objective_type TEXT NOT NULL,  -- cultivation:修炼, combat:战斗, collection:收集, exploration:探索
                objective_target TEXT NOT NULL,  -- 目标对象（如"修炼次数"、"击败妖兽"、"收集灵草"等）
                objective_count INTEGER NOT NULL DEFAULT 1,  -- 需要完成的数量
                min_level INTEGER DEFAULT 0,  -- 最低境界要求
                max_level INTEGER DEFAULT 99,  -- 最高境界要求
                pre_quest_id TEXT,  -- 前置任务ID
                rewards TEXT NOT NULL,  -- JSON格式的奖励数据
                is_repeatable INTEGER DEFAULT 0,  -- 是否可重复
                created_at TEXT NOT NULL
            )
        """)

        # 创建玩家任务表 - 存储玩家接取的任务进度
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                quest_id TEXT NOT NULL,
                quest_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',  -- active:进行中, completed:已完成, claimed:已领取奖励
                current_progress INTEGER DEFAULT 0,
                target_progress INTEGER NOT NULL,
                accepted_at TEXT NOT NULL,
                completed_at TEXT,
                claimed_at TEXT,
                expires_at TEXT,  -- 日常任务过期时间
                UNIQUE(player_id, quest_id)
            )
        """)

        # 创建任务完成记录表 - 记录已完成的主线任务（用于追踪剧情进度）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                quest_id TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                UNIQUE(player_id, quest_id)
            )
        """)

        # 创建日常任务刷新记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_quest_refresh (
                player_id TEXT PRIMARY KEY,
                last_refresh_date TEXT NOT NULL,
                refresh_count INTEGER DEFAULT 0
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_quests_player ON player_quests(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_quests_status ON player_quests(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quest_templates_type ON quest_templates(quest_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quest_history_player ON quest_history(player_id)
        """)

        conn.commit()

    def save_quest_template(self, quest_data: Dict[str, Any]) -> str:
        """
        保存任务模板

        Args:
            quest_data: 任务数据字典

        Returns:
            任务ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        quest_id = quest_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO quest_templates (
                id, name, description, quest_type, objective_type,
                objective_target, objective_count, min_level, max_level,
                pre_quest_id, rewards, is_repeatable, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quest_id,
            quest_data.get('name', ''),
            quest_data.get('description', ''),
            quest_data.get('quest_type', 'side'),
            quest_data.get('objective_type', 'cultivation'),
            quest_data.get('objective_target', ''),
            quest_data.get('objective_count', 1),
            quest_data.get('min_level', 0),
            quest_data.get('max_level', 99),
            quest_data.get('pre_quest_id'),
            json.dumps(quest_data.get('rewards', {}), ensure_ascii=False),
            1 if quest_data.get('is_repeatable', False) else 0,
            now
        ))

        conn.commit()
        return quest_id

    def get_quest_template(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务模板

        Args:
            quest_id: 任务ID

        Returns:
            任务模板数据，不存在返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM quest_templates WHERE id = ?", (quest_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'quest_type': row['quest_type'],
            'objective_type': row['objective_type'],
            'objective_target': row['objective_target'],
            'objective_count': row['objective_count'],
            'min_level': row['min_level'],
            'max_level': row['max_level'],
            'pre_quest_id': row['pre_quest_id'],
            'rewards': json.loads(row['rewards']) if row['rewards'] else {},
            'is_repeatable': bool(row['is_repeatable']),
            'created_at': row['created_at']
        }

    def get_quest_templates_by_type(self, quest_type: str, player_level: int = None) -> List[Dict[str, Any]]:
        """
        获取指定类型的任务模板

        Args:
            quest_type: 任务类型（main/side/daily）
            player_level: 玩家境界等级，用于筛选

        Returns:
            任务模板列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if player_level is not None:
            cursor.execute("""
                SELECT * FROM quest_templates 
                WHERE quest_type = ? AND min_level <= ? AND max_level >= ?
                ORDER BY min_level ASC
            """, (quest_type, player_level, player_level))
        else:
            cursor.execute("""
                SELECT * FROM quest_templates WHERE quest_type = ? ORDER BY min_level ASC
            """, (quest_type,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'quest_type': row['quest_type'],
                'objective_type': row['objective_type'],
                'objective_target': row['objective_target'],
                'objective_count': row['objective_count'],
                'min_level': row['min_level'],
                'max_level': row['max_level'],
                'pre_quest_id': row['pre_quest_id'],
                'rewards': json.loads(row['rewards']) if row['rewards'] else {},
                'is_repeatable': bool(row['is_repeatable']),
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def accept_quest(self, player_id: str, quest_id: str, quest_type: str, target_progress: int, expires_at: str = None) -> bool:
        """
        玩家接受任务

        Args:
            player_id: 玩家ID
            quest_id: 任务ID
            quest_type: 任务类型
            target_progress: 目标进度
            expires_at: 过期时间（日常任务用）

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO player_quests (
                    player_id, quest_id, quest_type, status, current_progress,
                    target_progress, accepted_at, expires_at
                ) VALUES (?, ?, ?, 'active', 0, ?, ?, ?)
            """, (player_id, quest_id, quest_type, target_progress, now, expires_at))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"接受任务失败: {e}")
            return False

    def get_player_quests(self, player_id: str, status: str = None) -> List[Dict[str, Any]]:
        """
        获取玩家的任务列表

        Args:
            player_id: 玩家ID
            status: 任务状态筛选

        Returns:
            任务列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT * FROM player_quests 
                WHERE player_id = ? AND status = ?
                ORDER BY accepted_at DESC
            """, (player_id, status))
        else:
            cursor.execute("""
                SELECT * FROM player_quests 
                WHERE player_id = ?
                ORDER BY accepted_at DESC
            """, (player_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'quest_id': row['quest_id'],
                'quest_type': row['quest_type'],
                'status': row['status'],
                'current_progress': row['current_progress'],
                'target_progress': row['target_progress'],
                'accepted_at': row['accepted_at'],
                'completed_at': row['completed_at'],
                'claimed_at': row['claimed_at'],
                'expires_at': row['expires_at']
            }
            for row in rows
        ]

    def update_quest_progress(self, player_id: str, quest_id: str, progress: int) -> bool:
        """
        更新任务进度

        Args:
            player_id: 玩家ID
            quest_id: 任务ID
            progress: 当前进度

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE player_quests 
                SET current_progress = ?
                WHERE player_id = ? AND quest_id = ? AND status = 'active'
            """, (progress, player_id, quest_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新任务进度失败: {e}")
            return False

    def complete_quest(self, player_id: str, quest_id: str) -> bool:
        """
        完成任务（标记为可领取奖励）

        Args:
            player_id: 玩家ID
            quest_id: 任务ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE player_quests 
                SET status = 'completed', completed_at = ?
                WHERE player_id = ? AND quest_id = ? AND status = 'active'
            """, (now, player_id, quest_id))

            # 同时记录到历史表
            if cursor.rowcount > 0:
                cursor.execute("""
                    INSERT OR IGNORE INTO quest_history (player_id, quest_id, completed_at)
                    VALUES (?, ?, ?)
                """, (player_id, quest_id, now))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"完成任务失败: {e}")
            return False

    def claim_quest_reward(self, player_id: str, quest_id: str) -> bool:
        """
        领取任务奖励

        Args:
            player_id: 玩家ID
            quest_id: 任务ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE player_quests 
                SET status = 'claimed', claimed_at = ?
                WHERE player_id = ? AND quest_id = ? AND status = 'completed'
            """, (now, player_id, quest_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"领取奖励失败: {e}")
            return False

    def has_completed_quest(self, player_id: str, quest_id: str) -> bool:
        """
        检查玩家是否已完成某任务

        Args:
            player_id: 玩家ID
            quest_id: 任务ID

        Returns:
            是否已完成
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM quest_history 
            WHERE player_id = ? AND quest_id = ?
        """, (player_id, quest_id))

        return cursor.fetchone() is not None

    def get_last_daily_refresh(self, player_id: str) -> Optional[str]:
        """
        获取玩家上次刷新日常任务的时间

        Args:
            player_id: 玩家ID

        Returns:
            上次刷新时间，如果没有返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT last_refresh_date FROM daily_quest_refresh WHERE player_id = ?
        """, (player_id,))

        row = cursor.fetchone()
        return row['last_refresh_date'] if row else None

    def update_daily_refresh(self, player_id: str) -> bool:
        """
        更新日常任务刷新时间

        Args:
            player_id: 玩家ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO daily_quest_refresh (player_id, last_refresh_date, refresh_count)
                VALUES (?, ?, COALESCE((SELECT refresh_count + 1 FROM daily_quest_refresh WHERE player_id = ?), 1))
            """, (player_id, now, player_id))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新日常刷新时间失败: {e}")
            return False

    def abandon_quest(self, player_id: str, quest_id: str) -> bool:
        """
        放弃任务

        Args:
            player_id: 玩家ID
            quest_id: 任务ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM player_quests 
                WHERE player_id = ? AND quest_id = ? AND status = 'active'
            """, (player_id, quest_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"放弃任务失败: {e}")
            return False

    # ==================== 灵兽系统操作 ====================

    def init_pet_tables(self):
        """创建灵兽系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 spirit_pets 表 - 存储玩家拥有的灵兽
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spirit_pets (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                pet_template_id TEXT NOT NULL,
                name TEXT NOT NULL,
                pet_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                exp_to_next INTEGER DEFAULT 100,
                stage INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 0,
                is_battle INTEGER DEFAULT 0,
                
                -- 基础属性
                attack INTEGER DEFAULT 10,
                defense INTEGER DEFAULT 10,
                health INTEGER DEFAULT 100,
                max_health INTEGER DEFAULT 100,
                speed INTEGER DEFAULT 10,
                
                -- 资质属性 (1-100)
                attack_potential INTEGER DEFAULT 50,
                defense_potential INTEGER DEFAULT 50,
                health_potential INTEGER DEFAULT 50,
                speed_potential INTEGER DEFAULT 50,
                
                -- 成长值
                growth_rate REAL DEFAULT 1.0,
                
                -- 亲密度
                intimacy INTEGER DEFAULT 0,
                max_intimacy INTEGER DEFAULT 100,
                
                -- 状态
                status TEXT DEFAULT 'normal',
                
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 创建 pet_skills 表 - 存储灵兽技能
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_skills (
                id TEXT PRIMARY KEY,
                pet_id TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                max_level INTEGER DEFAULT 10,
                damage INTEGER DEFAULT 0,
                effect_type TEXT,
                effect_value REAL DEFAULT 0,
                cooldown INTEGER DEFAULT 0,
                mana_cost INTEGER DEFAULT 0,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES spirit_pets(id) ON DELETE CASCADE
            )
        """)

        # 创建 pet_evolutions 表 - 存储灵兽进化记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_evolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id TEXT NOT NULL,
                from_stage INTEGER NOT NULL,
                to_stage INTEGER NOT NULL,
                from_name TEXT NOT NULL,
                to_name TEXT NOT NULL,
                evolved_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES spirit_pets(id) ON DELETE CASCADE
            )
        """)

        # 创建 pet_catch_records 表 - 存储捕捉记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_catch_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                pet_template_id TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                location TEXT,
                success INTEGER DEFAULT 0,
                catch_at TEXT NOT NULL
            )
        """)

        # 创建 pet_training_records 表 - 存储培养记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id TEXT NOT NULL,
                training_type TEXT NOT NULL,
                attribute_changed TEXT,
                old_value INTEGER,
                new_value INTEGER,
                cost TEXT,
                trained_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES spirit_pets(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_spirit_pets_player ON spirit_pets(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_spirit_pets_active ON spirit_pets(is_active)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pet_skills_pet ON pet_skills(pet_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pet_evolutions_pet ON pet_evolutions(pet_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pet_catch_player ON pet_catch_records(player_id)
        """)

        conn.commit()

    def save_spirit_pet(self, pet_data: Dict[str, Any]) -> str:
        """
        保存灵兽信息

        Args:
            pet_data: 灵兽数据字典

        Returns:
            灵兽ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        pet_id = pet_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO spirit_pets (
                id, player_id, pet_template_id, name, pet_type, level, exp, exp_to_next,
                stage, is_active, is_battle, attack, defense, health, max_health, speed,
                attack_potential, defense_potential, health_potential, speed_potential,
                growth_rate, intimacy, max_intimacy, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pet_id,
            pet_data.get('player_id', ''),
            pet_data.get('pet_template_id', ''),
            pet_data.get('name', ''),
            pet_data.get('pet_type', 'attack'),
            pet_data.get('level', 1),
            pet_data.get('exp', 0),
            pet_data.get('exp_to_next', 100),
            pet_data.get('stage', 1),
            1 if pet_data.get('is_active', False) else 0,
            1 if pet_data.get('is_battle', False) else 0,
            pet_data.get('attack', 10),
            pet_data.get('defense', 10),
            pet_data.get('health', 100),
            pet_data.get('max_health', 100),
            pet_data.get('speed', 10),
            pet_data.get('attack_potential', 50),
            pet_data.get('defense_potential', 50),
            pet_data.get('health_potential', 50),
            pet_data.get('speed_potential', 50),
            pet_data.get('growth_rate', 1.0),
            pet_data.get('intimacy', 0),
            pet_data.get('max_intimacy', 100),
            pet_data.get('status', 'normal'),
            pet_data.get('created_at', now),
            now
        ))

        conn.commit()
        return pet_id

    def get_spirit_pet(self, pet_id: str) -> Optional[Dict[str, Any]]:
        """
        获取灵兽信息

        Args:
            pet_id: 灵兽ID

        Returns:
            灵兽数据字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM spirit_pets WHERE id = ?", (pet_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'player_id': row['player_id'],
            'pet_template_id': row['pet_template_id'],
            'name': row['name'],
            'pet_type': row['pet_type'],
            'level': row['level'],
            'exp': row['exp'],
            'exp_to_next': row['exp_to_next'],
            'stage': row['stage'],
            'is_active': bool(row['is_active']),
            'is_battle': bool(row['is_battle']),
            'attack': row['attack'],
            'defense': row['defense'],
            'health': row['health'],
            'max_health': row['max_health'],
            'speed': row['speed'],
            'attack_potential': row['attack_potential'],
            'defense_potential': row['defense_potential'],
            'health_potential': row['health_potential'],
            'speed_potential': row['speed_potential'],
            'growth_rate': row['growth_rate'],
            'intimacy': row['intimacy'],
            'max_intimacy': row['max_intimacy'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def get_player_spirit_pets(self, player_id: str) -> List[Dict[str, Any]]:
        """
        获取玩家的所有灵兽

        Args:
            player_id: 玩家ID

        Returns:
            灵兽列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM spirit_pets WHERE player_id = ? ORDER BY is_battle DESC, level DESC
        """, (player_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'pet_template_id': row['pet_template_id'],
                'name': row['name'],
                'pet_type': row['pet_type'],
                'level': row['level'],
                'exp': row['exp'],
                'exp_to_next': row['exp_to_next'],
                'stage': row['stage'],
                'is_active': bool(row['is_active']),
                'is_battle': bool(row['is_battle']),
                'attack': row['attack'],
                'defense': row['defense'],
                'health': row['health'],
                'max_health': row['max_health'],
                'speed': row['speed'],
                'attack_potential': row['attack_potential'],
                'defense_potential': row['defense_potential'],
                'health_potential': row['health_potential'],
                'speed_potential': row['speed_potential'],
                'growth_rate': row['growth_rate'],
                'intimacy': row['intimacy'],
                'max_intimacy': row['max_intimacy'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            for row in rows
        ]

    def get_battle_pet(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家出战的灵兽

        Args:
            player_id: 玩家ID

        Returns:
            出战灵兽数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM spirit_pets WHERE player_id = ? AND is_battle = 1 LIMIT 1
        """, (player_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'player_id': row['player_id'],
            'pet_template_id': row['pet_template_id'],
            'name': row['name'],
            'pet_type': row['pet_type'],
            'level': row['level'],
            'exp': row['exp'],
            'exp_to_next': row['exp_to_next'],
            'stage': row['stage'],
            'is_active': bool(row['is_active']),
            'is_battle': bool(row['is_battle']),
            'attack': row['attack'],
            'defense': row['defense'],
            'health': row['health'],
            'max_health': row['max_health'],
            'speed': row['speed'],
            'attack_potential': row['attack_potential'],
            'defense_potential': row['defense_potential'],
            'health_potential': row['health_potential'],
            'speed_potential': row['speed_potential'],
            'growth_rate': row['growth_rate'],
            'intimacy': row['intimacy'],
            'max_intimacy': row['max_intimacy'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def update_pet_battle_status(self, pet_id: str, is_battle: bool) -> bool:
        """
        更新灵兽出战状态

        Args:
            pet_id: 灵兽ID
            is_battle: 是否出战

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE spirit_pets SET is_battle = ?, updated_at = ? WHERE id = ?
            """, (1 if is_battle else 0, now, pet_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新灵兽出战状态失败: {e}")
            return False

    def clear_battle_pet(self, player_id: str) -> bool:
        """
        清除玩家的出战灵兽

        Args:
            player_id: 玩家ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE spirit_pets SET is_battle = 0, updated_at = ? WHERE player_id = ? AND is_battle = 1
            """, (now, player_id))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"清除出战灵兽失败: {e}")
            return False

    def delete_spirit_pet(self, pet_id: str) -> bool:
        """
        删除灵兽

        Args:
            pet_id: 灵兽ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM spirit_pets WHERE id = ?", (pet_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除灵兽失败: {e}")
            return False

    def save_pet_skill(self, skill_data: Dict[str, Any]) -> str:
        """
        保存灵兽技能

        Args:
            skill_data: 技能数据字典

        Returns:
            技能ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        skill_id = skill_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO pet_skills (
                id, pet_id, skill_id, skill_name, skill_type, level, max_level,
                damage, effect_type, effect_value, cooldown, mana_cost, description, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_id,
            skill_data.get('pet_id', ''),
            skill_data.get('skill_id', ''),
            skill_data.get('skill_name', ''),
            skill_data.get('skill_type', 'attack'),
            skill_data.get('level', 1),
            skill_data.get('max_level', 10),
            skill_data.get('damage', 0),
            skill_data.get('effect_type', ''),
            skill_data.get('effect_value', 0),
            skill_data.get('cooldown', 0),
            skill_data.get('mana_cost', 0),
            skill_data.get('description', ''),
            1 if skill_data.get('is_active', True) else 0,
            now
        ))

        conn.commit()
        return skill_id

    def get_pet_skills(self, pet_id: str) -> List[Dict[str, Any]]:
        """
        获取灵兽的所有技能

        Args:
            pet_id: 灵兽ID

        Returns:
            技能列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pet_skills WHERE pet_id = ? ORDER BY level DESC
        """, (pet_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'pet_id': row['pet_id'],
                'skill_id': row['skill_id'],
                'skill_name': row['skill_name'],
                'skill_type': row['skill_type'],
                'level': row['level'],
                'max_level': row['max_level'],
                'damage': row['damage'],
                'effect_type': row['effect_type'],
                'effect_value': row['effect_value'],
                'cooldown': row['cooldown'],
                'mana_cost': row['mana_cost'],
                'description': row['description'],
                'is_active': bool(row['is_active']),
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def update_pet_skill_level(self, skill_id: str, new_level: int) -> bool:
        """
        更新技能等级

        Args:
            skill_id: 技能ID
            new_level: 新等级

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE pet_skills SET level = ? WHERE id = ?
            """, (new_level, skill_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新技能等级失败: {e}")
            return False

    def save_pet_evolution(self, evolution_data: Dict[str, Any]) -> int:
        """
        保存灵兽进化记录

        Args:
            evolution_data: 进化数据字典

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO pet_evolutions (
                pet_id, from_stage, to_stage, from_name, to_name, evolved_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            evolution_data.get('pet_id', ''),
            evolution_data.get('from_stage', 1),
            evolution_data.get('to_stage', 2),
            evolution_data.get('from_name', ''),
            evolution_data.get('to_name', ''),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_pet_evolutions(self, pet_id: str) -> List[Dict[str, Any]]:
        """
        获取灵兽的进化历史

        Args:
            pet_id: 灵兽ID

        Returns:
            进化记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pet_evolutions WHERE pet_id = ? ORDER BY evolved_at ASC
        """, (pet_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'pet_id': row['pet_id'],
                'from_stage': row['from_stage'],
                'to_stage': row['to_stage'],
                'from_name': row['from_name'],
                'to_name': row['to_name'],
                'evolved_at': row['evolved_at']
            }
            for row in rows
        ]

    def save_catch_record(self, record_data: Dict[str, Any]) -> int:
        """
        保存捕捉记录

        Args:
            record_data: 捕捉记录数据

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO pet_catch_records (
                player_id, pet_template_id, pet_name, location, success, catch_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record_data.get('player_id', ''),
            record_data.get('pet_template_id', ''),
            record_data.get('pet_name', ''),
            record_data.get('location', ''),
            1 if record_data.get('success', False) else 0,
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_catch_records(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取玩家的捕捉记录

        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制

        Returns:
            捕捉记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pet_catch_records WHERE player_id = ? ORDER BY catch_at DESC LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'player_id': row['player_id'],
                'pet_template_id': row['pet_template_id'],
                'pet_name': row['pet_name'],
                'location': row['location'],
                'success': bool(row['success']),
                'catch_at': row['catch_at']
            }
            for row in rows
        ]

    def save_training_record(self, record_data: Dict[str, Any]) -> int:
        """
        保存培养记录

        Args:
            record_data: 培养记录数据

        Returns:
            记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO pet_training_records (
                pet_id, training_type, attribute_changed, old_value, new_value, cost, trained_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record_data.get('pet_id', ''),
            record_data.get('training_type', ''),
            record_data.get('attribute_changed', ''),
            record_data.get('old_value', 0),
            record_data.get('new_value', 0),
            json.dumps(record_data.get('cost', {}), ensure_ascii=False),
            now
        ))

        conn.commit()
        return cursor.lastrowid

    def get_training_records(self, pet_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取灵兽的培养记录

        Args:
            pet_id: 灵兽ID
            limit: 返回记录数量限制

        Returns:
            培养记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pet_training_records WHERE pet_id = ? ORDER BY trained_at DESC LIMIT ?
        """, (pet_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'pet_id': row['pet_id'],
                'training_type': row['training_type'],
                'attribute_changed': row['attribute_changed'],
                'old_value': row['old_value'],
                'new_value': row['new_value'],
                'cost': json.loads(row['cost']) if row['cost'] else {},
                'trained_at': row['trained_at']
            }
            for row in rows
        ]

    # ==================== 洞府系统操作 ====================

    def init_cave_tables(self):
        """创建洞府系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 player_caves 表 - 玩家洞府信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_caves (
                id TEXT PRIMARY KEY,
                player_name TEXT NOT NULL UNIQUE,
                cave_name TEXT,
                location_id TEXT NOT NULL,
                cave_level INTEGER DEFAULT 0,
                spirit_array_level INTEGER DEFAULT 0,
                defense_array_level INTEGER DEFAULT 0,
                max_fields INTEGER DEFAULT 2,
                created_at TEXT NOT NULL,
                last_visit TEXT NOT NULL,
                cultivation_bonus REAL DEFAULT 0.0,
                defense_power INTEGER DEFAULT 0,
                spirit_recovery INTEGER DEFAULT 0
            )
        """)

        # 创建 cave_fields 表 - 灵田信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cave_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cave_id TEXT NOT NULL,
                field_index INTEGER NOT NULL,
                crop_id TEXT,
                crop_name TEXT,
                planted_at TEXT,
                growth_days INTEGER DEFAULT 0,
                total_growth_days INTEGER DEFAULT 0,
                stage TEXT DEFAULT 'empty',
                yield_amount INTEGER DEFAULT 0,
                is_fertilized INTEGER DEFAULT 0,
                fertilizer_bonus REAL DEFAULT 0.0,
                FOREIGN KEY (cave_id) REFERENCES player_caves(id) ON DELETE CASCADE
            )
        """)

        # 创建 cave_upgrades 表 - 洞府升级记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cave_upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cave_id TEXT NOT NULL,
                upgrade_type TEXT NOT NULL,
                from_level INTEGER NOT NULL,
                to_level INTEGER NOT NULL,
                cost TEXT NOT NULL,
                upgraded_at TEXT NOT NULL,
                FOREIGN KEY (cave_id) REFERENCES player_caves(id) ON DELETE CASCADE
            )
        """)

        # 创建 cave_harvests 表 - 收获记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cave_harvests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cave_id TEXT NOT NULL,
                field_id INTEGER NOT NULL,
                crop_id TEXT NOT NULL,
                crop_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                quality TEXT DEFAULT '普通',
                harvested_at TEXT NOT NULL,
                FOREIGN KEY (cave_id) REFERENCES player_caves(id) ON DELETE CASCADE,
                FOREIGN KEY (field_id) REFERENCES cave_fields(id) ON DELETE CASCADE
            )
        """)

        # 创建 cave_defense_logs 表 - 护山大阵防御记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cave_defense_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cave_id TEXT NOT NULL,
                enemy_name TEXT NOT NULL,
                enemy_level INTEGER DEFAULT 1,
                defense_result TEXT NOT NULL,
                damage_dealt INTEGER DEFAULT 0,
                damage_taken INTEGER DEFAULT 0,
                defended_at TEXT NOT NULL,
                FOREIGN KEY (cave_id) REFERENCES player_caves(id) ON DELETE CASCADE
            )
        """)

        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_caves_player ON player_caves(player_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_caves_location ON player_caves(location_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fields_cave ON cave_fields(cave_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fields_stage ON cave_fields(stage)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_upgrades_cave ON cave_upgrades(cave_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_harvests_cave ON cave_harvests(cave_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_defense_logs_cave ON cave_defense_logs(cave_id)
        """)

        conn.commit()

    def save_player_cave(self, cave_data: Dict[str, Any]) -> str:
        """
        保存玩家洞府信息

        Args:
            cave_data: 洞府数据字典

        Returns:
            洞府ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cave_id = cave_data.get('id', str(uuid.uuid4()))
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO player_caves (
                id, player_name, cave_name, location_id, cave_level,
                spirit_array_level, defense_array_level, max_fields,
                created_at, last_visit, cultivation_bonus, defense_power, spirit_recovery
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cave_id,
            cave_data.get('player_name', ''),
            cave_data.get('cave_name', '无名洞府'),
            cave_data.get('location_id', 'newbie_village'),
            cave_data.get('cave_level', 0),
            cave_data.get('spirit_array_level', 0),
            cave_data.get('defense_array_level', 0),
            cave_data.get('max_fields', 2),
            cave_data.get('created_at', now),
            now,
            cave_data.get('cultivation_bonus', 0.0),
            cave_data.get('defense_power', 0),
            cave_data.get('spirit_recovery', 0)
        ))

        conn.commit()
        return cave_id

    def get_player_cave(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家洞府信息

        Args:
            player_name: 玩家名称

        Returns:
            洞府数据字典，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM player_caves WHERE player_name = ?
        """, (player_name,))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'player_name': row['player_name'],
            'cave_name': row['cave_name'],
            'location_id': row['location_id'],
            'cave_level': row['cave_level'],
            'spirit_array_level': row['spirit_array_level'],
            'defense_array_level': row['defense_array_level'],
            'max_fields': row['max_fields'],
            'created_at': row['created_at'],
            'last_visit': row['last_visit'],
            'cultivation_bonus': row['cultivation_bonus'],
            'defense_power': row['defense_power'],
            'spirit_recovery': row['spirit_recovery']
        }

    def update_cave_visit(self, cave_id: str) -> bool:
        """
        更新洞府最后访问时间

        Args:
            cave_id: 洞府ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE player_caves SET last_visit = ? WHERE id = ?
            """, (now, cave_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新洞府访问时间失败: {e}")
            return False

    def save_cave_field(self, field_data: Dict[str, Any]) -> int:
        """
        保存灵田信息

        Args:
            field_data: 灵田数据字典

        Returns:
            灵田ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        field_id = field_data.get('id')
        if field_id:
            # 更新现有记录
            cursor.execute("""
                UPDATE cave_fields SET
                    crop_id = ?,
                    crop_name = ?,
                    planted_at = ?,
                    growth_days = ?,
                    total_growth_days = ?,
                    stage = ?,
                    yield_amount = ?,
                    is_fertilized = ?,
                    fertilizer_bonus = ?
                WHERE id = ?
            """, (
                field_data.get('crop_id'),
                field_data.get('crop_name', ''),
                field_data.get('planted_at', ''),
                field_data.get('growth_days', 0),
                field_data.get('total_growth_days', 0),
                field_data.get('stage', 'empty'),
                field_data.get('yield_amount', 0),
                1 if field_data.get('is_fertilized', False) else 0,
                field_data.get('fertilizer_bonus', 0.0),
                field_id
            ))
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO cave_fields (
                    cave_id, field_index, crop_id, crop_name, planted_at,
                    growth_days, total_growth_days, stage, yield_amount,
                    is_fertilized, fertilizer_bonus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                field_data.get('cave_id', ''),
                field_data.get('field_index', 0),
                field_data.get('crop_id'),
                field_data.get('crop_name', ''),
                field_data.get('planted_at', ''),
                field_data.get('growth_days', 0),
                field_data.get('total_growth_days', 0),
                field_data.get('stage', 'empty'),
                field_data.get('yield_amount', 0),
                1 if field_data.get('is_fertilized', False) else 0,
                field_data.get('fertilizer_bonus', 0.0)
            ))
            field_id = cursor.lastrowid

        conn.commit()
        return field_id

    def get_cave_fields(self, cave_id: str) -> List[Dict[str, Any]]:
        """
        获取洞府的所有灵田

        Args:
            cave_id: 洞府ID

        Returns:
            灵田列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM cave_fields WHERE cave_id = ? ORDER BY field_index ASC
        """, (cave_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'cave_id': row['cave_id'],
                'field_index': row['field_index'],
                'crop_id': row['crop_id'],
                'crop_name': row['crop_name'],
                'planted_at': row['planted_at'],
                'growth_days': row['growth_days'],
                'total_growth_days': row['total_growth_days'],
                'stage': row['stage'],
                'yield_amount': row['yield_amount'],
                'is_fertilized': bool(row['is_fertilized']),
                'fertilizer_bonus': row['fertilizer_bonus']
            }
            for row in rows
        ]

    def clear_cave_field(self, field_id: int) -> bool:
        """
        清空灵田（收获后）

        Args:
            field_id: 灵田ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE cave_fields SET
                    crop_id = NULL,
                    crop_name = '',
                    planted_at = '',
                    growth_days = 0,
                    total_growth_days = 0,
                    stage = 'empty',
                    yield_amount = 0,
                    is_fertilized = 0,
                    fertilizer_bonus = 0.0
                WHERE id = ?
            """, (field_id,))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"清空灵田失败: {e}")
            return False

    def record_cave_upgrade(self, cave_id: str, upgrade_type: str,
                           from_level: int, to_level: int, cost: Dict[str, Any]) -> bool:
        """
        记录洞府升级

        Args:
            cave_id: 洞府ID
            upgrade_type: 升级类型（cave/spirit_array/defense_array）
            from_level: 原等级
            to_level: 新等级
            cost: 消耗

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO cave_upgrades
                (cave_id, upgrade_type, from_level, to_level, cost, upgraded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cave_id, upgrade_type, from_level, to_level,
                  json.dumps(cost, ensure_ascii=False), now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录洞府升级失败: {e}")
            return False

    def record_cave_harvest(self, cave_id: str, field_id: int,
                           crop_id: str, crop_name: str, quantity: int,
                           quality: str = '普通') -> bool:
        """
        记录收获

        Args:
            cave_id: 洞府ID
            field_id: 灵田ID
            crop_id: 作物ID
            crop_name: 作物名称
            quantity: 数量
            quality: 品质

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO cave_harvests
                (cave_id, field_id, crop_id, crop_name, quantity, quality, harvested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cave_id, field_id, crop_id, crop_name, quantity, quality, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录收获失败: {e}")
            return False

    def record_defense_log(self, cave_id: str, enemy_name: str,
                          enemy_level: int, defense_result: str,
                          damage_dealt: int = 0, damage_taken: int = 0) -> bool:
        """
        记录护山大阵防御日志

        Args:
            cave_id: 洞府ID
            enemy_name: 敌人名称
            enemy_level: 敌人等级
            defense_result: 防御结果（success/failed）
            damage_dealt: 造成伤害
            damage_taken: 受到伤害

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO cave_defense_logs
                (cave_id, enemy_name, enemy_level, defense_result, damage_dealt, damage_taken, defended_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cave_id, enemy_name, enemy_level, defense_result,
                  damage_dealt, damage_taken, now))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录防御日志失败: {e}")
            return False

    def get_cave_harvest_history(self, cave_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取收获历史

        Args:
            cave_id: 洞府ID
            limit: 返回记录数量限制

        Returns:
            收获记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM cave_harvests
            WHERE cave_id = ?
            ORDER BY harvested_at DESC
            LIMIT ?
        """, (cave_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'cave_id': row['cave_id'],
                'field_id': row['field_id'],
                'crop_id': row['crop_id'],
                'crop_name': row['crop_name'],
                'quantity': row['quantity'],
                'quality': row['quality'],
                'harvested_at': row['harvested_at']
            }
            for row in rows
        ]

    def get_defense_logs(self, cave_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取防御日志

        Args:
            cave_id: 洞府ID
            limit: 返回记录数量限制

        Returns:
            防御记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM cave_defense_logs
            WHERE cave_id = ?
            ORDER BY defended_at DESC
            LIMIT ?
        """, (cave_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'cave_id': row['cave_id'],
                'enemy_name': row['enemy_name'],
                'enemy_level': row['enemy_level'],
                'defense_result': row['defense_result'],
                'damage_dealt': row['damage_dealt'],
                'damage_taken': row['damage_taken'],
                'defended_at': row['defended_at']
            }
            for row in rows
        ]

    # ==================== 成就系统操作 ====================

    def init_achievement_tables(self):
        """创建成就系统相关的数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 achievements 表 - 存储成就模板
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                tier TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_target TEXT NOT NULL,
                condition_value INTEGER DEFAULT 1,
                icon TEXT DEFAULT '🏆',
                hidden INTEGER DEFAULT 0,
                pre_achievement_id TEXT,
                rewards TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # 创建 player_achievements 表 - 存储玩家成就进度
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                target_value INTEGER DEFAULT 1,
                status TEXT DEFAULT 'locked',
                unlocked_at TEXT,
                claimed_at TEXT,
                UNIQUE(player_id, achievement_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
            )
        """)

        # 创建 achievement_stats 表 - 存储玩家成就统计
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievement_stats (
                player_id TEXT PRIMARY KEY,
                total_achievements INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                bronze_count INTEGER DEFAULT 0,
                silver_count INTEGER DEFAULT 0,
                gold_count INTEGER DEFAULT 0,
                diamond_count INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)

        # 创建 achievement_history 表 - 存储成就解锁历史
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievement_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                tier TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                unlocked_at TEXT NOT NULL
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_achievements_player ON player_achievements(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_achievements_status ON player_achievements(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_achievement_history_player ON achievement_history(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category)
        """)

        conn.commit()

    def save_achievement_template(self, achievement_data: Dict[str, Any]) -> str:
        """
        保存成就模板

        Args:
            achievement_data: 成就数据字典

        Returns:
            成就ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO achievements (
                id, name, description, category, tier, condition_type,
                condition_target, condition_value, icon, hidden,
                pre_achievement_id, rewards, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            achievement_data.get('id', ''),
            achievement_data.get('name', ''),
            achievement_data.get('description', ''),
            achievement_data.get('category', ''),
            achievement_data.get('tier', ''),
            achievement_data.get('condition_type', ''),
            achievement_data.get('condition_target', ''),
            achievement_data.get('condition_value', 1),
            achievement_data.get('icon', '🏆'),
            1 if achievement_data.get('hidden', False) else 0,
            achievement_data.get('pre_achievement_id'),
            json.dumps(achievement_data.get('rewards', {}), ensure_ascii=False),
            now
        ))

        conn.commit()
        return achievement_data.get('id', '')

    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """
        获取所有成就模板

        Returns:
            成就模板列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM achievements ORDER BY category, tier, id
        """)

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'tier': row['tier'],
                'condition_type': row['condition_type'],
                'condition_target': row['condition_target'],
                'condition_value': row['condition_value'],
                'icon': row['icon'],
                'hidden': bool(row['hidden']),
                'pre_achievement_id': row['pre_achievement_id'],
                'rewards': json.loads(row['rewards']) if row['rewards'] else {},
                'created_at': row['created_at']
            }
            for row in rows
        ]

    def get_achievement_by_id(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取成就模板

        Args:
            achievement_id: 成就ID

        Returns:
            成就模板数据，如果不存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM achievements WHERE id = ?
        """, (achievement_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'category': row['category'],
            'tier': row['tier'],
            'condition_type': row['condition_type'],
            'condition_target': row['condition_target'],
            'condition_value': row['condition_value'],
            'icon': row['icon'],
            'hidden': bool(row['hidden']),
            'pre_achievement_id': row['pre_achievement_id'],
            'rewards': json.loads(row['rewards']) if row['rewards'] else {},
            'created_at': row['created_at']
        }

    def init_player_achievements(self, player_id: str, achievements: List[Dict[str, Any]]) -> bool:
        """
        初始化玩家的成就进度

        Args:
            player_id: 玩家ID
            achievements: 成就模板列表

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            for achievement in achievements:
                cursor.execute("""
                    INSERT OR IGNORE INTO player_achievements
                    (player_id, achievement_id, progress, target_value, status)
                    VALUES (?, ?, 0, ?, 'locked')
                """, (player_id, achievement['id'], achievement['condition_value']))

            # 初始化成就统计
            cursor.execute("""
                INSERT OR IGNORE INTO achievement_stats
                (player_id, total_achievements, total_points, last_updated)
                VALUES (?, 0, 0, ?)
            """, (player_id, datetime.now().isoformat()))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"初始化玩家成就失败: {e}")
            return False

    def update_achievement_progress(self, player_id: str, achievement_id: str,
                                    progress: int, auto_unlock: bool = True) -> Dict[str, Any]:
        """
        更新成就进度

        Args:
            player_id: 玩家ID
            achievement_id: 成就ID
            progress: 当前进度
            auto_unlock: 是否自动解锁

        Returns:
            更新结果 {'updated': bool, 'unlocked': bool}
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取当前进度和目标值
            cursor.execute("""
                SELECT progress, target_value, status FROM player_achievements
                WHERE player_id = ? AND achievement_id = ?
            """, (player_id, achievement_id))

            row = cursor.fetchone()
            if row is None:
                return {'updated': False, 'unlocked': False}

            current_progress = row['progress']
            target_value = row['target_value']
            status = row['status']

            if status == 'claimed':
                return {'updated': False, 'unlocked': False}

            # 更新进度
            new_progress = max(current_progress, progress)
            new_status = status

            # 检查是否达成
            unlocked = False
            if auto_unlock and new_progress >= target_value and status == 'locked':
                new_status = 'unlocked'
                unlocked = True
                now = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE player_achievements
                    SET progress = ?, status = ?, unlocked_at = ?
                    WHERE player_id = ? AND achievement_id = ?
                """, (new_progress, new_status, now, player_id, achievement_id))
            else:
                cursor.execute("""
                    UPDATE player_achievements
                    SET progress = ?
                    WHERE player_id = ? AND achievement_id = ?
                """, (new_progress, player_id, achievement_id))

            conn.commit()
            return {'updated': True, 'unlocked': unlocked}
        except sqlite3.Error as e:
            print(f"更新成就进度失败: {e}")
            return {'updated': False, 'unlocked': False}

    def unlock_achievement(self, player_id: str, achievement_id: str) -> bool:
        """
        解锁成就

        Args:
            player_id: 玩家ID
            achievement_id: 成就ID

        Returns:
            是否成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE player_achievements
                SET status = 'unlocked', progress = target_value, unlocked_at = ?
                WHERE player_id = ? AND achievement_id = ? AND status != 'claimed'
            """, (now, player_id, achievement_id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"解锁成就失败: {e}")
            return False

    def claim_achievement_reward(self, player_id: str, achievement_id: str) -> Dict[str, Any]:
        """
        领取成就奖励

        Args:
            player_id: 玩家ID
            achievement_id: 成就ID

        Returns:
            领取结果 {'success': bool, 'rewards': dict}
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 检查成就状态
            cursor.execute("""
                SELECT status FROM player_achievements
                WHERE player_id = ? AND achievement_id = ?
            """, (player_id, achievement_id))

            row = cursor.fetchone()
            if row is None:
                return {'success': False, 'rewards': None, 'message': '成就不存在'}

            if row['status'] == 'locked':
                return {'success': False, 'rewards': None, 'message': '成就未解锁'}

            if row['status'] == 'claimed':
                return {'success': False, 'rewards': None, 'message': '奖励已领取'}

            # 获取奖励信息
            cursor.execute("""
                SELECT rewards, name, tier FROM achievements WHERE id = ?
            """, (achievement_id,))

            ach_row = cursor.fetchone()
            if ach_row is None:
                return {'success': False, 'rewards': None, 'message': '成就模板不存在'}

            rewards = json.loads(ach_row['rewards']) if ach_row['rewards'] else {}
            achievement_name = ach_row['name']
            tier = ach_row['tier']

            # 更新状态为已领取
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE player_achievements
                SET status = 'claimed', claimed_at = ?
                WHERE player_id = ? AND achievement_id = ?
            """, (now, player_id, achievement_id))

            # 记录历史
            points = {'bronze': 10, 'silver': 25, 'gold': 50, 'diamond': 100}.get(tier, 0)
            cursor.execute("""
                INSERT INTO achievement_history
                (player_id, achievement_id, achievement_name, tier, points, unlocked_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (player_id, achievement_id, achievement_name, tier, points, now))

            # 更新统计
            cursor.execute("""
                UPDATE achievement_stats
                SET total_achievements = total_achievements + 1,
                    total_points = total_points + ?,
                    {}_count = {}_count + 1,
                    last_updated = ?
                WHERE player_id = ?
            """.format(tier, tier), (points, now, player_id))

            conn.commit()
            return {'success': True, 'rewards': rewards}
        except sqlite3.Error as e:
            print(f"领取成就奖励失败: {e}")
            return {'success': False, 'rewards': None, 'message': str(e)}

    def get_player_achievements(self, player_id: str, status: str = None) -> List[Dict[str, Any]]:
        """
        获取玩家成就列表

        Args:
            player_id: 玩家ID
            status: 状态筛选（locked/unlocked/claimed）

        Returns:
            成就列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT pa.*, a.name, a.description, a.category, a.tier,
                       a.icon, a.hidden, a.pre_achievement_id, a.rewards
                FROM player_achievements pa
                JOIN achievements a ON pa.achievement_id = a.id
                WHERE pa.player_id = ? AND pa.status = ?
                ORDER BY a.category, a.tier, a.id
            """, (player_id, status))
        else:
            cursor.execute("""
                SELECT pa.*, a.name, a.description, a.category, a.tier,
                       a.icon, a.hidden, a.pre_achievement_id, a.rewards
                FROM player_achievements pa
                JOIN achievements a ON pa.achievement_id = a.id
                WHERE pa.player_id = ?
                ORDER BY a.category, a.tier, a.id
            """, (player_id,))

        rows = cursor.fetchall()
        return [
            {
                'id': row['achievement_id'],
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'tier': row['tier'],
                'icon': row['icon'],
                'hidden': bool(row['hidden']),
                'pre_achievement_id': row['pre_achievement_id'],
                'progress': row['progress'],
                'target_value': row['target_value'],
                'status': row['status'],
                'unlocked_at': row['unlocked_at'],
                'claimed_at': row['claimed_at'],
                'rewards': json.loads(row['rewards']) if row['rewards'] else {}
            }
            for row in rows
        ]

    def get_player_achievement_stats(self, player_id: str) -> Dict[str, Any]:
        """
        获取玩家成就统计

        Args:
            player_id: 玩家ID

        Returns:
            成就统计数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM achievement_stats WHERE player_id = ?
        """, (player_id,))

        row = cursor.fetchone()
        if row is None:
            return {
                'total_achievements': 0,
                'total_points': 0,
                'bronze_count': 0,
                'silver_count': 0,
                'gold_count': 0,
                'diamond_count': 0
            }

        return {
            'total_achievements': row['total_achievements'],
            'total_points': row['total_points'],
            'bronze_count': row['bronze_count'],
            'silver_count': row['silver_count'],
            'gold_count': row['gold_count'],
            'diamond_count': row['diamond_count'],
            'last_updated': row['last_updated']
        }

    def get_achievement_history(self, player_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取成就解锁历史

        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制

        Returns:
            成就历史列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM achievement_history
            WHERE player_id = ?
            ORDER BY unlocked_at DESC
            LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'achievement_id': row['achievement_id'],
                'achievement_name': row['achievement_name'],
                'tier': row['tier'],
                'points': row['points'],
                'unlocked_at': row['unlocked_at']
            }
            for row in rows
        ]

    def get_recent_unlocked_achievements(self, player_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取最近解锁的成就

        Args:
            player_id: 玩家ID
            limit: 返回记录数量限制

        Returns:
            最近解锁的成就列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pa.*, a.name, a.description, a.category, a.tier, a.icon
            FROM player_achievements pa
            JOIN achievements a ON pa.achievement_id = a.id
            WHERE pa.player_id = ? AND pa.status IN ('unlocked', 'claimed')
            ORDER BY pa.unlocked_at DESC
            LIMIT ?
        """, (player_id, limit))

        rows = cursor.fetchall()
        return [
            {
                'id': row['achievement_id'],
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'tier': row['tier'],
                'icon': row['icon'],
                'status': row['status'],
                'unlocked_at': row['unlocked_at']
            }
            for row in rows
        ]

    def has_unclaimed_achievements(self, player_id: str) -> bool:
        """
        检查是否有未领取奖励的成就

        Args:
            player_id: 玩家ID

        Returns:
            是否有未领取的成就
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM player_achievements
            WHERE player_id = ? AND status = 'unlocked'
        """, (player_id,))

        row = cursor.fetchone()
        return row['count'] > 0
