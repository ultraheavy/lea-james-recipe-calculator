#!/usr/bin/env python3
"""
Enhanced PDF Recipe Parser v3
Improved handling of metadata extraction, allergen parsing, and ingredient cost assignment.
Focuses on the specific issues identified in S-02 J-Blaze Chicken and S-03 Plain Jane Sandwich PDFs.
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFRecipeParserV3:
    """Enhanced parser for recipe PDFs with improved formatting handling."""
    
    def __init__(self):
        self.prep_recipe_keywords = {
            'ranch', 'sauce', 'seasoning', 'blend', 'dip', 'hot fat',
            'chili oil', 'pickled', 'kimchi', 'mac sauce', 'comeback sauce',
            'buffalo sauce', 'lemon pepper sauce', 'hot honey', 'bbq sauce',
            'alabama white bbq', 'charred onion', 'habanero', 'clucking spice',
            'dressing', 'mayo', 'aioli', 'vinaigrette', 'marinade', 'brine',
            'recipe'  # Added to catch "Lea Jane Recipe", "Kale Kimchi Recipe" etc.
        }
        
        # Common UOM patterns
        self.uom_patterns = r'(each|ea|oz|lbs?|cups?|tsp|tbsp|tablespoon|g|kg|ml|l|qt|gal|pt)'
        
        # Track metadata for deduplication
        self.metadata_found = {}
    
    def _clean_doubled_text(self, text: str) -> str:
        """Clean up doubled characters and patterns from PDF extraction."""
        # First pass: clean doubled alphanumeric characters
        cleaned = []
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i] == text[i + 1]:
                # Check if it's a letter or digit that appears doubled
                if text[i].isalpha():
                    cleaned.append(text[i])
                    i += 2
                    continue
                elif text[i].isdigit() and i + 3 < len(text) and text[i:i+2] == text[i+2:i+4]:
                    # Handle patterns like "0022" -> "02"
                    cleaned.append(text[i:i+2])
                    i += 4
                    continue
            cleaned.append(text[i])
            i += 1
        
        result = ''.join(cleaned)
        
        # Clean specific patterns
        result = re.sub(r'(\d)\1+', r'\1', result)  # "22" -> "2", "333" -> "3"
        result = result.replace('&&', '&')
        result = result.replace('--', '-')
        result = re.sub(r'minsmins', 'mins', result)
        result = re.sub(r'eaea\b', 'ea', result)
        result = re.sub(r'ozoz\b', 'oz', result)
        
        return result
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a single PDF file with enhanced error handling."""
        result = {
            'source_file': Path(pdf_path).name,
            'metadata': {},
            'ingredients': [],
            'raw_lines': [],  # For admin preview
            'errors': [],
            'warnings': [],
            'debug_info': []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract all text
                full_text = ""
                all_lines = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        page_lines = text.split('\n')
                        all_lines.extend(page_lines)
                        result['debug_info'].append(f"Page {page_num + 1}: {len(page_lines)} lines extracted")
                
                # Store raw lines for review
                result['raw_lines'] = all_lines[:50]  # First 50 lines for preview
                
                # Reset metadata tracking for new document
                self.metadata_found = {}
                
                # Parse with enhanced methods
                result['metadata'] = self._extract_metadata_v3(full_text, all_lines)
                result['ingredients'] = self._extract_ingredients_v3(full_text, all_lines)
                
                # Validate and add warnings
                self._validate_recipe_data(result)
                
                logger.info(f"Parsed {pdf_path}: {len(result['ingredients'])} ingredients, "
                          f"{len(result['warnings'])} warnings")
                
        except Exception as e:
            error_msg = f"Error parsing PDF: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _extract_metadata_v3(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Enhanced metadata extraction with deduplication."""
        metadata = {
            'recipe_name': None,
            'prefix': None,
            'yield': None,
            'yield_uom': None,
            'shelf_life': None,
            'shelf_life_uom': None,
            'serving_size': None,
            'serving_uom': None,
            'prep_time': None,
            'prep_time_unit': 'mins',
            'cook_time': None,
            'cook_time_unit': 'mins',
            'allergens': {},
            'is_prep_recipe': False,
            'food_cost': None
        }
        
        # Clean the full text
        clean_text = self._clean_doubled_text(text)
        
        # Look for recipe name with prefix in the first few lines
        # Skip the restaurant name header
        found_recipe = False
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            original_line = line.strip()
            line = self._clean_doubled_text(original_line)
            if not line:
                continue
            
            # Skip restaurant name
            if i == 0 and 'lea james' in line.lower():
                continue
            
            # Look for prefix patterns like "S-02 J-Blaze Chicken" 
            # In the PDF, this appears as "SS--0022 JJ--BBllaazzee CChhiicckkeenn"
            if not found_recipe and re.search(r'[A-Z]+-\d+|[A-Z]{2}--\d{4}', original_line):
                # This line likely has our recipe with prefix
                # Clean it up more aggressively
                cleaned = self._clean_doubled_text(original_line)
                
                # Extract prefix and name
                prefix_match = re.match(r'^([A-Z]{1,3}-\d{2,3})\s+(.+)$', cleaned)
                if prefix_match:
                    metadata['prefix'] = prefix_match.group(1)
                    metadata['recipe_name'] = prefix_match.group(2).strip()
                    found_recipe = True
                    break
                else:
                    # If still can't parse, just use the cleaned line
                    metadata['recipe_name'] = cleaned
                    found_recipe = True
                    break
        
        # Check if prep recipe
        if metadata['recipe_name']:
            name_lower = metadata['recipe_name'].lower()
            metadata['is_prep_recipe'] = any(kw in name_lower for kw in self.prep_recipe_keywords)
        
        # Extract serving/yield info - handle various formats
        self._extract_serving_info(clean_text, metadata)
        
        # Extract prep/cook times
        self._extract_time_info(clean_text, metadata)
        
        # Extract food cost - only first occurrence
        cost_match = re.search(r'Food\s+Cost[:\s]+\$?([\d.]+)', clean_text, re.IGNORECASE)
        if cost_match and not metadata['food_cost']:
            metadata['food_cost'] = cost_match.group(1)
        
        # Extract allergens with improved parsing
        metadata['allergens'] = self._extract_allergens_v3(text, lines)
        
        return metadata
    
    def _extract_serving_info(self, text: str, metadata: Dict[str, Any]):
        """Extract serving/yield information from various formats."""
        # Only extract if not already found
        if metadata['yield']:
            return
            
        # Format 1: "Yield: 1 ea" or "Serving Size: 1 ea"
        yield_match = re.search(r'(?:Yield|Makes|Serves)[:\s]+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?', text, re.IGNORECASE)
        if yield_match:
            metadata['yield'] = yield_match.group(1)
            if yield_match.group(2):
                metadata['yield_uom'] = yield_match.group(2).lower()
        
        # Format 2: Table format "Serving Serving Size Prep Time Cook Time\n1 ea mins mins"
        table_match = re.search(r'Serving\s+Serving\s+Size.*?\n\s*(\d+)\s+(\w+)\s+', text, re.IGNORECASE | re.DOTALL)
        if table_match and not metadata['yield']:
            metadata['yield'] = table_match.group(1)
            metadata['yield_uom'] = table_match.group(2).lower()
            metadata['serving_size'] = table_match.group(1)
            metadata['serving_uom'] = table_match.group(2).lower()
    
    def _extract_time_info(self, text: str, metadata: Dict[str, Any]):
        """Extract prep and cook time information."""
        # Look for prep time - only first occurrence
        if not metadata['prep_time']:
            prep_match = re.search(r'Prep\s*(?:Time)?[:\s]+(\d+)\s*([a-zA-Z]+)?', text, re.IGNORECASE)
            if prep_match:
                metadata['prep_time'] = prep_match.group(1)
                if prep_match.group(2):
                    metadata['prep_time_unit'] = prep_match.group(2).lower()
        
        # Look for cook time - only first occurrence
        if not metadata['cook_time']:
            cook_match = re.search(r'Cook\s*(?:Time)?[:\s]+(\d+)\s*([a-zA-Z]+)?', text, re.IGNORECASE)
            if cook_match:
                metadata['cook_time'] = cook_match.group(1)
                if cook_match.group(2):
                    metadata['cook_time_unit'] = cook_match.group(2).lower()
    
    def _extract_allergens_v3(self, text: str, lines: List[str]) -> Dict[str, bool]:
        """Enhanced allergen extraction returning structured dict."""
        allergens = {}
        allergen_names = ['Eggs', 'Fish', 'Gluten', 'Milk', 'Peanuts', 
                         'Sesame', 'Shellfish', 'Soy', 'Tree Nuts']
        
        # Find allergen section
        allergen_start = -1
        for i, line in enumerate(lines):
            if 'ALLERGENS' in line.upper() or 'AALLLLEERRGGEENNSS' in line.upper():
                allergen_start = i
                break
        
        if allergen_start >= 0:
            # Look at next 15 lines for allergen data
            allergen_lines = lines[allergen_start:allergen_start + 15]
            allergen_text = '\n'.join(allergen_lines)
            
            # Clean doubled text
            allergen_text = self._clean_doubled_text(allergen_text)
            
            # Parse each allergen
            for allergen in allergen_names:
                # Look for pattern: "Allergen Yes" or "Allergen No"
                pattern = rf'{allergen}\s*(Yes|No)'
                match = re.search(pattern, allergen_text, re.IGNORECASE)
                if match:
                    allergens[allergen.lower()] = match.group(1).lower() == 'yes'
                else:
                    # Try multiline format where allergen and Yes/No are on different lines
                    allergen_idx = allergen_text.find(allergen)
                    if allergen_idx >= 0:
                        # Look at text after allergen name (within next 20 chars)
                        after_text = allergen_text[allergen_idx + len(allergen):allergen_idx + len(allergen) + 20]
                        if 'Yes' in after_text:
                            allergens[allergen.lower()] = True
                        elif 'No' in after_text:
                            allergens[allergen.lower()] = False
        
        return allergens
    
    def _extract_ingredients_v3(self, text: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Enhanced ingredient extraction with better cost assignment."""
        ingredients = []
        
        # Find ingredients section
        ing_start = -1
        for i, line in enumerate(lines):
            if re.search(r'INGREDIENTS|IINNGGRREEDDIIEENNTTSS|Ingredients:', line, re.IGNORECASE):
                ing_start = i + 1
                break
        
        if ing_start == -1:
            logger.warning("Could not find ingredients section")
            return ingredients
        
        # Track pending cost assignment
        pending_ingredient = None
        skip_next = False
        
        # Process ingredient lines
        for i in range(ing_start, len(lines)):
            if skip_next:
                skip_next = False
                continue
                
            line = lines[i].strip()
            if not line:
                continue
            
            # Stop conditions
            if self._is_section_end(line):
                break
            
            # Clean the line
            clean_line = self._clean_doubled_text(line)
            
            # Extra cleaning for common issues
            clean_line = clean_line.replace('Gods', 'Goods')  # Common OCR error
            clean_line = clean_line.replace('Mayonaise', 'Mayonnaise')  # Spelling fix
            clean_line = clean_line.replace('DIl', 'Dill')  # Spelling fix
            
            # Check if next line might be a cost for current line
            next_line = None
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
            
            # Parse ingredient(s) from line
            parsed = self._parse_ingredient_line_v3(clean_line, next_line)
            
            if parsed:
                if isinstance(parsed, tuple) and parsed[0] == 'skip_next':
                    # This means we consumed the next line as a cost
                    ingredients.extend(parsed[1])
                    skip_next = True
                elif isinstance(parsed, list):
                    # Multiple ingredients on one line
                    ingredients.extend(parsed)
                else:
                    # Single ingredient
                    ingredients.append(parsed)
        
        return ingredients
    
    def _parse_ingredient_line_v3(self, line: str, next_line: Optional[str] = None) -> Any:
        """Enhanced ingredient line parser with better pattern matching."""
        # Skip invalid lines
        if len(line) < 3 or line.lower() in ['page', 'plastic', 'clear', 'souffle']:
            return None
        
        # Special handling for lines like "Lea Jane Recipe" that appear alone
        if 'recipe' in line.lower() and not any(char.isdigit() for char in line):
            return {
                'quantity': None,
                'unit': None,
                'ingredient_name': line.strip(),
                'cost': None,
                'category': None,
                'is_prep_recipe': True,
                'raw_line': line
            }
        
        # First check if line contains multiple prices (indicates multiple ingredients)
        price_count = len(re.findall(r'\$\d+(?:\.\d+)?', line))
        
        if price_count >= 2:
            # Multiple ingredients on one line
            # Split by price patterns and reconstruct
            ingredients = []
            
            # Split the line by finding ingredient boundaries
            # Pattern: "8 oz Protein, Chicken, Thighs $1.88 3 oz Dry Goods, Chicken Breading, $0.36"
            parts = re.split(r'(\$\d+(?:\.\d+)?)', line)
            
            current_ing = ""
            for i, part in enumerate(parts):
                if part.startswith('$'):
                    # This is a price, parse the preceding ingredient
                    if current_ing.strip():
                        # The current_ing might look like "8 oz Protein, Chicken, Thighs"
                        ing_parts = current_ing.strip().split(None, 2)  # Split into 3 parts max
                        if len(ing_parts) >= 3:
                            ing = {
                                'quantity': ing_parts[0],
                                'unit': ing_parts[1].lower(),
                                'ingredient_name': ing_parts[2].strip(),
                                'cost': part.replace('$', ''),
                                'category': None,
                                'is_prep_recipe': self._is_prep_recipe(ing_parts[2]),
                                'raw_line': line
                            }
                            ingredients.append(ing)
                    current_ing = ""
                else:
                    current_ing += part
            
            if ingredients:
                return ingredients
        
        # Single ingredient patterns
        # Pattern with price
        single_pattern = r'^(\d+(?:\.\d+)?)\s+(' + self.uom_patterns + r')\s+(.+?)\s+\$(\d+(?:\.\d+)?)$'
        match = re.match(single_pattern, line, re.IGNORECASE)
        
        if match:
            return {
                'quantity': match.group(1),
                'unit': match.group(2).lower(),
                'ingredient_name': match.group(3).strip(),
                'cost': match.group(4),
                'category': None,
                'is_prep_recipe': self._is_prep_recipe(match.group(3)),
                'raw_line': line
            }
        
        # Pattern 2: Ingredient without cost, but cost might be on next line
        no_cost_pattern = r'^(\d+(?:\.\d+)?)\s+(' + self.uom_patterns + r')\s+(.+?)$'
        match = re.match(no_cost_pattern, line, re.IGNORECASE)
        
        if match:
            ingredient = {
                'quantity': match.group(1),
                'unit': match.group(2).lower(),
                'ingredient_name': match.group(3).strip(),
                'cost': None,
                'category': None,
                'is_prep_recipe': self._is_prep_recipe(match.group(3)),
                'raw_line': line
            }
            
            # Check if next line is just a cost
            if next_line and re.match(r'^\$?([\d.]+)$', next_line):
                ingredient['cost'] = next_line.replace('$', '')
                # Signal to skip next line
                return ('skip_next', [ingredient])
            
            return ingredient
        
        # Pattern 3: Malformed lines like "2 Worcestershire Sauce $0.00"
        if 'worcestershire' in line.lower():
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                return {
                    'quantity': parts[0],
                    'unit': 'tbsp',  # Assume tablespoon for worcestershire
                    'ingredient_name': ' '.join(parts[1:-1]) if '$' in parts[-1] else ' '.join(parts[1:]),
                    'cost': parts[-1].replace('$', '') if '$' in parts[-1] else None,
                    'category': None,
                    'is_prep_recipe': False,
                    'raw_line': line
                }
        
        # Pattern 4: Lines like "tablespoon tablespoon Spice"
        if re.match(r'^(tablespoon|tbsp|tsp|cup|oz)\s+\1', line, re.IGNORECASE):
            # Clean up doubled unit
            cleaned = re.sub(r'^(\w+)\s+\1\s+', r'\1 ', line, flags=re.IGNORECASE)
            parts = cleaned.split(None, 1)
            if len(parts) == 2:
                return {
                    'quantity': '1',  # Assume 1 if no quantity given
                    'unit': parts[0].lower(),
                    'ingredient_name': parts[1],
                    'cost': None,
                    'category': None,
                    'is_prep_recipe': False,
                    'raw_line': line
                }
        
        # Pattern 5: Just text (like "Slices", "Frying") - skip these
        if line.lower() in ['slices', 'frying', 'portion']:
            return None
        
        # Log unparseable lines for debugging
        if line and not line.lower() in ['slices', 'frying', 'portion']:
            logger.debug(f"Could not parse ingredient line: {line}")
        
        return None
    
    def _is_prep_recipe(self, name: str) -> bool:
        """Check if ingredient name indicates a prep recipe."""
        if not name:
            return False
        
        name_lower = name.lower()
        
        # Check against known prep recipe keywords
        return any(kw in name_lower for kw in self.prep_recipe_keywords)
    
    def _is_section_end(self, line: str) -> bool:
        """Check if line indicates end of ingredients section."""
        line_lower = line.lower()
        
        # Common section headers
        section_headers = ['method', 'instructions', 'directions', 'notes', 'procedure', 'steps', 'preparation']
        if any(header in line_lower for header in section_headers):
            return True
        
        # Page markers
        if 'page :' in line_lower or re.match(r'\d{2}/\d{2}/\d{4}', line):
            return True
        
        return False
    
    def _validate_recipe_data(self, result: Dict[str, Any]):
        """Validate parsed data and add warnings."""
        # Check for missing recipe name
        if not result['metadata'].get('recipe_name'):
            result['warnings'].append("Missing recipe name")
        
        # Check for doubled characters in recipe name
        if result['metadata'].get('recipe_name'):
            name = result['metadata']['recipe_name']
            if re.search(r'(\w)\1{2,}', name):
                result['warnings'].append(f"Recipe name may have formatting issues: {name}")
        
        # Check ingredients
        if not result['ingredients']:
            result['warnings'].append("No ingredients found")
        else:
            # Check for ingredients without costs
            no_cost = [ing for ing in result['ingredients'] if not ing.get('cost')]
            if no_cost:
                result['warnings'].append(f"{len(no_cost)} ingredients missing cost information")
            
            # Check for malformed ingredients
            malformed = [ing for ing in result['ingredients'] 
                        if not ing.get('ingredient_name') or len(ing['ingredient_name']) < 3]
            if malformed:
                result['warnings'].append(f"{len(malformed)} malformed ingredient entries")


def parse_all_pdfs_v3(pdf_dir: Path, output_file: str = "parsed_recipes_v3.json"):
    """Parse all PDFs with the enhanced parser."""
    parser = PDFRecipeParserV3()
    all_results = []
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    print(f"\nEnhanced PDF Recipe Parser v3")
    print(f"Found {len(pdf_files)} PDF files to parse")
    print("=" * 80)
    
    total_warnings = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Parsing: {pdf_file.name}")
        result = parser.parse_pdf(str(pdf_file))
        
        # Summary
        meta = result['metadata']
        ing_count = len(result['ingredients'])
        warn_count = len(result.get('warnings', []))
        total_warnings += warn_count
        
        print(f"  ✓ Recipe: {meta.get('recipe_name', 'Unknown')}")
        if meta.get('prefix'):
            print(f"  ✓ Prefix: {meta['prefix']}")
        if meta.get('is_prep_recipe'):
            print(f"  ✓ Type: Prep Recipe")
        print(f"  ✓ Ingredients: {ing_count}")
        if meta.get('allergens'):
            allergen_list = [k for k, v in meta['allergens'].items() if v]
            if allergen_list:
                print(f"  ✓ Allergens: {', '.join(allergen_list)}")
        if warn_count:
            print(f"  ⚠ Warnings: {warn_count}")
            for warning in result['warnings'][:3]:  # Show first 3 warnings
                print(f"    - {warning}")
        
        all_results.append(result)
    
    # Save results
    output_path = pdf_dir.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print(f"Enhanced parsing complete! Results saved to: {output_path}")
    print(f"Total recipes parsed: {len(all_results)}")
    print(f"Total ingredients found: {sum(len(r['ingredients']) for r in all_results)}")
    print(f"Prep recipes identified: {sum(1 for r in all_results if r['metadata'].get('is_prep_recipe'))}")
    print(f"Total warnings: {total_warnings}")
    
    return all_results


def main():
    """Main entry point."""
    pdf_dir = Path("/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/updated_recipes_csv_pdf/pdf")
    
    # Test mode
    test_mode = False
    
    if test_mode:
        # Test specific problematic PDFs
        parser = PDFRecipeParserV3()
        test_files = ["S-02 J-Blaze Chicken.pdf", "S-03 Plain Jane Sandwich.pdf", "Alabama White BBQ .pdf"]
        
        for pdf_name in test_files:
            pdf_path = pdf_dir / pdf_name
            if pdf_path.exists():
                print(f"\n{'='*80}")
                print(f"Testing: {pdf_name}")
                print('='*80)
                
                result = parser.parse_pdf(str(pdf_path))
                
                # Pretty print result
                print(json.dumps(result, indent=2))
                print(f"\nWarnings: {result.get('warnings', [])}")
    else:
        # Parse all PDFs
        parse_all_pdfs_v3(pdf_dir)


if __name__ == "__main__":
    main()