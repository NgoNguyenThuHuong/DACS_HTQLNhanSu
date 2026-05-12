# Hướng dẫn chi tiết mã nguồn HTQLNhanSu

Dưới đây là giải thích chức năng của từng file và thư mục trong dự án của bạn:

## 1. Thư mục gốc (Root)
- `index.php`: Trang Dashboad chính. Hiển thị thông tin thống kê khác nhau tùy theo vai trò (Admin, HR, hay Nhân viên).
- `login.php`: Xử lý đăng nhập và xác thực người dùng.
- `logout.php`: Đăng xuất và hủy phiên làm việc (session).
- `register.php`: Trang đăng ký tài khoản nhân viên mới.
- `profile.php`: Cho phép người dùng xem và cập nhật thông tin cá nhân.
- `database.sql`: File chứa cấu trúc cơ sở dữ liệu để nhập (import) vào MySQL.
- `README.md`: Hướng dẫn tổng quan về dự án.

## 2. Thư mục `setup/`
- Chứa các file cài đặt dữ liệu mẫu, công cụ sửa lỗi và kiểm tra hệ thống (`debug_db.php`, `setup_manager.php`, v.v.). Nên xóa hoặc bảo vệ thư mục này khi đưa ứng dụng lên môi trường thực tế.

## 3. Thư mục `config/`
- `database.php`: Chứa cấu hình kết nối PDO tới cơ sở dữ liệu MySQL và định nghĩa `BASE_URL`.
- `auth.php`: Các hàm tiện ích để kiểm tra trạng thái đăng nhập và phân quyền (`isAdmin`, `isHR`, v.v.).

## 3. Thư mục `includes/`
- `header.php`: Chứa các thẻ meta, link CSS và logic kiểm tra đăng nhập đầu mỗi trang.
- `footer.php`: Chứa các thẻ đóng HTML và script JS dùng chung.
- `sidebar.php`: Thanh menu bên trái, tự động thay đổi các mục menu dựa trên quyền của người dùng.

## 4. Thư mục `modules/` (Các chức năng chính)
- `admin/`: Quản lý tài khoản, phân quyền, sao lưu dữ liệu và xem log hệ thống.
- `employees/`: Quản lý hồ sơ nhân viên (Thêm, Sửa, Xóa, Xem chi tiết).
- `departments/`: Quản lý danh sách các phòng ban trong công ty.
- `attendance/`: Hệ thống chấm công (Người dùng tự chấm công hoặc Admin theo dõi).
- `leave/`: Quản lý đơn xin nghỉ phép và quy trình phê duyệt.
- `tasks/`: Quản lý và giao việc cho nhân viên.
- `reports/`: Xuất báo cáo hiệu suất và thống kê nhân sự.
- `ai_insight.php`: Logic xử lý dự báo rủi ro nghỉ việc bằng AI (dựa trên dữ liệu có sẵn).
- `dashboard_employee.php`: Giao diện Dashboard dành riêng cho nhân viên.

## 5. Thư mục `assets/`
- `css/style.css`: File định kiểu chính, chứa các hiệu ứng giao diện cao cấp (Glassmorphism, Blobs, v.v.).
- `js/`: Các file scripts xử lý logic giao diện phía người dùng.
- `img/`: Lưu trữ các hình ảnh tĩnh của hệ thống.
