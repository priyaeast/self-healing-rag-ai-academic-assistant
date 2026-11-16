
import faiss
import pickle
import numpy as np

from rank_bm25 import BM25Okapi
from rag.embedder import get_model


def retrieve_chunks(
    query,
    keywords=None,
    category=None,
    strategy="semantic",
    top_k=4
):

    print("\n===== RETRIEVAL STRATEGY =====")
    print(strategy)
    print("==============================")

    model = get_model()

    # Load FAISS index
    index = faiss.read_index(
        "data/faiss_index/index.bin"
    )

    # Load document chunks
    with open("data/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    search_query = query

    if keywords:
        search_query += " " + " ".join(keywords)

    # =====================================================
    # Semantic Search
    # =====================================================

    if strategy == "semantic":

        print("Using Semantic Search")

        query_embedding = model.encode(
            [search_query]
        )

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        distances, indices = index.search(
            query_embedding,
            top_k * 3
        )

        results = []

        THRESHOLD = 2.5

        for distance, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx == -1:
                continue

            if distance <= THRESHOLD:
                results.append(chunks[idx])

        if not results:

            print("No chunks under threshold.")
            print("Returning top semantic matches.")

            for idx in indices[0]:

                if idx != -1:
                    results.append(chunks[idx])

        return results[:top_k]

    # =====================================================
    # Metadata Search
    # =====================================================

    elif strategy == "metadata":

        print("Using Metadata Search")

        results = []

        search = search_query.lower()

        for chunk in chunks:

            chunk_text = chunk["text"].lower()

            if (
                search in chunk_text
                or any(
                    keyword.lower() in chunk_text
                    for keyword in (keywords or [])
                )
            ):

                results.append(chunk)

        return results[:top_k]

    # =====================================================
    # Hybrid Search: FAISS + BM25
    # =====================================================

    elif strategy == "hybrid":

        print("Using Hybrid Search")

        query_embedding = model.encode(
            [search_query]
        )

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        _, faiss_indices = index.search(
            query_embedding,
            top_k * 3
        )

        corpus = [
            chunk["text"]
            for chunk in chunks
        ]

        tokenized = [
            doc.lower().split()
            for doc in corpus
        ]

        bm25 = BM25Okapi(tokenized)

        scores = bm25.get_scores(
            search_query.lower().split()
        )

        bm25_indices = np.argsort(scores)[::-1][:top_k * 3]

        merged = []
        seen = set()

        for idx in (
            list(faiss_indices[0]) +
            list(bm25_indices)
        ):

            if idx == -1:
                continue

            if idx not in seen and idx < len(chunks):

                seen.add(idx)
                merged.append(chunks[idx])

        return merged[:top_k]

    # =====================================================
    # Default: Semantic Search
    # =====================================================

    else:

        print("Unknown strategy. Using Semantic Search.")

        query_embedding = model.encode(
            [search_query]
        )

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        _, indices = index.search(
            query_embedding,
            top_k
        )

        return [
            chunks[i]
            for i in indices[0]
            if i != -1
        ]
