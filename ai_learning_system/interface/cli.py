import os
import sys
import time
import threading
from typing import Optional

# 导入颜色工具
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.colors import (
    Color, colorize, success, warning, error, info,
    green, yellow, blue, cyan, magenta, bold, dim, Spinner
)
from utils.logger import Logger, LogLevel

# 导入UI组件
from interface.ui import (
    UIPanel, UITable, UIProgress, UIInfoCard,
    UIFormatter, UITheme
)

# 导入命令处理器
from interface.handlers import (
    CultivationHandler,
    NPCHandler,
    InventoryHandler,
    MapHandler,
    TechniqueHandler,
    ExplorationHandler,
    CharacterHandler,
    AdminHandler,
    CombatHandler,
)

# 导入热更新管理器
try:
    from core.hot_reload_manager import init_hot_reload, get_hot_reload_manager
    from core.module_reloader import get_module_reloader
    HOT_RELOAD_AVAILABLE = True
except ImportError:
    HOT_RELOAD_AVAILABLE = False

# 导入游戏系统
try:
    from game import Player, CultivationSystem, NPCManager, World, EventSystem, judge_ai_reply, filter_ai_response
    from config import get_realm_icon, get_realm_info
    GAME_AVAILABLE = True
except ImportError:
    GAME_AVAILABLE = False


