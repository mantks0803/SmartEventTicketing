<template>
  <div class="payment-result-page min-vh-100 py-5">
    <div class="container">
      <div class="result-card mx-auto">
        <div v-if="state === 'checking'" class="result-content">
          <div class="spinner-border text-primary result-spinner"></div>
          <h3 class="fw-bold text-slate-900 mt-4">Đang xác nhận thanh toán</h3>
          <p class="text-muted mb-0">
            Hệ thống đang kiểm tra trực tiếp trạng thái giao dịch với PayOS.
          </p>
        </div>

        <div v-else-if="state === 'success'" class="result-content">
          <div class="result-icon success-icon">
            <i class="bi bi-check-lg"></i>
          </div>
          <h3 class="fw-bold text-slate-900 mt-4">Thanh toán thành công!</h3>
          <p class="text-muted">
            Vé điện tử đã được tạo và email xác nhận đang được gửi đến bạn.
          </p>

          <div v-if="order" class="order-summary">
            <div class="summary-row">
              <span>Mã đơn hàng</span>
              <strong>#{{ order.id }}</strong>
            </div>
            <div class="summary-row">
              <span>Sự kiện</span>
              <strong>{{ order.event_title }}</strong>
            </div>
            <div class="summary-row">
              <span>Trạng thái</span>
              <span class="badge bg-success rounded-pill">Đã thanh toán</span>
            </div>
            <div class="summary-row">
              <span>Tổng tiền</span>
              <strong class="text-primary fs-5">
                {{ formatCurrency(order.total_amount) }}
              </strong>
            </div>
          </div>

          <button
            type="button"
            class="btn btn-primary rounded-pill px-5 py-3 fw-bold"
            @click="viewTickets"
          >
            <i class="bi bi-ticket-perforated me-2"></i>Xem vé của tôi
          </button>
        </div>

        <div v-else-if="state === 'cancelled'" class="result-content">
          <div class="result-icon cancelled-icon">
            <i class="bi bi-x-lg"></i>
          </div>
          <h3 class="fw-bold text-slate-900 mt-4">Đã hủy thanh toán</h3>
          <p class="text-muted">
            Giao dịch chưa được thanh toán. Các ghế đang giữ sẽ tự động được
            trả lại khi đơn hàng hết hạn.
          </p>
          <router-link to="/" class="btn btn-outline-primary rounded-pill px-5 py-3">
            Chọn sự kiện khác
          </router-link>
        </div>

        <div v-else-if="state === 'waiting'" class="result-content">
          <div class="result-icon waiting-icon">
            <i class="bi bi-hourglass-split"></i>
          </div>
          <h3 class="fw-bold text-slate-900 mt-4">Giao dịch đang được đối soát</h3>
          <p class="text-muted">
            PayOS chưa gửi kết quả về hệ thống. Nếu bạn đã chuyển tiền, hãy đợi
            thêm một lúc rồi kiểm tra lại.
          </p>
          <div class="d-flex flex-wrap justify-content-center gap-2">
            <button
              type="button"
              class="btn btn-primary rounded-pill px-4"
              @click="retryPaymentCheck"
            >
              <i class="bi bi-arrow-clockwise me-2"></i>Kiểm tra lại
            </button>
            <router-link to="/my-tickets" class="btn btn-outline-primary rounded-pill px-4">
              Mở ví vé
            </router-link>
          </div>
        </div>

        <div v-else class="result-content">
          <div class="result-icon error-icon">
            <i class="bi bi-exclamation-lg"></i>
          </div>
          <h3 class="fw-bold text-slate-900 mt-4">Không thể kiểm tra giao dịch</h3>
          <p class="text-muted">
            {{ errorMessage }}
          </p>
          <router-link to="/" class="btn btn-primary rounded-pill px-5">
            Về trang chủ
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Swal from 'sweetalert2'

import apiClient from '@/services/api'

const route = useRoute()
const router = useRouter()

const state = ref('checking')
const order = ref(null)
const errorMessage = ref(
  'Không tìm thấy đơn hàng hoặc bạn không có quyền xem đơn này.'
)

let pollTimer = null
let pollAttempts = 0
let stopped = false
let successMessageShown = false

const maxPollAttempts = 15

const orderId = computed(() => String(
  route.query.orderCode || route.query.orderId || ''
))

const reconcileOrder = async () => {
  const response = await apiClient.post(
    `orders/${orderId.value}/reconcile-payos/`,
    {},
    { timeout: 8000 }
  )
  if (response.data.order) {
    order.value = response.data.order
  }
  return response.data
}

