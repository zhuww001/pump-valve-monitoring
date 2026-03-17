from typing import List, Dict
from ..db import get_postgres_connection
from ..config import settings


# 本地模式使用的静态设备列表
_MOCK_DEVICES: List[Dict] = [
    {"id": 1, "device_id": "device_1", "name": "泵A", "location": "一号车间",
     "pressure_threshold": 2.0, "flow_threshold": 5.0, "temperature_threshold": 80.0, "status": "normal"},
    {"id": 2, "device_id": "device_2", "name": "泵B", "location": "二号车间",
     "pressure_threshold": 2.0, "flow_threshold": 5.0, "temperature_threshold": 80.0, "status": "normal"},
    {"id": 3, "device_id": "device_3", "name": "泵C", "location": "三号车间",
     "pressure_threshold": 2.0, "flow_threshold": 5.0, "temperature_threshold": 80.0, "status": "normal"},
]


def _row_to_device(row) -> Dict:
    return {
        "id": row[0],
        "device_id": row[1],
        "name": row[2],
        "location": row[3],
        "pressure_threshold": row[4],
        "flow_threshold": row[5],
        "temperature_threshold": row[6],
        "status": row[7],
        "created_at": row[8].isoformat(),
        "updated_at": row[9].isoformat(),
    }


class DeviceService:
    """设备管理服务"""

    @staticmethod
    def get_device_list() -> List[Dict]:
        """获取设备列表"""
        if settings.LOCAL_MODE:
            return _MOCK_DEVICES

        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM device")
            devices = [_row_to_device(row) for row in cursor.fetchall()]
            cursor.close()
            return devices
        except Exception as e:
            print(f"获取设备列表失败: {e}")
            return _MOCK_DEVICES

    @staticmethod
    def update_device_threshold(device_id: str, thresholds: Dict) -> bool:
        """更新设备阈值"""
        if settings.LOCAL_MODE:
            return True

        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE device SET
                    pressure_threshold = %s,
                    flow_threshold = %s,
                    temperature_threshold = %s,
                    updated_at = NOW()
                WHERE device_id = %s
                """,
                (
                    thresholds.get("pressure_threshold"),
                    thresholds.get("flow_threshold"),
                    thresholds.get("temperature_threshold"),
                    device_id,
                ),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"更新设备阈值失败: {e}")
            return False

    @staticmethod
    def get_device_by_id(device_id: str) -> Dict:
        """根据设备ID获取设备信息"""
        if settings.LOCAL_MODE:
            return next((d for d in _MOCK_DEVICES if d["device_id"] == device_id), {})

        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM device WHERE device_id = %s", (device_id,))
            row = cursor.fetchone()
            cursor.close()
            return _row_to_device(row) if row else {}
        except Exception as e:
            print(f"获取设备信息失败: {e}")
            return {}
