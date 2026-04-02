"""
测试背包系统修复
"""

from game.player import Player
from game.generator import InfiniteGenerator
from storage.database import Database


def test_generated_items_persistence():
    """测试生成物品的持久化"""
    print("测试生成物品的持久化...")
    
    # 创建数据库连接
    db = Database()
    
    # 创建玩家
    player = Player(name="测试修士", load_from_db=False)
    print(f"创建玩家: {player.stats.name}")
    
    # 创建生成器
    generator = InfiniteGenerator(use_llm=False)
    
    # 生成一些物品
    generated_items = []
    for i in range(5):
        item = generator.generate_item()
        generated_items.append(item)
        print(f"生成物品: {item.name} ({item.item_type.value}, {item.rarity.value})")
    
    # 添加到背包
    for item in generated_items:
        # 转换为字典格式
        item_data = {
            "name": item.name,
            "description": item.description,
            "type": item.item_type.value,
            "rarity": item.rarity.value,
            "effects": item.effects if isinstance(item.effects, list) else list(item.effects.keys()),
            "value": item.attributes.get('power', 100) * 10,
            "stackable": True,
            "max_stack": 99,
            "usable": True,
            "level_required": 0,
            "origin": "测试生成"
        }
        
        success = player.inventory.add_generated_item(item.name, item_data, 1)
        print(f"添加到背包: {item.name} - {'成功' if success else '失败'}")
    
    # 保存玩家数据
    player_data = player.to_dict()
    print(f"保存前背包物品: {list(player.inventory.items.keys())}")
    print(f"保存前生成道具: {list(player.inventory.generated_items.keys())}")
    
    db.save_player(player.stats.name, player_data)
    print("保存玩家数据成功")
    
    # 直接从数据库加载数据查看
    saved_data = db.load_player(player.stats.name)
    print(f"数据库中的背包数据: {saved_data.get('inventory', {})}")
    
    # 重新加载玩家
    loaded_player = Player(name="测试修士", load_from_db=False)
    loaded_player.from_dict(saved_data)
    print(f"重新加载玩家: {loaded_player.stats.name}")
    
    # 检查背包
    print("\n背包内容:")
    for item_name, data in loaded_player.inventory.items.items():
        item_data = data['data']
        print(f"  {item_name} x{data['count']}")
        print(f"    类型: {item_data.get('type', '未知')}")
        print(f"    稀有度: {item_data.get('rarity', '未知')}")
        print(f"    效果: {item_data.get('effects', [])}")
    
    # 检查生成的道具是否正确加载
    print("\n生成的道具定义:")
    for item_name, item_data in loaded_player.inventory.generated_items.items():
        print(f"  {item_name}: {item_data.get('type', '未知')}")
    
    # 验证所有生成的物品都已正确加载
    missing_items = []
    for item in generated_items:
        if item.name not in loaded_player.inventory.items:
            missing_items.append(item.name)
    
    if missing_items:
        print(f"\n❌ 以下物品未正确加载: {missing_items}")
    else:
        print("\n✅ 所有生成的物品都已正确加载")
    
    # 清理测试数据
    db.delete_player(player.stats.name)
    db.close()
    
    return len(missing_items) == 0


def test_exploration_items():
    """测试探索获得的物品"""
    print("\n测试探索获得的物品...")
    
    # 创建数据库连接
    db = Database()
    
    # 创建玩家
    player = Player(name="探索修士", load_from_db=False)
    player.stats.location = "新手村"
    print(f"创建玩家: {player.stats.name}")
    
    # 模拟探索获得物品
    from game.generator import InfiniteGenerator
    generator = InfiniteGenerator(use_llm=False)
    
    # 生成物品
    items = generator.generate_items_batch(3)
    print(f"生成 {len(items)} 个探索物品")
    
    # 添加到背包（模拟探索处理器的逻辑）
    for item in items:
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
        
        success = player.inventory.add_generated_item(item.name, item_data, 1)
        print(f"添加探索物品: {item.name} - {'成功' if success else '失败'}")
    
    # 保存并重新加载
    player_data = player.to_dict()
    print(f"保存前背包物品: {list(player.inventory.items.keys())}")
    db.save_player(player.stats.name, player_data)
    
    # 直接从数据库加载数据查看
    saved_data = db.load_player(player.stats.name)
    
    # 重新加载玩家
    loaded_player = Player(name="探索修士", load_from_db=False)
    loaded_player.from_dict(saved_data)
    
    # 检查物品
    print("\n探索获得的物品:")
    for item_name, data in loaded_player.inventory.items.items():
        item_data = data['data']
        print(f"  {item_name}")
        print(f"    类型: {item_data.get('type', '未知')}")
        print(f"    来源: {item_data.get('origin', '未知')}")
    
    # 清理测试数据
    db.delete_player(player.stats.name)
    db.close()
    
    return len(loaded_player.inventory.items) == len(items)


if __name__ == "__main__":
    print("=" * 60)
    print("背包系统修复测试")
    print("=" * 60)
    
    try:
        test1_result = test_generated_items_persistence()
        test2_result = test_exploration_items()
        
        print("\n" + "=" * 60)
        if test1_result and test2_result:
            print("🎉 所有测试通过！")
            print("✅ 生成的物品能正确保存和加载")
            print("✅ 探索获得的物品显示正常")
        else:
            print("❌ 测试失败")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()