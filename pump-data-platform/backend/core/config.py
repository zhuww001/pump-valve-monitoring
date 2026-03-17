from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """全局配置类"""
    # 应用配置
    APP_NAME: str = "Pump Valve Monitoring Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "pump_data"
    
    # InfluxDB配置
    INFLUXDB_URL: str = "http://influxdb:8086"
    INFLUXDB_TOKEN: str = "your-token"
    INFLUXDB_ORG: str = "your-org"
    INFLUXDB_BUCKET: str = "pump_data"
    
    # Redis配置
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # 数据源配置
    DATA_SOURCE_TYPE: str = "simulate"  # simulate, api, report
    
    # API数据源配置
    API_BASE_URL: Optional[str] = None
    API_TOKEN: Optional[str] = None
    API_ENDPOINT: str = "/api/pump-data"
    
    # 采集配置
    COLLECTION_INTERVAL: int = 5  # 秒
    
    # 预警阈值
    PRESSURE_THRESHOLD: float = 2.0  # MPa
    FLOW_THRESHOLD: float = 5.0  # m³/h
    TEMPERATURE_THRESHOLD: float = 80.0  # °C
    
    # 本地运行模式
    LOCAL_MODE: bool = True  # 本地运行模式，不依赖数据库
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
