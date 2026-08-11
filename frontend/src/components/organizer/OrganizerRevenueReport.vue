<template>
  <section class="revenue-report">
    <div class="report-panel mb-4">
      <div class="report-toolbar">
        <div>
          <h4 class="fw-bold text-slate-900 mb-1">
            Báo cáo doanh thu
          </h4>
          <p class="text-muted mb-0">
            Doanh thu chỉ tính từ các đơn hàng đã thanh toán thành công.
          </p>
        </div>

        <div v-if="events.length > 0" class="event-select-box">
          <label for="report-event" class="form-label fw-semibold mb-1">
            Chọn sự kiện
          </label>

          <div class="d-flex gap-2">
            <select
              id="report-event"
              v-model="selectedEventId"
              class="form-select"
              :disabled="loading"
              @change="loadReport"
            >
              <option
                v-for="event in events"
                :key="event.id"
                :value="event.id"
              >
                {{ event.title }}
              </option>
            </select>

            <button
              type="button"
              class="btn btn-outline-primary"
              title="Làm mới báo cáo"
              :disabled="loading || !selectedEventId"
              @click="loadReport"
            >
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="events.length === 0" class="report-panel empty-report">
      <i class="bi bi-bar-chart empty-report-icon"></i>
      <h5 class="fw-bold mt-3">Chưa có sự kiện để lập báo cáo</h5>
      <p class="text-muted mb-0">
        Hãy tạo sự kiện trước khi xem báo cáo doanh thu.
      </p>
    </div>

    <div v-else-if="loading" class="report-panel text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-3 mb-0">
        Đang tổng hợp dữ liệu doanh thu...
      </p>
    </div>

    <template v-else-if="report">
      <div class="report-title-row mb-3">
        <div>
          <h5 class="fw-bold text-slate-900 mb-1">
            {{ report.event_title }}
          </h5>

          <div class="d-flex flex-wrap gap-2">
            <span
              class="report-status"
              :class="getStatusClass(report.event_status)"
            >
              {{ getStatusText(report.event_status) }}
            </span>

            <span
              class="report-status"
              :class="
                report.is_payout_completed
                  ? 'status-payout-done'
                  : 'status-payout-pending'
              "
            >
              {{
                report.is_payout_completed
                  ? 'Đã đối soát'
                  : 'Chưa đối soát'
              }}
            </span>
          </div>
        </div>

        <small class="text-muted">Dữ liệu hiện tại của sự kiện</small>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card">
            <div class="report-stat-icon icon-blue">
              <i class="bi bi-grid-3x3-gap"></i>
            </div>
            <small>Tổng ghế</small>
            <strong>{{ formatNumber(report.total_seats) }}</strong>
          </div>
        </div>

        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card">
            <div class="report-stat-icon icon-green">
              <i class="bi bi-ticket-perforated"></i>
            </div>
            <small>Đã bán</small>
            <strong>{{ formatNumber(report.sold_seats) }}</strong>
          </div>
        </div>

        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card">
            <div class="report-stat-icon icon-slate">
              <i class="bi bi-check2-circle"></i>
            </div>
            <small>Còn trống</small>
            <strong>{{ formatNumber(report.available_seats) }}</strong>
          </div>
        </div>

        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card">
            <div class="report-stat-icon icon-orange">
              <i class="bi bi-hourglass-split"></i>
            </div>
            <small>Đang giữ</small>
            <strong>{{ formatNumber(report.locked_seats) }}</strong>
          </div>
        </div>

        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card">
            <div class="report-stat-icon icon-purple">
              <i class="bi bi-qr-code-scan"></i>
            </div>
            <small>Đã check-in</small>
            <strong>{{ formatNumber(report.checked_in_tickets) }}</strong>
          </div>
        </div>

        <div class="col-sm-6 col-md-4 col-xl-2">
          <div class="report-stat-card revenue-card">
            <div class="report-stat-icon icon-revenue">
              <i class="bi bi-cash-stack"></i>
            </div>
            <small>Doanh thu</small>
            <strong class="revenue-value">
              {{ formatCurrency(report.total_revenue) }}
            </strong>
          </div>
        </div>
      </div>

      <div class="report-panel mb-4">
        <div class="table-heading">
          <div>
            <h5 class="fw-bold mb-1">Doanh thu theo loại vé</h5>
            <small class="text-muted">
              Số lượng và doanh thu của từng hạng vé
            </small>
          </div>
        </div>

        <div class="table-responsive mt-3">
          <table class="table report-table align-middle mb-0">
            <thead>
              <tr>
                <th>Loại vé</th>
                <th class="text-center">Số vé đã bán</th>
                <th class="text-end">Doanh thu</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="ticketType in report.revenue_by_ticket_type"
                :key="ticketType.ticket_type_id"
              >
                <td class="fw-semibold">
                  {{ ticketType.ticket_type_name }}
                </td>
                <td class="text-center">
                  {{ formatNumber(ticketType.sold_quantity) }}
                </td>
                <td class="text-end fw-semibold text-success">
                  {{ formatCurrency(ticketType.revenue) }}
                </td>
              </tr>

              <tr v-if="report.revenue_by_ticket_type.length === 0">
                <td colspan="3" class="text-center text-muted py-4">
                  Sự kiện chưa có loại vé.
                </td>
              </tr>
            </tbody>

            <tfoot>
              <tr>
                <th colspan="2">Tổng doanh thu</th>
                <th class="text-end text-success">
                  {{ formatCurrency(report.total_revenue) }}
                </th>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div class="report-panel">
        <div class="table-heading">
          <div>
            <h5 class="fw-bold mb-1">Giao dịch đã thanh toán</h5>
            <small class="text-muted">
              Chỉ hiển thị các đơn hàng có trạng thái PAID
            </small>
          </div>

          <span class="transaction-count">
            {{ report.transactions.length }} giao dịch
          </span>
        </div>

        <div class="table-responsive mt-3">
          <table class="table report-table align-middle mb-0">
            <thead>
              <tr>
                <th>Mã đơn</th>
                <th>Khách hàng</th>
                <th class="text-center">Số ghế</th>
                <th>Thời gian</th>
                <th class="text-end">Tổng tiền</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="transaction in report.transactions"
                :key="transaction.order_id"
              >
                <td>
                  <span class="order-code">#{{ transaction.order_id }}</span>
                </td>
                <td class="fw-semibold">{{ transaction.customer_name }}</td>
                <td class="text-center">{{ transaction.seat_count }}</td>
                <td class="text-muted">
                  {{ formatDate(transaction.created_at) }}
                </td>
                <td class="text-end fw-semibold">
                  {{ formatCurrency(transaction.total_amount) }}
                </td>
              </tr>

              <tr v-if="report.transactions.length === 0">
                <td colspan="5" class="text-center text-muted py-5">
                  <i class="bi bi-receipt d-block fs-2 mb-2"></i>
                  Sự kiện chưa có giao dịch thanh toán thành công.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import Swal from 'sweetalert2'

