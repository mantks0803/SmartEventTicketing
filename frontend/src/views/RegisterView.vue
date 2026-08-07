<template>
  <div class="auth-container d-flex align-items-center justify-content-center py-5">
    <div class="card auth-card shadow-lg border-0 rounded-4 w-100 overflow-hidden">
      <div class="card-body p-4 p-sm-5">
        <div class="text-center mb-4">
          <div class="icon-circle bg-primary-subtle text-primary mb-3 mx-auto">
            <i class="bi bi-person-plus-fill fs-3"></i>
          </div>
          <h3 class="fw-bold">Tạo tài khoản</h3>
          <p class="text-muted small">Đến với SmartTicket, bạn là: </p>
        </div>

        <div class="role-selector mb-4 p-1 bg-light rounded-pill d-flex">
          <button
            type="button"
            class="btn flex-fill rounded-pill py-2 fw-semibold btn-role"
            :class="form.role === 'CUSTOMER' ? 'btn-primary-custom shadow-sm' : 'text-muted'"
            @click="setRole('CUSTOMER')"
          >
            <i class="bi bi-person me-1"></i> Khách hàng
          </button>
          <button
            type="button"
            class="btn flex-fill rounded-pill py-2 fw-semibold btn-role"
            :class="form.role === 'ORGANIZER' ? 'btn-primary-custom shadow-sm' : 'text-muted'"
            @click="setRole('ORGANIZER')"
          >
            <i class="bi bi-building me-1"></i> Ban tổ chức
          </button>
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
              class="form-control bg-light"
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
            class="btn btn-primary-custom w-100 py-2.5 fw-bold rounded-pill mb-3"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            <span>{{ isSubmitting ? 'Đang tạo tài khoản...' : (form.role === 'CUSTOMER' ? 'Đăng ký Khách hàng' : 'Đăng ký Ban tổ chức') }}</span>
          </button>
        </form>

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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const router = useRouter()

const showPassword = ref(false)
const isSubmitting = ref(false)

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
  Object.keys(errors).forEach((key) => (errors[key] = ''))
}

const validateForm = () => {
  clearErrors()
  let isValid = true

  if (!form.name.trim()) {
    errors.name = 'Vui lòng nhập Họ và tên.'
    isValid = false
  }

  if (!form.username.trim()) {
    errors.username = 'Vui lòng nhập Tên đăng nhập.'
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email.trim() || !emailRegex.test(form.email)) {
    errors.email = 'Vui lòng nhập Email hợp lệ.'
    isValid = false
  }

  if (!form.phone_number.trim()) {
    errors.phone_number = 'Vui lòng nhập Số điện thoại.'
    isValid = false
  }

  if (form.role === 'CUSTOMER' && form.dob) {
    const selectedDate = new Date(form.dob)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (selectedDate > today) {
      errors.dob = 'Ngày sinh không được ở tương lai.'
      isValid = false
    } else {
      const minAgeDate = new Date()
      minAgeDate.setFullYear(minAgeDate.getFullYear() - 13)
      minAgeDate.setHours(0, 0, 0, 0)

      if (selectedDate > minAgeDate) {
        errors.dob = 'Bạn phải từ 13 tuổi trở lên để đăng ký.'
        isValid = false
      }
    }
  }

  if (form.role === 'ORGANIZER') {
    if (!form.company_name.trim()) {
      errors.company_name = 'Vui lòng nhập Tên đơn vị tổ chức.'
      isValid = false
    }
    if (!form.bank_account.trim()) {
      errors.bank_account = 'Vui lòng nhập Số tài khoản.'
      isValid = false
    }
  }

  if (!form.password || form.password.length < 6) {
    errors.password = 'Mật khẩu phải từ 6 ký tự.'
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
      text: 'Tài khoản SmartTicket của bạn đã sẵn sàng sử dụng.',
      icon: 'success',
      confirmButtonText: 'Đăng nhập ngay',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })

    router.push({
      path: '/login',
      query: { prefill: form.username || form.email }
    })
  } else {
    Swal.fire({
      title: 'Đăng ký thất bại',
      text: result.message || 'Vui lòng kiểm tra lại thông tin đăng ký.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
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

.fs-8 {
  font-size: 0.78rem;
}
</style>