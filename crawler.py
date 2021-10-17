#!/usr/bin/env python
# -*- coding:utf-8 -*-

from time import sleep
import random
from wenshu import wenshu_class
from database.conn_mongoDB import GetByDate
import argparse

if __name__ == '__main__':

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
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }

    # 爬虫相关功能基本类
    wenshu = wenshu_class(ws_username=userInf['username'], ws_password=userInf['password'], ws_proxyMeta = proxyMeta)
    # 获取登陆后的Cookie
    json_cookie = wenshu.send_login()
    # 退出selenium浏览器自动化
    wenshu.chrome.quit()
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
                while True:
                    try:
                        response = wenshu.send_post_request(params)
                    except:
                        sleep(random.randint(2, 4))
                        continue
                    else:
                        # 可能返回无权限访问
                        while True:
                            try:
                                doc_list = response['queryResult']['resultList'][:]
                            except:
                                # 获取登陆后的Cookie
                                json_cookie = wenshu.send_login()
                                # 退出selenium浏览器自动化
                                wenshu.chrome.quit()
                                wenshu.headers['Cookie'] = json_cookie
                                # 重新获取数据
                                response = wenshu.send_post_request(params)
                            else:
                                # 跳出无权访问循环
                                break
                        # 跳出访问出错循环
                        break

                if len(doc_list) < 15:
                    relWenshu = None

                for index, value in enumerate(doc_list):

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
                    while True:
                        try:
                            response = wenshu.send_post_request(params)
                        except:
                            sleep(random.randint(2, 4))
                            continue
                        else:
                            # 可能返回无权限访问
                            while True:
                                try:
                                    if response['code'] == 9:
                                        # 获取登陆后的Cookie
                                        json_cookie = wenshu.send_login()
                                        # 退出selenium浏览器自动化
                                        wenshu.chrome.quit()
                                        wenshu.headers['Cookie'] = json_cookie
                                        # 重新获取数据
                                        response = wenshu.send_post_request(params)
                                    else:
                                        # 跳出无权访问循环
                                        break
                                except:
                                    break
                            # 跳出访问出错循环
                            break

                    database.insert_data(response)
                    sleep(random.randint(3, 5))

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
