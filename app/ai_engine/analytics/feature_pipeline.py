from typing import Dict, Any, Optional
from app.dtos import EmployeeFeatureDTO

def extract_employee_feature_vector(employee_data: Dict[str, Any], 
                                    performance_metrics: Dict[str, Any],
                                    turnover_risk: Dict[str, Any]) -> EmployeeFeatureDTO:
    """
    Chuẩn hóa đặc trưng (Feature Vector Extraction) của một nhân viên theo đúng quy chuẩn đặt tên đặc trưng 
    (Feature Naming Convention) để sẵn sàng nạp vào các mô hình Machine Learning như XGBoost, LightGBM.
    """
    emp = employee_data
    perf = performance_metrics
    risk = turnover_risk
    
    gender_male = 1 if emp.get('gender') == 'Nam' else 0
    
    js_raw = emp.get('job_satisfaction')
    job_satisfaction_score = (js_raw / 4.0) if js_raw else 0.75
    
    overtime_ratio_30d = 1.0 if emp.get('overtime') == 'Yes' else 0.0
    
    probation_status = emp.get('probation_status', 0)

    return EmployeeFeatureDTO(
        employee_id=emp.get('id', 0),
        fullname=emp.get('fullname', ''),
        position_title=emp.get('position', 'Nhân viên'),
        department_name=emp.get('department_name', 'Chưa có'),
        birthday_year=emp.get('birthday_year'),
        gender_male=gender_male,
        job_satisfaction_score=job_satisfaction_score,
        monthly_income_amount=float(emp.get('monthly_income') or 0.0),
        overtime_ratio_30d=overtime_ratio_30d,
        distance_from_home_km=float(emp.get('distance_from_home') or 0.0),
        performance_rating_score=float(emp.get('performance_rating') or 3.0),
        attendance_ratio_30d=float(perf.get('att_score') or 0.0) / 100.0,
        late_ratio_30d=0.0,
        task_completion_rate=float(perf.get('task_score', 100.0)) / 100.0,
        leave_frequency_90d=int(emp.get('leave_frequency_90d', 0)),
        probation_status=probation_status,
        turnover_risk_score=float(risk.get('score', 0.0)),
        turnover_risk_level=risk.get('level', 'LOW')
    )
