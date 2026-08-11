<template>
  <div class="organizer-page min-vh-100 py-4">
    <div class="container">
      <section class="welcome-card mb-4">
        <div>
          <span class="welcome-label">TRUNG TÂM BAN TỔ CHỨC</span>

          <h2 class="fw-bold text-white mt-2 mb-2">
            Xin chào, {{ authStore.user?.name || 'Ban tổ chức' }}
          </h2>

          <p class="text-white-50 mb-0">
            Tạo sự kiện, theo dõi trạng thái và thực hiện soát vé tại đây.
          </p>
        </div>

        <router-link
          to="/organizer/events/create"
          class="btn create-event-btn rounded-pill px-4 py-2"
        >
          <i class="bi bi-plus-lg me-2"></i>
          Tạo sự kiện mới
        </router-link>
      </section>

      <div class="row g-4">
        <div class="col-lg-3">
          <aside class="sidebar-card">
            <div class="organizer-info">
              <div class="organizer-avatar">
                <i class="bi bi-building"></i>
              </div>

              <div>
                <div class="fw-bold text-slate-900">
                  {{ authStore.user?.name || 'Ban tổ chức' }}
                </div>
                <small class="text-muted">Tài khoản Organizer</small>
              </div>
            </div>

            <router-link
              to="/organizer/events/create"
              class="btn btn-primary w-100 rounded-pill py-2 mb-4"
            >
              <i class="bi bi-calendar-plus me-2"></i>
              Tạo sự kiện
            </router-link>

            <div class="sidebar-title">QUẢN LÝ</div>

            <button
              type="button"
              class="sidebar-link"
              :class="{ active: activeTab === 'overview' }"
              @click="activeTab = 'overview'"
            >
              <i class="bi bi-grid-1x2"></i>
              Tổng quan
            </button>

            <button
              type="button"
              class="sidebar-link"
              :class="{ active: activeTab === 'events' }"
              @click="activeTab = 'events'"
            >
              <i class="bi bi-calendar-event"></i>
              Sự kiện của tôi
              <span class="sidebar-count">{{ events.length }}</span>
            </button>

            <button
              type="button"
              class="sidebar-link"
              :class="{ active: activeTab === 'checkin' }"
              @click="activeTab = 'checkin'"
            >
              <i class="bi bi-qr-code-scan"></i>
              Soát vé
            </button>

            <button
              type="button"
              class="sidebar-link"
              :class="{ active: activeTab === 'revenue' }"
              @click="activeTab = 'revenue'"
            >
              <i class="bi bi-bar-chart-line"></i>
              Báo cáo doanh thu
            </button>
          </aside>
        </div>

        <div class="col-lg-9">
          <div v-if="loading" class="content-card text-center py-5">
            <div class="spinner-border text-primary"></div>
            <p class="text-muted mt-3 mb-0">
              Đang tải dữ liệu sự kiện...
            </p>
          </div>

          <template v-else>
            <div v-if="activeTab === 'overview'">
              <div class="section-heading mb-3">
                <div>
                  <h4 class="fw-bold text-slate-900 mb-1">Tổng quan</h4>
                  <p class="text-muted mb-0">
                    Số liệu được lấy từ các sự kiện của bạn.
                  </p>
                </div>

                <button
                  type="button"
                  class="btn btn-light border rounded-pill px-3"
                  @click="fetchEvents"
                >
                  <i class="bi bi-arrow-clockwise me-1"></i>
                  Làm mới
                </button>
              </div>

              <div class="row g-3 mb-4">
                <div class="col-md-6 col-xl-3">
                  <div class="stat-card">
                    <div class="stat-icon icon-blue">
                      <i class="bi bi-calendar-event"></i>
                    </div>

                    <div>
                      <small class="text-muted">Tổng sự kiện</small>
                      <h3 class="fw-bold mb-0">{{ events.length }}</h3>
                    </div>
                  </div>
                </div>

                <div class="col-md-6 col-xl-3">
                  <div class="stat-card">
                    <div class="stat-icon icon-green">
                      <i class="bi bi-broadcast"></i>
                    </div>

                    <div>
                      <small class="text-muted">Đang công khai</small>
                      <h3 class="fw-bold mb-0">{{ publishedCount }}</h3>
                    </div>
                  </div>
                </div>

                <div class="col-md-6 col-xl-3">
                  <div class="stat-card">
                    <div class="stat-icon icon-orange">
                      <i class="bi bi-hourglass-split"></i>
                    </div>

                    <div>
                      <small class="text-muted">Chờ duyệt</small>
                      <h3 class="fw-bold mb-0">{{ pendingCount }}</h3>
                    </div>
                  </div>
                </div>

                <div class="col-md-6 col-xl-3">
                  <div class="stat-card">
                    <div class="stat-icon icon-purple">
                      <i class="bi bi-ticket-perforated"></i>
                    </div>

                    <div>
                      <small class="text-muted">Tổng sức chứa</small>
                      <h3 class="fw-bold mb-0">
                        {{ formatNumber(totalCapacity) }}
                      </h3>
                    </div>
                  </div>
                </div>
              </div>

              <div class="content-card">
                <div class="section-heading mb-3">
                  <div>
                    <h5 class="fw-bold text-slate-900 mb-1">
                      Sự kiện mới tạo
                    </h5>
                    <small class="text-muted">
                      Các sự kiện gần đây của bạn
                    </small>
                  </div>

                  <button
                    v-if="events.length > 4"
                    type="button"
                    class="btn btn-sm btn-outline-primary rounded-pill px-3"
                    @click="activeTab = 'events'"
                  >
                    Xem tất cả
                  </button>
                </div>

                <EventList
                  :events="recentEvents"
                  @create-event="goToCreateEvent"
                />
              </div>
            </div>

            <div v-if="activeTab === 'events'">
              <div class="section-heading mb-3">
                <div>
                  <h4 class="fw-bold text-slate-900 mb-1">
                    Sự kiện của tôi
                  </h4>
                  <p class="text-muted mb-0">
                    Chỉ hiển thị các sự kiện thuộc tài khoản Ban tổ chức này.
                  </p>
                </div>

                <router-link
                  to="/organizer/events/create"
                  class="btn btn-primary rounded-pill px-4"
                >
                  <i class="bi bi-plus-lg me-1"></i>
                  Tạo sự kiện
                </router-link>
              </div>

              <div class="content-card">
                <EventList
                  :events="events"
                  @create-event="goToCreateEvent"
                />
              </div>
            </div>

            <OrganizerRevenueReport
              v-if="activeTab === 'revenue'"
              :events="events"
            />

            <div v-if="activeTab === 'checkin'" class="content-card">
              <div class="checkin-box">
                <div class="checkin-icon">
                  <i class="bi bi-qr-code-scan"></i>
                </div>

                <h4 class="fw-bold text-slate-900 mt-3">
                  Cổng soát vé
                </h4>

                <p class="text-muted">
                  Nhập mã vé hoặc dùng thiết bị quét QR rồi nhấn Enter.
                </p>

                <div class="mx-auto mt-4" style="max-width: 480px">
                  <input
                    v-model.trim="qrCodeInput"
                    type="text"
                    class="form-control form-control-lg rounded-pill text-center mb-3"
                    placeholder="Nhập mã QR của vé..."
                    :disabled="checkingIn"
                    @keyup.enter="handleCheckIn"
                  />

                  <button
                    type="button"
                    class="btn btn-cta rounded-pill w-100 py-3"
                    :disabled="checkingIn"
                    @click="handleCheckIn"
                  >
                    <span
                      v-if="checkingIn"
                      class="spinner-border spinner-border-sm me-2"
                    ></span>

                    <i v-else class="bi bi-check-circle me-2"></i>

                    {{ checkingIn ? 'Đang kiểm tra...' : 'Soát vé ngay' }}
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'

