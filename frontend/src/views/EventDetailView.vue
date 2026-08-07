<template>
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary"></div>
  </div>
  <div v-else-if="event" class="bg-page-custom">
    <div class="position-relative text-white hero-detail">
      <img :src="event.thumbnail" class="w-100 h-100" style="object-fit: cover;" />
      <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-end p-4 p-md-5 detail-overlay">
        <div class="container">
          <span class="badge bg-primary-custom mb-2 px-3 py-2 rounded-pill fs-6">{{ event.category }}</span>
          <h1 class="fw-extrabold display-6 mb-3 text-shadow">{{ event.title }}</h1>
          <div class="d-flex flex-wrap gap-4 fs-6 text-light">
            <span><i class="bi bi-calendar-event me-2 text-warning"></i>{{ formatDate(event.start_time) }}</span>
            <span><i class="bi bi-geo-alt me-2 text-danger"></i>{{ event.location }}</span>
            <span><i class="bi bi-building me-2 text-cyan"></i>{{ event.organizer_name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container py-5">
      <div class="row g-4">
        <div class="col-lg-7">
          <div class="bg-white p-4 p-md-5 rounded-xl border shadow-sm mb-4">
            <h4 class="fw-bold mb-3 text-slate-900">Giới thiệu sự kiện</h4>
            <p class="lh-lg text-secondary style-pre-line fs-6">{{ event.description }}</p>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="bg-white p-4 rounded-xl border shadow-sm sticky-top-custom">
            <h4 class="fw-bold mb-4 text-slate-900">Thông tin loại vé</h4>
            <div class="mb-4">
              <div v-for="tt in event.ticket_types" :key="tt.id" class="p-3 mb-2 rounded-xl border bg-light-custom d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-bold text-slate-900">{{ tt.name }}</div>
                  <div class="text-muted fs-6">Sức chứa: {{ tt.quantity }} ghế</div>
                </div>
                <div class="fw-extrabold text-primary-custom fs-5">{{ formatCurrency(tt.price) }}</div>
              </div>
            </div>
            <button class="btn btn-cta w-100 rounded-pill py-3 fs-5" @click="fetchSeatsAndOpenModal">
              <i class="bi bi-grid-3x3-gap-fill me-2"></i>Mở sơ đồ chọn ghế
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="seatModal" tabindex="-1" ref="seatModalRef">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content rounded-xl border-0 shadow-lg">
          <div class="modal-header border-0 bg-dark-slate text-white rounded-top-xl p-3 px-4">
            <h5 class="modal-title fw-bold">Sơ đồ chọn ghế</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <SeatMap
              :seats="seats"
              :selected-seat-ids="selectedSeatIds"
              @toggle-select-seat="toggleSelectSeat"
            />
          </div>
          <div class="modal-footer border-0 d-flex justify-content-between align-items-center bg-light-custom rounded-bottom-xl p-3 px-4">
            <div>
              <span class="text-muted d-block small">Đã chọn: <strong class="text-slate-900 fs-6">{{ selectedSeatIds.length }} ghế</strong></span>
              <span class="fw-extrabold text-primary-custom fs-4">{{ formatCurrency(selectedSeatsTotal) }}</span>
            </div>
            <button class="btn btn-cta rounded-pill px-4 py-2.5 fw-bold" :disabled="selectedSeatIds.length === 0" @click="proceedHoldSeats">
              Giữ ghế ngay
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/services/api'
import { Modal } from 'bootstrap'
import Swal from 'sweetalert2'
import SeatMap from '@/components/SeatMap.vue'

const route = useRoute()
const router = useRouter()
const event = ref(null)
const seats = ref([])
const loading = ref(true)
const selectedSeatIds = ref([])
const seatModalRef = ref(null)

onMounted(async () => {
  try {
    const res = await apiClient.get(`events/${route.params.id}/`)
    event.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const selectedSeatsTotal = computed(() => {
  if (!selectedSeatIds.value || selectedSeatIds.value.length === 0 || !seats.value) return 0
  return seats.value
    .filter(s => selectedSeatIds.value.includes(s.id))
    .reduce((sum, s) => sum + parseFloat(s.price || 0), 0)
})

const fetchSeatsAndOpenModal = async () => {
  try {
    const res = await apiClient.get(`seats/event/${event.value.id}/`)
    seats.value = res.data
    selectedSeatIds.value = []
    
    if (seatModalRef.value) {
      const modalInstance = Modal.getOrCreateInstance(seatModalRef.value)
      modalInstance.show()
    }
  } catch (err) {
    Swal.fire({
      title: 'Lỗi sơ đồ ghế',
      text: 'Không thể lấy thông tin sơ đồ ghế, vui lòng thử lại sau.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  }
}

const toggleSelectSeat = (seatId) => {
  const idx = selectedSeatIds.value.indexOf(seatId)
  if (idx > -1) {
    selectedSeatIds.value.splice(idx, 1)
  } else {
    selectedSeatIds.value.push(seatId)
  }
}

const proceedHoldSeats = async () => {
  if (selectedSeatIds.value.length === 0) {
    Swal.fire({
      title: 'Chưa chọn ghế',
      text: 'Vui lòng chọn ít nhất 1 ghế trước khi bấm giữ ghế.',
      icon: 'info',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
    return
  }
  try {
    const res = await apiClient.post('orders/hold/', { seat_ids: selectedSeatIds.value })
    
    if (seatModalRef.value) {
      const modalInstance = Modal.getInstance(seatModalRef.value)
      modalInstance?.hide()
    }
    
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Giữ ghế thành công! Bạn có 10 phút thanh toán.',
      showConfirmButton: false,
      timer: 2000
    })
    router.push(`/checkout/${res.data.id}`)
  } catch (err) {
    Swal.fire({
      title: 'Giữ ghế thất bại',
      text: err.response?.data?.error || 'Không thể giữ ghế, vui lòng thử chọn ghế khác.',
      icon: 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
</script>

<style scoped>
.hero-detail {
  height: 400px;
}

.detail-overlay {
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.3) 100%);
}

.style-pre-line {
  white-space: pre-line;
}

.bg-dark-slate {
  background-color: #0F172A;
}

.text-cyan {
  color: #38BDF8;
}

.fw-extrabold {
  font-weight: 800;
}

.text-slate-900 {
  color: #0F172A;
}
</style>