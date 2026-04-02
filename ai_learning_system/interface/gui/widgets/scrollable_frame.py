"""
可滚动框架组件
"""

import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """可滚动框架"""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # 创建画布
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置画布滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # 在画布上创建窗口
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 配置画布和滚动条
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定事件
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

    def _on_canvas_configure(self, event):
        """画布大小改变时调整内部框架宽度"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mousewheel(self, event):
        """绑定鼠标滚轮"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """解绑鼠标滚轮"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_to_top(self):
        """滚动到顶部"""
        self.canvas.yview_moveto(0)

    def scroll_to_bottom(self):
        """滚动到底部"""
        self.canvas.yview_moveto(1)
