"""
管理员命令处理器

处理管理员和GM相关的游戏管理命令。
"""

import uuid
from typing import Optional

from .base_handler import BaseHandler
from utils.colors import Color, colorize, bold


class AdminHandler(BaseHandler):
    """
    管理员命令处理器
    
    处理管理员命令(/admin)和GM命令(/gm)，包括：
    - 玩家属性管理（修为、法力、灵石等）
    - 游戏世界管理（生成NPC、妖兽、地图等）
    """
    
    def handle_admin_command(self, args: str):
        """
        处理管理员命令
        
        可用命令:
        - /admin exp <数值>    - 增加修为
        - /admin sp <数值>     - 增加法力
        - /admin stones <数值> - 增加灵石
        - /admin item <名称> [数量] - 添加道具
        - /admin realm <等级>  - 设置境界(0-8)
        - /admin age <数值>    - 设置年龄
        - /admin lifespan <数值> - 设置寿元
        - /admin heal          - 恢复满状态
        - /admin max           - 满状态（修为、法力、生命）
        """
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not args:
            self.display_admin_help()
            return
        
        parts = args.split()
        cmd = parts[0].lower()
        
        try:
            if cmd == "exp" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.add_exp(amount)
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 修为 +{amount}")
                print(f"  当前修为: {self.player.stats.exp}/{self.player.get_exp_needed()}")
                
            elif cmd == "sp" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.stats.spiritual_power = min(
                    self.player.stats.max_spiritual_power,
                    self.player.stats.spiritual_power + amount
                )
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 法力 +{amount}")
                print(f"  当前法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                
            elif cmd == "stones" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.stats.spirit_stones += amount
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 灵石 +{amount}")
                print(f"  当前灵石: {self.player.stats.spirit_stones}")
                
            elif cmd == "item":
                if len(parts) < 2:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 用法: /admin item <道具名> [数量]")
                    return
                # 支持带空格的道具名（用引号或直到数字前）
                # 例如: /admin item 罕见的回春丹 12
                # 或: /admin item "罕见的回春丹" 12
                remaining = ' '.join(parts[1:])
                # 尝试解析数量
                count = 1
                item_name = remaining
                # 如果最后一部分是数字，则作为数量
                if parts[-1].isdigit():
                    count = int(parts[-1])
                    item_name = ' '.join(parts[1:-1])
                
                success, msg = self.player.add_item(item_name, count)
                if success:
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} {msg}")
                else:
                    print(f"\n{self.colorize('❌', Color.BOLD_RED)} {msg}")
                    
            elif cmd == "realm" and len(parts) >= 2:
                level = int(parts[1])
                if 0 <= level <= 8:
                    self.player.stats.realm_level = level
                    from config import get_realm_info
                    realm_info = get_realm_info(level)
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 境界已设置为: {realm_info.name if realm_info else '未知'}")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 境界等级必须在 0-8 之间")
                    
            elif cmd == "age" and len(parts) >= 2:
                age = int(parts[1])
                self.player.stats.age = age
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 年龄已设置为: {age}岁")
                
            elif cmd == "lifespan" and len(parts) >= 2:
                lifespan = int(parts[1])
                self.player.stats.lifespan = lifespan
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 寿元已设置为: {lifespan}年")
                
            elif cmd == "heal":
                self.player.stats.health = 100
                self.player.stats.spiritual_power = self.player.stats.max_spiritual_power
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 状态已恢复满")
                print(f"  生命: 100/100")
                print(f"  法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                
            elif cmd == "max":
                # 满状态
                self.player.stats.health = 100
                self.player.stats.spiritual_power = self.player.stats.max_spiritual_power
                # 满修为
                exp_needed = self.player.get_exp_needed()
                self.player.add_exp(exp_needed)
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 已设置为满状态")
                print(f"  生命: 100/100")
                print(f"  法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                print(f"  修为: 已满，可以突破！")
                
            elif cmd == "help" or cmd == "?":
                self.display_admin_help()
                
            else:
                print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 未知的管理员命令: {cmd}")
                self.display_admin_help()
                
        except ValueError:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 参数必须是数字")
        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 执行命令时出错: {e}")
    
    def display_admin_help(self):
        """显示管理员命令帮助"""
        print(f"\n{self.colorize('═' * 60, Color.BOLD_RED)}")
        print(f"  {self.colorize('👑', Color.BOLD_YELLOW)}  {bold('管理员命令')}")
        print(f"{self.colorize('═' * 60, Color.BOLD_RED)}")
        print(f"  {self.colorize('/admin exp <数值>', Color.BOLD_CYAN)}    - 增加修为")
        print(f"  {self.colorize('/admin sp <数值>', Color.BOLD_CYAN)}     - 增加法力")
        print(f"  {self.colorize('/admin stones <数值>', Color.BOLD_CYAN)} - 增加灵石")
        print(f"  {self.colorize('/admin item <名称> [数量]', Color.BOLD_CYAN)} - 添加道具")
        print(f"  {self.colorize('/admin realm <等级>', Color.BOLD_CYAN)}  - 设置境界(0-8)")
        print(f"  {self.colorize('/admin age <数值>', Color.BOLD_CYAN)}    - 设置年龄")
        print(f"  {self.colorize('/admin lifespan <数值>', Color.BOLD_CYAN)} - 设置寿元")
        print(f"  {self.colorize('/admin heal', Color.BOLD_CYAN)}          - 恢复满状态")
        print(f"  {self.colorize('/admin max', Color.BOLD_CYAN)}           - 满状态（修为、法力、生命）")
        print(f"  {self.colorize('/admin help', Color.BOLD_CYAN)}          - 显示此帮助")
        print(f"{self.colorize('═' * 60, Color.BOLD_RED)}")
    
    def handle_gm_command(self, args: str):
        """
        处理GM命令（游戏管理命令）
        
        可用命令:
        - /gm npc <数量>              - 在当前地点生成NPC
        - /gm monster <数量>          - 在当前地点生成妖兽
        - /gm item <数量>             - 生成随机道具
        - /gm clear                   - 清空背包
        - /gm save                    - 强制保存游戏
        - /gm time <天数>             - 推进时间
        - /gm location <地点>         - 瞬移到指定地点
        - /gm list locations          - 列出所有地点
        - /gm map [数量] [名字] [境界] - 生成新地图
        - /gm refresh                 - 强制刷新NPC独立系统
        """
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not args:
            self.display_gm_help()
            return
        
        parts = args.split()
        cmd = parts[0].lower()
        
        try:
            if cmd == "npc":
                count = int(parts[1]) if len(parts) >= 2 else 1
                if self.world:
                    npcs = self.world.npc_manager.generate_npcs_for_location(
                        self.player.stats.location, count
                    )
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 已生成 {len(npcs)} 个NPC")
                    
                    # 保存到数据库
                    from storage.database import Database
                    db = Database()
                    for npc in npcs:
                        print(f"  • {npc.data.dao_name}")
                        # 转换为字典并保存
                        npc_dict = npc.to_dict()
                        db.save_generated_npc(npc_dict)
                    db.close()
                    print(f"\n{self.colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "monster":
                count = int(parts[1]) if len(parts) >= 2 else 1
                if self.world:
                    from game.generator import InfiniteGenerator
                    generator = InfiniteGenerator(use_llm=False)
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 已生成 {count} 只妖兽:")
                    
                    # 保存到数据库
                    from storage.database import Database
                    db = Database()
                    
                    for i in range(count):
                        monster = generator.generate_monster(
                            level=self.player.stats.realm_level,
                            location=self.player.stats.location
                        )
                        print(f"  • {monster.name} (Lv.{monster.level})")
                        # 保存妖兽到数据库
                        monster_dict = {
                            'id': getattr(monster, 'id', str(uuid.uuid4())),
                            'name': monster.name,
                            'monster_type': getattr(monster, 'monster_type', '普通'),
                            'level': monster.level,
                            'realm_level': getattr(monster, 'realm_level', self.player.stats.realm_level),
                            'location': self.player.stats.location,
                            'description': getattr(monster, 'description', ''),
                            'attributes': getattr(monster, 'attributes', {}),
                            'skills': getattr(monster, 'skills', []),
                            'drops': getattr(monster, 'drops', [])
                        }
                        db.save_generated_monster(monster_dict)
                    
                    db.close()
                    print(f"\n{self.colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "item":
                count = int(parts[1]) if len(parts) >= 2 else 1
                from game.generator import InfiniteGenerator
                generator = InfiniteGenerator(use_llm=False)
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 已生成 {count} 件道具:")
                
                # 保存到数据库
                from storage.database import Database
                db = Database()
                
                for i in range(count):
                    item = generator.generate_item()
                    # 添加到背包
                    item_data = {
                        "name": item.name,
                        "description": getattr(item, 'description', f'这是一件{item.rarity.value}的{item.item_type.value}'),
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "effects": list(getattr(item, 'effects', {}).keys()) if hasattr(item, 'effects') else [],
                        "value": getattr(item, 'attributes', {}).get('power', 100) * 10,
                        "stackable": True,
                        "max_stack": 99,
                        "usable": True,
                        "level_required": 0,
                        "origin": "GM生成"
                    }
                    self.player.inventory.add_generated_item(item.name, item_data, 1)
                    print(f"  • {item.name}")
                    
                    # 保存道具到数据库
                    item_dict = {
                        'id': str(uuid.uuid4()),
                        'name': item.name,
                        'item_type': item.item_type.value,
                        'rarity': item.rarity.value,
                        'description': getattr(item, 'description', ''),
                        'attributes': getattr(item, 'attributes', {}),
                        'effects': list(getattr(item, 'effects', {}).keys()) if hasattr(item, 'effects') else [],
                        'value': getattr(item, 'attributes', {}).get('power', 100) * 10,
                        'level_required': 0
                    }
                    db.save_generated_item(item_dict)
                
                db.close()
                print(f"\n{self.colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                    
            elif cmd == "clear":
                self.player.inventory.items.clear()
                self.player.inventory.generated_items.clear()
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 背包已清空")
                
            elif cmd == "save":
                if self.save_player():
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 游戏已保存")
                else:
                    print(f"\n{self.colorize('❌', Color.BOLD_RED)} 保存失败")
                    
            elif cmd == "time" and len(parts) >= 2:
                days = int(parts[1])
                self.player.advance_time(days)
                print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 时间已推进 {days} 天")
                print(f"  当前年龄: {self.player.stats.age}岁")
                
            elif cmd == "location":
                if len(parts) < 2:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 用法: /gm location <地点名>")
                    return
                location_name = parts[1]
                if self.world and location_name in self.world.locations:
                    self.player.stats.location = location_name
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 已瞬移到: {location_name}")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 地点不存在: {location_name}")
                    print(f"  使用 /gm list locations 查看所有地点")
                    
            elif cmd == "list" and len(parts) >= 2 and parts[1].lower() == "locations":
                if self.world:
                    print(f"\n{self.colorize('📍 可用地点列表', Color.BOLD_CYAN)}")
                    print(self.colorize("─" * 50, Color.BOLD_BLUE))
                    for loc_name in self.world.locations.keys():
                        current = " 👈 当前" if loc_name == self.player.stats.location else ""
                        print(f"  • {loc_name}{current}")
                    print(self.colorize("─" * 50, Color.BOLD_BLUE))
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "map":
                # 解析参数: /gm map [数量] [名字] [境界等级]
                # 例如: /gm map 1 幽冥山谷 3
                # 或: /gm map 3 (生成3个随机地图)
                count = 1
                custom_name = None
                realm_level = None
                
                if len(parts) >= 2:
                    # 检查第一个参数是否是数字（数量）
                    if parts[1].isdigit():
                        count = int(parts[1])
                        # 剩余部分可能是名字和境界
                        if len(parts) >= 3:
                            # 检查最后一部分是否是数字（境界）
                            if parts[-1].isdigit() and len(parts) > 2:
                                realm_level = int(parts[-1])
                                # 中间部分是名字
                                if len(parts) > 3:
                                    custom_name = ' '.join(parts[2:-1])
                            else:
                                # 没有指定境界，剩余部分是名字
                                custom_name = ' '.join(parts[2:])
                    else:
                        # 第一个参数不是数字，视为名字
                        custom_name = parts[1]
                        if len(parts) >= 3 and parts[-1].isdigit():
                            realm_level = int(parts[-1])
                
                if self.world:
                    from game.generator import InfiniteGenerator
                    from config import get_realm_info
                    generator = InfiniteGenerator(use_llm=False)
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 正在生成 {count} 个新地图...")
                    if custom_name:
                        print(f"  自定义名称: {custom_name}")
                    if realm_level is not None:
                        realm_info = get_realm_info(realm_level)
                        print(f"  境界限制: {realm_info.name if realm_info else '未知'}")
                    
                    for i in range(count):
                        # 生成地图
                        from game.generator import MapType
                        new_map = generator.generate_map(
                            target_level=realm_level if realm_level is not None else self.player.stats.realm_level
                        )
                        
                        if new_map:
                            # 如果指定了自定义名字，替换生成的名字
                            if custom_name:
                                if count > 1:
                                    new_map.name = f"{custom_name}{i+1}"
                                else:
                                    new_map.name = custom_name
                            
                            # 如果指定了境界限制，设置进入要求
                            if realm_level is not None:
                                new_map.level = realm_level
                                # 更新描述中的境界要求
                                realm_info = get_realm_info(realm_level)
                                if realm_info:
                                    new_map.description = f"[{realm_info.name}以上可进入] {new_map.description}"
                            
                            # 添加到世界连接
                            if self.player.stats.location not in new_map.connections:
                                new_map.connections.append(self.player.stats.location)
                            
                            # 保存到数据库
                            from storage.database import Database
                            db = Database()
                            db.save_generated_map(new_map.to_dict())
                            db.close()
                            
                            # 显示信息
                            realm_req = ""
                            if new_map.level is not None:
                                req_realm = get_realm_info(new_map.level)
                                if req_realm:
                                    realm_req = f" [需{req_realm.name}]"
                            print(f"  • {new_map.name} ({new_map.map_type.value}){realm_req}")
                    
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} 地图生成完成！")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "refresh" or cmd == "refreshnpc":
                if self.world:
                    print(f"\n{self.colorize('🔄', Color.BOLD_CYAN)} 正在强制刷新NPC独立系统...")
                    # 更新所有NPC
                    import time
                    current_time = time.time()
                    updated_count = 0
                    for npc_id, npc in self.world.npc_manager.npcs.items():
                        if npc.independent.update(current_time, player_nearby=True):
                            updated_count += 1
                    
                    stats = self.world.get_npc_stats()
                    print(f"\n{self.colorize('✅', Color.BOLD_GREEN)} NPC独立系统已刷新")
                    print(f"  总NPC数: {stats.get('total_npcs', 0)}")
                    print(f"  活跃NPC数: {stats.get('active_npcs', 0)}")
                    print(f"  本轮更新: {updated_count}")
                    print(f"  总记忆数: {stats.get('total_memories', 0)}")
                    print(f"  总关系数: {stats.get('total_relationships', 0)}")
                    print(f"  总行动数: {stats.get('total_actions', 0)}")
                else:
                    print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "help" or cmd == "?":
                self.display_gm_help()
                
            else:
                print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 未知的GM命令: {cmd}")
                self.display_gm_help()
                
        except ValueError:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 参数必须是数字")
        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 执行命令时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def display_gm_help(self):
        """显示GM命令帮助"""
        print(f"\n{self.colorize('═' * 60, Color.BOLD_MAGENTA)}")
        print(f"  {self.colorize('🎮', Color.BOLD_YELLOW)}  {bold('GM命令')}")
        print(f"{self.colorize('═' * 60, Color.BOLD_MAGENTA)}")
        print(f"  {self.colorize('/gm npc <数量>', Color.BOLD_CYAN)}       - 在当前地点生成NPC")
        print(f"  {self.colorize('/gm monster <数量>', Color.BOLD_CYAN)}  - 在当前地点生成妖兽")
        print(f"  {self.colorize('/gm item <数量>', Color.BOLD_CYAN)}     - 生成随机道具")
        print(f"  {self.colorize('/gm clear', Color.BOLD_CYAN)}          - 清空背包")
        print(f"  {self.colorize('/gm save', Color.BOLD_CYAN)}           - 强制保存游戏")
        print(f"  {self.colorize('/gm time <天数>', Color.BOLD_CYAN)}    - 推进时间")
        print(f"  {self.colorize('/gm location <地点>', Color.BOLD_CYAN)} - 瞬移到指定地点")
        print(f"  {self.colorize('/gm list locations', Color.BOLD_CYAN)} - 列出所有地点")
        print(f"  {self.colorize('/gm map [数量] [名字] [境界]', Color.BOLD_CYAN)} - 生成新地图")
        print(f"  {self.colorize('/gm refresh', Color.BOLD_CYAN)}        - 强制刷新NPC独立系统")
        print(f"  {self.colorize('/gm help', Color.BOLD_CYAN)}           - 显示此帮助")
        print(f"{self.colorize('═' * 60, Color.BOLD_MAGENTA)}")
