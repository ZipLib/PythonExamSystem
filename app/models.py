
from werkzeug.security import generate_password_hash, check_password_hash
'''
    Calculate password hash values and check by 'Werkzeug'
        generate_password_hash(password, **kwargs),
            input original password string and output its hash value which save in database
        check_password_hash(hash, password),
            'hash' get its value and password from database and check
'''
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
'''
    Generate and check encrypted security tokens
'''
# from flask import current_app

from flask_login import UserMixin, AnonymousUserMixin
''' Two ways to use flask-login

    The realization in the user model of
        is_authenticated() method, returns whether the user is logged in
            #In later versions of the login manager module
                is_authenticated is an attribute rather than a method
        is_active() method, returns whether to allow the user login,
            the user will not be able to login if returns False
        is_anonymous() method, returns whether the landing is anonymous users,
            which is not logged in users
        get_id() method, returns a string as Unicode which can be uniquely identifies the user

    Direct inheritance UserMixin class in the user model,
        the class has the default implementation of the above 4 methods
'''
from datetime import datetime
from . import db, login_manager


class Permission:
    EXAMINEE = 0x01
    QUESTION_MAKER = 0x02
    CORRECTOR = 0x03
    ADMINISTER = 0x04
    
# class User(UserMixin, db.Model):
#     pass


# 管理员 表
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    phone = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, default=1)  # v2
    # age = db.Column(db.Integer)
    # address = db.Column(db.String(64))
    login_times = db.Column(db.Integer, nullable=True, default=int(0))  # v2
    last_login = db.Column(db.DateTime(), nullable=True)  # v2
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    notices = db.relationship('Notice', backref='admin')    # v2    管理员与通知表 一对多

    @property
    def password(self):
        raise AttributeError('密码不可见')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.account.encode('utf-8')

    def can(self, permissions):
        return permissions == Permission.ADMINISTER

    def is_administrator(self):
        return True


# # 友情链接 表    ++
# class RelationLink(db.Model):
#     __tablename__ = 'relationLinks'
#     id = db.Column(db.Integer, primary_key=True)
#     link_name = db.Column(db.String(64))
#     link_url = db.Column(db.String(64))


# 公告 表
class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    notice_title = db.Column(db.String(64))
    notice_content = db.Column(db.String(128))
    order = db.Column(db.Integer)    # v2    顺序
    reader = db.Column(db.Integer)    # 阅读人
    title_color = db.Column(db.String(64))    # v2
    show_time = db.Column(db.Date)    # 展示时间
    visit_times = db.Column(db.Integer)    # v2
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)    # 生成时间
    # 通知发布人
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))    # v2
    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id'))    # v2
    corrector_id = db.Column(db.Integer, db.ForeignKey('correctors.id'))    # v2

    def get_reader(self):
        if self.reader == 1:
            readers = '考生'
        elif self.reader == 2:
            readers = '出题员'
        else:
            readers = '改卷员'
        return readers

# 试卷详情 关系表    # 试卷与其他关系的 多对多关系  ！！此关联表不可调用
# exam_paper_details = db.Table('exam_paper_details',
#                               db.Column('exam_paper_id', db.Integer, db.ForeignKey('examPapers.id',
#                                                                                    ondelete='CASCADE',
#                                                                                    onupdate='CASCADE')),
#                               db.Column('single_question_id', db.Integer, db.ForeignKey('singleQuestions.id')),
#                               db.Column('multi_question_id', db.Integer, db.ForeignKey('multiQuestions.id')),
#                               db.Column('judge_question_id', db.Integer, db.ForeignKey('judgeQuestions.id')),
#                               db.Column('fill_question_id', db.Integer, db.ForeignKey('fillQuestions.id')),
#                               db.Column('answer_question_id', db.Integer, db.ForeignKey('answerQuestions.id')),
#                               db.Column('examinee_id', db.Integer, db.ForeignKey('examinees.id'))
#                               )


class ExamPaperDetail(db.Model):
    __tablename__ = 'examPaperDetails'
    id = db.Column(db.Integer, primary_key=True)
    examinee_id = db.Column(db.Integer, db.ForeignKey('examinees.id'))
    exam_paper_id = db.Column(db.Integer, db.ForeignKey('examPapers.id'))
    question_type = db.Column(db.String(64))    # 题型   省略五种题外键？
    question_id = db.Column(db.Integer)    # 题号
    # 删除以下 ？ 免除多对多关系
    # single_question_id = db.Column(db.Integer, db.ForeignKey('singleQuestions.id'))
    # multi_question_id = db.Column(db.Integer, db.ForeignKey('multiQuestions.id'))
    # judge_question_id = db.Column(db.Integer, db.ForeignKey('judgeQuestions.id'))
    # fill_question_id = db.Column(db.Integer, db.ForeignKey('fillQuestions.id'))
    # answer_question_id = db.Column(db.Integer, db.ForeignKey('answerQuestions.id'))


