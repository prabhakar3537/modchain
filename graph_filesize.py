"""
25kb - 1156
50kb - 800
100kb- 448
1mb  - 60
"""
import time
import json
import numpy as np
import matplotlib.pyplot as plt

l = [1156,800,448,60]
x = [25,50,100,1024]
plt.plot(x, l,label = "Performance measure on changing average sub-block size")
plt.xlabel("Size of sub-block (in kilobytes)")
plt.ylabel("Transactions per Second (TPS")
plt.show()

