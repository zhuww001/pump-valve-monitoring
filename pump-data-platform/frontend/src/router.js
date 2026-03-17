import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/dashboard/:device_id',
    name: 'DeviceDashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/device-list',
    name: 'DeviceList',
    component: () => import('./views/DeviceList.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('./views/History.vue')
  },
  {
    path: '/history/:device_id',
    name: 'DeviceHistory',
    component: () => import('./views/History.vue')
  },
  {
    path: '/warning',
    name: 'Warning',
    component: () => import('./views/Warning.vue')
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('./views/Config.vue')
  },
  {
    path: '/gateway',
    name: 'GatewayMonitor',
    component: () => import('./views/GatewayMonitor.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
