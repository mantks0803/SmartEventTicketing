<template>
  <div class="admin-payments-page min-vh-100 py-5">
    <div class="container-fluid px-3 px-xl-4 px-xxl-5">
      <div class="row g-4 align-items-start">
        <main class="col-xl-10 order-2 order-xl-1 payment-main-column">
          <div class="page-heading mb-4">
            <div>
              <span class="admin-label">QUẢN TRỊ VIÊN</span>
              <h2 class="fw-bold mb-1 mt-1">Quản lý thanh toán</h2>
              <p class="text-muted mb-0">
                {{
                  activeSection === 'transactions'
                    ? 'Theo dõi đơn hàng, phát hiện bất thường và đối soát lại với PayOS.'
                    : 'Xem doanh thu và xác nhận quyết toán mô phỏng cho ban tổ chức.'
                }}
              </p>
            </div>

            <button
              type="button"
              class="btn btn-outline-primary rounded-pill px-4"
              :disabled="currentLoading"
              @click="refreshCurrentSection"
            >
              <i class="bi bi-arrow-clockwise me-2"></i>Làm mới
            </button>
          </div>

          <div class="payment-section-tabs mb-4" role="tablist" aria-label="Nội dung thanh toán">
            <button
              type="button"
              class="payment-section-tab"
              :class="{ active: activeSection === 'transactions' }"
              @click="changeSection('transactions')"
            >
              <span class="section-tab-icon"><i class="bi bi-credit-card"></i></span>
              <span>
                <strong>Giao dịch PayOS</strong>
                <small>Đơn hàng và đối soát</small>
              </span>
            </button>

            <button
              type="button"
              class="payment-section-tab"
              :class="{ active: activeSection === 'payouts' }"
              @click="changeSection('payouts')"
            >
              <span class="section-tab-icon"><i class="bi bi-wallet2"></i></span>
              <span>
                <strong>Quyết toán BTC</strong>
                <small>Xác nhận doanh thu sự kiện</small>
              </span>
            </button>
          </div>

          <template v-if="activeSection === 'transactions'">
          <div class="payment-summary-grid mb-4">
            <div class="summary-card">
              <span class="summary-icon icon-blue"><i class="bi bi-receipt"></i></span>
              <div>
                <small>Tổng đơn hàng</small><strong>{{ number(summary.total_orders) }}</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon icon-green"><i class="bi bi-check-circle"></i></span>
              <div>
                <small>Đã thanh toán</small><strong>{{ number(summary.paid_orders) }}</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon icon-orange"><i class="bi bi-hourglass-split"></i></span>
              <div>
                <small>Chờ thanh toán</small><strong>{{ number(summary.pending_orders) }}</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon icon-gray"><i class="bi bi-x-circle"></i></span>
              <div>
                <small>Đã hủy / hết hạn</small>
                <strong>{{ number(summary.cancelled_expired_orders) }}</strong>
              </div>
            </div>
            <div class="summary-card">
              <span class="summary-icon icon-red"><i class="bi bi-exclamation-triangle"></i></span>
              <div>
                <small>Cần chú ý</small><strong>{{ number(summary.needs_attention) }}</strong>
              </div>
            </div>
            <div class="summary-card revenue-card">
              <span class="summary-icon icon-purple"><i class="bi bi-cash-stack"></i></span>
              <div>
                <small>Doanh thu PAID</small><strong>{{ currency(summary.total_revenue) }}</strong>
              </div>
            </div>
          </div>

          <form class="filter-card mb-4" @submit.prevent="applyFilters">
            <div class="row g-3">
              <div class="col-xl-6">
                <label for="payment-search" class="form-label fw-semibold">Tìm kiếm</label>
                <div class="input-group">
                  <span class="input-group-text bg-white border-end-0">
                    <i class="bi bi-search text-muted"></i>
                  </span>
                  <input
                    id="payment-search"
                    v-model.trim="filterForm.search"
                    type="text"
                    class="form-control border-start-0"
                    placeholder="Mã đơn, transaction ID, khách hàng, sự kiện..."
                  />
                </div>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="payment-status" class="form-label fw-semibold">Trạng thái</label>
                <select id="payment-status" v-model="filterForm.status" class="form-select">
                  <option value="">Tất cả trạng thái</option>
                  <option v-for="item in orderStatuses" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="payment-event" class="form-label fw-semibold">Sự kiện</label>
                <select id="payment-event" v-model="filterForm.event_id" class="form-select">
                  <option value="">Tất cả sự kiện</option>
                  <option v-for="event in filterOptions.events" :key="event.id" :value="event.id">
                    {{ event.title }}
                  </option>
                </select>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="payment-organizer" class="form-label fw-semibold">Ban tổ chức</label>
                <select
                  id="payment-organizer"
                  v-model="filterForm.organizer_id"
                  class="form-select"
                >
                  <option value="">Tất cả ban tổ chức</option>
                  <option
                    v-for="organizer in filterOptions.organizers"
                    :key="organizer.id"
                    :value="organizer.id"
                  >
                    {{ organizer.company_name }}
                  </option>
                </select>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="payment-date-from" class="form-label fw-semibold">Từ ngày</label>
                <input
                  id="payment-date-from"
                  v-model="filterForm.date_from"
                  type="date"
                  class="form-control"
                />
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="payment-date-to" class="form-label fw-semibold">Đến ngày</label>
                <input
                  id="payment-date-to"
                  v-model="filterForm.date_to"
                  type="date"
                  class="form-control"
                />
              </div>

              <div class="col-sm-6 col-xl-3 filter-actions">
                <button type="button" class="btn btn-light" @click="resetFilters">Đặt lại</button>
                <button type="submit" class="btn btn-primary">Áp dụng</button>
              </div>
            </div>
          </form>

          <section class="content-card">
            <div v-if="loading" class="state-box">
              <div class="spinner-border text-primary"></div>
              <p class="text-muted mt-3 mb-0">Đang tải giao dịch...</p>
            </div>

            <div v-else-if="orders.length === 0" class="state-box">
              <i class="bi bi-receipt-cutoff empty-icon"></i>
              <h5 class="fw-bold mt-3">Không tìm thấy giao dịch</h5>
              <p class="text-muted mb-0">Hãy thử thay đổi từ khóa hoặc bộ lọc.</p>
            </div>

            <div v-else class="payment-list">
              <div class="payment-list-heading">
                <div>
                  <strong>Danh sách giao dịch</strong>
                  <small>Thông tin tổng hợp theo bộ lọc đang chọn</small>
                </div>
                <span>{{ number(totalCount) }} kết quả</span>
              </div>

              <article
                v-for="order in orders"
                :key="order.id"
                class="payment-order-card"
                :class="{ 'has-warning': order.needs_attention }"
              >
                <header class="payment-card-header">
                  <div class="order-heading">
                    <span class="order-icon"><i class="bi bi-receipt"></i></span>
                    <div>
                      <div class="order-number">Đơn hàng #{{ order.id }}</div>
                      <span class="order-time">
                        <i class="bi bi-clock me-1"></i>{{ dateTime(order.created_at) }}
                      </span>
                    </div>
                  </div>

                  <div class="order-badges">
                    <span v-if="order.needs_attention" class="warning-badge">
                      <i class="bi bi-exclamation-triangle me-1"></i>Cần kiểm tra
                    </span>
                    <span v-else class="normal-badge">
                      <i class="bi bi-shield-check me-1"></i>Bình thường
                    </span>
                    <span class="status-badge" :class="statusClass(order.status)">
                      {{ statusText(order.status) }}
                    </span>
                  </div>
                </header>

                <div class="payment-card-body">
                  <section class="payment-info-block">
                    <span class="info-icon customer-icon"><i class="bi bi-person"></i></span>
                    <div class="info-content">
                      <span class="info-label">Khách hàng</span>
                      <strong>{{ order.customer_name }}</strong>
                      <small>{{ order.customer_email }}</small>
                    </div>
                  </section>

                  <section class="payment-info-block">
                    <span class="info-icon event-icon"><i class="bi bi-calendar-event"></i></span>
                    <div class="info-content">
                      <span class="info-label">Sự kiện</span>
                      <strong>{{ order.event_title }}</strong>
                      <small>{{ order.organizer_name }}</small>
                    </div>
                  </section>

                  <section class="amount-block">
                    <span class="info-label">Tổng thanh toán</span>
                    <strong>{{ currency(order.total_amount) }}</strong>
                    <small>
                      <i class="bi bi-ticket-perforated me-1"></i>
                      {{ order.ticket_count }}/{{ order.item_count }} vé đã phát hành
                    </small>
                  </section>
                </div>

                <div v-if="order.needs_attention" class="inline-warning">
                  <i class="bi bi-exclamation-circle-fill"></i>
                  <span>{{ order.warning_message }}</span>
                </div>

                <footer class="payment-card-footer">
                  <div class="transaction-row">
                    <span class="transaction-label">Mã giao dịch PayOS</span>
                    <code>{{ order.transaction_id || 'Chưa có mã giao dịch' }}</code>
                  </div>

                  <button
                    type="button"
                    class="btn btn-outline-primary rounded-pill px-4 detail-button"
                    @click="openDetail(order.id)"
                  >
                    Xem chi tiết<i class="bi bi-arrow-right ms-2"></i>
                  </button>
                </footer>
              </article>
            </div>
          </section>

          <PaginationControls
            :current-page="currentPage"
            :total-pages="totalPages"
            @page-change="changePage"
          />
          </template>

          <AdminPayoutPanel v-else ref="payoutPanelRef" />
        </main>

        <aside class="col-xl-2 order-1 order-xl-2">
          <AdminSidebar />
        </aside>
      </div>
    </div>

    <div ref="detailModalRef" class="modal fade" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content payment-modal">
          <div class="modal-header border-0 px-4 pt-4">
            <div>
              <span class="admin-label">CHI TIẾT GIAO DỊCH</span>
              <h4 class="modal-title fw-bold mt-1">Đơn hàng #{{ selectedOrder?.id || '' }}</h4>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body px-4 pb-4">
            <div v-if="detailLoading" class="state-box py-5">
              <div class="spinner-border text-primary"></div>
            </div>

            <template v-else-if="selectedOrder">
              <div v-if="selectedOrder.needs_attention" class="payment-warning mb-4">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <div>
                  <strong>{{ selectedOrder.warning_code }}</strong>
                  <p class="mb-0">{{ selectedOrder.warning_message }}</p>
                </div>
              </div>

              <div class="detail-grid mb-4">
                <div class="detail-card">
                  <small>Khách hàng</small>
                  <strong>{{ selectedOrder.customer_name }}</strong>
                  <span>{{ selectedOrder.customer_email }}</span>
                </div>
                <div class="detail-card">
                  <small>Sự kiện</small>
                  <strong>{{ selectedOrder.event_title }}</strong>
                  <span>{{ selectedOrder.organizer_name }}</span>
                </div>
                <div class="detail-card">
                  <small>Tổng tiền</small>
                  <strong class="text-primary">{{ currency(selectedOrder.total_amount) }}</strong>
                  <span>{{ statusText(selectedOrder.status) }}</span>
                </div>
                <div class="detail-card">
                  <small>Thời gian</small>
                  <strong>{{ dateTime(selectedOrder.created_at) }}</strong>
                  <span>Hết hạn: {{ dateTime(selectedOrder.expires_at) }}</span>
                </div>
              </div>

              <h6 class="section-title">Ghế và loại vé</h6>
              <div class="table-responsive detail-table-wrap mb-4">
                <table class="table align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Ghế</th>
                      <th>Loại vé</th>
                      <th>Đơn giá</th>
                      <th>Trạng thái ghế</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in selectedOrder.items" :key="item.id">
                      <td>{{ item.seat_details?.seat_name }}</td>
                      <td>{{ item.ticket_type_name }}</td>
                      <td>{{ currency(item.unit_price) }}</td>
                      <td>{{ item.seat_details?.status }}</td>
                    </tr>
                    <tr v-if="selectedOrder.items.length === 0">
                      <td colspan="4" class="text-center text-muted">Đơn hàng chưa có ghế.</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h6 class="section-title">Bản ghi thanh toán</h6>
              <div class="table-responsive detail-table-wrap mb-4">
                <table class="table align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Nhà cung cấp</th>
                      <th>Transaction ID</th>
                      <th>Số tiền</th>
                      <th>Trạng thái</th>
                      <th>Thời gian</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="payment in selectedOrder.payments" :key="payment.id">
                      <td>{{ payment.provider }}</td>
                      <td class="transaction-text">{{ payment.transaction_id || 'Chưa có' }}</td>
                      <td>{{ currency(payment.amount) }}</td>
                      <td>{{ payment.payment_status || payment.status }}</td>
                      <td>{{ dateTime(payment.created_at) }}</td>
                    </tr>
                    <tr v-if="selectedOrder.payments.length === 0">
                      <td colspan="5" class="text-center text-muted">
                        Chưa có bản ghi thanh toán.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h6 class="section-title">Vé đã phát hành</h6>
              <div class="table-responsive detail-table-wrap">
                <table class="table align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Mã vé</th>
                      <th>Ghế</th>
                      <th>Loại vé</th>
                      <th>Check-in</th>
                      <th>Ngày phát hành</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ticket in selectedOrder.tickets" :key="ticket.id">
                      <td>#{{ ticket.id }}</td>
                      <td>{{ ticket.seat_details?.seat_name }}</td>
                      <td>{{ ticket.ticket_type_name }}</td>
                      <td>{{ ticket.is_checked_in ? 'Đã check-in' : 'Chưa check-in' }}</td>
                      <td>{{ dateTime(ticket.issued_at) }}</td>
                    </tr>
                    <tr v-if="selectedOrder.tickets.length === 0">
                      <td colspan="5" class="text-center text-muted">Chưa phát hành vé.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
          </div>

          <div class="modal-footer border-0 px-4 pb-4">
            <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">
              Đóng
            </button>
            <button
              v-if="canReconcile(selectedOrder)"
              type="button"
              class="btn btn-primary rounded-pill px-4"
              :disabled="reconciling"
              @click="confirmReconcile"
            >
              <span v-if="reconciling" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-arrow-repeat me-2"></i>
              Kiểm tra PayOS
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

