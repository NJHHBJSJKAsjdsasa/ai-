"""
地图处理器类

处理与地图、移动、位置相关的命令。
"""

from typing import TYPE_CHECKING

from .base_handler import BaseHandler
from utils.colors import Color, green
from config import get_realm_info

if TYPE_CHECKING:
    from ..cli import CLI


class MapHandler(BaseHandler):
    """
    地图处理器类
    
    处理与地图、移动、位置相关的命令。
    """
    
    def __init__(self, cli: 'CLI'):
        """
        初始化地图处理器
        
        Args:
            cli: CLI 实例
        """
        super().__init__(cli)
    
    def _handle_move(self, location_name: str):
        """处理移动命令"""
        if not self.world or not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        if not location_name:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要前往的地点")
            print(f"  可用命令: /前往 <地点名>")
            return
        
        # 检查是否可以进入
        if not self.world.can_enter(location_name, self.player.stats.realm_level):
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 境界不足，无法进入{location_name}")
            realm_info = self.world.get_location(location_name)
            if realm_info:
                required_realm = get_realm_info(realm_info.realm_required)
                if required_realm:
                    print(f"  需要境界: {required_realm.name}")
            return
        
        # 检查是否可以从当前位置到达
        accessible = self.world.get_accessible_locations(self.player.stats.location, self.player.stats.realm_level)
        if location_name not in accessible:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 无法直接前往{location_name}")
            print(f"  当前可前往: {', '.join(accessible) if accessible else '无'}")
            return
        
        # 移动
        old_location = self.player.stats.location
        self.player.stats.location = location_name
        
        # 消耗时间
        self.player.advance_time(1)
        
        print(f"\n{self.colorize('🚶 移动', Color.BOLD_CYAN)}: {old_location} → {location_name}")
        print(self.world.get_location_description(location_name))
        
        # 生成新地点的NPC
        if self.npc_manager:
            existing_npcs = self.npc_manager.get_npcs_in_location(location_name)
            if len(existing_npcs) < 3:
                self.npc_manager.generate_npcs_for_location(location_name, 3 - len(existing_npcs))
    
    def _handle_map(self):
        """处理地图命令"""
        if not self.world:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        print(f"\n{self.colorize('🗺️ 世界地图', Color.BOLD_CYAN)}")
        print(self.colorize("═" * 50, Color.BOLD_BLUE))
        
        for location in self.world.get_all_locations():
            marker = "📍" if self.player and self.player.stats.location == location.name else "  "
            realm_info = get_realm_info(location.realm_required)
            realm_name = realm_info.name if realm_info else "凡人"
            print(f"{marker} {location.name:<10} (需{realm_name})")
        
        print(self.colorize("═" * 50, Color.BOLD_BLUE))
    
    def _handle_secret_maps(self):
        """处理秘境命令 - 显示生成的地图/秘境列表"""
        if not self.world:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        print(f"\n{self.colorize('🏛️ 秘境/生成地图列表', Color.BOLD_CYAN)}")
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
        
        # 从数据库加载生成的地图
        from storage.database import Database
        db = Database()
        generated_maps = db.get_all_generated_maps()
        db.close()
        
        if not generated_maps:
            print(f"  {self.colorize('📭', Color.DIM)} 暂无秘境")
            print(f"\n  使用 {green('/gm map [数量] [名字] [境界]')} 生成新秘境")
        else:
            # 按类型分类显示
            maps_by_type = {}
            for map_data in generated_maps:
                map_type = map_data.get('map_type', '未知')
                if map_type not in maps_by_type:
                    maps_by_type[map_type] = []
                maps_by_type[map_type].append(map_data)
            
            for map_type, maps in maps_by_type.items():
                print(f"\n  {self.colorize('▸', Color.BOLD_YELLOW)} {map_type}:")
                for map_data in maps:
                    name = map_data.get('name', '未知')
                    level = map_data.get('level', 0)
                    realm_info = get_realm_info(level)
                    realm_name = realm_info.name if realm_info else "凡人"
                    
                    # 标记当前所在位置
                    marker = "📍" if self.player and self.player.stats.location == name else "  "
                    
                    # 检查是否满足进入条件
                    can_enter = self.player and self.player.stats.realm_level >= level
                    enter_icon = "✓" if can_enter else "✗"
                    
                    print(f"    {marker} {name:<15} (需{realm_name}) [{enter_icon}]")
        
        print(self.colorize("═" * 60, Color.BOLD_BLUE))
        print(f"\n  提示: 使用 {green('/前往 <秘境名>')} 进入秘境")
    
    def _handle_location(self):
        """处理位置命令"""
        if not self.player or not self.world:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        location = self.world.get_location(self.player.stats.location)
        if location:
            print(self.world.get_location_description(location.name))
            
            # 显示可前往的地点
            accessible = self.world.get_accessible_locations(location.name, self.player.stats.realm_level)
            if accessible:
                print(f"\n{self.colorize('🚶 可前往', Color.BOLD_CYAN)}: {', '.join(accessible)}")
            
            # 显示可前往的秘境
            from storage.database import Database
            db = Database()
            generated_maps = db.get_all_generated_maps()
            db.close()
            
            accessible_maps = []
            for map_data in generated_maps:
                map_name = map_data.get('name', '')
                map_level = map_data.get('level', 0)
                connections = map_data.get('connections', [])
                
                # 检查是否与当前位置相连且满足境界要求
                if location.name in connections and self.player.stats.realm_level >= map_level:
                    accessible_maps.append(map_name)
            
            if accessible_maps:
                print(f"\n{self.colorize('🏛️ 可前往秘境', Color.BOLD_MAGENTA)}: {', '.join(accessible_maps)}")
