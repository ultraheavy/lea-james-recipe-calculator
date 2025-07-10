#!/usr/bin/env python3
"""
AUTOMATED HEALTH MONITORING HOOK
Continuous system health monitoring using hooks integration

This script runs automated health checks and can be triggered:
1. Manually for immediate health check
2. Via cron for scheduled monitoring  
3. Via git hooks for change validation
4. Via API for external monitoring integration
"""

import sqlite3
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class HealthMonitor:
    """Continuous health monitoring for Lea James Hot Chicken system"""
    
    def __init__(self, database_path: str = 'restaurant_calculator.db'):
        self.database_path = database_path
        self.health_data = {}
        
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Test database connection and basic functionality"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'table_count': table_count,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'table_count': 0,
                'error': str(e)
            }
    
    def check_xtrachef_integration(self) -> Dict[str, Any]:
        """Monitor XtraChef integration health"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check for XtraChef data presence
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE item_code IS NOT NULL AND current_price > 0
            """)
            items_with_xtrachef_data = cursor.fetchone()[0]
            
            # Check for recent price updates (last 30 days as example)
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE last_purchased_date IS NOT NULL
            """)
            items_with_dates = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy' if items_with_xtrachef_data > 0 else 'warning',
                'items_with_data': items_with_xtrachef_data,
                'items_with_dates': items_with_dates,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'items_with_data': 0,
                'items_with_dates': 0,
                'error': str(e)
            }
    
    def check_recipe_costing_accuracy(self) -> Dict[str, Any]:
        """Monitor recipe costing engine health"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check for recipes with costs
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE food_cost > 0")
            recipes_with_costs = cursor.fetchone()[0]
            
            # Check for recipe ingredients
            cursor.execute("SELECT COUNT(*) FROM recipe_ingredients")
            total_ingredients = cursor.fetchone()[0]
            
            # Check for ingredients linked to inventory
            cursor.execute("""
                SELECT COUNT(*) FROM recipe_ingredients ri
                LEFT JOIN inventory i ON ri.ingredient_id = i.id
                WHERE i.id IS NOT NULL
            """)
            linked_ingredients = cursor.fetchone()[0]
            
            conn.close()
            
            link_rate = (linked_ingredients / total_ingredients * 100) if total_ingredients > 0 else 0
            
            return {
                'status': 'healthy' if link_rate > 80 else 'warning',
                'recipes_with_costs': recipes_with_costs,
                'total_ingredients': total_ingredients,
                'linked_ingredients': linked_ingredients,
                'link_rate': link_rate,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'recipes_with_costs': 0,
                'total_ingredients': 0,
                'linked_ingredients': 0,
                'link_rate': 0,
                'error': str(e)
            }
    
    def check_menu_integrity(self) -> Dict[str, Any]:
        """Monitor menu system health"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check menu items
            cursor.execute("SELECT COUNT(*) FROM menu_items")
            total_menu_items = cursor.fetchone()[0]
            
            # Check menu items with pricing
            cursor.execute("SELECT COUNT(*) FROM menu_items WHERE menu_price > 0")
            items_with_pricing = cursor.fetchone()[0]
            
            # Check menu assignments (new schema)
            cursor.execute("SELECT COUNT(*) FROM menu_assignments")
            total_assignments = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'total_menu_items': total_menu_items,
                'items_with_pricing': items_with_pricing,
                'total_assignments': total_assignments,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'total_menu_items': 0,
                'items_with_pricing': 0,
                'total_assignments': 0,
                'error': str(e)
            }
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Execute all health checks and compile report"""
        print(f"🏥 Running health check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Run all health checks
        health_report['checks']['database'] = self.check_database_connectivity()
        health_report['checks']['xtrachef'] = self.check_xtrachef_integration()
        health_report['checks']['recipe_costing'] = self.check_recipe_costing_accuracy()
        health_report['checks']['menu_system'] = self.check_menu_integrity()
        
        # Determine overall status
        error_count = sum(1 for check in health_report['checks'].values() if check['status'] == 'error')
        warning_count = sum(1 for check in health_report['checks'].values() if check['status'] == 'warning')
        
        if error_count > 0:
            health_report['overall_status'] = 'error'
        elif warning_count > 0:
            health_report['overall_status'] = 'warning'
        
        return health_report
    
    def save_health_report(self, report: Dict[str, Any], filename: str = None):
        """Save health report to file"""
        if filename is None:
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Health report saved: {filename}")
    
    def print_health_summary(self, report: Dict[str, Any]):
        """Print human-readable health summary"""
        status_icon = {
            'healthy': '✅',
            'warning': '⚠️ ',
            'error': '❌'
        }
        
        print(f"\n{status_icon[report['overall_status']]} OVERALL SYSTEM STATUS: {report['overall_status'].upper()}")
        print("=" * 50)
        
        for check_name, check_data in report['checks'].items():
            icon = status_icon[check_data['status']]
            print(f"{icon} {check_name.upper()}: {check_data['status']}")
            
            # Print key metrics
            for key, value in check_data.items():
                if key not in ['status', 'error'] and value is not None:
                    print(f"   - {key}: {value}")
            
            if check_data['error']:
                print(f"   - ERROR: {check_data['error']}")
            print()

def main():
    """Main health monitoring execution"""
    if not os.path.exists('restaurant_calculator.db'):
        print("❌ Error: Database file not found!")
        return 1
    
    monitor = HealthMonitor()
    health_report = monitor.run_comprehensive_health_check()
    
    # Print summary
    monitor.print_health_summary(health_report)
    
    # Save detailed report
    monitor.save_health_report(health_report)
    
    # Return appropriate exit code
    if health_report['overall_status'] == 'error':
        return 1
    elif health_report['overall_status'] == 'warning':
        return 2
    else:
        return 0

if __name__ == "__main__":
    exit(main())
