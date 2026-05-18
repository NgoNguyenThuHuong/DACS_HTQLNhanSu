import os
from flask import Flask
from flask_migrate import Migrate
from app.extensions import db, login_manager
from app.core.config import Config
# Tạm thời nạp model từ app/models/ cho Phase 2
from app.models import Employee

def create_app():
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    app.config.from_object(Config)

    # Khởi tạo db và login manager từ app/extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Employee, int(user_id))

    # Đăng ký Blueprints từ app.routes
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.routes.attendance import attendance as attendance_blueprint
    app.register_blueprint(attendance_blueprint)

    from app.routes.recruitment import recruitment as recruitment_blueprint
    app.register_blueprint(recruitment_blueprint)

    from app.routes.hr import hr as hr_blueprint
    app.register_blueprint(hr_blueprint, url_prefix='/hr')

    from app.routes.employee import employee as employee_blueprint
    app.register_blueprint(employee_blueprint, url_prefix='/employee')

    from app.routes.ai_dashboard import ai as ai_blueprint
    app.register_blueprint(ai_blueprint, url_prefix='/ai')

    # Đảm bảo các thư mục upload tồn tại
    os.makedirs(app.config['ATTENDANCE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CV_UPLOAD_FOLDER'], exist_ok=True)

    return app
