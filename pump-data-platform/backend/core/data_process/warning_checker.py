from typing import Dict, Tuple
from ..config import settings


class WarningChecker:
    """预警判断"""
    
    @staticmethod
    def check_warning(data: Dict) -> Tuple[str, str]:
        """检查预警状态
        
        Args:
            data: 标准化后的数据
            
        Returns:
            (状态, 预警类型)
        """
        pressure = data.get("pressure", 0.0)
        flow = data.get("flow", 0.0)
        temperature = data.get("temperature", 0.0)
        
        # 获取阈值
        pressure_threshold = settings.PRESSURE_THRESHOLD
        flow_threshold = settings.FLOW_THRESHOLD
        temperature_threshold = settings.TEMPERATURE_THRESHOLD
        
        # 检查压力
        if pressure > pressure_threshold:
            return "warning", "pressure"
        
        # 检查流量
        if flow < flow_threshold:
            return "warning", "flow"
        
        # 检查温度
        if temperature > temperature_threshold:
            return "warning", "temperature"
        
        # 正常状态
        return "normal", ""
