# Tổng hợp Các Biểu đồ UML (UML Diagrams)

Tài liệu này cung cấp các biểu đồ thiết kế hệ thống quan trọng bằng ngôn ngữ Mermaid, bao gồm: Use Case, Class Diagram, Activity Diagram, và Sequence Diagram. Bạn có thể sử dụng trực tiếp các biểu đồ này cho báo cáo đồ án của mình.

---

## 1. Biểu đồ Use Case (Use Case Diagram)

Mô tả sự tương tác giữa các tác nhân (Actors) và các chức năng của hệ thống.

```mermaid
flowchart LR
    %% Định nghĩa các Actor bằng hình chữ nhật
    Employee[Nhân viên]
    HR[Quản lý Nhân sự]
    Admin[Quản trị viên]
    Candidate[Ứng viên]
    
    %% Định nghĩa các Use Case bằng hình oval/tròn
    UC_C1([Xem Tin tuyển dụng])
    UC_C2([Nộp Hồ sơ ứng tuyển])
    UC_C3([Làm bài thi Trắc nghiệm])
    
    Candidate --> UC_C1
    Candidate --> UC_C2
    Candidate --> UC_C3

    UC_E1([Đăng nhập / Đăng xuất])
    UC_E2([Điểm danh])
    UC_E3([Gửi Đơn xin nghỉ phép])
    UC_E4([Nhận và Cập nhật Task])
    UC_E5([Xem Hồ sơ cá nhân])
    
    Employee --> UC_E1
    Employee --> UC_E2
    Employee --> UC_E3
    Employee --> UC_E4
    Employee --> UC_E5

    UC_H1([Quản lý Hồ sơ nhân sự])
    UC_H2([Duyệt Đơn nghỉ phép])
    UC_H3([Giao việc])
    UC_H4([Quản lý Tuyển dụng & Đề thi])
    UC_H5([Xem Báo cáo AI XAI Dashboard])
    
    HR --> UC_E1
    HR --> UC_H1
    HR --> UC_H2
    HR --> UC_H3
    HR --> UC_H4
    HR --> UC_H5

    UC_A1([Quản lý Phòng ban])
    UC_A2([Quản lý Phân quyền hệ thống])
    
    Admin --> UC_E1
    Admin --> UC_H1
    Admin --> UC_H2
    Admin --> UC_H3
    Admin --> UC_H4
    Admin --> UC_H5
    Admin --> UC_A1
    Admin --> UC_A2
```

---

## 2. Biểu đồ Lớp (Class Diagram)

Mô tả cấu trúc các lớp (Classes/Entities) và mối quan hệ giữa chúng trong Cơ sở dữ liệu ORM.

```mermaid
classDiagram
    class Department {
        +int id
        +string name
        +string description
        +datetime created_at
    }

    class Employee {
        +int id
        +int department_id
        +string employee_code
        +string username
        +string fullname
        +string position
        +string role
        +check_password()
    }

    class EmployeeAnalytics {
        +int id
        +int employee_id
        +float job_satisfaction
        +float monthly_income
        +float performance_rating
        +boolean overtime
    }

    class Attendance {
        +int id
        +int employee_id
        +date work_date
        +datetime check_in
        +datetime check_out
        +string status
    }

    class Task {
        +int id
        +int employee_id
        +string title
        +string status
        +date due_date
    }

    class JobPost {
        +int id
        +string title
        +string status
        +datetime created_at
    }

    class Candidate {
        +int id
        +int job_id
        +string fullname
        +string status
    }

    class Exam {
        +int id
        +int job_id
        +string title
        +int duration_minutes
    }

    Department "1" -- "*" Employee : có
    Employee "1" -- "1" EmployeeAnalytics : sở hữu
    Employee "1" -- "*" Attendance : ghi nhận
    Employee "1" -- "*" Task : thực hiện
    JobPost "1" -- "*" Candidate : thu hút
    JobPost "1" -- "*" Exam : yêu cầu
```

---

## 3. Biểu đồ Hoạt động (Activity Diagram)

Mô tả luồng nghiệp vụ của tính năng **Điểm danh (Check-in/Check-out)** và **Duyệt nghỉ phép**.

### Quy trình Chấm công bằng Camera/QR
```mermaid
flowchart TD
    Start([Nhân viên mở tính năng Điểm danh]) --> A{Quét Khuôn mặt / QR?}
    A -->|Thất bại| B[Hệ thống báo lỗi & Yêu cầu thử lại] --> A
    A -->|Thành công| C[Gửi thông tin xác thực lên Server]
    C --> D{Kiểm tra giờ hiện tại?}
    
    D -->|< 8:00 AM| E[Ghi nhận Check-in: ON_TIME]
    D -->|> 8:00 AM| F[Ghi nhận Check-in: LATE]
    
    E --> G[Lưu bản ghi vào Database]
    F --> G
    
    G --> End([Kết thúc / Hiển thị thông báo thành công])
```

### Quy trình Duyệt Đơn Nghỉ Phép
```mermaid
flowchart TD
    Start([Nhân viên nộp Đơn xin nghỉ]) --> A[Lưu đơn vào DB với trạng thái PENDING]
    A --> B[Quản lý HR nhận thông báo]
    B --> C{HR xem xét & Quyết định}
    
    C -->|Phê duyệt| D[Đổi trạng thái thành APPROVED]
    C -->|Từ chối| E[Đổi trạng thái thành REJECTED]
    
    D --> F[Trừ số ngày phép còn lại của Nhân viên]
    E --> G[Giữ nguyên số ngày phép]
    
    F --> H[Gửi email/thông báo cho Nhân viên]
    G --> H
    H --> End([Kết thúc quy trình])
```

---

## 4. Biểu đồ Tuần tự (Sequence Diagram)

Mô tả thứ tự các lời gọi hàm và trao đổi thông điệp giữa các đối tượng trong tính năng **Dự báo rủi ro nghỉ việc bằng AI**.

```mermaid
sequenceDiagram
    participant HR as HR Manager
    participant UI as Web Dashboard
    participant API as Route (ai_dashboard.py)
    participant SVC as AIService
    participant ML as TurnoverPredictor & SHAP
    participant DB as MySQL Database

    HR->>UI: Bấm xem "Phân tích Rủi ro Nhân viên A"
    UI->>API: GET /ai/employee/1/dashboard
    
    API->>SVC: get_ai_profile(employee_id=1)
    
    SVC->>DB: Truy vấn dữ liệu thô (Employee, Attendance, Tasks...)
    DB-->>SVC: Trả về Object ORM (Dữ liệu chưa xử lý)
    
    SVC->>SVC: extract_features() -> Chuyển đổi thành Vector 12 chiều
    
    SVC->>ML: predict_turnover_probability(Vector)
    ML-->>SVC: Trả về % Xác suất Nghỉ việc (VD: 85%)
    
    SVC->>ML: explain_employee(Vector) (Dùng TreeSHAP)
    ML-->>SVC: Trả về các Nhân tố rủi ro (Risk Factors)
    
    SVC->>SVC: generate_recommendations(Risk Factors)
    
    SVC-->>API: Trả về DTO tổng hợp (JSON)
    API-->>UI: Cập nhật giao diện (Vẽ biểu đồ Chart.js)
    UI-->>HR: Hiển thị Biểu đồ SHAP và Lời khuyên
```
