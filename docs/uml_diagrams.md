# Tổng hợp Các Biểu đồ UML (UML Diagrams)

Tài liệu này cung cấp các biểu đồ thiết kế hệ thống quan trọng bằng ngôn ngữ Mermaid, bao gồm: Use Case, Class Diagram, Activity Diagram, và Sequence Diagram. Bạn có thể sử dụng trực tiếp các biểu đồ này cho báo cáo đồ án của mình.

---

## 1. Biểu đồ Use Case (Use Case Diagram)

Mô tả sự tương tác giữa các tác nhân (Actors) và các chức năng của hệ thống.

```mermaid
usecaseDiagram
    actor Employee as "Nhân viên (Employee)"
    actor HR as "Quản lý Nhân sự (HR)"
    actor Admin as "Quản trị viên (Admin)"
    actor Candidate as "Ứng viên (Candidate)"
    
    %% Chức năng của Ứng viên
    usecase "Xem Tin tuyển dụng" as UC_C1
    usecase "Nộp Hồ sơ ứng tuyển" as UC_C2
    usecase "Làm bài thi Trắc nghiệm (Exam)" as UC_C3
    
    Candidate --> UC_C1
    Candidate --> UC_C2
    Candidate --> UC_C3

    %% Chức năng của Nhân viên
    usecase "Đăng nhập / Đăng xuất" as UC_E1
    usecase "Điểm danh (Check-in/out)" as UC_E2
    usecase "Gửi Đơn xin nghỉ phép" as UC_E3
    usecase "Nhận và Cập nhật Task" as UC_E4
    usecase "Xem Hồ sơ cá nhân" as UC_E5
    
    Employee --> UC_E1
    Employee --> UC_E2
    Employee --> UC_E3
    Employee --> UC_E4
    Employee --> UC_E5

    %% Chức năng của HR
    usecase "Quản lý Hồ sơ nhân sự" as UC_H1
    usecase "Duyệt Đơn nghỉ phép" as UC_H2
    usecase "Giao việc (Giao Task)" as UC_H3
    usecase "Quản lý Tuyển dụng & Đề thi" as UC_H4
    usecase "Xem Báo cáo AI (XAI Dashboard)" as UC_H5
    
    HR --> UC_E1
    HR --> UC_H1
    HR --> UC_H2
    HR --> UC_H3
    HR --> UC_H4
    HR --> UC_H5

    %% Quản trị viên kế thừa HR và thêm chức năng
    usecase "Quản lý Phòng ban" as UC_A1
    usecase "Quản lý Phân quyền hệ thống" as UC_A2
    
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
