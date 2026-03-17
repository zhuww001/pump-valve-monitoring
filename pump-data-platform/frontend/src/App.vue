<template>
  <div class="app-container">
    <el-container>
      <el-header height="60px" class="header">
        <h1>泵阀管道堵塞预警系统</h1>
      </el-header>
      <el-container>
        <el-aside width="200px" class="aside">
          <el-menu
            default-active="/"
            class="el-menu-vertical-demo"
            router
          >
            <el-menu-item index="/">
              <el-icon><i-ep-monitor /></el-icon>
              <span>实时监控</span>
            </el-menu-item>
            <el-menu-item index="/device-list">
              <el-icon><i-ep-list /></el-icon>
              <span>设备列表</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><i-ep-data-line /></el-icon>
              <span>历史数据</span>
            </el-menu-item>
            <el-menu-item index="/warning">
              <el-icon><i-ep-warning /></el-icon>
              <span>预警管理</span>
            </el-menu-item>
            <el-menu-item index="/config">
              <el-icon><i-ep-setting /></el-icon>
              <span>配置中心</span>
            </el-menu-item>
            <el-menu-item index="/gateway">
              <el-icon><i-ep-cpu /></el-icon>
              <span>边缘网关</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { Monitor, DataLine, Warning, Setting, List, Cpu } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    'i-ep-monitor': Monitor,
    'i-ep-data-line': DataLine,
    'i-ep-warning': Warning,
    'i-ep-setting': Setting,
    'i-ep-list': List,
    'i-ep-cpu': Cpu
  }
}
</script>

<style>
.app-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding-left: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.main {
  padding: 20px;
  overflow-y: auto;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}
</style>
