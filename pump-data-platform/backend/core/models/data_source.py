from datetime import datetime
from pydantic import BaseModel, Field


class DataSource(BaseModel):
    """数据源模型"""
    id: int = Field(..., description="数据源ID")
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    config: str = Field(..., description="配置参数（JSON格式）")
    is_enabled: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
