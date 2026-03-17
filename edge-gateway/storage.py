#!/usr/bin/env python3
"""
本地 SQLite 缓冲 + 重试队列持久化
"""

import aiosqlite
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "edge_data.db"


class EdgeStorage:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """建表（幂等）"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    pressure REAL NOT NULL,
                    flow REAL NOT NULL,
                    temperature REAL NOT NULL,
                    status TEXT DEFAULT 'normal',
                    gateway_id TEXT NOT NULL,
                    forwarded INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS gateway_stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_received INTEGER DEFAULT 0,
                    total_forwarded INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            """)
            # 确保统计行存在
            await db.execute("""
                INSERT OR IGNORE INTO gateway_stats (id, total_received, total_forwarded, total_failed, last_updated)
                VALUES (1, 0, 0, 0, ?)
            """, (datetime.now().isoformat(),))
            await db.commit()

    async def save_data(self, record: Dict) -> int:
        """保存一条传感器数据，返回插入的 id"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO sensor_data
                    (device_id, timestamp, pressure, flow, temperature, status, gateway_id, forwarded, retry_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
            """, (
                record["device_id"],
                record["timestamp"],
                record["pressure"],
                record["flow"],
                record["temperature"],
                record.get("status", "normal"),
                record["gateway_id"],
                datetime.now().isoformat(),
            ))
            await db.execute("""
                UPDATE gateway_stats SET total_received = total_received + 1, last_updated = ? WHERE id = 1
            """, (datetime.now().isoformat(),))
            await db.commit()
            return cursor.lastrowid

    async def get_pending_data(self, limit: int = 50) -> List[Dict]:
        """获取待重传数据（未转发且重试次数 <= 5）"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM sensor_data
                WHERE forwarded = 0 AND retry_count <= 5
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def mark_forwarded(self, ids: List[int]):
        """标记为已成功转发"""
        if not ids:
            return
        placeholders = ",".join("?" * len(ids))
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE sensor_data SET forwarded = 1 WHERE id IN ({placeholders})
            """, ids)
            await db.execute("""
                UPDATE gateway_stats
                SET total_forwarded = total_forwarded + ?, last_updated = ?
                WHERE id = 1
            """, (len(ids), datetime.now().isoformat()))
            await db.commit()

    async def increment_retry(self, record_id: int):
        """重试计数 +1，超过 5 次时标记失败"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE sensor_data SET retry_count = retry_count + 1 WHERE id = ?
            """, (record_id,))
            # 超过5次重试，计入失败统计
            row = await (await db.execute(
                "SELECT retry_count FROM sensor_data WHERE id = ?", (record_id,)
            )).fetchone()
            if row and row[0] >= 5:
                await db.execute("""
                    UPDATE gateway_stats SET total_failed = total_failed + 1, last_updated = ? WHERE id = 1
                """, (datetime.now().isoformat(),))
            await db.commit()

    async def get_stats(self) -> Dict:
        """获取统计数字"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            stats_row = await (await db.execute(
                "SELECT * FROM gateway_stats WHERE id = 1"
            )).fetchone()
            pending_count = (await (await db.execute(
                "SELECT COUNT(*) FROM sensor_data WHERE forwarded = 0 AND retry_count <= 5"
            )).fetchone())[0]

            stats = dict(stats_row) if stats_row else {}
            stats["pending_count"] = pending_count
            return stats

    async def get_sensors(self) -> List[Dict]:
        """列出所有已上报过的传感器及最新状态"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT device_id, gateway_id, pressure, flow, temperature, status, timestamp
                FROM sensor_data
                WHERE id IN (
                    SELECT MAX(id) FROM sensor_data GROUP BY device_id
                )
                ORDER BY device_id
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
