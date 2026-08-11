<template>
  <div class="admin-page min-vh-100 py-5">
    <div class="container">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div>
          <span class="admin-label">QUẢN TRỊ VIÊN</span>
          <h2 class="fw-bold text-slate-900 mb-1 mt-1">Duyệt sự kiện</h2>
          <p class="text-muted mb-0">
            Kiểm tra thông tin trước khi công khai sự kiện cho khách hàng.
          </p>
        </div>

        <button
          type="button"
          class="btn btn-outline-primary rounded-pill px-4"
          :disabled="loading"
          @click="fetchEvents"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>Làm mới
        </button>
      </div>

      <div class="filter-card mb-4">
        <div class="d-flex flex-wrap gap-2 mb-3">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            type="button"
            class="btn rounded-pill px-3"
            :class="statusFilter === filter.value ? 'btn-primary' : 'btn-light border'"
            @click="changeStatusFilter(filter.value)"
          >
            {{ filter.label }}
          </button>
        </div>

        <form class="input-group" @submit.prevent="applySearch">
          <span class="input-group-text bg-white border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input
            v-model.trim="searchInput"
            type="text"
            class="form-control border-start-0"
            placeholder="Tìm theo tên sự kiện, địa điểm..."
          />
          <button class="btn btn-primary px-4" type="submit">
            Tìm kiếm
          </button>
        </form>
      </div>

      <div class="content-card">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-3 mb-0">Đang tải danh sách sự kiện...</p>
        </div>

        <div v-else-if="events.length === 0" class="empty-state">
          <i class="bi bi-calendar2-check"></i>
          <h5 class="fw-bold text-slate-900 mt-3">Không có sự kiện phù hợp</h5>
          <p class="text-muted mb-0">Hãy thử đổi trạng thái hoặc từ khóa tìm kiếm.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table align-middle mb-0">
            <thead>
              <tr>
                <th>Sự kiện</th>
                <th>Ban tổ chức</th>
                <th>Thời gian</th>
                <th>Sức chứa</th>
                <th>Trạng thái</th>
                <th class="text-end">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="event in events" :key="event.id">
                <td>
                  <div class="d-flex align-items-center gap-3 event-cell">
                    <img
                      :src="event.thumbnail || fallbackImage"
                      :alt="event.title"
                      class="event-thumbnail"
                      @error="useFallbackImage"
                    />
                    <div>
                      <div class="fw-bold text-slate-900 event-title">
                        {{ event.title }}
                      </div>
                      <small class="text-muted">
                        <i class="bi bi-geo-alt me-1"></i>{{ event.location }}
                      </small>
                    </div>
                  </div>
                </td>
                <td>{{ event.organizer_name }}</td>
                <td>{{ formatDate(event.start_time) }}</td>
                <td>{{ formatNumber(getCapacity(event)) }} ghế</td>
                <td>
                  <span class="status-badge" :class="getStatusClass(event.status)">
                    {{ getStatusText(event.status) }}
                  </span>
                </td>
                <td>
                  <div class="d-flex justify-content-end flex-wrap gap-2 action-buttons">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary rounded-pill"
                      @click="openEventDetail(event.id)"
                    >
                      Chi tiết
                    </button>

                    <template v-if="event.status === 'PENDING'">
                      <button
                        type="button"
                        class="btn btn-sm btn-success rounded-pill"
                        :disabled="actionLoadingId === event.id"
                        @click="approveEvent(event)"
                      >
                        <span
                          v-if="actionLoadingId === event.id"
                          class="spinner-border spinner-border-sm me-1"
                        ></span>
                        Duyệt
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-danger rounded-pill"
                        :disabled="actionLoadingId === event.id"
                        @click="rejectEvent(event)"
                      >
                        Từ chối
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <PaginationControls
        :current-page="currentPage"
        :total-pages="totalPages"
        @page-change="changePage"
      />

      <div
        ref="detailModalRef"
        class="modal fade"
        tabindex="-1"
        aria-hidden="true"
      >
        <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
          <div class="modal-content rounded-xl border-0">
            <div class="modal-header">
              <h5 class="modal-title fw-bold">Chi tiết sự kiện</h5>
              <button
                type="button"
                class="btn-close"
                data-bs-dismiss="modal"
                aria-label="Đóng"
              ></button>
            </div>

            <div v-if="detailLoading" class="modal-body text-center py-5">
              <div class="spinner-border text-primary"></div>
            </div>

            <div v-else-if="selectedEvent" class="modal-body p-4">
              <img
                :src="selectedEvent.thumbnail || fallbackImage"
                :alt="selectedEvent.title"
                class="detail-thumbnail mb-4"
                @error="useFallbackImage"
              />

              <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
                <h4 class="fw-bold text-slate-900 mb-0">
                  {{ selectedEvent.title }}
                </h4>
                <span
                  class="status-badge"
                  :class="getStatusClass(selectedEvent.status)"
                >
                  {{ getStatusText(selectedEvent.status) }}
                </span>
              </div>

              <p class="text-muted mb-1">
                <i class="bi bi-building me-2"></i>{{ selectedEvent.organizer_name }}
              </p>
              <p class="text-muted mb-1">
                <i class="bi bi-calendar3 me-2"></i>{{ formatDate(selectedEvent.start_time) }}
              </p>
              <p class="text-muted mb-4">
                <i class="bi bi-geo-alt me-2"></i>{{ selectedEvent.location }}
              </p>

              <h6 class="fw-bold">Mô tả</h6>
              <p class="event-description text-secondary">
                {{ selectedEvent.description }}
              </p>

              <h6 class="fw-bold mt-4">Loại vé</h6>
              <div class="row g-2">
                <div
                  v-for="ticket in selectedEvent.ticket_types"
                  :key="ticket.id"
                  class="col-md-6"
                >
                  <div class="ticket-type-card">
                    <strong>{{ ticket.name }}</strong>
                    <span>{{ formatCurrency(ticket.price) }}</span>
                    <small>{{ formatNumber(ticket.quantity) }} ghế</small>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-if="selectedEvent?.status === 'PENDING'"
              class="modal-footer border-0"
            >
              <button
                type="button"
                class="btn btn-outline-danger rounded-pill px-4"
                :disabled="actionLoadingId === selectedEvent.id"
                @click="rejectEvent(selectedEvent)"
              >
                Từ chối
              </button>
              <button
                type="button"
                class="btn btn-success rounded-pill px-4"
                :disabled="actionLoadingId === selectedEvent.id"
                @click="approveEvent(selectedEvent)"
              >
                Duyệt sự kiện
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Modal } from 'bootstrap'
import Swal from 'sweetalert2'

