import json
import networkx as nx
from pyvis.network import Network


def convert_edge_list(edge_list):
    return ["{} {}".format(edge[0], edge[1]) for edge in edge_list]


def create_node_attributes(ordered_metadata):
    node_url = [x['url'] for x in ordered_metadata]
    node_dereferenced_bool = [True if 'dereferencePosition' in x else False for x in ordered_metadata]
    node_dereference_order = [x['dereferencePosition'] if 'dereferencePosition' in x else 0 for x in ordered_metadata]
    node_discover_order = [x['discoverPosition'] if 'dereferencePosition' in x else 0 for x in ordered_metadata]
    node_request_time = [x['requestTime'] if 'requestTime' in x else -1 for x in ordered_metadata]
    node_dereference_timestamp = [x['dereferencedTimestamp']
                                  if 'dereferencedTimestamp' in x else -1 for x in ordered_metadata]
    node_discover_timestamp = [x['discoveredTimestamp']
                               if 'discoveredTimestamp' in x else -1 for x in ordered_metadata]
    node_type = [x['type'] if 'type' in x else '' for x in ordered_metadata]

    return [
        (node_url, "url"),
        (node_dereferenced_bool, "dereferenced"),
        (node_discover_timestamp, "discover timestamp"),
        (node_discover_order, "discover order"),
        (node_type, "source type"),
        (node_dereference_timestamp, "dereference timestamp"),
        (node_dereference_order, "dereference order"),
        (node_request_time, "HTTP request time")
    ]


def create_node_dict(node_attributes):
    node_dicts = [{} for i in range(len(node_attributes[0][0]))]
    for attribute in node_attributes:
        for i, attr in enumerate(attribute[0]):
            node_dicts[i][attribute[1]] = attr
    return node_dicts


def set_attributes(nt, node_dicts):
    for i, node in enumerate(nt.nodes):
        node['title'] = json.dumps(node_dicts[i], indent=2)[1:-1]
        node['dereferenced'] = node_dicts[i]['dereferenced']


def set_color(nt):
    for node in nt.nodes:
        if node['dereferenced']:
            node['color'] = "red"


def create_network(edge_list, ordered_metadata):
    edge_list = convert_edge_list(edge_list)
    G = nx.parse_edgelist(edge_list, nodetype=int,
                          create_using=nx.DiGraph)
    G = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    node_attributes = create_node_attributes(ordered_metadata)
    node_dicts = create_node_dict(node_attributes)

    nx.draw_kamada_kawai(G,
                         node_size=20,
                         with_labels=True
                         )

    nt = Network('1000px', '1000px', notebook=False, directed=True)
    nt.from_nx(G)

    set_attributes(nt, node_dicts)

    set_color(nt)

    nt.show('traversed_topology.html', notebook=False)
