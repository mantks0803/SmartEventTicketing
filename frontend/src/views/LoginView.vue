<template>
  <div class="auth-container d-flex align-items-center justify-content-center py-5">
    <div class="card auth-card shadow-lg border-0 rounded-4 w-100">
      <div class="card-body p-4 p-sm-5">
        <!-- Header -->
        <div class="text-center mb-4">
          <div class="icon-circle bg-primary-subtle text-primary mb-3 mx-auto">
            <i class="bi bi-box-arrow-in-right fs-3"></i>
          </div>
          <h3 class="fw-bold">Đăng nhập</h3>
          <p class="text-muted small">Chào mừng bạn quay trở lại với SmartTicket</p>
        </div>

        <!-- Thông báo lỗi khi 401 hoặc lỗi server -->
        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show mb-4 small" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMessage }}
          <button type="button" class="btn-close" @click="errorMessage = ''"></button>
        </div>

        <!-- Form Đăng nhập -->
        <form @submit.prevent="handleLogin" novalidate>
          <!-- Email / Username -->
          <div class="mb-3">
            <label class="form-label fw-semibold small">Tên đăng nhập hoặc Email</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0 text-muted">
                <i class="bi bi-person"></i>
              </span>
              <input
                v-model="form.email"
                type="text"
                class="form-control bg-light border-start-0"
                placeholder="..."
                required
              />
            </div>
          </div>

          <!-- Password với Icon con mắt -->
          <div class="mb-4">
            <label class="form-label fw-semibold small">Mật khẩu</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0 text-muted">
                <i class="bi bi-lock"></i>
              </span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control bg-light border-start-0 border-end-0"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                class="input-group-text bg-light border-start-0 text-muted btn-toggle-eye"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Button Submit -->
          <button
            type="submit"
            class="btn btn-primary w-100 py-2.5 fw-bold rounded-pill mb-3"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            <span>{{ isSubmitting ? 'Đang xử lý...' : 'Đăng nhập' }}</span>
          </button>
        </form>

        <!-- Footer link -->
        <div class="text-center mt-3">
          <span class="text-muted small">Chưa có tài khoản? </span>
          <router-link to="/register" class="text-primary text-decoration-none fw-semibold small">
            Đăng ký ngay
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const showPassword = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  password: ''
})

// Prefill từ query param nếu có
onMounted(() => {
  if (route.query.prefill) {
    form.email = route.query.prefill
  }
})

const handleLogin = async () => {
  errorMessage.value = ''

  if (!form.email || !form.password) {
    errorMessage.value = 'Vui lòng điền đầy đủ Tên đăng nhập/Email và Mật khẩu.'
    return
  }

  isSubmitting.value = true

  const result = await authStore.login({
    email: form.email,
    password: form.password
  })

  isSubmitting.value = false

  if (result.success) {
    const redirectPath = route.query.redirect
    if (redirectPath) {
      router.push(redirectPath)
    } else if (result.role === 'ORGANIZER') {
      router.push('/organizer/dashboard')
    } else {
      router.push('/')
    }
  } else {
    // Báo lỗi 401 nhưng GIỮ NGUYÊN dữ liệu form
    errorMessage.value = result.message
  }
}
</script>

<style scoped>
.auth-container {
  min-height: calc(100vh - 160px);
}

.auth-card {
  max-width: 440px;
}

.icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-toggle-eye {
  cursor: pointer;
}

.btn-toggle-eye:hover {
  color: #4f46e5 !important;
}
</style>