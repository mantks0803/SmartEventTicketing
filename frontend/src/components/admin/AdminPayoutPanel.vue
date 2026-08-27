<template>
  <div class="payout-panel">
    <div class="payout-notice mb-4">
      <i class="bi bi-info-circle-fill"></i>
      <div>
        <strong>Chức năng quyết toán mô phỏng</strong>
        <span>Xác nhận tại đây chỉ cập nhật trạng thái, không chuyển tiền thật.</span>
      </div>
    </div>

    <div class="payout-summary-grid mb-4">
      <div class="payout-summary-card">
        <span class="summary-icon icon-orange"><i class="bi bi-hourglass-split"></i></span>
        <div>
          <small>Sự kiện chờ quyết toán</small>
          <strong>{{ formatNumber(summary.pending_events) }}</strong>
        </div>
      </div>
      <div class="payout-summary-card">
        <span class="summary-icon icon-purple"><i class="bi bi-cash-coin"></i></span>
        <div>
          <small>Doanh thu chờ quyết toán</small>
          <strong>{{ formatCurrency(summary.pending_revenue) }}</strong>
        </div>
      </div>
      <div class="payout-summary-card">
        <span class="summary-icon icon-green"><i class="bi bi-check2-circle"></i></span>
        <div>
          <small>Sự kiện đã quyết toán</small>
          <strong>{{ formatNumber(summary.completed_events) }}</strong>
        </div>
      </div>
      <div class="payout-summary-card">
        <span class="summary-icon icon-blue"><i class="bi bi-wallet2"></i></span>
        <div>
          <small>Doanh thu đã ghi nhận</small>
          <strong>{{ formatCurrency(summary.completed_revenue) }}</strong>
        </div>
      </div>
    </div>

    <form class="payout-filter-card mb-4" @submit.prevent="applyFilters">
      <div class="row g-3 align-items-end">
        <div class="col-lg-5">
          <label for="payout-search" class="form-label fw-semibold">Tìm kiếm</label>
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0">
              <i class="bi bi-search text-muted"></i>
            </span>
            <input
              id="payout-search"
              v-model.trim="filterForm.search"
              type="text"
              class="form-control border-start-0"
              placeholder="Tên sự kiện hoặc ban tổ chức..."
            />
          </div>
        </div>

        <div class="col-sm-6 col-lg-3">
          <label for="payout-status" class="form-label fw-semibold">Trạng thái</label>
          <select id="payout-status" v-model="filterForm.status" class="form-select">
            <option value="">Tất cả trạng thái</option>
            <option value="PENDING">Chờ quyết toán</option>
            <option value="COMPLETED">Đã quyết toán</option>
          </select>
        </div>

        <div class="col-sm-6 col-lg-2">
          <label for="payout-date-from" class="form-label fw-semibold">Từ ngày</label>
          <input
            id="payout-date-from"
            v-model="filterForm.date_from"
            type="date"
            class="form-control"
          />
        </div>

        <div class="col-sm-6 col-lg-2">
          <label for="payout-date-to" class="form-label fw-semibold">Đến ngày</label>
          <input
            id="payout-date-to"
            v-model="filterForm.date_to"
            type="date"
            class="form-control"
          />
        </div>

        <div class="col-12 payout-filter-actions">
          <button type="button" class="btn btn-light" @click="resetFilters">Đặt lại</button>
          <button type="submit" class="btn btn-primary">Áp dụng</button>
        </div>
      </div>
    </form>

    <section class="payout-content-card">
      <div v-if="loading" class="state-box">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3 mb-0">Đang tải danh sách quyết toán...</p>
      </div>

      <div v-else-if="payouts.length === 0" class="state-box">
        <i class="bi bi-wallet2 empty-icon"></i>
        <h5 class="fw-bold mt-3">Không tìm thấy sự kiện</h5>
        <p class="text-muted mb-0">Chỉ hiển thị sự kiện đã diễn ra và có đơn PAID.</p>
      </div>

      <div v-else class="payout-list">
        <div class="payout-list-heading">
          <div>
            <strong>Quyết toán theo sự kiện</strong>
            <small>Doanh thu chỉ tính từ các đơn hàng PAID</small>
          </div>
          <span>{{ formatNumber(totalCount) }} kết quả</span>
        </div>

        <article v-for="payout in payouts" :key="payout.event_id" class="payout-event-card">
          <header class="payout-card-header">
            <div class="payout-event-heading">
              <img
                v-if="payout.event_thumbnail"
                :src="payout.event_thumbnail"
                :alt="payout.event_title"
                class="payout-thumbnail"
              />
              <span v-else class="payout-event-icon">
                <i class="bi bi-calendar2-event"></i>
              </span>
              <div>
                <h5>{{ payout.event_title }}</h5>
                <small><i class="bi bi-building me-1"></i>{{ payout.organizer_name }}</small>
              </div>
            </div>

            <span
              class="payout-status-badge"
              :class="payout.is_payout_completed ? 'completed' : 'pending'"
            >
              <i
                class="bi me-1"
                :class="payout.is_payout_completed ? 'bi-check-circle-fill' : 'bi-clock-fill'"
              ></i>
              {{ payout.is_payout_completed ? 'Đã quyết toán' : 'Chờ quyết toán' }}
            </span>
          </header>

          <div class="payout-card-body">
            <div class="payout-stat">
              <span>Ngày diễn ra</span>
              <strong>{{ formatDateTime(payout.start_time) }}</strong>
            </div>
            <div class="payout-stat">
              <span>Đơn PAID</span>
              <strong>{{ formatNumber(payout.paid_orders) }}</strong>
            </div>
            <div class="payout-stat">
              <span>Vé đã bán / check-in</span>
              <strong>
                {{ formatNumber(payout.sold_tickets) }} /
                {{ formatNumber(payout.checked_in_tickets) }}
              </strong>
            </div>
            <div class="payout-stat revenue">
              <span>Tổng doanh thu</span>
              <strong>{{ formatCurrency(payout.total_revenue) }}</strong>
            </div>
          </div>

          <footer class="payout-card-footer">
            <p v-if="payout.is_payout_completed" class="completed-note mb-0">
              <i class="bi bi-check2-circle me-1"></i>Trạng thái đã được ghi nhận trong hệ thống.
            </p>
            <p v-else-if="payout.can_settle" class="eligible-note mb-0">
              <i class="bi bi-shield-check me-1"></i>Sự kiện đã đủ điều kiện quyết toán.
            </p>
            <p v-else class="mb-0">
              <i class="bi bi-info-circle me-1"></i>Sự kiện chưa đủ điều kiện quyết toán.
            </p>

            <div class="payout-actions">
              <button
                type="button"
                class="btn btn-outline-primary rounded-pill"
                @click="openDetail(payout.event_id)"
              >
                <i class="bi bi-eye me-1"></i>Chi tiết
              </button>
              <button
                v-if="canComplete(payout)"
                type="button"
                class="btn btn-success rounded-pill"
                :disabled="completingEventId === payout.event_id"
                @click="confirmComplete(payout)"
              >
                <span
                  v-if="completingEventId === payout.event_id"
                  class="spinner-border spinner-border-sm me-1"
                ></span>
                <i v-else class="bi bi-check2-circle me-1"></i>
                Xác nhận quyết toán
              </button>
            </div>
          </footer>
        </article>
      </div>
    </section>

    <PaginationControls
      :current-page="currentPage"
      :total-pages="totalPages"
      @page-change="changePage"
    />

    <div ref="detailModalRef" class="modal fade" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content payout-modal">
          <div class="modal-header border-0 px-4 pt-4">
            <div>
              <span class="admin-label">CHI TIẾT QUYẾT TOÁN</span>
              <h4 class="modal-title fw-bold mt-1">
                {{ selectedPayout?.event_title || 'Đang tải...' }}
              </h4>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body px-4 pb-4">
            <div v-if="detailLoading" class="state-box py-5">
              <div class="spinner-border text-primary"></div>
            </div>

            <template v-else-if="selectedPayout">
              <div class="payout-modal-note mb-4">
                <i class="bi bi-info-circle"></i>
                <span>Đây là xác nhận nội bộ, hệ thống không thực hiện chuyển tiền thật.</span>
              </div>

              <div class="payout-detail-grid mb-4">
                <div class="detail-card">
                  <small>Ban tổ chức</small>
                  <strong>{{ selectedPayout.organizer_name }}</strong>
                  <span>{{ formatDateTime(selectedPayout.start_time) }}</span>
                </div>
                <div class="detail-card">
                  <small>Đơn đã thanh toán</small>
                  <strong>{{ formatNumber(selectedPayout.paid_orders) }}</strong>
                  <span>Chỉ tính đơn PAID</span>
                </div>
                <div class="detail-card">
                  <small>Vé / Check-in</small>
                  <strong>
                    {{ formatNumber(selectedPayout.sold_tickets) }} /
                    {{ formatNumber(selectedPayout.checked_in_tickets) }}
                  </strong>
                  <span>Vé đã phát hành</span>
                </div>
                <div class="detail-card">
                  <small>Tổng doanh thu</small>
                  <strong class="text-primary">
                    {{ formatCurrency(selectedPayout.total_revenue) }}
                  </strong>
                  <span>
                    {{ selectedPayout.is_payout_completed ? 'Đã quyết toán' : 'Chờ quyết toán' }}
                  </span>
                </div>
              </div>

              <h6 class="section-title">Doanh thu theo loại vé</h6>
              <div class="table-responsive detail-table-wrap mb-4">
                <table class="table align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Loại vé</th>
                      <th>Số lượng đã bán</th>
                      <th>Doanh thu</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in selectedPayout.revenue_by_ticket_type"
                      :key="item.ticket_type_id || item.ticket_type_name"
                    >
                      <td>{{ item.ticket_type_name }}</td>
                      <td>{{ formatNumber(item.sold_quantity) }}</td>
                      <td class="fw-semibold">{{ formatCurrency(item.revenue) }}</td>
                    </tr>
                    <tr v-if="selectedPayout.revenue_by_ticket_type.length === 0">
                      <td colspan="3" class="text-center text-muted">
                        Chưa có doanh thu theo loại vé.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h6 class="section-title">Các đơn hàng đã thanh toán</h6>
              <div v-if="selectedPayout.transactions.length" class="payout-transactions">
                <div
                  v-for="transaction in selectedPayout.transactions"
                  :key="transaction.order_id"
                  class="payout-transaction-item"
                >
                  <div>
                    <strong>Đơn #{{ transaction.order_id }}</strong>
                    <small
                      >{{ transaction.customer_name }} · {{ transaction.customer_email }}</small
                    >
                  </div>
                  <div>
                    <strong>{{ formatCurrency(transaction.total_amount) }}</strong>
                    <small>
                      {{ formatNumber(transaction.ticket_count) }} vé ·
                      {{ formatDateTime(transaction.created_at) }}
                    </small>
                  </div>
                </div>
              </div>
              <p v-else class="empty-detail mb-0">Chưa có đơn hàng PAID.</p>
            </template>
          </div>

          <div class="modal-footer border-0 px-4 pb-4">
            <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">
              Đóng
            </button>
            <button
              v-if="canComplete(selectedPayout)"
              type="button"
              class="btn btn-success rounded-pill px-4"
              :disabled="completingEventId === selectedPayout.event_id"
              @click="confirmComplete(selectedPayout, true)"
            >
              <span
                v-if="completingEventId === selectedPayout.event_id"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              <i v-else class="bi bi-check2-circle me-2"></i>
              Xác nhận quyết toán
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { Modal } from 'bootstrap'
import Swal from 'sweetalert2'

