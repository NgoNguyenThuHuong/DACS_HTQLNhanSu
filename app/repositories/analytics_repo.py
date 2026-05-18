from app.repositories.base_repo import BaseRepository
from app.models import Employee, EmployeeAnalytics, Attendance, LeaveRequest, Task, Department, ExamResult
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from typing import Dict, List, Any

class AnalyticsRepository(BaseRepository):
    model = EmployeeAnalytics

    def get_system_dashboard_metrics(self, thirty_days_ago: datetime) -> Dict[str, Any]:
        today = datetime.now().date()
        
        total_emp = db.session.query(func.count(Employee.id)).scalar() or 0
        attendance_count = db.session.query(func.count(Attendance.id)).filter(Attendance.work_date == today).scalar() or 0
        attendance_rate = round((attendance_count / total_emp * 100.0), 1) if total_emp > 0 else 0.0

        avg_leave = db.session.query(func.avg(Employee.leave_days_used)).scalar() or 0.0
        avg_leave = round(float(avg_leave), 1)

        new_emps = db.session.query(func.count(Employee.id)).filter(Employee.created_at >= thirty_days_ago).scalar() or 0

        avg_score = db.session.query(func.avg(ExamResult.mcq_score)).scalar() or 0.0
        avg_score = round(float(avg_score), 1)

        return {
            'attendance_rate': attendance_rate,
            'avg_leave': avg_leave,
            'new_emps': new_emps,
            'avg_score': avg_score
        }

    def get_department_distribution(self) -> Dict[str, List[Any]]:
        results = db.session.query(
            Department.name,
            func.count(Employee.id)
        ).outerjoin(Employee).group_by(Department.name).all()

        dept_labels = [r[0] for r in results]
        dept_counts = [r[1] for r in results]

        return {
            'labels': dept_labels,
            'counts': dept_counts
        }

    def get_attendance_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        trend = []
        today = datetime.now().date()
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            count = db.session.query(func.count(Attendance.id)).filter(Attendance.work_date == date).scalar() or 0
            trend.append({
                'date': date.strftime('%d/%m'),
                'count': count
            })
        return trend

    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        activities = []
        
        attendances = db.session.query(Attendance)\
            .options(joinedload(Attendance.employee))\
            .order_by(desc(Attendance.check_in))\
            .limit(limit)\
            .all()
        for att in attendances:
            if att.check_in and att.employee:
                activities.append({
                    'user': att.employee.fullname,
                    'action': 'đã Check-in',
                    'time': att.check_in,
                    'icon': 'fa-fingerprint',
                    'color': 'primary'
                })

        leaves = db.session.query(LeaveRequest)\
            .options(joinedload(LeaveRequest.employee))\
            .order_by(desc(LeaveRequest.created_at))\
            .limit(limit)\
            .all()
        for l in leaves:
            if l.employee:
                activities.append({
                    'user': l.employee.fullname,
                    'action': f'gửi đơn nghỉ {l.leave_type} ({l.status})',
                    'time': l.created_at or datetime.utcnow(),
                    'icon': 'fa-calendar-alt',
                    'color': 'warning'
                })

        new_hires = db.session.query(Employee)\
            .order_by(desc(Employee.created_at))\
            .limit(limit)\
            .all()
        for e in new_hires:
            activities.append({
                'user': 'Hệ thống',
                'action': f'đã thêm nhân viên mới: {e.fullname}',
                'time': e.created_at or datetime.utcnow(),
                'icon': 'fa-user-plus',
                'color': 'success'
            })

        activities.sort(key=lambda x: x['time'], reverse=True)
        return activities[:limit]

    def get_employee_performance_base(self, emp_id: int, thirty_days_ago: datetime) -> Dict[str, Any]:
        present_days = db.session.query(func.count(Attendance.id))\
            .filter(Attendance.employee_id == emp_id, Attendance.work_date >= thirty_days_ago.date())\
            .scalar() or 0

        total_tasks = db.session.query(func.count(Task.id))\
            .filter(Task.employee_id == emp_id)\
            .scalar() or 0

        completed_tasks = db.session.query(func.count(Task.id))\
            .filter(Task.employee_id == emp_id, Task.status == 'Completed')\
            .scalar() or 0

        leave_reqs = db.session.query(LeaveRequest)\
            .filter(LeaveRequest.employee_id == emp_id, LeaveRequest.status == 'Approved', LeaveRequest.start_date >= thirty_days_ago.date())\
            .all()
        leave_days = sum((r.end_date - r.start_date).days + 1 for r in leave_reqs)

        return {
            'present_days': present_days,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'leave_days': leave_days
        }

    def get_all_employees_with_analytics(self) -> List[Employee]:
        return db.session.query(Employee)\
            .options(joinedload(Employee.analytics), joinedload(Employee.leave_requests))\
            .all()
