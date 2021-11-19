import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
print(count)
while 1:
    while count:
        run_depth_pct = 'python crawler_by_cookie.py --break-point=6169282cb5b6d832ad606acc --user-id=616cc7aeb5b6d832ad606b45'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()