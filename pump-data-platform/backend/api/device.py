from fastapi import APIRouter, HTTPException
from typing import List, Dict
from core.service import DeviceService

device_router = APIRouter()


@device_router.get("/list", response_model=List[Dict])
def get_device_list():
    """获取设备列表"""
    return DeviceService.get_device_list()


@device_router.put("/threshold/{device_id}")
def update_device_threshold(device_id: str, thresholds: Dict):
    """更新设备阈值"""
    success = DeviceService.update_device_threshold(device_id, thresholds)
    if not success:
        raise HTTPException(status_code=500, detail="更新设备阈值失败")
    return {"message": "更新成功"}


@device_router.get("/{device_id}", response_model=Dict)
def get_device(device_id: str):
    """根据设备ID获取设备信息"""
    device = DeviceService.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device
