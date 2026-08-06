<template>
  <div class="bg-page-custom">
    <section class="mb-5">
      <div id="heroCarousel" class="carousel slide carousel-fade shadow-md" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div v-for="(evt, idx) in featuredEvents" :key="evt.id" class="carousel-item" :class="{ active: idx === 0 }">
            <div class="position-relative hero-container">
              <img :src="evt.thumbnail" class="d-block w-100 h-100 hero-img" />
              <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-end p-4 p-md-5 hero-overlay">
                <div class="container text-white">
                  <span class="badge bg-warning text-dark mb-3 px-3 py-2 rounded-pill fw-bold">SẮP DIỄN RA</span>
                  <h1 class="fw-extrabold display-5 mb-2 text-shadow">{{ evt.title }}</h1>
                  <p class="mb-4 fs-5 text-light opacity-90"><i class="bi bi-geo-alt-fill text-danger me-2"></i>{{ evt.location }}</p>
                  <router-link :to="`/events/${evt.id}`" class="btn btn-cta rounded-pill px-4 py-3 fs-5">
                    <i class="bi bi-ticket-perforated me-2"></i>Mua vé ngay
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="container mb-5">
      <div class="d-flex gap-2 overflow-auto pb-2 scrollbar-hidden">
        <button 
          v-for="cat in categories" 
          :key="cat.value" 
          class="btn rounded-pill px-4 py-2 fw-semibold text-nowrap shadow-sm"
          :class="selectedCategory === cat.value ? 'btn-primary-custom' : 'btn-white border-slate'"
          @click="filterCategory(cat.value)"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="mt-4">
        <div class="d-flex align-items-center justify-content-between mb-4">
          <h3 class="fw-bold text-slate-900 mb-0">Sự kiện dành cho bạn</h3>
          <span class="badge bg-blue-subtle text-primary px-3 py-2 rounded-pill fw-semibold fs-6">
            {{ filteredEvents.length }} Sự kiện
          </span>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else-if="filteredEvents.length === 0" class="text-center py-5 bg-white rounded-xl border shadow-sm">
          <i class="bi bi-calendar-x display-4 text-muted"></i>
          <p class="text-secondary mt-3 fs-5">Không tìm thấy sự kiện phù hợp.</p>
        </div>

        <div v-else class="row g-4">
          <div v-for="evt in filteredEvents" :key="evt.id" class="col-lg-3 col-md-6 col-12">
            <div class="card card-event h-100">
              <div class="position-relative">
                <img :src="evt.thumbnail" class="card-img-top" />
                <span class="position-absolute top-0 end-0 bg-primary-custom text-white fs-6 px-3 py-1 m-2 rounded-pill fw-semibold shadow-sm">
                  {{ getCategoryLabel(evt.category) }}
                </span>
              </div>
              <div class="card-body d-flex flex-column p-3.5">
                <h6 class="card-title fw-bold text-truncate-2 mb-2 text-slate-900" style="min-height: 44px;">{{ evt.title }}</h6>
                <p class="text-muted small mb-1.5 text-truncate"><i class="bi bi-calendar3 text-primary me-2"></i>{{ formatDate(evt.start_time) }}</p>
                <p class="text-muted small mb-3 text-truncate"><i class="bi bi-geo-alt text-danger me-2"></i>{{ evt.location }}</p>
                <div class="mt-auto d-flex align-items-center justify-content-between pt-3 border-top">
                  <div>
                    <small class="text-muted d-block fs-7">Giá từ</small>
                    <span class="fw-extrabold text-primary-custom fs-5">{{ formatCurrency(getMinPrice(evt.ticket_types)) }}</span>
                  </div>
                  <router-link :to="`/events/${evt.id}`" class="btn btn-outline-primary rounded-pill btn-sm px-3 fw-semibold">
                    Chi tiết
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/services/api'

const route = useRoute()
const events = ref([])
const loading = ref(true)
const selectedCategory = ref('ALL')

const categories = [
  { label: 'Tất cả', value: 'ALL' },
  { label: 'Âm nhạc', value: 'MUSIC' },
  { label: 'Hội thảo', value: 'WORKSHOP' },
  { label: 'Thể thao', value: 'SPORTS' },
  { label: 'Giải trí', value: 'ENTERTAINMENT' }
]

const fetchEvents = async () => {
  loading.value = true
  try {
    const res = await apiClient.get('events/')
    events.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchEvents)

const featuredEvents = computed(() => events.value.slice(0, 4))

const filteredEvents = computed(() => {
  let result = events.value
  const searchQuery = route.query.search?.toLowerCase()

  if (searchQuery) {
    result = result.filter(e => 
      e.title.toLowerCase().includes(searchQuery) || 
      e.location.toLowerCase().includes(searchQuery)
    )
  }

  if (selectedCategory.value !== 'ALL') {
    result = result.filter(e => e.category === selectedCategory.value)
  }

  return result
})

const filterCategory = (cat) => {
  selectedCategory.value = cat
}

const getCategoryLabel = (catVal) => {
  const found = categories.find(c => c.value === catVal)
  return found ? found.label : catVal
}

const getMinPrice = (ticketTypes) => {
  if (!ticketTypes || ticketTypes.length === 0) return 0
  return Math.min(...ticketTypes.map(t => parseFloat(t.price)))
}

const formatCurrency = (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val)
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.hero-container {
  height: 480px;
}

.hero-img {
  object-fit: cover;
}

.hero-overlay {
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.4) 60%, rgba(0, 0, 0, 0.1) 100%);
}

.text-shadow {
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.fw-extrabold {
  font-weight: 800;
}

.btn-white {
  background-color: #FFFFFF;
  color: #334155;
}

.border-slate {
  border: 1px solid #E2E8F0;
}

.text-slate-900 {
  color: #0F172A;
}

.bg-blue-subtle {
  background-color: #EFF6FF;
}

.fs-7 {
  font-size: 0.75rem;
}
</style>