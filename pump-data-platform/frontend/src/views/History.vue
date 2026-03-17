<template>
  <div class="history">
    <h2>历史数据</h2>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="设备">
          <el-select v-model="filterForm.device_id" placeholder="请选择设备" style="width:160px" @change="loadHistoryData">
            <el-option
              v-for="d in devices"
              :key="d.device_id"
              :label="d.name"
              :value="d.device_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
            <el-radio-button label="1h">1小时</el-radio-button>
            <el-radio-button label="24h">24小时</el-radio-button>
            <el-radio-button label="72h">72小时</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始时间" v-if="timeRange === 'custom'">
          <el-date-picker
            v-model="filterForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="结束时间" v-if="timeRange === 'custom'">
          <el-date-picker
            v-model="filterForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistoryData">查询</el-button>
          <el-button @click="exportData">导出</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- Tab页 -->
    <el-card style="margin-top: 20px;">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="趋势图" name="chart">
          <!-- 数据趋势图表 -->
          <div ref="chartRef" class="chart-container"></div>
        </el-tab-pane>
        <el-tab-pane label="数据列表" name="table">
          <!-- 数据表格 -->
          <el-table :data="historyData" style="width: 100%">
            <el-table-column prop="timestamp" label="时间" width="200">
              <template #default="scope">
                {{ formatDateTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="pressure" label="压力 (MPa)" />
            <el-table-column prop="flow" label="流量 (m³/h)" />
            <el-table-column prop="temperature" label="温度 (°C)" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'normal' ? 'success' : 'warning'">
                  {{ scope.row.status === 'normal' ? '正常' : '预警' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source_type" label="数据源" />
          </el-table>
          <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'History',
  data() {
    return {
      devices: [],
      timeRange: '1h', // 默认1小时
      activeTab: 'chart', // 默认显示趋势图
      filterForm: {
        device_id: '',
        start_time: new Date(Date.now() - 3600000), // 1小时前
        end_time: new Date()
      },
      historyData: [],
      pagination: {
        currentPage: 1,
        pageSize: 20
      },
      total: 0,
      chart: null
    }
  },
  computed: {
    routeDeviceId() {
      return this.$route.params.device_id
    },
    currentDeviceName() {
      const device = this.devices.find(d => d.device_id === this.filterForm.device_id)
      return device ? device.name : ''
    }
  },
  mounted() {
    this.loadDevices()
    this.initChart()
  },
  watch: {
    routeDeviceId: {
      handler(newVal) {
        if (newVal) {
          this.filterForm.device_id = newVal
          this.loadHistoryData()
        }
      },
      immediate: true
    }
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose()
    }
  },
  methods: {
    async loadDevices() {
      try {
        const response = await axios.get('/api/device/list')
        this.devices = response.data
        if (this.routeDeviceId) {
          this.filterForm.device_id = this.routeDeviceId
        } else if (!this.filterForm.device_id && this.devices.length > 0) {
          this.filterForm.device_id = this.devices[0].device_id
        }
        this.loadHistoryData()
      } catch (error) {
        console.error('获取设备列表失败:', error)
      }
    },
    async loadHistoryData() {
      if (!this.filterForm.device_id) return
      
      try {
        const response = await axios.get(`/api/data/history/${this.filterForm.device_id}`, {
          params: {
            start_time: this.filterForm.start_time.toISOString(),
            end_time: this.filterForm.end_time.toISOString()
          }
        })
        
        this.historyData = response.data
        this.total = this.historyData.length
        this.updateChart()
      } catch (error) {
        console.error('获取历史数据失败:', error)
      }
    },
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef)
      this.chart.setOption({
        title: {
          text: '历史数据趋势',
          left: 'center',
          top: 4,
          textStyle: { fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } },
          formatter(params) {
            if (!params.length) return ''
            const ts = params[0].value[0]
            const d = new Date(ts)
            const pad = n => String(n).padStart(2, '0')
            const time = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
            let html = `<div style="font-weight:bold;margin-bottom:4px">${time}</div>`
            params.forEach(p => {
              html += `<div>${p.marker}${p.seriesName}：<b>${p.value[1]}</b></div>`
            })
            return html
          }
        },
        legend: {
          data: ['压力 (MPa)', '流量 (m³/h)', '温度 (°C)'],
          top: 28
        },
        grid: { left: 70, right: 100, top: 72, bottom: 58 },
        dataZoom: [
          { type: 'inside', xAxisIndex: 0, filterMode: 'filter' },
          { type: 'slider', xAxisIndex: 0, bottom: 4, height: 22, borderColor: 'transparent' }
        ],
        xAxis: {
          type: 'time',
          boundaryGap: false,
          splitLine: { show: false },
          axisLabel: {
            rotate: 20,
            fontSize: 11,
            formatter(value) {
              const d = new Date(value)
              const pad = n => String(n).padStart(2, '0')
              return `${pad(d.getMonth()+1)}-${pad(d.getDate())}\n${pad(d.getHours())}:${pad(d.getMinutes())}`
            }
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '压力(MPa)',
            nameTextStyle: { fontSize: 11, color: '#5470c6' },
            axisLine: { show: true, lineStyle: { color: '#5470c6' } },
            axisLabel: { color: '#5470c6', fontSize: 11 },
            splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
          },
          {
            type: 'value',
            name: '流量(m³/h)',
            position: 'right',
            nameTextStyle: { fontSize: 11, color: '#91cc75' },
            axisLine: { show: true, lineStyle: { color: '#91cc75' } },
            axisLabel: { color: '#91cc75', fontSize: 11 },
            splitLine: { show: false }
          },
          {
            type: 'value',
            name: '温度(°C)',
            position: 'right',
            offset: 68,
            nameTextStyle: { fontSize: 11, color: '#ee6666' },
            axisLine: { show: true, lineStyle: { color: '#ee6666' } },
            axisLabel: { color: '#ee6666', fontSize: 11 },
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: '压力 (MPa)',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, color: '#5470c6' },
            itemStyle: { color: '#5470c6' },
            data: []
          },
          {
            name: '流量 (m³/h)',
            type: 'line',
            smooth: true,
            symbol: 'none',
            yAxisIndex: 1,
            lineStyle: { width: 2, color: '#91cc75' },
            itemStyle: { color: '#91cc75' },
            data: []
          },
          {
            name: '温度 (°C)',
            type: 'line',
            smooth: true,
            symbol: 'none',
            yAxisIndex: 2,
            lineStyle: { width: 2, color: '#ee6666' },
            itemStyle: { color: '#ee6666' },
            data: []
          }
        ]
      })
    },
    updateChart() {
      const toMs = ts => new Date(ts).getTime()
      const pressure    = this.historyData.map(item => [toMs(item.timestamp), item.pressure])
      const flow        = this.historyData.map(item => [toMs(item.timestamp), item.flow])
      const temperature = this.historyData.map(item => [toMs(item.timestamp), item.temperature])

      this.chart.setOption({
        series: [
          { name: '压力 (MPa)',   data: pressure },
          { name: '流量 (m³/h)',  data: flow },
          { name: '温度 (°C)',    data: temperature }
        ]
      })
    },
    exportData() {
      // 简单的CSV导出功能
      if (this.historyData.length === 0) {
        this.$message.warning('没有数据可导出')
        return
      }
      
      const headers = ['时间', '压力 (MPa)', '流量 (m³/h)', '温度 (°C)', '状态', '数据源']
      const rows = this.historyData.map(item => [
        item.timestamp,
        item.pressure,
        item.flow,
        item.temperature,
        item.status === 'normal' ? '正常' : '预警',
        item.source_type
      ])
      
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.setAttribute('href', url)
      link.setAttribute('download', `history_${this.filterForm.device_id}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    handleSizeChange(size) {
      this.pagination.pageSize = size
    },
    handleCurrentChange(current) {
      this.pagination.currentPage = current
    },
    handleTimeRangeChange(value) {
      const now = new Date()
      switch (value) {
        case '1h':
          this.filterForm.start_time = new Date(now.getTime() - 3600000) // 1小时前
          this.filterForm.end_time = now
          break
        case '24h':
          this.filterForm.start_time = new Date(now.getTime() - 24 * 3600000) // 24小时前
          this.filterForm.end_time = now
          break
        case '72h':
          this.filterForm.start_time = new Date(now.getTime() - 72 * 3600000) // 72小时前
          this.filterForm.end_time = now
          break
        case 'custom':
          // 保持当前时间范围不变
          break
      }
      // 自动加载数据
      if (this.filterForm.device_id) {
        this.loadHistoryData()
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  }
}
</script>

<style scoped>
.history {
  padding: 0;
}

.filter-form {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
