import base64
import os
import io
import uuid
import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app.core.exceptions import ValidationError, AIVerificationError, BusinessException
from app.repositories import AttendanceRepository, ShiftRepository, AttendanceLogRepository, UnitOfWork
from app.services.attendance_policies import CooldownPolicy, StateMachinePolicy, ShiftPolicy
from app.services.attendance_session_service import AttendanceSessionService
from app.extensions import db

class AttendanceService:
    def __init__(self):
        self.attendance_repo = AttendanceRepository()
        self.shift_repo = ShiftRepository()
        self.attendance_log_repo = AttendanceLogRepository()
        self.session_service = AttendanceSessionService()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def verify_and_record_attendance(self, employee_id, employee_fullname, employee_code, 
                                     department_name, position_str, action, image_base64, upload_folder,
                                     latitude=None, longitude=None, device_id=None):
        if not image_base64:
            raise ValidationError("Không nhận được ảnh xác thực.")
        if action not in ['check_in', 'check_out']:
            raise ValidationError("Thao tác chấm công không hợp lệ.")

        now = datetime.now()
        today = now.date()
        action_mapped = 'CHECK_IN' if action == 'check_in' else 'CHECK_OUT'

        # Cooldown check
        latest_log = self.attendance_log_repo.get_latest_success_log(employee_id, now_dt=now)
        CooldownPolicy.validate(latest_log, now)

        # State Machine transition check
        current_state = StateMachinePolicy.get_current_state(latest_log)
        is_valid, anomaly_type, description = StateMachinePolicy.validate_transition(current_state, action_mapped)
        
        if not is_valid:
            with UnitOfWork():
                # Persist the invalid log and register anomaly in event stream
                log_err = self.attendance_log_repo.create_log(
                    employee_id=employee_id,
                    timestamp=now,
                    action_type=action_mapped,
                    verification_type='face',
                    latitude=latitude,
                    longitude=longitude,
                    device_id=device_id,
                    photo_path=None
                )
                db.session.flush()
                self.attendance_log_repo.create_anomaly(
                    employee_id=employee_id,
                    log_id=log_err.id,
                    anomaly_type=anomaly_type,
                    description=description
                )
            raise BusinessException(description)

        att = self.attendance_repo.get_today_attendance(employee_id)

        try:
            if "," in image_base64:
                header, encoded = image_base64.split(",", 1)
            else:
                encoded = image_base64
            image_bytes = base64.b64decode(encoded)
        except Exception:
            raise ValidationError("Lỗi định dạng dữ liệu hình ảnh Base64.")

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValidationError("Lỗi giải mã hình ảnh chấm công.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        if brightness < 30:
            raise AIVerificationError("❌ Ánh sáng quá yếu hoặc camera bị che. Vui lòng thử lại.")

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            raise AIVerificationError("❌ Không phát hiện khuôn mặt. Vui lòng nhìn thẳng vào camera.")
        if len(faces) > 1:
            raise AIVerificationError("❌ Phát hiện nhiều khuôn mặt. Chỉ một người được phép chấm công.")

        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            raise ValidationError("Không thể xử lý định dạng ảnh.")

        weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        date_str = f"{weekdays[now.weekday()]}, {now.strftime('%d/%m/%Y')}"
        time_str = now.strftime('%H:%M:%S')
        
        name_str = f"{employee_fullname} - {employee_code}" if employee_code else employee_fullname
        role_str = f"{position_str} - {department_name}" if position_str and department_name else (position_str or department_name or "Nhân viên")
        
        draw = ImageDraw.Draw(image, 'RGBA')
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_title = ImageFont.truetype("arialbd.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
            font_title = font

        padding = 10
        texts = [name_str, role_str, date_str, time_str]
        
        max_width = 0
        total_height = 0
        line_spacing = 5
        for i, text in enumerate(texts):
            cur_font = font_title if i == 0 else font
            bbox = draw.textbbox((0, 0), text, font=cur_font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width > max_width: max_width = width
            total_height += height + line_spacing
            
        bg_width = max_width + padding * 2
        bg_height = total_height + padding * 2
        
        margin = 15
        x0 = margin
        y0 = image.height - bg_height - margin
        x1 = x0 + bg_width
        y1 = image.height - margin
        
        draw.rectangle(((x0, y0), (x1, y1)), fill=(0, 0, 0, 150))
        
        current_y = y0 + padding
        for i, text in enumerate(texts):
            cur_font = font_title if i == 0 else font
            draw.text((x0 + padding, current_y), text, font=cur_font, fill=(255, 255, 255, 255))
            bbox = draw.textbbox((0, 0), text, font=cur_font)
            current_y += (bbox[3] - bbox[1]) + line_spacing

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = f"{employee_code}_{action}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(upload_folder, filename)
        if image.mode in ('RGBA', 'P'): 
            image = image.convert('RGB')
        image.save(filepath, "JPEG")

        token = str(uuid.uuid4())[:8].upper()
        
        with UnitOfWork():
            # Resolve Shift
            shifts = self.shift_repo.get_all_shifts()
            matched_shift = ShiftPolicy.match_shift(shifts, now)
            shift_id = matched_shift.id if matched_shift else None

            # Create immutable log in event stream
            self.attendance_log_repo.create_log(
                employee_id=employee_id,
                timestamp=now,
                action_type=action_mapped,
                shift_id=shift_id,
                verification_type='face',
                face_confidence=1.0,
                latitude=latitude,
                longitude=longitude,
                device_id=device_id,
                photo_path=filename
            )

            # Sync to backward compatibility snapshot row in old 'attendance' table
            if action == 'check_in':
                if not att:
                    self.attendance_repo.create_checkin(
                        employee_id=employee_id,
                        work_date=today,
                        check_in_time=now,
                        check_in_photo=filename,
                        qr_code_token=token
                    )
            else:
                if att:
                    self.attendance_repo.update_checkout(
                        attendance_id=att.id,
                        check_out_time=now,
                        check_out_photo=filename,
                        qr_code_token=token
                    )

            db.session.flush()
            
            # Recalculate daily summary for multi-session and save on old table snapshot row
            summary = self.session_service.calculate_daily_summary(employee_id, today)
            att_snapshot = self.attendance_repo.get_today_attendance(employee_id)
            if att_snapshot:
                att_snapshot.total_work_hours = summary['total_work_hours']
                att_snapshot.total_break_minutes = summary['total_break_minutes']
                att_snapshot.overtime_hours = summary['overtime_hours']
                if summary['first_check_in']:
                    att_snapshot.check_in = summary['first_check_in']
                if summary['last_check_out']:
                    att_snapshot.check_out = summary['last_check_out']

        qr_img = qrcode.make(f"ATT:{token}:{employee_code}")
        qr_filename = f"qr_{token}.png"
        qr_path = os.path.join(upload_folder, qr_filename)
        qr_img.save(qr_path)

        return token, qr_filename

    def manual_checkout(self, employee_id, employee_code, upload_folder):
        now = datetime.now()
        today = now.date()

        # Cooldown check
        latest_log = self.attendance_log_repo.get_latest_success_log(employee_id, now_dt=now)
        CooldownPolicy.validate(latest_log, now)

        # State Machine transition check
        current_state = StateMachinePolicy.get_current_state(latest_log)
        is_valid, anomaly_type, description = StateMachinePolicy.validate_transition(current_state, 'CHECK_OUT')
        
        if not is_valid:
            with UnitOfWork():
                # Persist log and register anomaly in DB
                log_err = self.attendance_log_repo.create_log(
                    employee_id=employee_id,
                    timestamp=now,
                    action_type='CHECK_OUT',
                    verification_type='manual',
                    photo_path=None
                )
                db.session.flush()
                self.attendance_log_repo.create_anomaly(
                    employee_id=employee_id,
                    log_id=log_err.id,
                    anomaly_type=anomaly_type,
                    description=description
                )
            raise BusinessException(description)

        att = self.attendance_repo.get_today_attendance(employee_id)
        token = str(uuid.uuid4())[:8].upper()

        with UnitOfWork():
            # Resolve Shift
            shifts = self.shift_repo.get_all_shifts()
            matched_shift = ShiftPolicy.match_shift(shifts, now)
            shift_id = matched_shift.id if matched_shift else None

            # Create immutable log in event stream
            self.attendance_log_repo.create_log(
                employee_id=employee_id,
                timestamp=now,
                action_type='CHECK_OUT',
                shift_id=shift_id,
                verification_type='manual',
                photo_path=None
            )

            # Sync to backward compatibility snapshot row
            if att:
                self.attendance_repo.update_checkout(
                    attendance_id=att.id,
                    check_out_time=now,
                    check_out_photo=None,
                    qr_code_token=token
                )
                
            db.session.flush()

            # Recalculate daily summary for compatibility snapshot
            summary = self.session_service.calculate_daily_summary(employee_id, today)
            att_snapshot = self.attendance_repo.get_today_attendance(employee_id)
            if att_snapshot:
                att_snapshot.total_work_hours = summary['total_work_hours']
                att_snapshot.total_break_minutes = summary['total_break_minutes']
                att_snapshot.overtime_hours = summary['overtime_hours']
                if summary['first_check_in']:
                    att_snapshot.check_in = summary['first_check_in']
                if summary['last_check_out']:
                    att_snapshot.check_out = summary['last_check_out']

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        qr_img = qrcode.make(f"ATT:{token}:{employee_code}")
        qr_filename = f"qr_{token}.png"
        qr_path = os.path.join(upload_folder, qr_filename)
        qr_img.save(qr_path)

        return token, qr_filename, now.strftime("%H:%M")
