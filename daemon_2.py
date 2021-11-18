import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
print(count)
while 1:
    while count:
        run_depth_pct = 'python crawler_by_cookie.py --break-point=6167f1d5227d6c6a3647abe6 --user-id=6167ebb1227d6c6a3647abcf'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()