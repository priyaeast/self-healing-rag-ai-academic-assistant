
from rag.graph_retriever import retrieve_graph_context

tests = [
    {
        "question": "Who teaches Mechanics?",
        "expected": "Dr. Rajesh Sharma --[TEACHES]--> Mechanics"
    },
    {
        "question": "What topics does Physics cover?",
        "expected": "Physics --[COVERS]--> Mechanics"
    },
    {
        "question": "What study materials are available for Physics?",
        "expected": "Physics"
    },
    {
        "question": "Which subjects are included in JEE?",
        "expected": "JEE Programs"
    },
    {
        "question": "What assessments are conducted?",
        "expected": "Diagnostic Tests"
    },
    {
        "question": "What is the attendance policy?",
        "expected": "Attendance Policy"
    }
]

passed = 0

print("\n========== GRAPHRAG EVALUATION ==========")

for index, test in enumerate(tests, 1):

    print(f"\nTest {index}: {test['question']}")

    result = retrieve_graph_context(test["question"])

    success = test["expected"] in result

    if success:
        passed += 1
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
        print("Expected:", test["expected"])

print("\n========== FINAL RESULTS ==========")
print(f"Passed: {passed}/{len(tests)}")
print(f"Failed: {len(tests) - passed}/{len(tests)}")
print(f"Accuracy: {passed / len(tests) * 100:.2f}%")
