# Bản đồ Thuật toán và Trí tuệ Nhân tạo (AI Algorithm Guide)

Tài liệu này giải thích chi tiết toàn bộ các luồng thuật toán, mô hình AI và cách hoạt động của hệ thống dự báo nghỉ việc trong đồ án **HTQLNhanSu**, kèm theo chỉ dẫn chính xác vị trí mã nguồn (Tên file và số dòng).

---

## 1. Thuật toán Học máy Cốt lõi (Machine Learning Model)

Hệ thống sử dụng **XGBoost Classifier (Extreme Gradient Boosting)** làm thuật toán cốt lõi. Đây là một thuật toán học máy giám sát dạng tập hợp (Ensemble) dựa trên cây quyết định (Decision Trees), có khả năng phân tách xuất sắc các biến thể dữ liệu nhân sự phức tạp. Trong trường hợp môi trường không cài đặt thư viện XGBoost, hệ thống sẽ tự động fallback (chuyển đổi) sang sử dụng **RandomForestClassifier**.

*   **Vị trí File:** [app/ai_engine/ml/training/train_attrition.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/ai_engine/ml/training/train_attrition.py)
*   **Chỉ dẫn Dòng (Line):**
    *   `Dòng 47:` Khởi tạo cấu hình thuật toán `XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05...)`.
    *   `Dòng 58:` Thuật toán dự phòng `RandomForestClassifier(n_estimators=100, max_depth=6)`.
    *   `Dòng 87-88:` Đóng gói và lưu trữ mô hình đã huấn luyện thành file nhị phân `xgboost_attrition_v1.bin` bằng `pickle`.

---

## 2. Hệ thống Dự báo Thời gian thực (Real-time Inference / Predictor)

Khi có một yêu cầu phân tích rủi ro từ người dùng, hệ thống không gọi database để tính toán tay mà nạp mô hình đã được huấn luyện sẵn ở bước 1 vào để dự báo (Predict) xác suất nghỉ việc từ `0.0` đến `1.0`. Nếu mô hình `.bin` chưa tồn tại, nó sẽ kích hoạt tính năng **Self-Bootstrapping** để tự động huấn luyện lại từ đầu.

*   **Vị trí File:** [app/ai_engine/ml/inference/turnover_predictor.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/ai_engine/ml/inference/turnover_predictor.py)
*   **Chỉ dẫn Dòng (Line):**
    *   `Dòng 28-31:` Cơ chế Self-Bootstrapping (tự động chạy lại luồng huấn luyện nếu file model chưa tồn tại).
    *   `Dòng 37:` Hàm `predict_turnover_probability` nhận đầu vào là dictionary vector 12 đặc trưng.
    *   `Dòng 51:` Gọi lệnh `model.predict_proba(X)[0, 1]` của thư viện Scikit-learn để sinh ra xác suất nghỉ việc cụ thể.
    *   `Dòng 53-54:` Quy chuẩn xác suất thành 3 cấp độ `HIGH (>60%)`, `MEDIUM (>30%)`, `LOW`.

---

## 3. Trí tuệ Nhân tạo có thể Giải thích (Explainable AI - XAI với SHAP)

Để khắc phục nhược điểm "hộp đen" (Black-box) của XGBoost/Random Forest, hệ thống tích hợp thư viện **SHAP (Shapley Additive Explanations)** dựa trên lý thuyết trò chơi. Thuật toán này bóc tách xác suất của dự đoán thành các giá trị đóng góp (SHAP values) của từng đặc trưng. Đặc trưng nào có giá trị dương lớn (Positive) là nhân tố thúc đẩy rủi ro (Risk Factor), ngược lại giá trị âm (Negative) là nhân tố giữ chân (Mitigation Factor).

