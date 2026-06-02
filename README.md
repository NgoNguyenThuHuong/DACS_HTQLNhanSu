# Hệ thống Quản lý Nhân sự Thông minh (HTQLNhanSu AI-HRM)

Hệ thống HTQLNhanSu AI-HRM là một nền tảng quản trị nhân sự hiện đại được xây dựng trên ngôn ngữ **Python** bằng **Flask Framework**, tuân thủ nghiêm ngặt mô hình kiến trúc **Modular Monolith** kết hợp **Clean Architecture** và cấu trúc **AI-Ready Architecture**. 

Hệ thống tích hợp các mô hình Machine Learning tiên tiến (XGBoost) kết hợp Explainable AI (SHAP) để dự đoán realtime và giải thích lý do nguy cơ nghỉ việc của nhân sự, đồng thời tích hợp Hệ thống khuyến nghị thông minh hỗ trợ bộ phận quản lý (HR) đưa ra quyết định tối ưu.

---

## 1. Bản đồ Kiến trúc Hệ thống

Hệ thống được tổ chức thành các phân tầng rõ ràng nhằm đảm bảo tính độc lập, dễ mở rộng và dễ bảo trì:

```text
Presentation Layer (Flask Blueprints/Routes)
         │
         ▼
Application Service Layer (Business Orchestration Services)
         │
   ┌─────┴─────────────────────────────────────┐
   ▼                                           ▼
Domain / AI Layer (XGBoost, SHAP Engine)   Data Access Layer (Repository Pattern)
                                               │
                                               ▼
                                           SQLAlchemy Models (MySQL)
```

---

## 2. Các Phân Hệ Tính Năng Chính

Hệ thống phân quyền chặt chẽ theo 3 nhóm đối tượng sử dụng:

### 💼 Đối với Quản trị viên (Admin)
- **Quản trị hệ thống**: Quản lý tài khoản, cấp quyền truy cập, giám sát nhật ký bảo mật hệ thống.
- **Quản lý cốt lõi**: Khởi tạo, theo dõi cấu trúc phòng ban và toàn bộ thông tin cơ cấu nhân sự.

### 📊 Đối với Bộ phận Nhân sự (HR Specialist / Manager)
- **Explainable AI (XAI) Dashboard**: Xem phân tích thời gian thực về rủi ro nghỉ việc của nhân viên, biểu đồ SHAP đóng góp biên trị, biểu đồ Radar năng lực cá nhân.
- **Hệ khuyến nghị thông minh (Retention Recommendation)**: Nhận các đề xuất hành động thực tiễn (ưu tiên Cao/Trung bình) để giảm thiểu tỷ lệ nghỉ việc.
- **Giám sát Chuyên cần & Công việc**: Quản lý chấm công bằng khuôn mặt (OpenCV), duyệt đơn nghỉ phép linh hoạt và phân bổ công việc.
- **Quản lý Tuyển dụng (Recruitment & ATS)**: Quản lý đăng tuyển (Job Posts), quản lý ứng viên (Candidates), thiết lập bộ đề thi đánh giá năng lực ứng viên (Exams) tự động chấm điểm.

### 👤 Đối với Nhân viên (Employee)
- **Check-in thông minh**: Điểm danh hàng ngày bằng nhận diện khuôn mặt hoặc mã QR bảo mật.
- **Quản lý công việc & Nghỉ phép**: Theo dõi Kanban Task cá nhân, gửi đơn xin phép nghỉ và theo dõi tiến trình phê duyệt trực tuyến.

---

## 3. Công nghệ & Thư viện sử dụng

- **Backend Framework**: Python 3.10+ / Flask Framework
- **Database Access (ORM)**: SQLAlchemy / Flask-SQLAlchemy (MySQL)
- **Machine Learning & AI**: 
  - **XGBoost / Scikit-Learn**: Bộ phân loại dự đoán nguy cơ nghỉ việc (Attrition Classification).
  - **SHAP (Shapley Additive exPlanations)**: Giải thích quyết định mô hình hộp đen (Black-box Explanations).
- **Computer Vision**: OpenCV / Pillow (Xử lý ảnh & Nhận diện chấm công khuôn mặt).
- **Caching Layer**: Redis / In-memory Cache Abstraction
- **Frontend Layer**: Vanilla CSS (Premium Glassmorphism & Blobs design), Chart.js (Biểu đồ động).

---

## 4. Hướng dẫn Khởi chạy & Phát triển

