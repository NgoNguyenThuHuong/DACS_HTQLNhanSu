from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.services import AuthService
from app.core.exceptions import ValidationError

auth = Blueprint('auth', __name__)
auth_service = AuthService()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        try:
            user = auth_service.authenticate_user(username, password)
            if not user:
                flash('Tên đăng nhập hoặc mật khẩu không chính xác.', 'error')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)
            return redirect(url_for('main.index'))
        except ValidationError as e:
            flash(e.message, 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        employee_code = request.form.get('employee_code')
        email = request.form.get('email')

        try:
            auth_service.register_user(username, password, fullname, employee_code, email)
            flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except ValidationError as e:
            flash(e.message, 'error')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
