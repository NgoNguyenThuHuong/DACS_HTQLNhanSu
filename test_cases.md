# Tài Liệu Kịch Bản Kiểm Thử Doanh Nghiệp (Enterprise Test Case Documentation)

Tài liệu này chứa danh sách toàn bộ các kịch bản kiểm thử (Test Cases) được thiết kế cho hệ thống **HTQLNhanSu (AI-HRM)** theo chuẩn QA doanh nghiệp cấp cao.

---

## 1. Kiểm thử chức năng (Functional Testing)

| Test Case ID | Phân hệ (Module) | Kịch bản (Scenario) | Điều kiện tiên quyết | Các bước thực hiện | Dữ liệu kiểm thử | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FT-001** | Xác thực | Đăng nhập thành công | Tài khoản đã tồn tại trong DB | 1. Nhập username<br>2. Nhập password hợp lệ<br>3. Click "Đăng nhập" | Username: `admin`<br>Password: `123` | Đăng nhập thành công, chuyển hướng đến trang Dashboard chính | Chuyển hướng thành công về trang Dashboard | **PASS** |
| **FT-002** | Xác thực | Đăng ký tài khoản mới | Username/Mã NV chưa tồn tại | 1. Điền đầy đủ thông tin đăng ký<br>2. Click "Đăng ký" | Username: `nv_test`<br>Password: `123`<br>Mã NV: `NV999`<br>Email: `nv@test.com` | Tài khoản được tạo thành công, chuyển hướng về trang Login | Tạo tài khoản thành công trong database | **PASS** |
| **FT-003** | Điểm danh | Chấm công khuôn mặt | Đã gán khuôn mặt mẫu | 1. Mở camera chấm công<br>2. Đứng trước camera quét khuôn mặt | Ảnh chụp camera thời gian thực | Nhận diện thành công mã nhân viên, ghi nhận log check-in | Log chấm công được ghi nhận đúng giờ | **PASS** |
| **FT-004** | Nghỉ phép | Đăng ký đơn nghỉ phép | Nhân viên đã đăng nhập | 1. Chọn loại nghỉ phép<br>2. Chọn ngày<br>3. Click "Gửi đơn" | StartDate: `2026-06-01`<br>EndDate: `2026-06-03`<br>Lý do: `Việc gia đình` | Đơn phép chuyển sang trạng thái "Pending", HR/Admin nhận được thông báo | Đơn phép hiển thị đúng trạng thái chờ duyệt | **PASS** |
| **FT-005** | Quản lý | HR duyệt đơn nghỉ phép | HR đã đăng nhập | 1. Truy cập danh sách đơn phép<br>2. Click "Duyệt" (Approve) | ID đơn phép: `1` | Trạng thái đơn phép đổi thành "Approved", trừ số ngày phép của NV | Trạng thái cập nhật và gửi thông báo thành công | **PASS** |
| **FT-006** | Tuyển dụng | Ứng viên nộp hồ sơ & thi MCQ | Tin tuyển dụng đang mở | 1. Điền thông tin ứng viên<br>2. Tải CV lên<br>3. Làm bài thi MCQ trực tuyến | File CV: `cv.pdf`<br>Bài thi trắc nghiệm | Lưu hồ sơ ứng viên thành công, chấm điểm thi tự động | Hệ thống chấm điểm thi MCQ chính xác | **PASS** |
| **FT-007** | Dashboard | Dashboard Realtime cập nhật | Có dữ liệu hoạt động mới | 1. Thực hiện điểm danh/nộp đơn phép<br>2. Quan sát biểu đồ Dashboard | Hoạt động chấm công mới | Biểu đồ cập nhật số liệu realtime tự động qua SSE/Polling | Dữ liệu cập nhật ngay lập tức | **PASS** |

---

## 2. Kiểm thử Mô hình AI (AI/ML Testing)

| Test Case ID | Phân hệ | Kịch bản | Điều kiện | Các bước | Dữ liệu | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AIT-001** | AI Attrition | Dự đoán rủi ro nghỉ việc | Mô hình đã được train và lưu tại `xgboost_attrition_v1.bin` | 1. Truy vấn API dự báo rủi ro cho nhân viên | ID nhân viên: `1` | Trả về JSON chứa xác suất nghỉ việc, mức độ rủi ro (HIGH/MEDIUM/LOW) | Phản hồi JSON chuẩn, có mức độ rủi ro hợp lệ | **PASS** |
| **AIT-002** | AI Risk | Đánh giá độ nhạy với Overtime | Khách thể có chỉ số overtime tăng mạnh | 1. Gửi vector đặc trưng có overtime cao nhất | Overtime: `1.0` (Có làm thêm) | Mức độ rủi ro nghỉ việc tăng tối thiểu 15% so với không overtime | Rủi ro tăng và hiển thị cảnh báo đỏ trên dashboard | **PASS** |
| **AIT-003** | AI Recs | Gợi ý giữ chân (Recommendation) | Nhân viên có nguy cơ nghỉ việc cao | 1. Gọi API gợi ý giữ chân cho nhân viên rủi ro HIGH | ID nhân viên: `1` | Hệ thống tự động phân tích SHAP và đưa ra hành động tối ưu (Tăng lương, giảm tải công việc) | Xuất các hành động giữ chân thực tế có độ ưu tiên cao | **PASS** |

