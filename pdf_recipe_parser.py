#!/usr/bin/env python3
"""
Enhanced PDF Recipe Parser
Robust handling of multi-line ingredients, section boundaries, and character cleanup.
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ParsingState(Enum):
    """Track the current parsing state."""
    SEARCHING = "searching"
    INGREDIENT_START = "ingredient_start"
    INGREDIENT_CONTINUATION = "ingredient_continuation"
    SECTION_END = "section_end"


@dataclass
class IngredientBuffer:
    """Buffer for assembling multi-line ingredients."""
    quantity: Optional[str] = None
    unit: Optional[str] = None
    name_parts: List[str] = field(default_factory=list)
    cost: Optional[str] = None
    raw_lines: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)
    needs_review: bool = False
    
    def is_complete(self) -> bool:
        """Check if we have a complete ingredient."""
        return bool(self.quantity and self.unit and self.name_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to ingredient dictionary."""
        return {
            'quantity': self.quantity,
            'unit': self.unit,
            'ingredient_name': ' '.join(self.name_parts) if self.name_parts else None,
            'cost': self.cost,
            'raw_lines': self.raw_lines,
            'line_numbers': self.line_numbers,
            'needs_review': self.needs_review,
            'category': None
        }


class PDFRecipeParser:
    """Enhanced PDF Recipe Parser with robust multi-line handling."""
    
    def __init__(self):
        self.prep_recipes = self._load_prep_recipes()
        self.section_headers = self._load_section_headers()
        self.unit_patterns = self._load_unit_patterns()
        
    def _load_prep_recipes(self) -> set:
        """Load known prep recipe names or patterns."""
        prep_patterns = {
            'ranch', 'sauce', 'seasoning', 'blend', 'dip', 'hot fat',
            'chili oil', 'pickled', 'kimchi', 'mac sauce', 'comeback sauce',
            'buffalo sauce', 'lemon pepper sauce', 'hot honey', 'bbq sauce',
            'alabama white bbq', 'charred onion', 'habanero', 'clucking spice',
            'recipe', 'dressing', 'marinade', 'mayo', 'aioli'
        }
        return prep_patterns
    
    def _load_section_headers(self) -> Dict[str, str]:
        """Map of malformed section headers to clean versions."""
        return {
            # Doubled character versions
            'IINNGGRREEDDIIEENNTTSS': 'INGREDIENTS',
            'PPRREEPPAARRAATTIIOONN': 'PREPARATION',
            'PPRROOCCEEDDUURREESS': 'PROCEDURES',
            'MMEETTHHOODD': 'METHOD',
            'IINNSSTTRRUUCCTTIIOONNSS': 'INSTRUCTIONS',
            'AALLLLEERRGGEENNSS': 'ALLERGENS',
            'DDEESSCCRRIIPPTTIIOONN': 'DESCRIPTION',
            'NNOOTTEES': 'NOTES',
            # Common variations
            'PREPARATION & PROCEDURES': 'PREPARATION',
            'PPRREEPPAARRAATTIIOONN && PPRROOCCEEDDUURREESS': 'PREPARATION',
            'INSTRUCTIONS:': 'INSTRUCTIONS',
            'METHOD:': 'METHOD',
            'DIRECTIONS': 'INSTRUCTIONS',
            'DIRECTIONS:': 'INSTRUCTIONS'
        }
    
    def _load_unit_patterns(self) -> str:
        """Common unit patterns for ingredient parsing."""
        return r'(each|ea|oz|ounce|lb|lbs?|pound|cup|cups?|tsp|teaspoon|tbsp|tablespoon|g|gram|kg|ml|l|liter|qt|quart|gal|gallon|pt|pint)'
    
    def _clean_doubled_chars(self, text: str) -> str:
        """Enhanced cleanup of doubled characters with context awareness."""
        if not text:
            return text
        
        # First, normalize known section headers
        for malformed, clean in self.section_headers.items():
            text = text.replace(malformed, clean)
        
        # Smart character doubling cleanup
        result = []
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i] == text[i + 1]:
                # Check if this is systematic doubling
                if text[i].isalpha():
                    # Look ahead to see if pattern continues
                    j = i + 2
                    systematic = True
                    while j + 1 < len(text) and j < i + 10:
                        if text[j] != text[j + 1]:
                            systematic = False
                            break
                        j += 2
                    
                    if systematic and j > i + 4:
                        # This is systematic doubling
                        result.append(text[i])
                        i += 2
                    else:
                        # Might be legitimate doubling
                        result.append(text[i])
                        i += 1
                else:
                    # Non-alphabetic character
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        cleaned = ''.join(result)
        
        # Fix common patterns
        cleaned = cleaned.replace('&&', '&')
        cleaned = cleaned.replace('--', '-')
        cleaned = re.sub(r'(\d)\1+', r'\1', cleaned)  # Fix doubled digits
        
        # Fix common doubled words
        patterns = {
            r'\bminsmins\b': 'mins',
            r'\beaea\b': 'ea',
            r'\bozoz\b': 'oz',
            r'\btablespoon\s+tablespoon\b': 'tablespoon',
            r'\bcup\s+cup\b': 'cup',
            r'\bDays\s*Days\b': 'Days'
        }
        
        for pattern, replacement in patterns.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _is_section_boundary(self, line: str) -> bool:
        """Check if a line marks the end of ingredients section."""
        line_clean = self._clean_doubled_chars(line.strip().upper())
        
        # Check for section headers
        section_markers = [
            'PREPARATION', 'PROCEDURE', 'METHOD', 'INSTRUCTIONS',
            'DIRECTIONS', 'NOTES', 'DESCRIPTION'
        ]
        
        for marker in section_markers:
            if marker in line_clean:
                return True
        
        # Check for page markers
        if re.match(r'Page\s*:', line, re.IGNORECASE):
            return True
        if re.match(r'\d{2}/\d{2}/\d{4}', line):
            return True
        
        return False
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a single PDF file and extract all recipe data."""
        result = {
            'source_file': Path(pdf_path).name,
            'metadata': {},
            'ingredients': [],
            'errors': [],
            'warnings': [],
            'debug_info': []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                full_text = ""
                all_lines = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        page_lines = text.split('\n')
                        all_lines.extend(page_lines)
                        full_text += text + "\n"
                        result['debug_info'].append(f"Page {page_num + 1}: {len(page_lines)} lines extracted")
                
                # Parse metadata
                result['metadata'] = self._extract_metadata(full_text, all_lines)
                
                # Check if this is a prep recipe
                recipe_name_lower = result['metadata'].get('recipe_name', '').lower()
                is_prep = any(prep in recipe_name_lower for prep in self.prep_recipes)
                result['metadata']['is_prep_recipe'] = is_prep
                
                # Parse ingredients with line tracking
                result['ingredients'] = self._extract_ingredients_enhanced(all_lines)
                
                # Log summary
                logger.info(f"Parsed {pdf_path}: {len(result['ingredients'])} ingredients found")
                
        except Exception as e:
            error_msg = f"Error parsing PDF: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _extract_metadata(self, text: str, lines: List[str]) -> Dict[str, Any]:
        """Extract recipe metadata from text."""
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
            'cook_time': None,
            'allergens': {}
        }
        
        # Clean the full text
        clean_text = self._clean_doubled_chars(text)
        
        # Extract recipe name and prefix
        for i, line in enumerate(lines[:10]):
            original_line = line.strip()
            clean_line = self._clean_doubled_chars(original_line)
            
            if not clean_line:
                continue
            
            # Skip restaurant name header
            if i == 0 and 'lea james' in clean_line.lower():
                continue
            
            # Look for prefix pattern
            prefix_match = re.match(r'^([A-Z]{1,3}-\d{2,3})\s+(.+)$', clean_line)
            if prefix_match and not metadata['recipe_name']:
                metadata['prefix'] = prefix_match.group(1)
                metadata['recipe_name'] = prefix_match.group(2).strip()
                break
            
            # If no prefix found and line 2, use as recipe name
            if i == 1 and not metadata['recipe_name'] and len(clean_line) > 5:
                metadata['recipe_name'] = clean_line
        
        # Extract serving/yield info
        self._extract_serving_info(clean_text, metadata)
        
        # Extract allergens
        metadata['allergens'] = self._extract_allergens(text, lines)
        
        return metadata
    
    def _extract_serving_info(self, text: str, metadata: Dict[str, Any]):
        """Extract serving and yield information."""
        # Look for yield patterns
        yield_match = re.search(r'(?:Yield|Makes|Serves)[:\s]+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?', text, re.IGNORECASE)
        if yield_match:
            metadata['yield'] = yield_match.group(1)
            if yield_match.group(2):
                metadata['yield_uom'] = yield_match.group(2).lower()
        
        # Look for serving table format
        serving_match = re.search(r'Serving\s+Serving\s+Size.*?\n\s*(\d+)\s+(\w+)', text, re.IGNORECASE | re.DOTALL)
        if serving_match:
            metadata['serving_size'] = serving_match.group(1)
            metadata['serving_uom'] = serving_match.group(2).lower()
            if not metadata['yield']:
                metadata['yield'] = serving_match.group(1)
                metadata['yield_uom'] = serving_match.group(2).lower()
    
    def _extract_allergens(self, text: str, lines: List[str]) -> Dict[str, bool]:
        """Extract allergen information as structured dict."""
        allergens = {}
        allergen_names = ['Eggs', 'Fish', 'Gluten', 'Milk', 'Peanuts', 
                         'Sesame', 'Shellfish', 'Soy', 'Tree Nuts']
        
        # Find allergen section
        allergen_start = -1
        for i, line in enumerate(lines):
            if 'ALLERGENS' in line.upper():
                allergen_start = i
                break
        
        if allergen_start >= 0 and allergen_start + 5 < len(lines):
            # Look at next few lines
            allergen_text = '\n'.join(lines[allergen_start:allergen_start + 5])
            allergen_text = self._clean_doubled_chars(allergen_text)
            
            # Parse each allergen
            for allergen in allergen_names:
                pattern = rf'{allergen}\s*(Yes|No)'
                match = re.search(pattern, allergen_text, re.IGNORECASE)
                if match:
                    allergens[allergen.lower()] = match.group(1).lower() == 'yes'
        
        return allergens
    
    def _extract_ingredients_enhanced(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Enhanced ingredient extraction with multi-line handling."""
        ingredients = []
        
        # Find ingredients section
        ing_start = -1
        for i, line in enumerate(lines):
            clean_line = self._clean_doubled_chars(line.strip().upper())
            if 'INGREDIENTS' in clean_line:
                ing_start = i + 1
                break
        
        if ing_start == -1:
            logger.warning("Could not find ingredients section")
            return ingredients
        
        # Process ingredients with state tracking
        state = ParsingState.SEARCHING
        buffer = IngredientBuffer()
        
        for line_num in range(ing_start, len(lines)):
            line = lines[line_num].strip()
            
            if not line:
                # Empty line - might signal end of current ingredient
                if buffer.quantity:
                    ingredients.append(buffer.to_dict())
                    buffer = IngredientBuffer()
                    state = ParsingState.SEARCHING
                continue
            
            # Check for section boundary
            if self._is_section_boundary(line):
                # Save any buffered ingredient
                if buffer.quantity:
                    ingredients.append(buffer.to_dict())
                break
            
            # Clean the line
            clean_line = self._clean_doubled_chars(line)
            
            # Add to raw lines tracking
            buffer.raw_lines.append(line)
            buffer.line_numbers.append(line_num)
            
            # Try to parse the line
            parsed = self._parse_ingredient_line_enhanced(clean_line, state, buffer)
            
            if parsed:
                state = parsed
            else:
                # Mark for review if we can't parse
                buffer.needs_review = True
        
        # Don't forget last ingredient
        if buffer.quantity:
            ingredients.append(buffer.to_dict())
        
        return ingredients
    
    def _parse_ingredient_line_enhanced(self, line: str, state: ParsingState, 
                                      buffer: IngredientBuffer) -> Optional[ParsingState]:
        """Enhanced line parser with state tracking."""
        # Skip obvious non-ingredient lines
        if line.lower() in ['plastic', 'clear', 'souffle', 'slices', 'frying', 'portion']:
            return state
        
        # Main ingredient regex
        ingredient_regex = rf'^(\d+(?:\.\d+)?)\s+({self.unit_patterns})\s+(.+?)(?:\s+\$(\d+(?:\.\d+)?))?$'
        match = re.match(ingredient_regex, line, re.IGNORECASE)
        
        if match:
            # Start new ingredient or update current
            if state == ParsingState.SEARCHING or buffer.is_complete():
                # Save previous if complete
                if buffer.is_complete():
                    return None  # Signal to save current and start new
                
                # Start new ingredient
                buffer.quantity = match.group(1)
                buffer.unit = match.group(2).lower()
                buffer.name_parts = [match.group(3).strip()]
                if match.group(4):
                    buffer.cost = match.group(4)
                
                return ParsingState.INGREDIENT_START
            else:
                # This might be a continuation or new ingredient
                return None
        
        # Check for cost-only line
        cost_match = re.match(r'^\$?(\d+(?:\.\d+)?)$', line)
        if cost_match:
            if buffer.quantity and not buffer.cost:
                buffer.cost = cost_match.group(1)
                return state
        
        # Check for quantity + unit only (incomplete ingredient)
        qty_unit_match = re.match(rf'^(\d+(?:\.\d+)?)\s+({self.unit_patterns})$', line, re.IGNORECASE)
        if qty_unit_match:
            if state == ParsingState.SEARCHING:
                buffer.quantity = qty_unit_match.group(1)
                buffer.unit = qty_unit_match.group(2).lower()
                return ParsingState.INGREDIENT_CONTINUATION
        
        # Check for continuation patterns
        if state == ParsingState.INGREDIENT_CONTINUATION:
            # This line might be the ingredient name
            if not re.match(r'^\d', line):  # Doesn't start with number
                buffer.name_parts.append(line)
                return ParsingState.INGREDIENT_START
        
        # Handle special cases like "tablespoon tablespoon Spice"
        doubled_unit_match = re.match(rf'^({self.unit_patterns})\s+\1\s+(.+)', line, re.IGNORECASE)
        if doubled_unit_match:
            if not buffer.quantity:
                buffer.quantity = "1"  # Assume 1 if no quantity given
            buffer.unit = doubled_unit_match.group(1).lower()
            buffer.name_parts.append(doubled_unit_match.group(2))
            return ParsingState.INGREDIENT_START
        
        # Check for lines that are just ingredient names or descriptions
        if state in [ParsingState.INGREDIENT_START, ParsingState.INGREDIENT_CONTINUATION]:
            if len(line) > 3 and not line.startswith('$'):
                # Might be continuation of ingredient name
                buffer.name_parts.append(line)
                return state
        
        # If we can't parse it, mark for review
        buffer.needs_review = True
        return state


