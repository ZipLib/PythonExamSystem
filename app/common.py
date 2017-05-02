# -*- cording: utf-8 -*-
# import traceback
from _datetime import datetime
from .models import SingleQuestion, MultiQuestion, JudgeQuestion, \
    FillQuestion, AnswerQuestion, ExamPaperDetail
from flask import request

# 单个导入考生
def register_examinee(Examinee, account, password, name, sex, birthday, phone='', address='', id_card=''):
    user = Examinee(account=account,
                    password=password,
                    name=name,
                    sex=sex,
                    birthday=birthday,
                    id_card=id_card,
                    phone=phone,
                    address=address,
                    )
    return user


# 提供数据库题目类型
def question_db_type(question):
    if question.__tablename__ == 'singleQuestions':
        return 1
    elif question.__tablename__ == 'multiQuestions':
        return 2
    elif question.__tablename__ == 'judgeQuestions':
        return 3
    elif question.__tablename__ == 'fillQuestions':
        return 4
    elif question.__tablename__ == 'answerQuestions':
        return 5
    else:
        print('not a builtin question type.')
        return 0


def db_type_question(number):
    if number == 1:
        return '单选题'
    elif number == 2:
        return '多选题'
    elif number == 3:
        return '判断题'
    elif number == 4:
        return '填空题'
    elif number == 5:
        return '问答题'
    else:
        return '未知，非内部类型'


# 导入Excel表的题目及其类型
def import_question(db, question_type, question, option1, option2, difficulty=3, score=5, *args):
    # print('import question : ', question_type, type(question_type), question_type.__name__)
    if question_type.__name__ == 'SingleQuestion':
        # question_type传入的是类对象，
        #  用__name__取回类名。
        question_its = question_type(question=question, difficulty=difficulty,
                                     score=score, option1=option1,
                                     option2=option2, option3=args[0], option4=args[1],
                                     answer=args[2], department=args[3])
    elif question_type.__name__ == 'MultiQuestion':
        question_its = question_type(question=question, difficulty=difficulty,
                                     score=score, option1=option1,
                                     option2=option2, option3=args[0], option4=args[1],
                                     option5=args[2], option6=args[3],
                                     answer=args[4], department=args[5])
    elif question_type.__name__ == 'JudgeQuestion':
        question_its = question_type(question=question, difficulty=difficulty,
                                     score=score, option1=option1,
                                     option2=option2, answer=args[0], department=args[1])
    elif question_type.__name__ == 'FillQuestion':
        question_its = question_type(question=question, difficulty=difficulty,
                                     score=score, fill1=option1,    # ?op1 empty
                                     fill2=option2, fill3=args[0], fill4=args[1],
                                     fill5=args[2], fill6=args[3],
                                     answer=args[4], department=args[5])
    elif question_type.__name__ == 'AnswerQuestion':
        question_its = question_type(question=question, difficulty=difficulty,
                                     score=score, answer=args[0], department=args[1])
        # print('question type in common :', question_type, type(question_type), question_its)
    else:
        return '没有此题目Model类型：{}'.format(question_type)
    if question_its:
        db.session.add(question_its)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错 : ', e)
            db.session.rollback()
            return False
        return True


# 集成数据库提交
def db_add_commit(db, db_add):
    db.session.add(db_add)
    try:
        db.session.commit()
    except Exception as e:
        print('数据提交出错 : ', e)
        db.session.rollback()
        return False
    return True


# 读取Excel表信息
def excel_submit(os, request, current_app, files, open_workbook, sheet1='Sheet1'):
    file = request.files[files]    # 获取提交的表单文件
    print('file s :', files, type(files), file, type(file))
    if file:
        filename = file.filename
        paths = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(paths)    # !文件打开状态不能保存和使用
        wb = open_workbook(paths)    # !当前Excel表使用类型“.xlsx”
        sheets = wb.sheet_by_name(sheet1)
        rows = sheets.nrows
        cols = sheets.ncols
        excel_list = []
        for i in range(2, rows):    # 获取格式化文件的数据列表
            row_data = sheets.row_values(i)
            excel_list.append(row_data)
        return excel_list, rows, cols, filename
    else:
        return False


