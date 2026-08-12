<template>
  <div class="admin-revenue-page min-vh-100 py-5">
    <div class="container">
      <div class="row g-4 align-items-start">
        <main class="col-lg-9 order-2 order-lg-1 admin-main-column">
          <div class="report-header mb-4">
            <div>
              <span class="admin-label">QUẢN TRỊ VIÊN</span>
              <h2 class="fw-bold text-slate-900 mb-1 mt-1">Báo cáo doanh thu toàn hệ thống</h2>
              <p class="text-muted mb-0">
                Theo dõi doanh thu từ các đơn hàng đã thanh toán thành công.
              </p>
            </div>
          </div>

          <form class="filter-card mb-4" @submit.prevent="fetchReport">
            <div class="d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-funnel text-primary"></i>
              <h5 class="fw-bold mb-0">Bộ lọc báo cáo</h5>
            </div>

            <div class="row g-3">
              <div class="col-md-6 col-xxl-3">
                <label for="event-filter" class="form-label">Sự kiện</label>
                <select
                  id="event-filter"
                  v-model="filterForm.event_id"
                  class="form-select"
                  :disabled="filterLoading || loading"
                  @change="fetchReport"
                >
                  <option value="">Tất cả sự kiện</option>
                  <option v-for="event in filterOptions.events" :key="event.id" :value="event.id">
                    {{ event.title }}
                  </option>
                </select>
              </div>

              <div class="col-md-6 col-xxl-3">
                <label for="organizer-filter" class="form-label"> Ban tổ chức </label>
                <select
                  id="organizer-filter"
                  v-model="filterForm.organizer_id"
                  class="form-select"
                  :disabled="filterLoading || loading"
                  @change="fetchReport"
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

              <div class="col-md-6 col-xxl-2">
                <label for="category-filter" class="form-label">Thể loại</label>
                <select
                  id="category-filter"
                  v-model="filterForm.category"
                  class="form-select"
                  :disabled="filterLoading || loading"
                  @change="fetchReport"
                >
                  <option value="">Tất cả thể loại</option>
                  <option
                    v-for="category in filterOptions.categories"
                    :key="category.value"
                    :value="category.value"
                  >
                    {{ category.label }}
                  </option>
                </select>
              </div>

              <div class="col-md-6 col-xxl-2">
                <label for="date-from-filter" class="form-label">Từ ngày</label>
                <input
                  id="date-from-filter"
                  v-model="filterForm.date_from"
                  type="date"
                  class="form-control"
                  :disabled="loading"
                  @change="fetchReport"
                />
              </div>

              <div class="col-md-6 col-xxl-2">
                <label for="date-to-filter" class="form-label">Đến ngày</label>
                <input
                  id="date-to-filter"
                  v-model="filterForm.date_to"
                  type="date"
                  class="form-control"
                  :disabled="loading"
                  @change="fetchReport"
                />
              </div>
            </div>

            <div class="d-flex flex-wrap justify-content-end gap-2 mt-3">
              <button
                type="button"
                class="btn btn-light border rounded-pill px-4"
                :disabled="loading"
                @click="resetFilters"
              >
                <i class="bi bi-x-circle me-2"></i>
                Xóa lọc
              </button>

              <button type="submit" class="btn btn-primary rounded-pill px-4" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check2-circle me-2"></i>
                Áp dụng
              </button>
            </div>
          </form>

          <div v-if="loading" class="content-card loading-state">
            <div class="spinner-border text-primary"></div>
            <p class="text-muted mt-3 mb-0">Đang tổng hợp dữ liệu doanh thu...</p>
          </div>

          <template v-else>
            <div class="summary-grid mb-4">
              <div class="summary-card revenue-summary-card">
                <div class="summary-icon icon-green">
                  <i class="bi bi-cash-stack"></i>
                </div>
                <div>
                  <span>Tổng doanh thu</span>
                  <strong>{{ formatCurrency(report.overview.total_revenue) }}</strong>
                </div>
              </div>

              <div class="summary-card">
                <div class="summary-icon icon-blue">
                  <i class="bi bi-receipt"></i>
                </div>
                <div>
                  <span>Đơn đã thanh toán</span>
                  <strong>{{ formatNumber(report.overview.total_paid_orders) }}</strong>
                </div>
              </div>

              <div class="summary-card">
                <div class="summary-icon icon-purple">
                  <i class="bi bi-ticket-perforated"></i>
                </div>
                <div>
                  <span>Vé đã bán</span>
                  <strong>{{ formatNumber(report.overview.total_tickets_sold) }}</strong>
                </div>
              </div>

              <div class="summary-card">
                <div class="summary-icon icon-orange">
                  <i class="bi bi-calendar-event"></i>
                </div>
                <div>
                  <span>Sự kiện có doanh thu</span>
                  <strong>{{ formatNumber(report.overview.total_events) }}</strong>
                </div>
              </div>

              <div class="summary-card">
                <div class="summary-icon icon-cyan">
                  <i class="bi bi-qr-code-scan"></i>
                </div>
                <div>
                  <span>Vé đã check-in</span>
                  <strong>{{ formatNumber(report.overview.total_checked_in) }}</strong>
                </div>
              </div>
            </div>

            <div v-if="!hasReportData" class="content-card empty-state">
              <i class="bi bi-bar-chart"></i>
              <h5 class="fw-bold text-slate-900 mt-3">Không có dữ liệu doanh thu</h5>
              <p class="text-muted mb-0">Chưa có đơn hàng PAID phù hợp với bộ lọc hiện tại.</p>
            </div>

            <div v-else class="row g-4">
              <div class="col-xxl-7">
                <div class="chart-card">
                  <div class="chart-heading">
                    <div>
                      <h5 class="fw-bold mb-1">Doanh thu theo tháng</h5>
                      <small class="text-muted"> Xu hướng doanh thu của các đơn PAID </small>
                    </div>
                    <i class="bi bi-graph-up-arrow chart-heading-icon"></i>
                  </div>

                  <div class="chart-wrapper">
                    <Line :data="monthlyChartData" :options="lineChartOptions" />
                  </div>
                </div>
              </div>

              <div class="col-xxl-5">
                <div class="chart-card">
                  <div class="chart-heading">
                    <div>
                      <h5 class="fw-bold mb-1">Doanh thu theo thể loại</h5>
                      <small class="text-muted"> Tỷ trọng doanh thu giữa các nhóm sự kiện </small>
                    </div>
                    <i class="bi bi-pie-chart chart-heading-icon"></i>
                  </div>

                  <div class="chart-wrapper doughnut-wrapper">
                    <Doughnut
                      v-if="hasCategoryChartData"
                      :data="categoryChartData"
                      :options="doughnutChartOptions"
                    />
                    <div v-else class="chart-empty-state">Không có dữ liệu thể loại</div>
                  </div>
                </div>
              </div>

              <div class="col-xxl-6">
                <div class="chart-card">
                  <div class="chart-heading">
                    <div>
                      <h5 class="fw-bold mb-1">Top 10 ban tổ chức</h5>
                      <small class="text-muted"> Xếp hạng theo tổng doanh thu </small>
                    </div>
                    <i class="bi bi-building chart-heading-icon"></i>
                  </div>

                  <div class="chart-wrapper organizer-chart-wrapper">
                    <Bar :data="organizerChartData" :options="horizontalBarOptions" />
                  </div>
                </div>
              </div>

              <div class="col-xxl-6">
                <div class="chart-card">
                  <div class="chart-heading">
                    <div>
                      <h5 class="fw-bold mb-1">Top 10 sự kiện</h5>
                      <small class="text-muted"> Các sự kiện tạo ra doanh thu cao nhất </small>
                    </div>
                    <i class="bi bi-trophy chart-heading-icon"></i>
                  </div>

                  <div class="chart-wrapper">
                    <Bar :data="eventChartData" :options="barChartOptions" />
                  </div>
                </div>
              </div>
            </div>
          </template>
        </main>

        <aside class="col-lg-3 order-1 order-lg-2">
          <AdminSidebar />
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import Swal from 'sweetalert2'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import apiClient from '@/services/api'

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
)

