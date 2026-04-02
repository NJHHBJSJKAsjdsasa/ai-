"""
动画管理器 - 统一管理GUI动画效果
"""
import tkinter as tk
from typing import Callable, Optional, Dict, List, Tuple, Union
from enum import Enum
import time
import math


class EasingType(Enum):
    """缓动函数类型"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_IN_SINE = "ease_in_sine"
    EASE_OUT_SINE = "ease_out_sine"
    EASE_IN_OUT_SINE = "ease_in_out_sine"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    EASE_IN_QUINT = "ease_in_quint"
    EASE_OUT_QUINT = "ease_out_quint"
    EASE_IN_OUT_QUINT = "ease_in_out_quint"
    EASE_IN_EXPO = "ease_in_expo"
    EASE_OUT_EXPO = "ease_out_expo"
    EASE_IN_OUT_EXPO = "ease_in_out_expo"
    EASE_IN_CIRC = "ease_in_circ"
    EASE_OUT_CIRC = "ease_out_circ"
    EASE_IN_OUT_CIRC = "ease_in_out_circ"
    EASE_IN_BACK = "ease_in_back"
    EASE_OUT_BACK = "ease_out_back"
    EASE_IN_OUT_BACK = "ease_in_out_back"
    EASE_IN_ELASTIC = "ease_in_elastic"
    EASE_OUT_ELASTIC = "ease_out_elastic"
    EASE_IN_OUT_ELASTIC = "ease_in_out_elastic"


class AnimationType(Enum):
    """动画类型"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    MOVE = "move"
    SCALE = "scale"
    COLOR = "color"
    ROTATE = "rotate"
    SHAKE = "shake"
    PULSE = "pulse"
    SLIDE_IN_LEFT = "slide_in_left"
    SLIDE_IN_RIGHT = "slide_in_right"
    SLIDE_IN_TOP = "slide_in_top"
    SLIDE_IN_BOTTOM = "slide_in_bottom"
    BOUNCE = "bounce"
    FLIP = "flip"


