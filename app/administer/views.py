import datetime
import os
# from flask import render_template, redirect, url_for, abort, flash, request,\
#     current_app
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app
# from flask_login import login_required, current_user

from flask_login import login_required, current_user
from flask import jsonify
from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime
from .. import db
from ..models import Admin, QuestionMaker, Examinee, Corrector, Profession, ClassTable, \
    Department, ChapterName, RelationLink
from .forms import AddQuestionMakerForm, AddExamineeForm, \
     AddDepartmentForm, AddCorrectorForm, ChangeDepartmentForm, \
     ChangeQuestionMakerForm, AddProfessionForm, ChangeProfessionForm, \
     AddClassTableForm, ChangeClassTableForm, AddChapterForm, \
    ChangeChapterForm, AddLinkForm, ChangeLinkForm
from ..main.forms import AddFileForm
from ..decorators import admin_required
from . import administer
from ..common import db_add_commit, excel_submit, register_examinee


@administer.route('/', methods=['GET', 'POST'])
def ad_test():
    return render_template('admin.html')


@administer.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    user = request.args.get('user')    # ...? '
    name = current_user.name
    print('current user :', user, name, current_user, current_user.id, current_user.__name__)
    return render_template('admin.html', name=user.name)


# 考生管理
    # 单个添加考生
@administer.route('/add examinee', methods=['GET', 'POST'])
@login_required
@admin_required
def add_examinee():
    form = AddExamineeForm()
    form.sex.choices = [(1, '男'), (2, '女')]
    if form.validate_on_submit():
        # 表单导入考生模型 库
        user = register_examinee(Examinee,
                                 form.account.data, form.password.data,
                                 form.name.data, form.sex.data, form.birthday.data)    # common.py
        add_user = db_add_commit(db, user)    # common.py
        if add_user:
            flash('考生已添加!')
        else:
            flash('信息格式有误，导入失败.')

        return redirect(url_for('.add_examinee'))
    return render_template('administer/add_examinee.html', form=form)


# 通过上传Excel表批量自动导入考生
@administer.route('/add large examinee', methods=['GET', 'POST'])
@login_required
@admin_required
def add_excel_examinee():
    form = AddFileForm()
    if request.method == 'POST':
        print('submit ')
        try:
            excel_data = excel_submit(os, request, current_app, 'file',
                                 open_workbook)    # functions.py
        except:
            flash('Excel表项设置有误，不符合要求。')
            return redirect(url_for('.add_excel_examinee'))
        print('excels ')
        if excel_data[3].find('用户') == -1:
            flash('请选择表名正确的Excel(“用户表”)。')
            return redirect(url_for('.add_excel_examinee'))
        for key in excel_data[0]:
            if key[6] == '男':    # 设置符合数据库导入的Integer数据类型
                key[6] = int(1)
            elif key[6] == '女':
                key[6] = int(2)

            d = xldate_as_datetime(key[7], 0)    # 日期格式转化
            d2 = datetime.date(d.year, d.month, d.day)  # date type; datetime.datetime.strftime(d, '%Y-%m-%d')

            if Examinee.query.filter_by(account=str(key[1])).first():
                # Excel表重复的考生不导入数据库
                continue
            else:
                user = register_examinee(Examinee, str(key[1]), str(int(key[2])),    # functions.py
                                         key[4], key[6], d2, key[5], key[3], key[8])
            add_user = db_add_commit(db, user)    # functions.py
            if not add_user:
                flash('信息格式有误，导入失败.')

        flash('成功导入考生.共有 {} 行, {} 项'.format(excel_data[1], excel_data[2]))
        # time.sleep(1)
        return redirect(url_for('.examinee_list'))
    return render_template('administer/add_excel_examinee.html', form=form)


@administer.route('/examinee list', methods=['GET', 'POST'])
@login_required
@admin_required
def examinee_list():
    page = request.args.get('page', 1, type=int)
    name = request.form.get('search_examinee', None, type=str)

    pagination = Examinee.query.order_by(Examinee.id.asc()).paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    if name:
        users = []
        examinee = Examinee.query.filter_by(name=name).first()
        if not examinee:
            examinee = Examinee.query.filter_by(account=name).first()
        users.append(examinee)
        print('users ', users)
        if not users[0]:
            flash('没有此考生。')
    return render_template('administer/examinee_list.html', examinees=users, pagination=pagination)


