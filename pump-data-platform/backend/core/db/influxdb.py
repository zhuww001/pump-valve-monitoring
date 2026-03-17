from ..config import settings

# 创建InfluxDB客户端
influxdb_client = None

# 模拟InfluxDB客户端类
class MockInfluxDBClient:
    def write_api(self):
        return MockWriteAPI()
    
    def query_api(self):
        return MockQueryAPI()
    
    def close(self):
        pass

# 模拟WriteAPI类
class MockWriteAPI:
    def write(self, bucket, org, record):
        pass
    
    def close(self):
        pass

# 模拟QueryAPI类
class MockQueryAPI:
    def query(self, query, org):
        return []


def init_influxdb_client():
    """初始化InfluxDB客户端"""
    global influxdb_client
    if not settings.LOCAL_MODE:
        from influxdb_client import InfluxDBClient
        influxdb_client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )

def get_influxdb_client():
    """获取InfluxDB客户端"""
    # 本地运行模式下返回模拟客户端
    if settings.LOCAL_MODE:
        return MockInfluxDBClient()
    
    global influxdb_client
    if influxdb_client is None:
        init_influxdb_client()
    return influxdb_client
