from flask import Flask
from flask_bootstrap import Bootstrap
'''
    template of HTML
'''
from flask_mail import Mail
'''
    send and authenticate relational email
'''
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
'''
    to specify database by using URL
'''
from flask_login import LoginManager
'''
    manage user session who logged in
        protect routing only allow authenticated user access
'''
from flask_pagedown import PageDown

from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'    # 设置登录页面端点


def create_app(config_name):
    """
    factory function
        delay create instance of program(and more than one),
        then save time to configure program for script

        then use blueprint define route in the global action scope
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Delay creation by init_app() method
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    #  add blueprint to application in factory function
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .administer import administer as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app


# # 测试本模块
# if __name__ == '__main__':
#     print('config : ', config['default'])
