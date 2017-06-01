from graphviz import Digraph


def make_graph(name, edgelist, nodelist):
    g = Digraph(name)
    g.attr(rankdir='LR')

    # add nodes
    cluster_id = 0
    for nodes, subgraph in nodelist:
        if subgraph == 'main':
            for node in nodes:
                g.node(str(node))
        else:
            with g.subgraph(name='cluster_{}'.format(cluster_id)) as c:
                c.attr(color='blue')
                c.attr(label=subgraph)
                for node in nodes:
                    c.node(str(node))
            cluster_id += 1

    # add edges
    for edge in edgelist:
        kw_args = {}
        if edge.keywords != ['default']:
            kw_args['label'] = ','.join(edge.keywords)
        if edge.thruput_reference == 'clear':
            kw_args['style'] = 'dashed'
        if 'reflec' in edge.thruput_reference:
            kw_args['color'] = 'red'
        g.edge(str(edge.innode), str(edge.outnode), **kw_args)

    return g
