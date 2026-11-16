
import json

from llm.gemini_client import client, MODEL_NAME
from rag.graph_store import (
    add_entity,
    add_relationship,
    save_graph
)


def extract_graph_from_text(text, source="unknown"):
    """
    Extract entities and relationships from source text.
    Only relationships with verifiable evidence are stored.
    """

    prompt = f"""
You are an information extraction system for an
academic institute's Knowledge Graph.

Extract entities and relationships ONLY from the
provided source text.

SOURCE DOCUMENT:
{source}

SOURCE TEXT:
{text}

Rules:
1. Never invent entities or relationships.
2. Extract only explicitly mentioned information.
3. Preserve original entity names.
4. Identify entity types such as:
   Institute, Subject, Course, Batch, Class,
   Exam, Topic, Faculty, Platform, Policy,
   Assessment, StudyMaterial, Schedule.
5. Extract relationships such as:
   OFFERS, TEACHES, COVERS, PREPARES_FOR,
   HAS_SUBJECT, HELD_ON, STARTS_AT,
   PROVIDES, AVAILABLE_ON.
6. Do not create duplicate entities.
7. Every relationship must reference entities
   present in the entities list.
8. Return valid JSON only. No Markdown.
9. Every relationship MUST include an evidence field.
10. Evidence must be an exact, continuous quotation
    from SOURCE TEXT.
11. Never paraphrase or invent evidence.
12. If no exact supporting sentence exists,
    do not extract that relationship.

Required JSON format:

{{
    "entities": [
        {{
            "name": "Physics",
            "type": "Subject"
        }}
    ],
    "relationships": [
        {{
            "source": "Class 11 Physics Batch",
            "target": "Physics",
            "relation": "HAS_SUBJECT",
            "evidence": "Exact sentence copied from the source text."
        }}
    ]
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        response_text = response.text.strip()

        # Remove Markdown code fences if Gemini adds them
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        extracted_data = json.loads(response_text)

        entities = extracted_data.get("entities", [])
        relationships = extracted_data.get("relationships", [])

        # Validate entity names
        valid_entities = {
            entity["name"].strip()
            for entity in entities
            if isinstance(entity, dict)
            and entity.get("name")
            and entity.get("type")
        }

        # Add entities to NetworkX
        for entity in entities:

            if not isinstance(entity, dict):
                continue

            name = str(entity.get("name", "")).strip()
            entity_type = str(entity.get("type", "")).strip()

            if name and entity_type:
                add_entity(name, entity_type)

        # Add only relationships with verifiable source evidence
        verified_relationships = 0
        rejected_relationships = 0

        for relationship in relationships:

            if not isinstance(relationship, dict):
                rejected_relationships += 1
                continue

            source_entity = str(
                relationship.get("source", "")
            ).strip()

            target_entity = str(
                relationship.get("target", "")
            ).strip()

            relation = str(
                relationship.get("relation", "")
            ).strip()

            evidence = str(
                relationship.get("evidence", "")
            ).strip()

            # Validate entity references and evidence
            if (
                source_entity not in valid_entities
                or target_entity not in valid_entities
                or not relation
                or not evidence
            ):
                rejected_relationships += 1
                continue

            # Verify exact evidence against original source text
            if evidence.casefold() not in text.casefold():

                print(
                    f"Rejected unsupported relationship: "
                    f"{source_entity} --[{relation}]--> "
                    f"{target_entity}"
                )

                rejected_relationships += 1
                continue

            # Heuristic score for exact source evidence.
            # This is not a statistically calibrated probability.
            confidence = 0.90

            add_relationship(
                source_entity,
                target_entity,
                relation,
                source_document=source,
                evidence=evidence,
                confidence=confidence
            )

            verified_relationships += 1

        print(
            f"\nGraph extraction from: {source}"
        )

        print(
            f"Extracted entities: {len(valid_entities)}"
        )

        print(
            f"Proposed relationships: {len(relationships)}"
        )

        print(
            f"Verified relationships: {verified_relationships}"
        )

        print(
            f"Rejected relationships: {rejected_relationships}"
        )

        return extracted_data

    except json.JSONDecodeError as e:

        print(f"Invalid JSON returned by Gemini: {e}")

        return {
            "entities": [],
            "relationships": []
        }

    except Exception as e:

        print(f"Graph extraction failed: {e}")

        return {
            "entities": [],
            "relationships": []
        }


def build_graph_from_chunks(chunks, batch_size=5):
    """
    Build the knowledge graph while preserving
    individual chunk source information.

    batch_size is retained for compatibility.
    """

    total_chunks = len(chunks)

    print(f"Total chunks: {total_chunks}")

    for index, chunk in enumerate(chunks):

        if isinstance(chunk, dict):

            text = chunk.get("text", "")
            source = chunk.get("source", "unknown")

        else:

            text = str(chunk)
            source = "unknown"

        if not text.strip():
            continue

        print(
            f"\nProcessing chunk {index + 1}/{total_chunks}"
        )

        extract_graph_from_text(
            text=text,
            source=source
        )

        # Save after every chunk
        save_graph()

    print("\nKnowledge Graph construction completed!")
