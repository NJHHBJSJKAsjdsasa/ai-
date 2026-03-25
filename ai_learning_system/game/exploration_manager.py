"""
探索管理器模块
实现按需生成策略和探索功能
"""

import random
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.generator import (
    InfiniteGenerator, GeneratedMap, GeneratedNPC, GeneratedItem, GeneratedMonster,
    MapType, NPCOccupation, NPCPersonality
)
from game.world import World, GeneratedLocation
from storage.database import Database


@dataclass
class ExplorationResult:
    """探索结果数据类"""
    success: bool = False
    message: str = ""
    discovered_location: Optional[GeneratedLocation] = None
    discovered_npcs: List[GeneratedNPC] = field(default_factory=list)
    discovered_items: List[GeneratedItem] = field(default_factory=list)
    discovered_monsters: List[GeneratedMonster] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'discovered_location': self.discovered_location.to_dict() if self.discovered_location else None,
            'discovered_npcs': [npc.to_dict() for npc in self.discovered_npcs],
            'discovered_items': [item.to_dict() for item in self.discovered_items],
            'discovered_monsters': [monster.to_dict() for monster in self.discovered_monsters],
            'events': self.events,
        }


class ExplorationManager:
    """
    探索管理器类
    管理探索逻辑、按需生成、后台预生成
    """
    
    def __init__(self, world: World, db: Database = None, use_llm: bool = True):
        """
        初始化探索管理器
        
        Args:
            world: 世界实例
            db: 数据库实例
            use_llm: 是否使用LLM生成描述
        """
        self.world = world
        self.db = db or Database()
        self.generator = InfiniteGenerator(use_llm=use_llm)
        
        # 缓存机制
        self._location_cache: Dict[str, GeneratedLocation] = {}
        self._npc_cache: Dict[str, GeneratedNPC] = {}
        self._cache_lock = threading.Lock()
        
        # 预生成线程
        self._pregen_thread: Optional[threading.Thread] = None
        self._pregen_stop_event = threading.Event()
        self._pregen_queue: List[str] = []
        
        # 探索冷却（秒）
        self._exploration_cooldown = 5
        self._last_exploration_time: Dict[str, float] = {}
        
        # 初始化数据库表
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            self.db.init_generated_tables()
        except Exception as e:
            print(f"初始化数据库表时出错: {e}")
    
    # ==================== 探索功能 ====================
    
    def explore(self, player_location: str, player_realm_level: int = 0) -> ExplorationResult:
        """
        探索新区域
        
        Args:
            player_location: 玩家当前位置
            player_realm_level: 玩家修为等级
            
        Returns:
            探索结果
        """
        result = ExplorationResult()
        
        # 检查冷却
        current_time = time.time()
        last_time = self._last_exploration_time.get(player_location, 0)
        if current_time - last_time < self._exploration_cooldown:
            result.message = f"探索冷却中，请等待 {int(self._exploration_cooldown - (current_time - last_time))} 秒"
            return result
        
        # 更新探索时间
        self._last_exploration_time[player_location] = current_time
        
        # 获取当前地点
        current_loc = self.world.get_location(player_location)
        if not current_loc:
            result.message = "当前位置无效"
            return result
        
        # 探索事件概率
        exploration_events = [
            ("发现新区域", 0.3),
            ("遇到NPC", 0.25),
            ("发现物品", 0.2),
            ("遭遇妖兽", 0.15),
            ("一无所获", 0.1),
        ]
        
        event = random.choices(
            [e[0] for e in exploration_events],
            weights=[e[1] for e in exploration_events]
        )[0]
        
        result.events.append(event)
        
        if event == "发现新区域":
            # 生成新地图
            new_location = self._generate_new_location(player_location, player_realm_level)
            if new_location:
                result.success = True
                result.discovered_location = new_location
                result.message = f"你发现了一处新的区域：{new_location.name}！"
                
                # 为新地点生成内容
                content = self._generate_location_content(new_location, player_realm_level)
                result.discovered_npcs = content.get('npcs', [])
                result.discovered_monsters = content.get('monsters', [])
                result.discovered_items = content.get('items', [])
                
                # 触发后台预生成
                self._trigger_pregeneration(new_location.name)
            else:
                result.message = "你探索了一番，但没有发现新的区域。"
                
        elif event == "遇到NPC":
            # 生成NPC
            npc = self.generator.generate_npc(location=player_location)
            self._save_npc(npc)
            result.success = True
            result.discovered_npcs.append(npc)
            result.message = f"你遇到了一位修仙者：{npc.full_name}"
            
        elif event == "发现物品":
            # 生成物品
            item = self.generator.generate_item()
            self._save_item(item)
            result.success = True
            result.discovered_items.append(item)
            result.message = f"你发现了一件物品：{item.name}"
            
        elif event == "遭遇妖兽":
            # 生成妖兽
            monster_level = max(1, player_realm_level + random.randint(-1, 2))
            monster = self.generator.generate_monster(level=monster_level, location=player_location)
            self._save_monster(monster)
            result.success = True
            result.discovered_monsters.append(monster)
            result.message = f"你遭遇了一只妖兽：{monster.name}！"
            
        else:  # 一无所获
            result.message = "你仔细探索了周围，但没有特别的发现。"
        
        return result
    
    def _generate_new_location(self, connected_to: str, player_realm_level: int) -> Optional[GeneratedLocation]:
        """
        生成新地点
        
        Args:
            connected_to: 连接的现有地点
            player_realm_level: 玩家修为等级
            
        Returns:
            生成的新地点
        """
        # 随机选择地图类型
        map_type = random.choice(list(MapType))
        
        # 根据玩家修为确定地图等级
        target_level = max(1, min(9, player_realm_level + random.randint(-1, 1)))
        
        # 生成地图
        generated_map = self.generator.generate_map(
            map_type=map_type,
            target_level=target_level,
            connected_location=connected_to
        )
        
        # 检查是否已存在同名地点
        if generated_map.name in self.world.locations:
            # 添加编号避免重复
            base_name = generated_map.name
            for i in range(2, 100):
                new_name = f"{base_name}{i}"
                if new_name not in self.world.locations:
                    generated_map.name = new_name
                    break
        
        # 创建GeneratedLocation对象
        gen_loc = GeneratedLocation(
            id=generated_map.id,
            name=generated_map.name,
            description=generated_map.description,
            realm_required=max(0, target_level - 1),
            map_type=generated_map.map_type.value,
            level=generated_map.level,
            size=generated_map.size,
            history=generated_map.history,
            environment=generated_map.environment,
            connections=[connected_to],
        )
        
        # 建立双向连接
        self.world.connect_locations(connected_to, gen_loc.name)
        
        # 保存到世界和数据库
        self.world.add_generated_location(gen_loc)
        
        # 添加到缓存
        with self._cache_lock:
            self._location_cache[gen_loc.name] = gen_loc
        
        return gen_loc
    
    def _generate_location_content(self, location: GeneratedLocation, player_realm_level: int) -> Dict[str, Any]:
        """
        为地点生成内容（NPC、妖兽、物品）
        
        Args:
            location: 地点对象
            player_realm_level: 玩家修为等级
            
        Returns:
            生成的内容字典
        """
        content = {
            'npcs': [],
            'monsters': [],
            'items': [],
        }
        
        # 生成NPC
        npc_count = random.randint(2, 5)
        for _ in range(npc_count):
            npc = self.generator.generate_npc(
                location=location.name,
                target_realm=self.generator.generate_realm_level(player_realm_level)
            )
            self._save_npc(npc)
            content['npcs'].append(npc)
        
        # 更新地点的NPC列表
        location.npcs = [npc.id for npc in content['npcs']]
        
        # 生成妖兽（根据地点等级）
        if location.level >= 2:
            monster_count = random.randint(0, min(3, location.level))
            for _ in range(monster_count):
                monster = self.generator.generate_monster(
                    level=random.randint(location.level, location.level + 3),
                    location=location.name
                )
                self._save_monster(monster)
                content['monsters'].append(monster)
            
            # 更新地点的妖兽列表
            location.monsters = [m.id for m in content['monsters']]
        
        # 生成物品
        item_count = random.randint(1, 4)
        for _ in range(item_count):
            item = self.generator.generate_item()
            self._save_item(item)
            content['items'].append(item)
        
        # 更新地点的物品列表
        location.items = [item.id for item in content['items']]
        
        # 保存更新后的地点
        self.world.add_generated_location(location)
        
        return content
    
    def _save_npc(self, npc: GeneratedNPC):
        """保存NPC到数据库"""
        try:
            self.db.save_generated_npc(npc.to_dict())
            with self._cache_lock:
                self._npc_cache[npc.id] = npc
        except Exception as e:
            print(f"保存NPC时出错: {e}")
    
    def _save_item(self, item: GeneratedItem):
        """保存物品到数据库"""
        try:
            self.db.save_generated_item(item.to_dict())
        except Exception as e:
            print(f"保存物品时出错: {e}")
    
    def _save_monster(self, monster: GeneratedMonster):
        """保存妖兽到数据库"""
        try:
            self.db.save_generated_monster(monster.to_dict())
        except Exception as e:
            print(f"保存妖兽时出错: {e}")
    
    # ==================== 后台预生成 ====================
    
    def _trigger_pregeneration(self, location_name: str):
        """
        触发后台预生成
        
        Args:
            location_name: 触发预生成的地点
        """
        # 将地点添加到预生成队列
        if location_name not in self._pregen_queue:
            self._pregen_queue.append(location_name)
        
        # 启动预生成线程（如果未运行）
        if self._pregen_thread is None or not self._pregen_thread.is_alive():
            self._pregen_stop_event.clear()
            self._pregen_thread = threading.Thread(target=self._pregeneration_worker)
            self._pregen_thread.daemon = True
            self._pregen_thread.start()
    
    def _pregeneration_worker(self):
        """预生成工作线程"""
        while not self._pregen_stop_event.is_set() and self._pregen_queue:
            location_name = self._pregen_queue.pop(0)
            
            try:
                # 预生成相邻区域（1-2个）
                pregen_count = random.randint(1, 2)
                for _ in range(pregen_count):
                    # 检查是否已存在足够的连接
                    location = self.world.get_location(location_name)
                    if location and len(location.connections) >= 4:
                        break
                    
                    # 获取地点等级
                    gen_loc = self.world.get_generated_location(location_name)
                    if gen_loc:
                        # 生成新地点
                        self._generate_new_location(
                            location_name,
                            gen_loc.realm_required
                        )
                    
                    # 短暂休眠避免占用过多资源
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"预生成时出错: {e}")
            
            # 队列为空时退出
            if not self._pregen_queue:
                break
    
    def stop_pregeneration(self):
        """停止后台预生成"""
        self._pregen_stop_event.set()
        if self._pregen_thread and self._pregen_thread.is_alive():
            self._pregen_thread.join(timeout=2)
    
    # ==================== 缓存管理 ====================
    
    def get_cached_location(self, name: str) -> Optional[GeneratedLocation]:
        """从缓存获取地点"""
        with self._cache_lock:
            return self._location_cache.get(name)
    
    def get_cached_npc(self, npc_id: str) -> Optional[GeneratedNPC]:
        """从缓存获取NPC"""
        with self._cache_lock:
            return self._npc_cache.get(npc_id)
    
    def clear_cache(self):
        """清空缓存"""
        with self._cache_lock:
            self._location_cache.clear()
            self._npc_cache.clear()
    
    # ==================== 便捷方法 ====================
    
    def get_explorable_locations(self, current_location: str, realm_level: int) -> List[str]:
        """
        获取可探索的地点列表
        
        Args:
            current_location: 当前位置
            realm_level: 修为等级
            
        Returns:
            可探索的地点名称列表
        """
        return self.world.get_accessible_locations(current_location, realm_level)
    
    def format_exploration_result(self, result: ExplorationResult) -> str:
        """
        格式化探索结果为字符串
        
        Args:
            result: 探索结果
            
        Returns:
            格式化后的字符串
        """
        lines = []
        lines.append("=" * 50)
        lines.append("🔍 探索结果")
        lines.append("=" * 50)
        lines.append("")
        lines.append(result.message)
        lines.append("")
        
        if result.discovered_location:
            loc = result.discovered_location
            lines.append(f"📍 发现新区域: {loc.name}")
            lines.append(f"   类型: {loc.map_type} | 等级: {loc.level} | 规模: {loc.size}")
            lines.append(f"   {loc.description[:60]}...")
            lines.append("")
        
        if result.discovered_npcs:
            lines.append(f"👥 遇到NPC ({len(result.discovered_npcs)}人):")
            for npc in result.discovered_npcs:
                lines.append(f"   • {npc.full_name} - {npc.occupation.value} ({npc.realm_level})")
            lines.append("")
        
        if result.discovered_monsters:
            lines.append(f"👹 遭遇妖兽 ({len(result.discovered_monsters)}只):")
            for monster in result.discovered_monsters:
                lines.append(f"   • {monster.name} - 等级{monster.level} ({monster.realm_level})")
            lines.append("")
        
        if result.discovered_items:
            lines.append(f"📦 发现物品 ({len(result.discovered_items)}件):")
            for item in result.discovered_items:
                lines.append(f"   • {item.name} - {item.rarity.value}")
            lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


