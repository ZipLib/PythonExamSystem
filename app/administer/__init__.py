from flask import Blueprint

administer = Blueprint('administer', __name__)

# 末尾导入蓝本关联模块
    # 避免循环导入依赖（在关联模块还要导入蓝本）
from . import views
