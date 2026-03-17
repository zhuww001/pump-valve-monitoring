#!/bin/bash
# 泵阀管道堵塞预警系统 - 一键启动脚本

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 模式选择
MODE="local"
WITH_EDGE=true
WITH_PLATFORM=true
SKIP_INSTALL=false

for arg in "$@"; do
    case $arg in
        --docker)   MODE="docker" ;;
        --simple)   WITH_PLATFORM=false ;;
        --no-edge)  WITH_EDGE=false ;;
        --skip-install) SKIP_INSTALL=true ;;
        -h|--help)
            echo "用法: ./start.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --docker        使用 Docker Compose 启动（需要安装 Docker）"
            echo "  --simple        仅启动主监控服务（Flask，不含完整平台）"
            echo "  --no-edge       不启动边缘计算网关"
            echo "  --skip-install  跳过依赖安装步骤"
            echo "  -h, --help      显示帮助信息"
            echo ""
            echo "默认（无参数）：本地开发模式，启动所有服务"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║     泵阀管道堵塞预警系统  v1.0.0         ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ────────────────────────────────────────────
# Docker 模式
# ────────────────────────────────────────────
if [ "$MODE" == "docker" ]; then
    echo -e "${YELLOW}► Docker 模式${NC}"

    if ! command -v docker &>/dev/null; then
        echo -e "${RED}错误: 未检测到 Docker，请先安装 Docker Desktop${NC}"
        exit 1
    fi

    echo -e "${YELLOW}► 启动主系统（Docker Compose）...${NC}"
    cd "$ROOT_DIR/pump-data-platform"
    docker-compose up -d
    echo -e "${GREEN}✓ 主系统已启动${NC}"

    if [ "$WITH_EDGE" = true ]; then
        echo -e "${YELLOW}► 构建并启动边缘网关...${NC}"
        cd "$ROOT_DIR/edge-gateway"
        docker build -t edge-gateway . -q
        docker stop edge-gateway 2>/dev/null || true
        docker rm   edge-gateway 2>/dev/null || true
        docker run -d --name edge-gateway -p 8001:8001 \
            -e MAIN_SYSTEM_URL=http://host.docker.internal:8000 \
            edge-gateway
        echo -e "${GREEN}✓ 边缘网关已启动${NC}"
    fi

    echo ""
    echo -e "${GREEN}════════════════════════════════════${NC}"
    echo -e "${GREEN}  启动完成！访问地址：${NC}"
    echo -e "${GREEN}════════════════════════════════════${NC}"
    echo -e "  前端页面:  ${BLUE}http://localhost${NC}"
    echo -e "  后端 API:  ${BLUE}http://localhost:8000${NC}"
    echo -e "  API 文档:  ${BLUE}http://localhost:8000/docs${NC}"
    [ "$WITH_EDGE" = true ] && echo -e "  边缘网关:  ${BLUE}http://localhost:8001${NC}"
    echo ""
    echo -e "  停止服务: ${YELLOW}cd pump-data-platform && docker-compose down${NC}"
    exit 0
fi

# ────────────────────────────────────────────
# 本地开发模式
# ────────────────────────────────────────────
echo -e "${YELLOW}► 本地开发模式${NC}"

# 进程 PID 列表，用于退出时清理
PIDS=()

cleanup() {
    echo ""
    echo -e "${YELLOW}► 正在停止所有服务...${NC}"
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
    exit 0
}
trap cleanup INT TERM

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}错误: 未检测到 Python 3，请先安装 Python 3.8+${NC}"
    exit 1
fi

# 虚拟环境
VENV="$ROOT_DIR/.venv"
if [ ! -d "$VENV" ]; then
    echo -e "${YELLOW}► 创建 Python 虚拟环境...${NC}"
    python3 -m venv "$VENV"
fi
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

# 安装依赖
if [ "$SKIP_INSTALL" = false ]; then
    echo -e "${YELLOW}► 安装 Python 依赖...${NC}"
    # 主监控服务依赖（flask、pandas、pyyaml）
    $PIP install --quiet flask pandas pyyaml requests

    # 边缘网关依赖
    if [ "$WITH_EDGE" = true ]; then
        $PIP install --quiet -r "$ROOT_DIR/edge-gateway/requirements.txt"
    fi

    # 完整平台后端依赖（仅安装基础部分，数据库相关可选）
    if [ "$WITH_PLATFORM" = true ]; then
        $PIP install --quiet fastapi uvicorn pydantic pydantic-settings \
            python-dotenv requests websockets 2>/dev/null || true
    fi

    # 前端依赖
    if [ "$WITH_PLATFORM" = true ]; then
        if ! command -v node &>/dev/null; then
            echo -e "${RED}错误: 未检测到 Node.js，请安装 Node.js 16+ 或使用 --simple 模式${NC}"
            exit 1
        fi
        echo -e "${YELLOW}► 安装前端依赖...${NC}"
        cd "$ROOT_DIR/pump-data-platform/frontend"
        npm install --silent
    fi
fi

# 确保日志目录存在
mkdir -p "$ROOT_DIR/logs"

# ─── 启动服务 ───

# 1. 主监控服务（Flask，端口 5001）
echo -e "${YELLOW}► 启动主监控服务 (Flask :5001)...${NC}"
cd "$ROOT_DIR"
$PY app.py >"$ROOT_DIR/logs/flask.log" 2>&1 &
PIDS+=($!)

# 2. 完整平台后端（FastAPI，端口 8000）
if [ "$WITH_PLATFORM" = true ]; then
    echo -e "${YELLOW}► 启动后端 API 服务 (FastAPI :8000)...${NC}"
    cd "$ROOT_DIR/pump-data-platform/backend"
    $PY main.py >"$ROOT_DIR/logs/backend.log" 2>&1 &
    PIDS+=($!)

    # 3. 前端开发服务（Vite，端口 5173）
    echo -e "${YELLOW}► 启动前端开发服务 (Vite :5173)...${NC}"
    cd "$ROOT_DIR/pump-data-platform/frontend"
    npm run dev >"$ROOT_DIR/logs/frontend.log" 2>&1 &
    PIDS+=($!)
fi

# 4. 边缘计算网关（FastAPI，端口 8001）
if [ "$WITH_EDGE" = true ]; then
    echo -e "${YELLOW}► 启动边缘计算网关 (FastAPI :8001)...${NC}"
    cd "$ROOT_DIR/edge-gateway"
    $PY main.py >"$ROOT_DIR/logs/edge-gateway.log" 2>&1 &
    PIDS+=($!)
fi

# 等待服务启动
sleep 2

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  系统启动完成！访问地址：${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "  主监控界面:  ${BLUE}http://localhost:5001${NC}"
if [ "$WITH_PLATFORM" = true ]; then
    echo -e "  前端平台:    ${BLUE}http://localhost:5173${NC}"
    echo -e "  后端 API:    ${BLUE}http://localhost:8000${NC}"
    echo -e "  API 文档:    ${BLUE}http://localhost:8000/docs${NC}"
fi
[ "$WITH_EDGE" = true ] && echo -e "  边缘网关:    ${BLUE}http://localhost:8001${NC}"
echo ""
echo -e "  日志目录:    ${YELLOW}$ROOT_DIR/logs/${NC}"
echo -e "  按 ${RED}Ctrl+C${NC} 停止所有服务"
echo ""

# 阻塞等待，直到用户中断
wait
