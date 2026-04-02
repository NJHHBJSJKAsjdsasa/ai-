"""
日志面板组件 - 重构版
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from .theme import Theme


class LogPanel(tk.Frame):
    """日志显示面板 - 重构版"""

    LOG_TYPES = {
        "system": ("☯ 系统", Theme.ACCENT_BLUE),
        "combat": ("⚔️ 战斗", Theme.ACCENT_RED),
        "npc": ("👤 NPC", Theme.ACCENT_GOLD),
        "cultivation": ("🧘 修炼", Theme.ACCENT_GREEN),
        "exploration": ("🔍 探索", Theme.ACCENT_PURPLE),
        "item": ("📦 物品", Theme.ACCENT_ORANGE),
        "social": ("💕 社交", Theme.ACCENT_PINK),
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=Theme.BG_SECONDARY)
        self.filters = {log_type: True for log_type in self.LOG_TYPES.keys()}
        self.auto_scroll = True
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 顶部工具栏
        toolbar_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        toolbar_frame.pack(fill=tk.X, padx=Theme.SPACING_MD, pady=Theme.SPACING_SM)

        # 标题
        title_label = tk.Label(
            toolbar_frame,
            text="📜 日志",
            font=Theme.get_font(Theme.FONT_SIZE_MD, bold=True),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY
        )
        title_label.pack(side=tk.LEFT)

        # 过滤按钮
        filter_frame = tk.Frame(toolbar_frame, bg=Theme.BG_SECONDARY)
        filter_frame.pack(side=tk.LEFT, padx=(Theme.SPACING_LG, 0))

        self.filter_vars = {}
        for log_type, (name, color) in self.LOG_TYPES.items():
            var = tk.BooleanVar(value=True)
            self.filter_vars[log_type] = var

            # 创建过滤按钮样式
            cb = tk.Checkbutton(
                filter_frame,
                text=name,
                variable=var,
                command=self._apply_filter,
                bg=Theme.BG_SECONDARY,
                fg=color,
                selectcolor=Theme.BG_PRIMARY,
                activebackground=Theme.BG_SECONDARY,
                activeforeground=color,
                font=Theme.get_font(Theme.FONT_SIZE_SM),
                cursor="hand2"
            )
            cb.pack(side=tk.LEFT, padx=Theme.SPACING_XS)

        # 右侧操作按钮
        btn_frame = tk.Frame(toolbar_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(side=tk.RIGHT)

        # 自动滚动开关
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_cb = tk.Checkbutton(
            btn_frame,
            text="自动滚动",
            variable=self.auto_scroll_var,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            selectcolor=Theme.BG_PRIMARY,
            activebackground=Theme.BG_SECONDARY,
            activeforeground=Theme.TEXT_PRIMARY,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            cursor="hand2"
        )
        auto_scroll_cb.pack(side=tk.LEFT, padx=Theme.SPACING_XS)

        # 清空按钮
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ 清空",
            command=self.clear,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_SECONDARY,
            activebackground=Theme.ACCENT_RED,
            activeforeground=Theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=Theme.SPACING_SM,
            pady=Theme.SPACING_XS,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=Theme.SPACING_XS)

        # 日志文本区域
        text_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=Theme.SPACING_MD, pady=Theme.SPACING_SM)

        self.log_text = tk.Text(
            text_frame,
            height=6,
            state=tk.DISABLED,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(Theme.FONT_SIZE_SM),
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=Theme.BORDER_DEFAULT,
            wrap=tk.WORD,
            padx=Theme.SPACING_SM,
            pady=Theme.SPACING_SM
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 自定义滚动条
        scrollbar = tk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.log_text.yview,
            bg=Theme.BG_TERTIARY,
            troughcolor=Theme.BG_SECONDARY,
            activebackground=Theme.BG_ELEVATED,
            width=12
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # 配置标签样式
        self._setup_tags()

    def _setup_tags(self):
        """配置文本标签样式"""
        # 日志类型标签
        for log_type, (name, color) in self.LOG_TYPES.items():
            self.log_text.tag_config(
                f"type_{log_type}",
                foreground=color,
                font=Theme.get_font(Theme.FONT_SIZE_SM, bold=True)
            )

        # 时间戳标签
        self.log_text.tag_config(
            "timestamp",
            foreground=Theme.TEXT_DIM,
            font=Theme.get_mono_font(Theme.FONT_SIZE_XS)
        )

        # 消息内容标签
        self.log_text.tag_config(
            "message",
            foreground=Theme.TEXT_PRIMARY,
            font=Theme.get_font(Theme.FONT_SIZE_SM)
        )

        # 高亮标签（用于重要日志）
        self.log_text.tag_config(
            "highlight",
            background=Theme.BG_ELEVATED,
            foreground=Theme.ACCENT_GOLD
        )

    def _apply_filter(self):
        """应用日志过滤"""
        for log_type, var in self.filter_vars.items():
            self.filters[log_type] = var.get()

        # 重新显示日志
        self._refresh_display()

    def _refresh_display(self):
        """刷新日志显示（根据过滤器）"""
        # 保存当前内容
        current_content = self.log_text.get(1.0, tk.END)

        # 清空并重新显示
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)

        # 解析并过滤日志条目
        lines = current_content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue

            # 检查是否应该显示
            should_show = False
            for log_type, (name, color) in self.LOG_TYPES.items():
                if name in line and self.filters.get(log_type, True):
                    should_show = True
                    break

            if should_show or not any(name in line for name in [n for n, _ in self.LOG_TYPES.values()]):
                self.log_text.insert(tk.END, line + '\n')

        self.log_text.config(state=tk.DISABLED)

    def log(self, message, log_type="system"):
        """添加日志"""
        if not self.filters.get(log_type, True):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        type_name, type_color = self.LOG_TYPES.get(log_type, ("☯ 未知", Theme.TEXT_SECONDARY))

        self.log_text.config(state=tk.NORMAL)

        # 时间戳
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")

        # 日志类型
        self.log_text.insert(tk.END, f"{type_name} ", f"type_{log_type}")

        # 消息内容
        self.log_text.insert(tk.END, f"{message}\n", "message")

        # 自动滚动
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)

        self.log_text.config(state=tk.DISABLED)

    def clear(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def log_system(self, message):
        """记录系统日志"""
        self.log(message, "system")

    def log_combat(self, message):
        """记录战斗日志"""
        self.log(message, "combat")

    def log_npc(self, message):
        """记录NPC日志"""
        self.log(message, "npc")

    def log_cultivation(self, message):
        """记录修炼日志"""
        self.log(message, "cultivation")

    def log_exploration(self, message):
        """记录探索日志"""
        self.log(message, "exploration")

    def log_item(self, message):
        """记录物品日志"""
        self.log(message, "item")

    def log_social(self, message):
        """记录社交日志"""
        self.log(message, "social")
