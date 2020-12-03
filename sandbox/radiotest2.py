
def divisor_view(G, div=None, index='', **kwargs):
	N = G.nodes()
	
	if div is None:
		div = divisors.spanning_div(G)
	if not 'c' in kwargs:
		kwargs['c'] = 'b'
		
	def labeldata(d):
		labels = {x:(str(d[x]) if d[x] != 0 else '') for x in N}
		nodesizedict = {x: 800*np.abs(d[x]) + 100 for x in N}
		return labels, nodesizedict

	localdiv = div # or div.copy() # if we don't want modification
	labels, nodesizedict	 = labeldata(localdiv)
	nodesizelist = [nodesizedict[x] for x in N]
	
	pos,ax,cf = fig_setup(G, kwargs.pop('ax')) if 'ax' in kwargs else fig_setup(G)
		
	cf.canvas.set_window_title('Graph Divisor View '+str(index))
	
	emph = divisors.div2tree(G=G, D=divisors.to_q_reduced(localdiv, G))	
	noemph = [e for e in G.edges(keys=True) if e not in emph]

	edgepatches = [
		ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=noemph), ec='0.8', fc='none', lw=3)),
		ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=emph), ec='0.6', fc='none', lw=5)) ]
	
	xy=np.asarray([pos[v] for v in N])
	nodespatch = ax.scatter(xy[:,0], xy[:,1], s = nodesizelist, picker=True, **kwargs)
	nodespatch.set_zorder(2)
	#nx.draw_networkx_nodes(G, pos, node_size=nodesizedict, picker=True, **kwargs)
	
	ftcolor = 'k' if sum(colorConverter.to_rgb(kwargs['c'])) > 1.5 else 'w'
	labelpatch = nx.draw_networkx_labels(G, pos, labels=labels, font_family='serif', font_color=ftcolor, font_size=20)


	annotations = annotate(ax, pos, nodesizedict)

	rax = plt.axes([0.05, 0.7, 0.15, 0.15])
	radio = RadioButtons(rax, ('2 Hz', '4 Hz', '8 Hz'))
	
	
	def hzfunc(label):
		print(label)
		hzdict = {'2 Hz': s0, '4 Hz': s1, '8 Hz': s2}
		ydata = hzdict[label]
		l.set_ydata(ydata)
		plt.draw()
	radio.on_clicked(hzfunc)

	
	def onpick(event):
		ind = event.ind
		way = {1: 1, 3:-1}[event.mouseevent.button]
		
		if mode[0] is 'firing':
			divisors.fire(localdiv, {N[i]:way for i in ind}, G)
		elif mode[0] is 'adding':
			for i in ind:
				localdiv[N[i]] += way

		labs, nodsizdic = labeldata(localdiv)
		nodespatch.set_sizes([nodsizdic[x] for x in N])
		annotate(ax, pos, nodsizdic, annotations)

		## UPDATE EDGES ###
		emph = divisors.div2tree(G=G, D=divisors.to_q_reduced(localdiv, G))	
		noemph = [e for e in G.edges(keys=True) if e not in emph]
		
		for e in edgepatches:
			e.remove()
			
		edgepatches.clear()
		edgepatches.append(ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=noemph), ec='0.8', fc='none', lw=3)))
		edgepatches.append(ax.add_patch(patches.PathPatch(multiedge_path(G,pos,E=emph), ec='0.6', fc='none', lw=5)))
		##################
	
		for v, l in labs.items():
			labelpatch[v].set_text(l)

		plt.draw()
		
	
	cf.canvas.mpl_connect('pick_event', onpick)
	#return nodespatch,labelpatch