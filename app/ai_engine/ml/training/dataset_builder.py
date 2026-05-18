import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from app.extensions import db
from app.models import Employee, EmployeeAnalytics, Attendance, LeaveRequest, Task

class DatasetBuilder:
    def __init__(self):
        from app.services.analytics_service import AnalyticsService
        self.analytics_service = AnalyticsService()

    def build_employee_dataset(self, include_synthetic: bool = True, target_size: int = 500) -> pd.DataFrame:
        """
        Trích xuất và chuẩn bị tập dữ liệu huấn luyện ML hoàn chỉnh từ các nhân viên hiện tại trong DB.
        Nếu include_synthetic=True, tự động tạo thêm dữ liệu tổng hợp (synthetic data) có tương quan thực tế
        để bảo đảm mô hình học máy (như XGBoost) học được phân phối xác suất Attrition chính xác.
        """
        employees = self.analytics_service.analytics_repo.get_all_employees_with_analytics()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        raw_records = []
        for emp in employees:
            perf = self.analytics_service.get_individual_performance_metrics(emp.id)
            
            leave_count_90d = sum(1 for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= ninety_days_ago.date())

            task_delays = []
            for t in emp.tasks:
                if t.status == 'Completed' and t.due_date:
                    delay = (t.created_at - t.due_date).days
                    task_delays.append(max(0, delay))
            avg_delay = float(np.mean(task_delays)) if task_delays else 0.0

            delta_days = (datetime.utcnow() - (emp.created_at or datetime.utcnow())).days
            years_at_company = round(delta_days / 365.0, 2)
            probation_status = 1 if delta_days < 90 else 0

            js_raw = emp.analytics.job_satisfaction if emp.analytics else 3
            monthly_income = emp.analytics.monthly_income if emp.analytics else 4500.0
            overtime_val = 1.0 if (emp.analytics and emp.analytics.overtime == 'Yes') else 0.0
            env_sat = emp.analytics.performance_rating if emp.analytics else 3
            workload = min(10.0, 4.0 + len(emp.tasks) * 0.5)

            attrition_label = 0

            record = {
                'employee_id': emp.id,
                'attendance_ratio_30d': float(perf.get('att_score', 95.0)) / 100.0,
                'overtime_ratio_30d': overtime_val,
                'task_completion_rate': float(perf.get('task_score', 100.0)) / 100.0,
                'leave_frequency_90d': leave_count_90d,
                'avg_task_delay_days': avg_delay,
                'monthly_income_amount': float(monthly_income),
                'years_at_company': years_at_company,
                'promotion_gap_months': int(years_at_company * 12) % 24,
                'job_satisfaction_score': float(js_raw) / 4.0,
                'environment_satisfaction_score': float(env_sat) / 4.0,
                'workload_score': workload / 10.0,
                'probation_status': probation_status,
                'attrition_label': attrition_label
            }
            raw_records.append(record)

        df = pd.DataFrame(raw_records)

        if include_synthetic and len(df) < target_size:
            synthetic_df = self._generate_synthetic_records(target_size - len(df))
            df = pd.concat([df, synthetic_df], ignore_index=True)

        return df

    def _generate_synthetic_records(self, num_records: int) -> pd.DataFrame:
        """
        Sinh ra dữ liệu nhân sự tổng hợp mang các mối tương quan thực tế:
        - Job satisfaction thấp + Overtime cao + Lương thấp -> Tỷ lệ nghỉ việc (attrition) cao.
        - Khối lượng công việc cao + nghỉ phép nhiều -> Tỷ lệ nghỉ việc cao.
        """
        np.random.seed(42)
        records = []
        
        for i in range(num_records):
            js_score = np.random.choice([1, 2, 3, 4], p=[0.15, 0.20, 0.45, 0.20]) / 4.0
            env_sat = np.random.choice([1, 2, 3, 4], p=[0.10, 0.25, 0.45, 0.20]) / 4.0
            overtime = np.random.choice([0.0, 1.0], p=[0.70, 0.30])
            income = float(np.random.normal(6500, 2000))
            income = max(3000.0, min(18000.0, income))
            
            att_ratio = float(np.random.beta(8, 1))
            task_completion = float(np.random.beta(7, 1.5))
            
            leave_90d = int(np.random.poisson(1.5))
            avg_delay = float(max(0.0, np.random.normal(1.5, 2.0)))
            years = float(max(0.1, np.random.exponential(3.0)))
            probation = 1 if years < 0.25 else 0
            workload = float(np.random.uniform(0.3, 0.9))

            risk_logit = (
                (1.0 - js_score) * 2.0 +
                overtime * 1.5 -
                (income / 10000.0) * 1.0 -
                att_ratio * 1.5 -
                task_completion * 1.2 +
                (avg_delay / 5.0) * 1.0 +
                workload * 1.0 +
                probation * 0.5
            )
            
            probability = 1.0 / (1.0 + np.exp(-risk_logit))
            attrition_label = 1 if np.random.rand() < probability else 0

            records.append({
                'employee_id': 9999 + i,
                'attendance_ratio_30d': round(att_ratio, 3),
                'overtime_ratio_30d': overtime,
                'task_completion_rate': round(task_completion, 3),
                'leave_frequency_90d': leave_90d,
                'avg_task_delay_days': round(avg_delay, 1),
                'monthly_income_amount': round(income, 1),
                'years_at_company': round(years, 2),
                'promotion_gap_months': int(np.random.randint(0, 36)),
                'job_satisfaction_score': js_score,
                'environment_satisfaction_score': env_sat,
                'workload_score': round(workload, 2),
                'probation_status': probation,
                'attrition_label': attrition_label
            })
            
        return pd.DataFrame(records)

    def export_csv(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

    def export_parquet(self, df: pd.DataFrame, path: str):
        df.to_parquet(path, index=False)
