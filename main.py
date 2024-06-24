from src.data_loader import load_data_main
from src.visualizer import create_network

if __name__ == "__main__":
    # Define this using cmd arguments
    location = r"C:\Users\Administrator\projects\traversed-topology-visualization\temp-data\traversal-log-file.json"
    tracked_metadata = {'type', 'requestTime', "producedByActor", "discoveredTimestamp", "dereferencedTimestamp"}
    graph_data = load_data_main(location, tracked_metadata)
    create_network(graph_data[-1]["edge_list"], graph_data[-1]["metadata"])
