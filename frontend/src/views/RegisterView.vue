<template>
  <div class="auth-container d-flex align-items-center justify-content-center py-5">
    <div class="card auth-card shadow-lg border-0 rounded-4 w-100 overflow-hidden">
      <div class="card-body p-4 p-sm-5">
        <div class="text-center mb-4">
          <div class="icon-circle bg-primary-subtle text-primary mb-3 mx-auto">
            <i class="bi bi-person-plus-fill fs-3"></i>
          </div>
          <h3 class="fw-bold">Tạo tài khoản</h3>
          <p class="text-muted small">Chọn tư cách tham gia hệ thống SmartTicket</p>
        </div>

        <div class="role-selector mb-4 p-1 bg-light rounded-pill d-flex">
          <button
            type="button"
            class="btn flex-fill rounded-pill py-2 fw-semibold btn-role"
            :class="form.role === 'CUSTOMER' ? 'btn-primary shadow-sm' : 'text-muted'"
            @click="setRole('CUSTOMER')"
          >
            <i class="bi bi-person me-1"></i> Khách hàng
          </button>
          <button
            type="button"
            class="btn flex-fill rounded-pill py-2 fw-semibold btn-role"
            :class="form.role === 'ORGANIZER' ? 'btn-primary shadow-sm' : 'text-muted'"
            @click="setRole('ORGANIZER')"
          >
            <i class="bi bi-building me-1"></i> Ban tổ chức
          </button>
        </div>

        <div v-if="generalError" class="alert alert-danger alert-dismissible fade show small mb-4" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ generalError }}
          <button type="button" class="btn-close" @click="generalError = ''"></button>
        </div>

        <transition name="role-slide" mode="out-in">
          <div :key="form.role">
            <div
              class="role-badge-banner p-2.5 rounded-3 mb-4 d-flex align-items-center gap-2"
              :class="form.role === 'CUSTOMER' ? 'bg-primary-subtle text-primary' : 'bg-warning-subtle text-dark'"
            >
              <i :class="form.role === 'CUSTOMER' ? 'bi bi-person-badge fs-5' : 'bi bi-briefcase fs-5'"></i>
              <div>
                <div class="fw-bold fs-7">
                  {{ form.role === 'CUSTOMER' ? 'Đăng ký Tài khoản Cá nhân' : 'Đăng ký Tài khoản Doanh nghiệp / Tổ chức' }}
                </div>
                <div class="fs-8 text-muted">
                  {{ form.role === 'CUSTOMER' ? 'Dành cho khán giả mua vé tham gia sự kiện' : 'Dành cho đơn vị tạo show, bán vé và quản lý doanh thu' }}
                </div>
              </div>
            </div>

            <form @submit.prevent="handleRegister" novalidate>
              <div class="mb-3">
                <label class="form-label fw-semibold small">
                  {{ form.role === 'CUSTOMER' ? 'Họ và tên' : 'Họ và tên người đại diện' }}
                  <span class="text-danger">*</span>
                </label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.name }"
                  :placeholder="form.role === 'CUSTOMER' ? 'Nguyễn Văn A' : 'Nguyễn Văn A (Đại diện BTC)'"
                />
                <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
              </div>

              <div v-if="form.role === 'ORGANIZER'" class="mb-3">
                <label class="form-label fw-semibold small">Tên công ty / Đơn vị tổ chức <span class="text-danger">*</span></label>
                <input
                  v-model="form.company_name"
                  type="text"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.company_name }"
                  placeholder="Công ty TNHH Sự kiện Sài Gòn"
                />
                <div v-if="errors.company_name" class="invalid-feedback">{{ errors.company_name }}</div>
              </div>

              <div v-if="form.role === 'ORGANIZER'" class="mb-3">
                <label class="form-label fw-semibold small">Số tài khoản ngân hàng nhận tiền <span class="text-danger">*</span></label>
                <input
                  v-model="form.bank_account"
                  type="text"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.bank_account }"
                  placeholder="STK - Ngân hàng (VD: 99998888 - MBBank)"
                />
                <div v-if="errors.bank_account" class="invalid-feedback">{{ errors.bank_account }}</div>
                <div class="form-text text-muted fs-8 mt-1">
                  <i class="bi bi-info-circle me-1"></i>Dùng để đối soát doanh thu bán vé tự động qua PayOS.
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold small">Tên đăng nhập (Username) <span class="text-danger">*</span></label>
                <input
                  v-model="form.username"
                  type="text"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.username }"
                  placeholder="nguyenvana"
                />
                <div v-if="errors.username" class="invalid-feedback">{{ errors.username }}</div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold small">Email <span class="text-danger">*</span></label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.email }"
                  placeholder="name@example.com"
                />
                <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold small">Số điện thoại <span class="text-danger">*</span></label>
                <input
                  v-model="form.phone_number"
                  type="tel"
                  class="form-control bg-light"
                  :class="{ 'is-invalid': errors.phone_number }"
                  placeholder="0912345678"
                />
                <div v-if="errors.phone_number" class="invalid-feedback">{{ errors.phone_number }}</div>
              </div>

              <div v-if="form.role === 'CUSTOMER'" class="mb-3">
                <label class="form-label fw-semibold small">Ngày sinh <span class="text-muted fs-8">(Tùy chọn)</span></label>
                <input
                  v-model="form.dob"
                  type="date"
                  class="form-control bg-light text-muted"
                  :class="{ 'is-invalid': errors.dob }"
                />
                <div v-if="errors.dob" class="invalid-feedback">{{ errors.dob }}</div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold small">Mật khẩu <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control bg-light border-end-0"
                    :class="{ 'is-invalid': errors.password }"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    class="input-group-text bg-light border-start-0 text-muted btn-eye"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
                <div v-if="errors.password" class="text-danger fs-8 mt-1">{{ errors.password }}</div>

                <div v-if="form.password" class="mt-2">
                  <div class="progress" style="height: 5px;">
                    <div
                      class="progress-bar"
                      :class="passwordStrength.colorClass"
                      :style="{ width: passwordStrength.percent + '%' }"
                    ></div>
                  </div>
                  <div class="d-flex justify-content-between align-items-center mt-1 fs-8">
                    <span class="text-muted">Độ mạnh mật khẩu:</span>
                    <span :class="passwordStrength.textClass" class="fw-bold">{{ passwordStrength.label }}</span>
                  </div>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-semibold small">Xác nhận mật khẩu <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input
                    v-model="form.confirmPassword"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control bg-light border-end-0"
                    :class="{ 'is-invalid': errors.confirmPassword }"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    class="input-group-text bg-light border-start-0 text-muted btn-eye"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
                <div v-if="errors.confirmPassword" class="text-danger fs-8 mt-1">{{ errors.confirmPassword }}</div>
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100 py-2.5 fw-bold rounded-pill mb-3"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                <span>{{ isSubmitting ? 'Đang tạo tài khoản...' : (form.role === 'CUSTOMER' ? 'Đăng ký Khách hàng' : 'Đăng ký Ban tổ chức') }}</span>
              </button>
            </form>
          </div>
        </transition>

        <div class="text-center mt-3">
          <span class="text-muted small">Đã có tài khoản? </span>
          <router-link to="/login" class="text-primary text-decoration-none fw-semibold small">
            Đăng nhập ngay
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const router = useRouter()

