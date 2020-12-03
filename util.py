# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 12:05:40 2017

@author: Oliver
"""

import numpy as np
from itertools import filterfalse, tee

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)
				
def rotMat2D(theta):
	st = np.sin(theta)
	ct = np.cos(theta)
	return np.array([[ct, -st], [st, ct]])
	

def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)