class CLI:
    def __init__(self, memory_manager, dialogue_engine=None, game_mode: bool = True):
        self.memory_manager = memory_manager
        self.dialogue_engine = dialogue_engine
        self.running = False
        self.logger = Logger(
            name="cli",
            console_level=LogLevel.INFO,
            enable_file=True
        )
        
        # 游戏模式
        self.game_mode = game_mode and GAME_AVAILABLE
        self.player = None
        self.cultivation_system = None
        self.npc_manager = None
        self.world = None
        self.event_system = None
        self.combat_handler = None
        
        # 状态管理（用于多步骤命令）
        self._state = {}

        if self.game_mode:
            self._init_game()

        # 初始化命令处理器
        self.cultivation_handler = CultivationHandler(self)
        self.npc_handler = NPCHandler(self)
        self.inventory_handler = InventoryHandler(self)
        self.map_handler = MapHandler(self)
        self.technique_handler = TechniqueHandler(self)
        self.exploration_handler = ExplorationHandler(self)
        self.character_handler = CharacterHandler(self)
        self.admin_handler = AdminHandler(self)
        self.combat_handler = CombatHandler(self)
        
        # 初始化热更新管理器
        self.hot_reload_manager = None
        self.module_reloader = None
        if HOT_RELOAD_AVAILABLE:
            self._init_hot_reload()
        
        # 设置输入历史记录
        self._setup_readline()
    
    def _init_hot_reload(self):
        """初始化热更新系统"""
        try:
            self.hot_reload_manager = init_hot_reload()
            self.module_reloader = get_module_reloader()
            self.logger.info("热更新系统已初始化")
        except Exception as e:
            self.logger.warning(f"热更新系统初始化失败: {e}")
            self.hot_reload_manager = None
            self.module_reloader = None
    
    def _init_game(self):
        """初始化游戏系统"""
        # 检查是否有已保存的角色
        from storage.database import Database
        db = Database()
        players = db.list_players()
        db.close()
        
        if players:
            # 显示已有角色列表
            print(f"\n{colorize('📋', Color.BOLD_CYAN)} 发现已有角色：")
            for i, p in enumerate(players, 1):
                print(f"  {i}. {p['name']}")
            print(f"\n{colorize('💡', Color.BOLD_YELLOW)} 提示：使用 /加载 <角色名> 加载角色")
            print(f"{colorize('💡', Color.BOLD_YELLOW)} 提示：使用 /新建角色 创建新角色")
            
            # 默认加载最新的角色
            self.player = self._load_player()
            if self.player:
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 自动加载角色：{self.player.stats.name}")
                print(f"  当前境界: {self.player.get_realm_name()}")
                print(f"  当前年龄: {self.player.stats.age}岁")
        else:
            # 创建新玩家
            self.player = Player(name="道友", load_from_db=False)
            print(f"\n{colorize('🎮', Color.BOLD_CYAN)} 创建新角色！")
        
        # 创建修炼系统
        self.cultivation_system = CultivationSystem(self.player)
        
        # 创建世界（传入数据库实例以支持动态地点）
        # World类内部会创建NPC管理器
        from storage.database import Database
        self.world = World(db=Database())
        
        # 使用World的NPC管理器，确保数据一致性
        self.npc_manager = self.world.npc_manager
        
        # 创建事件系统
        self.event_system = EventSystem()
        
        # 创建探索管理器（用于无限生成系统）
        from game.exploration_manager import ExplorationManager
        self.exploration_manager = ExplorationManager(self.world, use_llm=False)
        
        print(f"{colorize('✨', Color.BOLD_GREEN)} 无限生成系统已启动！")
    
    def _load_player(self) -> Optional[Player]:
        """
        从数据库加载玩家数据
        
        Returns:
            加载的玩家对象，如果没有存档则返回None
        """
        try:
            # 从数据库加载
            from storage.database import Database
            db = Database()
            data = db.load_player()
            db.close()
            
            if not data:
                return None
            
            # 调试信息
            self.logger.debug(f"加载玩家数据: {data.keys() if isinstance(data, dict) else '非字典类型'}")
            if isinstance(data, dict) and 'stats' in data:
                stats = data['stats']
                self.logger.debug(f"玩家状态: 境界={stats.get('realm_level')}, 层数={stats.get('realm_layer')}, 位置={stats.get('location')}")
            
            # 创建玩家对象并从数据加载
            player = Player(name="道友", load_from_db=False)
            player.from_dict(data)
            
            # 验证加载后的数据
            self.logger.info(f"成功加载玩家存档: {player.stats.name}, 境界={player.get_realm_name()}, 位置={player.stats.location}")
            return player
            
        except Exception as e:
            self.logger.error(f"加载玩家存档失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_player(self) -> bool:
        """
        保存玩家数据到数据库
        
        Returns:
            是否保存成功
        """
        if not self.player:
            return False
        
        try:
            from storage.database import Database
            db = Database()
            
            # 获取玩家数据
            data = self.player.to_dict()
            
            # 调试信息
            self.logger.debug(f"保存玩家数据: {data.keys() if isinstance(data, dict) else '非字典类型'}")
            if isinstance(data, dict) and 'stats' in data:
                stats = data['stats']
                self.logger.debug(f"玩家状态: 境界={stats.get('realm_level')}, 层数={stats.get('realm_layer')}, 位置={stats.get('location')}")
            
            # 保存到数据库
            db.save_player(self.player.stats.name, data)
            db.close()
            
            self.logger.info(f"成功保存玩家存档: {self.player.stats.name}, 境界={self.player.get_realm_name()}, 位置={self.player.stats.location}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存玩家存档失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_readline(self):
        """设置输入历史记录支持"""
        try:
            import readline
            
            # 历史记录文件路径
            history_file = os.path.expanduser("~/.ai_learning_history")
            
            # 尝试加载历史记录
            try:
                readline.read_history_file(history_file)
            except FileNotFoundError:
                pass
            
            # 设置历史记录长度
            readline.set_history_length(1000)
            
            # 程序退出时保存历史记录
            import atexit
            atexit.register(readline.write_history_file, history_file)
            
            self.logger.debug("输入历史记录已启用")
        except ImportError:
            # Windows 可能没有 readline 模块，尝试使用 pyreadline3
            try:
                import pyreadline3 as readline
                history_file = os.path.expanduser("~/.ai_learning_history")
                try:
                    readline.read_history_file(history_file)
                except FileNotFoundError:
                    pass
                readline.set_history_length(1000)
                import atexit
                atexit.register(readline.write_history_file, history_file)
                self.logger.debug("输入历史记录已启用 (pyreadline3)")
            except ImportError:
                self.logger.warning("无法加载 readline 模块，输入历史记录不可用")
    
    def set_state(self, state_name: str, state_data: dict):
        """
        设置状态（用于多步骤命令）
        
        Args:
            state_name: 状态名称
            state_data: 状态数据
        """
        self._state[state_name] = state_data
        self.logger.debug(f"设置状态: {state_name}")
    
    def get_state(self, state_name: str) -> dict:
        """
        获取状态
        
        Args:
            state_name: 状态名称
            
        Returns:
            状态数据，如果不存在则返回空字典
        """
        return self._state.get(state_name, {})
    
    def clear_state(self, state_name: str):
        """
        清除状态
        
        Args:
            state_name: 状态名称
        """
        if state_name in self._state:
            del self._state[state_name]
            self.logger.debug(f"清除状态: {state_name}")
    
    def has_state(self, state_name: str) -> bool:
        """
        检查是否存在指定状态
        
        Args:
            state_name: 状态名称
            
        Returns:
            是否存在该状态
        """
        return state_name in self._state
    
    def start(self):
        self.running = True
        self.display_welcome()
        self.logger.info("CLI 已启动")

        while self.running:
            try:
                # 检查热更新（如果有代码变更）
                if self.hot_reload_manager and self.hot_reload_manager.has_changes():
                    print(f"\n{colorize('🔄', Color.BOLD_YELLOW)} 检测到代码变更，输入 /热更新 重新加载")
                
                # 使用带颜色的提示符
                if self.game_mode and self.player:
                    player_name = self.player.name if hasattr(self.player, 'name') and self.player.name else "无名"
                    realm_name = self.player.get_realm_name() if hasattr(self.player, 'get_realm_name') else "凡人"
                    location = self.player.stats.location if hasattr(self.player, 'stats') and hasattr(self.player.stats, 'location') else "未知"
                    prompt = colorize(f"\n{player_name}<{realm_name}><{location}>", Color.BOLD_CYAN) + colorize("> ", Color.RESET)
                else:
                    prompt = colorize("\n🤖 AI", Color.BOLD_CYAN) + colorize("> ", Color.RESET)
                user_input = input(prompt).strip()

                if not user_input:
                    # 游戏模式下，即使没有输入也更新NPC
                    if self.game_mode and self.world and self.player:
                        self.world.update_npcs(player_location=self.player.stats.location)
                    continue

                # 游戏模式下，更新NPC状态
                if self.game_mode and self.world and self.player:
                    self.world.update_npcs(player_location=self.player.stats.location)

                # 游戏模式下，检查是否为游戏命令（支持中文命令）
                if self.game_mode and self._is_game_command(user_input):
                    self.handle_command(self._convert_to_command(user_input))
                elif user_input.startswith("/"):
                    self.handle_command(user_input)
                else:
                    self.process_message(user_input)

            except KeyboardInterrupt:
                # 忽略 Ctrl+C，提示用户使用 /退出游戏 或 /quit 命令
                print(f"\n{colorize('💡 提示：使用 /退出游戏 或 /quit 命令退出', Color.BOLD_YELLOW)}")
                self.logger.info("用户按下 Ctrl+C，已忽略")
                continue
            except EOFError:
                # 保存玩家数据
                if self.game_mode:
                    self.save_player()
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 游戏进度已保存")
                print(f"\n{colorize('👋 再见！', Color.BOLD_GREEN)}")
                self.logger.info("用户通过 EOF 退出")
                break
            except Exception as e:
                error_msg = f"发生错误: {e}"
                print(f"\n{colorize('❌', Color.BOLD_RED)} {error_msg}")
                self.logger.exception("CLI 运行时错误")

    def display_welcome(self):
        if self.game_mode:
            # 使用新的UIPanel组件
            panel = UIPanel.welcome_panel(
                title="☯️ 修仙世界 - AI驱动文字修仙游戏",
                subtitle="欢迎来到修仙世界！",
                width=62
            )
            print(panel.render())
            
            # 显示玩家初始状态
            if self.player:
                print(self.player.get_status_text())
        else:
            # AI学习系统欢迎面板
            panel = UIPanel(
                title="🤖 AI 学习系统",
                width=62,
                border_style='double',
                border_color=UITheme.BORDER_PRIMARY,
                title_color=UITheme.TITLE_PRIMARY
            )
            panel.add_empty_line()
            panel.add_line("欢迎使用 AI 学习系统！", align='center')
            panel.add_line("这是一个智能对话和记忆管理平台。", align='center')
            panel.add_empty_line()
            panel.add_line("输入 /help 查看可用命令", align='center')
            print(panel.render())

    def display_help(self):
        if self.game_mode:
            # 使用新的UIPanel组件
            panel = UIPanel.help_panel(title="📖 修仙指令大全", width=62)
            
            # 修炼相关
            panel.add_line(colorize("修炼相关:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/修炼')} 或 {green('/xiulian')}  - 闭关修炼，增加修为")
            panel.add_line(f"  {green('/突破')} 或 {green('/tupo')}    - 尝试突破当前境界")
            panel.add_line(f"  {green('/状态')} 或 {green('/status')}  - 查看自身状态")
            panel.add_empty_line()
            
            # 移动探索
            panel.add_line(colorize("移动探索:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/前往')} <地点> 或 {green('/go')} - 前往指定地点")
            panel.add_line(f"  {green('/地图')} 或 {green('/map')}     - 查看世界地图")
            panel.add_line(f"  {green('/秘境')} 或 {green('/secret')}  - 查看秘境/生成地图")
            panel.add_line(f"  {green('/探索')} 或 {green('/explore')} - 探索新区域")
            panel.add_empty_line()
            
            # NPC交互
            panel.add_line(colorize("NPC交互:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/交谈')} <NPC名字>    - 与NPC对话")
            panel.add_line(f"  {green('/npcs')}             - 查看当前地点的NPC")
            panel.add_line(f"  {green('/npc')} <名字>       - 查看NPC详细信息")
            panel.add_line(f"  {green('/npc_goals')} <名字>  - 查看NPC的目标列表")
            panel.add_line(f"  {green('/npc_schedule')} <名字> - 查看NPC的日程安排")
            panel.add_line(f"  {green('/npc_relations')} <名字> - 查看NPC的关系网络")
            panel.add_line(f"  {green('/npc_story')} <名字>  - 查看NPC的人生故事")
            panel.add_line(f"  {green('/npc_personality')} <名字> - 查看NPC的个性")
            panel.add_empty_line()
            
            # 功法系统
            panel.add_line(colorize("功法系统:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/功法')}             - 查看已学功法")
            panel.add_line(f"  {green('/学习')} <功法名>    - 学习功法")
            panel.add_empty_line()
            
            # 道具系统
            panel.add_line(colorize("道具系统:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/背包')}             - 查看背包内容")
            panel.add_line(f"  {green('/使用')} <道具名>    - 使用道具")
            panel.add_empty_line()
            
            # 战斗系统
            panel.add_line(colorize("战斗系统:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/战斗')} <目标>      - 发起战斗")
            panel.add_line(f"  {green('/切磋')} <目标>      - 友好切磋")
            panel.add_line(f"  {green('/逃跑')}             - 尝试逃跑")
            panel.add_empty_line()
            
            # 系统指令
            panel.add_line(colorize("系统指令:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/quit')}, {green('/exit')}     - 退出游戏")
            panel.add_line(f"  {green('/help')}             - 显示此帮助信息")
            panel.add_line(f"  {green('/clear')}            - 清屏")
            panel.add_empty_line()
            
            panel.add_line(colorize("使用说明: 直接输入消息与AI道友交流，使用 / 开头的命令执行操作", UITheme.TEXT_DIM))
            
            print(panel.render())
        else:
            # AI学习系统帮助面板
            panel = UIPanel.help_panel(title="📖 帮助信息", width=62)
            
            panel.add_line(colorize("命令:", UITheme.TITLE_SECONDARY))
            panel.add_line(f"  {green('/quit')}, {green('/exit')}  - 退出程序")
            panel.add_line(f"  {green('/help')}         - 显示此帮助信息")
            panel.add_line(f"  {green('/clear')}        - 清屏")
            panel.add_line(f"  {green('/memories')}     - 查看当前记忆列表")
            panel.add_line(f"  {green('/stats')}        - 查看记忆统计信息")
            panel.add_empty_line()
            
            panel.add_line(colorize("使用说明: 直接输入消息与AI对话，使用 / 开头的命令执行特定操作", UITheme.TEXT_DIM))
            
            print(panel.render())

    def _handle_hot_reload(self):
        """处理热更新命令"""
        if not HOT_RELOAD_AVAILABLE or not self.hot_reload_manager:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 热更新功能未启用")
            return
        
        # 检查是否有变更
        changed_files = self.hot_reload_manager.check_for_changes()
        if not changed_files:
            print(f"\n{colorize('ℹ️', Color.BOLD_CYAN)} 没有检测到代码变更")
            return
        
        print(f"\n{colorize('🔄', Color.BOLD_CYAN)} 检测到 {len(changed_files)} 个文件变更，开始热更新...")
        
        # 执行热更新
        results = self.module_reloader.reload_modules(
            self.hot_reload_manager.get_changed_modules(),
            cli_instance=self
        )
        
        # 显示结果
        success_count = sum(1 for success, _ in results.values() if success)
        failed_count = len(results) - success_count
        
        if success_count > 0:
            print(f"\n{colorize('✅', Color.BOLD_GREEN)} 成功重载 {success_count} 个模块")
        
        if failed_count > 0:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 失败 {failed_count} 个模块:")
            for module_name, (success, error) in results.items():
                if not success:
                    print(f"  - {module_name}: {error}")
        
        # 清除已处理的变更
        self.hot_reload_manager.clear_changes()

    def handle_command(self, command: str):
        cmd = command.lower()
        
        # 游戏模式命令
        if self.game_mode:
            if cmd.startswith("/修炼") or cmd == "/xiulian":
                self.cultivation_handler.handle_cultivation()
                return
            elif cmd.startswith("/突破") or cmd == "/tupo":
                self.cultivation_handler.handle_breakthrough()
                return
            elif cmd.startswith("/状态") or cmd == "/status":
                self.cultivation_handler.handle_status()
                return
            elif cmd.startswith("/前往") or cmd.startswith("/go"):
                args = command[3:].strip() if command.startswith("/前往") else command[3:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要前往的地点")
                    print(f"  用法: /前往 <地点名> 或 /go <地点名>")
                    return
                self.map_handler._handle_move(args)
                return
            elif cmd.startswith("/地图") or cmd == "/map":
                self.map_handler._handle_map()
                return
            elif cmd == "/秘境" or cmd == "/secret" or cmd == "/maps":
                self.map_handler._handle_secret_maps()
                return
            elif cmd.startswith("/位置") or cmd == "/location":
                self.map_handler._handle_location()
                return
            elif cmd.startswith("/交谈") or cmd.startswith("/talk"):
                args = command[3:].strip() if command.startswith("/交谈") else command[5:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要交谈的NPC")
                    print(f"  用法: /交谈 <NPC名> 或 /talk <NPC名>")
                    return
                self.npc_handler.handle_talk(args)
                return
            elif cmd == "/npcs":
                self.npc_handler.handle_npc_list()
                return
            elif cmd.startswith("/npc "):
                args = command[4:].strip()
                self.npc_handler.handle_npc_detail(args)
                return
            elif cmd == "/npc_stats":
                self.npc_handler.handle_npc_stats()
                return
            elif cmd.startswith("/npc_goals"):
                args = command[10:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
                    print(f"  用法: /npc_goals <NPC名字>")
                    return
                self.npc_handler.handle_npc_goals(args)
                return
            elif cmd.startswith("/npc_schedule"):
                args = command[13:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
                    print(f"  用法: /npc_schedule <NPC名字>")
                    return
                self.npc_handler.handle_npc_schedule(args)
                return
            elif cmd.startswith("/npc_relations"):
                args = command[14:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
                    print(f"  用法: /npc_relations <NPC名字>")
                    return
                self.npc_handler.handle_npc_relations(args)
                return
            elif cmd.startswith("/npc_story"):
                args = command[10:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
                    print(f"  用法: /npc_story <NPC名字>")
                    return
                self.npc_handler.handle_npc_story(args)
                return
            elif cmd.startswith("/npc_personality"):
                args = command[16:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
                    print(f"  用法: /npc_personality <NPC名字>")
                    return
                self.npc_handler.handle_npc_personality(args)
                return
            elif cmd.startswith("/功法") or cmd == "/gongfa":
                self.technique_handler.handle_techniques()
                return
            elif cmd.startswith("/学习") or cmd.startswith("/learn"):
                args = command[3:].strip() if command.startswith("/学习") else command[5:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要学习的功法")
                    print(f"  用法: /学习 <功法名> 或 /learn <功法名>")
                    return
                self.technique_handler.handle_learn_technique(args)
                return
            elif cmd.startswith("/可学功法") or cmd == "/available":
                self.technique_handler.handle_available_techniques()
                return
            elif cmd.startswith("/背包") or cmd == "/bag":
                self.inventory_handler.handle_inventory()
                return
            elif cmd.startswith("/使用") or cmd.startswith("/use"):
                args = command[3:].strip() if command.startswith("/使用") else command[4:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要使用的道具")
                    print(f"  用法: /使用 <道具名> 或 /use <道具名>")
                    return
                self.inventory_handler.handle_use_item(args)
                return
            elif cmd.startswith("/装备") or cmd.startswith("/equip"):
                args = command[3:].strip() if command.startswith("/装备") else command[6:].strip()
                if not args:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要装备的法宝")
                    print(f"  用法: /装备 <法宝名> 或 /equip <法宝名>")
                    return
                self.inventory_handler.handle_equip_treasure(args)
                return
            elif cmd.startswith("/门派") or cmd == "/sect":
                self.npc_handler.handle_sects()
                return
            elif cmd.startswith("/探索") or cmd == "/explore":
                self.exploration_handler._handle_explore()
                return
            elif cmd.startswith("/生成") or cmd == "/generate":
                args = command[3:].strip() if command.startswith("/生成") else command[9:].strip()
                self.exploration_handler._handle_generate(args)
                return
            elif cmd.startswith("/妖兽") or cmd == "/monsters":
                self.exploration_handler._handle_monsters()
                return
            elif cmd.startswith("/战斗") or cmd == "/combat":
                args = command[3:].strip() if command.startswith("/战斗") else command[7:].strip()
                self.combat_handler.handle_combat(args)
                return
            elif cmd.startswith("/切磋") or cmd == "/spar":
                args = command[3:].strip() if command.startswith("/切磋") else command[5:].strip()
                self.combat_handler.handle_spar(args)
                return
            elif cmd.startswith("/死斗") or cmd == "/deathmatch":
                args = command[3:].strip() if command.startswith("/死斗") else command[10:].strip()
                self.combat_handler.handle_deathmatch(args)
                return
            elif cmd.startswith("/攻击") or cmd == "/attack":
                self.combat_handler.handle_attack()
                return
            elif cmd.startswith("/技能") or cmd == "/skill":
                args = command[3:].strip() if command.startswith("/技能") else command[6:].strip()
                self.combat_handler.handle_skill(args)
                return
            elif cmd.startswith("/逃跑") or cmd == "/flee":
                self.combat_handler.handle_flee()
                return
            # ========== 处决与饶恕命令 ==========
            # 处决战败的敌人，获得战利品但增加杀戮值
            elif cmd.startswith("/处决") or cmd == "/execute":
                # 提取目标参数：/处决 <目标> 或 /execute <目标>
                args = command[3:].strip() if command.startswith("/处决") else command[8:].strip()
                self.combat_handler.handle_execute(args)
                return
            # 饶恕战败的敌人，获得道德值但无战利品
            elif cmd.startswith("/饶恕") or cmd == "/spare":
                # 提取目标参数：/饶恕 <目标> 或 /spare <目标>
                args = command[3:].strip() if command.startswith("/饶恕") else command[6:].strip()
                self.combat_handler.handle_spare(args)
                return

            # ========== 管理员命令 ==========
            elif cmd.startswith("/admin"):
                args = command[6:].strip()
                self.admin_handler.handle_admin_command(args)
                return
            elif cmd.startswith("/gm"):
                args = command[3:].strip()
                self.admin_handler.handle_gm_command(args)
                return
        
        # 基础命令
        if cmd in ["/quit", "/exit", "/退出游戏"]:
            # 保存玩家数据
            if self.game_mode and self.player:
                if self.save_player():
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 游戏进度已保存")
            print(f"\n{colorize('👋 再见！', Color.BOLD_GREEN)}")
            self.logger.info("用户执行退出命令")
            self.running = False
        
        elif cmd.startswith("/新建角色") or cmd == "/new":
            self.character_handler.handle_new_character()
            return
        
        elif cmd.startswith("/加载") or cmd.startswith("/load"):
            args = command[3:].strip() if command.startswith("/加载") else command[5:].strip()
            self.character_handler.handle_load_character(args)
            return
        
        elif cmd.startswith("/角色列表") or cmd == "/chars":
            self.character_handler.handle_list_characters()
            return

        elif cmd == "/help":
            self.display_help()
            self.logger.debug("显示帮助信息")

        elif cmd == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            self.display_welcome()
            self.logger.debug("清屏")

        elif cmd == "/memories":
            self._display_memories()

        elif cmd == "/stats":
            self._display_stats()

        elif cmd == "/history":
            self._display_history()

        elif cmd.startswith("/model"):
            args = cmd[6:].strip()
            self._handle_model_command(args)

        elif cmd == "/intent":
            self._display_intent()

        elif cmd == "/context":
            self._display_context()
        
        elif cmd == "/热更新" or cmd == "/reload":
            self._handle_hot_reload()

        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('未知命令:')} {colorize(command, Color.BOLD_RED)}")
            print(f"   {dim('输入 /help 查看可用命令')}")

    def _is_game_command(self, user_input: str) -> bool:
        """
        检查是否为游戏命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否为游戏命令
        """
        game_commands = [
            "修炼", "xiulian", "突破", "tupo", "状态", "status",
            "前往", "go", "地图", "map", "位置", "location",
            "交谈", "talk", "npc", "帮助", "help", "退出", "quit", "exit",
            "角色列表", "chars", "加载", "load", "新建角色", "new",
            "功法", "gongfa", "学习", "learn", "可学功法", "available",
            "背包", "bag", "使用", "use", "装备", "equip", "门派", "sect",
            "探索", "explore", "生成", "generate", "妖兽", "monsters",
            "战斗", "combat", "切磋", "spar", "死斗", "deathmatch",
            "攻击", "attack", "技能", "skill", "逃跑", "flee",
            # 处决与饶恕命令：用于处理战败敌人的道德选择
            "处决", "execute", "饶恕", "spare",
            "admin", "gm"
        ]
        
        # 标准化输入：去除多余空格，转小写
        normalized_input = user_input.strip().lower()
        
        # 获取输入的第一个词
        parts = normalized_input.split(maxsplit=1)
        if not parts:
            return False
        
        first_word = parts[0]
        
        # 检查是否以命令词开头
        for cmd in game_commands:
            if normalized_input.startswith(cmd.lower()):
                return True
        
        return False
    
    def _convert_to_command(self, user_input: str) -> str:
        """
        将中文命令转换为标准命令格式
        
        Args:
            user_input: 用户输入
            
        Returns:
            标准命令格式
        """
        # 标准化输入
        normalized_input = user_input.strip().lower()
        
        # 命令映射（按长度降序排列，避免短命令匹配错误）
        command_map = {
            # 中文命令
            "修炼": "/修炼",
            "突破": "/突破",
            "状态": "/状态",
            "前往": "/前往",
            "地图": "/地图",
            "秘境": "/秘境",
            "位置": "/位置",
            "交谈": "/交谈",
            "帮助": "/help",
            "退出": "/quit",
            "角色列表": "/角色列表",
            "加载": "/加载",
            "新建角色": "/新建角色",
            "功法": "/功法",
            "学习": "/学习",
            "可学功法": "/可学功法",
            "背包": "/背包",
            "使用": "/使用",
            "装备": "/装备",
            "门派": "/门派",
            "探索": "/探索",
            "生成": "/生成",
            "妖兽": "/妖兽",
            "战斗": "/战斗",
            "切磋": "/切磋",
            "死斗": "/死斗",
            "攻击": "/攻击",
            "技能": "/技能",
            "逃跑": "/逃跑",
            # 处决与饶恕命令映射：中文命令映射到标准命令格式
            "处决": "/处决",
            "饶恕": "/饶恕",
            "admin": "/admin",
            "gm": "/gm",
            # 英文命令
            "explore": "/探索",
            "generate": "/生成",
            "monsters": "/妖兽",
            "combat": "/战斗",
            "spar": "/切磋",
            "deathmatch": "/死斗",
            "attack": "/攻击",
            "skill": "/技能",
            "flee": "/逃跑",
            # 处决与饶恕命令映射：英文命令映射到标准命令格式
            "execute": "/处决",
            "spare": "/饶恕",
            "xiulian": "/修炼",
            "tupo": "/突破",
            "status": "/状态",
            "go": "/前往",
            "map": "/地图",
            "location": "/位置",
            "talk": "/交谈",
            "help": "/help",
            "quit": "/quit",
            "exit": "/quit",
            "npc": "/npc",
            "chars": "/角色列表",
            "load": "/加载",
            "new": "/新建角色",
            "gongfa": "/功法",
            "learn": "/学习",
            "available": "/可学功法",
            "bag": "/背包",
            "use": "/使用",
            "equip": "/装备",
            "sect": "/门派",
        }
        
        # 查找匹配的命令
        matched_cmd = None
        matched_key = None
        
        for key in sorted(command_map.keys(), key=len, reverse=True):
            if normalized_input.startswith(key):
                matched_key = key
                matched_cmd = command_map[key]
                break
        
        if not matched_cmd:
            return f"/{normalized_input}"
        
        # 提取参数
        args = normalized_input[len(matched_key):].strip()
        
        if args:
            return f"{matched_cmd} {args}"
        return matched_cmd

    def process_message(self, message: str):
        try:
            # 显示加载动画
            self._show_loading("正在思考")

            # 使用对话引擎生成回复
            if self.dialogue_engine:
                response = self.dialogue_engine.chat(message)
            else:
                # 如果没有对话引擎，使用简单回显
                response = f"收到您的消息: {message}"
            
            # 游戏模式下，过滤AI回复（防止"乱说"）
            if self.game_mode and self.player:
                filtered_response, was_modified = filter_ai_response(
                    message, 
                    response, 
                    dao_name=self.player.get_title() if self.player else "贫道"
                )
                if was_modified:
                    # 如果回复被修改，显示提示
                    print(f"\n{colorize('🤖 AI:', Color.BOLD_GREEN)} {filtered_response}")
                    print(f"{colorize('⚠️ 注：AI原回复违反修仙设定，已自动修正', Color.BOLD_YELLOW)}")
                else:
                    print(f"\n{colorize('🤖 AI:', Color.BOLD_GREEN)} {filtered_response}")
                response = filtered_response
            else:
                print(f"\n{colorize('🤖 AI:', Color.BOLD_GREEN)} {response}")

            # 添加到记忆
            if self.memory_manager:
                self.memory_manager.add_memory(response, source="ai")
                self.logger.info("添加 AI 回复到记忆")
            
            # 游戏模式下，评判AI回复并给予修为奖励
            if self.game_mode and self.player:
                self._judge_ai_response(message, response)

        except Exception as e:
            error_msg = f"处理消息时出错: {e}"
            print(f"\n{colorize('❌', Color.BOLD_RED)} {error(error_msg)}")
            self.logger.exception("处理消息失败")
    
    def _judge_ai_response(self, user_input: str, ai_response: str):
        """
        评判AI回复并给予修为奖励
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
        """
        try:
            # 评判AI回复
            context = {
                "realm_level": self.player.stats.realm_level,
            }
            result = judge_ai_reply(user_input, ai_response, **context)
            
            # 显示评判结果
            print(f"\n{colorize('☯️ 天道评判', Color.BOLD_CYAN)}")
            print(f"{colorize('─' * 50, Color.BOLD_BLUE)}")
            print(result.feedback)
            print(f"{colorize('─' * 50, Color.BOLD_BLUE)}")
            print(f"  总分: {result.score}/100 | 沉浸感: {result.immersion_score} | 有用性: {result.helpfulness_score}")
            print(f"  术语使用: {result.xiuxian_term_count}处 | 创意: {result.creativity_score}")
            
            # 给予修为奖励
            if result.exp_reward > 0:
                self.player.add_exp(result.exp_reward)
                print(f"\n  {colorize('🎁 修为奖励', Color.BOLD_YELLOW)}: +{result.exp_reward} 修为")
                
                # 检查是否可以突破
                if self.player.can_breakthrough():
                    print(f"  {colorize('⚡ 突破提示', Color.BOLD_GREEN)}: 修为已满，可尝试突破！")
            
            # 推进时间（对话消耗1天）
            self.player.advance_time(1)
            
        except Exception as e:
            self.logger.error(f"评判AI回复时出错: {e}")

    def _show_loading(self, message: str = "处理中", duration: float = 0.5):
        """
        显示加载动画
        
        Args:
            message: 加载消息
            duration: 动画持续时间（秒）
        """
        spinner = Spinner(message, Color.CYAN)
        start_time = time.time()
        
        while time.time() - start_time < duration:
            print(f"\r{spinner.next()}", end='', flush=True)
            time.sleep(0.1)
        
        # 清除加载动画
        print(f"\r{' ' * 30}\r", end='')

    def _display_memories(self):
        if not self.memory_manager:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('记忆管理器未初始化')}")
            return

        try:
            memories = self.memory_manager.get_all_memories()

            if not memories:
                empty_panel = UIPanel.info_panel("📚 记忆列表", width=60)
                empty_panel.add_line(colorize("当前没有记忆", UITheme.TEXT_DIM), align='center')
                print(empty_panel.render())
                return

            # 使用UITable显示记忆列表
            headers = ['#', '来源', '内容']
            rows = []
            
            for idx, memory in enumerate(memories, 1):
                content = memory.get("content", "") if isinstance(memory, dict) else str(memory)
                content = content[:40] + "..." if len(content) > 40 else content
                
                source = memory.get("source", "unknown") if isinstance(memory, dict) else "unknown"
                if source == "user":
                    source_display = colorize("👤 用户", Color.BOLD_GREEN)
                    content_display = green(content)
                elif source == "ai":
                    source_display = colorize("🤖 AI", Color.BOLD_CYAN)
                    content_display = cyan(content)
                else:
                    source_display = colorize("📄 其他", Color.DIM)
                    content_display = dim(content)
                
                rows.append([str(idx), source_display, content_display])
            
            # 创建面板
            panel = UIPanel.info_panel("📚 当前记忆列表", width=62)
            print(panel.render())
            
            # 创建表格
            table = UITable(headers=headers, rows=rows, width=62)
            print(table.render())
            
            # 底部信息
            footer_panel = UIPanel(width=62, border_style='none')
            footer_panel.add_line(colorize(f"共 {len(memories)} 条记忆 (使用 /stats 查看统计)", UITheme.TEXT_DIM), align='center')
            print(footer_panel.render())
            
            self.logger.info(f"显示记忆列表，共 {len(memories)} 条")

        except Exception as e:
            error_msg = f"获取记忆列表失败: {e}"
            print(f"\n{colorize('❌', Color.BOLD_RED)} {error(error_msg)}")
            self.logger.exception("获取记忆列表失败")

    def _display_stats(self):
        if not self.memory_manager:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('记忆管理器未初始化')}")
            return

        try:
            memories = self.memory_manager.get_all_memories()
            total_memories = len(memories)

            user_memories = sum(1 for m in memories
                              if isinstance(m, dict) and m.get("source") == "user")
            ai_memories = sum(1 for m in memories
                            if isinstance(m, dict) and m.get("source") == "ai")
            other_memories = total_memories - user_memories - ai_memories

            # 使用UIInfoCard显示统计信息
            card = UIInfoCard(title="📊 记忆统计信息", width=60)
            
            # 添加统计数据
            card.add_key_value("总记忆数", total_memories, "📦")
            card.add_key_value("用户消息", colorize(str(user_memories), Color.BOLD_GREEN), "👤")
            card.add_key_value("AI 回复", colorize(str(ai_memories), Color.BOLD_CYAN), "🤖")
            if other_memories > 0:
                card.add_key_value("其他来源", colorize(str(other_memories), Color.DIM), "📄")
            
            print(card.render())
            
            self.logger.info(f"显示统计信息: 总计={total_memories}, 用户={user_memories}, AI={ai_memories}")

        except Exception as e:
            error_msg = f"获取统计信息失败: {e}"
            print(f"\n{colorize('❌', Color.BOLD_RED)} {error(error_msg)}")
            self.logger.exception("获取统计信息失败")

    def _display_history(self):
        """显示输入历史记录"""
        try:
            import readline
            
            history_length = readline.get_current_history_length()
            
            if history_length == 0:
                print(f"\n{colorize('📭', Color.BOLD_YELLOW)}  {dim('暂无输入历史')}")
                return
            
            print(f"\n{colorize('─' * 60, Color.BOLD_YELLOW)}")
            print(f"  {colorize('📝', Color.BOLD_YELLOW)}  {bold('输入历史记录')}")
            print(f"{colorize('─' * 60, Color.BOLD_YELLOW)}")
            
            # 显示最近 20 条历史记录
            start_idx = max(1, history_length - 19)
            for i in range(start_idx, history_length + 1):
                item = readline.get_history_item(i)
                if item:
                    idx_colored = colorize(f"{i:3d}.", Color.BOLD_BLUE)
                    # 截断过长的历史记录
                    display_item = item[:50] + "..." if len(item) > 50 else item
                    print(f"  {idx_colored} {dim(display_item)}")
            
            print(f"{colorize('─' * 60, Color.BOLD_YELLOW)}")
            print(f"  {dim(f'共 {history_length} 条历史记录')}  {dim('(使用 ↑ ↓ 键浏览)')}")
            
        except ImportError:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('输入历史记录功能不可用')}")

    def _handle_model_command(self, args: str):
        """处理模型相关命令"""
        if not args:
            self._display_model_status()
        elif args == "list":
            self._display_available_models()
        elif args.startswith("load "):
            model_path = args[5:].strip()
            self._load_model(model_path)
        elif args == "unload":
            self._unload_model()
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('未知的模型命令:')} {colorize(args, Color.BOLD_RED)}")
            print(f"   {dim('用法: /model [list|load <路径>|unload]')}")

    def _display_model_status(self):
        """显示模型状态"""
        print(f"\n{colorize('─' * 60, Color.BOLD_CYAN)}")
        print(f"  {colorize('🤖', Color.BOLD_CYAN)}  {bold('模型状态')}")
        print(f"{colorize('─' * 60, Color.BOLD_CYAN)}")
        
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'model_loaded'):
            if self.dialogue_engine.model_loaded:
                model_name = getattr(self.dialogue_engine, 'current_model_name', '未知模型')
                print(f"  {colorize('✅', Color.BOLD_GREEN)}  模型状态: {green('已加载')}")
                print(f"  {colorize('📦', Color.BOLD_BLUE)}  模型名称: {cyan(model_name)}")
            else:
                print(f"  {colorize('❌', Color.BOLD_RED)}  模型状态: {red('未加载')}")
        else:
            print(f"  {colorize('⚠️', Color.BOLD_YELLOW)}  {warning('对话引擎未初始化或不可用')}")
        
        print(f"{colorize('─' * 60, Color.BOLD_CYAN)}")

    def _display_available_models(self):
        """显示可用模型列表"""
        print(f"\n{colorize('─' * 60, Color.BOLD_BLUE)}")
        print(f"  {colorize('📦', Color.BOLD_YELLOW)}  {bold('可用模型列表')}")
        print(f"{colorize('─' * 60, Color.BOLD_BLUE)}")
        
        # 获取可用模型列表
        models = []
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'get_available_models'):
            try:
                models = self.dialogue_engine.get_available_models()
            except Exception as e:
                self.logger.warning(f"获取模型列表失败: {e}")
        
        # 默认模型列表
        if not models:
            models = [
                {"name": "default", "path": "models/default", "description": "默认模型"},
                {"name": "gpt2", "path": "models/gpt2", "description": "GPT-2 模型"},
            ]
        
        for idx, model in enumerate(models, 1):
            idx_colored = colorize(f"{idx:3d}.", Color.BOLD_BLUE)
            name_colored = bold(model.get('name', '未知'))
            desc_colored = dim(model.get('description', ''))
            path_colored = cyan(model.get('path', ''))
            print(f"  {idx_colored} {name_colored}")
            print(f"      {dim('路径:')} {path_colored}")
            if desc_colored:
                print(f"      {dim('描述:')} {desc_colored}")
        
        print(f"{colorize('─' * 60, Color.BOLD_BLUE)}")
        print(f"  {dim(f'共 {len(models)} 个模型')}  {dim('(使用 /model load <路径> 加载)')}")

    def _load_model(self, model_path: str):
        """加载模型"""
        if not model_path:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('请提供模型路径')}")
            print(f"   {dim('用法: /model load <路径>')}")
            return
        
        print(f"\n{colorize('⏳', Color.BOLD_YELLOW)}  {info('正在加载模型...')}")
        self.logger.info(f"正在加载模型: {model_path}")
        
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'load_model'):
            try:
                self._show_loading("加载模型中", duration=1.0)
                success_load = self.dialogue_engine.load_model(model_path)
                if success_load:
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)}  {success('模型加载成功！')}")
                    self.logger.info(f"模型加载成功: {model_path}")
                else:
                    print(f"\n{colorize('❌', Color.BOLD_RED)}  {error('模型加载失败')}")
                    self.logger.error(f"模型加载失败: {model_path}")
            except Exception as e:
                print(f"\n{colorize('❌', Color.BOLD_RED)}  {error(f'加载模型时出错: {e}')}")
                self.logger.exception("加载模型失败")
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('对话引擎未初始化或不可用')}")
            self.logger.warning("尝试加载模型但对话引擎不可用")

    def _unload_model(self):
        """卸载模型"""
        print(f"\n{colorize('⏳', Color.BOLD_YELLOW)}  {info('正在卸载模型...')}")
        self.logger.info("正在卸载模型")
        
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'unload_model'):
            try:
                self._show_loading("卸载模型中", duration=0.5)
                self.dialogue_engine.unload_model()
                print(f"\n{colorize('✅', Color.BOLD_GREEN)}  {success('模型已卸载')}")
                self.logger.info("模型卸载成功")
            except Exception as e:
                print(f"\n{colorize('❌', Color.BOLD_RED)}  {error(f'卸载模型时出错: {e}')}")
                self.logger.exception("卸载模型失败")
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('对话引擎未初始化或不可用')}")
            self.logger.warning("尝试卸载模型但对话引擎不可用")

    def _display_intent(self):
        """显示当前消息的意图分析"""
        print(f"\n{colorize('─' * 60, Color.BOLD_GREEN)}")
        print(f"  {colorize('🎯', Color.BOLD_GREEN)}  {bold('意图分析')}")
        print(f"{colorize('─' * 60, Color.BOLD_GREEN)}")
        
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'get_last_intent'):
            try:
                intent = self.dialogue_engine.get_last_intent()
                if intent:
                    print(f"  {colorize('📌', Color.BOLD_YELLOW)}  意图类型: {cyan(intent.get('type', '未知'))}")
                    confidence = intent.get('confidence', 0)
                    print(f"  {colorize('📊', Color.BOLD_BLUE)}  置信度: {green(f'{confidence:.2%}')}")
                    if 'entities' in intent:
                        print(f"  {colorize('🏷️', Color.BOLD_MAGENTA)}  实体: {dim(str(intent.get('entities', [])))}")
                else:
                    print(f"  {colorize('📭', Color.BOLD_YELLOW)}  {dim('暂无意图分析数据')}")
            except Exception as e:
                print(f"  {colorize('⚠️', Color.BOLD_YELLOW)}  {warning(f'获取意图分析失败: {e}')}")
        else:
            print(f"  {colorize('⚠️', Color.BOLD_YELLOW)}  {warning('对话引擎未初始化或不可用')}")
        
        print(f"{colorize('─' * 60, Color.BOLD_GREEN)}")

    def _display_context(self):
        """显示检索到的上下文记忆"""
        print(f"\n{colorize('─' * 60, Color.BOLD_MAGENTA)}")
        print(f"  {colorize('🔗', Color.BOLD_MAGENTA)}  {bold('上下文记忆')}")
        print(f"{colorize('─' * 60, Color.BOLD_MAGENTA)}")
        
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'get_last_context'):
            try:
                context = self.dialogue_engine.get_last_context()
                if context:
                    for idx, item in enumerate(context, 1):
                        idx_colored = colorize(f"{idx:3d}.", Color.BOLD_BLUE)
                        content = item.get('content', str(item)) if isinstance(item, dict) else str(item)
                        content = content[:60] + "..." if len(content) > 60 else content
                        relevance = item.get('relevance', 0) if isinstance(item, dict) else 0
                        print(f"  {idx_colored} {dim(content)}")
                        if relevance > 0:
                            print(f"      {dim('相关度:')} {cyan(f'{relevance:.2f}')}")
                else:
                    print(f"  {colorize('📭', Color.BOLD_YELLOW)}  {dim('暂无上下文记忆')}")
            except Exception as e:
                print(f"  {colorize('⚠️', Color.BOLD_YELLOW)}  {warning(f'获取上下文记忆失败: {e}')}")
        else:
            print(f"  {colorize('⚠️', Color.BOLD_YELLOW)}  {warning('对话引擎未初始化或不可用')}")
        
        print(f"{colorize('─' * 60, Color.BOLD_MAGENTA)}")
