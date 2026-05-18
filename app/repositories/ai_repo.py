from app.extensions import db
from app.models import Employee, EmployeeAnalytics, Attendance, LeaveRequest, Task
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class AIRepository:
    """
    Data Access Layer tối ưu hóa hiệu năng phục vụ suy luận AI.
    Sử dụng joinedload và SQL Aggregates để tránh triệt để N+1 Queries.
    """
    def get_employee_full_ai_profile(self, employee_id: int) -> Optional[Employee]:
        """
        Nạp đầy đủ thông tin nhân viên cùng các thực thể liên quan (analytics, tasks, leave_requests)
        chỉ bằng 1 câu truy vấn JOIN duy nhất để tối ưu I/O.
        """
        return db.session.query(Employee)\
            .options(
                joinedload(Employee.analytics),
                joinedload(Employee.tasks),
                joinedload(Employee.leave_requests)
            )\
            .filter(Employee.id == employee_id)\
            .first()

    def get_employee_attendance_features(self, employee_id: int, days_limit: int = 30) -> Dict[str, Any]:
        """
        Tính toán hiệu năng chấm công (chuyên cần, đi trễ) của nhân viên 30 ngày qua bằng SQL Aggregation.
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=days_limit)
        
        # Đếm số ngày đi làm và số lần đi trễ
        res = db.session.query(
            func.count(Attendance.id).label('present_days'),
            func.sum(db.case((Attendance.status == 'Late', 1), else_=0)).label('late_days')
        ).filter(
            Attendance.employee_id == employee_id,
            Attendance.work_date >= thirty_days_ago.date()
        ).first()
        
        present = res.present_days if res and res.present_days is not None else 0
        late = res.late_days if res and res.late_days is not None else 0
        
        return {
            'present_days': present,
            'late_days': late,
            'attendance_ratio': present / float(days_limit) if days_limit > 0 else 1.0,
            'late_ratio': late / float(present) if present > 0 else 0.0
        }

    def get_employee_task_features(self, employee_id: int) -> Dict[str, Any]:
        """
        Tính toán tỷ lệ hoàn thành task, trễ hạn task trung bình bằng SQL Aggregation.
        """
        res = db.session.query(
            func.count(Task.id).label('total_tasks'),
            func.sum(db.case((Task.status == 'Completed', 1), else_=0)).label('completed_tasks')
        ).filter(Task.employee_id == employee_id).first()
        
        total = res.total_tasks if res and res.total_tasks is not None else 0
        completed = res.completed_tasks if res and res.completed_tasks is not None else 0
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'task_completion_rate': completed / float(total) if total > 0 else 1.0
        }

    def get_employee_leave_features(self, employee_id: int, days_limit: int = 90) -> Dict[str, Any]:
        """
        Đếm số ngày nghỉ phép đã duyệt trong vòng 90 ngày qua.
        """
        ninety_days_ago = datetime.utcnow() - timedelta(days=days_limit)
        
        count = db.session.query(func.count(LeaveRequest.id))\
            .filter(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date >= ninety_days_ago.date()
            ).scalar() or 0
            
        return {
            'leave_count_90d': count
        }
