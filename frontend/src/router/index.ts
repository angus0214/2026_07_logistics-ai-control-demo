import { createRouter, createWebHistory } from 'vue-router'
import ControlTowerView from '../views/ControlTowerView.vue'
import PitchView from '../views/PitchView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ControlTowerView
    },
    {
      path: '/pitch',
      name: 'pitch',
      component: PitchView
    },
    {
      path: '/:catchAll(.*)',
      redirect: '/'
    }
  ]
})

export default router
