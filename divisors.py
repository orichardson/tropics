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
from interactive import contextual
import operator
import networkx as nx
from collections import defaultdict

def fire(div, vs, G):
	""" vs is a map from vertex -> ammount of firing """
	for v, k in vs.items():
		for _, u in G.edges(v):
			div[u] += k
			div[v] -= k

# DO NOT LISTIFY THIS METHOD
def enum_div(G):
	deg = 0
	while(True):
		for d in gen_all(deg, G):
			yield d
		deg += 1

@contextual
def gen_all(degree, G):
	"""
	For a graph G with N nodes, and degree = d, return an n-vector with sum of
	degree $d$. This is of cardinalty N choose d with replacement (but unordered).
	"""
	return map(lambda p: div(*p, G=G), itertools.combinations_with_replacement(G.nodes(), degree))

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
	Creates a G.nodes() - indexed list based on the elements.
	Use Divisor instead for most purposes.
	 """
	if len(elems) == 1 and hasattr(elems[0], '__iter__'):
		elems = elems[0]
	if size is None:
		size = max(elems) +1 if G is None else len(G)
		
	vec = [0]*size
	
	index = G.nodes().index if G is not None else lambda x: x
		

	if type(elems) is dict:
		for (v, count) in elems.items():
			vec[index(v)] += count
	else:
		for v in elems:
			vec[index(v)] += 1
	
	return vec
	
	
def _npa(matrix):
	return np.asarray(matrix).flatten()
	

@contextual
def to_q_reduced(D, G, q=0):
	
	# Step 1
	Q = formal.getQ(G)
	L = formal.getL(Q)
	
	Dr = D - _npa(Q * np.floor(L.dot(D)).T)

	# Step 2
	while True:
		for v in G:
			if (v != q) and (Dr[v] < 0):
				Dr += _npa(Q.dot(vec(v, G=G)))

				break
		else:
			break
		
	# Step 3
	Ai = set(G.nodes()) - {q}
	i = 1
	
	while i <= len(G)-1:
		for v in Ai:
			if Dr[v] < outdeg(Ai,v,G):
				i += 1
				Ai.remove(v)
				break;
		else:
			Dr -= _npa(Q.dot(vec(Ai, G=G)))
			i = 1
			Ai = set(G.nodes()) - {q}
			
	return Dr.each(int)
	
@contextual		
def enum_qred(degree, G, q=0):
	return filter(is_q_reduced.expect_D(G, q), gen_all.original(degree, G))

@contextual
def full_classes(G, degree, q=0, keep_trivial=True):
	""" Returns a dict of equivalence classes for divisors on G, where the keys
	are the reduced divisors, and  the values are the divisors themselves."""
	qred = {} # map from q-reduced tuple to all divisors equivalent	

	if degree is None or degree < 0:
		for deg in range(0, len(G)):
			qred.update(full_classes(G,deg,q,keep_trivial))
		return qred

	divisors = gen_all(degree, G)
	
	for d in divisors:
		red = to_q_reduced(d, G)
		qr = tuple(red)
		
		if not keep_trivial and qr == tuple(d):
			continue
		
		if qr in qred:
			qred[qr].append(d)
		elif keep_trivial:
			qred[qr] = [d]
		else:
			qred[qr] = [red, d]
	
	return qred
	
def cover(divs):
	return sum(divs).each(lambda v: v > 0)
	
def span(divs) :
	return sum(cover(divs))

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
	
def edges(G, *args, **kwargs):
	if isinstance(G, nx.MultiGraph):
		kwargs['keys'] = True
	return list(map(E, G.edges(*args, **kwargs)))

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

	
	
def has_gonality(G, gonality):
	return len(G) is gonality or any(h == len(G) for h in hist(full_classes(G,gonality,keep_trivial=False)))
	
def gonality(G):
	## equal to the max cut???
	## TODO: find efficient way to do this.
	for g in range(1, len(G)):
		if has_gonality(G, g):
			return g

def is_hyperelliptic(G): return not has_gonality(G,1) and has_gonality(G,2)
def is_trigonal(G): return not has_gonality(G,2) and has_gonality(G,3)
	
def spanning_div(G, keep_trivial=False):
	for g in range(len(G)):
		for d in spanning_divs(G, g, keep_trivial):
			return d

def spanning_divs(G, gonality, keep_trivial=False, save_class=False): 
	return (((Divisor(d, G), divs) if save_class else Divisor(d, G)) \
		for d, divs in full_classes(G, gonality, keep_trivial=keep_trivial).items() \
			if span(divs) == len(G) )	

@contextual
def all_hyper(Gs):
	return filter(is_hyperelliptic, Gs)
	
@contextual
def all_trig(Gs):
	return filter(is_trigonal, Gs)


@contextual
def div(*things, G):
	div = Divisor.zeros(G)
	
	if len(things) == 1 and hasattr(things[0], '__iter__'):
		things = things[0]
		
	if isinstance(things, dict):
		return div + things
	
	for v in things:
		div[v] += 1
	return div

@contextual	
def maptotree(G, fold):
	div, klass = next(spanning_divs(G, fold, False, True))
	
	the_map = defaultdict(list)
	the_tree = nx.MultiGraph()
	
	for v in G:
		for i,d in enumerate(klass):
			if klass[v] > 0:
				the_map[v].append(i)
				
	assert all(len(i) ==1 for i in the_map.values())
		
	
	return the_map, the_tree	
	

	
	
	
class Divisor(object):
	def __init__(self, things, G):
		self.G = G
		if isinstance(things, dict):
			self.data = {n:(things[n] if n in things else 0) for n in G.nodes()}
		elif hasattr(things, '__iter__'):
			self.data = {n:val for n,val in zip(G.nodes(),things)}

	@classmethod
	def zeros(cls, G):
		return Divisor({n:0 for n in G.nodes()}, G)
	
	def as_(self, cls):
		return cls(self.data[n] for n in self.G.nodes())
		
	def __getitem__(self, name):
		return self.data[name]
		
	def __setitem__(self, name, val):
		assert name in self.G, "you can only set a divisor at node values (%s not in %s)"%(name, self.G.nodes())
		
		self.data[name] = val
		
	def copy(self):
		return Divisor(self.data.copy(), self.G)
		
	def each(self, fun, send_n=False):
		for n in self.data:
			self.data[n] = fun(self.data[n], n) if send_n else fun(self.data[n])
		return self
		
	def __agg__(self, other, op):
		if isinstance(other, Divisor):
			assert other.G == self.G, "Underlying Graphs need to be the same to combine divisors."

			return self.copy().each(lambda v, n: op(v, other[n]), send_n = True)
			
		elif hasattr(other, '__iter__'):
			return self.__agg__(Divisor(other, self.G), op)
			
		else: #try to add other to items individually
			try:
				return self.copy().each(lambda v: op(v, other))
			except Exception as e:
				print(e)
				raise ValueError('%s (of type %s) cannot be combined with a divisor via %s'%(other, type(other), op))


	def __add__(self, other): return self.__agg__(other, operator.add)
	def __radd__(self, other): return self.__add__(other)
	def __sub__(self, other): return self.__agg__(other, operator.sub)
	def __mul__(self, other): return self.copy().each(lambda v: v * other)
	def __rmul__(self, other): return self.__mul__(other)


	def __iter__(self):
		for n, v in self.data.items():
			yield  v
			
	def __len__(self):
		return len(self.G)

	def __reversed__(self):
		for n, v in reversed(self.data.items()):
			yield  v

#	def __rsub__(self, other): return self.__sub__(other)		
	
	
	def __repr__(self):
		return ' + '.join('%s[v%s]'%(v,n) for n,v in self.data.items())