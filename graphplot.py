import time
import json
import numpy as np
import matplotlib.pyplot as plt
l1 = []
l2=[]
l3=[]
l4=[]
x1=[]
x2=[]
x3=[]
x4=[]

with open('app/new_time.json', 'r+') as f:
    data = json.load(f)
    l1 = data['leader_size_1_10n']
    l1.sort(reverse=True)
for i in range(len(l1)):
    x1.append(i)
plt.plot(x1, l1,label = "10% Leader group size")

with open('app/new_time.json', 'r+') as f:
    data = json.load(f)
    l2 = data['leader_size_3_10n']
    l2.sort(reverse=True)
for i in range(len(l2)):
    x2.append(i)
plt.plot(x2, l2,label = "35% Leader group size")

with open('app/new_time.json', 'r+') as f:
    data = json.load(f)
    l3 = data['leader_size_6_10n']
    l3.sort(reverse=True)
for i in range(len(l3)):
    x3.append(i)
plt.plot(x3, l3,label = "60% Leader group size")

with open('app/new_time.json', 'r+') as f:
    data = json.load(f)
    l4 = data['leader_size_10_10n']
    l4.sort(reverse=True)
for i in range(len(l4)):
    x4.append(i)
plt.plot(x4, l4,label = "100% Leader group size")
plt.legend()
plt.xlabel("Number of Transactions")
plt.ylabel("Time taken for transaction (in seconds)")
plt.show()