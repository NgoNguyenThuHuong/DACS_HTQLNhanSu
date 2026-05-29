# AI Employee Attrition Prediction Architecture

## Tổng Quan (Overview)
Hệ thống sử dụng Machine Learning (Random Forest) để dự báo xác suất một nhân viên sẽ nghỉ việc (Resigned) dựa trên các dữ liệu hành vi thực tế (Attendance, Task, Performance) trên hệ thống HTQLNhanSu.

Đây là giải pháp Enterprise-Grade tích hợp **Explainable AI (XAI)** để không chỉ đưa ra cảnh báo mà còn giải thích được lý do đằng sau các dự đoán (Top Risk Factors).

## Workflow Huấn Luyện (Training Pipeline)
1. **Dữ liệu đầu vào**: Lấy từ bảng `employees`, `attendance`, `tasks`, `employee_analytics`.
2. **Feature Engineering**: Trích xuất các đặc trưng tĩnh (Static Features) và đặc trưng xu hướng (Trend Features) trong 30-60 ngày gần nhất.
3. **Training**: Sử dụng `RandomForestClassifier` từ thư viện `scikit-learn`.
4. **Imbalance Handling**: Kích hoạt siêu tham số `class_weight='balanced'` để tự động điều chỉnh trọng số với tập dữ liệu mất cân bằng (Active >> Resigned).
5. **Evaluation**: Đánh giá bằng Precision, Recall, F1-Score, ROC-AUC và Confusion Matrix.
6. **Export**: Xuất model ra dạng file `.pkl` (`joblib`) kèm metadata JSON phiên bản hóa (`models/model_metadata.json`).

## Feature Engineering (Các đặc trưng trích xuất)
* **Demographic / Profile**: `years_in_company`, `distance_from_home`, `monthly_income`.
* **Attendance**: `late_count`, `avg_work_hours`, `total_overtime_hours`.
* **Temporal / Trend Features**: 
  * `attendance_decline_rate`: Biến động trễ/vắng mặt 30 ngày so với 60 ngày.
  * `monthly_late_trend`: Số lần đi trễ trong tháng.
  * `overtime_growth_rate`: Tốc độ tăng trưởng Overtime.
* **Performance**: `task_completion_rate`, `pending_task_rate`, `performance_trend` (Xu hướng hoàn thành task).
* **Target Variable**: `target_attrition` (Mã hóa từ `employment_status`: Active=0, Resigned=1).

## Explainable AI (XAI) - Giải Thích Mô Hình
Khi chạy API Dự đoán (`/api/ai/attrition-risk/<id>`), hệ thống không chỉ trả về Probability và Confidence, mà còn trả về `top_factors`.
Điều này đạt được bằng cách so sánh các Feature Importance toàn cục (từ `model.feature_importances_`) với các Feature Value nội bộ của nhân viên đó để dịch thành ngôn ngữ tự nhiên (VD: "Frequent lateness (3 times)", "Low job satisfaction (Score: 2)").

## Ngăn Ngừa Target Leakage
* Chỉ lấy hành vi trong quá khứ hoặc hiện hành, KHÔNG dùng nhãn `employment_status` làm input cho mô hình.
* Tách biệt hàm sinh dataset `get_training_dataset()` (có target) và hàm `extract_features()` lúc prediction (drop target).

## Cấu trúc API
`GET /api/ai/attrition-risk/<employee_id>`
Trả về:
```json
{
    "employee_id": 1,
    "employee_name": "Nguyen Van A",
    "prediction": "High Risk",
    "probability": 0.87,
    "confidence": 0.87,
    "risk_level": "High",
    "top_factors": [
        "Frequent lateness (5 times)",
        "High overtime hours (25.0h)"
    ],
    "model_version": "v1.0"
}
```
