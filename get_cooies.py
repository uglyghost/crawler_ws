import time
from wenshu import wenshu_class
from database.conn_mongoDB import GetByDate
from database.conn_mongoDB import get_outnet_ip,get_usful_count
import numpy as np
import re
userid = ''
database = GetByDate('61684020884484b96b11ad11',userid)
proxyHost, proxyPort = database.getIPAddress()
ip = get_outnet_ip()
def updatesession_from_db():
    i=0
    usersInf = database.get_all_user()
    for userInf in usersInf:
        wenshu = wenshu_class(ws_username=userInf['username'], ws_password=userInf['password'], ws_proxyHost=proxyHost,
                              ws_proxyPort=proxyPort)
        # 获取登陆后的Cookie
        username = userInf['username']
        json_cookie = wenshu.send_login()
        UM_distinctid = re.findall('UM_distinctid=(.*?);',json_cookie,re.S)[0]
        try:
            SESSION = re.findall('SESSION=(.*?);',json_cookie,re.S)[0]
        except:
            SESSION = 'NAN'
        inuse = 0
        status = 1
        if SESSION == 'NAN':
            status =3
        ssdict = {'UM_distinctid':UM_distinctid,'SESSION':SESSION,'username':username,'inuse':inuse,'status':status,'ip':ip}
        database.insert_session_data(ssdict)
        print('UM_distinctid=',UM_distinctid,'SESSION=',SESSION)
        wenshu.chrome.quit()
        i+=1
        print('当前',i,'共',usersInf.count())
# 爬虫相关功能基本类
def updatesession_one(user_name,password):
    wenshu = wenshu_class(ws_username=user_name, ws_password=password, ws_proxyHost=proxyHost,
                          ws_proxyPort=proxyPort)
    # 获取登陆后的Cookie
    inuse = 1 #1:busy,0: available
    database.update_field('ws_session_list','username',user_name,'inuse',inuse) #inuse置1，正在更新
    json_cookie = wenshu.send_login()
    UM_distinctid = re.findall('UM_distinctid=(.*?);', json_cookie, re.S)[0]
    try:
        SESSION = re.findall('SESSION=(.*?);', json_cookie, re.S)[0]
        status = 1 #1: available ,2:login failed,3:forbidden
    except:
        SESSION = 'NAN'
        print(user_name,'maybe forbidden! please check！')
        status = 3
    inuse = 0
    print("当前IP：",ip)
    ssdict = {'UM_distinctid': UM_distinctid, 'SESSION': SESSION, 'username': user_name, 'inuse': inuse,
              'status': status,'ip':ip}
    database.insert_session_data(ssdict)
    print('UM_distinctid=', UM_distinctid, 'SESSION=', SESSION)
    wenshu.chrome.quit()

def check_and_uppdate(num):
    available = get_usful_count()
    status_errors = database.get_status_bug(2)
    count = status_errors.count()

    status_errors = [error for error in status_errors]


    if num<count:  #如果要求可用数目小于可更新数
        update = num - available
        shuffled_indices = np.random.permutation(update)
        print('共可更新：{}条,可用数：{}条,本次更新：{}条'.format(count,available,update))
        k=1
        for i in shuffled_indices:
            print(status_errors[i]['status'], ' ', status_errors[i]['inuse'], '\n',k, '/', update)
            password = database.get_user_passord(status_errors[i]['username'])
            updatesession_one(status_errors[i]['username'], password)
            k+=1


    else: #超出可更新数，只更新可更新
        j=1
        for error in status_errors:
            print(error['status'],' ',error['inuse'],'\n',j,'/',count)
            password = database.get_user_passord(error['username'])
            updatesession_one(error['username'], password)
            j+=1
while 1:#5s扫描一次
    check_and_uppdate(7) #根据实际需要更新可用用户数,当前维护4个可用session
    time.sleep(5)


# 退出selenium浏览器自动化