# 试卷 表
class ExamPaper(db.Model):
    __tablename__ = 'examPapers'
    id = db.Column(db.Integer, primary_key=True)
    exam_paper_name = db.Column(db.String(64), unique=True, index=True)
    total_score = db.Column(db.Integer)    # 总分
    # single_number = db.Column(db.Integer)    # 单选题数    +？
    # multi_number = db.Column(db.Integer)  #      +？
    # judge_number = db.Column(db.Integer)  #      +？
    # fill_number = db.Column(db.Integer)  #  +？
    # answer_number = db.Column(db.Integer)  #  +？
    status = db.Column(db.Integer)    # 试卷状态，（用、禁）
    is_examinees = db.Column(db.Integer)    # 是否考生出卷  &&  改成考生编号 ? 存在或不存在
    timestamp = db.Column(db.DateTime(), default=datetime.now)    # 生成时间
    start_time = db.Column(db.String(64), default=0)    # 试卷统考开考时间 （结合“is_examinees”）    # timestamp is Float
    end_time = db.Column(db.String(64))    # 试卷统考结束时间 （通过“answer_time_set”生成，用于判断是否再用 ？）
    answer_time_set = db.Column(db.String(64))    # 考试需要时间
    temp_timestamp = db.Column(db.String(64), default=0)

    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'))  # 选择出卷的专业
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))    # 选择出卷的课程
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))    # 选择出卷的章节
    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id',
                                                            ondelete='CASCADE', onupdate='CASCADE'))

    exam_paper_details = db.relationship('ExamPaperDetail',  # 试卷与详情表 一对多  与生成（使用）者多对多
                                         backref='examPapers', lazy='dynamic')
    exam_paper_finish = db.relationship('ExamPaperFinished',    # 试卷与答卷题表 一对多
                                        backref='examPapers')

    # 生成此试卷的详情表
    def set_detail(self):
        exam_paper_detail = ExamPaperDetail(examPapers=self)
        db.session.add(exam_paper_detail)
        # print('self id......:', self.id)
        # print('exam paper detail in ExamPaper......:', exam_paper_detail, exam_paper_detail.id)
        db.session.commit()    # 提交后保存数据
        # print('ExamPaper id in detail ......:', self.id, exam_paper_detail.id, exam_paper_detail.exam_paper_id)
        return exam_paper_detail

    # 把试卷的用户和主观题导入答卷库 DNF
    def exam_finished(self, examinees, question):
        e = ExamPaperFinished(answered_content=question.answer, per_score=question.score, )
        e.examPapers.append(self)
        e.examinees.append(examinees)
        db.session.add(e)

    # 获取生成试卷的考生
    def exam_paper_user(self):
        # exam_paper_detail = ExamPaperDetail.query.join(ExamPaper, ExamPaper.id == ExamPaperDetail.exam_paper_id)\
        #     .filter(ExamPaper.id == self.id).first()

        user = Examinee.query.filter_by(id=self.is_examinees).first()    # is_examinees改成examinee_id ?   DNF
        return user

    def exam_finished_user(self):
        exam_finisheds = ExamPaperFinished.query.filter_by(exam_paper_id=self.id).all()

        return exam_finisheds


