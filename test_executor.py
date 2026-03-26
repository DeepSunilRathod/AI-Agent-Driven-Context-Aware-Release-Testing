# test_executor.py - Execute generated tests and track results
import json
import os
import random
from datetime import datetime

class TestExecutor:
    """Execute test cases and track results"""
    
    def __init__(self):
        self.history_dir = "test_history"
        os.makedirs(self.history_dir, exist_ok=True)
    
    def execute_test_cases(self, test_cases, run_name=None):
        """
        Simulate test execution
        
        Args:
            test_cases: List of test case dictionaries
            run_name: Optional name for this test run
            
        Returns:
            Execution results
        """
        if not run_name:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("=" * 80)
        print(" TEST EXECUTION ENGINE")
        print("=" * 80)
        print(f"\nRun Name: {run_name}")
        print(f"Total Tests: {len(test_cases)}\n")
        
        results = []
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Executing [{i}/{len(test_cases)}]: {test_case['id']} - {test_case['name'][:50]}...")
            
            # Simulate test execution (random pass/fail based on priority)
            execution_result = self._simulate_execution(test_case)
            
            if execution_result['status'] == 'PASS':
                passed += 1
                print(f"  PASS")
            else:
                failed += 1
                print(f" FAIL - {execution_result['failure_reason']}")
            
            results.append(execution_result)
        
        # Summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(test_cases)}")
        print(f"Passed: {passed} ")
        print(f"Failed: {failed} ")
        print(f"Pass Rate: {round(passed/len(test_cases)*100, 1)}%")
        
        # Save results
        self._save_results(run_name, results)
        
        return {
            'run_name': run_name,
            'timestamp': datetime.now().isoformat(),
            'total': len(test_cases),
            'passed': passed,
            'failed': failed,
            'pass_rate': round(passed/len(test_cases)*100, 1),
            'results': results
        }
    
    def _simulate_execution(self, test_case):
        """Simulate test execution with realistic pass/fail rates"""
        
        # Base pass probability on priority
        priority = test_case.get('priority', 'Medium')
        
        if priority in ['High', 'Critical']:
            pass_probability = 0.85  # 85% pass rate for critical tests
        elif priority == 'Medium':
            pass_probability = 0.75  # 75% pass rate for medium
        else:
            pass_probability = 0.90  # 90% pass rate for low priority
        
        # Simulate execution
        passed = random.random() < pass_probability
        
        result = {
            'test_id': test_case['id'],
            'test_name': test_case['name'],
            'priority': priority,
            'test_type': test_case.get('test_type', 'Functional'),
            'status': 'PASS' if passed else 'FAIL',
            'execution_time_ms': random.randint(100, 2000),
            'timestamp': datetime.now().isoformat(),
            'source_pattern': test_case.get('source_pattern', 'Unknown')
        }
        
        if not passed:
            # Generate realistic failure reasons
            failure_reasons = [
                "Assertion failed: Expected value did not match actual",
                "Timeout: Operation exceeded 30 second limit",
                "Element not found: Locator returned no results",
                "Connection error: Unable to reach API endpoint",
                "Validation error: Required field missing in response",
                "Database error: Constraint violation detected"
            ]
            result['failure_reason'] = random.choice(failure_reasons)
            result['failure_details'] = f"Test failed at step {random.randint(1, 5)}"
        
        return result
    
    def _save_results(self, run_name, results):
        """Save test results to history"""
        
        filepath = os.path.join(self.history_dir, f"{run_name}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n Results saved to: {filepath}")
    
    def get_all_runs(self):
        """Get list of all test runs"""
        runs = []
        
        if os.path.exists(self.history_dir):
            for filename in os.listdir(self.history_dir):
                if filename.endswith('.json'):
                    runs.append(filename.replace('.json', ''))
        
        return sorted(runs, reverse=True)  # Most recent first
    
    def load_run_results(self, run_name):
        """Load results from a specific run"""
        filepath = os.path.join(self.history_dir, f"{run_name}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


# Demo/Test
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" TEST EXECUTOR - DEMO")
    print("=" * 80)
    
    # Create sample test cases
    sample_tests = [
        {
            'id': 'TC_001',
            'name': 'User login with valid credentials',
            'priority': 'Critical',
            'test_type': 'Functional'
        },
        {
            'id': 'TC_002',
            'name': 'Login with invalid password',
            'priority': 'High',
            'test_type': 'Negative'
        },
        {
            'id': 'TC_003',
            'name': 'API endpoint returns correct data',
            'priority': 'High',
            'test_type': 'API'
        },
        {
            'id': 'TC_004',
            'name': 'Database constraint validation',
            'priority': 'Medium',
            'test_type': 'Database'
        },
        {
            'id': 'TC_005',
            'name': 'UI responsive on mobile',
            'priority': 'Low',
            'test_type': 'UI'
        }
    ]
    
    # Execute tests
    executor = TestExecutor()
    results = executor.execute_test_cases(sample_tests, run_name="demo_run")
    
    print("\n" + "=" * 80)
    print(" Test execution complete!")
    print("=" * 80)