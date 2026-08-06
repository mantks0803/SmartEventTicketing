<template>
  <div class="bg-page-custom py-4 min-vh-100">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-2">
          <div class="bg-white p-3 rounded-xl border shadow-sm">
            <h6 class="fw-bold mb-3 text-uppercase text-muted fs-7">Ban tổ chức</h6>
            <div class="nav flex-column nav-pills gap-2">
              <button class="nav-link text-start rounded-pill py-2.5" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
                <i class="bi bi-graph-up me-2"></i>Tổng quan
              </button>
              <button class="nav-link text-start rounded-pill py-2.5" :class="{ active: activeTab === 'checkin' }" @click="activeTab = 'checkin'">
                <i class="bi bi-qr-code-scan me-2"></i>Soát vé
              </button>
            </div>
          </div>
        </div>

        <div class="col-lg-10">
          <div v-if="activeTab === 'overview'">
            <div class="row g-4 mb-4">
              <div class="col-md-4">
                <div class="bg-white p-4 rounded-xl border shadow-sm">
                  <span class="text-muted small">Tổng doanh thu</span>
                  <h2 class="fw-extrabold text-primary-custom mt-2 mb-0">128.500.000 ₫</h2>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-white p-4 rounded-xl border shadow-sm">
                  <span class="text-muted small">Vé đã bán</span>
                  <h2 class="fw-extrabold text-success mt-2 mb-0">450 / 500</h2>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-white p-4 rounded-xl border shadow-sm">
                  <span class="text-muted small">Sự kiện đang mở</span>
                  <h2 class="fw-extrabold text-warning mt-2 mb-0">3 sự kiện</h2>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'checkin'" class="bg-white p-5 rounded-xl border shadow-sm text-center">
            <h4 class="fw-bold mb-4 text-slate-900">Cổng soát vé tự động</h4>
            <div class="mx-auto" style="max-width: 420px;">
              <input 
                type="text" 
                class="form-control form-control-lg rounded-pill text-center mb-3 shadow-sm border" 
                placeholder="Nhập hoặc Quét mã QR tại đây..." 
                v-model="qrCodeInput"
                @keyup.enter="handleCheckIn"
              />
              <button class="btn btn-cta rounded-pill px-5 py-2.5 fs-5 w-100" @click="handleCheckIn">Soát vé ngay</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import apiClient from '@/services/api'
import Swal from 'sweetalert2'

const activeTab = ref('overview')
const qrCodeInput = ref('')

const handleCheckIn = async () => {
  if (!qrCodeInput.value.trim()) {
    Swal.fire({
      title: 'Thiếu mã QR',
      text: 'Vui lòng nhập hoặc quét mã vé QR.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  try {
    const res = await apiClient.post('orders/check-in/', { qr_code: qrCodeInput.value.trim() })
    
    Swal.fire({
      title: 'Soát vé thành công!',
      text: res.data.message,
      icon: 'success',
      confirmButtonColor: '#10B981',
      customClass: { popup: 'rounded-4' }
    })
    
    qrCodeInput.value = ''
  } catch (err) {
    Swal.fire({
      title: 'Soát vé thất bại!',
      text: err.response?.data?.error || 'Mã vé không hợp lệ hoặc đã được sử dụng.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' }
    })
  }
}
</script>

<style scoped>
.fw-extrabold {
  font-weight: 800;
}

.text-slate-900 {
  color: #0F172A;
}

.fs-7 {
  font-size: 0.75rem;
}
</style>