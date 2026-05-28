# Báo Cáo Đánh Giá Mô Hình AI & Khả Năng Giải Thích (AI Model Evaluation & XAI Report)

Báo cáo này trình bày các chỉ số đo lường hiệu năng thực tế thu thập từ việc chạy đánh giá kiểm định trực tiếp trên mô hình học máy dự báo rủi ro nghỉ việc của hệ thống **HTQLNhanSu**.

---

## 1. Kết Quả Đo Lường Hiệu Năng Mô Hình (Model Performance Metrics)

Dữ liệu kiểm thử thu thập từ tập dữ liệu gồm **600 mẫu** (được chia theo tỷ lệ 80/20 Train/Test, stratify phân bố lớp):

| Chỉ số (Metric) | Giá trị thực tế | Ý nghĩa kinh doanh (Business Impact) |
| :--- | :--- | :--- |
| **Accuracy (Độ chính xác tổng thể)** | **72.50%** | Tỷ lệ dự đoán đúng (cả ở lại và nghỉ việc) trên tổng số nhân viên kiểm thử. |
| **Precision (Độ chuẩn xác)** | **64.29%** | Khi AI cảnh báo một nhân viên có nguy cơ nghỉ việc, xác suất người đó thực sự nghỉ việc là 64.29%. |
| **Recall (Độ nhạy)** | **24.32%** | Tỷ lệ nhân viên thực sự nghỉ việc được AI phát hiện thành công là 24.32%. |
| **F1-Score (Trung bình điều hòa)** | **35.29%** | Chỉ số cân bằng giữa Precision và Recall. |
| **ROC-AUC** | **61.54%** | Khả năng phân biệt giữa nhân viên ở lại và nhân viên nghỉ việc của mô hình. |

---

## 2. Ma Trận Nhầm Lẫn (Confusion Matrix Heatmap)

Dưới đây là ma trận phân bổ kết quả dự báo trên tập dữ liệu Test (**120 mẫu**):

| | Thực tế: Ở LẠI (0) | Thực tế: NGHỈ VIỆC (1) |
| :--- | :---: | :---: |
| **Dự báo: Ở LẠI (0)** | **TN = 78** | **FN = 28** |
| **Dự báo: NGHỈ VIỆC (1)** | **FP = 5** | **TP = 9** |

### Giải thích các thuật ngữ chuyên môn:
* **TN (True Negative - 78 trường hợp)**: AI dự đoán nhân viên **ở lại** và thực tế họ **ở lại**. Đây là dự đoán chính xác, giúp HR yên tâm duy trì chính sách hiện tại.
* **TP (True Positive - 9 trường hợp)**: AI dự đoán nhân viên **nghỉ việc** và thực tế họ **nghỉ việc**. Đây là điểm sáng cốt lõi, giúp doanh nghiệp chủ động can thiệp kịp thời để giữ chân nhân sự cốt cán.
* **FP (False Positive - 5 trường hợp)**: AI đưa ra cảnh báo **nhầm** rằng nhân viên sắp nghỉ việc nhưng thực tế họ vẫn **ở lại**. Điều này gây lãng phí một phần nhỏ chi phí và nguồn lực giữ chân (như phỏng vấn, tăng lương không cần thiết).
* **FN (False Negative - 28 trường hợp)**: AI dự đoán nhân viên **ở lại** nhưng thực tế họ lại đột ngột **nghỉ việc**. Đây là lỗi nghiêm trọng nhất vì doanh nghiệp hoàn toàn bị động trước sự ra đi của nhân viên, không có kế hoạch bàn giao công việc hay tuyển dụng thay thế.

---

## 3. Khả Năng Giải Thích Của Mô Hình AI (Explainable AI - XAI với SHAP Surrogate)

Hệ thống sử dụng cơ chế giải thích quyết định nhằm đảm bảo tính minh bạch (Transparency). Dưới đây là mức độ đóng góp (Feature Importance) của các thuộc tính chính:

