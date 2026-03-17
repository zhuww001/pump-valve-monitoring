#!/bin/bash

# 启动泵阀管道堵塞预警系统统一数据后台
echo "正在启动泵阀管道堵塞预警系统统一数据后台..."

docker-compose up -d

echo "启动完成！"
echo "前端页面地址: http://localhost"
echo "后端API地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"
