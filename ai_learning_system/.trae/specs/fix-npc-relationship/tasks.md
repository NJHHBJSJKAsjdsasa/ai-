# Tasks

- [x] Task 1: 创建NPC关系数据库表
  - [x] SubTask 1.1: 在database.py中添加npc_relations表的创建语句
  - [x] SubTask 1.2: 添加NPC关系CRUD操作方法
  - [x] SubTask 1.3: 添加NPC关系查询方法（按NPC ID、按关系类型等）

- [x] Task 2: 完善NPC关系网络系统
  - [x] SubTask 2.1: 在NPCRelationshipNetwork类中添加数据库集成
  - [x] SubTask 2.2: 实现关系数据的保存和加载方法
  - [x] SubTask 2.3: 添加关系变化时的数据库同步

- [x] Task 3: 集成关系网络到NPC核心类
  - [x] SubTask 3.1: 在NPC类中添加relationship_network属性
  - [x] SubTask 3.2: 实现get_relationships方法返回真实数据
  - [x] SubTask 3.3: 实现update_relationship_with方法更新关系
  - [x] SubTask 3.4: 在to_dict/from_dict中处理关系数据

- [x] Task 4: 在NPC管理器中添加关系维护
  - [x] SubTask 4.1: 实现initialize_relationships方法自动建立初始关系
  - [x] SubTask 4.2: 基于门派、位置、性格计算初始关系值
  - [x] SubTask 4.3: 在社交和战斗后更新关系

- [x] Task 5: 更新NPC面板使用真实数据
  - [x] SubTask 5.1: 修改_on_view_relations方法使用真实关系数据
  - [x] SubTask 5.2: 从NPCRelationshipNetwork获取关系数据
  - [x] SubTask 5.3: 完善关系展示UI

- [x] Task 6: 测试和验证
  - [x] SubTask 6.1: 测试关系数据保存和加载
  - [x] SubTask 6.2: 测试关系自动建立
  - [x] SubTask 6.3: 测试关系动态更新

# Task Dependencies
- Task 2 依赖于 Task 1
- Task 3 依赖于 Task 2
- Task 4 依赖于 Task 3
- Task 5 依赖于 Task 3
- Task 6 依赖于 Task 4 和 Task 5
