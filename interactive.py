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
from types import GeneratorType

class Context(object):
	GENS_TYPES = (zip, range, map, filter, GeneratorType)
	
	def __init__(self):
		self._vars = {}
		self._post = {}
		
	def __getattr__(self, name):
		return self.__getitem__(name)		
			
	def __setattr__(self, name, value):
		if name[0] is '_':
			self.__dict__[name] = value
		else:
			self.__setitem__(name, value)
			
	def __delitem__(self, key):
		del self._vars[key]
	
	def __getitem__(self, key):
		if key not in self._vars:
			return None

		hist = self._vars[key]
		if len(hist) == 0 : 
			return None
		
		return hist[-1]
		
	def __setitem__(self, key, val):
		if key not in self._vars:
			self._vars[key] = [val]
		else:
			self._vars[key].append(val)
		
	def __contains__(self, key):
		return key in self._vars
				
	def __str__(self):
		return self._vars.__str__()
		
	def __repr__(self):
		return 'Context: '+self._vars.__repr__()
		
	def _repr_html_(self):
		return "<table>" +  \
			''.join('<tr><td>{0}</td> <td>{1}</td> <td>{2}</td></tr>'.format(n,len(vals), vals[-1]) for n,vals in self._vars.items()) + \
			"</table>"

	def __dir__(self):
		return super(object,self).__dir__() + list(self._vars.keys())
		
	def hist(self, name):
		return self._vars[name]
		
	def output_lists(self, should_output_lists):
		self._post['listify'] = should_output_lists
		
	def transform(self, obj):
		""" after calling a method, there might be a mapping. Sometimes we want to
		automatically turn mappings and zips and stuff into lists"""
		if self._post.get('listify', False) and isinstance(obj, Context.GENS_TYPES):
			return list(obj)
			
		return obj
		
	################ helpful methods that use properties of contexts ################

	
#	def revert(self, name, index):
		

	
#if type(locals().get('CXT', None)).__name__ is not Context.__name__:
#if __name__ is not '__main__':
global CXT
CXT = Context()

def _score(position, param):
	return log(len(param.name)) \
		- position \
		+ 5*param.name[0].isupper() # - 10*(param.default is Parameter.empty)

def sub(D, keys):
	for k in keys:
		if k in D:
			del D[k]

def nodefault(param):
	return param.default is Parameter.empty
	
def _append_doc(fun, text):
	if fun.__doc__ is None:
		fun.__doc__ = text
	else:
		fun.__doc__ += '\n'+text
		
def makepart(function, param):
	sig = signature(function)
	
	if type(param) is str:
		param = sig.parameters[param]
	
	@wraps(function)
	def fun(*args, **kwargs):
		@wraps(function)
		def f(value):
			kwargs[param.name] = value
			return function(*args, **kwargs)
			
		
		_append_doc(f, 'Preselected Arguments: %s -- %s'%(str(args), str(kwargs)))
		_append_doc(f, 'Awaiting Final Parameter %s'% param.name)
		f.__signature__ = sig.replace(parameters = [param])
		return f
		
	_append_doc(fun, '[<%s> will be filled later, and cannot be supplied]' % param.name)
	
	newparams = sig.parameters.copy()
	del newparams[param.name]
	fun.__signature__ = sig.replace(parameters = newparams.values())
	return contextual(fun)

def contextual(func):
	params = signature(func).parameters

	groups = defaultdict(list)
	
	for n,par in params.items():
		groups[par.kind].append(par)
	
	# first fill all of the positional-only parameters; 
	num_ponly = len(groups[Parameter.POSITIONAL_ONLY])
	kwgroups = groups[Parameter.POSITIONAL_OR_KEYWORD] + groups[Parameter.KEYWORD_ONLY]
	has_varpos = len(groups[Parameter.VAR_POSITIONAL]) > 0 
	has_varkey = len(groups[Parameter.VAR_KEYWORD]) > 0
	
	@wraps(func) # just want to keep doc 'n stuff the same.
	def wrapper(*args, **kwargs):
		global CXT
		# First priority: kwargs, second:args; third: context
		# BUT: args are last in name priority
		# so after applying kwargs and 
		
		debug = kwargs.get('debug', False)		

		if debug:
			del kwargs['debug']
			print('#'*80)
			print("Wrapper around ", func, 'explicitly passed', args,kwargs)
			print('  with signature: ', signature(func))
			print('   and context', CXT)
	

		newargs, args = list(args[:num_ponly]), list(args[num_ponly:])
		# The next step is to deal with kwargs passed recently
		
		# then filter the new kewargs not to have any extra values
		newkwargs = {k:v for k,v in kwargs.items() if( has_varkey or params[k] in kwgroups) }
		kwcands = [c for c in kwgroups if c.name not in newkwargs]

		if debug:
			for k,v in newkwargs.items():
				print('\tusing passed kwarg %s = '%k, v)

		# Then add kwargs from context leaving room for *args passed recently
		candidates = sorted((_score(i, r), r.name) for i,r in enumerate(kwcands))
		if debug > 1: print("CONTEXT SCORES: {", ', '.join('%s:%0.2f'%(k,v) for v,k in reversed(candidates)),'}')
		
		
		# 
		# Then, deal with keyword-or-positional args
		while((len(kwcands) > len(args) or has_varpos)  and len(candidates) > 0):
				# there are more unsatisfied parameters that need values
				# than unused positional values, so take one from context
			sco, arg = candidates.pop()
			if debug > 1: print('Popped: ', arg,sco)
			if arg in CXT:
				# I there is a default argument, we don't want to overwrite it until
				# we have to. Ex: func(a, b, c=3), where a is in context. Then f(1,2) should
				# assign to a and b, but not c, even though we could have taken a from context
				# and assigned to b and c.
				if nodefault(params[arg]) and sum(map(nodefault, kwcands)) <= len(args):
					if not has_varpos:
						continue
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

		if debug > 1: print('Successfully assigned arguments')

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
			
		if debug: print('  FINAL INVOCATION: ', newargs, newkwargs)	
		
		return CXT.transform(func(*newargs, **newkwargs))
		
	wrapper.original = func
	_append_doc(wrapper, """This method will autofill parameters from <interactive.CXT>; 
		to see what inferences have been made, run with the parameter debug=True, or debug=<num>. 
		To access the original, call <%s.original>"""%func.__name__)
	
	for p in kwgroups:
		setattr(wrapper, "expect_%s"%p.name, makepart(wrapper, p))

	return wrapper
