<template>
  <div class="warning">
    <h2>预警管理</h2>
    
    <!-- 预警列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>预警记录列表</span>
        </div>
      </template>
      <el-table :data="warningList" style="width: 100%">
        <el-table-column prop="id" label="预警ID" width="100" />
        <el-table-column prop="device_id" label="设备ID" width="120" />
        <el-table-column prop="warning_type" label="预警类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.warning_type === 'pressure' ? 'danger' : scope.row.warning_type === 'flow' ? 'warning' : 'info'">
              {{ scope.row.warning_type === 'pressure' ? '压力' : scope.row.warning_type === 'flow' ? '流量' : '温度' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_value" label="预警值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'unprocessed' ? 'warning' : 'success'">
              {{ scope.row.status === 'unprocessed' ? '未处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="200" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleWarning(scope.row)"
              :disabled="scope.row.status === 'processed'"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 处理预警对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="处理预警"
      width="500px"
    >
      <el-form :model="warningForm" label-width="80px">
        <el-form-item label="预警ID">
          <el-input v-model="warningForm.id" disabled />
        </el-form-item>
        <el-form-item label="设备ID">
          <el-input v-model="warningForm.device_id" disabled />
        </el-form-item>
        <el-form-item label="预警类型">
          <el-input v-model="warningForm.warning_type" disabled />
        </el-form-item>
        <el-form-item label="预警值">
          <el-input v-model="warningForm.warning_value" disabled />
        </el-form-item>
        <el-form-item label="阈值">
          <el-input v-model="warningForm.threshold" disabled />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input type="textarea" v-model="warningForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitWarning">提交</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Warning',
  data() {
    return {
      warningList: [],
      dialogVisible: false,
      warningForm: {
        id: '',
        device_id: '',
        warning_type: '',
        warning_value: '',
        threshold: '',
        remark: ''
      }
    }
  },
  mounted() {
    this.loadWarningList()
    // 定时更新预警列表
    this.interval = setInterval(() => {
      this.loadWarningList()
    }, 10000)
  },
  beforeUnmount() {
    clearInterval(this.interval)
  },
  methods: {
    async loadWarningList() {
      try {
        const response = await axios.get('/api/warning/list')
        this.warningList = response.data
      } catch (error) {
        console.error('获取预警列表失败:', error)
      }
    },
    handleWarning(warning) {
      this.warningForm = {
        id: warning.id,
        device_id: warning.device_id,
        warning_type: warning.warning_type === 'pressure' ? '压力' : warning.warning_type === 'flow' ? '流量' : '温度',
        warning_value: warning.warning_value,
        threshold: warning.threshold,
        remark: ''
      }
      this.dialogVisible = true
    },
    async submitWarning() {
      try {
        await axios.put(`/api/warning/status/${this.warningForm.id}`, {
          status: 'processed'
        })
        this.$message.success('处理成功')
        this.dialogVisible = false
        this.loadWarningList()
      } catch (error) {
        console.error('处理预警失败:', error)
        this.$message.error('处理失败')
      }
    }
  }
}
</script>

<style scoped>
.warning {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
