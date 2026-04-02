"""
验证背包系统修复
"""

from game.player import Player
from game.generator import InfiniteGenerator
from storage.database import Database
from game.exploration_manager import explore
from game.world import World


def test_exploration_items_display():
    """测试探索获得的物品是否正确显示"""
    print("测试探索获得的物品是否正确显示...")
    
    # 创建数据库连接
    db = Database()
    
    # 创建玩家
    player = Player(name="测试修士", load_from_db=False)
    player.stats.location = "新手村"
    print(f"创建玩家: {player.stats.name}")
    
    # 直接生成物品并添加到背包
    generator = InfiniteGenerator(use_llm=False)
    print("\n生成物品并添加到背包:")
    for i in range(3):
        item = generator.generate_item()
        print(f"  • {item.name} - {item.rarity.value}")
        
        # 将物品添加到背包（模拟exploration_handler的逻辑）
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
        print(f"  添加到背包: {'成功' if success else '失败'}")
    
    # 查看背包
    print("\n背包内容:")
    print(player.get_inventory_info())
    
    # 测试使用物品
    print("\n测试使用物品:")
    # 创建物品名称列表的副本，避免在遍历过程中修改字典
    item_names = list(player.inventory.items.keys())
    for item_name in item_names:
        success, message = player.use_item(item_name)
        print(f"  使用{item_name}: {message}")
    
    # 查看背包
    print("\n使用后背包内容:")
    print(player.get_inventory_info())
    
    # 保存玩家数据
    print("\n保存玩家数据...")
    player_data = player.to_dict()
    db.save_player(player.stats.name, player_data)
    
    # 重新加载玩家
    print("重新加载玩家...")
    loaded_player = Player(name="测试修士", load_from_db=False)
    saved_data = db.load_player(player.stats.name)
    loaded_player.from_dict(saved_data)
    
    # 查看重新加载后的背包
    print("\n重新加载后背包内容:")
    print(loaded_player.get_inventory_info())
    
    # 测试使用重新加载的物品
    print("\n测试使用重新加载的物品:")
    # 创建物品名称列表的副本，避免在遍历过程中修改字典
    loaded_item_names = list(loaded_player.inventory.items.keys())
    for item_name in loaded_item_names:
        success, message = loaded_player.use_item(item_name)
        print(f"  使用{item_name}: {message}")
    
    # 清理测试数据
    db.delete_player(player.stats.name)
    db.close()
    
    print("\n测试完成！")


if __name__ == "__main__":
    print("=" * 60)
    print("验证背包系统修复")
    print("=" * 60)
    
    try:
        test_exploration_items_display()
        print("\n" + "=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()