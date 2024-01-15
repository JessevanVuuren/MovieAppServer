import datetime
import time

now = int(time.time())
date = datetime.datetime.fromtimestamp(now)
ban = (date + datetime.timedelta(seconds=10)).timestamp()

print(now)
print(ban)

while (True):
    now = int(time.time())
    time.sleep(1)
    if (now >= ban):
        print("not banned")
    else:
        print("banned")