const showPassword = ref(false)
const isSubmitting = ref(false)
const generalError = ref('')

const form = reactive({
  role: 'CUSTOMER',
  name: '',
  username: '',
  email: '',
  phone_number: '',
  dob: '',
  company_name: '',
  bank_account: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  name: '',
  username: '',
  email: '',
  phone_number: '',
  dob: '',
  company_name: '',
  bank_account: '',
  password: '',
  confirmPassword: ''
})

const setRole = (role) => {
  form.role = role
  clearErrors()
}

const clearErrors = () => {
  generalError.value = ''
  Object.keys(errors).forEach((key) => (errors[key] = ''))
}

const passwordStrength = computed(() => {
  const pwd = form.password
  if (!pwd) return { percent: 0, label: '', colorClass: '', textClass: '' }

  let score = 0
  if (pwd.length >= 6) score += 25
  if (pwd.length >= 10) score += 25
  if (/[A-Z]/.test(pwd)) score += 15
  if (/[0-9]/.test(pwd)) score += 15
  if (/[^A-Za-z0-9]/.test(pwd)) score += 20

  if (score < 40) {
    return { percent: score, label: 'Yếu', colorClass: 'bg-danger', textClass: 'text-danger' }
  } else if (score < 75) {
    return { percent: score, label: 'Trung bình', colorClass: 'bg-warning', textClass: 'text-warning' }
  } else {
    return { percent: score, label: 'Mạnh', colorClass: 'bg-success', textClass: 'text-success' }
  }
})

