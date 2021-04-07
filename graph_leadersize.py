"""
10 nodes 1 leader - 801
10 nodes 3 leader - 802
10 nodes 6 leader - 772
10 nodes 10 leader- 640
"""

import time
import json
import numpy as np
import matplotlib.pyplot as plt

l = [801, 802, 772, 640]
x = [1, 3, 6, 10]

plt.plot(x, l,label = "Comparison of ratio of leader group size")
plt.xlabel("Leader group size (No.)")
plt.ylabel("Transactions Per Second (TPS)")
plt.show()