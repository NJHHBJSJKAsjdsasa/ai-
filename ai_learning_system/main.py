#!/usr/bin/env python3
"""
AI 学习系统 - 程序入口

这是一个智能对话和记忆管理平台的主入口模块。
支持 CLI 和 GUI 两种界面模式。
"""

import argparse
import signal
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from interface.cli import CLI
from interface.gui import MainWindow
from core.dialogue_engine import DialogueEngine
from core.selector import Selector
from utils.privacy_detector import PrivacyDetector
from core.memory import MemoryManager as FullMemoryManager
from utils.colors import colorize, Color


class MemoryManager:
    """
    记忆管理器包装类
    
    包装完整的 MemoryManager，提供兼容性接口。
    """

    def __init__(self, database: Database):
        """
        初始化记忆管理器

        Args:
            database: Database 实例
        """
        # 初始化数据库表
        database.init_tables()
        
        # 初始化完整记忆管理器所需的依赖
        selector = Selector()
        privacy_detector = PrivacyDetector()
        
        # 创建完整的记忆管理器实例
        self._memory_manager = FullMemoryManager(database, selector, privacy_detector)

    def add_memory(self, content: str, source: str = "user", **kwargs) -> dict:
        """
        添加新记忆

        Args:
            content: 记忆内容
            source: 记忆来源 (user/ai)
            **kwargs: 其他可选参数

        Returns:
            创建的记忆数据字典
        """
        result = self._memory_manager.add_memory(content, source)
        
        # 转换为兼容的返回格式
        if result.get('success'):
            return {
                'id': result.get('memory_id'),
                'content': content,
                'category': kwargs.get('category', 'conversation'),
                'importance': result.get('importance', 5),
                'source': source,
                'is_encrypted': result.get('is_encrypted', False),
                'risk_level': result.get('risk_level', 'none')
            }
        else:
            # 如果记忆被拒绝（重要性不足），仍然返回基本信息
            return {
                'id': None,
                'content': content,
                'category': kwargs.get('category', 'conversation'),
                'importance': result.get('importance', 1),
                'source': source,
                'rejected': True,
                'message': result.get('message', '记忆被拒绝')
            }

    def get_all_memories(self) -> list:
        """
        获取所有记忆

        Returns:
            记忆列表
        """
        memories = self._memory_manager.get_all_memories()
        return [
            {
                'id': m.id,
                'content': m.content,
                'category': m.category if hasattr(m, 'category') else 'conversation',
                'importance': m.importance,
                'created_at': m.created_at if hasattr(m, 'created_at') else None,
                'source': m.source
            }
            for m in memories
        ]

    def get_memory(self, memory_id: int) -> dict:
        """
        根据 ID 获取记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            记忆数据字典，如果不存在返回 None
        """
        memory = self._memory_manager.get_memory(memory_id)
        if memory is None:
            return None
        return {
            'id': memory.id,
            'content': memory.content,
            'category': getattr(memory, 'category', 'conversation'),
            'importance': memory.importance,
            'created_at': getattr(memory, 'created_at', None),
            'source': memory.source
        }

    def search_memories(self, keyword: str = None, **kwargs) -> list:
        """
        搜索记忆

        Args:
            keyword: 搜索关键词
            **kwargs: 其他搜索条件

        Returns:
            匹配的记忆列表
        """
        memories = self._memory_manager.search_memories(keyword)
        return [
            {
                'id': m.id,
                'content': m.content,
                'category': getattr(m, 'category', 'conversation'),
                'importance': m.importance,
                'source': m.source
            }
            for m in memories
        ]

    def get_recent_dialogue(self, limit: int = 10) -> list:
        """获取最近的对话记录"""
        return self._memory_manager.get_recent_dialogue(limit)

    def save_dialogue(self, user_message: str, ai_response: str) -> None:
        """保存对话记录"""
        self._memory_manager.save_dialogue(user_message, ai_response)

    def search_related_memory(self, query: str) -> list:
        """搜索相关记忆"""
        return self._memory_manager.search_related_memory(query)

    def get_user_preferences(self) -> dict:
        """获取用户偏好"""
        return self._memory_manager.get_user_preferences()


