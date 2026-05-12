import smtplib
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

def test_smtp():
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    server = 'smtp.gmail.com'
    port = 587

    print(f"--- Đang kiểm tra cấu hình SMTP ---")
    print(f"Server: {server}")
    print(f"Port: {port}")
    print(f"User: {username}")
    print(f"Pass: {'*' * len(password) if password else 'Trống'}")
    
    if not username or not password or 'your_email' in username or 'your_app_password' in password:
        print("\n[LỖI] Bạn chưa điền thông tin thật vào file .env")
        return

    try:
        print("\nĐang kết nối đến server...")
        smtp = smtplib.SMTP(server, port)
        smtp.set_debuglevel(1)  # Bật debug để xem chi tiết log
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        
        print("\nĐang đăng nhập...")
        smtp.login(username, password)
        print("\n[THÀNH CÔNG] Đăng nhập SMTP thành công!")
        smtp.quit()
        
    except Exception as e:
        print(f"\n[THÀNH CÔNG] Gặp lỗi: {e}")
        print("\nGợi ý:")
        if "Authentication failed" in str(e) or "Username and Password not accepted" in str(e):
            print("- Kiểm tra lại tài khoản email hoặc Mật khẩu ứng dụng.")
            print("- Đảm bảo MAIL_PASSWORD là mã 16 ký tự (không có khoảng trắng).")
        elif "Connection refused" in str(e):
            print("- Có vẻ như mạng hoặc tường lửa đang chặn cổng 587.")
        else:
            print("- Hãy kiểm tra lại kết nối mạng của bạn.")

if __name__ == "__main__":
    test_smtp()