class Animation:
    """单个动画实例"""

    def __init__(
        self,
        widget: tk.Widget,
        animation_type: AnimationType,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        start_value: Union[float, Tuple] = 0,
        end_value: Union[float, Tuple] = 1,
        on_update: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        delay: int = 0
    ):
        self.widget = widget
        self.animation_type = animation_type
        self.duration = duration
        self.easing = easing
        self.start_value = start_value
        self.end_value = end_value
        self.on_update = on_update
        self.on_complete = on_complete
        self.delay = delay

        self._start_time: Optional[float] = None
        self._after_id: Optional[str] = None
        self._is_running = False
        self._is_cancelled = False
        self._last_update_time = 0.0

    def start(self):
        """开始动画"""
        if self.delay > 0:
            self._after_id = self.widget.after(self.delay, self._do_start)
        else:
            self._do_start()

    def _do_start(self):
        """实际开始动画"""
        self._start_time = time.time()
        self._is_running = True
        self._is_cancelled = False
        self._update()

    def _update(self):
        """更新动画帧 - 优化性能，减少不必要的重绘"""
        if self._is_cancelled or not self._is_running:
            return

        elapsed = (time.time() - self._start_time) * 1000
        progress = min(elapsed / self.duration, 1.0)

        # 应用缓动函数
        eased_progress = self._apply_easing(progress)

        # 计算当前值
        if isinstance(self.start_value, tuple):
            current_value = tuple(
                start + (end - start) * eased_progress
                for start, end in zip(self.start_value, self.end_value)
            )
        else:
            current_value = self.start_value + (self.end_value - self.start_value) * eased_progress

        # 调用更新回调
        if self.on_update:
            self.on_update(current_value)

        if progress < 1.0:
            # 动态调整帧率，优化性能
            # 对于高DPI屏幕，保持60fps；对于普通情况，可以适当降低
            interval = 16  # ~60fps
            self._after_id = self.widget.after(interval, self._update)
        else:
            self._is_running = False
            if self.on_complete:
                self.on_complete()

    def _apply_easing(self, t: float) -> float:
        """应用缓动函数 - 包含所有新增的缓动函数"""
        c1 = 1.70158
        c2 = c1 * 1.525
        c3 = c1 + 1
        c4 = (2 * math.pi) / 3
        c5 = (2 * math.pi) / 4.5
        n1 = 7.5625
        d1 = 2.75

        if self.easing == EasingType.LINEAR:
            return t
        elif self.easing == EasingType.EASE_IN:
            return t * t
        elif self.easing == EasingType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.easing == EasingType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - pow(-2 * t + 2, 2) / 2
        elif self.easing == EasingType.EASE_OUT_BOUNCE:
            if t < 1 / d1:
                return n1 * t * t
            elif t < 2 / d1:
                t -= 1.5 / d1
                return n1 * t * t + 0.75
            elif t < 2.5 / d1:
                t -= 2.25 / d1
                return n1 * t * t + 0.9375
            else:
                t -= 2.625 / d1
                return n1 * t * t + 0.984375
        elif self.easing == EasingType.EASE_IN_SINE:
            return 1 - math.cos((t * math.pi) / 2)
        elif self.easing == EasingType.EASE_OUT_SINE:
            return math.sin((t * math.pi) / 2)
        elif self.easing == EasingType.EASE_IN_OUT_SINE:
            return -(math.cos(math.pi * t) - 1) / 2
        elif self.easing == EasingType.EASE_IN_QUAD or self.easing == EasingType.EASE_IN:
            return t * t
        elif self.easing == EasingType.EASE_OUT_QUAD or self.easing == EasingType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.easing == EasingType.EASE_IN_OUT_QUAD or self.easing == EasingType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - pow(-2 * t + 2, 2) / 2
        elif self.easing == EasingType.EASE_IN_CUBIC:
            return t * t * t
        elif self.easing == EasingType.EASE_OUT_CUBIC:
            return 1 - pow(1 - t, 3)
        elif self.easing == EasingType.EASE_IN_OUT_CUBIC:
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 3) / 2
        elif self.easing == EasingType.EASE_IN_QUART:
            return t * t * t * t
        elif self.easing == EasingType.EASE_OUT_QUART:
            return 1 - pow(1 - t, 4)
        elif self.easing == EasingType.EASE_IN_OUT_QUART:
            if t < 0.5:
                return 8 * t * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 4) / 2
        elif self.easing == EasingType.EASE_IN_QUINT:
            return t * t * t * t * t
        elif self.easing == EasingType.EASE_OUT_QUINT:
            return 1 - pow(1 - t, 5)
        elif self.easing == EasingType.EASE_IN_OUT_QUINT:
            if t < 0.5:
                return 16 * t * t * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 5) / 2
        elif self.easing == EasingType.EASE_IN_EXPO:
            return 0 if t == 0 else pow(2, 10 * t - 10)
        elif self.easing == EasingType.EASE_OUT_EXPO:
            return 1 if t == 1 else 1 - pow(2, -10 * t)
        elif self.easing == EasingType.EASE_IN_OUT_EXPO:
            if t == 0:
                return 0
            elif t == 1:
                return 1
            elif t < 0.5:
                return pow(2, 20 * t - 10) / 2
            else:
                return (2 - pow(2, -20 * t + 10)) / 2
        elif self.easing == EasingType.EASE_IN_CIRC:
            return 1 - math.sqrt(1 - pow(t, 2))
        elif self.easing == EasingType.EASE_OUT_CIRC:
            return math.sqrt(1 - pow(t - 1, 2))
        elif self.easing == EasingType.EASE_IN_OUT_CIRC:
            if t < 0.5:
                return (1 - math.sqrt(1 - pow(2 * t, 2))) / 2
            else:
                return (math.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2
        elif self.easing == EasingType.EASE_IN_BACK:
            return c3 * t * t * t - c1 * t * t
        elif self.easing == EasingType.EASE_OUT_BACK:
            return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
        elif self.easing == EasingType.EASE_IN_OUT_BACK:
            if t < 0.5:
                return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
            else:
                return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
        elif self.easing == EasingType.EASE_IN_ELASTIC:
            if t == 0:
                return 0
            elif t == 1:
                return 1
            else:
                return -pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * c4)
        elif self.easing == EasingType.EASE_OUT_ELASTIC:
            if t == 0:
                return 0
            elif t == 1:
                return 1
            else:
                return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
        elif self.easing == EasingType.EASE_IN_OUT_ELASTIC:
            if t == 0:
                return 0
            elif t == 1:
                return 1
            elif t < 0.5:
                return -(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
            else:
                return (pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1
        return t

    def cancel(self):
        """取消动画"""
        self._is_cancelled = True
        self._is_running = False
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def is_running(self) -> bool:
        """检查动画是否正在运行"""
        return self._is_running


class AnimationManager:
    """动画管理器 - 统一管理所有动画"""

    _instance: Optional['AnimationManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._animations: Dict[str, Animation] = {}
        self._animation_id_counter = 0
        self._enabled = True

    def set_enabled(self, enabled: bool):
        """设置动画是否启用"""
        self._enabled = enabled
        if not enabled:
            self.cancel_all()

    def is_enabled(self) -> bool:
        """检查动画是否启用"""
        return self._enabled

    def _generate_id(self) -> str:
        """生成动画ID"""
        self._animation_id_counter += 1
        return f"anim_{self._animation_id_counter}"

    def animate(
        self,
        widget: tk.Widget,
        animation_type: AnimationType,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        start_value: Union[float, Tuple] = 0,
        end_value: Union[float, Tuple] = 1,
        on_update: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        delay: int = 0
    ) -> str:
        """
        创建并启动动画

        Args:
            widget: 目标组件
            animation_type: 动画类型
            duration: 动画时长（毫秒）
            easing: 缓动函数类型
            start_value: 起始值
            end_value: 结束值
            on_update: 更新回调
            on_complete: 完成回调
            delay: 延迟（毫秒）

        Returns:
            动画ID
        """
        if not self._enabled:
            if on_update:
                on_update(end_value)
            if on_complete:
                on_complete()
            return ""

        anim_id = self._generate_id()
        animation = Animation(
            widget=widget,
            animation_type=animation_type,
            duration=duration,
            easing=easing,
            start_value=start_value,
            end_value=end_value,
            on_update=on_update,
            on_complete=on_complete,
            delay=delay
        )
        self._animations[anim_id] = animation

        # 在动画完成时清理
        original_complete = on_complete
        def cleanup():
            self._animations.pop(anim_id, None)
            if original_complete:
                original_complete()

        animation.on_complete = cleanup
        animation.start()

        return anim_id

    def fade_in(
        self,
        widget: tk.Widget,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """淡入动画"""
        def update_opacity(value):
            try:
                alpha = int(value * 255)
                if isinstance(widget, tk.Toplevel):
                    widget.attributes('-alpha', value)
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.FADE_IN,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_opacity,
            on_complete=on_complete
        )

    def fade_out(
        self,
        widget: tk.Widget,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_IN,
        on_complete: Optional[Callable] = None
    ) -> str:
        """淡出动画"""
        def update_opacity(value):
            try:
                if isinstance(widget, tk.Toplevel):
                    widget.attributes('-alpha', value)
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.FADE_OUT,
            duration=duration,
            easing=easing,
            start_value=1.0,
            end_value=0.0,
            on_update=update_opacity,
            on_complete=on_complete
        )

    def move(
        self,
        widget: tk.Widget,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """移动动画"""
        def update_position(value):
            try:
                x, y = value
                widget.place(x=int(x), y=int(y))
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.MOVE,
            duration=duration,
            easing=easing,
            start_value=(start_x, start_y),
            end_value=(end_x, end_y),
            on_update=update_position,
            on_complete=on_complete
        )

    def scale(
        self,
        widget: tk.Widget,
        start_scale: float,
        end_scale: float,
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """缩放动画"""
        def update_scale(value):
            try:
                pass
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SCALE,
            duration=duration,
            easing=easing,
            start_value=start_scale,
            end_value=end_scale,
            on_update=update_scale,
            on_complete=on_complete
        )

    def color_transition(
        self,
        widget: tk.Widget,
        start_color: Tuple[int, int, int],
        end_color: Tuple[int, int, int],
        duration: int = 300,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """颜色过渡动画"""
        def update_color(value):
            try:
                r, g, b = int(value[0]), int(value[1]), int(value[2])
                color = f"#{r:02x}{g:02x}{b:02x}"
                widget.config(bg=color)
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.COLOR,
            duration=duration,
            easing=easing,
            start_value=start_color,
            end_value=end_color,
            on_update=update_color,
            on_complete=on_complete
        )

    def shake(
        self,
        widget: tk.Widget,
        amplitude: int = 10,
        duration: int = 500,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None
    ) -> str:
        """抖动动画"""
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()

        def update_shake(value):
            try:
                offset = math.sin(value * math.pi * 8) * (1 - value) * amplitude
                widget.place(x=original_x + int(offset), y=original_y)
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SHAKE,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_shake,
            on_complete=on_complete
        )

    def pulse(
        self,
        widget: tk.Widget,
        scale_factor: float = 1.1,
        duration: int = 500,
        easing: EasingType = EasingType.EASE_IN_OUT_SINE,
        on_complete: Optional[Callable] = None
    ) -> str:
        """脉冲动画"""
        def update_pulse(value):
            try:
                if value < 0.5:
                    scale = 1 + (scale_factor - 1) * (value * 2)
                else:
                    scale = scale_factor - (scale_factor - 1) * ((value - 0.5) * 2)
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.PULSE,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_pulse,
            on_complete=on_complete
        )

    def slide_in_left(
        self,
        widget: tk.Widget,
        distance: int = 200,
        duration: int = 400,
        easing: EasingType = EasingType.EASE_OUT_CUBIC,
        on_complete: Optional[Callable] = None
    ) -> str:
        """从左侧滑入动画"""
        original_x = widget.winfo_x()
        
        def update_slide(value):
            try:
                current_x = original_x - distance + distance * value
                widget.place(x=int(current_x), y=widget.winfo_y())
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SLIDE_IN_LEFT,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_slide,
            on_complete=on_complete
        )

    def slide_in_right(
        self,
        widget: tk.Widget,
        distance: int = 200,
        duration: int = 400,
        easing: EasingType = EasingType.EASE_OUT_CUBIC,
        on_complete: Optional[Callable] = None
    ) -> str:
        """从右侧滑入动画"""
        original_x = widget.winfo_x()
        
        def update_slide(value):
            try:
                current_x = original_x + distance - distance * value
                widget.place(x=int(current_x), y=widget.winfo_y())
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SLIDE_IN_RIGHT,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_slide,
            on_complete=on_complete
        )

    def slide_in_top(
        self,
        widget: tk.Widget,
        distance: int = 200,
        duration: int = 400,
        easing: EasingType = EasingType.EASE_OUT_CUBIC,
        on_complete: Optional[Callable] = None
    ) -> str:
        """从顶部滑入动画"""
        original_y = widget.winfo_y()
        
        def update_slide(value):
            try:
                current_y = original_y - distance + distance * value
                widget.place(x=widget.winfo_x(), y=int(current_y))
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SLIDE_IN_TOP,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_slide,
            on_complete=on_complete
        )

    def slide_in_bottom(
        self,
        widget: tk.Widget,
        distance: int = 200,
        duration: int = 400,
        easing: EasingType = EasingType.EASE_OUT_CUBIC,
        on_complete: Optional[Callable] = None
    ) -> str:
        """从底部滑入动画"""
        original_y = widget.winfo_y()
        
        def update_slide(value):
            try:
                current_y = original_y + distance - distance * value
                widget.place(x=widget.winfo_x(), y=int(current_y))
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.SLIDE_IN_BOTTOM,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_slide,
            on_complete=on_complete
        )

    def bounce(
        self,
        widget: tk.Widget,
        height: int = 50,
        duration: int = 600,
        easing: EasingType = EasingType.EASE_OUT_BOUNCE,
        on_complete: Optional[Callable] = None
    ) -> str:
        """弹跳动画"""
        original_y = widget.winfo_y()
        
        def update_bounce(value):
            try:
                offset = height * (1 - value)
                widget.place(x=widget.winfo_x(), y=int(original_y - offset))
            except tk.TclError:
                pass

        return self.animate(
            widget=widget,
            animation_type=AnimationType.BOUNCE,
            duration=duration,
            easing=easing,
            start_value=0.0,
            end_value=1.0,
            on_update=update_bounce,
            on_complete=on_complete
        )

    def cancel(self, anim_id: str):
        """取消指定动画"""
        if anim_id in self._animations:
            self._animations[anim_id].cancel()
            del self._animations[anim_id]

    def cancel_all(self):
        """取消所有动画"""
        for animation in list(self._animations.values()):
            animation.cancel()
        self._animations.clear()

    def cancel_widget_animations(self, widget: tk.Widget):
        """取消指定组件的所有动画"""
        to_cancel = [
            anim_id for anim_id, anim in self._animations.items()
            if anim.widget == widget
        ]
        for anim_id in to_cancel:
            self.cancel(anim_id)


# 全局动画管理器实例
animation_manager = AnimationManager()


def get_animation_manager() -> AnimationManager:
    """获取动画管理器实例"""
    return animation_manager
