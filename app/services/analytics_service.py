from app.repositories import AnalyticsRepository, EmployeeRepository
from app.dtos import EmployeeFeatureDTO
from ai_engine.analytics.hr_metrics import calculate_turnover_risk, calculate_performance, calculate_radar_metrics
from ai_engine.analytics.feature_pipeline import extract_employee_feature_vector

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class AnalyticsService:
    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.employee_repo = EmployeeRepository()

    def get_individual_performance_metrics(self, emp_id: int) -> Dict[str, Any]:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        base = self.analytics_repo.get_employee_performance_base(emp_id, thirty_days_ago)
        
        perf = calculate_performance(
            present_days=base['present_days'],
            total_tasks=base['total_tasks'],
            completed_tasks=base['completed_tasks']
        )
        
        perf['leave_days'] = base['leave_days']
        perf['present_days'] = base['present_days']
        return perf

    def get_turnover_risk_ai_dashboard(self) -> List[Dict[str, Any]]:
        employees = self.analytics_repo.get_all_employees_with_analytics()
        risk_data = []
        month_ago = datetime.utcnow() - timedelta(days=30)

        for emp in employees:
            recent_leaves_count = sum(1 for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= month_ago.date())
            
            delta = datetime.utcnow() - (emp.created_at or datetime.utcnow())
            probation_status = 1 if delta.days < 90 else 0
            
            job_satisfaction = emp.analytics.job_satisfaction if emp.analytics else None
            overtime = emp.analytics.overtime if emp.analytics else None
            monthly_income = emp.analytics.monthly_income if emp.analytics else None

            risk = calculate_turnover_risk(
                job_satisfaction=job_satisfaction,
                overtime=overtime,
                monthly_income=monthly_income,
                recent_leaves_count=recent_leaves_count,
                probation_status=probation_status
            )

            if risk['score'] > 0:
                risk_data.append({
                    'id': emp.id,
                    'fullname': emp.fullname,
                    'position': emp.position or "Nhân viên",
                    'score': risk['score'],
                    'level': risk['level'],
                    'color': risk['color'],
                    'reasons': risk['reasons']
                })

        risk_data.sort(key=lambda x: x['score'], reverse=True)
        return risk_data[:5]

    def get_system_radar_data(self) -> Dict[str, Any]:
        employees = self.analytics_repo.get_all_employees_with_analytics()
        if not employees:
            return {
                'labels': ["Hiệu suất", "Chuyên cần", "Hoàn thành Task", "Hài lòng", "Thâm niên", "Bảo mật"],
                'values': [0, 0, 0, 0, 0, 0],
                'insight': "Chưa có nhân viên nào trong hệ thống."
            }

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        employees_metrics = []

        for emp in employees:
            perf = self.get_individual_performance_metrics(emp.id)
            satisfaction = (emp.analytics.job_satisfaction / 4.0) * 100.0 if emp.analytics and emp.analytics.job_satisfaction else 75.0
            
            employees_metrics.append({
                'perf_score': perf['score'],
                'att_score': perf['att_score'],
                'task_score': perf['task_score'],
                'satisfaction_score': satisfaction
            })

        return calculate_radar_metrics(employees_metrics)

    def get_individual_radar_data(self, emp_id: int) -> Optional[Dict[str, Any]]:
        emp = self.employee_repo.get_by_id(emp_id)
        if not emp:
            return None

        perf = self.get_individual_performance_metrics(emp_id)
        labels = ["Hiệu suất", "Chuyên cần", "Khối lượng", "Hài lòng", "Thâm niên", "Kỷ luật"]
        
        pending_tasks = sum(1 for t in emp.tasks if t.status == 'Pending')
        w = min(10, 5 + (pending_tasks * 0.5))
        
        s = (emp.analytics.job_satisfaction / 4.0 * 10.0) if emp.analytics and emp.analytics.job_satisfaction else 8.0
        
        delta = datetime.utcnow() - (emp.created_at or datetime.utcnow())
        t = min(10, (delta.days / 365.0) * 2.0 + 5.0)
        
        d = 9.5

        return {
            'labels': labels,
            'values': [perf['score'] / 10.0, perf['att_score'] / 10.0, w, s, t, d],
            'score': perf['score']
        }

    def get_weekly_attendance_trend(self) -> List[Dict[str, Any]]:
        return self.analytics_repo.get_attendance_trend(7)

    def get_recent_activities(self) -> List[Dict[str, Any]]:
        return self.analytics_repo.get_recent_activities(10)

    # --- PIPELINE TRÍCH XUẤT ĐẶC TRƯNG CHUẨN HOÁ AI ---
    def get_employee_features_pipeline(self, emp_id: int) -> Optional[Dict[str, Any]]:
        emp = self.employee_repo.get_by_id(emp_id)
        if not emp:
            return None

        perf = self.get_individual_performance_metrics(emp_id)
        
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        leave_count_90d = sum(1 for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= ninety_days_ago.date())

        delta = datetime.utcnow() - (emp.created_at or datetime.utcnow())
        probation_status = 1 if delta.days < 90 else 0

        js_raw = emp.analytics.job_satisfaction if emp.analytics else None
        overtime = emp.analytics.overtime if emp.analytics else None
        monthly_income = emp.analytics.monthly_income if emp.analytics else None
        distance = emp.analytics.distance_from_home if emp.analytics else None

        risk = calculate_turnover_risk(
            job_satisfaction=js_raw,
            overtime=overtime,
            monthly_income=monthly_income,
            recent_leaves_count=sum(1 for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= (datetime.utcnow() - timedelta(days=30)).date()),
            probation_status=probation_status
        )

        emp_data_map = {
            'id': emp.id,
            'fullname': emp.fullname,
            'position': emp.position or "Nhân viên",
            'department_name': emp.department.name if emp.department else 'Chưa có',
            'birthday_year': emp.birthday.year if emp.birthday else None,
            'gender': emp.gender,
            'job_satisfaction': js_raw,
            'monthly_income': monthly_income,
            'overtime': overtime,
            'distance_from_home': distance,
            'probation_status': probation_status,
            'leave_frequency_90d': leave_count_90d
        }

        dto = extract_employee_feature_vector(emp_data_map, perf, risk)
        return dto.__dict__
