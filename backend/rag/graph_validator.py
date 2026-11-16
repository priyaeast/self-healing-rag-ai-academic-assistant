
import re
import pickle

from rag.graph_store import load_graph


def load_document_chunks():

    with open("data/chunks.pkl", "rb") as file:
        chunks = pickle.load(file)

    documents = []

    for index, chunk in enumerate(chunks):

        if isinstance(chunk, dict):
            text = chunk.get("text", "")
            source = chunk.get("source", "unknown")

        elif hasattr(chunk, "page_content"):
            text = chunk.page_content
            source = getattr(
                chunk, "metadata", {}
            ).get("source", "unknown")

        else:
            text = str(chunk)
            source = "unknown"

        if text.strip():
            documents.append({
                "id": index + 1,
                "source": source,
                "text": text
            })

    return documents


def contains_entity(text, entity):

    return entity.casefold() in text.casefold()


def validate_graph():

    print("\nLoading Knowledge Graph...")

    graph = load_graph()
    documents = load_document_chunks()

    print("Total document chunks:", len(documents))
    print("Total graph entities:", graph.number_of_nodes())
    print("Total graph relationships:", graph.number_of_edges())

    # --------------------------------
    # ENTITY VALIDATION
    # --------------------------------

    print("\n========== ENTITY VALIDATION ==========")

    valid_entities = []
    unsupported_entities = []

    for entity, attributes in graph.nodes(data=True):

        matches = [
            doc for doc in documents
            if contains_entity(doc["text"], entity)
        ]

        if matches:

            valid_entities.append(entity)

            print(
                f"[FOUND] {entity} | "
                f"Type: {attributes.get('type', 'Unknown')} | "
                f"Chunks: {[doc['id'] for doc in matches]}"
            )

        else:

            unsupported_entities.append(entity)

            print(f"[NOT FOUND] {entity}")

    # --------------------------------
    # RELATIONSHIP VALIDATION
    # --------------------------------

    print("\n========== RELATIONSHIP VALIDATION ==========")

    supported_edges = []
    chunk_only_edges = []
    unsupported_edges = []

    for source, target, attributes in graph.edges(data=True):

        relation = attributes.get("relation", "UNKNOWN")

        same_sentence_evidence = []
        same_chunk_evidence = []

        for doc in documents:

            text = doc["text"]

            if (
                contains_entity(text, source)
                and contains_entity(text, target)
            ):

                same_chunk_evidence.append(doc["id"])

                sentences = re.split(
                    r'(?<=[.!?])\s+|\n+',
                    text
                )

                for sentence in sentences:

                    if (
                        contains_entity(sentence, source)
                        and contains_entity(sentence, target)
                    ):
                        same_sentence_evidence.append(
                            (doc["id"], sentence.strip())
                        )

        if same_sentence_evidence:

            supported_edges.append((source, target, relation))

            print(
                f"[SAME SENTENCE] {source} "
                f"-> {relation} -> {target}"
            )

            for doc_id, sentence in same_sentence_evidence[:2]:
                print(f"  Chunk {doc_id}: {sentence[:220]}")

        elif same_chunk_evidence:

            chunk_only_edges.append((source, target, relation))

            print(
                f"[SAME CHUNK ONLY] {source} "
                f"-> {relation} -> {target} | "
                f"Chunks: {same_chunk_evidence}"
            )

        else:

            unsupported_edges.append((source, target, relation))

            print(
                f"[NOT FOUND TOGETHER] {source} "
                f"-> {relation} -> {target}"
            )

    # --------------------------------
    # FINAL REPORT
    # --------------------------------

    print("\n========== VALIDATION SUMMARY ==========")

    print(
        f"Entities found: "
        f"{len(valid_entities)}/{graph.number_of_nodes()}"
    )

    print(
        f"Entities not found: "
        f"{len(unsupported_entities)}"
    )

    print(
        f"Relationships found in same sentence: "
        f"{len(supported_edges)}"
    )

    print(
        f"Relationships found only in same chunk: "
        f"{len(chunk_only_edges)}"
    )

    print(
        f"Relationships not found together: "
        f"{len(unsupported_edges)}"
    )

    print("\nValidation completed!")


if __name__ == "__main__":
    validate_graph()
