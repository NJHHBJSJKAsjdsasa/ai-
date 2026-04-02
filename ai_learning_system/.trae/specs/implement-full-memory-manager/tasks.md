# Tasks

- [x] Task 1: 检查并导入完整记忆管理器依赖
  - [x] SubTask 1.1: 检查 `core/selector.py` 是否存在并可用
  - [x] SubTask 1.2: 检查 `utils/privacy_detector.py` 是否存在并可用
  - [x] SubTask 1.3: 在 `main.py` 中添加完整记忆管理器的导入

- [x] Task 2: 修改 main.py 初始化逻辑
  - [x] SubTask 2.1: 移除简化版 MemoryManager 类定义
  - [x] SubTask 2.2: 初始化 Selector 和 PrivacyDetector
  - [x] SubTask 2.3: 使用完整的 MemoryManager 初始化

- [x] Task 3: 验证接口兼容性
  - [x] SubTask 3.1: 确保 `add_memory` 接口兼容
  - [x] SubTask 3.2: 确保 `get_all_memories` 接口兼容
  - [x] SubTask 3.3: 运行语法检查

- [x] Task 4: 测试记忆管理功能
  - [x] SubTask 4.1: 测试记忆添加功能
  - [x] SubTask 4.2: 测试记忆搜索功能
  - [x] SubTask 4.3: 验证隐私检测功能

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 2
- Task 4 依赖于 Task 3
