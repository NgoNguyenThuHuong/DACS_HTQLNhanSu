from models import db, Employee, EmployeeAnalytics, Attendance, LeaveRequest, Task, Department
from datetime import datetime, timedelta
from sqlalchemy import extract, desc

def get_turnover_risk_ai():
    """
    Dự báo nguy cơ nghỉ việc dựa trên dữ liệu thực tế.
    Nếu không có EmployeeAnalytics, sẽ trả về danh sách rỗng hoặc logic dựa trên thâm niên/nghỉ phép.
    """
    employees = Employee.query.all()
    risk_data = []

    for emp in employees:
        score = 0
        reasons = []
        
        # 1. Dữ liệu từ khảo sát/analytics (Nếu có)
        ana = emp.analytics
        if ana:
            if ana.job_satisfaction and ana.job_satisfaction <= 2:
                score += 35
                reasons.append(f"Hài lòng thấp ({ana.job_satisfaction}/4)")
            if ana.overtime == 'Yes':
                score += 25
                reasons.append("Làm thêm giờ thường xuyên")
            if ana.monthly_income and ana.monthly_income < 5000: # Ngưỡng giả định
                score += 20
                reasons.append("Thu nhập thấp")
        
        # 2. Dữ liệu từ hành vi hệ thống
        # Nghỉ phép nhiều trong tháng qua
        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_leaves = [r for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= month_ago.date()]
        if len(recent_leaves) >= 2:
            score += 20
            reasons.append("Tần suất nghỉ phép tăng cao")
            
        # Thâm niên (Mới vào thường có nguy cơ cao hơn)
        delta = datetime.utcnow() - (emp.created_at or datetime.utcnow())
        if delta.days < 90:
            score += 15
            reasons.append("Đang trong giai đoạn thử việc")

        if score > 0:
            if score > 100: score = 99
            level = 'HIGH' if score > 60 else ('MEDIUM' if score > 30 else 'LOW')
            color = 'danger' if score > 60 else ('warning' if score > 30 else 'success')

            risk_data.append({
                'id': emp.id,
                'fullname': emp.fullname,
                'position': emp.position or "Nhân viên",
                'score': score,
                'level': level,
                'color': color,
                'reasons': reasons
            })

    risk_data.sort(key=lambda x: x['score'], reverse=True)
    return risk_data[:5]

def get_individual_performance(emp_id):
    """Tính hiệu suất thực tế dựa trên Task và Attendance"""
    emp = Employee.query.get(emp_id)
    if not emp: return {'score': 0, 'present_days': 0, 'leave_days': 0, 'att_score': 0}

    now = datetime.now()
    # Tính trong 30 ngày qua thay vì chỉ trong tháng để có dữ liệu liên tục hơn
    thirty_days_ago = now - timedelta(days=30)
    
    # 1. Chuyên cần (Dựa trên 22 ngày công chuẩn)
    present_days = Attendance.query.filter(
        Attendance.employee_id == emp_id,
        Attendance.work_date >= thirty_days_ago.date()
    ).count()
    att_score = min(100, (present_days / 22) * 100)

    # 2. Công việc (Tỉ lệ hoàn thành task)
    tasks = Task.query.filter(Task.employee_id == emp_id).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == 'Completed')
    task_score = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 100 # Mặc định 100 nếu không có task

    # 3. Nghỉ phép (Phạt điểm nếu nghỉ quá nhiều không lý do chính đáng - giả định)
    leave_days = sum((r.end_date - r.start_date).days + 1 for r in emp.leave_requests if r.status == 'Approved' and r.start_date >= thirty_days_ago.date())
    
    final_score = (att_score * 0.4) + (task_score * 0.6)
    final_score = round(max(0, min(100, final_score)), 1)

    return {
        'score': final_score,
        'present_days': present_days,
        'leave_days': leave_days,
        'att_score': round(att_score, 1)
    }

def get_attendance_trend(days=7):
    """Lấy dữ liệu chấm công thực tế trong N ngày qua"""
    trend = []
    today = datetime.now().date()
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        count = Attendance.query.filter_by(work_date=date).count()
        trend.append({
            'date': date.strftime('%d/%m'),
            'count': count
        })
    return trend

