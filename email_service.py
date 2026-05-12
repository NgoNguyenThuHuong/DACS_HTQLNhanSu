import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Hàm gửi email nội bộ qua SMTP Gmail."""
    try:
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        server   = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        port     = current_app.config.get('MAIL_PORT', 587)

        if not username or not password:
            logger.warning("MAIL_USERNAME hoặc MAIL_PASSWORD chưa được cấu hình.")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"HR System <{username}>"
        msg['To']      = to_email
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(server, port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(username, to_email, msg.as_string())

        logger.info(f"Email gửi thành công đến {to_email}")
        return True

    except Exception as e:
        logger.error(f"Lỗi gửi email đến {to_email}: {e}")
        return False


def send_passed_email(candidate_name: str, candidate_email: str,
                      job_title: str, score: float) -> bool:
    """Gửi email chúc mừng ứng viên đậu."""
    subject = f"Chúc mừng bạn đã trúng tuyển vị trí {job_title}"
    body = f"""
    <html><body style="font-family: 'Segoe UI', Arial, sans-serif; background:#f4f7fc; margin:0; padding:0;">
    <div style="max-width:580px; margin:40px auto; background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <div style="background:linear-gradient(135deg,#10b981,#059669); padding:36px 32px; text-align:center;">
            <div style="font-size:48px;">🎉</div>
            <h1 style="color:#fff; margin:12px 0 4px; font-size:24px; font-weight:700;">Chúc mừng bạn đã trúng tuyển!</h1>
            <p style="color:rgba(255,255,255,0.85); margin:0; font-size:14px;">Hành trình mới của bạn bắt đầu từ đây</p>
        </div>
        <div style="padding:32px;">
            <p style="color:#374151; font-size:15px; margin-bottom:20px;">Chào <strong>{candidate_name}</strong>,</p>
            <p style="color:#374151; font-size:14px; line-height:1.7;">
                Chúng tôi rất vui mừng thông báo rằng bạn đã vượt qua vòng tuyển dụng và chính thức 
                <strong style="color:#10b981;">TRÚNG TUYỂN</strong> vào vị trí <strong>{job_title}</strong>.
            </p>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:20px; margin:24px 0; text-align:center;">
                <div style="color:#6b7280; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Kết quả xét tuyển</div>
                <div style="font-size:32px; font-weight:800; color:#10b981;">{score}/10 điểm</div>
                <div style="color:#10b981; font-size:12px; margin-top:4px;">✅ Đạt yêu cầu chuyên môn</div>
            </div>
            <h3 style="color:#111827; font-size:16px; font-weight:700; margin-bottom:12px;">Hướng dẫn tiếp theo:</h3>
            <ul style="color:#374151; font-size:14px; line-height:1.7; padding-left:20px;">
                <li>Vui lòng phản hồi email này để xác nhận việc nhận việc trong vòng 48h.</li>
                <li>Bộ phận HR sẽ liên hệ qua điện thoại để trao đổi chi tiết về hợp đồng và ngày bắt đầu.</li>
                <li>Chuẩn bị các hồ sơ cần thiết (CCCD, bằng cấp...) cho ngày nhận việc.</li>
            </ul>
            <p style="color:#374151; font-size:14px; line-height:1.7; margin-top:20px;">
                Nếu có bất kỳ thắc mắc nào, bạn có thể liên hệ trực tiếp với bộ phận Nhân sự qua email này.
            </p>
            <p style="color:#374151; font-size:14px; margin-top:28px;">Trân trọng,<br><strong>Bộ phận Nhân sự</strong></p>
        </div>
        <div style="background:#f9fafb; padding:16px 32px; text-align:center; border-top:1px solid #e5e7eb;">
            <p style="color:#9ca3af; font-size:11px; margin:0;">Email này được gửi tự động từ Hệ thống Quản lý Nhân sự. Vui lòng không trả lời.</p>
        </div>
    </div>
    </body></html>
    """
    return _send(candidate_email, subject, body)


def send_failed_email(candidate_name: str, candidate_email: str,
                      job_title: str, score: float) -> bool:
    """Gửi email thông báo ứng viên không đạt."""
    subject = f"Kết quả ứng tuyển vị trí {job_title}"
    body = f"""
    <html><body style="font-family: 'Segoe UI', Arial, sans-serif; background:#f4f7fc; margin:0; padding:0;">
    <div style="max-width:580px; margin:40px auto; background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <div style="background:linear-gradient(135deg,#6366f1,#4f46e5); padding:36px 32px; text-align:center;">
            <div style="font-size:48px;">📋</div>
            <h1 style="color:#fff; margin:12px 0 4px; font-size:24px; font-weight:700;">Kết quả ứng tuyển</h1>
            <p style="color:rgba(255,255,255,0.85); margin:0; font-size:14px;">Thông tin về quy trình xét tuyển của bạn</p>
        </div>
        <div style="padding:32px;">
            <p style="color:#374151; font-size:15px; margin-bottom:20px;">Chào <strong>{candidate_name}</strong>,</p>
            <p style="color:#374151; font-size:14px; line-height:1.7;">
                Cảm ơn bạn đã dành thời gian quan tâm và tham gia quy trình thi tuyển cho vị trí <strong>{job_title}</strong> 
                tại công ty chúng tôi.
            </p>
            <p style="color:#374151; font-size:14px; line-height:1.7;">
                Sau khi xem xét kỹ lưỡng hồ sơ và kết quả bài thi, chúng tôi rất tiếc phải thông báo rằng bạn 
                <strong>chưa phù hợp</strong> với các yêu cầu của vị trí này ở thời điểm hiện tại.
            </p>
            <div style="background:#f8fafb; border:1px solid #e5e7eb; border-radius:12px; padding:20px; margin:24px 0; text-align:center;">
                <div style="color:#6b7280; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Điểm thi ghi nhận</div>
                <div style="font-size:32px; font-weight:800; color:#4b5563;">{score}/10 điểm</div>
            </div>
            <p style="color:#374151; font-size:14px; line-height:1.7;">
                Chúng tôi đánh giá cao năng lực của bạn và sẽ lưu trữ hồ sơ của bạn vào "Danh sách tiềm năng" 
                để liên hệ khi có các cơ hội khác phù hợp hơn trong tương lai. Đừng quá thất vọng, hãy tiếp tục 
                trau dồi và chúng tôi hy vọng có cơ hội hợp tác với bạn sau này.
            </p>
            <p style="color:#374151; font-size:14px; line-height:1.7; margin-top:20px;">
                Chúc bạn nhiều sức khỏe và sớm tìm được công việc như ý.
            </p>
            <p style="color:#374151; font-size:14px; margin-top:28px;">Trân trọng,<br><strong>Bộ phận Nhân sự</strong></p>
        </div>
        <div style="background:#f9fafb; padding:16px 32px; text-align:center; border-top:1px solid #e5e7eb;">
            <p style="color:#9ca3af; font-size:11px; margin:0;">Email này được gửi tự động từ Hệ thống Quản lý Nhân sự. Vui lòng không trả lời.</p>
        </div>
    </div>
    </body></html>
    """
    return _send(candidate_email, subject, body)
