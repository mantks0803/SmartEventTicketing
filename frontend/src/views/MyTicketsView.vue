<template>
  <div class="bg-page-custom py-5">
    <div class="container">
      <h3 class="fw-bold mb-4 text-slate-900">Ví vé điện tử của tôi</h3>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="tickets.length === 0" class="text-center py-5 bg-white rounded-xl border shadow-sm">
        <i class="bi bi-ticket-perforated display-1 text-muted"></i>
        <p class="text-secondary mt-3 fs-5">Bạn chưa có vé điện tử nào.</p>
      </div>

      <div v-else class="row g-4">
        <div v-for="t in tickets" :key="t.id" class="col-md-6 col-12">
          <div class="card rounded-xl border shadow-sm p-3.5 bg-white">
            <div class="d-flex align-items-center gap-3">
              <div class="bg-blue-subtle p-3 rounded-xl text-center" style="min-width: 90px;">
                <i class="bi bi-qr-code fs-1 text-primary-custom"></i>
              </div>
              <div class="flex-grow-1">
                <h6 class="fw-bold mb-1 text-slate-900">{{ t.event_title }}</h6>
                <p class="text-muted small mb-1"><i class="bi bi-geo-alt text-danger me-1"></i>{{ t.event_location }}</p>
                <p class="text-primary-custom fw-bold small mb-0">Ghế: {{ t.seat_row }}{{ t.seat_number }} ({{ t.ticket_type_name }})</p>
              </div>
            </div>
            <div class="mt-3 pt-3 border-top d-flex justify-content-between align-items-center">
              <span class="badge" :class="t.is_checked_in ? 'bg-secondary' : 'bg-success'">
                {{ t.is_checked_in ? 'Đã soát vé' : 'Hợp lệ' }}
              </span>
              <button class="btn btn-outline-primary btn-sm rounded-pill px-3 fw-semibold" @click="showQrModal(t)">Xem QR</button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal fade" id="qrModal" tabindex="-1" ref="qrModalRef">
        <div class="modal-dialog modal-dialog-centered modal-sm">
          <div class="modal-content rounded-xl border-0 shadow-lg text-center p-4" v-if="selectedTicket">
            <h6 class="fw-bold mb-3 text-slate-900">Mã Soát Vé QR</h6>
            <div class="bg-light p-3 rounded-xl mb-3 d-inline-block mx-auto border">
              <i class="bi bi-qr-code display-1 text-dark"></i>
            </div>
            <p class="font-monospace fw-bold mb-1 fs-6 text-primary-custom">{{ selectedTicket.qr_code }}</p>
            <p class="text-muted small mb-0">Đưa mã này cho Ban tổ chức tại cổng</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/services/api'
import { Modal } from 'bootstrap'

const tickets = ref([])
const loading = ref(true)
const selectedTicket = ref(null)
const qrModalRef = ref(null)
let bsQrModal = null

onMounted(async () => {
  try {
    const res = await apiClient.get('orders/my-tickets/')
    tickets.value = res.data
    if (qrModalRef.value) {
      bsQrModal = new Modal(qrModalRef.value)
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const showQrModal = (ticket) => {
  selectedTicket.value = ticket
  bsQrModal?.show()
}
</script>

<style scoped>
.text-slate-900 {
  color: #0F172A;
}

.bg-blue-subtle {
  background-color: #EFF6FF;
}
</style>