import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'    # 密匙设置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True    # 数据库变动自动提交
    FLASKY_ADMIN = '444444444444444444'
    QUESTIONS_PER_PAGE = 7    # 分页显示条目
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = 'tmp'    # 上传文件目录

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):    # 程序开发环境数据库
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123@localhost/myExam'    # 显示方式 #


class DevelopmentConfig2(Config):    # SQLite本地数据库
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):    # 测试环境数据库
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123@localhost/test'


class ProductionConfig(Config):    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123@localhost/myExam'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,    # MySQL
    'default_local': DevelopmentConfig2    # SQLite
}
