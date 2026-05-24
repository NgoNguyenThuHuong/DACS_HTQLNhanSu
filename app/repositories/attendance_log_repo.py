from app.repositories.base_repo import BaseRepository
from app.models.models import AttendanceLog, AttendanceAnomaly
from app.extensions import db
from datetime import datetime, time

class AttendanceLogRepository(BaseRepository):
    model = AttendanceLog

    def get_logs_by_employee_and_date_range(self, employee_id, start_date, end_date):
        # start_date and end_date are date objects
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        return db.session.query(AttendanceLog).filter(
            AttendanceLog.employee_id == employee_id,
            AttendanceLog.timestamp >= start_dt,
            AttendanceLog.timestamp <= end_dt
        ).order_by(AttendanceLog.timestamp.asc()).all()

    def get_latest_log(self, employee_id):
        return db.session.query(AttendanceLog).filter_by(
            employee_id=employee_id
        ).order_by(AttendanceLog.timestamp.desc()).first()

    def get_latest_success_log(self, employee_id, now_dt=None):
        if now_dt is None:
            now_dt = datetime.now()
        return db.session.query(AttendanceLog).outerjoin(
            AttendanceAnomaly, AttendanceLog.id == AttendanceAnomaly.attendance_log_id
        ).filter(
            AttendanceLog.employee_id == employee_id,
            AttendanceAnomaly.id == None,
            AttendanceLog.timestamp <= now_dt
        ).order_by(AttendanceLog.timestamp.desc()).first()

    def create_log(self, employee_id, timestamp, action_type, shift_id=None,
                   verification_type='face', face_confidence=None,
                   latitude=None, longitude=None, device_id=None, photo_path=None):
        if device_id:
            device_id = str(device_id)[:255]
        log = AttendanceLog(
            employee_id=employee_id,
            timestamp=timestamp,
            action_type=action_type,
            shift_id=shift_id,
            verification_type=verification_type,
            face_confidence=face_confidence,
            latitude=latitude,
            longitude=longitude,
            device_id=device_id,
            photo_path=photo_path
        )
        self.add(log)
        return log

    def create_anomaly(self, employee_id, log_id, anomaly_type, description):
        anomaly = AttendanceAnomaly(
            employee_id=employee_id,
            attendance_log_id=log_id,
            anomaly_type=anomaly_type,
            description=description,
            resolved=False
        )
        db.session.add(anomaly)
        return anomaly
