
from rag.graph_store import load_graph

graph = load_graph()

print("\n========== JEE / COURSE ENTITIES ==========")

for node, data in graph.nodes(data=True):
    if any(word in node.casefold() for word in ["jee", "neet", "program", "course"]):
        print(f"\nENTITY: {node} | TYPE: {data.get('type')}")

        for source, target, edge in graph.in_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")

        for source, target, edge in graph.out_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")


print("\n========== ASSESSMENT ENTITIES ==========")

for node, data in graph.nodes(data=True):
    if any(word in node.casefold() for word in ["test", "exam", "assessment", "evaluation", "mock"]):
        print(f"\nENTITY: {node} | TYPE: {data.get('type')}")

        for source, target, edge in graph.in_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")

        for source, target, edge in graph.out_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")


print("\n========== POLICY ENTITIES ==========")

for node, data in graph.nodes(data=True):
    if any(word in node.casefold() for word in ["policy", "attendance", "refund", "scholarship", "discipline", "conduct", "emi"]):
        print(f"\nENTITY: {node} | TYPE: {data.get('type')}")

        for source, target, edge in graph.in_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")

        for source, target, edge in graph.out_edges(node, data=True):
            print(f"  {source} --[{edge.get('relation')}]--> {target}")