class AILearningSystem:
    """
    AI 学习系统主类

    负责协调数据库、记忆管理器和 CLI 界面，提供统一的系统入口。
    """

    def __init__(self):
        """初始化 AI 学习系统"""
        self.db: Database = None
        self.memory_manager: MemoryManager = None
        self.dialogue_engine = None
        self.cli: CLI = None
        self._shutdown_requested = False

    def run(self):
        """
        启动 AI 学习系统

        初始化所有组件并启动 CLI 界面。
        """
        try:
            self._initialize()
            self._setup_signal_handlers()
            self._start_cli()
        except Exception as e:
            print(f"\n❌ 系统启动失败: {e}")
            sys.exit(1)
        finally:
            self.cleanup()

    def _initialize(self):
        """初始化系统组件"""
        print("🚀 正在初始化 AI 学习系统...")

        # 初始化数据库
        self.db = Database()

        # 初始化记忆管理器
        self.memory_manager = MemoryManager(self.db)

        # 初始化对话引擎
        dialogue_engine = DialogueEngine(self.memory_manager)

        # 尝试自动加载 models/ 目录下的模型（如果有）
        # 首先检查项目目录下的 models/
        models_dir = project_root / "models"
        # 如果没有，检查父目录下的 models/
        if not models_dir.exists():
            models_dir = project_root.parent / "models"
        
        if models_dir.exists():
            model_files = list(models_dir.glob("*.gguf")) + list(models_dir.glob("*.bin")) + list(models_dir.glob("*.pt"))
            if model_files:
                try:
                    print(f"📦 发现 {len(model_files)} 个模型文件，正在加载...")
                    dialogue_engine.load_model(str(model_files[0]))
                    print(f"✅ 已加载模型: {model_files[0].name}")
                except Exception as e:
                    print(f"⚠️  模型加载失败: {e}")
            else:
                print("ℹ️  models/ 目录下未找到模型文件")
        else:
            print("ℹ️  models/ 目录不存在，跳过模型加载")

        self.dialogue_engine = dialogue_engine

        # 初始化 CLI
        self.cli = CLI(self.memory_manager, self.dialogue_engine)

        print("✅ 系统初始化完成")

    def _setup_signal_handlers(self):
        """设置信号处理器，支持优雅退出"""
        # 处理 Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Windows 平台也支持 SIGTERM
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """
        信号处理器 - 忽略 Ctrl+C，只能通过 /退出游戏 或 /quit 退出

        Args:
            signum: 信号编号
            frame: 当前栈帧
        """
        # 忽略 Ctrl+C 信号，打印提示信息
        print(f"\n{colorize('💡 提示：使用 /退出游戏 或 /quit 命令退出', Color.BOLD_YELLOW)}")
        # 不设置 running = False，程序继续运行

    def _start_cli(self):
        """启动 CLI 界面"""
        if self.cli:
            self.cli.start()

    def cleanup(self):
        """清理系统资源"""
        if self._shutdown_requested:
            return

        self._shutdown_requested = True
        print("🧹 正在清理资源...")

        # 关闭数据库连接
        if self.db:
            self.db.close()
            print("✅ 数据库连接已关闭")

        print("👋 系统已安全关闭")


def main():
    """
    程序入口点

    解析命令行参数，创建 AILearningSystem 实例并运行。
    """
    parser = argparse.ArgumentParser(
        description="AI 学习系统 - 支持 CLI 和 GUI 两种界面模式"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="使用命令行界面 (CLI) 模式"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="使用图形界面 (GUI) 模式"
    )

    args = parser.parse_args()

    # 默认使用 CLI 模式，除非显式指定 --gui
    if args.gui:
        # GUI 模式
        print("🚀 启动 GUI 模式...")
        try:
            # 创建游戏实例（简化版）
            game_instance = GameInstance()
            # 启动 GUI
            window = MainWindow(game_instance)
            window.run()
        except Exception as e:
            print(f"❌ GUI 启动失败: {e}")
            sys.exit(1)
    else:
        # CLI 模式（默认）
        system = AILearningSystem()
        system.run()


class GameInstance:
    """
    游戏实例类

    为 GUI 提供游戏数据和操作接口。使用真实的游戏系统类。
    """

    def __init__(self):
        """初始化游戏实例"""
        # 初始化数据库
        self.db = Database()
        self.db.init_tables()

        # 初始化玩家数据（使用真实的 Player 类）
        from game.player import Player
        self.player = Player(name="修仙者", load_from_db=False)

        # 初始化世界（使用真实的 World 类）
        from game.world import World
        self.world = World(db=self.db)

        # 初始化 NPC 管理器（使用真实的 NPCManager 类）
        self.npc_manager = self.world.npc_manager

        # 初始化世界演化管理器
        self.world_evolution_manager = self.world.world_evolution_manager

        # 初始化成就管理器
        from game.achievement_system import create_achievement_manager
        self.achievement_manager = create_achievement_manager(self.db)

        # 游戏时间
        self.game_time = {"year": 1, "month": 1, "day": 1}

        # 设置玩家初始位置
        self.player.stats.location = "新手村"

        # 为初始位置生成 NPC
        self.npc_manager.generate_npcs_for_location("新手村", count=3)

    def save(self):
        """保存游戏"""
        try:
            # 保存玩家数据
            self.player.save_to_db(self.db)
            self.log("游戏已保存", "system")
        except Exception as e:
            self.log(f"保存失败: {e}", "system")

    def load(self):
        """加载游戏"""
        try:
            # 加载玩家数据
            self.player.load_from_db(self.db)
            self.log("游戏已加载", "system")
        except Exception as e:
            self.log(f"加载失败: {e}", "system")

    def log(self, message, log_type="system"):
        """添加日志（会被 GUI 重写）"""
        print(f"[{log_type}] {message}")

    def update(self, dt: float = 1.0):
        """
        更新游戏状态

        Args:
            dt: 时间间隔（天）
        """
        # 更新游戏时间
        self.game_time["day"] += int(dt)
        if self.game_time["day"] > 30:
            self.game_time["day"] = 1
            self.game_time["month"] += 1
        if self.game_time["month"] > 12:
            self.game_time["month"] = 1
            self.game_time["year"] += 1

        # 更新世界演化系统
        if hasattr(self, 'world_evolution_manager'):
            self.world_evolution_manager.update(
                self.game_time,
                npc_manager=self.npc_manager,
                player=self.player
            )

    def advance_time(self, days: int = 1):
        """
        推进游戏时间

        Args:
            days: 推进天数
        """
        for _ in range(days):
            self.update(1.0)


if __name__ == "__main__":
    main()
