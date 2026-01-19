import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import DashboardPage from '../views/DashboardPage.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/dashboard',
    name: 'DashboardPage',
    component: DashboardPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router