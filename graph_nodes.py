"""
10 nodes 3 leader - 802
50 nodes 18leader - 1380
100nodes 35leader - 1383
"""

import time
import json
import numpy as np
import matplotlib.pyplot as plt

l = [802, 1380, 1383]
x = [10,50,100]

plt.plot(x, l,label = "Performance measure on changing size of blockchain")
plt.xlabel("Number of nodes in blockchain (No.)")
plt.ylabel("Transactions Per Second (TPS)")
plt.show()