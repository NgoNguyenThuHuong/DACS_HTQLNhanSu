from typing import Dict, List, Any, Optional

def calculate_turnover_risk(job_satisfaction: Optional[int], overtime: Optional[str], 
                            monthly_income: Optional[float], recent_leaves_count: int, 
                            probation_status: int) -> Dict[str, Any]:
    """
    Thuật toán Heuristic / Rule-based ban đầu dự báo nguy cơ nghỉ việc của nhân viên.
    Đây là bước đệm chuẩn bị cho các mô hình Machine Learning thực tế sau này (như XGBoost).
    """
    score = 0
    reasons = []

    if job_satisfaction and job_satisfaction <= 2:
        score += 35
        reasons.append(f"Hài lòng thấp ({job_satisfaction}/4)")
    
    if overtime == 'Yes':
        score += 25
        reasons.append("Làm thêm giờ thường xuyên")
        
    if monthly_income and monthly_income < 5000:
        score += 20
        reasons.append("Thu nhập thấp")
        
    if recent_leaves_count >= 2:
        score += 20
        reasons.append("Tần suất nghỉ phép tăng cao")
        
    if probation_status == 1:
        score += 15
        reasons.append("Đang trong giai đoạn thử việc")

    if score > 100:
        score = 99

    level = 'HIGH' if score > 60 else ('MEDIUM' if score > 30 else 'LOW')
    color = 'danger' if score > 60 else ('warning' if score > 30 else 'success')

    return {
        'score': score,
        'level': level,
        'color': color,
        'reasons': reasons
    }

def calculate_performance(present_days: int, total_tasks: int, completed_tasks: int) -> Dict[str, Any]:
    """
    Tính toán chỉ số hiệu suất cá nhân dựa trên chuyên cần (Attendance) và công việc (Task).
    Công thức: 40% Chuyên cần + 60% Hoàn thành công việc.
    """
    att_score = min(100.0, (present_days / 22) * 100.0)
    task_score = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 100.0
    
    final_score = (att_score * 0.4) + (task_score * 0.6)
    final_score = round(max(0.0, min(100.0, final_score)), 1)

    return {
        'score': final_score,
        'att_score': round(att_score, 1),
        'task_score': round(task_score, 1)
    }

def calculate_radar_metrics(employees_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tổng hợp dữ liệu trung bình cho Radar Chart hệ thống.
    """
    labels = ["Hiệu suất", "Chuyên cần", "Hoàn thành Task", "Hài lòng", "Thâm niên", "Bảo mật"]
    
    if not employees_metrics:
        return {
            'labels': labels,
            'values': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'insight': "Không có dữ liệu tổng hợp hệ thống."
        }

    perf_total = 0.0
    att_total = 0.0
    task_total = 0.0
    satisfaction_total = 0.0
    
    count = len(employees_metrics)
    for m in employees_metrics:
        perf_total += m['perf_score']
        att_total += m['att_score']
        task_total += m['task_score']
        satisfaction_total += m['satisfaction_score']
        
    avg_values = [
        round(perf_total / count / 10.0, 1),
        round(att_total / count / 10.0, 1),
        round(task_total / count / 10.0, 1),
        round(satisfaction_total / count / 10.0, 1),
        8.5,
        9.0
    ]

    return {
        'labels': labels,
        'values': avg_values,
        'insight': "Dữ liệu được tổng hợp từ hiệu suất thực tế và báo cáo chuyên cần của toàn bộ nhân viên."
    }
