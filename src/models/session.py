"""
TwoYaTimer — 计时会话数据模型

定义计次记录 (LapRecord) 和计时会话 (TimerSession) 的数据结构，
支持 dict 序列化/反序列化以便 JSON 持久化。
"""

from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class LapRecord:
    """
    单次计次记录。

    Attributes:
        number:     圈号（从 1 开始递增）
        split_time: 从计时开始到该圈记录点的累计时间（秒）
        lap_time:   该圈耗时 = split_time - 上一圈的 split_time（秒）
    """
    number: int
    split_time: float
    lap_time: float


@dataclass
class TimerSession:
    """
    一次完整的计时会话。

    当用户从「开始」到「重置」（或关闭窗口）为止，构成一次会话。
    包含开始/结束时间戳、总时长、以及所有计次记录。

    Attributes:
        id:             唯一标识符（UUID 前 8 位，便于显示与检索）
        start_datetime: 会话开始时间（ISO 8601 格式字符串）
        end_datetime:   会话结束时间
        total_duration: 总时长（秒）
        laps:           计次记录列表
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_datetime: str = ""
    end_datetime: str = ""
    total_duration: float = 0.0
    laps: List[LapRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        """序列化为可 JSON 化的字典。"""
        return {
            "id": self.id,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "total_duration": self.total_duration,
            "laps": [
                {
                    "number": lap.number,
                    "split_time": lap.split_time,
                    "lap_time": lap.lap_time,
                }
                for lap in self.laps
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimerSession":
        """从字典反序列化为 TimerSession 实例。"""
        laps = [LapRecord(**lap) for lap in data.get("laps", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            start_datetime=data.get("start_datetime", ""),
            end_datetime=data.get("end_datetime", ""),
            total_duration=data.get("total_duration", 0.0),
            laps=laps,
        )
