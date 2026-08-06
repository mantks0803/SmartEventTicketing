<template>
  <footer class="footer-dark border-top-slate mt-auto">
    <div class="container py-5">
      <div class="row g-4">
        <div class="col-lg-4 col-md-6">
          <div class="d-flex align-items-center gap-2 fw-extrabold fs-4 text-white mb-3">
            <div class="logo-icon-bg">
              <i class="bi bi-ticket-perforated-fill fs-4 text-white"></i>
            </div>
            <span>Smart<span class="text-accent">Ticket</span></span>
          </div>
          <p class="text-slate-muted small lh-lg pe-lg-4">
            Nền tảng đặt vé sự kiện, concert âm nhạc và workshop hàng đầu Việt Nam. Trải nghiệm mua vé nhanh chóng, bảo mật tuyệt đối với mã VietQR PayOS và vé điện tử QR Code.
          </p>
        </div>

        <div class="col-lg-2 col-md-6">
          <h6 class="fw-bold text-white mb-3">Về chúng tôi</h6>
          <ul class="list-unstyled text-slate-muted small d-flex flex-column gap-2.5">
            <li><a href="#" class="footer-link">Giới thiệu SmartTicket</a></li>
            <li><a href="#" class="footer-link">Điều khoản sử dụng</a></li>
            <li><a href="#" class="footer-link">Chính sách bảo mật</a></li>
            <li><a href="#" class="footer-link">Quy chế hoạt động</a></li>
          </ul>
        </div>

        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold text-white mb-3">Liên hệ hỗ trợ</h6>
          <div class="d-flex flex-column gap-2 text-slate-muted small">
            <p class="mb-0"><i class="bi bi-geo-alt text-primary me-2"></i>TP. Hồ Chí Minh, Việt Nam</p>
            <p class="mb-0"><i class="bi bi-envelope text-primary me-2"></i>hotro@smartticket.vn</p>
            <p class="mb-0"><i class="bi bi-telephone text-primary me-2"></i>1900 1234 (8:00 - 21:00)</p>
          </div>
        </div>

        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold text-white mb-3">Thanh toán an toàn</h6>
          <div class="d-flex gap-2 align-items-center mb-3">
            <span class="badge bg-payos fs-6 px-3 py-2">PayOS</span>
            <span class="badge bg-vietqr fs-6 px-3 py-2">VietQR</span>
          </div>
          <small class="text-slate-muted d-block">Hỗ trợ tất cả ngân hàng nội địa và ứng dụng Mobile Banking.</small>
        </div>
      </div>
    </div>

    <div class="footer-bottom py-3 border-top-slate-subtle">
      <div class="container text-center text-slate-muted small">
        © 2026 SmartTicket System. Tất cả quyền được bảo lưu.
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer-dark {
  background-color: #0F172A;
  color: #94A3B8;
}

.border-top-slate {
  border-top: 1px solid #1E293B;
}

.border-top-slate-subtle {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.text-slate-muted {
  color: #94A3B8;
}

.footer-link {
  color: #94A3B8;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #38BDF8;
}

.logo-icon-bg {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-accent {
  color: #38BDF8;
}

.bg-payos {
  background-color: #2563EB;
  color: #FFFFFF;
  font-weight: 700;
}

.bg-vietqr {
  background-color: #059669;
  color: #FFFFFF;
  font-weight: 700;
}

.fw-extrabold {
  font-weight: 800;
}
</style>