# 更新用户个人信息
@administer.route('/user update', methods=['GET', 'POST'])
@login_required
def update_user():
    user_account = request.form.get('update_account', None, type=str)
    content = request.form.get('content', None, type=str)
    content_type = request.form.get('content_type', None, type=str)
    # print('user is  ', user_account)
    if current_user.__tablename__ == 'admins' and user_account:
        if user_account[0] == 'E':
            user = Examinee
        elif user_account[0] == 'C':
            user = Corrector
        elif user_account[0] == 'Q':
            user = QuestionMaker
        else:
            user = Admin
        user_he = user.query.filter_by(account=user_account).first()
        # print('user is ', user, user_he)
        # print('account : ', user_account, '!--- content :', content, '!--- type :', content_type)
    else:
        user_he = current_user
    # 选择修改项
    if content_type == 'account':
        user_he.account = content
    if content_type == 'name':
        user_he.name = content
    elif content_type == 'password':
        user_he.password = content
    elif content_type == 'sex':
        user_he.sex = content
    elif content_type == 'birthday':
        user_he.birthday = content
    elif content_type == 'phone':
        user_he.phone = content
    elif content_type == 'address':
        user_he.address = content
    elif content_type == 'status':
        user_he.status = content
    elif content_type == 'id_card':
        user_he.id_card = content
    if user_he:
        db.session.add(user_he)    # 数据库更新
        db.session.commit()
        # flash('已更新该项。')
        return jsonify({'ok': True})


