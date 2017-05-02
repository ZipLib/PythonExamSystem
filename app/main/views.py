import datetime
import os
import random
import json

from flask import jsonify, abort
from flask import render_template, redirect, url_for, flash, request,\
    current_app
from xlrd import open_workbook
from flask_login import login_required, current_user
# from flask_sqlalchemy import func
from . import main
from .forms import AddSingleQuestionForm, AddMultiQuestionForm, AddJudgeQuestionForm,\
    AddFillQuestionForm, AddAnswerQuestionForm, AddFileForm, \
    MakeExamPaperForm
from .. import db
from ..decorators import examinee_required, question_maker_required, \
    corrector_required
from ..models import QuestionMaker, Examinee, SingleQuestion, \
    ExamPaper, MultiQuestion, JudgeQuestion, FillQuestion, AnswerQuestion, \
    ExamPaperFinished, ExamPaperDetail, ExamPaperFinishedDetail, \
    Profession, ClassTable, Department, ChapterName, Score, ExamPaperCorrected, RelationLink
from ..common import excel_submit, import_question, AddScore, random_make_exam, \
    find_detail_question, question_number


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/introduce')
def introduce():
    return render_template('all_introduce.html')


@main.route('/examinee', methods= ['GET', 'POST'])
@login_required
@examinee_required
def examinee():
    relation_links = RelationLink.query.all()
    print('relation links ', relation_links[0].link_name)
    return render_template('examinee.html', relation_links=relation_links)


@main.route('/question_maker', methods=['GET', 'POST'])
@login_required
@question_maker_required
def question_maker():
    return render_template('question_maker.html')


@main.route('/corrector', methods=['GET', 'POST'])
@login_required
@corrector_required
def corrector():
    return render_template('corrector.html')


# 导入单个选择题
@main.route('/question maker/add questions', methods=['GET', 'POST'])
@login_required
@question_maker_required
def add_question():
    form = AddSingleQuestionForm()
    question_type = request.args.get('question_type', '单选题', type=str)
    # global question_type
    if question_type == '单选题':
        form = AddMultiQuestionForm()
        type_question = SingleQuestion
    elif question_type == '多选题':
        form = AddMultiQuestionForm()
        type_question = MultiQuestion
    elif question_type == '判断题':
        form = AddJudgeQuestionForm()
        type_question = JudgeQuestion
    elif question_type == '填空题':
        form = AddFillQuestionForm()
        type_question = FillQuestion
    elif question_type == '问答题':
        form = AddAnswerQuestionForm()
        type_question = AnswerQuestion
    print('question type from args : ', question_type, type(question_type))
    if form.validate_on_submit():
        db_can = import_question(db, type_question,
                                 form.question.data,
                                 request.form.get('option1', None, type=str),
                                 request.form.get('option2', None, type=str),
                                 form.difficulty.data,
                                 form.score.data,
                                 request.form.get('option3', None, type=str),
                                 request.form.get('option4', None, type=str),
                                 form.answer.data,
                                 request.form.get('option5', None, type=str),
                                 request.form.get('option6', None, type=str))

        if not db_can:
            flash('信息格式有误，请检查内容。')
        flash('已添加' + question_type + '!')
        return redirect(url_for('.add_question', question_type=question_type))
    return render_template('add_question.html', form=form, question_type=question_type)


# Excel批量导入题目
@main.route('/question maker/add excel questions', methods=['GET', 'POST'])
@login_required
@question_maker_required
def add_excel_questions():
    form = AddFileForm()

    if form.validate_on_submit():
        excel_list = excel_submit(os, request, current_app, 'file', open_workbook)  # common.py
        line = 0
        ok_line = 0
        if form.question_type.data == '单选题' or '单选' in excel_list[3]:    # 指定单选题题库
            if '单选' in excel_list[3]:
                for key in excel_list[0]:
                    if SingleQuestion.query.filter_by(question=str(key[4])).first():
                        line += 1    # 重复的题数累加
                        continue    # Excel表重复的考生不导入数据库
                    else:
                        db_can = import_question(db, SingleQuestion,    # common.py
                                                 key[4], key[5], key[6],
                                                 key[1], key[2],
                                                 key[7], key[8], key[9], key[3]
                                                 )
                        ok_line += 1
                        if not db_can:
                            ok_line -= 1
                            flash('信息格式有误，请检查文件或文件内容。')
            else:
                flash('单选题，类型选择错误？或把文件名纠正。')

        if form.question_type.data == '多选题' or '多选' in excel_list[3]:    # 指定多选题题库
            if '多选' in excel_list[3]:
                for key in excel_list[0]:
                    if MultiQuestion.query.filter_by(question=str(key[4])).first():
                        line += 1    # 重复的题数累加
                        continue    # Excel表重复的题目不导入数据库
                    else:
                        db_can = import_question(db, MultiQuestion,    # common.py
                                                 key[4], key[5], key[6],
                                                 key[1], key[2],
                                                 key[7], key[8], key[9],
                                                 key[10], key[11], key[3]
                                                 )
                        ok_line += 1
                        if not db_can:
                            ok_line -= 1
                            flash('信息格式有误，请检查文件或文件内容。.')
            else:
                flash('多选题，类型选择错误？或把文件名纠正。')
        if form.question_type.data == '判断题' or '判断' in excel_list[3]:  # 指定判断题题库
            if '判断' in excel_list[3]:
                for key in excel_list[0]:
                    if JudgeQuestion.query.filter_by(question=str(key[4])).first():
                        line += 1  # 重复的题数累加
                        continue  # Excel表重复的考生不导入数据库
                    else:
                        db_can = import_question(db, JudgeQuestion,  # common.py
                                                 key[4], key[5], key[6],
                                                 key[1], key[2],
                                                 key[7], key[3]
                                                 )
                        ok_line += 1
                        if not db_can:
                            ok_line -= 1
                            flash('信息格式有误，请检查文件或文件内容。.')
            else:
                flash('判断题，类型选择错误？或把文件名纠正。')
        if form.question_type.data == '填空题' or '填空' in excel_list[3]:  # 指定填空题题库
            print('fill question here.')
            if '填空' in excel_list[3]:
                for key in excel_list[0]:
                    if FillQuestion.query.filter_by(question=str(key[4])).first():
                        line += 1  # 重复的题数累加
                        continue  # Excel表重复的考生不导入数据库
                    else:
                        answers = []
                        for i in range(6):
                            if key[5+i]:
                                answers.append(key[5+i])
                        answers_str = ",".join(answers)
                        db_can = import_question(db, FillQuestion,  # common.py
                                                 key[4], key[5], key[6],
                                                 key[1], key[2],
                                                 key[7], key[8], key[9],
                                                 key[10], answers_str, key[3]
                                                 )
                        ok_line += 1
                        if not db_can:
                            ok_line -= 1
                            flash('信息格式有误，请检查文件或文件内容。.')
            else:
                flash('填空题，类型选择错误？或把文件名纠正。')
        if form.question_type.data == '问答题' or '问答' in excel_list[3]:  # 指定问答题题库
            if '问答' in excel_list[3]:
                for key in excel_list[0]:
                    if AnswerQuestion.query.filter_by(question=str(key[4])).first():
                        line += 1  # 重复的题数累加
                        continue  # Excel表重复的考生不导入数据库
                    else:
                        db_can = import_question(db, AnswerQuestion,  # common.py
                                                 key[4], None, None,
                                                 key[1], key[2],
                                                 key[6], key[3]
                                                 )
                        ok_line += 1
                        if not db_can:
                            ok_line -= 1
                            line += 1
                            flash('信息格式有误，请检查文件或文件内容。.')
            else:
                flash('问答题，类型选择错误？或把文件名纠正。')
        flash('成功导入{}: {}行.共有 {} 行, {} 项'.format(form.question_type.data, ok_line,
                                                 excel_list[1]-line, excel_list[2]))
        return redirect(url_for('.question_list',
                                question_type=form.question_type.data))    # +需要ajax
    return render_template('add_excel_questions.html', form=form)


