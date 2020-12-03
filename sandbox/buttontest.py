# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:49:05 2017

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def go():
	freqs = np.arange(2, 20, 3)
	
	fig, ax = plt.subplots()
	plt.subplots_adjust(bottom=0.2)
	t = np.arange(0.0, 1.0, 0.001)
	s = np.sin(2*np.pi*freqs[0]*t)
	l, = plt.plot(t, s, lw=2)
	
	
	
	ind = [1]
	def prev(event):
		print('oiii')
		ind[0] -= 1
		i = ind[0] % len(freqs)
		ydata = np.sin(2*np.pi*freqs[i]*t)
		l.set_ydata(ydata)
		plt.draw()
	
	axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
	axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
	bnext = Button(axnext, 'Next')
	bprev = Button(axprev, 'Previous')
	bprev.on_clicked(prev)
	
	go.buttons = [bnext, bprev]
	
	plt.show()