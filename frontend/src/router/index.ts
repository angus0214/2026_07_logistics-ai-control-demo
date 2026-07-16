import { createRouter, createWebHistory } from 'vue-router'
import ControlTowerView from '../views/ControlTowerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ControlTowerView
    }
  ]
})

export default router
