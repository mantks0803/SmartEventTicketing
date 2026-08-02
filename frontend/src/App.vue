<template>
  <div class="d-flex flex-column min-vh-100">
    <AppNavbar />

    <main class="flex-grow-1">
      <router-view />
    </main>

    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from '@/components/AppNavbar.vue'
import AppFooter from '@/components/AppFooter.vue'
</script>