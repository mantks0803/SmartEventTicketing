<template>
  <div class="ticket-wallet-page min-vh-100 py-5">
    <div class="container">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div>
          <h3 class="fw-bold text-slate-900 mb-1">Ví vé điện tử của tôi</h3>
          <p class="text-muted mb-0">
            Chỉ các vé đã thanh toán thành công mới xuất hiện tại đây.
          </p>
        </div>

        <button
          type="button"
          class="btn btn-outline-primary rounded-pill px-4"
          :disabled="loading"
          @click="fetchTickets"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>Làm mới
        </button>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3">Đang tải vé điện tử...</p>
      </div>

      <div v-else-if="tickets.length === 0" class="empty-ticket-state">
        <div class="empty-ticket-icon">
          <i class="bi bi-ticket-perforated"></i>
        </div>
        <h4 class="fw-bold text-slate-900 mt-3">Bạn chưa có vé điện tử</h4>
        <p class="text-muted">
          Sau khi thanh toán thành công, vé và mã QR sẽ xuất hiện ở đây.
        </p>
        <router-link to="/" class="btn btn-primary rounded-pill px-4">
          Khám phá sự kiện
        </router-link>
      </div>

      <div v-else class="row g-4">
        <div v-for="ticket in tickets" :key="ticket.id" class="col-lg-6">
          <article
            class="ticket-card"
            :class="{ 'highlight-ticket': isHighlighted(ticket) }"
          >
            <div class="ticket-image-wrapper">
              <img
                :src="ticket.event_thumbnail || fallbackImage"
                :alt="ticket.event_title"
                class="ticket-image"
                @error="useFallbackImage"
              />
              <span
                class="ticket-status"
                :class="ticket.is_checked_in ? 'status-used' : 'status-valid'"
              >
                {{ ticket.is_checked_in ? 'Đã soát vé' : 'Vé hợp lệ' }}
              </span>
            </div>

            <div class="ticket-content">
              <small class="text-muted">Đơn hàng #{{ ticket.order_id }}</small>
              <h5 class="fw-bold text-slate-900 mt-1 mb-3">
                {{ ticket.event_title }}
              </h5>

              <div class="ticket-info-row">
                <i class="bi bi-calendar3 text-primary"></i>
                <span>{{ formatDate(ticket.event_start_time) }}</span>
              </div>
              <div class="ticket-info-row">
                <i class="bi bi-geo-alt text-danger"></i>
                <span>{{ ticket.event_location }}</span>
              </div>

              <div class="ticket-details">
                <div>
                  <small>Loại vé</small>
                  <strong>{{ ticket.ticket_type_name }}</strong>
                </div>
                <div>
                  <small>Ghế</small>
                  <strong>{{ ticket.seat_name }}</strong>
                </div>
                <div>
                  <small>Giá vé</small>
                  <strong>{{ formatCurrency(ticket.price) }}</strong>
                </div>
              </div>

              <button
                type="button"
                class="btn btn-primary rounded-pill w-100 py-2 fw-bold"
                @click="showQrModal(ticket)"
              >
                <i class="bi bi-qr-code me-2"></i>Xem mã QR
              </button>
            </div>
          </article>
        </div>
      </div>

      <div
        id="qrModal"
        ref="qrModalRef"
        class="modal fade"
        tabindex="-1"
        aria-hidden="true"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div v-if="selectedTicket" class="modal-content qr-modal-content">
            <div class="modal-header border-0">
              <h5 class="modal-title fw-bold">Vé điện tử</h5>
              <button
                type="button"
                class="btn-close"
                data-bs-dismiss="modal"
                aria-label="Đóng"
              ></button>
            </div>

            <div class="modal-body text-center pt-0">
              <h5 class="fw-bold text-slate-900 mb-1">
                {{ selectedTicket.event_title }}
              </h5>
              <p class="text-muted small mb-4">
                {{ formatDate(selectedTicket.event_start_time) }}
              </p>

              <div v-if="!selectedTicket.is_checked_in" class="qr-code-wrapper">
                <QrcodeVue
                  :value="selectedTicket.qr_code"
                  :size="220"
                  level="H"
                  render-as="svg"
                />
              </div>

              <div v-else class="used-ticket-box">
                <i class="bi bi-check-circle-fill"></i>
                <strong>Vé đã được sử dụng</strong>
              </div>

              <div class="mt-4">
                <div class="fw-bold">
                  {{ selectedTicket.ticket_type_name }} – Ghế {{ selectedTicket.seat_name }}
                </div>
                <div class="font-monospace small text-muted mt-2 qr-text">
                  {{ selectedTicket.qr_code }}
                </div>
              </div>

              <div class="qr-warning mt-4">
                <i class="bi bi-shield-lock me-2"></i>
                Không chia sẻ mã QR cho người khác. Mỗi vé chỉ được check-in một lần.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Modal } from 'bootstrap'
