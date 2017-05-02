from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField, FileField, RadioField, DateTimeField
from flask_pagedown.fields import PageDownField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
# from ..models import Examinee, QuestionMaker, Department, SingleQuestion, MultiQuestion,\
#     JudgeQuestion, FillQuestion, AnswerQuestion, Corrector
import datetime


class NameForm(Form):

    name = StringField('您的姓名?', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, name):
        self.name = name


class AddFileForm(Form):
    file = FileField('上传文件', validators=[DataRequired()])
    question_type = RadioField('题型：', choices=[('单选题', '单选题'),
                                               ('多选题', '多选题'), ('判断题', '判断题'),
                                               ('填空题', '填空题'), ('问答题', '问答题')], default='单选题')
    submit = SubmitField('提交')

    def validate_file(self, field):
        if True:
            pass    # raise ValidationError('文件已导入。')
    pass


# 导入题目表单
class AddSingleQuestionForm(Form):
    question = PageDownField('题目', validators=[DataRequired()])
    difficulty = StringField('难度', validators=[DataRequired()])
    score = StringField('分值', validators=[DataRequired()])
    option1 = StringField('选项1', validators=[DataRequired()])
    option2 = StringField('选项2', validators=[DataRequired()])
    option3 = StringField('选项3', validators=[DataRequired()])
    option4 = StringField('选项4', validators=[DataRequired()])
    answer = StringField('答案', validators=[DataRequired()])
    submit = SubmitField('添加')
    # def validate_file(self, field):
    #     if SingleQuestion.query.filter_by(name=field.data).first():
    #         raise ValidationError('科室已被添加。')


class AddMultiQuestionForm(Form):
    question = PageDownField('题目', validators=[DataRequired()])
    difficulty = StringField('难度', validators=[DataRequired()])
    score = StringField('分值', validators=[DataRequired()])
    option1 = StringField('选项1', validators=[DataRequired()])
    option2 = StringField('选项2', validators=[DataRequired()])
    option3 = StringField('选项3', validators=[DataRequired()])
    option4 = StringField('选项4', validators=[DataRequired()])
    option5 = StringField('选项5')
    option6 = StringField('选项6')
    answer = StringField('答案', validators=[DataRequired()])
    submit = SubmitField('添加')


class AddJudgeQuestionForm(Form):
    question = PageDownField('题目', validators=[DataRequired()])
    difficulty = StringField('难度', validators=[DataRequired()])
    score = StringField('分值', validators=[DataRequired()])
    option1 = StringField('选项1', validators=[DataRequired()])
    option2 = StringField('选项2', validators=[DataRequired()])
    answer = StringField('答案', validators=[DataRequired()])
    submit = SubmitField('添加')


class AddFillQuestionForm(Form):
    question = PageDownField('题目', validators=[DataRequired()])
    difficulty = StringField('难度', validators=[DataRequired()])
    score = StringField('分值', validators=[DataRequired()])
    option1 = StringField('填空1', validators=[DataRequired()])
    option2 = StringField('填空2')
    option3 = StringField('填空3')
    option4 = StringField('填空4')
    option5 = StringField('填空5')
    option6 = StringField('填空6')
    answer = StringField('答案', validators=[DataRequired()])
    submit = SubmitField('添加')


class AddAnswerQuestionForm(Form):
    question = PageDownField('题目', validators=[DataRequired()])
    difficulty = StringField('难度', validators=[DataRequired()])
    score = StringField('分值', validators=[DataRequired()])
    answer = StringField('答案', validators=[DataRequired()])
    submit = SubmitField('添加')


class ExamSelfForm(Form):
    pass


class MakeExamPaperForm(Form):
    exam_title = StringField('试卷名', default='WEB 阶段测试卷', validators=[DataRequired()])
    profession = SelectField('专业', coerce=int, default=1)
    classes = SelectField('班级', coerce=int, default=1)
    department = SelectField('课程', coerce=int, default=1)
    # chapter = SelectField('章节', coerce=int, default=1)
    total_score = StringField('总分', default=100)
    answer_time = StringField('考试时间', default=120)
    difficulty_id = SelectField(u'难度', coerce=int, default=3)
    single_number = SelectField(u'单选题', coerce=int, default=10,
                                render_kw={'class': 'form-group question_number', 'width': '20px'})
    multi_number = SelectField(u'多选题', coerce=int, default=5,
                               render_kw={'class': 'form-group question_number', 'width': '20px'})
    judge_number = SelectField(u'判断题', coerce=int, default=10,
                               render_kw={'class': 'form-group question_number', 'width': '20px'})
    fill_number = SelectField(u'填空题', coerce=int, default=5,
                              render_kw={'class': 'form-group question_number', 'width': '20px'})
    answer_number = SelectField(u'问答题', coerce=int, default=3,
                                render_kw={'class': 'form-group question_number', 'width': '20px'})
    start_time = DateTimeField('开考时间', validators=[DataRequired()])  # , format='%Y-%m-%d')
    submit = SubmitField('提交')

    def validate_start_time(self, field):
        if field.data < datetime.datetime.now():
            raise ValidationError('选择时间已过期。')


class HelpExamPaperForm(Form):
    examinee_account = StringField('学号', validators=[DataRequired(), Length(8,8),
                                                   Regexp('[0-9]', 0, '卡号必须为数字。')])
    password = PasswordField('密码', validators=[])
    #     DataRequired(), EqualTo('password2', message='密码要一致。')])
    # password2 = PasswordField('确认密码', validators=[DataRequired()])
    difficulty_id = SelectField(u'难度', coerce=int)
    made_day = DateField('出卷日期', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('提交')

    def validate_made_day(self, field):
        if field.data < datetime.datetime.now().date():
            raise ValidationError('不能选择过期时间。')


class HelpExamStyleForm(Form):
    question_maker_id = SelectField(u'考试方式', coerce=int)
    submit = SubmitField('提交')


class SubmitForm(Form):
    submit = SubmitField('检查完毕 确认提交')


if __name__ == '__main__':
    print(' data time : ', '')
