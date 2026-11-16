


import re
from rag.graph_store import load_graph


# --------------------------------
# 1. INTENT CONFIGURATION
# --------------------------------

INTENT_RELATIONS = {
    "faculty": {"TEACHES"},

    "topics": {"COVERS"},

    "materials": {"PROVIDES"},

    "courses": {
        "HAS_SUBJECT",
        "PROVIDES",
    },

    "assessments": {
        "HELD_ON",
        "PROVIDES",
        "COVERS",
        "HAS_ASSESSMENT",
        "CONDUCTS",
        "INCLUDES",
        "HAS_TEST",
    },

    "policies": {
        "COVERS",
        "GOVERNS",
        "FOLLOWS",
        "REQUIRES",
        "HAS_POLICY",
    },

    "general": set(),
}


# --------------------------------
# 2. QUESTION INTENT DETECTION
# --------------------------------

def detect_query_intent(query):

    q = query.casefold()

    # Check specific intents before broad course keywords.

    if any(word in q for word in [
        "attendance policy",
        "refund policy",
        "scholarship",
        "discipline policy",
        "conduct policy",
        "digital platform policy",
        "assessment policy",
        "policy",
        "policies",
        "attendance rules",
    ]):
        return "policies"

    if any(word in q for word in [
        "who teaches",
        "who is teaching",
        "faculty",
        "teacher",
        "teachers",
        "professor",
        "instructor",
        "teaches",
    ]):
        return "faculty"

    if any(word in q for word in [
        "study material",
        "study materials",
        "notes",
        "books",
        "workbook",
        "question bank",
        "resources",
    ]):
        return "materials"

    if any(word in q for word in [
        "assessment",
        "assessments",
        "exam",
        "exams",
        "test",
        "tests",
        "mock",
        "evaluation",
    ]):
        return "assessments"

    if any(word in q for word in [
        "what topics",
        "which topics",
        "chapters",
        "concepts",
        "syllabus",
        "topics",
        "covers",
        "cover",
    ]):
        return "topics"

    if any(word in q for word in [
        "which subjects",
        "what subjects",
        "subjects in",
        "course",
        "courses",
        "program",
        "programs",
        "jee",
        "neet",
    ]):
        return "courses"

    return "general"


# --------------------------------
# 3. ENTITY MATCHING + ALIASES
# --------------------------------

ENTITY_ALIASES = {
    "jee": "JEE Programs",
    "neet": "NEET Programs",
}



def find_matching_entities(query, graph):

    query_lower = query.casefold()
    matched = []

    # Exact entity matching
    for entity in graph.nodes:
        pattern = (
            r"(?<!\w)"
            + re.escape(entity.casefold())
            + r"(?!\w)"
        )

        if re.search(pattern, query_lower):
            matched.append(entity)

    # Add aliases even if other entities matched.
    for alias, entity_name in ENTITY_ALIASES.items():

        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(pattern, query_lower):
            if entity_name in graph and entity_name not in matched:
                matched.append(entity_name)

    matched.sort(key=len, reverse=True)

    return matched



# --------------------------------
# 4. ENTITY PRIORITIZATION
# --------------------------------

def prioritize_entities(entities, graph, intent):

    preferred_types = {
        "faculty": {"topic", "subject"},
        "topics": {"subject"},
        "materials": {"subject"},
        "courses": {"course"},
        "assessments": {"assessment", "exam", "test"},
        "policies": {"policy"},
        "general": set(),
    }

    preferred = preferred_types.get(intent, set())

    def entity_score(entity):

        entity_type = str(
            graph.nodes[entity].get("type", "")
        ).casefold()

        score = 10 if entity_type in preferred else 0

        score += min(len(entity), 50) / 50

        return score

    return sorted(
        entities,
        key=entity_score,
        reverse=True
    )


# --------------------------------
# 5. RELATIONSHIP FILTERING
# --------------------------------

def is_relevant_relation(relation, intent):

    relation = relation.upper().strip()

    if intent == "general":
        return True

    allowed = INTENT_RELATIONS.get(intent, set())

    if relation in allowed:
        return True

    # Support variations in extracted relation names.
    if intent == "policies":
        return any(word in relation for word in [
            "POLICY", "GOVERN", "FOLLOW", "REQUIRE"
        ])

    if intent == "assessments":
        return any(word in relation for word in [
            "ASSESS", "TEST", "EXAM", "MOCK",
            "EVALUAT", "HELD", "CONDUCT"
        ])

    return False


