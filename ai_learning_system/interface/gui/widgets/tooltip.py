"""
工具提示组件
"""

import tkinter as tk


class ToolTip:
    """工具提示类"""

    def __init__(self, widget, text, delay=500):
        """
        初始化工具提示

        Args:
            widget: 要添加提示的组件
            text: 提示文本
            delay: 显示延迟（毫秒）
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.id = None

        # 绑定事件
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)

    def _on_enter(self, event=None):
        """鼠标进入时"""
        self._schedule()

    def _on_leave(self, event=None):
        """鼠标离开时"""
        self._unschedule()
        self._hide()

    def _schedule(self):
        """计划显示提示"""
        self.id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        """取消计划"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def _show(self):
        """显示提示"""
        if self.tooltip:
            return

        # 获取组件位置
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        # 创建提示窗口
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # 创建提示标签
        label = tk.Label(
            self.tooltip,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("微软雅黑", 9),
            padx=5,
            pady=3
        )
        label.pack()

    def _hide(self):
        """隐藏提示"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def update_text(self, text):
        """更新提示文本"""
        self.text = text
