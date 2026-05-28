# Báo Cáo Đánh Giá An Toàn Bảo Mật (Security Hardening Assessment Report)

Báo cáo này tập trung phân tích các rủi ro bảo mật tiềm ẩn trong mã nguồn hiện tại của hệ thống **HTQLNhanSu** và đề xuất giải pháp khắc phục chi tiết để đạt chuẩn doanh nghiệp (Enterprise-grade security).

---

## 1. Danh Sách Lỗ Hổng Bảo Mật Phát Hiện (Vulnerability Log)

Dựa trên phân tích mã nguồn tĩnh (SAST), chúng tôi phát hiện một số điểm yếu bảo mật nghiêm trọng:

### 🚨 LỖ HỔNG 1: Lưu trữ mật khẩu dạng văn bản thuần (Plain-text Password Storage) - Mức độ: NGUY HIỂM (CRITICAL)

* **Vị trí mã nguồn**: [auth_service.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/services/auth_service.py#L24-L38)
* **Chi tiết kỹ thuật**:
  ```python
  new_user = Employee(
      username=username,
      password=password, # Plain text theo yêu cầu hệ thống cũ
      ...
  )
  ```
* **Rủi ro**: Nếu cơ sở dữ liệu MySQL bị lộ lọt (SQL Injection hoặc lộ file backup), toàn bộ mật khẩu của nhân viên, quản trị viên và nhân sự (HR) sẽ bị hacker chiếm đoạt ngay lập tức mà không cần giải mã. Hacker có thể sử dụng thông tin này để đăng nhập vào các hệ thống khác của doanh nghiệp (Credential Stuffing).

---

### ⚠️ LỖ HỔNG 2: Thiếu Token CSRF cho các yêu cầu POST/API (Missing CSRF Protection) - Mức độ: CAO (HIGH)

* **Vị trí mã nguồn**: Các API endpoints và các form nhập liệu trong `templates/`.
* **Chi tiết kỹ thuật**: Hệ thống sử dụng Flask thông thường nhưng chưa kích hoạt tiện ích mở rộng `Flask-WTF` hoặc `SeaSurf` để tự động đính kèm và xác thực mã thông báo CSRF (Cross-Site Request Forgery) trên mỗi yêu cầu thay đổi trạng thái (POST, PUT, DELETE).
* **Rủi ro**: Kẻ tấn công có thể lừa người dùng (đặc biệt là HR hoặc Admin đang đăng nhập) nhấp vào một liên kết độc hại, từ đó tự động gửi yêu cầu phê duyệt nghỉ phép khống hoặc thay đổi mức lương của nhân viên.

---

### ℹ️ LỖ HỔNG 3: Cấu hình phiên làm việc lỏng lẻo (Weak Session Management) - Mức độ: TRUNG BÌNH (MEDIUM)

* **Vị trí mã nguồn**: [__init__.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/__init__.py) và `Config`.
* **Chi tiết kỹ thuật**:
  * Chưa cấu hình thời gian hết hạn phiên làm việc cụ thể (`PERMANENT_SESSION_LIFETIME`). Phiên đăng nhập mặc định có thể tồn tại quá lâu.
  * Chưa thiết lập các cờ bảo mật cho session cookie như `SESSION_COOKIE_SECURE=True` (chỉ gửi qua HTTPS) và `SESSION_COOKIE_HTTPONLY=True` (ngăn Javascript truy cập cookie để phòng chống Session Hijacking qua XSS).

---

## 2. Đánh Giá Cơ Chế Phân Quyền Vai Trò (Role-Based Access Control - RBAC)

Hệ thống đã triển khai các decorator phân quyền rất tốt tại `app/core/decorators.py`:
* `@hr_required`: Ngăn nhân viên thường truy cập các tài nguyên quản lý của HR.
* `@admin_required`: Giới hạn các tính năng cấu hình hệ thống chỉ dành riêng cho Admin.

> [!TIP]
> **Điểm cộng**: Cơ chế decorator này được áp dụng nhất quán trên các routes tại `app/routes/hr.py` và `app/routes/ai_dashboard.py`, giúp ngăn chặn hiệu quả lỗi **Bypassing Authorization** (Broken Object Level Authorization).

---

## 3. Kế Hoạch Khắc Phục & Tối Ưu Bảo Mật (Security Hardening Plan)

Để đảm bảo hệ thống đạt độ tin cậy tuyệt đối, chúng tôi đề xuất triển khai các nâng cấp sau:

```diff
# Giải pháp khắc phục plain-text password sử dụng Werkzeug Security Hashing
- password=password, # Plain text theo yêu cầu hệ thống cũ
+ password=generate_password_hash(password, method='scrypt'),
```

1. **Băm mật khẩu (Password Hashing)**:
   * Sử dụng thư viện bảo mật mặc định `werkzeug.security` tích hợp sẵn trong Flask với hàm `generate_password_hash` và `check_password_hash`.
2. **Kích hoạt Flask-WTF CSRF**:
   * Cài đặt `Flask-WTF` và khởi tạo `CSRFProtect(app)` trong `create_app()` để bảo vệ toàn bộ các form nhập liệu và API endpoints.
3. **Cấu hình Cookie Bảo Mật**:
   * Thiết lập cấu hình môi trường sản xuất:
     ```python
     SESSION_COOKIE_HTTPONLY = True
     SESSION_COOKIE_SECURE = True  # Yêu cầu HTTPS
     SESSION_COOKIE_SAMESITE = 'Lax'
     PERMANENT_SESSION_LIFETIME = 1800  # Tự động đăng xuất sau 30 phút không hoạt động
     ```