# 确定题型 题数
def question_number(request):
    single_number, multi_number, judge_number, fill_number, answer_number = None, None, None, None, None
    if True: # request.form.get('question_type_single', None, type=str):
        single_number = request.form.get('single_number', 0, type=int)  # 获取表单单选题（数量）存在
        if request.form.get('single_number_input', 0, type=int):
            single_number = request.form.get('single_number_input', 0, type=str)
    print('common # question_number() # single_number ', single_number, type(single_number))
    if True: # request.form.get('question_type_multi', None, type=str):
        multi_number = request.form.get('multi_number', 0, type=int)  # 获取表单单选题（数量）存在
        if request.form.get('multi_number_input', 0, type=int):
            multi_number = request.form.get('multi_number_input', 0, type=int)
    if True: # request.form.get('question_type_judge', None, type=str):
        judge_number = request.form.get('judge_number', 0, type=int)  # 获取表单单选题（数量）存在
        if request.form.get('judge_number_input', 0, type=int):
            judge_number = request.form.get('judge_number_input', 0, type=int)
    if True: # request.form.get('question_type_fill', None, type=str):
        fill_number = request.form.get('fill_number', 0, type=int)  # 获取表单单选题（数量）存在
        if request.form.get('fill_number_input', 0, type=int):
            fill_number = request.form.get('fill_number_input', 0, type=int)
    if True: # request.form.get('question_type_answer', None, type=str):
        answer_number = request.form.get('answer_number', 0, type=int)  # 获取表单单选题（数量）存在
        if request.form.get('answer_number_input', 0, type=int):
            answer_number = request.form.get('answer_number_input', 0, type=int)
    return single_number, multi_number, judge_number, fill_number, answer_number


