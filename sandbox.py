# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 10:58:38 2016

@author: Oliver
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

def plot_undirected_graph(xy, z):

    fig, ax = plt.subplots(1, 1)
    ax.hold(True)

    # the indices of the start, stop nodes for each edge
    i, j = np.where(z)

    # an array of xy values for each line to draw, with dimensions
    # [nedges, start/stop (2), xy (2)]
    segments = np.hstack((xy[i, None, :], xy[j, None, :]))

    # the 'intensity' values for each existing edge
    z_connected = z[i, j]

    # this object will normalize the 'intensity' values into the range [0, 1]
    norm = plt.Normalize(z_connected.min(), z_connected.max())

    # LineCollection wants a sequence of RGBA tuples, one for each line
    colors = plt.cm.jet(norm(z_connected))

    # we can now create a LineCollection from the xy and color values for each
    # line
    lc = LineCollection(segments, colors=colors, linewidths=2,
                        antialiased=True)

    # add the LineCollection to the axes
    ax.add_collection(lc)

    # we'll also plot some markers and numbers for the nodes
    ax.plot(xy[:, 0], xy[:, 1], 'ok', ms=10)
    for ni in range(z.shape[0]):
        ax.annotate(str(ni), xy=xy[ni, :], xytext=(5, 5),
                    textcoords='offset points', fontsize='large')

    # to make a color bar, we first create a ScalarMappable, which will map the
    # intensity values to the colormap scale
    sm = plt.cm.ScalarMappable(norm, plt.cm.jet)
    sm.set_array(z_connected)
    cb = plt.colorbar(sm)

    ax.set_xlabel('X position')
    ax.set_ylabel('Y position')
    cb.set_label('Edge intensity')

    return fig, ax
				
xy = np.random.rand(10, 2)

# a random adjacency matrix
adj = np.random.poisson(0.2, (10, 10))

# we multiply by this by a matrix of random edge 'intensities'
z = adj * np.random.randn(*adj.shape)

# do the plotting
plot_undirected_graph(xy, z)
                              