import QrcodeVue from 'qrcode.vue'
import Swal from 'sweetalert2'

import apiClient from '@/services/api'

const route = useRoute()

const tickets = ref([])
const loading = ref(true)
const selectedTicket = ref(null)
const qrModalRef = ref(null)

const fallbackImage = '/ticket_icon_150905.png'
let qrModal = null

const fetchTickets = async () => {
  loading.value = true

  try {
    const response = await apiClient.get('orders/my-tickets/')
    tickets.value = Array.isArray(response.data)
      ? response.data
      : response.data.results || []
  } catch (error) {
    tickets.value = []

    await Swal.fire({
      title: 'Không thể tải vé',
      text: error.response?.data?.detail || 'Vui lòng thử lại sau.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    loading.value = false
  }
}

const showQrModal = async (ticket) => {
  selectedTicket.value = ticket
  await nextTick()
  qrModal?.show()
}

const isHighlighted = (ticket) => (
  route.query.order
  && String(ticket.order_id) === String(route.query.order)
)

const useFallbackImage = (event) => {
  if (event.target.src.endsWith(fallbackImage)) return
  event.target.src = fallbackImage
}

const formatCurrency = (value) => new Intl.NumberFormat('vi-VN', {
  style: 'currency',
  currency: 'VND',
  maximumFractionDigits: 0
}).format(Number(value || 0))

const formatDate = (dateValue) => {
  if (!dateValue) return 'Chưa xác định'

  return new Date(dateValue).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

onMounted(async () => {
  if (qrModalRef.value) {
    qrModal = new Modal(qrModalRef.value)
  }
  await fetchTickets()
})

onUnmounted(() => {
  qrModal?.dispose()
})
</script>

<style scoped>
.ticket-wallet-page {
  background: radial-gradient(circle at top right, rgba(37, 99, 235, 0.08), transparent 32%), #F8FAFC;
}

.ticket-card {
  overflow: hidden;
  height: 100%;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  background: #FFFFFF;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  transition: all 0.25s ease;
}

.ticket-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.11);
}

.highlight-ticket {
  border: 2px solid #2563EB;
  box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.1);
}

.ticket-image-wrapper {
  position: relative;
  height: 190px;
}

.ticket-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ticket-status {
  position: absolute;
  top: 14px;
  right: 14px;
  padding: 7px 13px;
  border-radius: 999px;
  color: #FFFFFF;
  font-size: 0.75rem;
  font-weight: 700;
  box-shadow: 0 5px 14px rgba(15, 23, 42, 0.2);
}

.status-valid {
  background: #059669;
}

.status-used {
  background: #64748B;
}

.ticket-content {
  padding: 22px;
}

.ticket-info-row {
  margin-bottom: 10px;
  color: #475569;
  font-size: 0.9rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.ticket-details {
  padding: 16px;
  margin: 20px 0;
  border-radius: 14px;
  background: #F8FAFC;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.ticket-details small {
  display: block;
  margin-bottom: 4px;
  color: #94A3B8;
}

.ticket-details strong {
  color: #0F172A;
  font-size: 0.88rem;
}

.empty-ticket-state {
  padding: 70px 20px;
  border: 1px solid #E2E8F0;
  border-radius: 22px;
  background: #FFFFFF;
  text-align: center;
}

.empty-ticket-icon {
  width: 90px;
  height: 90px;
  margin: 0 auto;
  border-radius: 24px;
  background: #EFF6FF;
  color: #2563EB;
  font-size: 2.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-modal-content {
  padding: 8px;
  border: none;
  border-radius: 22px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
}

.qr-code-wrapper {
  width: fit-content;
  padding: 18px;
  margin: 0 auto;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  background: #FFFFFF;
}

.used-ticket-box {
  width: 220px;
  height: 220px;
  margin: 0 auto;
  border-radius: 16px;
  background: #F1F5F9;
  color: #64748B;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
}

.used-ticket-box i {
  font-size: 3rem;
}

.qr-text {
  overflow-wrap: anywhere;
}

.qr-warning {
  padding: 12px;
  border-radius: 12px;
  background: #FFF7ED;
  color: #C2410C;
  font-size: 0.8rem;
}

.text-slate-900 {
  color: #0F172A;
}

@media (max-width: 576px) {
  .ticket-details {
    grid-template-columns: 1fr;
  }
}
</style>
