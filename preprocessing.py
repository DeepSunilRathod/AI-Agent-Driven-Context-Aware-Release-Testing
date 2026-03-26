# ingest.py - Preprocess and chunk documents, then store in vector database
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os
import re

print("=" * 70)
print(" DOCUMENT INGESTION PIPELINE")
print("=" * 70)

# STEP 1: PREPROCESSING
def preprocess_text(text):
    """Clean and normalize text before chunking"""
    print("   Preprocessing text...")
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\-\:\;\?]', '', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


# STEP 2: LOAD DOCUMENTS
def load_documents(directory):
    """Load all text files from directory"""
    print(f"\n Loading documents from: {directory}")
    
    documents = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Preprocess
                clean_content = preprocess_text(content)
                
                # Store with metadata
                documents.append({
                    'content': clean_content,
                    'source': filename,
                    'doc_id': filename.replace('.txt', '')
                })
                
                print(f"   Loaded: {filename} ({len(clean_content)} characters)")
    
    return documents


# STEP 3: CHUNK DOCUMENTS
def chunk_documents(documents):
    """Split documents into chunks using RecursiveCharacterTextSplitter"""
    print(f"\n  Chunking documents...")
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # Each chunk ~500 characters
        chunk_overlap=50,      # 50 character overlap between chunks
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    all_chunks = []
    
    for doc in documents:
        # Split into chunks
        chunks = text_splitter.split_text(doc['content'])
        
        print(f"   {doc['source']}: {len(chunks)} chunks created")
        
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'content': chunk,
                'source': doc['source'],
                'doc_id': doc['doc_id'],
                'chunk_id': i,
                'chunk_total': len(chunks)
            })
    
    return all_chunks


# STEP 4: STORE IN VECTOR DATABASE
def store_in_database(chunks):
    """Store chunks in ChromaDB with metadata"""
    print(f"\n Storing {len(chunks)} chunks in vector database...")
    
    # Connect to persistent ChromaDB
    client = chromadb.PersistentClient(path="./vector_store")
    
    # Delete old collection if exists
    try:
        client.delete_collection(name="documents")
        print("    Deleted old collection")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(name="documents")
    
    # Batch store chunks
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        collection.add(
            documents=[chunk['content'] for chunk in batch],
            ids=[f"{chunk['doc_id']}_chunk_{chunk['chunk_id']}" for chunk in batch],
            metadatas=[{
                'source': chunk['source'],
                'doc_id': chunk['doc_id'],
                'chunk_id': chunk['chunk_id'],
                'chunk_total': chunk['chunk_total']
            } for chunk in batch]
        )
    
    print(f"   Stored {len(chunks)} chunks successfully")
    print(f"   Database location: ./vector_store")


# MAIN PIPELINE
if __name__ == "__main__":
    # Load documents
    documents = load_documents('knowledge_base')
    
    # Chunk documents
    chunks = chunk_documents(documents)
    
    # Store in database
    store_in_database(chunks)
    
    # Summary
    print("\n" + "=" * 70)
    print(" INGESTION COMPLETE!")
    print("=" * 70)
    print(f"\n Summary:")
    print(f"   • Documents processed: {len(documents)}")
    print(f"   • Total chunks created: {len(chunks)}")
    print(f"   • Average chunks per document: {len(chunks)//len(documents)}")
    print(f"   • Storage location: ./vector_store")
    print("\n Ready for retrieval and test generation!")