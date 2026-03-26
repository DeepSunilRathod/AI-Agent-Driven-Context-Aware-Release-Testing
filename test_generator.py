# test_generator.py - Generate test cases using RAG + LLM
import chromadb
import re
from datetime import datetime
from llm_client import LLMClient

def retrieve_relevant_patterns(user_story, category=None, n_results=5):
    """Retrieve relevant test patterns from knowledge base"""
    client = chromadb.PersistentClient(path="./vector_store")
    collection = client.get_collection(name="documents")
    
    search_query = f"{category} {user_story}" if category else user_story
    
    print(f"\n Searching knowledge base...")
    print(f"   Query: '{user_story[:60]}...'")
    
    results = collection.query(
        query_texts=[search_query],
        n_results=n_results
    )
    
    retrieved_patterns = []
    if results['documents'][0]:
        print(f"\n Found {len(results['documents'][0])} relevant test patterns\n")
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"   {i+1}. Source: {metadata['source']}")
            retrieved_patterns.append({
                'content': doc,
                'source': metadata['source'],
                'doc_id': metadata['doc_id']
            })
    
    return retrieved_patterns


def generate_test_cases(user_story, category=None, max_cases=10):
    """Generate test cases from user story using RAG + LLM"""
    
    print("=" * 80)
    print(" AI TEST CASE GENERATOR")
    print("=" * 80)
    print(f"\n User Story:\n{user_story}\n")
    
    # Initialize LLM client
    llm_client = LLMClient(provider="mock")
    
    # Retrieve relevant patterns
    patterns = retrieve_relevant_patterns(user_story, category, n_results=5)
    
    if not patterns:
        print(" No relevant patterns found.")
        return []
    
    # Prepare patterns for LLM
    patterns_text = "\n\n".join([p['content'][:500] for p in patterns])
    
    # Generate prompt
    try:
        prompt = llm_client.generate_prompt(
            "test_generation_prompt",
            user_story=user_story,
            retrieved_patterns=patterns_text
        )
        
        # Call LLM
        llm_response = llm_client.call_llm(prompt)
        
        # Save response
        llm_client.save_response(llm_response, f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    except Exception as e:
        print(f" LLM call failed: {e}")
    
    # Extract test cases from patterns (fallback)
    test_cases = []
    test_id_counter = 1
    
    print("=" * 80)
    print(" GENERATING TEST CASES")
    print("=" * 80)
    
    for pattern in patterns:
        content = pattern['content']
        test_blocks = content.split('Test ID:')
        
        for block in test_blocks[1:]:
            if test_id_counter > max_cases:
                break
                
            try:
                lines = block.strip().split('\n')
                original_id = lines[0].split('Description:')[0].strip()
                
                description = ""
                for line in lines:
                    if line.startswith('Description:'):
                        description = line.replace('Description:', '').strip()
                        break
                
                test_type = "Functional"
                for line in lines:
                    if 'Test Type:' in line:
                        test_type = line.split('Test Type:')[-1].strip()
                        break
                
                priority = "Medium"
                for line in lines:
                    if 'Priority:' in line:
                        priority = line.split('Priority:')[-1].strip()
                        break
                
                steps = []
                in_steps = False
                for line in lines:
                    if line.startswith('Steps:'):
                        in_steps = True
                        continue
                    if in_steps:
                        if line.startswith('Expected Result:') or line.startswith('Priority:'):
                            break
                        if line.strip():
                            steps.append(line.strip())
                
                expected = ""
                for line in lines:
                    if line.startswith('Expected Result:'):
                        expected = line.replace('Expected Result:', '').strip()
                        break
                
                test_case = {
                    'id': f'TC_{test_id_counter:03d}',
                    'original_id': original_id,
                    'name': description[:100] if description else f"Test case {test_id_counter}",
                    'description': description,
                    'test_type': test_type,
                    'priority': priority,
                    'steps': steps[:5],
                    'expected_result': expected,
                    'source_pattern': pattern['source'],
                    'generated_from': 'RAG',
                    'user_story': user_story[:100]
                }
                
                test_cases.append(test_case)
                test_id_counter += 1
                
            except:
                continue
    
    print(f"\n Generated {len(test_cases)} test cases\n")
    
    for tc in test_cases:
        print(f"  {tc['id']}: {tc['name']}")
        print(f"       Type: {tc['test_type']} | Priority: {tc['priority']}")
    
    return test_cases


def save_test_cases(test_cases, filename=None):
    """Save generated test cases to file"""
    import json
    import os
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_tests_{timestamp}.json"
    
    os.makedirs("test_output", exist_ok=True)
    filepath = os.path.join("test_output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    print(f" Test cases saved to: {filepath}")
    return filepath


def generate_test_report(test_cases):
    """Generate HTML report"""
    import os
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Generated Test Cases</title>
    <style>
        body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
        .header {{ background: #2563eb; color: white; padding: 30px; border-radius: 10px; }}
        .test-case {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #2563eb; }}
        .test-id {{ font-size: 18px; font-weight: bold; color: #2563eb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1> Generated Test Cases</h1>
        <p>{timestamp}</p>
        <p>Total: {len(test_cases)}</p>
    </div>
"""
    
    for tc in test_cases:
        html += f"""
    <div class="test-case">
        <div class="test-id">{tc['id']}: {tc['name']}</div>
        <p><strong>Type:</strong> {tc.get('test_type', 'N/A')} | <strong>Priority:</strong> {tc.get('priority', 'N/A')}</p>
        <p><strong>Expected Result:</strong> {tc.get('expected_result', 'N/A')}</p>
    </div>
"""
    
    html += "</body></html>"
    
    os.makedirs("test_output", exist_ok=True)
    filepath = f"test_output/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" HTML report: {filepath}")
    return filepath