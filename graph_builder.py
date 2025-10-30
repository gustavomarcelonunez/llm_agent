import networkx as nx

def build_graph(results):
    G = nx.Graph()
    for item in results:
        G.add_node(item['nombre'], type='portal')
        G.add_edge('consulta', item['nombre'], relation='ofrece_datos')
    return G