const loading = ref(true)
const filterLoading = ref(true)

const filterForm = reactive({
  event_id: '',
  organizer_id: '',
  category: '',
  date_from: '',
  date_to: '',
})

const filterOptions = reactive({
  events: [],
  organizers: [],
  categories: [],
})

const createEmptyReport = () => ({
  overview: {
    total_revenue: '0.00',
    total_paid_orders: 0,
    total_tickets_sold: 0,
    total_events: 0,
    total_checked_in: 0,
  },
  revenue_by_month: [],
  revenue_by_category: [],
  revenue_by_organizer: [],
  revenue_by_event: [],
})

const report = ref(createEmptyReport())

const categoryLabels = {
  MUSIC: 'Âm nhạc',
  WORKSHOP: 'Workshop',
  ENTERTAINMENT: 'Giải trí',
  SPORTS: 'Thể thao',
}

const chartColors = [
  '#2563EB',
  '#10B981',
  '#F59E0B',
  '#8B5CF6',
  '#06B6D4',
  '#EF4444',
  '#EC4899',
  '#14B8A6',
  '#6366F1',
  '#84CC16',
]

const formatNumber = (value) => new Intl.NumberFormat('vi-VN').format(Number(value || 0))

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))

const formatMonth = (value) => {
  if (!value) return 'Chưa xác định'

  const monthParts = String(value).match(/^(\d{4})-(\d{2})$/)
  if (monthParts) return `${monthParts[2]}/${monthParts[1]}`

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString('vi-VN', {
    month: '2-digit',
    year: 'numeric',
  })
}

