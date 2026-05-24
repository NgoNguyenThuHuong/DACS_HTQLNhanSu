from app import create_app
from database.models import Department, Employee, JobPost, Exam, ExamQuestion, Attendance, LeaveRequest, Candidate, Task, ExamResult, EmployeeAnalytics, RolePermission, UserPermission, Shift, AttendanceLog, AttendanceAnomaly
from core.extensions import db
from datetime import datetime, time
from sqlalchemy import create_engine, text

# Create database if not exists
engine = create_engine('mysql+mysqlconnector://root:@localhost:3306')
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS ql_nhansu"))
    print("Da dam bao co so du lieu ql_nhansu ton tai.")

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()

    # Fix: Ensure recruitment columns exist in 'candidates' table (for existing databases)
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('candidates')]
        
        # Ensure new compatibility snapshot columns exist in 'attendance' table
        att_columns = [c['name'] for c in inspector.get_columns('attendance')]
        if 'total_work_hours' not in att_columns:
            db.session.execute(text("ALTER TABLE attendance ADD COLUMN total_work_hours FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("Da bo sung cot 'total_work_hours' vao bang 'attendance'.")
        if 'total_break_minutes' not in att_columns:
            db.session.execute(text("ALTER TABLE attendance ADD COLUMN total_break_minutes FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("Da bo sung cot 'total_break_minutes' vao bang 'attendance'.")
        if 'overtime_hours' not in att_columns:
            db.session.execute(text("ALTER TABLE attendance ADD COLUMN overtime_hours FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("Da bo sung cot 'overtime_hours' vao bang 'attendance'.")
        
        # List of columns to check and add
        required_cols = {
            'notes': "ALTER TABLE candidates ADD COLUMN notes TEXT AFTER status",
            'email_sent': "ALTER TABLE candidates ADD COLUMN email_sent BOOLEAN DEFAULT FALSE AFTER notes",
            'reviewed_at': "ALTER TABLE candidates ADD COLUMN reviewed_at DATETIME AFTER email_sent",
            'reviewed_by': "ALTER TABLE candidates ADD COLUMN reviewed_by INT AFTER reviewed_at"
        }
        
        for col, sql in required_cols.items():
            if col not in columns:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Da bo sung cot '{col}' vao bang 'candidates'.")
        
        # Ensure 'avatar' column exists in 'employees' table
        emp_columns = [c['name'] for c in inspector.get_columns('employees')]
        if 'avatar' not in emp_columns:
            db.session.execute(text("ALTER TABLE employees ADD COLUMN avatar VARCHAR(255) DEFAULT 'default_avatar.png' AFTER role"))
            db.session.commit()
            print("Da bo sung cot 'avatar' vao bang 'employees'.")
        
        # Ensure exam_results columns exist
        res_columns = [c['name'] for c in inspector.get_columns('exam_results')]
        required_res_cols = {
            'mcq_score': "ALTER TABLE exam_results ADD COLUMN mcq_score FLOAT DEFAULT 0 AFTER exam_id",
            'mcq_correct': "ALTER TABLE exam_results ADD COLUMN mcq_correct INT DEFAULT 0 AFTER mcq_score",
            'mcq_total': "ALTER TABLE exam_results ADD COLUMN mcq_total INT DEFAULT 0 AFTER mcq_correct"
        }
        for col, sql in required_res_cols.items():
            if col not in res_columns:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Da bo sung cot '{col}' vao bang 'exam_results'.")

        # Ensure exams columns exist
        exam_columns = [c['name'] for c in inspector.get_columns('exams')]
        if 'pass_threshold' not in exam_columns:
            db.session.execute(text("ALTER TABLE exams ADD COLUMN pass_threshold FLOAT DEFAULT 7.0 AFTER duration_minutes"))
            db.session.commit()
            print("Da bo sung cot 'pass_threshold' vao bang 'exams'.")

        # Ensure exam_questions columns exist
        q_columns = [c['name'] for c in inspector.get_columns('exam_questions')]
        required_q_cols = {
            'question_type': "ALTER TABLE exam_questions ADD COLUMN question_type ENUM('MCQ', 'Essay') DEFAULT 'MCQ' AFTER question_text",
            'order_num': "ALTER TABLE exam_questions ADD COLUMN order_num INT DEFAULT 0 AFTER question_type",
            'option_a': "ALTER TABLE exam_questions ADD COLUMN option_a VARCHAR(255) AFTER order_num",
            'option_b': "ALTER TABLE exam_questions ADD COLUMN option_b VARCHAR(255) AFTER option_a",
            'option_c': "ALTER TABLE exam_questions ADD COLUMN option_c VARCHAR(255) AFTER option_b",
            'option_d': "ALTER TABLE exam_questions ADD COLUMN option_d VARCHAR(255) AFTER option_c",
            'correct_option': "ALTER TABLE exam_questions ADD COLUMN correct_option VARCHAR(1) AFTER option_d"
        }
        for col, sql in required_q_cols.items():
            if col not in q_columns:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Da bo sung cot '{col}' vao bang 'exam_questions'.")

        # Ensure tasks columns exist
        task_columns = [c['name'] for c in inspector.get_columns('tasks')]
        if 'description' not in task_columns:
            db.session.execute(text("ALTER TABLE tasks ADD COLUMN description TEXT AFTER title"))
            db.session.commit()
            print("Da bo sung cot 'description' vao bang 'tasks'.")
        if 'category' not in task_columns:
            db.session.execute(text("ALTER TABLE tasks ADD COLUMN category VARCHAR(50) DEFAULT 'Chung' AFTER description"))
            db.session.commit()
            print("Da bo sung cot 'category' vao bang 'tasks'.")
        
        # Update status enum for tasks if needed
        # Note: MySQL ENUM modification is a bit tricky, but usually adding values is fine.
        try:
            db.session.execute(text("ALTER TABLE tasks MODIFY COLUMN status ENUM('Pending', 'In_Progress', 'Completed') DEFAULT 'Pending'"))
            db.session.commit()
        except:
            pass

    except Exception as e:
        print(f"Loi khi kiem tra/cap nhat schema: {e}")
    
    # Check if data already exists
    if Department.query.first():
        print("Du lieu da ton tai.")
    else:
        # 1. Departments
        d1 = Department(name='Phòng Kỹ thuật', description='Phát triển phần mềm')
        d2 = Department(name='Phòng Nhân sự', description='Tuyển dụng và đào tạo')
        db.session.add_all([d1, d2])
        db.session.commit()
        
        # 2. Admin User
        admin = Employee(
            employee_code='NV001',
            fullname='Quản trị viên',
            username='admin',
            password='123',
            role='Admin',
            department_id=d2.id
        )
        # 3. HR User
        hr_emp = Employee(
            employee_code='NV002',
            fullname='Nguyễn Thị HR',
            username='hr',
            password='123',
            role='HR',
            department_id=d2.id
        )
        db.session.add_all([admin, hr_emp])
        
    # Check and add sample Job & Exam if missing
    if not JobPost.query.first():
        job = JobPost(title='Lập trình viên Python (Flask)', description='Phát triển hệ thống HRM thông minh.', status='Open')
        db.session.add(job)
        db.session.commit()
        print("Da tao tin tuyen dung mau.")

    if not Exam.query.first():
        exam = Exam(title='Kiểm tra Tư duy Lập trình', duration_minutes=15, pass_threshold=7.0)
        db.session.add(exam)
        db.session.commit()
        print("Da tao bai thi mau.")
        
        q1 = ExamQuestion(
            exam_id=exam.id,
            question_text='Flask là gì?',
            question_type='MCQ',
            option_a='Một thư viện JS',
            option_b='Một Web Framework cho Python',
            option_c='Một hệ quản trị CSDL',
            option_d='Một ngôn ngữ lập trình',
            correct_option='B',
            order_num=1
        )
        q2 = ExamQuestion(
            exam_id=exam.id,
            question_text='Tại sao bạn chọn công ty chúng tôi?',
            question_type='Essay',
            order_num=2
        )
        db.session.add_all([q1, q2])
        db.session.commit()
        print("Da tao cau hoi mau.")

    # Seed default shifts if none exist
    if not Shift.query.first():
        s1 = Shift(name='Morning Shift', start_time=time(8, 0), end_time=time(12, 0), is_overnight=False)
        s2 = Shift(name='Afternoon Shift', start_time=time(13, 0), end_time=time(17, 0), is_overnight=False)
        s3 = Shift(name='Overtime Shift', start_time=time(18, 0), end_time=time(21, 0), is_overnight=False)
        s4 = Shift(name='Overnight Shift', start_time=time(22, 0), end_time=time(6, 0), is_overnight=True)
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()
        print("Da khoi tao cac ca lam viec enterprise mac dinh.")

    print("Kiem tra/Khoi tao du lieu hoan tat!")
