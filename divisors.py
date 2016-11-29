# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 15:46:31 2016

@author: Oliver
"""

class Divisor:
	def __init__(self, graph, values):
		self.graph = graph
		self.values = values
		
	def fire(self, vertex_number):
		change = [-1 if v in  else 0 for v in self.graph.]
		val2 = self.values