<template>
  <div class="seat-map-wrapper">
    <div class="stage-bar shadow-sm">
      SÂN KHẤU / STAGE
    </div>

    <div class="legend-container">
      <div class="legend-item">
        <span class="legend-box seat-available border"></span>
        <span>Còn trống</span>
      </div>
      <div class="legend-item">
        <span class="legend-box seat-selected"></span>
        <span>Đang chọn</span>
      </div>
      <div class="legend-item">
        <span class="legend-box seat-locked"></span>
        <span>Đang giữ</span>
      </div>
      <div class="legend-item">
        <span class="legend-box seat-sold"></span>
        <span>Đã bán</span>
      </div>
    </div>

    <div class="seat-map-scroll-area">
      <div
        v-for="block in groupedBlocks"
        :key="block.ticketTypeId"
        class="block-card"
        :style="{ borderColor: block.color }"
      >
        <div class="block-header d-flex align-items-center justify-content-between mb-3">
          <span class="fw-bold fs-6 text-slate-900">{{ block.ticketTypeName }}</span>
          <span class="badge rounded-pill text-white px-3 py-1.5 fw-bold" :style="{ backgroundColor: block.color }">
            {{ formatCurrency(block.price) }}
          </span>
        </div>

        <div class="block-rows d-flex flex-column gap-2">
          <div
            v-for="rowGroup in block.rows"
            :key="rowGroup.rowName"
            class="seat-row"
          >
            <div class="row-label">{{ rowGroup.rowName }}</div>
            <div class="seats-grid">
              <button
                v-for="seat in rowGroup.seats"
                :key="seat.id"
                class="seat-btn-item"
                :class="getSeatClass(seat)"
                :style="getSeatStyle(seat, block.color)"
                :disabled="seat.status === 'SOLD' || seat.status === 'LOCKED'"
                :title="seat.status === 'AVAILABLE' ? `${seat.seat_name} - ${formatCurrency(seat.price)}` : ''"
                @click="$emit('toggle-select-seat', seat.id)"
              >
                <i v-if="selectedSeatIds.includes(seat.id)" class="bi bi-check-lg"></i>
                <i v-else-if="seat.status === 'LOCKED'" class="bi bi-lock-fill fs-8"></i>
                <i v-else-if="seat.status === 'SOLD'" class="bi bi-x-lg fs-8"></i>
                <span v-else>{{ seat.number }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  seats: {
    type: Array,
    required: true,
    default: () => []
  },
  selectedSeatIds: {
    type: Array,
    required: true,
    default: () => []
  }
})

defineEmits(['toggle-select-seat'])

const colorPalette = ['#1976D2', '#7C3AED', '#059669', '#D97706', '#E11D48']

const getTicketTypeColor = (ticketTypeId) => {
  const index = Math.abs(ticketTypeId || 0) % colorPalette.length
  return colorPalette[index]
}

const groupedBlocks = computed(() => {
  if (!props.seats || props.seats.length === 0) return []

  const blocksMap = new Map()

  props.seats.forEach(seat => {
    const typeId = seat.ticket_type
    if (!blocksMap.has(typeId)) {
      blocksMap.set(typeId, {
        ticketTypeId: typeId,
        ticketTypeName: seat.ticket_type_name || 'Loại vé',
        price: seat.price || 0,
        color: getTicketTypeColor(typeId),
        rowsMap: new Map()
      })
    }

    const block = blocksMap.get(typeId)
    const rowName = seat.row || 'A'
    if (!block.rowsMap.has(rowName)) {
      block.rowsMap.set(rowName, [])
    }
    block.rowsMap.get(rowName).push(seat)
  })

  return Array.from(blocksMap.values()).map(block => {
    const rows = Array.from(block.rowsMap.entries()).map(([rowName, seatsList]) => {
      return {
        rowName,
        seats: seatsList.sort((a, b) => (a.number || 0) - (b.number || 0))
      }
    })
    return {
      ...block,
      rows
    }
  })
})

const getSeatClass = (seat) => {
  if (props.selectedSeatIds.includes(seat.id)) return 'seat-selected'
  if (seat.status === 'LOCKED') return 'seat-locked'
  if (seat.status === 'SOLD') return 'seat-sold'
  return 'seat-available'
}

const getSeatStyle = (seat, blockColor) => {
  if (seat.status === 'AVAILABLE' && !props.selectedSeatIds.includes(seat.id)) {
    return {
      borderColor: blockColor,
      color: '#0F172A'
    }
  }
  return {}
}

const formatCurrency = (val) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
}
</script>

<style scoped>
.seat-map-wrapper {
  width: 100%;
}

.stage-bar {
  background-color: #0F172A;
  color: #FFFFFF;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 800;
  letter-spacing: 2px;
  text-align: center;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.legend-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.seat-map-scroll-area {
  max-height: 55vh;
  overflow: auto;
  padding: 8px;
  border-radius: 12px;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
}

.block-card {
  border-width: 2px;
  border-style: solid;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  background-color: #FFFFFF;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.seat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: max-content;
}

.row-label {
  min-width: 54px;
  font-weight: 700;
  font-size: 0.825rem;
  color: #475569;
  text-align: right;
}

.seats-grid {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
}

.seat-btn-item {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease-in-out;
  padding: 0;
  border-width: 2px;
  border-style: solid;
}

.seat-btn-item.seat-available {
  background-color: #FFFFFF;
}

.seat-btn-item.seat-available:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
}

.seat-btn-item.seat-selected {
  background-color: #1976D2 !important;
  border-color: #1976D2 !important;
  color: #FFFFFF !important;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.3);
}

.seat-btn-item.seat-locked {
  background-color: #FEF3C7 !important;
  border-color: #F59E0B !important;
  color: #92400E !important;
  cursor: not-allowed;
  opacity: 0.85;
}

.seat-btn-item.seat-sold {
  background-color: #CBD5E1 !important;
  border-color: #64748B !important;
  color: #475569 !important;
  cursor: not-allowed;
  opacity: 0.6;
}

.text-slate-900 {
  color: #0F172A;
}

.fs-8 {
  font-size: 0.7rem;
}

@media (max-width: 576px) {
  .seat-btn-item {
    width: 30px;
    height: 30px;
    font-size: 0.65rem;
    border-radius: 6px;
  }
  .row-label {
    min-width: 40px;
    font-size: 0.75rem;
  }
  .block-card {
    padding: 12px;
  }
}
</style>