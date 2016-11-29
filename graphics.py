# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:05:53 2016

@author: Oliver
"""
from matplotlib import pyplot as plt
from matplotlib.colors import cnames, colorConverter 
from matplotlib.path import Path
import matplotlib.patches as patches

import networkx as nx
import numpy as np
import time

import math, random

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

def bend(pu, pv, i, num) :
	factor =  (-1 + (i+1)*2.0/float(num+1)) * 	2 
	return 0.5*(pu+pv) + perp(pv-pu) * factor

def multiedge_path(G, pos):
	E = G.edges()
	counts = {(u,v):len(G[u][v]) for u,v in E}
	
	verts = []
	codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]*len(E)
	hist = {}
	

	for u,v in E:
		bend_idx = hist.get((u,v), 0)
		hist[u,v] = bend_idx+1
		
		pu = np.array(pos[u])
		pv = np.array(pos[v])
		verts.append(pu)
		verts.append(bend(pu,pv, bend_idx, counts[u,v]))
		verts.append(pv)
	
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
		
def paint_multi(G, ax=None, offset=None, **kwargs):
	pos,ax,cf = fig_setup(G, ax, offset)	
	ax.add_patch(patches.PathPatch(multiedge_path(G,pos), ec='gray', fc='none', lw=2))
	#ax.add_patch(patches.PathPatch(Path(verts,[1,2,2]*len(G.edges())), ec='black', lw=1))
	nx.draw_networkx_nodes(G,pos,ax=ax,**kwargs)


def divisor_view(G, painter, div=None, index='', **kwargs):
	if div is None:
		div = np.array([ n % 4 for n in G.nodes() ])
		
	labels = {x:  (str(div[x]) if div[x] != 0 else '') for x in G.nodes()}
	
	pos,ax,cf = fig_setup(G)
	cf.canvas.set_window_title('Graph Divisor View '+str(index))
	ax.add_patch(patches.PathPatch(multiedge_path(G,pos), ec='0.8', fc='none', lw=3))
	nx.draw_networkx_nodes(G, pos, node_size=800*div + 100, **kwargs)
	
	ftcolor = 'k' if sum(colorConverter.to_rgb(kwargs['node_color'])) > 1.5 else 'w'
	nx.draw_networkx_labels(G, pos, labels=labels, font_weight='bold', font_family='serif', font_color=ftcolor, font_size=20)		

def get_dims(L):
	M = min(5,math.ceil(L/math.sqrt(L)))
	N = math.ceil(L/M)
	return N,M

	
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
			divisor_view(Gs[idx], painter=painter, index=idx, node_color=colors[idx])
	
	fig.canvas.mpl_connect('scroll_event', scroll)
	fig.canvas.mpl_connect('button_press_event', pressed)
	axes.set_aspect('equal', 'datalim')
	axes.axis([-0.1,M*spacing, pos[0], pos[0]+M*spacing])
		
	plt.show()
	paintAll.current_timer = timer # prevent GC in spyder