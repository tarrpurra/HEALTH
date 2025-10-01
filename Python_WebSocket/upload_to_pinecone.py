import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import index
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def load_data(jsonl_file):
    """Load the extracted data from JSONL file."""
    data = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line.strip()))
    return data

def prepare_documents(data):
    """Prepare documents for Pinecone upload."""
    documents = []
    for qa in data:
        focus = qa.get('focus', '')
        source = qa.get('source', '')
        url = qa.get('url', '')
        question = qa.get('question', '')
        answer = qa.get('answer', '')
        qtype = qa.get('qtype', '')
        qid = qa.get('qid', '')
        document_id = qa.get('document_id', '')

        # Skip if answer is empty
        if not answer.strip():
            continue

        # Combine into a single text
        text = f"Focus: {focus}\nQuestion: {question}\nAnswer: {answer}"

        # Metadata
        metadata = {
            'source': source,
            'url': url,
            'focus': focus,
            'qtype': qtype,
            'qid': qid,
            'document_id': document_id,
            'text': text
        }

        documents.append({
            'id': qid or f"{document_id}_{qa.get('pid', '')}",
            'text': text,
            'metadata': metadata
        })

    return documents

def upload_to_pinecone(documents, namespace="medical_resources", embed_batch_size=32):
    """Upload documents to Pinecone with batched embedding."""
    # Load the Hugging Face embedding model
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    total_uploaded = 0
    for i in tqdm(range(0, len(documents), embed_batch_size), desc="Processing batches"):
        batch_docs = documents[i:i+embed_batch_size]
        texts = [doc['text'] for doc in batch_docs]

        # Generate embeddings in batch
        embeddings = model.encode(texts)

        vectors = []
        for j, doc in enumerate(batch_docs):
            vectors.append({
                'id': doc['id'],
                'values': embeddings[j].tolist(),
                'metadata': doc['metadata']
            })

        # Upsert the batch
        index.upsert(vectors=vectors, namespace=namespace)
        total_uploaded += len(vectors)
        print(f"Uploaded batch {i//embed_batch_size + 1} with {len(vectors)} vectors")

    print(f"Total uploaded: {total_uploaded} documents to namespace '{namespace}'")

if __name__ == "__main__":
    # Load from medical_qa.jsonl
    jsonl_file = os.path.join(os.path.dirname(__file__), 'medical_qa.jsonl')
    data = []
    if os.path.exists(jsonl_file):
        print("Loading data from medical_qa.jsonl...")
        data.extend(load_data(jsonl_file))
    else:
        print(f"Data file {jsonl_file} not found.")

    # Load from all_medical_data.json (extracted XML data)
    json_file = os.path.join(os.path.dirname(__file__), 'all_medical_data.json')
    if os.path.exists(json_file):
        print("Loading data from all_medical_data.json...")
        xml_data = load_data(json_file)  # This will fail since load_data is now for JSONL
        # Need to handle differently
        with open(json_file, 'r', encoding='utf-8') as f:
            xml_data = json.load(f)
        # Convert XML data to list of Q&A dicts
        for doc in xml_data:
            for qa in doc.get('qa_pairs', []):
                qa_entry = {
                    'focus': doc.get('focus', ''),
                    'source': doc.get('source', ''),
                    'url': doc.get('url', ''),
                    'question': qa.get('question', ''),
                    'answer': qa.get('answer', ''),
                    'qtype': qa.get('qtype', ''),
                    'qid': qa.get('qid', ''),
                    'document_id': doc.get('document_id', ''),
                    'pid': qa.get('pid', '')
                }
                data.append(qa_entry)
    else:
        print(f"Data file {json_file} not found. Run extract_data.py first.")

    if not data:
        print("No data found to upload.")
        sys.exit(1)

    print("Preparing documents...")
    documents = prepare_documents(data)

    print(f"Prepared {len(documents)} documents")

    print("Uploading to Pinecone...")
    upload_to_pinecone(documents)
