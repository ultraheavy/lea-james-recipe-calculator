"""
Unit Conversion Service for Recipe Cost Calculation
Handles conversions between different units of measure for accurate costing
"""

import re
import sqlite3
from typing import Optional, Tuple, Dict

class UnitConverter:
    """Handles unit conversions for recipe cost calculations"""
    
    # Standard conversion factors
    WEIGHT_CONVERSIONS = {
        'kg': 1000,      # to grams
        'g': 1,          # base unit
        'mg': 0.001,
        'lb': 453.592,
        'oz': 28.3495,
    }
    
    VOLUME_CONVERSIONS = {
        'l': 1000,       # to milliliters  
        'ml': 1,         # base unit
        'cup': 236.588,
        'tbsp': 14.7868,
        'tsp': 4.92892,
        'fl oz': 29.5735,
        'gal': 3785.41,
        'qt': 946.353,
        'pt': 473.176,
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def parse_pack_size(self, pack_size: str) -> Tuple[float, str]:
        """
        Parse pack size string like '25kg' or '12 x 400g' into quantity and unit
        Returns: (quantity, unit)
        """
        if not pack_size:
            return 1.0, 'each'
            
        pack_size = pack_size.lower().strip()
        
        # Handle multi-pack formats like "12 x 400g"
        if ' x ' in pack_size:
            parts = pack_size.split(' x ')
            if len(parts) == 2:
                try:
                    count = float(parts[0])
                    qty, unit = self.parse_pack_size(parts[1])
                    return count * qty, unit
                except:
                    pass
        
        # Regular format like "25kg" or "1.5 l"
        match = re.match(r'([0-9.,]+)\s*([a-zA-Z]+)', pack_size)
        if match:
            quantity = float(match.group(1).replace(',', ''))
            unit = match.group(2).lower()
            return quantity, unit
            
        # Just a number
        try:
            return float(pack_size), 'each'
        except:
            return 1.0, 'each'
    
    def convert_to_base_unit(self, quantity: float, from_unit: str, 
                           dimension: str = None) -> Tuple[float, str]:
        """
        Convert quantity to base unit (grams for weight, ml for volume)
        Returns: (converted_quantity, base_unit)
        """
        from_unit = from_unit.lower().strip()
        
        # Check weight units
        if from_unit in self.WEIGHT_CONVERSIONS:
            return quantity * self.WEIGHT_CONVERSIONS[from_unit], 'g'
            
        # Check volume units  
        if from_unit in self.VOLUME_CONVERSIONS:
            return quantity * self.VOLUME_CONVERSIONS[from_unit], 'ml'
            
        # Count units stay as is
        if from_unit in ['each', 'ea', 'pc', 'piece']:
            return quantity, 'each'
            
        # Unknown unit - return as is
        return quantity, from_unit
    
    def convert_between_units(self, quantity: float, from_unit: str, 
                            to_unit: str, density_g_per_ml: float = None) -> float:
        """
        Convert between any two units, using density for volume/weight conversions
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        # Same unit
        if from_unit == to_unit:
            return quantity
            
        # Convert to base units first
        base_qty, base_unit = self.convert_to_base_unit(quantity, from_unit)
        
        # If target is base unit, we're done
        if to_unit == base_unit:
            return base_qty
            
        # Both weight units
        if from_unit in self.WEIGHT_CONVERSIONS and to_unit in self.WEIGHT_CONVERSIONS:
            grams = base_qty  # already in grams
            return grams / self.WEIGHT_CONVERSIONS[to_unit]
            
        # Both volume units
        if from_unit in self.VOLUME_CONVERSIONS and to_unit in self.VOLUME_CONVERSIONS:
            ml = base_qty  # already in ml
            return ml / self.VOLUME_CONVERSIONS[to_unit]
            
        # Volume to weight conversion (need density)
        if base_unit == 'ml' and to_unit in self.WEIGHT_CONVERSIONS:
            if density_g_per_ml:
                grams = base_qty * density_g_per_ml
                return grams / self.WEIGHT_CONVERSIONS[to_unit]
                
        # Weight to volume conversion (need density)
        if base_unit == 'g' and to_unit in self.VOLUME_CONVERSIONS:
            if density_g_per_ml:
                ml = base_qty / density_g_per_ml
                return ml / self.VOLUME_CONVERSIONS[to_unit]
                
        # Cannot convert
        raise ValueError(f"Cannot convert from {from_unit} to {to_unit} without density")
    
    def calculate_ingredient_cost(self, inventory_item: Dict, 
                                recipe_quantity: float, 
                                recipe_unit: str) -> float:
        """
        Calculate the cost of an ingredient in a recipe
        
        Args:
            inventory_item: Row from inventory table with fields:
                - current_price: price paid for purchase_unit
                - pack_size: e.g. "25kg", "12 x 400g"
                - yield_percent: usable percentage after prep
                - density_g_per_ml: for volume/weight conversions
                - count_to_weight_g: for 'each' to weight conversions
            recipe_quantity: amount needed in recipe
            recipe_unit: unit of measure for recipe
            
        Returns:
            Cost in dollars
        """
        # Get purchase price
        current_price = inventory_item.get('current_price', 0)
        if not current_price:
            return 0
            
        # Parse pack size to get quantity and unit
        pack_qty, pack_unit = self.parse_pack_size(inventory_item.get('pack_size', '1 each'))
        
        # Calculate price per base unit
        base_pack_qty, base_unit = self.convert_to_base_unit(pack_qty, pack_unit)
        price_per_base_unit = current_price / base_pack_qty if base_pack_qty > 0 else 0
        
        # Apply yield percentage
        yield_percent = inventory_item.get('yield_percent', 100)
        if yield_percent > 0:
            effective_price_per_base = price_per_base_unit / (yield_percent / 100)
        else:
            effective_price_per_base = price_per_base_unit
            
        # Convert recipe quantity to base unit
        try:
            # Get density if available
            density = inventory_item.get('density_g_per_ml')
            
            # Special handling for 'each' units
            if recipe_unit.lower() in ['each', 'ea', 'pc', 'piece']:
                if base_unit == 'g' and inventory_item.get('count_to_weight_g'):
                    # Convert each to grams
                    recipe_base_qty = recipe_quantity * inventory_item['count_to_weight_g']
                else:
                    # Can't convert 'each' without conversion factor
                    recipe_base_qty = recipe_quantity
                    base_unit = 'each'
            else:
                # Normal unit conversion
                recipe_base_qty = self.convert_between_units(
                    recipe_quantity, recipe_unit, base_unit, density
                )
        except ValueError:
            # If conversion fails, assume units match
            recipe_base_qty = recipe_quantity
            
        # Calculate final cost
        cost = recipe_base_qty * effective_price_per_base
        
        return round(cost, 4)  # Round to 4 decimal places for accuracy