#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE RUNNER
Runs all Lea James Hot Chicken tests in the correct order
"""

import os
import sys
import time
import subprocess
from datetime import datetime

class ComprehensiveTestRunner:
    """Runs all test categories in proper order"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    def run_test_category(self, category_name: str, test_script: str, description: str):
        """Run a specific test category"""
        print(f"\n{category_name}")
        print("=" * 60)
        print(f"Running: {description}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run([
                sys.executable, test_script
            ], cwd=os.getcwd())
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            self.results[category_name] = {
                'success': success,
                'duration': duration,
                'script': test_script,
                'description': description
            }
            
            print(f"\n⏱️  Duration: {duration:.2f}s")
            print(f"📊 Result: {'✅ PASSED' if success else '❌ FAILED'}")
            
        except Exception as e:
            self.results[category_name] = {
                'success': False,
                'duration': time.time() - start_time,
                'script': test_script,
                'description': description,
                'error': str(e)
            }
            print(f"❌ Test execution failed: {str(e)}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 LEA JAMES HOT CHICKEN - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Test execution order (dependency-aware)
        test_categories = [
            ("🏗️  FRAMEWORK TESTS", "tests/simple_test_runner.py", "Basic system validation"),
            ("🗄️  DATABASE TESTS", "tests/data/schema_aware_integrity_test.py", "Database integrity and schema validation"),
            ("🔒 XTRACHEF TESTS", "tests/integration/simple_xtrachef_test.py", "XtraChef integration protection (CRITICAL)"),
            ("💰 BUSINESS TESTS", "tests/business/simple_enhanced_costing_test.py", "Recipe costing and business logic")
        ]
        
        # Run each test category
        for category, script, description in test_categories:
            if os.path.exists(script):
                self.run_test_category(category, script, description)
            else:
                print(f"\n{category}")
                print("=" * 60)
                print(f"⚠️  Test script not found: {script}")
                self.results[category] = {
                    'success': False,
                    'duration': 0,
                    'script': script,
                    'description': description,
                    'error': 'Script not found'
                }
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test execution summary"""
        total_duration = time.time() - time.mktime(self.start_time.timetuple())
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUITE SUMMARY")
        print("=" * 70)
        
        passed_count = sum(1 for r in self.results.values() if r['success'])
        total_count = len(self.results)
        
        print(f"📋 Test Categories: {passed_count}/{total_count} passed")
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📊 DETAILED RESULTS:")
        
        for category, result in self.results.items():
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {category}: {result['duration']:.2f}s")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        
        if passed_count == total_count:
            print("🎉 ALL TEST CATEGORIES PASSED!")
            print("✅ System is healthy and production-ready")
            print("✅ XtraChef integration is protected")
            print("✅ Database integrity is maintained") 
            print("✅ Business logic is functioning correctly")
        else:
            failed_count = total_count - passed_count
            print(f"⚠️  {failed_count} TEST CATEGORIES FAILED!")
            print("❌ System needs attention before production use")
            
            # Specific guidance based on failures
            for category, result in self.results.items():
                if not result['success']:
                    if 'XTRACHEF' in category:
                        print("🚨 CRITICAL: XtraChef integration may be compromised!")
                    elif 'DATABASE' in category:
                        print("🚨 WARNING: Database integrity issues detected!")
                    elif 'BUSINESS' in category:
                        print("⚠️  Business logic validation failed!")
        
        # Save summary to file
        self.save_summary_report()
        
        return passed_count == total_count
    
    def save_summary_report(self):
        """Save summary report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"comprehensive_test_summary_{timestamp}.md"
        
        total_duration = time.time() - time.mktime(self.start_time.timetuple())
        passed_count = sum(1 for r in self.results.values() if r['success'])
        total_count = len(self.results)
        
        report_content = f"""# Comprehensive Test Suite Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {total_duration:.2f} seconds
**Results:** {passed_count}/{total_count} categories passed

## Test Results

"""
        
        for category, result in self.results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            report_content += f"### {category}\n"
            report_content += f"- **Status:** {status}\n"
            report_content += f"- **Duration:** {result['duration']:.2f}s\n"
            report_content += f"- **Script:** {result['script']}\n"
            if 'error' in result:
                report_content += f"- **Error:** {result['error']}\n"
            report_content += "\n"
        
        report_content += f"""## Overall Assessment

{"🎉 ALL TESTS PASSED - System is production-ready!" if passed_count == total_count else f"⚠️ {total_count - passed_count} categories failed - System needs attention"}

## Next Steps

"""
        
        if passed_count == total_count:
            report_content += """- ✅ System validated and ready for production
- ✅ Continue regular automated testing
- ✅ Monitor system health trends
"""
        else:
            report_content += """- ❌ Address failed test categories immediately
- ❌ Do not deploy until all tests pass
- ❌ Review specific error messages above
"""
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"📄 Summary report saved: {report_filename}")

def main():
    """Main execution"""
    if not os.path.exists('restaurant_calculator.db'):
        print("❌ Error: Database file not found!")
        print("Tests require restaurant_calculator.db in the current directory.")
        return 1
    
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
