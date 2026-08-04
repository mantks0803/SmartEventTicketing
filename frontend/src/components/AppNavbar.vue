<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm py-2">
    <div class="container">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand d-flex align-items-center gap-2 fw-bold fs-4">
        <i class="bi bi-ticket-perforated-fill text-primary-color fs-3"></i>
        <span>Smart<span class="text-primary-color">Ticket</span></span>
      </router-link>

      <!-- Toggle Button cho Mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Content -->
      <div class="collapse navbar-collapse" id="navbarContent">
        <!-- Ô Tìm kiếm nhanh phong cách Ticketbox -->
        <form class="d-flex mx-auto my-2 my-lg-0 w-50" @submit.prevent>
          <div class="input-group">
            <span class="input-group-text bg-secondary border-secondary text-light">
              <i class="bi bi-search"></i>
            </span>
            <input
              type="text"
              class="form-control bg-secondary text-light border-secondary placeholder-light"
              placeholder="Tìm kiếm sự kiện, ca sĩ, địa điểm..."
            />
          </div>
        </form>

        <!-- Dynamic Menu bên phải -->
        <ul class="navbar-nav ms-auto align-items-lg-center gap-2">
          <li class="nav-item">
            <router-link to="/" class="nav-link text-light">Vé của tôi</router-link>
          </li>

          <!-- Khi chưa đăng nhập -->
          <template v-if="!authStore.isAuthenticated">
            <li class="nav-item">
              <router-link to="/login" class="btn btn-outline-light btn-sm px-3 rounded-pill"
                >Đăng nhập</router-link
              >
            </li>
            <li class="nav-item">
              <router-link to="/register" class="btn btn-primary btn-sm px-3 rounded-pill"
                >Đăng ký</router-link
              >
            </li>
          </template>

          <!-- Khi đã đăng nhập -->
          <template v-else>
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle text-light d-flex align-items-center gap-2"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-person-circle fs-5 text-primary-color"></i>
                <span>{{ authStore.user?.name || 'Tài khoản' }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow">
                <!-- Menu riêng cho Khách hàng -->
                <template v-if="authStore.isCustomer">
                  <li>
                    <router-link to="/my-tickets" class="dropdown-item">
                      <i class="bi bi-wallet2 me-2"></i>Ví vé của tôi
                    </router-link>
                  </li>
                  <li>
                    <router-link to="/my-orders" class="dropdown-item">
                      <i class="bi bi-receipt me-2"></i>Lịch sử đơn hàng
                    </router-link>
                  </li>
                </template>

                <!-- Menu riêng cho Ban tổ chức -->
                <template v-if="authStore.isOrganizer">
                  <li>
                    <router-link to="/organizer/dashboard" class="dropdown-item">
                      <i class="bi bi-speedometer2 me-2"></i>Dashboard Thống kê
                    </router-link>
                  </li>
                  <li>
                    <router-link to="/organizer/check-in" class="dropdown-item">
                      <i class="bi bi-qr-code-scan me-2"></i>Máy quét QR Soát vé
                    </router-link>
                  </li>
                  <li>
                    <router-link to="/organizer/create-event" class="dropdown-item">
                      <i class="bi bi-plus-circle me-2"></i>Tạo sự kiện mới
                    </router-link>
                  </li>
                </template>

                <li><hr class="dropdown-divider" /></li>
                <li>
                  <button @click="handleLogout" class="dropdown-item text-danger">
                    <i class="bi bi-box-arrow-right me-2"></i>Đăng xuất
                  </button>
                </li>
              </ul>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>