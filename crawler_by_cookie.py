#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
from time import sleep
import random
from wenshu import wenshu_class_crawler
from database.conn_mongoDB import GetByDate
from database.conn_mongoDB import get_outnet_ip
import argparse

data_num = 0
dett = 0


if __name__ == '__main__':
    print('开始执行主程序')
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--break-point', type=str, default=None)
    parser.add_argument('--user-id', type=str, default=None)
    args = parser.parse_args()

    # 数据库相关基本类
    database = GetByDate(args.break_point, args.user_id)
    check_point = database.load_check_point()

    # 读取账户用户名和密码
    userInf = database.getUserByID()

    # 设置代理
    proxyHost, proxyPort = database.getIPAddress()

    # 爬虫相关功能基本类

    wenshu = wenshu_class_crawler(ws_username=userInf['username'], ws_password=userInf['password'], ws_proxyHost = proxyHost, ws_proxyPort = proxyPort)

    cookie = database.get_random_cookie()  #获取数据只与sesion有关，不检查ip
    database.update_field('ws_session_list', 'username', cookie['username'], 'inuse', 1)
    # json_cookie = "UM_distinctid="+cookie['UM_distinctid']+';'+"SESSION="+cookie['SESSION']+';'
    # json_cookie = "UM_distinctid=" + cookie['UM_distinctid'] + ';'
    json_cookie = "SESSION=" + cookie['SESSION'] + ';'
    wenshu.headers['Cookie'] = json_cookie

    # 获取断点信息
    start_date = check_point["datetime"]
    province = check_point["province"]
    pageNum = int(check_point["pagenum"])
    # date_list = Date.date_range('2021-09-09', '2021-09-09', out_format="%Y-%m-%d")
    # province_list = ['北京市','天津市','上海市','重庆市','河北省','山西省','辽宁省','吉林省','黑龙江省','江苏省',
    #                  '浙江省','安徽省','福建省','江西省','山东省','河南省','湖北省','湖南省','广东省','海南省',
    #                  '四川省','贵州省','云南省','陕西省','甘肃省','青海省','台湾省','内蒙古自治区','广西壮族自治区','西藏自治区',
    #                  '宁夏回族自治区','新疆维吾尔自治区','新疆维吾尔自治区高级人民法院生产建设兵团分院']

    localtime = time.time()
    while 1:
        while province != '0':
            relWenshu = 1

            while (pageNum < 41 and relWenshu != None):

                # 查询条件
                queryCondition = '''[{"key": "cprq", "value": "''' + start_date + ''' TO ''' + start_date + '''"}, 
                                     {"key": "s33", "value": "''' + province + '''"}]'''
                print(queryCondition)

                # 通过加载js生成ciphertext参数
                ciphertext = wenshu.ctx.eval("cipher()")
                # 通过加载js生成__RequestVerificationToken参数
                verification_token = wenshu.ctx.eval("random(24)")
                params = {
                    'pageId': '582f08a63c24765216d45fe020395efc',
                    'cprqStart': start_date,
                    'cprqEnd': start_date,
                    'groupFields': 's50:desc',
                    'ciphertext': ciphertext,
                    'pageNum': str(pageNum),
                    'pageSize': '15',
                    'queryCondition': str(queryCondition),
                    'cfg': 'com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc',
                    '__RequestVerificationToken': verification_token
                }

                print({'pageNum': pageNum})
                # 发送请求获取返回结果
                # response = wenshu.send_post_request(params)

                # 考虑可能请求出现错误的情况
                i = 1
                while True:

                    print('开始发送查询请求，参数为：{}'.format(params))
                    response = wenshu.send_post_request(params)
                    print('查询请求返回结果：{}'.format(response))
                    print(type(response),response.keys())

                    if ('code' in response.keys()):
                        while True:
                                if response['code'] ==9:
                                    print('文档列表请求返回代码为9，文档列表请求失败，休眠5秒后，重复{}次请求'.format(i))
                                    i = i + 1
                                    if i < 4:
                                        sleep(5)
                                        break
                                    print('进入文档列表异常处理,准备切换账号--->')
                                    wenshu.headers['Cookie'] = ""
                                    # 获取登陆后的Cookie
                                    database.update_field('ws_session_list', 'username', cookie['username'], 'inuse', 0)
                                    database.update_field('ws_session_list', 'username', cookie['username'], 'status', 2)

                                    cookie = database.get_random_cookie()
                                    database.update_field('ws_session_list', 'username', cookie['username'], 'inuse', 1)
                                    # json_cookie = "UM_distinctid=" + cookie['UM_distinctid'] + ';' + "SESSION=" + cookie['SESSION'] + ';'
                                    # json_cookie = "UM_distinctid=" + cookie['UM_distinctid'] + ';'
                                    json_cookie = "SESSION=" + cookie['SESSION'] + ';'
                                    wenshu.headers['Cookie'] = json_cookie
                                    # 重新获取数据
                                    print('更换账号后完成--->')
                                    i = 1
                                    break

                    else:
                        print('开始解析返回文档列表')
                        doc_list = response['queryResult']['resultList'][:]
                        print('返回文档列表解析完成')
                        break





                if len(doc_list) < 15:
                    print('列表长度小于15')
                    relWenshu = None

                #print(doc_list)

                for index, value in enumerate(doc_list):
                    print('处理列表中第{}条数据'.format(index))
                    doc_ID = value['rowkey']
                    ciphertext = wenshu.ctx.eval("cipher()")
                    verification_token = wenshu.ctx.eval("random(24)")
                    params = {
                        'docId': doc_ID,
                        'ciphertext': ciphertext,
                        'cfg': 'com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch',
                        '__RequestVerificationToken': verification_token
                    }

                    # response = wenshu.send_post_request(params)

                    # 考虑可能请求出现错误的情况
                    j=1
                    while True:
                        try:
                            print('开始请求单条具体内容---->')
                            response = wenshu.send_post_request(params)
                            print('单条具体内容返回结果---->{}'.format(response))
                        except:
                            print('单条具体内容请求异常,休眠几秒后重新发起请求！')
                            sleep(random.randint(2, 4))
                            continue

                        if 'code' in response.keys():
                            # 可能返回无权限访问
                            while True:
                                print(response.keys())

                                if response['code'] == 9:
                                    print('单条请求返回代码为9，单条请求失败，休眠5秒后，重复{}次请求'.format(j))
                                    j = j + 1
                                    if j < 4:
                                        sleep(5)
                                        break
                                    print('单条内容请求失败，开始更换用户...')
                                    wenshu.headers['Cookie'] = ""
                                    # 获取登陆后的Cookie
                                    database.update_field('ws_session_list', 'username', cookie['username'],
                                                          'inuse', 0)
                                    database.update_field('ws_session_list', 'username', cookie['username'],
                                                          'status', 2)
                                    cookie = database.get_random_cookie()
                                    database.update_field('ws_session_list', 'username', cookie['username'],
                                                          'inuse', 1)
                                    # json_cookie = "UM_distinctid=" + cookie['UM_distinctid'] + ';' + "SESSION=" + cookie['SESSION'] + ';'
                                    # json_cookie = "UM_distinctid=" + cookie['UM_distinctid'] + ';'
                                    json_cookie = "SESSION=" + cookie['SESSION'] + ';'
                                    wenshu.headers['Cookie'] = json_cookie
                                    j=1
                                    # 重新获取数据
                                    break
                        else:
                            print('单条应该成功返回，开始写入数据：')
                            break


                    database.insert_data(response)
                    localtime2 = time.time()

                    dett = localtime2-localtime

                    data_num+=1
                    print('连接时长:{}秒'.format(dett),'获取数据：{}条'.format(data_num))
                    sleep(random.randint(4,6))

                # 切换到下一页
                pageNum = pageNum + 1
                # 保存check point
                database.save_check_point(province, start_date, pageNum)
                sleep(random.randint(2, 4))

            # 切换到下一个城市
            province = database.next_province()
            # 重置到首页
            pageNum = 1
            # 保存check point
            database.save_check_point(province, start_date, pageNum)
            sleep(random.randint(2, 4))

        # 切换到下一天
        start_date = database.next_date()
        # 重置到首页
        pageNum = 1
        # 重置到北京市
        province = '北京市'
        # 保存check point
        database.save_check_point(province, start_date, pageNum)
        sleep(random.randint(2, 4))
