#!/usr/bin/env python3
"""
Generate a comprehensive report on nested recipe implementation
"""

import sqlite3
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

def generate_report():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    report = []
    report.append("# Nested Recipe Implementation Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 1. Summary Statistics
    report.append("## Summary Statistics")
    
    total_recipes = cursor.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    prep_recipes = cursor.execute("SELECT COUNT(*) FROM recipes WHERE recipe_type = 'PrepRecipe'").fetchone()[0]
    regular_recipes = cursor.execute("SELECT COUNT(*) FROM recipes WHERE recipe_type = 'Recipe'").fetchone()[0]
    
    report.append(f"- Total Recipes: {total_recipes}")
    report.append(f"- Prep Recipes: {prep_recipes}")
    report.append(f"- Regular Recipes: {regular_recipes}")
    report.append("")
    
    # Recipe components
    total_components = cursor.execute("SELECT COUNT(*) FROM recipe_components").fetchone()[0]
    recipes_with_components = cursor.execute("""
        SELECT COUNT(DISTINCT parent_recipe_id) FROM recipe_components
    """).fetchone()[0]
    
    report.append(f"- Recipe Component Relationships: {total_components}")
    report.append(f"- Recipes Using Other Recipes: {recipes_with_components}")
    report.append("")
    
    # 2. Migration Results
    report.append("## Migration Results")
    
    migrated = cursor.execute("""
        SELECT COUNT(*) FROM recipe_components 
        WHERE notes = 'Migrated from recipe_ingredients'
    """).fetchone()[0]
    
    report.append(f"- Prep recipe relationships migrated to recipe_components: {migrated}")
    report.append("")
    
    # 3. Prep Recipe Details
    report.append("## Prep Recipe Details")
    report.append("")
    report.append("| Recipe Name | Yield | Unit | Total Cost | Unit Cost |")
    report.append("|-------------|-------|------|------------|-----------|")
    
    prep_recipes_data = cursor.execute("""
        SELECT recipe_name, prep_recipe_yield, prep_recipe_yield_uom, food_cost
        FROM recipes 
        WHERE recipe_type = 'PrepRecipe'
        ORDER BY recipe_name
    """).fetchall()
    
    for recipe in prep_recipes_data:
        if recipe['prep_recipe_yield'] and recipe['prep_recipe_yield_uom']:
            unit_cost = recipe['food_cost'] / float(recipe['prep_recipe_yield'])
            report.append(f"| {recipe['recipe_name']} | {recipe['prep_recipe_yield']} | {recipe['prep_recipe_yield_uom']} | ${recipe['food_cost']:.2f} | ${unit_cost:.2f} |")
        else:
            report.append(f"| {recipe['recipe_name']} | - | - | ${recipe['food_cost']:.2f} | - |")
    
    report.append("")
    
    # 4. Recipe Nesting Structure
    report.append("## Recipe Nesting Structure")
    report.append("")
    
    nested_recipes = cursor.execute("""
        SELECT 
            parent.recipe_name as parent_name,
            parent.recipe_type as parent_type,
            COUNT(rc.id) as component_count,
            parent.food_cost
        FROM recipes parent
        JOIN recipe_components rc ON parent.id = rc.parent_recipe_id
        GROUP BY parent.id
        ORDER BY parent.recipe_name
    """).fetchall()
    
    for recipe in nested_recipes:
        report.append(f"### {recipe['parent_name']} ({recipe['parent_type']})")
        report.append(f"- Total Cost: ${recipe['food_cost']:.2f}")
        report.append(f"- Uses {recipe['component_count']} prep recipe(s):")
        
        # Get components
        components = cursor.execute("""
            SELECT 
                comp.recipe_name,
                rc.quantity,
                rc.unit_of_measure,
                rc.cost
            FROM recipe_components rc
            JOIN recipes comp ON rc.component_recipe_id = comp.id
            WHERE rc.parent_recipe_id = (
                SELECT id FROM recipes WHERE recipe_name = ?
            )
        """, (recipe['parent_name'],)).fetchall()
        
        for comp in components:
            cost_str = f"${comp['cost']:.2f}" if comp['cost'] is not None else "Not calculated"
            report.append(f"  - {comp['quantity']} {comp['unit_of_measure']} **{comp['recipe_name']}** ({cost_str})")
        
        report.append("")
    
    # 5. Cost Analysis
    report.append("## Cost Analysis")
    report.append("")
    
    # Recipes with high costs
    high_cost = cursor.execute("""
        SELECT recipe_name, recipe_type, food_cost
        FROM recipes
        WHERE food_cost > 50
        ORDER BY food_cost DESC
        LIMIT 10
    """).fetchall()
    
    if high_cost:
        report.append("### High-Cost Recipes (>$50)")
        report.append("| Recipe | Type | Cost |")
        report.append("|--------|------|------|")
        for r in high_cost:
            report.append(f"| {r['recipe_name']} | {r['recipe_type']} | ${r['food_cost']:.2f} |")
        report.append("")
    
    # 6. Data Quality Issues
    report.append("## Data Quality Issues")
    report.append("")
    
    # Missing yields
    missing_yields = cursor.execute("""
        SELECT COUNT(*) FROM recipes 
        WHERE recipe_type = 'PrepRecipe' 
        AND (prep_recipe_yield IS NULL OR prep_recipe_yield_uom IS NULL)
    """).fetchone()[0]
    
    report.append(f"- Prep recipes missing yield information: {missing_yields}")
    
    # Unit conversion issues
    conversion_issues = cursor.execute("""
        SELECT COUNT(*) FROM recipe_components rc
        JOIN recipes r ON rc.component_recipe_id = r.id
        WHERE rc.unit_of_measure != r.prep_recipe_yield_uom
    """).fetchone()[0]
    
    report.append(f"- Recipe components requiring unit conversion: {conversion_issues}")
    
    # Zero costs
    zero_cost_components = cursor.execute("""
        SELECT COUNT(*) FROM recipe_components WHERE cost = 0
    """).fetchone()[0]
    
    report.append(f"- Recipe components with zero cost: {zero_cost_components}")
    
    # Write report
    report_path = f"audit_reports/nested_recipe_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Report saved to: {report_path}")
    
    # Also print summary to console
    print("\nNested Recipe Implementation Summary:")
    print("="*50)
    print(f"Total recipes: {total_recipes} ({prep_recipes} prep, {regular_recipes} regular)")
    print(f"Recipe component relationships: {total_components}")
    print(f"Recipes using other recipes: {recipes_with_components}")
    print(f"High-cost recipes (>$50): {len(high_cost)}")
    print(f"Data quality issues: {missing_yields + conversion_issues + zero_cost_components}")
    
    conn.close()

if __name__ == '__main__':
    generate_report()