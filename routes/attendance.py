from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from models import db, Attendance
from datetime import datetime
import cv2
import numpy as np
import os
import base64
import qrcode
import uuid
import io
from PIL import Image, ImageDraw, ImageFont

attendance = Blueprint('attendance', __name__)

# Initialize OpenCV Face Detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@attendance.route('/attendance')
@login_required
def index():
    today = datetime.now().date()
    att = Attendance.query.filter_by(employee_id=current_user.id, work_date=today).first()
    return render_template('modules/attendance/index.html', att=att)

@attendance.route('/attendance/verify', methods=['POST'])
@login_required
def verify():
    data = request.get_json()
    image_data = data.get('image')
    action = data.get('action') # 'check_in' or 'check_out'
    
    if not image_data:
        return jsonify({'success': False, 'message': 'Không nhận được ảnh xác thực.'})

    try:
        # 1. Decode base64 image
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        
        # 2. Advanced Verification with OpenCV & Mediapipe
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'message': '❌ Lỗi xử lý hình ảnh.'})

        # A. Brightness Check (Anti-Cheating with covered camera)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        if brightness < 30: # Threshold for dark/covered camera
            return jsonify({'success': False, 'message': '❌ Ánh sáng quá yếu hoặc camera bị che. Vui lòng thử lại.'})

        # B. Face Detection with OpenCV
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': '❌ Không phát hiện khuôn mặt. Vui lòng nhìn thẳng vào camera.'})
        
        if len(faces) > 1:
            return jsonify({'success': False, 'message': '❌ Phát hiện nhiều khuôn mặt. Chỉ một người được phép chấm công.'})

        # 3. Add Watermark via Pillow (on original image)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Determine text content
        now = datetime.now()
        weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        date_str = f"{weekdays[now.weekday()]}, {now.strftime('%d/%m/%Y')}"
        time_str = now.strftime('%H:%M:%S')
        
        name_str = f"{current_user.fullname} - {current_user.employee_code}" if current_user.employee_code else current_user.fullname
        department_name = current_user.department.name if current_user.department else ""
        position_str = current_user.position if current_user.position else ""
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
        
        # Calculate bounding box for background
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
            
        # 4. Save photo record
        filename = f"{current_user.employee_code}_{action}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(current_app.config['ATTENDANCE_UPLOAD_FOLDER'], filename)
        if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
        image.save(filepath, "JPEG")
            
        # 5. Update Database
        today = datetime.now().date()
        att = Attendance.query.filter_by(employee_id=current_user.id, work_date=today).first()
        token = str(uuid.uuid4())[:8].upper()
        
        if not att:
            if action == 'check_out':
                return jsonify({'success': False, 'message': 'Bạn chưa check-in hôm nay.'})
            att = Attendance(
                employee_id=current_user.id,
                work_date=today,
                check_in=datetime.now(),
                check_in_photo=filename,
                qr_code_token=token,
                status='Normal'
            )
            db.session.add(att)
        else:
            if action == 'check_out':
                if att.check_out: return jsonify({'success': False, 'message': 'Bạn đã check-out hôm nay.'})
                att.check_out = datetime.now()
                att.check_out_photo = filename
                att.qr_code_token = token
            else:
                return jsonify({'success': False, 'message': 'Bạn đã check-in hôm nay.'})
        
        db.session.commit()
        
        # 6. Generate QR
        qr_img = qrcode.make(f"ATT:{token}:{current_user.employee_code}")
        qr_filename = f"qr_{token}.png"
        qr_path = os.path.join(current_app.config['ATTENDANCE_UPLOAD_FOLDER'], qr_filename)
        qr_img.save(qr_path)
        
        return jsonify({
            'success': True, 
            'message': f'Xác thực {action} thành công!',
            'qr_url': url_for('static', filename=f'uploads/attendance/{qr_filename}'),
            'token': token
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})

@attendance.route('/attendance/checkout', methods=['POST'])
@login_required
def checkout():
    today = datetime.now().date()
    att = Attendance.query.filter_by(employee_id=current_user.id, work_date=today).first()
    
    if not att:
        return jsonify({'success': False, 'message': 'Bạn chưa check-in hôm nay.'})
    
    if att.check_out:
        return jsonify({'success': False, 'message': 'Bạn đã check-out hôm nay rồi.'})
    
    now = datetime.now()
    att.check_out = now
    token = str(uuid.uuid4())[:8].upper()
    att.qr_code_token = token
    
    db.session.commit()
    
    # Generate QR for final step verification
    qr_img = qrcode.make(f"ATT:{token}:{current_user.employee_code}")
    qr_filename = f"qr_{token}.png"
    qr_path = os.path.join(current_app.config['ATTENDANCE_UPLOAD_FOLDER'], qr_filename)
    qr_img.save(qr_path)

    return jsonify({
        'success': True,
        'message': f'Check-out thành công lúc {now.strftime("%H:%M")}',
        'qr_url': url_for('static', filename=f'uploads/attendance/{qr_filename}'),
        'token': token,
        'time': now.strftime("%H:%M")
    })
