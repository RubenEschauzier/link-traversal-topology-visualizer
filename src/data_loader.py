import json
import math

import numpy as np


def load_file(location):
    data = []
    with open(location, 'r') as f:
        for json_object in f:
            event = json.loads(json_object.strip())
            data.append(event)
    return data


"""
Function to preprocess the data needed for visualization. Each entry in the log is a new event, so we prepare graph data
equal to the number of time steps to allow for interactive visualization.
"""


def preprocess(data, tracked_metadata, step_size):
    traversal_time_steps = []
    for i in range(step_size, len(data), step_size):
        edge_list, metadata = extract_relevant_data(data[:i], tracked_metadata)
        traversal_time_steps.append({"edge_list": edge_list, "metadata": metadata})
    return traversal_time_steps


"""
Processes data to be: Edgelist - Metadata where metadata[i] is metadata of node with number i
"""


def extract_relevant_data(data, tracked_metadata):
    edge_list = []
    discover_metadata_raw = {}

    # Get last Discover Event log to get full edge list from data and metadata
    for event in reversed(data):
        if event['msg'] == "Discover Event":
            event_json = json.loads(event['data'])
            edge_list = event_json['discoveredLinks']
            discover_metadata_raw = event_json['metadata']
            break

    # Get last Dereference Event log to get full dereference order and metadata
    dereference_order = []
    for event in reversed(data):
        if event['msg'] == "Dereference Event":
            event_json = json.loads(event['data'])
            dereference_order = event_json['dereferencedLinks']
            break

    # Construct the edge list and url to index/index to url dictionaries. '
    idx = 0
    url_to_index = {}
    index_to_url = {}
    edge_list_index = []
    for edge in edge_list:
        if edge[0] not in url_to_index:
            url_to_index[edge[0]] = idx
            index_to_url[idx] = edge[0]
            idx += 1
        if edge[1] not in url_to_index:
            url_to_index[edge[1]] = idx
            index_to_url[idx] = edge[1]
            idx += 1
        edge_list_index.append([url_to_index[node] for node in edge])

    # Get metadata per node from discover information
    discover_metadata = {}
    for (url, metadata) in discover_metadata_raw.items():
        discover_link_metadata = {"discoverPosition": url_to_index[url]}
        for (key, value) in metadata.items():
            if key in tracked_metadata:
                discover_link_metadata[key] = value
        discover_metadata[url] = discover_link_metadata

    # Get metadata per node from dereference information
    deref_number = 1
    dereference_metadata = {}
    for link in dereference_order:
        deref_link_metadata = {"dereferencePosition": deref_number}
        for (key, value) in link['metadata'].items():
            if key in tracked_metadata:
                deref_link_metadata[key] = value

        dereference_metadata[link['url']] = deref_link_metadata
        deref_number += 1

    # Merge the two types of metadata
    merged_metadata = {}
    for (url, metadata_d) in discover_metadata.items():
        if url in dereference_metadata:
            merged = metadata_d | dereference_metadata[url]
        else:
            merged = metadata_d
        merged_metadata[url] = merged

    # Order them by node index
    ordered_metadata_by_node_index = []
    for (url, idx) in url_to_index.items():
        if url in merged_metadata:
            ordered_metadata_by_node_index.append(merged_metadata[url])
        else:
            ordered_metadata_by_node_index.append({})
        ordered_metadata_by_node_index[-1]['url'] = url
    relative_timestamps(['discoveredTimestamp', 'dereferencedTimestamp'], ordered_metadata_by_node_index)
    return edge_list_index, ordered_metadata_by_node_index


def relative_timestamps(timestamp_names, metadata_list):
    min_timestamp = math.inf
    for metadata in metadata_list:
        for timestamp_name in timestamp_names:
            if timestamp_name in metadata:
                if min_timestamp > metadata[timestamp_name]:
                    min_timestamp = metadata[timestamp_name]

    for metadata in metadata_list:
        for timestamp_name in timestamp_names:
            if timestamp_name in metadata:
                metadata[timestamp_name] = metadata[timestamp_name] - min_timestamp


def load_data_main(location, tracked_metadata):
    traversal_data = load_file(location)
    graph_data = preprocess(traversal_data, tracked_metadata, 5)
    return graph_data
