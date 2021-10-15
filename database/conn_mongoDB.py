from pymongo import MongoClient
from database.ws_datetime import Date
import datetime
from bson import ObjectId
from pandas import json_normalize

import sys
sys.path.append("..")

client = MongoClient('localhost', 27017)
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

        query = {'_id': ObjectId(self.user_id)}
        tmp = mongodb['ws_user'].find_one(query)
        result = {
            'username': tmp['username'],
            'password': tmp['password']
        }
        return result