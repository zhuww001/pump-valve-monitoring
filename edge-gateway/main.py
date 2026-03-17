#!/usr/bin/env python3
"""
边缘计算数据采集网关 v2
集成：本地 SQLite 缓冲、数据预处理、WebSocket 实时推流、后台重试队列
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import httpx
import json
import os

from storage import EdgeStorage
from preprocessor import DataPreprocessor
from ws_manager import ConnectionManager

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
MAIN_SYSTEM_URL = os.getenv("MAIN_SYSTEM_URL", "http://localhost:8000")
DATA_API_ENDPOINT = f"{MAIN_SYSTEM_URL}/api/data/receive"
RETRY_INTERVAL = 30  # 秒

# 全局单例
storage = EdgeStorage()
preprocessor = DataPreprocessor()
ws_manager = ConnectionManager()

# 网关运行时状态（内存）
gateway_status: Dict[str, dict] = {}

# 可动态修改的网关配置
gateway_config: Dict[str, Any] = {
    "main_system_url": MAIN_SYSTEM_URL,
    "collect_interval": 5,
    "thresholds": {
        "pressure_max": 5.0,
        "flow_max": 50.0,
        "temperature_max": 200.0,
    }
}


# ──────────────────────────────────────────────
# 生命周期
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await storage.init_db()
    task = asyncio.create_task(retry_background_task())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="边缘计算数据采集网关",
    description="接收传感器数据并转发到泵阀监控系统（含本地缓冲 + WebSocket 推流）",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────
class SensorData(BaseModel):
    device_id: str
    timestamp: str
    pressure: float
    flow: float
    temperature: float
    status: str = "normal"
    source_type: str = "edge_gateway"


class EdgeGatewayData(BaseModel):
    gateway_id: str
    timestamp: str
    sensors: List[SensorData]


class GatewayStatus(BaseModel):
    gateway_id: str
    status: str
    last_report: Optional[str] = None
    sensor_count: int = 0


class GatewayConfig(BaseModel):
    main_system_url: Optional[str] = None
    collect_interval: Optional[int] = None
    thresholds: Optional[dict] = None


# ──────────────────────────────────────────────
# 后台重试任务
# ──────────────────────────────────────────────
async def retry_background_task():
    """每 RETRY_INTERVAL 秒检查 pending 数据并批量重传"""
    while True:
        await asyncio.sleep(RETRY_INTERVAL)
        try:
            pending = await storage.get_pending_data(limit=50)
            if not pending:
                continue

            forwarded_ids = []
            async with httpx.AsyncClient() as client:
                for record in pending:
                    try:
                        resp = await client.post(
                            f"{gateway_config['main_system_url']}/api/data/receive",
                            json={
                                "device_id": record["device_id"],
                                "timestamp": record["timestamp"],
                                "pressure": record["pressure"],
                                "flow": record["flow"],
                                "temperature": record["temperature"],
                                "status": record["status"],
                                "source_type": "edge_gateway",
                                "gateway_id": record["gateway_id"],
                            },
                            timeout=5.0,
                        )
                        if resp.status_code == 200:
                            forwarded_ids.append(record["id"])
                        else:
                            await storage.increment_retry(record["id"])
                    except Exception:
                        await storage.increment_retry(record["id"])

            if forwarded_ids:
                await storage.mark_forwarded(forwarded_ids)
                print(f"[retry] 补传成功 {len(forwarded_ids)} 条")

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[retry] 后台重试异常: {e}")


async def forward_to_main_system(record: dict) -> bool:
    """立即转发单条数据到主系统，返回是否成功"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{gateway_config['main_system_url']}/api/data/receive",
                json=record,
                timeout=5.0,
            )
            return resp.status_code == 200
    except Exception:
        return False


# ──────────────────────────────────────────────
# 端点
# ──────────────────────────────────────────────
@app.get("/")
def root():
    return {"service": "边缘计算数据采集网关", "version": "2.0.0", "status": "running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "main_system_url": gateway_config["main_system_url"],
    }


