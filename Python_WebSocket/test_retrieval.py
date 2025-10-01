import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from rag import retrieve_mental_health_resources

def test_retrieval():
    """Test the retrieval functionality with sample queries."""

    test_queries = [
        "What are the symptoms of depression?",
        "How to manage anxiety?",
        "Information about diabetes",
        "Mental health resources for stress",
        "What is hypertension?"
    ]

    print("Testing Pinecone retrieval functionality...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: Query - '{query}'")
        print("-" * 50)

        try:
            result = retrieve_mental_health_resources(query)
            print(f"Result:\n{result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_retrieval()