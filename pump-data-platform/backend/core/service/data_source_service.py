from typing import Dict
from ..data_source.manager import DataSourceManager
from ..config import settings


class DataSourceService:
    """数据源管理服务"""
    
    @staticmethod
    def get_current_data_source() -> Dict:
        """获取当前数据源配置"""
        try:
            return {
                "type": settings.DATA_SOURCE_TYPE,
                "config": {
                    "api_base_url": settings.API_BASE_URL,
                    "api_token": settings.API_TOKEN,
                    "api_endpoint": settings.API_ENDPOINT
                }
            }
        except Exception as e:
            print(f"获取数据源配置失败: {e}")
            return {
                "type": "simulate",
                "config": {}
            }
    
    @staticmethod
    def switch_data_source(data_source_type: str, config: Dict = None) -> bool:
        """切换数据源
        
        Args:
            data_source_type: 数据源类型 (simulate, api, report)
            config: 数据源配置
        """
        try:
            # 切换数据源
            manager = DataSourceManager()
            success = manager.switch_data_source(data_source_type)
            
            # 更新配置
            if config:
                if data_source_type == "api":
                    settings.API_BASE_URL = config.get("api_base_url")
                    settings.API_TOKEN = config.get("api_token")
                    settings.API_ENDPOINT = config.get("api_endpoint", "/api/pump-data")
            
            return success
        except Exception as e:
            print(f"切换数据源失败: {e}")
            return False
