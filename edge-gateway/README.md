# 边缘计算数据采集网关

## 简介

边缘计算数据采集网关是一个独立的服务，用于接收来自传感器设备的数据，并将数据转发到泵阀监控系统主系统。

## 架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   传感器设备     │────▶│   边缘计算网关    │────▶│  数据采集后台    │
│  (压力/流量/温度)│     │  (数据预处理/缓存) │     │ (数据接收/转发)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────┐
                                               │  泵阀监控系统    │
                                               │  (主系统)        │
                                               └─────────────────┘
```

## 功能特性

- **数据采集**：接收来自传感器设备的数据
- **数据预处理**：数据校验、单位转换、状态判断
- **数据缓存**：本地缓存，支持断网续传
- **数据转发**：通过HTTP API将数据转发到主系统
- **网关管理**：支持多网关接入，网关状态监控

## 快速开始

### 1. 安装依赖

```bash
cd edge-gateway
pip install -r requirements.txt
```

### 2. 启动边缘网关服务

```bash
python main.py
```

服务将在 http://localhost:8001 启动

### 3. 启动模拟客户端（测试用）

```bash
python client.py
```

客户端将模拟传感器数据采集，并上报到边缘网关服务

## API接口

### 数据上传

**POST** `/api/data/upload`

接收边缘网关上传的传感器数据

**请求参数：**

```json
{
  "gateway_id": "gateway_001",
  "timestamp": "2026-03-16T10:00:00",
  "sensors": [
    {
      "device_id": "device_1",
      "timestamp": "2026-03-16T10:00:00",
      "pressure": 1.2,
      "flow": 10.5,
      "temperature": 45.0,
      "status": "normal",
      "source_type": "edge_gateway"
    }
  ]
}
```

**响应：**

```json
{
  "success": true,
  "message": "数据接收成功",
  "gateway_id": "gateway_001",
  "sensor_count": 1
}
```

### 网关状态查询

**GET** `/api/gateways`

获取所有网关状态

**GET** `/api/gateways/{gateway_id}`

获取指定网关状态

### 健康检查

**GET** `/health`

服务健康检查

## 配置

通过环境变量配置：

- `MAIN_SYSTEM_URL`: 主系统地址（默认：http://localhost:8000）

## 数据流

1. **传感器数据采集**：边缘网关定期从传感器采集数据
2. **数据预处理**：对数据进行校验、转换、状态判断
3. **数据上报**：通过HTTP POST将数据发送到主系统
4. **数据存储**：主系统接收数据并存储到Redis/InfluxDB

## 与主系统对接

主系统需要提供以下API接口：

**POST** `/api/data/receive`

接收来自边缘网关的数据

**请求参数：**

```json
{
  "device_id": "device_1",
  "timestamp": "2026-03-16T10:00:00",
  "pressure": 1.2,
  "flow": 10.5,
  "temperature": 45.0,
  "status": "normal",
  "source_type": "edge_gateway",
  "gateway_id": "gateway_001"
}
```

## 生产环境部署

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  edge-gateway:
    build: ./edge-gateway
    ports:
      - "8001:8001"
    environment:
      - MAIN_SYSTEM_URL=http://main-system:8000
    networks:
      - pump-network

networks:
  pump-network:
    external: true
```

## 注意事项

1. **网络稳定性**：边缘网关需要稳定的网络连接到主系统
2. **数据缓存**：建议配置本地缓存，支持断网续传
3. **安全性**：生产环境建议添加API认证机制
4. **监控**：建议添加网关状态监控和告警

## 开发计划

- [ ] 添加MQTT协议支持
- [ ] 添加Modbus协议支持
- [ ] 实现断网续传功能
- [ ] 添加数据压缩功能
- [ ] 添加API认证机制
