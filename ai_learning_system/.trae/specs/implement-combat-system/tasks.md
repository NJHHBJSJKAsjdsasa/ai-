# 战斗系统开发任务列表

## 任务1: 创建战斗系统核心模块
- [x] 创建 `game/combat.py` 文件
  - [x] 定义 CombatMode 枚举 (SPAR=切磋, DEATHMATCH=死斗)
  - [x] 定义 CombatUnit 类 (战斗单位基类)
  - [x] 定义 CombatSkill 类 (战斗技能)
  - [x] 定义 CombatResult 类 (战斗结果)
  - [x] 定义 CombatSystem 类 (战斗管理器)
  - [x] 实现回合制战斗逻辑
  - [x] 实现伤害计算系统
  - [x] 实现战斗状态管理
  - [x] 实现切磋模式（生命值不低于1，结束后恢复）
  - [x] 实现死斗模式（可能死亡，掉落物品）

## 任务2: 创建NPC之间战斗系统
- [x] 创建 `game/npc_combat.py` 文件
  - [x] 定义 NPCCombatManager 类
  - [x] 实现 NPC之间切磋逻辑
  - [x] 实现 NPC之间死斗逻辑
  - [x] 实现 NPC与妖兽战斗逻辑
  - [x] 实现 门派冲突检测
  - [x] 实现 NPC战斗AI决策
  - [x] 实现 NPC战斗自动结算

## 任务3: 扩展玩家战斗属性
- [x] 修改 `game/player.py`
  - [x] 在 PlayerStats 中添加 attack 属性
  - [x] 在 PlayerStats 中添加 defense 属性
  - [x] 在 PlayerStats 中添加 speed 属性
  - [x] 在 PlayerStats 中添加 crit_rate 属性
  - [x] 在 PlayerStats 中添加 dodge_rate 属性
  - [x] 添加 combat_wins 属性（胜利次数）
  - [x] 添加 combat_losses 属性（失败次数）
  - [x] 实现 get_attack_power() 方法
  - [x] 实现 get_defense_power() 方法
  - [x] 实现 get_combat_stats() 方法

## 任务4: 扩展功法系统战斗属性
- [x] 修改 `config/techniques.py`
  - [x] 在 Technique 类中添加 is_combat_skill 属性
  - [x] 在 Technique 类中添加 mana_cost 属性
  - [x] 在 Technique 类中添加 cooldown 属性
  - [x] 在 Technique 类中添加 damage_type 属性 (PHYSICAL/MAGIC/TRUE)
  - [x] 更新现有功法数据，添加战斗相关属性

## 任务5: 扩展NPC系统战斗功能
- [x] 修改 `game/npc.py`
  - [x] 在 NPCData 中添加战斗属性
  - [x] 添加 get_combat_power() 方法
  - [x] 添加 combat_ai_config 属性
  - [x] 添加 combat_record 属性
- [x] 修改 `game/npc_independent.py`
  - [x] 添加自主战斗决策逻辑
  - [x] 添加与其他NPC互动时触发战斗的概率
  - [x] 集成 NPCCombatManager

## 任务6: 创建战斗命令处理器
- [x] 创建 `interface/handlers/combat_handler.py` 文件
  - [x] 创建 CombatHandler 类继承 BaseHandler
  - [x] 实现 handle_combat() 方法 (发起战斗，选择模式)
  - [x] 实现 handle_spar() 方法 (发起切磋)
  - [x] 实现 handle_deathmatch() 方法 (发起死斗)
  - [x] 实现 handle_attack() 方法 (普通攻击)
  - [x] 实现 handle_skill() 方法 (使用技能)
  - [x] 实现 handle_flee() 方法 (逃跑)
  - [x] 实现 handle_combat_status() 方法 (查看战斗状态)
  - [x] 实现 _display_combat_ui() 方法 (显示战斗界面)
  - [x] 实现 _display_spar_result() 方法 (显示切磋结果)
  - [x] 实现 _display_deathmatch_result() 方法 (显示死斗结果)

## 任务7: 集成战斗系统到CLI
- [x] 修改 `interface/cli.py`
  - [x] 导入 CombatHandler
  - [x] 在 __init__ 中初始化 combat_handler
  - [x] 添加战斗相关命令映射:
    - `/战斗` 或 `/combat` -> handle_combat
    - `/切磋` 或 `/spar` -> handle_spar
    - `/死斗` 或 `/deathmatch` -> handle_deathmatch
    - `/攻击` 或 `/attack` -> handle_attack
    - `/技能` 或 `/skill` -> handle_skill
    - `/逃跑` 或 `/flee` -> handle_flee
  - [x] 在 _is_game_command() 中添加战斗命令
  - [x] 在 _convert_to_command() 中添加战斗命令映射
  - [x] 在 display_help() 中添加战斗命令说明

## 任务8: 更新处理器模块导出
- [x] 修改 `interface/handlers/__init__.py`
  - [x] 导入 CombatHandler
  - [x] 将 CombatHandler 添加到 __all__ 列表

## 任务9: 创建妖兽/敌人数据
- [x] 创建 `config/enemies.py` 文件
  - [x] 定义 Enemy 数据类
  - [x] 定义 Beast 数据类 (继承 Enemy)
  - [x] 定义 BeastType 枚举
  - [x] 创建常见妖兽数据库 (至少10种)
  - [x] 实现根据境界生成敌人方法
  - [x] 实现敌人战利品掉落配置
  - [x] 实现妖兽AI配置

## 任务10: 实现战斗奖励系统
- [x] 修改 `game/combat.py`
  - [x] 实现 calculate_spar_rewards() 方法 (切磋奖励)
  - [x] 实现 calculate_deathmatch_rewards() 方法 (死斗奖励)
  - [x] 实现掉落物品生成逻辑
  - [x] 实现经验值计算逻辑
- [x] 修改 `game/npc_combat.py`
  - [x] 实现 NPC战斗奖励分配

## 任务11: 测试战斗系统
- [x] 运行游戏并测试以下功能:
  - [x] 发起切磋命令
  - [x] 发起死斗命令
  - [x] 与妖兽战斗
  - [x] 普通攻击
  - [x] 使用技能
  - [x] 逃跑功能
  - [x] 切磋结束后状态恢复
  - [x] 死斗胜利奖励
  - [x] 死斗失败处理
  - [x] NPC之间切磋
  - [x] NPC之间死斗
  - [x] NPC与妖兽战斗

# 任务依赖关系
- 任务3 依赖 任务1
- 任务4 依赖 任务1
- 任务5 依赖 任务1, 任务2
- 任务6 依赖 任务1, 任务3, 任务4, 任务5
- 任务7 依赖 任务6
- 任务8 依赖 任务6
- 任务9 依赖 任务1
- 任务10 依赖 任务1, 任务9
- 任务11 依赖 所有其他任务
