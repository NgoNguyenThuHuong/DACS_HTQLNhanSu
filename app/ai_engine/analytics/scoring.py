from typing import Dict, Any

def score_overall_index(attendance_score: float, task_completion_rate: float, satisfaction_score: float) -> float:
    """
    Tính điểm chỉ số tổng hợp của nhân viên dựa trên các trọng số nghiệp vụ.
    """
    score = (attendance_score * 0.35) + (task_completion_rate * 0.45) + (satisfaction_score * 0.20)
    return round(score, 2)
