import { defineStore } from 'pinia'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: JSON.parse(localStorage.getItem('user_info')) || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isCustomer: (state) => state.user?.role === 'CUSTOMER' || state.user?.type === 'CUSTOMER',
    isOrganizer: (state) => state.user?.role === 'ORGANIZER' || state.user?.type === 'ORGANIZER',
    userRole: (state) => state.user?.role || state.user?.type || null
  },

  actions: {
    async login(credentials) {
      try {
        const response = await apiClient.post('auth/login/', credentials)
        const { access, refresh, user } = response.data

        this.accessToken = access
        this.refreshToken = refresh
        this.user = user

        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        localStorage.setItem('user_info', JSON.stringify(user))

        return { success: true, role: user.role }
      } catch (error) {
        let message = 'Đăng nhập thất bại. Vui lòng thử lại sau.'
        if (error.response?.status === 401) {
          message = 'Tên đăng nhập/Email hoặc mật khẩu không chính xác.'
        } else if (error.response?.data?.detail) {
          message = error.response.data.detail
        }
        return { success: false, message }
      }
    },

    async registerCustomer(payload) {
      try {
        await apiClient.post('auth/register/customer/', payload)
        return { success: true }
      } catch (error) {
        const fieldErrors = error.response?.data || {}
        let message = error.response?.data?.detail

        if (!message && typeof fieldErrors === 'object') {
          const firstKey = Object.keys(fieldErrors)[0]
          if (firstKey) {
            const errVal = fieldErrors[firstKey]
            const errTxt = Array.isArray(errVal) ? errVal[0] : errVal
            message = `${firstKey}: ${errTxt}`
          }
        }

        return {
          success: false,
          fieldErrors,
          message: message || 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.'
        }
      }
    },

    async registerOrganizer(payload) {
      try {
        await apiClient.post('auth/register/organizer/', payload)
        return { success: true }
      } catch (error) {
        const fieldErrors = error.response?.data || {}
        let message = error.response?.data?.detail

        if (!message && typeof fieldErrors === 'object') {
          const firstKey = Object.keys(fieldErrors)[0]
          if (firstKey) {
            const errVal = fieldErrors[firstKey]
            const errTxt = Array.isArray(errVal) ? errVal[0] : errVal
            message = `${firstKey}: ${errTxt}`
          }
        }

        return {
          success: false,
          fieldErrors,
          message: message || 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.'
        }
      }
    },

    updateUser(userData) {
      this.user = { ...this.user, ...userData }
      localStorage.setItem('user_info', JSON.stringify(this.user))
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    }
  }
})