"""
集成测试脚本
验证新的世界领域模型与现有系统的集成
"""

from game import World


def test_world_initialization():
    """测试世界初始化"""
    print("=== 测试世界初始化 ===")
    world = World()
    print("✅ 世界初始化成功")
    
    # 测试获取地点
    novice_village = world.get_location("新手村")
    if novice_village:
        print(f"✅ 成功获取地点: {novice_village.name}")
        print(f"   描述: {novice_village.description}")
        print(f"   境界要求: {novice_village.realm_required}")
    else:
        print("❌ 无法获取新手村")
    
    # 测试可访问性
    print("\n=== 测试地点可访问性 ===")
    can_enter = world.can_enter("新手村", 0)
    print(f"凡人是否可以进入新手村: {can_enter}")
    
    can_enter = world.can_enter("黄枫谷", 0)
    print(f"凡人是否可以进入黄枫谷: {can_enter}")
    
    can_enter = world.can_enter("黄枫谷", 1)
    print(f"炼气期是否可以进入黄枫谷: {can_enter}")
    
    # 测试获取可到达地点
    print("\n=== 测试获取可到达地点 ===")
    accessible = world.get_accessible_locations("新手村", 0)
    print(f"新手村可到达的地点: {accessible}")
    
    # 测试地点描述
    print("\n=== 测试地点描述 ===")
    description = world.get_location_description("新手村")
    print(description)
    
    # 测试NPC系统
    print("\n=== 测试NPC系统 ===")
    npcs = world.get_npcs_in_location("新手村")
    print(f"新手村的NPC数量: {len(npcs)}")
    for npc in npcs[:3]:
        print(f"   - {npc.data.dao_name} ({npc.get_realm_name()})")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_world_initialization()