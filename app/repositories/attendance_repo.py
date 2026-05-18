from app.repositories.base_repo import BaseRepository
from app.models import Attendance
from app.extensions import db
from datetime import datetime

class AttendanceRepository(BaseRepository):
    model = Attendance

    def get_today_attendance(self, employee_id):
        today = datetime.now().date()
        return db.session.query(Attendance).filter_by(employee_id=employee_id, work_date=today).first()

    def create_checkin(self, employee_id, work_date, check_in_time, check_in_photo, qr_code_token):
        att = Attendance(
            employee_id=employee_id,
            work_date=work_date,
            check_in=check_in_time,
            check_in_photo=check_in_photo,
            qr_code_token=qr_code_token,
            status='Normal'
        )
        self.add(att)
        return att

    def update_checkout(self, attendance_id, check_out_time, check_out_photo, qr_code_token):
        att = self.get_by_id(attendance_id)
        if att:
            att.check_out = check_out_time
            if check_out_photo:
                att.check_out_photo = check_out_photo
            if qr_code_token:
                att.qr_code_token = qr_code_token
        return att

    def get_attendance_by_date(self, employee_id, date):
        return db.session.query(Attendance).filter_by(employee_id=employee_id, work_date=date).first()

    def get_employee_attendance_logs(self, employee_id):
        return db.session.query(Attendance).filter_by(employee_id=employee_id).order_by(Attendance.work_date.desc()).all()

    def get_attendance_statistics(self, employee_id):
        logs = self.get_employee_attendance_logs(employee_id)
        total_days = len(logs)
        normal_days = sum(1 for log in logs if log.status == 'Normal')
        late_days = sum(1 for log in logs if log.status == 'Late')
        return {
            'total_days': total_days,
            'normal_days': normal_days,
            'late_days': late_days
        }
