"""
终端颜色支持模块
提供跨平台的颜色输出功能，支持 Windows 和 Unix 系统
"""

import os
import sys


class Color:
    """颜色常量类"""
    # 基本颜色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # 加粗颜色
    BOLD_RED = '\033[1;91m'
    BOLD_GREEN = '\033[1;92m'
    BOLD_YELLOW = '\033[1;93m'
    BOLD_BLUE = '\033[1;94m'
    BOLD_MAGENTA = '\033[1;95m'
    BOLD_CYAN = '\033[1;96m'
    BOLD_WHITE = '\033[1;97m'
    
    # 背景颜色
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # 重置
    RESET = '\033[0m'


def _enable_windows_colors():
    """在 Windows 上启用 ANSI 颜色支持"""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (AttributeError, OSError, ImportError):
            pass


def _supports_color():
    """检测终端是否支持颜色"""
    if os.name == 'nt':
        _enable_windows_colors()
    
    # 检查是否在支持颜色的终端中
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        return True
    
    # 检查环境变量
    if os.environ.get('TERM') in ('xterm', 'xterm-color', 'xterm-256color', 
                                   'linux', 'screen', 'screen-256color', 
                                   'tmux', 'tmux-256color'):
        return True
    
    if os.environ.get('COLORTERM') in ('truecolor', '24bit'):
        return True
    
    if os.environ.get('FORCE_COLOR'):
        return True
    
    return False


# 全局颜色支持标志
_SUPPORTS_COLOR = _supports_color()


def colorize(text: str, color: str) -> str:
    """
    为文本添加颜色
    
    Args:
        text: 要着色的文本
        color: 颜色代码（使用 Color 类的常量）
    
    Returns:
        着色后的文本
    
    Example:
        >>> print(colorize("成功！", Color.GREEN))
        >>> print(colorize("错误！", Color.BOLD_RED))
    """
    if not _SUPPORTS_COLOR:
        return text
    return f"{color}{text}{Color.RESET}"


def strip_colors(text: str) -> str:
    """
    移除文本中的颜色代码
    
    Args:
        text: 包含颜色代码的文本
    
    Returns:
        移除颜色代码后的纯文本
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def print_colored(text: str, color: str, **kwargs):
    """
    打印带颜色的文本
    
    Args:
        text: 要打印的文本
        color: 颜色代码
        **kwargs: 传递给 print 函数的其他参数
    """
    print(colorize(text, color), **kwargs)


# 便捷函数
def red(text: str) -> str:
    """红色文本"""
    return colorize(text, Color.RED)


def green(text: str) -> str:
    """绿色文本"""
    return colorize(text, Color.GREEN)


def yellow(text: str) -> str:
    """黄色文本"""
    return colorize(text, Color.YELLOW)


def blue(text: str) -> str:
    """蓝色文本"""
    return colorize(text, Color.BLUE)


def magenta(text: str) -> str:
    """洋红色文本"""
    return colorize(text, Color.MAGENTA)


def cyan(text: str) -> str:
    """青色文本"""
    return colorize(text, Color.CYAN)


def white(text: str) -> str:
    """白色文本"""
    return colorize(text, Color.WHITE)


def bold(text: str) -> str:
    """加粗文本"""
    return colorize(text, Color.BOLD)


def dim(text: str) -> str:
    """暗淡文本"""
    return colorize(text, Color.DIM)


def success(text: str) -> str:
    """成功消息样式（绿色加粗）"""
    return colorize(text, Color.BOLD_GREEN)


def warning(text: str) -> str:
    """警告消息样式（黄色加粗）"""
    return colorize(text, Color.BOLD_YELLOW)


def error(text: str) -> str:
    """错误消息样式（红色加粗）"""
    return colorize(text, Color.BOLD_RED)


def info(text: str) -> str:
    """信息消息样式（蓝色加粗）"""
    return colorize(text, Color.BOLD_BLUE)


# 进度指示器样式
class Spinner:
    """简单的加载动画"""
    
    def __init__(self, message: str = "加载中", color: str = Color.CYAN):
        self.message = message
        self.color = color
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
        self.running = False
    
    def next(self) -> str:
        """获取下一帧"""
        char = self.spinner_chars[self.idx]
        self.idx = (self.idx + 1) % len(self.spinner_chars)
        return colorize(f"{char} {self.message}...", self.color)
    
    def get_frame(self) -> str:
        """获取当前帧（不推进）"""
        char = self.spinner_chars[self.idx]
        return colorize(f"{char} {self.message}...", self.color)


if __name__ == "__main__":
    # 测试代码
    print("颜色测试:")
    print(f"  {red('红色')} {green('绿色')} {yellow('黄色')} {blue('蓝色')} {magenta('洋红')} {cyan('青色')} {white('白色')}")
    print(f"  {success('成功')} {warning('警告')} {error('错误')} {info('信息')}")
    print(f"  {bold('加粗')} {dim('暗淡')} {colorize('下划线', Color.UNDERLINE)}")
    
    print("\n加载动画测试:")
    import time
    spinner = Spinner("处理中", Color.GREEN)
    for _ in range(20):
        print(f"\r{spinner.next()}", end='', flush=True)
        time.sleep(0.1)
    print(f"\r{success('✓ 完成！')}      ")
