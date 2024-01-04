from datetime import datetime
import time, copy


# Error while getting seconds after a minute and validating condition
# stime = datetime.now()
# ntime = datetime.now()

# while True:
#     ntime = datetime.now()
#     if stime.second < ntime.second:
#         stime = copy.deepcopy(ntime)
#         print(stime.second, "--", ntime.second)
#         print(stime.strftime("%H:%M:%S"), "---", ntime.strftime("%H:%M:%S"))



stime = datetime.now().strftime("%H:%M:%S")
t1 = datetime.strptime(stime, "%H:%M:%S")

ntime = datetime.now().strftime("%H:%M:%S")
t2 = datetime.strptime(ntime, "%H:%M:%S")

print(t1, t2)

while True:
    ntime = datetime.now().strftime("%H:%M:%S")
    t2 = datetime.strptime(ntime, "%H:%M:%S")
    if t2.time() > t1.time():
        t1 = copy.deepcopy(t2)
        print(t2, "--", t1)
        # print(stime.strftime("%H:%M:%S"), "---", ntime.strftime("%H:%M:%S"))


# counter = 1

# while True:
#     ntime = datetime.now().strftime("%H:%M:%S")
#     t2 = datetime.strptime(ntime, "%H:%M:%S")

#     # print(t1.time(), "------", t2.time())
#     if t2.time() > t1.time():
#         #ctime.strftime("%H:%M:%S"):
#         # ctime = datetime.now()
#         # ntime = datetime.now()
#         # counter += 1

#         # t1 = datetime.strftime(ctime, "%H:%M:%S")
#         # t2 = datetime.strftime(ntime, "%H:%M:%S")
#         print(t2.time())
        # print(str(counter) , str(t2 - t1))
