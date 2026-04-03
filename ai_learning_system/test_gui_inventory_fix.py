#!/usr/bin/env python3
"""
测试GUI背包面板修复是否有效
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game.player import Player
from storage.database import Database
from game.generator import InfiniteGenerator


def test_gui_inventory_fix():
    """测试GUI背包面板修复"""
    print("=" * 60)
    print("测试GUI背包面板修复")
    print("=" * 60)
    
    # 初始化数据库
    db = Database()
    db.init_tables()
    db.init_generated_tables()
    
    # 创建玩家
    player = Player(name="GUI测试玩家", load_from_db=False)
    print(f"创建玩家: {player.stats.name}")
    
    # 生成一些物品（模拟探索获得）
    generator = InfiniteGenerator(use_llm=False)
    print("\n生成测试物品...")
    
    discovered_items = []
    for i in range(3):
        item = generator.generate_item()
        discovered_items.append(item)
        print(f"  生成物品: {item.name}")
    
    # 添加物品到背包
    print("\n添加物品到背包...")
    for item in discovered_items:
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
        
        if player.inventory.add_generated_item(item.name, item_data, 1):
            print(f"  ✓ {item.name} 已添加到背包")
        else:
            print(f"  ✗ {item.name} 添加失败")
    
    # 显示当前背包
    print("\n当前背包内容:")
    for item_name, data in player.inventory.items.items():
        print(f"  {item_name} x{data['count']}")
    
    # 测试模拟GUI背包面板的_get_items方法
    print("\n测试模拟GUI背包面板的_get_items方法...")
    
    # 模拟GUI的_get_items方法
    inventory = player.inventory
    items_list = []
    if inventory and hasattr(inventory, 'items'):
        if isinstance(inventory.items, dict):
            for item_name, item_info in inventory.items.items():
                item_data = item_info.get('data', {})
                item_obj = type('ItemWrapper', (), {})()
                item_obj.name = item_name
                item_obj.quantity = item_info.get('count', 1)
                item_obj.item_type = item_data.get('type', 'other')
                item_obj.description = item_data.get('description', '暂无描述')
                item_obj.rarity = item_data.get('rarity', '普通')
                item_obj.data = item_data
                items_list.append(item_obj)
    
    print(f"\n解析出 {len(items_list)} 个物品:")
    for item in items_list:
        print(f"  {item.name} x{item.quantity} ({item.item_type})")
        print(f"    描述: {item.description[:50]}...")
    
    # 测试使用物品
    print("\n测试使用物品...")
    if items_list:
        test_item = items_list[0]
        success, message = player.use_item(test_item.name)
        print(f"  使用{test_item.name}: {message}")
    
    # 显示最终背包
    print("\n最终背包内容:")
    for item_name, data in player.inventory.items.items():
        print(f"  {item_name} x{data['count']}")
    
    # 保存游戏
    print("\n保存游戏...")
    if player.save_to_db(db):
        print("  ✓ 游戏保存成功")
    else:
        print("  ✗ 游戏保存失败")
    
    # 加载游戏
    print("\n加载游戏...")
    new_player = Player(name="GUI测试玩家", load_from_db=False)
    if new_player.load_from_db(db):
        print("  ✓ 游戏加载成功")
    else:
        print("  ✗ 游戏加载失败")
    
    # 显示加载后的背包
    print("\n加载后的背包内容:")
    for item_name, data in new_player.inventory.items.items():
        print(f"  {item_name} x{data['count']}")
    
    # 清理数据库
    db.delete_player("GUI测试玩家")
    db.close()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_gui_inventory_fix()
