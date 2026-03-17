import requests
from datetime import datetime
from typing import List, Dict
from .base import BaseDataSource
from .simulate import SimulateDataSource
from ..config import settings


class ApiDataSource(BaseDataSource):
    """API对接数据源"""
    
    def __init__(self):
        # 初始化模拟数据源作为降级方案
        self.simulate_data_source = SimulateDataSource()
        
        # API配置
        self.base_url = settings.API_BASE_URL
        self.token = settings.API_TOKEN
        self.endpoint = settings.API_ENDPOINT
    
    def get_realtime_data(self, device_id: str) -> Dict:
        """获取实时数据"""
        if not self.base_url:
            # 降级为模拟数据
            return self.simulate_data_source.get_realtime_data(device_id)
        
        try:
            # 构建请求URL
            url = f"{self.base_url}{self.endpoint}"
            
            # 构建请求参数
            params = {"device_id": device_id}
            
            # 构建请求头
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # 发送请求
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                
                # 标准化数据格式
                return {
                    "device_id": device_id,
                    "timestamp": data.get("timestamp", datetime.now().isoformat()),
                    "pressure": data.get("pressure", 0.0),
                    "flow": data.get("flow", 0.0),
                    "temperature": data.get("temperature", 0.0),
                    "status": data.get("status", "normal"),
                    "source_type": "api"
                }
            else:
                # 降级为模拟数据
                return self.simulate_data_source.get_realtime_data(device_id)
        except Exception as e:
            # 发生异常时降级为模拟数据
            print(f"API请求失败: {e}")
            return self.simulate_data_source.get_realtime_data(device_id)
    
    def get_history_data(self, device_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取历史数据"""
        if not self.base_url:
            # 降级为模拟数据
            return self.simulate_data_source.get_history_data(device_id, start_time, end_time)
        
        try:
            # 构建请求URL
            url = f"{self.base_url}{self.endpoint}/history"
            
            # 构建请求参数
            params = {
                "device_id": device_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            # 构建请求头
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # 发送请求
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                
                # 标准化数据格式
                history_data = []
                for item in data:
                    history_data.append({
                        "device_id": device_id,
                        "timestamp": item.get("timestamp"),
                        "pressure": item.get("pressure", 0.0),
                        "flow": item.get("flow", 0.0),
                        "temperature": item.get("temperature", 0.0),
                        "status": item.get("status", "normal"),
                        "source_type": "api"
                    })
                return history_data
            else:
                # 降级为模拟数据
                return self.simulate_data_source.get_history_data(device_id, start_time, end_time)
        except Exception as e:
            # 发生异常时降级为模拟数据
            print(f"API请求失败: {e}")
            return self.simulate_data_source.get_history_data(device_id, start_time, end_time)
    
    def get_device_list(self) -> List[Dict]:
        """获取设备列表"""
        if not self.base_url:
            # 降级为模拟数据
            return self.simulate_data_source.get_device_list()
        
        try:
            # 构建请求URL
            url = f"{self.base_url}{self.endpoint}/devices"
            
            # 构建请求头
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=5)
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            else:
                # 降级为模拟数据
                return self.simulate_data_source.get_device_list()
        except Exception as e:
            # 发生异常时降级为模拟数据
            print(f"API请求失败: {e}")
            return self.simulate_data_source.get_device_list()
