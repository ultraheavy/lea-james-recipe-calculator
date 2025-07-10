#!/usr/bin/env python3
"""
AUTOMATED TEST RUNNER - Comprehensive System Testing
Runs all critical business tests and generates reports
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class TestRunner:
    """Automated test execution and reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def run_business_tests(self) -> Dict[str, Any]:
        """Run critical business logic tests"""
        print("🧪 Running CRITICAL BUSINESS TESTS...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/business/test_recipe_costing.py',
                '-v', '--tb=short', '--json-report', '--json-report-file=test_results_business.json'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run XtraChef integration tests"""
        print("🔗 Running XTRACHEF INTEGRATION TESTS...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                'tests/integration/test_xtrachef_integration.py', 
                '-v', '--tb=short', '--json-report', '--json-report-file=test_results_integration.json'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_database_health_check(self) -> Dict[str, Any]:
        """Quick database health verification"""
        print("🗄️  Running DATABASE HEALTH CHECK...")
        
        try:
            import sqlite3
            
            conn = sqlite3.connect('restaurant_calculator.db')
            cursor = conn.cursor()
            
            # Check table counts
            health_data = {}
            
            tables = ['inventory', 'recipes', 'recipe_ingredients', 'menu_items']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                health_data[f"{table}_count"] = count
            
            # Check for critical data
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE current_price > 0")
            health_data['items_with_prices'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE food_cost > 0")
            health_data['recipes_with_costs'] = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'data': health_data,
                'errors': ''
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': {},
                'errors': str(e)
            }
    
    def generate_report(self, business_results: Dict, integration_results: Dict, health_results: Dict) -> str:
        """Generate comprehensive test report"""
        
        report = f"""
# 🧪 AUTOMATED TEST REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Duration:** {(datetime.now() - self.start_time).seconds} seconds

## 📊 OVERALL STATUS

{'✅ PASS' if all([business_results['success'], integration_results['success'], health_results['success']]) else '❌ FAIL'}

---

## 🏢 BUSINESS LOGIC TESTS
**Status:** {'✅ PASS' if business_results['success'] else '❌ FAIL'}
**Return Code:** {business_results['return_code']}

### Output:
```
{business_results['output'][:1000]}...
```

### Errors:
```
{business_results['errors'] if business_results['errors'] else 'None'}
```

---

## 🔗 XTRACHEF INTEGRATION TESTS  
**Status:** {'✅ PASS' if integration_results['success'] else '❌ FAIL'}
**Return Code:** {integration_results['return_code']}

### Output:
```
{integration_results['output'][:1000]}...
```

### Errors:
```
{integration_results['errors'] if integration_results['errors'] else 'None'}
```

---

## 🗄️ DATABASE HEALTH CHECK
**Status:** {'✅ PASS' if health_results['success'] else '❌ FAIL'}

### Data Summary:
"""
        
        if health_results['success']:
            for key, value in health_results['data'].items():
                report += f"- **{key}**: {value}\n"
        else:
            report += f"**Errors:** {health_results['errors']}\n"
        
        report += """
---

## 🎯 RECOMMENDATIONS

### If Tests Pass:
- ✅ System is ready for production use
- ✅ XtraChef integration is working correctly  
- ✅ Recipe costing engine is accurate
- ✅ Database integrity is maintained

### If Tests Fail:
- ❌ Review error messages above
- ❌ Check database connectivity
- ❌ Verify XtraChef data integrity
- ❌ Validate business logic calculations

---

**Next Steps:**
1. Review any failed tests
2. Implement automated monitoring
3. Schedule regular test execution
4. Setup alerting for failures

"""
        return report
    
    def run_all_tests(self):
        """Execute complete test suite"""
        print("🚀 STARTING COMPREHENSIVE TEST SUITE...")
        print("=" * 60)
        
        # Run all test categories
        business_results = self.run_business_tests()
        integration_results = self.run_integration_tests()
        health_results = self.run_database_health_check()
        
        # Generate report
        report = self.generate_report(business_results, integration_results, health_results)
        
        # Save report
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print("=" * 60)
        print(f"📄 Test report saved: {report_filename}")
        
        # Print summary
        total_passed = sum([
            business_results['success'],
            integration_results['success'], 
            health_results['success']
        ])
        
        print(f"📊 SUMMARY: {total_passed}/3 test categories passed")
        
        if total_passed == 3:
            print("🎉 ALL TESTS PASSED! System is healthy.")
            return 0
        else:
            print("⚠️  Some tests failed. Check the report for details.")
            return 1

def main():
    """Main test execution"""
    if not os.path.exists('restaurant_calculator.db'):
        print("❌ Error: Database file not found!")
        print("Make sure you're running this from the project root directory.")
        return 1
    
    runner = TestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
