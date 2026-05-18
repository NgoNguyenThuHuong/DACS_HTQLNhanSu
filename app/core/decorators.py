from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash("Bạn không có quyền truy cập trang này.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['Admin', 'HR']:
            flash("Bạn không có quyền thực hiện chức năng này.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
