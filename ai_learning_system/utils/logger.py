"""
日志工具模块
提供统一的日志记录功能，支持输出到控制台和文件
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from .colors import Color, colorize, success, warning, error, info, dim


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    """
    日志记录器类
    
    支持同时输出到控制台和文件，带颜色支持
    """
    
    # 日志级别对应的颜色
    LEVEL_COLORS = {
        LogLevel.DEBUG: Color.DIM,
        LogLevel.INFO: Color.BLUE,
        LogLevel.WARNING: Color.YELLOW,
        LogLevel.ERROR: Color.RED,
        LogLevel.CRITICAL: Color.BOLD_RED,
    }
    
    # 日志级别对应的图标
    LEVEL_ICONS = {
        LogLevel.DEBUG: "🐛",
        LogLevel.INFO: "ℹ️",
        LogLevel.WARNING: "⚠️",
        LogLevel.ERROR: "❌",
        LogLevel.CRITICAL: "🔥",
    }
    
    def __init__(
        self,
        name: str = "ai_learning_system",
        log_dir: Optional[str] = None,
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
        enable_console: bool = True,
        enable_file: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录，默认为项目根目录下的 logs 文件夹
            console_level: 控制台日志级别
            file_level: 文件日志级别
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出
            max_file_size: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
        """
        self.name = name
        self.console_level = console_level
        self.file_level = file_level
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # 创建日志目录
        if log_dir is None:
            # 默认在项目根目录的 logs 文件夹
            project_root = Path(__file__).parent.parent
            log_dir = project_root / "logs"
        else:
            log_dir = Path(log_dir)
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Python 日志记录器
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []  # 清除已有处理器
        
        # 添加控制台处理器
        if enable_console:
            self._setup_console_handler()
        
        # 添加文件处理器
        if enable_file:
            self._setup_file_handler(max_file_size, backup_count)
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level.value)
        console_handler.setFormatter(ColoredFormatter())
        self._logger.addHandler(console_handler)
    
    def _setup_file_handler(self, max_file_size: int, backup_count: int):
        """设置文件处理器"""
        from logging.handlers import RotatingFileHandler
        
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.file_level.value)
        file_handler.setFormatter(PlainFormatter())
        self._logger.addHandler(file_handler)
    
    def _log(self, level: LogLevel, message: str, *args, **kwargs):
        """内部日志记录方法"""
        self._logger.log(level.value, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """
        记录调试信息
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        self._log(LogLevel.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """
        记录信息
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        self._log(LogLevel.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """
        记录警告
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        self._log(LogLevel.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """
        记录错误
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        self._log(LogLevel.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """
        记录严重错误
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        self._log(LogLevel.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """
        记录异常信息（自动包含堆栈跟踪）
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        kwargs['exc_info'] = True
        self._log(LogLevel.ERROR, message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs):
        """
        记录成功消息（使用 info 级别，带成功样式）
        
        Args:
            message: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数
        """
        if args:
            message = message % args
        formatted = f"✓ {message}"
        self._log(LogLevel.INFO, formatted, **kwargs)
    
    def section(self, title: str):
        """
        打印分隔线标题
        
        Args:
            title: 标题文本
        """
        separator = "─" * 50
        self.info(f"\n{separator}")
        self.info(f"  {title}")
        self.info(f"{separator}")
    
    def set_level(self, level: LogLevel):
        """
        设置日志级别
        
        Args:
            level: 新的日志级别
        """
        self._logger.setLevel(level.value)
        for handler in self._logger.handlers:
            handler.setLevel(level.value)
    
    def get_log_file_path(self) -> Optional[Path]:
        """
        获取当前日志文件路径
        
        Returns:
            日志文件路径，如果文件输出未启用则返回 None
        """
        if not self.enable_file:
            return None
        return self.log_dir / f"{self.name}.log"


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 获取时间戳
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        
        # 获取级别名称和颜色
        level_name = record.levelname
        level = LogLevel(record.levelno)
        color = Logger.LEVEL_COLORS.get(level, Color.RESET)
        icon = Logger.LEVEL_ICONS.get(level, "")
        
        # 格式化消息
        if record.args:
            message = record.getMessage()
        else:
            message = record.getMessage()
        
        # 构建带颜色的输出
        colored_level = colorize(f"[{level_name:8}]", color)
        colored_time = dim(f"[{timestamp}]")
        
        # 构建完整日志行
        log_line = f"{colored_time} {colored_level} {icon} {message}"
        
        return log_line


class PlainFormatter(logging.Formatter):
    """纯文本日志格式化器（用于文件输出）"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level_name = record.levelname
        message = record.getMessage()
        
        log_line = f"[{timestamp}] [{level_name:8}] {message}"
        
        # 如果有异常信息，添加堆栈跟踪
        if record.exc_info:
            import traceback
            exc_text = traceback.format_exception(*record.exc_info)
            log_line += "\n" + "".join(exc_text)
        
        return log_line


# 全局日志实例
_default_logger: Optional[Logger] = None


def get_logger(name: str = "ai_learning_system", **kwargs) -> Logger:
    """
    获取或创建日志记录器
    
    Args:
        name: 日志记录器名称
        **kwargs: 传递给 Logger 构造函数的参数
    
    Returns:
        Logger 实例
    """
    global _default_logger
    
    if _default_logger is None or name != _default_logger.name:
        _default_logger = Logger(name=name, **kwargs)
    
    return _default_logger


def setup_logging(
    level: LogLevel = LogLevel.INFO,
    log_dir: Optional[str] = None,
    enable_file: bool = True
) -> Logger:
    """
    快速设置日志系统
    
    Args:
        level: 日志级别
        log_dir: 日志目录
        enable_file: 是否启用文件日志
    
    Returns:
        配置好的 Logger 实例
    """
    global _default_logger
    _default_logger = Logger(
        console_level=level,
        file_level=LogLevel.DEBUG if enable_file else None,
        log_dir=log_dir,
        enable_file=enable_file
    )
    return _default_logger


# 便捷函数
def debug(message: str, *args, **kwargs):
    """记录调试信息"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """记录信息"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """记录警告"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """记录错误"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """记录严重错误"""
    get_logger().critical(message, *args, **kwargs)


def success(message: str, *args, **kwargs):
    """记录成功消息"""
    get_logger().success(message, *args, **kwargs)


if __name__ == "__main__":
    # 测试代码
    logger = setup_logging(level=LogLevel.DEBUG)
    
    logger.section("日志系统测试")
    
    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.success("操作成功完成")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    logger.critical("这是一条严重错误消息")
    
    logger.section("格式化测试")
    
    # 测试格式化
    logger.info("用户 %s 登录成功，IP: %s", "admin", "192.168.1.1")
    logger.info("处理 %d 条记录，耗时 %.2f 秒", 1000, 3.14)
    
    # 测试异常记录
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("发生除以零错误")
    
    print(f"\n日志文件位置: {logger.get_log_file_path()}")
