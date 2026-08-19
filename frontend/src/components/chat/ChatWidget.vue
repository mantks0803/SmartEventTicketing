<template>
  <div v-if="canUseChat" class="chat-widget">
    <button
      v-if="!isOpen"
      type="button"
      class="chat-launcher"
      aria-label="Mở trợ lý SmartTicket"
      @click="openChat"
    >
      <i class="bi bi-chat-dots-fill"></i>
    </button>

    <section
      v-else
      class="chat-panel"
      aria-label="Trợ lý SmartTicket"
    >
      <header class="chat-header">
        <div class="chat-brand">
          <div class="chat-brand-icon">
            <i class="bi bi-stars"></i>
          </div>
          <div>
            <strong>SmartTicket AI</strong>
            <small>Tư vấn sự kiện trực tuyến</small>
          </div>
        </div>

        <div class="chat-header-actions">
          <button
            type="button"
            class="chat-icon-button"
            title="Cuộc trò chuyện mới"
            :disabled="loading"
            @click="startNewConversation"
          >
            <i class="bi bi-plus-lg"></i>
          </button>
          <button
            type="button"
            class="chat-icon-button"
            title="Đóng"
            @click="isOpen = false"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </header>

      <div ref="messageContainerRef" class="chat-messages">
        <div
          v-if="messages.length === 0 && !mode"
          class="chat-welcome"
        >
          <div class="chat-welcome-icon">
            <i class="bi bi-robot"></i>
          </div>
          <h5>Xin chào! Bạn cần hỗ trợ gì?</h5>
          <p>
            Chọn một chức năng để bắt đầu trò chuyện với trợ lý.
          </p>

          <div class="chat-mode-cards">
            <button
              v-for="option in modeOptions"
              :key="option.value"
              type="button"
              class="chat-mode-card"
              @click="selectMode(option.value)"
            >
              <i :class="option.icon"></i>
              <span>
                <strong>{{ option.label }}</strong>
                <small>{{ option.description }}</small>
              </span>
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>

        <div
          v-else-if="messages.length === 0"
          class="chat-mode-ready"
        >
          <i :class="selectedModeOption.icon"></i>
          <strong>{{ selectedModeOption.label }}</strong>
          <span>{{ selectedModeOption.description }}</span>
        </div>

        <article
          v-for="chatMessage in messages"
          :key="chatMessage.id"
          class="chat-message"
          :class="chatMessage.sender === 'USER' ? 'chat-message-user' : 'chat-message-assistant'"
        >
          <div class="chat-bubble">
            {{ chatMessage.text }}
          </div>

          <div
            v-if="chatMessage.sources.length"
            class="chat-result-card chat-sources"
          >
            <strong>
              <i class="bi bi-journal-text"></i>
              Nguồn tham khảo
            </strong>
            <div
              v-for="source in chatMessage.sources"
              :key="source.source_path || source.title"
              class="chat-source-item"
            >
              <span>{{ source.title }}</span>
              <small>{{ source.source_path }}</small>
            </div>
          </div>

          <div
            v-if="chatMessage.recommendedEvents.length"
            class="chat-event-list"
          >
            <article
              v-for="event in chatMessage.recommendedEvents"
              :key="event.event_id"
              class="chat-event-card"
            >
              <img
                :src="event.thumbnail || fallbackImage"
                :alt="event.title"
                @error="useFallbackImage"
              />
              <div class="chat-event-content">
                <strong>{{ event.title }}</strong>
                <span>
                  <i class="bi bi-geo-alt"></i>
                  {{ event.location }}
                </span>
                <span>
                  <i class="bi bi-calendar3"></i>
                  {{ formatDate(event.start_time) }}
                </span>
                <div class="chat-event-summary">
                  <b>
                    {{ event.min_ticket_price != null ? formatCurrency(event.min_ticket_price) : 'Chưa có giá' }}
                  </b>
                  <small>{{ event.available_seats }} ghế còn</small>
                </div>
                <button
                  type="button"
                  class="chat-detail-button"
                  @click="viewEvent(event.event_id)"
                >
                  Xem chi tiết
                </button>
              </div>
            </article>
          </div>

          <div
            v-if="chatMessage.eventAvailability?.status === 'found'"
            class="chat-result-card chat-availability"
          >
            <div class="chat-result-heading">
              <span>
                <i class="bi bi-ticket-perforated"></i>
                Tình trạng ghế
              </span>
              <b>
                {{ chatMessage.eventAvailability.available_seats || 0 }}/{{ chatMessage.eventAvailability.total_seats || 0 }} ghế còn
              </b>
            </div>
            <h6>{{ chatMessage.eventAvailability.title }}</h6>
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th>Loại vé</th>
                    <th>Giá</th>
                    <th class="text-end">Còn</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!(chatMessage.eventAvailability.ticket_types || []).length">
                    <td colspan="3" class="text-center text-muted py-2">
                      Chưa có thông tin loại vé.
                    </td>
                  </tr>
                  <tr
                    v-for="ticketType in chatMessage.eventAvailability.ticket_types || []"
                    :key="ticketType.ticket_type_id || ticketType.ticket_type_name"
                  >
                    <td>{{ ticketType.ticket_type_name }}</td>
                    <td>{{ formatCurrency(ticketType.price) }}</td>
                    <td class="text-end">
                      {{ ticketType.available_count }}/{{ ticketType.total_count }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <button
              v-if="chatMessage.eventAvailability.event_id"
              type="button"
              class="chat-detail-button mt-2"
              @click="viewEvent(chatMessage.eventAvailability.event_id)"
            >
              Xem sự kiện
            </button>
          </div>

          <div
            v-else-if="chatMessage.eventAvailability?.status === 'multiple_matches'"
            class="chat-result-card chat-suggestions"
          >
            <strong>Chọn sự kiện cần kiểm tra</strong>
            <div
              v-for="suggestion in chatMessage.eventAvailability.suggestions || []"
              :key="suggestion.event_id"
              class="chat-suggestion-item"
            >
              <div>
                <b>{{ suggestion.title }}</b>
                <small>
                  {{ suggestion.location }} · {{ formatDate(suggestion.start_time) }}
                </small>
              </div>
              <button
                type="button"
                :disabled="loading"
                @click="selectSuggestion(suggestion)"
              >
                Chọn
              </button>
            </div>
          </div>

          <div
            v-else-if="chatMessage.eventAvailability?.status === 'not_found'
              && chatMessage.eventAvailability.message !== chatMessage.text"
            class="chat-result-card chat-not-found"
          >
            <i class="bi bi-search"></i>
            <span>{{ chatMessage.eventAvailability.message }}</span>
          </div>

          <div
            v-if="chatMessage.costBreakdown"
            class="chat-result-card chat-cost-card"
          >
            <strong>
              <i class="bi bi-calculator"></i>
              Dự toán tham khảo
            </strong>
            <div class="chat-cost-row">
              <span>Số khách</span>
              <b>{{ formatNumber(chatMessage.costBreakdown.guest_count) }}</b>
            </div>
            <div class="chat-cost-row">
              <span>Chi phí thấp nhất</span>
              <b>{{ formatCurrency(chatMessage.costBreakdown.min_cost) }}</b>
            </div>
            <div class="chat-cost-row">
              <span>Chi phí cao nhất</span>
              <b>{{ formatCurrency(chatMessage.costBreakdown.max_cost) }}</b>
            </div>
            <div class="chat-cost-row">
              <span>Dự phòng</span>
              <b>{{ formatCurrency(chatMessage.costBreakdown.contingency) }}</b>
            </div>
            <div class="chat-cost-row chat-cost-total">
              <span>Tổng dự kiến</span>
              <b>{{ formatCurrency(chatMessage.costBreakdown.total_estimated_cost) }}</b>
            </div>
            <div
              v-if="chatMessage.ticketPriceSuggestion"
              class="chat-ticket-price"
            >
              <div class="chat-cost-row">
                <span>Giá vé hòa vốn</span>
                <b>{{ formatCurrency(chatMessage.ticketPriceSuggestion.breakeven_price) }}</b>
              </div>
              <div
                v-if="chatMessage.ticketPriceSuggestion.market_reference_avg_price != null"
                class="chat-cost-row"
              >
                <span>Giá thị trường tham khảo</span>
                <b>{{ formatCurrency(chatMessage.ticketPriceSuggestion.market_reference_avg_price) }}</b>
              </div>
            </div>
            <small class="chat-cost-note">
              Số liệu dùng cho mục đích tham khảo trong bản demo.
            </small>
          </div>
        </article>

        <div v-if="loading" class="chat-message chat-message-assistant">
          <div class="chat-bubble chat-typing">
            <span></span>
            <span></span>
            <span></span>
            <small>Đang trả lời...</small>
          </div>
        </div>
      </div>

      <footer v-if="mode" class="chat-composer-area">
        <div class="chat-mode-tabs">
          <button
            v-for="option in modeOptions"
            :key="option.value"
            type="button"
            :class="{ active: mode === option.value }"
            :disabled="loading"
            @click="selectMode(option.value)"
          >
            <i :class="option.icon"></i>
            {{ option.shortLabel }}
          </button>
        </div>

        <div
          v-if="mode === 'RECOMMEND_EVENT'"
          class="chat-smart-form"
        >
          <div class="chat-submode-tabs">
            <button
              type="button"
              :class="{ active: recommendType === 'search' }"
              :disabled="loading"
              @click="recommendType = 'search'"
            >
              Tìm kiếm
            </button>
            <button
              type="button"
              :class="{ active: recommendType === 'availability' }"
              :disabled="loading"
              @click="recommendType = 'availability'"
            >
              Kiểm tra ghế
            </button>
          </div>

          <div
            v-if="recommendType === 'search'"
            class="chat-form-grid"
          >
            <label>
              <span>Danh mục</span>
              <select v-model="recommendForm.category" :disabled="loading">
                <option value="">Tất cả</option>
                <option
                  v-for="category in categoryOptions"
                  :key="category.value"
                  :value="category.value"
                >
                  {{ category.label }}
                </option>
              </select>
            </label>
            <label>
              <span>Địa điểm</span>
              <input
                v-model="recommendForm.location"
                type="text"
                placeholder="Ví dụ: TP.HCM"
                :disabled="loading"
              />
            </label>
            <label class="chat-form-full">
              <span>Giá vé tối đa</span>
              <input
                v-model="recommendForm.max_price"
                type="number"
                min="0"
                step="1000"
                placeholder="Ví dụ: 500000"
                :disabled="loading"
              />
            </label>
          </div>

          <label v-else class="chat-form-field">
            <span>Tên sự kiện</span>
            <input
              v-model="recommendForm.event_name"
              type="text"
              placeholder="Nhập tên sự kiện cần kiểm tra"
              :disabled="loading"
            />
          </label>
        </div>

        <div
          v-if="mode === 'PLAN_EVENT'"
          class="chat-smart-form"
        >
          <button
            type="button"
            class="chat-collapse-button"
            :disabled="loading"
            @click="isPlanFormOpen = !isPlanFormOpen"
          >
            <span>
              <i class="bi bi-sliders"></i>
              Thông tin sự kiện
            </span>
            <i :class="isPlanFormOpen ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
          </button>

          <div v-show="isPlanFormOpen" class="chat-plan-form">
            <div class="chat-form-grid">
              <label>
                <span>Loại sự kiện *</span>
                <select v-model="planForm.category" :disabled="loading">
                  <option
                    v-for="category in categoryOptions"
                    :key="category.value"
                    :value="category.value"
                  >
                    {{ category.label }}
                  </option>
                </select>
              </label>
              <label>
                <span>Số khách *</span>
                <input
                  v-model="planForm.guest_count"
                  type="number"
                  min="1"
                  step="1"
                  :disabled="loading"
                />
              </label>
              <label>
                <span>Chất lượng *</span>
                <select v-model="planForm.quality_level" :disabled="loading">
                  <option
                    v-for="quality in qualityOptions"
                    :key="quality.value"
                    :value="quality.value"
                  >
                    {{ quality.label }}
                  </option>
                </select>
              </label>
              <label>
                <span>Địa điểm *</span>
                <input
                  v-model="planForm.location"
                  type="text"
                  placeholder="Ví dụ: TP.HCM"
                  :disabled="loading"
                />
              </label>
              <label class="chat-form-full">
                <span>Thời lượng giờ</span>
                <input
                  v-model="planForm.duration_hours"
                  type="number"
                  min="0.01"
                  step="0.5"
                  placeholder="Không bắt buộc"
                  :disabled="loading"
                />
              </label>
            </div>

            <fieldset class="chat-service-options">
              <legend>Dịch vụ cần dùng *</legend>
              <label
                v-for="service in serviceOptions"
                :key="service.value"
              >
                <input
                  v-model="planForm.service_categories"
                  type="checkbox"
                  :value="service.value"
                  :disabled="loading"
                />
                <span>{{ service.label }}</span>
              </label>
            </fieldset>
          </div>
        </div>

        <form class="chat-composer" @submit.prevent="sendMessage">
          <textarea
            v-model="messageText"
            rows="2"
            maxlength="1000"
            :placeholder="messagePlaceholder"
            :disabled="loading"
            @keydown="handleMessageKeydown"
          ></textarea>
          <button
            type="submit"
            :disabled="loading"
            aria-label="Gửi tin nhắn"
          >
            <i class="bi bi-send-fill"></i>
          </button>
        </form>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'

import apiClient from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const modeOptions = [
  {
    value: 'GENERAL',
    label: 'Hỏi hệ thống',
    shortLabel: 'Hỏi đáp',
    description: 'Hỏi về giữ ghế, thanh toán và vé QR',
    icon: 'bi bi-chat-square-text'
  },
  {
    value: 'RECOMMEND_EVENT',
    label: 'Tìm sự kiện',
    shortLabel: 'Sự kiện',
    description: 'Tìm sự kiện phù hợp hoặc kiểm tra ghế',
    icon: 'bi bi-calendar-event'
  },
  {
    value: 'PLAN_EVENT',
    label: 'Tư vấn tổ chức',
    shortLabel: 'Tổ chức',
    description: 'Dự toán chi phí và tham khảo giá vé',
    icon: 'bi bi-calculator'
  }
]

const categoryOptions = [
  { value: 'MUSIC', label: 'Âm nhạc' },
  { value: 'WORKSHOP', label: 'Workshop' },
  { value: 'ENTERTAINMENT', label: 'Giải trí' },
  { value: 'SPORTS', label: 'Thể thao' }
]

const qualityOptions = [
  { value: 'ECONOMY', label: 'Tiết kiệm' },
  { value: 'STANDARD', label: 'Tiêu chuẩn' },
  { value: 'PREMIUM', label: 'Cao cấp' }
]

const serviceOptions = [
  { value: 'VENUE', label: 'Địa điểm' },
  { value: 'CATERING', label: 'Ăn uống' },
  { value: 'SOUND_LIGHT', label: 'Âm thanh ánh sáng' },
  { value: 'DECORATION', label: 'Trang trí' },
  { value: 'STAFF', label: 'Nhân sự' },
  { value: 'MEDIA', label: 'Truyền thông' }
]

const fallbackImage = '/ticket_icon_150905.png'

const isOpen = ref(false)
const loading = ref(false)
const forbiddenByApi = ref(false)
const mode = ref(null)
const recommendType = ref('search')
const isPlanFormOpen = ref(true)
const messageText = ref('')
const sessionId = ref(null)
const messages = ref([])
const messageContainerRef = ref(null)

let messageId = 0
let requestVersion = 0

const recommendForm = reactive({
  category: '',
  location: '',
  max_price: '',
  event_name: ''
})

const planForm = reactive({
  category: 'MUSIC',
  guest_count: 100,
  quality_level: 'STANDARD',
  location: 'TP.HCM',
  service_categories: ['VENUE', 'SOUND_LIGHT'],
  duration_hours: 4
})

const canUseChat = computed(() => (
  authStore.isAuthenticated
  && (authStore.isCustomer || authStore.isOrganizer)
  && !forbiddenByApi.value
))

const selectedModeOption = computed(() => (
  modeOptions.find((option) => option.value === mode.value)
  || modeOptions[0]
))

const messagePlaceholder = computed(() => {
  if (mode.value === 'RECOMMEND_EVENT') {
    return recommendType.value === 'availability'
      ? 'Bạn muốn kiểm tra điều gì về sự kiện này?'
      : 'Mô tả sự kiện bạn muốn tìm...'
  }

  if (mode.value === 'PLAN_EVENT') {
    return 'Bạn muốn được tư vấn thêm điều gì?'
  }

  return 'Nhập câu hỏi của bạn...'
})

const scrollToBottom = async () => {
  await nextTick()

  if (messageContainerRef.value) {
    messageContainerRef.value.scrollTop = (
      messageContainerRef.value.scrollHeight
    )
  }
}

const openChat = async () => {
  isOpen.value = true
  await scrollToBottom()
}

const resetForms = () => {
  recommendType.value = 'search'
  Object.assign(recommendForm, {
    category: '',
    location: '',
    max_price: '',
    event_name: ''
  })
  Object.assign(planForm, {
    category: 'MUSIC',
    guest_count: 100,
    quality_level: 'STANDARD',
    location: 'TP.HCM',
    service_categories: ['VENUE', 'SOUND_LIGHT'],
    duration_hours: 4
  })
  isPlanFormOpen.value = true
  messageText.value = ''
}

const clearConversation = () => {
  sessionId.value = null
  messages.value = []
  mode.value = null
  messageId = 0
  resetForms()
}

const startNewConversation = () => {
  if (loading.value) return
  clearConversation()
}

const selectMode = (selectedMode) => {
  if (loading.value) return
  mode.value = selectedMode

  if (selectedMode === 'PLAN_EVENT') {
    isPlanFormOpen.value = true
  }
}

const buildRecommendPreferences = () => {
  if (recommendType.value === 'availability') {
    const eventName = recommendForm.event_name.trim()

    if (!eventName) {
      throw new Error('Vui lòng nhập tên sự kiện cần kiểm tra.')
    }

    return {
      event_name: eventName
    }
  }

  const preferences = {}
  const location = recommendForm.location.trim()

  if (recommendForm.category) {
    preferences.category = recommendForm.category
  }

  if (location) {
    preferences.location = location
  }

  if (
    recommendForm.max_price !== ''
    && recommendForm.max_price !== null
  ) {
    const maxPrice = Number(recommendForm.max_price)

    if (!Number.isFinite(maxPrice) || maxPrice < 0) {
      throw new Error('Giá vé tối đa không hợp lệ.')
    }

    preferences.max_price = maxPrice
  }

  return preferences
}

const buildPlanPreferences = () => {
  const guestCount = Number(planForm.guest_count)
  const location = planForm.location.trim()

  if (!planForm.category) {
    throw new Error('Vui lòng chọn loại sự kiện.')
  }

  if (!Number.isInteger(guestCount) || guestCount <= 0) {
    throw new Error('Số khách phải là số nguyên lớn hơn 0.')
  }

  if (!planForm.quality_level) {
    throw new Error('Vui lòng chọn mức chất lượng.')
  }

  if (!location) {
    throw new Error('Vui lòng nhập địa điểm tổ chức.')
  }

  if (!planForm.service_categories.length) {
    throw new Error('Vui lòng chọn ít nhất một dịch vụ.')
  }

  const preferences = {
    category: planForm.category,
    guest_count: guestCount,
    quality_level: planForm.quality_level,
    location,
    service_categories: [...planForm.service_categories]
  }

  if (
    planForm.duration_hours !== ''
    && planForm.duration_hours !== null
  ) {
    const durationHours = Number(planForm.duration_hours)

    if (!Number.isFinite(durationHours) || durationHours <= 0) {
      throw new Error('Thời lượng phải lớn hơn 0 giờ.')
    }

    preferences.duration_hours = durationHours
  }

  return preferences
}

const getDefaultMessage = (selectedMode) => {
  if (selectedMode === 'RECOMMEND_EVENT') {
    return recommendType.value === 'availability'
      ? 'Kiểm tra tình trạng ghế của sự kiện'
      : 'Tìm sự kiện phù hợp'
  }

  if (selectedMode === 'PLAN_EVENT') {
    return 'Tư vấn kế hoạch, chi phí tổ chức và giá vé phù hợp'
  }

  return ''
}

const findErrorText = (value) => {
  if (typeof value === 'string') return value

  if (Array.isArray(value)) {
    for (const item of value) {
      const message = findErrorText(item)
      if (message) return message
    }
  }

  if (value && typeof value === 'object') {
    const preferredKeys = ['error', 'detail', 'preferences', 'message']

    for (const key of preferredKeys) {
      if (key in value) {
        const message = findErrorText(value[key])
        if (message) return message
      }
    }

    for (const item of Object.values(value)) {
      const message = findErrorText(item)
      if (message) return message
    }
  }

  return ''
}

const showInputError = async (message) => {
  await Swal.fire({
    title: 'Thông tin chưa đầy đủ',
    text: message,
    icon: 'warning',
    confirmButtonColor: '#2563EB',
    customClass: { popup: 'rounded-4' }
  })
}

const createUserMessage = (text) => ({
  id: ++messageId,
  sender: 'USER',
  text,
  sources: [],
  recommendedEvents: [],
  eventAvailability: null,
  costBreakdown: null,
  ticketPriceSuggestion: null
})

const createAssistantMessage = (data) => ({
  id: ++messageId,
  sender: 'ASSISTANT',
  text: data.answer || 'Trợ lý chưa có nội dung trả lời.',
  sources: Array.isArray(data.sources) ? data.sources : [],
  recommendedEvents: Array.isArray(data.recommended_events)
    ? data.recommended_events
    : [],
  eventAvailability: data.event_availability || null,
  costBreakdown: data.cost_breakdown || null,
  ticketPriceSuggestion: data.ticket_price_suggestion || null
})

const submitMessage = async (options = {}) => {
  if (loading.value) return

  const selectedMode = options.mode || mode.value

  if (!selectedMode) return

  let preferences

  try {
    if (options.preferences) {
      preferences = options.preferences
    } else if (selectedMode === 'RECOMMEND_EVENT') {
      preferences = buildRecommendPreferences()
    } else if (selectedMode === 'PLAN_EVENT') {
      preferences = buildPlanPreferences()
    }
  } catch (error) {
    await showInputError(error.message)
    return
  }

  const typedMessage = String(
    options.message ?? messageText.value
  ).trim()
  const finalMessage = typedMessage || getDefaultMessage(selectedMode)

  if (!finalMessage) {
    await showInputError('Vui lòng nhập câu hỏi cần hỗ trợ.')
    return
  }

  if (finalMessage.length > 1000) {
    await showInputError('Tin nhắn không được vượt quá 1000 ký tự.')
    return
  }

  const payload = {
    message: finalMessage,
    mode: selectedMode
  }

  if (sessionId.value) {
    payload.session_id = sessionId.value
  }

  if (selectedMode !== 'GENERAL') {
    payload.preferences = preferences || {}
  }

  mode.value = selectedMode
  const pendingUserMessage = createUserMessage(finalMessage)
  messages.value.push(pendingUserMessage)
  messageText.value = ''
  loading.value = true
  const currentRequestVersion = ++requestVersion
  const requestToken = authStore.accessToken
  const requestUserId = authStore.user?.id || null
  await scrollToBottom()

  try {
    const response = await apiClient.post('ai/chat/', payload)

    if (
      currentRequestVersion !== requestVersion
      || requestToken !== authStore.accessToken
      || requestUserId !== (authStore.user?.id || null)
    ) {
      return
    }

    sessionId.value = response.data.session_id
    messages.value.push(createAssistantMessage(response.data))

    if (selectedMode === 'PLAN_EVENT') {
      isPlanFormOpen.value = false
    }
  } catch (error) {
    if (
      currentRequestVersion !== requestVersion
      || requestToken !== authStore.accessToken
      || requestUserId !== (authStore.user?.id || null)
    ) {
      return
    }

    const httpStatus = error.response?.status

    if (httpStatus === 403) {
      forbiddenByApi.value = true
      isOpen.value = false
      clearConversation()
      return
    }

    if (httpStatus === 401) {
      authStore.logout()
      isOpen.value = false
      clearConversation()

      await Swal.fire({
        title: 'Phiên đăng nhập đã hết hạn',
        text: 'Vui lòng đăng nhập lại để tiếp tục sử dụng trợ lý.',
        icon: 'info',
        confirmButtonColor: '#2563EB',
        customClass: { popup: 'rounded-4' }
      })
      return
    }

    messages.value = messages.value.filter(
      (chatMessage) => chatMessage.id !== pendingUserMessage.id
    )
    messageText.value = typedMessage

    await Swal.fire({
      title: 'Không thể gửi câu hỏi',
      text: findErrorText(error.response?.data)
        || 'Vui lòng kiểm tra thông tin và thử lại.',
      icon: 'error',
      confirmButtonColor: '#EF4444',
      customClass: { popup: 'rounded-4' }
    })
  } finally {
    if (currentRequestVersion === requestVersion) {
      loading.value = false
      await scrollToBottom()
    }
  }
}

const sendMessage = () => submitMessage()

const selectSuggestion = async (suggestion) => {
  if (loading.value) return

  mode.value = 'RECOMMEND_EVENT'
  recommendType.value = 'availability'
  recommendForm.event_name = suggestion.title

  await submitMessage({
    mode: 'RECOMMEND_EVENT',
    message: `Kiểm tra ghế của sự kiện ${suggestion.title}`,
    preferences: {
      event_id: suggestion.event_id
    }
  })
}

const handleMessageKeydown = (event) => {
  if (
    event.key === 'Enter'
    && !event.shiftKey
    && !event.isComposing
  ) {
    event.preventDefault()
    sendMessage()
  }
}

const viewEvent = async (eventId) => {
  isOpen.value = false
  await router.push({
    name: 'event-detail',
    params: { id: eventId }
  })
}

const useFallbackImage = (event) => {
  if (event.target.src.endsWith(fallbackImage)) return
  event.target.src = fallbackImage
}

const formatCurrency = (value) => new Intl.NumberFormat('vi-VN', {
  style: 'currency',
  currency: 'VND',
  maximumFractionDigits: 0
}).format(Number(value || 0))

const formatNumber = (value) => new Intl.NumberFormat('vi-VN').format(
  Number(value || 0)
)

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

watch(
  () => [authStore.accessToken, authStore.user?.id || null],
  ([newToken, newUserId], [oldToken, oldUserId]) => {
    if (newToken === oldToken && newUserId === oldUserId) return

    requestVersion += 1
    loading.value = false
    clearConversation()
    forbiddenByApi.value = false

    if (!newUserId) {
      isOpen.value = false
    }
  }
)
</script>

<style scoped src="./ChatWidget.css"></style>
