import random
from app import create_app
from app.extensions import db
from app.models import Employee, Department

def randomize_departments():
    app = create_app()
    with app.app_context():
        employees = Employee.query.all()
        departments = Department.query.all()
        
        if not departments:
            print("Không có phòng ban nào trong hệ thống! Vui lòng tạo phòng ban trước.")
            return
            
        dept_ids = [d.id for d in departments]
        
        for emp in employees:
            # Optionally, don't change Admin role department if needed, but let's just change everyone
            # or we can check if they are not Admin to keep it safe. Let's just randomize all for now.
            emp.department_id = random.choice(dept_ids)
            
        db.session.commit()
        
        # In ra số lượng nhân sự mỗi phòng ban
        print(f"Đã phân bổ ngẫu nhiên {len(employees)} nhân sự vào {len(departments)} phòng ban.")
        for d in departments:
            count = Employee.query.filter_by(department_id=d.id).count()
            print(f"- {d.name}: {count} nhân sự")

if __name__ == "__main__":
    randomize_departments()
