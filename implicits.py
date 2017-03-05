# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 22:50:19 2017

@author: Oliver
"""
import inspect, os

""" 
Usage
W = WS()
G = nx.Graph()
W.register(G = G)

W.load('divisors') # or done by default
	# or W.load(divisors)	

d = [1,2,3,4]
W.register(d = d)

W.div2tree #binds G, and d to method, and calls it


"""
class WS:

	def __init__(self):
		files = [f for f in os.listdir( os.curdir ) if f.endswith('.py')]

		for 	f in files:
			print(f)
			#self.load(f)

		self.VARS = {}
		self.a = Var("a", 3)
			
	
		# <name> ->
		#  value -> <value>
		#  attrs -> [<attrs>]
			
	def __getattr__(self, key):
		# only overridden if not one of our methods
		try:
			return self.VARS[key].get()
		except KeyError as k:
			raise AttributeError from k
			
	def register(self, **kwargs):
		for n, v in kwargs.items():
			self.VARS[n] = Var(n,v)
		
#	def __setattr__(self, k,v):
#		self.VARS[k] = v
	
	def load(self, modulename):
		mod = __import__(modulename)
		
		for n,f in vars(mod).items():
			if callable(f):
				self.__dict__[n] = inspect.signature(f)
				
				
	def reload():
		pass
				
	def back():
		pass
#	inspect.getargspec()
		

class Var(object):
	def __init__(self, name, value=None):
		self.name = name
		self.value = value
		
	def __get__(self, obj, objtype):
		print("using get")
		return self.value
		
	def __set__(self, obj, val):
		print("using set")
		self.value = val
		
	def __iadd__(self, attrs):
		print("adding", attrs)
		
	#def __ipl