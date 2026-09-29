"""
TwoYaTimer — JSON 持久化存储

历史记录存放在 %APPDATA%/TwoYaTimer/ 目录下，
确保不同运行位置都能访问同一份数据。
"""

import json
import os
from typing import List

from models.session import TimerSession
from utils.constants import DATA_FILENAME, APP_NAME


class Storage:
    """
    计时会话的 JSON 持久化管理器。

    存储路径优先级：
    1. %APPDATA%/TwoYaTimer/  (Windows 标准应用数据目录)
    2. 程序所在目录             (环境变量不可用时的回退)
    """

    def __init__(self):
        self._data_dir = self._resolve_data_dir()
        self._filepath = os.path.join(self._data_dir, DATA_FILENAME)

    @staticmethod
    def _resolve_data_dir() -> str:
        """确定并创建数据存储目录。"""
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            data_dir = os.path.join(appdata, APP_NAME)
        else:
            # 回退到程序同目录
            data_dir = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def load_sessions(self) -> List[TimerSession]:
        """
        从 JSON 文件加载所有历史会话。

        Returns:
            会话列表（按保存顺序，最新在前）。
            文件不存在或损坏时返回空列表。
        """
        if not os.path.exists(self._filepath):
            return []
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [TimerSession.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # 文件损坏时不崩溃，返回空
            return []

    def save_sessions(self, sessions: List[TimerSession]) -> None:
        """将完整会话列表写入 JSON 文件。"""
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(
                [s.to_dict() for s in sessions],
                f,
                ensure_ascii=False,
                indent=2,
            )

    def add_session(self, session: TimerSession) -> None:
        """在列表头部插入一条新会话并保存。"""
        sessions = self.load_sessions()
        sessions.insert(0, session)
        self.save_sessions(sessions)

    def delete_session(self, session_id: str) -> None:
        """按 ID 删除单条会话并保存。"""
        sessions = self.load_sessions()
        sessions = [s for s in sessions if s.id != session_id]
        self.save_sessions(sessions)
