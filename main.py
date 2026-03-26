# main.py - Complete AI Tester Demo (for submission video)
"""
AI-Agent Driven Release Testing System
Demonstrates: Chunking → Upload → Query → LLM → Test Generation
"""

from preprocessing import load_documents, preprocess_text, chunk_documents, store_in_vector_db
from ado_client import AzureDevOpsClient
from test_generator import generate_test_cases, save_test_cases, generate_test_report
from test_executor import TestExecutor
from regression_detector import RegressionDetector
from datetime import datetime
import os

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    """Complete end-to-end demonstration"""
    
    print_section("🚀 AI-AGENT DRIVEN RELEASE TESTING SYSTEM")
    print("\n📋 Features:")
    print("   ✅ Document chunking and preprocessing")
    print("   ✅ Vector database storage")
    print("   ✅ RAG-based test generation")
    print("   ✅ LLM integration")
    print("   ✅ Azure DevOps integration")
    print("   ✅ Automated test execution")
    print("   ✅ Regression detection")
    
    input("\nPress Enter to start...")
    
    # ========== PHASE 1: PREPROCESSING ==========
    print_section("PHASE 1: PREPROCESSING & CHUNKING")
    
    print("\n📂 Loading test knowledge base...")
    documents = load_documents('knowledge_base')
    print(f"   Loaded {len(documents)} documents")
    
    print("\n✂️  Chunking documents...")
    chunks = chunk_documents(documents)
    total_chunks = sum(len(c) for c in chunks.values())
    print(f"   Created {total_chunks} chunks")
    
    print("\n💾 Storing in vector database...")
    store_in_vector_db(chunks)
    print("   Vector database ready")
    
    input("\nPress Enter to continue...")
    
    # ========== PHASE 2: FETCH USER STORIES ==========
    print_section("PHASE 2: FETCHING USER STORIES")
    
    print("\n🔗 Connecting to Azure DevOps...")
    ado_client = AzureDevOpsClient(use_mock=True)
    user_stories = ado_client.fetch_user_stories(max_stories=2)
    
    print(f"\n✅ Fetched {len(user_stories)} user stories:")
    for story in user_stories:
        print(f"\n   📌 {story['id']}: {story['title']}")
        print(f"      Priority: {story['priority']}")
    
    input("\nPress Enter to continue...")
    
    # ========== PHASE 3: TEST GENERATION WITH LLM ==========
    print_section("PHASE 3: TEST GENERATION (RAG + LLM)")
    
    all_test_cases = []
    
    for story in user_stories:
        print(f"\n🎯 Processing: {story['id']}")
        print(f"   Story: {story['title']}")
        
        # Generate test cases using RAG + LLM
        test_cases = generate_test_cases(
            user_story=story['description'],
            max_cases=5
        )
        
        for tc in test_cases:
            tc['user_story_id'] = story['id']
        
        all_test_cases.extend(test_cases)
        print(f"   ✅ Generated {len(test_cases)} test cases")
    
    print(f"\n📊 TOTAL: {len(all_test_cases)} test cases generated")
    
    # Save test cases
    save_test_cases(all_test_cases, "demo_tests.json")
    
    input("\nPress Enter to continue...")
    
    # ========== PHASE 4: TEST EXECUTION ==========
    print_section("PHASE 4: AUTOMATED TEST EXECUTION")
    
    executor = TestExecutor()
    run_name = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    execution_results = executor.execute_test_cases(all_test_cases, run_name)
    
    print(f"\n📊 Execution Results:")
    print(f"   Total: {execution_results['total']}")
    print(f"   Passed: {execution_results['passed']} ✅")
    print(f"   Failed: {execution_results['failed']} ❌")
    print(f"   Pass Rate: {execution_results['pass_rate']}%")
    
    input("\nPress Enter to continue...")
    
    # ========== PHASE 5: REGRESSION DETECTION ==========
    print_section("PHASE 5: REGRESSION DETECTION")
    
    detector = RegressionDetector()
    regression_results = detector.detect_regressions(
        execution_results['results'],
        comparison_runs=3
    )
    
    if regression_results['regressions_found']:
        print(f"\n⚠️  ALERT: {regression_results['regression_count']} regression(s) detected")
    else:
        if regression_results.get('is_baseline'):
            print("\n✅ Baseline established")
        else:
            print("\n✅ No regressions detected")
    
    input("\nPress Enter to continue...")
    
    # ========== PHASE 6: REPORT GENERATION ==========
    print_section("PHASE 6: GENERATING REPORTS")
    
    print("\n📊 Creating comprehensive reports...")
    report_path = generate_test_report(all_test_cases)
    
    # ========== SUMMARY ==========
    print_section("🎉 DEMONSTRATION COMPLETE")
    
    print("\n📊 SUMMARY:")
    print(f"   Knowledge Base Documents: {len(documents)}")
    print(f"   Total Chunks Created: {total_chunks}")
    print(f"   User Stories Processed: {len(user_stories)}")
    print(f"   Test Cases Generated: {len(all_test_cases)}")
    print(f"   Tests Executed: {execution_results['total']}")
    print(f"   Pass Rate: {execution_results['pass_rate']}%")
    print(f"   Regressions: {regression_results.get('regression_count', 0)}")
    
    print("\n📁 Generated Files:")
    print(f"   • Test cases: test_output/demo_tests.json")
    print(f"   • HTML report: {report_path}")
    print(f"   • Execution: test_history/{run_name}.json")
    
    print("\n" + "=" * 80)
    print("✅ SYSTEM READY FOR HACKATHON SUBMISSION!")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()