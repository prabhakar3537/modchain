import time
import json
import numpy as np
l = []
x = []
with open('app/globals.json', 'r+') as f:
    data = json.load(f)
    l = data['time_mod']
for i in range(len(l)):
    x.append(i)
print("Sample time for 50 transactions: ")
print(l)
import matplotlib.pyplot as plt
plt.plot(x, l)
plt.xlabel("X-axis")
plt.ylabel("Time taken for transaction (in seconds)")
plt.show()
arr = np.array(l)
print("Average time for a single transaction: ")
print(np.average(arr))
print("Average Transactions per second: ")
print(np.floor(1/np.average(arr)))
#print(len(l))
