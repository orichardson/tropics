# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 15:46:31 2016

There are three formats for a divisor:

 - Multiset format: {v0, v1, v2, v2}
 - Vector format: [1, 0, 2, 0, 0]
 - Polynomial format: 1 + 2 x^2

@author: Oliver
"""
import itertools
import formal
import numpy as np

from functools import wraps, partial
from inspect import signature

class Context(dict):		
	def __getattr__(self, name):
		return self.get(name, None)	
			
	def __setattr__(self, name, value):
		self[name] = value
	
#if type(locals().get('CXT', None)).__name__ is not Context.__name__:
if __name__ is not '__main__':
	CXT = Context()

def contextual(func):
	@wraps(func) # just want to keep doc 'n stuff the same.
	def wrapper(*args, **kwargs):
		p = list(signature(func).parameters.keys())[len(args):]
		if '?!?' in args or kwargs.get('debug', False):
			print('Function: ', func)
			print('\tparams: ', p)
			print('\tgiven: ', args, kwargs)
			print('\textra:', {n:CXT[n] for n in p.keys() if n in CXT})
		return partial(func, *args,**kwargs)(**{n:CXT[n] for n in p if n in CXT})

	return wrapper
	
@contextual
def gen_all(d, G):
	"""
	For a graph G with N nodes, and degree = d, return an n-vector with sum of
	degree $d$. This is of cardinalty N choose d with replacement (but unordered).
	"""
	return map(vecN(len(G)), itertools.combinations_with_replacement(range(len(G)), d))

@contextual
def outdeg(A, v, G):
	return sum(len(G[v][u]) for u in G[v]  if u not in A)

@contextual
def is_q_reduced(D, G, q=0):
	""" Dahr's Burning Algorithm. D is assumed to be in vector format. """
	if any( d < 0 for d in D if d != q ):
		return False
		
	Ai = set(G.nodes())
	vi = q
	
	for i in range(1,len(G)):
		Ai.remove(vi)
		
		for v in Ai:
			if D[v] < outdeg(Ai,v,G):
				vi = v
				break;
		else:
			return False
		
	return True
	

@contextual
def vec(*elems, size=None, G=None):
	""" items can be an iterable or a dict.
	The parameter 'G' should only be used through contextualization, and
	it replaces 'size' with 'len(G)'.
	 """
	if len(elems) == 1 and hasattr(elems[0], '__iter__'):
		elems = elems[0]
	if size is None:
		size = max(elems) +1 if G is None else len(G)
		
	vec = [0]*size

	if type(elems) is dict:
		for (v, count) in elems.items():
			vec[v] += count
	else:
		for v in elems:
			vec[v] += 1
	
	return vec
	
def vecN(size):
	def v(*elems):
		return vec(*elems, size=size)
	return v
	
def _npa(matrix):
	return np.asarray(matrix).flatten()
	

@contextual
def to_q_reduced(D, G, q=0):
	# Step 1
	Q = formal.getQ(G)
	L = formal.getL(Q)
	N = len(G)
	tov = vecN(N)
	
	Dr = np.array(D) - _npa(Q * np.floor(L.dot(D)).T)

	# Step 2
	while True:
		for v in G:
			if (v != q) and (Dr[v] < 0):
				Dr += _npa(Q.dot(tov(v)))

				break
		else:
			break
		
	# Step 3
	Ai = set(G.nodes()) - {q}
	i = 1
	
	while i <= N-1:
		for v in Ai:
			if Dr[v] < outdeg(Ai,v,G):
				i += 1
				Ai.remove(v)
				break;
		else:
			Dr -= _npa(Q.dot(tov(Ai)))
			i = 1
			Ai = set(G.nodes()) - {q}
	
	return list(map(int, Dr))
	
@contextual		
def enum_qred(degree, G, q=0):
	return filter(is_q_reduced(G,q), gen_all(degree))

@contextual
def full_classes(G, degree, q=0, keep_trivial=True):
	""" Returns a dict of equivalence classes for divisors on G, where the keys
	are the reduced divisors, and  the values are the divisors themselves."""
	divisors = gen_all(degree, G)
	qred = {} # map from q-reduced tuple to all divisors equivalent
	
	for d in divisors:
		qr = tuple(to_q_reduced(d, G))
		
		if not keep_trivial and qr == tuple(d):
			continue
		
		if qr in qred:
			qred[qr].append(d)
		elif keep_trivial:
			qred[qr] = [d]
		else:
			qred[qr] = [list(qr), d]
	
	return qred
	
def span(divs) :
	return sum(x > 0 for x in np.array(divs).sum(axis=0))

def hist(classes, fun=span):
	hist = {}
	for qred, divs in classes.items():
		l = fun(divs)
		hist[l] = hist.get(l,0) + 1
		
	return hist
	
def ghistN(N, fun=span):
	def make_histogram(G):
		return hist(full_classes(G,N), span)
	return make_histogram


#### Deprecated: just returns the genus!
def qdeg(G):
	last = None	
	for deg in reversed(range(len(G))):
		n = sum(1 for d in enum_qred(G, deg))
		if last is None:
			last = n
		elif last != n:
			return deg + 1
	
def E(edat):
	a, b = edat[:2]
	return ((a,b) if a < b else (b,a)) + edat[2:]
	
@contextual					
def edges(G, *args, **kwargs):
	return list(map(E, G.edges(*args, keys=True,**kwargs)))

@contextual					
def div2tree(G, D, q=0):
	NX = set(G) - {q} # unburnt vertices
	NR = set(edges(G)) # unburt edges
	T = set() # marked edges
	
	while len(NX) > 0:
		f = min(e for e in NR if (e[0] in NX) ^ (e[1] in NX))
		v = f[0] if f[0] in NX else f[1]
		
		if D[v] == sum(1 for e in edges(G,v) if e not in NR):
			NX.remove(v)
			T.add(f)
		
		NR.remove(f)
	return T

@contextual					
def tree2div(T, G, q=0):
	NX = set(G) - {q} # unburnt vertices
	NR = set(edges(G)) # unburt edges
	D = [0]*len(G) # divisor
	
	while len(NX) > 0:
		f = min(e for e in NR if (e[0] in NX) ^ (e[1] in NX))

		if f in T:
			v = f[0] if f[0] in NX else f[1]
			D[v] = sum(1 for e in edges(G,v) if e not in NR)
			NX.remove(v)
			T.add(f)
		
		NR.remove(f)	
	
	return D