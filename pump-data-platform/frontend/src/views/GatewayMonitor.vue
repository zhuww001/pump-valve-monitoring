<template>
  <div class="gateway-monitor">
    <h2>边缘网关监控</h2>

    <!-- 顶部状态栏 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.online_gateways ?? 0 }}</div>
          <div class="stat-label">网关在线</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.sensor_count ?? 0 }}</div>
          <div class="stat-label">传感器在线</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total_received ?? 0 }}</div>
          <div class="stat-label">今日接收</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total_forwarded ?? 0 }}</div>
          <div class="stat-label">已转发</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" :class="{ 'stat-warn': (stats.pending_count ?? 0) > 0 }">
          <div class="stat-value">{{ stats.pending_count ?? 0 }}</div>
          <div class="stat-label">待重传</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">
            <el-tag :type="mainSystemOnline ? 'success' : 'danger'" size="large">
              {{ mainSystemOnline ? '已连接' : '断开' }}
            </el-tag>
          </div>
          <div class="stat-label">主系统</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网关 + 传感器卡片 -->
    <h3 class="section-title">网关与传感器</h3>
    <el-empty v-if="gateways.length === 0" description="暂无网关数据" />
    <el-row :gutter="16">
      <el-col :span="8" v-for="gw in gateways" :key="gw.gateway_id">
        <el-card class="gw-card" :class="{ 'gw-offline': gw.status !== 'online' }">
          <template #header>
            <div class="card-header">
              <span class="gw-id">{{ gw.gateway_id }}</span>
              <el-tag :type="gw.status === 'online' ? 'success' : 'danger'" size="small">
                {{ gw.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </div>
          </template>
          <div class="gw-meta">
            <div><span class="meta-label">传感器数：</span>{{ gw.sensor_count }}</div>
            <div><span class="meta-label">最后上报：</span>{{ formatTime(gw.last_report) }}</div>
          </div>

          <!-- 该网关传感器读数 -->
          <div v-if="sensorsOf(gw.gateway_id).length > 0" class="sensor-list">
            <el-divider content-position="left">传感器读数</el-divider>
            <el-table :data="sensorsOf(gw.gateway_id)" size="small" :show-header="true">
              <el-table-column prop="device_id" label="设备" width="100" />
              <el-table-column label="压力(MPa)" width="90">
                <template #default="{ row }">{{ row.pressure?.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column label="流量(m³/h)" width="90">
                <template #default="{ row }">{{ row.flow?.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column label="温度(°C)" width="80">
                <template #default="{ row }">{{ row.temperature?.toFixed(1) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时数据流 -->
    <h3 class="section-title">
      实时数据流
      <el-tag size="small" :type="wsConnected ? 'success' : 'danger'" style="margin-left:8px">
        {{ wsConnected ? 'WebSocket 已连接' : 'WebSocket 断开' }}
      </el-tag>
    </h3>
    <el-card>
      <el-table :data="streamData" size="small" max-height="340" :show-header="true">
        <el-table-column prop="device_id" label="设备ID" width="110" />
        <el-table-column prop="gateway_id" label="网关" width="110" />
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
        </el-table-column>
        <el-table-column label="压力(MPa)" width="100">
          <template #default="{ row }">{{ row.pressure?.toFixed(3) }}</template>
        </el-table-column>
        <el-table-column label="流量(m³/h)" width="100">
          <template #default="{ row }">{{ row.flow?.toFixed(3) }}</template>
        </el-table-column>
        <el-table-column label="温度(°C)" width="90">
          <template #default="{ row }">{{ row.temperature?.toFixed(1) }}</template>
        </el-table-column>
        <el-table-column label="已转发" width="80">
          <template #default="{ row }">
            <el-tag :type="row.forwarded ? 'success' : 'warning'" size="small">
              {{ row.forwarded ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 操作区 -->
    <div class="action-bar">
      <el-button type="primary" @click="switchToEdgeSource">
        切换主系统数据源为边缘网关
      </el-button>
      <span class="action-hint">将主系统的数据接入方式切换为边缘网关上报模式</span>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const EDGE_BASE = 'http://localhost:8001'
const MAIN_BASE = '' // 同源，走 vite proxy
const STREAM_MAX = 50

export default {
  name: 'GatewayMonitor',
  data() {
    return {
      stats: {},
      gateways: [],
      sensors: [],
      streamData: [],
      wsConnected: false,
      mainSystemOnline: false,
      ws: null,
      refreshTimer: null,
    }
  },
  mounted() {
    this.fetchAll()
    this.connectWs()
    this.refreshTimer = setInterval(() => this.fetchAll(), 5000)
  },
  beforeUnmount() {
    clearInterval(this.refreshTimer)
    if (this.ws) this.ws.close()
  },
  methods: {
    async fetchAll() {
      await Promise.allSettled([
        this.fetchStats(),
        this.fetchGateways(),
        this.fetchSensors(),
        this.checkMainSystem(),
      ])
    },
    async fetchStats() {
      try {
        const { data } = await axios.get(`${EDGE_BASE}/api/stats`)
        this.stats = data
      } catch { /* ignore */ }
    },
    async fetchGateways() {
      try {
        const { data } = await axios.get(`${EDGE_BASE}/api/gateways`)
        this.gateways = data
      } catch { /* ignore */ }
    },
    async fetchSensors() {
      try {
        const { data } = await axios.get(`${EDGE_BASE}/api/sensors`)
        this.sensors = data.sensors ?? []
        // 统计传感器数量
        this.stats = { ...this.stats, sensor_count: this.sensors.length }
      } catch { /* ignore */ }
    },
    async checkMainSystem() {
      try {
        await axios.get('/api/device/list', { timeout: 3000 })
        this.mainSystemOnline = true
      } catch {
        this.mainSystemOnline = false
      }
    },
    connectWs() {
      try {
        this.ws = new WebSocket('ws://localhost:8001/ws/stream')
        this.ws.onopen = () => { this.wsConnected = true }
        this.ws.onclose = () => {
          this.wsConnected = false
          // 5 秒后重连
          setTimeout(() => this.connectWs(), 5000)
        }
        this.ws.onerror = () => { this.wsConnected = false }
        this.ws.onmessage = (ev) => {
          try {
            const msg = JSON.parse(ev.data)
            this.streamData.unshift(msg)
            if (this.streamData.length > STREAM_MAX) {
              this.streamData = this.streamData.slice(0, STREAM_MAX)
            }
          } catch { /* ignore */ }
        }
      } catch { /* ignore */ }
    },
    sensorsOf(gatewayId) {
      return this.sensors.filter(s => s.gateway_id === gatewayId)
    },
    formatTime(ts) {
      if (!ts) return '—'
      try {
        return new Date(ts).toLocaleString('zh-CN', {
          month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', second: '2-digit',
          hour12: false,
        })
      } catch { return ts }
    },
    async switchToEdgeSource() {
      try {
        await axios.post('/api/data-source/switch', { type: 'report' })
        this.$message.success('已切换主系统数据源为边缘网关上报模式')
      } catch (e) {
        this.$message.error('切换失败：' + (e.response?.data?.detail ?? e.message))
      }
    },
  },
}
</script>

<style scoped>
.gateway-monitor {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-card.stat-warn {
  border-color: #e6a23c;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.section-title {
  margin: 20px 0 12px;
  color: #303133;
  font-weight: 600;
}

.gw-card {
  margin-bottom: 16px;
}

.gw-card.gw-offline {
  opacity: 0.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gw-id {
  font-weight: bold;
  font-size: 15px;
}

.gw-meta {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.meta-label {
  font-weight: bold;
}

.sensor-list {
  margin-top: 8px;
}

.action-bar {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-hint {
  font-size: 13px;
  color: #909399;
}
</style>
