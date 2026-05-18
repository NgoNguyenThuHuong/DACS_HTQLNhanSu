# Bản đồ Chỉ dẫn Mã nguồn Hệ thống HTQLNhanSu

Tài liệu này cung cấp bản đồ chi tiết và giải thích chức năng của từng thư mục, tệp tin trong hệ thống **HTQLNhanSu** sau khi đã được tái cấu trúc sang kiến trúc **Modular Monolith & Clean Architecture**.

---

## 1. Thư mục cốt lõi `app/` (Gói ứng dụng chính)

Đây là nơi chứa toàn bộ mã nguồn nghiệp vụ của hệ thống, được phân chia theo các phân tầng quy chuẩn:

* **`app/__init__.py`**: Entrypoint chính của Flask App Factory. Thực hiện khởi tạo cấu hình, kết nối cơ sở dữ liệu (`SQLAlchemy`), đăng ký tất cả Blueprints/Routes và cấu hình hệ thống quản lý đăng nhập.
* **`app/core/` (Phân tầng Core Utilities)**:
  * `config.py`: Định nghĩa tất cả các thông số cấu hình môi trường, thư mục tải lên (upload) và SMTP cấu hình email.
  * `decorators.py`: Chứa các decorators phân quyền truy cập hệ thống như `@hr_required` và `@admin_required`.
  * `exceptions.py`: Định nghĩa các lỗi hệ thống chuẩn hóa như `ValidationError`.
  * `cache.py`: Lớp trừu tượng hóa bộ nhớ đệm (Caching Abstraction) hỗ trợ Redis hoặc In-memory Cache.
  * `ai_audit.py`: Trình ghi log kiểm định AI (Inference Audit Logging) lưu trữ dưới dạng định dạng `.jsonl`.
* **`app/dtos/` (Data Transfer Objects)**:
  * `dtos.py`: Chứa các DTOs chuẩn hóa dữ liệu đầu ra cho giao diện UI như `PerformanceDTO`, `RetentionRecommendationDTO`.
  * `dtos_ai.py`: Định nghĩa cấu hình dữ liệu phục vụ Explainable AI Dashboard (`EmployeeAIDashboardDTO`).
* **`app/models/` (Data Access Domain Models)**:
  * `models.py`: Định nghĩa tất cả các bảng dữ liệu SQLAlchemy (ORM) như `Employee`, `Attendance`, `JobPost`, `Candidate`, `Task`...
* **`app/repositories/` (Phân tầng Repositories - Data Access)**:
  * `employee_repo.py`: Tập hợp các truy vấn ORM tối ưu liên quan đến nhân sự.
  * `attendance_repo.py`: Các xử lý liên quan đến chấm công, đi muộn, chuyên cần.
  * `hr_repo.py`: Quản lý truy vấn liên quan đến đơn nghỉ phép, công việc, tuyển dụng.
  * `analytics_repo.py`: Xử lý tổng hợp các chỉ số KPI, hiệu suất, Radar Chart.
  * `ai_repo.py`: Tối ưu hóa truy vấn tổng hợp hiệu suất và thông tin phục vụ dự đoán ML.
* **`app/services/` (Phân tầng Service Layer - Business Logic)**:
  * `auth_service.py`: Xử lý đăng ký, đăng nhập mã hóa bảo mật.
  * `employee_service.py`: Nghiệp vụ hồ sơ, cập nhật thông tin cá nhân.
  * `attendance_service.py`: Nghiệp vụ chấm công tích hợp OpenCV xử lý ảnh khuôn mặt và mã QR.
  * `hr_service.py`: Nghiệp vụ duyệt đơn phép, phân tải công việc, thống kê.
  * `analytics_service.py`: Tính toán hiệu suất cá nhân và tổng hợp Radar Chart toàn hệ thống.
  * `ai_service.py`: Điều phối luồng dự báo rủi ro nghỉ việc realtime, SHAP XAI và Recommendation Engine.
  * `email_service.py`: Tự động gửi email chúc mừng trúng tuyển hoặc thông báo ứng viên.
* **`app/routes/` (Presentation Layer - Controllers)**:
  * `auth.py`: Controller xử lý đăng nhập, đăng ký và đăng xuất phía client.
  * `main.py`: Trang Dashboard chính của hệ thống.
  * `employee.py`: Giao diện dành riêng cho nhân viên.
  * `attendance.py`: Xử lý camera check-in khuôn mặt, QR code.
  * `hr.py`: Giao diện quản lý, duyệt phép, Kanban Task dành cho HR/Admin.
  * `recruitment.py`: Cổng thông tin tuyển dụng, nộp hồ sơ trực tuyến, làm bài thi MCQ.
  * `ai_dashboard.py`: Cung cấp các RESTful APIs suy luận và Explainable AI Dashboard.
* **`app/ai_engine/` (AI & Machine Learning Core)**:
  * `analytics/`: Các thuật toán heuristic, rule-based thống kê dữ liệu.
  * `ml/training/`: Dataset builder sinh dữ liệu huấn luyện cân bằng (synthetic data), offline pipeline huấn luyện XGBoost và bộ đánh giá mô hình (`evaluation.py`).
  * `ml/inference/`: Bộ dự báo realtime (`turnover_predictor.py`), bộ giải thích XAI (`shap_explainer.py`) và bộ khuyến nghị (`recommender.py`).
  * `ml/models/`: Chứa mô hình đã được huấn luyện sẵn `xgboost_attrition_v1.bin` và file nhật ký kiểm định `ai_inference_audit.jsonl`.

---

## 2. Thư mục và Tệp tin Hỗ trợ ở thư mục gốc (Root)

* **`run.py`**: Điểm khởi chạy ứng dụng chính của toàn hệ thống Flask.
* **`setup_db.py`**: Script tự động tạo bảng, thiết lập quan hệ và khởi tạo dữ liệu mẫu cho CSDL MySQL.
* **`database.sql`**: Bản sao lưu cấu trúc database thuần MySQL.
* **`tkmk.txt`**: Lưu trữ danh sách tài khoản, mật khẩu kiểm thử mặc định của hệ thống.
* **`requirements.txt`**: Định nghĩa danh sách các thư viện Python cần cài đặt.
* **`static/`**: Chứa các file tĩnh dùng chung (CSS định kiểu cao cấp, Javascript xử lý camera/Chart.js và hình ảnh).
* **`templates/`**: Chứa toàn bộ giao diện HTML động của Flask (`Jinja2 templates`).

---

## 3. Các Lớp Tương Thích Ngược (Backward Compatibility Adapters)

Để bảo đảm hệ thống cũ vẫn có thể tích hợp bình thường, các file sau ở thư mục gốc hoạt động như adapter chuyển tiếp import trực tiếp vào phân tầng mới của `app/`:
* `models.py` -> Liên kết tới `app.models`
* `auth.py` -> Liên kết tới `app.routes.auth`
* `config.py` -> Liên kết tới `app.core.config`
* `email_service.py` -> Liên kết tới `app.services.email_service`
* `analytics.py` -> Liên kết tới `app.services.analytics_service`
* `core/` -> Forward sang `app.core/`
* `services/` -> Forward sang `app.services/`
* `repositories/` -> Forward sang `app.repositories/`
* `routes/` -> Forward sang `app.routes/`
* `ai_engine/` -> Forward sang `app.ai_engine/`
