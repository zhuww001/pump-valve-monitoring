from datetime import datetime
from typing import Dict


class DataStandardizer:
    """数据标准化"""
    
    @staticmethod
    def standardize(data: Dict) -> Dict:
        """标准化数据
        
        Args:
            data: 原始数据
            
        Returns:
            标准化后的数据
        """
        # 统一字段
        standardized_data = {
            "device_id": data.get("device_id", ""),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "pressure": float(data.get("pressure", 0.0)),
            "flow": float(data.get("flow", 0.0)),
            "temperature": float(data.get("temperature", 0.0)),
            "status": data.get("status", "normal"),
            "source_type": data.get("source_type", "unknown")
        }
        
        # 确保timestamp是ISO格式字符串
        if isinstance(standardized_data["timestamp"], datetime):
            standardized_data["timestamp"] = standardized_data["timestamp"].isoformat()
        
        # 确保状态值有效
        valid_statuses = ["normal", "warning", "alert", "offline"]
        if standardized_data["status"] not in valid_statuses:
            standardized_data["status"] = "normal"
        
        # 确保数值非负
        standardized_data["pressure"] = max(0, standardized_data["pressure"])
        standardized_data["flow"] = max(0, standardized_data["flow"])
        standardized_data["temperature"] = max(0, standardized_data["temperature"])
        
        return standardized_data
