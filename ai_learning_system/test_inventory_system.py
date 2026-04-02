"""
背包系统测试
"""

from config.items import Inventory, get_item, ItemType, ItemRarity


def test_inventory_basic_operations():
    """测试背包基本操作"""
    print("测试背包基本操作...")
    
    # 创建背包
    inventory = Inventory(max_slots=10)
    
    # 测试添加道具
    assert inventory.add_item("下品灵石", 100) == True
    assert inventory.add_item("筑基丹", 5) == True
    assert inventory.add_item("掌天瓶", 1) == True
    
    # 测试获取道具数量
    assert inventory.get_item_count("下品灵石") == 100
    assert inventory.get_item_count("筑基丹") == 5
    assert inventory.get_item_count("掌天瓶") == 1
    
    # 测试使用道具
    success, message = inventory.use_item("筑基丹")
    assert success == True
    assert inventory.get_item_count("筑基丹") == 4
    
    # 测试移除道具
    assert inventory.remove_item("下品灵石", 50) == True
    assert inventory.get_item_count("下品灵石") == 50
    
    # 测试背包满
    for i in range(7):  # 已用3个槽位，再添加7个
        inventory.add_item(f"测试道具{i}", 1, {
            "name": f"测试道具{i}",
            "description": "测试道具",
            "type": "消耗品",
            "rarity": "普通",
            "effects": [],
            "value": 10,
            "stackable": False,
            "max_stack": 1,
            "usable": True,
            "level_required": 0
        })
    
    # 背包已满，添加失败
    assert inventory.add_item("回气丹", 10) == False
    
    # 测试背包总价值
    total_value = inventory.get_total_value()
    assert total_value > 0
    
    print("✓ 背包基本操作测试通过")


def test_inventory_advanced_features():
    """测试背包高级功能"""
    print("测试背包高级功能...")
    
    inventory = Inventory(max_slots=20)
    
    # 添加各种类型的道具
    inventory.add_item("下品灵石", 200)
    inventory.add_item("中品灵石", 50)
    inventory.add_item("上品灵石", 10)
    inventory.add_item("筑基丹", 5)
    inventory.add_item("回气丹", 20)
    inventory.add_item("疗伤丹", 15)
    inventory.add_item("青竹蜂云剑", 1)
    inventory.add_item("风雷翅", 1)
    inventory.add_item("万年灵乳", 3)
    inventory.add_item("金雷竹", 2)
    
    # 测试按类型获取道具
    treasures = inventory.get_items_by_type("法宝")
    assert len(treasures) == 2  # 青竹蜂云剑和风雷翅
    
    pills = inventory.get_items_by_type("丹药")
    assert len(pills) == 3  # 筑基丹、回气丹、疗伤丹
    
    # 测试排序功能
    sorted_by_value = inventory.sort_items(sort_by="value", reverse=True)
    assert len(sorted_by_value) > 0
    
    sorted_by_name = inventory.sort_items(sort_by="name", reverse=False)
    assert len(sorted_by_name) > 0
    
    # 测试整理功能
    inventory.organize()
    
    # 测试搜索功能
    search_result = inventory.search("灵石")
    assert len(search_result) == 3  # 下品、中品、上品灵石
    
    # 测试批量使用
    success, message = inventory.batch_use_item("回气丹", 5)
    assert success == True
    assert inventory.get_item_count("回气丹") == 15
    
    # 测试等级限制
    success, message = inventory.can_use_item("青竹蜂云剑", 3)  # 青竹蜂云剑需要4级
    assert success == False
    assert "等级不足" in message
    
    success, message = inventory.can_use_item("青竹蜂云剑", 4)
    assert success == True
    
    # 测试背包摘要
    summary = inventory.get_inventory_summary()
    assert summary["total_items"] > 0
    assert summary["max_slots"] == 20
    assert summary["total_value"] > 0
    assert "items_by_type" in summary
    
    print("✓ 背包高级功能测试通过")


def test_generated_items():
    """测试动态生成的道具"""
    print("测试动态生成的道具...")
    
    inventory = Inventory(max_slots=10)
    
    # 添加动态生成的道具
    custom_item_data = {
        "name": "自定义道具",
        "description": "测试动态生成的道具",
        "type": "消耗品",
        "rarity": "稀有",
        "effects": ["测试效果1", "测试效果2"],
        "value": 500,
        "stackable": True,
        "max_stack": 50,
        "usable": True,
        "level_required": 2
    }
    
    success = inventory.add_generated_item("自定义道具", custom_item_data, 10)
    assert success == True
    assert inventory.get_item_count("自定义道具") == 10
    
    # 使用动态生成的道具
    success, message = inventory.use_item("自定义道具", 2)
    assert success == True
    assert inventory.get_item_count("自定义道具") == 8
    
    # 测试等级限制
    success, message = inventory.can_use_item("自定义道具", 1)
    assert success == False
    
    success, message = inventory.can_use_item("自定义道具", 2)
    assert success == True
    
    print("✓ 动态生成道具测试通过")


def test_edge_cases():
    """测试边缘情况"""
    print("测试边缘情况...")
    
    inventory = Inventory(max_slots=5)
    
    # 测试添加不存在的道具
    assert inventory.add_item("不存在的道具", 1) == False
    
    # 测试移除不存在的道具
    assert inventory.remove_item("不存在的道具", 1) == False
    
    # 测试使用不存在的道具
    success, message = inventory.use_item("不存在的道具")
    assert success == False
    
    # 测试移除超过数量的道具
    inventory.add_item("下品灵石", 10)
    assert inventory.remove_item("下品灵石", 20) == False
    assert inventory.get_item_count("下品灵石") == 10
    
    # 测试使用超过数量的道具
    success, message = inventory.use_item("下品灵石", 20)
    assert success == False
    assert inventory.get_item_count("下品灵石") == 10
    
    # 测试堆叠上限
    inventory2 = Inventory(max_slots=5)
    # 回气丹最大堆叠99
    assert inventory2.add_item("回气丹", 99) == True
    assert inventory2.add_item("回气丹", 1) == False  # 超过堆叠上限
    
    print("✓ 边缘情况测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("背包系统测试")
    print("=" * 60)
    
    try:
        test_inventory_basic_operations()
        test_inventory_advanced_features()
        test_generated_items()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()