import time
import json
import numpy as np
l = []
x = []
"""
            Old
50 50kb - 839.376846629079
100 50kb - 822.6593285454867
25 50kb - 800.8970046452029
25 1mb- 60.133737432048896
25 100kb - 448.61557234374743
25 25kb - 1156.0159067788516

"""
"""
            New

10 nodes 1 leader - 801
10 nodes 3 leader - 802
10 nodes 6 leader - 772
10 nodes 10 leader- 640

10 nodes 3 leader - 802
50 nodes 18leader - 1380
100nodes 35leader - 1383

25kb - 1156
50kb - 800
100kb- 448
1mb  - 60
"""
with open('app/time_mod.json', 'r+') as f:
    data = json.load(f)
    l = data['time_mod_25_50kb_difficulty0']
for i in range(len(l)):
    x.append(i)

print("Sample time for "+ str(len(l))+ "transactions: ")
print(l)
arr = np.array(l)
print("Average time for a single transaction: ")
print(np.average(arr))
print("Average Transactions per second: ")
print(np.floor(1/np.average(arr)))
print(1/np.average(arr))
import matplotlib.pyplot as plt
plt.plot(x, l)
plt.xlabel("Number of Transactions")
plt.ylabel("Time taken for transaction (in seconds)")
plt.show()
#print(len(l))
