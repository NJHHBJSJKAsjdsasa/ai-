# Tasks

- [x] Task 1: 创建NPC模块目录结构和 `__init__.py`
  - [x] SubTask 1.1: 创建 `game/npc/` 目录
  - [x] SubTask 1.2: 创建 `game/npc/__init__.py`，导出所有公共接口

- [x] Task 2: 拆分数据模型到 `models.py`
  - [x] SubTask 2.1: 将 `NPCMemory` 数据类迁移到 `game/npc/models.py`
  - [x] SubTask 2.2: 将 `NPCData` 数据类迁移到 `game/npc/models.py`
  - [x] SubTask 2.3: 确保所有导入和类型注解正确

- [x] Task 3: 拆分NPC核心逻辑到 `core.py`
  - [x] SubTask 3.1: 将 `NPC` 类迁移到 `game/npc/core.py`
  - [x] SubTask 3.2: 更新 `NPC` 类的导入语句，从相对路径导入 `NPCMemory` 和 `NPCData`
  - [x] SubTask 3.3: 确保所有方法、属性和内部引用正确

- [x] Task 4: 拆分NPC管理器到 `manager.py`
  - [x] SubTask 4.1: 将 `NPCManager` 类迁移到 `game/npc/manager.py`
  - [x] SubTask 4.2: 更新导入语句，从相对路径导入 `NPC` 类
  - [x] SubTask 4.3: 确保所有管理功能正确

- [x] Task 5: 创建向后兼容的 `npc.py` 重定向文件
  - [x] SubTask 5.1: 将原 `game/npc.py` 重命名为备份
  - [x] SubTask 5.2: 创建新的 `game/npc.py`，从 `game.npc` 重新导出所有公共接口

- [x] Task 6: 验证重构结果
  - [x] SubTask 6.1: 验证所有导入正常工作
  - [x] SubTask 6.2: 运行Python语法检查确保无错误

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 2
- Task 4 依赖于 Task 3
- Task 5 依赖于 Task 4
- Task 6 依赖于 Task 5