# ── 传感器数据上传 ──────────────────────────────
@app.post("/api/data/upload")
async def upload_data(data: EdgeGatewayData, background_tasks: BackgroundTasks):
    """
    接收边缘网关上传的传感器数据：
    1. 校验 → 2. 滤波 → 3. 本地持久化 → 4. 异步转发主系统 → 5. WebSocket 广播
    """
    results = []

    for sensor in data.sensors:
        raw = {
            "device_id": sensor.device_id,
            "timestamp": sensor.timestamp,
            "pressure": sensor.pressure,
            "flow": sensor.flow,
            "temperature": sensor.temperature,
            "status": sensor.status,
            "gateway_id": data.gateway_id,
        }

        # 1. 校验
        ok, err = preprocessor.validate(raw)
        if not ok:
            results.append({"device_id": sensor.device_id, "accepted": False, "reason": err})
            continue

        # 2. 滤波
        smoothed = preprocessor.filter(sensor.device_id, {
            "pressure": sensor.pressure,
            "flow": sensor.flow,
            "temperature": sensor.temperature,
        })
        raw.update(smoothed)

        # 3. 本地持久化
        record_id = await storage.save_data(raw)

        # 4. 异步转发主系统
        payload = {**raw, "source_type": "edge_gateway"}
        success = await forward_to_main_system(payload)
        if success:
            await storage.mark_forwarded([record_id])

        # 5. WebSocket 广播
        broadcast_msg = {
            **raw,
            "record_id": record_id,
            "forwarded": success,
            "source_type": "edge_gateway",
        }
        background_tasks.add_task(ws_manager.broadcast, broadcast_msg)

        results.append({"device_id": sensor.device_id, "accepted": True, "forwarded": success})

    # 更新网关内存状态
    gateway_status[data.gateway_id] = {
        "gateway_id": data.gateway_id,
        "status": "online",
        "last_report": data.timestamp,
        "sensor_count": len(data.sensors),
    }

    return {
        "success": True,
        "message": "数据接收完成",
        "gateway_id": data.gateway_id,
        "results": results,
    }


# ── 网关状态 ────────────────────────────────────
@app.get("/api/gateways", response_model=List[GatewayStatus])
def get_gateways():
    return list(gateway_status.values())


@app.get("/api/gateways/{gateway_id}")
def get_gateway(gateway_id: str):
    if gateway_id not in gateway_status:
        raise HTTPException(status_code=404, detail="网关不存在")
    return gateway_status[gateway_id]


# ── 传感器列表 ──────────────────────────────────
@app.get("/api/sensors")
async def get_sensors():
    """列出所有已上报过的传感器及最新状态"""
    sensors = await storage.get_sensors()
    return {"sensors": sensors, "count": len(sensors)}


# ── 统计 ────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    """传输统计（总接收/转发/失败数，队列积压数）"""
    stats = await storage.get_stats()
    stats["online_gateways"] = len(gateway_status)
    return stats


# ── 待重传 ──────────────────────────────────────
@app.get("/api/pending")
async def get_pending():
    """查看待重传数据条数"""
    pending = await storage.get_pending_data(limit=200)
    return {"pending_count": len(pending)}


# ── 配置 ────────────────────────────────────────
@app.get("/api/config")
def get_config():
    return gateway_config


@app.put("/api/config")
def update_config(cfg: GatewayConfig):
    if cfg.main_system_url is not None:
        gateway_config["main_system_url"] = cfg.main_system_url
    if cfg.collect_interval is not None:
        gateway_config["collect_interval"] = cfg.collect_interval
    if cfg.thresholds is not None:
        gateway_config["thresholds"].update(cfg.thresholds)
    return {"success": True, "config": gateway_config}


# ── 模拟上传（测试用） ───────────────────────────
@app.post("/api/simulate/upload")
async def simulate_upload(gateway_id: str = "gateway_001"):
    import random

    now = datetime.now().isoformat()
    sensors = [
        SensorData(
            device_id=f"device_{i}",
            timestamp=now,
            pressure=round(random.uniform(0.5, 2.0), 2),
            flow=round(random.uniform(5.0, 15.0), 2),
            temperature=round(random.uniform(30.0, 60.0), 2),
            status="normal",
        )
        for i in range(1, 4)
    ]
    data = EdgeGatewayData(gateway_id=gateway_id, timestamp=now, sensors=sensors)
    return await upload_data(data, BackgroundTasks())


# ── WebSocket 实时推流 ──────────────────────────
@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # 保持连接，前端发送任意数据（ping/pong）不处理
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