# 题库列表
@main.route('/question maker/question list', methods=['GET', 'POST'])
@login_required
@question_maker_required
def question_list():
    page = request.args.get('page', 1, type=int)
    question_type = request.args.get('question_type', '单选题', type=str)

    if question_type == '单选题':
        pagination = SingleQuestion.query.order_by(SingleQuestion.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    elif question_type == '多选题':
        pagination = MultiQuestion.query.order_by(MultiQuestion.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    elif question_type == '填空题':
        pagination = FillQuestion.query.order_by(FillQuestion.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    elif question_type == '判断题':
        pagination = JudgeQuestion.query.order_by(JudgeQuestion.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    elif question_type == '问答题':
        pagination = AnswerQuestion.query.order_by(AnswerQuestion.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    else:
        flash('{}：题型不支持。'.format(question_type))
    if not pagination:
        abort(404)
    questions = pagination.items
    print('question_type in question list is: ', question_type)    # test
    return render_template('question_list.html', questions=questions,
                           pagination=pagination, question_type=question_type)


# 删除题目
@main.route('/question maker/delete question', methods=['GET', 'POST'])
@login_required
@question_maker_required
def delete_question():
    question_id = request.form.get('question_id', 0, type=int)
    question_type = request.form.get('question_type', '单选题', type=str)
    page = request.args.get('page', 1, type=int)
    delete_page = request.args.get('delete_page', 0, type=int)
    all_questions = request.args.get('all', False, type=str)
    print('page ', page)
    if question_type == '单选题':
        question = SingleQuestion.query.filter_by(id=question_id).first()
        if delete_page:
            pagination = SingleQuestion.query.order_by(SingleQuestion.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            questions = pagination.items
        if all_questions:
            questions = SingleQuestion.query.all()
        print('delete single question ', question)
    elif question_type == '多选题':
        question = MultiQuestion.query.filter_by(id=question_id).first()
        if delete_page:
            pagination = MultiQuestion.query.order_by(MultiQuestion.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            questions = pagination.items
        if all_questions:
            questions = MultiQuestion.query.all()
    elif question_type == '判断题':
        question = JudgeQuestion.query.filter_by(id=question_id).first()
        if delete_page:
            pagination = JudgeQuestion.query.order_by(JudgeQuestion.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            questions = pagination.items
        if all_questions:
            questions = JudgeQuestion.query.all()
    elif question_type == '填空题':
        question = FillQuestion.query.filter_by(id=question_id).first()
        if delete_page:
            pagination = FillQuestion.query.order_by(FillQuestion.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            questions = pagination.items
        if all_questions:
            questions = FillQuestion.query.all()
    elif question_type == '问答题':
        question = AnswerQuestion.query.filter_by(id=question_id).first()
        if delete_page:
            pagination = AnswerQuestion.query.order_by(AnswerQuestion.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            questions = pagination.items
        if all_questions:
            questions = AnswerQuestion.query.all()
    else:
        flash('没有此题型')
    print('delete them:  question id ', question_id, ', question type ', question_type)

    if question:
        print('delete question ', question)
        question_id = question.id
        db.session.delete(question)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错 : ', e)
        flash('已删除\'{}\',题号:{}. '.format(question_type, question_id))
        return jsonify({'ok': True})  # 响应ajax的DataType'json'
    if questions:
        print('delete questions', questions)
        for question in questions:
            db.session.delete(question)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错. 错误是：', e)
        flash('已删除此页(所有)\'{}\'. '.format(question_type))
        return redirect(url_for('.question_list',
                                question_type=question_type))


# 出题员出卷
@main.route('/question maker/make exam paper', methods=['GET', 'POST'])
@login_required
@question_maker_required
def make_exam_paper():
    profession_choice = request.form.get('profession_choose', None, type=str)
    form = MakeExamPaperForm()
    form.profession.choices = [(d.id, d.name) for d in Profession.query.order_by('id')]
    form.classes.choices = [(d.id, d.name) for d in ClassTable.query.order_by('id')]
    # ajax 二级联动  DNF
    if profession_choice:
        profession_id = profession_choice
        form.classes.choices = [(d.id, d.name) for d in
                                ClassTable.query.filter_by(profession_id=profession_id).order_by('id')]
    class_choice = request.form.get('class_choose', None, type=str)

    form.department.choices = [(0, '无')]+[(d.id, d.name) for d in Department.query.order_by('id')]
    if class_choice:
        classes_id = class_choice
        form.department.choices = [(0, '无')] + [(d.id, d.name) for d in Department.query
            .filter_by(class_id=classes_id).order_by('id')]
    # 课程 选择  入库 DNF
    # form.chapter.choices = [(0, '无')]+[(d.id, d.name) for d in ChapterName.query.order_by('id')]
    # 章节 选择   入库 DNF
    # print('chapter choices type : ', type(form.chapter.choices), form.chapter.choices)

    form.difficulty_id.choices = [(key, value) for key, value in
                                  {0: '空', 1: '1星', 2: '2星', 3: '3星', 4: '4星', 5: '5星'}.items()]
    form.single_number.choices = [(key, value) for key, value in
                                  {0: '空', 5: '5道题', 10: '10道题', 15: '15道题'}.items()]
    form.multi_number.choices = [(key, value) for key, value in
                                 {0: '空', 5: '5道题', 10: '10道题', 15: '15道题'}.items()]
    form.judge_number.choices = [(key, value) for key, value in
                                 {0: '空', 5: '5道题', 10: '10道题', 15: '15道题'}.items()]
    form.fill_number.choices = [(key, value) for key, value in
                                {0: '空', 5: '5道题', 10: '10道题', 15: '15道题'}.items()]
    form.answer_number.choices = [(key, value) for key, value in
                                  {0: '空', 3: '3道题', 5: '5道题', 10: '10道题', 15: '15道题'}.items()]
    if profession_choice:
        return jsonify({'ok': True})
    if class_choice:
        return jsonify({'ok': True})

    if form.validate_on_submit():
        # 生成的试卷导入题库，限时考生调用
        print('question maker has done.', form.exam_title.data)
        print('request form get question type : ', request.form.get('single_number'))
        print('type of form start_time ------: ', type(form.start_time.data))

        question_maker_id, examinee_id = 0, 0
        if current_user.__tablename__ == 'questionMakers':
            question_maker_id = current_user.id
        else:
            examinee_id = current_user.id
        # 获取表单提交内容，生成试卷
        if not ExamPaper.query.filter_by(exam_paper_name=form.exam_title.data).first():
            exam_detail = random_make_exam(db, random, Examinee, examinee_id,
                                           form.exam_title.data,
                                           form.total_score.data, form.answer_time.data, form.start_time.data,
                                           form.profession.data, form.department.data, 0,  # form.chapter.data,
                                           question_maker_id)    # common.py
            print('main # unit exam # detail and paper : ', exam_detail[0], exam_detail[1])

            db.session.commit()
            page = request.args.get('page', 1, type=int)
            pagination = ExamPaper.query.order_by(ExamPaper.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)    # 获取 试卷 列表
            exam_papers = pagination.items
            print('exam list  , pagination : ', exam_papers, pagination)

            return redirect(url_for('.exam_paper_list', exam_papers=exam_papers, pagination=pagination))
        flash('试卷名重复，请更改。')
    return render_template('exam_qm_make.html', form=form)


# 考生个人选择出卷
@main.route('/examinee/exam self', methods=['GET', 'POST'])
@login_required
@examinee_required
def exam_self():    # 换用Bootstrap框架 &&++    向上合并 DNF
    departments = Department.query.order_by(Department.id.asc()).all()
    if request.method == 'POST':
        exam_time = request.form.get('exam_time')
        exam_title = request.form.get('exam_title')
        total_score = request.form.get('total_score')
        profession_id = request.form.get('profession_id', 0, type=int)
        department_id = request.form.get('department', 0, type=int)
        chapter_id = request.form.get('chapter_id', 0, type=int)
        start_time, question_maker_id = 0, 0
        if request.form.get('exam_time_input'):
            exam_time = request.form.get('exam_time_input')
        if not ExamPaper.query.filter_by(exam_paper_name=exam_title).first():
            exam_detail = random_make_exam(db, random, Examinee, current_user.id,
                                           exam_title,
                                           total_score, exam_time, start_time,
                                           profession_id, department_id, chapter_id,
                                           question_maker_id)    # common.py

            print('main # exam_self() # detail and paper : ', exam_detail[0], exam_detail[1])

            db.session.commit()
            page = request.args.get('page', 1, type=int)
            exam_paper_self = ExamPaper.query.filter(ExamPaper.is_examinees)
            print('main # exam_self() # exam_paper_self ', exam_paper_self.first().id)

            pagination = ExamPaper.query.order_by(ExamPaper.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)    # 获取 试卷 列表
            exam_papers = pagination.items
            print('exam self name  , pagination : ', exam_papers[0].exam_paper_name, pagination)

            # 表单题量 # common.py
            single_number, multi_number, judge_number, fill_number, answer_number = question_number(request)
            return redirect(url_for('main.examination',
                                    exam_title=exam_papers[0].exam_paper_name,
                                    # question_type_single=single_number,
                                    # question_type_multi=multi_number,
                                    # question_type_judge=judge_number,
                                    # question_type_fill=fill_number,
                                    # question_type_answer=answer_number,
                                    exam_self=1))
        flash('试卷名重复，请更改。')

    return render_template('exam_self_make.html', departments=departments)  # , form=form)    # 取代快速渲染表单来增加加内容，更改样式


# 试卷列表
@main.route('/exam paper list', methods=['GET', 'POST'])
@login_required    # @question_maker_required
def exam_paper_list():
    page = request.args.get('page', 1, type=int)
    is_examinee = request.args.get('is_examinee', 0, type=int)
    print('second or .')

    pagination = ExamPaper.query.order_by(ExamPaper.id.desc())\
        .paginate(page,
                  per_page=current_app.config['QUESTIONS_PER_PAGE'],
                  error_out=False)
    exam_papers = pagination.items
    print('second exam list  , pagination : ', exam_papers, pagination)

    return render_template('exam_paper_list.html',
                           exam_papers=exam_papers, pagination=pagination,
                           QuestionMaker=QuestionMaker, Department=Department,
                           is_examinee=is_examinee)


# 统考卷 进入卷面
@main.route('/examinee/unit_exam', methods=['GET', 'POST'])
@login_required
@examinee_required
def unit_exam():
    start_time = datetime.datetime.now()
    recent_timestamp = start_time.timestamp()    # 当前时间 浮点数

    # import time
    # print(' # unit_exam()  recent time : ', start_time, recent_timestamp,
    #       time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(recent_timestamp+3600)))

    unit_exam_paper1 = ExamPaper.query.filter(ExamPaper.start_time <= recent_timestamp+3600)
    unit_exam_paper2 = unit_exam_paper1.filter(ExamPaper.start_time >= recent_timestamp-3600)
    unit_exam_paper = unit_exam_paper2.first()
        # .filter(ExamPaper.is_examinees != 0)    # 调用 开考60分钟之内的试卷
    print(' # unit_exam() unit paper id !! , name :', unit_exam_paper.exam_paper_name)
    # print(unit_exam_paper2.filter(ExamPaper.is_examinees != 0).first().id)


    # try:
    #     print('unit exam paper is : ', unit_exam_paper.id)
    # except:
    #     print('unit exam paper is None.')

    if unit_exam_paper:
        try:
            print('unit exam paper id ', unit_exam_paper.id)
            unit_exam_finished = ExamPaperFinished.query.filter_by(exam_finished_id=unit_exam_paper.id).\
                filter_by(examinee_id=current_user.id).first()
        except:
            unit_exam_finished = None
            print('此考生暂未做此卷。')
        if not unit_exam_finished:    # 未统考开考
            exam_paper_details = unit_exam_paper.exam_paper_details.all()    # 当前试卷详情 列表
            single_question = 'False'
            multi_question = 'False'
            judge_question = 'False'
            fill_question = 'False'
            answer_question = 'False'

            find_questions = find_detail_question(unit_exam_paper)    # common.py
            if find_questions[0]:    # 从详情表查找单选题型的存在
                single_question = 'True'
            if find_questions[1]:
                multi_question = 'True'
            if find_questions[2]:
                judge_question = 'True'
            if find_questions[3]:
                fill_question = 'True'
            if find_questions[4]:
                answer_question = 'True'
            return redirect(url_for('main.examination',
                                    exam_title=unit_exam_paper.exam_paper_name,
                                    # question_type_single=single_question,
                                    # question_type_multi=multi_question,
                                    # question_type_judge=judge_question,
                                    # question_type_fill=fill_question,
                                    # question_type_answer=answer_question,
                                    is_unit=1))
        else:
            flash('你已参加此次统考，不可重复开考。')
    else:
        flash('当前没有统考卷，不需要统考。')
    return redirect(url_for('main.examinee'))


# 试卷详情
@main.route('/exam paper detail', methods=['GET', 'POST'])
@login_required    # @question_maker_required
def exam_paper_detail():
     if True:  # current_user.__tablename__ == 'questionMakers' or current_user.__tablename__ == 'examinees':
        exam_paper_name = request.args.get('exam_name', None, type=str)
        print('exam paper name is : ', exam_paper_name)

        exam_paper = ExamPaper.query.filter_by(exam_paper_name=exam_paper_name).first()
        try:
            single_questions = SingleQuestion.query.join(ExamPaperDetail,
                                                         ExamPaperDetail.exam_paper_id == exam_paper.id
                                                         ) \
                .filter(ExamPaperDetail.question_type == '单选题')\
                .filter(ExamPaperDetail.question_id == SingleQuestion.id).all()   # 试卷详情 单选题list
            print('single questions is : ', single_questions)
        except:
            single_questions = 0
            flash('卷面没有单选题目。')
        try:
            multi_questions = MultiQuestion.query.join(ExamPaperDetail,
                                                         ExamPaperDetail.exam_paper_id == exam_paper.id
                                                         ) \
                .filter(ExamPaperDetail.question_type == '多选题')\
                .filter(ExamPaperDetail.question_id == MultiQuestion.id).all()
            print('multi questions is : ', multi_questions)
        except:
            multi_questions = 0
            flash('卷面没有多选题目。')
        try:
            judge_questions = JudgeQuestion.query.join(ExamPaperDetail,
                                                         ExamPaperDetail.exam_paper_id == exam_paper.id
                                                         ) \
                .filter(ExamPaperDetail.question_type == '判断题') \
                .filter(ExamPaperDetail.question_id == JudgeQuestion.id).all()
            print('judge questions is : ', judge_questions)
        except:
            judge_questions = 0
            flash('卷面没有判断题目。')
        try:
            fill_questions = FillQuestion.query.join(ExamPaperDetail,
                                                         ExamPaperDetail.exam_paper_id == exam_paper.id
                                                         ) \
                .filter(ExamPaperDetail.question_type == '填空题') \
                .filter(ExamPaperDetail.question_id == FillQuestion.id).all()
            print('fill questions is : ', fill_questions)
        except:
            fill_questions = 0
            flash('卷面没有填空题目。')
        try:
            answer_questions = AnswerQuestion.query.join(ExamPaperDetail,
                                                         ExamPaperDetail.exam_paper_id == exam_paper.id
                                                         ) \
                .filter(ExamPaperDetail.question_type == '问答题') \
                .filter(ExamPaperDetail.question_id == AnswerQuestion.id).all()
            print('answer questions is : ', answer_questions)
        except:
            answer_questions = 0
            flash('卷面没有问答题目。')
        return render_template('exam_paper_detail.html', exam_name=exam_paper_name,
                               single_questions=single_questions,
                               multi_questions=multi_questions,
                               judge_questions=judge_questions,
                               fill_questions=fill_questions,
                               answer_questions=answer_questions)


# 删除试卷
@main.route('/question maker/delete exam', methods=['GET', 'POST'])
@login_required
@question_maker_required
def delete_exam():
    exam_id = request.form.get('exam_id', 0, type=int)
    # delete_type = request.form.get('delete_type', '0', type=str)
    page = request.args.get('page', 1, type=int)
    all_exams = request.args.get('all', False)

    exam = ExamPaper.query.filter_by(id=exam_id).first()
    if page:
        pagination = ExamPaper.query.order_by(ExamPaper.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
        exams = pagination.items
    if all_exams:
        exams = ExamPaper.query.all()
    if exam:
        db.session.delete(exam)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错. 错误是: ', e)
        flash('已删除\'{}\',编号 :{}. '.format(exam.exam_paper_name, exam.id))
        return jsonify({'ok': True})  # 必须有返回值，响应ajax的DataType'json'
    if exams:
        exam_count = len(exams)
        for exam in exams:
            db.session.delete(exam)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错. 错误是：', e)

        flash('已删除此页(所有)，{}项. '.format(exam_count))
        return jsonify({'ok': True})


# 考生考试界面
@main.route('/examination', methods=['GET', 'POST'])
@login_required
def examination():    # 用生成的试卷开考
    exam_self = request.args.get('exam_self', 0, type=int)
    page = request.args.get('page', 1, type=int)

    title = request.args.get('exam_title', 'What Is The Title')

    is_unit = request.args.get('is_unit', 0, type=int)

    start_time = datetime.datetime.now()    # 获取当前 完整时间
    print('start_time is :', start_time, start_time.timestamp())
    print('exam title :  ', title)

    exam_paper = ExamPaper.query.filter(ExamPaper.exam_paper_name == title).first()    # 当前卷名 试卷
    # current_paper_finish = ExamPaperFinished(answer_time=start_time.timestamp())
    # db.session.add(exam_paper)
    # # db.session.commit()
    exam_paper_id = exam_paper.id
    # 开考时间 持久化
    if exam_paper.temp_timestamp != 0 or exam_paper.temp_timestamp != str(0):
        pass
    else:
        exam_paper.temp_timestamp = start_time.timestamp()
        db.session.add(exam_paper)
        db.session.commit()
    print(' long temp_timestamp : ', exam_paper.temp_timestamp, start_time.timestamp())

    import time
    # print('exam_paper start_time  :', exam_paper.start_time,
    #       time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exam_paper.start_time)))

    pagination = []
    question_type = []
    print('exam paper id before post :', exam_paper_id)

    paper_detail = ExamPaperDetail.query.filter(ExamPaperDetail.exam_paper_id == exam_paper_id)
    if paper_detail.filter_by(question_type='单选题').first():    # 单选题 试卷详情
        question_type.append('True')
        questions = SingleQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.exam_paper_id == exam_paper_id)\
            .filter(ExamPaperDetail.question_id == SingleQuestion.id) \
            .filter(ExamPaperDetail.question_type == '单选题')
        pagination_single = questions \
            .paginate(page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False)
        pagination.append(pagination_single)
        # print('examination() #S questions first id: ', questions.first().id)
    else:
        question_type.append('False')
        pagination.append(0)

    if paper_detail.filter_by(question_type='多选题').first():
        question_type.append('True')
        questions = MultiQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.exam_paper_id == exam_paper_id) \
            .filter(ExamPaperDetail.question_id == MultiQuestion.id) \
            .filter(ExamPaperDetail.question_type == '多选题')
        pagination_multi = questions \
            .paginate(page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False)
        pagination.append(pagination_multi)
        # print('examination() #M questions first id: ', questions.first().id)
    else:
        question_type.append('False')
        pagination.append(0)

    if paper_detail.filter_by(question_type='判断题').first():
        question_type.append('True')
        questions = JudgeQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.exam_paper_id == exam_paper_id) \
            .filter(ExamPaperDetail.question_id == JudgeQuestion.id) \
            .filter(ExamPaperDetail.question_type == '判断题')
        pagination_judge = questions \
            .paginate(page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False)
        pagination.append(pagination_judge)
        # print('examination() #J questions first id: ', questions.first().id)

    else:
        question_type.append('False')
        pagination.append(0)

    if paper_detail.filter_by(question_type='填空题').first():
        question_type.append('True')
        questions = FillQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.exam_paper_id == exam_paper_id) \
            .filter(ExamPaperDetail.question_id == FillQuestion.id) \
            .filter(ExamPaperDetail.question_type == '填空题')
        pagination_fill = questions \
            .paginate(page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False)
        pagination.append(pagination_fill)
        # print('examination() #F questions first id: ', questions.first().id)

    else:
        question_type.append('False')
        pagination.append(0)

    if paper_detail.filter_by(question_type='问答题').first():
        question_type.append('True')
        questions = AnswerQuestion.query \
            .join(ExamPaperDetail, ExamPaperDetail.exam_paper_id == exam_paper_id) \
            .filter(ExamPaperDetail.question_id == AnswerQuestion.id) \
            .filter(ExamPaperDetail.question_type == '问答题')
        pagination_answer = questions \
            .paginate(page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False)
        pagination.append(pagination_answer)
        # print('examination() #A questions first id: ', questions.first().id)

    else:
        question_type.append('False')
        pagination.append(0)

    if request.method == 'POST':    # 验证表单不为空  调用jQuery.js验证? DNF

        end_time = datetime.datetime.now()    # 当前结束时间
        print(' end_time  : ', end_time, end_time.timestamp())

        d1 = datetime.datetime.fromtimestamp(int(exam_paper.temp_timestamp))
        str1 = d1.strftime("%Y-%m-%d %H:%M:%S")
        d2 = datetime.datetime.fromtimestamp(int(exam_paper.start_time))
        str2 = d2.strftime("%Y-%m-%d %H:%M:%S.%f")
        print(' temp_time , start_time , end_time : ', str1, '--', str2, '--', end_time)

        used_time = end_time.timestamp() - float(exam_paper.temp_timestamp)
        str1 = datetime.datetime.strptime(str1, "%Y-%m-%d %H:%M:%S")
        print('used_time -!! , s- , paper id :', end_time-str1, used_time, exam_paper.id, type(exam_paper))

        # 生成 答卷表
        exam_paper_finished = ExamPaperFinished(answer_time=used_time)
        exam_paper_finished.examPapers = exam_paper
        exam_paper_finished.examinees = current_user
        exam_paper_finished.is_corrected = 0
        if exam_self:
            exam_paper_finished.is_corrected = 1
        db.session.add(exam_paper_finished)
        # db.session.commit()
        # print('main # examination # exam paper finished id , finished exam paper id : ', exam_paper_finished.id,
        #       exam_paper_finished.exam_paper_id)

        # 获取 考试提交表单回答内容 生成 答卷详情
        # 答卷详情 单选题
        if pagination[0]:    # 使用 表单提交前的试卷信息
            for question in pagination[0].items:
                question_input_name = 'sq'+str(question.id)    # 获取 考试input框“name”属性值
                exam_finished_paper = ExamPaperFinishedDetail(
                    answered_content=request.form.get(question_input_name),
                    question_type='单选题',
                    question_id=question.id,
                    answer=question.answer,
                    per_score=question.score,
                    examFinished=exam_paper_finished)
                db.session.add(exam_finished_paper)
                db.session.commit()

        # 答卷详情 多选题
        if pagination[1]:  # 使用 表单提交前的试卷信息
            for question in pagination[1].items:
                question_input_name = 'mq'+str(question.id)  # 获取 考试input框“name”属性值
                content_str = request.form.getlist(question_input_name)
                content_strs = "".join(content_str)
                # print('content str :', content_strs)
                exam_finished_paper = ExamPaperFinishedDetail(
                    answered_content=content_strs,
                    question_type='多选题',
                    question_id=question.id,
                    answer=question.answer,
                    per_score=question.score)
                db.session.add(exam_finished_paper)
                exam_finished_paper.examFinished = exam_paper_finished  # 答卷与详情 绑定外键
                db.session.commit()

        # 答卷详情 判断题
        if pagination[2]:  # 使用 表单提交前的试卷信息
            for question in pagination[2].items:
                question_input_name = 'jq'+str(question.id)  # 获取 考试input框“name”属性值
                exam_finished_paper = ExamPaperFinishedDetail(
                    answered_content=request.form.get(question_input_name),
                    question_type='判断题',
                    question_id=question.id,
                    answer=question.answer,
                    per_score=question.score)
                db.session.add(exam_finished_paper)
                exam_finished_paper.examFinished = exam_paper_finished  # 答卷与详情 绑定外键
                db.session.commit()

        # 答卷详情 填空题
        if pagination[3]:  # 使用 表单提交前的试卷信息
            for question in pagination[3].items:
                form_content = []
                for i in range(6):
                    i += 1
                    question_input_name = ('fq'+str(i)+str(question.id))  # 获取 考试input框“name”属性值
                    print('fill question input answer name : ', question_input_name)
                    if request.form.get(question_input_name, None, type=str):
                        form_content.append(request.form.get(question_input_name))
                form_content_str = ",".join(form_content)    # 多空答案 list 转 str
                print(' form content str : ', form_content_str)

                exam_finished_paper = ExamPaperFinishedDetail(
                    answered_content=form_content_str,
                    question_type='填空题',
                    question_id=question.id,
                    answer=question.answer,
                    per_score=question.score)
                db.session.add(exam_finished_paper)
                exam_finished_paper.examFinished = exam_paper_finished  # 答卷与详情 绑定外键
                db.session.commit()

        # 答卷详情 问答题
        if pagination[4]:
            for question in pagination[4].items:
                question_input_name = 'aq'+str(question.id)
                exam_finished_paper = ExamPaperFinishedDetail(
                    answered_content=request.form.get(question_input_name),
                    question_type='问答题',
                    question_id=question.id,
                    answer=question.answer,
                    per_score=question.score)
                db.session.add(exam_finished_paper)
                exam_finished_paper.examFinished = exam_paper_finished
                db.session.commit()

        return redirect(url_for('.complete_exam', exam_paper_finished_id=exam_paper_finished.id))
    return render_template('examination.html',
                           question_type=question_type,
                           pagination=pagination,
                           start_time=float(exam_paper.start_time),    # exam_paper.start_time 持久化时间 DNC
                           exam_time=float(exam_paper.end_time),
                           exam_title=title)


# 考生答卷
@main.route('/examinee/complete exam paper', methods=['GET', 'POST'])
@login_required
@examinee_required
def complete_exam():
    exam_paper_finished_id = request.args.get('exam_paper_finished_id')
    print('complete_exam() ## exam paper finished id : {} . '.format(exam_paper_finished_id))

    exam_paper_finished = ExamPaperFinished.query.filter_by(id=exam_paper_finished_id).first()

    answer_time = exam_paper_finished.answer_time  # // 60    # 用时 分钟    DNF useless
    print('complete answer_time : ', answer_time, type(answer_time))
    exam_paper_id = exam_paper_finished.exam_paper_id
    exam_paper = ExamPaper.query.filter_by(id=exam_paper_id).first()
    exam_paper_name = exam_paper.exam_paper_name
    answer_time_set = exam_paper.answer_time_set
    print('answer_time_set : ', answer_time_set)
    if answer_time_set:
        if float(answer_time_set) > answer_time:
            submit_type = '主动'
        else:
            submit_type = '强制'
    else:
        submit_type = '主动'
    question_count = [0, 0, 0, 0, 0]
    answer_bytes = 0
    exam_paper_finished_detail = ExamPaperFinishedDetail.query.filter(
        ExamPaperFinishedDetail.exam_paper_finished_id == exam_paper_finished.id).all()
    for paper_detail in exam_paper_finished_detail:
        if paper_detail.question_type == '单选题' and paper_detail.answered_content:
            question_count[0] += 1
        elif paper_detail.question_type == '多选题' and paper_detail.answered_content:
            question_count[1] += 1
        elif paper_detail.question_type == '判断题' and paper_detail.answered_content:
            question_count[2] += 1
        elif paper_detail.question_type == '填空题' and paper_detail.answered_content:
            question_count[3] += 1
            answer_bytes += len(paper_detail.answered_content)
        elif paper_detail.question_type == '问答题' and paper_detail.answered_content:
            question_count[4] += 1
            answer_bytes += len(paper_detail.answered_content)

    # 客观题 自动改卷
    exam_paper_finish = ExamPaperFinished.query.filter_by(id=exam_paper_finished_id)  # 指定试卷 答卷(统考可有多个)
    exam_finishes = exam_paper_finish.all()
    # if len(exam_finishes) <= 1:
    #     print('exam finish len 1 id : ', exam_finishes[0].id)
    #     exam_finished_details_all = ExamPaperFinishedDetail.query \
    #         .filter_by(exam_paper_finished_id=exam_finishes[0].id)    # 答卷题详情列表
    # else:
    for exam_finish in exam_finishes:
        print('# complete_exam()  exam finish id  : ', exam_finish.id)
        exam_finished_details = ExamPaperFinishedDetail.query \
            .filter_by(exam_paper_finished_id=exam_finish.id)
        exam_finished_objective = exam_finished_details.filter(ExamPaperFinishedDetail.question_type != '问答题').all()
        # 客观题分数统计
        scores = 0
        for exam_finished in exam_finished_objective:
            if exam_finished.question_type != '填空题' and exam_finished.question_type != '多选题':
                if exam_finished.answered_content == exam_finished.answer:
                    scores += exam_finished.per_score
            else:
                print(' exam finished id , answered content : ', exam_finished.id, exam_finished.answered_content)

                content_list = exam_finished.answered_content  #.split(",")
                print('answered_content list : ', content_list)

                if exam_finished.question_type == '多选题':
                    answers = exam_finished.answer
                    if content_list == answers:
                        print('TTTTTTTTTTTTT')
                        scores += exam_finished.per_score
                        print('per_score : ', exam_finished.per_score)
                    print('multiQuestion answers : ', answers)
                else:
                    answers = exam_finished.answer.split(",")
                    print('finished answer : ', answers, type(answers))
                    all_check = []
                    for answers_content in content_list:
                        for answer in answers:
                            print('content list answer , content answer : ', answer, type(answer), answers_content)
                            if answers_content != answer:
                                all_check.append(0)
                            else:
                                all_check.append(1)
                        print('all check : ', all_check)
                    check_num = [check_num for check_num in all_check if check_num != 0]
                    print('check num : ', check_num)
                    if check_num:
                        scores += exam_finished.per_score

        score = Score(objective_score=scores)
        score.exam_paper_finish_id = exam_finish.id
        score.examinee_id = exam_finish.examinee_id
        print(' scores , id : ', scores, score.id)
        db.session.add(score)
    return render_template('complete_exam.html',
                           exam_paper_name=exam_paper_name,
                           answer_time=int(answer_time),
                           question_count=question_count,
                           answer_bytes=answer_bytes,
                           submit_type=submit_type)
    # DNF 传入情况   设置status是否查看回答情况


# 答卷列表
@main.route('/exam finished list', methods=['GET', 'POST'])
@login_required    # @examinee_required
def exam_finished_list():
    page = request.args.get('page', 1, type=int)
    is_examinee = request.args.get('is_examinee', 0, type=int)
    is_corrected = request.args.get('is_corrected', 0, type=int)
    unit_count = request.args.get('unit_count', 0, type=int)

    pagination = None
    exam_paper = None
    exam_finisheds = []
    try:
        # 已作答的试卷(多份)
        exam_paper = ExamPaper.query.join(ExamPaperFinished, ExamPaperFinished.exam_paper_id == ExamPaper.id)
        # 已有答卷
        exam_paper_finished = ExamPaperFinished.query.join(ExamPaper, ExamPaper.id == ExamPaperFinished.exam_paper_id)
        # 一对多联结查询？
    except:
        flash('没有作答和答卷。')
    if exam_paper_finished:
        if is_examinee:
            pagination = exam_paper_finished.order_by(
                ExamPaperFinished.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
            print('finished list is examinee .', (pagination.items)[0].id)
        else:
            pagination = exam_paper_finished.filter(ExamPaperFinished.is_corrected != 1).order_by(
                ExamPaperFinished.id.asc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)    # 未改答卷
        if is_corrected:
            pagination = exam_paper_finished.filter(ExamPaperFinished.is_corrected == 1).order_by(
                ExamPaperFinished.id.asc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)    # 已改答卷
        # if exam_paper.all().__len__() > 1:
        #     for exam_paper in exam_paper.all():
        #         exam_finisheds += ExamPaperFinished.query.filter_by(exam_paper_id=exam_paper.id).all()
        # else:
        #     exam_finisheds = ExamPaperFinished.query.filter_by(exam_paper_id=exam_paper.first().id).all()
        #
        # for exam in pagination.items:
        #     print('exam finished list id : ', exam.id, type(exam))
    return render_template('exam_finished_list.html',
                           exam_papers=exam_paper, pagination=pagination,
                           Department=Department, ExamPaperFinished=ExamPaperFinished,
                           Score=Score, is_corrected=is_corrected, unit_count=unit_count,
                           exam_finisheds=exam_finisheds, Examinee=Examinee, ExamPaper=ExamPaper,
                           is_examinee=is_examinee)


# 答卷 详情
@main.route('/exam finished detail', methods=['GET', 'POST'])
@login_required
def exam_finished_detail():
    exam_paper_id = request.args.get('exam_paper_id', 0, type=int)
    examinee_id = request.args.get('examinee_id', 0, type=int)

    exam_paper_name = ExamPaper.query.filter_by(id=exam_paper_id).first().exam_paper_name
    exam_finisheds = ExamPaperFinished.query.filter_by(exam_paper_id=exam_paper_id).\
        filter_by(examinee_id=examinee_id).all()
    exam_finished_id = exam_finisheds[-1].id    # 最新的答卷
    print(' # finished_detail finished id ', exam_finished_id)

    exam_finished_details = ExamPaperFinishedDetail.query.filter_by(exam_paper_finished_id=exam_finished_id)
    print(' # finished_detail details ', exam_finished_details.first().question_type)

    try:
        exam_finished_detail_singles = exam_finished_details.filter_by(question_type='单选题').all()
    except:
        exam_finished_detail_singles = None
    try:
        exam_finished_detail_multis = exam_finished_details.filter_by(question_type='多选题').all()
    except:
        exam_finished_detail_multis = None
    try:
        exam_finished_detail_judges = exam_finished_details.filter_by(question_type='判断题').all()
    except:
        exam_finished_detail_judges = None
    try:
        exam_finished_detail_fills = exam_finished_details.filter_by(question_type='填空题').all()
    except:
        exam_finished_detail_fills = None
    try:
        exam_finished_detail_answers = exam_finished_details.filter_by(question_type='问答题').all()
    except:
        exam_finished_detail_answers = None
    return render_template('exam_finished_detail.html',
                           exam_paper_name=exam_paper_name, singles=exam_finished_detail_singles,
                           multis=exam_finished_detail_multis, judges=exam_finished_detail_judges,
                           fills=exam_finished_detail_fills, answers=exam_finished_detail_answers,
                           SingleQuestion=SingleQuestion, MultiQuestion=MultiQuestion, JudgeQuestion=JudgeQuestion,
                           FillQuestion=FillQuestion, AnswerQuestion=AnswerQuestion)


# 待改答卷  由答卷列表点击进入判改页面
@main.route('/corrector/correct exam paper', methods=['GET', 'POST'])
@login_required
@corrector_required
def correct_exam_paper():
    page = request.args.get('page', 1, type=int)
    examinee_id = request.args.get('correct_examinee_id', 0, type=int)
    exam_paper_id = request.args.get('correct_exam_paper_id', 0, type=int)
    print(' # correct_exam_paper()examinee , exam_paper id request ', examinee_id, exam_paper_id)

    exam_paper_finish = ExamPaperFinished.query.join(ExamPaper, ExamPaper.id == ExamPaperFinished.exam_paper_id)\
        .filter(ExamPaper.id == exam_paper_id).filter(ExamPaperFinished.examinee_id == examinee_id)    # 指定考生答卷
    exam_finishes = exam_paper_finish.all()
    exam_finished_last = (exam_paper_finish.all())[-1]
    print('correct_exam_paper() # exam finishes :', exam_finishes, type(exam_finishes))
    exam_finish_list = []
    pagination = 0
    exam_finished_details = 0
    for exam_finish in exam_finishes:
        print(' # correct_exam_paper()  exam finish id  : ', exam_finish.id)

        finished_correct_detail = ExamPaperFinishedDetail.query \
            .filter_by(exam_paper_finished_id=exam_finish.id)

        exam_finished_details = finished_correct_detail.filter_by(question_type='问答题')    # 最新答卷 详情

        pagination = exam_finished_details.paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
        exam_finished_details = exam_finished_details.all()
        print(' # correct_exam_paper()  exam paper , one finish id : ', exam_paper_id, exam_paper_finish.first().id)

    if request.method == 'POST':
        correct_scores = 0
        for finished_detail in exam_finished_details:
            correct_scores += request.form.get('correct_score'+str(finished_detail.id), 0, type=int)
            correct = ExamPaperCorrected(
                corrected_content=request.form.get('correct_item'+str(finished_detail.id), None, type=str),
                corrected_score=request.form.get('correct_score'+str(finished_detail.id), 0, type=int)
            )
            correct.exam_paper_finished_id = exam_finished_last.id    # 一人一卷 只考一次？
            correct.corrector_id = current_user.id
            db.session.add(correct)
            db.session.commit()

        score = Score.query.filter(Score.exam_paper_finish_id == exam_finished_last.id).first()
        score.subjective_score = correct_scores
        score.total_score = score.objective_score + correct_scores
        db.session.add(score)
        # commit()+?
        print('# main # correct_exam_paper() score.sub and total ', score.subjective_score, score.total_score)

        exam_finished_last.is_corrected = 1
        db.session.add(exam_finished_last)
        print('exam finished last  is_corrected : ', exam_finished_last.is_corrected,
              ExamPaperFinished.query.filter_by(id=exam_finished_last.id).first().is_corrected)

        return redirect(url_for('main.exam_finished_list', is_corrected=1))
    return render_template('correct_exam_paper.html',
                           pagination=pagination, exam_paper_finish=exam_paper_finish.first(),
                           exam_finished_details=exam_finished_details, AnswerQuestion=AnswerQuestion)


# 已改卷
@main.route('/corrector/corrected exam paper', methods=['GET', 'POST'])
@login_required
@corrector_required
def corrected_exam_paper():    # 统考 统计（排序）等   DNF

    page = request.args.get('page', 1, type=int)
    exam_paper_id = request.args.get('exam_paper_id', 0, type=int)
    examinee_id = request.args.get('examinee_id', 0, type=int)
    # exam_paper_name = request.args.get('exam_paper_name')

    # 答卷的问答题
    exam_paper_finish = ExamPaperFinished.query.filter_by(exam_paper_id=exam_paper_id) \
        .filter_by(examinee_id=examinee_id)# 指定试卷 答卷
    print('main # corrected_exam_paper() # exam_paper_finish ', exam_paper_finish.first().id, exam_paper_finish.all())

    # 答卷题详情列表
    exam_finished_details_all = ExamPaperFinishedDetail.query \
        .filter_by(exam_paper_finished_id=exam_paper_finish.first().id)

    exam_finished_details = exam_finished_details_all.filter_by(question_type='问答题').all()    # 最新答卷 详情
    pagination = exam_paper_finish.paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False)
    # exam_paper_finish = ExamPaperFinished.query.filter_by(id=exam_finished_id).first()
    print('exam paper and one finish id : ', exam_paper_id, exam_paper_finish.first().id)

    return render_template('corrected_exam_paper.html',
                           pagination=pagination, exam_paper_finish=(exam_paper_finish.all())[-1],
                           exam_finished_details=exam_finished_details, AnswerQuestion=AnswerQuestion,
                           ExamPaperCorrected=ExamPaperCorrected)    # DNF check


# 统考统计
@main.route('/unit exam count -', methods=['GET', 'POST'])
@login_required
def unit_exam_count():
    exam_paper_id = request.args.get('exam_paper_id', 0, type=int)
    is_examinee = request.args.get('is_examinee', 0, type=int)
    examinee_id = request.args.get('examinee_id', 0, type=int)
    print(' # unit_exam_count()  is examinee  : ', is_examinee)
    pagination = None
    exam_paper = None
    exam_finisheds = None
    try:
        exam_paper = ExamPaper.query.filter_by(id=exam_paper_id).first()
        exam_finisheds = ExamPaperFinished.query.filter_by(exam_paper_id=exam_paper_id)
        # exam_finisheds2 = ExamPaperFinished.query.filter_by(is_corrected=1).all()
    except:
        flash('考试统计 此试卷没有答卷。')
    scores = []
    try:
        for exam_finished in exam_finisheds.all():
            scores.append(Score.query.filter_by(exam_paper_finish_id=exam_finished.id).first())
    except:
        flash('没有答卷的分数。')
    try:
        if current_user.id == is_examinee:
            my_exam_finished = exam_finisheds.filter_by(examinee_id=is_examinee).first()
            print(' my finished : ', my_exam_finished.id)
            my_score = Score.query.filter_by(exam_paper_finish_id=my_exam_finished.id).first().total_score
        # my_score = my_scores.filter_by(examinee_id=current_user.id)
        print(' # unit_exam_count()  my score : ', my_score, type(my_score))
    except:
        if current_user.__tablename__ == 'examinees':
            print('my score is not found.')
            flash('没有我的这张试卷成绩。')
            return redirect(url_for('main.exam_finished_list', is_examinee=1))
    count_scores = 0
    count_score = []
    bad_score_count = 0
    my_order = 1
    for score in scores:
        if score:
            print('unit_exam_count() # score id ', score.id)
            if score.total_score:
                count_score.append(score.total_score)
                print('score total_score : ', score.total_score)
                if score.total_score < 60:
                    bad_score_count += 1
                    print('bad count :', bad_score_count)
    if count_score.__len__() < scores.__len__():
        flash('统考卷还未改完。')
        if current_user.__tablename__ == 'correctors':
            return redirect(url_for('main.corrector'))
        else:
            return redirect(url_for('main.exam_finished_list', is_examinee=1))
    if scores.__len__() > 1:
        print(' scores len ', scores.__len__(), '')
        list_score = sorted(count_score)
        list_score = list_score[::-1]
        try:
            my_order = list_score.index(my_score)
            my_order += 1
            print('scores , my score , order :', list_score, my_score, my_order)
        except:
            print('unit my score is None.')

    for add_scores in count_score:
        count_scores += add_scores
    per_score = count_scores / scores.__len__()
    good_rate = (scores.__len__() - bad_score_count) / scores.__len__()
    good_rate = round(good_rate, 2)
    return render_template('unit_exam_count.html',
                           exam_paper=exam_paper, per_score=per_score,
                           bad_score_count=bad_score_count, good_rate=good_rate,
                           Department=Department, ExamPaperFinished=ExamPaperFinished,
                           scores=scores, is_examinee=is_examinee, my_order=my_order,
                           Score=Score)


# 通知
@main.route('/corrector/corrected exam paper', methods=['GET', 'POST'])
@login_required
def xxx():
    pass