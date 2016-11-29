# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 13:41:14 2016

@author: Oliver
"""

def paintAll_multiaxis(ingraphs):
	
	if type(ingraphs) is dict:
		Gs, counts = zip(*ingraphs.items())
		L = len(Gs) + 1 
	elif type(ingraphs) is list:
		Gs = ingraphs
		counts = None
		L = len(Gs)
	else:
		raise ValueError("expected list or dict, not "+str(type(ingraphs)))
	
	colors = list(cnames.values())

	N,M = get_dims(L)

	fig, axes = plt.subplots(N,M, figsize=(M*3,N*3))
	if N == 1:
		axes = [axes]
	
	if counts is not None:
		heatmap = np.zeros(get_dims(len(Gs)))
		heataxes = axes[(L-1)//M][(L-1)%M]	
		heataxes.set_axis_off()
	
	offset = 0.005 * N

	for i,g in enumerate(Gs):
		y,x = i//M, i%M
		ax = axes[y][x]
		paint_multi(g, ax, node_color=random.choice(colors)) #, node_color=random.choice(colors)
		
		
		if counts is not None:
			heatmap[y,x] = counts[i]	
			heataxes.text(x,y, counts[i], va='center', ha='center', color='black')
			heataxes.text(x-offset,y-offset, counts[i], va='center', ha='center', color='white')
		
	if counts is not None: heataxes.matshow(heatmap,cmap='Greys')
	
	for j in range(L, N*M):
		axes[j//M][j%M].remove()
		
	plt.show()