"""测试新的背包系统"""

from game.inventory import Inventory


def test_inventory_basic():
    """测试背包基本功能"""
    print("=== 测试背包基本功能 ===")
    
    # 创建背包
    inventory = Inventory(max_slots=10)
    
    # 测试添加物品
    print("1. 测试添加物品:")
    item1_data = {
        "name": "回春丹",
        "type": "丹药",
        "rarity": "普通",
        "description": "恢复生命值的丹药",
        "value": 50,
        "stackable": True,
        "max_stack": 99,
        "usable": True
    }
    
    success, msg = inventory.add_item("回春丹", 5, item1_data)
    print(f"   添加回春丹 x5: {success}, {msg}")
    
    # 测试添加可堆叠物品
    success, msg = inventory.add_item("回春丹", 3)
    print(f"   添加回春丹 x3: {success}, {msg}")
    print(f"   回春丹数量: {inventory.get_item_count('回春丹')}")
    
    # 测试添加不可堆叠物品
    item2_data = {
        "name": "青竹蜂云剑",
        "type": "法宝",
        "rarity": "传说",
        "description": "韩立本命法宝",
        "value": 500000,
        "stackable": False,
        "max_stack": 1,
        "usable": True
    }
    
    success, msg = inventory.add_item("青竹蜂云剑", 1, item2_data)
    print(f"   添加青竹蜂云剑: {success}, {msg}")
    
    # 测试添加第二个不可堆叠物品
    success, msg = inventory.add_item("青竹蜂云剑", 1)
    print(f"   添加第二个青竹蜂云剑: {success}, {msg}")
    
    # 测试使用物品
    print("\n2. 测试使用物品:")
    success, msg = inventory.use_item("回春丹", 2)
    print(f"   使用回春丹 x2: {success}, {msg}")
    print(f"   回春丹剩余: {inventory.get_item_count('回春丹')}")
    
    # 测试移除物品
    print("\n3. 测试移除物品:")
    success, msg = inventory.remove_item("回春丹", 4)
    print(f"   移除回春丹 x4: {success}, {msg}")
    print(f"   回春丹剩余: {inventory.get_item_count('回春丹')}")
    
    # 测试背包已满
    print("\n4. 测试背包已满:")
    for i in range(8):
        item_data = {
            f"测试物品{i}": {
                "type": "材料",
                "rarity": "普通",
                "value": 10,
                "stackable": True
            }
        }
        success, msg = inventory.add_item(f"测试物品{i}", 1, item_data[f"测试物品{i}"])
        print(f"   添加测试物品{i}: {success}, {msg}")
    
    # 测试获取物品数据
    print("\n5. 测试获取物品数据:")
    item_data = inventory.get_item_data("青竹蜂云剑")
    if item_data:
        print(f"   青竹蜂云剑数据: {item_data}")
    
    # 测试背包摘要
    print("\n6. 测试背包摘要:")
    summary = inventory.get_inventory_summary()
    print(f"   背包摘要: {summary}")
    
    # 测试整理背包
    print("\n7. 测试整理背包:")
    inventory.organize()
    print("   背包已整理")
    
    # 测试搜索
    print("\n8. 测试搜索:")
    results = inventory.search("测试")
    print(f"   搜索'测试'结果: {[item_name for item_name in results]}")
    
    # 测试转换为字典和从字典加载
    print("\n9. 测试序列化和反序列化:")
    inv_dict = inventory.to_dict()
    print(f"   背包字典长度: {len(inv_dict['items'])}")
    
    # 创建新背包并从字典加载
    new_inventory = Inventory()
    new_inventory.from_dict(inv_dict)
    print(f"   新背包物品数量: {len(new_inventory.items)}")
    
    # 测试清空背包
    print("\n10. 测试清空背包:")
    inventory.clear()
    print(f"   背包清空后物品数量: {len(inventory.items)}")
    print(f"   生成道具定义数量: {len(inventory.generated_items)}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_inventory_basic()
