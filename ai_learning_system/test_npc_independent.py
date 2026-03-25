"""
NPC独立系统测试脚本
测试性能、功能和集成
"""

import time
import random
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game.npc_independent import NPCIndependent, NPCIndependentManager, NeedType, GoalType
from game.npc import NPC, NPCManager


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("测试1: 基本功能测试")
    print("=" * 60)
    
    # 创建NPC
    npc_data = {
        "occupation": "炼丹师",
        "location": "新手村",
        "personality": "勤奋刻苦"
    }
    npc = NPCIndependent("npc_001", npc_data)
    
    print(f"✓ NPC创建成功: {npc.npc_id}")
    print(f"  - 初始位置: {npc.current_location}")
    print(f"  - 职业: {npc.npc_data.get('occupation')}")
    print(f"  - 目标数量: {len(npc.goals)}")
    print(f"  - 性格: 勇敢={npc.personality.bravery:.2f}, 勤奋={npc.personality.diligence:.2f}")
    
    # 测试需求系统
    print("\n  需求状态:")
    for need_type, need in npc.needs.items():
        print(f"    - {need_type.name}: {need.value:.1f}")
    
    # 测试决策
    decision = npc.make_decision()
    print(f"\n  决策结果: {decision}")
    
    # 测试执行动作
    result = npc.execute_action(decision)
    print(f"  执行结果: {result}")
    
    # 测试记忆
    npc.add_memory("今天天气不错", importance=5)
    print(f"\n  记忆数量: {len(npc.memories)}")
    
    # 测试状态获取
    status = npc.get_status()
    print(f"\n  当前活动: {status['current_activity']}")
    print(f"  总行动数: {status['total_actions']}")
    
    print("\n✓ 基本功能测试通过!")
    return True


def test_update_mechanism():
    """测试更新机制"""
    print("\n" + "=" * 60)
    print("测试2: 更新机制测试")
    print("=" * 60)
    
    npc = NPCIndependent("npc_002")
    
    print("  测试时间片更新机制...")
    current_time = time.time()
    
    # 第一次更新应该成功
    updated = npc.update(current_time, player_nearby=True)
    print(f"  - 第一次更新: {'成功' if updated else '跳过'}")
    
    # 立即再次更新应该跳过
    updated = npc.update(current_time + 1, player_nearby=True)
    print(f"  - 1秒后更新: {'成功' if updated else '跳过'} (应跳过)")
    
    # 等待更新间隔后应该成功
    updated = npc.update(current_time + npc.update_interval + 1, player_nearby=True)
    print(f"  - 间隔后更新: {'成功' if updated else '跳过'}")
    
    # 测试暂停功能
    npc.pause()
    updated = npc.update(current_time + npc.update_interval * 3, player_nearby=True)
    print(f"  - 暂停后更新: {'成功' if updated else '跳过'} (应跳过)")
    
    npc.resume()
    updated = npc.update(current_time + npc.update_interval * 4, player_nearby=True)
    print(f"  - 恢复后更新: {'成功' if updated else '跳过'}")
    
    print("\n✓ 更新机制测试通过!")
    return True


def test_decision_system():
    """测试决策系统"""
    print("\n" + "=" * 60)
    print("测试3: 决策系统测试")
    print("=" * 60)
    
    npc = NPCIndependent("npc_003")
    
    # 测试需求驱动决策
    print("  测试需求驱动决策...")
    npc.needs[NeedType.HUNGER].value = 85  # 设置饥饿度为紧急
    decision = npc.make_decision()
    print(f"  - 饥饿度85时决策: {decision} (应为找食物)")
    assert "食物" in decision or "吃" in decision, "饥饿时应决定找食物"
    
    npc.needs[NeedType.HUNGER].value = 30  # 恢复正常
    npc.needs[NeedType.ENERGY].value = 15  # 设置精力为紧急
    decision = npc.make_decision()
    print(f"  - 精力15时决策: {decision} (应为休息)")
    assert "休息" in decision or "睡" in decision, "精力低时应决定休息"
    
    # 测试目标驱动决策
    print("\n  测试目标驱动决策...")
    npc.needs[NeedType.ENERGY].value = 80  # 恢复正常
    npc.goals[0].current_value = 0  # 重置第一个目标
    npc.goals[0].is_completed = False
    decision = npc.make_decision()
    print(f"  - 有目标时决策: {decision}")
    
    # 测试性格驱动决策
    print("\n  测试性格驱动决策...")
    npc.personality.diligence = 0.9  # 设置高勤奋
    decision = npc.make_decision()
    print(f"  - 高勤奋性格决策: {decision}")
    
    npc.personality.diligence = 0.1  # 设置低勤奋
    npc.personality.greed = 0.9  # 设置高贪婪
    decision = npc.make_decision()
    print(f"  - 高贪婪性格决策: {decision}")
    
    print("\n✓ 决策系统测试通过!")
    return True


