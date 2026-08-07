<template>
  <div class="bg-page-custom py-5 min-vh-100">
    <div class="container" style="max-width: 900px;">
      <h3 class="fw-bold mb-4 text-slate-900">Hồ sơ cá nhân</h3>

      <div class="row g-4">
        <div class="col-md-4">
          <div class="bg-white p-4 rounded-xl border shadow-sm text-center">
            <div class="position-relative d-inline-block mb-3">
              <img
                :src="avatarPreview || profile.avatar || defaultAvatar"
                class="rounded-circle object-fit-cover border border-3 border-primary"
                width="120"
                height="120"
              />
              <div
                v-if="uploadingAvatar"
                class="position-absolute top-0 start-0 w-100 h-100 rounded-circle bg-dark bg-opacity-50 d-flex align-items-center justify-content-center"
              >
                <div class="spinner-border text-light spinner-border-sm"></div>
              </div>
              <button
                class="btn btn-primary btn-sm rounded-circle position-absolute bottom-0 end-0 p-2 shadow-sm"
                style="width: 36px; height: 36px;"
                @click="triggerFileInput"
                :disabled="uploadingAvatar"
              >
                <i class="bi bi-pencil-fill"></i>
              </button>
            </div>
            <input
              type="file"
              ref="fileInputRef"
              class="d-none"
              accept="image/jpeg,image/png,image/webp"
              @change="handleAvatarChange"
            />
            <h5 class="fw-bold mb-1 text-slate-900">{{ profile.name }}</h5>
            <span class="badge bg-blue-subtle text-primary rounded-pill px-3 py-1 fw-semibold mb-2">
              {{ profile.type === 'ORGANIZER' ? 'Ban tổ chức' : 'Khách hàng' }}
            </span>
            <p class="text-muted small mb-0"><i class="bi bi-envelope me-1"></i>{{ profile.email }}</p>
          </div>
        </div>

        <div class="col-md-8">
          <div class="bg-white p-4 rounded-xl border shadow-sm mb-4">
            <ul class="nav nav-tabs border-bottom mb-4">
              <li class="nav-item">
                <button
                  class="nav-link fw-semibold"
                  :class="{ active: activeTab === 'info' }"
                  @click="activeTab = 'info'"
                >
                  <i class="bi bi-person me-2"></i>Thông tin cá nhân
                </button>
              </li>
              <li class="nav-item">
                <button
                  class="nav-link fw-semibold"
                  :class="{ active: activeTab === 'password' }"
                  @click="activeTab = 'password'"
                >
                  <i class="bi bi-shield-lock me-2"></i>Đổi mật khẩu
                </button>
              </li>
            </ul>

            <div v-if="activeTab === 'info'">
              <form @submit.prevent="submitProfile">
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Tên đăng nhập</label>
                    <input type="text" class="form-control bg-light" :value="profile.username" disabled />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Email</label>
                    <input type="email" class="form-control bg-light" :value="profile.email" disabled />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Họ và tên <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" v-model="profile.name" required />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Số điện thoại <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" v-model="profile.phone_number" required />
                  </div>

                  <div v-if="profile.type === 'CUSTOMER'" class="col-md-6">
                    <label class="form-label fw-semibold small">Ngày sinh <span class="text-muted fs-8">*</span></label>
                    <input type="date" class="form-control bg-light" :value="profile.dob" disabled />
                  </div>

                  <template v-if="profile.type === 'ORGANIZER'">
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small">Tên công ty / Đơn vị tổ chức</label>
                      <input type="text" class="form-control" v-model="profile.company_name" required />
                    </div>
                    <div class="col-12">
                      <label class="form-label fw-semibold small">Số tài khoản ngân hàng</label>
                      <input type="text" class="form-control" v-model="profile.bank_account" required />
                    </div>
                  </template>
                </div>

                <button type="submit" class="btn btn-primary-custom rounded-pill px-4 py-2 mt-4" :disabled="savingProfile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
                  Lưu thay đổi
                </button>
              </form>
            </div>

            <div v-if="activeTab === 'password'">
              <form @submit.prevent="submitPassword">
                <div class="mb-3">
                  <label class="form-label fw-semibold small">Mật khẩu hiện tại <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="passwordForm.old_password" required />
                </div>
                <div class="mb-3">
                  <label class="form-label fw-semibold small">Mật khẩu mới <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="passwordForm.new_password" required />
                </div>
                <div class="mb-4">
                  <label class="form-label fw-semibold small">Xác nhận mật khẩu mới <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="passwordForm.confirm_password" required />
                </div>

                <button type="submit" class="btn btn-primary-custom rounded-pill px-4 py-2" :disabled="savingPassword">
                  <span v-if="savingPassword" class="spinner-border spinner-border-sm me-2"></span>
                  Cập nhật mật khẩu
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import apiClient from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const activeTab = ref('info')
const fileInputRef = ref(null)
const avatarPreview = ref(null)
const uploadingAvatar = ref(false)
const savingProfile = ref(false)
const savingPassword = ref(false)
const defaultAvatar = 'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1777361181/tickethub_avatars/btsrovtumjgqlaharj2r.jpg'

