"""
修炼处理器类

处理与修炼相关的命令，包括修炼、突破和查看状态。
"""

from .base_handler import BaseHandler
from utils.colors import Color, dim, colorize
from interface.ui import UIPanel, UIProgress, UIInfoCard, UITheme


class CultivationHandler(BaseHandler):
    """
    修炼处理器类
    
    处理修炼相关的命令：
    - /修炼 - 闭关修炼，增加修为
    - /突破 - 尝试突破当前境界
    - /状态 - 查看自身状态
    """
    
    def handle_cultivation(self):
        """处理修炼命令"""
        if not self.cultivation_system:
            error_panel = UIPanel.error_panel("错误", "修炼系统未初始化")
            print(error_panel.render())
            return
        
        result = self.cultivation_system.practice(times=1)
        
        if result["success"]:
            # 使用新的UIPanel组件
            panel = UIPanel.info_panel("☯️ 修炼", width=60, border_color=UITheme.BORDER_PRIMARY)
            panel.add_line(result['message'])
            
            if result.get("messages"):
                panel.add_empty_line()
                for msg in result["messages"]:
                    panel.add_line(f"  • {msg}")
            
            print(panel.render())
            
            # 检查随机事件
            self._check_random_event()
        else:
            warning_panel = UIPanel(
                title="⚠️ 提示",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            warning_panel.add_line(result['message'])
            print(warning_panel.render())
    
    def handle_breakthrough(self):
        """处理突破命令"""
        if not self.cultivation_system:
            error_panel = UIPanel.error_panel("错误", "突破系统未初始化")
            print(error_panel.render())
            return
        
        # 先显示突破信息
        info = self.cultivation_system.get_breakthrough_info()
        
        # 使用新的UIPanel组件
        panel = UIPanel.info_panel("🎯 突破信息", width=60, border_color=UITheme.BORDER_ACCENT)
        panel.add_line(info["message"])
        print(panel.render())
        
        if info["can_breakthrough"]:
            # 显示突破进度
            progress_panel = UIPanel(
                title="⚡ 正在尝试突破...",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            print(progress_panel.render())
            
            result = self.cultivation_system.attempt_breakthrough()
            
            # 显示突破结果
            result_panel = UIPanel.info_panel("突破结果", width=60)
            result_panel.add_line(result["message"])
            print(result_panel.render())
            
            # 突破成功后自动保存
            if result.get("result") and result["result"].name == "SUCCESS":
                if self.save_player():
                    success_panel = UIPanel.success_panel("保存成功", "突破进度已自动保存")
                    print(success_panel.render())
                else:
                    warning_panel = UIPanel(
                        title="⚠️ 提示",
                        width=60,
                        border_style='rounded',
                        border_color=UITheme.WARNING,
                        title_color=UITheme.WARNING
                    )
                    warning_panel.add_line("自动保存失败，请手动保存")
                    print(warning_panel.render())
            
            # 检查是否死亡
            if self.player and self.player.stats.is_dead:
                death_panel = UIPanel(
                    title="💀 道友已陨落...",
                    width=60,
                    border_style='double',
                    border_color=UITheme.ERROR,
                    title_color=UITheme.ERROR
                )
                print(death_panel.render())
                
                # 转世重生
                if result.get("death_info"):
                    input(f"\n{colorize('按回车键转世重生...', Color.BOLD_YELLOW)}")
                    self.player.reincarnate(result["death_info"]["inheritance"])
                    
                    reincarnate_panel = UIPanel.success_panel("✨ 转世成功！", "")
                    print(reincarnate_panel.render())
                    print(self.player.get_status_text())
                    # 转世后也保存
                    self.save_player()
    
    def handle_status(self):
        """处理状态命令"""
        if not self.player:
            error_panel = UIPanel.error_panel("错误", "玩家未初始化")
            print(error_panel.render())
            return
        
        # 获取突破所需经验
        exp_needed = self.player.get_exp_needed()
        
        # 使用UIInfoCard显示玩家状态
        player_data = {
            'name': self.player.stats.name,
            'realm': self.player.get_realm_name(),
            'age': self.player.stats.age,
            'lifespan': self.player.stats.lifespan,
            'exp': self.player.stats.exp,
            'max_exp': exp_needed,
            'cultivation_speed': f"{self.player.get_cultivation_speed():.1f}倍",
            'attack': self.player.stats.attack,
            'defense': self.player.stats.defense,
            'speed': self.player.stats.speed,
            'spirit_stones': self.player.stats.spirit_stones,
            'fortune': self.player.stats.fortune,
            'karma': self.player.stats.karma,
        }
        
        card = UIInfoCard.player_status_card(player_data, width=60)
        print(card.render())
        
        # 显示修为进度条
        exp_bar = UIProgress.cultivation_bar(
            current_exp=self.player.stats.exp,
            max_exp=exp_needed,
            realm_name=self.player.get_realm_name(),
            width=40
        )
        print(f"\n{exp_bar.render()}")
        
        # 显示灵根信息
        spirit_panel = UIPanel.info_panel("🌟 灵根资质", width=60, border_color=UITheme.BORDER_ACCENT)
        spirit_root_name = self.player.get_spirit_root_name()
        spirit_root_desc = self.player.get_spirit_root_description()
        spirit_panel.add_line(f"{colorize(spirit_root_name, UITheme.TITLE_SECONDARY)}")
        spirit_panel.add_line(dim(spirit_root_desc))
        print(spirit_panel.render())
    
    def _check_random_event(self):
        """检查随机事件"""
        if not self.cli.event_system or not self.player:
            return
        
        player_stats = {
            "realm_level": self.player.stats.realm_level,
            "fortune": self.player.stats.fortune,
            "karma": self.player.stats.karma,
            "location": self.player.stats.location,
            "spirit_stones": self.player.stats.spirit_stones,
        }
        
        event = self.cli.event_system.check_random_event(player_stats)
        if event:
            # 使用新的UIPanel组件显示事件
            panel = UIPanel(
                title="⚡ 突发事件",
                width=60,
                border_style='rounded',
                border_color=UITheme.WARNING,
                title_color=UITheme.WARNING
            )
            panel.add_line(colorize(f"【{event.name}】", UITheme.TITLE_SECONDARY))
            panel.add_empty_line()
            panel.add_line(event.description)
            
            if event.choices:
                panel.add_empty_line()
                panel.add_line(colorize("选择:", UITheme.TITLE_SECONDARY))
                for i, choice in enumerate(event.choices):
                    panel.add_line(f"  {i+1}. {choice['text']}")
                # 简化处理，自动选择第一个
                effects = self.cli.event_system.apply_event_effects(event, 0)
                panel.add_empty_line()
                panel.add_line(colorize(f"结果: 你选择了{event.choices[0]['text']}", UITheme.SUCCESS))
            
            print(panel.render())
            
            self.cli.event_system.record_event(event.id)
