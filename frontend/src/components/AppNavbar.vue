<template>
  <nav class="navbar navbar-expand-lg sticky-top py-3 navbar-dark-theme">
    <div class="container">
      <router-link
        to="/"
        class="navbar-brand d-flex align-items-center gap-2 fw-extrabold fs-4 text-white"
      >
        <div class="logo-icon-bg">
          <i class="bi bi-ticket-perforated-fill fs-4 text-white"></i>
        </div>

        <span>
          Smart<span class="text-accent">Ticket</span>
        </span>
      </router-link>

      <div
        class="d-none d-md-flex flex-grow-1 mx-4"
        style="max-width: 420px"
      >
        <div class="input-group search-box-dark">
          <span class="input-group-text bg-transparent border-0 text-slate">
            <i class="bi bi-search"></i>
          </span>

          <input
            v-model="searchQuery"
            type="text"
            class="form-control bg-transparent border-0 text-white ps-0 search-input"
            placeholder="Tìm kiếm sự kiện, ca sĩ, địa điểm..."
            @keyup.enter="handleSearch"
          />
        </div>
      </div>

      <button
        class="navbar-toggler border-0 text-white"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
        aria-controls="navbarContent"
        aria-expanded="false"
        aria-label="Mở menu"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="navbarContent" class="collapse navbar-collapse">
        <ul
          class="navbar-nav ms-auto align-items-lg-center gap-2 mt-3 mt-lg-0"
        >
          <li class="nav-item">
            <router-link
              to="/"
              class="nav-link text-slate-light fw-medium"
            >
              Sự kiện
            </router-link>
          </li>

          <template v-if="!authStore.isAuthenticated">
            <li class="nav-item">
              <router-link
                to="/login"
                class="btn btn-outline-light rounded-pill btn-sm px-3 ms-lg-2"
              >
                Đăng nhập
              </router-link>
            </li>

            <li class="nav-item">
              <router-link
                to="/register"
                class="btn btn-cta rounded-pill btn-sm px-3"
              >
                Đăng ký
              </router-link>
            </li>
          </template>

          <template v-else>
            <li v-if="authStore.isCustomer" class="nav-item">
              <router-link
                to="/my-tickets"
                class="nav-link text-slate-light fw-medium"
              >
                <i class="bi bi-ticket-detailed me-1"></i>
                Vé của tôi
              </router-link>
            </li>

            <template v-if="authStore.isOrganizer">
              <li class="nav-item">
                <router-link
                  to="/organizer/events/create"
                  class="btn btn-cta btn-sm rounded-pill px-3 ms-lg-2"
                >
                  <i class="bi bi-plus-lg me-1"></i>
                  Tạo sự kiện
                </router-link>
              </li>

              <li class="nav-item">
                <router-link
                  to="/organizer/dashboard"
                  class="btn btn-outline-info text-cyan btn-sm rounded-pill px-3"
                >
                  <i class="bi bi-speedometer2 me-1"></i>
                  Quản lý
                </router-link>
              </li>
            </template>

            <li v-if="authStore.isAdmin" class="nav-item">
              <router-link
                to="/admin/events"
                class="btn btn-outline-info text-cyan btn-sm rounded-pill px-3 ms-lg-2"
              >
                <i class="bi bi-speedometer2 me-1"></i>
                Quản trị
              </router-link>
            </li>

            <li
              ref="dropdownContainerRef"
              class="nav-item dropdown ms-lg-2 position-relative"
            >
              <a
                href="#"
                role="button"
                class="nav-link dropdown-toggle text-white d-flex align-items-center gap-2 cursor-pointer"
                @click.prevent="toggleDropdown"
              >
                <img
                  :src="authStore.user?.avatar || defaultAvatar"
                  alt="Ảnh đại diện"
                  class="rounded-circle object-fit-cover user-avatar"
                  width="32"
                  height="32"
                />

                <span class="fw-semibold fs-6">
                  {{ authStore.user?.name || 'Tài khoản' }}
                </span>
              </a>

              <ul
                class="dropdown-menu dropdown-menu-end rounded-xl border-0 shadow-lg py-2 position-absolute"
                :class="{ show: isDropdownOpen }"
              >
                <li v-if="!authStore.isAdmin">
                  <router-link
                    to="/profile"
                    class="dropdown-item py-2 fs-6"
                    @click="closeDropdown"
                  >
                    <i class="bi bi-person-circle me-2 text-primary"></i>
                    Hồ sơ của tôi
                  </router-link>
                </li>

                <template v-if="authStore.isCustomer">
                  <li>
                    <router-link
                      to="/my-tickets"
                      class="dropdown-item py-2 fs-6"
                      @click="closeDropdown"
                    >
                      <i class="bi bi-wallet2 me-2 text-primary"></i>
                      Ví vé của tôi
                    </router-link>
                  </li>
                </template>

                <template v-if="authStore.isOrganizer">
                  <li>
                    <router-link
                      to="/organizer/events/create"
                      class="dropdown-item py-2 fs-6"
                      @click="closeDropdown"
                    >
                      <i class="bi bi-plus-circle me-2 text-primary"></i>
                      Tạo sự kiện
                    </router-link>
                  </li>

                  <li>
                    <router-link
                      to="/organizer/dashboard"
                      class="dropdown-item py-2 fs-6"
                      @click="closeDropdown"
                    >
                      <i class="bi bi-speedometer2 me-2 text-primary"></i>
                      Quản lý sự kiện
                    </router-link>
                  </li>
                </template>

                <template v-if="authStore.isAdmin">
                  <li>
                    <router-link
                      to="/admin/events"
                      class="dropdown-item py-2 fs-6"
                      @click="closeDropdown"
                    >
                      <i class="bi bi-speedometer2 me-2 text-primary"></i>
                      Quản trị
                    </router-link>
                  </li>
                </template>

                <li>
                  <hr class="dropdown-divider my-1" />
                </li>

                <li>
                  <button
                    type="button"
                    class="dropdown-item text-danger py-2 fs-6"
                    @click="handleLogout"
                  >
                    <i class="bi bi-box-arrow-right me-2"></i>
                    Đăng xuất
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
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const isDropdownOpen = ref(false)
const dropdownContainerRef = ref(null)

const defaultAvatar =
  'https://res.cloudinary.com/dmhnfoc9i/image/upload/v1777361181/tickethub_avatars/btsrovtumjgqlaharj2r.jpg'

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleClickOutside = (event) => {
  if (
    dropdownContainerRef.value
    && !dropdownContainerRef.value.contains(event.target)
  ) {
    closeDropdown()
  }
}

const handleSearch = () => {
  const keyword = searchQuery.value.trim()

  if (!keyword) return

  router.push({
    name: 'home',
    query: {
      search: keyword
    }
  })
}

const handleLogout = async () => {
  closeDropdown()

  const result = await Swal.fire({
    title: 'Xác nhận đăng xuất',
    text: 'Bạn có chắc chắn muốn đăng xuất khỏi ứng dụng?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Đăng xuất',
    cancelButtonText: 'Hủy',
    confirmButtonColor: '#EF4444',
    cancelButtonColor: '#6F7976',
    customClass: {
      popup: 'rounded-4'
    }
  })

  if (!result.isConfirmed) return

  authStore.logout()

  await Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: 'Đã đăng xuất thành công',
    showConfirmButton: false,
    timer: 2000,
    timerProgressBar: true
  })

  router.push('/')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped src="./AppNavbar.css"></style>
