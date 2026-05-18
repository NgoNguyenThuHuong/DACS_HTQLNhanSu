import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'htqln-smart-auth-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:@localhost/ql_nhansu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload configurations
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    ATTENDANCE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'attendance')
    CV_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'cv')

    # Allowed extensions
    ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_EXTENSIONS_CV  = {'pdf', 'doc', 'docx'}

    # Email SMTP (Gmail)
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your_email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your_app_password_here'
