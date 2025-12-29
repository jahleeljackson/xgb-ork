import time 


start = time.perf_counter()

x = 0
for i in range(1_000):
    x += 1

stop = time.perf_counter()

dur = stop - start 

print(dur)