const clearPollTimer = () => {
  if (pollTimer) {
    window.clearTimeout(pollTimer)
    pollTimer = null
  }
}

const showPaymentSuccess = async () => {
  clearPollTimer()
  state.value = 'success'

  if (successMessageShown) return
  successMessageShown = true

  await Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: 'Thanh toán thành công',
    text: 'Vé điện tử của bạn đã được phát hành.',
    showConfirmButton: false,
    timer: 2500,
    timerProgressBar: true
  })
}

const pollOrderStatus = async () => {
  if (stopped || !orderId.value) return

  try {
    const result = await reconcileOrder()
    if (stopped) return

    const currentOrder = result.order
    const payosStatus = String(result.payos_status || '').toUpperCase()

    if (!currentOrder) {
      clearPollTimer()
      errorMessage.value = 'Phản hồi kiểm tra giao dịch không hợp lệ.'
      state.value = 'error'
      return
    }

    if (result.status === 'success' && currentOrder.status === 'PAID') {
      await showPaymentSuccess()
      return
    }

    if (
      ['CANCELLED', 'EXPIRED', 'REFUNDED'].includes(currentOrder.status)
      || ['CANCELLED', 'EXPIRED'].includes(payosStatus)
    ) {
      clearPollTimer()
      state.value = 'cancelled'
      return
    }

    pollAttempts += 1

    if (pollAttempts >= maxPollAttempts) {
      clearPollTimer()
      state.value = 'waiting'
      return
    }

    pollTimer = window.setTimeout(pollOrderStatus, 2000)
  } catch (error) {
    console.error(error)

    const responseStatus = error.response?.status

    if (responseStatus === 409) {
      clearPollTimer()
      errorMessage.value = `${
        error.response?.data?.error
        || 'PayOS đã ghi nhận giao dịch nhưng vé chưa thể phát hành.'
      } Không thanh toán lại; vui lòng liên hệ hỗ trợ với mã đơn #${orderId.value}.`
      state.value = 'error'
      return
    }

    if (
      responseStatus >= 400
      && responseStatus < 500
    ) {
      clearPollTimer()
      errorMessage.value = (
        error.response?.data?.error
        || 'Giao dịch không thể được xác nhận tự động.'
      )
      state.value = 'error'
      return
    }

    pollAttempts += 1
    if (pollAttempts >= maxPollAttempts) {
      clearPollTimer()
      state.value = 'waiting'
      return
    }

    pollTimer = window.setTimeout(pollOrderStatus, 2000)
  }
}

const retryPaymentCheck = () => {
  clearPollTimer()
  pollAttempts = 0
  errorMessage.value = 'Không thể xác nhận giao dịch.'
  state.value = 'checking'
  pollOrderStatus()
}

const viewTickets = () => {
  router.push({
    name: 'my-tickets',
    query: { order: orderId.value }
  })
}

const formatCurrency = (value) => new Intl.NumberFormat('vi-VN', {
  style: 'currency',
  currency: 'VND',
  maximumFractionDigits: 0
}).format(Number(value || 0))

onMounted(() => {
  if (!orderId.value || !/^\d+$/.test(orderId.value)) {
    state.value = 'error'
    return
  }

  pollOrderStatus()
})

onUnmounted(() => {
  stopped = true
  clearPollTimer()
})
</script>

<style scoped>
.payment-result-page {
  background: radial-gradient(circle at top, rgba(37, 99, 235, 0.12), transparent 35%), #F8FAFC;
}

.result-card {
  max-width: 650px;
  overflow: hidden;
  border: 1px solid #E2E8F0;
  border-radius: 24px;
  background: #FFFFFF;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
}

.result-content {
  padding: 55px 40px;
  text-align: center;
}

.result-spinner {
  width: 64px;
  height: 64px;
}

.result-icon {
  width: 92px;
  height: 92px;
  margin: 0 auto;
  border-radius: 50%;
  font-size: 2.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-icon {
  background: #D1FAE5;
  color: #059669;
}

.cancelled-icon,
.error-icon {
  background: #FEE2E2;
  color: #DC2626;
}

.waiting-icon {
  background: #FEF3C7;
  color: #D97706;
}

.order-summary {
  padding: 18px;
  margin: 28px 0;
  border: 1px solid #DBEAFE;
  border-radius: 16px;
  background: #F8FAFC;
  text-align: left;
}

.summary-row {
  padding: 10px 0;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.summary-row:last-child {
  border-bottom: none;
}

.text-slate-900 {
  color: #0F172A;
}

@media (max-width: 576px) {
  .result-content {
    padding: 40px 20px;
  }

  .summary-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
