
import datetime
from time import sleep
import random

def datetime_test():
    # print(type(datetime.datetime.now()))
    now_is = datetime.datetime.now()
    now_date = datetime.datetime.now().date()
    now_time = datetime.datetime.now().time()
    print('datetime.datetime.now() timestamp：', now_is.timestamp())
    print('datetime.datetime.now()date() : ', now_date)
    print('datetime.datetime.now().time() : ', now_time)

    return now_is, now_date


def varibles_parameter(one, two, *, three, four):
    print('*, arg1, arg2.！！ one:  {} two:  {},  three:  {},  four:  {}'
          .format(one, two, three, four))


def varibles_parameter2(one, two, three=3, four=4, *args):
    print('*args... ... .！！  {} {} {} {}, more args by : {} {} {} .more is:{}'
          .format(one, three, two,  four, args[0], args[1], args[2], args))


def keywords_parameter(one, two, **more):
    print('**keyword... .！！ one:  {} two:  {},  more keywords:  {}'
          .format(one, two, more))


class ClassName():
    one = 'a'
    two = 'b'

    def add_three(self):
        pass


def append_demo():
    i = 5
    qt = ['question']
    qt = 'question' + str(i)
    print('strs append is str : ', isinstance(qt, str))
    print(int(False))


def random_demo():
    list1 = [1, 2, 3, 4, 5, 6]
    l1 = random.sample(list1, 1)
    l3 = random.sample(list1, 3)
    c1 = random.choice(list1)
    return l1, l3, c1

if __name__ == '__main__':
    print('***  ***  ***')
    # varibles_parameter(2, 4, three=5, four=6)
    # varibles_parameter2(1, 2, 3, 4, '紧急', '出动', 758)
    # keywords_parameter(3, 4, six=6, seven=7)
    # what_name = ClassName()
    # print('what\'s the name: ', ClassName)
    # append_demo()
    # if int(False):
    #     print('GG')
    #
    # a = datetime_test()
    # print(a, '....', a[0].timestamp() + 10)
    # print('xxxxxxxxxxxxxx')
    # time_now = '2017-03-29 20:10:51'
    # str_time = datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
    # print('time and timestamp type   ', str_time, type(str_time), type(str_time.timestamp()))
    # sleep(2)
    # b = datetime_test()
    # print('b - a now() is : ', b[0].timestamp()-a[0].timestamp())

    # print('a class and instance ', ClassName, ClassName())
    # print(' random demo ', random_demo()[0], random_demo()[2])
    # print(' random demo ', random_demo()[0], random_demo()[2])

    # d1 = datetime.datetime.fromtimestamp(1493560020)
    # str1 = d1.strftime("%Y-%m-%d %H:%M:%S")
    # t1 = 1493560000 + 60 * 60
    # d2 = datetime.datetime.fromtimestamp(t1)
    # str2 = d2.strftime("%Y-%m-%d %H:%M:%S.%f")
    # print(' exam_paper.start_time   now date : ', str1, type(str1), '--', str2)
    #

    timeStamp = 1493572000
    dateArray = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    print('time : ', otherStyleTime, type(otherStyleTime))
    #
    # import time
    # times = datetime.datetime.strptime(str1, "%Y-%m-%d %H:%M:%S")
    # times2 = time.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    # print(' === ', times, type(times))
    #
    # # list1 = [0, 0]
    # x = [x for x in list1 if x != 0]
    # print('x ', x, type(x))
    # if x:
    #     print('not empty.')

    # list1 = ['a', 'b']
    # list2 = ['a', 'b']
    # if list1 == list2:
    #     print('aaaa')
    # a = "".join(list1)
    # print(' list to str ', a, type(a))

    # a = 1234
    # b = str(a)
    #
    # print(' str ', b.__int__())