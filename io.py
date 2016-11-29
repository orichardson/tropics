# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 22:01:10 2016

@author: Oliver
"""
import networkx as nx

def read(filename):
    file = open(filename)
    G = None
    Gs = {}

    def end(G):
        if G != None:
            Gs[G] = freq
        return nx.MultiGraph()
    
    for line in file:
        if line.startswith("FREQ"):
            G = end(G)
            freq = int(line.split()[1])
        else:
            G.add_edge(*map(int,line.split()))
            
    G = end(G)

    file.close()
    return Gs

def write(filename, Gs):
    file = open(filename, 'w')
    
    if type(Gs) is list:
        gen = ('GRAPH\n{}'.format( nx.generate_edgelist(G,data=False)) for G in Gs)
    else:
        gen = ('FREQUENCY %d\n'%freq + '\n'.join(nx.generate_edgelist(
                    G,data=False))+ '\n' for G,freq in Gs.items() )
    
    file.writelines(gen)
    file.close()
    