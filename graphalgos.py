# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:47:10 2017

@author: Oliver
"""
from interactive import contextual, CXT
import networkx as nx
import itertools

def mincut(G):
	for t in range(len(G)):
		pass

@contextual	
def disconnects(G, edges):
	for e in edges:
		G.remove_edge(*e)
	
	answer = not nx.is_connected(G)

	for e in edges:	
		G.add_edge(*e)
	
	return answer

def reduce(G, edges, self_loops=True):
	for u, v in edges:
		new_edges = ((u, w, d) for x, w, d in G.edges(v, data=True)
	                     if self_loops or w != u)
		v_data = G.node[v]
		G.remove_node(v)
		G.add_edges_from(new_edges)
		if 'contraction' in G.node[u]:
			G.node[u]['contraction'][v] = v_data
		else:
			G.node[u]['contraction'] = {v: v_data}

		
def unbridge(G, highest):
	for n in range(1, highest+1):
		while(True):
			for edgeset in itertools.combinations(G.edges(), n):
				if disconnects(G, edgeset):
					reduce(G, edgeset)
					CXT.int = G.copy()
					break
			else:
				break
	return G

@contextual	
def unbridged(G, highest):
	return unbridge(G.copy(), highest)
			
			
def edgekeys(graphs, prin=True):
	geds = [set(tuple(set(g[e[0]][e[1]].keys())) for e in g.edges(keys=True)) for g in graphs]
	if prin: print('\n'.join(map(repr,set( map(tuple, map(sorted, geds) )))))
	return geds
	
def image(G, mapping):
	return nx.MultiGraph(map(mapping, e) for e in G.edges(data=True))