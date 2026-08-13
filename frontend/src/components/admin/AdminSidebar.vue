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

      <div class="admin-sidebar-divider">Chức năng sắp tới</div>

      <div
        v-for="item in upcomingItems"
        :key="item.title"
        class="admin-menu-item disabled"
        aria-disabled="true"
      >
        <span class="admin-menu-icon">
          <i :class="item.icon"></i>
        </span>
        <span>
          <strong>{{ item.title }}</strong>
          <small>{{ item.description }}</small>
          <span class="coming-soon-badge">Chưa triển khai</span>
        </span>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

// Các mục này chỉ hiển thị giao diện, chưa điều hướng hoặc gọi API.
const upcomingItems = [
  {
    title: 'Quản lý thanh toán',
    description: 'Đối soát và hoàn tiền',
    icon: 'bi bi-credit-card',
  },
  {
    title: 'Cấu hình hệ thống',
    description: 'Thiết lập chung',
    icon: 'bi bi-gear',
  },
]
</script>

<style scoped src="./AdminSidebar.css"></style>
