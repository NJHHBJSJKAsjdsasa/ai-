"""
热更新管理器模块
负责监视代码文件变更并协调重新加载
"""

import os
import sys
import time
import importlib
import py_compile
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime


class HotReloadManager:
    """热更新管理器 - 监视代码变更并协调重新加载"""
    
    def __init__(self, watch_paths: List[str] = None):
        """
        初始化热更新管理器
        
        Args:
            watch_paths: 要监视的代码路径列表，默认为 ['interface/handlers', 'game', 'core']
        """
        self.watch_paths = watch_paths or [
            'interface/handlers',
            'game',
            'core',
            'config',
        ]
        self.file_mtimes: Dict[str, float] = {}  # 文件最后修改时间
        self.changed_files: Set[str] = set()  # 已变更的文件
        self.reload_callbacks: List[Callable] = []  # 重载回调函数
        self.is_enabled = True  # 是否启用热更新
        self.last_check_time = 0  # 上次检查时间
        self.check_interval = 1.0  # 检查间隔（秒）
        
        # 初始化文件修改时间
        self._init_file_mtimes()
    
    def _init_file_mtimes(self):
        """初始化所有监视文件的修改时间"""
        for path in self.watch_paths:
            full_path = Path(path)
            if full_path.exists():
                for py_file in full_path.rglob('*.py'):
                    if py_file.name != '__init__.py':
                        try:
                            mtime = py_file.stat().st_mtime
                            self.file_mtimes[str(py_file)] = mtime
                        except OSError:
                            continue
    
    def check_for_changes(self) -> List[str]:
        """
        检查是否有代码文件变更
        
        Returns:
            变更的文件路径列表
        """
        if not self.is_enabled:
            return []
        
        # 限制检查频率
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return list(self.changed_files)
        
        self.last_check_time = current_time
        changed = []
        
        for path in self.watch_paths:
            full_path = Path(path)
            if not full_path.exists():
                continue
            
            for py_file in full_path.rglob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                
                file_path = str(py_file)
                try:
                    current_mtime = py_file.stat().st_mtime
                    last_mtime = self.file_mtimes.get(file_path, 0)
                    
                    if current_mtime > last_mtime:
                        changed.append(file_path)
                        self.changed_files.add(file_path)
                        self.file_mtimes[file_path] = current_mtime
                except OSError:
                    continue
        
        return changed
    
    def has_changes(self) -> bool:
        """
        检查是否有待处理的变更
        
        Returns:
            是否有变更
        """
        self.check_for_changes()
        return len(self.changed_files) > 0
    
    def get_changed_modules(self) -> List[str]:
        """
        获取变更的模块名称列表
        
        Returns:
            模块名称列表（如 'interface.handlers.cultivation_handler'）
        """
        modules = []
        for file_path in self.changed_files:
            module_name = self._file_path_to_module(file_path)
            if module_name:
                modules.append(module_name)
        return modules
    
    def _file_path_to_module(self, file_path: str) -> Optional[str]:
        """
        将文件路径转换为模块名称
        
        Args:
            file_path: 文件路径
            
        Returns:
            模块名称
        """
        path = Path(file_path)
        if not path.suffix == '.py':
            return None
        
        # 获取相对于项目根目录的路径
        try:
            # 移除 .py 后缀
            relative_path = path.with_suffix('')
            # 转换为模块名（用 . 替换 /）
            module_name = str(relative_path).replace(os.sep, '.')
            return module_name
        except Exception:
            return None
    
    def validate_syntax(self, file_path: str) -> tuple[bool, str]:
        """
        验证Python文件语法
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            py_compile.compile(file_path, doraise=True)
            return True, ""
        except py_compile.PyCompileError as e:
            return False, str(e)
    
    def reload_module(self, module_name: str) -> tuple[bool, str]:
        """
        重新加载指定模块
        
        Args:
            module_name: 模块名称
            
        Returns:
            (是否成功, 错误信息)
        """
        if module_name not in sys.modules:
            return False, f"模块 {module_name} 未加载"
        
        try:
            # 先验证语法
            module = sys.modules[module_name]
            if hasattr(module, '__file__') and module.__file__:
                is_valid, error = self.validate_syntax(module.__file__)
                if not is_valid:
                    return False, f"语法错误: {error}"
            
            # 重新加载模块
            importlib.reload(module)
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def reload_all_changed(self) -> Dict[str, tuple[bool, str]]:
        """
        重新加载所有变更的模块
        
        Returns:
            重载结果字典 {模块名: (是否成功, 错误信息)}
        """
        results = {}
        modules = self.get_changed_modules()
        
        for module_name in modules:
            success, error = self.reload_module(module_name)
            results[module_name] = (success, error)
            
            if success:
                # 从变更列表中移除成功重载的模块
                self.changed_files.discard(module_name.replace('.', os.sep) + '.py')
        
        # 执行回调
        for callback in self.reload_callbacks:
            try:
                callback(results)
            except Exception:
                pass
        
        return results
    
    def add_reload_callback(self, callback: Callable):
        """
        添加重载回调函数
        
        Args:
            callback: 回调函数，接收重载结果字典作为参数
        """
        self.reload_callbacks.append(callback)
    
    def remove_reload_callback(self, callback: Callable):
        """
        移除重载回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self.reload_callbacks:
            self.reload_callbacks.remove(callback)
    
    def enable(self):
        """启用热更新"""
        self.is_enabled = True
    
    def disable(self):
        """禁用热更新"""
        self.is_enabled = False
    
    def clear_changes(self):
        """清除所有待处理的变更"""
        self.changed_files.clear()
    
    def get_status(self) -> Dict:
        """
        获取热更新状态
        
        Returns:
            状态信息字典
        """
        return {
            'enabled': self.is_enabled,
            'watch_paths': self.watch_paths,
            'watched_files': len(self.file_mtimes),
            'pending_changes': len(self.changed_files),
            'changed_modules': self.get_changed_modules(),
            'check_interval': self.check_interval,
        }


# 全局热更新管理器实例
_hot_reload_manager: Optional[HotReloadManager] = None


def get_hot_reload_manager() -> HotReloadManager:
    """
    获取全局热更新管理器实例
    
    Returns:
        HotReloadManager 实例
    """
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = HotReloadManager()
    return _hot_reload_manager


def init_hot_reload(watch_paths: List[str] = None) -> HotReloadManager:
    """
    初始化热更新管理器
    
    Args:
        watch_paths: 要监视的路径列表
        
    Returns:
        HotReloadManager 实例
    """
    global _hot_reload_manager
    _hot_reload_manager = HotReloadManager(watch_paths)
    return _hot_reload_manager
