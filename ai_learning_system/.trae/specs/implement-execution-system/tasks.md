# 处决系统与动态材料开发任务列表

## 任务1: 创建动态材料生成系统
- [x] 创建 `game/material_generator.py` 文件
  - [x] 定义 MaterialRarity 枚举 (普通/优秀/稀有/史诗/传说)
  - [x] 定义 GeneratedMaterial 数据类
  - [x] 实现 generate_material() 函数
  - [x] 实现 generate_material_name() 函数
  - [x] 实现 calculate_material_stats() 函数
  - [x] 实现 get_material_quality_text() 函数

## 任务2: 创建处决系统
- [x] 创建 `game/execution_system.py` 文件
  - [x] 定义 ExecutionChoice 枚举 (处决/饶恕)
  - [x] 定义 ExecutionResult 数据类
  - [x] 实现 ExecutionSystem 类
  - [x] 实现 prompt_execution_choice() 方法 (提示玩家选择)
  - [x] 实现 execute_npc() 方法 (执行处决)
  - [x] 实现 spare_npc() 方法 (执行饶恕)
  - [x] 实现 calculate_karma_change() 方法 (计算业力变化)

## 任务3: 创建死亡NPC管理系统
- [x] 创建 `game/death_manager.py` 文件
  - [x] 定义 DeathRecord 数据类
  - [x] 实现 DeathManager 类
  - [x] 实现 mark_npc_dead() 方法 (标记NPC死亡)
  - [x] 实现 get_dead_npcs() 方法 (获取死亡NPC列表)
  - [x] 实现 can_resurrect() 方法 (检查是否可复活)
  - [x] 实现 resurrect_npc() 方法 (复活NPC)
  - [x] 实现 filter_alive_npcs() 方法 (过滤存活NPC)

## 任务4: 扩展数据库支持
- [x] 修改 `storage/database.py`
  - [x] 创建 materials 表
  - [x] 扩展 npcs 表添加死亡相关字段
  - [x] 创建 death_records 表
  - [x] 实现 save_material() 方法
  - [x] 实现 load_material() 方法
  - [x] 实现 save_death_record() 方法
  - [x] 实现 load_alive_npcs_only() 方法

## 任务5: 扩展NPC数据结构
- [x] 修改 `game/npc.py`
  - [x] 在 NPCData 中添加 is_alive 字段 (默认True)
  - [x] 添加 death_info 字段 (记录死亡信息)
  - [x] 添加 can_resurrect 字段 (默认True)
  - [x] 添加 morality 字段 (善恶值 -100到100)
  - [x] 实现 mark_as_dead() 方法
  - [x] 实现 resurrect() 方法

## 任务6: 扩展战斗结果处理
- [x] 修改 `game/combat.py`
  - [x] 在 CombatResult 中添加 execution_pending 字段
  - [x] 在 CombatResult 中添加 can_execute 字段
  - [x] 修改战斗结束逻辑，支持处决选择

## 任务7: 扩展NPC战斗系统
- [x] 修改 `game/npc_combat.py`
  - [x] 实现 NPC处决决策逻辑
  - [x] 根据NPC性格决定是否处决
  - [x] 实现 NPC处决玩家逻辑
  - [x] 实现 NPC之间处决逻辑
  - [x] 集成 DeathManager

## 任务8: 扩展战斗命令处理器
- [x] 修改 `interface/handlers/combat_handler.py`
  - [x] 实现 handle_execute() 方法 (/处决)
  - [x] 实现 handle_spare() 方法 (/饶恕)
  - [x] 修改死斗结束处理，添加处决选择提示
  - [x] 集成 MaterialGenerator 生成动态材料
  - [x] 集成 ExecutionSystem

## 任务9: 集成到CLI
- [x] 修改 `interface/cli.py`
  - [x] 添加 /处决 命令映射
  - [x] 添加 /饶恕 命令映射
  - [x] 在 help 中添加处决命令说明

## 任务10: 扩展玩家业力系统
- [x] 修改 `game/player.py`
  - [x] 添加 karma 字段 (业力值)
  - [x] 实现 add_karma() 方法
  - [x] 实现 get_karma_level() 方法

## 任务11: 测试处决系统
- [x] 测试玩家处决NPC
- [x] 测试玩家饶恕NPC
- [x] 测试NPC处决玩家
- [x] 测试NPC之间处决
- [x] 测试动态材料生成
- [x] 测试死亡NPC过滤
- [x] 测试业力变化

# 任务依赖关系
- 任务4 依赖 任务1, 任务2, 任务3
- 任务5 依赖 任务3
- 任务6 依赖 任务2
- 任务7 依赖 任务3, 任务5
- 任务8 依赖 任务2, 任务6, 任务7
- 任务9 依赖 任务8
- 任务10 依赖 任务8
- 任务11 依赖 所有其他任务
