# regression_detector.py - Detect regressions by comparing test runs
import json
import os
from datetime import datetime

class RegressionDetector:
    """Detect regressions by comparing current and historical test results"""
    
    def __init__(self, history_dir="test_history"):
        self.history_dir = history_dir
    
    def detect_regressions(self, current_results, comparison_runs=3):
        """
        Detect regressions by comparing current results with history
        
        Args:
            current_results: Current test execution results
            comparison_runs: Number of previous runs to compare against
            
        Returns:
            Regression analysis results
        """
        print("=" * 80)
        print(" REGRESSION DETECTION ENGINE")
        print("=" * 80)
        
        # Load historical runs
        historical_runs = self._load_historical_runs(comparison_runs)
        
        if not historical_runs:
            print("\n No historical data found. This is the first run.")
            print("   Baseline established for future regression detection.")
            return {
                'regressions_found': False,
                'is_baseline': True,
                'regressions': [],
                'improvements': [],
                'message': 'Baseline run - no regressions detected'
            }
        
        print(f"\n Comparing against {len(historical_runs)} previous run(s)...")
        
        # Analyze current results
        regressions = []
        improvements = []
        
        for test_result in current_results:
            test_id = test_result['test_id']
            current_status = test_result['status']
            
            # Check historical performance
            historical_data = self._get_test_history(test_id, historical_runs)
            
            if historical_data:
                historical_pass_rate = historical_data['pass_rate']
                historical_runs_count = historical_data['runs']
                
                # Regression: Test failing now but passed historically
                if current_status == 'FAIL' and historical_pass_rate >= 70:
                    severity = self._calculate_severity(
                        test_result['priority'],
                        historical_pass_rate
                    )
                    
                    regression = {
                        'test_id': test_id,
                        'test_name': test_result['test_name'],
                        'priority': test_result['priority'],
                        'current_status': 'FAIL',
                        'historical_pass_rate': historical_pass_rate,
                        'historical_runs': historical_runs_count,
                        'severity': severity,
                        'failure_reason': test_result.get('failure_reason', 'Unknown'),
                        'detected_at': datetime.now().isoformat()
                    }
                    
                    regressions.append(regression)
                
                # Improvement: Test passing now but failed historically
                elif current_status == 'PASS' and historical_pass_rate < 70:
                    improvement = {
                        'test_id': test_id,
                        'test_name': test_result['test_name'],
                        'previous_pass_rate': historical_pass_rate,
                        'now_passing': True
                    }
                    improvements.append(improvement)
        
        # Display results
        self._display_regression_results(regressions, improvements)
        
        # Save regression report
        self._save_regression_report(regressions, improvements, current_results)
        
        return {
            'regressions_found': len(regressions) > 0,
            'regression_count': len(regressions),
            'critical_regressions': sum(1 for r in regressions if r['severity'] == 'CRITICAL'),
            'regressions': regressions,
            'improvements': improvements,
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_historical_runs(self, limit):
        """Load previous test runs from history"""
        
        if not os.path.exists(self.history_dir):
            return []
        
        # Get all run files
        run_files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
        run_files.sort(reverse=True)  # Most recent first
        
        historical_runs = []
        
        for filename in run_files[:limit]:
            filepath = os.path.join(self.history_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historical_runs.append({
                        'filename': filename,
                        'results': data
                    })
            except:
                continue
        
        return historical_runs
    
    def _get_test_history(self, test_id, historical_runs):
        """Get historical performance for a specific test"""
        
        total_runs = 0
        passed_runs = 0
        
        for run in historical_runs:
            for result in run['results']:
                if result['test_id'] == test_id:
                    total_runs += 1
                    if result['status'] == 'PASS':
                        passed_runs += 1
        
        if total_runs == 0:
            return None
        
        return {
            'runs': total_runs,
            'passed': passed_runs,
            'pass_rate': round((passed_runs / total_runs) * 100, 1)
        }
    
    def _calculate_severity(self, priority, historical_pass_rate):
        """Calculate regression severity"""
        
        # Critical if high priority test that always passed before
        if priority in ['Critical', 'High'] and historical_pass_rate >= 90:
            return 'CRITICAL'
        
        # Major if high priority or very stable test
        elif priority in ['Critical', 'High'] or historical_pass_rate >= 80:
            return 'MAJOR'
        
        # Minor otherwise
        else:
            return 'MINOR'
    
    def _display_regression_results(self, regressions, improvements):
        """Display regression analysis results"""
        
        print("\n" + "=" * 80)
        print(" REGRESSION ANALYSIS RESULTS")
        print("=" * 80)
        
        if regressions:
            print(f"\n {len(regressions)} REGRESSION(S) DETECTED:\n")
            
            # Sort by severity
            critical = [r for r in regressions if r['severity'] == 'CRITICAL']
            major = [r for r in regressions if r['severity'] == 'MAJOR']
            minor = [r for r in regressions if r['severity'] == 'MINOR']
            
            if critical:
                print(f"   CRITICAL ({len(critical)}):")
                for r in critical:
                    print(f"     {r['test_id']}: {r['test_name'][:60]}")
                    print(f"     Historical Pass Rate: {r['historical_pass_rate']}% → Now FAILING")
                    print(f"     Reason: {r['failure_reason']}")
                    print()
            
            if major:
                print(f"   MAJOR ({len(major)}):")
                for r in major:
                    print(f"     {r['test_id']}: {r['test_name'][:60]}")
                    print(f"     Historical Pass Rate: {r['historical_pass_rate']}%")
                    print()
            
            if minor:
                print(f"   MINOR ({len(minor)}):")
                for r in minor:
                    print(f"     {r['test_id']}: {r['test_name'][:60]}")
                    print()
        else:
            print("\n NO REGRESSIONS DETECTED")
            print("   All tests performing as expected compared to baseline.")
        
        if improvements:
            print(f"\n {len(improvements)} IMPROVEMENT(S) DETECTED:")
            for imp in improvements:
                print(f"   {imp['test_id']}: Now passing (was {imp['previous_pass_rate']}%)")
    
    def _save_regression_report(self, regressions, improvements, current_results):
        """Save regression report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(current_results),
            'regressions': regressions,
            'improvements': improvements,
            'summary': {
                'critical_regressions': sum(1 for r in regressions if r['severity'] == 'CRITICAL'),
                'major_regressions': sum(1 for r in regressions if r['severity'] == 'MAJOR'),
                'minor_regressions': sum(1 for r in regressions if r['severity'] == 'MINOR'),
                'improvements': len(improvements)
            }
        }
        
        os.makedirs("regression_reports", exist_ok=True)
        filepath = f"regression_reports/regression_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n Regression report saved to: {filepath}")


# Demo/Test
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" REGRESSION DETECTOR - DEMO")
    print("=" * 80)
    
    # Simulate current test results
    current_results = [
        {'test_id': 'TC_001', 'test_name': 'User login valid', 'status': 'PASS', 'priority': 'Critical'},
        {'test_id': 'TC_002', 'test_name': 'Login invalid password', 'status': 'FAIL', 'priority': 'High', 'failure_reason': 'Assertion failed'},
        {'test_id': 'TC_003', 'test_name': 'API endpoint test', 'status': 'PASS', 'priority': 'High'},
        {'test_id': 'TC_004', 'test_name': 'Database constraint', 'status': 'FAIL', 'priority': 'Critical', 'failure_reason': 'Timeout exceeded'},
        {'test_id': 'TC_005', 'test_name': 'UI responsive', 'status': 'PASS', 'priority': 'Medium'}
    ]
    
    # Run regression detection
    detector = RegressionDetector()
    results = detector.detect_regressions(current_results)
    
    print("\n" + "=" * 80)
    print(" Regression detection complete!")
    print("=" * 80)