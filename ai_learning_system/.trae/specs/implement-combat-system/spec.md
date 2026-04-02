# 战斗系统规格文档

## Why
当前游戏缺少完整的战斗功能，玩家无法与妖兽或其他修士进行战斗交互。需要实现一个模块化的战斗系统，支持玩家与NPC/妖兽的战斗（切磋与死斗两种模式），同时支持NPC之间的自主战斗，整合到现有的游戏架构中，提供丰富的战斗体验。

## What Changes
- 新增战斗系统核心模块 (`game/combat.py`)
- 新增战斗命令处理器 (`interface/handlers/combat_handler.py`)
- 新增战斗相关数据模型 (战斗单位、技能效果、战斗记录等)
- 新增战斗相关的CLI命令 (/战斗, /切磋, /死斗, /技能, /逃跑 等)
- 新增NPC之间战斗系统 (`game/npc_combat.py`)
- 集成战斗系统到现有游戏循环中
- 扩展NPC独立系统，支持自主发起战斗

## Impact
- 受影响模块: game/, interface/handlers/, config/
- 新增文件: game/combat.py, game/npc_combat.py, interface/handlers/combat_handler.py
- 修改文件: interface/cli.py, interface/handlers/__init__.py, game/player.py, game/npc.py, game/npc_independent.py

## ADDED Requirements

### Requirement: 战斗核心系统
战斗系统 SHALL 提供完整的回合制战斗机制，支持切磋和死斗两种模式。

#### Scenario: 发起战斗
- **WHEN** 玩家使用 `/战斗 <目标>` 命令
- **THEN** 系统提示选择战斗模式（切磋/死斗）
- **AND** 检查目标是否存在且可战斗
- **AND** 初始化战斗场景
- **AND** 显示战斗开始信息

#### Scenario: 发起切磋
- **WHEN** 玩家使用 `/切磋 <目标>` 命令
- **THEN** 系统检查目标是否接受切磋
- **AND** 初始化切磋模式战斗
- **AND** 切磋模式下生命值不会归零（最低保留1点）
- **AND** 切磋结束后双方恢复战斗前状态

#### Scenario: 发起死斗
- **WHEN** 玩家使用 `/死斗 <目标>` 命令
- **THEN** 系统检查目标是否接受死斗（NPC根据好感度和性格决定）
- **AND** 初始化死斗模式战斗
- **AND** 死斗模式下可能死亡或重伤
- **AND** 胜利者获得大量奖励，失败者可能掉落物品

#### Scenario: 与妖兽战斗
- **WHEN** 玩家使用 `/战斗 <妖兽名>` 命令
- **THEN** 系统自动进入死斗模式（妖兽不会切磋）
- **AND** 战胜后获得妖兽材料和经验

#### Scenario: 战斗回合
- **WHEN** 战斗进行中
- **THEN** 玩家和敌人轮流行动（根据速度决定先手）
- **AND** 玩家可以选择使用普通攻击、技能、道具或逃跑
- **AND** 系统计算伤害并更新双方状态
- **AND** 显示战斗日志

#### Scenario: 战斗结束
- **WHEN** 一方生命值归零或玩家逃跑成功
- **THEN** 战斗结束
- **AND** 如果是切磋，双方恢复战斗前状态，获得少量经验
- **AND** 如果是死斗，胜利者获得经验和战利品，失败者可能死亡/重伤

### Requirement: 战斗技能系统
战斗系统 SHALL 支持使用已学习的功法作为战斗技能。

#### Scenario: 使用技能
- **WHEN** 玩家在战斗中使用 `/技能 <技能名>`
- **THEN** 检查玩家是否已学习该技能
- **AND** 检查灵力是否足够
- **AND** 计算技能伤害/效果
- **AND** 扣除相应灵力

#### Scenario: 技能效果
- **WHEN** 技能成功释放
- **THEN** 根据技能类型产生不同效果
- **AND** 攻击类技能造成伤害
- **AND** 辅助类技能提供增益效果
- **AND** 控制类技能限制敌人行动

### Requirement: NPC之间战斗系统
NPC系统 SHALL 支持NPC之间自主发起战斗。

#### Scenario: NPC发起切磋
- **WHEN** 两个NPC在同一地点且关系良好
- **THEN** 有概率发起切磋战斗
- **AND** 切磋不影响双方关系
- **AND** 双方获得少量经验

#### Scenario: NPC发起死斗
- **WHEN** 两个NPC有深仇大恨（好感度极低）
- **THEN** 有概率发起死斗战斗
- **AND** 死斗结果影响双方生死
- **AND** 胜者获得败者的部分物品

#### Scenario: NPC与妖兽战斗
- **WHEN** NPC在野外探索时遇到妖兽
- **THEN** 根据NPC性格和实力决定是否战斗
- **AND** 战斗结果自动计算
- **AND** 胜利NPC获得经验和材料

#### Scenario: 门派冲突战斗
- **WHEN** 不同门派的NPC相遇且门派关系敌对
- **THEN** 高概率发起死斗
- **AND** 战斗结果影响门派关系

### Requirement: 战斗奖励系统
战斗系统 SHALL 提供战斗胜利奖励。

#### Scenario: 切磋奖励
- **WHEN** 切磋结束
- **THEN** 双方获得少量经验值（胜利的更多）
- **AND** 不影响双方关系和状态

#### Scenario: 死斗胜利奖励
- **WHEN** 死斗胜利
- **THEN** 根据敌人强度获得大量经验值
- **AND** 获得灵石奖励
- **AND** 有机会获得敌人的物品/装备

#### Scenario: 妖兽战利品
- **WHEN** 战胜妖兽
- **THEN** 获得妖兽材料（可用于炼丹/炼器）
- **AND** 有机会获得妖兽内丹
- **AND** 战利品存入背包

### Requirement: 战斗AI系统
敌人 SHALL 拥有基本的战斗AI。

#### Scenario: 妖兽AI
- **WHEN** 妖兽回合
- **THEN** 根据妖兽类型选择攻击方式
- **AND** 攻击性妖兽优先使用高伤害技能
- **AND** 狡猾妖兽可能使用控制技能或逃跑

#### Scenario: NPC AI
- **WHEN** NPC回合
- **THEN** 根据NPC性格和境界选择行动
- **AND** 谨慎型NPC可能使用防御技能
- **AND** 好战型NPC优先攻击
- **AND** 低生命值时可能逃跑（死斗模式下不会）

## MODIFIED Requirements

### Requirement: 玩家属性扩展
玩家系统 SHALL 扩展战斗相关属性。

#### Changes:
- 添加攻击力属性 (基于境界和功法)
- 添加防御力属性 (基于境界和装备)
- 添加速度属性 (影响出手顺序)
- 添加暴击率和闪避率
- 添加战斗记录（胜负次数）

### Requirement: 功法系统扩展
功法系统 SHALL 支持战斗相关属性。

#### Changes:
- 功法添加战斗技能标识
- 功法添加灵力消耗属性
- 功法添加冷却回合属性
- 功法添加伤害类型（物理/法术/真实）

### Requirement: NPC系统扩展
NPC系统 SHALL 支持战斗功能。

#### Changes:
- NPC添加战斗属性（攻击力、防御力等）
- NPC添加战斗记录
- NPC添加战斗AI配置
- NPC独立系统添加自主战斗决策

## REMOVED Requirements
无
