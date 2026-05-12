from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import db, Employee

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = Employee.query.filter_by(username=username).first()

        # In a real app, use werkzeug.security.check_password_hash
        # But for this migration, we check against the plain password from the old DB first
        if not user or user.password != password:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        employee_code = request.form.get('employee_code')
        email = request.form.get('email')

        # Kiểm tra trùng lặp
        user_exists = Employee.query.filter_by(username=username).first()
        code_exists = Employee.query.filter_by(employee_code=employee_code).first()

        if user_exists:
            flash('Tên đăng nhập đã tồn tại.', 'error')
            return redirect(url_for('auth.register'))
        
        if code_exists:
            flash('Mã nhân viên đã được đăng ký.', 'error')
            return redirect(url_for('auth.register'))

        # Tạo nhân viên mới
        new_user = Employee(
            username=username, 
            password=password, # Plain text for now to match old system logic
            fullname=fullname,
            employee_code=employee_code,
            email=email,
            role='Employee'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
