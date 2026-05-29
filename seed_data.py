import os
import random
import string
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.models import Employee, Attendance, EmployeeAnalytics, Task, Department
from faker import Faker
import math

fake = Faker()

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_seed():
    app = create_app()
    with app.app_context():
        # Clean existing mock data safely (only for AI evaluation employees)
        print("Cleaning previous AI seed data...")
        employees_to_delete = Employee.query.filter(Employee.email.like('%@seed.local')).all()
        emp_ids = [e.id for e in employees_to_delete]
        if emp_ids:
            Task.query.filter(Task.employee_id.in_(emp_ids)).delete(synchronize_session=False)
            Attendance.query.filter(Attendance.employee_id.in_(emp_ids)).delete(synchronize_session=False)
            EmployeeAnalytics.query.filter(EmployeeAnalytics.employee_id.in_(emp_ids)).delete(synchronize_session=False)
            Employee.query.filter(Employee.id.in_(emp_ids)).delete(synchronize_session=False)
            db.session.commit()

        # Create some departments if empty
        dept = Department.query.first()
        if not dept:
            dept = Department(name="IT", description="IT Department")
            db.session.add(dept)
            db.session.commit()

        print("Seeding new employees...")
        employees = []
        statuses = ['Active'] * 85 + ['Resigned'] * 15
        random.shuffle(statuses)

        for i, status in enumerate(statuses):
            # Noise addition: not all resigned are bad, not all active are perfect.
            is_anomaly = random.random() < 0.15 # 15% chance to break the expected pattern

            if status == 'Resigned':
                # Generally bad stats, unless anomaly
                yic = round(random.uniform(0.5, 3.0) if not is_anomaly else random.uniform(3.0, 10.0), 1)
                satisfaction = random.choice([1, 2]) if not is_anomaly else random.choice([3, 4])
                perf = random.choice([1, 2]) if not is_anomaly else random.choice([3, 4])
                overtime_flag = 'Yes' if random.random() < 0.7 else 'No' # Often burn out
            else:
                # Generally good stats, unless anomaly
                yic = round(random.uniform(1.0, 10.0) if not is_anomaly else random.uniform(0.5, 2.0), 1)
                satisfaction = random.choice([3, 4]) if not is_anomaly else random.choice([1, 2])
                perf = random.choice([3, 4]) if not is_anomaly else random.choice([1, 2])
                overtime_flag = 'No' if random.random() < 0.8 else 'Yes' # Usually normal

            emp = Employee(
                employee_code=f'SEED{i+1:03d}_{generate_random_string(4)}',
                fullname=fake.name(),
                email=f'seed_{i}_{generate_random_string(4)}@seed.local',
                phone=fake.phone_number()[:15],
                department_id=dept.id,
                position=fake.job()[:100],
                username=f'seed_{i}_{generate_random_string(4)}',
                role='Employee',
                employment_status=status,
                years_in_company=yic
            )
            employees.append((emp, status, is_anomaly, satisfaction, perf, overtime_flag))

        # We need IDs, so commit employees first
        emp_objs = [e[0] for e in employees]
        db.session.add_all(emp_objs)
        db.session.commit()

        print("Seeding Analytics...")
        analytics_list = []
        for emp, status, is_anomaly, satisfaction, perf, overtime_flag in employees:
            salary = random.uniform(1000, 3000)
            if status == 'Resigned' and not is_anomaly:
                salary = random.uniform(800, 1500) # Often lower pay

            dist = random.randint(2, 20)
            if status == 'Resigned' and random.random() < 0.3:
                dist = random.randint(15, 30) # Sometimes far away

            analytics_list.append(EmployeeAnalytics(
                employee_id=emp.id,
                job_satisfaction=satisfaction,
                monthly_income=salary,
                overtime=overtime_flag,
                distance_from_home=dist,
                performance_rating=perf
            ))
        db.session.add_all(analytics_list)
        db.session.commit()

        print("Seeding Tasks & Attendance (this might take a bit)...")
        # Generate last 6 months of attendance
        today = datetime.now().date()
        start_date = today - timedelta(days=180)
        
        attendance_records = []
        task_records = []

        for emp, status, is_anomaly, satisfaction, perf, overtime_flag in employees:
            # Task completion probability based on performance
            base_task_prob = 0.9 if perf >= 3 else 0.6
            
            for t_idx in range(random.randint(20, 50)):
                is_completed = random.random() < base_task_prob
                task_status = 'Completed' if is_completed else random.choice(['Pending', 'In_Progress'])
                task_records.append(Task(
                    employee_id=emp.id,
                    title=f'Task {t_idx} for {emp.fullname}',
                    category=random.choice(['Development', 'Meeting', 'Review', 'Support']),
                    status=task_status
                ))

            # Attendance logic
            current_date = start_date
            while current_date <= today:
                # Skip weekends
                if current_date.weekday() < 5:
                    is_late = False
                    is_absent = False
                    
                    if status == 'Resigned' and not is_anomaly:
                        is_late = random.random() < 0.3  # 30% late
                        is_absent = random.random() < 0.05
                    else:
                        is_late = random.random() < 0.05 # 5% late
                        is_absent = random.random() < 0.01

                    if not is_absent:
                        check_in_base = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=8)
                        if is_late:
                            check_in = check_in_base + timedelta(minutes=random.randint(15, 120))
                        else:
                            check_in = check_in_base - timedelta(minutes=random.randint(0, 30))

                        # Overtime?
                        check_out_base = check_in_base + timedelta(hours=9) # 1 hour break
                        has_ot_today = (overtime_flag == 'Yes' and random.random() < 0.4)
                        
                        if has_ot_today:
                            ot_hours = random.uniform(1.0, 4.0)
                            check_out = check_out_base + timedelta(hours=ot_hours)
                        else:
                            ot_hours = 0.0
                            check_out = check_out_base + timedelta(minutes=random.randint(0, 30))

                        work_hours = (check_out - check_in).total_seconds() / 3600 - 1.0 # Minus break
                        
                        attendance_records.append(Attendance(
                            employee_id=emp.id,
                            work_date=current_date,
                            check_in=check_in,
                            check_out=check_out,
                            status='Late' if is_late else 'Normal',
                            total_work_hours=max(0.0, work_hours),
                            overtime_hours=ot_hours
                        ))

                current_date += timedelta(days=1)
                
            if len(attendance_records) > 5000:
                db.session.add_all(attendance_records)
                db.session.commit()
                attendance_records = []
                
        # Final flush
        if attendance_records:
            db.session.add_all(attendance_records)
        if task_records:
            db.session.add_all(task_records)
        db.session.commit()

        print("Seed data generated successfully.")

if __name__ == '__main__':
    run_seed()
