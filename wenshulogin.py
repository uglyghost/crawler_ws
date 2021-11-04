import requests,pickle
import http.cookiejar as cookielib
session = requests.session()
post_url = 'https://gw.datayes.com/usermaster/authenticate/web.json'
postdata = {
    'username':'Bg2mFAwT9/3K5DUj0CRw5c9ffcg4OYe6ONE+DvSDcaCzZYwlsfZECId9S8omLiP4FmEeXzqoGZYDF1jG94QpOalD+hIas4rsghANy2AcrWBy8/bqie428SQesvv0n0eH/zC7msySzFg2l6lImDGzEJX4v13Zeqm/212sGCFBbxo=',
    'password':'s4HCeCrq5lqwlyS8OLMBDaKwpifP8GUlMg+PMS5pxuYPv4gHjESK15CZqrZ/vQNlq5UjAIa5LQL4sJnUV9WJ25iWaEplY8/+B9MGy1NiAhO7oLsCAf+uvfXOSvKbOkUy1V7A4k2RZwBN95NCe8Tp6LaTFOcWSNYqCEDgtwROgZQ=',
    'rememberMe':'false',
    'app':'robo_pc'
}
# post_url = 'https://wenshu.court.gov.cn/website/wenshu/181010CARHS5BS3C/index.html?open=login'
# postdata = {
#     'username':'15213395979',
#     'password':'EF%2B4mx0nZuj3CmJHuj0g4Qq9GYI8fQMHiCA4knFw7oDMRKJZ36dvejoiThlIN1JUAJfn%2F5uSY7Bb%2BL3gXT9KDvWGefb12q47IThDgXxDOIir9XAis2Hy2nAkhh5uTBAH5uNXUr9uRrbPlGFM8zx9JTXNcowEVl4PwMuB2ZjdxEKeCelafqt%2FtTNIwhVnDMnl9qLC%2BfzAXZ8eIFPpUHk%2BS2Z%2Fp5bxCi7pi8PZqII2AfhIb4MQd7JwDK8JrDXZgbhT4d%2BFULdkJz26Au0F7Rkdp5nYezGlH8wT9T4lCkpl5Kyts%2FVp37q7tR3sbYITeBX4a3c5w8ugaleG8M%2BWgB6Vyg%3D%3D',
#     'appDomain':'wenshu.court.gov.cn'
# }
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            #'User-Agent':  ua.random,
            'Host': 'gw.datayes.com',
            'Origin': 'https://robo.datayes.com',
            'sec-ch-ua': 'Google Chrome";v="94", "Chromium";v="94", ";Not A Brand";v="99',

            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '',
            'sec-ch-ua-platform': 'Windows',
            'Content-Length': '848',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'same-origin',
        }
login_page = session.post(post_url,data=postdata,headers=headers)  #登录网页
#
# try:
#     with open('somefile', 'wb') as f:
#         pickle.dump(session.cookies, f)
# except:
#     print("Cookie未能加载")
# print(login_page.status_code)
# with open('somefile', 'rb') as f:
#     session.cookies.update(pickle.load(f))
# f = open('somefile','rb')
# print(f.read())

r = session.get('https://app.datayes.com/cloud-portal/#/myaccount/personalInfo?RelayState=https:%2F%2Frobo.datayes.com%2Fv2%2Fthirdparty%2Forder') #查看个人中心
print('rcoder',r.status_code,r.content.decode())