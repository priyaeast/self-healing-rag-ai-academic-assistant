
import os
import pickle
import networkx as nx

# Knowledge Graph storage location
GRAPH_PATH = os.path.join(
    "data",
    "knowledge_graph.pkl"
)

# Create an empty directed graph
knowledge_graph = nx.DiGraph()


def add_entity(entity, entity_type):
    """
    Add an entity to the Knowledge Graph.
    """

    entity = entity.strip()

    if not entity:
        return

    knowledge_graph.add_node(
        entity,
        type=entity_type
    )



def add_relationship(
    source,
    target,
    relation,
    source_document="unknown",
    evidence="",
    confidence=None
):
    """
    Add a relationship with source and evidence metadata.
    """

    if not source or not target or not relation:
        return

    source = source.strip()
    target = target.strip()
    relation = relation.strip()

    if not source or not target:
        return

    edge_data = knowledge_graph.get_edge_data(source, target)

    if edge_data:
        # Preserve existing relationship metadata.
        sources = edge_data.get("sources", [])
        evidences = edge_data.get("evidences", [])

        if source_document and source_document not in sources:
            sources.append(source_document)

        if evidence and evidence not in evidences:
            evidences.append(evidence)

        old_confidence = edge_data.get("confidence")

        if confidence is not None:
            if old_confidence is None:
                old_confidence = confidence
            else:
                old_confidence = max(old_confidence, confidence)

        knowledge_graph.add_edge(
            source,
            target,
            relation=relation,
            sources=sources,
            evidences=evidences,
            confidence=old_confidence,
            evidence_verified=bool(evidences)
        )

    else:
        knowledge_graph.add_edge(
            source,
            target,
            relation=relation,
            sources=[source_document] if source_document else [],
            evidences=[evidence] if evidence else [],
            confidence=confidence,
            evidence_verified=bool(evidence)
        )



def save_graph():
    """
    Save the Knowledge Graph locally.
    """

    os.makedirs(
        os.path.dirname(GRAPH_PATH),
        exist_ok=True
    )

    with open(GRAPH_PATH, "wb") as file:
        pickle.dump(
            knowledge_graph,
            file
        )

    print(
        f"Knowledge Graph saved: "
        f"{knowledge_graph.number_of_nodes()} entities, "
        f"{knowledge_graph.number_of_edges()} relationships"
    )


def load_graph():
    """
    Load an existing Knowledge Graph.
    """

    global knowledge_graph

    if os.path.exists(GRAPH_PATH):
        with open(GRAPH_PATH, "rb") as file:
            knowledge_graph = pickle.load(file)

        print("Knowledge Graph loaded successfully!")

    else:
        knowledge_graph = nx.DiGraph()
        print("No existing graph found. Created a new graph.")

    return knowledge_graph


def get_graph():
    """
    Return the current Knowledge Graph.
    """

    return knowledge_graph
