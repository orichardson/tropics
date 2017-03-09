# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 21:44:14 2017

@author: Oliver
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 21:40:05 2017

@author: Oliver
"""


from functools import wraps
from inspect import signature, Parameter
from math import log
from collections import defaultdict

class Context(dict):	
	def __init__(self):
		self.vars = defaultdict(list)
		
	def __getattr__(self, name):
		return self.__getitem__(name)		
			
	def __setattr__(self, name, value):
		self.vars[name].append(value)
		
	def __delitem__(self, key):
		del self.vars[key]
	
	def __getitem__(self, key):
		if key not in self.vars:
			return None

		hist = self.vars[key]
		if len(hist == 0) : 
			return None
		
		return hist[-1]
	
	def __setitem__(self, key, val):
		self.vars[key] = val
		
	def hist(self, name):
		return self.vars[name]
	
	def revert(self, name, index)

	
#if type(locals().get('CXT', None)).__name__ is not Context.__name__:
#if __name__ is not '__main__':
global CXT
CXT = Context()

def _score(position, param):
	return log(len(param.name)) - position

def sub(D, keys):
	for k in keys:
		if k in D:
			del D[k]

def contextual(func):
	@wraps(func) # just want to keep doc 'n stuff the same.
	def wrapper(*args, **kwargs):
		global CXT
		# First priority: kwargs, second:args; third: context
		# BUT: args are last in name priority
		# so after applying kwargs and 
		debug = kwargs.get('debug', False)
		params = signature(func).parameters		

		if debug:
			del kwargs['debug']
			print("Wrapper around ", func, 'explicitly passed', args,kwargs)
			print('  with signature: ', signature(func))
			print('   and context', CXT)
	

		groups = defaultdict(list)
		
		for n,par in params.items():
			groups[par.kind].append(par)
		
		# first fill all of the positional-only parameters; 
		num_ponly = len(groups[Parameter.POSITIONAL_ONLY])
		newargs, args = list(args[:num_ponly]), list(args[num_ponly:])
		# The next step is to deal with kwargs passed recently
		kwcands = groups[Parameter.POSITIONAL_OR_KEYWORD] + groups[Parameter.KEYWORD_ONLY]

		newkwargs = {k:v for k,v in kwargs.items() if params[k] in kwcands }
		sub(kwcands, newkwargs)

		if debug:
			for k,v in newkwargs.items():
				print('\tusing passed kwarg %s = '%k, v)

		# Then add kwargs from context leaving room for *args passed recently
		candidates = sorted((_score(i, r), r.name) for i,r in enumerate(kwcands))
		if debug > 1: print("CONTEXT SCORES: {", ', '.join('%s:%0.2f'%(k,v) for v,k in reversed(candidates)),'}')
		
		has_varpos = len(groups[Parameter.VAR_POSITIONAL]) > 0 
		
		while((len(kwcands) > len(args) or has_varpos)  and len(candidates) > 0):
				# there are more unsatisfied parameters that need values
				# than unused positional values, so take one from context
			sco, arg = candidates.pop()
			if arg in CXT:
				newkwargs[arg] = CXT[arg]
				kwcands.remove(params[arg])
				if debug: print('\tusing context variable', arg)
				
		for k, v in zip(tuple(kwcands), tuple(args)):
			if k.kind is Parameter.KEYWORD_ONLY:
				continue
			newkwargs[k.name] = v
			kwcands.remove(k)
			args.remove(v) # will remove the first value (that matches), as desired.
			if debug: print('\tassigning passed value ',v,' to var ', k, 'of kind ', k.kind)

		if has_varpos and len(args) > 0:
			# Need to reconstruct the earlier arguments to be positional
			for p in groups[Parameter.POSITIONAL_OR_KEYWORD]:
				n = p.name
				if n in newkwargs:
					newargs.append(newkwargs[n])
					del newkwargs[n]
			newargs += args
		if len(groups[Parameter.VAR_KEYWORD]) > 0:
			newkwargs = dict(kwargs, **newkwargs) #There should be no duplicates now.
			
		if debug: print('  FINAL INVOKATION: ', newargs, newkwargs)	
		
		return func(*newargs, **newkwargs)

	return wrapper