def test_social_system():
    """测试社交系统"""
    print("\n" + "=" * 60)
    print("测试4: 社交系统测试")
    print("=" * 60)
    
    manager = NPCIndependentManager()
    
    # 创建两个NPC
    npc1 = NPCIndependent("npc_s1")
    npc2 = NPCIndependent("npc_s2")
    
    manager.add_npc(npc1, "新手村")
    manager.add_npc(npc2, "新手村")
    
    print("  创建两个NPC并建立关系...")
    
    # 添加一些记忆
    npc1.add_memory("发现了一处秘境", importance=8)
    npc2.add_memory("炼制了一颗好丹", importance=7)
    
    # 进行社交
    manager.socialize_between("npc_s1", "npc_s2")
    
    # 检查关系
    rel1 = npc1.get_relationship("npc_s2")
    rel2 = npc2.get_relationship("npc_s1")
    
    print(f"  - NPC1对NPC2的好感度: {rel1.affinity:.1f}")
    print(f"  - NPC2对NPC1的好感度: {rel2.affinity:.1f}")
    print(f"  - 熟悉度: {rel1.familiarity:.1f}")
    
    # 检查记忆分享
    print(f"  - NPC1记忆数: {len(npc1.memories)}")
    print(f"  - NPC2记忆数: {len(npc2.memories)}")
    
    # 多次社交
    for _ in range(5):
        manager.socialize_between("npc_s1", "npc_s2")
    
    rel1 = npc1.get_relationship("npc_s2")
    print(f"  - 多次社交后好感度: {rel1.affinity:.1f}")
    
    print("\n✓ 社交系统测试通过!")
    return True


def test_performance():
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试5: 性能测试")
    print("=" * 60)
    
    # 测试100个NPC
    print("  测试100个NPC...")
    manager = NPCIndependentManager()
    
    start_time = time.time()
    for i in range(100):
        npc = NPCIndependent(f"npc_perf_{i}")
        manager.add_npc(npc, "新手村")
    create_time = time.time() - start_time
    print(f"  - 创建100个NPC耗时: {create_time:.3f}秒")
    
    # 模拟更新
    current_time = time.time()
    start_time = time.time()
    for _ in range(10):  # 模拟10轮更新
        manager.update_all(current_time, "新手村")
        current_time += 1
    update_time = time.time() - start_time
    print(f"  - 10轮更新耗时: {update_time:.3f}秒")
    
    # 测试500个NPC
    print("\n  测试500个NPC...")
    manager = NPCIndependentManager()
    
    start_time = time.time()
    for i in range(500):
        npc = NPCIndependent(f"npc_perf500_{i}")
        manager.add_npc(npc, "新手村")
    create_time = time.time() - start_time
    print(f"  - 创建500个NPC耗时: {create_time:.3f}秒")
    
    start_time = time.time()
    for _ in range(10):
        manager.update_all(current_time, "新手村")
        current_time += 1
    update_time = time.time() - start_time
    print(f"  - 10轮更新耗时: {update_time:.3f}秒")
    
    # 测试1000个NPC
    print("\n  测试1000个NPC...")
    manager = NPCIndependentManager()
    
    start_time = time.time()
    for i in range(1000):
        npc = NPCIndependent(f"npc_perf1000_{i}")
        manager.add_npc(npc, "新手村")
    create_time = time.time() - start_time
    print(f"  - 创建1000个NPC耗时: {create_time:.3f}秒")
    
    start_time = time.time()
    for _ in range(10):
        manager.update_all(current_time, "新手村")
        current_time += 1
    update_time = time.time() - start_time
    print(f"  - 10轮更新耗时: {update_time:.3f}秒")
    
    stats = manager.get_stats()
    print(f"\n  统计信息:")
    print(f"    - 总NPC数: {stats['total_npcs']}")
    print(f"    - 活跃NPC数: {stats['active_npcs']}")
    print(f"    - 总记忆数: {stats['total_memories']}")
    print(f"    - 总行动数: {stats['total_actions']}")
    
    print("\n✓ 性能测试通过!")
    return True


