
import networkx as nx
import numpy as np
from  matplotlib import pyplot as plt
import pylab
import matplotlib as mpl
import pandas as pd
import math

class QGGraphError(Exception):
    #涵盖：输入电流的两节点间不边的异常
    pass


class QGNode():
    def __init__(self, name, decay=0.8, r=0) -> None:
        super().__init__()
        self.name = name
        #self.father=None
        #self.attr= production/company
        self.decay = decay  #衰减系数
        self.r = r  #r，节点净库存流
        self.nbr = {}  #neighbor+关系 par/raw/st
        self.adj = []
        self.par = []
        self.pred = []

    def update_r(self, change):
        self.r = round(self.r + change, 2)

    def get_item(self):
        return self.name

    def add_adj(self, name, re, i=0):
        self.nbr[name] = {'re': re, 'i': i}
        self.adj.append(name)

    def add_parity(self, name, re, i=0):
        self.nbr[name] = {'re': re, 'i': i}
        self.par.append(name)

    def add_pred(self, name, re, i=0):
        self.nbr[name] = {'re': re, 'i': i}
        self.pred.append(name)

    def __dict__(self):
        return {self.name: {x for x in self.nbr}}

    def get_r(self):
        return self.r

    def get_edge_list(self):
        # ('B', 'A', {'re': 'raw','i': 0}),
        edge_list = []
        for neighbor in self.nbr:
            edge_list.append((self.name, neighbor, self.nbr[neighbor]))
        return edge_list


