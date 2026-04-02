"""
探索处理器类

处理与探索、生成和妖兽相关的命令。
"""

from .base_handler import BaseHandler
from utils.colors import Color


class ExplorationHandler(BaseHandler):
    """
    探索处理器类

    处理探索命令、生成命令和妖兽命令。
    """

    def _handle_explore(self):
        """处理探索命令 - 使用探索管理器探索新区域"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return

        if not hasattr(self, 'exploration_manager') or not self.exploration_manager:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 探索系统未初始化")
            return

        try:
            # 使用探索管理器进行探索
            result = self.exploration_manager.explore(
                self.player.stats.location,
                self.player.stats.realm_level
            )

            # 格式化并显示结果
            print(self.exploration_manager.format_exploration_result(result))

            # 如果发现了物品，添加到玩家背包
            if result.discovered_items:
                for item in result.discovered_items:
                    # 将生成的物品转换为字典格式
                    item_data = {
                        "name": item.name,
                        "description": getattr(item, 'description', f'这是一件{item.rarity.value}的{item.item_type.value}'),
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "effects": getattr(item, 'effects', []) if isinstance(getattr(item, 'effects', []), list) else list(getattr(item, 'effects', {}).keys()),
                        "value": getattr(item, 'attributes', {}).get('power', 100) * 10,
                        "stackable": True,
                        "max_stack": 99,
                        "usable": True,
                        "level_required": 0,
                        "origin": "探索获得"
                    }

                    # 添加到背包
                    if self.player.inventory.add_generated_item(item.name, item_data, 1):
                        print(f"  ✓ {item.name} 已添加到背包")
                    else:
                        print(f"  ✗ {item.name} 添加失败")

            # 如果发现了NPC，添加到NPC管理器和数据库
            if result.discovered_npcs:
                from storage.database import Database
                from game.npc import NPC, NPCData
                
                db = Database()
                for npc in result.discovered_npcs:
                    try:
                        # 保存到数据库
                        npc_dict = npc.to_dict() if hasattr(npc, 'to_dict') else npc
                        db.save_generated_npc(npc_dict)
                        
                        # 添加到NPC管理器（如果存在）
                        if self.world and hasattr(self.world, 'npc_manager'):
                            # 构建NPC信息
                            full_name = npc_dict.get('full_name', npc_dict.get('name', '无名'))
                            npc_info = {
                                "id": npc_dict.get('id') or f"npc_{full_name}_{npc_dict.get('age', 20)}",
                                "name": npc_dict.get('name', ''),
                                "dao_name": full_name,
                                "age": npc_dict.get('age', 20),
                                "lifespan": 100,
                                "realm_level": npc_dict.get('realm_level', 0),
                                "sect": "",
                                "personality": npc_dict.get('personality', '普通'),
                                "occupation": npc_dict.get('occupation', '散修'),
                                "location": self.player.stats.location,
                                "favor": {}
                            }
                            
                            # 创建NPC对象并添加到管理器
                            npc_obj = NPC()
                            npc_obj.data = NPCData(**npc_info)
                            self.world.npc_manager.npcs[npc_obj.data.id] = npc_obj
                            
                            # 添加到独立NPC管理器
                            if hasattr(self.world.npc_manager, 'independent_manager'):
                                self.world.npc_manager.independent_manager.add_npc(npc_obj.independent, self.player.stats.location)
                        
                        print(f"  ✓ {full_name} 已添加到世界")
                    except Exception as e:
                        print(f"  ✗ 添加NPC失败: {e}")
                
                db.close()

            # 如果发现了妖兽，保存到数据库
            if result.discovered_monsters:
                from storage.database import Database
                
                db = Database()
                for monster in result.discovered_monsters:
                    try:
                        # 保存到数据库
                        monster_dict = monster.to_dict() if hasattr(monster, 'to_dict') else monster
                        db.save_generated_monster(monster_dict)
                        
                        # 添加到当前地点的妖兽列表
                        if self.world:
                            location = self.world.get_location(self.player.stats.location)
                            if location:
                                if not hasattr(location, 'monsters'):
                                    location.monsters = []
                                monster_id = monster_dict.get('id') or monster_dict.get('name', '未知')
                                if monster_id not in location.monsters:
                                    location.monsters.append(monster_id)
                        
                        print(f"  ✓ {monster_dict.get('name', '未知妖兽')} 已添加到{self.player.stats.location}")
                    except Exception as e:
                        print(f"  ✗ 添加妖兽失败: {e}")
                
                db.close()

            # 如果发现了新地点，推进时间
            if result.success and result.discovered_location:
                self.player.advance_time(1)

        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 探索失败: {e}")
            import traceback
            traceback.print_exc()

    def _handle_generate(self, args: str):
        """处理生成命令 - 手动生成内容"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return

        try:
            from game.generator import InfiniteGenerator
            from storage.database import Database

            generator = InfiniteGenerator(use_llm=False)

            if not args:
                print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 请指定要生成的内容类型")
                print(f"  用法: /生成 <地图|NPC|物品|妖兽>")
                return

            arg_lower = args.lower()
            db = Database()

            if arg_lower in ["地图", "map"]:
                # 生成地图
                new_map = generator.generate_map(target_level=self.player.stats.realm_level)
                db.save_generated_map(new_map.to_dict())

                print(f"\n{self.colorize('🗺️ 生成新地图', Color.BOLD_GREEN)}")
                print(f"  名称: {new_map.name}")
                print(f"  类型: {new_map.map_type.value}")
                print(f"  等级: {new_map.level}")
                print(f"  规模: {new_map.size}")
                print(f"  描述: {new_map.description[:50]}...")

            elif arg_lower in ["npc", "人物"]:
                # 生成NPC
                location = self.player.stats.location if self.player else "未知"
                npc = generator.generate_npc(
                    location=location,
                    target_realm=generator.generate_realm_level(self.player.stats.realm_level)
                )
                db.save_generated_npc(npc.to_dict())

                print(f"\n{self.colorize('👤 生成新NPC', Color.BOLD_GREEN)}")
                print(f"  姓名: {npc.full_name}")
                print(f"  性别: {npc.gender}")
                print(f"  年龄: {npc.age}岁")
                from config import get_realm_info
                realm_info = get_realm_info(npc.realm_level)
                print(f"  修为: {realm_info.name if realm_info else '凡人'}")
                print(f"  职业: {npc.occupation.value}")
                print(f"  性格: {npc.personality.value}")
                print(f"  口头禅: {npc.catchphrase}")

            elif arg_lower in ["物品", "item"]:
                # 生成物品
                item = generator.generate_item()
                db.save_generated_item(item.to_dict())

                print(f"\n{self.colorize('📦 生成新物品', Color.BOLD_GREEN)}")
                print(f"  名称: {item.name}")
                print(f"  类型: {item.item_type.value}")
                print(f"  稀有度: {item.rarity.value}")
                print(f"  描述: {item.description[:50]}...")

            elif arg_lower in ["妖兽", "monster"]:
                # 生成妖兽
                location = self.player.stats.location if self.player else "未知"
                monster = generator.generate_monster(
                    level=self.player.stats.realm_level + 1,
                    location=location
                )
                db.save_generated_monster(monster.to_dict())

                print(f"\n{self.colorize('👹 生成新妖兽', Color.BOLD_GREEN)}")
                print(f"  名称: {monster.name}")
                print(f"  类型: {monster.monster_type.value}")
                print(f"  等级: {monster.level}")
                from config import get_realm_info
                realm_info = get_realm_info(monster.realm_level)
                print(f"  修为: {realm_info.name if realm_info else '凡人'}")
                print(f"  描述: {monster.description[:50]}...")
                print(f"  弱点: {monster.weakness}")

            else:
                print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 未知的生成类型: {args}")
                print(f"  可用类型: 地图、NPC、物品、妖兽")

            db.close()

        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 生成失败: {e}")
            import traceback
            traceback.print_exc()

    def _handle_monsters(self):
        """处理妖兽命令 - 查看当前地图的妖兽"""
        if not self.player:
            print(f"\n{self.colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return

        try:
            from storage.database import Database
            from config import get_realm_info

            location = self.player.stats.location

            db = Database()
            monsters = db.get_generated_monsters_by_location(location)
            db.close()

            if not monsters:
                print(f"\n{self.colorize('👹', Color.BOLD_CYAN)} {location} 暂无妖兽")
                return

            print(f"\n{self.colorize('👹 当前区域妖兽', Color.BOLD_RED)} ({location})")
            print(self.colorize("─" * 50, Color.BOLD_BLUE))

            for monster in monsters:
                realm_info = get_realm_info(monster.get('realm_level', 0))
                realm_name = realm_info.name if realm_info else "凡人"
                print(f"\n  {self.colorize('•', Color.BOLD_RED)} {monster.get('name', '未知')}")
                print(f"    类型: {monster.get('monster_type', '未知')}")
                print(f"    修为: {realm_name}")
                print(f"    描述: {monster.get('description', '无')[:40]}...")
                if monster.get('weakness'):
                    print(f"    弱点: {monster.get('weakness')}")

            print(self.colorize("─" * 50, Color.BOLD_BLUE))
            print(f"{self.colorize('💡', Color.BOLD_YELLOW)} 共 {len(monsters)} 只妖兽")

        except Exception as e:
            print(f"\n{self.colorize('❌', Color.BOLD_RED)} 获取妖兽列表失败: {e}")
