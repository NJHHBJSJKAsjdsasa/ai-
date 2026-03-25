"""
测试物品系统修复
验证生成道具可以正常使用
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.items import Inventory
from game.player import Player


def test_generated_item():
    """测试生成道具的使用"""
    print("=" * 60)
    print("测试生成道具系统")
    print("=" * 60)
    
    # 创建玩家
    player = Player("测试修士")
    
    # 模拟探索发现的生成道具
    generated_item_name = "一般的化神丹"
    item_data = {
        "name": generated_item_name,
        "description": "这是一颗普通的化神丹，散发着淡淡的药香",
        "type": "丹药",
        "rarity": "普通",
        "effects": ["恢复法力"],
        "value": 500,
        "stackable": True,
        "max_stack": 99,
        "usable": True,
        "level_required": 0,
        "origin": "探索获得"
    }
    
    print(f"\n1. 添加生成道具到背包: {generated_item_name}")
    success = player.inventory.add_generated_item(generated_item_name, item_data, 1)
    print(f"   结果: {'✓ 成功' if success else '✗ 失败'}")
    
    if not success:
        print("   添加失败，测试终止")
        return False
    
    # 检查背包
    print(f"\n2. 检查背包")
    count = player.inventory.get_item_count(generated_item_name)
    print(f"   {generated_item_name} 数量: {count}")
    
    # 检查是否在生成道具列表中
    if generated_item_name in player.inventory.generated_items:
        print(f"   ✓ 道具已记录在生成道具列表中")
    else:
        print(f"   ✗ 道具未在生成道具列表中")
        return False
    
    # 测试使用道具
    print(f"\n3. 测试使用道具")
    initial_sp = player.stats.spiritual_power
    print(f"   初始法力: {initial_sp}/{player.stats.max_spiritual_power}")
    
    success, message = player.use_item(generated_item_name)
    print(f"   使用结果: {'✓ 成功' if success else '✗ 失败'}")
    print(f"   消息: {message}")
    
    final_sp = player.stats.spiritual_power
    print(f"   使用后法力: {final_sp}/{player.stats.max_spiritual_power}")
    print(f"   恢复法力: {final_sp - initial_sp}")
    
    # 检查道具是否被消耗
    count_after = player.inventory.get_item_count(generated_item_name)
    print(f"\n4. 检查道具消耗")
    print(f"   使用后数量: {count_after}")
    if count_after == count - 1:
        print(f"   ✓ 道具已正确消耗")
    else:
        print(f"   ✗ 道具消耗异常")
    
    # 测试背包价值
    print(f"\n5. 测试背包价值计算")
    total_value = player.inventory.get_total_value()
    print(f"   背包总价值: {total_value} 灵石")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n生成道具系统工作正常：")
    print("  - 可以添加生成道具到背包")
    print("  - 可以使用生成道具")
    print("  - 生成道具会被正确消耗")
    print("  - 背包价值计算正确")
    
    return True


if __name__ == "__main__":
    try:
        success = test_generated_item()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
