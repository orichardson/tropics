# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 09:03:23 2017

@author: Oliver
"""

from graphics import *
from generator import *
from divisors import *
from formal import *
from graphalgos import *
from gio import *

from interactive import CXT

G6s = read('./data/genus6.txt')
G5s = read('./data/genus5.txt')
G4s = read('./data/genus4.txt')

CXT.q = 'A'


fire_example = nx.MultiGraph('AB AC AD DB DC CE BE'.split())
divisor_view( fire_example, div('AAAAA', G=fire_example))
plt.show()


CXT.q = 0
T = nx.balanced_tree(2,3)
paint_multi(T)
plt.show()


#CXT.


#H1 = 