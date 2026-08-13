<template>
  <div class="admin-sidebar">
    <div class="admin-sidebar-heading">
      <div class="admin-sidebar-icon">
        <i class="bi bi-speedometer2"></i>
      </div>

      <div>
        <h5 class="mb-1">Quản trị hệ thống</h5>
        <small>Chọn chức năng quản lý</small>
      </div>
    </div>

    <nav class="admin-sidebar-menu" aria-label="Chức năng quản trị">
      <RouterLink
        :to="{ name: 'admin-events' }"
        class="admin-menu-item"
        :class="{ active: route.name === 'admin-events' }"
      >
        <span class="admin-menu-icon">
          <i class="bi bi-calendar2-check"></i>
        </span>
        <span>
          <strong>Duyệt sự kiện</strong>
          <small>Kiểm tra sự kiện mới</small>
        </span>
        <i class="bi bi-chevron-right admin-menu-arrow"></i>
      </RouterLink>

      <RouterLink
        :to="{ name: 'admin-revenue-report' }"
        class="admin-menu-item"
        :class="{ active: route.name === 'admin-revenue-report' }"
      >
        <span class="admin-menu-icon">
          <i class="bi bi-bar-chart-line"></i>
        </span>
        <span>
          <strong>Báo cáo doanh thu</strong>
          <small>Thống kê toàn hệ thống</small>
        </span>
        <i class="bi bi-chevron-right admin-menu-arrow"></i>
      </RouterLink>

      <RouterLink
        :to="{ name: 'admin-users' }"
        class="admin-menu-item"
        :class="{ active: route.name === 'admin-users' }"
      >
        <span class="admin-menu-icon">
          <i class="bi bi-people"></i>
        </span>
        <span>
          <strong>Quản lý người dùng</strong>
          <small>Tài khoản và trạng thái</small>
        </span>
        <i class="bi bi-chevron-right admin-menu-arrow"></i>
      </RouterLink>

      <RouterLink
        :to="{ name: 'admin-payments' }"
        class="admin-menu-item"
        :class="{ active: route.name === 'admin-payments' }"
      >
        <span class="admin-menu-icon">
          <i class="bi bi-credit-card"></i>
        </span>
        <span>
          <strong>Quản lý thanh toán</strong>
          <small>Giao dịch và đối soát</small>
        </span>
        <i class="bi bi-chevron-right admin-menu-arrow"></i>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped src="./AdminSidebar.css"></style>
