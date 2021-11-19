import os
import time
import datetime
from database.conn_mongoDB import get_usful_count
from crawler_by_cookie import data_num,dett
count = get_usful_count()
print('可用session数：',count)
now_time = datetime.datetime.now()
dead_count =0
total_data  = 0
total_time = 0
while 1:
    while count:
        run_depth_pct = 'python crawler_by_cookie.py --break-point=61684020884484b96b11add2 --user-id=6168218d884484b96b111db8'
        os.system(run_depth_pct)
        count = get_usful_count()
    dead_count+=1
    total_data += data_num
    total_time += dett
    print('\n运行总时长{}秒，获取数据共{}条。\n'.format(total_time,total_data))
    print('第{}次挂掉，5分重后重新运行。当前时间为:{}'.format(dead_count,datetime.datetime.now()))

    time.sleep(300)
    count = get_usful_count()