def parse_all_pdfs(parser, pdf_dir, output_file="parsed_recipes.json"):
    """Parse all PDFs in the directory and save results."""
    all_results = []
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    print(f"\nEnhanced PDF Recipe Parser - Robust Multi-line Handling")
    print(f"Found {len(pdf_files)} PDF files to parse")
    print("=" * 80)
    
    total_ingredients = 0
    total_reviews_needed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Parsing: {pdf_file.name}")
        result = parser.parse_pdf(str(pdf_file))
        
        # Summary
        ingredient_count = len(result['ingredients'])
        review_count = sum(1 for ing in result['ingredients'] if ing.get('needs_review', False))
        errors = len(result['errors'])
        
        total_ingredients += ingredient_count
        total_reviews_needed += review_count
        
        print(f"  ✓ Recipe: {result['metadata'].get('recipe_name', 'Unknown')}")
        if result['metadata'].get('prefix'):
            print(f"  ✓ Prefix: {result['metadata']['prefix']}")
        print(f"  ✓ Ingredients: {ingredient_count}")
        if review_count > 0:
            print(f"  ⚠ Needs Review: {review_count}")
        if result['metadata'].get('is_prep_recipe'):
            print(f"  ✓ Type: Prep Recipe")
        if errors:
            print(f"  ✗ Errors: {errors}")
        
        all_results.append(result)
    
    # Save to JSON
    output_path = pdf_dir.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print(f"Parsing complete! Results saved to: {output_path}")
    print(f"Total recipes parsed: {len(all_results)}")
    print(f"Total ingredients found: {total_ingredients}")
    print(f"Ingredients needing review: {total_reviews_needed}")
    print(f"Prep recipes identified: {sum(1 for r in all_results if r['metadata'].get('is_prep_recipe'))}")
    
    return all_results


