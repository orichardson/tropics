# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:32:09 2017

@author: Oliver
"""


from graphics import *
from generator import *
from divisors import *
from formal import *
from gio import *

from interactive import CXT

G5s = read('./data/genus5.txt')
G = next(iter(G5s))