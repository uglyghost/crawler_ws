from wenshu import wenshu_class
from database.conn_mongoDB import GetByDate
import re
userid = ''
database = GetByDate('61684020884484b96b11ad11',userid)
proxyHost, proxyPort = database.getIPAddress()
usersInf = database.get_all_user()
i=0
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
    ssdict = {'UM_distinctid':UM_distinctid,'SESSION':SESSION,'username':username,'inuse':inuse,'status':status}
    database.insert_session_data(ssdict)
    print('UM_distinctid=',UM_distinctid,'SESSION=',SESSION)
    wenshu.chrome.quit()
    i+=1
    print('当前',i,'共',usersInf.count())
# 爬虫相关功能基本类

# 退出selenium浏览器自动化