const validateForm = () => {
  clearErrors()
  let isValid = true

  if (!form.name.trim()) {
    errors.name = form.role === 'CUSTOMER' ? 'Vui lòng nhập Họ và tên.' : 'Vui lòng nhập Họ và tên người đại diện.'
    isValid = false
  }

  if (!form.username.trim()) {
    errors.username = 'Vui lòng nhập Tên đăng nhập.'
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email.trim()) {
    errors.email = 'Vui lòng nhập Email.'
    isValid = false
  } else if (!emailRegex.test(form.email)) {
    errors.email = 'Định dạng Email không hợp lệ.'
    isValid = false
  }

  const phoneRegex = /^0\d{9}$/
  if (!form.phone_number.trim()) {
    errors.phone_number = 'Vui lòng nhập Số điện thoại.'
    isValid = false
  } else if (!phoneRegex.test(form.phone_number)) {
    errors.phone_number = 'Số điện thoại không hợp lệ (10 số, bắt đầu bằng 0).'
    isValid = false
  }

  if (form.role === 'ORGANIZER') {
    if (!form.company_name.trim()) {
      errors.company_name = 'Vui lòng nhập Tên công ty/đơn vị tổ chức.'
      isValid = false
    }
    if (!form.bank_account.trim()) {
      errors.bank_account = 'Vui lòng nhập Số tài khoản ngân hàng.'
      isValid = false
    }
  }

  if (!form.password) {
    errors.password = 'Vui lòng nhập Mật khẩu.'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Mật khẩu phải chứa ít nhất 6 ký tự.'
    isValid = false
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Mật khẩu xác nhận không trùng khớp.'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  isSubmitting.value = true

  const payload = {
    name: form.name.trim(),
    username: form.username.trim(),
    email: form.email.trim(),
    phone_number: form.phone_number.trim(),
    password: form.password
  }

  if (form.role === 'CUSTOMER' && form.dob) {
    payload.dob = form.dob
  }

  let result
  if (form.role === 'ORGANIZER') {
    payload.company_name = form.company_name.trim()
    payload.bank_account = form.bank_account.trim()
    result = await authStore.registerOrganizer(payload)
  } else {
    result = await authStore.registerCustomer(payload)
  }

  isSubmitting.value = false

  if (result.success) {
    await Swal.fire({
      title: 'Đăng ký thành công!',
      text: 'Tài khoản SmartTicket của bạn đã được khởi tạo thành công.',
      icon: 'success',
      confirmButtonText: 'Đăng nhập ngay',
      confirmButtonColor: '#6366f1',
      customClass: {
        popup: 'rounded-4'
      }
    })

    router.push({
      path: '/login',
      query: { prefill: form.username || form.email }
    })
  } else {
    let errorMessages = []
    if (result.fieldErrors && typeof result.fieldErrors === 'object') {
      Object.keys(result.fieldErrors).forEach((field) => {
        const errList = result.fieldErrors[field]
        const textStr = Array.isArray(errList) ? errList[0] : errList
        if (errors[field] !== undefined) {
          errors[field] = textStr
        }
        errorMessages.push(`${field}: ${textStr}`)
      })
    }

    if (errorMessages.length > 0) {
      generalError.value = errorMessages.join(' | ')
    } else if (result.message) {
      generalError.value = result.message
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: calc(100vh - 160px);
}

.auth-card {
  max-width: 520px;
}

.icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-role {
  border: none;
  transition: all 0.25s ease;
}

.btn-eye {
  cursor: pointer;
}

.btn-eye:hover {
  color: #4f46e5 !important;
}

.fs-8 {
  font-size: 0.78rem;
}

.role-slide-enter-active,
.role-slide-leave-active {
  transition: all 0.25s ease-out;
}

.role-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.role-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>