import OrganizerRevenueReport from '@/components/organizer/OrganizerRevenueReport.vue'
import apiClient from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('overview')
const events = ref([])
const loading = ref(true)
const checkingIn = ref(false)
const qrCodeInput = ref('')

const publishedCount = computed(() =>
  events.value.filter((event) => event.status === 'PUBLISHED').length
)

const pendingCount = computed(() =>
  events.value.filter((event) => event.status === 'PENDING').length
)

const totalCapacity = computed(() =>
  events.value.reduce((eventTotal, event) => {
    const capacity = (event.ticket_types || []).reduce(
      (ticketTotal, ticket) =>
        ticketTotal + Number(ticket.quantity || 0),
      0
    )

    return eventTotal + capacity
  }, 0)
)

const recentEvents = computed(() => events.value.slice(0, 4))

const fetchEvents = async () => {
  loading.value = true

  try {
    const response = await apiClient.get('events/organizer/events/')

    events.value = Array.isArray(response.data)
      ? response.data
      : response.data.results || []
  } catch (error) {
    events.value = []

    await Swal.fire({
      title: 'Không thể tải sự kiện',
      text:
        error.response?.data?.detail
        || 'Vui lòng đăng nhập lại hoặc thử lại sau.',
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

const goToCreateEvent = () => {
  router.push({
    name: 'organizer-event-create'
  })
}

const handleCheckIn = async () => {
  if (!qrCodeInput.value) {
    await Swal.fire({
      title: 'Thiếu mã QR',
      text: 'Vui lòng nhập hoặc quét mã vé QR.',
      icon: 'warning',
      confirmButtonColor: '#2563EB',
      customClass: {
        popup: 'rounded-4'
      }
    })

    return
  }

  checkingIn.value = true

  try {
    const response = await apiClient.post('orders/check-in/', {
      qr_code: qrCodeInput.value
    })

    await Swal.fire({
      title: 'Soát vé thành công!',
      text: response.data.message || 'Vé hợp lệ và đã được check-in.',
      icon: 'success',
      confirmButtonColor: '#10B981',
      customClass: {
        popup: 'rounded-4'
      }
    })

    qrCodeInput.value = ''
  } catch (error) {
    await Swal.fire({
      title: 'Soát vé thất bại!',
      text:
        error.response?.data?.error
        || 'Mã vé không hợp lệ hoặc đã được sử dụng.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: {
        popup: 'rounded-4'
      }
    })
  } finally {
    checkingIn.value = false
  }
}

const formatNumber = (value) =>
  new Intl.NumberFormat('vi-VN').format(value)

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

const getCapacity = (event) =>
  (event.ticket_types || []).reduce(
    (total, ticket) => total + Number(ticket.quantity || 0),
    0
  )

const getMinPrice = (event) => {
  const prices = (event.ticket_types || []).map(
    (ticket) => Number(ticket.price || 0)
  )

  if (prices.length === 0) return 0
  return Math.min(...prices)
}

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0
  }).format(value)

const getStatusText = (status) => {
  const labels = {
    PUBLISHED: 'Đang công khai',
    PENDING: 'Chờ duyệt',
    CANCELLED: 'Bị từ chối'
  }

  return labels[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    PUBLISHED: 'status-published',
    PENDING: 'status-pending',
    CANCELLED: 'status-cancelled'
  }

  return classes[status] || 'status-pending'
}

/*
 * Component nhỏ dùng ngay trong file để tránh phải tạo thêm file mới.
 */
const EventList = defineComponent({
  name: 'OrganizerEventList',

  props: {
    events: {
      type: Array,
      default: () => []
    }
  },

  emits: ['create-event'],

  setup(props, { emit }) {
    return () => {
      if (props.events.length === 0) {
        return h(
          'div',
          {
            class: 'empty-state'
          },
          [
            h('i', {
              class: 'bi bi-calendar2-plus empty-icon'
            }),
            h(
              'h5',
              {
                class: 'fw-bold text-slate-900 mt-3'
              },
              'Bạn chưa có sự kiện nào'
            ),
            h(
              'p',
              {
                class: 'text-muted'
              },
              'Hãy tạo sự kiện đầu tiên và cấu hình các loại vé.'
            ),
            h(
              'button',
              {
                type: 'button',
                class: 'btn btn-primary rounded-pill px-4',
                onClick: () => emit('create-event')
              },
              [
                h('i', {
                  class: 'bi bi-plus-lg me-2'
                }),
                'Tạo sự kiện'
              ]
            )
          ]
        )
      }

      return h(
        'div',
        {
          class: 'event-list'
        },
        props.events.map((event) =>
          h(
            'div',
            {
              key: event.id,
              class: 'event-row'
            },
            [
              h('img', {
                src: event.thumbnail,
                alt: event.title,
                class: 'event-thumbnail',
                loading: 'lazy',
                onError: (imageEvent) => {
                  imageEvent.target.src = '/ticket_icon_150905.png'
                }
              }),

              h(
                'div',
                {
                  class: 'event-main'
                },
                [
                  h(
                    'div',
                    {
                      class: 'd-flex flex-wrap align-items-center gap-2'
                    },
                    [
                      h(
                        'h6',
                        {
                          class: 'fw-bold text-slate-900 mb-0'
                        },
                        event.title
                      ),
                      h(
                        'span',
                        {
                          class: [
                            'event-status',
                            getStatusClass(event.status)
                          ]
                        },
                        getStatusText(event.status)
                      )
                    ]
                  ),

                  h(
                    'div',
                    {
                      class: 'event-meta'
                    },
                    [
                      h(
                        'span',
                        {},
                        [
                          h('i', {
                            class: 'bi bi-calendar3 me-1'
                          }),
                          formatDate(event.start_time)
                        ]
                      ),

                      h(
                        'span',
                        {},
                        [
                          h('i', {
                            class: 'bi bi-geo-alt me-1'
                          }),
                          event.location
                        ]
                      )
                    ]
                  ),

                  h(
                    'div',
                    {
                      class: 'event-meta mt-1'
                    },
                    [
                      h(
                        'span',
                        {},
                        `${formatNumber(getCapacity(event))} ghế`
                      ),
                      h(
                        'span',
                        {},
                        `Giá từ ${formatCurrency(getMinPrice(event))}`
                      )
                    ]
                  )
                ]
              ),

              event.status === 'PUBLISHED'
                ? h(
                    'a',
                    {
                      href: `/events/${event.id}`,
                      class:
                        'btn btn-sm btn-outline-primary rounded-pill px-3'
                    },
                    'Xem'
                  )
                : h(
                    'button',
                    {
                      type: 'button',
                      class:
                        'btn btn-sm btn-light border rounded-pill px-3',
                      disabled: true
                    },
                    'Chưa công khai'
                  )
            ]
          )
        )
      )
    }
  }
})

onMounted(fetchEvents)
</script>

<style scoped src="./OrganizerDashboardView.css"></style>
