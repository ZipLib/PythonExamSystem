# -*- coding: utf-8 -*-
#  from django_shortcuts import render_to_response,render
# from pyExcelerator import *
import xlrd
from xlrd import xldate_as_tuple # , xldate_from_date_tuple
from xlrd.xldate import xldate_as_datetime
import time
import datetime
from flask import Flask, request, redirect, url_for, flash
# from werkzeug import secure_filename
import os
from xlrd import open_workbook

def index(req):
    fname=u'用户表.xlsx'
    bk=xlrd.open_workbook(fname)
    shxrange=range(bk.nsheets)
    try:
        sh=bk.sheet_by_name("用户信息")
    except:
        print('no sheet in {} named 用户信息'.format(fname))
        return None
    nrows =sh.nrows
    ncols=sh.ncols
    print('nrows {:d}, ncols {:d}'.format(nrows,ncols))
    cell_value=sh.cell_value(1,1)
    print(cell_value)
    row_list=[]
    for i in range(1,nrows):
        row_data=sh.row_values(i)
        row_list.append(row_data)
    print('show -----: ', row_list)


def timetest1():
    dateC = datetime.datetime(1999, 9, 1)
    timestamp = time.mktime(dateC.timetuple())
    print('time 1 ', timestamp/1000/60)

def timetest2(times):
    ltime = time.localtime(times)
    timeStr = time.strftime("%Y-%m-%d", ltime)
    print('time 2 ', timeStr)

def timetest3():
    a = '1999-9-1'
    timeArray = time.strptime(a, "%Y-%m-%d")
    timeStamp = int(time.mktime(timeArray))
    print('time 3 ', timeStamp/3600)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp'

@app.route('/loaded', methods=['GET'])
def uploaded_file():
    return 'filename'
@app.route('/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['files']
        if file:
            filename = file.filename

            # flash('filename is -- {}'.format(filename))
            paths = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f = file.save(paths)
            wb = open_workbook(paths)
            sheets = wb.sheet_by_name('用户信息')
            rows = sheets.nrows
            cols = sheets.ncols
            return 'rows :{}'.format(rows)
    return '''
    <!DOCTYPE html>
    <title>Upload New File</title>
    <h1>Upload File</h1>
    <form action="/" method="POST" enctype="multipart/form-data">
    <input type="file" name="files" />
    <input type="submit" value="Upload" />
    </form>
    '''
if __name__ ==  '__main__':

    # timetest1()
    # timetest2(260032.0*3600)
    # d = xldate_as_tuple(36000, 0)
    # print('d --', d)
    # d2 = xldate_as_datetime(36000, 0)
    # d2 = datetime.datetime.strftime(d2, '%Y-%m-%d')
    # print('d2 ++', d2)
    # app.run(debug=True)

    # import time
    # d = datetime.date('1999-1-1')
    # print('date :', d)

    # dict = {1: '限时', 2: '自由'}
    # for d, k in dict.items():
    #     print('d -- ', d, k)
    # print(dict.keys())
    for i, j in enumerate(('a', 'b', 'c')):
        print(i, j)