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
                <i class="bi bi-shield-check me-1"></i>
                Duyệt sự kiện
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
                      <i class="bi bi-shield-check me-2 text-primary"></i>
                      Duyệt sự kiện
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
    cancelButtonColor: '#64748B',
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

<style scoped>
.navbar-dark-theme {
  background-color: #0F172A;
  border-bottom: 1px solid #1E293B;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.logo-icon-bg {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-accent {
  color: #38BDF8;
}

.text-slate-light {
  color: #CBD5E1 !important;
}

.text-slate-light:hover {
  color: #FFFFFF !important;
}

.search-box-dark {
  padding: 2px 12px;
  border: 1px solid #334155;
  border-radius: 9999px;
  background-color: #1E3A5F;
}

.search-input::placeholder {
  color: #CBD5E1;
  font-size: 0.9rem;
}

.search-input:focus {
  box-shadow: none;
}

.text-cyan {
  color: #38BDF8 !important;
  border-color: #38BDF8 !important;
}

.text-cyan:hover {
  background-color: #38BDF8 !important;
  color: #0F172A !important;
}

.dropdown-menu {
  right: 0;
  top: calc(100% + 8px);
  min-width: 220px;
}

.dropdown-item {
  white-space: nowrap;
}

.dropdown-item:active {
  background-color: #EFF6FF;
  color: #0F172A;
}

.user-avatar {
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.fw-extrabold {
  font-weight: 800;
}

.cursor-pointer {
  cursor: pointer;
}

@media (max-width: 991px) {
  .dropdown-menu {
    position: static !important;
    margin-top: 8px;
  }

  .nav-item .btn {
    width: 100%;
  }
}
</style>
