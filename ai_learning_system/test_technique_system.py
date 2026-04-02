#!/usr/bin/env python3
"""
测试功法系统的各项功能
"""

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game.player import Player
from config.techniques import (
    get_technique, get_techniques_by_realm, 
    get_techniques_by_element, get_techniques_by_type,
    can_learn_technique, calculate_learning_success_rate,
    get_technique_combos, calculate_combo_bonuses
)

print('=== 功法系统测试 ===')

# 测试1: 功法基本信息
def test_technique_basic():
    print('\n1. 测试功法基本信息')
    # 测试获取功法
    technique = get_technique('狐仙决')
    if technique:
        print('✅ 成功获取狐仙决')
        print(f'  名称: {technique.name}')
        print(f'  描述: {technique.description}')
        print(f'  类型: {technique.technique_type.value}')
        print(f'  属性: {technique.element.value}')
        print(f'  所需境界: {technique.realm_required}')
        print(f'  学习难度: {technique.learning_difficulty}')
        print(f'  修炼速度加成: {technique.cultivation_speed_bonus}')
        print(f'  战斗力加成: {technique.combat_power_bonus}')
        print(f'  特殊能力: {technique.special_abilities}')
        
        # 测试新方法
        print('\n  功法效果描述:')
        print(technique.get_effect_description())
        print('\n  特殊能力描述:')
        print(technique.get_special_abilities_description())
        
        # 测试使用条件
        print('\n  使用条件测试:')
        print(f'  筑基期(2)，50灵力: {technique.can_use(2, 50)}')
        print(f'  练气期(1)，50灵力: {technique.can_use(1, 50)}')
        print(f'  筑基期(2)，5灵力: {technique.can_use(2, 5)}')
    else:
        print('❌ 无法获取狐仙决')

# 测试2: 功法获取方法
def test_technique_retrieval():
    print('\n2. 测试功法获取方法')
    # 按境界获取
    techniques_by_realm = get_techniques_by_realm(2)  # 筑基期
    print(f'  筑基期可学功法数量: {len(techniques_by_realm)}')
    print('  功法列表:', [t.name for t in techniques_by_realm])
    
    # 按属性获取
    from config.techniques import ElementType
    techniques_by_element = get_techniques_by_element(ElementType.WOOD)
    print(f'  木属性功法数量: {len(techniques_by_element)}')
    print('  功法列表:', [t.name for t in techniques_by_element])
    
    # 按类型获取
    from config.techniques import TechniqueType
    techniques_by_type = get_techniques_by_type(TechniqueType.CULTIVATION)
    print(f'  修炼功法数量: {len(techniques_by_type)}')
    print('  功法列表:', [t.name for t in techniques_by_type])

# 测试3: 功法学习条件
def test_technique_learning_conditions():
    print('\n3. 测试功法学习条件')
    # 测试学习条件
    test_cases = [
        ('长春功', 1, 'mu', True),  # 练气期，木灵根
        ('青元剑诀', 1, 'mu', False),  # 练气期（不足），木灵根
        ('青元剑诀', 2, 'mu', True),  # 筑基期，木灵根
        ('狐仙决', 2, 'mu', True),  # 筑基期，木灵根
        ('狐仙决', 1, 'mu', False),  # 练气期（不足），木灵根
        ('狐仙决', 2, 'wu', True),  # 筑基期，五灵根
    ]
    
    for technique_name, realm, spirit_root, expected in test_cases:
        result = can_learn_technique(technique_name, realm, spirit_root)
        status = '✅' if result == expected else '❌'
        print(f'  {status} {technique_name} - 境界{realm}, {spirit_root}灵根: {result}')

# 测试4: 功法学习成功率
def test_learning_success_rate():
    print('\n4. 测试学习成功率计算')
    test_cases = [
        ('长春功', 1, 50),  # 练气期，普通悟性
        ('青元剑诀', 2, 70),  # 筑基期，高悟性
        ('狐仙决', 2, 60),  # 筑基期，中等悟性
        ('大衍决', 4, 80),  # 元婴期，高悟性
    ]
    
    for technique_name, realm, comprehension in test_cases:
        rate = calculate_learning_success_rate(technique_name, realm, comprehension)
        print(f'  {technique_name} - 境界{realm}, 悟性{comprehension}: {rate:.2f}')