*   **Vị trí File:** [app/ai_engine/ml/inference/shap_explainer.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/ai_engine/ml/inference/shap_explainer.py)
*   **Chỉ dẫn Dòng (Line):**
    *   `Dòng 36:` Khởi tạo cấu trúc `shap.TreeExplainer(model)` chuyên biệt để giải thích các mô hình dạng cây với độ phức tạp tính toán thấp nhất.
    *   `Dòng 40:` Hàm `explain_employee` xử lý tính toán.
    *   `Dòng 55:` Lệnh cốt lõi `explainer.shap_values(X)` trả về mảng các trọng số của từng biến.
    *   `Dòng 68-96:` Logic Rule-based tính điểm (Scoring) dự phòng tự viết trong trường hợp thư viện SHAP bị thiếu, đảm bảo hệ thống không bao giờ crash.
    *   `Dòng 115-127:` Vòng lặp tách SHAP values thành 2 mảng `risk_factors` (Giá trị dương) và `mitigation_factors` (Giá trị âm).

---

## 4. Hệ Khuyến nghị Tự động (Actionable HR Recommendation Engine)

Khối AI này đóng vai trò quyết định: Nó tự động phân tích các nhân tố rủi ro cao nhất được lấy ra từ SHAP Explainer (ví dụ: Lương thấp, Làm thêm giờ nhiều) để ánh xạ sang một Thư viện Hành động (Action Library). Dựa trên luật (Rule-Based Mapping), hệ thống sinh ra các khuyến nghị ưu tiên Cao/Trung bình/Thấp cho phòng HR xử lý (ví dụ: Tăng lương, cho nghỉ bù).

*   **Vị trí File:** [app/ai_engine/ml/inference/recommender.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/ai_engine/ml/inference/recommender.py)
*   **Chỉ dẫn Dòng (Line):**
    *   `Dòng 4:` Phương thức tĩnh `generate_recommendations` nhận đầu vào là `risk_factors`.
    *   `Dòng 12-73:` Cấu trúc dữ liệu Tự điển `action_library` (Dictionary) quy định sẵn các quy tắc tương ứng cho từng loại đặc trưng (VD: `overtime_ratio_30d` thì ánh xạ ra hành động phê duyệt nghỉ bù).
    *   `Dòng 75-81:` Vòng lặp so sánh các Risk Factors của nhân viên với Thư viện hành động để gán `priority` và `impact_score` vào cấu trúc trả về.

---

## 5. Trích xuất Đặc trưng (Feature Engineering & Dataset Builder)

Trước khi đi vào mô hình Machine Learning, dữ liệu thô của MySQL (từ các bảng Employee, Attendance, Task, Leave) phải được tổng hợp, biến đổi thành Vector Đặc trưng 1 chiều (12 chiều dữ liệu).

*   **Vị trí File 1 (Khởi tạo Dữ liệu Huấn luyện Offline):** [app/ai_engine/ml/training/dataset_builder.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/ai_engine/ml/training/dataset_builder.py)
    *   `Dòng 20-30:` Các hàm sinh dữ liệu thực tế (Synthetic Data) và liên kết ngẫu nhiên để bù đắp sự thiếu hụt dữ liệu trong pha mồi mô hình.
*   **Vị trí File 2 (Trích xuất Đặc trưng Realtime):** [app/services/ai_service.py](file:///c:/laragon/www/HTQLNhanSu1/DACS_HTQLNhanSu/app/services/ai_service.py)
    *   `Dòng 137:` Phương thức `extract_employee_features`. Tại đây, hệ thống biến đổi từ Entity MySQL (`emp_data`) thành Dictionary thuần túy chứa 12 chỉ số như `attendance_ratio_30d` (Tính trên tổng đi làm), `task_completion_rate`, `probation_status`,...

---

### Tóm tắt luồng hoạt động tổng quan (Workflow AI):
1. Giao diện gọi API `ai_dashboard` -> 2. `ai_service` lấy dữ liệu MySQL -> 3. Biến đổi thành Vector (`extract_employee_features`) -> 4. Gọi `TurnoverPredictor` tính Xác suất -> 5. Gọi `AttritionShapExplainer` tìm nguyên nhân -> 6. Gọi `HRActionRecommender` đưa ra Đề xuất -> 7. Tổng hợp và trả về hiển thị lên Chart.js.
