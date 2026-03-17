from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from core.data_source import DataSourceManager
from core.data_process import DataStandardizer, WarningChecker, DataIngestion

websocket_router = APIRouter()


@websocket_router.websocket("/report")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，接收设备上报数据"""
    await websocket.accept()
    
    # 获取ReportDataSource实例
    manager = DataSourceManager()
    data_source = manager.get_data_source()
    
    try:
        while True:
            # 接收数据
            data = await websocket.receive_text()
            
            try:
                # 解析数据
                device_data = json.loads(data)
                device_id = device_data.get("device_id")
                
                if device_id:
                    # 更新设备数据
                    if hasattr(data_source, "update_device_data"):
                        data_source.update_device_data(device_id, device_data)
                    
                    # 标准化数据
                    standardized_data = DataStandardizer.standardize(device_data)
                    
                    # 检查预警状态
                    status, warning_type = WarningChecker.check_warning(standardized_data)
                    standardized_data["status"] = status
                    
                    # 数据入库
                    DataIngestion.ingest(standardized_data)
                    
                    # 发送确认
                    await websocket.send_json({"status": "success", "message": "数据接收成功"})
                else:
                    await websocket.send_json({"status": "error", "message": "缺少device_id"})
            except json.JSONDecodeError:
                await websocket.send_json({"status": "error", "message": "数据格式错误"})
            except Exception as e:
                await websocket.send_json({"status": "error", "message": str(e)})
    except WebSocketDisconnect:
        print("WebSocket连接断开")
