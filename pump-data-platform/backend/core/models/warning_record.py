from datetime import datetime
from pydantic import BaseModel, Field


class WarningRecord(BaseModel):
    """预警记录模型"""
    id: int = Field(..., description="预警ID")
    device_id: str = Field(..., description="设备ID")
    warning_type: str = Field(..., description="预警类型")
    warning_value: float = Field(..., description="预警值")
    threshold: float = Field(..., description="阈值")
    status: str = Field(..., description="处理状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