import apiClient from '@/services/api'

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

const selectedEventId = ref('')
const report = ref(null)
const loading = ref(false)

// Mỗi lần chọn sự kiện, frontend gọi API báo cáo riêng của sự kiện đó.
const loadReport = async () => {
  if (!selectedEventId.value) {
    report.value = null
    return
  }

  loading.value = true

  try {
    const response = await apiClient.get(
      `orders/organizer/events/${selectedEventId.value}/report/`
    )

    report.value = response.data
  } catch (error) {
    report.value = null

    await Swal.fire({
      title: 'Không thể tải báo cáo',
      text:
        error.response?.data?.error
        || error.response?.data?.detail
        || 'Vui lòng kiểm tra lại quyền truy cập và thử lại.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: {
        popup: 'rounded-4'
      }
    })
  } finally {
    loading.value = false
  }
}

// Tự chọn sự kiện đầu tiên khi Dashboard tải xong danh sách sự kiện.
watch(
  () => props.events,
  (eventList) => {
    if (eventList.length === 0) {
      selectedEventId.value = ''
      report.value = null
      return
    }

    const selectedEventStillExists = eventList.some(
      (event) => Number(event.id) === Number(selectedEventId.value)
    )

    if (!selectedEventStillExists) {
      selectedEventId.value = eventList[0].id
    }

    loadReport()
  },
  {
    immediate: true
  }
)

const formatNumber = (value) =>
  new Intl.NumberFormat('vi-VN').format(Number(value || 0))

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
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

const getStatusText = (eventStatus) => {
  const labels = {
    PUBLISHED: 'Đang công khai',
    PENDING: 'Chờ duyệt',
    CANCELLED: 'Đã hủy / từ chối'
  }

  return labels[eventStatus] || eventStatus
}

const getStatusClass = (eventStatus) => {
  const classes = {
    PUBLISHED: 'status-published',
    PENDING: 'status-pending',
    CANCELLED: 'status-cancelled'
  }

  return classes[eventStatus] || 'status-pending'
}
</script>

<style scoped src="./OrganizerRevenueReport.css"></style>
