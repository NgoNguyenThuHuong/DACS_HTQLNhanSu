import random
from app import create_app
from app.extensions import db
from app.models import Employee

vietnamese_ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
vietnamese_dem_nam = ["Văn", "Hữu", "Đức", "Công", "Quang", "Minh", "Xuân", "Thành", "Hoàng", "Trọng"]
vietnamese_dem_nu = ["Thị", "Ngọc", "Thu", "Phương", "Thanh", "Bích", "Hồng", "Mai", "Như", "Diễm"]
vietnamese_ten_nam = ["Anh", "Bảo", "Cường", "Dũng", "Đạt", "Hải", "Hào", "Hiếu", "Hùng", "Huy", "Khang", "Khánh", "Khoa", "Kiên", "Lâm", "Long", "Nam", "Phong", "Phúc", "Quân", "Sơn", "Thái", "Thắng", "Thịnh", "Tiến", "Toàn", "Trí", "Trung", "Tuấn", "Tùng", "Việt", "Vinh"]
vietnamese_ten_nu = ["An", "Anh", "Chi", "Châu", "Diệp", "Hà", "Hân", "Hoa", "Huyền", "Lan", "Linh", "Ly", "Mai", "My", "Nga", "Ngân", "Nhung", "Oanh", "Quyên", "Tâm", "Thảo", "Thi", "Thủy", "Tiên", "Trang", "Trâm", "Tú", "Uyên", "Vân", "Vy", "Yến"]

positions = [
    "Nhân viên văn phòng", "Chuyên viên IT", "Lập trình viên", "Kỹ sư phần mềm", 
    "Chuyên viên nhân sự", "Kế toán viên", "Nhân viên Marketing", "Trưởng phòng", 
    "Chuyên viên phân tích", "Nhân viên kinh doanh", "Kỹ thuật viên", "Chuyên gia dữ liệu",
    "Chuyên viên chăm sóc khách hàng", "Trợ lý giám đốc", "Nhân viên thiết kế"
]

def generate_vn_name():
    is_male = random.choice([True, False])
    ho = random.choice(vietnamese_ho)
    if is_male:
        dem = random.choice(vietnamese_dem_nam)
        ten = random.choice(vietnamese_ten_nam)
    else:
        dem = random.choice(vietnamese_dem_nu)
        ten = random.choice(vietnamese_ten_nu)
    return f"{ho} {dem} {ten}"

def rename_to_vn():
    app = create_app()
    with app.app_context():
        employees = Employee.query.all()
        count = 0
        for emp in employees:
            if emp.username not in ['admin', 'quanly', 'nhanvien'] and 'test' not in (emp.username or ''):
                emp.fullname = generate_vn_name()
                emp.position = random.choice(positions)
                count += 1
        db.session.commit()
        print(f"Updated {count} employees to Vietnamese names.")

if __name__ == "__main__":
    rename_to_vn()
