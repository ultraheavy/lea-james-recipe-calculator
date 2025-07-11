#!/usr/bin/env python3
"""
PDF Recipe Data Extractor
Extracts accurate recipe data from PDF files to establish ground truth
"""

import os
import re
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import PyPDF2
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFRecipeExtractor:
    """Extract recipe data from PDF files"""
    
    def __init__(self, pdf_directory: str):
        self.pdf_directory = Path(pdf_directory)
        self.extracted_data = {}
        
    def extract_all_pdfs(self) -> Dict:
        """Extract data from all PDF files in directory"""
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        # Filter out duplicates (files with (1), (2) suffixes)
        unique_pdfs = {}
        for pdf in pdf_files:
            base_name = re.sub(r'\s*\(\d+\)\.pdf$', '.pdf', pdf.name)
            if base_name not in unique_pdfs:
                unique_pdfs[base_name] = pdf
        
        results = {}
        for base_name, pdf_path in unique_pdfs.items():
            try:
                recipe_data = self.extract_pdf_data(pdf_path)
                if recipe_data:
                    results[base_name] = recipe_data
                    logger.info(f"Successfully extracted: {base_name}")
            except Exception as e:
                logger.error(f"Failed to extract {pdf_path}: {e}")
                
        self.extracted_data = results
        return results
    
    def extract_pdf_data(self, pdf_path: Path) -> Dict:
        """Extract recipe data from a single PDF"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # Extract key recipe information
        recipe_data = {
            'pdf_filename': pdf_path.name,
            'recipe_name': self._extract_recipe_name(text),
            'recipe_type': self._extract_recipe_type(text),
            'food_cost': self._extract_food_cost(text),
            'menu_price': self._extract_menu_price(text),
            'gross_margin': self._extract_gross_margin(text),
            'portions': self._extract_portions(text),
            'ingredients': self._extract_ingredients(text),
            'extracted_at': datetime.now().isoformat()
        }
        
        return recipe_data
    
    def _extract_recipe_name(self, text: str) -> str:
        """Extract recipe name from PDF text"""
        # Look for common patterns
        patterns = [
            r'Recipe Name[:\s]+([^\n]+)',
            r'Prep Recipe Name[:\s]+([^\n]+)',
            r'Menu Item[:\s]+([^\n]+)',
            r'^([A-Z][^:\n]{3,50})(?=\n)',  # Title at start
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Recipe"
    
    def _extract_recipe_type(self, text: str) -> str:
        """Extract recipe type (Main, Side, Sauce, etc.)"""
        # Look for type indicators
        if re.search(r'(sandwich|sando|burger)', text, re.IGNORECASE):
            return "Sandwich"
        elif re.search(r'(wing|tender|chicken|fish)', text, re.IGNORECASE):
            return "Main"
        elif re.search(r'(sauce|dip|dressing)', text, re.IGNORECASE):
            return "Sauce"
        elif re.search(r'(side|fries|mac|slaw|green)', text, re.IGNORECASE):
            return "Side"
        elif re.search(r'(salad)', text, re.IGNORECASE):
            return "Salad"
        
        return "Recipe"
    
    def _extract_food_cost(self, text: str) -> Optional[Decimal]:
        """Extract food cost from PDF"""
        patterns = [
            r'Food Cost[:\s]+\$?([0-9.,]+)',
            r'Total Cost[:\s]+\$?([0-9.,]+)',
            r'Recipe Cost[:\s]+\$?([0-9.,]+)',
            r'Cost[:\s]+\$?([0-9.,]+)(?=\s|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_str = match.group(1).replace(',', '')
                try:
                    return Decimal(cost_str)
                except:
                    continue
        
        return None
    
    def _extract_menu_price(self, text: str) -> Optional[Decimal]:
        """Extract menu price from PDF"""
        patterns = [
            r'Menu Price[:\s]+\$?([0-9.,]+)',
            r'Selling Price[:\s]+\$?([0-9.,]+)',
            r'Price[:\s]+\$?([0-9.,]+)(?=\s|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    continue
        
        return None
    
    def _extract_gross_margin(self, text: str) -> Optional[Decimal]:
        """Extract gross margin percentage from PDF"""
        patterns = [
            r'Gross Margin[:\s]+([0-9.,]+)%?',
            r'Margin[:\s]+([0-9.,]+)%?',
            r'GP[:\s]+([0-9.,]+)%?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                margin_str = match.group(1).replace(',', '').replace('%', '')
                try:
                    return Decimal(margin_str)
                except:
                    continue
        
        return None
    
    def _extract_portions(self, text: str) -> Dict:
        """Extract portion/serving information"""
        portion_data = {
            'batch_size': None,
            'serving_size': None,
            'yield': None
        }
        
        # Batch size patterns
        batch_patterns = [
            r'Batch Size[:\s]+([0-9.,]+)\s*([a-zA-Z]+)',
            r'Recipe Yield[:\s]+([0-9.,]+)\s*([a-zA-Z]+)',
            r'Yield[:\s]+([0-9.,]+)\s*([a-zA-Z]+)',
        ]
        
        for pattern in batch_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                portion_data['batch_size'] = {
                    'quantity': float(match.group(1).replace(',', '')),
                    'unit': match.group(2)
                }
                break
        
        return portion_data
    
    def _extract_ingredients(self, text: str) -> List[Dict]:
        """Extract ingredients with proper UOM separation"""
        ingredients = []
        
        # Look for ingredient section
        ingredient_section = re.search(
            r'(Ingredient[s]?.*?)(Food Cost|Labor Cost|Prime Cost|$)', 
            text, 
            re.IGNORECASE | re.DOTALL
        )
        
        if not ingredient_section:
            return ingredients
        
        lines = ingredient_section.group(1).split('\n')
        
        for line in lines:
            # Skip header lines
            if re.match(r'^(Ingredient|Type|Measurement|Yield|Cost)', line, re.IGNORECASE):
                continue
                
            # Parse ingredient lines - multiple formats
            # Format 1: "Product Name",Product,1920 gram,100%,100%,$5.78
            # Format 2: Product Name,1920 gram,$5.78
            
            # Clean up quotes and split
            parts = [p.strip().strip('"') for p in line.split(',')]
            
            if len(parts) >= 3:
                ingredient = self._parse_ingredient_line(parts)
                if ingredient:
                    ingredients.append(ingredient)
        
        return ingredients
    
    def _parse_ingredient_line(self, parts: List[str]) -> Optional[Dict]:
        """Parse a single ingredient line into structured data"""
        ingredient = {}
        
        # Find the measurement (contains number + unit)
        measurement_pattern = r'([0-9.,]+)\s*([a-zA-Z]+)'
        
        for i, part in enumerate(parts):
            # Check if this part contains a measurement
            match = re.match(measurement_pattern, part)
            if match:
                ingredient['quantity'] = float(match.group(1).replace(',', ''))
                ingredient['unit'] = match.group(2).lower()
                
                # Name is usually before measurement
                if i > 0:
                    ingredient['name'] = parts[0]
                
                # Cost is usually after measurement, starts with $
                for j in range(i+1, len(parts)):
                    if '$' in parts[j]:
                        cost_str = parts[j].replace('$', '').replace(',', '')
                        try:
                            ingredient['cost'] = float(cost_str)
                        except:
                            pass
                        break
                
                return ingredient
        
        return None
    
    def save_extracted_data(self, output_path: str):
        """Save extracted data to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.extracted_data, f, indent=2, default=str)
        logger.info(f"Saved extracted data to {output_path}")
    
    def create_validation_report(self) -> Dict:
        """Create a report summarizing extraction results"""
        report = {
            'total_pdfs': len(self.extracted_data),
            'recipes_with_costs': 0,
            'recipes_with_ingredients': 0,
            'recipes_with_margins': 0,
            'extraction_issues': []
        }
        
        for recipe_name, data in self.extracted_data.items():
            if data.get('food_cost'):
                report['recipes_with_costs'] += 1
            else:
                report['extraction_issues'].append(f"{recipe_name}: Missing food cost")
                
            if data.get('ingredients'):
                report['recipes_with_ingredients'] += 1
            else:
                report['extraction_issues'].append(f"{recipe_name}: No ingredients found")
                
            if data.get('gross_margin'):
                report['recipes_with_margins'] += 1
        
        return report


def main():
    """Run PDF extraction"""
    pdf_dir = "/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/updated_recipes_csv_pdf"
    
    extractor = PDFRecipeExtractor(pdf_dir)
    
    print("Extracting recipe data from PDFs...")
    recipes = extractor.extract_all_pdfs()
    
    # Save results
    extractor.save_extracted_data("extracted_pdf_recipes.json")
    
    # Generate report
    report = extractor.create_validation_report()
    print("\nExtraction Report:")
    print(f"Total PDFs processed: {report['total_pdfs']}")
    print(f"Recipes with costs: {report['recipes_with_costs']}")
    print(f"Recipes with ingredients: {report['recipes_with_ingredients']}")
    print(f"Recipes with margins: {report['recipes_with_margins']}")
    
    if report['extraction_issues']:
        print("\nIssues found:")
        for issue in report['extraction_issues'][:10]:  # Show first 10
            print(f"  - {issue}")


if __name__ == "__main__":
    main()