# 答卷 表 and 改卷（表）
class ExamPaperFinished(db.Model):
    __tablename__ = 'examPaperFinished'
    id = db.Column(db.Integer, primary_key=True)

    # 删除中间 DNF
    # answered_content = db.Column(db.String(64))
    # per_score = db.Column(db.Integer)
    # question_type = db.Column(db.String(64))    # 此回答题型
    # question_id = db.Column(db.Integer)    # 此回答题号

    answer_time = db.Column(db.Float)  # 考试用时 （传入）
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    is_corrected = db.Column(db.Integer)  # 是否已改 (改卷表)

    examinee_id = db.Column(db.ForeignKey('examinees.id', ondelete='CASCADE', onupdate='CASCADE'))
    exam_paper_id = db.Column(db.ForeignKey('examPapers.id', ondelete='CASCADE', onupdate='CASCADE'))

    exam_paper_corrected = db.relationship('ExamPaperCorrected',
                                           backref='examFinished')  # 答卷与改卷一对多 ？
    exam_paper_finished_detail = db.relationship('ExamPaperFinishedDetail',
                                                 backref='examFinished')  # 答卷与详情一对多
    # 更改方法与关系 ？ DNF
    scores = db.relationship('Score',
                             backref='examFinished')    # v2 （uselist:）答题与分数表一对一 ?

    def set_score(self, objective_score, user):
        s = Score(objective_score=objective_score,
                  exam_paper_finish_id=self.id,
                  examinee_id=user.id)
        # print('self scores is : ', objective_score, type(objective_score))  # s.examFinished, type(s.examFinished),
        # s.examFinished.append(self)
        # s.examinees.append(user)
        db.session.add(s)
        db.session.commit()

    def get_exam_paper(self):
        return ExamPaper.query.filter_by(id=self.exam_paper_id).first()


# 答卷详情 表
class ExamPaperFinishedDetail(db.Model):
    __tablename__ = 'examPaperFinishedDetail'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(64))  # 回答题型
    question_id = db.Column(db.Integer)  # 回答题号
    answer = db.Column(db.Text())    # 答案
    per_score = db.Column(db.Integer)    # 题目分数
    answered_content = db.Column(db.Text())    # 回答内容
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    exam_paper_finished_id = db.Column(db.ForeignKey('examPaperFinished.id',
                                                     ondelete='CASCADE', onupdate='CASCADE'))


# 改卷 （详情）表
class ExamPaperCorrected(db.Model):
    __tablename__ = 'examPaperCorrected'
    id = db.Column(db.Integer, primary_key=True)
    corrected_content = db.Column(db.String(64), nullable=True)    # 批示
    corrected_score = db.Column(db.Integer)    # 得分
    start_time = db.Column(db.DateTime())    #
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    exam_paper_finished_id = db.Column(db.Integer, db.ForeignKey('examPaperFinished.id'))
    corrector_id = db.Column(db.Integer, db.ForeignKey('correctors.id'))


# 分数 表
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    single_score = db.Column(db.Integer)    # 各题型分
    multi_score = db.Column(db.Integer)
    judge_score = db.Column(db.Integer)
    fill_score = db.Column(db.Integer)
    objective_score = db.Column(db.Integer, nullable=True)    # 客观题总分
    subjective_score = db.Column(db.Integer, nullable=True)    # 问答题
    total_score = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    examinee_id = db.Column(db.Integer, db.ForeignKey('examinees.id'))
    exam_paper_finish_id = db.Column(db.ForeignKey('examPaperFinished.id'))


# 考生 表
class Examinee(UserMixin, db.Model):
    __tablename__ = 'examinees'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)    # 用户名登录  ++ 通过用户名查找账号（账号登录）
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), index=True)
    # photo = db.Column(db.Unicode)    # 头像    ？数据库或者文件夹（账号名文件夹下的图像文件）
    sex = db.Column(db.Integer, nullable=True)
    age = db.Column(db.Integer)
    birthday = db.Column(db.Date())
    id_card = db.Column(db.String(64), unique=True, nullable=True)
    phone = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    status = db.Column(db.Integer, default=1)
    login_times = db.Column(db.Integer, nullable=True, default=int(0))
    last_login = db.Column(db.DateTime(), nullable=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    class_id = db.Column(db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))

    examinee_scores = db.relationship('Score',    # 考生与分数表 一对多
                                      backref='examinees',
                                      lazy='dynamic')
    exam_paper_finishes = db.relationship('ExamPaperFinished',    # 考生与答卷表 一对多
                                          backref='examinees',
                                          lazy='dynamic')
    exam_paper_details = db.relationship('ExamPaperDetail',  # 考生与试卷详情表 一对多 （考生与试卷表 多对多）
                                         backref='examinees',
                                         lazy='dynamic')

    @property    # 属性装饰器
    def password(self):
        raise AttributeError('密码不可见')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
            return self.account.encode('utf-8')

    def can(self, permissions):
        return permissions == Permission.EXAMINEE

    def is_administrator(self):
        return False

    @staticmethod
    def exam_paper(title, total_score, set_time, start_time, profession_id, department=0, chapter=0,
                   status=1, is_examinees=0, *args):    # 考生出卷 入库 "1"
        if start_time:
            end_time = start_time + float(set_time)*60    # 试卷作答结束时间
        else:
            end_time = 0
        exam_paper = ExamPaper(exam_paper_name=title, answer_time_set=set_time,
                               start_time=start_time, end_time=end_time,
                               status=status, total_score=total_score,
                               is_examinees=is_examinees)
        try:
            if profession_id:
                exam_paper.profession_id = profession_id
            if department:
                exam_paper.department_id = department
            if chapter:
                exam_paper.chapter_id = chapter
            if not is_examinees:
                exam_paper.question_maker_id = args[0]
        except Exception as e:
            print('参数错误。参考：', e)    # 抛出异常 +
        db.session.add(exam_paper)
        return exam_paper


