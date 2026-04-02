# 处决系统与动态材料规格文档

## Why
当前战斗系统缺少完整的处决机制和动态材料生成保存功能。需要实现死斗后的处决选择系统，支持玩家和NPC之间的生死抉择，同时实现战斗掉落材料的动态生成和数据库持久化。

## What Changes
- 新增动态材料生成系统 (`game/material_generator.py`)
- 新增处决系统 (`game/execution_system.py`)
- 新增死亡NPC管理 (`game/death_manager.py`)
- 扩展战斗结果处理，支持处决选择
- 扩展数据库支持动态材料和死亡NPC存储
- 新增处决相关CLI命令 (/处决, /饶恕)

## Impact
- 受影响模块: game/, interface/handlers/, storage/
- 新增文件: game/material_generator.py, game/execution_system.py, game/death_manager.py
- 修改文件: game/combat.py, game/npc_combat.py, interface/handlers/combat_handler.py, storage/database.py

## ADDED Requirements

### Requirement: 动态材料生成系统
系统 SHALL 支持战斗中动态生成材料并保存到数据库。

#### Scenario: 生成战斗材料
- **WHEN** 战斗胜利时
- **THEN** 根据敌人类型和境界动态生成材料属性
- **AND** 材料具有唯一ID和随机属性
- **AND** 材料保存到数据库的 materials 表

#### Scenario: 材料属性随机化
- **WHEN** 生成材料时
- **THEN** 材料品质根据敌人等级随机确定
- **AND** 材料属性（效果、价值）根据品质浮动
- **AND** 材料名称根据类型和品质生成

### Requirement: 处决系统
系统 SHALL 支持死斗胜利后选择处决或饶恕。

#### Scenario: 玩家选择处决NPC
- **WHEN** 玩家在死斗中战胜NPC
- **THEN** 系统提示选择 (/处决 或 /饶恕)
- **AND** 选择 /处决 后，NPC被标记为死亡
- **AND** 死亡NPC保留在数据库，但不再被读取
- **AND** 处决者获得额外奖励（业力变化、物品）

#### Scenario: 玩家饶恕NPC
- **WHEN** 玩家在死斗中战胜NPC并选择 /饶恕
- **THEN** NPC保留1点生命值
- **AND** NPC对玩家好感度大幅提升
- **AND** NPC获得"被饶恕"记忆

#### Scenario: NPC处决玩家
- **WHEN** NPC在死斗中战胜玩家
- **THEN** 根据NPC性格决定是否处决
- **AND** 邪恶NPC高概率处决玩家
- **AND** 玩家死亡后进入轮回/转世系统

#### Scenario: NPC之间处决
- **WHEN** NPC在死斗中战胜另一个NPC
- **THEN** 根据AI性格决定是否处决
- **AND** 处决后败者标记为死亡
- **AND** 胜者获得败者全部物品

### Requirement: 死亡NPC管理
系统 SHALL 管理死亡NPC的数据。

#### Scenario: NPC死亡标记
- **WHEN** NPC被处决
- **THEN** 在数据库中标记 is_alive = False
- **AND** 记录死亡时间、死亡原因、处决者
- **AND** 保留NPC全部数据用于可能的复活

#### Scenario: 死亡NPC不显示
- **WHEN** 系统加载NPC列表时
- **THEN** 自动过滤 is_alive = False 的NPC
- **AND** 死亡NPC不在游戏中出现
- **AND** 死亡NPC不参与任何游戏活动

#### Scenario: NPC复活可能性
- **WHEN** 有复活手段时（如大还丹、复活术）
- **THEN** 可以复活死亡NPC
- **AND** 复活后NPC恢复 is_alive = True
- **AND** NPC保留死亡前的记忆

### Requirement: 业力系统
系统 SHALL 根据处决行为影响业力。

#### Scenario: 处决增加业力
- **WHEN** 玩家处决NPC
- **THEN** 根据NPC善恶属性增加业力
- **AND** 处决邪恶NPC增加善业
- **AND** 处决善良NPC增加恶业

#### Scenario: 饶恕减少业力
- **WHEN** 玩家饶恕NPC
- **THEN** 根据NPC善恶属性减少业力
- **AND** 饶恕邪恶NPC增加大量善业
- **AND** 饶恕善良NPC小幅增加善业

## MODIFIED Requirements

### Requirement: 战斗结果处理扩展
战斗系统 SHALL 扩展支持处决选择。

#### Changes:
- 死斗胜利后添加处决/饶恕选择阶段
- 战斗结果包含处决状态
- 奖励根据是否处决调整

### Requirement: NPC数据库扩展
NPC数据 SHALL 支持死亡状态存储。

#### Changes:
- 添加 is_alive 字段（默认True）
- 添加 death_info 字段记录死亡信息
- 添加 can_resurrect 字段标记是否可复活

### Requirement: 数据库扩展
数据库 SHALL 支持新材料表和死亡NPC存储。

#### Changes:
- 新增 materials 表存储动态材料
- 扩展 npcs 表添加死亡相关字段
- 新增 death_records 表记录死亡日志

## REMOVED Requirements
无
