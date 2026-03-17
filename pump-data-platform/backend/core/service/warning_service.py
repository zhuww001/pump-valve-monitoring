from typing import List, Dict
from datetime import datetime, timedelta
import random
from ..db import get_postgres_connection
from ..config import settings


class WarningService:
    """预警管理服务"""
    
    @staticmethod
    def get_warning_list() -> List[Dict]:
        """获取预警列表"""
        # 本地运行模式下返回模拟数据
        if settings.LOCAL_MODE:
            warnings = []
            warning_types = ["pressure", "flow", "temperature"]
            device_ids = ["device_1", "device_2", "device_3"]
            
            # 生成10条模拟预警记录
            for i in range(10):
                warning_type = random.choice(warning_types)
                device_id = random.choice(device_ids)
                
                # 根据预警类型生成对应的值和阈值
                if warning_type == "pressure":
                    threshold = settings.PRESSURE_THRESHOLD
                    warning_value = round(random.uniform(threshold + 0.1, threshold + 1.0), 2)
                elif warning_type == "flow":
                    threshold = settings.FLOW_THRESHOLD
                    warning_value = round(random.uniform(threshold - 2.0, threshold - 0.1), 2)
                else:  # temperature
                    threshold = settings.TEMPERATURE_THRESHOLD
                    warning_value = round(random.uniform(threshold + 1.0, threshold + 10.0), 2)
                
                # 随机生成状态
                status = random.choice(["unprocessed", "processed"])
                
                # 生成随机时间
                created_at = datetime.now() - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 59))
                
                warnings.append({
                    "id": i + 1,
                    "device_id": device_id,
                    "warning_type": warning_type,
                    "warning_value": warning_value,
                    "threshold": threshold,
                    "status": status,
                    "created_at": created_at.isoformat(),
                    "updated_at": created_at.isoformat()
                })
            
            # 按创建时间排序
            warnings.sort(key=lambda x: x["created_at"], reverse=True)
            
            return warnings
        
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            
            # 查询预警列表
            query = "SELECT * FROM warning_record ORDER BY created_at DESC"
            cursor.execute(query)
            
            # 处理结果
            warnings = []
            for row in cursor.fetchall():
                warnings.append({
                    "id": row[0],
                    "device_id": row[1],
                    "warning_type": row[2],
                    "warning_value": row[3],
                    "threshold": row[4],
                    "status": row[5],
                    "created_at": row[6].isoformat(),
                    "updated_at": row[7].isoformat()
                })
            
            cursor.close()
            return warnings
        except Exception as e:
            print(f"获取预警列表失败: {e}")
            # 返回空列表
            return []
    
    @staticmethod
    def update_warning_status(warning_id: int, status: str) -> bool:
        """更新预警状态"""
        # 本地运行模式下直接返回成功
        if settings.LOCAL_MODE:
            return True
        
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            
            # 更新状态
            query = """
                UPDATE warning_record SET 
                    status = %s, 
                    updated_at = NOW()
                WHERE id = %s
            """
            
            cursor.execute(query, (status, warning_id))
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"更新预警状态失败: {e}")
            return False
