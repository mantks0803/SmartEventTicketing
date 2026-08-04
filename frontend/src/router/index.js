import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guestOnly: true }
    },
    {
      path: '/my-tickets',
      name: 'my-tickets',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true, role: 'CUSTOMER' }
    },
    {
      path: '/organizer/dashboard',
      name: 'organizer-dashboard',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true, role: 'ORGANIZER' }
    }
  ]
})

// Route Guard bảo vệ các trang riêng tư
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()


  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isOrganizer) {
      return next({ name: 'organizer-dashboard' })
    }
    return next({ name: 'home' })
  }

  if (to.meta.role && authStore.userRole !== to.meta.role) {
    return next({ name: 'home' })
  }

  next()
})

export default router