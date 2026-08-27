<template>
  <div class="bg-page-custom py-5 min-vh-100">
    <div class="container">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div>
          <h2 class="fw-bold text-slate-900 mb-1">Tạo sự kiện mới</h2>
          <p class="text-muted mb-0">
            Chọn một sơ đồ mẫu hoặc tự cấu hình các loại vé và hàng ghế.
          </p>
        </div>

        <router-link
          to="/organizer/dashboard"
          class="btn btn-outline-secondary rounded-pill px-4"
        >
          <i class="bi bi-arrow-left me-2"></i>Quay lại Dashboard
        </router-link>
      </div>

      <form @submit.prevent="submitEvent">
        <div class="bg-white rounded-xl border shadow-sm p-4 mb-4">
          <h5 class="fw-bold text-slate-900 mb-3">
            <i class="bi bi-grid-3x3-gap me-2 text-primary"></i>
            Chọn sơ đồ ghế
          </h5>

          <div class="row g-3">
            <div
              v-for="preset in presets"
              :key="preset.id"
              class="col-lg-4 col-md-6"
            >
              <button
                type="button"
                class="preset-card w-100 text-start"
                :class="{ active: selectedPreset === preset.id }"
                @click="applyPreset(preset)"
              >
                <div class="d-flex align-items-start gap-3">
                  <div class="preset-icon">
                    <i :class="preset.icon"></i>
                  </div>

                  <div>
                    <div class="fw-bold text-slate-900">
                      {{ preset.name }}
                    </div>
                    <div class="text-muted small mt-1">
                      {{ preset.description }}
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-lg-7">
            <div class="bg-white rounded-xl border shadow-sm p-4 mb-4">
              <h5 class="fw-bold text-slate-900 mb-4">
                <i class="bi bi-calendar-event me-2 text-primary"></i>
                Thông tin sự kiện
              </h5>

              <div class="mb-3">
                <label class="form-label fw-semibold">
                  Tên sự kiện <span class="text-danger">*</span>
                </label>
                <input
                  v-model.trim="form.title"
                  type="text"
                  class="form-control"
                  placeholder="Ví dụ: Đêm nhạc Acoustic Sài Gòn"
                  maxlength="250"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold">
                  Ảnh sự kiện <span class="text-danger">*</span>
                </label>
                <input
                  ref="fileInputRef"
                  type="file"
                  class="form-control"
                  accept="image/jpeg,image/png,image/webp"
                  @change="handleThumbnailChange"
                  required
                />

                <small class="text-muted d-block mt-2">
                  Chọn ảnh JPG, PNG hoặc WEBP, dung lượng tối đa 5MB.
                </small>

                <img
                  v-if="thumbnailPreview"
                  :src="thumbnailPreview"
                  alt="Xem trước ảnh sự kiện"
                  class="thumbnail-preview mt-3"
                />

                <button
                  v-if="thumbnailPreview"
                  type="button"
                  class="btn btn-sm btn-outline-danger rounded-pill mt-2"
                  @click="clearThumbnail"
                >
                  <i class="bi bi-trash me-1"></i>Xóa ảnh
                </button>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold">
                  Mô tả <span class="text-danger">*</span>
                </label>
                <textarea
                  v-model.trim="form.description"
                  class="form-control"
                  rows="5"
                  placeholder="Giới thiệu nội dung và thông tin sự kiện..."
                  required
                ></textarea>
              </div>

              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Địa điểm <span class="text-danger">*</span>
                  </label>
                  <input
                    v-model.trim="form.location"
                    type="text"
                    class="form-control"
                    placeholder="Nhà hát Hòa Bình, TP.HCM"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Thời gian bắt đầu <span class="text-danger">*</span>
                  </label>
                  <input
                    v-model="form.start_time"
                    type="datetime-local"
                    class="form-control"
                    :min="minDateTime"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Danh mục <span class="text-danger">*</span>
                  </label>
                  <select
                    v-model="form.category"
                    class="form-select"
                    required
                  >
                    <option value="MUSIC">Âm nhạc</option>
                    <option value="WORKSHOP">Hội thảo</option>
                    <option value="SPORTS">Thể thao</option>
                    <option value="ENTERTAINMENT">Giải trí</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl border shadow-sm p-4">
              <div class="d-flex align-items-center justify-content-between mb-4">
                <div>
                  <h5 class="fw-bold text-slate-900 mb-1">
                    <i class="bi bi-ticket-perforated me-2 text-primary"></i>
                    Loại vé và hàng ghế
                  </h5>
                  <small class="text-muted">
                    Mỗi loại vé cần dùng tiền tố hàng khác nhau.
                  </small>
                </div>

                <button
                  type="button"
                  class="btn btn-outline-primary rounded-pill"
                  @click="addTicketType"
                >
                  <i class="bi bi-plus-lg me-1"></i>Thêm loại vé
                </button>
              </div>

              <div
                v-for="(ticket, index) in ticketTypes"
                :key="ticket.localId"
                class="ticket-card border rounded-xl p-3 mb-3"
              >
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <strong>Loại vé {{ index + 1 }}</strong>

                  <button
                    v-if="ticketTypes.length > 1"
                    type="button"
                    class="btn btn-sm btn-outline-danger rounded-circle"
                    title="Xóa loại vé"
                    @click="removeTicketType(index)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-semibold">
                      Tên loại vé
                    </label>
                    <input
                      v-model.trim="ticket.name"
                      type="text"
                      class="form-control"
                      placeholder="VIP, Phổ thông..."
                      required
                    />
                  </div>

                  <div class="col-md-6">
                    <label class="form-label small fw-semibold">
                      Giá vé
                    </label>
                    <div class="input-group">
                      <input
                        v-model.number="ticket.price"
                        type="number"
                        min="1000"
                        step="1000"
                        class="form-control"
                        required
                      />
                      <span class="input-group-text">VNĐ</span>
                    </div>
                  </div>

                  <div class="col-md-4">
                    <label class="form-label small fw-semibold">
                      Tiền tố hàng
                    </label>
                    <input
                      v-model.trim="ticket.row_prefix"
                      type="text"
                      class="form-control text-uppercase"
                      placeholder="VIP"
                      maxlength="10"
                      required
                    />
                    <small class="text-muted">
                      Ví dụ: VIP1, VIP2
                    </small>
                  </div>

                  <div class="col-md-4">
                    <label class="form-label small fw-semibold">
                      Số hàng
                    </label>
                    <input
                      v-model.number="ticket.total_rows"
                      type="number"
                      min="1"
                      max="50"
                      class="form-control"
                      required
                    />
                  </div>

                  <div class="col-md-4">
                    <label class="form-label small fw-semibold">
                      Ghế mỗi hàng
                    </label>
                    <input
                      v-model.number="ticket.seats_per_row"
                      type="number"
                      min="1"
                      max="100"
                      class="form-control"
                      required
                    />
                  </div>
                </div>

                <div class="mt-3 p-2 rounded bg-light text-muted small">
                  Sức chứa:
                  <strong class="text-primary">
                    {{ getTicketQuantity(ticket) }} ghế
                  </strong>
                  · Giá:
                  <strong class="text-primary">
                    {{ formatCurrency(ticket.price) }}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-5">
            <div class="bg-white rounded-xl border shadow-sm p-4 sticky-top-custom">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold text-slate-900 mb-0">
                  Xem trước sơ đồ
                </h5>

                <span class="badge bg-primary rounded-pill px-3 py-2">
                  {{ totalSeats }} ghế
                </span>
              </div>

              <div class="stage-bar">SÂN KHẤU / STAGE</div>

              <div class="seat-preview">
                <div
                  v-for="block in previewBlocks"
                  :key="block.localId"
                  class="preview-block"
                >
                  <div class="d-flex justify-content-between mb-2">
                    <strong>{{ block.name || 'Chưa đặt tên' }}</strong>
                    <span class="text-primary fw-bold small">
                      {{ formatCurrency(block.price) }}
                    </span>
                  </div>

                  <div
                    v-for="row in block.rows"
                    :key="row.name"
                    class="preview-row"
                  >
                    <span class="preview-row-name">{{ row.name }}</span>

                    <div class="preview-seats">
                      <span
                        v-for="seatNumber in row.seats"
                        :key="seatNumber"
                        class="preview-seat"
                      >
                        {{ seatNumber }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="totalSeats > 5000"
                class="alert alert-danger mt-3 mb-0"
              >
                Sự kiện chỉ được tạo tối đa 5.000 ghế.
              </div>

              <button
                type="submit"
                class="btn btn-cta w-100 rounded-pill py-3 mt-4 fw-bold"
                :disabled="submitting || totalSeats <= 0 || totalSeats > 5000"
              >
                <span
                  v-if="submitting"
                  class="spinner-border spinner-border-sm me-2"
                ></span>
                {{ submitButtonText }}
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import apiClient from '@/services/api'

const router = useRouter()
const submitting = ref(false)
const submitStep = ref('')
const thumbnailFile = ref(null)
const thumbnailPreview = ref('')
const fileInputRef = ref(null)
const selectedPreset = ref('custom')
let localId = 1

const form = reactive({
  title: '',
  description: '',
  location: '',
  start_time: '',
  category: 'MUSIC'
})

const createTicket = (
  name = '',
  price = 100000,
  totalRows = 1,
  seatsPerRow = 10,
  rowPrefix = 'A'
) => ({
  localId: localId++,
  name,
  price,
  total_rows: totalRows,
  seats_per_row: seatsPerRow,
  row_prefix: rowPrefix
})

const ticketTypes = ref([
  createTicket('Phổ thông', 100000, 3, 10, 'A')
])

const presets = [
  {
    id: 'small',
    name: 'Phòng nhỏ',
    icon: 'bi bi-people-fill',
    description: 'Khoảng 30–50 ghế, phù hợp workshop nhỏ.',
    tickets: [
      ['Phổ thông', 100000, 4, 10, 'A']
    ]
  },
  {
    id: 'theater',
    name: 'Nhà hát',
    icon: 'bi bi-building',
    description: 'Chia khu VIP và phổ thông theo từng hàng.',
    tickets: [
      ['VIP', 500000, 3, 10, 'VIP'],
      ['Phổ thông', 250000, 6, 12, 'A']
    ]
  },
  {
    id: 'concert',
    name: 'Concert',
    icon: 'bi bi-music-note-beamed',
    description: 'VIP, Fan Zone và khu phổ thông.',
    tickets: [
      ['VIP', 1000000, 3, 10, 'VIP'],
      ['Fan Zone', 700000, 4, 15, 'F'],
      ['Phổ thông', 350000, 8, 20, 'A']
    ]
  },
  {
    id: 'conference',
    name: 'Hội thảo',
    icon: 'bi bi-mic-fill',
    description: 'Khu đại biểu và khách tham dự.',
    tickets: [
      ['Đại biểu', 500000, 3, 10, 'D'],
      ['Khách tham dự', 200000, 7, 12, 'K']
    ]
  },
  {
    id: 'arena',
    name: 'Nhà thi đấu',
    icon: 'bi bi-trophy-fill',
    description: 'Sức chứa lớn cho thể thao và giải trí.',
    tickets: [
      ['VIP', 800000, 5, 20, 'VIP'],
      ['Khán đài A', 400000, 8, 25, 'A'],
      ['Khán đài B', 300000, 8, 25, 'B']
    ]
  },
  {
    id: 'custom',
    name: 'Tùy chỉnh',
    icon: 'bi bi-sliders',
    description: 'Tự tạo loại vé, số hàng và số ghế.',
    tickets: [
      ['Phổ thông', 100000, 3, 10, 'A']
    ]
  }
]

const applyPreset = async (preset) => {
  const result = await Swal.fire({
    title: `Chọn sơ đồ "${preset.name}"?`,
    text: 'Các loại vé đang nhập sẽ được thay bằng sơ đồ mẫu.',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Chọn sơ đồ',
    cancelButtonText: 'Hủy',
    confirmButtonColor: '#F47C5A',
    customClass: {
      popup: 'rounded-4'
    }
  })

  if (!result.isConfirmed) return

  selectedPreset.value = preset.id
  ticketTypes.value = preset.tickets.map((ticket) =>
    createTicket(...ticket)
  )
}

const addTicketType = () => {
  ticketTypes.value.push(
    createTicket('', 100000, 1, 10, `K${ticketTypes.value.length + 1}`)
  )
  selectedPreset.value = 'custom'
}

const removeTicketType = (index) => {
  ticketTypes.value.splice(index, 1)
  selectedPreset.value = 'custom'
}

const getTicketQuantity = (ticket) => {
  return (
    Number(ticket.total_rows || 0)
    * Number(ticket.seats_per_row || 0)
  )
}

const totalSeats = computed(() =>
  ticketTypes.value.reduce(
    (total, ticket) => total + getTicketQuantity(ticket),
    0
  )
)

const previewBlocks = computed(() =>
  ticketTypes.value.map((ticket) => {
    const totalRows = Math.max(0, Number(ticket.total_rows || 0))
    const seatsPerRow = Math.max(0, Number(ticket.seats_per_row || 0))
    const prefix = (ticket.row_prefix || 'A').toUpperCase()

    const rows = []

    for (let rowIndex = 0; rowIndex < totalRows; rowIndex++) {
      rows.push({
        name: `${prefix}${rowIndex + 1}`,
        seats: Array.from(
          { length: seatsPerRow },
          (_, index) => index + 1
        )
      })
    }

    return {
      ...ticket,
      rows
    }
  })
)

const minDateTime = computed(() => {
  const date = new Date()
  date.setMinutes(date.getMinutes() + 5)

  const pad = (value) => String(value).padStart(2, '0')

  return (
    `${date.getFullYear()}-`
    + `${pad(date.getMonth() + 1)}-`
    + `${pad(date.getDate())}T`
    + `${pad(date.getHours())}:`
    + `${pad(date.getMinutes())}`
  )
})

const submitButtonText = computed(() => {
  if (!submitting.value) return 'Tạo sự kiện'
  if (submitStep.value === 'upload') return 'Đang tải ảnh...'
  return 'Đang tạo sự kiện...'
})

const clearThumbnail = () => {
  thumbnailFile.value = null
  thumbnailPreview.value = ''

  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleThumbnailChange = async (event) => {
  const file = event.target.files?.[0]

  if (!file) {
    clearThumbnail()
    return
  }

  const validTypes = ['image/jpeg', 'image/png', 'image/webp']

  if (!validTypes.includes(file.type)) {
    clearThumbnail()
    await Swal.fire({
      title: 'Định dạng ảnh không hợp lệ',
      text: 'Vui lòng chọn ảnh JPG, PNG hoặc WEBP.',
      icon: 'warning',
      confirmButtonColor: '#F47C5A',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    clearThumbnail()
    await Swal.fire({
      title: 'Dung lượng ảnh quá lớn',
      text: 'Ảnh sự kiện không được vượt quá 5MB.',
      icon: 'warning',
      confirmButtonColor: '#F47C5A',
      customClass: { popup: 'rounded-4' }
    })
    return
  }

  thumbnailFile.value = file

  const reader = new FileReader()
  reader.onload = (readerEvent) => {
    thumbnailPreview.value = readerEvent.target.result
  }
  reader.readAsDataURL(file)
}

const validateForm = () => {
  if (
    !form.title
    || !thumbnailFile.value
    || !form.description
    || !form.location
    || !form.start_time
  ) {
    return 'Vui lòng nhập đầy đủ thông tin sự kiện.'
  }

  if (new Date(form.start_time) <= new Date()) {
    return 'Thời gian bắt đầu phải ở tương lai.'
  }

  if (ticketTypes.value.length === 0) {
    return 'Sự kiện phải có ít nhất một loại vé.'
  }

  const names = new Set()
  const rows = new Set()

  for (const ticket of ticketTypes.value) {
    if (!ticket.name.trim()) {
      return 'Vui lòng nhập tên cho tất cả loại vé.'
    }

    const normalizedName = ticket.name.trim().toLowerCase()

    if (names.has(normalizedName)) {
      return `Loại vé "${ticket.name}" đang bị trùng.`
    }

    names.add(normalizedName)

    if (Number(ticket.price) < 1000) {
      return 'Giá vé phải từ 1.000đ.'
    }

    if (
      Number(ticket.total_rows) < 1
      || Number(ticket.seats_per_row) < 1
    ) {
      return 'Số hàng và số ghế phải lớn hơn 0.'
    }

    const prefix = ticket.row_prefix.trim().toUpperCase()

    if (!/^[A-Z0-9]+$/.test(prefix)) {
      return 'Tiền tố hàng chỉ được chứa chữ cái và chữ số.'
    }

    for (let index = 0; index < Number(ticket.total_rows); index++) {
      const rowName = `${prefix}${index + 1}`

      if (rows.has(rowName)) {
        return `Hàng ghế "${rowName}" đang bị trùng.`
      }

      rows.add(rowName)
    }
  }

  if (totalSeats.value > 5000) {
    return 'Mỗi sự kiện chỉ được tạo tối đa 5.000 ghế.'
  }

  return null
}

const extractError = (data) => {
  if (!data) return null
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return extractError(data[0])

  if (typeof data === 'object') {
    for (const value of Object.values(data)) {
      const message = extractError(value)
      if (message) return message
    }
  }

  return null
}

const submitEvent = async () => {
  const validationError = validateForm()

  if (validationError) {
    await Swal.fire({
      title: 'Thông tin chưa hợp lệ',
      text: validationError,
      icon: 'warning',
      confirmButtonColor: '#F47C5A',
      customClass: {
        popup: 'rounded-4'
      }
    })
    return
  }

  submitting.value = true

  try {
    // Upload ảnh trước để API tạo sự kiện vẫn giữ payload JSON đơn giản như cũ.
    submitStep.value = 'upload'

    const imageData = new FormData()
    imageData.append('thumbnail', thumbnailFile.value)

    const uploadResponse = await apiClient.post(
      'events/upload-thumbnail/',
      imageData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    const thumbnailUrl = (
      uploadResponse.data.thumbnail
      || uploadResponse.data.secure_url
    )

    if (!thumbnailUrl) {
      throw new Error('Không nhận được đường dẫn ảnh sau khi upload.')
    }

    submitStep.value = 'create'

    const payload = {
      title: form.title,
      thumbnail: thumbnailUrl,
      description: form.description,
      location: form.location,
      start_time: new Date(form.start_time).toISOString(),
      category: form.category,
      ticket_types: ticketTypes.value.map((ticket) => ({
        name: ticket.name.trim(),
        price: Number(ticket.price),
        total_rows: Number(ticket.total_rows),
        seats_per_row: Number(ticket.seats_per_row),
        row_prefix: ticket.row_prefix.trim().toUpperCase()
      }))
    }

    const response = await apiClient.post('events/create/', payload)

    await Swal.fire({
      title: 'Đã gửi sự kiện thành công!',
      text: `Sự kiện có ${totalSeats.value} ghế đang chờ quản trị viên duyệt.`,
      icon: 'success',
      confirmButtonText: 'Về Dashboard',
      confirmButtonColor: '#10B981',
      customClass: {
        popup: 'rounded-4'
      }
    })

    router.push({
      name: 'organizer-dashboard',
      query: {
        created: response.data.id
      }
    })
  } catch (error) {
    await Swal.fire({
      title: 'Tạo sự kiện thất bại',
      text:
        extractError(error.response?.data)
        || 'Không thể tạo sự kiện. Vui lòng kiểm tra lại thông tin.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: {
        popup: 'rounded-4'
      }
    })
  } finally {
    submitting.value = false
    submitStep.value = ''
  }
}

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(Number(value || 0))
</script>

<style scoped src="./OrganizerEventCreateView.css"></style>
