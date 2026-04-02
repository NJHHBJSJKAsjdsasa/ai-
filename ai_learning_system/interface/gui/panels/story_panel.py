"""
剧情面板
显示剧情对话、选择和回放功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

from .base_panel import BasePanel
from ..theme import Theme

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from game.story_system import StoryManager, StoryEffectApplier


class StoryPanel(BasePanel):
    """剧情面板"""

    def __init__(self, parent, main_window, **kwargs):
        self.story_manager: Optional[StoryManager] = None
        self.current_dialogue: Optional[Dict[str, Any]] = None
        super().__init__(parent, main_window, **kwargs)

    def _setup_ui(self):
        """设置界面"""
        # 主分割面板
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=Theme.BG_SECONDARY)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 左侧：剧情列表
        self._setup_story_list()

        # 右侧：剧情播放区
        self._setup_story_player()

        # 初始化剧情管理器
        self._init_story_manager()

    def _setup_story_list(self):
        """设置剧情列表"""
        left_frame = tk.Frame(self.paned, bg=Theme.BG_SECONDARY, width=300)
        self.paned.add(left_frame, minsize=250)

        # 标题
        title_label = tk.Label(
            left_frame,
            text="📖 剧情列表",
            **Theme.get_label_style("title")
        )
        title_label.pack(pady=10)

        # 分类标签
        self.tab_frame = tk.Frame(left_frame, bg=Theme.BG_SECONDARY)
        self.tab_frame.pack(fill=tk.X, padx=10, pady=5)

        self.tab_var = tk.StringVar(value="available")

        tk.Radiobutton(
            self.tab_frame,
            text="可用",
            variable=self.tab_var,
            value="available",
            command=self._on_tab_changed,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            selectcolor=Theme.BG_TERTIARY,
            activebackground=Theme.ACCENT_CYAN,
            activeforeground=Theme.BG_PRIMARY
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            self.tab_frame,
            text="已完成",
            variable=self.tab_var,
            value="completed",
            command=self._on_tab_changed,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            selectcolor=Theme.BG_TERTIARY,
            activebackground=Theme.ACCENT_CYAN,
            activeforeground=Theme.BG_PRIMARY
        ).pack(side=tk.LEFT, padx=5)

        # 剧情列表
        list_frame = tk.Frame(left_frame, bg=Theme.BG_SECONDARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame, bg=Theme.BG_TERTIARY)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.story_listbox = tk.Listbox(
            list_frame,
            **Theme.get_listbox_style(),
            yscrollcommand=scrollbar.set,
            height=20
        )
        self.story_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.story_listbox.yview)

        self.story_listbox.bind('<<ListboxSelect>>', self._on_story_selected)

        # 操作按钮
        btn_frame = tk.Frame(left_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="开始剧情",
            command=self._on_start_story,
            **Theme.get_button_style("primary")
        )
        self.start_btn.pack(fill=tk.X, pady=2)

        self.replay_btn = tk.Button(
            btn_frame,
            text="回放剧情",
            command=self._on_replay_story,
            state=tk.DISABLED,
            **Theme.get_button_style("secondary")
        )
        self.replay_btn.pack(fill=tk.X, pady=2)

        self.refresh_btn = tk.Button(
            btn_frame,
            text="刷新列表",
            command=self.refresh,
            **Theme.get_button_style("secondary")
        )
        self.refresh_btn.pack(fill=tk.X, pady=2)

    def _setup_story_player(self):
        """设置剧情播放区"""
        right_frame = tk.Frame(self.paned, bg=Theme.BG_SECONDARY)
        self.paned.add(right_frame, minsize=500)

        # 剧情标题
        self.story_title_label = tk.Label(
            right_frame,
            text="请选择或开始一个剧情",
            **Theme.get_label_style("title")
        )
        self.story_title_label.pack(pady=10)

        # 场景背景
        self.scene_bg_label = tk.Label(
            right_frame,
            text="",
            **Theme.get_label_style("dim")
        )
        self.scene_bg_label.pack(pady=5)

        # 对话显示区
        dialogue_frame = tk.Frame(right_frame, bg=Theme.BG_TERTIARY, padx=20, pady=20)
        dialogue_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 说话者名称
        self.speaker_label = tk.Label(
            dialogue_frame,
            text="",
            **Theme.get_label_style("subtitle")
        )
        self.speaker_label.pack(anchor=tk.W, pady=(0, 10))

        # 对话内容
        text_style = Theme.get_text_style()
        text_style.pop('wrap', None)  # 移除wrap避免重复
        self.dialogue_text = tk.Text(
            dialogue_frame,
            **text_style,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.dialogue_text.pack(fill=tk.BOTH, expand=True)

        # 下一句按钮
        self.next_btn = tk.Button(
            dialogue_frame,
            text="▶ 继续",
            command=self._on_next_dialogue,
            state=tk.DISABLED,
            **Theme.get_button_style("primary")
        )
        self.next_btn.pack(anchor=tk.E, pady=10)

        # 选择区
        self.choices_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        self.choices_frame.pack(fill=tk.X, padx=20, pady=10)

        self.choices_label = tk.Label(
            self.choices_frame,
            text="",
            **Theme.get_label_style("subtitle")
        )
        self.choices_label.pack(anchor=tk.W, pady=5)

        self.choice_buttons = []

        # 剧情信息区
        info_frame = tk.Frame(right_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        self.info_label = tk.Label(
            info_frame,
            text="",
            **Theme.get_label_style("dim")
        )
        self.info_label.pack(anchor=tk.W)

        # 奖励区
        self.rewards_frame = tk.LabelFrame(
            right_frame,
            text="剧情奖励",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.get_font(10, bold=True)
        )
        self.rewards_frame.pack(fill=tk.X, padx=20, pady=10)

        self.rewards_label = tk.Label(
            self.rewards_frame,
            text="暂无奖励",
            **Theme.get_label_style("normal")
        )
        self.rewards_label.pack(pady=10)

    def _init_story_manager(self):
        """初始化剧情管理器"""
        player = self.get_player()
        if player:
            player_id = getattr(player, 'id', player.stats.name)
            self.story_manager = StoryManager(player_id)

    def refresh(self):
        """刷新面板"""
        if not self.story_manager:
            self._init_story_manager()

        self._refresh_story_list()

        # 如果有进行中的剧情，显示当前状态
        if self.story_manager and self.story_manager.active_story:
            self._update_story_display()

    def _refresh_story_list(self):
        """刷新剧情列表"""
        self.story_listbox.delete(0, tk.END)
        self.story_data = []

        player = self.get_player()
        if not player or not self.story_manager:
            return

        realm_level = getattr(player.stats, 'realm_level', 0)
        location = getattr(player.stats, 'location', '新手村')

        tab = self.tab_var.get()

        if tab == "available":
            # 获取可用剧情
            stories = self.story_manager.get_available_stories(realm_level, location)
            for story in stories:
                story_type = "【主】" if story['story_type'] == 'main' else "【支】"
                self.story_listbox.insert(tk.END, f"{story_type} {story['title']}")
                self.story_data.append(story)
        else:
            # 获取已完成剧情
            stories = self.story_manager.get_completed_stories()
            for story in stories:
                story_type = "【主】" if story['story_type'] == 'main' else "【支】"
                replay_text = f" (已回放{story['replay_count']}次)" if story['replay_count'] > 0 else ""
                self.story_listbox.insert(tk.END, f"{story_type} {story['title']}{replay_text}")
                self.story_data.append(story)

    def _on_tab_changed(self):
        """标签切换事件"""
        self._refresh_story_list()

        # 更新按钮状态
        tab = self.tab_var.get()
        if tab == "available":
            self.start_btn.config(state=tk.NORMAL)
            self.replay_btn.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.DISABLED)
            self.replay_btn.config(state=tk.NORMAL)

    def _on_story_selected(self, event):
        """剧情选择事件"""
        selection = self.story_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self.story_data):
            story = self.story_data[index]
            self._show_story_info(story)

    def _show_story_info(self, story: Dict[str, Any]):
        """显示剧情信息"""
        self.story_title_label.config(text=story['title'])
        self.scene_bg_label.config(text=story.get('description', ''))

        # 显示奖励信息
        rewards = self.story_manager.get_story_rewards() if self.story_manager else []
        if rewards:
            reward_text = "\n".join([
                f"• {r['reward_item']} x{r['quantity']} {'(已领取)' if r.get('claimed') else ''}"
                for r in rewards
            ])
            self.rewards_label.config(text=reward_text)
        else:
            self.rewards_label.config(text="完成剧情可获得奖励")

    def _on_start_story(self):
        """开始剧情"""
        selection = self.story_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个剧情")
            return

        index = selection[0]
        story = self.story_data[index]

        success, msg = self.story_manager.start_story(story['id'])
        if success:
            self.log(f"开始剧情: {story['title']}", "story")
            self._update_story_display()
        else:
            messagebox.showerror("错误", msg)

    def _on_replay_story(self):
        """回放剧情"""
        selection = self.story_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个剧情")
            return

        index = selection[0]
        story = self.story_data[index]

        if not self.story_manager.can_replay(story['id']):
            messagebox.showinfo("提示", "该剧情不可回放")
            return

        success, msg = self.story_manager.replay_story(story['id'])
        if success:
            self.log(f"回放剧情: {story['title']}", "story")
            self._update_story_display()
        else:
            messagebox.showerror("错误", msg)

    def _update_story_display(self):
        """更新剧情显示"""
        if not self.story_manager or not self.story_manager.active_story:
            return

        story = self.story_manager.active_story
        self.story_title_label.config(text=story.title)

        # 显示当前场景
        if self.story_manager.current_scene:
            scene = self.story_manager.current_scene
            self.scene_bg_label.config(text=f"场景: {scene.title}")

        # 显示当前对话
        self._show_current_dialogue()

    def _show_current_dialogue(self):
        """显示当前对话"""
        dialogue = self.story_manager.get_current_dialogue()

        if dialogue:
            self.current_dialogue = dialogue

            # 更新说话者
            speaker_text = dialogue['speaker_name']
            if dialogue['speaker_type'] == 'npc':
                speaker_text = f"【{speaker_text}】"
            elif dialogue['speaker_type'] == 'player':
                speaker_text = f"<{speaker_text}>"
            self.speaker_label.config(text=speaker_text)

            # 更新对话内容
            self.dialogue_text.config(state=tk.NORMAL)
            self.dialogue_text.delete(1.0, tk.END)
            self.dialogue_text.insert(tk.END, dialogue['content'])
            self.dialogue_text.config(state=tk.DISABLED)

            # 启用继续按钮
            self.next_btn.config(state=tk.NORMAL)

            # 隐藏选择区
            self._clear_choices()
        else:
            # 对话结束，显示选择
            self._show_choices()

    def _on_next_dialogue(self):
        """下一段对话"""
        if not self.story_manager:
            return

        has_next, dialogue = self.story_manager.advance_dialogue()

        if has_next:
            self._show_current_dialogue()
        else:
            # 显示选择
            self._show_choices()

    def _show_choices(self):
        """显示选择选项"""
        # 禁用继续按钮
        self.next_btn.config(state=tk.DISABLED)

        # 清空对话显示
        self.speaker_label.config(text="")
        self.dialogue_text.config(state=tk.NORMAL)
        self.dialogue_text.delete(1.0, tk.END)
        self.dialogue_text.insert(tk.END, "（剧情发展到了关键时刻，你需要做出选择...）")
        self.dialogue_text.config(state=tk.DISABLED)

        # 获取选择
        choices = self.story_manager.get_current_choices()

        # 清除旧的选择按钮
        self._clear_choices()

        if choices:
            self.choices_label.config(text="请选择你的行动:")

            for choice in choices:
                btn = tk.Button(
                    self.choices_frame,
                    text=choice['text'],
                    command=lambda c=choice: self._on_make_choice(c),
                    wraplength=400,
                    **Theme.get_button_style("secondary")
                )
                btn.pack(fill=tk.X, pady=3)
                self.choice_buttons.append(btn)
        else:
            # 没有选择了，剧情结束
            self.choices_label.config(text="剧情已结束")
            self._show_completion_message()

    def _clear_choices(self):
        """清除选择按钮"""
        for btn in self.choice_buttons:
            btn.destroy()
        self.choice_buttons.clear()
        self.choices_label.config(text="")

    def _on_make_choice(self, choice: Dict[str, Any]):
        """做出选择"""
        success, msg, effects = self.story_manager.make_choice(choice['id'])

        if success:
            # 记录效果
            for effect in effects:
                effect_desc = self._format_effect(effect)
                if effect_desc:
                    self.log(effect_desc, "system")

            self.log(msg, "story")

            if msg == "剧情完成":
                self._show_completion_message()
            else:
                self._update_story_display()

            # 刷新玩家状态
            if self.main_window:
                self.main_window.refresh_all_panels()

    def _format_effect(self, effect) -> str:
        """格式化效果描述"""
        effect_type = effect.effect_type
        value = effect.value
        target = effect.target

        if effect_type == 'exp':
            return f"获得 {value} 经验值"
        elif effect_type == 'spirit_stones':
            return f"{'获得' if int(value) > 0 else '失去'} {abs(int(value))} 灵石"
        elif effect_type == 'health':
            return f"{'恢复' if int(value) > 0 else '损失'} {abs(int(value))} 生命值"
        elif effect_type == 'karma':
            return f"业力 {'增加' if int(value) > 0 else '减少'} {abs(int(value))}"
        elif effect_type == 'npc_favor':
            return f"{target} 好感度 {'增加' if int(value) > 0 else '减少'} {abs(int(value))}"
        elif effect_type == 'item':
            return f"获得物品: {value}"
        elif effect_type == 'technique':
            return f"习得功法: {value}"
        elif effect_type == 'reputation':
            return f"获得声望: {value}"
        return ""

    def _show_completion_message(self):
        """显示完成信息"""
        self._clear_choices()

        self.choices_label.config(text="🎉 剧情已完成！")

        # 显示奖励
        rewards = self.story_manager.get_story_rewards()
        if rewards:
            reward_text = "获得奖励:\n"
            for reward in rewards:
                if not reward.get('claimed'):
                    reward_text += f"• {reward['reward_item']} x{reward['quantity']}\n"
            self.rewards_label.config(text=reward_text)

            # 领取奖励按钮
            claim_btn = tk.Button(
                self.choices_frame,
                text="领取奖励",
                command=self._on_claim_rewards,
                **Theme.get_button_style("primary")
            )
            claim_btn.pack(pady=5)
            self.choice_buttons.append(claim_btn)

        # 返回按钮
        back_btn = tk.Button(
            self.choices_frame,
            text="返回剧情列表",
            command=self._on_return_to_list,
            **Theme.get_button_style("secondary")
        )
        back_btn.pack(pady=5)
        self.choice_buttons.append(back_btn)

    def _on_claim_rewards(self):
        """领取奖励"""
        rewards = self.story_manager.get_story_rewards()
        claimed_count = 0

        for reward in rewards:
            if not reward.get('claimed'):
                success, _ = self.story_manager.claim_reward(reward['id'])
                if success:
                    claimed_count += 1

        if claimed_count > 0:
            messagebox.showinfo("成功", f"成功领取 {claimed_count} 项奖励！")
            self.rewards_label.config(text="所有奖励已领取")
            self._clear_choices()
            self._on_return_to_list()

            # 刷新玩家状态
            if self.main_window:
                self.main_window.refresh_all_panels()

    def _on_return_to_list(self):
        """返回剧情列表"""
        self.story_manager.active_story = None
        self.story_manager.current_state = None
        self.story_manager.current_scene = None

        # 重置显示
        self.story_title_label.config(text="请选择或开始一个剧情")
        self.scene_bg_label.config(text="")
        self.speaker_label.config(text="")
        self.dialogue_text.config(state=tk.NORMAL)
        self.dialogue_text.delete(1.0, tk.END)
        self.dialogue_text.config(state=tk.DISABLED)
        self._clear_choices()
        self.next_btn.config(state=tk.DISABLED)

        # 刷新列表
        self.refresh()

    def on_show(self):
        """当面板显示时调用"""
        self.refresh()