class QGGraph():
    def __init__(self, ):
        self.node_dict = {}
        self.edge_dict = {}
        self.updated_node_list = []
        self.node_i_out_dict = {}
        self.updated_edge_list = []
        self.num_nodes = 0
        self.num_edges = 0
        self.c_par = -0.5
        self.c_node = 0.8
        self.source_node = ''
        self.source_input = 0

    #构建和检索部分
    def add_Node(self, name):
        new_Node = QGNode(name)
        self.node_dict[name] = new_Node
        self.num_nodes += 1
        return new_Node

    def get_Node(self, name) -> dict:
        if name in self.node_dict:
            return self.node_dict[name]
        else:
            return None

    def get_all_Nodes(self) -> dict:
        dic = {}
        for node in self.node_dict:
            dic[node] = self.node_dict[node].get_r()
        return dic

    def add_Edge(self, f, t, re, i):
        if f not in self.node_dict:
            nn = self.add_Node(f)
        if t not in self.node_dict:
            nn = self.add_Node(t)
        if re in ('raw', 'st'):
            self.node_dict[f].add_adj(t, re, i)
            self.node_dict[t].add_pred(f, re, i)
        if re == 'par':
            self.node_dict[f].add_parity(t, re, i)
            self.node_dict[t].add_parity(f, re, i)
        self.edge_dict[(f, t)] = {
            're': re,
            'i': i
        }  #在图里保存并更新所有边的信息,点只存变量r，不存边的i
        self.num_edges += 1

    def get_all_Edges(self):
        return self.edge_dict

    # networkx 可视化部分
    def build_nx_dic(self):
        nx_node_list = []
        for n in self.node_dict:
            dic = {'node': self.node_dict[n], 'r': self.node_dict[n].get_r()}
            nx_node_list.append((n, dic))
        nx_edge_list = []
        for e in self.edge_dict:
            f, t = e
            nx_edge_list.append((f, t, self.edge_dict[e]))
        return nx_node_list, nx_edge_list

    def build_networkx(self):
        node, edge = self.build_nx_dic()
        G = nx.DiGraph()
        G.add_nodes_from(node)
        G.add_edges_from(edge)
        return G

    def draw_networkx(self):
        G = self.build_networkx()

        options = {
            "font_size": 15,
            "node_size": 1100,
            "node_color": "w",
            "edgecolors": "black",
            "linewidths": 0.5,
            "width": 1,
        }
        fig, ax = plt.subplots(dpi=200)
        pos = nx.spring_layout(G, 50/G.number_of_nodes(),
                               seed=6)  # Seed layout for reproducibility
        nx.draw(
            G,
            pos,
            **options,ax=ax
        )
        node_labels = {}
        for node in G.nodes:
            node_labels[node] = str(node) + ': ' + str(G.nodes[node]['r'])
        nx.draw_networkx_labels(G, pos, labels=node_labels)
        edge_labels = {}
        for edge in G.edges:
            edge_labels[edge] = str(G[edge[0]][edge[1]]['re']) + ' ' + str(
                G[edge[0]][edge[1]]['i'])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.show()

    # 计算、更新部分
    #轮子
    def update_Edge(self, f, t, i):
        if (f, t) in self.edge_dict:
            assert (f, t) not in self.updated_edge_list, ('该边已被更新过:', f, t)
            self.edge_dict[f, t]['i'] = round(i + self.edge_dict[f, t]['i'], 2)
            self.updated_edge_list.append((f, t))
        elif (t, f) in self.edge_dict:
            assert (t, f) not in self.updated_edge_list, ('该边已被更新过:', t, f)
            self.edge_dict[t, f]['i'] = round(i + self.edge_dict[t, f]['i'], 2)
            self.updated_edge_list.append((t, f))
        else:
            raise QGGraphError('更新的边不在图中存在:', f, t)

    def update_Node(self, name, r):
        assert name in self.node_dict, ('该节点不在图中:', name)
        assert name not in self.updated_node_list, ('该节点已被更新:', name)
        self.node_dict[name].update_r(r)
        self.updated_node_list.append(name)

    def get_pred_par(self, name):

        #假定互为同位的节点被全部输入，即两两间都为同位关系,获得分组列表
        query = []
        result = []
        for pred in self.node_dict[name].pred:
            group = [pred]
            if pred not in query:
                for par in self.node_dict[pred].par:
                    if par not in query:
                        if name in self.node_dict[par].adj:
                            group.append(par)
                            query.append(par)
                result.append(group)
                query.append(pred)
        return result
        
    def get_adj_par(self, name):
        query = []
        result = []
        for adj in self.node_dict[name].adj:
            group = [adj]
            if adj not in query:
                for par in self.node_dict[adj].par:
                    if par not in query:
                        if name in self.node_dict[par].pred:
                            group.append(par)
                            query.append(par)
                result.append(group)
                query.append(adj)
        return result

    #输入和响应
    def update_graph(self, input):
        self.add_source(input)
        self.source_node = input['f']
        self.source_input = input['i']
        q = [input['t']]
        while len(q) > 0:
            current = q.pop(0)
            nbr = []
            #print(current)
            #print(q)
            for adj in self.node_dict[current].adj:
                if adj not in self.updated_node_list:
                    q.append(adj)
                    #print(current,adj,self.edge_dict[current,adj]['i'])
                    self.update(f=current,
                                t=adj,
                                i_in=self.edge_dict[current, adj]['i'])
                for pred in self.node_dict[current].pred:
                    if pred not in self.updated_node_list:
                        q.append(pred)
                        #print(pred,current,self.edge_dict[pred,current]['i'])
                        self.update(f=current,
                                    t=pred,
                                    i_in=self.edge_dict[pred, current]['i'])
                '''for n in nbr:
                    q.append(n)
                    self.update(f=current,t=n,i_in=self.edge_dict[(current,n)])'''
        print('本次输入更新的边为:', self.updated_edge_list)
        print('本次输入更新的点为:', self.updated_node_list)
        self.updated_node_list = []
        self.updated_edge_list = []

    def add_source(self, input):
        #input={'f':'B','t':'A','i':20}
        f = input['f']
        t = input['t']
        i = input['i']
        self.update(f=f, t=t, i_in=i)

    def bfs(self, start):
        q = [start]
        over = []
        #start,i_out=
        while len(q) > 0:
            #if q[0] not in over:

            current = q.pop(0)

            print(current)
            nbr = []
            for adj in self.node_dict[current].adj:
                if adj not in self.updated_node_list:
                    nbr.append(adj)
            for pred in self.node_dict[current].pred:
                if pred not in self.updated_node_list:
                    nbr.append(pred)
            for n in nbr:
                print(n)
                q.append(n, )

                self.updated_node_list.append(n)
                #print(self.updated_node_list)
            over.append(current)

    def update(self, f, t, i_in) -> None:

        #先分组，再计算，再递归传导
        #对一个点产生影响的只有一个源（或者经过同位衰减的一组源）
        #f='b',t='a',i_in=20
        #此处f，t为影响力传播，非边的方向,i为ft之间的影响力，同时为t的i_in更新前的初值
        #只对t更新，然后由t传播(与边的方向无关)
        if t == self.source_node:
            i_in = self.source_input

        c_node = self.c_node
        c_par = self.c_par
        preds = self.get_pred_par(t)
        adjs = self.get_adj_par(t)
        print(t,adjs)
        f_node = self.node_dict[f]
        t_node = self.node_dict[t]
        if f in t_node.pred:
            #f为t的上游时，f-t是源，找上游组
            for group in preds:
                if f in group:
                    if len(group) > 1:
                        group.remove(f)
                        for other in group:
                            if (other, t) not in self.updated_edge_list:
                                self.update_Edge(
                                    other, t,
                                    round(c_par * i_in / len(group), 2))
                                i_in += round(c_par * i_in / len(group), 2)
                            else:

                                i_in += round(self.edge_dict[(other, t)]['i'],
                                              2)

        else:
            #否则相反，找下游组

            for group in adjs:
                
                if f in group:
                    print(group)
                    if len(group) > 1:

                        group.remove(f)
                        for other in group:
                            if (t, other) not in self.updated_edge_list:
                                self.update_Edge(
                                    t, other,
                                    round(c_par * i_in / len(group), 2))
                                i_in += round(c_par * i_in / len(group), 2)
                                #print('trigger', i_in)
                            else:
                                i_in += round(self.edge_dict[(t, other)]['i'],
                                              2)
                                #print('trigger', i_in)
        print(t, i_in)
        #更新ir
        if t not in self.updated_node_list:
            #print(t,round(i_in*(1-c_node),2))
            self.update_Node(t, r=round(i_in * (1 - c_node), 2))
        else:
            pass
        #对其他所有组更新iout
        i_out = round(i_in * c_node, 2)
        self.node_i_out_dict[t] = i_out
        for group in preds:
            num = len(group)
            for other in group:
                if (other, t) not in self.updated_edge_list:
                    self.update_Edge(other, t, round(i_out / num, 2))
        for group in adjs:
            num = len(group)
            for other in group:
                if (t, other) not in self.updated_edge_list:
                    self.update_Edge(t, other, round(i_out / num, 2))
        #更新相邻节点 #BFS
       
