import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/public/HomeView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import EventDetailView from '@/views/public/EventDetailView.vue'
import CheckoutView from '@/views/customer/CheckoutView.vue'
import PaymentResultView from '@/views/customer/PaymentResultView.vue'
import MyTicketsView from '@/views/customer/MyTicketsView.vue'
import OrganizerDashboardView from '@/views/organizer/OrganizerDashboardView.vue'
import OrganizerEventCreateView from '@/views/organizer/OrganizerEventCreateView.vue'

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
      path: '/payment/result',
      name: 'payment-result',
      component: PaymentResultView,
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
      path: '/admin/events',
      name: 'admin-events',
      component: () => import('@/views/admin/AdminEventApprovalView.vue'),
      meta: {
        requiresAuth: true,
        role: 'ADMIN'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/account/ProfileView.vue'),
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
    if (authStore.isAdmin) {
      return { name: 'admin-events' }
    }

    if (authStore.isOrganizer) {
      return { name: 'organizer-dashboard' }
    }

    return { name: 'home' }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      return { name: 'admin-events' }
    }

    if (authStore.isOrganizer) {
      return { name: 'organizer-dashboard' }
    }

    return { name: 'home' }
  }
})

export default router