# 题目表
    # 单选题 表
class SingleQuestion(db.Model):    # deleted UserMixin,
    __tablename__ = 'singleQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())
    department = db.Column(db.String(64))
    difficulty = db.Column(db.String(6), nullable=True)
    score = db.Column(db.Integer)
    option1 = db.Column(db.String(64))
    option2 = db.Column(db.String(64))
    option3 = db.Column(db.String(64))
    option4 = db.Column(db.String(64))
    answer = db.Column(db.String(64))
    answer_describe = db.Column(db.Text, nullable=True)    # v2
    status = db.Column(db.Integer, default=1)    # v2
    is_examinee = db.Column(db.Boolean, default=False)    # v2    bool ?
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id',
                                                            ondelete='CASCADE', onupdate='CASCADE'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id',
                                                     ondelete='CASCADE', onupdate='CASCADE'))
    # exam_paper_details = db.relationship('ExamPaperDetail',  # 题目与详情表 一对多
    #                                      backref='singleQuestions')

    @property
    def get_type(self):
        return '单选题'

    def set_to_detail(self, exam_paper=None, user=None):    # 添加选择的题号到试卷详情
        detail = ExamPaperDetail(single_question_id=self.id)
        if exam_paper:    # 题号与试卷号对应
            try:
                details = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper.id).first()
                if details:
                    detail = details
            except Exception as e:
                print('没有当前试卷的详情。查看：', e)
            print('detail +id +sq in SQ ', detail.id, detail.single_question_id)
            detail.exam_paper_id = exam_paper.id
            if user:
                if user.__tablename__ == 'examinees':
                    detail.examinee_id = user.id
        db.session.add(detail)
        db.session.commit()
        return detail


# 多选题 表
class MultiQuestion(db.Model):
    __tablename__ = 'multiQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())
    department = db.Column(db.String(64))
    difficulty = db.Column(db.String(6))
    score = db.Column(db.Integer)
    option1 = db.Column(db.String(64))
    option2 = db.Column(db.String(64))
    option3 = db.Column(db.String(64))
    option4 = db.Column(db.String(64))
    option5 = db.Column(db.String(64))
    option6 = db.Column(db.String(64))
    answer = db.Column(db.String(64))
    answer_describe = db.Column(db.Text, nullable=True)  # v2
    status = db.Column(db.Integer, default=1)  # v2
    is_examinee = db.Column(db.Boolean, default=False)  # v2
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    # exam_paper_details = db.relationship('ExamPaperDetail',
    #                                      backref='multiQuestions')

    @property
    def get_type(self):
        return '多选题'

    def set_to_detail(self, exam_paper=None):    # 添加选择的题号到绑定试卷（outer）的详情
        detail = ExamPaperDetail(multi_question_id=self.id)
        if exam_paper:
            try:
                details = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper.id).first()
                if details:
                    detail = details
            except Exception as e:
                print('没有当前试卷的详情。查看：', e)
            detail.exam_paper_id = exam_paper.id
        db.session.add(detail)
        db.session.commit()
        return detail


# 判断题 表
class JudgeQuestion(db.Model):
    __tablename__ = 'judgeQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())
    department = db.Column(db.String(64))
    difficulty = db.Column(db.String(6))
    score = db.Column(db.Integer)
    option1 = db.Column(db.String(64))
    option2 = db.Column(db.String(64))
    answer = db.Column(db.String(64))
    answer_describe = db.Column(db.Text, nullable=True)  # v2
    status = db.Column(db.Integer, default=1)  # v2
    is_examinee = db.Column(db.Boolean, default=False)  # v2
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    # exam_paper_details = db.relationship('ExamPaperDetail',
    #                                      backref='judgeQuestions')

    @property
    def get_type(self):
        return '判断题'

    def set_to_detail(self, exam_paper=None):    # 添加选择的题号到绑定试卷（outer）的详情
        detail = ExamPaperDetail(judge_question_id=self.id)
        if exam_paper:
            try:
                details = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper.id).first()
                if details:
                    detail = details
            except Exception as e:
                print('没有当前试卷的详情。查看：', e)
            detail.exam_paper_id = exam_paper.id
        db.session.add(detail)
        db.session.commit()
        return detail


