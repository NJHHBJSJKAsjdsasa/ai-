# NPC关系功能完善规范

## Why
当前NPC关系系统存在以下问题：
1. NPC之间的关系数据存储在内存中，没有持久化到数据库
2. NPC关系网络系统(`npc_relationship_network.py`)与NPC核心类(`core.py`)集成不完整
3. NPC面板中的关系查看功能使用的是模拟数据而非真实数据
4. 缺少NPC之间关系的自动建立和维护机制
5. 社交系统(`social_system.py`)主要面向玩家，NPC之间的社交关系管理不完善

## What Changes
- **新增** NPC关系数据库表，持久化存储NPC之间的关系数据
- **修改** NPC核心类，集成完整的关系网络功能
- **修改** NPC管理器，添加关系维护和同步机制
- **修改** NPC面板，使用真实关系数据展示
- **新增** NPC关系自动建立机制（基于门派、位置、性格等因素）
- **新增** NPC关系事件系统，记录关系变化历史

## Impact
- 受影响代码：
  - `game/npc_relationship_network.py` - 需要完善数据库集成
  - `game/npc/core.py` - 需要集成关系网络
  - `game/npc/manager.py` - 需要添加关系维护
  - `storage/database.py` - 需要添加关系表
  - `interface/gui/panels/npc_panel.py` - 需要使用真实数据
- 新增数据库表：`npc_relations` - 存储NPC间关系

## ADDED Requirements

### Requirement: NPC关系数据持久化
系统 SHALL 将NPC之间的关系数据持久化存储到数据库。

#### Scenario: 关系数据保存
- **WHEN** NPC之间的关系发生变化
- **THEN** 变化应该被保存到数据库

#### Scenario: 关系数据加载
- **WHEN** 游戏加载时
- **THEN** NPC之间的关系应该从数据库恢复

### Requirement: NPC关系自动建立
系统 SHALL 根据NPC的属性自动建立初始关系。

#### Scenario: 同门派关系
- **WHEN** 两个NPC属于同一门派
- **THEN** 应该自动建立友好关系

#### Scenario: 同位置关系
- **WHEN** 两个NPC在同一位置
- **THEN** 应该建立熟人关系

#### Scenario: 性格匹配关系
- **WHEN** 两个NPC性格互补
- **THEN** 应该建立更好的关系

### Requirement: NPC关系动态变化
系统 SHALL 根据NPC交互动态更新关系。

#### Scenario: 社交提升关系
- **WHEN** 两个NPC进行社交
- **THEN** 根据社交结果更新关系值

#### Scenario: 战斗影响关系
- **WHEN** NPC之间发生战斗
- **THEN** 根据战斗结果更新关系值

### Requirement: NPC关系查询接口
系统 SHALL 提供完整的NPC关系查询接口。

#### Scenario: 获取NPC关系列表
- **WHEN** 查询某个NPC的所有关系
- **THEN** 返回该NPC的所有关系数据

#### Scenario: 获取两个NPC关系
- **WHEN** 查询两个NPC之间的关系
- **THEN** 返回具体的关系数据

## MODIFIED Requirements

### Requirement: NPC核心类关系功能
NPC核心类 SHALL 集成完整的关系网络功能。

#### Scenario: 关系数据访问
- **WHEN** 通过NPC对象访问关系
- **THEN** 应该返回真实的关系数据

#### Scenario: 关系更新
- **WHEN** 通过NPC对象更新关系
- **THEN** 应该同步更新数据库

## REMOVED Requirements
无
