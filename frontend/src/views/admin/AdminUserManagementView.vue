<template>
  <div class="admin-users-page min-vh-100 py-5">
    <div class="container-fluid px-3 px-xl-4 px-xxl-5">
      <div class="row g-4 align-items-start">
        <main class="col-xl-10 order-2 order-xl-1 admin-main-column">
          <div class="page-heading mb-4">
            <div>
              <span class="admin-label">QUẢN TRỊ VIÊN</span>
              <h2 class="fw-bold text-slate-900 mb-1 mt-1">Quản lý người dùng</h2>
              <p class="text-muted mb-0">
                Theo dõi tài khoản và khóa hoặc mở khóa quyền truy cập hệ thống.
              </p>
            </div>

            <button
              type="button"
              class="btn btn-outline-primary rounded-pill px-4"
              :disabled="loading"
              @click="refreshPage"
            >
              <i class="bi bi-arrow-clockwise me-2"></i>Làm mới
            </button>
          </div>

          <div class="user-summary-grid mb-4">
            <div class="user-summary-card">
              <span class="summary-icon icon-blue"><i class="bi bi-people"></i></span>
              <div>
                <small>Tổng tài khoản</small>
                <strong>{{ formatNumber(getSummaryValue('total_users', 'total')) }}</strong>
              </div>
            </div>

            <div class="user-summary-card">
              <span class="summary-icon icon-cyan"><i class="bi bi-person"></i></span>
              <div>
                <small>Khách hàng</small>
                <strong>{{ formatNumber(getSummaryValue('total_customers', 'customers')) }}</strong>
              </div>
            </div>

            <div class="user-summary-card">
              <span class="summary-icon icon-purple"><i class="bi bi-building"></i></span>
              <div>
                <small>Ban tổ chức</small>
                <strong>{{
                  formatNumber(getSummaryValue('total_organizers', 'organizers'))
                }}</strong>
              </div>
            </div>

            <div class="user-summary-card">
              <span class="summary-icon icon-red"><i class="bi bi-person-lock"></i></span>
              <div>
                <small>Đang bị khóa</small>
                <strong>{{ formatNumber(getSummaryValue('total_locked')) }}</strong>
              </div>
            </div>
          </div>

          <form class="filter-card mb-4" @submit.prevent="applySearch">
            <div class="row g-3 align-items-end">
              <div class="col-xl-6">
                <label for="user-search" class="form-label fw-semibold">Tìm kiếm</label>
                <div class="input-group">
                  <span class="input-group-text bg-white border-end-0">
                    <i class="bi bi-search text-muted"></i>
                  </span>
                  <input
                    id="user-search"
                    v-model.trim="searchInput"
                    type="text"
                    class="form-control border-start-0"
                    placeholder="Tên, username, email hoặc số điện thoại..."
                  />
                  <button type="submit" class="btn btn-primary px-4">Tìm</button>
                </div>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="role-filter" class="form-label fw-semibold">Vai trò</label>
                <select
                  id="role-filter"
                  v-model="roleFilter"
                  class="form-select"
                  @change="changeFilter"
                >
                  <option value="ALL">Tất cả vai trò</option>
                  <option value="CUSTOMER">Khách hàng</option>
                  <option value="ORGANIZER">Ban tổ chức</option>
                  <option value="ADMIN">Quản trị viên</option>
                </select>
              </div>

              <div class="col-sm-6 col-xl-3">
                <label for="status-filter" class="form-label fw-semibold">Trạng thái</label>
                <select
                  id="status-filter"
                  v-model="statusFilter"
                  class="form-select"
                  @change="changeFilter"
                >
                  <option value="ALL">Tất cả trạng thái</option>
                  <option value="ACTIVE">Đang hoạt động</option>
                  <option value="LOCKED">Đã khóa</option>
                </select>
              </div>
            </div>
          </form>

          <div class="content-card">
            <div v-if="loading" class="loading-state">
              <div class="spinner-border text-primary"></div>
              <p class="text-muted mt-3 mb-0">Đang tải danh sách người dùng...</p>
            </div>

            <div v-else-if="users.length === 0" class="empty-state">
              <i class="bi bi-person-search"></i>
              <h5 class="fw-bold text-slate-900 mt-3">Không tìm thấy tài khoản</h5>
              <p class="text-muted mb-0">Hãy thử thay đổi từ khóa hoặc bộ lọc.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0 user-table">
                <thead>
                  <tr>
                    <th>Người dùng</th>
                    <th>Liên hệ</th>
                    <th>Vai trò</th>
                    <th>Ngày tham gia</th>
                    <th>Trạng thái</th>
                    <th class="text-end">Thao tác</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>
                      <div class="user-cell">
                        <img
                          :src="user.avatar || fallbackAvatar"
                          :alt="user.name"
                          class="user-avatar"
                          @error="useFallbackAvatar"
                        />
                        <div>
                          <strong>{{ user.name || 'Chưa cập nhật tên' }}</strong>
                          <small>@{{ user.username }}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="contact-cell">
                        <span>{{ user.email }}</span>
                        <small>{{ user.phone_number || 'Chưa có số điện thoại' }}</small>
                      </div>
                    </td>
                    <td>
                      <span class="role-badge" :class="getRoleClass(user.role)">
                        {{ getRoleText(user.role) }}
                      </span>
                    </td>
                    <td>{{ formatDate(user.date_joined) }}</td>
                    <td>
                      <span
                        class="status-badge"
                        :class="isUserActive(user) ? 'status-active' : 'status-locked'"
                      >
                        {{ isUserActive(user) ? 'Hoạt động' : 'Đã khóa' }}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button
                          type="button"
                          class="btn btn-sm btn-outline-secondary rounded-pill"
                          @click="openUserDetail(user.id)"
                        >
                          Chi tiết
                        </button>

                        <button
                          v-if="canChangeStatus(user)"
                          type="button"
                          class="btn btn-sm rounded-pill"
                          :class="isUserActive(user) ? 'btn-outline-danger' : 'btn-outline-success'"
                          :disabled="actionLoadingId === user.id"
                          @click="confirmStatusChange(user)"
                        >
                          <span
                            v-if="actionLoadingId === user.id"
                            class="spinner-border spinner-border-sm me-1"
                          ></span>
                          {{ isUserActive(user) ? 'Khóa' : 'Mở khóa' }}
                        </button>
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

          <div ref="detailModalRef" class="modal fade" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
              <div class="modal-content border-0 rounded-4">
                <div class="modal-header px-4 py-3">
                  <h5 class="modal-title fw-bold">Chi tiết người dùng</h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Đóng"
                  ></button>
                </div>

                <div v-if="detailLoading" class="modal-body loading-state">
                  <div class="spinner-border text-primary"></div>
                </div>

                <div v-else-if="selectedUser" class="modal-body p-4">
                  <div class="detail-heading">
                    <img
                      :src="selectedUser.avatar || fallbackAvatar"
                      :alt="selectedUser.name"
                      class="detail-avatar"
                      @error="useFallbackAvatar"
                    />
                    <div>
                      <div class="d-flex flex-wrap align-items-center gap-2 mb-1">
                        <h4 class="fw-bold mb-0">{{ selectedUser.name }}</h4>
                        <span class="role-badge" :class="getRoleClass(selectedUser.role)">
                          {{ getRoleText(selectedUser.role) }}
                        </span>
                      </div>
                      <div class="text-muted">@{{ selectedUser.username }}</div>
                      <span
                        class="status-badge mt-2"
                        :class="isUserActive(selectedUser) ? 'status-active' : 'status-locked'"
                      >
                        {{ isUserActive(selectedUser) ? 'Đang hoạt động' : 'Tài khoản đã khóa' }}
                      </span>
                    </div>
                  </div>

                  <div class="detail-section mt-4">
                    <h6>Thông tin tài khoản</h6>
                    <div class="row g-3">
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Email</small>
                          <strong>{{ selectedUser.email }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Số điện thoại</small>
                          <strong>{{ selectedUser.phone_number || 'Chưa cập nhật' }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Ngày sinh</small>
                          <strong>{{ formatDay(selectedUser.dob) }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Ngày tham gia</small>
                          <strong>{{ formatDateTime(selectedUser.date_joined) }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Đăng nhập gần nhất</small>
                          <strong>{{ formatDateTime(selectedUser.last_login) }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="selectedUser.role === 'CUSTOMER'" class="detail-section mt-4">
                    <h6>Hoạt động khách hàng</h6>
                    <div class="detail-stat-grid">
                      <div class="detail-stat">
                        <small>Hạng thành viên</small>
                        <strong>{{
                          selectedUser.customer_profile?.tier || 'Chưa có hồ sơ'
                        }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Tổng đơn</small>
                        <strong>{{ formatNumber(customerStats.total_orders) }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Đơn đã thanh toán</small>
                        <strong>{{ formatNumber(customerStats.paid_orders) }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Vé đang sở hữu</small>
                        <strong>{{ formatNumber(customerStats.total_tickets) }}</strong>
                      </div>
                      <div class="detail-stat detail-stat-wide">
                        <small>Tổng tiền đã thanh toán</small>
                        <strong class="text-success">
                          {{ formatCurrency(customerStats.total_paid_amount) }}
                        </strong>
                      </div>
                    </div>
                  </div>

                  <div v-if="selectedUser.role === 'ORGANIZER'" class="detail-section mt-4">
                    <h6>Thông tin Ban tổ chức</h6>
                    <div class="row g-3 mb-3">
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Tên công ty</small>
                          <strong>
                            {{ selectedUser.organizer_profile?.company_name || 'Chưa có hồ sơ' }}
                          </strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-item">
                          <small>Tài khoản ngân hàng</small>
                          <strong>
                            {{ selectedUser.organizer_profile?.bank_account || 'Chưa có hồ sơ' }}
                          </strong>
                        </div>
                      </div>
                    </div>

                    <div class="detail-stat-grid">
                      <div class="detail-stat">
                        <small>Tổng sự kiện</small>
                        <strong>{{ formatNumber(organizerStats.total_events) }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Chờ duyệt</small>
                        <strong>{{ formatNumber(organizerStats.pending_events) }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Đã công khai</small>
                        <strong>{{ formatNumber(organizerStats.published_events) }}</strong>
                      </div>
                      <div class="detail-stat">
                        <small>Đã hủy / từ chối</small>
                        <strong>{{ formatNumber(organizerStats.cancelled_events) }}</strong>
                      </div>
                      <div class="detail-stat detail-stat-wide">
                        <small>Tổng doanh thu</small>
                        <strong class="text-success">
                          {{ formatCurrency(organizerStats.total_revenue) }}
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="selectedUser" class="modal-footer border-0 px-4 pb-4">
                  <button
                    type="button"
                    class="btn btn-light rounded-pill px-4"
                    data-bs-dismiss="modal"
                  >
                    Đóng
                  </button>
                  <button
                    v-if="canChangeStatus(selectedUser)"
                    type="button"
                    class="btn rounded-pill px-4"
                    :class="isUserActive(selectedUser) ? 'btn-danger' : 'btn-success'"
                    :disabled="actionLoadingId === selectedUser.id"
                    @click="confirmStatusChange(selectedUser)"
                  >
                    {{ isUserActive(selectedUser) ? 'Khóa tài khoản' : 'Mở khóa tài khoản' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>

        <aside class="col-xl-2 order-1 order-xl-2">
          <AdminSidebar />
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Modal } from 'bootstrap'
import Swal from 'sweetalert2'

import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import PaginationControls from '@/components/PaginationControls.vue'
import apiClient from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const users = ref([])
const summary = ref({})
const loading = ref(true)
const detailLoading = ref(false)
const actionLoadingId = ref(null)
const selectedUser = ref(null)
const detailModalRef = ref(null)

const searchInput = ref('')
const searchKeyword = ref('')
const roleFilter = ref('ALL')
const statusFilter = ref('ALL')
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 10
const fallbackAvatar = '/ticket_icon_150905.png'

let detailModal = null

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))

const customerStats = computed(() => selectedUser.value?.statistics || {})

const organizerStats = computed(() => selectedUser.value?.statistics || {})

const fetchUsers = async () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize,
  }

  if (searchKeyword.value) params.search = searchKeyword.value
  if (roleFilter.value !== 'ALL') params.role = roleFilter.value
  if (statusFilter.value !== 'ALL') params.account_status = statusFilter.value

  const response = await apiClient.get('auth/admin/users/', { params })
  users.value = response.data.results || []
  totalCount.value = Number(response.data.count || 0)
}

const fetchSummary = async () => {
  const response = await apiClient.get('auth/admin/users/summary/')
  summary.value = response.data || {}
}

const refreshPage = async () => {
  loading.value = true

  try {
    // Danh sách và số liệu tổng quan không phụ thuộc nhau nên tải cùng lúc.
    await Promise.all([fetchUsers(), fetchSummary()])
  } catch (error) {
    users.value = []
    totalCount.value = 0

    await Swal.fire({
      title: 'Không thể tải người dùng',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' },
    })
  } finally {
    loading.value = false
  }
}

const applySearch = () => {
  searchKeyword.value = searchInput.value
  currentPage.value = 1
  refreshPage()
}

const changeFilter = () => {
  currentPage.value = 1
  refreshPage()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  refreshPage()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const openUserDetail = async (userId) => {
  selectedUser.value = null
  detailLoading.value = true
  detailModal?.show()

  try {
    const response = await apiClient.get(`auth/admin/users/${userId}/`)
    selectedUser.value = response.data
  } catch (error) {
    detailModal?.hide()

    await Swal.fire({
      title: 'Không thể tải chi tiết',
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' },
    })
  } finally {
    detailLoading.value = false
  }
}

const confirmStatusChange = async (user) => {
  const active = isUserActive(user)
  const actionText = active ? 'khóa' : 'mở khóa'
  const result = await Swal.fire({
    title: active ? 'Khóa tài khoản?' : 'Mở khóa tài khoản?',
    text: active
      ? `Tài khoản "${user.name}" sẽ không thể đăng nhập.`
      : `Tài khoản "${user.name}" sẽ có thể đăng nhập trở lại.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: active ? 'Khóa tài khoản' : 'Mở khóa',
    cancelButtonText: 'Quay lại',
    confirmButtonColor: active ? '#DC2626' : '#059669',
    customClass: { popup: 'rounded-4' },
  })

  if (!result.isConfirmed) return

  actionLoadingId.value = user.id

  try {
    const action = active ? 'lock' : 'unlock'
    const response = await apiClient.post(`auth/admin/users/${user.id}/${action}/`)

    // Khi đang lọc trạng thái, tài khoản vừa đổi sẽ rời khỏi danh sách hiện tại.
    if (statusFilter.value !== 'ALL') currentPage.value = 1
    await Promise.all([fetchUsers(), fetchSummary()])

    if (selectedUser.value?.id === user.id) {
      const detailResponse = await apiClient.get(`auth/admin/users/${user.id}/`)
      selectedUser.value = detailResponse.data
    }

    await Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: response.data.message || `Đã ${actionText} tài khoản.`,
      showConfirmButton: false,
      timer: 2200,
      timerProgressBar: true,
    })
  } catch (error) {
    await Swal.fire({
      title: `Không thể ${actionText} tài khoản`,
      text: getErrorMessage(error, 'Vui lòng thử lại sau.'),
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' },
    })
  } finally {
    actionLoadingId.value = null
  }
}

const getSummaryValue = (...keys) => {
  for (const key of keys) {
    if (summary.value[key] !== undefined) return summary.value[key]
  }
  return 0
}

const isUserActive = (user) =>
  user?.account_status
    ? user.account_status === 'ACTIVE'
    : user?.is_active !== false && user?.status !== false

const canChangeStatus = (user) =>
  user?.can_change_status !== undefined
    ? user.can_change_status
    : !user?.is_superuser && Number(user?.id) !== Number(authStore.user?.id)

const getRoleText = (role) =>
  ({
    CUSTOMER: 'Khách hàng',
    ORGANIZER: 'Ban tổ chức',
    ADMIN: 'Quản trị viên',
  })[role] || role

const getRoleClass = (role) =>
  ({
    CUSTOMER: 'role-customer',
    ORGANIZER: 'role-organizer',
    ADMIN: 'role-admin',
  })[role] || 'role-customer'

const getErrorMessage = (error, fallback) =>
  error.response?.data?.error || error.response?.data?.detail || fallback

const formatNumber = (value) => new Intl.NumberFormat('vi-VN').format(Number(value || 0))

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))

const formatDay = (value) => {
  if (!value) return 'Chưa cập nhật'
  return new Date(value).toLocaleDateString('vi-VN')
}

const formatDate = (value) => {
  if (!value) return 'Chưa xác định'
  return new Date(value).toLocaleDateString('vi-VN')
}

const formatDateTime = (value) => {
  if (!value) return 'Chưa có dữ liệu'

  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const useFallbackAvatar = (event) => {
  if (event.target.src.endsWith(fallbackAvatar)) return
  event.target.src = fallbackAvatar
}

onMounted(async () => {
  if (detailModalRef.value) detailModal = new Modal(detailModalRef.value)
  await refreshPage()
})

onUnmounted(() => {
  detailModal?.dispose()
})
</script>

<style scoped src="./AdminUserManagementView.css"></style>
