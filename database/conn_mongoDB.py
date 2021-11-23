from pymongo import MongoClient
from database.ws_datetime import Date
import datetime
from bson import ObjectId
from pandas.io.json import json_normalize
import numpy as np
import sys
sys.path.append("..")
import settings.ws_setting as ws_settings
import random

# 导入需要的模块，若没有需要去pip在线下载“pymongo”s
from urllib.request import urlopen
from pymongo import MongoClient

user = 'wenshu'
pwd = '123456'
host = '10.220.139.140'
port = '27017'
db_name = 'wenshu'

uri = "mongodb://%s:%s@%s" % (user, pwd, host + ":" + port + "/" + db_name)

# 连接数据库

client = MongoClient(uri)

# client = MongoClient('localhost', 27017)
mongodb = client.wenshu

class GetByDate:
    def __init__(self, ws_break_point, ws_user_id):
        self.break_point = ws_break_point
        self.user_id = ws_user_id

        query = {'_id': ObjectId(self.break_point)}
        tmp = mongodb['ws_tmp'].find_one(query)
        self.datetime = tmp['datetime']
        self.province = tmp['province']
        self.pagenum = tmp['pagenum']

    def next_date(self):

        start = Date.str_to_date(self.datetime)
        next = start + datetime.timedelta(days=1)

        return next.strftime('%Y-%m-%d')

    def next_province(self):
        start = self.province

        query = {"province": start}
        start_province = mongodb['ws_province'].find_one(query)

        if start_province['province'] != '0':
            query = {"id": start_province['id'] + 1}
            next_province = mongodb['ws_province'].find_one(query)
        else:
            query = {"id": 0}
            next_province = mongodb['ws_province'].find_one(query)
            self.datetime = self.next_date()

        next = next_province['province']

        return next

    def next_page(self):

        start = self.pagenum
        next = start + 1

        return next

    def save_check_point(self, province, datetime, pagenum):

        query = {'_id': ObjectId(self.break_point)}
        tmp = mongodb['ws_tmp'].find_one(query)
        tmp['province'] = province
        tmp['datetime'] = datetime
        tmp['pagenum'] = pagenum
        self.datetime = tmp['datetime']
        self.province = tmp['province']
        self.pagenum = tmp['pagenum']
        result = mongodb['ws_tmp'].update_one(query, {'$set': tmp})

        return result

    def load_check_point(self):

        query = {'_id': ObjectId(self.break_point)}
        tmp = mongodb['ws_tmp'].find_one(query)
        self.datetime = tmp['datetime']
        self.province = tmp['province']
        self.pagenum = tmp["pagenum"]

        return tmp

    def insert_data(self, new_data):

        tmp_df = json_normalize(new_data)
        print(tmp_df)
        query = {"s5": tmp_df['s5'][0]}

        # 重复检查，看是否存在数据
        count = mongodb['ws_list'].count_documents(query)
        tmp_dict = tmp_df.to_dict('records')
        # print(tmp_dict)

        if count == 0:
            # 不存在，添加
            result = mongodb['ws_list'].insert_one(tmp_dict[0])
        else:
            # 已存在，更新
            result = mongodb['ws_list'].update_one(query, {'$set': tmp_dict[0]})

        return result

    def getUserByID(self):

        # query = {'_id': ObjectId(self.user_id)}
        # tmp = mongodb['ws_user'].find_one(query)
        tmp = list(mongodb['ws_user'].aggregate([{"$sample": {"size": 1}}]))
        print(tmp[0])
        for i in tmp:
            print(i)
        result = {
            'username': tmp[0]['username'],
            'password': tmp[0]['password']
        }
        return result

    def getIPAddress(self):

        query = {'_id': ObjectId(ws_settings.PROXY_LIST)}
        tmp = mongodb['ws_ip_list'].find_one(query)
        tmp_proxy = tmp['data'][random.randint(0, len(tmp['data']))]

        IP = tmp_proxy['ip']
        Port = tmp_proxy['port']

        print('IP: '+ str(IP) + ' ' + "Port: " + str(Port))

        return IP, Port

    def get_all_user(self):
        tmp = mongodb['ws_user'].find()
        return  tmp

    def insert_session_data(self, ssdict):


        query = {"username": ssdict['username']}

        # 重复检查，看是否存在数据
        count = mongodb['ws_session_list'].count_documents(query)
        # print(tmp_dict)

        if count == 0:
            # 不存在，添加
            result = mongodb['ws_session_list'].insert(ssdict)
        else:
            # 已存在，更新
            result = mongodb['ws_session_list'].update_one(query, {'$set': ssdict})

        return result
    def get_status_bug(self,errcode):#错误码 （1: available ,2:login failed,3:forbidden)
        tmp = mongodb['ws_session_list'].find({'status':errcode})
        return tmp

    def get_user_passord(self,user_name):
        uesr = mongodb['ws_user'].find({'username': user_name}).distinct('password')
        return uesr

    def update_field(self,  collection,query_key,query_value,field_key,set_v):
        mongodb[collection].update({query_key:query_value},{'$set':{field_key:set_v}})

    def get_random_cookie(self,ip):

        tmp = mongodb['ws_session_list'].find({"inuse":0,"status":1,"ip":ip})
        count = mongodb['ws_session_list'].find({"inuse":0,"status":1,"ip":ip}).count()
        print('当前共有',count,'个账号可用')
        num = np.random.choice(count,1)[0]
        print('num=',num)
        i=0;
        for cookie in tmp:
            if(i==num):
                print('选择账号：',cookie['username'],cookie['ip'])

                return cookie
            else:
                i+=1


def get_outnet_ip():
    my_ip = urlopen('http://ip.42.pl/raw').read().decode("ascii")
    print('外网ip:', my_ip)
    return my_ip

ip = get_outnet_ip()
def get_usful_count():
    count = mongodb['ws_session_list'].find({"inuse": 0, "status": 1,"ip":ip}).count()
    return count