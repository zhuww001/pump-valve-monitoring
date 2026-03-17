from fastapi import APIRouter, HTTPException
from typing import Dict
from core.service import DataSourceService

data_source_router = APIRouter()


@data_source_router.get("/current", response_model=Dict)
def get_current_data_source():
    """获取当前数据源配置"""
    return DataSourceService.get_current_data_source()


@data_source_router.post("/switch")
def switch_data_source(data: Dict):
    """切换数据源"""
    data_source_type = data.get("type")
    config = data.get("config", {})
    
    success = DataSourceService.switch_data_source(data_source_type, config)
    if not success:
        raise HTTPException(status_code=500, detail="切换数据源失败")
    return {"message": "切换成功"}
