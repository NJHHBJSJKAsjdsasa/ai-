"""
战斗特效组件 - 提供战斗动画效果
"""
import tkinter as tk
from typing import Optional, Callable
import random
from ..theme import Theme
from ..animation_manager import animation_manager, EasingType


class CombatEffects:
    """战斗特效管理器"""

    @staticmethod
    def show_damage_number(
        parent: tk.Widget,
        damage: int,
        x: int,
        y: int,
        is_critical: bool = False,
        is_heal: bool = False,
        on_complete: Optional[Callable] = None
    ):
        """显示伤害数字浮动动画

        Args:
            parent: 父组件
            damage: 伤害数值
            x: 起始X坐标
            y: 起始Y坐标
            is_critical: 是否暴击
            is_heal: 是否治疗
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        # 创建伤害数字标签
        if is_heal:
            color = Theme.ACCENT_GREEN
            text = f"+{damage}"
            font_size = 14
        elif is_critical:
            color = "#ff6b6b"
            text = f"{damage}!"
            font_size = 18
        else:
            color = Theme.ACCENT_RED
            text = f"-{damage}"
            font_size = 14

        label = tk.Label(
            parent,
            text=text,
            fg=color,
            bg=Theme.BG_SECONDARY,
            font=Theme.get_font(font_size, bold=True)
        )
        label.place(x=x, y=y)

        # 浮动动画参数
        start_y = y
        end_y = y - 50  # 向上浮动50像素
        start_x = x
        end_x = x + random.randint(-20, 20)  # 随机左右偏移

        # 淡出动画
        def update_position(progress):
            try:
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
                label.place(x=int(current_x), y=int(current_y))

                # 同时淡出
                alpha = 1.0 - progress
                if alpha > 0.3:
                    label.config(fg=color)
            except tk.TclError:
                pass

        def cleanup():
            try:
                label.destroy()
            except tk.TclError:
                pass
            if on_complete:
                on_complete()

        animation_manager.animate(
            label,
            None,
            duration=800,
            easing=EasingType.EASE_OUT,
            start_value=0.0,
            end_value=1.0,
            on_update=update_position,
            on_complete=cleanup
        )

    @staticmethod
    def shake_widget(
        widget: tk.Widget,
        intensity: int = 5,
        duration: int = 300,
        on_complete: Optional[Callable] = None
    ):
        """震动效果

        Args:
            widget: 目标组件
            intensity: 震动强度（像素）
            duration: 动画时长
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        # 获取当前位置
        try:
            current_x = widget.winfo_x()
            current_y = widget.winfo_y()
        except:
            current_x = current_y = 0

        original_pos = (current_x, current_y)

        def shake_update(progress):
            try:
                # 使用正弦波产生震动效果
                import math
                shake_x = int(math.sin(progress * 20) * intensity * (1 - progress))
                shake_y = int(math.cos(progress * 15) * intensity * (1 - progress))
                widget.place(x=original_pos[0] + shake_x, y=original_pos[1] + shake_y)
            except tk.TclError:
                pass

        def cleanup():
            try:
                widget.place(x=original_pos[0], y=original_pos[1])
            except tk.TclError:
                pass
            if on_complete:
                on_complete()

        animation_manager.animate(
            widget,
            None,
            duration=duration,
            easing=EasingType.LINEAR,
            start_value=0.0,
            end_value=1.0,
            on_update=shake_update,
            on_complete=cleanup
        )

    @staticmethod
    def flash_effect(
        widget: tk.Widget,
        flash_color: str = Theme.ACCENT_GOLD,
        duration: int = 200,
        on_complete: Optional[Callable] = None
    ):
        """闪光效果

        Args:
            widget: 目标组件
            flash_color: 闪光颜色
            duration: 动画时长
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        original_bg = widget.cget("bg")
        original_fg = widget.cget("fg")

        flash_rgb = Theme.hex_to_rgb(flash_color)
        bg_rgb = Theme.hex_to_rgb(original_bg) if original_bg.startswith("#") else (22, 33, 62)
        fg_rgb = Theme.hex_to_rgb(original_fg) if original_fg.startswith("#") else (234, 234, 234)

        def flash_update(progress):
            try:
                # 先变亮再恢复
                if progress < 0.5:
                    # 变亮阶段
                    p = progress * 2
                    r = int(bg_rgb[0] + (flash_rgb[0] - bg_rgb[0]) * p)
                    g = int(bg_rgb[1] + (flash_rgb[1] - bg_rgb[1]) * p)
                    b = int(bg_rgb[2] + (flash_rgb[2] - bg_rgb[2]) * p)
                else:
                    # 恢复阶段
                    p = (progress - 0.5) * 2
                    r = int(flash_rgb[0] + (bg_rgb[0] - flash_rgb[0]) * p)
                    g = int(flash_rgb[1] + (bg_rgb[1] - flash_rgb[1]) * p)
                    b = int(flash_rgb[2] + (bg_rgb[2] - flash_rgb[2]) * p)

                color = f"#{r:02x}{g:02x}{b:02x}"
                widget.config(bg=color)
            except tk.TclError:
                pass

        def cleanup():
            try:
                widget.config(bg=original_bg, fg=original_fg)
            except tk.TclError:
                pass
            if on_complete:
                on_complete()

        animation_manager.animate(
            widget,
            None,
            duration=duration,
            easing=EasingType.EASE_IN_OUT,
            start_value=0.0,
            end_value=1.0,
            on_update=flash_update,
            on_complete=cleanup
        )

    @staticmethod
    def skill_cast_effect(
        parent: tk.Widget,
        skill_name: str,
        x: int,
        y: int,
        on_complete: Optional[Callable] = None
    ):
        """技能释放效果

        Args:
            parent: 父组件
            skill_name: 技能名称
            x: 位置X
            y: 位置Y
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        # 创建技能名称标签
        label = tk.Label(
            parent,
            text=f"✨ {skill_name}",
            fg=Theme.ACCENT_PURPLE,
            bg=Theme.BG_SECONDARY,
            font=Theme.get_font(12, bold=True)
        )
        label.place(x=x, y=y)

        start_y = y
        end_y = y - 30

        def update_position(progress):
            try:
                current_y = start_y + (end_y - start_y) * progress
                label.place(y=int(current_y))

                # 放大效果
                scale = 1.0 + progress * 0.5
                font_size = int(12 * scale)
                label.config(font=Theme.get_font(font_size, bold=True))
            except tk.TclError:
                pass

        def cleanup():
            try:
                label.destroy()
            except tk.TclError:
                pass
            if on_complete:
                on_complete()

        animation_manager.animate(
            label,
            None,
            duration=600,
            easing=EasingType.EASE_OUT,
            start_value=0.0,
            end_value=1.0,
            on_update=update_position,
            on_complete=cleanup
        )

    @staticmethod
    def victory_effect(
        parent: tk.Widget,
        on_complete: Optional[Callable] = None
    ):
        """胜利效果

        Args:
            parent: 父组件
            on_complete: 完成回调
        """
        if not Theme.is_animation_enabled():
            if on_complete:
                on_complete()
            return

        # 创建胜利标签
        label = tk.Label(
            parent,
            text="🎉 胜利!",
            fg=Theme.ACCENT_GOLD,
            bg=Theme.BG_SECONDARY,
            font=Theme.get_font(24, bold=True)
        )
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        def scale_update(progress):
            try:
                # 弹跳缩放效果
                import math
                scale = 1.0 + math.sin(progress * math.pi) * 0.5
                font_size = int(24 * scale)
                label.config(font=Theme.get_font(font_size, bold=True))
            except tk.TclError:
                pass

        def cleanup():
            try:
                label.destroy()
            except tk.TclError:
                pass
            if on_complete:
                on_complete()

        animation_manager.animate(
            label,
            None,
            duration=1000,
            easing=EasingType.EASE_OUT_BOUNCE,
            start_value=0.0,
            end_value=1.0,
            on_update=scale_update,
            on_complete=cleanup
        )


# 便捷函数
def show_damage(
    parent: tk.Widget,
    damage: int,
    x: int,
    y: int,
    is_critical: bool = False,
    on_complete: Optional[Callable] = None
):
    """显示伤害数字"""
    CombatEffects.show_damage_number(parent, damage, x, y, is_critical, False, on_complete)


def show_heal(
    parent: tk.Widget,
    amount: int,
    x: int,
    y: int,
    on_complete: Optional[Callable] = None
):
    """显示治疗数字"""
    CombatEffects.show_damage_number(parent, amount, x, y, False, True, on_complete)


def shake_widget(widget: tk.Widget, intensity: int = 5, duration: int = 300):
    """震动组件"""
    CombatEffects.shake_widget(widget, intensity, duration)


def flash_widget(widget: tk.Widget, flash_color: str = None, duration: int = 200):
    """闪光效果"""
    color = flash_color or Theme.ACCENT_GOLD
    CombatEffects.flash_effect(widget, color, duration)