---

## 3. Kiểm thử Giao diện Lập trình Ứng dụng (API Testing)

| Test Case ID | Phân hệ | Kịch bản | Điều kiện | Các bước | Dữ liệu | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **APIT-001** | REST API | Xác thực phân quyền GET Risk | Chưa đăng nhập hệ thống | 1. Gửi request GET tới `/ai/employee/1/risk` | Không có session cookie | Trả về HTTP 302 redirect hoặc HTTP 401 Unauthorized | Trả về mã lỗi 302 Redirect | **PASS** |
| **APIT-002** | REST API | Gửi ID nhân viên không tồn tại | Đã đăng nhập với quyền HR/Admin | 1. Gửi request GET tới `/ai/employee/99999/risk` | ID: `99999` (Không tồn tại) | Trả về mã lỗi HTTP 400 Bad Request kèm nội dung lỗi cụ thể | Trả về 400 Bad Request | **PASS** |
| **APIT-003** | REST API | Xác thực cấu trúc JSON Dashboard | Đăng nhập hợp lệ | 1. Gửi request GET tới `/ai/employee/1/dashboard?format=json` | format: `json` | JSON phản hồi khớp cấu trúc DTO với đầy đủ labels, values, giải thích SHAP | JSON khớp hoàn toàn với cấu trúc DTO chuẩn | **PASS** |

---

## 4. Kiểm thử An toàn Thông tin (Security Testing)

| Test Case ID | Phân hệ | Kịch bản | Điều kiện | Các bước | Dữ liệu | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SECT-001** | Database | Phòng chống SQL Injection | Form đăng nhập | 1. Nhập mã độc SQL vào trường username<br>2. Click Đăng nhập | Username: `' OR '1'='1`<br>Password: `any` | Hệ thống báo lỗi mật khẩu hoặc từ chối xác thực, SQL không bị thực thi | Sử dụng SQLAlchemy ORM nên tham số được bind an toàn, chống SQLi triệt để | **PASS** |
| **SECT-002** | XSS | Chặn mã độc XSS phản xạ/lưu trữ | Trường nhập liệu họ tên | 1. Đăng ký tài khoản với họ tên chứa script độc hại | Fullname: `<script>alert('xss')</script>` | Trình duyệt escape ký tự hoặc Jinja2 tự động render dạng text an toàn | Jinja2 tự động sanitize đầu ra, tag script bị vô hiệu hóa | **PASS** |
| **SECT-003** | Auth | Broken Authentication | Lưu trữ mật khẩu | 1. Kiểm tra cấu trúc lưu trữ mật khẩu trong DB | Password trong DB | Mật khẩu phải được băm (hashing) bảo mật bằng bcrypt/pbkdf2 | **WARNING**: Mật khẩu đang được lưu trữ dưới dạng plain-text (Hệ thống cũ) | **FAIL** |

---

## 5. Kiểm thử Chấm công Khuôn mặt (Face Recognition Testing)

| Test Case ID | Phân hệ | Kịch bản | Điều kiện | Các bước | Dữ liệu | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FACET-001**| Check-in | Không phát hiện khuôn mặt | Không có người đứng trước cam | 1. Kích hoạt camera check-in<br>2. Che camera hoặc để camera trống | Khung hình trống | Trả về thông báo lỗi "Không phát hiện khuôn mặt" | Hiển thị đúng thông báo lỗi | **PASS** |
| **FACET-002**| Check-in | Phát hiện nhiều khuôn mặt | 2 người đứng trước camera | 1. Mở camera điểm danh<br>2. Hai người cùng xuất hiện | Khung hình chứa 2 người | Từ chối điểm danh hoặc chỉ điểm danh người ở trung tâm có độ tin cậy cao nhất | Hệ thống xử lý an toàn, yêu cầu điểm danh từng người | **PASS** |
| **FACET-003**| Check-in | Giả mạo ảnh (Spoofing) | Dùng điện thoại chụp ảnh nhân viên | 1. Đưa ảnh chụp chân dung trên điện thoại trước camera | Ảnh kỹ thuật số | Từ chối điểm danh, phát hiện giả mạo sinh trắc học | **WARNING**: Cần nâng cấp mô hình Anti-spoofing liveness detection | **FAIL** |
