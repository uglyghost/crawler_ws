import time
from wenshu import wenshu_class
from database.conn_mongoDB import GetByDate
from database.conn_mongoDB import get_outnet_ip
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

    ssdict = {'UM_distinctid': UM_distinctid, 'SESSION': SESSION, 'username': user_name, 'inuse': inuse,
              'status': status,'ip':ip}
    database.insert_session_data(ssdict)
    print('UM_distinctid=', UM_distinctid, 'SESSION=', SESSION)
    wenshu.chrome.quit()

def check_and_uppdate():
    status_errors = database.get_status_bug(2)
    count = status_errors.count()
    print('共需更新：',count,'条')
    i=1
    for error in status_errors:
        print(error['status'],' ',error['inuse'],'\n',i,'/',count)
        password = database.get_user_passord(error['username'])
        updatesession_one(error['username'], password)
        i+=1
while 1:#5s扫描一次
    check_and_uppdate()
    time.sleep(5)


# 退出selenium浏览器自动化


