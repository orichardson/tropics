# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:05:53 2016

@author: Oliver
"""
from matplotlib import pyplot as plt
from matplotlib.colors import cnames, colorConverter, rgb2hex 
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.widgets import RadioButtons, Button

from threading import Thread, Lock
from collections import defaultdict

import networkx as nx
import numpy as np
import time
import math, random
import itertools

import divisors
from interactive import CXT
import util

_STYLE = [(2,'solid'), (4,'dashed'), (8,'dotted')]
_BENDS = [0,1,-1,0.5,-0.5]

def perp ( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def paintG(G,ax=None, offset=None, **kwargs):	
	G2 = nx.Graph(G)
	edges = G2.edges()
	
	pos = nx. nx.layout.fruchterman_reingold_layout(G2) # spring_layout also good
	#pos = nx. nx.layout.spring_layout(G)
	if offset is None:
		offset = np.array([0,0])
	
	for k in pos.keys():
		pos[k] += offset
	
	weights, styles = zip(*[_STYLE[len(G[u][v])-1] for u,v in edges])	
	nx.draw(G2, pos=pos, edges=edges, width=weights, ax=ax, style=styles, **kwargs)
	
	
	if ax is None:
		plt.show()

def bend(pu, pv, i, num):	
	factor =  (-1 + (i+1)*2.0/float(num+1)) / math.sqrt(num)
	prc = (0.45+random.random()/10)
	return pu*prc + pv*(1-prc) + perp(pv-pu) * factor
	
def reposition(pos, G, layout='fruchterman_reingold_layout', **layoutargs):
	shorthand = dict(fruch='fruchterman_reingold_layout', 
						spring='spring_layout', 
						spec='spectral_layout', 
						shell='shell_layout')
	
	if layout in shorthand:
		layout = shorthand[layout]
	
	newp = getattr(nx.layout, layout)(G,**layoutargs)
	for v in pos:
		pos[v] = newp[v]
		
def add_reposition_buttons(fig, pos, G, repaint_callback):
	def make_onclick(**kwargs):
		def onclick(evt):
			reposition(pos, G, **kwargs)
			repaint_callback()
		return onclick
		
	buttons = []
	
	layouts = [ 'spring', 'spectral', 'shell', 'random']
	scales = [ 1, 1, 0.5, 0.9]
			
	for i,(lname,s) in enumerate(zip(layouts,scales)):
		butax = fig.add_axes([1-0.11*(i+1), 0.95, 0.1, 0.05], alpha = 0.2)
		button = Button(butax, lname)
		button.on_clicked(make_onclick(layout=lname+'_layout', scale=s, center=(0.5,0.5)))
		buttons.append(button)
		
	return buttons
		

def multiedge_path(G, pos, E = None):
	if E is None:
		E = divisors.edges(G)
	counts = {(u,v):max(1,len(G[u][v])) for u,v,*_ in E}
	hist = {}
	
	verts = []
	codes = []
	
	center = np.average(list(pos.values()), axis=0)

	for u,v, *_ in E:
		bend_idx = hist.get((u,v), 0)
		hist[(u,v)] = bend_idx +1
		
		pu = np.array(pos[u])
		pv = np.array(pos[v])
		
		if u == v:
			rot = util.rotMat2D(0.6  + random.random()/10)
			roti = util.rotMat2D(-0.6  - random.random()/10)

			scale = np.sqrt(bend_idx+2)/ 5
			vec = pu - center
			norm = np.linalg.norm(vec)
			if norm > 0:
				vec *= scale / norm
			else:
				vec = np.array([0,1]) * scale
						
			verts += [pu, pu + (vec.dot(rot)).flatten(), pu + (vec.dot(roti)).flatten(), pu]
			codes += [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
		else:
			verts += [pu, bend(pu,pv, bend_idx, counts[u,v]), pv]
			codes += [Path.MOVETO, Path.CURVE3, Path.CURVE3]

	return Path(verts, codes)
	
def fig_setup(G, ax=None, offset=None):
	pos = nx. nx.layout.fruchterman_reingold_layout(G) # spring_layout also good
	#pos = nx. nx.layout.spring_layout(G)
	
	if offset is None:
		offset = np.array([0,0])
	
	for k in pos.keys():
		pos[k] += offset

	cf = plt.gcf() if ax is None else ax.get_figure()
	if ax is None:
		if cf._axstack() is None:
			ax = cf.add_axes((0, 0, 1, 1))
		else:
			ax = cf.gca()
	
	ax.set_axis_off()
	cf.set_facecolor('w')
	return pos, ax, cf
	
def annotate(ax, pos, sizes = None, annotations = None):
	if annotations is None:
		annotations = {}
		
	if sizes is not None:
		inv = ax.transData.inverted()
		zero = inv.transform_point((0,0))
	
	for (v, xy) in pos.items():
		if sizes is None:
			dx,dy = np.array([0,0]), np.array([0,0])
		else:
			dx = (inv.transform_point((math.sqrt(sizes[v])+5, 0)) - zero) / 2
			dy = (inv.transform_point((0, math.sqrt(sizes[v])+5)) - zero) / 2

		if v in annotations:
			x,y = xy + dx + dy
			annotations[v].set_x(x)
			annotations[v].set_y(y)
		else:
			annotations[v] = ax.annotate("$v_{%s}$"%str(v), xy + dx + dy , ha="center", va="center")

	return annotations
	
		
def paint_multi(G, ax=None, offset=None, **kwargs):
	pos,ax,cf = fig_setup(G, ax, offset)	
	edgepatch = [ax.add_patch(patches.PathPatch(multiedge_path(G,pos), ec='gray', fc='none', lw=2))]
	nodepatch = nx.draw_networkx_nodes(G,pos,ax=ax,**kwargs)
	annots = annotate(ax, pos)
	
	def repaint():
		nodepatch.set_offsets(np.array([pos[v] for v in G]))
		edgepatch[0].remove()
		edgepatch[0] = ax.add_patch(patches.PathPatch(multiedge_path(G,pos), ec='gray', fc='none', lw=2))
		annotate(ax, pos, annotations=annots)
		plt.draw()
		
	
	if offset is None:
		paint_multi.baggage = add_reposition_buttons(cf, pos, G, repaint)
	


def divisor_view(G, div=None, index='', **kwargs):
	N = G.nodes()

	edgepatches = []
	loaded = []
	allclasses = {} # divisors.full_classes(G, -1, keep_trivial=False)
	
	if div is None:
		div = divisors.spanning_div(G, keep_trivial=True)
		if div is None:
			div = divisors.Divisor.zeros(G)
	if not 'c' in kwargs:
		kwargs['c'] = 'b'

	localdiv = div # or div.copy() # if we don't want modification
	print(localdiv)
		
	def labeldata(d):
		labels = {x:(str(d[x]) if d[x] != 0 else '') for x in N}
		nodesizedict = {x: 800*np.abs(d[x]) + 200 for x in N}
		return labels, nodesizedict
		
	def update():
		is_qred = divisors.is_q_reduced(localdiv, G)
		qred_div = divisors.to_q_reduced(localdiv, G)
				
		labs, nodsizdic = labeldata(localdiv)

		annotate(ax, pos, nodsizdic, annotations)
		for v, l in labs.items():
			labelpatch[v].set_position(pos[v])
			labelpatch[v].set_text(l)
		
		tupform = qred_div.as_(tuple)
		cover = None
		
		with classlock:
			if tupform in allclasses:
				cover = divisors.cover(allclasses[tupform])
				
		nodespatch.set_offsets(np.array([pos[v] for v in G]))
		if cover is not None:
			nodespatch.set_facecolors([(ncolor if cover[x] else '0.5') for x in N])
			nodespatch.set_linestyle([('-' if cover[x] else ':') for x in N])
			nodespatch.set_lw(1)
		else:
			nodespatch.set_facecolor(np.array(ncolor)/2)
			nodespatch.set_linestyle(':')
			nodespatch.set_lw(2)
			
		nodespatch.set_sizes([nodsizdic[x] for x in N])

		emph = divisors.div2tree(G=G, D=qred_div)	

		highlight = '0.6' if is_qred else '0.7' #rgb2hex(np.array(ncolor)/2 + [0.35]*3)
		
		for e in edgepatches:
			e.remove()
		edgepatches.clear()

		edgepatches.append(ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=G.edges(keys=True)), ec='0.8', fc='none', lw=2.5)))
		edgepatches.append(ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=emph), ec=highlight, fc='none', lw=4)))
		
		loadtext.set_text(r'loaded $\mathcal{G} \in \{'+', '.join(['c_{'+str(l)+'}' for l in loaded])+r'\}~\ldots$')

	
	classlock = Lock()
	def populate_classes():
		g = sum(div)
		for i in itertools.chain((g,), reversed(range(g)), range(g+1, len(G))):
			newvals = divisors.full_classes(G, i, keep_trivial=True)
			with classlock:
				allclasses.update(newvals)
				
			update()
			loaded.append(i)

	
	labels, nodesizedict	 = labeldata(localdiv)
	nodesizelist = [nodesizedict[x] for x in N]
	
	pos,ax,cf = fig_setup(G, kwargs.pop('ax')) if 'ax' in kwargs else fig_setup(G)
	
	loadtext = ax.text(0.5,0.02,'loading:',horizontalalignment='center', transform=ax.transAxes)
		
	cf.canvas.set_window_title('Graph Divisor View '+str(index))
	ncolor = colorConverter.to_rgb(kwargs['c'])	
	
	xy=np.asarray([pos[v] for v in N])
	nodespatch = ax.scatter(xy[:,0], xy[:,1], s = nodesizelist, picker=True, **kwargs)
	nodespatch.set_zorder(2)
	#nx.draw_networkx_nodes(G, pos, node_size=nodesizedict, picker=True, **kwargs)
	
	ftcolor = 'k' if sum(ncolor) > 1.5 else 'w'
	labelpatch = nx.draw_networkx_labels(G, pos, labels=labels, font_family='serif', font_color=ftcolor, font_size=20)

	annotations = annotate(ax, pos, nodesizedict)
	update()
		
	modes = ['firing', 'adding']
	mode = [modes[0]]

	def modeswitch(label):
		mode[0] = label
		plt.draw()
		
	rax = plt.axes([0.01, 0.01, 0.14, 0.11])
	radio = RadioButtons(rax, modes)
	radio.on_clicked(modeswitch)


	buts = add_reposition_buttons(cf, pos, G, update)	
	divisor_view.baggage = buts + [radio]
	
	
	
	def onpick(event):
		ind = event.ind
		way = {1: 1, 3:-1}[event.mouseevent.button]
		
		if mode[0] is 'firing':
			divisors.fire(localdiv, {N[i]:way for i in ind}, G)
		elif mode[0] is 'adding':
			for i in ind:
				localdiv[N[i]] += way


		update()

		plt.draw()		
	
	cf.canvas.mpl_connect('pick_event', onpick)
	
	updater = Thread(target=populate_classes)
	updater.start()
	
	def drw():
		#print("drawing")
		#updateD(localdiv)
		cf.canvas.draw_idle()
		#plt.draw()
	
	timer = cf.canvas.new_timer(interval=150)
	timer.add_callback(drw)
	timer.start()
	
	divisor_view.current_timer = timer
	#return nodespatch,labelpatch
	

def get_dims(L):
	M = min(5,math.ceil(L/math.sqrt(L)))
	N = math.ceil(L/M)
	return N,M
	
def display_complete(Gs, degree=2):	
	colors = list(cnames.values())

	for G in Gs:
		color = random.choice(colors)
		qreds = divisors.full_classes(G, degree)
		todisp = [qred for qred in qreds if divisors.span(qreds[qred]) == len(G)] 
		
		if len(todisp) == 0:
			continue
		
		N,M = get_dims(len(todisp))
		
		fig, ax = plt.subplots(M,N)
		ax = np.array(ax).flatten()
		print(ax)
		for i, qred in enumerate(todisp):
			print(i, qred)
			divisor_view(G, qred, ax=ax[i], c=color)
	
def paintAll(ingraphs, spacing=1.4, painter=paint_multi):
	fig = plt.figure()
	
	if type(ingraphs) is dict:
		Gs, counts = zip(*ingraphs.items())
		L = len(Gs) + 1 
		axes = plt.axes([0.01,0,0.85,1])
	elif type(ingraphs) is list:
		Gs = ingraphs
		counts = None
		L = len(Gs)
		axes = plt.axes([0.01,0,0.98,1])
	else:
		raise ValueError("expected list or dict, not "+str(type(ingraphs)))
	
	colors = list(cnames.values())

	N,M = get_dims(L)

	
	if counts is not None:
		heatmap = np.zeros(get_dims(len(Gs)))
		heataxes = fig.add_axes([0.8,0.1,0.2,(0.2*N)/M])
		heataxes.set_axis_off()
	
	offset = 0.02
	colors = [random.choice(colors) for i in range(len(Gs))]
	

	for i,g in enumerate(Gs):
		y,x = i//M, i%M
		painter(g, axes, offset=spacing*np.array([x,N-y]), node_color=colors[i]) #, node_color=random.choice(colors)
		
		
		if counts is not None:
			heatmap[y,x] = counts[i]	
			heataxes.text(x,y, counts[i], va='center', ha='center', color='black')
			heataxes.text(x-offset,y-offset, counts[i], va='center', ha='center', color='white')
		
	if counts is not None: heataxes.matshow(heatmap,cmap='Greys')


	# first is the place I want to be, second is the place I am
	top_pos = spacing*(N+1-min(N,M))
	pos = [top_pos]*2
	def scroll(mouse_event):		
		pos[0] =  min(top_pos, max(0, pos[0]+ 0.3*float(mouse_event.step)))
		
	def update(timer):
		if not plt.fignum_exists(fig.number):
			timer.stop()

		thistime = time.time()
			
		if ( abs(pos[0]-pos[1]) < 0.05 or not hasattr(update,'last_time')):
			update.last_time = thistime
			return
			
		dtime = thistime - update.last_time			
		pos[1] += (pos[0]-pos[1])*(1-1.0/(1+dtime*7))
		axes.axis([-0.1,M*spacing, pos[1], pos[1]+M*spacing])		
		fig.canvas.draw_idle()
		update.last_time = thistime
		

	timer = fig.canvas.new_timer(interval=20)
	timer.add_callback(update,timer)
	
	def start_timer(evt):
		timer.start()
		fig.canvas.mpl_disconnect(drawid)
	drawid = fig.canvas.mpl_connect('draw_event', start_timer)
	
	def pressed(mouse_event):
		x,y = int(mouse_event.xdata/spacing), N-int(mouse_event.ydata/spacing)
		idx = x+M*y
		if x >= 0 and x < M and y >= 0 and y < N and idx < len(Gs):
			plt.figure()
			CXT['select_G'] = Gs[idx]
			divisor_view(Gs[idx], index=idx, c=colors[idx])
	
	fig.canvas.mpl_connect('scroll_event', scroll)
	fig.canvas.mpl_connect('button_press_event', pressed)
	axes.set_aspect('equal', 'datalim')
	axes.axis([-0.1,M*spacing, pos[0], pos[0]+M*spacing])
		
	plt.show()
	paintAll.current_timer = timer # prevent GC in spyder