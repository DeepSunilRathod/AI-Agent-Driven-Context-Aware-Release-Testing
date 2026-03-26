# query.py - Query vector database and generate test cases
import chromadb

def retrieve_relevant_chunks(query, n_results=3):
    """Retrieve most relevant chunks for a query"""
    
    # Connect to vector database
    client = chromadb.PersistentClient(path="./vector_store")
    collection = client.get_collection(name="documents")
    
    print(f" Query: '{query}'")
    print("=" * 70)
    
    # Search for relevant chunks
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # Display results
    print(f"\n Found {len(results['documents'][0])} relevant chunks:\n")
    
    retrieved_chunks = []
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f" Chunk {i+1}:")
        print(f" Source: {metadata['source']}")
        print(f" Doc ID: {metadata['doc_id']}")
        print(f" Chunk: {metadata['chunk_id'] + 1}/{metadata['chunk_total']}")
        print(f" Content: {doc[:150]}...")
        print()
        
        retrieved_chunks.append({
            'content': doc,
            'metadata': metadata
        })
    
    return retrieved_chunks


def generate_test_cases_from_chunks(chunks, query):
    """Generate test cases based on retrieved chunks"""
    
    print("=" * 70)
    print(" GENERATING TEST CASES")
    print("=" * 70)
    
    test_cases = []
    test_id_counter = 1
    
    for chunk in chunks:
        doc_id = chunk['metadata']['doc_id']
        content = chunk['content']
        
        # Extract facts from content
        sentences = content.split('.')
        
        for sentence in sentences[:3]:  # Use first 3 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only meaningful sentences
                
                test_case = {
                    'id': f"TC_{test_id_counter:03d}",
                    'name': f"Verify: {sentence[:60]}...",
                    'source_document': chunk['metadata']['source'],
                    'doc_id': doc_id,
                    'test_type': 'data_validation',
                    'priority': 'Medium',
                    'steps': [
                        f"1. Retrieve data about {doc_id}",
                        f"2. Validate: {sentence[:80]}",
                        "3. Assert data matches expected value"
                    ],
                    'expected_result': f"Data should confirm: {sentence}",
                    'source_chunk': chunk['metadata']['chunk_id']
                }
                
                test_cases.append(test_case)
                test_id_counter += 1
    
    # Display generated test cases
    print(f"\n Generated {len(test_cases)} test cases:\n")
    
    for tc in test_cases:
        print(f"  {tc['id']}: {tc['name']}")
        print(f"       Source: {tc['source_document']}")
        print(f"       Type: {tc['test_type']} | Priority: {tc['priority']}")
        print()
    
    return test_cases


# MAIN DEMO
if __name__ == "__main__":
    print("=" * 70)
    print(" RAG-BASED TEST CASE GENERATOR")
    print("=" * 70)
    print()
    
    # Example queries
    queries = [
        "Tell me about population statistics",
        "What are the capital cities?",
        "Information about economy and GDP"
    ]
    
    all_test_cases = []
    
    for query in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)
        
        # Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(query, n_results=2)
        
        # Generate test cases
        test_cases = generate_test_cases_from_chunks(chunks, query)
        all_test_cases.extend(test_cases)
        
        print("\n")
    
    # Final summary
    print("=" * 70)
    print(" FINAL SUMMARY")
    print("=" * 70)
    print(f"\n Total test cases generated: {len(all_test_cases)}")
    print(f" Based on chunked knowledge base")
    print(f" Using RAG (Retrieval Augmented Generation)")
    print("\n System ready for deployment!\n")