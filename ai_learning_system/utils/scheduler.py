import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Scheduler:
    """定期清理任务调度器"""

    def __init__(self, forgetter):
        """
        初始化调度器

        Args:
            forgetter: 遗忘器实例，需要实现 forget_expired_memories() 和 archive_old_memories() 方法
        """
        self.forgetter = forgetter
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # 执行时间配置
        self.daily_cleanup_hour = 3
        self.daily_cleanup_minute = 0
        self.weekly_cleanup_day = 6  # 周日 (0=周一, 6=周日)

        # 状态记录
        self.last_daily_cleanup: Optional[datetime] = None
        self.last_weekly_archive: Optional[datetime] = None
        self.next_daily_cleanup: Optional[datetime] = None
        self.next_weekly_archive: Optional[datetime] = None

        # 记录当天是否已经执行过（防止重复执行）
        self._daily_executed_today = False
        self._weekly_executed_this_week = False

    def start(self) -> None:
        """启动调度器，在后台线程中运行"""
        with self.lock:
            if self.running:
                logger.warning("调度器已经在运行中")
                return

            self.running = True
            self.thread = threading.Thread(target=self._schedule_loop, daemon=True)
            self.thread.start()
            logger.info("调度器已启动")

    def stop(self) -> None:
        """停止调度器，设置 running 标志为 False 并等待线程结束"""
        with self.lock:
            if not self.running:
                logger.warning("调度器未在运行")
                return

            self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("调度器线程未能在5秒内结束")
            else:
                logger.info("调度器已停止")

    def run_daily_cleanup(self) -> None:
        """每日清理任务：调用 forgetter.forget_expired_memories() 清理过期记忆"""
        try:
            logger.info("开始执行每日清理任务")
            if hasattr(self.forgetter, 'forget_expired_memories'):
                self.forgetter.forget_expired_memories()
                self.last_daily_cleanup = datetime.now()
                logger.info("每日清理任务执行完成")
            else:
                logger.error("forgetter 对象没有 forget_expired_memories 方法")
        except Exception as e:
            logger.error(f"每日清理任务执行失败: {e}")

    def run_weekly_archive(self) -> None:
        """每周归档任务：调用 forgetter.archive_old_memories() 归档旧记忆"""
        try:
            logger.info("开始执行每周归档任务")
            if hasattr(self.forgetter, 'archive_old_memories'):
                self.forgetter.archive_old_memories()
                self.last_weekly_archive = datetime.now()
                logger.info("每周归档任务执行完成")
            else:
                logger.error("forgetter 对象没有 archive_old_memories 方法")
        except Exception as e:
            logger.error(f"每周归档任务执行失败: {e}")

    def _schedule_loop(self) -> None:
        """调度循环：每分钟检查一次，在指定时间执行任务"""
        while self.running:
            try:
                now = datetime.now()

                # 检查是否需要执行每日清理（每天凌晨3点）
                if (now.hour == self.daily_cleanup_hour and
                    now.minute == self.daily_cleanup_minute and
                    not self._daily_executed_today):
                    self.run_daily_cleanup()
                    self._daily_executed_today = True

                # 重置每日执行标志（如果不是执行时间点）
                if not (now.hour == self.daily_cleanup_hour and
                        now.minute == self.daily_cleanup_minute):
                    self._daily_executed_today = False

                # 检查是否需要执行每周归档（每周日凌晨3点）
                if (now.weekday() == self.weekly_cleanup_day and
                    now.hour == self.daily_cleanup_hour and
                    now.minute == self.daily_cleanup_minute and
                    not self._weekly_executed_this_week):
                    self.run_weekly_archive()
                    self._weekly_executed_this_week = True

                # 重置每周执行标志（如果不是周日或执行时间点）
                if not (now.weekday() == self.weekly_cleanup_day and
                        now.hour == self.daily_cleanup_hour and
                        now.minute == self.daily_cleanup_minute):
                    self._weekly_executed_this_week = False

                # 更新下次执行时间
                self._update_next_run_times(now)

                # 每分钟检查一次
                time.sleep(60)

            except Exception as e:
                logger.error(f"调度循环发生错误: {e}")
                time.sleep(60)

    def _update_next_run_times(self, now: datetime) -> None:
        """更新下次执行时间"""
        # 计算下次每日清理时间
        next_daily = now.replace(hour=self.daily_cleanup_hour,
                                  minute=self.daily_cleanup_minute,
                                  second=0, microsecond=0)
        if next_daily <= now:
            next_daily += timedelta(days=1)
        self.next_daily_cleanup = next_daily

        # 计算下次每周归档时间
        days_until_sunday = (self.weekly_cleanup_day - now.weekday()) % 7
        next_weekly = now.replace(hour=self.daily_cleanup_hour,
                                   minute=self.daily_cleanup_minute,
                                   second=0, microsecond=0)
        next_weekly += timedelta(days=days_until_sunday)
        if next_weekly <= now:
            next_weekly += timedelta(days=7)
        self.next_weekly_archive = next_weekly

    def get_next_run_times(self) -> Dict[str, Optional[datetime]]:
        """
        获取下次运行时间

        Returns:
            包含下次每日清理和每周归档时间的字典
        """
        if self.next_daily_cleanup is None or self.next_weekly_archive is None:
            self._update_next_run_times(datetime.now())

        return {
            "next_daily_cleanup": self.next_daily_cleanup,
            "next_weekly_archive": self.next_weekly_archive
        }

    def get_status(self) -> Dict[str, Any]:
        """
        获取调度器状态

        Returns:
            包含运行状态、上次执行时间和下次执行时间的字典
        """
        next_times = self.get_next_run_times()

        return {
            "running": self.running,
            "last_daily_cleanup": self.last_daily_cleanup,
            "last_weekly_archive": self.last_weekly_archive,
            "next_daily_cleanup": next_times["next_daily_cleanup"],
            "next_weekly_archive": next_times["next_weekly_archive"],
            "daily_cleanup_hour": self.daily_cleanup_hour,
            "weekly_cleanup_day": self.weekly_cleanup_day
        }
