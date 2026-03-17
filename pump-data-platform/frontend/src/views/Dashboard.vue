<template>
  <div class="dashboard">
    <h2>实时监控</h2>
    
    <!-- 设备状态卡片 -->
    <el-row :gutter="20">
      <el-col :span="8" v-for="device in devices" :key="device.device_id">
        <el-card :body-style="{ padding: '20px' }" :class="{ 'warning-card': device.status === 'warning' }">
          <template #header>
            <div class="card-header">
              <span>{{ device.name }}</span>
              <div style="display:flex;align-items:center;gap:6px">
                <el-tag size="small" type="info" v-if="device.realtime_data?.source_type === 'edge_gateway'">边缘</el-tag>
                <el-tag size="small" type="success" v-else-if="device.realtime_data?.source_type === 'simulate'">模拟</el-tag>
                <el-tag :type="device.status === 'normal' ? 'success' : 'warning'">
                  {{ device.status === 'normal' ? '正常' : '预警' }}
                </el-tag>
              </div>
            </div>
          </template>
          <div class="card-body">
            <div class="data-item">
              <span class="label">位置：</span>
              <span class="value">{{ device.location }}</span>
            </div>
            <div class="data-item">
              <span class="label">压力：</span>
              <span class="value">{{ device.realtime_data?.pressure || 0 }} MPa</span>
            </div>
            <div class="data-item">
              <span class="label">流量：</span>
              <span class="value">{{ device.realtime_data?.flow || 0 }} m³/h</span>
            </div>
            <div class="data-item">
              <span class="label">温度：</span>
              <span class="value">{{ device.realtime_data?.temperature || 0 }} °C</span>
            </div>
            <div class="data-item">
              <span class="label">更新时间：</span>
              <span class="value">{{ formatDateTime(device.realtime_data?.timestamp) || '无数据' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数据趋势图表 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据趋势</span>
          <el-select v-model="selectedDevice" placeholder="选择设备" v-if="!routeDeviceId">
            <el-option 
              v-for="device in devices" 
              :key="device.device_id" 
              :label="device.name" 
              :value="device.device_id"
            />
          </el-select>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  data() {
    return {
      devices: [],
      selectedDevice: '',
      chart: null
    }
  },
  computed: {
    routeDeviceId() {
      return this.$route.params.device_id
    }
  },
  mounted() {
    this.loadDevices()
    this.initChart()
    // 定时更新数据
    this.interval = setInterval(() => {
      this.loadDevices()
      this.updateChart()
    }, 5000)
  },
  beforeUnmount() {
    clearInterval(this.interval)
    if (this.chart) {
      this.chart.dispose()
    }
  },
  methods: {
    async loadDevices() {
      try {
        if (this.routeDeviceId) {
          const device = (await axios.get(`/api/device/${this.routeDeviceId}`)).data
          try {
            device.realtime_data = (await axios.get(`/api/data/realtime/${device.device_id}`)).data
          } catch (error) {
            console.error(`获取设备 ${device.name} 实时数据失败:`, error)
          }
          this.devices = [device]
          this.selectedDevice = device.device_id
          this.updateChart()
        } else {
          const devices = (await axios.get('/api/device/list')).data
          // 并行获取所有设备实时数据
          await Promise.all(
            devices.map(async (device) => {
              try {
                device.realtime_data = (await axios.get(`/api/data/realtime/${device.device_id}`)).data
              } catch (error) {
                console.error(`获取设备 ${device.name} 实时数据失败:`, error)
              }
            })
          )
          this.devices = devices
          if (devices.length > 0 && !this.selectedDevice) {
            this.selectedDevice = devices[0].device_id
            this.updateChart()
          }
        }
      } catch (error) {
        console.error('获取设备列表失败:', error)
      }
    },
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef)
      this.chart.setOption({
        title: {
          text: '实时数据趋势'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['压力', '流量', '温度']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: []
        },
        yAxis: [
          {
            type: 'value',
            name: '压力 (MPa)'
          },
          {
            type: 'value',
            name: '流量 (m³/h)'
          },
          {
            type: 'value',
            name: '温度 (°C)'
          }
        ],
        series: [
          {
            name: '压力',
            type: 'line',
            data: []
          },
          {
            name: '流量',
            type: 'line',
            yAxisIndex: 1,
            data: []
          },
          {
            name: '温度',
            type: 'line',
            yAxisIndex: 2,
            data: []
          }
        ]
      })
    },
    async updateChart() {
      if (!this.selectedDevice) return
      
      try {
        // 模拟历史数据
        const now = new Date()
        const start = new Date(now.getTime() - 3600000) // 1小时前
        
        const response = await axios.get(`/api/data/history/${this.selectedDevice}`, {
          params: {
            start_time: start.toISOString(),
            end_time: now.toISOString()
          }
        })
        
        const data = response.data
        const timestamps = data.map(item => item.timestamp)
        const pressure = data.map(item => item.pressure)
        const flow = data.map(item => item.flow)
        const temperature = data.map(item => item.temperature)
        
        this.chart.setOption({
          xAxis: {
            data: timestamps
          },
          series: [
            {
              name: '压力',
              data: pressure
            },
            {
              name: '流量',
              data: flow
            },
            {
              name: '温度',
              data: temperature
            }
          ]
        })
      } catch (error) {
        console.error('更新图表失败:', error)
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) return ''
      return new Date(timestamp).toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false,
      }).replace(/\//g, '-')
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-body {
  margin-top: 10px;
}

.data-item {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}

.label {
  font-weight: bold;
  color: #606266;
}

.value {
  color: #303133;
}

.warning-card {
  border-color: #e6a23c;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
