import { defineStore } from 'pinia'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: JSON.parse(localStorage.getItem('user_info')) || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isCustomer: (state) => state.user?.role === 'CUSTOMER',
    isOrganizer: (state) => state.user?.role === 'ORGANIZER'
  },

  actions: {
    async login(email, password) {
      try {
        const response = await apiClient.post('auth/login/', { email, password })
        const { access, user } = response.data

        this.token = access
        this.user = user

        localStorage.setItem('access_token', access)
        localStorage.setItem('user_info', JSON.stringify(user))

        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.'
        }
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    }
  }
})