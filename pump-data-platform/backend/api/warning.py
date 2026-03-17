from fastapi import APIRouter, HTTPException
from typing import List, Dict
from core.service import WarningService

warning_router = APIRouter()


@warning_router.get("/list", response_model=List[Dict])
def get_warning_list():
    """获取预警列表"""
    return WarningService.get_warning_list()


@warning_router.put("/status/{warning_id}")
def update_warning_status(warning_id: int, status: Dict):
    """更新预警状态"""
    success = WarningService.update_warning_status(warning_id, status.get("status"))
    if not success:
        raise HTTPException(status_code=500, detail="更新预警状态失败")
    return {"message": "更新成功"}
