# Checklist

- [x] `core/hot_reload_manager.py` 文件已创建，实现文件变更检测
- [x] `core/module_reloader.py` 文件已创建，封装安全的模块重载
- [x] 热更新管理器能够检测代码文件变更
- [x] 模块重载器能够安全重载处理器模块
- [x] CLI主循环集成热更新检查
- [x] `/热更新` 命令可用，能手动触发代码重载
- [x] 热更新后玩家数据保持不变
- [x] 热更新后世界状态保持不变
- [x] 语法错误时系统不崩溃，显示错误信息
- [x] 各处理器模块（cultivation, combat, npc等）支持热更新
