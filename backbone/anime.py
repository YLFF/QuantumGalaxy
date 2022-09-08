import random
import pylab
from matplotlib.pyplot import pause
import networkx as nx
import itertools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation




graph = nx.Graph()
node_number = 0
graph.add_node(node_number, Position=(random.randrange(0, 100), random.randrange(0, 100)))
fig, ax = plt.subplots(dpi=200)

def gen_fig(i,ax=ax):


    graph.add_node(i, Position=(random.randrange(0, 100), random.randrange(0, 100)))
    graph.add_edge(i, random.choice(list(graph.nodes())))
    #fig = pylab.figure()
    #fig=plt.figure()
    nx.draw_networkx_nodes(graph,pos=nx.get_node_attributes(graph,'Position'),ax=ax,node_size=15)
    nx.draw(graph, pos=nx.get_node_attributes(graph,'Position'),ax=ax)
    pause(1)
    return 
#fig=gen_fig(0)

ani = animation.FuncAnimation(fig, gen_fig, 50, interval=10, init_func=None)
plt.show()