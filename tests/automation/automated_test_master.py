#!/usr/bin/env python3
"""
AUTOMATED TEST EXECUTION MASTER CONTROLLER
Configures and runs the complete Lea Jane's Hot Chicken test suite
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class AutomatedTestExecutor:
    """Master controller for automated test execution"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'framework': {'passed': 0, 'failed': 0, 'total': 0, 'duration': 0},
            'business': {'passed': 0, 'failed': 0, 'total': 0, 'duration': 0},
            'integration': {'passed': 0, 'failed': 0, 'total': 0, 'duration': 0},
            'data': {'passed': 0, 'failed': 0, 'total': 0, 'duration': 0},
            'overall': {'passed': 0, 'failed': 0, 'total': 0, 'duration': 0}
        }
        self.reports = []
        
        # Test execution order (dependency-aware)
        self.test_execution_order = [
            ('framework', 'Simple Test Framework Validation'),
            ('data', 'Database Integrity Tests'),
            ('integration', 'XtraChef Integration Protection'),
            ('business', 'Recipe Costing Engine Tests')
        ]
    
    def run_framework_tests(self) -> Dict[str, Any]:
        """Run basic framework and database connectivity tests"""
        print("🏗️  RUNNING FRAMEWORK TESTS...")
        start_time = time.time()
        
        try:
            # Check database connectivity
            import sqlite3
            conn = sqlite3.connect('restaurant_calculator.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory")
            inventory_count = cursor.fetchone()[0]
            conn.close()
            
            if inventory_count >= 100:
                self.results['framework']['passed'] = 1
                self.results['framework']['total'] = 1
                print(f"✅ Framework test passed - {inventory_count} inventory items found")
            else:
                self.results['framework']['failed'] = 1
                self.results['framework']['total'] = 1
                print(f"❌ Framework test failed - only {inventory_count} inventory items")
            
        except Exception as e:
            self.results['framework']['failed'] = 1
            self.results['framework']['total'] = 1
            print(f"❌ Framework test failed - {str(e)}")
        
        self.results['framework']['duration'] = time.time() - start_time
        return self.results['framework']
    
    def run_data_integrity_tests(self) -> Dict[str, Any]:
        """Run database integrity tests"""
        print("🗄️  RUNNING DATABASE INTEGRITY TESTS...")
        start_time = time.time()
        
        try:
            # Run the schema-aware database integrity test
            result = subprocess.run([
                sys.executable, 'tests/data/schema_aware_integrity_test.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Parse output for test counts
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'TEST SUMMARY:' in line:
                        continue
                    elif 'Total:' in line and 'Passed:' in line and 'Failed:' in line:
                        # Extract numbers from output
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'Total:' and i+1 < len(parts):
                                self.results['data']['total'] = int(parts[i+1])
                            elif part == 'Passed:' and i+1 < len(parts):
                                self.results['data']['passed'] = int(parts[i+1])
                            elif part == 'Failed:' and i+1 < len(parts):
                                self.results['data']['failed'] = int(parts[i+1])
                        break
                
                print(f"✅ Database integrity tests completed")
            else:
                self.results['data']['failed'] = 1
                self.results['data']['total'] = 1
                print(f"❌ Database integrity tests failed")
            
        except Exception as e:
            self.results['data']['failed'] = 1
            self.results['data']['total'] = 1
            print(f"❌ Database integrity test execution failed: {str(e)}")
        
        self.results['data']['duration'] = time.time() - start_time
        return self.results['data']
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run XtraChef integration protection tests"""
        print("🔒 RUNNING XTRACHEF INTEGRATION TESTS...")
        start_time = time.time()
        
        try:
            # Run the XtraChef integration test
            result = subprocess.run([
                sys.executable, 'tests/integration/simple_xtrachef_test.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Parse output for test counts
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'PROTECTION TEST SUMMARY:' in line:
                        continue
                    elif 'Total:' in line and 'Passed:' in line and 'Failed:' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'Total:' and i+1 < len(parts):
                                self.results['integration']['total'] = int(parts[i+1])
                            elif part == 'Passed:' and i+1 < len(parts):
                                self.results['integration']['passed'] = int(parts[i+1])
                            elif part == 'Failed:' and i+1 < len(parts):
                                self.results['integration']['failed'] = int(parts[i+1])
                        break
                
                print(f"✅ XtraChef integration tests completed")
            else:
                self.results['integration']['failed'] = 1
                self.results['integration']['total'] = 1
                print(f"❌ XtraChef integration tests failed")
            
        except Exception as e:
            self.results['integration']['failed'] = 1
            self.results['integration']['total'] = 1
            print(f"❌ XtraChef integration test execution failed: {str(e)}")
        
        self.results['integration']['duration'] = time.time() - start_time
        return self.results['integration']
    
    def run_business_tests(self) -> Dict[str, Any]:
        """Run business logic and recipe costing tests"""
        print("💰 RUNNING BUSINESS LOGIC TESTS...")
        start_time = time.time()
        
        try:
            # Run the enhanced recipe costing test
            result = subprocess.run([
                sys.executable, 'tests/business/simple_enhanced_costing_test.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Parse output for test counts
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'ENHANCED TEST SUMMARY:' in line:
                        continue
                    elif 'Total:' in line and 'Passed:' in line and 'Failed:' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'Total:' and i+1 < len(parts):
                                self.results['business']['total'] = int(parts[i+1])
                            elif part == 'Passed:' and i+1 < len(parts):
                                self.results['business']['passed'] = int(parts[i+1])
                            elif part == 'Failed:' and i+1 < len(parts):
                                self.results['business']['failed'] = int(parts[i+1])
                        break
                
                print(f"✅ Business logic tests completed")
            else:
                self.results['business']['failed'] = 1
                self.results['business']['total'] = 1
                print(f"❌ Business logic tests failed")
            
        except Exception as e:
            self.results['business']['failed'] = 1
            self.results['business']['total'] = 1
            print(f"❌ Business logic test execution failed: {str(e)}")
        
        self.results['business']['duration'] = time.time() - start_time
        return self.results['business']
    
    def calculate_overall_results(self):
        """Calculate overall test results"""
        categories = ['framework', 'business', 'integration', 'data']
        
        for category in categories:
            self.results['overall']['total'] += self.results[category]['total']
            self.results['overall']['passed'] += self.results[category]['passed']
            self.results['overall']['failed'] += self.results[category]['failed']
        
        self.results['overall']['duration'] = time.time() - time.mktime(self.start_time.timetuple())
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        self.calculate_overall_results()
        
        report = f"""
# 🧪 AUTOMATED TEST EXECUTION REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {self.results['overall']['duration']:.2f} seconds
**Environment:** Lea Jane's Hot Chicken Production System

## 📊 OVERALL TEST RESULTS

{'🎉 ALL TESTS PASSED' if self.results['overall']['failed'] == 0 else f"⚠️  {self.results['overall']['failed']} TESTS FAILED"}

**Summary:** {self.results['overall']['passed']}/{self.results['overall']['total']} tests passed

---

## 🏗️ FRAMEWORK TESTS
**Status:** {'✅ PASS' if self.results['framework']['failed'] == 0 else '❌ FAIL'}
**Results:** {self.results['framework']['passed']}/{self.results['framework']['total']} passed
**Duration:** {self.results['framework']['duration']:.2f}s

**Purpose:** Basic system connectivity and framework validation

---

## 🗄️ DATABASE INTEGRITY TESTS  
**Status:** {'✅ PASS' if self.results['data']['failed'] == 0 else '❌ FAIL'}
**Results:** {self.results['data']['passed']}/{self.results['data']['total']} passed
**Duration:** {self.results['data']['duration']:.2f}s

**Purpose:** Schema validation, relationship constraints, data consistency

---

## 🔒 XTRACHEF INTEGRATION TESTS
**Status:** {'✅ PASS' if self.results['integration']['failed'] == 0 else '❌ FAIL'}
**Results:** {self.results['integration']['passed']}/{self.results['integration']['total']} passed
**Duration:** {self.results['integration']['duration']:.2f}s

**Purpose:** CRITICAL - Protects sacred XtraChef data mapping per DATA_MODEL.md

---

## 💰 BUSINESS LOGIC TESTS
**Status:** {'✅ PASS' if self.results['business']['failed'] == 0 else '❌ FAIL'}
**Results:** {self.results['business']['passed']}/{self.results['business']['total']} passed
**Duration:** {self.results['business']['duration']:.2f}s

**Purpose:** Recipe costing engine, profit margins, menu pricing validation

---

## 🎯 RECOMMENDATIONS

### If All Tests Pass:
- ✅ System is production-ready
- ✅ XtraChef integration is secure
- ✅ Recipe costing engine is accurate
- ✅ Database integrity is maintained
- ✅ Business logic is functioning correctly

### If Tests Fail:
- ❌ Review failed test categories above
- ❌ Check database connectivity and data integrity
- ❌ Verify XtraChef integration hasn't been compromised
- ❌ Validate business logic calculations
- ❌ DO NOT deploy until issues are resolved

---

## 📋 NEXT STEPS

1. **Review Results:** Address any failed tests immediately
2. **Monitor Trends:** Track test results over time
3. **Schedule Regular Runs:** Daily automated execution recommended
4. **Update Tests:** Keep test suite current with system changes

**Test Suite Version:** 1.0  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""
        return report
    
    def save_report(self, report: str) -> str:
        """Save test report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"automated_test_report_{timestamp}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        return report_filename
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Execute complete automated test suite"""
        print("🚀 STARTING COMPREHENSIVE AUTOMATED TEST SUITE")
        print("=" * 70)
        print("Lea Jane's Hot Chicken - Production System Validation")
        print("=" * 70)
        
        # Run tests in dependency order
        for test_category, description in self.test_execution_order:
            print(f"\n📋 {description}")
            print("-" * 50)
            
            if test_category == 'framework':
                self.run_framework_tests()
            elif test_category == 'data':
                self.run_data_integrity_tests()
            elif test_category == 'integration':
                self.run_integration_tests()
            elif test_category == 'business':
                self.run_business_tests()
        
        # Generate and save report
        report = self.generate_test_report()
        report_filename = self.save_report(report)
        
        print("\n" + "=" * 70)
        print("🧪 AUTOMATED TEST EXECUTION COMPLETE")
        print("=" * 70)
        
        # Print summary
        total_passed = self.results['overall']['passed']
        total_tests = self.results['overall']['total']
        
        if self.results['overall']['failed'] == 0:
            print("🎉 ALL TESTS PASSED! System is healthy and production-ready.")
            print(f"✅ {total_passed}/{total_tests} tests passed")
        else:
            failed_count = self.results['overall']['failed']
            print(f"⚠️  {failed_count} TESTS FAILED! System needs attention.")
            print(f"❌ {total_passed}/{total_tests} tests passed")
        
        print(f"📄 Full report saved: {report_filename}")
        print(f"⏱️  Total execution time: {self.results['overall']['duration']:.2f} seconds")
        
        return self.results
    
    def create_ci_cd_hooks(self):
        """Create CI/CD integration hooks"""
        print("🔗 Creating CI/CD integration hooks...")
        
        # Create GitHub Actions workflow
        github_workflow = """name: Lea Jane's Hot Chicken - Automated Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 6 AM
    - cron: '0 6 * * *'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
    
    - name: Run Automated Test Suite
      run: |
        python tests/automation/automated_test_master.py
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: automated_test_report_*.md
"""
        
        # Create pre-commit hook
        pre_commit_hook = """#!/bin/bash
# Pre-commit hook for Lea Jane's Hot Chicken
# Runs critical tests before allowing commits

echo "🧪 Running pre-commit tests..."

# Run critical tests only (faster for commits)
python3 tests/integration/simple_xtrachef_test.py
XTRACHEF_RESULT=$?

python3 tests/data/schema_aware_integrity_test.py
DB_RESULT=$?

if [ $XTRACHEF_RESULT -ne 0 ] || [ $DB_RESULT -ne 0 ]; then
    echo "❌ Critical tests failed! Commit blocked."
    echo "🔒 XtraChef integration or database integrity compromised."
    echo "Run 'python tests/automation/automated_test_master.py' for full diagnostics."
    exit 1
fi

echo "✅ Critical tests passed. Commit allowed."
exit 0
"""
        
        # Create monitoring script
        monitoring_script = """#!/usr/bin/env python3
\"\"\"
CONTINUOUS MONITORING SCRIPT
Runs lightweight health checks every hour
\"\"\"

import time
import subprocess
import sys
from datetime import datetime

def run_health_check():
    \"\"\"Run lightweight system health check\"\"\"
    print(f"🏥 Health check at {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Quick database connectivity test
        result = subprocess.run([
            sys.executable, '-c', 
            "import sqlite3; conn = sqlite3.connect('restaurant_calculator.db'); print('DB OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database connectivity OK")
            return True
        else:
            print("❌ Database connectivity failed")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    \"\"\"Main monitoring loop\"\"\"
    print("🔄 Starting continuous monitoring...")
    
    while True:
        healthy = run_health_check()
        
        if not healthy:
            print("🚨 ALERT: System health check failed!")
            # In production, this would send alerts
        
        # Wait 1 hour
        time.sleep(3600)

if __name__ == "__main__":
    main()
"""
        
        # Create directories and files
        os.makedirs('.github/workflows', exist_ok=True)
        os.makedirs('.git/hooks', exist_ok=True)
        os.makedirs('scripts', exist_ok=True)
        
        # Write files
        with open('.github/workflows/automated-tests.yml', 'w') as f:
            f.write(github_workflow)
        
        with open('.git/hooks/pre-commit', 'w') as f:
            f.write(pre_commit_hook)
        os.chmod('.git/hooks/pre-commit', 0o755)  # Make executable
        
        with open('scripts/health_monitor.py', 'w') as f:
            f.write(monitoring_script)
        os.chmod('scripts/health_monitor.py', 0o755)  # Make executable
        
        print("✅ CI/CD hooks created:")
        print("   • GitHub Actions workflow")
        print("   • Pre-commit hook")
        print("   • Health monitoring script")

def main():
    """Main execution entry point"""
    if not os.path.exists('restaurant_calculator.db'):
        print("❌ Error: Database file not found!")
        print("Automated tests require the restaurant database.")
        return 1
    
    executor = AutomatedTestExecutor()
    
    # Run the complete test suite
    results = executor.run_all_tests()
    
    # Create CI/CD integration hooks
    executor.create_ci_cd_hooks()
    
    # Return appropriate exit code
    return 0 if results['overall']['failed'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
