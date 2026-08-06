<template>
  <div v-if="totalPages > 1" class="d-flex justify-content-center align-items-center gap-2 my-4">
    <button
      class="btn btn-outline-primary rounded-circle p-0 d-flex align-items-center justify-content-center"
      style="width: 40px; height: 40px;"
      :disabled="currentPage === 1"
      @click="$emit('page-change', currentPage - 1)"
    >
      <i class="bi bi-chevron-left"></i>
    </button>

    <button
      v-for="page in totalPages"
      :key="page"
      class="btn rounded-circle p-0 fw-bold d-flex align-items-center justify-content-center"
      style="width: 40px; height: 40px;"
      :class="page === currentPage ? 'btn-primary-custom text-white' : 'btn-white border-slate text-dark'"
      @click="$emit('page-change', page)"
    >
      {{ page }}
    </button>

    <button
      class="btn btn-outline-primary rounded-circle p-0 d-flex align-items-center justify-content-center"
      style="width: 40px; height: 40px;"
      :disabled="currentPage === totalPages"
      @click="$emit('page-change', currentPage + 1)"
    >
      <i class="bi bi-chevron-right"></i>
    </button>
  </div>
</template>

<script setup>
defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true }
})

defineEmits(['page-change'])
</script>

<style scoped>
.btn-white {
  background-color: #FFFFFF;
}
.border-slate {
  border: 1px solid #E2E8F0;
}
</style>