# 填空题 表
class FillQuestion(db.Model):
    __tablename__ = 'fillQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())
    department = db.Column(db.String(64))
    difficulty = db.Column(db.String(6))
    score = db.Column(db.Integer)
    fill1 = db.Column(db.String(64), default=0)
    fill2 = db.Column(db.String(64), default=0)
    fill3 = db.Column(db.String(64), default=0)
    fill4 = db.Column(db.String(64), default=0)
    fill5 = db.Column(db.String(64), default=0)
    fill6 = db.Column(db.String(64), default=0)
    answer = db.Column(db.String(64))
    answer_describe = db.Column(db.Text, nullable=True)  # v2
    status = db.Column(db.Integer, default=1)  # v2
    is_examinee = db.Column(db.Boolean, default=False)  # v2
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    # exam_paper_details = db.relationship('ExamPaperDetail',
    #                                      backref='fillQuestions')

    @property
    def get_type(self):
        return '填空题'

    def set_to_detail(self, exam_paper=None):    # 添加选择的题号到绑定试卷详情
        detail = ExamPaperDetail(fill_question_id=self.id)
        if exam_paper:
            try:
                details = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper.id).first()
                if details:
                    detail = details
            except Exception as e:
                print('没有当前试卷的详情。查看：', e)
            detail.exam_paper_id = exam_paper.id
        db.session.add(detail)
        db.session.commit()
        return detail


