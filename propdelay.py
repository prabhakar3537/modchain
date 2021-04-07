"""
25kb - 1156
50kb - 800
100kb- 448
1mb  - 60
"""
l1 = []
l2=[]
l3=[]
l4=[]
l=[]
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean

with open('app/time_mod.json', 'r+') as f:
    data = json.load(f)
    l1 = data['time_mod_25_1mb_difficulty0']
    l.append(mean(l1))
    l2 = data['time_mod_25_100kb_difficulty0']
    l.append(mean(l2))
    l3 =data['time_mod_25_50kb_difficulty0']
    l.append(mean(l3))
    l4 = data['time_mod_25_25kb_difficulty0']
    l.append(mean(l4))
x=[1024,100,50,25]
plt.plot(x, l)
plt.xlabel("Size of block (in KB)")
plt.ylabel("Propagation Latency (in seconds)")
plt.show()

