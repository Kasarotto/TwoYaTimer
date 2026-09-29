"""
TwoYaTimer — 计时核心引擎

使用 time.perf_counter() 提供微秒级高精度计时。
引擎仅负责时间计算逻辑，不包含任何 UI 代码，
便于单独测试和复用。

状态机:
    STOPPED ──start()──► RUNNING
    RUNNING ──pause()──► PAUSED
    PAUSED  ──start()──► RUNNING
    任意态  ──reset()──► STOPPED
"""

import time
from enum import Enum
from typing import Optional, Tuple, List


class TimerState(Enum):
    """计时器状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class TimerEngine:
    """
    高精度计时引擎。

    核心思路：
    - _accumulated: 暂停前累计的时间（秒）
    - _start_mark:  最近一次启动/恢复时的 perf_counter 标记
    - elapsed():    当前总耗时 = _accumulated + (当前 perf_counter - _start_mark)
    """

    def __init__(self):
        self._state: TimerState = TimerState.STOPPED
        self._accumulated: float = 0.0       # 暂停前已累计的秒数
        self._start_mark: float = 0.0        # 最近一次 start/resume 的时刻
        self._laps: List[Tuple[float, float]] = []  # [(split_time, lap_time), ...]
        self._last_lap_split: float = 0.0    # 上一次计次时的累计时间

    # ── 状态查询 ──

    @property
    def state(self) -> TimerState:
        """当前计时器状态。"""
        return self._state

    def elapsed(self) -> float:
        """
        获取当前总耗时（秒）。

        - RUNNING 状态: 返回累计 + 本次运行时长
        - PAUSED/STOPPED: 返回冻结的累计值
        """
        if self._state == TimerState.RUNNING:
            return self._accumulated + (time.perf_counter() - self._start_mark)
        return self._accumulated

    @property
    def laps(self) -> List[Tuple[float, float]]:
        """所有计次记录的拷贝: [(split_time, lap_time), ...]"""
        return list(self._laps)

    # ── 状态控制 ──

    def start(self) -> None:
        """
        启动或恢复计时。

        - STOPPED → RUNNING: 全新开始，清零所有数据
        - PAUSED  → RUNNING: 从暂停处恢复，保留累计时间
        - RUNNING: 无操作
        """
        if self._state == TimerState.STOPPED:
            # 全新开始
            self._accumulated = 0.0
            self._laps.clear()
            self._last_lap_split = 0.0
            self._start_mark = time.perf_counter()
            self._state = TimerState.RUNNING

        elif self._state == TimerState.PAUSED:
            # 从暂停恢复：重新打标记，累计值不变
            self._start_mark = time.perf_counter()
            self._state = TimerState.RUNNING

    def pause(self) -> None:
        """
        暂停计时。

        将当前运行时段的时间加入累计值，然后冻结。
        仅 RUNNING → PAUSED 有效。
        """
        if self._state == TimerState.RUNNING:
            self._accumulated += time.perf_counter() - self._start_mark
            self._state = TimerState.PAUSED

    def reset(self) -> None:
        """
        重置计时器。

        清零所有数据，回到 STOPPED 状态。
        可在任意状态下调用。
        """
        self._state = TimerState.STOPPED
        self._accumulated = 0.0
        self._start_mark = 0.0
        self._laps.clear()
        self._last_lap_split = 0.0

    def lap(self) -> Optional[Tuple[int, float, float]]:
        """
        记录一次计次。

        仅在 RUNNING 状态下有效。

        Returns:
            (圈号, 累计时间, 本圈耗时) 或 None（非运行状态）
        """
        if self._state != TimerState.RUNNING:
            return None

        split = self.elapsed()
        lap_time = split - self._last_lap_split
        self._last_lap_split = split
        self._laps.append((split, lap_time))

        return len(self._laps), split, lap_time