import PaginationControls from '@/components/PaginationControls.vue'
import apiClient from '@/services/api'

const payouts = ref([])
const summary = ref({})
const loading = ref(true)
const detailLoading = ref(false)
const selectedPayout = ref(null)
const completingEventId = ref(null)
const detailModalRef = ref(null)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 8

let detailModal = null

const filterForm = reactive({
  search: '',
  status: '',
  date_from: '',
  date_to: '',
})

const appliedFilters = reactive({ ...filterForm })
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))

const buildParams = (includePage = false) => {
  const params = {}
  Object.entries(appliedFilters).forEach(([key, value]) => {
    if (value !== '') params[key] = value
  })
  if (includePage) {
    params.page = currentPage.value
    params.page_size = pageSize
  }
  return params
}

const fetchPayouts = async () => {
  const response = await apiClient.get('orders/admin/payouts/', {
    params: buildParams(true),
  })
  payouts.value = response.data.results || []
  totalCount.value = Number(response.data.count || 0)
}

const fetchSummary = async () => {
  const response = await apiClient.get('orders/admin/payouts/summary/', {
    params: buildParams(),
  })
  summary.value = response.data || {}
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([fetchPayouts(), fetchSummary()])
  } catch (error) {
    payouts.value = []
    totalCount.value = 0
    await showError('Không thể tải dữ liệu quyết toán', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  if (filterForm.date_from && filterForm.date_to && filterForm.date_from > filterForm.date_to) {
    Swal.fire({
      title: 'Khoảng ngày không hợp lệ',
      text: 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.',
      icon: 'warning',
      confirmButtonColor: '#F47C5A',
    })
    return
  }

  Object.assign(appliedFilters, filterForm)
  currentPage.value = 1
  refreshData()
}

const resetFilters = () => {
  Object.keys(filterForm).forEach((key) => {
    filterForm[key] = ''
  })
  Object.assign(appliedFilters, filterForm)
  currentPage.value = 1
  refreshData()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  refreshData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const fetchDetail = async (eventId) => {
  const response = await apiClient.get(`orders/admin/payouts/${eventId}/`)
  selectedPayout.value = {
    ...response.data,
    revenue_by_ticket_type: response.data.revenue_by_ticket_type || [],
    transactions: response.data.transactions || [],
  }
}

const openDetail = async (eventId) => {
  selectedPayout.value = null
  detailLoading.value = true
  detailModal?.show()
  try {
    await fetchDetail(eventId)
  } catch (error) {
    detailModal?.hide()
    await showError('Không thể tải chi tiết quyết toán', error)
  } finally {
    detailLoading.value = false
  }
}

const canComplete = (payout) => Boolean(payout?.can_settle) && payout?.is_payout_completed === false

const confirmComplete = async (payout, detailIsOpen = false) => {
  if (!canComplete(payout) || completingEventId.value) return

  const result = await Swal.fire({
    title: 'Xác nhận đã quyết toán?',
    text: `Sự kiện "${payout.event_title}" sẽ được đánh dấu đã quyết toán. Đây chỉ là mô phỏng, không chuyển tiền thật.`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Xác nhận quyết toán',
    cancelButtonText: 'Quay lại',
    confirmButtonColor: '#16a34a',
  })
  if (!result.isConfirmed) return

  completingEventId.value = payout.event_id
  try {
    const response = await apiClient.post(`orders/admin/payouts/${payout.event_id}/complete/`, {})

    await Swal.fire({
      title: 'Đã quyết toán',
      text: response.data.message || 'Trạng thái quyết toán đã được cập nhật.',
      icon: 'success',
      confirmButtonColor: '#F47C5A',
    })

    await refreshData()
    if (detailIsOpen) await fetchDetail(payout.event_id)
  } catch (error) {
    await showError('Không thể xác nhận quyết toán', error)
    await refreshData()
    if (detailIsOpen) {
      try {
        await fetchDetail(payout.event_id)
      } catch {
        detailModal?.hide()
      }
    }
  } finally {
    completingEventId.value = null
  }
}

const showError = (title, error) =>
  Swal.fire({
    title,
    text: errorMessage(error),
    icon: 'error',
    confirmButtonColor: '#dc2626',
  })

const errorMessage = (error) =>
  error.response?.data?.error ||
  error.response?.data?.detail ||
  error.response?.data?.message ||
  'Vui lòng thử lại sau.'

const formatNumber = (value) => new Intl.NumberFormat('vi-VN').format(Number(value || 0))

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))

const formatDateTime = (value) => {
  if (!value) return 'Không có'
  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(() => {
  if (detailModalRef.value) detailModal = new Modal(detailModalRef.value)
  refreshData()
})

onUnmounted(() => {
  detailModal?.dispose()
})

defineExpose({ refreshData })
</script>

<style scoped src="./AdminPayoutPanel.css"></style>
