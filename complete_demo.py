# complete_demo.py - End-to-End Demo of AI Tester Agent
"""
Complete demonstration of AI-Agent Driven Release Testing System
Shows all features: ADO integration, RAG test generation, execution, regression detection
"""

from ado_client import AzureDevOpsClient
from test_generator import generate_test_cases, save_test_cases, generate_test_report
from test_executor import TestExecutor
from regression_detector import RegressionDetector
from datetime import datetime
import os

def print_banner(text, char="="):
    """Print formatted banner"""
    print("\n" + char * 80)
    print(text.center(80))
    print(char * 80)

def run_complete_demo():
    """Run complete end-to-end demonstration"""
    
    print_banner(" AI-AGENT DRIVEN RELEASE TESTING SYSTEM", "=")
    print_banner("Complete End-to-End Demonstration", "-")
    
    print("\n System Components:")
    print("    Azure DevOps Integration")
    print("    RAG-based Test Generation")
    print("    Automated Test Execution")
    print("    Regression Detection")
    print("    Comprehensive Reporting")
    
    input("\nPress Enter to start demonstration...")
    
    # ==================== PHASE 1: FETCH USER STORIES ====================
    print_banner("PHASE 1: FETCHING USER STORIES FROM AZURE DEVOPS", "=")
    
    ado_client = AzureDevOpsClient(use_mock=True)
    user_stories = ado_client.fetch_user_stories(max_stories=3)
    
    print(f"\n Successfully fetched {len(user_stories)} user stories:\n")
    for story in user_stories:
        print(f"   {story['id']}: {story['title']}")
        print(f"     Priority: {story['priority']} | Status: {story['status']}")
    
    input("\nPress Enter to continue to test generation...")
    
    # ==================== PHASE 2: GENERATE TEST CASES ====================
    print_banner("PHASE 2: GENERATING TEST CASES USING RAG", "=")
    
    all_test_cases = []
    
    for story in user_stories:
        print(f"\n Processing: {story['id']} - {story['title']}")
        print("-" * 80)
        
        # Generate test cases using RAG
        test_cases = generate_test_cases(
            user_story=story['description'],
            max_cases=5
        )
        
        # Add story metadata
        for tc in test_cases:
            tc['user_story_id'] = story['id']
            tc['user_story_title'] = story['title']
        
        all_test_cases.extend(test_cases)
        
        print(f"    Generated {len(test_cases)} test cases for this story")
    
    print(f"\n TOTAL TEST CASES GENERATED: {len(all_test_cases)}")
    
    # Save generated tests
    save_test_cases(all_test_cases, filename=f"generated_tests_demo.json")
    
    input("\nPress Enter to continue to test execution...")
    
    # ==================== PHASE 3: EXECUTE TEST CASES ====================
    print_banner("PHASE 3: EXECUTING TEST CASES", "=")
    
    executor = TestExecutor()
    run_name = f"demo_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    execution_results = executor.execute_test_cases(all_test_cases, run_name=run_name)
    
    print(f"\n Execution Summary:")
    print(f"   Total Tests: {execution_results['total']}")
    print(f"   Passed: {execution_results['passed']} ")
    print(f"   Failed: {execution_results['failed']} ")
    print(f"   Pass Rate: {execution_results['pass_rate']}%")
    
    input("\nPress Enter to continue to regression detection...")
    
    # ==================== PHASE 4: DETECT REGRESSIONS ====================
    print_banner("PHASE 4: REGRESSION DETECTION", "=")
    
    detector = RegressionDetector()
    regression_results = detector.detect_regressions(
        execution_results['results'],
        comparison_runs=3
    )
    
    if regression_results['regressions_found']:
        print(f"\n ALERT: {regression_results['regression_count']} regression(s) detected!")
        if regression_results['critical_regressions'] > 0:
            print(f"  {regression_results['critical_regressions']} CRITICAL regression(s)!")
    else:
        if regression_results.get('is_baseline'):
            print("\n Baseline run established for future comparisons")
        else:
            print("\n No regressions detected - all tests performing as expected")
    
    input("\nPress Enter to continue to report generation...")
    
    # ==================== PHASE 5: GENERATE REPORTS ====================
    print_banner("PHASE 5: GENERATING COMPREHENSIVE REPORTS", "=")
    
    print("\n Generating reports...")
    
    # Generate test report
    report_path = generate_test_report(all_test_cases)
    print(f" Test cases report: {report_path}")
    
    # Generate execution summary
    summary_path = generate_execution_summary(execution_results, regression_results)
    print(f" Execution summary: {summary_path}")
    
    # ==================== FINAL SUMMARY ====================
    print_banner(" DEMONSTRATION COMPLETE!", "=")
    
    print("\n COMPLETE SYSTEM SUMMARY:")
    print(f"   User Stories Processed: {len(user_stories)}")
    print(f"   Test Cases Generated: {len(all_test_cases)}")
    print(f"   Tests Executed: {execution_results['total']}")
    print(f"   Pass Rate: {execution_results['pass_rate']}%")
    print(f"   Regressions Detected: {regression_results.get('regression_count', 0)}")
    
    print("\n Generated Files:")
    print(f"   • Test cases: test_output/generated_tests_demo.json")
    print(f"   • Test report: {report_path}")
    print(f"   • Execution results: test_history/{run_name}.json")
    print(f"   • Execution summary: {summary_path}")
    
    if os.path.exists("regression_reports") and os.listdir("regression_reports"):
        latest_regression = sorted(os.listdir("regression_reports"))[-1]
        print(f"   • Regression report: regression_reports/{latest_regression}")
    
    print("\n" + "=" * 80)
    print(" All features demonstrated successfully!")
    print(" System ready for hackathon submission!")
    print("=" * 80)
    
    print("\n Next Steps:")
    print("   1. Review generated reports in your browser")
    print("   2. Run this demo again to see regression detection in action")
    print("   3. Prepare demo video showing this flow")
    print("   4. Document the system architecture")
    
    print("\n HACKATHON REQUIREMENTS MET:")
    print("    Ingests user stories from Azure DevOps")
    print("    Automatically generates test scenarios using RAG")
    print("    Executes test scenarios")
    print("    Learns from past test results (historical comparison)")
    print("    Detects regressions")
    print("    Produces comprehensive test reports with evidence")
    
    print("\n" + "=" * 80)
    print()