if __name__=='__main__':
    nodes_list = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
        'P', 'Q'
    ]
    g=QGGraph()
    for n in nodes_list:
        g.add_Node(n)

    whole_edges_list = [
        ('B', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('C', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('D', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('E', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('F', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('G', 'A', {
            're': 'raw',
            'i': 0
        }),
        ('K', 'G', {
            're': 'raw',
            'i': 0
        }),
        ('A', 'I', {
            're': 'raw',
            'i': 0
        }),
        ('A', 'J', {
            're': 'st',
            'i': 0
        }),
        ('H', 'I', {
            're': 'raw',
            'i': 0
        }),
        ('I', 'L', {
            're': 'raw',
            'i': 0
        }),
        ('L', 'M', {
            're': 'raw',
            'i': 0
        }),
        ('B', 'C', {
            're': 'par',
            'i': 0
        }),
        ('A', 'H', {
            're': 'par',
            'i': 0
        }),
        ('E', 'F', {
            're': 'par',
            'i': 0
        }),
        ('F', 'K', {
            're': 'par',
            'i': 0
        }),
        ('P', 'C', {
            're': 'raw',
            'i': 0
        }),
        ('B', 'N', {
            're': 'raw',
            'i': 0
        }),
        ('O', 'B', {
            're': 'raw',
            'i': 0
        }),
        ('Q', 'B', {
            're': 'raw',
            'i': 0
        }),
        ('Q', 'C', {
            're': 'raw',
            'i': 0
        }),
    ]
    for l in whole_edges_list:
        g.add_Edge(f=l[0],t=l[1],re=l[2]['re'],i=l[2]['i'])

    #g.draw_networkx()
    print(g.get_all_Nodes())
    print(g.get_all_Edges())

    g.update_graph(input={'f': 'B', 't': 'A', 'i': 20})
    #g.add_source(input={'f': 'B', 't': 'A', 'i': 20})

    g.draw_networkx()
    print(g.get_all_Nodes())
    print(g.get_all_Edges())