@administer.route('/delete examinee', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_examinee():
    examinee_id = request.form.get('examinee_id', 0, type=int)
    page = request.args.get('page', 1, type=int)
    delete_page = request.args.get('delete_page', 0, type=int)
    all_examinees = request.args.get('all', False, type=str)
    user = Examinee.query.filter_by(id=examinee_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        info = '已删除考生： '+user.name
        flash(info)
        return jsonify({'ok': True})
    if page or delete_page:
        pagination = Examinee.query.order_by(Examinee.id.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
        examinees = pagination.items
    if all_examinees:
        examinees = Examinee.query.all()
    if examinees:
        for examinee in examinees:
            db.session.delete(examinee)
        try:
            db.session.commit()
        except Exception as e:
            print('数据提交出错. 错误是：', e)
        flash('已删除此页(所有)\'{}\'. '.format('考生'))
        return redirect(url_for('administer.examinee_list'))


# 出题员管理
@administer.route('/add_question_maker', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question_maker():
    form = AddQuestionMakerForm()
    form.depart_id.choices = [(d.id, d.name) for d in Department.query.order_by('id')]
    if form.validate_on_submit():
        user = QuestionMaker(account=form.account.data,
                             id_card=form.id_card.data,
                             name=form.name.data,
                             password=form.password.data,
                             department_id=form.depart_id.data)
        db.session.add(user)
        db.session.commit()
        flash('已添加出题员: ' + user.name )
        return redirect(url_for('.add_question_maker'))
    return render_template('administer/add_question_maker.html', form=form)


# 出题员列表
@administer.route('/question_maker_list', methods=['GET', 'POST'])
@login_required
@admin_required
def question_maker_list():
    page = request.args.get('page', 1, type=int)
    pagination = QuestionMaker.query.order_by(QuestionMaker.id.desc()).paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('administer/question_maker_list.html', question_makers=users, pagination=pagination)


@administer.route('/delete question_maker', methods=['GET','POST'])
@login_required
@admin_required
def delete_question_maker():
    question_maker_id = int(request.form.get('question_maker_id', 0))
    user = QuestionMaker.query.filter_by(id=question_maker_id).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = '已删除出题员： '+username
        flash(info)
        return jsonify({'ok': True})


@administer.route('/change_question_maker/<question_maker_name>/<depart_name>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_question_maker(question_maker_name, depart_name):
    form = ChangeQuestionMakerForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by('id')]
    if form.validate_on_submit():
        QuestionMaker.query.filter_by(name=question_maker_name).update({
            'name': form.name.data,
            'department_id': form.department_id.data})    # flask-SQLAlchemy的数据库更新
        db.session.commit()
        flash('已更新出题员!')
        return redirect(url_for('.question_maker_list'))
    department = Department.query.filter_by(name=depart_name).first()
    form.name.data = question_maker_name
    if department:
        form.department_id.data = department.id
    return render_template('administer/change_question_maker.html', form=form)


# 改卷员管理
    # 单个添加改卷员
@administer.route('/add_corrector', methods=['GET', 'POST'])
@login_required
@admin_required
def add_corrector():
    form = AddCorrectorForm()
    if form.validate_on_submit():
        print('submited')
        user = Corrector(
            account=form.account.data,
            id_card=form.id_card.data,
            name=form.name.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('已添加改卷员： ' + user.name)
        return redirect(url_for('.add_corrector'))
    return render_template('administer/add_corrector.html', form=form)


# 改卷员列表
@administer.route('/corrector_list', methods=['GET', 'POST'])
@login_required
@admin_required
def corrector_list():
    page = request.args.get('page', 1, type=int)
    pagination = Corrector.query.order_by(Corrector.id.desc()).paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('administer/corrector_list.html', correctors=users, pagination=pagination)


# 删除改卷员
@administer.route('/delete_corrector', methods=['GET','POST'])
@login_required
@admin_required
def delete_corrector():
    corrector_id = int(request.form.get('corrector_id', 0))
    user = Corrector.query.filter_by(id=corrector_id).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = '已删除改卷员 ' + username
        flash(info)
        return jsonify({'ok': True})


# 设置专业
@administer.route('/profession', methods=['GET', 'POST'])
@login_required
def profession():
    form = 0
    pagination = 0
    empty = 1
    set_profession = request.args.get('set_profession', 0)
    profession_list = request.args.get('profession_list', 1)
    profession_id = request.args.get('profession_id', 0)
    # print('profession id in args : ', profession_id)
    if int(set_profession):
        if profession_id:
            form = ChangeProfessionForm()
        else:
            form = AddProfessionForm()
        empty = 0
        if form.validate_on_submit():  # 表单通过验证并提交
            if profession_id:    # 修改专业
                Profession.query.filter_by(id=profession_id).update({'name': form.name.data})
                db.session.commit()
                flash('已修改专业!')
            else:
                professions = Profession(name=form.name.data)    # 添加专业
                db.session.add(professions)
                db.session.commit()
                flash('已添加专业!')
            return redirect(url_for('administer.profession', set_profession=0, profession_list=1))

    if int(profession_list):  # 查看列表
        page = request.args.get('page', 1, type=int)
        try:
            pagination = Profession.query.order_by(Profession.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
        except: flash('没有设置专业，请添加。')
        empty = 0
    return render_template("administer/profession.html", form=form, pagination=pagination, empty=int(empty))


@administer.route('/delete profession', methods=['GET','POST'])
@login_required
@admin_required
def delete_profession():
    profession_id = int(request.form.get('profession_id', 0))
    profession_one = Profession.query.filter_by(id=profession_id).first()
    profession_name = profession_one.name
    if profession_one:
        db.session.delete(profession_one)
        db.session.commit()
        flash('已删除专业： '+profession_name)
        return jsonify({'ok': True})


# 设置班级
@administer.route('/class table', methods=['GET', 'POST'])
@login_required
def class_table():
    form = 0
    pagination = 0
    empty = 1
    set_class = request.args.get('set_class_table', 0)
    class_list = request.args.get('class_table_list', 1)
    class_id = request.args.get('class_table_id', 0)

    if int(set_class):
        if class_id:
            form = ChangeClassTableForm()
        else:
            form = AddClassTableForm()
        form.profession_id.choices = [(d.id, d.name) for d in Profession.query.order_by('id')]
        empty = 0
        if form.validate_on_submit():  # 表单通过验证并提交
            if class_id:
                ClassTable.query.filter_by(id=class_id).update({
                    'name': form.name.data,
                    'profession_id': form.profession_id.data})
                db.session.commit()
                flash('已修改班级!')
            else:
                classes = ClassTable(name=form.name.data, profession_id=form.profession_id.data)
                db.session.add(classes)
                db.session.commit()
                flash('已添加班级!')
            return redirect(url_for('administer.class_table', set_class=0, class_list=1))

    if int(class_list):  # 查看列表
        page = request.args.get('page', 1, type=int)
        try:
            pagination = ClassTable.query.order_by(ClassTable.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
        except:
            flash('没有设置班级，请添加。')
        empty = 0
    return render_template("administer/class.html", form=form, pagination=pagination, empty=int(empty))


@administer.route('/delete class', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_class_table():
    class_id = int(request.form.get('class_table_id', 0))
    class_one = ClassTable.query.filter_by(id=class_id).first()
    class_name = class_one.name
    if class_one:
        db.session.delete(class_one)
        db.session.commit()
        flash('已删除班级： ' + class_name)
        return jsonify({'ok': True})


# 添加课程管理
@administer.route('/add department', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    form = AddDepartmentForm()
    form.class_table_id.choices = [(d.id, d.name) for d in ClassTable.query.order_by('id')]
    if form.validate_on_submit():
        department = Department(name=form.name.data, class_id=form.class_table_id.data)
        db.session.add(department)
        db.session.commit()
        flash('已添加课程: ' + department.name)
        return redirect(url_for('.add_department'))
    return render_template('administer/add_department.html', form=form)


@administer.route('/department list', methods=['GET', 'POST'])
@login_required
@admin_required
def department_list():
    page = request.args.get('page', 1, type=int)
    pagination = Department.query.order_by(Department.id.desc()).paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False)
    departments = pagination.items
    return render_template('administer/department_list.html', departments=departments, pagination=pagination)


@administer.route('/delete department', methods=['GET','POST'])
@login_required
@admin_required
def delete_department():
    depart_id = request.form.get('depart_id', 0, type=int)
    depart = Department.query.filter_by(id=depart_id).first()
    depart_name = depart.name
    if depart:
        db.session.delete(depart)
        db.session.commit()
        info = '已删除课程： '+depart_name
        flash(info)
        return jsonify({'ok': True})


@administer.route('/change department/<dname>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_department(dname):
    form = ChangeDepartmentForm()
    form.class_table_id.choices = [(d.id, d.name) for d in ClassTable.query.order_by('id')]
    if form.validate_on_submit():
        depart_name = form.name.data
        depart = Department.query.filter_by(name=depart_name).first()
        if depart and not depart.name == dname:
            flash('课程： '+depart.name+' 已存在.')
            return redirect(url_for('administer.change_department', dname=dname))
        Department.query.filter_by(name=dname).update({
            'name': depart_name,
            'class_id': form.class_table_id.data
        })
        db.session.commit()
        flash('课程已更新!')
        return redirect(url_for('.department_list'))
    form.name.data = dname
    return render_template('administer/change_department.html', form=form)


# 设置章节
@administer.route('/chapter', methods=['GET', 'POST'])
@login_required
def chapter():
    form = 0
    pagination = 0
    empty = 1
    set_chapter = request.args.get('set_chapter', 0, type=int)
    chapter_list = request.args.get('chapter_list', 1, type=int)
    chapter_id = request.args.get('chapter_id', 0, type=int)
    if set_chapter:
        if chapter_id:
            form = ChangeChapterForm()
        else:
            form = AddChapterForm()
        form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by('id')]
        empty = 0
        if form.validate_on_submit():
            if chapter_id:    # 修改章节
                ChapterName.query.filter_by(id=chapter_id).update({
                    'name': form.name.data,
                    'department_id': form.department_id.data})
                db.session.commit()
                flash('已修改章节!')
            else:
                chapters = ChapterName(name=form.name.data, department_id=form.department_id.data)    # 添加章节
                db.session.add(chapters)
                db.session.commit()
                flash('已添加章节!')
            return redirect(url_for('administer.chapter', set_chapter=0, chapter_list=1))

    if chapter_list:  # 查看列表
        page = request.args.get('page', 1, type=int)
        try:
            pagination = ChapterName.query.order_by(ChapterName.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
        except: flash('没有设置章节，请添加。')
        empty = 0
    return render_template("administer/chapter.html", form=form, pagination=pagination, empty=int(empty))


@administer.route('/delete chapter', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_chapter():
    chapter_id = int(request.form.get('chapter_id', 0))
    chapter_one = chapter.query.filter_by(id=chapter_id).first()
    chapter_name = chapter_one.name
    if chapter_one:
        db.session.delete(chapter_one)
        db.session.commit()
        flash('已删除章节： '+chapter_name)
        return jsonify({'ok': True})


# 设置 链接
@administer.route('/relation link', methods=['GET', 'POST'])
@login_required
@admin_required
def relation_link():
    set_link = request.args.get('set_link', 0, type=int)
    link_list = request.args.get('link_list', 1, type=int)
    link_id = request.args.get('link_id', 0, type=int)
    delete_link = request.args.get('delete_link', 0, type=int)
    form = 0
    pagination = 0
    empty = 1
    print('link_list ', link_list)
    if set_link:
        if link_id:
            form = ChangeLinkForm()
        else:
            form = AddLinkForm()
        empty = 0
        print('form ', form)
        if form.validate_on_submit():
            if link_id:    # 修改链接
                RelationLink.query.filter_by(id=link_id).update({
                    'link_name': form.name.data,
                    'link_url': form.url.data})
                db.session.commit()
                flash('已修改链接!')
            else:
                links = RelationLink(link_name=form.name.data, link_url=form.url.data)
                db.session.add(links)
                db.session.commit()
                flash('已添加链接!')
            return redirect(url_for('administer.relation_link', set_link=0, link_list=1))

    if link_list:  # 查看列表
        page = request.args.get('page', 1, type=int)
        try:
            pagination = RelationLink.query.order_by(RelationLink.id.desc()).paginate(
                page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
                error_out=False)
        except: flash('没有设置链接，请添加。')
        empty = 0

    if delete_link:
        RelationLink.query.filter_by(id=link_id).delete()
        db.session.commit()
        flash('已修改链接!')

    print('form ', form, ', pagination ', pagination, ', empty ', empty)
    return render_template("administer/relation_link.html", form=form, pagination=pagination, empty=int(empty))
