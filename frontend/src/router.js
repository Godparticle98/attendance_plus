import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/regularizations',
    name: 'Regularizations',
    component: () => import('./views/Regularizations.vue')
  },
  {
    path: '/overtime',
    name: 'OvertimeSummary',
    component: () => import('./views/OvertimeSummary.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue')
  }
]

// The base path must match the frappe routing path
const router = createRouter({
  history: createWebHistory('/attendance_plus_dashboard'),
  routes
})

export default router
