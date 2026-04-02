import sys
import re
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.database import Database
from storage.models import Memory
from core.selector import Selector
from utils.privacy_detector import PrivacyDetector


class MemoryManager:
    """记忆核心类，负责管理记忆的增删改查和生命周期"""

    def __init__(self, database: Database, selector: Selector, privacy_detector: PrivacyDetector):
        """
        初始化记忆管理器

        Args:
            database: 数据库实例
            selector: 选择器实例，用于评估记忆重要性
            privacy_detector: 隐私检测器实例
        """
        self.database = database
        self.selector = selector
        self.privacy_detector = privacy_detector

    def add_memory(self, content: str, source: str = "user") -> dict:
        """
        添加新记忆的完整流程

        Args:
            content: 记忆内容
            source: 记忆来源，默认为 "user"

        Returns:
            dict: 处理结果，包含 success, memory_id, message 等信息
        """
        # 1. 隐私检测和风险评估
        privacy_check = self.privacy_detector.detect(content)
        risk_level = privacy_check.get("risk_level", "low")
        sensitive_types = privacy_check.get("sensitive_types", [])
        has_sensitive = len(sensitive_types) > 0

        # 2. 重要性评分
        importance = self.selector.evaluate_importance(content)

        # 3. 判断是否值得记忆
        if not self.selector.is_worth_remembering(content, importance):
            return {
                "success": False,
                "memory_id": None,
                "message": "内容重要性不足，不值得记忆",
                "importance": importance
            }

        # 4. 处理敏感信息（加密）
        is_encrypted = False
        if has_sensitive:
            content = self.privacy_detector.encrypt_sensitive(content)
            is_encrypted = True

        # 5. 计算保留天数
        retention_days = self._calculate_retention_days(importance)

        # 6. 存储到数据库
        from datetime import datetime
        memory = Memory(
            content=content,
            source=source,
            importance=importance,
            is_encrypted=is_encrypted,
            retention_days=retention_days,
            category="conversation",  # 默认分类
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            privacy_level=50 if is_encrypted else 0  # 加密内容默认隐私级别为50
        )

        memory_id = self.database.insert_memory(memory)

        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆添加成功",
            "importance": importance,
            "is_encrypted": is_encrypted,
            "retention_days": retention_days,
            "risk_level": risk_level if has_sensitive else "none"
        }

    def get_memory(self, memory_id: int) -> Memory | None:
        """
        获取记忆（自动更新访问次数）

        Args:
            memory_id: 记忆ID

        Returns:
            Memory | None: 记忆对象，如果不存在则返回 None
        """
        memory = self.database.get_memory(memory_id)
        if memory is not None:
            # 自动更新访问次数
            self.database.update_memory_access(memory_id)
        return memory

    def get_all_memories(self, limit: int | None = None) -> list[Memory]:
        """
        获取所有记忆

        Args:
            limit: 限制返回数量，默认为 None 表示无限制

        Returns:
            list[Memory]: 记忆列表
        """
        return self.database.get_all_memories(limit)

    def search_memories(self, query: str) -> list[Memory]:
        """
        搜索记忆

        Args:
            query: 搜索关键词

        Returns:
            list[Memory]: 匹配的记忆列表
        """
        return self.database.search_memories(query)

    def update_memory(self, memory_id: int, updates: dict) -> bool:
        """
        更新记忆

        Args:
            memory_id: 记忆ID
            updates: 要更新的字段字典

        Returns:
            bool: 更新是否成功
        """
        return self.database.update_memory(memory_id, updates)

    def delete_memory(self, memory_id: int) -> bool:
        """
        删除记忆

        Args:
            memory_id: 记忆ID

        Returns:
            bool: 删除是否成功
        """
        return self.database.delete_memory(memory_id)

    def get_stats(self) -> dict:
        """
        获取记忆统计

        Returns:
            dict: 统计数据，包含总数、加密数量、平均重要性等
        """
        return self.database.get_memory_stats()

    def _calculate_retention_days(self, importance: int) -> int:
        """
        根据重要性计算保留天数

        Args:
            importance: 重要性评分 (1-10)

        Returns:
            int: 保留天数
        """
        if importance >= 10:
            # 重要性 10: 永不遗忘 (3650天，约10年)
            return 3650
        elif importance >= 7:
            # 重要性 7-9: 1年 (365天)
            return 365
        elif importance >= 4:
            # 重要性 4-6: 30天
            return 30
        else:
            # 重要性 1-3: 7天
            return 7

    def get_recent_dialogue(self, limit: int = 10) -> list[dict]:
        """
        获取最近的对话记录

        Args:
            limit: 返回的对话数量，默认为10

        Returns:
            list[dict]: 对话记录列表，每条记录包含 role 和 content
        """
        memories = self.database.get_all_memories(limit=limit)
        dialogue = []
        for memory in memories:
            role = "user" if memory.source == "user" else "assistant"
            dialogue.append({
                "role": role,
                "content": memory.content
            })
        return dialogue

    def save_dialogue(self, user_message: str, ai_response: str) -> None:
        """
        保存对话记录

        Args:
            user_message: 用户消息
            ai_response: AI回复
        """
        # 用户消息已经在 process_message 中保存，这里只保存 AI 回复
        self.add_memory(ai_response, source="ai")

    def search_related_memory(self, query: str) -> list[dict]:
        """
        搜索相关记忆

        Args:
            query: 搜索关键词

        Returns:
            list[dict]: 相关记忆列表
        """
        memories = self.search_memories(query)
        return [{"content": m.content, "source": m.source} for m in memories]

    def get_user_preferences(self) -> dict:
        """
        获取用户偏好

        Returns:
            dict: 用户偏好字典
        """
        # 从记忆中提取用户偏好
        preferences = {}
        memories = self.get_all_memories()

        for memory in memories:
            content = memory.content
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
