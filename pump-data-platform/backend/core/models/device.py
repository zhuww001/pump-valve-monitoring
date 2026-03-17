from datetime import datetime
from pydantic import BaseModel, Field


class Device(BaseModel):
    """设备模型"""
    id: int = Field(..., description="设备ID")
    device_id: str = Field(..., description="设备唯一标识")
    name: str = Field(..., description="设备名称")
    location: str = Field(..., description="安装位置")
    pressure_threshold: float = Field(..., description="压力预警阈值")
    flow_threshold: float = Field(..., description="流量预警阈值")
    temperature_threshold: float = Field(..., description="温度预警阈值")
    status: str = Field(..., description="设备状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
