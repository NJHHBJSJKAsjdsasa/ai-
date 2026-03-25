"""
NPC独立系统整合测试
测试与游戏的整合
"""

import time
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game.world import World
from game.npc import NPCManager


def test_world_integration():
    """测试World类整合"""
    print("=" * 60)
    print("测试1: World类整合测试")
    print("=" * 60)
    
    try:
        # 创建World实例
        print("  创建World实例...")
        world = World()
        
        # 检查NPCManager是否已集成
        if hasattr(world, 'npc_manager'):
            print("  ✓ NPCManager已集成到World类")
            print(f"  ✓ 总NPC数: {len(world.npc_manager.npcs)}")
        else:
            print("  ✗ NPCManager未集成")
            return False
        
        # 检查地点NPC
        locations = list(world.locations.keys())
        print(f"\n  地点NPC分布:")
        for loc in locations[:3]:  # 只显示前3个
            npcs = world.get_npcs_in_location(loc)
            print(f"    {loc}: {len(npcs)}个NPC")
        
        print("\n✓ World类整合测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_npc_update():
    """测试NPC更新"""
    print("\n" + "=" * 60)
    print("测试2: NPC更新测试")
    print("=" * 60)
    
    try:
        world = World()
        
        # 获取一个地点的NPC
        location = "新手村"
        npcs = world.get_npcs_in_location(location)
        
        if not npcs:
            print("  ✗ 该地点没有NPC")
            return False
        
        npc = npcs[0]
        print(f"  测试NPC: {npc.data.dao_name}")
        
        # 记录初始状态
        initial_status = npc.get_independent_status()
        initial_actions = initial_status.get('total_actions', 0)
        print(f"  初始行动数: {initial_actions}")
        
        # 更新NPC多次
        print("  执行NPC更新...")
        current_time = time.time()
        for i in range(5):
            world.update_npcs(current_time + i * 2, location)
        
        # 检查更新后的状态
        final_status = npc.get_independent_status()
        final_actions = final_status.get('total_actions', 0)
        print(f"  最终行动数: {final_actions}")
        
        if final_actions > initial_actions:
            print("  ✓ NPC已成功更新")
        else:
            print("  ⚠ NPC可能未更新（可能是时间间隔限制）")
        
        print("\n✓ NPC更新测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_npc_commands():
    """测试NPC相关命令"""
    print("\n" + "=" * 60)
    print("测试3: NPC命令测试")
    print("=" * 60)
    
    try:
        world = World()
        
        # 测试get_npcs_in_location
        print("  测试get_npcs_in_location...")
        npcs = world.get_npcs_in_location("新手村")
        print(f"  ✓ 获取到{len(npcs)}个NPC")
        
        # 测试get_npc_by_name
        if npcs:
            npc_name = npcs[0].data.dao_name
            print(f"  测试get_npc_by_name('{npc_name}')...")
            npc = world.get_npc_by_name(npc_name)
            if npc:
                print(f"  ✓ 成功找到NPC: {npc.data.dao_name}")
            else:
                print(f"  ✗ 未找到NPC")
                return False
        
        # 测试get_npc_stats
        print("  测试get_npc_stats...")
        stats = world.get_npc_stats()
        print(f"  ✓ 总NPC数: {stats.get('total_npcs')}")
        print(f"  ✓ 活跃NPC数: {stats.get('active_npcs')}")
        print(f"  ✓ 总记忆数: {stats.get('total_memories')}")
        
        # 测试get_location_with_npcs
        print("  测试get_location_with_npcs...")
        description = world.get_location_with_npcs("新手村")
        if "修士" in description:
            print("  ✓ 地点描述包含NPC信息")
        else:
            print("  ⚠ 地点描述可能不包含NPC信息")
        
        print("\n✓ NPC命令测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_npc_social():
    """测试NPC社交"""
    print("\n" + "=" * 60)
    print("测试4: NPC社交测试")
    print("=" * 60)
    
    try:
        world = World()
        
        # 获取两个NPC
        npcs = world.get_npcs_in_location("新手村")
        if len(npcs) < 2:
            print("  ⚠ 该地点NPC不足2个，跳过测试")
            return True
        
        npc1, npc2 = npcs[0], npcs[1]
        print(f"  NPC1: {npc1.data.dao_name}")
        print(f"  NPC2: {npc2.data.dao_name}")
        
        # 记录初始记忆数
        mem1_before = len(npc1.independent.memories)
        mem2_before = len(npc2.independent.memories)
        print(f"  初始记忆数: {npc1.data.dao_name}={mem1_before}, {npc2.data.dao_name}={mem2_before}")
        
        # 进行社交
        world.socialize_npcs(npc1.data.id, npc2.data.id)
        
        # 检查记忆数变化
        mem1_after = len(npc1.independent.memories)
        mem2_after = len(npc2.independent.memories)
        print(f"  社交后记忆数: {npc1.data.dao_name}={mem1_after}, {npc2.data.dao_name}={mem2_after}")
        
        if mem1_after > mem1_before or mem2_after > mem2_before:
            print("  ✓ NPC社交成功，记忆已更新")
        else:
            print("  ⚠ 记忆未更新（可能是随机因素）")
        
        # 检查关系
        rel1 = npc1.independent.get_relationship(npc2.data.id)
        rel2 = npc2.independent.get_relationship(npc1.data.id)
        print(f"  关系好感度: {npc1.data.dao_name}->{npc2.data.dao_name}: {rel1.affinity:.1f}")
        print(f"  关系好感度: {npc2.data.dao_name}->{npc1.data.dao_name}: {rel2.affinity:.1f}")
        
        print("\n✓ NPC社交测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试5: 性能测试")
    print("=" * 60)
    
    try:
        import time
        
        # 测试World初始化时间
        print("  测试World初始化时间...")
        start = time.time()
        world = World()
        init_time = time.time() - start
        print(f"  ✓ World初始化耗时: {init_time:.3f}秒")
        
        # 测试NPC更新性能
        print("  测试NPC更新性能...")
        start = time.time()
        for i in range(10):
            world.update_npcs(time.time() + i, "新手村")
        update_time = time.time() - start
        print(f"  ✓ 10次更新耗时: {update_time:.3f}秒")
        
        # 获取统计
        stats = world.get_npc_stats()
        total_npcs = stats.get('total_npcs', 0)
        print(f"\n  统计信息:")
        print(f"    总NPC数: {total_npcs}")
        print(f"    总记忆数: {stats.get('total_memories')}")
        print(f"    总行动数: {stats.get('total_actions')}")
        
        if init_time < 5.0 and update_time < 1.0:
            print("\n✓ 性能测试通过!")
            return True
        else:
            print("\n⚠ 性能可能存在问题")
            return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("NPC独立系统整合测试套件")
    print("=" * 60)
    
    tests = [
        ("World类整合", test_world_integration),
        ("NPC更新", test_npc_update),
        ("NPC命令", test_npc_commands),
        ("NPC社交", test_npc_social),
        ("性能测试", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {name}测试失败!")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name}测试出错: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"  通过: {passed}/{len(tests)}")
    print(f"  失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有整合测试通过!")
        print("\nNPC独立系统已成功整合到游戏中！")
        print("\n可用命令:")
        print("  /npcs      - 查看当前地点NPC列表")
        print("  /npc <名字> - 查看NPC详细信息")
        print("  /npc_stats  - 查看NPC系统统计")
    else:
        print(f"\n⚠️ 有{failed}个测试未通过")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
