import os
import time

while 1:
    count = 4
    t1 = time.time()
    while count:
        run_depth_pct = 'python get_cooies.py'
        os.system(run_depth_pct)
        count-=1
    t2 = time.time()
    det = t2-t1
    if det <120:
        print('2分钟内连续4此请求失败，休眠3分钟')
        time.sleep(180)
