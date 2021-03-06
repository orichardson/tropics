# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:32:09 2017

@author: Oliver
"""


import os

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


def head(iterable):
	return next(iter(iterable))
	
def lmap(fun, iterable):
	return list(map(fun, iterable ))
	
paint = paint_multi

G = head(G5s)

CXT.output_lists(True)
CXT.G = G