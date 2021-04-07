import time
import json
import numpy as np
import matplotlib.pyplot as plt

l1=[]
l2=[]
x1=[]
x2=[]
with open('app/time_mod.json', 'r+') as f:
    data = json.load(f)
    l1 = data['time_mod_50_50kb_difficulty0']
    l1.sort(reverse=True)
for i in range(len(l1)):
    x1.append(i)    

with open('app/new_time.json', 'r+') as f:
    data = json.load(f)
    l2 = data['leader_size_35_100n']
l2.sort(reverse=True)
for i in range(len(l1)):
    x2.append(i) 
    
plt.plot(x1, l1,label = "Old Modchain implementation")
plt.plot(x2, l2,label = "New Modchain implementation")

plt.legend()
plt.xlabel("Number of Transactions (No.)")
plt.ylabel("Time taken for transaction (in seconds)")
plt.show()


    