def main():
    """Main entry point."""
    parser = PDFRecipeParser()
    
    pdf_dir = Path("/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/updated_recipes_csv_pdf/pdf")
    
    # Test mode - parse specific PDFs
    test_mode = False
    
    if test_mode:
        # Test with problematic PDFs
        test_pdfs = ["S-02 J-Blaze Chicken.pdf", "S-03 Plain Jane Sandwich.pdf", "Alabama White BBQ .pdf"]
        
        for pdf_name in test_pdfs:
            test_pdf = pdf_dir / pdf_name
            if test_pdf.exists():
                print(f"\nTesting: {test_pdf.name}")
                print("=" * 80)
                
                result = parser.parse_pdf(str(test_pdf))
                
                # Pretty print the result
                print(json.dumps(result, indent=2))
                
                # Show ingredients with review flags
                print("\nIngredients Summary:")
                for i, ing in enumerate(result['ingredients'], 1):
                    review = " [NEEDS REVIEW]" if ing.get('needs_review') else ""
                    print(f"{i}. {ing['quantity']} {ing['unit']} {ing['ingredient_name']} - ${ing.get('cost', 'N/A')}{review}")
            else:
                print(f"Test PDF not found: {test_pdf}")
    else:
        # Parse all PDFs
        parse_all_pdfs(parser, pdf_dir)


if __name__ == "__main__":
    main()