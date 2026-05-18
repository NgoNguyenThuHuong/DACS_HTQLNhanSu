from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class EmployeeDTO:
    id: int
    employee_code: str
    fullname: str
    username: str
    email: str
    role: str
    avatar: str
    department_name: str
    position: str

@dataclass
class DepartmentDTO:
    id: int
    name: str
    description: str
    employee_count: int

@dataclass
class LeaveRequestDTO:
    id: int
    employee_id: int
    fullname: str
    leave_type: str
    start_date: str
    end_date: str
    reason: str
    status: str
    duration_days: int

@dataclass
class TaskDTO:
    id: int
    employee_id: int
    fullname: str
    title: str
    description: str
    category: str
    due_date: Optional[str]
    priority: str
    status: str

@dataclass
class CandidateDTO:
    id: int
    fullname: str
    email: str
    phone: str
    job_title: str
    status: str
    score: float
    created_at: str
    notes: str
    email_sent: bool

@dataclass
class EmployeeFeatureDTO:
    """DTO chuẩn hóa đặc trưng (Feature Vector) cho pipeline huấn luyện AI/ML"""
    employee_id: int
    fullname: str
    position_title: str
    department_name: str
    birthday_year: Optional[int]
    gender_male: int
    job_satisfaction_score: float  # Scale 1-4 -> normalized to float
    monthly_income_amount: float
    overtime_ratio_30d: float       # 0.0 or 1.0 (binary or ratio)
    distance_from_home_km: float
    performance_rating_score: float
    attendance_ratio_30d: float    # Tỷ lệ ngày chuyên cần 30 ngày qua
    late_ratio_30d: float          # Tỷ lệ đi muộn 30 ngày qua
    task_completion_rate: float    # Tỷ lệ hoàn thành task
    leave_frequency_90d: int       # Số lần xin nghỉ phép trong 90 ngày
    probation_status: int          # 1 nếu thâm niên < 90 ngày (thử việc), ngược lại 0
    turnover_risk_score: float     # Điểm nguy cơ nghỉ việc
    turnover_risk_level: str       # HIGH, MEDIUM, LOW
