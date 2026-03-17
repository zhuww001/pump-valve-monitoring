#!/usr/bin/env python3
"""
数据校验 + 均值滤波去毛刺
"""

from collections import deque
from typing import Dict, Tuple, Optional

# 合法范围
RANGES = {
    "pressure":    (0.0, 5.0),     # MPa
    "flow":        (0.0, 50.0),    # m³/h
    "temperature": (-20.0, 200.0), # °C
}

REQUIRED_FIELDS = {"device_id", "timestamp", "pressure", "flow", "temperature", "gateway_id"}

FILTER_WINDOW = 3  # 滑动均值窗口大小


class DataPreprocessor:
    def __init__(self):
        # device_id -> {"pressure": deque, "flow": deque, "temperature": deque}
        self._buffers: Dict[str, Dict[str, deque]] = {}

    def validate(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        字段完整性 + 数值范围检查。
        返回 (ok, error_message)。
        """
        # 字段完整性
        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            return False, f"缺少必要字段: {missing}"

        # 数值范围
        for field, (lo, hi) in RANGES.items():
            val = data.get(field)
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                return False, f"字段 {field} 类型错误: {val}"
            if not (lo <= val <= hi):
                return False, f"字段 {field} 超出范围 [{lo}, {hi}]: {val}"

        return True, None

    def filter(self, device_id: str, values: Dict[str, float]) -> Dict[str, float]:
        """
        3 点滑动均值滤波。
        values 应包含 pressure / flow / temperature。
        返回平滑后的同结构字典。
        """
        if device_id not in self._buffers:
            self._buffers[device_id] = {
                "pressure":    deque(maxlen=FILTER_WINDOW),
                "flow":        deque(maxlen=FILTER_WINDOW),
                "temperature": deque(maxlen=FILTER_WINDOW),
            }

        buf = self._buffers[device_id]
        result = {}

        for key in ("pressure", "flow", "temperature"):
            raw = values.get(key)
            if raw is None:
                continue
            buf[key].append(float(raw))
            result[key] = round(sum(buf[key]) / len(buf[key]), 4)

        return result
