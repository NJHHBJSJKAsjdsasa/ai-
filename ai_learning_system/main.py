#!/usr/bin/env python3
"""
AI 学习系统 - 程序入口

这是一个智能对话和记忆管理平台的主入口模块。
"""

import signal
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from interface.cli import CLI
from core.dialogue_engine import DialogueEngine


class MemoryManager:
    """
    记忆管理器占位类

    这是一个简化版的记忆管理器，用于在核心记忆类完成之前提供基本功能。
    它直接与数据库交互，提供记忆的增删改查功能。
    """

    def __init__(self, database: Database):
        """
        初始化记忆管理器

        Args:
            database: Database 实例
        """
        self.db = database
        # 初始化数据库表
        self.db.init_tables()

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
        memory_data = {
            'content': content,
            'category': kwargs.get('category', 'conversation'),
            'importance': kwargs.get('importance', 5),
            'source': source
        }

        memory = self.db.create_memory(memory_data)
        return {
            'id': memory.id,
            'content': memory.content,
            'category': memory.category,
            'importance': memory.importance,
            'source': source
        }

    def get_all_memories(self) -> list:
        """
        获取所有记忆

        Returns:
            记忆列表
        """
        memories = self.db.get_all_memories()
        return [
            {
                'id': m.id,
                'content': m.content,
                'category': m.category,
                'importance': m.importance,
                'created_at': m.created_at
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
        memory = self.db.get_memory(memory_id)
        if memory is None:
            return None
        return {
            'id': memory.id,
            'content': memory.content,
            'category': memory.category,
            'importance': memory.importance,
            'created_at': memory.created_at
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
        memories = self.db.search_memories(keyword=keyword, **kwargs)
        return [
            {
                'id': m.id,
                'content': m.content,
                'category': m.category,
                'importance': m.importance
            }
            for m in memories
        ]

    def get_recent_dialogue(self, limit: int = 10) -> list:
        """获取最近的对话记录"""
        memories = self.db.get_all_memories(limit=limit)
        dialogue = []
        for memory in memories:
            role = "user" if memory.source == "user" else "assistant"
            dialogue.append({
                "role": role,
                "content": memory.content
            })
        return dialogue

    def save_dialogue(self, user_message: str, ai_response: str) -> None:
        """保存对话记录"""
        # AI回复已经在process_message中保存，这里不需要重复保存
        pass

    def search_related_memory(self, query: str) -> list:
        """搜索相关记忆"""
        memories = self.search_memories(keyword=query)
        return [{"content": m['content'], "source": m.get('source', 'unknown')} for m in memories]

    def get_user_preferences(self) -> dict:
        """获取用户偏好"""
        import re
        preferences = {}
        memories = self.get_all_memories()

        for memory in memories:
            content = memory.get('content', '')
            # 提取用户名字
            if "我叫" in content or "我的名字是" in content:
                match = re.search(r"(?:我叫|我的名字是)([^，。,.]+)", content)
                if match:
                    preferences["name"] = match.group(1).strip()
            # 提取AI名字（用户给AI起的名字）- 排除疑问句
            is_setting_name = ("你叫" in content or "你的名字是" in content or "你现在叫" in content)
            is_question = any(q in content for q in ["什么", "谁", "吗", "？", "?"])
            if is_setting_name and not is_question:
                match = re.search(r"(?:你叫|你的名字是|你现在叫)([^，。,.]+)", content)
                if match:
                    extracted_name = match.group(1).strip()
                    # 验证提取的名字不是疑问词
                    if extracted_name not in ["什么", "谁", "什么名字"]:
                        preferences["ai_name"] = extracted_name
            # 提取喜好
            if "喜欢" in content:
                match = re.search(r"喜欢(.+?)(?:，|。|$)", content)
                if match:
                    preferences.setdefault("likes", []).append(match.group(1).strip())
            # 提取不喜欢
            if "讨厌" in content or "不喜欢" in content:
                match = re.search(r"(?:讨厌|不喜欢)(.+?)(?:，|。|$)", content)
                if match:
                    preferences.setdefault("dislikes", []).append(match.group(1).strip())

        return preferences


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
        信号处理器

        Args:
            signum: 信号编号
            frame: 当前栈帧
        """
        signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
        print(f"\n\n⚠️  接收到信号 {signal_name}，正在优雅退出...")
        self._shutdown_requested = True
        self.cleanup()
        sys.exit(0)

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

    创建 AILearningSystem 实例并运行。
    """
    system = AILearningSystem()
    system.run()


if __name__ == "__main__":
    main()
