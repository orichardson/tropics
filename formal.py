# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 15:30:54 2017

@author: Oliver
"""

import divisors
import numpy as np
import networkx as nx

def delv(f, v, G) :
	return sum( len(G[v][w])*(f[v]-f[w]) for w in G[v])
def lap(f, G) : 
	return [ delv(f,v,G) for v in G.nodes() ]
	
def getQ(G):
	""" THe above two methods are summarized with this one; 
	returns diag(the degrees of G) - adjacency(G) """
	return np.diag(divisors.vec(nx.degree(G)))-nx.adjacency_matrix(G).todense()


def getL(Q):
	N = len(Q)
	JN = np.ones((N,N))/N
	
	Qp = (Q + JN).I - JN
	return Qp


def getE(Q):
	""" Energy pairing, given the laplacian matrix"""
	def E(d1, d2):
		return float(np.matrix(d1).dot(getL(Q)).dot(d2))
	return E
	
	
def getEq(Q, q):
	""" UNFINISHED. General energy pairing, for non-zero degree divisors. Strategy:
	put all of the excess degree in q and use the other energy parining"""
	
	def Eq(d1,d2):
		return float(np.matrix(d1).dot(getL(Q)).dot(d2))
	return Eq
	
""" Principal divisors are in the image of Q (or lap, equivalently) """