from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Examinee, QuestionMaker, Corrector, Admin


class LoginForm(Form):
    # email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    #                                          Email()])

    account = StringField('账号', validators=[DataRequired(message='请输入你的账号'), Length(3, 8, '长度 3到8。'),
                                            Regexp('[\S]', 0, '请输入你的账号。')],
                          render_kw={'class': 'text-body', 'rows': 20,
                                     'placeholder': u'start with：E, Q, C, A'})
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空'),
                                               Regexp('[\S]', 0, '密码不能为空。')],
                             render_kw={'class': 'text-body', 'rows': 20, 'placeholder': u'密码.'})
    remember_me = BooleanField('记住账号')
    submit = SubmitField('登录')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[DataRequired()],
                                 render_kw={'class': 'text-body', 'rows': 20,
                                            'placeholder': u'old password.'})
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='密码要一致。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('更新')


# class ChangeInformationForm():


class NoticeForm(Form):
    notice_title = StringField('标题', default='通知')
    title_color = SelectField('标题颜色', coerce=str, default='red')
    notice_content = StringField('内容')
    notice_order = SelectField('次序', coerce=int, default=1)
    reader = SelectField('阅读人', coerce=int, default=1)    # 可查看通知 人
    submit = SubmitField('提交')


# 注册用户表单
class RegistrationForm(Form):
    name = StringField('姓名', validators=[
        DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码要一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if Examinee.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')
        if QuestionMaker.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')
        if Corrector.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')
        if Admin.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')


class PasswordResetRequestForm(Form):
    # email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    #                                          Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(Form):
    # email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    #                                          Email()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='密码要一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')

    # def validate_email(self, field):
    #     if User.query.filter_by(email=field.data).first() is None:
    #         raise ValidationError('Unknown email address.')

