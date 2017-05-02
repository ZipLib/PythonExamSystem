# -*- coding: utf-8 -*-
# from openpyxl import load_workbook
from xlrd import open_workbook, xldate_as_tuple
from app.models import Examinee
from app import db
from xlrd.xldate import xldate_as_datetime
import datetime


def input_users():
    write_byte = open_workbook('用户表.xlsx')
    try:
        sheet_inf = write_byte.sheet_by_name('用户信息')
        print('reading Sheet1...')
    except:
        print(' \'Sheet1\' changed its name.')
        return None 
    
    rows = sheet_inf.nrows
    cols = sheet_inf.ncols
    print('rows {rows},cols {cols}.'.format(rows=rows, cols=cols))
    cell_values = sheet_inf.cell_value(1, 1)
    print('cell\'s values : {0}.'.format(cell_values))
    data_list = []
    for i in range(2, rows):
        row_data = sheet_inf.row_values(i)
        data_list.append(row_data)

    # print('data of list : {}'.format(data_list))

    for key in data_list:
        if key[6] == '男':
            key[6] = int(1)
        elif key[6] == '女':
            key[6] = int(2)
        d = xldate_as_datetime(key[7], 0)
        print('dddd :{}, type {}:'.format(d,type(d)))
        print('d.year :{}, type:{}'.format(d.year, type(d.year)))
        d2 = datetime.datetime.strftime(d, '%Y:%m:%d')

        print('+++++{} , type :{}'.format(d2, type(d2)))
        '''try:
            user = Examinee(studycard=str(int(key[1])),
                            password=str(int(key[2])),
                            name=key[4],
                            gender=key[6],
                            birthday='1999-9-1')  # xldate_as_datetime(key[7], 0)
            print('1 ok.')
        except:
            print('user wrong.')

        try:
            db.session.add(user)
        except:
            print('session add wrong.')
        try:
            db.session.commit()
            print('2 ok.')
        except:

            print('session commit wrong.')
            # db.session.rollback()'''
    '''userData = {}
    print('Reading rows...')
    obj = '教师'
    for row in range(4, sheet.max_row):
        name = sheet['B' + str(row)].value
        sex = sheet['C' + str(row)].value
        age = sheet['D' + str(row)].value

        #make sure the key for this name exists.
        userData.setdefault(obj, {})
        userData[obj].setdefault(name, {})
        userData[obj][name].setdefault(sex, {})
        userData[obj][name][sex].setdefault(age, 0)

    print('sheet.max_row is ...', sheet.max_row)
    print('Teachers\' userData is ...', userData)'''

if __name__ == '__main__' :
    input_users()