import PaginationControls from '@/components/PaginationControls.vue'
import apiClient from '@/services/api'

const events = ref([])
const loading = ref(true)
const detailLoading = ref(false)
const selectedEvent = ref(null)
const detailModalRef = ref(null)
const actionLoadingId = ref(null)

const statusFilter = ref('PENDING')
const searchInput = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 10
const fallbackImage = '/ticket_icon_150905.png'

let detailModal = null

const statusFilters = [
  { value: 'PENDING', label: 'Chờ duyệt' },
  { value: 'PUBLISHED', label: 'Đã duyệt' },
  { value: 'CANCELLED', label: 'Đã từ chối' },
  { value: 'ALL', label: 'Tất cả' }
]

const totalPages = computed(() => (
  Math.max(1, Math.ceil(totalCount.value / pageSize))
))

const fetchEvents = async () => {
  loading.value = true

  const params = {
    page: currentPage.value,
    page_size: pageSize
  }

  if (statusFilter.value !== 'ALL') {
    params.status = statusFilter.value
  }

  if (searchKeyword.value) {
    params.search = searchKeyword.value
  }

  try {
    const response = await apiClient.get('events/admin/', { params })
    events.value = response.data.results || []
    totalCount.value = Number(response.data.count || 0)
  } catch (error) {
    events.value = []
    totalCount.value = 0

    await Swal.fire({
      title: 'Không thể tải sự kiện',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    loading.value = false
  }
}

const changeStatusFilter = (status) => {
  if (statusFilter.value === status) return
  statusFilter.value = status
  currentPage.value = 1
  fetchEvents()
}

const applySearch = () => {
  searchKeyword.value = searchInput.value
  currentPage.value = 1
  fetchEvents()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchEvents()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const openEventDetail = async (eventId) => {
  selectedEvent.value = null
  detailLoading.value = true
  detailModal?.show()

  try {
    const response = await apiClient.get(`events/admin/${eventId}/`)
    selectedEvent.value = response.data
  } catch (error) {
    detailModal?.hide()

    await Swal.fire({
      title: 'Không thể tải chi tiết',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    detailLoading.value = false
  }
}

const approveEvent = async (event) => {
  const result = await Swal.fire({
    title: 'Duyệt sự kiện?',
    text: `Sự kiện "${event.title}" sẽ được công khai cho khách hàng.`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Duyệt sự kiện',
    cancelButtonText: 'Hủy',
    confirmButtonColor: '#10B981',
    customClass: { popup: 'rounded-4' }
  })

  if (!result.isConfirmed) return
  await updateEventStatus(event, 'approve')
}

const rejectEvent = async (event) => {
  const result = await Swal.fire({
    title: 'Từ chối sự kiện?',
    text: `Sự kiện "${event.title}" sẽ không được công khai.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Từ chối',
    cancelButtonText: 'Quay lại',
    confirmButtonColor: '#EF4444',
    customClass: { popup: 'rounded-4' }
  })

  if (!result.isConfirmed) return
  await updateEventStatus(event, 'reject')
}

const updateEventStatus = async (event, action) => {
  actionLoadingId.value = event.id

  try {
    // Backend kiểm tra quyền và chỉ cho đổi trạng thái từ PENDING.
    const response = await apiClient.post(
      `events/admin/${event.id}/${action}/`
    )

    detailModal?.hide()

    await Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: response.data.message || 'Cập nhật sự kiện thành công.',
      showConfirmButton: false,
      timer: 2200,
      timerProgressBar: true
    })

    currentPage.value = 1
    await fetchEvents()
  } catch (error) {
    const isConflict = error.response?.status === 409

    await Swal.fire({
      title: isConflict ? 'Sự kiện đã được xử lý' : 'Cập nhật thất bại',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: isConflict ? 'info' : 'error',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' }
    })

    if (isConflict) {
      detailModal?.hide()
      await fetchEvents()
    }
  } finally {
    actionLoadingId.value = null
  }
}

const getErrorMessage = (error, fallback) => (
  error.response?.data?.error
  || error.response?.data?.detail
  || fallback
)

const getCapacity = (event) => (
  (event.ticket_types || []).reduce(
    (total, ticket) => total + Number(ticket.quantity || 0),
    0
  )
)

const getStatusText = (status) => ({
  PENDING: 'Chờ duyệt',
  PUBLISHED: 'Đã duyệt',
  CANCELLED: 'Đã từ chối'
}[status] || status)

const getStatusClass = (status) => ({
  PENDING: 'status-pending',
  PUBLISHED: 'status-published',
  CANCELLED: 'status-cancelled'
}[status] || 'status-pending')

const useFallbackImage = (event) => {
  if (event.target.src.endsWith(fallbackImage)) return
  event.target.src = fallbackImage
}

const formatNumber = (value) => (
  new Intl.NumberFormat('vi-VN').format(Number(value || 0))
)

const formatCurrency = (value) => (
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0
  }).format(Number(value || 0))
)

const formatDate = (value) => {
  if (!value) return 'Chưa xác định'

  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

onMounted(async () => {
  if (detailModalRef.value) {
    detailModal = new Modal(detailModalRef.value)
  }

  await fetchEvents()
})

onUnmounted(() => {
  detailModal?.dispose()
})
</script>

<style scoped src="./AdminEventApprovalView.css"></style>
