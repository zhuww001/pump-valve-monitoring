from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from core.service import DataService
import json

data_router = APIRouter()


class ReceiveDataRequest(BaseModel):
    """接收边缘网关数据请求模型"""
    device_id: str
    timestamp: str
    pressure: float
    flow: float
    temperature: float
    status: str = "normal"
    source_type: str = "edge_gateway"
    gateway_id: Optional[str] = None


@data_router.get("/realtime/{device_id}", response_model=Dict)
def get_realtime_data(device_id: str):
    """获取实时数据"""
    return DataService.get_realtime_data(device_id)


@data_router.get("/history/{device_id}", response_model=List[Dict])
def get_history_data(
    device_id: str,
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间")
):
    """获取历史数据"""
    return DataService.get_history_data(device_id, start_time, end_time)


@data_router.post("/receive", response_model=Dict)
def receive_data(data: ReceiveDataRequest):
    """
    接收边缘网关上报的传感器数据
    
    - **device_id**: 设备ID
    - **timestamp**: 数据时间戳
    - **pressure**: 压力值 (MPa)
    - **flow**: 流量值 (m³/h)
    - **temperature**: 温度值 (°C)
    - **status**: 设备状态
    - **source_type**: 数据源类型
    - **gateway_id**: 网关ID（可选）
    """
    try:
        result = DataService.process_received_data(data.model_dump())
        if not result:
            raise HTTPException(status_code=500, detail="数据处理失败")
        return {
            "success": True,
            "message": "数据接收成功",
            "device_id": data.device_id,
            "timestamp": data.timestamp,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据处理失败: {str(e)}")


@data_router.post("/receive/batch", response_model=Dict)
def receive_batch_data(data_list: List[ReceiveDataRequest]):
    """
    批量接收边缘网关上报的传感器数据
    
    - **data_list**: 传感器数据列表
    """
    try:
        success_count = 0
        failed_count = 0
        
        for data in data_list:
            try:
                DataService.process_received_data(data.model_dump())
                success_count += 1
            except Exception as e:
                print(f"处理数据失败: {data.device_id}, 错误: {e}")
                failed_count += 1
        
        return {
            "success": True,
            "message": f"批量数据处理完成，成功: {success_count}, 失败: {failed_count}",
            "success_count": success_count,
            "failed_count": failed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量数据处理失败: {str(e)}")