const profile = reactive({
  id: null,
  name: '',
  username: '',
  email: '',
  phone_number: '',
  avatar: '',
  type: '',
  dob: '',
  company_name: '',
  bank_account: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const fetchProfile = async () => {
  try {
    const res = await apiClient.get('auth/me/')
    Object.assign(profile, res.data)
  } catch (err) {
    Swal.fire({
      title: 'Lỗi tải hồ sơ',
      text: 'Không thể lấy thông tin cá nhân. Vui lòng thử lại.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  }
}

onMounted(fetchProfile)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleAvatarChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    Swal.fire({
      title: 'Định dạng không hỗ trợ',
      text: 'Vui lòng chọn hình ảnh đuôi JPG, PNG hoặc WEBP.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    Swal.fire({
      title: 'Dung lượng quá lớn',
      text: 'File hình ảnh vượt quá giới hạn 5MB.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  const reader = new FileReader()
  reader.onload = (evt) => {
    avatarPreview.value = evt.target.result
  }
  reader.readAsDataURL(file)

  const formData = new FormData()
  formData.append('avatar', file)

  uploadingAvatar.value = true
  try {
    const res = await apiClient.post('auth/me/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    profile.avatar = res.data.avatar
    authStore.updateUser({ avatar: res.data.avatar })

    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Cập nhật ảnh đại diện thành công!',
      showConfirmButton: false,
      timer: 2000
    })
  } catch (err) {
    avatarPreview.value = null
    Swal.fire({
      title: 'Upload thất bại',
      text: err.response?.data?.error || 'Lỗi tải ảnh đại diện lên Cloudinary.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    uploadingAvatar.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

const submitProfile = async () => {
  savingProfile.value = true
  const payload = {
    name: profile.name,
    phone_number: profile.phone_number
  }

  if (profile.type === 'ORGANIZER') {
    payload.company_name = profile.company_name
    payload.bank_account = profile.bank_account
  }

  try {
    await apiClient.patch('auth/me/', payload)
    authStore.updateUser({ name: profile.name })

    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Cập nhật hồ sơ thành công!',
      showConfirmButton: false,
      timer: 2000
    })
  } catch (err) {
    Swal.fire({
      title: 'Cập nhật thất bại',
      text: err.response?.data?.detail || 'Không thể lưu thông tin cá nhân.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    savingProfile.value = false
  }
}

const submitPassword = async () => {
  if (passwordForm.new_password.length < 6) {
    Swal.fire({
      title: 'Mật khẩu yếu',
      text: 'Mật khẩu mới phải chứa ít nhất 6 ký tự.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    Swal.fire({
      title: 'Không trùng khớp',
      text: 'Xác nhận mật khẩu mới không trùng khớp.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  savingPassword.value = true
  try {
    await apiClient.post('auth/change-password/', passwordForm)
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''

    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Đổi mật khẩu thành công!',
      showConfirmButton: false,
      timer: 2000
    })
  } catch (err) {
    Swal.fire({
      title: 'Đổi mật khẩu thất bại',
      text: err.response?.data?.error || 'Mật khẩu hiện tại không chính xác.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    savingPassword.value = false
  }
}
</script>

<style scoped>
.text-slate-900 {
  color: #0F172A;
}

.bg-blue-subtle {
  background-color: #EFF6FF;
}

.nav-tabs .nav-link {
  color: #64748B;
  border: none;
  border-bottom: 2px solid transparent;
}

.nav-tabs .nav-link.active {
  color: #2563EB;
  border-bottom: 2px solid #2563EB;
  background: transparent;
}
</style>