# 出卷入库
def random_make_exam(db, random, user, is_examinees, exam_title, total_score, exam_time,
                     start_time, profession_id, department, chapter, question_maker_id):
    if start_time:
        start_timestamp = start_time.timestamp()    # timestamp是Float类型
    elif not is_examinees:
        start_timestamp = datetime.now().timestamp()
    else:
        start_timestamp = 0
    # print('stat time  type : ', type(start_time), start_timestamp)

    # 随机生成指定试卷题
    single_number, multi_number, judge_number, fill_number, answer_number = question_number(request)
    print('common # random_make_exam() # question_number(request)', question_number(request))
    # 出卷总分 由题量计算
    total_score = int(single_number) * 2 + int(multi_number) * 4 + int(judge_number) * 1 \
                  + int(fill_number) * 4 + int(answer_number) * 15
    exam_paper = user.exam_paper(exam_title, total_score, exam_time, start_timestamp,
                                 profession_id, department, chapter, 1,
                                 is_examinees, question_maker_id)    # DNF 数据项完善

    # single_number = request.form.get('single_number')    # 获取表单单选题数量
    # multi_number = request.form.get('multi_number')
    # judge_number = request.form.get('judge_number')
    # fill_number = request.form.get('fill_number')
    # answer_number = request.form.get('answer_number')
    if single_number:
        singles = SingleQuestion.query  # 提取查询
        single_difficulty = request.form.get('single_difficulty', 0, type=int)
        if single_difficulty:
            single_questions = singles.filter_by(difficulty=single_difficulty).all()
            if department:
                single_questions = singles.filter_by(difficulty=single_difficulty).\
                    filter_by(department=department).all()
        else:
            single_questions = singles.all()
        if int(single_number) > len(single_questions):
            single_number = len(single_questions)
        random_single_questions = random.sample(single_questions, int(single_number))  # 生成指定数量随机题目 列表
        # print('random single questions : ', random_single_questions)  # test
        for single_question in random_single_questions:
            # print('single question in random: ', single_question)  # test
            exam_detail = ExamPaperDetail(question_type='单选题',
                                          question_id=single_question.id)    # 添加 试卷详情 单选题号
            exam_detail.examPapers = exam_paper    # 添加 试卷详情外键 试卷号
            db.session.add(exam_detail)    # 添加到会话
    if multi_number:
        multis = MultiQuestion.query  # 提取查询
        multi_difficulty = request.form.get('multi_difficulty', 0, type=int)
        if multi_difficulty:
            multi_questions = multis.filter_by(difficulty=multi_difficulty).all()
            if department:
                multi_questions = multis.filter_by(difficulty=multi_difficulty).\
                    filter_by(department=department).all()
        else:
            multi_questions = multis.all()
        if int(multi_number) > len(multi_questions):
            multi_number = len(multi_questions)
        random_multi_questions = random.sample(multi_questions, int(multi_number))
        for multi_question in random_multi_questions:
            exam_detail = ExamPaperDetail(question_type='多选题',
                                          question_id=multi_question.id)
            exam_detail.examPapers = exam_paper
            db.session.add(exam_detail)
    if judge_number:
        judges = JudgeQuestion.query  # 提取查询
        judge_difficulty = request.form.get('judge_difficulty', 0, type=int)
        if judge_difficulty:
            judge_questions = judges.filter_by(difficulty=judge_difficulty).all()
            if department:
                judge_questions = judges.filter_by(difficulty=judge_difficulty).\
                    filter_by(department=department).all()
        else:
            judge_questions = judges.all()
        if int(judge_number) > len(judge_questions):
            judge_number = len(judge_questions)
        random_judge_questions = random.sample(judge_questions, int(judge_number))
        print('random judge questions : ', random_judge_questions)
        for judge_question in random_judge_questions:
            exam_detail = ExamPaperDetail(question_type='判断题',
                                          question_id=judge_question.id)
            exam_detail.examPapers = exam_paper
            db.session.add(exam_detail)
    if fill_number:
        fills = FillQuestion.query  # 提取查询
        fill_difficulty = request.form.get('fill_difficulty', 0, type=int)
        if fill_difficulty:
            fill_questions = fills.filter_by(difficulty=fill_difficulty).all()
            if department:
                fill_questions = fills.filter_by(difficulty=fill_difficulty).\
                    filter_by(department=department).all()
        else:
            fill_questions = fills.all()
        if int(fill_number) > len(fill_questions):
            fill_number = len(fill_questions)
        random_fill_questions = random.sample(fill_questions, int(fill_number))
        print('random fill questions : ', random_fill_questions)
        for fill_question in random_fill_questions:
            exam_detail = ExamPaperDetail(question_type='填空题',
                                          question_id=fill_question.id)
            exam_detail.examPapers = exam_paper
            db.session.add(exam_detail)
    if answer_number:
        answers = AnswerQuestion.query  # 提取查询
        answer_difficulty = request.form.get('answer_difficulty', 0, type=int)
        if answer_difficulty:
            answer_questions = answers.filter_by(difficulty=answer_difficulty).all()
            if department:
                answer_questions = answers.filter_by(difficulty=answer_difficulty).\
                    filter_by(department=department).all()
        else:
            answer_questions = answers.all()
        if int(answer_number) > len(answer_questions):
            answer_number = len(answer_questions)
        random_answer_questions = random.sample(answer_questions, int(answer_number))
        print('random answer questions : ', random_answer_questions)
        for answer_question in random_answer_questions:
            exam_detail = ExamPaperDetail(question_type='问答题',
                                          question_id=answer_question.id)
            exam_detail.examPapers = exam_paper
            db.session.add(exam_detail)
    if exam_detail and exam_paper:
        return exam_detail, exam_paper
    else:
        return 0, 0


# 查找详情表对应的 试卷题型
def find_detail_question(unit_exam_paper):
    try:
        single_question_first = SingleQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.single_question_id == SingleQuestion.id) \
            .filter(ExamPaperDetail.exam_paper_id == unit_exam_paper.id).first()
    except:
        single_question_first = 0
    try:
        multi_question_first = MultiQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.multi_question_id == MultiQuestion.id) \
            .filter(ExamPaperDetail.exam_paper_id == unit_exam_paper.id).first()
    except:
        multi_question_first = 0
    try:
        judge_question_first = JudgeQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.judge_question_id == JudgeQuestion.id) \
            .filter(ExamPaperDetail.exam_paper_id == unit_exam_paper.id).first()
    except:
        judge_question_first = 0
    try:
        fill_question_first = FillQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.fill_question_id == FillQuestion.id) \
            .filter(ExamPaperDetail.exam_paper_id == unit_exam_paper.id).first()
    except:
        fill_question_first = 0
    try:
        answer_question_first = AnswerQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.answer_question_id == AnswerQuestion.id) \
            .filter(ExamPaperDetail.exam_paper_id == unit_exam_paper.id).first()
    except:
        answer_question_first = 0
    return single_question_first, multi_question_first, judge_question_first, fill_question_first,\
           answer_question_first


