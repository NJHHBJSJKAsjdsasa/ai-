"""
动画管理器 - 统一管理GUI动画效果
"""
import tkinter as tk
from typing import Callable, Optional, Dict, List, Tuple, Union
from enum import Enum
import time


class EasingType(Enum):
    """缓动函数类型"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EASE_OUT_BOUNCE = "ease_out_bounce"


class AnimationType(Enum):
    """动画类型"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    MOVE = "move"
    SCALE = "scale"
    COLOR = "color"


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
        """更新动画帧"""
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
            self._after_id = self.widget.after(16, self._update)  # ~60fps
        else:
            self._is_running = False
            if self.on_complete:
                self.on_complete()

    def _apply_easing(self, t: float) -> float:
        """应用缓动函数"""
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
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
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
                # 对于Toplevel窗口
                if isinstance(widget, tk.Toplevel):
                    widget.attributes('-alpha', value)
                else:
                    # 对于普通组件，通过颜色模拟透明度
                    widget.update()
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
                else:
                    widget.update()
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
                # 缩放效果通过字体大小模拟
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
