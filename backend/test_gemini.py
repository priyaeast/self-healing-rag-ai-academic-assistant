from llm.gemini_client import client

try:
    print("Testing Gemini 2.5 Flash Lite...")

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Explain what RAG is in simple words."
    )

    print("\nGemini Response:")
    print(response.text)

except Exception as e:
    print("\nGemini Error:", e)