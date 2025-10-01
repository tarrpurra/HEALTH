import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import client, rag_tool, index, MODEL
from google.genai import types
import asyncio
from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def query_pinecone(query_text: str, top_k: int = 5):
    """Query Pinecone for relevant mental health resources."""
    try:
        # Generate embedding for the query
        query_embedding = embedding_model.encode(query_text).tolist()
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract and format results
        context = []
        for match in results.matches:
            metadata = match.metadata
            text = metadata.get('text', '')
            score = match.score
            context.append(f"[Relevance: {score:.2f}] {text}")
        
        return "\n\n".join(context) if context else "No relevant resources found."
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return "Error retrieving resources."

async def test_retrieval_and_reasoning():
    """Test the model's retrieval and reasoning capabilities with function calling."""
    query = "Where is bartholin's gland located and what is its function?"
    
    print("Testing RAG with Gemini + Pinecone...")
    print(f"Model: {MODEL}")
    print(f"Query: {query}")
    print("-" * 70)
    
    try:
        # Initial request
        messages = [
            types.Content(
                role="user",
                parts=[types.Part(text=f"Please answer this question using available health resources: {query}")]
            )
        ]
        
        # First API call - model may request function call
        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[rag_tool],
                temperature=0.7
            )
        )
        
        # Check if model wants to call a function
        function_calls = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "function_call"):
                    function_calls.append(part.function_call)
        
        if function_calls:
            print(f"✓ Model requested {len(function_calls)} function call(s)\n")
            
            # Add assistant's function call to conversation
            messages.append(response.candidates[0].content)
            
            # Execute function calls and prepare responses
            for fc in function_calls:
                print(f"Function called: {fc.name}")
                print(f"Arguments: {dict(fc.args)}\n")
                
                if fc.name == "medical-resources":
                    # Query Pinecone
                    query_arg = fc.args.get("query", query)
                    print(f"Querying Pinecone for: '{query_arg}'...")
                    rag_results = query_pinecone(query_arg)
                    print(f"Retrieved {len(rag_results.split('---'))} results\n")

                    # Add function response to conversation
                    function_response = types.Content(
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=fc.name,
                                    response={"result": rag_results}
                                )
                            )
                        ]
                    )
                    messages.append(function_response)
            
            # Second API call - model generates final answer using RAG results
            print("Generating final answer with retrieved context...\n")
            print("-" * 70)
            
            final_response = await client.aio.models.generate_content(
                model=MODEL,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[rag_tool],
                    temperature=0.7
                )
            )
            
            # Extract final answer
            final_text = ""
            for candidate in final_response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        final_text += part.text
            
            if final_text:
                print("Final Answer:")
                print(final_text)
            else:
                print("No final text generated.")
        else:
            # No function call - model answered directly
            print("✗ Model did not call the function (answered directly)\n")
            result_text = ""
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        result_text += part.text
            
            if result_text:
                print("Direct Answer:")
                print(result_text)
            else:
                print("No response text found.")
                print(f"\nFull response: {response}")
                
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_retrieval_and_reasoning())