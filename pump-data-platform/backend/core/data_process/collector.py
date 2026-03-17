from datetime import datetime
from typing import List
from ..data_source.manager import DataSourceManager
from .standardizer import DataStandardizer
from .warning_checker import WarningChecker
from .ingestion import DataIngestion
from ..config import settings


class DataCollector:
    """定时采集"""
    
    def __init__(self):
        self.data_source_manager = DataSourceManager()
    
    def collect(self):
        """采集数据"""
        # 获取当前数据源
        data_source = self.data_source_manager.get_data_source()
        
        # 获取设备列表
        devices = data_source.get_device_list()
        
        # 采集每个设备的数据
        for device in devices:
            device_id = device.get("id")
            
            # 获取实时数据
            raw_data = data_source.get_realtime_data(device_id)
            
            # 标准化数据
            standardized_data = DataStandardizer.standardize(raw_data)
            
            # 检查预警状态
            status, warning_type = WarningChecker.check_warning(standardized_data)
            standardized_data["status"] = status
            
            # 数据入库
            DataIngestion.ingest(standardized_data)
    
    def collect_history(self, start_time: datetime, end_time: datetime):
        """采集历史数据"""
        # 获取当前数据源
        data_source = self.data_source_manager.get_data_source()
        
        # 获取设备列表
        devices = data_source.get_device_list()
        
        # 采集每个设备的历史数据
        for device in devices:
            device_id = device.get("id")
            
            # 获取历史数据
            raw_data_list = data_source.get_history_data(device_id, start_time, end_time)
            
            # 处理每条数据
            for raw_data in raw_data_list:
                # 标准化数据
                standardized_data = DataStandardizer.standardize(raw_data)
                
                # 检查预警状态
                status, warning_type = WarningChecker.check_warning(standardized_data)
                standardized_data["status"] = status
                
                # 数据入库
                DataIngestion.ingest(standardized_data)