```mermaid
barChart
    title "Mức độ ảnh hưởng của các đặc trưng (Feature Importance %)"
    x-axis ["Đặc trưng", "Income", "Task Completion", "Overtime", "Attendance", "Tenure", "Task Delay", "Workload", "Promotion Gap"]
    y-axis ["Trọng số (%)"]
    "monthly_income_amount" : 13.84
    "task_completion_rate" : 12.91
    "overtime_ratio_30d" : 12.80
    "attendance_ratio_30d" : 11.37
    "years_at_company" : 9.80
    "avg_task_delay_days" : 9.67
    "workload_score" : 9.14
    "promotion_gap_months" : 9.13
```

### Phân tích chi tiết tác động của 5 Đặc Trưng Hàng Đầu:
1. **Mức lương (monthly_income_amount - 13.84%)**: Là yếu tố ảnh hưởng mạnh nhất đến quyết định đi hay ở của nhân sự. Lương thấp hơn mặt bằng trung bình trực tiếp làm tăng nguy cơ Attrition.
2. **Hiệu suất công việc (task_completion_rate - 12.91%)**: Tỷ lệ hoàn thành công việc thấp thường là dấu hiệu chán nản (Quiet Quitting), báo hiệu nhân viên đã bắt đầu xao nhãng công việc.
3. **Làm thêm giờ (overtime_ratio_30d - 12.80%)**: Làm thêm giờ liên tục dẫn đến tình trạng kiệt sức (Burnout), tăng tỷ lệ rời bỏ tổ chức.
4. **Tỷ lệ đi làm chuyên cần (attendance_ratio_30d - 11.37%)**: Nhân viên bắt đầu đi muộn, nghỉ không phép nhiều là dấu hiệu trực tiếp của sự rời rạc trong gắn kết.
5. **Thâm niên (years_at_company - 9.80%)**: Nhân viên có thâm niên quá ngắn (đang thử việc) hoặc quá lâu không được thăng tiến (Promotion Gap) dễ nảy sinh ý định chuyển việc.

---

## 4. Kiểm Định Tính Công Bằng & Đạo Đức AI (Bias & Fairness Evaluation)

Chúng tôi đã tiến hành đo lường rủi ro dự báo trung bình giữa các nhóm để kiểm định độ thiên lệch (Bias Check):

* **Rủi ro trung bình của nhóm Nam (Male Average Risk)**: `30.60%`
* **Rủi ro trung bình của nhóm Nữ (Female Average Risk)**: `30.71%`
* **Chỉ số công bằng giới tính (Gender Fairness Ratio)**: **`99.64%`** (Gần như tiệm cận mức lý tưởng 100%).

> [!TIP]
> **Nhận xét**: Mô hình không có sự thiên vị hay phân biệt đối xử theo giới tính. Điểm số rủi ro hoàn toàn dựa trên các chỉ số hiệu suất, lương và giờ làm việc thực tế, đảm bảo tính đạo đức và công bằng (Ethical AI).

---

## 5. Đề Xuất Nâng Cấp Kiến Trúc AI/ML

1. **Khắc phục chênh lệch Recall (FN quá cao)**:
   * Hiện tại Recall chỉ đạt **24.32%** do sự mất cân bằng dữ liệu gốc (Imbalance Ratio = 31%).
   * **Giải pháp**: Tích hợp thuật toán **SMOTE** (Synthetic Minority Over-sampling Technique) để sinh thêm mẫu dữ liệu nhân viên nghỉ việc ảo trong quá trình huấn luyện, nâng cao độ nhạy của mô hình với lớp thiểu số.
2. **Nâng cấp từ Rule-based/RF lên XGBoost thực thụ**:
   * Khi lượng dữ liệu tăng lên, cần kích hoạt chế độ huấn luyện XGBoost hoàn chỉnh với bộ siêu tham số được tinh chỉnh qua GridSearch.
3. **Tích hợp giải thích trực tiếp bằng thư viện SHAP**:
   * Chuyển từ mô hình surrogate sang tính toán SHAP values trực tiếp từ mô hình cây (TreeExplainer) để có biểu đồ lực lượng (Force Plot) và biểu đồ đóng góp (Waterfall Plot) trực quan nhất trên UI.
