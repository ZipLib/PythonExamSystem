from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):    # 登录权限装饰器
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def examinee_required(f):    # 考生认证
    return permission_required(Permission.EXAMINEE)(f)


def question_maker_required(f):    # 出题员认证
    return permission_required(Permission.QUESTION_MAKER)(f)


def corrector_required(f):    # 改卷员认证
    return permission_required(Permission.CORRECTOR)(f)


def admin_required(f):    # 管理员认证
    return permission_required(Permission.ADMINISTER)(f)
