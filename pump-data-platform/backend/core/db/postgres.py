from ..config import settings

# 创建数据库连接池
conn_pool = None

# 模拟数据库连接类
class MockConnection:
    def cursor(self):
        return MockCursor()
    
    def commit(self):
        pass
    
    def close(self):
        pass

# 模拟游标类
class MockCursor:
    def execute(self, query, params=None):
        pass
    
    def fetchall(self):
        return []
    
    def close(self):
        pass

def init_postgres_pool():
    """初始化PostgreSQL连接池"""
    global conn_pool
    if not settings.LOCAL_MODE:
        import psycopg2
        from psycopg2 import pool
        conn_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )

def get_postgres_connection():
    """获取PostgreSQL连接"""
    # 本地运行模式下返回模拟连接
    if settings.LOCAL_MODE:
        return MockConnection()
    
    global conn_pool
    if conn_pool is None:
        init_postgres_pool()
    return conn_pool.getconn()

def release_postgres_connection(conn):
    """释放PostgreSQL连接"""
    global conn_pool
    if not settings.LOCAL_MODE and conn_pool is not None:
        conn_pool.putconn(conn)
