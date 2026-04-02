# Tasks

- [x] Task 1: 创建热更新管理器核心模块
  - [x] SubTask 1.1: 创建 `core/hot_reload_manager.py`，实现文件变更检测
  - [x] SubTask 1.2: 实现模块重新加载逻辑，使用 `importlib.reload`
  - [x] SubTask 1.3: 添加错误处理和回滚机制

- [x] Task 2: 创建模块重载器
  - [x] SubTask 2.1: 创建 `core/module_reloader.py`，封装安全的模块重载
  - [x] SubTask 2.2: 实现处理器模块的特殊重载逻辑（保持handler实例状态）
  - [x] SubTask 2.3: 添加模块依赖追踪，确保按正确顺序重载

- [x] Task 3: 集成到CLI主循环
  - [x] SubTask 3.1: 在 `interface/cli.py` 中初始化热更新管理器
  - [x] SubTask 3.2: 在主循环中添加热更新检查（每次命令前或定时检查）
  - [x] SubTask 3.3: 添加热更新状态显示（如有变更提示用户）

- [x] Task 4: 添加 `/热更新` 命令
  - [x] SubTask 4.1: 在 `interface/cli.py` 添加热更新命令处理
  - [x] SubTask 4.2: 实现手动触发重载功能
  - [x] SubTask 4.3: 显示重载结果报告（成功/失败的模块列表）

- [x] Task 5: 支持处理器模块热更新
  - [x] SubTask 5.1: 修改 `BaseHandler` 支持重新初始化
  - [x] SubTask 5.2: 确保处理器重新加载后保持对player/world的引用
  - [x] SubTask 5.3: 测试各handler（cultivation, combat, npc等）的热更新

- [x] Task 6: 测试和验证
  - [x] SubTask 6.1: 测试语法错误保护机制
  - [x] SubTask 6.2: 测试数据保持功能（玩家状态不丢失）
  - [x] SubTask 6.3: 测试手动和自动两种触发方式

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 2
- Task 4 依赖于 Task 2
- Task 5 依赖于 Task 3
- Task 6 依赖于 Task 5
