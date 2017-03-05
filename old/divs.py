# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 17:06:31 2017

@author: Oliver
"""

def fire(div, vs, G):
	"""
	div is in vector format, vs is an iterable of vertices. This is the silly,
	non-matrix version of it. To do this properly, do
		div += Q.dot(f)
	"""
	for v, m in vs.items():
		for u in G[v]:
			div[u] += m * len(G[u][v])
			div[v] -= m * len(G[u][v])