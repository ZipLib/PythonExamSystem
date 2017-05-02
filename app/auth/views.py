import json
from flask import render_template, redirect, request, url_for, flash, current_app, jsonify, session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import Examinee, QuestionMaker, Corrector, Admin, Notice
from .forms import LoginForm,  ChangePasswordForm, NoticeForm, RegistrationForm

'''
def generate_account(length=8):
    import random
    account=''
    chars='1234567890'
    for i in range(length):
        account += random.choice(chars)
    return account
'''


@auth.route('/login', methods=['GET', 'POST'])    # auth.route: 路由修饰器由蓝本｛auth｝提供
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # account_length = len(form.account.data)
        account = form.account.data
        url = 'main.index'
        user = None
        if account[0] == 'E':
            user = Examinee.query.filter_by(account=form.account.data).first()
            url = 'main.examinee'
        elif account[0] == 'C':
            user = Corrector.query.filter_by(account=form.account.data).first()
            url = 'main.corrector'
        elif account[0] == 'Q':
            user = QuestionMaker.query.filter_by(account=form.account.data).first()
            url = 'main.question_maker'
        elif account[0] == 'A':
            user = Admin.query.filter_by(account=form.account.data).first()
            url = 'administer.admin'
        # elif account_length == 3:    # 或者添加一个表字段确认角色
        #     user = Admin.query.filter_by(account=form.account.data).first()
        #     url = 'administer.admin'
        # flash(user.timestamp)    # test
        # flash(str(user))    # test
        # del request.cookies['session']    # immutable type conversion dict ?X
        # print('request cookies , delete wanna.', request.cookies.get('session', 11), len(request.cookies))
        if user is not None and user.verify_password(form.password.data):
            user.login_times += 1
            login_user(user, form.remember_me.data)

            return redirect(request.args.get('next') or url_for(url, user=user))

        flash('无效账号或密码.')

    return render_template('auth/login.html', form=form)


@auth.route('/information', methods=['GET', 'POST'])
@login_required
def information():
    user_id = request.args.get('user_id', 0, type=int)
    user_type = request.args.get('user_type', None, type=str)
    if user_type == 'examinee':
        user = Examinee.query.filter_by(id=user_id).first()
    elif user_type == 'question_maker':
        user = QuestionMaker.query.filter_by(id=user_id).first()
    elif user_type == 'corrector':
        user = Corrector.query.filter_by(id=user_id).first()
    if not user_id:
        user = current_user
    return render_template('auth/user_information.html', user=user)


@auth.route('/information', methods=['GET', 'POST'])
@login_required
def change_information():
    # form = ChangeInformationForm()
    pass


# 通知可以显示在登录后的主页头部  DNF
@auth.route('/notice', methods=['GET', 'POST'])
@login_required
def notice():
    form = 0    # 初始化对象
    pagination = 0
    choice_notice = 0
    empty = 1

    set_notice = request.args.get('set_notice', 0, type=int)    # 获取请求
    notice_list = request.args.get('notice_list', 1, type=int)
    display_notice = request.args.get('display_notice', 0, type=int)
    notice_id = request.args.get('notice_id', 0, type=int)
    search_text = request.form.get('search_text', None, type=str)
    is_admin = request.args.get('is_admins', 0, type=int)

    if int(set_notice):   # 添加通知
        form = NoticeForm()
        if is_admin:
            form.reader.choices = [(key, value) for key, value in {1: '考生', 2: '出题员', 3: '改卷员'}.items()]
        else:
            form.reader.choices = [(key, value) for key, value in {1: '考生'}.items()]
        form.title_color.choices = [(key, value) for key, value in
                                    {0: '空', 'red': '红色', 'orange': '橙色', 'green': '绿色'}.items()]
        form.notice_order.choices = [(key, value) for key, value in
                                     {0: '空', 1: '第一条', 2: '第二条', 3: '第三条'}.items()]
        empty = 0
        if form.validate_on_submit():  # 验证表单，提交入库
            notices = Notice(notice_title=form.notice_title.data,
                             notice_content=form.notice_content.data,
                             title_color=form.title_color.data,
                             reader=form.reader.data,
                             order=form.notice_order.data)
            db.session.add(notices)
            if current_user.__tablename__ == 'admins':    # 添加通知的用户
                notices.admin_id = current_user.id
            if current_user.__tablename__ == 'questionMakers':
                notices.question_maker_id = current_user.id
            if current_user.__tablename__ == 'correctors':
                notices.corrector_id = current_user.id
            db.session.commit()
            return redirect(url_for('auth.notice', set_notice=0, notice_list=1, page=1))
    if int(notice_list):    # 查看列表
        page = request.args.get('page', 1, type=int)
        if current_user.__tablename__ == 'examinees':
            notices = Notice.query.filter_by(order=1 or 2 or 3).filter_by(reader=1)
            print('auth # notice() # examinees notice show is :', notices.first().notice_content)
        if current_user.__tablename__ == 'questionMakers':
            notices = Notice.query.filter_by(question_maker_id=QuestionMaker.id)

        if current_user.__tablename__ == 'correctors':
            notices = Notice.query.filter_by(corrector_id=Corrector.id)

        if current_user.__tablename__ == 'admins':
            notices = Notice.query.order_by(Notice.id.desc())

        if search_text:    # 查询功能
            try:
                search_notices = notices.filter(Notice.notice_title.like('%'+search_text+'%'))
                print('auth # notice() # search notices is : ', search_notices)
                notices = search_notices
            except:
                print('不存在标题有 {} 的通知。'.format(search_text))
                flash('找不到标题有 {} 的通知。'.format(search_text))
        pagination = notices.paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)

        empty = 0
    if int(display_notice):    # 展开通知
        choice_notice = Notice.query.filter_by(id=notice_id).first()
        empty = 0
    return render_template("auth/notice.html", form=form, pagination=pagination, display_notice=display_notice,
                           notice=choice_notice, empty=int(empty))


# 删改通知
@auth.route('/delete notice', methods=['GET', 'POST'])
@login_required
def delete_notice():
    notice_id = request.form.get('notice_id', 0, type=int)
    print('notice id  : ', notice_id)
    # page = request.args.get('page', 1, type=int)
    all_notices = request.args.get('all', False)
    # notice_id = Notice.notice_id
    choice_notice = Notice.query.filter_by(id=notice_id).first()
    db.session.delete(choice_notice)
    try:
        db.session.commit()
    except Exception as e:
        print('数据提交出错 : ', e)
    flash('已删除通知:{}. '.format(notice_id))
    return jsonify({'ok': True})


# 注册 路由 蓝本的路由
# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         current_user.name = form.name.data
#         current_user.password = form.password.data
#         db.session.add(current_user)
#         flash('您的密码已更新.')
#         return redirect(url_for('main.index'))
#     return render_template("auth/register.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session
    flash('您已退出.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    for_information = request.args.get('from_information', 0, type=int)
    form = ChangePasswordForm()
    # form.old_password.data = None
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('您的密码已更新.')
            if for_information:
                return redirect(url_for('auth.information'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('密码错误.')
    return render_template("auth/change_password.html", form=form)




