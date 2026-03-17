import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from .base import BaseDataSource


class ReportDataSource(BaseDataSource):
    """设备上报数据源"""
    
    def __init__(self):
        # 存储设备实时数据
        self.device_data = {}
        
        # 存储设备列表
        self.devices = [
            {"id": "device_1", "name": "泵A", "location": "一号车间"},
            {"id": "device_2", "name": "泵B", "location": "二号车间"},
            {"id": "device_3", "name": "泵C", "location": "三号车间"}
        ]
        
        # 初始化设备数据
        for device in self.devices:
            self.device_data[device["id"]] = {
                "timestamp": datetime.now().isoformat(),
                "pressure": 0.0,
                "flow": 0.0,
                "temperature": 0.0,
                "status": "offline"
            }
    
    def update_device_data(self, device_id: str, data: Dict):
        """更新设备数据"""
        if device_id not in self.device_data:
            # 添加新设备
            self.device_data[device_id] = {
                "timestamp": datetime.now().isoformat(),
                "pressure": 0.0,
                "flow": 0.0,
                "temperature": 0.0,
                "status": "offline"
            }
        
        # 更新设备数据
        self.device_data[device_id].update({
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "pressure": data.get("pressure", 0.0),
            "flow": data.get("flow", 0.0),
            "temperature": data.get("temperature", 0.0),
            "status": data.get("status", "normal")
        })
    
    def get_realtime_data(self, device_id: str) -> Dict:
        """获取实时数据"""
        if device_id not in self.device_data:
            return {
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "pressure": 0.0,
                "flow": 0.0,
                "temperature": 0.0,
                "status": "offline",
                "source_type": "report"
            }
        
        # 检查数据是否过期（超过5分钟）
        device_data = self.device_data[device_id]
        timestamp = datetime.fromisoformat(device_data["timestamp"])
        if (datetime.now() - timestamp).total_seconds() > 300:
            return {
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "pressure": 0.0,
                "flow": 0.0,
                "temperature": 0.0,
                "status": "offline",
                "source_type": "report"
            }
        
        # 返回设备数据
        return {
            "device_id": device_id,
            "timestamp": device_data["timestamp"],
            "pressure": device_data["pressure"],
            "flow": device_data["flow"],
            "temperature": device_data["temperature"],
            "status": device_data["status"],
            "source_type": "report"
        }
    
    def get_history_data(self, device_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取历史数据"""
        # 由于是设备上报模式，历史数据可能存储在其他地方
        # 这里返回空列表，实际项目中应该从存储中读取
        return []
    
    def get_device_list(self) -> List[Dict]:
        """获取设备列表"""
        return self.devices
