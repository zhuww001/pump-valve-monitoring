<template>
  <div class="config">
    <h2>配置中心</h2>
    
    <!-- 数据源配置 -->
    <el-card class="config-card" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据源配置</span>
        </div>
      </template>
      <el-form :model="dataSourceForm" label-width="120px">
        <el-form-item label="数据源类型">
          <el-radio-group v-model="dataSourceForm.type" @change="handleDataSourceChange">
            <el-radio label="simulate">模拟数据源</el-radio>
            <el-radio label="api">API数据源</el-radio>
            <el-radio label="report">设备上报数据源</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- API数据源配置 -->
        <el-collapse v-if="dataSourceForm.type === 'api'">
          <el-collapse-item title="API参数配置">
            <el-form-item label="API基础URL">
              <el-input v-model="dataSourceForm.config.api_base_url" placeholder="例如: http://localhost:8000" />
            </el-form-item>
            <el-form-item label="API Token">
              <el-input v-model="dataSourceForm.config.api_token" placeholder="API访问令牌" />
            </el-form-item>
            <el-form-item label="API端点">
              <el-input v-model="dataSourceForm.config.api_endpoint" placeholder="例如: /api/pump-data" />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
        
        <el-form-item>
          <el-button type="primary" @click="saveDataSourceConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 设备阈值配置 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>设备阈值配置</span>
        </div>
      </template>
      <el-form :model="thresholdForm" label-width="120px">
        <el-form-item label="选择设备">
          <el-select v-model="thresholdForm.device_id" placeholder="选择设备">
            <el-option 
              v-for="device in devices" 
              :key="device.device_id" 
              :label="device.name" 
              :value="device.device_id"
              @click="loadDeviceThresholds(device.device_id)"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="压力阈值 (MPa)">
          <el-input-number v-model="thresholdForm.pressure_threshold" :min="0" :step="0.1" />
        </el-form-item>
        <el-form-item label="流量阈值 (m³/h)">
          <el-input-number v-model="thresholdForm.flow_threshold" :min="0" :step="0.5" />
        </el-form-item>
        <el-form-item label="温度阈值 (°C)">
          <el-input-number v-model="thresholdForm.temperature_threshold" :min="0" :step="1" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveDeviceThresholds">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Config',
  data() {
    return {
      devices: [],
      dataSourceForm: {
        type: 'simulate',
        config: {
          api_base_url: '',
          api_token: '',
          api_endpoint: '/api/pump-data'
        }
      },
      thresholdForm: {
        device_id: '',
        pressure_threshold: 2.0,
        flow_threshold: 5.0,
        temperature_threshold: 80.0
      }
    }
  },
  mounted() {
    this.loadDevices()
    this.loadCurrentDataSource()
  },
  methods: {
    async loadDevices() {
      try {
        const response = await axios.get('/api/device/list')
        this.devices = response.data
        if (this.devices.length > 0 && !this.thresholdForm.device_id) {
          this.thresholdForm.device_id = this.devices[0].device_id
          this.loadDeviceThresholds(this.devices[0].device_id)
        }
      } catch (error) {
        console.error('获取设备列表失败:', error)
      }
    },
    async loadCurrentDataSource() {
      try {
        const response = await axios.get('/api/data-source/current')
        this.dataSourceForm.type = response.data.type
        this.dataSourceForm.config = response.data.config || {
          api_base_url: '',
          api_token: '',
          api_endpoint: '/api/pump-data'
        }
      } catch (error) {
        console.error('获取数据源配置失败:', error)
      }
    },
    async loadDeviceThresholds(device_id) {
      try {
        const response = await axios.get('/api/device/list')
        const device = response.data.find(d => d.device_id === device_id)
        if (device) {
          this.thresholdForm.pressure_threshold = device.pressure_threshold
          this.thresholdForm.flow_threshold = device.flow_threshold
          this.thresholdForm.temperature_threshold = device.temperature_threshold
        }
      } catch (error) {
        console.error('获取设备阈值失败:', error)
      }
    },
    handleDataSourceChange() {
      // 切换数据源类型时的处理
    },
    async saveDataSourceConfig() {
      try {
        await axios.post('/api/data-source/switch', {
          type: this.dataSourceForm.type,
          config: this.dataSourceForm.config
        })
        this.$message.success('数据源配置保存成功')
      } catch (error) {
        console.error('保存数据源配置失败:', error)
        this.$message.error('保存失败')
      }
    },
    async saveDeviceThresholds() {
      if (!this.thresholdForm.device_id) {
        this.$message.warning('请选择设备')
        return
      }
      
      try {
        await axios.put(`/api/device/threshold/${this.thresholdForm.device_id}`, {
          pressure_threshold: this.thresholdForm.pressure_threshold,
          flow_threshold: this.thresholdForm.flow_threshold,
          temperature_threshold: this.thresholdForm.temperature_threshold
        })
        this.$message.success('设备阈值保存成功')
      } catch (error) {
        console.error('保存设备阈值失败:', error)
        this.$message.error('保存失败')
      }
    }
  }
}
</script>

<style scoped>
.config {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-card {
  margin-bottom: 20px;
}
</style>