# # 答案入库
class AddScore(object):
    def __init__(self, exam_paper, exam_finished, current_user, request, scores, question_type):
        self.exam_paper = exam_paper
        self.exam_finished = exam_finished
        self.current_user = current_user
        self.request = request
        self.scores = scores
        self.question_type = question_type

    def qt(self):
        # 列出所有试卷的题目
        link_questions = []    # []
        if self.question_type == 'single_question':
            link_questions.append(SingleQuestion.query
                                  .join(ExamPaperDetail, ExamPaperDetail.single_question_id == SingleQuestion.id)
                                  .filter(ExamPaperDetail.exam_paper_id == self.exam_paper.id).all())
        if self.question_type == 'multi_question':
            link_questions.append(MultiQuestion.query
                                  .join(ExamPaperDetail, ExamPaperDetail.multi_question_id == MultiQuestion.id)
                                  .filter(ExamPaperDetail.exam_paper_id == self.exam_paper.id).all())
        if self.question_type == 'judge_question':
            link_questions.append(JudgeQuestion.query
                                  .join(ExamPaperDetail, ExamPaperDetail.judge_question_id == JudgeQuestion.id)
                                  .filter(ExamPaperDetail.exam_paper_id == self.exam_paper.id).all())
        if self.question_type == 'fill_question':
            link_questions.append(FillQuestion.query
                                  .join(ExamPaperDetail, ExamPaperDetail.fill_question_id == FillQuestion.id)
                                  .filter(ExamPaperDetail.exam_paper_id == self.exam_paper.id).all())
        if self.question_type == 'answer_question':
            link_questions.append(AnswerQuestion.query
                                  .join(ExamPaperDetail, ExamPaperDetail.answer_question_id == AnswerQuestion.id)
                                  .filter(ExamPaperDetail.exam_paper_id == self.exam_paper.id).all())
        return link_questions

    def add_to_score(self):
        link_questions = self.qt()
        print('link question from qt() is : ', link_questions, self.qt())
        for link_question in link_questions:
            exam_finish = self.iter_question(link_question)
            print('iter question show exam_finish is : ', exam_finish)
        return exam_finish

    def __call__(self, *args, **kwargs):
        return self

    def iter_question(self, link_questions):
        for question in link_questions:
            question_id = question.id
            answer_id = 'question' + str(question_id)
            answer = self.request.form.get(answer_id)
            print('answer in AddScore  : ', answer)
            # 生成答卷表
            exam_finish = self.exam_finished(answered_content=answer, exam_paper_id=self.exam_paper.id,
                                             examinee_id=self.current_user.id, per_score=question.score,
                                             question_type=question.get_type,
                                             question_id=question_id)

            if self.question_type == 'single_question':
                if answer == question.answer:
                    self.scores += question.score
                    print('single question answer in AddScore : ', question.answer)
                    print('scores in AddScore  : ', self.scores)
            if self.question_type == 'multi_question':
                if answer.__len__ == question.answer.__len__:    # 多选题作答与答案 长度和内容 比较
                    for answer_one in answer:
                        if answer_one in answer:
                            self.scores += question.score
            if self.question_type == 'judge_question':
                if answer == question.answer:
                    self.scores += question.score
            if self.question_type == 'fill_question':
                if answer.strip() in question.answer:    # answer1,2,3,4 ++    # 填空题作答 去除前后空格    DNF
                    self.scores += question.score
            print('scores in AddScore after if  : ', self.scores)

            print('self scores in AddScore is : ', self.scores, type(self.scores))
        exam_finish.set_score(self.scores, self.current_user)    # 客观题分加入分数表
        return exam_finish
