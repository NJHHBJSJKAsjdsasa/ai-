"""
GUI 主题配置 - 修仙风格深色主题（重构版）
"""
from typing import Tuple, Dict, Any


class Theme:
    """修仙风格主题配置 - 重构版"""

    # ========== 颜色系统 ==========
    # 主色调 - 深色背景层次
    BG_PRIMARY = "#0d1117"      # 最深背景 - 主窗口
    BG_SECONDARY = "#161b22"    # 次级背景 - 面板
    BG_TERTIARY = "#21262d"     # 三级背景 - 卡片
    BG_ELEVATED = "#30363d"     # 提升背景 - 悬停/选中

    # 边框颜色
    BORDER_LIGHT = "#30363d"
    BORDER_DEFAULT = "#21262d"
    BORDER_FOCUS = "#58a6ff"

    # 强调色 - 修仙氛围
    ACCENT_GOLD = "#ffd700"      # 金色 - 修为/重要
    ACCENT_CYAN = "#00d9ff"      # 青色 - 灵力/信息
    ACCENT_RED = "#f85149"       # 红色 - 生命/危险
    ACCENT_GREEN = "#3fb950"     # 绿色 - 成功/恢复
    ACCENT_PURPLE = "#a371f7"    # 紫色 - 特殊/神秘
    ACCENT_PINK = "#ff69b4"      # 粉红 - 社交/情感
    ACCENT_ORANGE = "#f0883e"    # 橙色 - 警告/注意
    ACCENT_BLUE = "#58a6ff"      # 蓝色 - 通用/链接

    # 文字颜色
    TEXT_PRIMARY = "#f0f6fc"     # 主文字 - 高对比
    TEXT_SECONDARY = "#c9d1d9"   # 次级文字
    TEXT_TERTIARY = "#8b949e"    # 三级文字
    TEXT_DIM = "#6e7681"         # 暗淡文字
    TEXT_DISABLED = "#484f58"    # 禁用文字

    # 状态颜色
    SUCCESS = "#3fb950"
    WARNING = "#f0883e"
    ERROR = "#f85149"
    INFO = "#58a6ff"

    # 渐变颜色（用于进度条等）
    GRADIENT_GOLD_START = "#ffd700"
    GRADIENT_GOLD_END = "#ffaa00"
    GRADIENT_CYAN_START = "#00d9ff"
    GRADIENT_CYAN_END = "#00a8cc"
    GRADIENT_RED_START = "#f85149"
    GRADIENT_RED_END = "#da3633"
    GRADIENT_GREEN_START = "#3fb950"
    GRADIENT_GREEN_END = "#2ea043"

    # ========== 字体系统 ==========
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_FAMILY_FALLBACK = "SimHei"
    FONT_MONO = "Consolas"

    # 字体大小
    FONT_SIZE_XS = 9
    FONT_SIZE_SM = 10
    FONT_SIZE_MD = 11
    FONT_SIZE_LG = 13
    FONT_SIZE_XL = 16
    FONT_SIZE_2XL = 20
    FONT_SIZE_3XL = 24

    # 字体配置字典
    FONTS = {
        'title': (FONT_FAMILY, FONT_SIZE_2XL, 'bold'),
        'heading': (FONT_FAMILY, FONT_SIZE_XL, 'bold'),
        'subheading': (FONT_FAMILY, FONT_SIZE_LG, 'bold'),
        'body': (FONT_FAMILY, FONT_SIZE_MD, 'normal'),
        'body_bold': (FONT_FAMILY, FONT_SIZE_MD, 'bold'),
        'small': (FONT_FAMILY, FONT_SIZE_SM, 'normal'),
        'small_bold': (FONT_FAMILY, FONT_SIZE_SM, 'bold'),
        'tiny': (FONT_FAMILY, FONT_SIZE_XS, 'normal'),
        'mono': (FONT_MONO, FONT_SIZE_SM, 'normal'),
    }

    # ========== 间距系统 ==========
    SPACING_XS = 2
    SPACING_SM = 5
    SPACING_MD = 10
    SPACING_LG = 15
    SPACING_XL = 20
    SPACING_2XL = 30

    # ========== 圆角系统 ==========
    RADIUS_SM = 3
    RADIUS_MD = 6
    RADIUS_LG = 10
    RADIUS_XL = 15
    RADIUS_FULL = 9999

    # ========== 动画配置 ==========
    ANIMATION_ENABLED = True
    ANIMATION_DURATION = 300
    ANIMATION_DURATION_FAST = 150
    ANIMATION_DURATION_SLOW = 500
    ANIMATION_EASING = "ease_out"
    ANIMATION_FPS = 60

    # 缓动函数类型
    EASING_LINEAR = "linear"
    EASING_EASE_IN = "ease_in"
    EASING_EASE_OUT = "ease_out"
    EASING_EASE_IN_OUT = "ease_in_out"
    EASING_BOUNCE = "bounce"

    # 悬停效果配置
    HOVER_BRIGHTNESS = 1.15
    HOVER_OPACITY = 0.8

    # ========== 尺寸配置 ==========
    NAV_WIDTH = 180
    NAV_COLLAPSED_WIDTH = 60
    HEADER_HEIGHT = 40
    STATUS_BAR_HEIGHT = 28
    LOG_PANEL_HEIGHT = 150
    CARD_PADDING = 15
    SECTION_SPACING = 15

    # ========== 颜色字典（供面板使用）==========
    COLORS = {
        'bg_primary': BG_PRIMARY,
        'bg_secondary': BG_SECONDARY,
        'bg_tertiary': BG_TERTIARY,
        'bg_elevated': BG_ELEVATED,
        'text_primary': TEXT_PRIMARY,
        'text_secondary': TEXT_SECONDARY,
        'text_tertiary': TEXT_TERTIARY,
        'text_dim': TEXT_DIM,
        'accent_gold': ACCENT_GOLD,
        'accent_cyan': ACCENT_CYAN,
        'accent_red': ACCENT_RED,
        'accent_green': ACCENT_GREEN,
        'accent_purple': ACCENT_PURPLE,
        'accent_orange': ACCENT_ORANGE,
        'accent_blue': ACCENT_BLUE,
        'border_light': BORDER_LIGHT,
        'border_default': BORDER_DEFAULT,
        'success': SUCCESS,
        'warning': WARNING,
        'error': ERROR,
        'info': INFO,
    }

    # ========== 类方法 ==========
    @classmethod
    def get_font(cls, size=None, bold=False, family=None):
        """获取字体配置"""
        if family is None:
            family = cls.FONT_FAMILY
        if size is None:
            size = cls.FONT_SIZE_MD
        weight = "bold" if bold else "normal"
        return (family, size, weight)

    @classmethod
    def get_title_font(cls, size=None):
        """获取标题字体"""
        if size is None:
            size = cls.FONT_SIZE_XL
        return (cls.FONT_FAMILY, size, "bold")

    @classmethod
    def get_mono_font(cls, size=None):
        """获取等宽字体"""
        if size is None:
            size = cls.FONT_SIZE_SM
        return (cls.FONT_MONO, size, "normal")

    # ========== 组件样式配置 ==========
    @classmethod
    def get_button_style(cls, button_type="primary") -> Dict[str, Any]:
        """获取按钮样式"""
        base_style = {
            "font": cls.get_font(cls.FONT_SIZE_MD),
            "relief": "flat",
            "cursor": "hand2",
            "padx": cls.SPACING_LG,
            "pady": cls.SPACING_SM,
        }

        styles = {
            "primary": {
                **base_style,
                "bg": cls.ACCENT_GOLD,
                "fg": cls.BG_PRIMARY,
                "activebackground": cls._lighten_color(cls.ACCENT_GOLD, 1.2),
                "activeforeground": cls.BG_PRIMARY,
            },
            "secondary": {
                **base_style,
                "bg": cls.BG_ELEVATED,
                "fg": cls.TEXT_PRIMARY,
                "activebackground": cls.ACCENT_BLUE,
                "activeforeground": cls.TEXT_PRIMARY,
            },
            "success": {
                **base_style,
                "bg": cls.ACCENT_GREEN,
                "fg": cls.BG_PRIMARY,
                "activebackground": cls._lighten_color(cls.ACCENT_GREEN, 1.2),
                "activeforeground": cls.BG_PRIMARY,
            },
            "danger": {
                **base_style,
                "bg": cls.ACCENT_RED,
                "fg": cls.TEXT_PRIMARY,
                "activebackground": cls._lighten_color(cls.ACCENT_RED, 1.2),
                "activeforeground": cls.TEXT_PRIMARY,
            },
            "ghost": {
                **base_style,
                "bg": cls.BG_SECONDARY,
                "fg": cls.TEXT_SECONDARY,
                "activebackground": cls.BG_TERTIARY,
                "activeforeground": cls.TEXT_PRIMARY,
            },
            "nav": {
                **base_style,
                "bg": cls.BG_SECONDARY,
                "fg": cls.TEXT_SECONDARY,
                "activebackground": cls.BG_TERTIARY,
                "activeforeground": cls.ACCENT_GOLD,
                "padx": cls.SPACING_MD,
                "pady": cls.SPACING_SM,
            },
            "nav_active": {
                **base_style,
                "bg": cls.BG_TERTIARY,
                "fg": cls.ACCENT_GOLD,
                "activebackground": cls.BG_ELEVATED,
                "activeforeground": cls.ACCENT_GOLD,
                "padx": cls.SPACING_MD,
                "pady": cls.SPACING_SM,
            },
        }
        return styles.get(button_type, styles["primary"])

    @classmethod
    def get_frame_style(cls, frame_type="default") -> Dict[str, Any]:
        """获取框架样式"""
        styles = {
            "default": {
                "bg": cls.BG_SECONDARY,
                "padx": cls.SPACING_MD,
                "pady": cls.SPACING_MD,
            },
            "card": {
                "bg": cls.BG_TERTIARY,
                "padx": cls.CARD_PADDING,
                "pady": cls.CARD_PADDING,
                "relief": "flat",
                "highlightbackground": cls.BORDER_DEFAULT,
                "highlightthickness": 1,
            },
            "panel": {
                "bg": cls.BG_SECONDARY,
                "padx": cls.SPACING_SM,
                "pady": cls.SPACING_SM,
            },
            "elevated": {
                "bg": cls.BG_ELEVATED,
                "padx": cls.CARD_PADDING,
                "pady": cls.CARD_PADDING,
                "relief": "flat",
            },
        }
        return styles.get(frame_type, styles["default"])

    @classmethod
    def get_label_style(cls, label_type="normal") -> Dict[str, Any]:
        """获取标签样式"""
        base_style = {
            "bg": cls.BG_SECONDARY,
        }

        styles = {
            "normal": {
                **base_style,
                "fg": cls.TEXT_PRIMARY,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
            "secondary": {
                **base_style,
                "fg": cls.TEXT_SECONDARY,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
            "dim": {
                **base_style,
                "fg": cls.TEXT_DIM,
                "font": cls.get_font(cls.FONT_SIZE_SM),
            },
            "title": {
                **base_style,
                "fg": cls.ACCENT_GOLD,
                "font": cls.get_title_font(cls.FONT_SIZE_XL),
            },
            "heading": {
                **base_style,
                "fg": cls.ACCENT_CYAN,
                "font": cls.get_font(cls.FONT_SIZE_LG, bold=True),
            },
            "subheading": {
                **base_style,
                "fg": cls.TEXT_SECONDARY,
                "font": cls.get_font(cls.FONT_SIZE_MD, bold=True),
            },
            "success": {
                **base_style,
                "fg": cls.SUCCESS,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
            "warning": {
                **base_style,
                "fg": cls.WARNING,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
            "error": {
                **base_style,
                "fg": cls.ERROR,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
            "info": {
                **base_style,
                "fg": cls.INFO,
                "font": cls.get_font(cls.FONT_SIZE_MD),
            },
        }
        return styles.get(label_type, styles["normal"])

    @classmethod
    def get_entry_style(cls) -> Dict[str, Any]:
        """获取输入框样式"""
        return {
            "bg": cls.BG_PRIMARY,
            "fg": cls.TEXT_PRIMARY,
            "insertbackground": cls.ACCENT_CYAN,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightcolor": cls.BORDER_FOCUS,
            "highlightbackground": cls.BORDER_DEFAULT,
            "font": cls.get_font(cls.FONT_SIZE_MD),
            "selectbackground": cls.ACCENT_BLUE,
            "selectforeground": cls.TEXT_PRIMARY,
        }

    @classmethod
    def get_listbox_style(cls) -> Dict[str, Any]:
        """获取列表框样式"""
        return {
            "bg": cls.BG_PRIMARY,
            "fg": cls.TEXT_PRIMARY,
            "selectbackground": cls.ACCENT_BLUE,
            "selectforeground": cls.TEXT_PRIMARY,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightcolor": cls.BORDER_DEFAULT,
            "font": cls.get_font(cls.FONT_SIZE_MD),
        }

    @classmethod
    def get_text_style(cls) -> Dict[str, Any]:
        """获取文本框样式"""
        return {
            "bg": cls.BG_PRIMARY,
            "fg": cls.TEXT_PRIMARY,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightcolor": cls.BORDER_DEFAULT,
            "font": cls.get_font(cls.FONT_SIZE_MD),
            "wrap": "word",
            "padx": cls.SPACING_SM,
            "pady": cls.SPACING_SM,
        }

    @classmethod
    def get_progressbar_colors(cls, bar_type="default") -> Tuple[str, str]:
        """获取进度条颜色 (填充色, 背景色)"""
        colors = {
            "default": (cls.ACCENT_BLUE, cls.BG_PRIMARY),
            "health": (cls.ACCENT_RED, cls.BG_PRIMARY),
            "exp": (cls.ACCENT_GOLD, cls.BG_PRIMARY),
            "mana": (cls.ACCENT_CYAN, cls.BG_PRIMARY),
            "energy": (cls.ACCENT_GREEN, cls.BG_PRIMARY),
            "purple": (cls.ACCENT_PURPLE, cls.BG_PRIMARY),
        }
        return colors.get(bar_type, colors["default"])

    @classmethod
    def get_scrollbar_style(cls) -> Dict[str, Any]:
        """获取滚动条样式"""
        return {
            "bg": cls.BG_TERTIARY,
            "troughcolor": cls.BG_SECONDARY,
            "activebackground": cls.BG_ELEVATED,
            "highlightthickness": 0,
            "relief": "flat",
            "width": 12,
        }

    # ========== 工具方法 ==========
    @classmethod
    def hex_to_rgb(cls, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @classmethod
    def rgb_to_hex(cls, r: int, g: int, b: int) -> str:
        """将RGB元组转换为十六进制颜色"""
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def _lighten_color(cls, color: str, factor: float = None) -> str:
        """提亮颜色"""
        if factor is None:
            factor = cls.HOVER_BRIGHTNESS
        try:
            r, g, b = cls.hex_to_rgb(color)
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return cls.rgb_to_hex(r, g, b)
        except:
            return color

    @classmethod
    def _darken_color(cls, color: str, factor: float = 0.8) -> str:
        """加深颜色"""
        try:
            r, g, b = cls.hex_to_rgb(color)
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return cls.rgb_to_hex(r, g, b)
        except:
            return color

    @classmethod
    def interpolate_color(cls, color1: str, color2: str, factor: float) -> str:
        """在两个颜色之间插值"""
        r1, g1, b1 = cls.hex_to_rgb(color1)
        r2, g2, b2 = cls.hex_to_rgb(color2)

        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)

        return cls.rgb_to_hex(r, g, b)

    @classmethod
    def get_animation_duration(cls, speed: str = "normal") -> int:
        """获取动画时长"""
        durations = {
            "fast": cls.ANIMATION_DURATION_FAST,
            "normal": cls.ANIMATION_DURATION,
            "slow": cls.ANIMATION_DURATION_SLOW,
        }
        return durations.get(speed, cls.ANIMATION_DURATION)

    @classmethod
    def is_animation_enabled(cls) -> bool:
        """检查动画是否启用"""
        return cls.ANIMATION_ENABLED

    @classmethod
    def create_card(cls, parent, title: str = None, **kwargs) -> Any:
        """创建统一风格的卡片框架"""
        import tkinter as tk

        card = tk.Frame(parent, **cls.get_frame_style("card"))

        if title:
            title_label = tk.Label(
                card,
                text=title,
                **cls.get_label_style("heading")
            )
            title_label.pack(anchor="w", pady=(0, cls.SPACING_MD))

        return card

    @classmethod
    def create_section_title(cls, parent, text: str) -> Any:
        """创建统一风格的节标题"""
        import tkinter as tk

        frame = tk.Frame(parent, bg=cls.BG_SECONDARY)

        label = tk.Label(
            frame,
            text=text,
            **cls.get_label_style("subheading")
        )
        label.pack(anchor="w")

        # 分隔线
        separator = tk.Frame(
            frame,
            bg=cls.BORDER_DEFAULT,
            height=1
        )
        separator.pack(fill="x", pady=(cls.SPACING_SM, 0))

        return frame
