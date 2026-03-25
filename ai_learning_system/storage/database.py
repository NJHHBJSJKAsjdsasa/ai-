import sqlite3
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import Memory


class Database:
    """SQLite 数据库管理类"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认为 data/memories.db
        """
        if db_path is None:
            # 获取当前文件所在目录的上级目录，然后指向 data/memories.db
            current_dir = Path(__file__).parent
            db_path = current_dir / "data" / "memories.db"

        self.db_path = Path(db_path)
        # 确保数据目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            # 启用外键支持
            self._connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂，使查询结果可以通过列名访问
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False

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
        保存生成的NPC

        Args:
            npc_data: NPC数据字典，包含 name, surname, gender, age, realm_level 等字段

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

        cursor.execute("""
            INSERT OR REPLACE INTO generated_npcs (
                id, name, surname, full_name, gender, age, realm_level,
                occupation, personality, appearance, catchphrase, story,
                location, favor, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            npc_id,
            npc_data.get('name', ''),
            npc_data.get('surname', ''),
            npc_data.get('full_name', ''),
            npc_data.get('gender', ''),
            npc_data.get('age', 0),
            npc_data.get('realm_level', ''),
            npc_data.get('occupation', ''),
            npc_data.get('personality', ''),
            npc_data.get('appearance', ''),
            npc_data.get('catchphrase', ''),
            npc_data.get('story', ''),
            npc_data.get('location', ''),
            favor,
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
        获取某地图的NPC

        Args:
            location: 地图名称或ID

        Returns:
            NPC数据字典列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM generated_npcs WHERE location = ? ORDER BY created_at DESC
        """, (location,))

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
