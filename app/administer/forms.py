from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
# from flask_pagedown.fields import PageDownField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Optional
from wtforms import ValidationError
from ..models import Examinee, QuestionMaker, Department,\
    Corrector, Profession, ChapterName
# import datetime


class AddExamineeForm(Form):
    account = StringField('学号', validators=[DataRequired(), Length(5, 12),
                                            ])   # Regexp('[0-9]', 0, '卡号必须为数字。')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码要一致。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    name = StringField('姓名', validators=[
        DataRequired(), Length(1, 64)])
    sex = SelectField(u'性别', coerce=int)
    birthday = DateField('出生日期', format='%Y-%m-%d')
    phone = StringField('电话号码', validators=[Optional(), Length(11, 11),
                                            Regexp('[0-9]', 0, '号码必须为数字。')])
    id_card = StringField('身份证号', validators=[Optional(), Length(18, 18),
                                              Regexp('[0-9]', 0, '身份证号必须为数字。')])
    address = StringField('住址', validators=[Optional(), Length(1, 128)])
    submit = SubmitField('添加')

    def validate_account(self, field):
        if Examinee.query.filter_by(account=field.data).first():
            raise ValidationError('学习卡已注册。')

    def validate_id_card(self, field):
        if Examinee.query.filter_by(id_card=field.data).first():
            raise ValidationError('身份证号已注册。')


class AddQuestionMakerForm(Form):
    account = StringField('工号', validators=[DataRequired(), Length(5, 12),
                                            ])  # Regexp('[0-9]', 0, '卡号必须为数字。')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 5)])
    password = PasswordField('密码', validators=[DataRequired(),
                                               EqualTo('password2', message='密码要一致。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    id_card = StringField('身份证号', validators=[Optional(), Length(18, 18),
                                              Regexp('[0-9]', 0, '身份证号必须为数字。')])
    depart_id = SelectField('课程', coerce=int)
    submit = SubmitField('添加')

    def validate_account(self, field):
        if QuestionMaker.query.filter_by(account=field.data).first():
            raise ValidationError('工号已注册。')

    def validate_id_card(self, field):
        if QuestionMaker.query.filter_by(id_card=field.data).first():
            raise ValidationError('身份证号已注册。')


class ChangeQuestionMakerForm(Form):
    name = StringField('姓名', validators=[
        DataRequired(), Length(1, 64)])
    department_id = SelectField('课程', coerce=int)
    submit = SubmitField('更新')


class AddCorrectorForm(Form):
    account = StringField('工号')
    id_card = StringField('身份证号', validators=[Optional(), Length(6, 18),
                                              Regexp('[0-9]', 0, '身份证号必须为数字。')])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(),
                                               EqualTo('password2', message='密码要一致。')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('添加')

    def validate_account(self, field):
        if Corrector.query.filter_by(account=field.data).first():
            raise ValidationError('工号已注册。')

    def validate_id_card(self, field):
        if Corrector.query.filter_by(id_card=field.data).first():
            raise ValidationError('身份证号已注册。')


# 管理专业
class AddProfessionForm(Form):
    name = StringField('专业名称', validators=[DataRequired(), Length(2, 15)])
    # examinee_id = SelectField() DNF
    submit = SubmitField('添加专业')

    def validate_name(self, field):
        if Profession.query.filter_by(name=field.data).first():
            raise ValidationError('专业已存在。')


class ChangeProfessionForm(Form):
    name = StringField('专业名称', validators=[DataRequired(), Length(2, 15)])
    submit = SubmitField('更新专业')


# 管理班级
class AddClassTableForm(Form):
    name = StringField('班级名称', validators=[DataRequired(), Length(2, 15)])
    profession_id = SelectField('专业', coerce=int)
    submit = SubmitField('添加班级')

    def validate_name(self, field):
        if Profession.query.filter_by(name=field.data).first():
            raise ValidationError('班级已存在。')


class ChangeClassTableForm(Form):
    name = StringField('班级名称', validators=[DataRequired(), Length(2, 15)])
    profession_id = SelectField('专业', coerce=int)
    submit = SubmitField('更新班级')


# 管理课程
class AddDepartmentForm(Form):
    name = StringField('课程名称', validators=[DataRequired(), Length(2, 15)])
    class_table_id = SelectField('专业', coerce=int)
    submit = SubmitField('添加课程')

    def validate_name(self, field):
        if Department.query.filter_by(name=field.data).first():
            raise ValidationError('课程已存在。')


class ChangeDepartmentForm(Form):
    name = StringField('课程名称', validators=[DataRequired(), Length(2, 15)])
    class_table_id = SelectField('专业', coerce=int)
    submit = SubmitField('更新课程')


# 管理章节
class AddChapterForm(Form):
    name = StringField('章节名称', validators=[DataRequired(), Length(2, 15)])
    department_id = SelectField('课程', coerce=int)
    submit = SubmitField('添加章节')

    def validate_name(self, field):
        if ChapterName.query.filter_by(name=field.data).first():
            raise ValidationError('章节已存在。')


class ChangeChapterForm(Form):
    name = StringField('章节名称', validators=[DataRequired(), Length(2, 15)])
    department_id = SelectField('课程', coerce=int)
    submit = SubmitField('更新章节')


class AddLinkForm(Form):
    name = StringField('链接名称', validators=[DataRequired(), Length(2, 15)])
    url = StringField('链接地址', validators=[DataRequired()])
    submit = SubmitField('添加链接')


class ChangeLinkForm(AddLinkForm):
    submit = SubmitField('更新链接')
