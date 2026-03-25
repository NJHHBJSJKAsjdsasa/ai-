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
        
        if self.game_mode:
            self._init_game()
        
        # 设置输入历史记录
        self._setup_readline()
    
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
        
        # 创建NPC管理器
        self.npc_manager = NPCManager()
        self.npc_manager.generate_npcs_for_location("新手村")
        
        # 创建世界（传入数据库实例以支持动态地点）
        from storage.database import Database
        self.world = World(db=Database())
        
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
            
            # 创建玩家对象并从数据加载
            player = Player(name="道友", load_from_db=False)
            player.from_dict(data)
            
            self.logger.info("成功从数据库加载玩家存档")
            return player
            
        except Exception as e:
            self.logger.error(f"加载玩家存档失败: {e}")
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
            
            # 保存到数据库
            db.save_player(self.player.stats.name, data)
            db.close()
            
            self.logger.info("成功保存玩家存档到数据库")
            return True
            
        except Exception as e:
            self.logger.error(f"保存玩家存档失败: {e}")
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
    
    def start(self):
        self.running = True
        self.display_welcome()
        self.logger.info("CLI 已启动")

        while self.running:
            try:
                # 使用带颜色的提示符
                if self.game_mode and self.player:
                    realm_icon = get_realm_icon(self.player.stats.realm_level)
                    prompt = colorize(f"\n{realm_icon} {self.player.get_realm_name()}", Color.BOLD_CYAN) + colorize("> ", Color.RESET)
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
                # 保存玩家数据
                if self.game_mode:
                    self.save_player()
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 游戏进度已保存")
                print(f"\n{colorize('👋 再见！', Color.BOLD_GREEN)}")
                self.logger.info("用户通过 Ctrl+C 退出")
                break
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
            welcome_text = f"""
{colorize('╔══════════════════════════════════════════════════════════════╗', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}              {colorize('☯️ 修仙世界 - AI驱动文字修仙游戏', Color.BOLD_WHITE)}              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}                                                              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {dim('欢迎来到修仙世界！这是一个由AI驱动的真实修仙体验。')}        {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {dim('资质平庸、突破艰难、寿元有限、因果报应...')}                    {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {dim('每个选择都会影响你的修仙之路。')}                              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}                                                              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {info('输入 /help 查看可用命令')}                                     {colorize('║', Color.BOLD_CYAN)}
{colorize('╚══════════════════════════════════════════════════════════════╝', Color.BOLD_CYAN)}
            """
            print(welcome_text)
            
            # 显示玩家初始状态
            if self.player:
                print(self.player.get_status_text())
        else:
            welcome_text = f"""
{colorize('╔══════════════════════════════════════════════════════════════╗', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}                    {colorize('🤖 AI 学习系统', Color.BOLD_WHITE)}                            {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}                                                              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {dim('欢迎使用 AI 学习系统！这是一个智能对话和记忆管理平台。')}      {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}                                                              {colorize('║', Color.BOLD_CYAN)}
{colorize('║', Color.BOLD_CYAN)}  {info('输入 /help 查看可用命令')}                                     {colorize('║', Color.BOLD_CYAN)}
{colorize('╚══════════════════════════════════════════════════════════════╝', Color.BOLD_CYAN)}
            """
            print(welcome_text)

    def display_help(self):
        if self.game_mode:
            help_text = f"""
{colorize('┌─────────────────────────────────────────────────────────────┐', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                     {colorize('📖 修仙指令大全', Color.BOLD_WHITE)}                        {colorize('│', Color.BOLD_BLUE)}
{colorize('├─────────────────────────────────────────────────────────────┤', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('修炼相关:')}                                                  {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/修炼')} 或 {green('/xiulian')}    - 闭关修炼，增加修为               {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/突破')} 或 {green('/tupo')}      - 尝试突破当前境界                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/状态')} 或 {green('/status')}    - 查看自身状态                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('移动探索:')}                                                  {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/前往')} <地点> 或 {green('/go')}   - 前往指定地点                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/地图')} 或 {green('/map')}       - 查看世界地图                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/秘境')} 或 {green('/secret')}     - 查看秘境/生成地图              {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/位置')} 或 {green('/location')}  - 查看当前位置                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/探索')} 或 {green('/explore')}   - 探索新区域                     {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/妖兽')} 或 {green('/monsters')}  - 查看当前区域妖兽               {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('NPC交互:')}                                                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/交谈')} <NPC名字>          - 与NPC对话                      {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/npcs')}                   - 查看当前地点的NPC              {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/npc')} <名字>             - 查看NPC详细信息                {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/npc_stats')}              - 查看NPC系统统计                {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/门派')}                   - 查看门派列表                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('功法系统:')}                                                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/功法')}                   - 查看已学功法                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/学习')} <功法名>          - 学习功法                       {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/可学功法')}               - 查看可学功法                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('道具系统:')}                                                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/背包')}                   - 查看背包内容                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/使用')} <道具名>          - 使用道具                       {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/装备')} <法宝名>          - 装备法宝                       {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('角色管理:')}                                                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/角色列表')}               - 查看所有角色                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/加载')} <角色名>          - 加载指定角色                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/新建角色')}               - 创建新角色                     {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('无限生成:')}                                                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/生成')} <类型>            - 手动生成内容                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                              (地图/NPC/物品/妖兽)              {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('系统指令:')}                                                  {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/quit')}, {green('/exit')}       - 退出游戏                       {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/help')}                   - 显示此帮助信息                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/clear')}                  - 清屏                           {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('管理员命令:')}                                                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/admin')}                  - 玩家属性管理                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/gm')}                     - 游戏世界管理                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('使用说明:')}                                                  {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 直接输入消息与AI道友交流                                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 使用 {yellow('/')} 开头的命令执行操作                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 修仙之路漫漫，祝道友早日飞升！                           {colorize('│', Color.BOLD_BLUE)}
{colorize('└─────────────────────────────────────────────────────────────┘', Color.BOLD_BLUE)}
            """
            print(help_text)
        else:
            help_text = f"""
{colorize('┌─────────────────────────────────────────────────────────────┐', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                        {colorize('📖 帮助信息', Color.BOLD_WHITE)}                           {colorize('│', Color.BOLD_BLUE)}
{colorize('├─────────────────────────────────────────────────────────────┤', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('命令:')}                                                      {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/quit')}, {green('/exit')}  - 退出程序                                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/help')}         - 显示此帮助信息                           {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/clear')}        - 清屏                                     {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/memories')}     - 查看当前记忆列表                         {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/stats')}        - 查看记忆统计信息                         {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/history')}      - 显示输入历史记录                         {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/model')}        - 模型管理命令                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/intent')}       - 显示当前消息的意图分析                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    {green('/context')}      - 显示检索到的上下文记忆                   {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}                                                             {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}  {bold('使用说明:')}                                                  {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 直接输入消息与 AI 对话                                 {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 使用 {yellow('/')} 开头的命令执行特定操作                          {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 按 {yellow('Ctrl+C')} 或输入 {yellow('/quit')} 退出                            {colorize('│', Color.BOLD_BLUE)}
{colorize('│', Color.BOLD_BLUE)}    • 使用 {yellow('↑ ↓')} 键浏览输入历史                               {colorize('│', Color.BOLD_BLUE)}
{colorize('└─────────────────────────────────────────────────────────────┘', Color.BOLD_BLUE)}
            """
            print(help_text)

    def handle_command(self, command: str):
        cmd = command.lower()
        
        # 游戏模式命令
        if self.game_mode:
            if cmd.startswith("/修炼") or cmd == "/xiulian":
                self._handle_cultivation()
                return
            elif cmd.startswith("/突破") or cmd == "/tupo":
                self._handle_breakthrough()
                return
            elif cmd.startswith("/状态") or cmd == "/status":
                self._handle_status()
                return
            elif cmd.startswith("/前往") or cmd.startswith("/go"):
                args = command[3:].strip() if command.startswith("/前往") else command[3:].strip()
                self._handle_move(args)
                return
            elif cmd.startswith("/地图") or cmd == "/map":
                self._handle_map()
                return
            elif cmd == "/秘境" or cmd == "/secret" or cmd == "/maps":
                self._handle_secret_maps()
                return
            elif cmd.startswith("/位置") or cmd == "/location":
                self._handle_location()
                return
            elif cmd.startswith("/交谈") or cmd.startswith("/talk"):
                args = command[3:].strip() if command.startswith("/交谈") else command[5:].strip()
                self._handle_talk(args)
                return
            elif cmd == "/npcs":
                self._handle_npc_list()
                return
            elif cmd.startswith("/npc "):
                args = command[4:].strip()
                self._handle_npc_detail(args)
                return
            elif cmd == "/npc_stats":
                self._handle_npc_stats()
                return
            elif cmd.startswith("/功法") or cmd == "/gongfa":
                self._handle_techniques()
                return
            elif cmd.startswith("/学习") or cmd.startswith("/learn"):
                args = command[3:].strip() if command.startswith("/学习") else command[5:].strip()
                self._handle_learn_technique(args)
                return
            elif cmd.startswith("/可学功法") or cmd == "/available":
                self._handle_available_techniques()
                return
            elif cmd.startswith("/背包") or cmd == "/bag":
                self._handle_inventory()
                return
            elif cmd.startswith("/使用") or cmd.startswith("/use"):
                args = command[3:].strip() if command.startswith("/使用") else command[4:].strip()
                self._handle_use_item(args)
                return
            elif cmd.startswith("/装备") or cmd.startswith("/equip"):
                args = command[3:].strip() if command.startswith("/装备") else command[6:].strip()
                self._handle_equip_treasure(args)
                return
            elif cmd.startswith("/门派") or cmd == "/sect":
                self._handle_sects()
                return
            elif cmd.startswith("/探索") or cmd == "/explore":
                self._handle_explore()
                return
            elif cmd.startswith("/生成") or cmd == "/generate":
                args = command[3:].strip() if command.startswith("/生成") else command[9:].strip()
                self._handle_generate(args)
                return
            elif cmd.startswith("/妖兽") or cmd == "/monsters":
                self._handle_monsters()
                return
            
            # ========== 管理员命令 ==========
            elif cmd.startswith("/admin"):
                args = command[6:].strip()
                self._handle_admin_command(args)
                return
            elif cmd.startswith("/gm"):
                args = command[3:].strip()
                self._handle_gm_command(args)
                return
        
        # 基础命令
        if cmd in ["/quit", "/exit"]:
            # 保存玩家数据
            if self.game_mode and self.player:
                if self.save_player():
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 游戏进度已保存")
            print(f"\n{colorize('👋 再见！', Color.BOLD_GREEN)}")
            self.logger.info("用户执行退出命令")
            self.running = False
        
        elif cmd.startswith("/新建角色") or cmd == "/new":
            self._handle_new_character()
            return
        
        elif cmd.startswith("/加载") or cmd.startswith("/load"):
            args = command[3:].strip() if command.startswith("/加载") else command[5:].strip()
            self._handle_load_character(args)
            return
        
        elif cmd.startswith("/角色列表") or cmd == "/chars":
            self._handle_list_characters()
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

        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)}  {warning('未知命令:')} {colorize(command, Color.BOLD_RED)}")
            print(f"   {dim('输入 /help 查看可用命令')}")
    
    # ==================== 游戏命令处理 ====================
    
    def _handle_cultivation(self):
        """处理修炼命令"""
        if not self.cultivation_system:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 修炼系统未初始化")
            return
        
        result = self.cultivation_system.practice(times=1)
        
        if result["success"]:
            print(f"\n{colorize('☯️ 修炼', Color.BOLD_CYAN)}")
            print(f"{result['message']}")
            if result.get("messages"):
                for msg in result["messages"]:
                    print(f"  • {msg}")
            
            # 检查随机事件
            self._check_random_event()
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} {result['message']}")
    
    def _handle_breakthrough(self):
        """处理突破命令"""
        if not self.cultivation_system:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 突破系统未初始化")
            return
        
        # 先显示突破信息
        info = self.cultivation_system.get_breakthrough_info()
        print(f"\n{colorize('🎯 突破信息', Color.BOLD_CYAN)}")
        print(info["message"])
        
        if info["can_breakthrough"]:
            print(f"\n{colorize('⚡ 正在尝试突破...', Color.BOLD_YELLOW)}")
            result = self.cultivation_system.attempt_breakthrough()
            print(result["message"])
            
            # 检查是否死亡
            if self.player and self.player.stats.is_dead:
                print(f"\n{colorize('💀 道友已陨落...', Color.BOLD_RED)}")
                # 转世重生
                if result.get("death_info"):
                    input(f"\n{colorize('按回车键转世重生...', Color.BOLD_YELLOW)}")
                    self.player.reincarnate(result["death_info"]["inheritance"])
                    print(f"\n{colorize('✨ 转世成功！', Color.BOLD_GREEN)}")
                    print(self.player.get_status_text())
    
    def _handle_status(self):
        """处理状态命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        print(self.player.get_status_text())
        
        # 显示灵根信息
        spirit_root_name = self.player.get_spirit_root_name()
        spirit_root_desc = self.player.get_spirit_root_description()
        print(f"\n{colorize('🌟 灵根资质', Color.BOLD_CYAN)}: {spirit_root_name}")
        print(f"  {dim(spirit_root_desc)}")
        print(f"  修炼速度: {self.player.get_cultivation_speed():.1f}倍")
    
    def _handle_move(self, location_name: str):
        """处理移动命令"""
        if not self.world or not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        if not location_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要前往的地点")
            print(f"  可用命令: /前往 <地点名>")
            return
        
        # 检查是否可以进入
        if not self.world.can_enter(location_name, self.player.stats.realm_level):
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 境界不足，无法进入{location_name}")
            realm_info = self.world.get_location(location_name)
            if realm_info:
                required_realm = get_realm_info(realm_info.realm_required)
                if required_realm:
                    print(f"  需要境界: {required_realm.name}")
            return
        
        # 检查是否可以从当前位置到达
        accessible = self.world.get_accessible_locations(self.player.stats.location, self.player.stats.realm_level)
        if location_name not in accessible:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 无法直接前往{location_name}")
            print(f"  当前可前往: {', '.join(accessible) if accessible else '无'}")
            return
        
        # 移动
        old_location = self.player.stats.location
        self.player.stats.location = location_name
        
        # 消耗时间
        self.player.advance_time(1)
        
        print(f"\n{colorize('🚶 移动', Color.BOLD_CYAN)}: {old_location} → {location_name}")
        print(self.world.get_location_description(location_name))
        
        # 生成新地点的NPC
        if self.npc_manager:
            existing_npcs = self.npc_manager.get_npcs_in_location(location_name)
            if len(existing_npcs) < 3:
                self.npc_manager.generate_npcs_for_location(location_name, 3 - len(existing_npcs))
    
    def _handle_map(self):
        """处理地图命令"""
        if not self.world:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        print(f"\n{colorize('🗺️ 世界地图', Color.BOLD_CYAN)}")
        print(colorize("═" * 50, Color.BOLD_BLUE))
        
        for location in self.world.get_all_locations():
            marker = "📍" if self.player and self.player.stats.location == location.name else "  "
            realm_info = get_realm_info(location.realm_required)
            realm_name = realm_info.name if realm_info else "凡人"
            print(f"{marker} {location.name:<10} (需{realm_name})")
        
        print(colorize("═" * 50, Color.BOLD_BLUE))
    
    def _handle_secret_maps(self):
        """处理秘境命令 - 显示生成的地图/秘境列表"""
        if not self.world:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
            return
        
        print(f"\n{colorize('🏛️ 秘境/生成地图列表', Color.BOLD_CYAN)}")
        print(colorize("═" * 60, Color.BOLD_BLUE))
        
        # 从数据库加载生成的地图
        from storage.database import Database
        db = Database()
        generated_maps = db.get_all_generated_maps()
        db.close()
        
        if not generated_maps:
            print(f"  {colorize('📭', Color.DIM)} 暂无秘境")
            print(f"\n  使用 {green('/gm map [数量] [名字] [境界]')} 生成新秘境")
        else:
            # 按类型分类显示
            maps_by_type = {}
            for map_data in generated_maps:
                map_type = map_data.get('map_type', '未知')
                if map_type not in maps_by_type:
                    maps_by_type[map_type] = []
                maps_by_type[map_type].append(map_data)
            
            for map_type, maps in maps_by_type.items():
                print(f"\n  {colorize('▸', Color.BOLD_YELLOW)} {map_type}:")
                for map_data in maps:
                    name = map_data.get('name', '未知')
                    level = map_data.get('level', 0)
                    realm_info = get_realm_info(level)
                    realm_name = realm_info.name if realm_info else "凡人"
                    
                    # 标记当前所在位置
                    marker = "📍" if self.player and self.player.stats.location == name else "  "
                    
                    # 检查是否满足进入条件
                    can_enter = self.player and self.player.stats.realm_level >= level
                    enter_icon = "✓" if can_enter else "✗"
                    
                    print(f"    {marker} {name:<15} (需{realm_name}) [{enter_icon}]")
        
        print(colorize("═" * 60, Color.BOLD_BLUE))
        print(f"\n  提示: 使用 {green('/前往 <秘境名>')} 进入秘境")
    
    def _handle_location(self):
        """处理位置命令"""
        if not self.player or not self.world:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        location = self.world.get_location(self.player.stats.location)
        if location:
            print(self.world.get_location_description(location.name))
            
            # 显示可前往的地点
            accessible = self.world.get_accessible_locations(location.name, self.player.stats.realm_level)
            if accessible:
                print(f"\n{colorize('🚶 可前往', Color.BOLD_CYAN)}: {', '.join(accessible)}")
            
            # 显示可前往的秘境
            from storage.database import Database
            db = Database()
            generated_maps = db.get_all_generated_maps()
            db.close()
            
            accessible_maps = []
            for map_data in generated_maps:
                map_name = map_data.get('name', '')
                map_level = map_data.get('level', 0)
                connections = map_data.get('connections', [])
                
                # 检查是否与当前位置相连且满足境界要求
                if location.name in connections and self.player.stats.realm_level >= map_level:
                    accessible_maps.append(map_name)
            
            if accessible_maps:
                print(f"\n{colorize('🏛️ 可前往秘境', Color.BOLD_MAGENTA)}: {', '.join(accessible_maps)}")
    
    def _handle_talk(self, npc_name: str):
        """处理交谈命令"""
        if not self.npc_manager or not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        if not npc_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要交谈的NPC")
            print(f"  可用命令: /交谈 <NPC名字>")
            return
        
        # 查找NPC
        npc = self.npc_manager.get_npc_by_name(npc_name)
        if not npc or npc.data.location != self.player.stats.location:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} {npc_name}不在此处")
            return
        
        # 显示问候
        greeting = npc.get_greeting(self.player.stats.name)
        print(f"\n{colorize('👤', Color.BOLD_CYAN)} {npc.data.dao_name} ({npc.get_realm_name()})")
        print(f"  {greeting}")
        print(f"  门派: {npc.data.sect}  职业: {npc.data.occupation}")
        print(f"  性格: {npc.data.personality}")
        
        # 更新好感度
        npc.update_favor(self.player.stats.name, 1)
        
        # 添加记忆
        npc.add_memory(f"与{self.player.stats.name}交谈", importance=3)
    
    def _handle_npc_list(self):
        """处理NPC列表命令 - 显示独立NPC系统信息"""
        if not self.world or not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        npcs = self.world.get_npcs_in_location(self.player.stats.location)
        
        if not npcs:
            print(f"\n{colorize('👤', Color.BOLD_CYAN)} 此处暂无其他修士")
            return
        
        print(f"\n{colorize('👥 当前地点的修士', Color.BOLD_CYAN)} ({self.player.stats.location})")
        print(colorize("─" * 60, Color.BOLD_BLUE))
        
        for npc in npcs:
            favor = npc.get_favor(self.player.stats.name)
            favor_icon = "😊" if favor > 30 else "😐" if favor > -30 else "😠"
            status = npc.get_independent_status()
            activity = status.get('current_activity', '闲逛')
            print(f"  {favor_icon} {npc.data.dao_name:<10} {npc.get_realm_name():<8} {npc.data.occupation:<6} [{activity}]")
        
        print(colorize("─" * 60, Color.BOLD_BLUE))
        print(f"  共{len(npcs)}位修士在此地活动")
        print(f"  使用 {green('/npc <名字>')} 查看详细信息")
    
    def _handle_npc_detail(self, npc_name: str):
        """处理NPC详情命令"""
        if not self.world or not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        if not npc_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定NPC名字")
            print(f"  可用命令: /npc <名字>")
            return
        
        npc = self.world.get_npc_by_name(npc_name)
        if not npc:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 未找到名为'{npc_name}'的修士")
            return
        
        # 获取独立系统状态
        status = npc.get_independent_status()
        
        print(f"\n{colorize('📋 NPC详情', Color.BOLD_CYAN)}")
        print(colorize("═" * 60, Color.BOLD_BLUE))
        print(f"  道号: {bold(npc.data.dao_name)}")
        print(f"  境界: {npc.get_realm_name()}")
        print(f"  年龄: {npc.data.age}岁 / {npc.data.lifespan}岁")
        print(f"  门派: {npc.data.sect}")
        print(f"  职业: {npc.data.occupation}")
        print(f"  位置: {npc.data.location}")
        print(f"  性格: {npc.data.personality}")
        print(colorize("─" * 60, Color.BOLD_BLUE))
        
        # 显示独立系统信息
        print(f"  {bold('当前活动:')} {status.get('current_activity', '未知')}")
        print(f"  {bold('最后行动:')} {status.get('last_action', '无')}")
        
        # 显示需求
        print(f"\n  {bold('需求状态:')}")
        needs = status.get('needs', {})
        for need_name, value in needs.items():
            bar = self._render_bar(value, 100, 20)
            print(f"    {need_name:<12} [{bar}] {value:.1f}")
        
        # 显示目标
        print(f"\n  {bold('当前目标:')}")
        goals = status.get('goals', [])
        for goal in goals[:3]:  # 最多显示3个
            progress = goal.get('progress', '0%')
            completed = "✓" if goal.get('completed') else "○"
            print(f"    {completed} {goal.get('description', '未知')} ({progress})")
        
        # 显示性格
        print(f"\n  {bold('性格属性:')}")
        personality = status.get('personality', {})
        for trait, value in personality.items():
            bar = self._render_bar(value * 100, 100, 20)
            print(f"    {trait:<6} [{bar}] {value:.2f}")
        
        # 显示记忆和关系
        print(f"\n  {bold('记忆数量:')} {status.get('memory_count', 0)}")
        print(f"  {bold('关系数量:')} {status.get('relationship_count', 0)}")
        print(f"  {bold('总行动数:')} {status.get('total_actions', 0)}")
        
        print(colorize("═" * 60, Color.BOLD_BLUE))
    
    def _handle_npc_stats(self):
        """处理NPC统计命令"""
        if not self.world:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 系统未初始化")
            return
        
        stats = self.world.get_npc_stats()
        
        print(f"\n{colorize('📊 NPC独立系统统计', Color.BOLD_CYAN)}")
        print(colorize("═" * 60, Color.BOLD_BLUE))
        print(f"  总NPC数: {stats.get('total_npcs', 0)}")
        print(f"  活跃NPC数: {stats.get('active_npcs', 0)}")
        print(f"  总记忆数: {stats.get('total_memories', 0)}")
        print(f"  总关系数: {stats.get('total_relationships', 0)}")
        print(f"  总行动数: {stats.get('total_actions', 0)}")
        
        # 显示区域分布
        zones = stats.get('zones', {})
        if zones:
            print(f"\n  {bold('区域分布:')}")
            for zone, count in zones.items():
                print(f"    {zone}: {count}个NPC")
        
        print(colorize("═" * 60, Color.BOLD_BLUE))
    
    def _render_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """渲染进度条"""
        ratio = min(1.0, value / max_value) if max_value > 0 else 0
        filled = int(width * ratio)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    def _handle_techniques(self):
        """处理功法命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        techniques = self.player.get_learned_techniques()
        
        if not techniques:
            print(f"\n{colorize('📖', Color.BOLD_CYAN)} 你还没有学习任何功法")
            print(f"  使用 /学习 <功法名> 学习功法")
            return
        
        print(f"\n{colorize('📖 已学功法', Color.BOLD_CYAN)}")
        print(colorize("─" * 50, Color.BOLD_BLUE))
        
        from config import get_technique
        for tech_name, tech_data in techniques.items():
            technique = get_technique(tech_name)
            if technique:
                level = tech_data.get("level", 1)
                print(f"  {technique.name} (Lv.{level}) - {technique.description[:30]}...")
    
    def _handle_learn_technique(self, technique_name: str):
        """处理学习功法命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not technique_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要学习的功法")
            print(f"  可用命令: /学习 <功法名>")
            return
        
        success, message = self.player.learn_technique(technique_name)
        if success:
            print(f"\n{colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} {message}")
    
    def _handle_available_techniques(self):
        """处理可学功法命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        from config import get_techniques_by_realm, can_learn_technique
        
        available = get_techniques_by_realm(self.player.stats.realm_level)
        learned = self.player.get_learned_techniques()
        
        print(f"\n{colorize('📚 可学功法', Color.BOLD_CYAN)} (当前境界: {self.player.get_realm_name()})")
        print(colorize("─" * 50, Color.BOLD_BLUE))
        
        for technique in available:
            if technique.name not in learned:
                can_learn = can_learn_technique(
                    technique.name, 
                    self.player.stats.realm_level,
                    self.player.stats.spirit_root
                )
                status = "✅" if can_learn else "❌"
                print(f"  {status} {technique.name} - {technique.description[:25]}...")
    
    def _handle_inventory(self):
        """处理背包命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        print(f"\n{colorize('🎒 背包', Color.BOLD_CYAN)}")
        print(colorize("─" * 50, Color.BOLD_BLUE))
        print(self.player.get_inventory_info())
    
    def _handle_use_item(self, item_name: str):
        """处理使用道具命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not item_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要使用的道具")
            print(f"  可用命令: /使用 <道具名>")
            return
        
        success, message = self.player.use_item(item_name)
        if success:
            print(f"\n{colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} {message}")
    
    def _handle_equip_treasure(self, treasure_name: str):
        """处理装备法宝命令"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not treasure_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要装备的法宝")
            print(f"  可用命令: /装备 <法宝名>")
            return
        
        success, message = self.player.equip_treasure(treasure_name)
        if success:
            print(f"\n{colorize('✅', Color.BOLD_GREEN)} {message}")
        else:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} {message}")
    
    def _handle_sects(self):
        """处理门派命令"""
        from config import SECT_DETAILS
        
        print(f"\n{colorize('🏛️ 门派列表', Color.BOLD_CYAN)}")
        print(colorize("─" * 50, Color.BOLD_BLUE))
        
        for sect_name, sect_info in SECT_DETAILS.items():
            sect_type = sect_info.get("type", "未知")
            location = sect_info.get("location", "未知")
            print(f"  {sect_name} ({sect_type}) - {location}")
            print(f"    {sect_info.get('description', '')[:40]}...")
    
    def _handle_explore(self):
        """处理探索命令 - 使用探索管理器探索新区域"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not hasattr(self, 'exploration_manager') or not self.exploration_manager:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 探索系统未初始化")
            return
        
        try:
            # 使用探索管理器进行探索
            result = self.exploration_manager.explore(
                self.player.stats.location, 
                self.player.stats.realm_level
            )
            
            # 格式化并显示结果
            print(self.exploration_manager.format_exploration_result(result))
            
            # 如果发现了物品，添加到玩家背包
            if result.discovered_items:
                for item in result.discovered_items:
                    # 将生成的物品转换为字典格式
                    item_data = {
                        "name": item.name,
                        "description": getattr(item, 'description', f'这是一件{item.rarity.value}的{item.item_type.value}'),
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "effects": list(getattr(item, 'effects', {}).keys()) if hasattr(item, 'effects') else [],
                        "value": getattr(item, 'attributes', {}).get('power', 100) * 10,
                        "stackable": True,
                        "max_stack": 99,
                        "usable": True,
                        "level_required": 0,
                        "origin": "探索获得"
                    }
                    
                    # 添加到背包
                    if self.player.inventory.add_generated_item(item.name, item_data, 1):
                        print(f"  ✓ {item.name} 已添加到背包")
                    else:
                        print(f"  ✗ {item.name} 添加失败")
            
            # 如果发现了新地点，推进时间
            if result.success and result.discovered_location:
                self.player.advance_time(1)
                
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 探索失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_generate(self, args: str):
        """处理生成命令 - 手动生成内容"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        try:
            from game.generator import InfiniteGenerator
            from storage.database import Database
            
            generator = InfiniteGenerator(use_llm=False)
            
            if not args:
                print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要生成的内容类型")
                print(f"  用法: /生成 <地图|NPC|物品|妖兽>")
                return
            
            arg_lower = args.lower()
            db = Database()
            
            if arg_lower in ["地图", "map"]:
                # 生成地图
                new_map = generator.generate_map(target_level=self.player.stats.realm_level)
                db.save_generated_map(new_map.to_dict())
                
                print(f"\n{colorize('🗺️ 生成新地图', Color.BOLD_GREEN)}")
                print(f"  名称: {new_map.name}")
                print(f"  类型: {new_map.map_type.value}")
                print(f"  等级: {new_map.level}")
                print(f"  规模: {new_map.size}")
                print(f"  描述: {new_map.description[:50]}...")
                
            elif arg_lower in ["npc", "人物"]:
                # 生成NPC
                location = self.player.stats.location if self.player else "未知"
                npc = generator.generate_npc(
                    location=location, 
                    target_realm=generator.generate_realm_level(self.player.stats.realm_level)
                )
                db.save_generated_npc(npc.to_dict())
                
                print(f"\n{colorize('👤 生成新NPC', Color.BOLD_GREEN)}")
                print(f"  姓名: {npc.full_name}")
                print(f"  性别: {npc.gender}")
                print(f"  年龄: {npc.age}岁")
                from config import get_realm_info
                realm_info = get_realm_info(npc.realm_level)
                print(f"  修为: {realm_info.name if realm_info else '凡人'}")
                print(f"  职业: {npc.occupation.value}")
                print(f"  性格: {npc.personality.value}")
                print(f"  口头禅: {npc.catchphrase}")
                
            elif arg_lower in ["物品", "item"]:
                # 生成物品
                item = generator.generate_item()
                db.save_generated_item(item.to_dict())
                
                print(f"\n{colorize('📦 生成新物品', Color.BOLD_GREEN)}")
                print(f"  名称: {item.name}")
                print(f"  类型: {item.item_type.value}")
                print(f"  稀有度: {item.rarity.value}")
                print(f"  描述: {item.description[:50]}...")
                
            elif arg_lower in ["妖兽", "monster"]:
                # 生成妖兽
                location = self.player.stats.location if self.player else "未知"
                monster = generator.generate_monster(
                    level=self.player.stats.realm_level + 1,
                    location=location
                )
                db.save_generated_monster(monster.to_dict())
                
                print(f"\n{colorize('👹 生成新妖兽', Color.BOLD_GREEN)}")
                print(f"  名称: {monster.name}")
                print(f"  类型: {monster.monster_type.value}")
                print(f"  等级: {monster.level}")
                from config import get_realm_info
                realm_info = get_realm_info(monster.realm_level)
                print(f"  修为: {realm_info.name if realm_info else '凡人'}")
                print(f"  描述: {monster.description[:50]}...")
                print(f"  弱点: {monster.weakness}")
                
            else:
                print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 未知的生成类型: {args}")
                print(f"  可用类型: 地图、NPC、物品、妖兽")
            
            db.close()
                
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_monsters(self):
        """处理妖兽命令 - 查看当前地图的妖兽"""
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        try:
            from storage.database import Database
            from config import get_realm_info
            
            location = self.player.stats.location
            
            db = Database()
            monsters = db.get_generated_monsters_by_location(location)
            db.close()
            
            if not monsters:
                print(f"\n{colorize('👹', Color.BOLD_CYAN)} {location} 暂无妖兽")
                return
            
            print(f"\n{colorize('👹 当前区域妖兽', Color.BOLD_RED)} ({location})")
            print(colorize("─" * 50, Color.BOLD_BLUE))
            
            for monster in monsters:
                realm_info = get_realm_info(monster.get('realm_level', 0))
                realm_name = realm_info.name if realm_info else "凡人"
                print(f"\n  {colorize('•', Color.BOLD_RED)} {monster.get('name', '未知')}")
                print(f"    类型: {monster.get('monster_type', '未知')}")
                print(f"    修为: {realm_name}")
                print(f"    描述: {monster.get('description', '无')[:40]}...")
                if monster.get('weakness'):
                    print(f"    弱点: {monster.get('weakness')}")
            
            print(colorize("─" * 50, Color.BOLD_BLUE))
            print(f"{colorize('💡', Color.BOLD_YELLOW)} 共 {len(monsters)} 只妖兽")
            
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 获取妖兽列表失败: {e}")
    
    def _handle_new_character(self):
        """处理新建角色命令"""
        # 保存当前角色
        if self.player and self.game_mode:
            if self.save_player():
                print(f"\n{colorize('💾', Color.BOLD_CYAN)} 已保存当前角色：{self.player.stats.name}")
        
        # 创建新角色
        print(f"\n{colorize('🎮', Color.BOLD_GREEN)} 创建新角色！")
        
        # 输入角色名称
        name = input(f"{colorize('请输入角色名称:', Color.BOLD_CYAN)} ").strip()
        if not name:
            name = "道友"
        
        # 创建新玩家
        self.player = Player(name=name, load_from_db=False)
        
        # 重新初始化游戏系统
        self.cultivation_system = CultivationSystem(self.player)
        
        print(f"\n{colorize('✅', Color.BOLD_GREEN)} 新角色创建成功！")
        print(f"  名称: {self.player.stats.name}")
        print(f"  灵根: {self.player.stats.spirit_root}")
        print(f"  寿元: {self.player.stats.lifespan}年")
    
    def _handle_load_character(self, character_name: str):
        """处理加载角色命令"""
        if not character_name:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 请指定要加载的角色名称")
            print(f"  可用命令: /加载 <角色名>")
            print(f"  使用 /角色列表 查看所有角色")
            return
        
        # 保存当前角色
        if self.player and self.game_mode:
            if self.save_player():
                print(f"\n{colorize('💾', Color.BOLD_CYAN)} 已保存当前角色")
        
        # 加载指定角色
        try:
            from storage.database import Database
            db = Database()
            data = db.load_player(character_name)
            db.close()
            
            if data:
                self.player = Player(name="道友", load_from_db=False)
                self.player.from_dict(data)
                self.cultivation_system = CultivationSystem(self.player)
                
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 成功加载角色：{self.player.stats.name}")
                print(f"  当前境界: {self.player.get_realm_name()}")
                print(f"  当前年龄: {self.player.stats.age}岁")
            else:
                print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 未找到角色：{character_name}")
                print(f"  使用 /角色列表 查看所有角色")
                
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 加载角色失败：{e}")
    
    def _handle_list_characters(self):
        """处理角色列表命令"""
        try:
            from storage.database import Database
            db = Database()
            players = db.list_players()
            db.close()
            
            if not players:
                print(f"\n{colorize('📋', Color.BOLD_CYAN)} 暂无角色")
                print(f"  使用 /新建角色 创建新角色")
                return
            
            print(f"\n{colorize('📋 角色列表', Color.BOLD_CYAN)}")
            print(colorize("─" * 50, Color.BOLD_BLUE))
            
            for i, p in enumerate(players, 1):
                current = " 👈 当前" if self.player and p['name'] == self.player.stats.name else ""
                print(f"  {i}. {p['name']}{current}")
                print(f"     创建时间: {p['created_at'][:10]}")
                print(f"     最后更新: {p['updated_at'][:10]}")
            
            print(colorize("─" * 50, Color.BOLD_BLUE))
            print(f"{colorize('💡', Color.BOLD_YELLOW)} 使用 /加载 <角色名> 切换角色")
            
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 获取角色列表失败：{e}")
    
    def _check_random_event(self):
        """检查随机事件"""
        if not self.event_system or not self.player:
            return
        
        player_stats = {
            "realm_level": self.player.stats.realm_level,
            "fortune": self.player.stats.fortune,
            "karma": self.player.stats.karma,
            "location": self.player.stats.location,
            "spirit_stones": self.player.stats.spirit_stones,
        }
        
        event = self.event_system.check_random_event(player_stats)
        if event:
            print(f"\n{colorize('⚡ 突发事件', Color.BOLD_YELLOW)}")
            print(f"【{event.name}】")
            print(f"{event.description}")
            
            if event.choices:
                print(f"\n{colorize('选择:', Color.BOLD_CYAN)}")
                for i, choice in enumerate(event.choices):
                    print(f"  {i+1}. {choice['text']}")
                # 简化处理，自动选择第一个
                effects = self.event_system.apply_event_effects(event, 0)
                print(f"\n{colorize('结果:', Color.BOLD_GREEN)} 你选择了{event.choices[0]['text']}")
            
            self.event_system.record_event(event.id)

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
            "admin": "/admin",
            "gm": "/gm",
            # 英文命令
            "explore": "/探索",
            "generate": "/生成",
            "monsters": "/妖兽",
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
                print(f"\n{colorize('📭', Color.BOLD_YELLOW)}  {dim('当前没有记忆')}")
                return

            # 使用颜色显示标题
            print(f"\n{colorize('─' * 60, Color.BOLD_BLUE)}")
            print(f"  {colorize('📚', Color.BOLD_YELLOW)}  {bold('当前记忆列表')}")
            print(f"{colorize('─' * 60, Color.BOLD_BLUE)}")

            for idx, memory in enumerate(memories, 1):
                content = memory.get("content", "") if isinstance(memory, dict) else str(memory)
                content = content[:50] + "..." if len(content) > 50 else content
                
                # 根据来源使用不同颜色
                source = memory.get("source", "unknown") if isinstance(memory, dict) else "unknown"
                if source == "user":
                    source_icon = colorize("👤", Color.BOLD_GREEN)
                    content_colored = green(content)
                elif source == "ai":
                    source_icon = colorize("🤖", Color.BOLD_CYAN)
                    content_colored = cyan(content)
                else:
                    source_icon = colorize("📄", Color.DIM)
                    content_colored = dim(content)
                
                # 显示序号和来源图标
                idx_colored = colorize(f"{idx:3d}.", Color.BOLD_BLUE)
                print(f"  {idx_colored} {source_icon} {content_colored}")

            print(f"{colorize('─' * 60, Color.BOLD_BLUE)}")
            print(f"  {dim(f'共 {len(memories)} 条记忆')}  {dim('(使用 /stats 查看统计)')}")
            
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

            # 使用颜色显示统计信息
            print(f"\n{colorize('─' * 60, Color.BOLD_MAGENTA)}")
            print(f"  {colorize('📊', Color.BOLD_YELLOW)}  {bold('记忆统计信息')}")
            print(f"{colorize('─' * 60, Color.BOLD_MAGENTA)}")
            print(f"  {colorize('📦', Color.BOLD_BLUE)}  总记忆数:     {bold(str(total_memories))}")
            print(f"  {colorize('👤', Color.BOLD_GREEN)}  用户消息:     {green(str(user_memories))}")
            print(f"  {colorize('🤖', Color.BOLD_CYAN)}  AI 回复:      {cyan(str(ai_memories))}")
            if other_memories > 0:
                print(f"  {colorize('📄', Color.DIM)}  其他来源:     {dim(str(other_memories))}")
            print(f"{colorize('─' * 60, Color.BOLD_MAGENTA)}")
            
            self.logger.info(f"显示统计信息: 总计={total_memories}, 用户={user_memories}, AI={ai_memories}")

        except Exception as e:
            error_msg = f"获取统计信息失败: {e}"
            print(f"\n{colorize('❌', Color.BOLD_RED)} {error(error_msg)}")
            self.logger.exception("获取统计信息失败")
    
    # ==================== 管理员命令 ====================
    
    def _handle_admin_command(self, args: str):
        """
        处理管理员命令
        
        可用命令:
        - /admin exp <数值>    - 增加修为
        - /admin sp <数值>     - 增加法力
        - /admin stones <数值> - 增加灵石
        - /admin item <名称> [数量] - 添加道具
        - /admin realm <等级>  - 设置境界(0-8)
        - /admin age <数值>    - 设置年龄
        - /admin lifespan <数值> - 设置寿元
        - /admin heal          - 恢复满状态
        - /admin max           - 满状态（修为、法力、生命）
        """
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not args:
            self._display_admin_help()
            return
        
        parts = args.split()
        cmd = parts[0].lower()
        
        try:
            if cmd == "exp" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.add_exp(amount)
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 修为 +{amount}")
                print(f"  当前修为: {self.player.stats.exp}/{self.player.get_exp_needed()}")
                
            elif cmd == "sp" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.stats.spiritual_power = min(
                    self.player.stats.max_spiritual_power,
                    self.player.stats.spiritual_power + amount
                )
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 法力 +{amount}")
                print(f"  当前法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                
            elif cmd == "stones" and len(parts) >= 2:
                amount = int(parts[1])
                self.player.stats.spirit_stones += amount
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 灵石 +{amount}")
                print(f"  当前灵石: {self.player.stats.spirit_stones}")
                
            elif cmd == "item":
                if len(parts) < 2:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 用法: /admin item <道具名> [数量]")
                    return
                # 支持带空格的道具名（用引号或直到数字前）
                # 例如: /admin item 罕见的回春丹 12
                # 或: /admin item "罕见的回春丹" 12
                remaining = ' '.join(parts[1:])
                # 尝试解析数量
                count = 1
                item_name = remaining
                # 如果最后一部分是数字，则作为数量
                if parts[-1].isdigit():
                    count = int(parts[-1])
                    item_name = ' '.join(parts[1:-1])
                
                success, msg = self.player.add_item(item_name, count)
                if success:
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} {msg}")
                else:
                    print(f"\n{colorize('❌', Color.BOLD_RED)} {msg}")
                    
            elif cmd == "realm" and len(parts) >= 2:
                level = int(parts[1])
                if 0 <= level <= 8:
                    self.player.stats.realm_level = level
                    realm_info = get_realm_info(level)
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 境界已设置为: {realm_info.name if realm_info else '未知'}")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 境界等级必须在 0-8 之间")
                    
            elif cmd == "age" and len(parts) >= 2:
                age = int(parts[1])
                self.player.stats.age = age
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 年龄已设置为: {age}岁")
                
            elif cmd == "lifespan" and len(parts) >= 2:
                lifespan = int(parts[1])
                self.player.stats.lifespan = lifespan
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 寿元已设置为: {lifespan}年")
                
            elif cmd == "heal":
                self.player.stats.health = 100
                self.player.stats.spiritual_power = self.player.stats.max_spiritual_power
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 状态已恢复满")
                print(f"  生命: 100/100")
                print(f"  法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                
            elif cmd == "max":
                # 满状态
                self.player.stats.health = 100
                self.player.stats.spiritual_power = self.player.stats.max_spiritual_power
                # 满修为
                exp_needed = self.player.get_exp_needed()
                self.player.add_exp(exp_needed)
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 已设置为满状态")
                print(f"  生命: 100/100")
                print(f"  法力: {self.player.stats.spiritual_power}/{self.player.stats.max_spiritual_power}")
                print(f"  修为: 已满，可以突破！")
                
            elif cmd == "help" or cmd == "?":
                self._display_admin_help()
                
            else:
                print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 未知的管理员命令: {cmd}")
                self._display_admin_help()
                
        except ValueError:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 参数必须是数字")
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 执行命令时出错: {e}")
    
    def _display_admin_help(self):
        """显示管理员命令帮助"""
        print(f"\n{colorize('═' * 60, Color.BOLD_RED)}")
        print(f"  {colorize('👑', Color.BOLD_YELLOW)}  {bold('管理员命令')}")
        print(f"{colorize('═' * 60, Color.BOLD_RED)}")
        print(f"  {colorize('/admin exp <数值>', Color.BOLD_CYAN)}    - 增加修为")
        print(f"  {colorize('/admin sp <数值>', Color.BOLD_CYAN)}     - 增加法力")
        print(f"  {colorize('/admin stones <数值>', Color.BOLD_CYAN)} - 增加灵石")
        print(f"  {colorize('/admin item <名称> [数量]', Color.BOLD_CYAN)} - 添加道具")
        print(f"  {colorize('/admin realm <等级>', Color.BOLD_CYAN)}  - 设置境界(0-8)")
        print(f"  {colorize('/admin age <数值>', Color.BOLD_CYAN)}    - 设置年龄")
        print(f"  {colorize('/admin lifespan <数值>', Color.BOLD_CYAN)} - 设置寿元")
        print(f"  {colorize('/admin heal', Color.BOLD_CYAN)}          - 恢复满状态")
        print(f"  {colorize('/admin max', Color.BOLD_CYAN)}           - 满状态（修为、法力、生命）")
        print(f"  {colorize('/admin help', Color.BOLD_CYAN)}          - 显示此帮助")
        print(f"{colorize('═' * 60, Color.BOLD_RED)}")
    
    def _handle_gm_command(self, args: str):
        """
        处理GM命令（游戏管理命令）
        
        可用命令:
        - /gm npc <数量>              - 在当前地点生成NPC
        - /gm monster <数量>          - 在当前地点生成妖兽
        - /gm item <数量>             - 生成随机道具
        - /gm clear                   - 清空背包
        - /gm save                    - 强制保存游戏
        - /gm time <天数>             - 推进时间
        - /gm location <地点>         - 瞬移到指定地点
        - /gm list locations          - 列出所有地点
        - /gm map [数量] [名字] [境界] - 生成新地图
        - /gm refresh                 - 强制刷新NPC独立系统
        """
        if not self.player:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 玩家未初始化")
            return
        
        if not args:
            self._display_gm_help()
            return
        
        parts = args.split()
        cmd = parts[0].lower()
        
        try:
            if cmd == "npc":
                count = int(parts[1]) if len(parts) >= 2 else 1
                if self.world:
                    npcs = self.world.npc_manager.generate_npcs_for_location(
                        self.player.stats.location, count
                    )
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 已生成 {len(npcs)} 个NPC")
                    
                    # 保存到数据库
                    from storage.database import Database
                    db = Database()
                    for npc in npcs:
                        print(f"  • {npc.data.dao_name}")
                        # 转换为字典并保存
                        npc_dict = npc.to_dict()
                        db.save_generated_npc(npc_dict)
                    db.close()
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "monster":
                count = int(parts[1]) if len(parts) >= 2 else 1
                if self.world:
                    from game.generator import InfiniteGenerator
                    generator = InfiniteGenerator(use_llm=False)
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 已生成 {count} 只妖兽:")
                    
                    # 保存到数据库
                    from storage.database import Database
                    db = Database()
                    
                    for i in range(count):
                        monster = generator.generate_monster(
                            level=self.player.stats.realm_level,
                            location=self.player.stats.location
                        )
                        print(f"  • {monster.name} (Lv.{monster.level})")
                        # 保存妖兽到数据库
                        monster_dict = {
                            'id': getattr(monster, 'id', str(uuid.uuid4())),
                            'name': monster.name,
                            'monster_type': getattr(monster, 'monster_type', '普通'),
                            'level': monster.level,
                            'realm_level': getattr(monster, 'realm_level', self.player.stats.realm_level),
                            'location': self.player.stats.location,
                            'description': getattr(monster, 'description', ''),
                            'attributes': getattr(monster, 'attributes', {}),
                            'skills': getattr(monster, 'skills', []),
                            'drops': getattr(monster, 'drops', [])
                        }
                        db.save_generated_monster(monster_dict)
                    
                    db.close()
                    print(f"\n{colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "item":
                count = int(parts[1]) if len(parts) >= 2 else 1
                from game.generator import InfiniteGenerator
                generator = InfiniteGenerator(use_llm=False)
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 已生成 {count} 件道具:")
                
                # 保存到数据库
                from storage.database import Database
                import uuid
                db = Database()
                
                for i in range(count):
                    item = generator.generate_item()
                    # 添加到背包
                    item_data = {
                        "name": item.name,
                        "description": getattr(item, 'description', f'这是一件{item.rarity.value}的{item.item_type.value}'),
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "effects": list(getattr(item, 'effects', {}).keys()) if hasattr(item, 'effects') else [],
                        "value": getattr(item, 'attributes', {}).get('power', 100) * 10,
                        "stackable": True,
                        "max_stack": 99,
                        "usable": True,
                        "level_required": 0,
                        "origin": "GM生成"
                    }
                    self.player.inventory.add_generated_item(item.name, item_data, 1)
                    print(f"  • {item.name}")
                    
                    # 保存道具到数据库
                    item_dict = {
                        'id': str(uuid.uuid4()),
                        'name': item.name,
                        'item_type': item.item_type.value,
                        'rarity': item.rarity.value,
                        'description': getattr(item, 'description', ''),
                        'attributes': getattr(item, 'attributes', {}),
                        'effects': list(getattr(item, 'effects', {}).keys()) if hasattr(item, 'effects') else [],
                        'value': getattr(item, 'attributes', {}).get('power', 100) * 10,
                        'level_required': 0
                    }
                    db.save_generated_item(item_dict)
                
                db.close()
                print(f"\n{colorize('💾', Color.BOLD_CYAN)} 已保存到数据库")
                    
            elif cmd == "clear":
                self.player.inventory.items.clear()
                self.player.inventory.generated_items.clear()
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 背包已清空")
                
            elif cmd == "save":
                if self.save_player():
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 游戏已保存")
                else:
                    print(f"\n{colorize('❌', Color.BOLD_RED)} 保存失败")
                    
            elif cmd == "time" and len(parts) >= 2:
                days = int(parts[1])
                self.player.advance_time(days)
                print(f"\n{colorize('✅', Color.BOLD_GREEN)} 时间已推进 {days} 天")
                print(f"  当前年龄: {self.player.stats.age}岁")
                
            elif cmd == "location":
                if len(parts) < 2:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 用法: /gm location <地点名>")
                    return
                location_name = parts[1]
                if self.world and location_name in self.world.locations:
                    self.player.stats.location = location_name
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 已瞬移到: {location_name}")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 地点不存在: {location_name}")
                    print(f"  使用 /gm list locations 查看所有地点")
                    
            elif cmd == "list" and len(parts) >= 2 and parts[1].lower() == "locations":
                if self.world:
                    print(f"\n{colorize('📍 可用地点列表', Color.BOLD_CYAN)}")
                    print(colorize("─" * 50, Color.BOLD_BLUE))
                    for loc_name in self.world.locations.keys():
                        current = " 👈 当前" if loc_name == self.player.stats.location else ""
                        print(f"  • {loc_name}{current}")
                    print(colorize("─" * 50, Color.BOLD_BLUE))
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "map":
                # 解析参数: /gm map [数量] [名字] [境界等级]
                # 例如: /gm map 1 幽冥山谷 3
                # 或: /gm map 3 (生成3个随机地图)
                count = 1
                custom_name = None
                realm_level = None
                
                if len(parts) >= 2:
                    # 检查第一个参数是否是数字（数量）
                    if parts[1].isdigit():
                        count = int(parts[1])
                        # 剩余部分可能是名字和境界
                        if len(parts) >= 3:
                            # 检查最后一部分是否是数字（境界）
                            if parts[-1].isdigit() and len(parts) > 2:
                                realm_level = int(parts[-1])
                                # 中间部分是名字
                                if len(parts) > 3:
                                    custom_name = ' '.join(parts[2:-1])
                            else:
                                # 没有指定境界，剩余部分是名字
                                custom_name = ' '.join(parts[2:])
                    else:
                        # 第一个参数不是数字，视为名字
                        custom_name = parts[1]
                        if len(parts) >= 3 and parts[-1].isdigit():
                            realm_level = int(parts[-1])
                
                if self.world:
                    from game.generator import InfiniteGenerator
                    generator = InfiniteGenerator(use_llm=False)
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 正在生成 {count} 个新地图...")
                    if custom_name:
                        print(f"  自定义名称: {custom_name}")
                    if realm_level is not None:
                        realm_info = get_realm_info(realm_level)
                        print(f"  境界限制: {realm_info.name if realm_info else '未知'}")
                    
                    for i in range(count):
                        # 生成地图
                        from game.generator import MapType
                        new_map = generator.generate_map(
                            target_level=realm_level if realm_level is not None else self.player.stats.realm_level
                        )
                        
                        if new_map:
                            # 如果指定了自定义名字，替换生成的名字
                            if custom_name:
                                if count > 1:
                                    new_map.name = f"{custom_name}{i+1}"
                                else:
                                    new_map.name = custom_name
                            
                            # 如果指定了境界限制，设置进入要求
                            if realm_level is not None:
                                new_map.level = realm_level
                                # 更新描述中的境界要求
                                realm_info = get_realm_info(realm_level)
                                if realm_info:
                                    new_map.description = f"[{realm_info.name}以上可进入] {new_map.description}"
                            
                            # 添加到世界连接
                            if self.player.stats.location not in new_map.connections:
                                new_map.connections.append(self.player.stats.location)
                            
                            # 保存到数据库
                            from storage.database import Database
                            db = Database()
                            db.save_generated_map(new_map.to_dict())
                            db.close()
                            
                            # 显示信息
                            realm_req = ""
                            if new_map.level is not None:
                                req_realm = get_realm_info(new_map.level)
                                if req_realm:
                                    realm_req = f" [需{req_realm.name}]"
                            print(f"  • {new_map.name} ({new_map.map_type.value}){realm_req}")
                    
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} 地图生成完成！")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "refresh" or cmd == "refreshnpc":
                if self.world:
                    print(f"\n{colorize('🔄', Color.BOLD_CYAN)} 正在强制刷新NPC独立系统...")
                    # 更新所有NPC
                    import time
                    current_time = time.time()
                    updated_count = 0
                    for npc_id, npc in self.world.npc_manager.npcs.items():
                        if npc.independent.update(current_time, player_nearby=True):
                            updated_count += 1
                    
                    stats = self.world.get_npc_stats()
                    print(f"\n{colorize('✅', Color.BOLD_GREEN)} NPC独立系统已刷新")
                    print(f"  总NPC数: {stats.get('total_npcs', 0)}")
                    print(f"  活跃NPC数: {stats.get('active_npcs', 0)}")
                    print(f"  本轮更新: {updated_count}")
                    print(f"  总记忆数: {stats.get('total_memories', 0)}")
                    print(f"  总关系数: {stats.get('total_relationships', 0)}")
                    print(f"  总行动数: {stats.get('total_actions', 0)}")
                else:
                    print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 世界系统未初始化")
                    
            elif cmd == "help" or cmd == "?":
                self._display_gm_help()
                
            else:
                print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 未知的GM命令: {cmd}")
                self._display_gm_help()
                
        except ValueError:
            print(f"\n{colorize('⚠️', Color.BOLD_YELLOW)} 参数必须是数字")
        except Exception as e:
            print(f"\n{colorize('❌', Color.BOLD_RED)} 执行命令时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _display_gm_help(self):
        """显示GM命令帮助"""
        print(f"\n{colorize('═' * 60, Color.BOLD_MAGENTA)}")
        print(f"  {colorize('🎮', Color.BOLD_YELLOW)}  {bold('GM命令')}")
        print(f"{colorize('═' * 60, Color.BOLD_MAGENTA)}")
        print(f"  {colorize('/gm npc <数量>', Color.BOLD_CYAN)}       - 在当前地点生成NPC")
        print(f"  {colorize('/gm monster <数量>', Color.BOLD_CYAN)}  - 在当前地点生成妖兽")
        print(f"  {colorize('/gm item <数量>', Color.BOLD_CYAN)}     - 生成随机道具")
        print(f"  {colorize('/gm clear', Color.BOLD_CYAN)}          - 清空背包")
        print(f"  {colorize('/gm save', Color.BOLD_CYAN)}           - 强制保存游戏")
        print(f"  {colorize('/gm time <天数>', Color.BOLD_CYAN)}    - 推进时间")
        print(f"  {colorize('/gm location <地点>', Color.BOLD_CYAN)} - 瞬移到指定地点")
        print(f"  {colorize('/gm list locations', Color.BOLD_CYAN)} - 列出所有地点")
        print(f"  {colorize('/gm map [数量] [名字] [境界]', Color.BOLD_CYAN)} - 生成新地图")
        print(f"  {colorize('/gm refresh', Color.BOLD_CYAN)}        - 强制刷新NPC独立系统")
        print(f"  {colorize('/gm help', Color.BOLD_CYAN)}           - 显示此帮助")
        print(f"{colorize('═' * 60, Color.BOLD_MAGENTA)}")

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
