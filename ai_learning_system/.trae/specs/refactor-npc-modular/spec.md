# NPC模块重构规范

## Why
`npc.py` 文件当前超过1400行，包含多个类（NPCMemory, NPCData, NPC, NPCManager）以及大量功能。这种单一文件结构导致：
1. 代码维护困难，定位特定功能耗时
2. 职责不清晰，一个文件承担过多责任
3. 测试困难，难以单独测试特定组件
4. 扩展性差，新增功能容易导致文件更加臃肿

通过模块化重构，将NPC系统拆分为独立的子模块，提高代码的可维护性和可扩展性。

## What Changes
- **新增** `npc/` 目录作为NPC模块的根目录
- **拆分** `NPCMemory` 和 `NPCData` 数据类到 `npc/models.py`
- **拆分** `NPC` 类的核心逻辑到 `npc/core.py`
- **拆分** `NPCManager` 管理器到 `npc/manager.py`
- **创建** `npc/__init__.py` 统一导出接口
- **保留** 原有导入路径的兼容性（通过 `npc.py` 重定向）
- **保留** 所有现有功能不变

## Impact
- 受影响代码：`game/npc.py` 将被重构
- 受影响导入：所有导入 `game.npc` 的模块
- 新增文件：
  - `game/npc/__init__.py`
  - `game/npc/models.py`
  - `game/npc/core.py`
  - `game/npc/manager.py`

## ADDED Requirements

### Requirement: 模块结构
系统 SHALL 提供清晰的模块结构，将NPC相关功能按职责分离。

#### Scenario: 数据模型分离
- **WHEN** 需要访问NPC数据类
- **THEN** 可以从 `game.npc.models` 导入 `NPCMemory` 和 `NPCData`

#### Scenario: 核心逻辑分离
- **WHEN** 需要创建或操作NPC实例
- **THEN** 可以从 `game.npc.core` 导入 `NPC` 类

#### Scenario: 管理器分离
- **WHEN** 需要管理多个NPC
- **THEN** 可以从 `game.npc.manager` 导入 `NPCManager`

#### Scenario: 向后兼容
- **WHEN** 现有代码导入 `from game.npc import NPC`
- **THEN** 导入应该继续正常工作

### Requirement: 功能完整性
系统 SHALL 保持所有现有功能不变。

#### Scenario: 功能等价性
- **WHEN** 重构完成后
- **THEN** 所有NPC相关功能（生成、交互、战斗、记忆等）应该与重构前完全一致

#### Scenario: 序列化兼容
- **WHEN** 加载已保存的NPC数据
- **THEN** 应该能够正确反序列化，数据不丢失

## MODIFIED Requirements
无

## REMOVED Requirements
无