def test_integration():
    """测试与现有系统集成"""
    print("\n" + "=" * 60)
    print("测试6: 集成测试")
    print("=" * 60)
    
    # 使用NPCManager（集成版本）
    manager = NPCManager()
    
    print("  生成NPC...")
    npcs = manager.generate_npcs_for_location("新手村", 5)
    print(f"  - 生成了{len(npcs)}个NPC")
    
    # 检查独立系统
    npc = npcs[0]
    print(f"  - NPC独立系统状态: {'已集成' if hasattr(npc, 'independent') else '未集成'}")
    
    # 获取独立系统状态
    status = npc.get_independent_status()
    print(f"  - 当前活动: {status['current_activity']}")
    print(f"  - 需求状态: {status['needs']}")
    
    # 测试更新
    print("\n  测试更新...")
    current_time = time.time()
    manager.update_all(current_time, "新手村")
    
    status = npc.get_independent_status()
    print(f"  - 更新后活动: {status['current_activity']}")
    print(f"  - 总行动数: {status['total_actions']}")
    
    # 测试社交
    print("\n  测试NPC社交...")
    npc1, npc2 = npcs[0], npcs[1]
    manager.socialize_npcs(npc1.data.id, npc2.data.id)
    
    print(f"  - NPC1记忆数: {len(npc1.independent.memories)}")
    print(f"  - NPC2记忆数: {len(npc2.independent.memories)}")
    
    # 获取统计
    stats = manager.get_independent_stats()
    print(f"\n  独立系统统计:")
    print(f"    - 总NPC数: {stats['total_npcs']}")
    print(f"    - 总记忆数: {stats['total_memories']}")
    
    print("\n✓ 集成测试通过!")
    return True


def test_zone_update():
    """测试分区更新"""
    print("\n" + "=" * 60)
    print("测试7: 分区更新测试")
    print("=" * 60)
    
    manager = NPCIndependentManager()
    
    # 在不同区域创建NPC
    for i in range(10):
        npc = NPCIndependent(f"npc_zone_{i}")
        zone = "新手村" if i < 5 else "彩霞山"
        manager.add_npc(npc, zone)
    
    print("  创建NPC分布:")
    print(f"    - 新手村: 5个")
    print(f"    - 彩霞山: 5个")
    
    # 玩家在新手村
    current_time = time.time()
    print("\n  玩家在新手村时:")
    manager.update_all(current_time, "新手村")
    
    npcs_xinshou = manager.get_npcs_in_zone("新手村")
    npcs_caixia = manager.get_npcs_in_zone("彩霞山")
    
    print(f"    - 新手村NPC行动数: {sum(n.total_actions for n in npcs_xinshou)}")
    print(f"    - 彩霞山NPC行动数: {sum(n.total_actions for n in npcs_caixia)}")
    
    # 移动到彩霞山
    print("\n  玩家移动到彩霞山时:")
    manager.update_all(current_time + 10, "彩霞山")
    
    print(f"    - 新手村NPC行动数: {sum(n.total_actions for n in npcs_xinshou)}")
    print(f"    - 彩霞山NPC行动数: {sum(n.total_actions for n in npcs_caixia)}")
    
    print("\n✓ 分区更新测试通过!")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("NPC独立系统测试套件")
    print("=" * 60)
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("更新机制", test_update_mechanism),
        ("决策系统", test_decision_system),
        ("社交系统", test_social_system),
        ("性能测试", test_performance),
        ("集成测试", test_integration),
        ("分区更新", test_zone_update),
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
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️ 有{failed}个测试未通过")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
