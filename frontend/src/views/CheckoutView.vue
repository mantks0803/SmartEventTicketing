<template>
  <div class="bg-page-custom py-5" v-if="order">
    <div class="container">
      <div class="row g-4 justify-content-center">
        <div class="col-lg-8">
          <div class="bg-warning bg-opacity-10 border border-warning rounded-xl p-3 text-center mb-4 shadow-sm">
            <span class="fw-bold text-dark me-2"><i class="bi bi-clock-history text-warning me-1"></i>Thời gian giữ ghế còn lại:</span>
            <span class="badge bg-danger fs-5 rounded-pill px-3 py-1">{{ timerDisplay }}</span>
          </div>

          <div class="bg-white p-4 p-md-5 rounded-xl border shadow-sm mb-4">
            <h4 class="fw-bold mb-3 border-bottom pb-3 text-slate-900">Tóm tắt đơn hàng #{{ order.id }}</h4>

            <div class="d-flex gap-3 mb-4">
              <div class="flex-grow-1">
                <h5 class="fw-bold mb-2 text-slate-900">Chi tiết ghế chọn</h5>
                <div class="d-flex flex-wrap gap-2 mb-3">
                  <span v-for="item in order.items" :key="item.id" class="badge bg-primary-custom fs-6 px-3 py-2 rounded-pill shadow-sm">
                    Ghế {{ item.seat_details?.seat_name || item.seat }} ({{ item.ticket_type_name }})
                  </span>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center fs-5 fw-bold border-top pt-3 text-slate-900">
              <span>Tổng tiền thanh toán:</span>
              <span class="text-primary-custom fs-2 fw-extrabold">{{ formatCurrency(order.total_amount) }}</span>
            </div>
          </div>

          <div class="bg-white p-4 p-md-5 rounded-xl border shadow-sm">
            <h5 class="fw-bold mb-3 text-slate-900">Phương thức thanh toán</h5>
            <div class="form-check p-3 border rounded-xl bg-light-custom mb-4">
              <input class="form-check-input" type="radio" checked id="payosRadio" />
              <label class="form-check-label fw-bold ms-2 text-slate-900" for="payosRadio">
                Thanh toán Online qua Cổng PayOS (VietQR / ATM / Mobile Banking)
              </label>
            </div>

            <button class="btn btn-cta w-100 rounded-pill py-3 fs-5" :disabled="loading || timeLeft <= 0 || order.status !== 'PENDING'" @click="handlePayOS">
              {{ loading ? 'Đang khởi tạo giao dịch...' : 'Thanh toán qua PayOS' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/services/api'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const loading = ref(false)
const timeLeft = ref(0)
const timerDisplay = ref('10:00')
let timerInterval = null

onMounted(async () => {
  try {
    const res = await apiClient.get(`orders/${route.params.orderId}/`)
    order.value = res.data

    if (order.value.status !== 'PENDING') {
      await Swal.fire({
        title: 'Đơn hàng không thể thanh toán',
        text: `Trạng thái hiện tại của đơn là ${order.value.status}.`,
        icon: 'info',
        confirmButtonColor: '#2563EB',
        customClass: { popup: 'rounded-4' }
      })
      router.push('/')
      return
    }

    startTimer()
  } catch (err) {
    Swal.fire({
      title: 'Lỗi tải đơn hàng',
      text: 'Không thể lấy thông tin đơn hàng hoặc đơn hàng không tồn tại.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    }).then(() => {
      router.push('/')
    })
  }
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

const startTimer = () => {
  const expiresAt = new Date(order.value.expires_at).getTime()
  timeLeft.value = Math.max(0, Math.floor((expiresAt - Date.now()) / 1000))
  updateTimerDisplay()

  if (timeLeft.value <= 0) {
    handleExpiredOrder()
    return
  }

  timerInterval = setInterval(() => {
    if (timeLeft.value <= 0) {
      clearInterval(timerInterval)
      handleExpiredOrder()
    } else {
      timeLeft.value--
      updateTimerDisplay()
    }
  }, 1000)
}

const updateTimerDisplay = () => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  timerDisplay.value = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const handleExpiredOrder = async () => {
  timeLeft.value = 0
  updateTimerDisplay()

  try {
    await apiClient.post(`orders/${order.value.id}/cancel/`)
  } catch (err) {
    console.info('Đơn hàng đã được backend xử lý hết hạn.', err.response?.data)
  }

  await Swal.fire({
    title: 'Hết thời gian giữ ghế',
    text: 'Đơn hàng đã hết hạn và ghế được trả về trạng thái trống.',
    icon: 'warning',
    confirmButtonText: 'Chọn lại ghế',
    confirmButtonColor: '#2563EB',
    customClass: { popup: 'rounded-4' }
  })
  router.push('/')
}

const handlePayOS = async () => {
  loading.value = true
  try {
    const res = await apiClient.post(`orders/${order.value.id}/payos-link/`)
    if (res.data.checkoutUrl) {
      window.location.href = res.data.checkoutUrl
    }
  } catch (err) {
    Swal.fire({
      title: 'Thanh toán thất bại',
      text: 'Không thể khởi tạo liên kết thanh toán PayOS. Vui lòng thử lại.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    loading.value = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val)
</script>

<style scoped>
.fw-extrabold {
  font-weight: 800;
}

.text-slate-900 {
  color: #0F172A;
}
</style>
