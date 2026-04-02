"""
社交事件系统模块
管理游戏中的社交事件，包括道侣结成、师徒关系建立、仇敌冲突等
"""

import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SocialEventType(Enum):
    """社交事件类型"""
    DAO_LV_ESTABLISHED = "dao_lv_established"           # 结为道侣
    DAO_LV_BROKEN = "dao_lv_broken"                     # 解除道侣
    MASTER_APPRENTICE_ESTABLISHED = "master_apprentice_established"  # 建立师徒
    MASTER_APPRENTICE_ENDED = "master_apprentice_ended" # 解除师徒
    ENEMY_CONFLICT = "enemy_conflict"                   # 仇敌冲突
    FRIENDSHIP_DEEPENED = "friendship_deepened"         # 友谊加深
    BETRAYAL = "betrayal"                               # 背叛事件
    RECONCILIATION = "reconciliation"                   # 和解事件
    RIVALRY = "rivalry"                                 # 竞争关系
    ALLIANCE = "alliance"                               # 结盟事件


@dataclass
class SocialEvent:
    """社交事件数据类"""
    event_type: SocialEventType
    npc1_id: str
    npc2_id: str
    npc1_name: str
    npc2_name: str
    timestamp: float
    description: str
    location: str = ""
    is_public: bool = False
    importance: int = 5  # 重要性 1-10
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'event_type': self.event_type.value,
            'npc1_id': self.npc1_id,
            'npc2_id': self.npc2_id,
            'npc1_name': self.npc1_name,
            'npc2_name': self.npc2_name,
            'timestamp': self.timestamp,
            'description': self.description,
            'location': self.location,
            'is_public': self.is_public,
            'importance': self.importance,
            'details': self.details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialEvent':
        """从字典创建"""
        return cls(
            event_type=SocialEventType(data.get('event_type', 'friendship_deepened')),
            npc1_id=data.get('npc1_id', ''),
            npc2_id=data.get('npc2_id', ''),
            npc1_name=data.get('npc1_name', ''),
            npc2_name=data.get('npc2_name', ''),
            timestamp=data.get('timestamp', time.time()),
            description=data.get('description', ''),
            location=data.get('location', ''),
            is_public=data.get('is_public', False),
            importance=data.get('importance', 5),
            details=data.get('details', {})
        )


