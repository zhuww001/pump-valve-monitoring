from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class BaseDataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_realtime_data(self, device_id: str) -> Dict:
        """获取实时数据
        
        Args:
            device_id: 设备ID
            
        Returns:
            包含设备实时数据的字典
        """
        pass
    
    @abstractmethod
    def get_history_data(self, device_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取历史数据
        
        Args:
            device_id: 设备ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            历史数据列表
        """
        pass
    
    @abstractmethod
    def get_device_list(self) -> List[Dict]:
        """获取设备列表
        
        Returns:
            设备列表
        """
        pass
