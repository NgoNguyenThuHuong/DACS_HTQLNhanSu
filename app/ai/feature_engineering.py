import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.models.models import Employee, Attendance, EmployeeAnalytics, Task
from app.extensions import db
from sqlalchemy import func

def extract_features(employee_id=None):
    """
    Trích xuất feature từ database cho ML pipeline hoặc online prediction.
    - Nếu employee_id = None, extract cho toàn bộ nhân viên (cho training).
    - Nếu có employee_id, extract cho 1 người (cho prediction).
    Tránh target leakage: Không dùng employment_status, không dùng time filter > hiện tại.
    """
    
    query = db.session.query(Employee)
    if employee_id:
        query = query.filter_by(id=employee_id)
        
    employees = query.all()
    if not employees:
        return pd.DataFrame()

    data = []
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    
    for emp in employees:
        analytics = EmployeeAnalytics.query.filter_by(employee_id=emp.id).first()
        if not analytics:
            continue # Bỏ qua nếu thiếu analytics

        # 1. Base Analytics Features
        emp_data = {
            'employee_id': emp.id,
            'job_satisfaction': analytics.job_satisfaction or 3,
            'performance_rating': analytics.performance_rating or 3,
            'monthly_income': analytics.monthly_income or 0.0,
            'distance_from_home': analytics.distance_from_home or 0,
            'years_in_company': emp.years_in_company or 0.0,
            'target_attrition': 1 if emp.employment_status == 'Resigned' else 0 # ONLY FOR TRAINING, DROPPED LATER
        }

        # 2. Attendance Features (Total & Trends)
        attendances = Attendance.query.filter_by(employee_id=emp.id).all()
        late_count = sum(1 for a in attendances if a.status == 'Late')
        avg_work_hours = np.mean([a.total_work_hours for a in attendances]) if attendances else 8.0
        overtime_hours = sum(a.overtime_hours or 0.0 for a in attendances)
        
        emp_data['late_count'] = late_count
        emp_data['avg_work_hours'] = avg_work_hours
        emp_data['total_overtime_hours'] = overtime_hours
        
        # Trend Features (Last 30 days vs Last 31-60 days)
        att_last_30 = [a for a in attendances if a.work_date >= thirty_days_ago]
        att_last_60 = [a for a in attendances if thirty_days_ago > a.work_date >= sixty_days_ago]
        
        late_30 = sum(1 for a in att_last_30 if a.status == 'Late')
        late_60 = sum(1 for a in att_last_60 if a.status == 'Late')
        
        ot_30 = sum(a.overtime_hours or 0.0 for a in att_last_30)
        ot_60 = sum(a.overtime_hours or 0.0 for a in att_last_60)
        
        # Avoid division by zero
        emp_data['monthly_late_trend'] = late_30
        emp_data['attendance_decline_rate'] = (late_30 - late_60) / (late_60 + 1)
        emp_data['overtime_growth_rate'] = (ot_30 - ot_60) / (ot_60 + 1.0)
        emp_data['recent_absence_frequency'] = 30 - len(att_last_30) # Roughly measuring skipped days
        
        # 3. Task Features (Total & Trends)
        tasks = Task.query.filter_by(employee_id=emp.id).all()
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == 'Completed')
        
        emp_data['task_completion_rate'] = (completed_tasks / total_tasks) if total_tasks > 0 else 1.0
        emp_data['pending_task_rate'] = 1.0 - emp_data['task_completion_rate']
        
        # Task Trend
        tasks_30 = [t for t in tasks if t.created_at and t.created_at.date() >= thirty_days_ago]
        tasks_60 = [t for t in tasks if t.created_at and thirty_days_ago > t.created_at.date() >= sixty_days_ago]
        
        comp_rate_30 = sum(1 for t in tasks_30 if t.status == 'Completed') / (len(tasks_30) + 0.1)
        comp_rate_60 = sum(1 for t in tasks_60 if t.status == 'Completed') / (len(tasks_60) + 0.1)
        emp_data['performance_trend'] = comp_rate_30 - comp_rate_60 # Positive is good

        data.append(emp_data)

    df = pd.DataFrame(data)
    # Fill any NaNs generated just in case
    df = df.fillna(0.0)
    return df

def get_training_dataset():
    """
    Chuẩn bị X, y cho training.
    """
    df = extract_features()
    if df.empty:
        return None, None
        
    y = df['target_attrition']
    X = df.drop(columns=['employee_id', 'target_attrition'])
    
    return X, y
