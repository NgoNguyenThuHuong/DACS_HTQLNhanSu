# Tài liệu chi tiết Đồ án: Hệ thống Quản lý Nhân sự Thông minh (HTQLNhanSu)

## 1. Giới thiệu tổng quan
Dự án **HTQLNhanSu** là một hệ thống quản trị nhân sự hiện đại, được thiết kế để tự động hóa các quy trình quản lý trong doanh nghiệp. Hệ thống không chỉ tập trung vào việc lưu trữ hồ sơ mà còn cung cấp các công cụ phân tích thông minh và giao diện trải nghiệm người dùng cao cấp.

## 2. Các chức năng chính
Hệ thống được phân quyền chặt chẽ với 3 vai trò chính:

### Đối với Quản trị viên (Admin)
- **Quản trị toàn diện**: Quản lý tài khoản người dùng, phân quyền truy cập hệ thống.
- **Kiểm soát hạ tầng**: Theo dõi logs hệ thống, thực hiện sao lưu (backup) dữ liệu.
- **Quản lý cốt lõi**: Quản lý danh sách nhân viên và cơ cấu phòng ban toàn công ty.

### Đối với Giám đốc / HR (Human Resources)
- **Phê duyệt nghỉ phép**: Quy trình duyệt đơn xin nghỉ phép trực tuyến nhanh chóng.
- **Giám sát chấm công**: Theo dõi hoạt động hiện diện của nhân viên theo thời gian thực.
- **AI Analytics**: Sử dụng trí tuệ nhân tạo để dự báo nguy cơ nghỉ việc dựa trên hiệu suất và chuyên cần.
- **Báo cáo thống kê**: Xuất các báo cáo hiệu suất và thống kê nhân sự chi tiết.

### Đối với Nhân viên (Employee)
- **Tự chấm công**: Chấm công hàng ngày dễ dàng qua giao diện web.
- **Quản lý nghỉ phép**: Gửi đơn xin nghỉ phép và theo dõi trạng thái phê duyệt.
- **Quản lý công việc**: Theo dõi các nhiệm vụ (tasks) được giao và cập nhật tiến độ.
- **Hồ sơ cá nhân**: Tự quản lý và cập nhật thông tin cá nhân của mình.

## 3. Công nghệ sử dụng
- **Ngôn ngữ**: PHP (Backend), JavaScript (Frontend logic).
- **Cơ sở dữ liệu**: MySQL (Sử dụng PDO để đảm bảo bảo mật và hiệu năng).
- **Giao diện**: Bootstrap 5, Font Awesome, Google Fonts, Chart.js (biểu đồ sinh động).
- **Phong cách thiết kế**: Glassmorphism (hiệu ứng kính), Modern Minimalist với các hiệu ứng Blobs động.

## 4. Hướng dẫn cài đặt
1. **Môi trường**: Khuyến nghị sử dụng Laragon hoặc XAMPP (PHP 7.4+).
2. **Database**: Tạo database có tên `ql_nhansu` và import file `database.sql` vào MySQL.
3. **Cấu hình**: Chỉnh sửa thông tin kết nối DB trong `config/database.php` nếu cần.
4. **Truy cập**: Truy cập qua trình duyệt với URL: `http://localhost/HTQLNhanSu/`.

## 5. Điểm nổi bật của đồ án
- **Giao diện chuẩn Premium**: Sử dụng các kỹ thuật CSS hiện đại mang lại cảm giác chuyên nghiệp.
- **Tính năng AI**: Dự báo thông minh giúp bộ phận HR có cái nhìn chủ động về tình hình nhân sự.
- **Thiết kế Responsive**: Hoạt động mượt mà trên cả máy tính và thiết bị di động.