### Bước 1: Chuẩn bị môi trường
1. Cài đặt Python (3.10 hoặc cao hơn).
2. Tạo và kích hoạt môi trường ảo:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Cài đặt các thư viện phụ thuộc:
   ```powershell
   pip install -r requirements.txt
   ```

### Bước 2: Thiết lập Cơ sở dữ liệu
1. Khởi chạy MySQL Server (Cổng mặc định: `3306`, ví dụ: qua Laragon hoặc XAMPP).
2. Tạo database tên `ql_nhansu`.
3. Nhập cơ sở dữ liệu mẫu:
   ```powershell
   python setup_db.py
   python seed_recruitment_data.py
   ```

### Bước 3: Khởi chạy Ứng dụng
Khởi chạy Flask server thông qua entrypoint chuẩn hóa:
```powershell
python run.py
```
Ứng dụng sẽ khả dụng tại địa chỉ: `http://127.0.0.1:5000/`.

---

## 5. Tài khoản Đăng nhập Mẫu (Mock Accounts)

Xem thông tin tài khoản demo chi tiết trong file `tkmk.txt`:
* **Admin**: `admin` / `123456`
* **HR Specialist**: `quanly` / `123456`
* **Employee**: `nhanvien` / `123456`

---

## 6. Cấu trúc Thư mục Chi tiết

Dự án được tổ chức theo **Clean Architecture** & **Modular Monolith**, phân tách rõ ràng tầng giao diện, logic nghiệp vụ, và tầng dữ liệu. Dưới đây là giải thích chi tiết chức năng của từng thư mục:

```text
DACS_HTQLNhanSu/
├── app/                        # 🌟 Mã nguồn chính của ứng dụng Flask
│   ├── ai/                     # Scripts hỗ trợ kỹ thuật trích xuất đặc trưng và huấn luyện mô hình AI
│   ├── ai_engine/              # Động cơ Trí tuệ Nhân tạo cốt lõi (Inference Engine)
│   │   ├── analytics/          # Xử lý tính toán, phân tích số liệu HR nâng cao (Metrics, Scoring)
│   │   ├── ml/                 # Chứa bộ nội suy dự đoán (XGBoost), công cụ giải thích SHAP và dữ liệu mẫu
│   │   └── utils/              # Các hàm tiện ích dùng chung cho AI engine
│   ├── core/                   # Tầng Core: Quản lý Caching, Bảo mật (Decorators), Xử lý Exception, Logging
│   ├── dtos/                   # Data Transfer Objects: Chuẩn hóa đóng gói dữ liệu truyền tải giữa các tầng
│   ├── extensions/             # Khởi tạo các thành phần mở rộng của Flask (Database, Migrate, Auth...)
│   ├── models/                 # Entities / Data Models: Các lớp định nghĩa cấu trúc bảng CSDL (SQLAlchemy)
│   ├── repositories/           # Tầng Data Access (Repository Pattern): Chịu trách nhiệm truy xuất CSDL thuần
│   ├── routes/                 # Tầng Presentation (Blueprints): Tiếp nhận API/HTTP Request và điều hướng
│   └── services/               # Tầng Application (Business Logic): Xử lý nghiệp vụ cốt lõi của toàn hệ thống
├── docs/                       # 📚 Tài liệu Đồ án: Chứa file phân tích thiết kế, biểu đồ UML, cấu trúc AI
├── migrations/                 # Script quản lý phiên bản thay đổi cấu trúc CSDL (Alembic Migrations)
├── scripts/                    # Chứa các tập lệnh tiện ích bổ trợ (VD: Sinh biểu đồ luồng hoạt động)
├── static/                     # Tài nguyên Frontend tĩnh: CSS (Vanilla/Tailwind), JS, Images, Uploads
├── templates/                  # Tầng Giao diện hiển thị: Các file HTML được viết theo cú pháp Jinja2
├── tests/                      # Bộ kiểm thử chất lượng mã nguồn tự động (Unit Test / Integration Test)
├── trained_models/             # Thư mục chứa các tệp mô hình đã qua huấn luyện (Backup)
├── config.py                   # Chứa các biến môi trường và thiết lập cấu hình chung (Database URI, Secret Key)
├── requirements.txt            # Danh sách thư viện Python cần cài đặt để chạy dự án
├── run.py                      # 🚀 Điểm neo khởi chạy ứng dụng (Entry Point) chính
├── setup_db.py                 # File script tự động khởi tạo cấu trúc các bảng CSDL lần đầu tiên
└── seed_*.py                   # Các file tự động phát sinh dữ liệu mẫu (Mock data) cho hệ thống
```
