# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:32:11 2017

@author: Oliver
"""


def parseMono(text):
	for 

class Poly:
	""" has a dict of (basis vector: str, power: int) => coefficient: float""" 
	POWER_SYMB = '^'
	
	def __init__(self, coefs):
		self.coefs = {}
		
		if type(coefs) is str:
			for term in coefs.split("+"):
				term = term.strip()
				
		
		elif type(coefs) is dict:
			for v,n in coefs.items():
				if type(v) is str and POWER_SYMB in v:
					idx = v.find(POWER_SYMB)
					self.coefs[(v[:idx], int(v[idx+1:]))] = coefs[v]

				elif type(v) is tuple and len(v) is 2:
					self.coefs[v] = coefs[v]
				else:
					self.coefs[(v,1)] = coefs[v]
					
		
		# Or it's a list like?
		
					
				
			# assume we've been passed coefficients indexed by strings
			self.coefs = {(v,1):d for v,d in coefs.items()}
			
			
		self.coefs = coefs
		
	def __radd__(self, other):
		return Poly(self.coefs + other.coefs)
		
	def __str__(self):
