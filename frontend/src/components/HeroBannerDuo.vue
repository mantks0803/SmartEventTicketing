<template>
  <div class="position-relative mb-5" @mouseenter="pauseTimer" @mouseleave="resumeTimer">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="pairs.length > 0" class="row g-3">
      <div
        v-for="(evt, idx) in currentPair"
        :key="evt.id || idx"
        class="col-md-6 col-12"
      >
        <div class="position-relative duo-banner-card overflow-hidden shadow-sm">
          <img :src="evt.thumbnail" class="w-100 h-100 duo-img" />
          <div class="position-absolute top-0 start-0 w-100 h-100 duo-overlay d-flex align-items-end p-4">
            <div class="text-white w-100">
              <span class="badge bg-warning text-dark mb-2 px-2.5 py-1 rounded-pill fw-bold fs-7">SẮP DIỄN RA</span>
              <h4 class="fw-extrabold text-truncate mb-1 text-shadow">{{ evt.title }}</h4>
              <p class="small text-slate-light mb-3"><i class="bi bi-calendar-event me-2 text-warning"></i>{{ formatDate(evt.start_time) }}</p>
              <router-link :to="`/events/${evt.id}`" class="btn btn-cta btn-sm rounded-pill px-3 py-1.5 fw-bold">
                Xem chi tiết
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template v-if="pairs.length > 1">
      <button class="nav-arrow nav-prev" @click="prevPair">
        <i class="bi bi-chevron-left fs-5"></i>
      </button>
      <button class="nav-arrow nav-next" @click="nextPair">
        <i class="bi bi-chevron-right fs-5"></i>
      </button>

      <div class="d-flex justify-content-center gap-2 mt-3">
        <button
          v-for="(_, idx) in pairs"
          :key="idx"
          class="dot-indicator"
          :class="{ active: currentPairIndex === idx }"
          @click="goToPair(idx)"
        ></button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '@/services/api'

const featuredEvents = ref([])
const loading = ref(true)
const currentPairIndex = ref(0)
let timer = null
const isHovered = ref(false)

const fetchFeatured = async () => {
  try {
    const res = await apiClient.get('events/featured/')
    featuredEvents.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const pairs = computed(() => {
  const list = featuredEvents.value
  const result = []
  for (let i = 0; i < list.length; i += 2) {
    if (i + 1 < list.length) {
      result.push([list[i], list[i + 1]])
    } else {
      result.push([list[i], list[0]])
    }
  }
  return result
})

const currentPair = computed(() => {
  if (pairs.value.length === 0) return []
  return pairs.value[currentPairIndex.value] || []
})

const startTimer = () => {
  stopTimer()
  timer = setInterval(() => {
    if (!isHovered.value && pairs.value.length > 1) {
      currentPairIndex.value = (currentPairIndex.value + 1) % pairs.value.length
    }
  }, 10000)
}

const stopTimer = () => {
  if (timer) clearInterval(timer)
}

const pauseTimer = () => {
  isHovered.value = true
}

const resumeTimer = () => {
  isHovered.value = false
}

const nextPair = () => {
  currentPairIndex.value = (currentPairIndex.value + 1) % pairs.value.length
  startTimer()
}

const prevPair = () => {
  currentPairIndex.value = (currentPairIndex.value - 1 + pairs.value.length) % pairs.value.length
  startTimer()
}

const goToPair = (idx) => {
  currentPairIndex.value = idx
  startTimer()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await fetchFeatured()
  if (pairs.value.length > 1) {
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
})
</script>

<style scoped>
.duo-banner-card {
  height: 260px;
  border-radius: 16px;
}

.duo-img {
  object-fit: cover;
  transition: transform 0.3s ease;
}

.duo-banner-card:hover .duo-img {
  transform: scale(1.03);
}

.duo-overlay {
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.2) 100%);
}

.fw-extrabold {
  font-weight: 800;
}

.fs-7 {
  font-size: 0.75rem;
}

.text-slate-light {
  color: #CBD5E1;
}

.text-shadow {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.75);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
}

.nav-arrow:hover {
  background: rgba(37, 99, 235, 0.9);
}

.nav-prev {
  left: -18px;
}

.nav-next {
  right: -18px;
}

.dot-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #CBD5E1;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: all 0.2s;
}

.dot-indicator.active {
  width: 24px;
  border-radius: 5px;
  background: #2563EB;
}
</style>