def generate_execution_summary(execution_results, regression_results):
    """Generate HTML summary of execution and regressions"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    regression_html = ""
    if regression_results.get('regressions'):
        regression_html = "<h2>🚨 Regressions Detected</h2><ul>"
        for reg in regression_results['regressions']:
            regression_html += f"""
            <li>
                <strong>{reg['test_id']}</strong>: {reg['test_name']}<br>
                Severity: <span style="color: red;">{reg['severity']}</span><br>
                Historical Pass Rate: {reg['historical_pass_rate']}%<br>
                Reason: {reg['failure_reason']}
            </li>
            """
        regression_html += "</ul>"
    else:
        regression_html = "<h2> No Regressions Detected</h2><p>All tests performing as expected.</p>"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Summary</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .header {{ background: #2563eb; color: white; padding: 30px; border-radius: 10px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric .value {{ font-size: 36px; font-weight: bold; }}
        .metric .label {{ color: #666; }}
        .pass {{ color: #10b981; }}
        .fail {{ color: #ef4444; }}
    </style>
</head>
<body>
    <div class="header">
        <h1> Test Execution Summary</h1>
        <p>{timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>Execution Results</h2>
        <div class="metric">
            <div class="value">{execution_results['total']}</div>
            <div class="label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="value pass">{execution_results['passed']}</div>
            <div class="label">Passed</div>
        </div>
        <div class="metric">
            <div class="value fail">{execution_results['failed']}</div>
            <div class="label">Failed</div>
        </div>
        <div class="metric">
            <div class="value">{execution_results['pass_rate']}%</div>
            <div class="label">Pass Rate</div>
        </div>
    </div>
    
    <div class="summary">
        {regression_html}
    </div>
</body>
</html>
"""
    
    os.makedirs("test_output", exist_ok=True)
    filepath = f"test_output/execution_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filepath


if __name__ == "__main__":
    run_complete_demo()