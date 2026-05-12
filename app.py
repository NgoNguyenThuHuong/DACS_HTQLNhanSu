from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, Employee
from config import Config
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Employee.query.get(int(user_id))

    # Register blueprints
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from routes.attendance import attendance as attendance_blueprint
    app.register_blueprint(attendance_blueprint)

    from routes.recruitment import recruitment as recruitment_blueprint
    app.register_blueprint(recruitment_blueprint)

    from routes.hr import hr as hr_blueprint
    app.register_blueprint(hr_blueprint, url_prefix='/hr')

    from routes.employee import employee as employee_blueprint
    app.register_blueprint(employee_blueprint, url_prefix='/employee')
    
    # We will add other blueprints as we progress
    # from routes.hr import hr as hr_blueprint
    # app.register_blueprint(hr_blueprint, url_for='/hr')

    # Ensure upload folders exist
    os.makedirs(app.config['ATTENDANCE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CV_UPLOAD_FOLDER'], exist_ok=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
