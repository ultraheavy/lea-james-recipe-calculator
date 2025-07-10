#!/usr/bin/env python3
"""
AUTOMATED TEST CONFIGURATION
Central configuration for all automated testing components
"""

import os
from datetime import datetime
from typing import Dict, List, Any

class TestConfig:
    """Central test configuration"""
    
    # Test execution configuration
    TEST_CATEGORIES = {
        'framework': {
            'name': '🏗️  FRAMEWORK TESTS',
            'script': 'tests/simple_test_runner.py',
            'description': 'Basic system validation and connectivity',
            'critical': True,
            'timeout': 30
        },
        'database': {
            'name': '🗄️  DATABASE TESTS', 
            'script': 'tests/data/schema_aware_integrity_test.py',
            'description': 'Database integrity and schema validation',
            'critical': True,
            'timeout': 60
        },
        'integration': {
            'name': '🔒 XTRACHEF TESTS',
            'script': 'tests/integration/simple_xtrachef_test.py', 
            'description': 'XtraChef integration protection (CRITICAL)',
            'critical': True,
            'timeout': 45
        },
        'business': {
            'name': '💰 BUSINESS TESTS',
            'script': 'tests/business/simple_enhanced_costing_test.py',
            'description': 'Recipe costing and business logic validation',
            'critical': True,
            'timeout': 90
        }
    }
    
    # Performance benchmarks
    PERFORMANCE_BENCHMARKS = {
        'recipe_calculation_ms': 100,    # Recipe cost calculation should be < 100ms
        'inventory_query_ms': 500,       # Inventory queries should be < 500ms
        'database_health_check_ms': 200, # Health checks should be < 200ms
        'full_test_suite_seconds': 300   # Full test suite should complete in < 5 minutes
    }
    
    # Data quality thresholds
    DATA_QUALITY_THRESHOLDS = {
        'inventory_description_completeness': 95,  # 95%+ inventory items must have descriptions
        'inventory_price_completeness': 90,        # 90%+ inventory items must have prices
        'recipe_cost_coverage': 80,                # 80%+ recipes should have calculated costs
        'menu_margin_quality': 60,                 # 60%+ menu items should have 50%+ margins
        'xtrachef_data_integrity': 100             # 100% XtraChef field integrity required
    }
    
    # Business validation rules
    BUSINESS_RULES = {
        'min_inventory_items': 100,        # System should have at least 100 inventory items
        'min_recipes': 10,                 # System should have at least 10 recipes
        'min_menu_items': 20,              # System should have at least 20 menu items
        'max_acceptable_failures': 5,      # Maximum 5% test failures acceptable
        'price_range_min': 0.01,          # Minimum acceptable price
        'price_range_max': 1000.00,       # Maximum reasonable price
        'margin_minimum': 30,              # Minimum acceptable profit margin (30%)
        'margin_target': 70                # Target profit margin (70%)
    }
    
    # Reporting configuration
    REPORTING = {
        'save_reports': True,
        'report_directory': 'test_reports',
        'report_retention_days': 30,
        'email_alerts': False,  # Would be enabled in production
        'slack_alerts': False,  # Would be enabled in production
        'dashboard_update': False  # Would be enabled in production
    }
    
    # CI/CD configuration
    CICD_CONFIG = {
        'pre_commit_tests': ['integration', 'database'],  # Fast critical tests for commits
        'daily_tests': ['framework', 'database', 'integration', 'business'],  # Full suite daily
        'deployment_tests': ['framework', 'database', 'integration', 'business'],  # All tests before deploy
        'monitoring_interval_minutes': 60,  # Health check every hour
        'failure_notification_threshold': 2  # Alert after 2 consecutive failures
    }
    
    @classmethod
    def get_test_script_path(cls, category: str) -> str:
        """Get the full path to a test script"""
        if category in cls.TEST_CATEGORIES:
            return cls.TEST_CATEGORIES[category]['script']
        return None
    
    @classmethod
    def is_critical_test(cls, category: str) -> bool:
        """Check if a test category is critical"""
        if category in cls.TEST_CATEGORIES:
            return cls.TEST_CATEGORIES[category].get('critical', False)
        return False
    
    @classmethod
    def get_test_timeout(cls, category: str) -> int:
        """Get timeout for a test category"""
        if category in cls.TEST_CATEGORIES:
            return cls.TEST_CATEGORIES[category].get('timeout', 60)
        return 60
    
    @classmethod
    def validate_environment(cls) -> Dict[str, bool]:
        """Validate test environment setup"""
        validation = {}
        
        # Check database file exists
        validation['database_exists'] = os.path.exists('restaurant_calculator.db')
        
        # Check test scripts exist
        for category, config in cls.TEST_CATEGORIES.items():
            script_path = config['script']
            validation[f'{category}_script_exists'] = os.path.exists(script_path)
        
        # Check required directories
        validation['test_reports_dir'] = True  # Will be created if needed
        
        return validation
    
    @classmethod
    def get_summary_thresholds(cls) -> Dict[str, Any]:
        """Get pass/fail thresholds for summary reporting"""
        return {
            'minimum_pass_rate': 80,  # 80% of tests must pass
            'critical_test_failures_allowed': 0,  # No critical test failures allowed
            'performance_degradation_threshold': 50,  # 50% performance degradation triggers alert
            'data_quality_minimum': 90  # 90% data quality score required
        }

# Test execution utilities
def create_test_report_directory():
    """Create test report directory if it doesn't exist"""
    report_dir = TestConfig.REPORTING['report_directory']
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"✅ Created test report directory: {report_dir}")

def cleanup_old_reports():
    """Clean up old test reports based on retention policy"""
    report_dir = TestConfig.REPORTING['report_directory']
    retention_days = TestConfig.REPORTING['report_retention_days']
    
    if os.path.exists(report_dir):
        # In a real implementation, this would clean up files older than retention_days
        print(f"🧹 Report cleanup: retaining last {retention_days} days")

def get_test_execution_summary() -> Dict[str, Any]:
    """Get summary of test execution configuration"""
    return {
        'total_test_categories': len(TestConfig.TEST_CATEGORIES),
        'critical_tests': [cat for cat, config in TestConfig.TEST_CATEGORIES.items() if config.get('critical')],
        'max_execution_time': sum(config.get('timeout', 60) for config in TestConfig.TEST_CATEGORIES.values()),
        'performance_benchmarks': len(TestConfig.PERFORMANCE_BENCHMARKS),
        'data_quality_checks': len(TestConfig.DATA_QUALITY_THRESHOLDS),
        'business_rules': len(TestConfig.BUSINESS_RULES)
    }

if __name__ == "__main__":
    # Configuration validation and summary
    print("🔧 AUTOMATED TEST CONFIGURATION")
    print("=" * 50)
    
    # Validate environment
    validation = TestConfig.validate_environment()
    print("📋 Environment Validation:")
    for check, result in validation.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {'OK' if result else 'MISSING'}")
    
    # Show configuration summary
    summary = get_test_execution_summary()
    print(f"\n📊 Configuration Summary:")
    print(f"   • Test Categories: {summary['total_test_categories']}")
    print(f"   • Critical Tests: {len(summary['critical_tests'])}")
    print(f"   • Max Execution Time: {summary['max_execution_time']}s")
    print(f"   • Performance Benchmarks: {summary['performance_benchmarks']}")
    print(f"   • Data Quality Checks: {summary['data_quality_checks']}")
    print(f"   • Business Rules: {summary['business_rules']}")
    
    # Create directories
    create_test_report_directory()
    
    print("\n✅ Test configuration validated and ready")
