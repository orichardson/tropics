# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 15:46:31 2016

@author: Oliver
"""

def fire(div, vs, G):
    for v in vs:
        for u in G[v]:
            div[u] += 1
            div[v] -= 1

def gen_all(degree):
	pass

def is_q_reduced(D, q, G):
	""" Dahr's Burning Algorithm """
	if any( d < 0 for d in D if d != q ):
		return False
		
	Ai = set(G.nodes())
	vi = q
	
	def outdeg(A, v):
		return sum(u not in A for u in G[v])
	
	for i in range(1,len(G)):
		Ai.remove(vi)
		
		for v in Ai:
			if D[v] < outdeg(Ai,v):
				vi = v
				break;
		else:
			return False
		
	return True

class Divisor:
	def __init__(self, graph, values):
		self.graph = graph
		self.values = values
		
	def fire(self, vertices):
		fire(self.values, vertices, self.graph)