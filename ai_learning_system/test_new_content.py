#!/usr/bin/env python3
"""
测试新添加的游戏内容
"""

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试新地点
from config.game_config import GAME_CONFIG
print('=== 测试新地点 ===')
locations = GAME_CONFIG['world']['locations']
found_qingqiu = False
for loc in locations:
    if loc['name'] == '青丘山':
        found_qingqiu = True
        print('✅ 找到新地点: 青丘山')
        print(f'描述: {loc["description"]}')
        print(f'境界要求: {loc["realm_required"]}')
        print(f'危险等级: {loc["danger_level"]}')
        print(f'地点类型: {loc["location_type"]}')
        print(f'父地点: {loc["parent_location"]}')
if not found_qingqiu:
    print('❌ 未找到新地点: 青丘山')

# 测试新功法
from config.techniques import TECHNIQUES_DB
print('\n=== 测试新功法 ===')
if '狐仙决' in TECHNIQUES_DB:
    technique = TECHNIQUES_DB['狐仙决']
    print('✅ 找到新功法: 狐仙决')
    print(f'描述: {technique.description}')
    print(f'功法类型: {technique.technique_type.value}')
    print(f'属性: {technique.element.value}')
    print(f'所需境界: {technique.realm_required}')
    print(f'效果: {technique.effects}')
else:
    print('❌ 未找到新功法: 狐仙决')

# 测试新道具
from config.items import ITEMS_DB
print('\n=== 测试新道具 ===')
if '狐仙内丹' in ITEMS_DB:
    item = ITEMS_DB['狐仙内丹']
    print('✅ 找到新道具: 狐仙内丹')
    print(f'描述: {item.description}')
    print(f'道具类型: {item.item_type.value}')
    print(f'稀有度: {item.rarity.value}')
    print(f'效果: {item.effects}')
    print(f'价值: {item.value} 灵石')
else:
    print('❌ 未找到新道具: 狐仙内丹')

# 测试新NPC属性
from game.npc.models import NPCData
print('\n=== 测试新NPC属性 ===')
try:
    # 创建一个狐仙NPC测试
    fox_fairy = NPCData(
        id='test_fox_fairy',
        name='白灵',
        dao_name='青丘仙子',
        age=500,
        lifespan=1000,
        realm_level=3,
        sect='青丘山',
        personality='温柔善良',
        occupation='狐仙',
        location='青丘山',
        race='狐族',
        special_trait='化形能力',
        unique_ability='魅惑术'
    )
    print('✅ 成功创建狐仙NPC')
    print(f'种族: {fox_fairy.race}')
    print(f'特殊特质: {fox_fairy.special_trait}')
    print(f'独特能力: {fox_fairy.unique_ability}')
except Exception as e:
    print(f'❌ 创建NPC失败: {e}')

print('\n=== 测试完成 ===')
