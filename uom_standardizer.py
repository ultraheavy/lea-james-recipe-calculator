#!/usr/bin/env python3
"""
UOM Standardization Engine
Fixes quantity/unit separation and provides comprehensive unit conversions
"""

import re
import sqlite3
from decimal import Decimal
from typing import Tuple, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class UOMStandardizer:
    """Standardize and convert units of measure"""
    
    # Comprehensive unit conversion table
    CONVERSIONS = {
        # Weight conversions (base unit: gram)
        'weight': {
            'g': 1,
            'gram': 1,
            'grams': 1,
            'kg': 1000,
            'kilogram': 1000,
            'kilograms': 1000,
            'mg': 0.001,
            'milligram': 0.001,
            'milligrams': 0.001,
            'oz': 28.3495,
            'ounce': 28.3495,
            'ounces': 28.3495,
            'lb': 453.592,
            'pound': 453.592,
            'pounds': 453.592,
            'lbs': 453.592,
        },
        
        # Volume conversions (base unit: milliliter)
        'volume': {
            'ml': 1,
            'milliliter': 1,
            'milliliters': 1,
            'l': 1000,
            'liter': 1000,
            'liters': 1000,
            'cup': 236.588,
            'cups': 236.588,
            'tbsp': 14.7868,
            'tablespoon': 14.7868,
            'tablespoons': 14.7868,
            'tsp': 4.92892,
            'teaspoon': 4.92892,
            'teaspoons': 4.92892,
            'fl oz': 29.5735,
            'fl.oz': 29.5735,
            'fluid ounce': 29.5735,
            'fluid ounces': 29.5735,
            'gal': 3785.41,
            'gallon': 3785.41,
            'gallons': 3785.41,
            'qt': 946.353,
            'quart': 946.353,
            'quarts': 946.353,
            'pt': 473.176,
            'pint': 473.176,
            'pints': 473.176,
        },
        
        # Count conversions (context-dependent)
        'count': {
            'each': 1,
            'ea': 1,
            'pc': 1,
            'piece': 1,
            'pieces': 1,
            'slice': 1,
            'slices': 1,
            'unit': 1,
            'units': 1,
            'portion': 1,
            'portions': 1,
            'serving': 1,
            'servings': 1,
        },
        
        # Package conversions (variable - needs context)
        'package': {
            'case': 24,  # Default, varies by product
            'cases': 24,
            'box': 1,
            'boxes': 1,
            'bag': 1,
            'bags': 1,
            'bottle': 1,
            'bottles': 1,
            'can': 1,
            'cans': 1,
            'jar': 1,
            'jars': 1,
            'container': 1,
            'containers': 1,
            'pack': 1,
            'packs': 1,
            'package': 1,
            'packages': 1,
        }
    }
    
    # Unit aliases and standardization
    UNIT_ALIASES = {
        # Weight
        'gm': 'g',
        'gr': 'g',
        'grm': 'g',
        'kilo': 'kg',
        'kilos': 'kg',
        'pound': 'lb',
        'pounds': 'lb',
        'lbs': 'lb',
        'ounce': 'oz',
        'ounces': 'oz',
        
        # Volume
        'ltr': 'l',
        'litre': 'l',
        'litres': 'l',
        'millilitre': 'ml',
        'millilitres': 'ml',
        'fluid ounce': 'fl oz',
        'fluid ounces': 'fl oz',
        'fl.oz': 'fl oz',
        'tablespoon': 'tbsp',
        'tablespoons': 'tbsp',
        'teaspoon': 'tsp',
        'teaspoons': 'tsp',
        'gallon': 'gal',
        'gallons': 'gal',
        'quart': 'qt',
        'quarts': 'qt',
        'pint': 'pt',
        'pints': 'pt',
        
        # Count
        'piece': 'each',
        'pieces': 'each',
        'ea': 'each',
        'pc': 'each',
        'unit': 'each',
        'units': 'each',
        'portion': 'each',
        'portions': 'each',
        'serving': 'each',
        'servings': 'each',
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_conversion_tables()
    
    def _init_conversion_tables(self):
        """Initialize or update conversion tables in database"""
        cursor = self.conn.cursor()
        
        # Create units table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unit_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_unit TEXT NOT NULL,
                to_unit TEXT NOT NULL,
                conversion_factor DECIMAL(20,10) NOT NULL,
                unit_type TEXT,
                notes TEXT,
                UNIQUE(from_unit, to_unit)
            )
        """)
        
        # Populate standard conversions
        for unit_type, conversions in self.CONVERSIONS.items():
            base_unit = 'g' if unit_type == 'weight' else 'ml' if unit_type == 'volume' else 'each'
            
            for unit, factor in conversions.items():
                # Store conversion to base unit
                cursor.execute("""
                    INSERT OR REPLACE INTO unit_conversions 
                    (from_unit, to_unit, conversion_factor, unit_type)
                    VALUES (?, ?, ?, ?)
                """, (unit, base_unit, factor, unit_type))
        
        self.conn.commit()
    
    def parse_measurement(self, measurement: str) -> Tuple[Decimal, str]:
        """
        Parse measurement string into quantity and unit
        Examples: "2 oz", "1.5 kg", "3lb", "1 each", "12 x 400g"
        """
        if not measurement:
            return Decimal('1'), 'each'
        
        measurement = measurement.strip().lower()
        
        # Handle multi-pack formats like "12 x 400g"
        if ' x ' in measurement:
            parts = measurement.split(' x ')
            if len(parts) == 2:
                try:
                    count = Decimal(parts[0].strip())
                    qty, unit = self.parse_measurement(parts[1])
                    return count * qty, unit
                except:
                    pass
        
        # Remove common delimiters
        measurement = measurement.replace(',', '')
        
        # Pattern to match number (including decimals) and unit
        patterns = [
            r'^([0-9.]+)\s*([a-zA-Z\s.]+)$',  # "2.5 fl oz"
            r'^([0-9.]+)([a-zA-Z]+)$',        # "2kg"
            r'^([0-9.]+)$',                    # Just a number
        ]
        
        for pattern in patterns:
            match = re.match(pattern, measurement)
            if match:
                if len(match.groups()) == 2:
                    quantity = Decimal(match.group(1))
                    unit = match.group(2).strip()
                    
                    # Standardize unit
                    unit = self.standardize_unit(unit)
                    return quantity, unit
                else:
                    # Just a number, assume 'each'
                    return Decimal(match.group(1)), 'each'
        
        # If no pattern matches, try to extract any number
        numbers = re.findall(r'[0-9.]+', measurement)
        if numbers:
            return Decimal(numbers[0]), 'each'
        
        # Default fallback
        return Decimal('1'), 'each'
    
    def standardize_unit(self, unit: str) -> str:
        """Standardize unit to canonical form"""
        unit = unit.lower().strip()
        
        # Remove periods except in specific cases like "fl.oz"
        if unit not in ['fl.oz']:
            unit = unit.replace('.', '')
        
        # Check aliases
        if unit in self.UNIT_ALIASES:
            return self.UNIT_ALIASES[unit]
        
        # Check all conversion tables
        for unit_type, conversions in self.CONVERSIONS.items():
            if unit in conversions:
                # Return the first/canonical form
                if unit_type == 'weight':
                    if unit in ['gram', 'grams']:
                        return 'g'
                    elif unit in ['kilogram', 'kilograms']:
                        return 'kg'
                    elif unit in ['pound', 'pounds', 'lbs']:
                        return 'lb'
                    elif unit in ['ounce', 'ounces']:
                        return 'oz'
                elif unit_type == 'volume':
                    if unit in ['milliliter', 'milliliters']:
                        return 'ml'
                    elif unit in ['liter', 'liters']:
                        return 'l'
                    elif unit in ['fluid ounce', 'fluid ounces', 'fl.oz']:
                        return 'fl oz'
                elif unit_type == 'count':
                    return 'each'
        
        return unit
    
    def get_unit_type(self, unit: str) -> Optional[str]:
        """Determine the type of unit (weight, volume, count, package)"""
        unit = self.standardize_unit(unit)
        
        for unit_type, conversions in self.CONVERSIONS.items():
            if unit in conversions:
                return unit_type
        
        return None
    
    def convert_units(self, quantity: Decimal, from_unit: str, to_unit: str, 
                     context: Optional[Dict] = None) -> Optional[Decimal]:
        """
        Convert between units
        
        Args:
            quantity: The amount to convert
            from_unit: Source unit
            to_unit: Target unit
            context: Optional context for conversions (e.g., density, case size)
        
        Returns:
            Converted quantity or None if conversion not possible
        """
        from_unit = self.standardize_unit(from_unit)
        to_unit = self.standardize_unit(to_unit)
        
        # Same unit
        if from_unit == to_unit:
            return quantity
        
        # Get unit types
        from_type = self.get_unit_type(from_unit)
        to_type = self.get_unit_type(to_unit)
        
        # Same type conversions
        if from_type == to_type and from_type in ['weight', 'volume']:
            from_factor = self.CONVERSIONS[from_type].get(from_unit, 1)
            to_factor = self.CONVERSIONS[to_type].get(to_unit, 1)
            
            # Convert to base unit then to target
            base_quantity = quantity * Decimal(str(from_factor))
            return base_quantity / Decimal(str(to_factor))
        
        # Volume to weight conversion (needs density)
        if from_type == 'volume' and to_type == 'weight':
            if context and 'density_g_per_ml' in context:
                density = Decimal(str(context['density_g_per_ml']))
                # Convert to ml first
                ml_quantity = self.convert_units(quantity, from_unit, 'ml')
                # Then to grams
                grams = ml_quantity * density
                # Then to target weight unit
                return self.convert_units(grams, 'g', to_unit)
        
        # Weight to volume conversion (needs density)
        if from_type == 'weight' and to_type == 'volume':
            if context and 'density_g_per_ml' in context:
                density = Decimal(str(context['density_g_per_ml']))
                # Convert to grams first
                gram_quantity = self.convert_units(quantity, from_unit, 'g')
                # Then to ml
                ml = gram_quantity / density
                # Then to target volume unit
                return self.convert_units(ml, 'ml', to_unit)
        
        # Count to weight conversion
        if from_type == 'count' and to_type == 'weight':
            if context and 'count_to_weight_g' in context:
                weight_per_unit = Decimal(str(context['count_to_weight_g']))
                grams = quantity * weight_per_unit
                return self.convert_units(grams, 'g', to_unit)
        
        # Package conversions
        if from_type == 'package':
            if context and f'{from_unit}_size' in context:
                package_size = Decimal(str(context[f'{from_unit}_size']))
                base_quantity = quantity * package_size
                # Assume the context provides the unit of the package contents
                if 'package_unit' in context:
                    return self.convert_units(base_quantity, context['package_unit'], to_unit, context)
        
        return None
    
    def fix_recipe_ingredients_uom(self):
        """Fix UOM separation in recipe_ingredients table"""
        cursor = self.conn.cursor()
        
        # Get all ingredients with measurement data
        ingredients = cursor.execute("""
            SELECT id, ingredient_name, quantity, unit_of_measure
            FROM recipe_ingredients
            WHERE unit_of_measure IS NOT NULL
        """).fetchall()
        
        fixed_count = 0
        issues = []
        
        for ing_id, name, qty, uom in ingredients:
            try:
                # Check if quantity contains unit info
                if qty and isinstance(qty, str) and any(c.isalpha() for c in str(qty)):
                    # Quantity field contains unit info - needs fixing
                    parsed_qty, parsed_unit = self.parse_measurement(str(qty))
                    
                    cursor.execute("""
                        UPDATE recipe_ingredients
                        SET quantity = ?,
                            unit_of_measure = ?,
                            canonical_quantity = ?,
                            canonical_unit = ?,
                            conversion_status = 'fixed'
                        WHERE id = ?
                    """, (float(parsed_qty), parsed_unit, float(parsed_qty), parsed_unit, ing_id))
                    
                    fixed_count += 1
                    logger.info(f"Fixed: {name} - {qty} -> {parsed_qty} {parsed_unit}")
                
                elif uom and ' ' in str(uom):
                    # UOM field might contain quantity info
                    parsed_qty, parsed_unit = self.parse_measurement(str(uom))
                    
                    if parsed_qty != 1:
                        # UOM field has quantity mixed in
                        actual_qty = Decimal(str(qty or 1)) * parsed_qty
                        
                        cursor.execute("""
                            UPDATE recipe_ingredients
                            SET quantity = ?,
                                unit_of_measure = ?,
                                canonical_quantity = ?,
                                canonical_unit = ?,
                                conversion_status = 'fixed'
                            WHERE id = ?
                        """, (float(actual_qty), parsed_unit, float(actual_qty), parsed_unit, ing_id))
                        
                        fixed_count += 1
                        logger.info(f"Fixed: {name} - {qty} {uom} -> {actual_qty} {parsed_unit}")
                
            except Exception as e:
                issues.append(f"Error fixing {name}: {e}")
                logger.error(f"Error fixing ingredient {ing_id}: {e}")
        
        self.conn.commit()
        
        return {
            'fixed_count': fixed_count,
            'total_processed': len(ingredients),
            'issues': issues
        }
    
    def create_conversion_report(self) -> Dict:
        """Create a report of all unit conversions in the system"""
        cursor = self.conn.cursor()
        
        # Get unique units used
        units_used = set()
        
        # From recipe ingredients
        recipe_units = cursor.execute("""
            SELECT DISTINCT unit_of_measure 
            FROM recipe_ingredients 
            WHERE unit_of_measure IS NOT NULL
        """).fetchall()
        
        for (unit,) in recipe_units:
            if unit:
                units_used.add(self.standardize_unit(unit))
        
        # From inventory
        inventory_units = cursor.execute("""
            SELECT DISTINCT unit_measure, purchase_unit, recipe_cost_unit
            FROM inventory
        """).fetchall()
        
        for unit_measure, purchase_unit, recipe_cost_unit in inventory_units:
            if unit_measure:
                units_used.add(self.standardize_unit(unit_measure))
            if purchase_unit:
                units_used.add(self.standardize_unit(purchase_unit))
            if recipe_cost_unit:
                units_used.add(self.standardize_unit(recipe_cost_unit))
        
        # Categorize units
        report = {
            'total_unique_units': len(units_used),
            'weight_units': [],
            'volume_units': [],
            'count_units': [],
            'unknown_units': [],
            'conversion_coverage': {}
        }
        
        for unit in units_used:
            unit_type = self.get_unit_type(unit)
            if unit_type == 'weight':
                report['weight_units'].append(unit)
            elif unit_type == 'volume':
                report['volume_units'].append(unit)
            elif unit_type == 'count':
                report['count_units'].append(unit)
            else:
                report['unknown_units'].append(unit)
        
        # Check conversion coverage
        all_units = list(units_used)
        for i, from_unit in enumerate(all_units):
            coverage = []
            for to_unit in all_units:
                if from_unit != to_unit:
                    if self.convert_units(Decimal('1'), from_unit, to_unit):
                        coverage.append(to_unit)
            
            report['conversion_coverage'][from_unit] = {
                'can_convert_to': coverage,
                'coverage_percent': len(coverage) / (len(all_units) - 1) * 100 if len(all_units) > 1 else 0
            }
        
        return report


def main():
    """Test UOM standardization"""
    standardizer = UOMStandardizer('restaurant_calculator.db')
    
    # Test parsing
    test_measurements = [
        "2 oz",
        "1.5 kg",
        "3lb",
        "1 each",
        "12 x 400g",
        "1000 gram",
        "2 qt",
        "1 slice",
        "4 fl oz",
        "1 case",
        "500ml",
        "2cups"
    ]
    
    print("Testing measurement parsing:")
    for measurement in test_measurements:
        qty, unit = standardizer.parse_measurement(measurement)
        print(f"  '{measurement}' -> {qty} {unit}")
    
    print("\nFixing recipe ingredients UOM...")
    results = standardizer.fix_recipe_ingredients_uom()
    print(f"Fixed {results['fixed_count']} out of {results['total_processed']} ingredients")
    
    print("\nGenerating conversion report...")
    report = standardizer.create_conversion_report()
    print(f"Total unique units: {report['total_unique_units']}")
    print(f"Weight units: {report['weight_units']}")
    print(f"Volume units: {report['volume_units']}")
    print(f"Unknown units: {report['unknown_units']}")


if __name__ == "__main__":
    main()