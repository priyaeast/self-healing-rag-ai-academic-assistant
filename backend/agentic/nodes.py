import re 
from rag.graph_retriever import retrieve_graph_context
from agentic.state import GraphState

from llm.planner import planner_agent

from rag.retriever import retrieve_chunks

from llm.generator import generator_agent

from llm.critic import critic_agent

from llm.reflection import reflection_agent

from rag.reranker import rerank

# from llm.verifier import verify_answer

def planner_node(state):

    print(">>> Planner START")
    print("\n===== PLANNER NODE =====")

    plan = planner_agent(
        state["query"],
        state["memory"]
    )

    # -----------------------------
    # Preserve Reflection Strategy
    # -----------------------------
    if state["memory"]:

        last = state["memory"][-1]

        if last["action"] == "change_strategy":

            print("Planner using Reflection Strategy")

            plan["strategy"] = state["strategy"]

    print("PLAN =", plan)

    # -----------------------------
    # Stop immediately
    # -----------------------------
    if plan.get("strategy") == "none":

       state["strategy"] = "none"
       state["approved"] = True

       state["answer"] = (
        "I don't have information about this "
        "in the knowledge base."
       )

       state["sources"] = []
       state["trace"].append("Planner")

       print("Planner decided to stop.")
       print(">>> Planner END")

       return state

    # -----------------------------
    # Update State
    # -----------------------------
    state["keywords"] = plan.get(
        "keywords",
        []
    )

    state["category"] = plan.get(
        "category",
        ""
    )

    state["strategy"] = plan.get(
        "strategy",
        state.get("strategy", "semantic")
    )

    print("========================")
    print("Planner Strategy =", state["strategy"])
    print(">>> Planner END")

    state["trace"].append("Planner")

    return state
    



def retriever_node(state):
    print("### GRAPH-ENABLED RETRIEVER NODE EXECUTED ###")
    print(">>> Retriever START")
    print("\n===== HYBRID GRAPH RETRIEVER =====")

    # =========================================
    # 1. FAISS + BM25 + Metadata Retrieval
    # =========================================

    chunks = retrieve_chunks(
        query=state["query"],
        keywords=state["keywords"],
        category=state["category"],
        strategy=state["strategy"],
        top_k=state["top_k"]
    )

    print(f"Document chunks retrieved: {len(chunks)}")

    # =========================================
    # 2. Cross Encoder Reranking
    # =========================================

    print("Running Cross Encoder...")

    if chunks:
       chunks = rerank(state["query"], chunks)
    else:
       chunks = []

    # =========================================
    # 3. Graph Retrieval
    # =========================================

    print("\n===== GRAPH RETRIEVAL =====")

    graph_context = retrieve_graph_context(
        query=state["query"],
        max_hops=1,
        max_entities=10,
        max_relationships=30
    )

    if graph_context and not graph_context.startswith(
        "No matching entities found"
    ):

        print("Graph context retrieved successfully.")

    else:

        graph_context = ""

        print("No relevant graph entities found.")

    # =========================================
    # 4. Handle Empty Retrieval
    # =========================================

    if len(chunks) == 0 and not graph_context:

        print("No relevant document or graph context found.")

        state["approved"] = True
        state["strategy"] = "none"

        state["answer"] = (
            "I don't have information about this "
            "in the knowledge base."
        )

        state["sources"] = []
        state["context"] = ""

        state["trace"].append("Retriever")

        return state

    # =========================================
    # 5. Build Document Context
    # =========================================

    document_context = ""

    sources = []

    for chunk in chunks:

        document_context += (
            chunk["text"] + "\n\n"
        )

        if chunk.get("source"):
            sources.append(chunk["source"])

    # =========================================
    # 6. Combine Document + Graph Context
    # =========================================

    combined_context = ""

    if document_context.strip():

        combined_context += (
            "DOCUMENT CONTEXT:\n"
            + document_context
        )

    if graph_context.strip():

        combined_context += (
            "\n\n"
            "GRAPH CONTEXT:\n"
            + graph_context
        )

    state["context"] = combined_context

        # Include source documents referenced by graph relationships.
    

    graph_sources = re.findall(
        r"\[Source: (.*?)\]",
        graph_context
    )

    sources.extend(
        source.strip()
        for source in graph_sources
        if source.strip() and source.strip() != "Unknown"
    )

    state["sources"] = sorted(set(sources))

    # =========================================
    # 7. Logging
    # =========================================

    print("\n===== RETRIEVAL SUMMARY =====")

    print("Document chunks:", len(chunks))

    print("Graph context available:", bool(graph_context))

    print("Top Sources:", state["sources"])

    print("Combined context length:", len(combined_context))

    print("=============================")

    state["trace"].append("Retriever")

    print(">>> Retriever END")

    return state


    


def generator_node(state):

    # No context -> directly stop
    if state["context"].strip() == "":

        state["approved"] = False

        state["answer"] = (
            "I don't have information about this "
            "in the knowledge base."
        )

        state["trace"].append("Generator")

        return state

    print(">>> Generator START")

    answer = generator_agent(

        state["query"],

        state["context"]

    )

    state["answer"] = answer

    state["trace"].append("Generator")

    print(">>> Generator END")

    return state

def critic_node(state):

    print(">>> CRITIC START")

    # ---------------------------------
    # Generator already returned fallback
    # ---------------------------------

    if (
        "sorry" in state["answer"].lower()
        or
        "don't have" in state["answer"].lower()
        or
        "unavailable" in state["answer"].lower()
    ):

        print("Fallback answer detected.")

        state["approved"] = False
        state["confidence"] = 0

        state["trace"].append("Critic")

        print(">>> CRITIC END")

        return state

    # ---------------------------------
    # Normal Critic
    # ---------------------------------

    result = critic_agent(

        state["query"],

        state["context"],

        state["answer"]

    )

    print(result)

    state["approved"] = (

        result["decision"] == "YES"

    )

    state["confidence"] = result["confidence"]

    # ---------------------------------
    # Hallucination Detection
    # ---------------------------------

    if state["context"]:

        if "sorry, answer unavailable" in state["answer"].lower():

            print("Hallucination detected.")

            state["approved"] = False
            state["confidence"] = 0

    print(

        "Approved :",

        state["approved"]

    )

    print(

        "Confidence :",

        state["confidence"]

    )
    
    state["trace"].append("Critic")

    print(">>> CRITIC END")

    return state

def reflection_node(state):

    print(">>> Reflection START")
    print("\n===== REFLECTION =====")

    reflection = reflection_agent(
        state["query"],
        state["context"],
        state["answer"]
    )

    print(reflection)

    state["retry"] += 1

    action = reflection.get("action", "stop")

    # -------------------------
    # Apply reflection action
    # -------------------------

    if action == "rewrite_query":

        state["query"] = reflection.get(
            "improved_query",
            state["query"]
        )

    elif action == "increase_top_k":

        state["top_k"] += 3

    elif action == "change_strategy":

        state["strategy"] = reflection.get(
            "strategy",
            "hybrid"
        )

    elif action == "stop":

     state["approved"] = False
     state["strategy"] = "none"

     state["answer"] = (
        "I don't have information about this "
        "in the knowledge base."
     )

     state["memory"].append({

        "attempt": state["retry"],
        "reason": reflection.get(
            "failure_reason",
            ""
        ),
        "action": "stop"

     })

     state["trace"].append("Reflection")

     print(">>> Reflection END")

     return state