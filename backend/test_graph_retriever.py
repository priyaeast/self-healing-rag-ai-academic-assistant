
from rag.graph_retriever import retrieve_graph_context


test_queries = [
    "What topics does Physics cover?",
    "Who teaches Mechanics?",
    "What topics are included in Mathematics?",
    "What study materials are available for Chemistry?",
    "What assessments are included in the Assessment Policy?"
]

for query in test_queries:

    print("\n" + "=" * 65)
    print("USER QUERY:", query)
    print("=" * 65)

    result = retrieve_graph_context(
        query=query,
        max_hops=1
    )

    print(result)
