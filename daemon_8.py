import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
while 1:
    while count:
        print('进程8，当前count为：',count)
        run_depth_pct = 'python crawler_by_cookie.py --break-point=61684020884484b96b11add2 --user-id=6168218d884484b96b111db8'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()