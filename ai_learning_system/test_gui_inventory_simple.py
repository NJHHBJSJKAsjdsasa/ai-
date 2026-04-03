#!/usr/bin/env python3
"""
简化版GUI背包面板修复测试
不依赖外部模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.items import Inventory, ItemType, ItemRarity


def test_gui_inventory_simple():
    """简化版GUI背包面板修复测试"""
    print("=" * 60)
    print("简化版GUI背包面板修复测试")
    print("=" * 60)
    
    # 创建背包
    inventory = Inventory(max_slots=50)
    print("创建背包")
    
    # 添加测试物品
    test_items = [
        {
            "name": "普通的回春丹",
            "description": "恢复生命值的基础丹药",
            "type": "丹药",
            "rarity": "普通",
            "effects": ["恢复生命值", "恢复法力"],
            "value": 50,
            "stackable": True,
            "max_stack": 99,
            "usable": True,
            "level_required": 0,
            "origin": "探索获得"
        },
        {
            "name": "精良的灵剑",
            "description": "一把精良的灵剑",
            "type": "法宝",
            "rarity": "优秀",
            "effects": ["攻击加成", "防御加成"],
            "value": 500,
            "stackable": False,
            "max_stack": 1,
            "usable": True,
            "level_required": 1,
            "origin": "探索获得"
        },
        {
            "name": "珍贵的灵草",
            "description": "珍贵的灵草",
            "type": "材料",
            "rarity": "稀有",
            "effects": ["炼丹材料"],
            "value": 1000,
            "stackable": True,
            "max_stack": 99,
            "usable": False,
            "level_required": 2,
            "origin": "探索获得"
        }
    ]
    
    print("\n添加测试物品到背包...")
    for item_data in test_items:
        if inventory.add_generated_item(item_data["name"], item_data, 1):
            print(f"  ✓ {item_data['name']} 已添加到背包")
        else:
            print(f"  ✗ {item_data['name']} 添加失败")
    
    # 显示当前背包
    print("\n当前背包内容:")
    for item_name, data in inventory.items.items():
        print(f"  {item_name} x{data['count']}")
    
    # 测试模拟GUI背包面板的_get_items方法
    print("\n测试模拟GUI背包面板的_get_items方法...")
    
    # 模拟GUI的_get_items方法
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
        print(f"    描述: {item.description}")
        print(f"    稀有度: {item.rarity}")
    
    # 测试物品筛选
    print("\n测试物品筛选...")
    category_map = {
        "pill": ["pill", "丹药"],
        "material": ["material", "材料", "灵石", "消耗品"],
        "technique": ["technique", "秘籍"],
        "equipment": ["equipment", "法宝"],
    }
    
    for category, target_types in category_map.items():
        filtered = []
        for item in items_list:
            item_type = item.item_type
            if item_type in target_types:
                filtered.append(item)
        print(f"  {category} 筛选结果: {len(filtered)} 个")
        for item in filtered:
            print(f"    - {item.name}")
    
    # 测试使用物品
    print("\n测试使用物品...")
    if items_list:
        test_item = items_list[0]
        success, message = inventory.use_item(test_item.name, 1)
        print(f"  使用{test_item.name}: {message}")
    
    # 显示最终背包
    print("\n最终背包内容:")
    for item_name, data in inventory.items.items():
        print(f"  {item_name} x{data['count']}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_gui_inventory_simple()