# --------------------------------
# 6. GRAPH TRAVERSAL
# --------------------------------


def collect_relevant_edges(
    graph,
    entities,
    intent,
    max_hops
):
    visited = set(entities)
    frontier = set(entities)
    retrieved_edges = {}

    for _ in range(max_hops):
        next_frontier = set()

        for entity in frontier:

            for source, target, attributes in graph.out_edges(
                entity, data=True
            ):
                relation = attributes.get("relation", "RELATED_TO")

                if not is_relevant_relation(relation, intent):
                    continue

                key = (source, target, relation)
                retrieved_edges[key] = dict(attributes)

                if target not in visited:
                    next_frontier.add(target)

            for source, target, attributes in graph.in_edges(
                entity, data=True
            ):
                relation = attributes.get("relation", "RELATED_TO")

                if not is_relevant_relation(relation, intent):
                    continue

                key = (source, target, relation)
                retrieved_edges[key] = dict(attributes)

                if source not in visited:
                    next_frontier.add(source)

        visited.update(next_frontier)
        frontier = next_frontier

        if not frontier:
            break

    return retrieved_edges



# --------------------------------
# 8. MAIN GRAPH RETRIEVER
# --------------------------------

def find_assessment_entities(graph):

    entities = []

    for node, data in graph.nodes(data=True):

        entity_type = str(
            data.get("type", "")
        ).casefold()

        if entity_type in {"assessment", "exam", "test"}:
            entities.append(node)

    return entities


def retrieve_graph_context(
    query,
    max_hops=1,
    max_entities=10,
    max_relationships=30
):

    graph = load_graph()

    intent = detect_query_intent(query)

    print("\n===== GRAPH INTENT =====")
    print("Detected intent:", intent)

    matched_entities = find_matching_entities(
        query,
        graph
    )

    # Generic assessment questions need discovery
    # by entity type because they may mention no exact entity.
    if intent == "assessments" and not matched_entities:
        matched_entities = find_assessment_entities(graph)

    if not matched_entities:
        return "No matching entities found in Knowledge Graph."

    matched_entities = prioritize_entities(
        matched_entities,
        graph,
        intent
    )

    matched_entities = matched_entities[:max_entities]

    print("Matched entities:", matched_entities)

    retrieved_edges = collect_relevant_edges(
        graph,
        matched_entities,
        intent,
        max_hops
    )

    # --------------------------------
    # FORMAT CONTEXT
    # --------------------------------

    context_lines = [
        "KNOWLEDGE GRAPH CONTEXT",
        f"Question Intent: {intent}",
        "\nMatched entities:",
    ]

    for entity in matched_entities:

        entity_type = graph.nodes[entity].get(
            "type",
            "Unknown"
        )

        context_lines.append(
            f"- {entity} (Type: {entity_type})"
        )

    context_lines.append("\nRelevant Relationships:")

    
    sorted_edges = sorted(
        retrieved_edges.items(),
        key=lambda item: (
            item[0][2],
            item[0][0],
            item[0][1]
        )
    )

    for (source, target, relation), attributes in sorted_edges[
        :max_relationships
    ]:

        sources = attributes.get("sources", [])
        evidences = attributes.get("evidences", [])
        confidence = attributes.get("confidence")
        verified = attributes.get("evidence_verified", False)

        source_text = ", ".join(sources) if sources else "Unknown"

        context_lines.append(
            f"- {source} --[{relation}]--> {target}"
            f" [Source: {source_text}]"
        )

        if evidences:
            for evidence in evidences:
                context_lines.append(
                    f"  Evidence: {evidence}"
                )

        context_lines.append(
            f"  Evidence verified: {verified}"
        )

        if confidence is not None:
            context_lines.append(
                f"  Confidence score: {confidence}"
            )

    if not sorted_edges:
        context_lines.append(
            "- No relationships found for these entities."
        )

    print("Relevant relationships:", len(sorted_edges))

    return "\n".join(context_lines)
