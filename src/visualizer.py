import json
import networkx as nx
from pyvis.network import Network

from src.data_loader_single_topology import load_and_process_topologies


def convert_edge_list(edge_list):
    # Reverse edge-list because its in the wrong format for some reason
    return ["{} {}".format(edge[0], edge[1]) for edge in edge_list]


def create_node_attributes(ordered_metadata):
    node_url = [x['url'] for x in ordered_metadata]
    node_dereferenced_bool = [True if 'dereferenceOrder' in x else False for x in ordered_metadata]
    node_dereference_order = [x['dereferenceOrder'] if 'dereferenceOrder' in x else 0 for x in ordered_metadata]
    node_discover_order = [x['discoverOrder'] if 'discoverOrder' in x else [] for x in ordered_metadata]
    node_request_time = [x['requestTime'] if 'requestTime' in x else -1 for x in ordered_metadata]
    node_dereference_timestamp = [x['dereferencedTimestamp']
                                  if 'dereferencedTimestamp' in x else -1 for x in ordered_metadata]
    node_discover_timestamp = [x['discoveredTimestamp']
                               if 'discoveredTimestamp' in x else [] for x in ordered_metadata]
    node_type = [x['type'] if 'type' in x else '' for x in ordered_metadata]
    node_seed = [x['seed'] if 'seed' in x else False for x in ordered_metadata]

    return [
        (node_url, "url"),
        (node_dereferenced_bool, "dereferenced"),
        (node_discover_timestamp, "discover timestamp"),
        (node_discover_order, "discover order"),
        (node_type, "source type"),
        (node_dereference_timestamp, "dereference timestamp"),
        (node_dereference_order, "dereference order"),
        (node_request_time, "HTTP request time"),
        (node_seed, "seed")
    ]


def create_node_dict(node_attributes):
    node_dicts = [{} for i in range(len(node_attributes[0][0]))]
    for attribute in node_attributes:
        for i, attr in enumerate(attribute[0]):
            node_dicts[i][attribute[1]] = attr
    return node_dicts


def set_attributes(nt, node_dicts):
    for i, node in enumerate(nt.nodes):
        node_id = str(i)
        node['title'] = json.dumps(node_dicts[node_id], indent=2)[1:-1]
        node['dereferenced'] = node_dicts[node_id]['dereferenced']
        node['type'] = node_dicts[node_id]['source type']
        node['d_timestamp'] = node_dicts[node_id]['discover timestamp']
        node['seed'] = node_dicts[node_id]['seed']


def set_attributes_metadata(nt, node_metadata):
    for node in nt.nodes:
        node_id = str(node['id'])
        if node_id == '1':
            node['title'] = "Virtual root node"
            continue
        node['title'] = json.dumps(node_metadata[node_id], indent=2)
        node['dereferenced'] = node_metadata[node_id]['dereferenced']
        node['seed'] = node_metadata[node_id]['seed']
        node['intermediate_solution_contribution'] = node_metadata[node_id].get('intermediate_solution_contribution', 0)
        node['solution_contribution'] = node_metadata[node_id].get('solution_contribution', 0)
        node['produced_by'] = node_metadata[node_id].get('producedBy')


def set_color(nt):
    for node in nt.nodes:
        if node['title'] == 'Virtual root node':
            node['color'] = "gray"
            continue
        if not node['dereferenced']:
            node['color'] = "orange"
        if node['dereferenced']:
            node['color'] = "green"
        if node['seed']:
            node['color'] = "blue"
        if node['intermediate_solution_contribution'] > 0:
            node['color'] = "orange"
        if node['solution_contribution'] > 0:
            node['color'] = "yellow"


def create_network(edge_list, ordered_metadata, output_name="test.html"):
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

    nt = Network("1800px", "1000px", notebook=False, directed=True)
    nt.from_nx(G)
    # nt.toggle_physics
    set_attributes(nt, node_dicts)

    set_color(nt)

    nt.show(output_name, notebook=False)


def create_network_single_topology(edge_list, metadata, output_name="test.html"):
    edge_list = convert_edge_list(edge_list)
    G = nx.parse_edgelist(edge_list, nodetype=int,
                          create_using=nx.DiGraph)
    # G = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)
    nx.draw_kamada_kawai(G,
                         node_size=20,
                         with_labels=True
                         )

    nt = Network("1800px", "1000px", notebook=False, directed=True)
    nt.from_nx(G)
    # nt.toggle_physics
    set_attributes_metadata(nt, metadata)

    set_color(nt)
    nt.toggle_physics(False)
    nt.show(output_name, notebook=False)


def create_topology_discover_queries():
    data = load_and_process_topologies("../data-solidbench-v3/")
    print("Done loading")
    for (name, query_data) in data.items():
        print(name)
        if name == "i-d-1":
            create_network_single_topology(query_data['edge_list'], query_data['metadata'], "{}.no-physics.html".format(name))
    pass


if __name__ == "__main__":
    create_topology_discover_queries()
    # data = load_and_process_topologies("../data-solidbench/")
    # print(data.keys())
    # create_network_single_topology(data['i-d-1']['edge_list'], data['i-d-1']['metadata'], 'single_topology.html')
