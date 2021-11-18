import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
print(count)
while 1:
    while count:

        run_depth_pct = 'python crawler_by_cookie.py --break-point=61684020884484b96b11add1 --user-id=616bb9c9b5b6d832ad606b2f'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()
