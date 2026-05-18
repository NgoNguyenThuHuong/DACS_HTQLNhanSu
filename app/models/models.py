from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    employees = db.relationship('Employee', backref='department', lazy=True)

class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10), default='Nam')
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    hometown = db.Column(db.String(255))
    social_id = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    emergency_contact = db.Column(db.String(255))
    education = db.Column(db.String(100))
    marital_status = db.Column(db.String(50))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Admin', 'HR', 'Employee'), default='Employee')
    avatar = db.Column(db.String(255), default='default_avatar.png')
    leave_days_quota = db.Column(db.Integer, default=12)
    leave_days_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance = db.relationship('Attendance', backref='employee', lazy=True)
    tasks = db.relationship('Task', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Normal')
    check_in_photo = db.Column(db.String(255))
    check_out_photo = db.Column(db.String(255))
    qr_code_token = db.Column(db.String(100))

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.String(100), default='Nghi phep nam')
    reason = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='Chung')
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.Enum('Low', 'Medium', 'High'), default='Medium')
    status = db.Column(db.Enum('Pending', 'In_Progress', 'Completed'), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobPost(db.Model):
    __tablename__ = 'recruitment_jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    status = db.Column(db.Enum('Open', 'Closed'), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidates = db.relationship('Candidate', backref='job', lazy=True)

class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('recruitment_jobs.id'))
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    cv_path = db.Column(db.String(255))
    status = db.Column(db.Enum('Applied', 'Testing', 'Passed', 'Failed'), default='Applied')
    notes = db.Column(db.Text)
    email_sent = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship('ExamResult', backref='candidate', lazy=True)

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    pass_threshold = db.Column(db.Float, default=7.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('ExamQuestion', backref='exam', lazy=True)
    results = db.relationship('ExamResult', backref='exam', lazy=True)

class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('MCQ', 'Essay'), default='MCQ')
    order_num = db.Column(db.Integer, default=0)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(1))

class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    mcq_score = db.Column(db.Float, default=0)
    mcq_correct = db.Column(db.Integer, default=0)
    mcq_total = db.Column(db.Integer, default=0)
    hr_feedback = db.Column(db.Text)
    status = db.Column(db.Enum('Under_Review', 'Completed'), default='Under_Review')
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.relationship('CandidateAnswer', backref='result', lazy=True)

    @property
    def score(self):
        return round(self.mcq_score, 1) if self.mcq_score is not None else 0

    @property
    def passed(self):
        threshold = self.exam.pass_threshold if self.exam else 7.0
        return self.mcq_score >= threshold

class CandidateAnswer(db.Model):
    __tablename__ = 'candidate_answers'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('exam_results.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('exam_questions.id'), nullable=False)
    given_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    question = db.relationship('ExamQuestion', backref='answers', lazy=True)

class EmployeeAnalytics(db.Model):
    __tablename__ = 'employee_analytics'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    job_satisfaction = db.Column(db.Integer)  # 1-4
    monthly_income = db.Column(db.Float)
    overtime = db.Column(db.String(10)) # 'Yes' or 'No'
    distance_from_home = db.Column(db.Integer)
    performance_rating = db.Column(db.Integer) # 1-4
    
    employee = db.relationship('Employee', backref=db.backref('analytics', uselist=False))

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.Enum('Admin', 'HR', 'Employee'), nullable=False)
    permission_key = db.Column(db.String(100), nullable=False)
    is_allowed = db.Column(db.Boolean, default=False)

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    permission_key = db.Column(db.String(100), nullable=False)
    is_allowed = db.Column(db.Boolean, default=False)
