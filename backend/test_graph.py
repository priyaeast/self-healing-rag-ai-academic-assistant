
from rag.graph_store import (
    add_entity,
    add_relationship,
    save_graph,
    load_graph,
    get_graph
)

add_entity("MCA", "Course")
add_entity("Computer Science", "Department")
add_entity("Python", "Subject")

add_relationship(
    "MCA",
    "Computer Science",
    "belongs_to"
)

add_relationship(
    "MCA",
    "Python",
    "includes_subject"
)

save_graph()

graph = load_graph()

print("\nEntities:")
print(list(graph.nodes(data=True)))

print("\nRelationships:")
print(list(graph.edges(data=True)))
