from app.repositories import (
    EmployeeRepository,
    DepartmentRepository,
    LeaveRepository,
    TaskRepository,
    RecruitmentRepository,
    UnitOfWork
)
from app.models import (
    Employee,
    Department,
    Candidate,
    Attendance,
    LeaveRequest,
    ExamResult,
    CandidateAnswer,
    JobPost,
    Exam,
    ExamQuestion,
    RolePermission,
    UserPermission,
    Task
)
from app.extensions import db
from app.core.exceptions import ValidationError, BusinessException, EntityNotFoundException
from email_service import send_passed_email, send_failed_email

from datetime import datetime
from typing import Dict, List, Any, Optional

class HRService:
    def __init__(self):
        self.employee_repo = EmployeeRepository()
        self.department_repo = DepartmentRepository()
        self.leave_repo = LeaveRepository()
        self.task_repo = TaskRepository()
        self.recruitment_repo = RecruitmentRepository()

    # --- NHÂN VIÊN ---
    def create_employee(self, form_data: Dict[str, Any]) -> Employee:
        employee_code = form_data.get('employee_code', '').strip()
        fullname = form_data.get('fullname', '').strip()
        username = form_data.get('username', '').strip()
        password = form_data.get('password', '').strip()
        email = form_data.get('email', '').strip()
        department_id = form_data.get('department_id')
        role = form_data.get('role', 'Employee')

        if not employee_code or not fullname or not username or not password:
            raise ValidationError("Vui lòng nhập đầy đủ thông tin bắt buộc.")

        if self.employee_repo.get_by_code(employee_code):
            raise ValidationError(f"Mã nhân viên {employee_code} đã tồn tại.")
        if self.employee_repo.get_by_username(username):
            raise ValidationError(f"Tên tài khoản {username} đã tồn tại.")

        new_emp = Employee(
            employee_code=employee_code,
            fullname=fullname,
            username=username,
            password=password,
            email=email,
            department_id=department_id,
            role=role
        )

        with UnitOfWork():
            self.employee_repo.add(new_emp)

        return new_emp

    def reset_password(self, emp_id: int) -> Employee:
        emp = self.employee_repo.get_by_id(emp_id)
        if not emp:
            raise EntityNotFoundException("Không tìm thấy nhân viên.")
        
        with UnitOfWork():
            emp.password = '123456'
            
        return emp

    def get_user_permissions(self, emp_id: int) -> Dict[str, Any]:
        emp = self.employee_repo.get_by_id(emp_id)
        if not emp:
            raise EntityNotFoundException("Không tìm thấy nhân viên.")
        
        all_perms_raw = db.session.query(RolePermission.permission_key).distinct().all()
        all_perms = [p[0] for p in all_perms_raw]
        
        if not all_perms:
            all_perms = ['VIEW_REPORTS', 'MANAGE_EMPLOYEES', 'APPROVE_LEAVE', 'MANAGE_RECRUITMENT']
            
        user_perms = {}
        for perm in all_perms:
            override = db.session.query(UserPermission).filter_by(user_id=emp_id, permission_key=perm).first()
            if override:
                user_perms[perm] = override.is_allowed
            else:
                role_p = db.session.query(RolePermission).filter_by(role_name=emp.role, permission_key=perm).first()
                user_perms[perm] = role_p.is_allowed if role_p else False
                
        return {
            'employee': emp,
            'all_perms': all_perms,
            'user_perms': user_perms
        }

    def update_user_permission(self, user_id: int, perm_key: str, value: bool):
        emp = self.employee_repo.get_by_id(user_id)
        if not emp:
            raise EntityNotFoundException("Không tìm thấy nhân viên.")

        with UnitOfWork():
            override = db.session.query(UserPermission).filter_by(user_id=user_id, permission_key=perm_key).first()
            if override:
                override.is_allowed = value
            else:
                new_override = UserPermission(user_id=user_id, permission_key=perm_key, is_allowed=value)
                db.session.add(new_override)

    # --- PHÒNG BAN ---
    def create_department(self, name: str, description: str) -> Department:
        name = name.strip()
        if not name:
            raise ValidationError("Tên phòng ban không được để trống.")

        new_dept = Department(name=name, description=description)
        
        with UnitOfWork():
            self.department_repo.add(new_dept)
            
        return new_dept

    def edit_department(self, dept_id: int, name: str, description: str):
        dept = self.department_repo.get_by_id(dept_id)
        if not dept:
            raise EntityNotFoundException("Không tìm thấy phòng ban.")
            
        name = name.strip()
        if not name:
            raise ValidationError("Tên phòng ban không được để trống.")
            
        with UnitOfWork():
            dept.name = name
            dept.description = description
            
    def delete_department(self, dept_id: int):
        dept = self.department_repo.get_by_id(dept_id)
        if not dept:
            raise EntityNotFoundException("Không tìm thấy phòng ban.")
            
        if dept.employees and len(dept.employees) > 0:
            raise BusinessException("Không thể xóa phòng ban đang có nhân viên.")
            
        with UnitOfWork():
            self.department_repo.delete(dept)
    # --- DUYỆT NGHỈ PHÉP ---
    def approve_or_reject_leave(self, req_id: int, action: str):
        leave_req = self.leave_repo.get_by_id_with_employee(req_id)
        if not leave_req:
            raise EntityNotFoundException("Không tìm thấy đơn xin nghỉ phép.")

        with UnitOfWork():
            if action == 'approve':
                leave_req.status = 'Approved'
                diff = (leave_req.end_date - leave_req.start_date).days + 1
                if leave_req.employee:
                    leave_req.employee.leave_days_used += diff
            elif action == 'reject':
                leave_req.status = 'Rejected'
            else:
                raise ValidationError("Thao tác duyệt không hợp lệ.")

    # --- TUYỂN DỤNG ---
    def decide_candidate(self, can_id: int, decision: str, notes: str, reviewer_id: int) -> Candidate:
        if decision not in ('Passed', 'Failed'):
            raise ValidationError("Quyết định duyệt ứng viên không hợp lệ.")

        candidate = self.recruitment_repo.get_candidate_by_id(can_id)
        if not candidate:
            raise EntityNotFoundException("Không tìm thấy ứng viên.")

        with UnitOfWork():
            candidate.status = decision
            candidate.notes = notes
            candidate.reviewed_at = datetime.utcnow()
            candidate.reviewed_by = reviewer_id

        if not candidate.email_sent:
            latest_result = candidate.results[-1] if candidate.results else None
            score = latest_result.score if latest_result else 0
            job_title = candidate.job.title if candidate.job else 'Chưa xác định'
            
            if decision == 'Passed':
                ok = send_passed_email(candidate.fullname, candidate.email, job_title, score)
            else:
                ok = send_failed_email(candidate.fullname, candidate.email, job_title, score)

            if ok:
                with UnitOfWork():
                    candidate.email_sent = True

        return candidate

    def save_exam_feedback(self, result_id: int, feedback: str):
        result = self.recruitment_repo.get_result_by_id(result_id)
        if not result:
            raise EntityNotFoundException("Không tìm thấy bài làm.")

        with UnitOfWork():
            result.hr_feedback = feedback.strip()
            result.status = 'Completed'

    def manage_jobs(self, action: str, job_id: Optional[int], form_data: Dict[str, Any]):
        if action == 'add':
            title = form_data.get('title', '').strip()
            desc = form_data.get('description', '').strip()
            reqs = form_data.get('requirements', '').strip()
            
            if not title:
                raise ValidationError("Tiêu đề công việc không được để trống.")
                
            with UnitOfWork():
                self.recruitment_repo.add_job_post(title, desc, reqs)

        elif action == 'edit' and job_id:
            job = self.recruitment_repo.get_job_by_id(job_id)
            if not job:
                raise EntityNotFoundException("Không tìm thấy tin tuyển dụng.")
                
            with UnitOfWork():
                job.title = form_data.get('title', '').strip()
                job.description = form_data.get('description', '').strip()
                job.requirements = form_data.get('requirements', '').strip()

        elif action == 'toggle_status' and job_id:
            job = self.recruitment_repo.get_job_by_id(job_id)
            if not job:
                raise EntityNotFoundException("Không tìm thấy tin tuyển dụng.")
                
            with UnitOfWork():
                job.status = 'Closed' if job.status == 'Open' else 'Open'

    def manage_exams(self, action: str, exam_id: Optional[int], form_data: Dict[str, Any]) -> Optional[Exam]:
        if action == 'add':
            title = form_data.get('title', '').strip()
            duration = int(form_data.get('duration_minutes', 30))
            pass_threshold = float(form_data.get('pass_threshold', 7.0))
            
            if not title:
                raise ValidationError("Tiêu đề bài thi không được để trống.")
                
            with UnitOfWork():
                exam = self.recruitment_repo.add_exam(title, duration, pass_threshold)
            return exam

        elif action == 'delete' and exam_id:
            exam = self.recruitment_repo.get_exam_by_id(exam_id)
            if not exam:
                raise EntityNotFoundException("Không tìm thấy bài thi.")
                
            with UnitOfWork():
                self.recruitment_repo.delete_exam(exam)
        return None

    def edit_exam(self, exam_id: int, action: str, form_data: Dict[str, Any]):
        exam = self.recruitment_repo.get_exam_by_id(exam_id)
        if not exam:
            raise EntityNotFoundException("Không tìm thấy bài thi.")

        with UnitOfWork():
            if action == 'update_exam':
                exam.title = form_data.get('title', '').strip()
                exam.duration_minutes = int(form_data.get('duration_minutes', 30))
                exam.pass_threshold = float(form_data.get('pass_threshold', 7.0))
            
            elif action == 'add_question':
                q_text = form_data.get('question_text', '').strip()
                q_type = form_data.get('question_type', 'MCQ')
                
                if not q_text:
                    raise ValidationError("Nội dung câu hỏi không được để trống.")
                
                option_a = form_data.get('option_a')
                option_b = form_data.get('option_b')
                option_c = form_data.get('option_c')
                option_d = form_data.get('option_d')
                correct_option = form_data.get('correct_option', '').upper()
                
                self.recruitment_repo.add_question(
                    exam_id=exam_id,
                    question_text=q_text,
                    question_type=q_type,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=correct_option,
                    order_num=len(exam.questions) + 1
                )

            elif action == 'delete_question':
                q_id = int(form_data.get('question_id', 0))
                q = self.recruitment_repo.get_question_by_id(q_id)
                if q:
                    self.recruitment_repo.delete_question(q)

    # --- NHIỆM VỤ (TASKS) ---
    def manage_tasks(self, action: str, task_id: Optional[int], form_data: Dict[str, Any]):
        with UnitOfWork():
            if action == 'add':
                employee_id = int(form_data.get('employee_id', 0))
                title = form_data.get('title', '').strip()
                desc = form_data.get('description', '').strip()
                category = form_data.get('category', 'Chung').strip()
                due_date_str = form_data.get('due_date')
                priority = form_data.get('priority', 'Medium')
                
                if not title or employee_id == 0:
                    raise ValidationError("Tiêu đề hoặc nhân viên giao nhiệm vụ không hợp lệ.")
                
                due_date = None
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                
                task = Task(
                    employee_id=employee_id,
                    title=title,
                    description=desc,
                    category=category,
                    due_date=due_date,
                    priority=priority
                )
                self.task_repo.add(task)

            elif action == 'edit' and task_id:
                task = self.task_repo.get_by_id(task_id)
                if not task:
                    raise EntityNotFoundException("Không tìm thấy nhiệm vụ.")
                    
                task.title = form_data.get('title', '').strip()
                task.description = form_data.get('description', '').strip()
                task.category = form_data.get('category', 'Chung').strip()
                task.priority = form_data.get('priority', 'Medium')
                task.status = form_data.get('status', 'Pending')
                
                due_date_str = form_data.get('due_date')
                if due_date_str:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')

            elif action == 'delete' and task_id:
                task = self.task_repo.get_by_id(task_id)
                if not task:
                    raise EntityNotFoundException("Không tìm thấy nhiệm vụ.")
                    
                self.task_repo.delete(task)
