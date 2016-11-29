# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 07:39:47 2016

@author: Oliver
"""
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from networkx import isomorphism

import random


def tickdown(array, indices):
	ar2 = array.copy()
	ar2[indices] -= 1
	return ar2

def gen_all(genus):
	# Genus g: 2g-2 vertices, and 3g-3 edges.
	all_graphs = []
	done_partials = []
	g0 = nx.MultiGraph()
	
	Nv = 2*genus-2	
		

	def subgen(todo, g) :
		edges_g = g.edges()

		if max(0,*todo) == 0:
			#if any(np.array_equal(edges_g, h.edges()) for h in all_graphs):
			#	return
			for h in all_graphs:
				if isomorphism.could_be_isomorphic(h,g):
					return

			print(len(all_graphs))
			#print(edges_g)
			all_graphs.append(g)
		else:
			if any([np.array_equal(edges_g, h.edges()) for h in done_partials]):
				return
				
			#print('******************* BASE: ******************', g.edges())
			u = todo.argmax()
			for x in np.nonzero(todo)[0]:
				if x != u: # *** No self loops condition lives here
					g2 = g.copy()
					g2.add_edge(u,x)				
					subgen(tickdown(todo, [u,x]), g2)
				
			done_partials.append(g)
	
	subgen(np.array([3]*Nv), g0)
		
	
	return all_graphs
	
def uniq(Gs):
	S = {}
	for g in Gs:
		for s in S.keys():
			if isomorphism.is_isomorphic(g,s):
				S[s] += 1
				break
		else:
			S[g] = 1
	
	return S
	
	
def gen_rand(genus):
	g = nx.MultiGraph()
	
	Nv = 2*genus-2
	Ne = 3*genus-3


	todo = np.array([3]*Nv)
	okay = {1}
	
	for i in range(Ne):
		u = todo.argmax()
		idx = [ x for x in np.nonzero(todo)[0] if (x != u and x in okay)] # *** No self loops condition lives here
		uv = [u,random.choice(idx)]
		
		okay.update(uv)
		# np.add.at(todo, uv, -1)
		todo = tickdown(todo, uv)
		g.add_edge(*uv)
		
	return g
	
def mcSample(genus, size) :
	return uniq([gen_rand(genus) for i in range(size)])