import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import EventDetailView from '@/views/EventDetailView.vue'
import CheckoutView from '@/views/CheckoutView.vue'
import MyTicketsView from '@/views/MyTicketsView.vue'
import OrganizerDashboardView from '@/views/OrganizerDashboardView.vue'
import OrganizerEventCreateView from '@/views/OrganizerEventCreateView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'home',
      alias: '/HomeView',
      component: HomeView
    },
    {
      path: '/events/:id',
      name: 'event-detail',
      component: EventDetailView
    },
    {
      path: '/checkout/:orderId',
      name: 'checkout',
      component: CheckoutView,
      meta: {
        requiresAuth: true,
        role: 'CUSTOMER'
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        guestOnly: true
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        guestOnly: true
      }
    },
    {
      path: '/my-tickets',
      name: 'my-tickets',
      component: MyTicketsView,
      meta: {
        requiresAuth: true,
        role: 'CUSTOMER'
      }
    },
    {
      path: '/organizer/dashboard',
      name: 'organizer-dashboard',
      component: OrganizerDashboardView,
      meta: {
        requiresAuth: true,
        role: 'ORGANIZER'
      }
    },
    {
      path: '/organizer/events/create',
      name: 'organizer-event-create',
      component: OrganizerEventCreateView,
      meta: {
        requiresAuth: true,
        role: 'ORGANIZER'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: {
        requiresAuth: true
      }
    }
  ],

  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath
      }
    }
  }

  if (
    to.meta.role
    && authStore.isAuthenticated
    && authStore.userRole !== to.meta.role
  ) {
    if (authStore.isOrganizer) {
      return { name: 'organizer-dashboard' }
    }

    return { name: 'home' }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isOrganizer) {
      return { name: 'organizer-dashboard' }
    }

    return { name: 'home' }
  }
})

export default router