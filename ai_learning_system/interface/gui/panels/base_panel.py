"""
面板基类 - 重构版（优化动画）
"""
import tkinter as tk
from enum import Enum
from typing import Optional, Callable
from ..theme import Theme
from ..animation_manager import animation_manager, EasingType


class PanelAnimationType(Enum):
    """面板动画类型"""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    SLIDE_AND_FADE = "slide_and_fade"
    SCALE = "scale"
    NONE = "none"


class BasePanel(tk.Frame):
    """面板基类 - 支持多种动画效果和统一样式"""

    def __init__(self, parent, main_window, **kwargs):
        super().__init__(parent, **kwargs)
        self.main_window = main_window
        self.game = main_window.game if main_window else None
        self.config(bg=Theme.BG_SECONDARY)

        # 动画相关
        self._is_visible = False
        self._fade_anim_id = None
        self._slide_anim_id = None
        self._scale_anim_id = None
        self._current_animation_id = None
        
        # 动画配置（保持向后兼容）
        self._animation_type = PanelAnimationType.FADE
        self._animation_easing = EasingType.EASE_OUT_CUBIC
        self._animation_duration = Theme.ANIMATION_DURATION
        self._slide_distance = 100

        # 设置UI
        self._setup_ui()

    def _setup_ui(self):
        """设置界面 - 子类重写"""
        pass

    def on_show(self):
        """当面板显示时调用"""
        self._is_visible = True
        if Theme.is_animation_enabled():
            self._animate_show()
        else:
            self.refresh()

    def on_hide(self):
        """当面板隐藏时调用"""
        self._is_visible = False
        self._cancel_animations()

    def set_animation_type(self, animation_type: PanelAnimationType):
        """设置面板切换动画类型
        
        Args:
            animation_type: 动画类型枚举
        """
        self._animation_type = animation_type

    def set_animation_easing(self, easing: EasingType):
        """设置动画缓动函数
        
        Args:
            easing: 缓动函数类型
        """
        self._animation_easing = easing

    def set_animation_duration(self, duration: int):
        """设置动画持续时间（毫秒）
        
        Args:
            duration: 动画持续时间
        """
        self._animation_duration = duration

    def set_slide_distance(self, distance: int):
        """设置滑动动画的距离（像素）
        
        Args:
            distance: 滑动距离
        """
        self._slide_distance = distance

    def _animate_show(self):
        """显示动画 - 根据配置的动画类型执行"""
        self.refresh()
        
        if not Theme.is_animation_enabled():
            return
            
        self._cancel_animations()
        
        if self._animation_type == PanelAnimationType.FADE:
            self._fade_in_advanced()
        elif self._animation_type == PanelAnimationType.SLIDE_LEFT:
            self._slide_in_advanced("left")
        elif self._animation_type == PanelAnimationType.SLIDE_RIGHT:
            self._slide_in_advanced("right")
        elif self._animation_type == PanelAnimationType.SLIDE_UP:
            self._slide_in_advanced("up")
        elif self._animation_type == PanelAnimationType.SLIDE_DOWN:
            self._slide_in_advanced("down")
        elif self._animation_type == PanelAnimationType.SLIDE_AND_FADE:
            self._slide_and_fade_in()
        elif self._animation_type == PanelAnimationType.SCALE:
            self._scale_in()

    def _fade_in_advanced(self, duration: int = None, easing: EasingType = None, on_complete=None):
        """优化的淡入动画
        
        Args:
            duration: 动画持续时间
            easing: 缓动函数
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        if duration is None:
            duration = self._animation_duration
        if easing is None:
            easing = self._animation_easing

        self._cancel_animations()
        self._fade_anim_id = animation_manager.fade_in(
            self, duration=duration, easing=easing, on_complete=on_complete
        )

    def _fade_out_advanced(self, duration: int = None, easing: EasingType = None, on_complete=None):
        """优化的淡出动画
        
        Args:
            duration: 动画持续时间
            easing: 缓动函数
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        if duration is None:
            duration = self._animation_duration
        if easing is None:
            easing = EasingType.EASE_IN_CUBIC

        self._cancel_animations()
        self._fade_anim_id = animation_manager.fade_out(
            self, duration=duration, easing=easing, on_complete=on_complete
        )

    def _slide_in_advanced(self, direction: str = "right", duration: int = None, easing: EasingType = None):
        """优化的滑入动画
        
        Args:
            direction: 滑动方向 ("left", "right", "up", "down")
            duration: 动画持续时间
            easing: 缓动函数
        """
        if not Theme.is_animation_enabled():
            return

        if duration is None:
            duration = self._animation_duration
        if easing is None:
            easing = self._animation_easing

        self._cancel_animations()

        # 根据方向设置起始位置
        distance = self._slide_distance
        if direction == "right":
            start_x, start_y = distance, 0
        elif direction == "left":
            start_x, start_y = -distance, 0
        elif direction == "down":
            start_x, start_y = 0, distance
        else:  # up
            start_x, start_y = 0, -distance

        end_x, end_y = 0, 0

        self._slide_anim_id = animation_manager.move(
            self, start_x, start_y, end_x, end_y,
            duration=duration, easing=easing
        )

    def _slide_and_fade_in(self):
        """滑动+淡入组合动画"""
        if not Theme.is_animation_enabled():
            return
            
        self._cancel_animations()
        
        # 同时执行滑动和淡入
        self._slide_in_advanced("right")
        self._fade_in_advanced()

    def _scale_in(self):
        """缩放动画"""
        if not Theme.is_animation_enabled():
            return
            
        self._cancel_animations()
        # 注意：缩放动画在 Tkinter 中需要额外实现，这里我们使用淡入作为替代
        self._fade_in_advanced(easing=EasingType.EASE_OUT_BACK)

    def _fade_in(self, duration: int = None, on_complete=None):
        """淡入动画（保持向后兼容）"""
        if duration is None:
            duration = Theme.ANIMATION_DURATION_FAST
        self._fade_in_advanced(duration=duration, easing=EasingType.EASE_OUT, on_complete=on_complete)

    def _fade_out(self, duration: int = None, on_complete=None):
        """淡出动画（保持向后兼容）"""
        if duration is None:
            duration = Theme.ANIMATION_DURATION_FAST
        self._fade_out_advanced(duration=duration, easing=EasingType.EASE_IN, on_complete=on_complete)

    def _slide_in(self, direction: str = "right", duration: int = None):
        """滑入动画（保持向后兼容）
        
        Args:
            direction: 滑动方向 ("left", "right", "up", "down")
        """
        if duration is None:
            duration = Theme.ANIMATION_DURATION
        self._slide_in_advanced(direction=direction, duration=duration, easing=EasingType.EASE_OUT)

    def _cancel_animations(self):
        """取消所有动画"""
        if self._fade_anim_id:
            animation_manager.cancel(self._fade_anim_id)
            self._fade_anim_id = None
        if self._slide_anim_id:
            animation_manager.cancel(self._slide_anim_id)
            self._slide_anim_id = None
        if self._scale_anim_id:
            animation_manager.cancel(self._scale_anim_id)
            self._scale_anim_id = None
        if self._current_animation_id:
            animation_manager.cancel(self._current_animation_id)
            self._current_animation_id = None

    def refresh(self):
        """刷新面板数据 - 子类重写"""
        pass

    def refresh_animated(self):
        """带动画的刷新（优化版）"""
        if Theme.is_animation_enabled():
            half_duration = self._animation_duration // 2
            self._fade_out_advanced(
                duration=half_duration,
                easing=EasingType.EASE_IN_QUAD,
                on_complete=lambda: [self.refresh(), self._fade_in_advanced(half_duration, EasingType.EASE_OUT_QUAD)]
            )
        else:
            self.refresh()

    def log(self, message, log_type="system"):
        """添加日志"""
        if self.main_window:
            self.main_window.log(message, log_type)

    def get_player(self):
        """获取玩家对象"""
        if self.game and hasattr(self.game, 'player'):
            return self.game.player
        return None

    def get_world(self):
        """获取世界对象"""
        if self.game and hasattr(self.game, 'world'):
            return self.game.world
        return None

    def get_npc_manager(self):
        """获取 NPC 管理器"""
        if self.game and hasattr(self.game, 'npc_manager'):
            return self.game.npc_manager
        return None

    # ========== 通用UI组件创建方法 ==========

    def create_card(self, parent, title: str = None, **kwargs) -> tk.Frame:
        """创建统一风格的卡片框架"""
        card = tk.Frame(parent, **Theme.get_frame_style("card"))

        if title:
            title_label = tk.Label(
                card,
                text=title,
                **Theme.get_label_style("heading")
            )
            title_label.pack(anchor="w", pady=(0, Theme.SPACING_MD))

        return card

    def create_section_title(self, parent, text: str) -> tk.Frame:
        """创建统一风格的节标题"""
        frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)

        label = tk.Label(
            frame,
            text=text,
            **Theme.get_label_style("subheading")
        )
        label.pack(anchor="w")

        # 分隔线
        separator = tk.Frame(
            frame,
            bg=Theme.BORDER_DEFAULT,
            height=1
        )
        separator.pack(fill="x", pady=(Theme.SPACING_SM, 0))

        return frame

    def create_button(self, parent, text: str, command, button_type="primary", **kwargs) -> tk.Button:
        """创建统一风格的按钮"""
        style = Theme.get_button_style(button_type)
        style.update(kwargs)

        btn = tk.Button(parent, text=text, command=command, **style)

        # 添加悬停效果
        original_bg = btn.cget("bg")
        hover_bg = Theme._lighten_color(original_bg, 1.1)

        btn.bind("<Enter>", lambda e, b=btn, hbg=hover_bg: b.config(bg=hbg))
        btn.bind("<Leave>", lambda e, b=btn, obg=original_bg: b.config(bg=obg))

        return btn

    def create_label(self, parent, text: str, label_type="normal", **kwargs) -> tk.Label:
        """创建统一风格的标签"""
        style = Theme.get_label_style(label_type)
        style.update(kwargs)
        return tk.Label(parent, text=text, **style)

    def create_progress_bar(self, parent, height=20, bar_type="default"):
        """创建进度条（返回Canvas）"""
        from ..widgets import AnimatedProgressBar

        fill_color, bg_color = Theme.get_progressbar_colors(bar_type)

        progress = AnimatedProgressBar(
            parent,
            height=height,
            bg_color=bg_color,
            fill_color=fill_color,
            animation_duration=Theme.ANIMATION_DURATION
        )

        return progress

    def create_scrollable_frame(self, parent) -> tuple:
        """创建可滚动的框架"""
        # 创建Canvas
        canvas = tk.Canvas(
            parent,
            bg=Theme.BG_SECONDARY,
            highlightthickness=0
        )

        # 创建滚动条
        scrollbar = tk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=canvas.yview,
            bg=Theme.BG_TERTIARY,
            troughcolor=Theme.BG_SECONDARY,
            activebackground=Theme.BG_ELEVATED,
            width=12
        )

        # 创建内容框架
        content_frame = tk.Frame(canvas, bg=Theme.BG_SECONDARY)

        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # 绑定事件
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        content_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # 鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)
        content_frame.bind("<MouseWheel>", on_mousewheel)

        return canvas, scrollbar, content_frame

    def create_info_row(self, parent, label_text: str, value_text: str = "", value_color=None) -> tk.Frame:
        """创建信息行（标签: 值）"""
        frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)

        # 标签
        label = tk.Label(
            frame,
            text=f"{label_text}: ",
            **Theme.get_label_style("normal")
        )
        label.pack(side=tk.LEFT)

        # 值
        value_style = Theme.get_label_style("normal")
        if value_color:
            value_style = {**value_style, "fg": value_color}

        value_label = tk.Label(
            frame,
            text=value_text,
            **value_style
        )
        value_label.pack(side=tk.LEFT)

        return frame, value_label

    def create_stat_row(self, parent, label_text: str, value_text: str, icon: str = None, color=None) -> tk.Frame:
        """创建统计行（带图标和颜色）"""
        frame = tk.Frame(parent, bg=Theme.BG_TERTIARY)

        # 图标
        if icon:
            icon_label = tk.Label(
                frame,
                text=icon,
                font=Theme.get_font(Theme.FONT_SIZE_MD),
                bg=Theme.BG_TERTIARY,
                fg=color or Theme.TEXT_PRIMARY
            )
            icon_label.pack(side=tk.LEFT, padx=(0, Theme.SPACING_XS))

        # 标签
        label = tk.Label(
            frame,
            text=label_text,
            **Theme.get_label_style("normal")
        )
        label.pack(side=tk.LEFT)

        # 值
        value_style = Theme.get_label_style("normal")
        if color:
            value_style = {**value_style, "fg": color}

        value_label = tk.Label(
            frame,
            text=value_text,
            font=Theme.get_font(Theme.FONT_SIZE_MD, bold=True),
            bg=Theme.BG_TERTIARY,
            fg=color or Theme.TEXT_PRIMARY
        )
        value_label.pack(side=tk.RIGHT)

        return frame, value_label
