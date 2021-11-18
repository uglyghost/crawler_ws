import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
print(count)
while 1:
    while count:
        run_depth_pct = 'python crawler_by_cookie.py --break-point=61692923b5b6d832ad606ad6 --user-id=616cc7d0b5b6d832ad606b46'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()