class SocialEventManager:
    """社交事件管理器"""

    def __init__(self):
        """初始化社交事件管理器"""
        self._events: List[SocialEvent] = []
        self._listeners: Dict[SocialEventType, List[Callable]] = {}
        self._player_notifications: List[Dict[str, Any]] = []

    def add_event(self, event: SocialEvent) -> bool:
        """
        添加社交事件

        Args:
            event: 社交事件对象

        Returns:
            是否成功添加
        """
        self._events.append(event)

        # 限制事件数量
        if len(self._events) > 1000:
            self._events = self._events[-1000:]

        # 触发监听器
        self._notify_listeners(event)

        # 如果是公开事件，添加到玩家通知
        if event.is_public:
            self._add_player_notification(event)

        # 保存到数据库
        self._save_event_to_db(event)

        return True

    def create_event(self, event_type: SocialEventType,
                    npc1_id: str, npc2_id: str,
                    npc1_name: str, npc2_name: str,
                    description: str, location: str = "",
                    is_public: bool = False, importance: int = 5,
                    details: Dict[str, Any] = None) -> SocialEvent:
        """
        创建并添加社交事件

        Args:
            event_type: 事件类型
            npc1_id: 第一个NPC的ID
            npc2_id: 第二个NPC的ID
            npc1_name: 第一个NPC的名称
            npc2_name: 第二个NPC的名称
            description: 事件描述
            location: 发生地点
            is_public: 是否公开
            importance: 重要性
            details: 详细信息

        Returns:
            创建的社交事件
        """
        event = SocialEvent(
            event_type=event_type,
            npc1_id=npc1_id,
            npc2_id=npc2_id,
            npc1_name=npc1_name,
            npc2_name=npc2_name,
            timestamp=time.time(),
            description=description,
            location=location,
            is_public=is_public,
            importance=importance,
            details=details or {}
        )

        self.add_event(event)
        return event

    def _save_event_to_db(self, event: SocialEvent):
        """保存事件到数据库"""
        try:
            from storage.database import Database
            db = Database()

            db.record_npc_social_event(
                event_type=event.event_type.value,
                npc1_id=event.npc1_id,
                npc2_id=event.npc2_id,
                description=event.description,
                location=event.location,
                result=str(event.details) if event.details else "",
                is_public=event.is_public
            )
        except Exception as e:
            print(f"保存社交事件到数据库失败: {e}")

    def _notify_listeners(self, event: SocialEvent):
        """通知所有监听器"""
        listeners = self._listeners.get(event.event_type, [])
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"通知监听器失败: {e}")

    def _add_player_notification(self, event: SocialEvent):
        """添加玩家通知"""
        notification = {
            'type': 'social_event',
            'event_type': event.event_type.value,
            'title': self._get_event_title(event.event_type),
            'message': event.description,
            'npc1_name': event.npc1_name,
            'npc2_name': event.npc2_name,
            'timestamp': event.timestamp,
            'importance': event.importance,
            'read': False
        }
        self._player_notifications.append(notification)

        # 限制通知数量
        if len(self._player_notifications) > 100:
            self._player_notifications = self._player_notifications[-100:]

    def _get_event_title(self, event_type: SocialEventType) -> str:
        """获取事件标题"""
        titles = {
            SocialEventType.DAO_LV_ESTABLISHED: "结为道侣",
            SocialEventType.DAO_LV_BROKEN: "解除道侣",
            SocialEventType.MASTER_APPRENTICE_ESTABLISHED: "收徒",
            SocialEventType.MASTER_APPRENTICE_ENDED: "逐出师门",
            SocialEventType.ENEMY_CONFLICT: "仇敌冲突",
            SocialEventType.FRIENDSHIP_DEEPENED: "友谊加深",
            SocialEventType.BETRAYAL: "背叛事件",
            SocialEventType.RECONCILIATION: "和解事件",
            SocialEventType.RIVALRY: "竞争关系",
            SocialEventType.ALLIANCE: "结盟事件",
        }
        return titles.get(event_type, "社交事件")

    def register_listener(self, event_type: SocialEventType, callback: Callable):
        """
        注册事件监听器

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unregister_listener(self, event_type: SocialEventType, callback: Callable):
        """
        注销事件监听器

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def get_player_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        获取玩家通知

        Args:
            unread_only: 是否只返回未读通知

        Returns:
            通知列表
        """
        if unread_only:
            return [n for n in self._player_notifications if not n.get('read', False)]
        return self._player_notifications.copy()

    def mark_notification_read(self, index: int) -> bool:
        """
        标记通知为已读

        Args:
            index: 通知索引

        Returns:
            是否成功
        """
        if 0 <= index < len(self._player_notifications):
            self._player_notifications[index]['read'] = True
            return True
        return False

    def mark_all_notifications_read(self):
        """标记所有通知为已读"""
        for notification in self._player_notifications:
            notification['read'] = True

    def get_events_by_npc(self, npc_id: str, limit: int = 50) -> List[SocialEvent]:
        """
        获取NPC相关的所有事件

        Args:
            npc_id: NPC的ID
            limit: 返回数量限制

        Returns:
            事件列表
        """
        events = [e for e in self._events if e.npc1_id == npc_id or e.npc2_id == npc_id]
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_events_by_type(self, event_type: SocialEventType, limit: int = 50) -> List[SocialEvent]:
        """
        获取特定类型的事件

        Args:
            event_type: 事件类型
            limit: 返回数量限制

        Returns:
            事件列表
        """
        events = [e for e in self._events if e.event_type == event_type]
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_recent_events(self, limit: int = 50) -> List[SocialEvent]:
        """
        获取最近的事件

        Args:
            limit: 返回数量限制

        Returns:
            事件列表
        """
        return sorted(self._events, key=lambda x: x.timestamp, reverse=True)[:limit]

    def clear_old_events(self, days: int = 30):
        """
        清理旧事件

        Args:
            days: 保留天数
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        self._events = [e for e in self._events if e.timestamp > cutoff_time]


# 全局社交事件管理器实例
social_event_manager = SocialEventManager()


def get_social_event_manager() -> SocialEventManager:
    """获取社交事件管理器实例"""
    return social_event_manager