# 全局探索管理器实例
_default_exploration_manager: Optional[ExplorationManager] = None


def get_exploration_manager(world: World = None, use_llm: bool = True) -> ExplorationManager:
    """
    获取默认的探索管理器实例
    
    Args:
        world: 世界实例
        use_llm: 是否使用LLM
        
    Returns:
        ExplorationManager实例
    """
    global _default_exploration_manager
    if _default_exploration_manager is None:
        if world is None:
            world = World()
        _default_exploration_manager = ExplorationManager(world, use_llm=use_llm)
    return _default_exploration_manager


# 便捷函数
def explore(player_location: str, player_realm_level: int = 0, world: World = None) -> ExplorationResult:
    """
    探索新区域（便捷函数）
    
    Args:
        player_location: 玩家当前位置
        player_realm_level: 玩家修为等级
        world: 世界实例
        
    Returns:
        探索结果
    """
    manager = get_exploration_manager(world)
    return manager.explore(player_location, player_realm_level)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("探索管理器测试")
    print("=" * 60)
    
    # 创建世界和探索管理器
    world = World()
    manager = ExplorationManager(world, use_llm=False)
    
    print("\n--- 测试探索功能 ---")
    
    # 模拟多次探索
    for i in range(5):
        print(f"\n第 {i+1} 次探索:")
        result = manager.explore("新手村", player_realm_level=0)
        print(manager.format_exploration_result(result))
        
        # 短暂延迟模拟玩家操作间隔
        time.sleep(0.5)
    
    print("\n--- 测试预生成功能 ---")
    
    # 等待预生成完成
    time.sleep(2)
    
    # 查看生成的地点
    generated_locs = world.get_all_generated_locations()
    print(f"\n已生成 {len(generated_locs)} 个新地点:")
    for loc in generated_locs[:5]:  # 只显示前5个
        print(f"  • {loc.name} ({loc.map_type}) - 等级{loc.level}")
        print(f"    连接: {', '.join(loc.connections)}")
    
    # 停止预生成线程
    manager.stop_pregeneration()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