const getErrorMessage = (error, fallback) =>
  error.response?.data?.error || error.response?.data?.detail || fallback

const hasReportData = computed(() => Number(report.value.overview?.total_paid_orders || 0) > 0)

const hasCategoryChartData = computed(() =>
  (report.value.revenue_by_category || []).some((item) => Number(item.total_revenue || 0) > 0),
)

const monthlyChartData = computed(() => ({
  labels: (report.value.revenue_by_month || []).map((item) => formatMonth(item.month)),
  datasets: [
    {
      label: 'Doanh thu',
      data: (report.value.revenue_by_month || []).map((item) => Number(item.total_revenue || 0)),
      borderColor: '#2563EB',
      backgroundColor: 'rgba(37, 99, 235, 0.14)',
      pointBackgroundColor: '#2563EB',
      pointRadius: 4,
      borderWidth: 3,
      tension: 0.3,
    },
  ],
}))

const categoryChartData = computed(() => ({
  labels: (report.value.revenue_by_category || []).map(
    (item) => item.category_name || categoryLabels[item.category] || item.category,
  ),
  datasets: [
    {
      data: (report.value.revenue_by_category || []).map((item) => Number(item.total_revenue || 0)),
      backgroundColor: chartColors,
      borderColor: '#FFFFFF',
      borderWidth: 3,
    },
  ],
}))

const organizerChartData = computed(() => ({
  labels: (report.value.revenue_by_organizer || []).map((item) => item.company_name),
  datasets: [
    {
      label: 'Doanh thu',
      data: (report.value.revenue_by_organizer || []).map((item) =>
        Number(item.total_revenue || 0),
      ),
      backgroundColor: '#10B981',
      borderRadius: 7,
    },
  ],
}))

const eventChartData = computed(() => ({
  labels: (report.value.revenue_by_event || []).map((item) => item.title),
  datasets: [
    {
      label: 'Doanh thu',
      data: (report.value.revenue_by_event || []).map((item) => Number(item.total_revenue || 0)),
      backgroundColor: '#8B5CF6',
      borderRadius: 7,
    },
  ],
}))

const currencyTooltip = {
  callbacks: {
    label: (context) => `${context.dataset.label || context.label}: ${formatCurrency(context.raw)}`,
  },
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: currencyTooltip,
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value) => formatCurrency(value),
      },
    },
    x: {
      grid: { display: false },
    },
  },
}

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '62%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 18,
      },
    },
    tooltip: currencyTooltip,
  },
}

const horizontalBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
    tooltip: currencyTooltip,
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        callback: (value) => formatCurrency(value),
      },
    },
    y: {
      grid: { display: false },
    },
  },
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: currencyTooltip,
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value) => formatCurrency(value),
      },
    },
    x: {
      grid: { display: false },
    },
  },
}

const buildFilterParams = () => {
  const params = {}

  // Chỉ gửi những bộ lọc Admin đã chọn lên backend.
  Object.entries(filterForm).forEach(([key, value]) => {
    if (value !== '') {
      params[key] = value
    }
  })

  return params
}

const validateDateRange = async () => {
  if (filterForm.date_from && filterForm.date_to && filterForm.date_from > filterForm.date_to) {
    await Swal.fire({
      title: 'Khoảng ngày không hợp lệ',
      text: 'Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: { popup: 'rounded-4' },
    })

    return false
  }

  return true
}

const fetchReport = async () => {
  if (!(await validateDateRange())) return

  loading.value = true

  try {
    const response = await apiClient.get('orders/admin/revenue-report/', {
      params: buildFilterParams(),
    })

    report.value = response.data
  } catch (error) {
    // Không giữ số liệu cũ khi bộ lọc mới tải thất bại.
    report.value = createEmptyReport()

    await Swal.fire({
      title: 'Không thể tải báo cáo',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' },
    })
  } finally {
    loading.value = false
  }
}

const fetchFilterOptions = async () => {
  filterLoading.value = true

  try {
    const response = await apiClient.get('orders/admin/revenue-report/filters/')

    filterOptions.events = response.data.events || []
    filterOptions.organizers = response.data.organizers || []
    filterOptions.categories = response.data.categories || []
  } catch (error) {
    await Swal.fire({
      title: 'Không thể tải bộ lọc',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' },
    })
  } finally {
    filterLoading.value = false
  }
}

const resetFilters = () => {
  Object.keys(filterForm).forEach((key) => {
    filterForm[key] = ''
  })

  fetchReport()
}

onMounted(async () => {
  await Promise.all([fetchFilterOptions(), fetchReport()])
})
</script>

<style scoped src="./AdminRevenueReportView.css"></style>
