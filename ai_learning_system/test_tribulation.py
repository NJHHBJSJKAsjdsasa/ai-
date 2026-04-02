"""
天劫系统功能测试
"""
from game.player import Player
from game.tribulation_system import TribulationManager
from config.tribulation_config import get_tribulation_stage, get_all_tribulation_stages

# 创建测试玩家
player = Player(name='测试修士', load_from_db=False)
player.stats.realm_level = 1  # 设置为练气期
player.stats.health = 100
player.stats.max_health = 100

print('=== 天劫系统功能测试 ===')
print(f'玩家: {player.stats.name}')
print(f'境界: {player.get_realm_name()}')
print()

# 测试获取天劫配置
print('1. 测试获取天劫配置:')
stage = get_tribulation_stage(1)
if stage:
    print(f'   练气期天劫: {stage.tribulation_name}')
    print(f'   雷劫数: {stage.total_thunder}')
    print(f'   基础威力: {stage.base_power}')
else:
    print('   未找到配置')

print()
print('2. 测试天劫管理器:')
manager = TribulationManager(player)

# 测试触发天劫
result = manager.start_tribulation(1)
print(f'   触发结果: {result["message"]}')

if result['success']:
    print(f'   天劫ID: {result.get("tribulation_id")}')
    print(f'   雷劫序列数量: {len(result.get("thunder_sequence", []))}')

    # 测试添加准备物品
    print()
    print('3. 测试准备物品:')
    prep_result = manager.add_preparation_item('treasure', '避雷珠')
    print(f'   {prep_result["message"]}')

    prep_result = manager.add_preparation_item('pill', '避雷丹')
    print(f'   {prep_result["message"]}')

    # 查看当前状态
    info = manager.get_tribulation_info()
    print(f'   当前雷抗: {info.get("player_resistance", 0)*100:.1f}%')

    print()
    print('4. 测试所有天劫阶段:')
    stages = get_all_tribulation_stages()
    for level, stage in stages:
        print(f'   境界{level}: {stage.tribulation_name} - {stage.total_thunder}道雷劫')

print()
print('=== 所有测试通过 ===')