# 问答题 表
class AnswerQuestion(db.Model):
    __tablename__ = 'answerQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text())
    department = db.Column(db.String(64))
    difficulty = db.Column(db.String(6))
    score = db.Column(db.Integer)
    answer = db.Column(db.Text())
    answer_describe = db.Column(db.Text(), nullable=True)
    status = db.Column(db.Integer, default=1)
    is_examinee = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    question_maker_id = db.Column(db.Integer, db.ForeignKey('questionMakers.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    # exam_paper_details = db.relationship('ExamPaperDetail',
    #                                      backref='answerQuestions')

    @property
    def get_type(self):
        return '问答题'

    def set_to_detail(self, exam_paper=None):    # 添加选择的题号到 试卷详情
        detail = ExamPaperDetail(answer_question_id=self.id)
        if exam_paper:
            try:
                details = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper.id).first()
                if details:
                    detail = details
            except Exception as e:
                print('没有当前试卷的详情。查看：', e)
            detail.exam_paper_id = exam_paper.id
        db.session.add(detail)
        db.session.commit()
        return detail


# 出题员表
class QuestionMaker(UserMixin, db.Model):
    __tablename__ = 'questionMakers'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    sex = db.Column(db.String(64), nullable=True)
    id_card = db.Column(db.String(64), unique=True, index=True, nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(64), nullable=True)
    status = db.Column(db.Integer, default=1)  # v2
    login_times = db.Column(db.Integer, nullable=True, default=int(0))  # v2
    last_login = db.Column(db.DateTime(), nullable=True, default=int(0))  # v2
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    notices = db.relationship('Notice', backref='question_maker')    # v2    出题员与通知表 一对多

    # DNF  删除题目与出题员的关联，用 字段（question_maker_id） 取代题目的归属  DNF
    single_questions = db.relationship('SingleQuestion',    # 出题员与题表 一对多
                                       backref=db.backref('question_maker', lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    multi_questions = db.relationship('MultiQuestion',    # 出题员与题表 一对多
                                      backref=db.backref('question_maker', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')
    judge_questions = db.relationship('JudgeQuestion',    # 出题员与题表 一对多
                                      backref=db.backref('question_maker', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')
    fill_questions = db.relationship('FillQuestion',    # 出题员与题表 一对多
                                     backref=db.backref('question_maker', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')
    answer_questions = db.relationship('AnswerQuestion',    # 出题员与题表 一对多
                                       backref=db.backref('question_maker', lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    exam_papers = db.relationship('ExamPaper',    # 出题员与试卷表 一对多   系统卷
                                  backref=db.backref('question_maker', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('密码不可见')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.account.encode('utf-8')

    def can(self, permissions):
        return permissions == Permission.QUESTION_MAKER

    def is_administrator(self):
        return False


# 专业 表
class Profession(db.Model):
    __tablename__ = 'professions'
    id = db.Column(db.Integer, primary_key=True)
    # number = db.Column(db.String(64), unique=True)    # 专业编号 ++ （and 班级、课程 ++）
    name = db.Column(db.String(64), unique=True)

    class_table_id = db.relationship('ClassTable',    # 专业与班级表 一对多
                                     backref='professions')
    exam_paper_id = db.relationship('ExamPaper',
                                    backref='professions')


# 班级 表
class ClassTable(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    # number = db.Column(db.String(64), unique=True)    # 专业编号 ++ （and 班级、课程 ++）
    grade = db.Column(db.String(64))
    name = db.Column(db.String(64))

    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'))
    examinee_id = db.relationship('Examinee',    # 班级与考生表 一对多
                                  backref='classes')
    department_id = db.relationship('Department',    # 班级与课程表 一对多
                                    backref='classes')


# 课程 表
class Department(UserMixin, db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    # number = db.Column(db.String(64), unique=True)    # 专业编号 ++ （and 班级、课程 ++）
    name = db.Column(db.String(64), index=True, unique=True)

    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    chapter_id = db.relationship('ChapterName',    # 课程与章节表 一对多
                                 backref='department')
    question_maker_id = db.relationship('QuestionMaker',    # 课程与出题员表 一对多
                                        backref='department')
    exam_papers = db.relationship('ExamPaper', backref='department')    # 课程与试卷 一对多


# 章节 表
class ChapterName(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    # number = db.Column(db.String(64), unique=True)    # 专业编号 ++ （and 班级、课程 ++）
    name = db.Column(db.String(64))

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    single_questions = db.relationship('SingleQuestion',    # 章节与题表 一对多
                                       backref=db.backref('chapter', lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    multi_questions = db.relationship('MultiQuestion',    # 章节与题表 一对多
                                      backref=db.backref('chapter', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')
    judge_questions = db.relationship('JudgeQuestion',    # 章节与题表 一对多
                                      backref=db.backref('chapter', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')
    fill_questions = db.relationship('FillQuestion',    # 章节与题表 一对多
                                     backref=db.backref('chapter', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')
    answer_questions = db.relationship('AnswerQuestion',    # 章节与题表 一对多
                                       backref=db.backref('chapter', lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    exam_paper_id = db.relationship('ExamPaper', backref='chapter')    # 章节与试卷 一对多


# 改卷员 表
class Corrector(UserMixin, db.Model):
    __tablename__ = 'correctors'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    id_card = db.Column(db.String(64), unique=True, nullable=True)
    name = db.Column(db.String(64))
    sex = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(64), nullable=True)
    status = db.Column(db.Integer, default=1)
    login_times = db.Column(db.Integer, nullable=True, default=int(0))
    last_login = db.Column(db.DateTime(), nullable=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    notices = db.relationship('Notice', backref='corrector')
    exam_paper_corrected = db.relationship('ExamPaperCorrected',    # 改卷员与判卷表 一对多
                                           backref=db.backref('corrector', lazy='joined'),
                                           lazy='dynamic',
                                           cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('密码不可见')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.account.encode('utf-8')

    def can(self, permissions):
        return permissions == Permission.CORRECTOR

    def is_administrator(self):
        return False


# 访客 表
class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# 链接 表
class RelationLink(db.Model):
    __tablename__ = 'relationLinks'
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=True)
    link_url = db.Column(db.String(64), nullable=True)


# 注册 表
# class Registration(db.Model):
#     __tablename__ = 'registrations'
#     id = db.Column(db.Integer, primary_key=True)
#     examinee_id = db.Column(db.Integer, db.ForeignKey('Examinees.id'))
#     questionMaker_id = db.Column(db.Integer, db.ForeignKey('QuestionMakers.id'))
#     handled = db.Column(db.Boolean, default=False)
#     timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

login_manager.anonymous_user = AnonymousUser    # 未登录current_user


# 首字母确定用户类型
@login_manager.user_loader    # 从会话中重载用户
def load_user(user_id):
    if not isinstance(user_id, str):
        user_id = user_id.decode('utf-8')
    # roles, query filter of SQlAlchemy
    if user_id[0] == 'E':
        return Examinee.query.filter_by(account=user_id).first()
    elif user_id[0] == 'C':
        return Corrector.query.filter_by(account=user_id).first()
    elif user_id[0] == 'Q':
        return QuestionMaker.query.filter_by(account=user_id).first()
    elif user_id[0] == 'A':
        return Admin.query.filter_by(account=user_id).first()
