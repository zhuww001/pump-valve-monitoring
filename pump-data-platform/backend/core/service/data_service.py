import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
from ..db import get_redis_client, get_influxdb_client
from ..config import settings
from ..data_process.warning_checker import WarningChecker



def _offline_response(device_id: str) -> Dict:
    return {
        "device_id": device_id,
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "pressure": 0.0,
        "flow": 0.0,
        "temperature": 0.0,
        "status": "offline",
        "source_type": "unknown",
    }


def _check_status(pressure: float, flow: float, temperature: float) -> str:
    status, _ = WarningChecker.check_warning(
        {"pressure": pressure, "flow": flow, "temperature": temperature}
    )
    return status


class DataService:
    """数据查询服务"""

    # 内存存储，用于接收边缘网关数据
    _received_data_cache: Dict = {}

    @staticmethod
    def get_realtime_data(device_id: str) -> Dict:
        """获取实时数据"""
        if settings.LOCAL_MODE:
            if device_id in DataService._received_data_cache:
                return DataService._received_data_cache[device_id]

            pressure = round(random.uniform(0.8, 1.5), 2)
            flow = round(random.uniform(8.0, 15.0), 2)
            temperature = round(random.uniform(35.0, 50.0), 2)
            return {
                "device_id": device_id,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "pressure": pressure,
                "flow": flow,
                "temperature": temperature,
                "status": _check_status(pressure, flow, temperature),
                "source_type": "simulate",
            }

        try:
            redis_client = get_redis_client()
            raw = redis_client.get(f"realtime:{device_id}")
            return json.loads(raw) if raw else _offline_response(device_id)
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return _offline_response(device_id)

    @staticmethod
    def get_history_data(device_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取历史数据"""
        if settings.LOCAL_MODE:
            history_data = []
            total_seconds = (end_time - start_time).total_seconds()
            # 动态步长：目标约 500 个数据点，最小 5 秒
            step_seconds = max(5, int(total_seconds / 500))
            step = timedelta(seconds=step_seconds)
            current_time = start_time
            while current_time <= end_time:
                pressure = round(random.uniform(0.8, 1.5), 2)
                flow = round(random.uniform(8.0, 15.0), 2)
                temperature = round(random.uniform(35.0, 50.0), 2)
                history_data.append({
                    "device_id": device_id,
                    "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "pressure": pressure,
                    "flow": flow,
                    "temperature": temperature,
                    "status": _check_status(pressure, flow, temperature),
                    "source_type": "simulate",
                })
                current_time += step
            return history_data

        try:
            client = get_influxdb_client()
            query_api = client.query_api()
            query = f"""
                from(bucket: '{settings.INFLUXDB_BUCKET}')
                |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
                |> filter(fn: (r) => r["_measurement"] == "pump_monitor")
                |> filter(fn: (r) => r["device_id"] == "{device_id}")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
            """
            result = query_api.query(query=query, org=settings.INFLUXDB_ORG)
            history_data = []
            for table in result:
                for record in table.records:
                    history_data.append({
                        "device_id": device_id,
                        "timestamp": record["_time"].isoformat(),
                        "pressure": record.get("pressure", 0.0),
                        "flow": record.get("flow", 0.0),
                        "temperature": record.get("temperature", 0.0),
                        "status": record.get("status", "normal"),
                        "source_type": record.get("source_type", "unknown"),
                    })
            return history_data
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return []

    @staticmethod
    def process_received_data(data: Dict) -> bool:
        """处理接收到的边缘网关数据"""
        try:
            device_id = data.get("device_id")
            if not device_id:
                print("接收到的数据缺少device_id")
                return False

            pressure = data.get("pressure", 0.0)
            flow = data.get("flow", 0.0)
            temperature = data.get("temperature", 0.0)
            data["status"] = _check_status(pressure, flow, temperature)

            if settings.LOCAL_MODE:
                DataService._received_data_cache[device_id] = data
                print(f"数据已缓存: {device_id}, 压力: {pressure}, 流量: {flow}, 温度: {temperature}")
                return True

            try:
                redis_client = get_redis_client()
                redis_client.setex(f"realtime:{device_id}", 3600, json.dumps(data))
                print(f"数据已存储到Redis: {device_id}")
            except Exception as e:
                print(f"存储到Redis失败，降级到内存缓存: {e}")
                DataService._received_data_cache[device_id] = data
            return True

        except Exception as e:
            print(f"处理接收数据失败: {e}")
            return False
