# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 14:19:19 2017

@author: Oliver
"""

import numpy as np
from numpy.random import rand
import matplotlib.pyplot as plt


x, y, c, s = rand(4, 100)

def onpick3(event):
	ind = event.ind
	print('onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind))

fig, ax = plt.subplots()
col = ax.scatter(x, y, 100*s, c, picker=True)
#fig.savefig('pscoll.eps')
fig.canvas.mpl_connect('pick_event', onpick3)
