<template>
  <div class="device-list">
    <h2>设备列表</h2>
    
    <!-- 搜索框 -->
    <el-card class="search-card" style="margin-bottom: 20px;">
      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索设备">
          <el-input v-model="searchKeyword" placeholder="输入设备名称或ID" style="width: 300px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchDevices">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 设备表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
        </div>
      </template>
      <el-table :data="filteredDevices" style="width: 100%">
        <el-table-column prop="device_id" label="设备ID" width="120" />
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="负责人" label="负责人" width="100" />
        <el-table-column prop="联系方式" label="联系方式" width="150" />
        <el-table-column label="操作" width="400">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="editDevice(scope.row)">编辑</el-button>
              <el-button type="success" size="small" @click="viewRealtimeData(scope.row.device_id)">实时数据</el-button>
              <el-button type="warning" size="small" @click="viewHistoryData(scope.row.device_id)">历史数据</el-button>
              <el-button type="danger" size="small" @click="viewWarningRecords(scope.row.device_id)">预警记录</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑设备对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑设备"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="设备ID">
          <el-input v-model="editForm.device_id" disabled />
        </el-form-item>
        <el-form-item label="设备名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="editForm.location" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="editForm.负责人" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="editForm.联系方式" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveDevice">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DeviceList',
  data() {
    return {
      devices: [
        { device_id: 'device_1', name: '一号泵阀', location: 'A车间', 负责人: '李经理', 联系方式: '13800138000' },
        { device_id: 'device_2', name: '二号泵阀', location: 'B车间', 负责人: '赵经理', 联系方式: '13900139009' },
        { device_id: 'device_3', name: '三号泵阀', location: 'C车间', 负责人: '王经理', 联系方式: '13800138003' }
      ],
      searchKeyword: '',
      dialogVisible: false,
      editForm: {
        device_id: '',
        name: '',
        location: '',
        负责人: '',
        联系方式: ''
      }
    }
  },
  computed: {
    filteredDevices() {
      if (!this.searchKeyword) {
        return this.devices
      }
      return this.devices.filter(device => 
        device.name.includes(this.searchKeyword) || 
        device.device_id.includes(this.searchKeyword)
      )
    }
  },
  methods: {
    searchDevices() {
      // 这里可以添加实际的搜索逻辑
    },
    editDevice(device) {
      // 编辑设备逻辑
      this.editForm = { ...device }
      this.dialogVisible = true
    },
    saveDevice() {
      // 保存设备逻辑
      const index = this.devices.findIndex(item => item.device_id === this.editForm.device_id)
      if (index !== -1) {
        this.devices[index] = { ...this.editForm }
        this.$message.success('设备信息已更新')
      }
      this.dialogVisible = false
    },
    viewRealtimeData(deviceId) {
      // 跳转到实时数据页面，带上设备ID参数
      this.$router.push(`/dashboard/${deviceId}`)
    },
    viewHistoryData(deviceId) {
      // 跳转到历史数据页面，带上设备ID参数
      this.$router.push(`/history/${deviceId}`)
    },
    viewWarningRecords(deviceId) {
      // 跳转到预警记录页面
      this.$router.push('/warning')
    }
  }
}
</script>

<style scoped>
.device-list {
  padding: 0;
}

.search-form {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.operation-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
