import requests
import execjs
import json
from selenium import webdriver
from time import sleep
from aip import AipOcr

import numpy as np
import torch
from torch.autograd import Variable
from captcha.captcha_cnn_model import CNN
import os
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
from PIL import Image
import captcha.one_hot_encoding as ohe
from settings import ws_setting
import random
import string
from fake_useragent import UserAgent


class wenshu_class:
    def __init__(self, ws_username, ws_password, ws_proxyHost, ws_proxyPort):
        # 配置请求数据包头
        random_str = ''.join(random.choice(string.digits) for _ in range(1))
        random_str = "181217BMTKHNT2W0"
        print(random_str)
        ua = UserAgent(verify_ssl=False)
        print(ua.random)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            #'User-Agent':  ua.random,
            'Host': 'wenshu.court.gov.cn',
            'Origin': 'https://wenshu.court.gov.cn',
            'sec-ch-ua': 'Google Chrome";v="94", "Chromium";v="94", ";Not A Brand";v="99',
            'Referer': 'https://wenshu.court.gov.cn/website/wenshu/' + random_str + '/index.html?',
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
        # 账号
        # self.username = '18728411189'
        self.username = ws_username
        # 密码
        # self.password = 'Cxy8335262!'
        self.password = ws_password
        # 文书接口URL
        self.url = 'https://wenshu.court.gov.cn/website/parse/rest.q4w'
        # 获取二维码URL
        # self.codeURL = 'https://wenshu.court.gov.cn/waf_captcha/'
        # 建立请求回话
        self.request = requests.session()

        # 初始化execjs
        node = execjs.get()
        # 加载需要执行的js文件 rest.q4w接口返回数据被加密 需要解密
        self.ctx = node.compile(open('./js/decrypt_content.js', encoding='utf-8').read())

        proxyMeta = "http://%(host)s:%(port)s" % {
            "host": ws_proxyHost,
            "port": ws_proxyPort,
        }

        self.proxies = {
            "http": proxyMeta,
        }

        proxyType = 'http'  # socks5

        # 代理隧道验证信息
        service_args = [
            "--proxy-type=%s" % proxyType,
            "--proxy-server=%(host)s:%(port)s" % {
                "host": ws_proxyHost,
                "port": ws_proxyPort,
            }
        ]

        p = {
            'proxyType': 'MANUAL',
            'httpProxy': proxyMeta,
            'noProxy': ''
        }

        self.request.proxies = proxyMeta

        # 初始化chrome驱动配置
        chrome_options = webdriver.ChromeOptions()
        # 让浏览器不显示自动化测试
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_experimental_option("detach", False)
        chrome_options.set_capability("proxy", p)
        # 设置window系统下的chrome驱动程序
        self.chrome = webdriver.Chrome(executable_path='./driver/chromedriver.exe', options=chrome_options,
                                       service_args=service_args)

        #p = self.chrome.get('http://icanhazip.com')
        #print(p)
        #sleep(random.randint(10))

        #self.chrome = webdriver.Chrome(options=chrome_options, service_args=service_args)

        # 要访问的目标页面
        # driver = webdriver.PhantomJS(service_args=service_args)

    # 加密内容解密
    def decrypt_response(self, ws_content):
        # 解密数据接口返回的加密内容
        # 解密的key
        secret_key = ws_content['secretKey']
        # 加密的数据内容
        result = ws_content['result']
        # 需要执行的方法名，第一个参数加密内容，第二个参数key
        func_name = 'DES3.decrypt("{0}", "{1}")'.format(result, secret_key)
        # 获取解密后的数据内容
        # 此处在windows下执行有报编码错误问题，需要将源码下的subprocess.py文件里的encoding改成utf-8
        return self.ctx.eval(func_name)

    # 模拟登录获取cookie
    def send_login(self):

        #self.headers['User-Agent'] = self.agentPools[random.randint(0, 3)]
        #print(self.headers['User-Agent'])
        # 模拟登陆获取到登陆的Cookie
        login_url = 'https://wenshu.court.gov.cn/website/wenshu/181010CARHS5BS3C/index.html?open=login'
        response = self.chrome.get(url=login_url)

        # p = self.chrome.get('http://icanhazip.com')
        # print(p)
        # sleep(random.randint(10))

        # 页面加载不完全，尝试刷新解决该问题
        self.chrome.refresh()
        self.chrome.implicitly_wait(10)

        # 最大化浏览器
        # self.chrome.maximize_window()

        # 判断是否发生页面跳转
        while login_url != self.chrome.current_url:
            # 获取二维码图片并保存到 "code.png"
            # save_path = './code/' + str(int(time.time())) + '.png'
            save_path = "./captcha/img/CODE_1634129427.png"

            self.get_pictures_save(save_path)

            # 识别二维码
            code = self.verification_code()

            # 填写验证码
            self.chrome.find_element_by_name('captcha').send_keys(code)
            sleep(random.randint(1, 2))

            # 确认提交验证码
            self.chrome.find_element_by_class_name('code-btn').click()
            sleep(random.randint(1, 2))

        try:
            # 因为登录框在iframe框中，需要先切换到iframe中
            self.chrome.switch_to.frame('contentIframe')
            self.chrome.find_element_by_xpath('//*[@id="root"]/div/form/div[1]/div[1]/div/div/div/input').send_keys(self.username)   # 账号
            self.chrome.find_element_by_xpath('//*[@id="root"]/div/form/div[1]/div[2]/div/div/div/input').send_keys(self.password)   # 密码
            sleep(random.randint(1, 2))

            # 确认登录
            self.chrome.find_element_by_xpath('//*[@id="root"]/div/form/div/div[3]/span').click()                                    # 点击登录
            sleep(random.randint(1, 2))

            # 获取cookies
            cookie_data = self.chrome.get_cookies()                                                                                  # 获取cookie
        except:
            # self.chrome.close()
            pass

        # cookies数据处理返回
        json_cookie = ''
        for cookie in cookie_data:
            name = cookie['name']
            value = cookie['value']
            # if (name == 'UM_distinctid' or name == 'SESSION'):
            json_cookie += name + '=' + value + '; '

        print(json_cookie)
        return json_cookie

    # 发送post请求
    def send_post_request(self, ws_params):
        # print(self.proxies)
        # print("11")
        # p = self.request.get('http://httpbin.org/ip', headers=self.headers, proxies=self.proxies)
        # print(p.text)
        # sleep(random.randint(10))
        # 尝试请求获取数据
        try:
            response = self.request.post(url=self.url, headers=self.headers, proxies=self.proxies, data=ws_params).json()       # 请求可能会出错，多次请求可以获取需要内容
            #response = self.request.post(url=self.url, headers=self.headers, data=ws_params).json()
            # response['success'] = True
        except:
            # 请求返回的数据格式报错，尝试检查
            response = {'code': 9, 'success': False}

        # 检查是否存在报错
        if response['success'] == False:
            return response
        else:
            # 解码后，正常返回数据
            real_data = self.decrypt_response(response)
            jsonData = json.loads(real_data)
            return jsonData

    # 发送get请求
    def send_get_request(self, ws_params):
        response = self.request.get(url=self.url, headers=self.headers, data=ws_params).json()
        jsonData = json.loads(response)
        return jsonData

    # 截取图片验证码
    def get_pictures_save(self, file):

        self.chrome.maximize_window()

        # 全屏截图
        self.chrome.save_screenshot('./tmp/screenshot.png')
        page_snap_obj = Image.open('./tmp/screenshot.png')

        # 验证码元素位置
        img = self.chrome.find_element_by_id('Image1')
        location = img.location

        # 获取验证码的大小参数
        size = img.size
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        # 按照验证码的长宽，切割验证码
        image_obj = page_snap_obj.crop((left, top, right, bottom))

        #im = Image.open(file)
        out = image_obj.resize((180, 100), Image.ANTIALIAS)
        out.save(file, 'PNG')
        # 查看切割后的图片
        # image_obj.show()

        # 通过Image保存处理的图像
        #image_obj.save(file)

        return out

    # 验证码识别函数
    def verification_code(self):

        i = open('./captcha/img/CODE_1634129427.png', 'rb')

        vcode = self.get_code_by_CNN(i.read())

        return vcode

    def get_code_by_CNN(self, file):
        cnn = CNN()
        cnn.eval()
        cnn.load_state_dict(torch.load('./captcha/model.pkl'))

        dataset = mydataset(ws_setting.PREDICT_DATASET_PATH, transform=transform)
        predict_dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

        for i, (images, labels) in enumerate(predict_dataloader):
            image = images
            vimage = Variable(image)
            predict_label = cnn(vimage)

            c0 = ws_setting.ALL_CHAR_SET[
                    np.argmax(predict_label[0, 0:ws_setting.ALL_CHAR_SET_LEN].data.numpy())]
            c1 = ws_setting.ALL_CHAR_SET[np.argmax(predict_label[0,
                    ws_setting.ALL_CHAR_SET_LEN:2 * ws_setting.ALL_CHAR_SET_LEN].data.numpy())]
            c2 = ws_setting.ALL_CHAR_SET[np.argmax(predict_label[0,
                    2 * ws_setting.ALL_CHAR_SET_LEN:3 * ws_setting.ALL_CHAR_SET_LEN].data.numpy())]
            c3 = ws_setting.ALL_CHAR_SET[np.argmax(predict_label[0,
                    3 * ws_setting.ALL_CHAR_SET_LEN:4 * ws_setting.ALL_CHAR_SET_LEN].data.numpy())]

            output = '%s%s%s%s' % (c0, c1, c2, c3)

        #print(output)

        return output

    # 通过百度OCR接口获取验证码（未使用）
    def get_code_by_baidu(self, file, option=None):

        # clinet登录所需数据
        # 需要注册百度智能云获取
        APP_ID = '18559740'
        API_KEY = 'Fw34XUgEhDTS20Ljakmrna5B'
        SECRECT_KEY = 'nopvfqjq4ESXSxSUQeN5EXlLfXITGuFU'
        client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)

        # 参数配置
        options = {}
        options["language_type"] = "CHN_ENG"
        # 是否检测图像朝向
        options["detect_direction"] = "true"
        options["detect_language"] = "true"
        # 是否返回识别结果中每一行的置信度
        options["probability"] = "true"

        # 通过本地图片识别二维码
        if type(file) == str:
            # print('图片链接')
            message = client.basicGeneralUrl(file, option)
        # 通过网络链接识别二维码
        else:
            # print('二进制图片')
            message = client.basicAccurate(file, option)

        #print(message)
        try:
            code_text = message['words_result'][0]['words']
        except:
            code_text = 1234
        print('识别结果为：', code_text)
        return code_text

transform = transforms.Compose([
    # transforms.ColorJitter(),
    transforms.Grayscale(),
    transforms.ToTensor(),
    # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class mydataset(Dataset):

    def __init__(self, folder, transform=None):
        self.train_image_file_paths = [os.path.join(folder, image_file) for image_file in os.listdir(folder)]
        self.transform = transform

    def __len__(self):
        return len(self.train_image_file_paths)

    def __getitem__(self, idx):
        image_root = self.train_image_file_paths[idx]
        image_name = image_root.split(os.path.sep)[-1]
        image = Image.open(image_root)
        if self.transform is not None:
            image = self.transform(image)
        label = ohe.encode(image_name.split('_')[0]) # 为了方便，在生成图片的时候，图片文件的命名格式 "4个数字或者数字_时间戳.PNG", 4个字母或者即是图片的验证码的值，字母大写,同时对该值做 one-hot 处理
        return image, label