import os
import time
from database.conn_mongoDB import get_usful_count
count = get_usful_count()
print(count)
while 1:
    while count:
        run_depth_pct = 'python crawler.py --break-point=61684020884484b96b11ad10 --user-id=6168218d444484b96b11adb8'
        os.system(run_depth_pct)
        count = get_usful_count()
    time.sleep(300)
    count = get_usful_count()