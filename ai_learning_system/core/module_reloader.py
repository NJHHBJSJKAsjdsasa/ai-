"""
模块重载器模块
封装安全的模块重载，特别针对处理器模块
"""

import sys
import importlib
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path


class ModuleReloader:
    """模块重载器 - 安全地重新加载模块"""
    
    def __init__(self):
        """初始化模块重载器"""
        self.reload_history: List[Dict] = []  # 重载历史记录
        self.backup_modules: Dict[str, Any] = {}  # 模块备份
    
    def reload_handler_module(self, module_name: str, cli_instance=None) -> tuple[bool, str]:
        """
        重新加载处理器模块
        
        Args:
            module_name: 模块名称（如 'interface.handlers.cultivation_handler'）
            cli_instance: CLI实例，用于重新初始化handler
            
        Returns:
            (是否成功, 错误信息)
        """
        if module_name not in sys.modules:
            return False, f"模块 {module_name} 未加载"
        
        try:
            # 备份当前模块
            old_module = sys.modules[module_name]
            self.backup_modules[module_name] = old_module
            
            # 重新加载模块
            new_module = importlib.reload(old_module)
            
            # 记录重载历史
            self.reload_history.append({
                'module': module_name,
                'success': True,
                'error': None,
            })
            
            # 如果提供了CLI实例，尝试重新初始化handler
            if cli_instance:
                self._reinit_handler(module_name, cli_instance)
            
            return True, ""
            
        except Exception as e:
            # 记录失败
            self.reload_history.append({
                'module': module_name,
                'success': False,
                'error': str(e),
            })
            return False, str(e)
    
    def _reinit_handler(self, module_name: str, cli_instance):
        """
        重新初始化处理器
        
        Args:
            module_name: 模块名称
            cli_instance: CLI实例
        """
        # 从模块名提取handler名称
        # 例如：interface.handlers.cultivation_handler -> cultivation_handler
        handler_name = module_name.split('.')[-1]
        
        # 映射到CLI中的handler属性名
        handler_mapping = {
            'cultivation_handler': 'cultivation_handler',
            'combat_handler': 'combat_handler',
            'npc_handler': 'npc_handler',
            'exploration_handler': 'exploration_handler',
            'map_handler': 'map_handler',
            'system_handler': 'system_handler',
            'chat_handler': 'chat_handler',
        }
        
        attr_name = handler_mapping.get(handler_name)
        if not attr_name:
            return
        
        # 获取当前handler的依赖
        old_handler = getattr(cli_instance, attr_name, None)
        if not old_handler:
            return
        
        # 保存依赖引用
        player = getattr(old_handler, 'player', None)
        world = getattr(old_handler, 'world', None)
        db = getattr(old_handler, 'db', None)
        
        # 尝试创建新的handler实例
        try:
            module = sys.modules[module_name]
            handler_class_name = self._get_handler_class_name(handler_name)
            handler_class = getattr(module, handler_class_name, None)
            
            if handler_class:
                # 创建新的handler实例
                new_handler = handler_class(cli_instance)
                
                # 恢复依赖引用
                if player:
                    new_handler.player = player
                if world:
                    new_handler.world = world
                if db:
                    new_handler.db = db
                
                # 替换CLI中的handler
                setattr(cli_instance, attr_name, new_handler)
                
        except Exception:
            # 如果重新初始化失败，保留旧的handler
            pass
    
    def _get_handler_class_name(self, handler_name: str) -> str:
        """
        根据handler文件名获取类名
        
        Args:
            handler_name: handler文件名（如 'cultivation_handler'）
            
        Returns:
            类名（如 'CultivationHandler'）
        """
        # 转换为驼峰命名
        parts = handler_name.split('_')
        return ''.join(part.capitalize() for part in parts)
    
    def reload_modules(self, module_names: List[str], cli_instance=None) -> Dict[str, tuple[bool, str]]:
        """
        批量重新加载模块
        
        Args:
            module_names: 模块名称列表
            cli_instance: CLI实例
            
        Returns:
            重载结果字典
        """
        results = {}
        
        for module_name in module_names:
            success, error = self.reload_handler_module(module_name, cli_instance)
            results[module_name] = (success, error)
        
        return results
    
    def get_reload_summary(self) -> str:
        """
        获取重载摘要
        
        Returns:
            摘要字符串
        """
        if not self.reload_history:
            return "暂无重载记录"
        
        total = len(self.reload_history)
        success_count = sum(1 for r in self.reload_history if r['success'])
        failed_count = total - success_count
        
        return f"重载记录：总计 {total} 次，成功 {success_count} 次，失败 {failed_count} 次"
    
    def clear_history(self):
        """清除重载历史"""
        self.reload_history.clear()
        self.backup_modules.clear()


# 全局模块重载器实例
_module_reloader: Optional[ModuleReloader] = None


def get_module_reloader() -> ModuleReloader:
    """
    获取全局模块重载器实例
    
    Returns:
        ModuleReloader 实例
    """
    global _module_reloader
    if _module_reloader is None:
        _module_reloader = ModuleReloader()
    return _module_reloader
