<template>
  <div class="bg-page-custom py-4">
    <div class="container">
      <HeroBannerDuo />

      <div class="d-flex gap-2 overflow-auto pb-2 scrollbar-hidden mb-4">
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

      <div class="d-flex align-items-center justify-content-between mb-4">
        <h3 class="fw-bold text-slate-900 mb-0">Sự kiện dành cho bạn</h3>
        <span class="badge bg-blue-subtle text-primary px-3 py-2 rounded-pill fw-semibold fs-6">
          {{ totalEvents }} Sự kiện
        </span>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="events.length === 0" class="text-center py-5 bg-white rounded-xl border shadow-sm">
        <i class="bi bi-calendar-x display-4 text-muted"></i>
        <p class="text-secondary mt-3 fs-5">Không tìm thấy sự kiện phù hợp.</p>
      </div>

      <div v-else>
        <div class="row g-4 mb-4">
          <div v-for="evt in events" :key="evt.id" class="col-lg-3 col-md-6 col-12">
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

        <PaginationControls
          :current-page="currentPage"
          :total-pages="totalPages"
          @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/services/api'
import HeroBannerDuo from '@/components/HeroBannerDuo.vue'
import PaginationControls from '@/components/PaginationControls.vue'

const route = useRoute()
const events = ref([])
const totalEvents = ref(0)
const currentPage = ref(1)
const pageSize = 12
const loading = ref(true)
const selectedCategory = ref('ALL')

const categories = [
  { label: 'Tất cả', value: 'ALL' },
  { label: 'Âm nhạc', value: 'MUSIC' },
  { label: 'Hội thảo', value: 'WORKSHOP' },
  { label: 'Thể thao', value: 'SPORTS' },
  { label: 'Giải trí', value: 'ENTERTAINMENT' }
]

const totalPages = computed(() => Math.ceil(totalEvents.value / pageSize) || 1)

const fetchEvents = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      category: selectedCategory.value !== 'ALL' ? selectedCategory.value : undefined,
      search: route.query.search || undefined
    }
    const res = await apiClient.get('events/', { params })
    events.value = res.data.results
    totalEvents.value = res.data.count
  } catch (err) {
    console.error(err)
    events.value = []
    totalEvents.value = 0
  } finally {
    loading.value = false
  }
}

const filterCategory = (cat) => {
  selectedCategory.value = cat
  currentPage.value = 1
  fetchEvents()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchEvents()
  window.scrollTo({ top: 380, behavior: 'smooth' })
}

watch(() => route.query.search, () => {
  currentPage.value = 1
  fetchEvents()
})

onMounted(fetchEvents)

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