import AdminPayoutPanel from '@/components/admin/AdminPayoutPanel.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import PaginationControls from '@/components/PaginationControls.vue'
import apiClient from '@/services/api'

const activeSection = ref('transactions')
const payoutPanelRef = ref(null)
const orders = ref([])
const summary = ref({})
const filterOptions = ref({ events: [], organizers: [] })
const loading = ref(true)
const detailLoading = ref(false)
const reconciling = ref(false)
const selectedOrder = ref(null)
const detailModalRef = ref(null)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 10

let detailModal = null

const filterForm = reactive({
  search: '',
  status: '',
  event_id: '',
  organizer_id: '',
  date_from: '',
  date_to: '',
})

const appliedFilters = reactive({ ...filterForm })

const orderStatuses = [
  { value: 'PENDING', label: 'Chờ thanh toán' },
  { value: 'PAID', label: 'Đã thanh toán' },
  { value: 'CANCELLED', label: 'Đã hủy' },
  { value: 'EXPIRED', label: 'Hết hạn' },
  { value: 'REFUNDED', label: 'Đã hoàn tiền' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const currentLoading = computed(() => activeSection.value === 'transactions' && loading.value)

const changeSection = (section) => {
  activeSection.value = section
}

const refreshCurrentSection = () => {
  if (activeSection.value === 'transactions') {
    refreshData()
    return
  }
  payoutPanelRef.value?.refreshData()
}

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

const fetchOrders = async () => {
  const response = await apiClient.get('orders/admin/payments/', {
    params: buildParams(true),
  })
  orders.value = response.data.results || []
  totalCount.value = Number(response.data.count || 0)
}

const fetchSummary = async () => {
  const response = await apiClient.get('orders/admin/payments/summary/', {
    params: buildParams(),
  })
  summary.value = response.data || {}
}

const fetchFilterOptions = async () => {
  const response = await apiClient.get('orders/admin/revenue-report/filters/')
  filterOptions.value = {
    events: response.data.events || [],
    organizers: response.data.organizers || [],
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([fetchOrders(), fetchSummary()])
  } catch (error) {
    orders.value = []
    totalCount.value = 0
    await showError('Không thể tải giao dịch', error)
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
      confirmButtonColor: '#2563eb',
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

const fetchDetail = async (orderId) => {
  const response = await apiClient.get(`orders/admin/payments/${orderId}/`)
  selectedOrder.value = response.data
}

const openDetail = async (orderId) => {
  selectedOrder.value = null
  detailLoading.value = true
  detailModal?.show()
  try {
    await fetchDetail(orderId)
  } catch (error) {
    detailModal?.hide()
    await showError('Không thể tải chi tiết giao dịch', error)
  } finally {
    detailLoading.value = false
  }
}

const canReconcile = (order) => ['PENDING', 'EXPIRED'].includes(order?.status)

const confirmReconcile = async () => {
  if (!selectedOrder.value || reconciling.value) return

  const result = await Swal.fire({
    title: 'Kiểm tra lại với PayOS?',
    text: `Hệ thống sẽ đối soát đơn #${selectedOrder.value.id} bằng dữ liệu PayOS.`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Kiểm tra PayOS',
    cancelButtonText: 'Quay lại',
    confirmButtonColor: '#2563eb',
  })
  if (!result.isConfirmed) return

  reconciling.value = true
  try {
    const response = await apiClient.post(
      `orders/admin/payments/${selectedOrder.value.id}/reconcile-payos/`,
      {},
    )

    if (response.data.status === 'success') {
      await Swal.fire({
        title: 'Đối soát thành công',
        text: 'Đơn hàng, thanh toán và vé đã được đồng bộ an toàn.',
        icon: 'success',
        confirmButtonColor: '#2563eb',
      })
    } else {
      await Swal.fire({
        title: 'PayOS chưa ghi nhận thanh toán',
        text: `Trạng thái hiện tại: ${response.data.payos_status || 'UNKNOWN'}. Dữ liệu đơn hàng chưa bị thay đổi.`,
        icon: 'info',
        confirmButtonColor: '#2563eb',
      })
    }

    const orderId = selectedOrder.value.id
    await Promise.all([refreshData(), fetchDetail(orderId)])
  } catch (error) {
    await Swal.fire({
      title: 'Không thể đối soát giao dịch',
      text: `${errorMessage(error)} Không tự ý thanh toán lại nếu PayOS đã trừ tiền.`,
      icon: 'error',
      confirmButtonColor: '#dc2626',
    })
  } finally {
    reconciling.value = false
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
  error.response?.data?.error || error.response?.data?.detail || 'Vui lòng thử lại sau.'

const statusText = (value) =>
  ({
    PENDING: 'Chờ thanh toán',
    PAID: 'Đã thanh toán',
    CANCELLED: 'Đã hủy',
    EXPIRED: 'Hết hạn',
    REFUNDED: 'Đã hoàn tiền',
  })[value] || value

const statusClass = (value) => `status-${String(value || '').toLowerCase()}`
const number = (value) => new Intl.NumberFormat('vi-VN').format(Number(value || 0))
const currency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))

const dateTime = (value) => {
  if (!value) return 'Không có'
  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(async () => {
  if (detailModalRef.value) detailModal = new Modal(detailModalRef.value)
  try {
    await fetchFilterOptions()
  } catch (error) {
    await showError('Không thể tải bộ lọc', error)
  }
  await refreshData()
})

onUnmounted(() => {
  detailModal?.dispose()
})
</script>

<style scoped src="./AdminPaymentManagementView.css"></style>
