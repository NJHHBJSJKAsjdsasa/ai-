# 处决系统与动态材料检查清单

## 动态材料生成系统

### Material Generator (`game/material_generator.py`)
- [x] MaterialRarity 枚举已定义
- [x] GeneratedMaterial 数据类已定义
- [x] generate_material() 函数已实现
- [x] generate_material_name() 函数已实现
- [x] calculate_material_stats() 函数已实现
- [x] get_material_quality_text() 函数已实现

## 处决系统

### Execution System (`game/execution_system.py`)
- [x] ExecutionChoice 枚举已定义
- [x] ExecutionResult 数据类已定义
- [x] ExecutionSystem 类已实现
- [x] prompt_execution_choice() 方法已实现
- [x] execute_npc() 方法已实现
- [x] spare_npc() 方法已实现
- [x] calculate_karma_change() 方法已实现

## 死亡NPC管理

### Death Manager (`game/death_manager.py`)
- [x] DeathRecord 数据类已定义
- [x] DeathManager 类已实现
- [x] mark_npc_dead() 方法已实现
- [x] get_dead_npcs() 方法已实现
- [x] can_resurrect() 方法已实现
- [x] resurrect_npc() 方法已实现
- [x] filter_alive_npcs() 方法已实现

## 数据库扩展

### Database (`storage/database.py`)
- [x] materials 表已创建
- [x] npcs 表已扩展死亡相关字段
- [x] death_records 表已创建
- [x] save_material() 方法已实现
- [x] load_material() 方法已实现
- [x] save_death_record() 方法已实现
- [x] load_alive_npcs_only() 方法已实现

## NPC数据结构扩展

### NPC (`game/npc.py`)
- [x] is_alive 字段已添加
- [x] death_info 字段已添加
- [x] can_resurrect 字段已添加
- [x] morality 字段已添加
- [x] mark_as_dead() 方法已实现
- [x] resurrect() 方法已实现

## 战斗系统扩展

### Combat (`game/combat.py`)
- [x] CombatResult 添加 execution_pending 字段
- [x] CombatResult 添加 can_execute 字段
- [x] 战斗结束逻辑支持处决选择

### NPC Combat (`game/npc_combat.py`)
- [x] NPC处决决策逻辑已实现
- [x] NPC处决玩家逻辑已实现
- [x] NPC之间处决逻辑已实现
- [x] DeathManager 已集成

## 命令处理器扩展

### Combat Handler (`interface/handlers/combat_handler.py`)
- [x] handle_execute() 方法已实现
- [x] handle_spare() 方法已实现
- [x] 死斗结束处理添加处决选择
- [x] MaterialGenerator 已集成
- [x] ExecutionSystem 已集成

## CLI集成

### CLI (`interface/cli.py`)
- [x] /处决 命令已映射
- [x] /饶恕 命令已映射
- [x] help 中添加处决命令说明

## 玩家业力系统

### Player (`game/player.py`)
- [x] karma 字段已添加
- [x] add_karma() 方法已实现
- [x] get_karma_level() 方法已实现

## 功能测试

### 处决功能
- [x] 玩家处决NPC正常工作
- [x] 玩家饶恕NPC正常工作
- [x] NPC处决玩家正常工作
- [x] NPC之间处决正常工作

### 材料系统
- [x] 动态材料生成正常工作
- [x] 材料保存到数据库正常
- [x] 材料属性随机化正常

### 死亡管理
- [x] NPC死亡标记正常
- [x] 死亡NPC过滤正常
- [x] NPC复活功能正常

### 业力系统
- [x] 处决业力变化正常
- [x] 饶恕业力变化正常
- [x] 业力等级显示正常
