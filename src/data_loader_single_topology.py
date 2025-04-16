import json
import os
from collections import defaultdict


def load_file(location):
    with open(location, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_result_file(location):
    data = []
    with open(location, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def process_result_data(result_json, topology_json):
    node_to_index = topology_json['nodeToIndexDict']
    intermediate_result_nodes = defaultdict(int)
    solution_nodes = defaultdict(int)
    for result_log in result_json:
        operation = result_log['operation']
        provenance = json.loads(result_log['provenance'])
        node = -1
        for url in provenance:
            node = node_to_index[url]

        if operation == 'project':
            solution_nodes[node] += 1
            pass
        if operation == 'inner':
            pass
    solution_nodes.default_factory = None
    intermediate_result_nodes.default_factory = None

    return solution_nodes, intermediate_result_nodes


def create_edge_list(topology_json):
    # adj_dict = topology_json['adjacencyListIn']
    # adj_list = []
    # for (start, target) in adj_dict.items():
    #     for target_node in target:
    #         adj_list.append([int(start), target_node])
    adj_dict = topology_json['adjacencyListOut']
    edge_list = []
    for (start, target) in adj_dict.items():
        for target_node in target:
            edge_list.append([int(start), target_node])

    return edge_list


def get_metadata(topology_json, solution_attribution, intermediate_solution_attribution):
    topology_metadata = topology_json['nodeMetadata']
    index_to_node = topology_json['indexToNodeDict']
    for (key, value) in solution_attribution.items():
        topology_metadata[str(key)]['solution_contribution'] = value
    for (key, value) in intermediate_solution_attribution.items():
        topology_metadata[str(key)]['intermediate_solution_contribution'] = value
    for (key, value) in topology_metadata.items():
        topology_metadata[key]['url'] = index_to_node[key]

    return topology_metadata

def get_metadata_updated(topology_json, solution_attribution, intermediate_solution_attribution):
    """
    Updated version to extract metadata. In accordance to the changed way comunica reports topology metadata
    :param topology_json:
    :param solution_attribution:
    :param intermediate_solution_attribution:
    :return:
    """
    topology_metadata = topology_json['nodeMetadata']
    index_to_node = topology_json['indexToNodeDict']

    extracted_metadata = {key: {} for key in topology_metadata.keys()}

    for (key, value) in solution_attribution.items():
        extracted_metadata[str(key)]['solution_contribution'] = value
    for (key, value) in intermediate_solution_attribution.items():
        extracted_metadata[str(key)]['intermediate_solution_contribution'] = value
    for (key, value) in topology_metadata.items():
        extracted_metadata[key]['url'] = index_to_node[key]
        extracted_metadata[key]['dereferenced'] = topology_metadata[key]['dereferenced']
        extracted_metadata[key]['dereferenceOrder'] = topology_metadata[key]['dereferenceOrder']
        extracted_metadata[key]['httpRequestTime'] = topology_metadata[key]['httpRequestTime']
        extracted_metadata[key]['dereferenceTimestamp'] = topology_metadata[key]['dereferenceTimestamp']
        discovered_timestamps = []
        discovered_order = []
        produced_by = []
        seed = False
        for link_metadata in topology_metadata[key]['linkMetadata']:
            if "seed" in link_metadata:
                seed = True
            discovered_order.append(link_metadata['discoverOrder'])
            discovered_timestamps.append(link_metadata['discoveredTimestamp'])
            if 'producedByActor' in link_metadata:
                produced_by.append(link_metadata['producedByActor']['name'])

        extracted_metadata[key]['seed'] = seed
        extracted_metadata[key]['discoverOrder'] = discovered_order
        extracted_metadata[key]['discoverTimestamp'] = discovered_timestamps
        extracted_metadata[key]['producedBy'] = produced_by

    return extracted_metadata


def load_and_process_single_topology(topology_data, result_data):
    edge_list = create_edge_list(topology_data)
    solution_node, intermediate_nodes = process_result_data(result_data, topology_data)
    metadata = get_metadata_updated(topology_data, solution_node, intermediate_nodes)
    return edge_list, metadata


def load_and_process_topologies(topology_dir):
    query_data = {}
    for query_dir in os.listdir(topology_dir):
        query_path = os.path.join(topology_dir, query_dir)
        topology_data = load_file(os.path.join(query_path, "StatisticTraversalTopology_0.txt"))
        # print(json.dumps(topology_data, indent=4))
        result_data = load_result_file(os.path.join(query_path, "StatisticIntermediateResults_0.txt"))
        edge_list, metadata = load_and_process_single_topology(topology_data, result_data)
        print(metadata)
        query_data[query_dir] = {'edge_list': edge_list, 'metadata': metadata}
        break
    return query_data


if __name__ == "__main__":
    data = load_and_process_topologies("../data-solidbench-v3/")