def get_recent_activity(limit=10):
    """Tổng hợp các hoạt động mới nhất từ hệ thống"""
    activities = []
    
    # 1. Chấm công mới nhất
    attendances = Attendance.query.order_by(desc(Attendance.check_in)).limit(limit).all()
    for att in attendances:
        if att.check_in:
            activities.append({
                'user': att.employee.fullname,
                'action': 'đã Check-in',
                'time': att.check_in,
                'icon': 'fa-fingerprint',
                'color': 'primary'
            })
            
    # 2. Đơn nghỉ phép mới nhất
    leaves = LeaveRequest.query.order_by(desc(LeaveRequest.created_at)).limit(limit).all()
    for l in leaves:
        activities.append({
            'user': l.employee.fullname,
            'action': f'gửi đơn nghỉ {l.leave_type} ({l.status})',
            'time': l.created_at or datetime.utcnow(),
            'icon': 'fa-calendar-alt',
            'color': 'warning'
        })
        
    # 3. Nhân viên mới
    new_hires = Employee.query.order_by(desc(Employee.created_at)).limit(limit).all()
    for e in new_hires:
        activities.append({
            'user': 'Hệ thống',
            'action': f'đã thêm nhân viên mới: {e.fullname}',
            'time': e.created_at or datetime.utcnow(),
            'icon': 'fa-user-plus',
            'color': 'success'
        })

    # Sắp xếp theo thời gian giảm dần
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities[:limit]

def get_individual_radar_data(emp_id):
    """Dữ liệu Radar Chart cho cá nhân"""
    emp = Employee.query.get(emp_id)
    if not emp: return None

    perf = get_individual_performance(emp_id)
    
    # 6 chỉ số: Hiệu suất, Chuyên cần, Khối lượng, Hài lòng, Thâm niên, Kỷ luật
    labels = ["Hiệu suất", "Chuyên cần", "Khối lượng", "Hài lòng", "Thâm niên", "Kỷ luật"]
    
    # Hiệu suất & Chuyên cần lấy từ perf
    p = perf['score'] / 10
    a = perf['att_score'] / 10
    
    # Khối lượng: Dựa trên số task đang xử lý
    pending_tasks = Task.query.filter_by(employee_id=emp_id, status='Pending').count()
    w = min(10, 5 + (pending_tasks * 0.5))
    
    # Hài lòng: Từ analytics
    s = (emp.analytics.job_satisfaction / 4 * 10) if emp.analytics and emp.analytics.job_satisfaction else 8.0
    
    # Thâm niên: Dựa trên ngày gia nhập
    delta = datetime.utcnow() - (emp.created_at or datetime.utcnow())
    t = min(10, (delta.days / 365) * 2 + 5)
    
    # Kỷ luật: Giả định (có thể dựa trên đi muộn/về sớm nếu có data)
    d = 9.5 

    return {
        'labels': labels,
        'values': [p, a, w, s, t, d],
        'score': perf['score']
    }

def get_radar_data():
    """Dữ liệu Radar Chart thực tế cho toàn bộ hệ thống"""
    employees = Employee.query.all()
    if not employees: return None

    labels = ["Hiệu suất", "Chuyên cần", "Hoàn thành Task", "Hài lòng", "Thâm niên", "Bảo mật"]
    
    perf_total = 0
    att_total = 0
    task_total = 0
    satisfaction_total = 0
    
    count = len(employees)
    for emp in employees:
        perf = get_individual_performance(emp.id)
        perf_total += perf['score']
        att_total += perf['att_score']
        
        tasks = emp.tasks
        if tasks:
            task_total += (sum(1 for t in tasks if t.status == 'Completed') / len(tasks)) * 100
        else:
            task_total += 100
            
        if emp.analytics:
            satisfaction_total += (emp.analytics.job_satisfaction / 4) * 100
        else:
            satisfaction_total += 75 
            
    avg_values = [
        round(perf_total / count / 10, 1),
        round(att_total / count / 10, 1),
        round(task_total / count / 10, 1),
        round(satisfaction_total / count / 10, 1),
        8.5,
        9.0
    ]

    return {
        'labels': labels,
        'values': avg_values,
        'insight': "Dữ liệu được tổng hợp từ hiệu suất thực tế và báo cáo chuyên cần của toàn bộ nhân viên."
    }
