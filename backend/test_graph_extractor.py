
import pickle

from rag.graph_extractor import build_graph_from_chunks
from rag.graph_store import load_graph


# Load the actual document chunks
with open("data/chunks.pkl", "rb") as file:
    chunks = pickle.load(file)

print("Total document chunks:", len(chunks))

# Extract entities and relationships
build_graph_from_chunks(chunks)

# Load the generated graph
graph = load_graph()

print("\n========== KNOWLEDGE GRAPH ==========")

print("\nTotal Entities:", graph.number_of_nodes())
print("Total Relationships:", graph.number_of_edges())

print("\n========== ENTITIES ==========")

for node, attributes in graph.nodes(data=True):
    print(node, attributes)

print("\n========== RELATIONSHIPS ==========")

for source, target, attributes in graph.edges(data=True):
    print(source, "->", target, attributes)