# 测试5: 玩家学习和练习功法
def test_player_technique_system():
    print('\n5. 测试玩家功法系统')
    # 创建玩家
    player = Player('测试修士', load_from_db=False)
    player.stats.realm_level = 2  # 筑基期
    player.stats.spirit_root = 'mu'  # 木灵根
    player.stats.fortune = 60  # 中等福缘
    
    print(f'  玩家: {player.stats.name}')
    print(f'  境界: {player.get_realm_name()}')
    print(f'  灵根: {player.get_spirit_root_name()}')
    
    # 测试学习功法
    techniques_to_learn = ['长春功', '狐仙决', '青元剑诀']
    for technique_name in techniques_to_learn:
        success, message = player.learn_technique(technique_name)
        status = '✅' if success else '❌'
        print(f'  {status} 学习{technique_name}: {message}')
    
    # 测试练习功法
    print('\n  测试练习功法:')
    for technique_name in techniques_to_learn:
        if technique_name in player.techniques.learned_techniques:
            success = player.practice_technique(technique_name)
            status = '✅' if success else '❌'
            mastery = player.techniques.get_mastery(technique_name)
            level = player.techniques.get_technique_level(technique_name)
            evaluation = player.techniques.get_technique_evaluation(technique_name)
            print(f'  {status} 练习{technique_name}: 等级{level}级, 熟练度{mastery:.1%}, 评价: {evaluation}')
        else:
            print(f'  ⚠️  未学习{technique_name}')
    
    # 测试功法加成
    cultivation_speed = player.get_cultivation_speed()
    combat_bonus = player.get_combat_power_bonus()
    print(f'\n  修炼速度: {cultivation_speed:.2f}')
    print(f'  战斗力加成: {combat_bonus:.2f}')
    
    # 测试已学功法
    learned_techniques = player.get_learned_techniques()
    print(f'\n  已学功法数量: {len(learned_techniques)}')
    for name, data in learned_techniques.items():
        info = player.techniques.get_technique_info(name)
        if info:
            print(f'  {name} - 等级: {info["level"]}, 熟练度: {player.techniques.get_mastery(name):.1%}, 类型: {info["technique_type"]}, 属性: {info.get("element", "无")}')

# 测试6: 功法组合效果
def test_technique_combos():
    print('\n6. 测试功法组合效果')
    # 测试木系精通组合
    wood_techniques = ['长春功', '青元剑诀', '狐仙决']
    wood_combos = get_technique_combos(wood_techniques)
    print(f'  木系功法组合: {list(wood_combos.keys())}')
    if wood_combos:
        for combo_name, combo_data in wood_combos.items():
            print(f'  组合效果: {combo_name}')
            print(f'  所需功法: {combo_data["required_techniques"]}')
            print(f'  效果: {combo_data["effects"]}')
            
    # 测试战斗大师组合
    combat_techniques = ['眨眼剑法', '青元剑诀', '火球术']
    combat_combos = get_technique_combos(combat_techniques)
    print(f'\n  战斗功法组合: {list(combat_combos.keys())}')
    if combat_combos:
        for combo_name, combo_data in combat_combos.items():
            print(f'  组合效果: {combo_name}')
            print(f'  所需功法: {combo_data["required_techniques"]}')
            print(f'  效果: {combo_data["effects"]}')
    
    # 测试组合加成计算
    total_bonuses = calculate_combo_bonuses(wood_combos)
    print(f'\n  组合总加成:')
    for bonus_type, value in total_bonuses.items():
        if value > 0:
            print(f'  {bonus_type}: {value:.2f}')

# 运行所有测试
if __name__ == '__main__':
    test_technique_basic()
    test_technique_retrieval()
    test_technique_learning_conditions()
    test_learning_success_rate()
    test_player_technique_system()
    test_technique_combos()
    print('\n=== 功法系统测试完成 ===')
