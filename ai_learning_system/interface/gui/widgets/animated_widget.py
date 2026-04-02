"""
动画组件基类 - 支持动画效果的UI组件
"""
import tkinter as tk
from typing import Optional, Callable, Tuple
from ..theme import Theme
from ..animation_manager import animation_manager, EasingType


class AnimatedMixin:
    """动画混入类 - 为组件添加动画支持"""

    def __init__(self, *args, **kwargs):
        self._anim_id: Optional[str] = None
        self._original_bg: Optional[str] = None
        self._is_animating = False

    def animate_color(
        self,
        target_color: str,
        duration: int = None,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """颜色过渡动画"""
        if not Theme.is_animation_enabled():
            self.config(bg=target_color)
            if on_complete:
                on_complete()
            return ""

        if duration is None:
            duration = Theme.ANIMATION_DURATION

        current_bg = self.cget("bg")
        if not self._original_bg:
            self._original_bg = current_bg

        start_rgb = Theme.hex_to_rgb(current_bg) if current_bg.startswith("#") else (30, 30, 46)
        end_rgb = Theme.hex_to_rgb(target_color)

        self._anim_id = animation_manager.color_transition(
            self,
            start_rgb,
            end_rgb,
            duration=duration,
            easing=easing,
            on_complete=on_complete
        )
        return self._anim_id

    def cancel_animation(self):
        """取消当前动画"""
        if self._anim_id:
            animation_manager.cancel(self._anim_id)
            self._anim_id = None


class AnimatedFrame(tk.Frame, AnimatedMixin):
    """支持动画的Frame"""

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        AnimatedMixin.__init__(self)
        self._setup_animation()

    def _setup_animation(self):
        """设置动画初始状态"""
        self._opacity = 1.0

    def fade_in(self, duration: int = None, on_complete: Optional[Callable] = None):
        """淡入"""
        if duration is None:
            duration = Theme.ANIMATION_DURATION
        return animation_manager.fade_in(self, duration, on_complete=on_complete)

    def fade_out(self, duration: int = None, on_complete: Optional[Callable] = None):
        """淡出"""
        if duration is None:
            duration = Theme.ANIMATION_DURATION
        return animation_manager.fade_out(self, duration, on_complete=on_complete)


class AnimatedLabel(tk.Label, AnimatedMixin):
    """支持动画的Label"""

    def __init__(self, parent, **kwargs):
        tk.Label.__init__(self, parent, **kwargs)
        AnimatedMixin.__init__(self)
        self._original_fg = kwargs.get("fg", Theme.TEXT_PRIMARY)

    def animate_text_color(
        self,
        target_color: str,
        duration: int = None,
        on_complete: Optional[Callable] = None
    ):
        """文字颜色动画"""
        if not Theme.is_animation_enabled():
            self.config(fg=target_color)
            if on_complete:
                on_complete()
            return ""

        if duration is None:
            duration = Theme.ANIMATION_DURATION

        current_fg = self.cget("fg")
        start_rgb = Theme.hex_to_rgb(current_fg) if current_fg.startswith("#") else (234, 234, 234)
        end_rgb = Theme.hex_to_rgb(target_color)

        def update_color(value):
            try:
                r, g, b = int(value[0]), int(value[1]), int(value[2])
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.config(fg=color)
            except tk.TclError:
                pass

        return animation_manager.animate(
            self,
            animation_manager.animate.__func__.__code__,
            duration=duration,
            easing=EasingType.EASE_OUT,
            start_value=start_rgb,
            end_value=end_rgb,
            on_update=update_color,
            on_complete=on_complete
        )

    def pulse(self, duration: int = 1000, count: int = 3):
        """脉冲动画效果"""
        if not Theme.is_animation_enabled():
            return

        original_color = self.cget("fg")
        highlight_color = Theme.ACCENT_GOLD

        def pulse_cycle(remaining):
            if remaining <= 0:
                self.config(fg=original_color)
                return

            self.animate_text_color(
                highlight_color,
                duration=duration // (count * 2),
                on_complete=lambda: self.animate_text_color(
                    original_color,
                    duration=duration // (count * 2),
                    on_complete=lambda: pulse_cycle(remaining - 1)
                )
            )

        pulse_cycle(count)


class AnimatedButton(tk.Button):
    """支持悬停动画的按钮"""

    def __init__(
        self,
        parent,
        hover_bg: Optional[str] = None,
        hover_fg: Optional[str] = None,
        animation_duration: int = None,
        **kwargs
    ):
        # 保存原始颜色
        self._original_bg = kwargs.get("bg", Theme.BG_TERTIARY)
        self._original_fg = kwargs.get("fg", Theme.TEXT_PRIMARY)
        self._hover_bg = hover_bg or self._lighten_color(self._original_bg)
        self._hover_fg = hover_fg or self._original_fg
        self._animation_duration = animation_duration or Theme.ANIMATION_DURATION_FAST
        self._anim_id = None

        super().__init__(parent, **kwargs)

        # 绑定悬停事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _lighten_color(self, color: str) -> str:
        """提亮颜色"""
        try:
            r, g, b = Theme.hex_to_rgb(color)
            factor = Theme.HOVER_BRIGHTNESS
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return Theme.rgb_to_hex(r, g, b)
        except:
            return color

    def _on_enter(self, event=None):
        """鼠标进入"""
        if not Theme.is_animation_enabled():
            self.config(bg=self._hover_bg, fg=self._hover_fg)
            return

        self._cancel_animation()
        self._anim_id = self._animate_to(self._hover_bg, self._hover_fg)

    def _on_leave(self, event=None):
        """鼠标离开"""
        if not Theme.is_animation_enabled():
            self.config(bg=self._original_bg, fg=self._original_fg)
            return

        self._cancel_animation()
        self._anim_id = self._animate_to(self._original_bg, self._original_fg)

    def _animate_to(self, target_bg: str, target_fg: str) -> str:
        """动画过渡到目标颜色"""
        current_bg = self.cget("bg")
        current_fg = self.cget("fg")

        start_bg_rgb = Theme.hex_to_rgb(current_bg) if current_bg.startswith("#") else Theme.hex_to_rgb(self._original_bg)
        end_bg_rgb = Theme.hex_to_rgb(target_bg)
        start_fg_rgb = Theme.hex_to_rgb(current_fg) if current_fg.startswith("#") else Theme.hex_to_rgb(self._original_fg)
        end_fg_rgb = Theme.hex_to_rgb(target_fg)

        def update_colors(value):
            try:
                progress = value if isinstance(value, (int, float)) else 0.5
                # 背景颜色
                r = int(start_bg_rgb[0] + (end_bg_rgb[0] - start_bg_rgb[0]) * progress)
                g = int(start_bg_rgb[1] + (end_bg_rgb[1] - start_bg_rgb[1]) * progress)
                b = int(start_bg_rgb[2] + (end_bg_rgb[2] - start_bg_rgb[2]) * progress)
                bg_color = f"#{r:02x}{g:02x}{b:02x}"

                # 前景颜色
                r = int(start_fg_rgb[0] + (end_fg_rgb[0] - start_fg_rgb[0]) * progress)
                g = int(start_fg_rgb[1] + (end_fg_rgb[1] - start_fg_rgb[1]) * progress)
                b = int(start_fg_rgb[2] + (end_fg_rgb[2] - start_fg_rgb[2]) * progress)
                fg_color = f"#{r:02x}{g:02x}{b:02x}"

                self.config(bg=bg_color, fg=fg_color)
            except tk.TclError:
                pass

        return animation_manager.animate(
            self,
            None,
            duration=self._animation_duration,
            easing=EasingType.EASE_OUT,
            start_value=0.0,
            end_value=1.0,
            on_update=update_colors
        )

    def _cancel_animation(self):
        """取消当前动画"""
        if self._anim_id:
            animation_manager.cancel(self._anim_id)
            self._anim_id = None


class AnimatedProgressBar(tk.Canvas):
    """支持平滑动画的进度条"""

    def __init__(
        self,
        parent,
        height: int = 20,
        bg_color: str = None,
        fill_color: str = None,
        animation_duration: int = None,
        **kwargs
    ):
        self._height = height
        self._bg_color = bg_color or Theme.BG_PRIMARY
        self._fill_color = fill_color or Theme.ACCENT_CYAN
        self._animation_duration = animation_duration or Theme.ANIMATION_DURATION
        self._current_progress = 0.0
        self._target_progress = 0.0
        self._anim_id = None

        super().__init__(
            parent,
            height=height,
            bg=self._bg_color,
            highlightthickness=0,
            **kwargs
        )

        # 等待组件渲染完成
        self.after(100, self._draw_initial)

    def _draw_initial(self):
        """绘制初始状态"""
        self._draw_progress(0)

    def _draw_progress(self, progress: float):
        """绘制进度"""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1:
            return

        # 背景
        self.create_rectangle(0, 0, width, height, fill=self._bg_color, outline="")

        # 进度
        if progress > 0:
            fill_width = int(width * progress)
            self.create_rectangle(0, 0, fill_width, height, fill=self._fill_color, outline="")

    def set_progress(
        self,
        value: float,
        maximum: float = 100,
        animate: bool = True
    ):
        """设置进度值

        Args:
            value: 当前值
            maximum: 最大值
            animate: 是否使用动画
        """
        if maximum <= 0:
            return

        target = min(value / maximum, 1.0)
        self._target_progress = target

        if not animate or not Theme.is_animation_enabled():
            self._current_progress = target
            self._draw_progress(target)
            return

        # 取消之前的动画
        if self._anim_id:
            animation_manager.cancel(self._anim_id)

        start_progress = self._current_progress

        def update_progress(value):
            self._current_progress = value
            self._draw_progress(value)

        self._anim_id = animation_manager.animate(
            self,
            None,
            duration=self._animation_duration,
            easing=EasingType.EASE_OUT,
            start_value=start_progress,
            end_value=target,
            on_update=update_progress
        )

    def set_color(self, fill_color: str):
        """设置进度条颜色"""
        self._fill_color = fill_color
        self._draw_progress(self._current_progress)


class AnimatedCard(tk.Frame):
    """带动画效果的卡片组件"""

    def __init__(
        self,
        parent,
        bg_color: str = None,
        border_color: str = None,
        padding: int = 15,
        animation_duration: int = None,
        **kwargs
    ):
        self._bg_color = bg_color or Theme.BG_TERTIARY
        self._border_color = border_color or Theme.BORDER_LIGHT
        self._animation_duration = animation_duration or Theme.ANIMATION_DURATION
        self._hover_scale = Theme.HOVER_SCALE
        self._is_hovered = False

        super().__init__(parent, bg=self._bg_color, **kwargs)

        # 内边距
        self.config(padx=padding, pady=padding)

        # 绑定悬停事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        """鼠标进入"""
        if not self._is_hovered:
            self._is_hovered = True
            if Theme.is_animation_enabled():
                self._animate_highlight(True)
            else:
                self.config(bg=self._lighten_color(self._bg_color))

    def _on_leave(self, event=None):
        """鼠标离开"""
        if self._is_hovered:
            self._is_hovered = False
            if Theme.is_animation_enabled():
                self._animate_highlight(False)
            else:
                self.config(bg=self._bg_color)

    def _animate_highlight(self, highlight: bool):
        """高亮动画"""
        target_color = self._lighten_color(self._bg_color) if highlight else self._bg_color
        current_color = self.cget("bg")

        start_rgb = Theme.hex_to_rgb(current_color) if current_color.startswith("#") else Theme.hex_to_rgb(self._bg_color)
        end_rgb = Theme.hex_to_rgb(target_color)

        def update_color(value):
            try:
                r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * value)
                g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * value)
                b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * value)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.config(bg=color)
            except tk.TclError:
                pass

        animation_manager.animate(
            self,
            None,
            duration=self._animation_duration,
            easing=EasingType.EASE_OUT,
            start_value=0.0,
            end_value=1.0,
            on_update=update_color
        )

    def _lighten_color(self, color: str) -> str:
        """提亮颜色"""
        try:
            r, g, b = Theme.hex_to_rgb(color)
            factor = Theme.HOVER_BRIGHTNESS
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return Theme.rgb_to_hex(r, g, b)
        except:
            return color
