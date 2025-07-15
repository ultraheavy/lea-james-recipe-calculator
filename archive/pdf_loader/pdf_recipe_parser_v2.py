#!/usr/bin/env python3
"""
Enhanced PDF Recipe Parser v2.0
Fixes parsing issues with doubled characters, section detection, and ingredient parsing.
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedPDFRecipeParser:
    """Enhanced PDF Recipe Parser with improved cleanup and section detection."""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.prep_recipes = self._load_prep_recipes()
        self.section_headers = self._load_section_headers()
        self.problematic_lines = []
        
        # Setup debug logging
        if debug_mode:
            debug_handler = logging.FileHandler('pdf_parser_debug.log')
            debug_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            debug_handler.setFormatter(debug_formatter)
            logger.addHandler(debug_handler)
            logger.setLevel(logging.DEBUG)
    
    def _load_prep_recipes(self) -> set:
        """Load known prep recipe patterns."""
        return {
            'ranch', 'sauce', 'seasoning', 'blend', 'dip', 'hot fat',
            'chili oil', 'pickled', 'kimchi', 'mac sauce', 'comeback sauce',
            'buffalo sauce', 'lemon pepper sauce', 'hot honey', 'bbq sauce',
            'alabama white bbq', 'charred onion', 'habanero', 'clucking spice',
            'oil', 'fat', 'aioli', 'mayo', 'mustard', 'vinaigrette'
        }
    
    def _load_section_headers(self) -> dict:
        """Map malformed section headers to clean versions."""
        return {
            'IINNGGRREEDDIIEENNTTSS': 'INGREDIENTS',
            'PPRREEPPAARRAATTIIOONN': 'PREPARATION',
            'PPRROOCCEEDDUURREESS': 'PROCEDURES', 
            'AALLLLEERRGGEENNSS': 'ALLERGENS',
            'DDEESSCCRRIIPPTTIIOONN': 'DESCRIPTION',
            'IINNSSTTRRUUCCTTIIOONNSS': 'INSTRUCTIONS',
            'MMEETTHHOODD': 'METHOD',
            'NNOOTTEES': 'NOTES'
        }
    
    def _clean_doubled_characters(self, text: str) -> str:
        """Enhanced cleanup of doubled characters with better pattern detection."""
        if not text:
            return text
        
        # Clean null bytes and other special characters
        text = text.replace('\x00', '').replace('\u0000', '')
        
        # Pattern 1: Fix doubled symbols and punctuation first
        text = text.replace('&&', '&')
        text = text.replace('--', '-')
        text = text.replace('..', '.')
        text = text.replace('$$', '$')
        
        # Pattern 2: Fix known section headers before general cleanup
        for malformed, clean in self.section_headers.items():
            text = text.replace(malformed, clean)
        
        # Pattern 3: More aggressive pattern for systematic character doubling
        # This handles cases like "AAllaabbaammaa" -> "Alabama"
        def fix_systematic_doubling(text_segment):
            result = []
            i = 0
            while i < len(text_segment):
                if (i + 1 < len(text_segment) and 
                    text_segment[i] == text_segment[i + 1] and
                    text_segment[i].isalpha()):
                    # Check if this is part of a systematic doubling pattern
                    # Look ahead to see if pattern continues
                    j = i + 2
                    doubled_pattern = True
                    while j + 1 < len(text_segment) and j < i + 10:  # Check next few chars
                        if (text_segment[j].isalpha() and 
                            j + 1 < len(text_segment) and
                            text_segment[j] == text_segment[j + 1]):
                            j += 2
                        else:
                            if j == i + 2:  # No pattern found
                                doubled_pattern = False
                            break
                    
                    if doubled_pattern and j > i + 4:  # At least 2 more doubled chars found
                        # This is systematic doubling, keep only one of each pair
                        result.append(text_segment[i])
                        i += 2
                    else:
                        # Might be legitimate doubling, keep both
                        result.append(text_segment[i])
                        i += 1
                else:
                    result.append(text_segment[i])
                    i += 1
            return ''.join(result)
        
        # Apply to each word separately to avoid breaking legitimate doubles
        words = re.split(r'(\s+)', text)  # Keep whitespace
        cleaned_words = []
        for word in words:
            if word.isspace():
                cleaned_words.append(word)
            else:
                cleaned_words.append(fix_systematic_doubling(word))
        
        text = ''.join(cleaned_words)
        
        # Pattern 4: Clean up remaining common doubled units and words
        unit_fixes = {
            r'\bccuuppss?\b': 'cup',
            r'\boouu\b': 'oz', r'\boozz\b': 'oz',
            r'\bllbbss?\b': 'lb',
            r'\bttsspp\b': 'tsp', r'\bttbbsspp\b': 'tbsp',
            r'\bggaall\b': 'gal', r'\bqquuaarrtt\b': 'quart',
            r'\bmmiinnss\b': 'mins', r'\bhhrrss\b': 'hrs',
            r'\beeaacchh\b': 'each', r'\beeaa\b': 'ea',
            r'\bDDaayyss\b': 'Days',
            r'\bSSaauucceess?\b': 'Sauce'
        }
        
        for pattern, replacement in unit_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _calculate_parse_quality(self, result: Dict[str, Any]) -> int:
        """Calculate parse quality score (0-100)."""
        score = 100
        warnings = result.get('warnings', [])
        
        # Deduct points for various issues
        if not result['metadata'].get('recipe_name'):
            score -= 20
            
        if not result['ingredients']:
            score -= 30
            
        # Deduct for warnings
        score -= min(len(warnings) * 5, 30)
        
        # Deduct for missing critical data
        missing_cost_count = sum(1 for ing in result['ingredients'] 
                               if not ing.get('cost') or ing.get('cost') == '0')
        if result['ingredients']:
            missing_cost_ratio = missing_cost_count / len(result['ingredients'])
            score -= int(missing_cost_ratio * 20)
        
        # Deduct for malformed ingredient names
        malformed_count = sum(1 for ing in result['ingredients']
                            if self._is_malformed_ingredient(ing.get('ingredient_name', '')))
        if result['ingredients']:
            malformed_ratio = malformed_count / len(result['ingredients'])
            score -= int(malformed_ratio * 15)
        
        return max(0, min(100, score))
    
    def _is_malformed_ingredient(self, name: str) -> bool:
        """Check if ingredient name appears malformed."""
        if not name or len(name) < 2:
            return True
        
        # Check for obvious parsing artifacts
        malformed_patterns = [
            r'^\$[\d.]+$',  # Just a price
            r'^\d+$',       # Just a number
            r'^[.,;:-]+$',  # Just punctuation
            r'Page\s*:\s*\d+',  # Page footer
            r'\d{2}/\d{2}/\d{4}',  # Date
            r'PREPARATION|PROCEDURES|METHOD|INSTRUCTIONS'  # Section headers
        ]
        
        for pattern in malformed_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return True
        
        return False
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a single PDF file with enhanced error handling."""
        result = {
            'source_file': Path(pdf_path).name,
            'metadata': {},
            'ingredients': [],
            'procedures': [],
            'errors': [],
            'warnings': [],
            'debug_info': [],
            'parse_quality_score': 0,
            'raw_sections': {}
        }
        
        if self.debug_mode:
            logger.debug(f"Starting parse of {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract and clean text
                raw_text = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        raw_text += page_text + "\n"
                        result['debug_info'].append(f"Page {page_num + 1}: {len(page_text)} characters")
                
                if not raw_text.strip():
                    result['errors'].append("No text extracted from PDF")
                    return result
                
                # Clean the text
                cleaned_text = self._clean_doubled_characters(raw_text)
                result['raw_sections']['original'] = raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
                result['raw_sections']['cleaned'] = cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
                
                if self.debug_mode:
                    logger.debug(f"Text cleaning: {len(raw_text)} -> {len(cleaned_text)} chars")
                
                # Parse sections
                sections = self._parse_sections(cleaned_text)
                result['raw_sections'].update(sections)
                
                # Extract metadata
                result['metadata'] = self._extract_metadata(cleaned_text, sections)
                
                # Check if prep recipe
                recipe_name_lower = result['metadata'].get('recipe_name', '').lower()
                is_prep = any(prep in recipe_name_lower for prep in self.prep_recipes)
                result['metadata']['is_prep_recipe'] = is_prep
                
                # Parse ingredients
                result['ingredients'] = self._extract_ingredients(sections.get('ingredients', ''), result['warnings'])
                
                # Parse procedures if present
                if 'procedures' in sections:
                    result['procedures'] = self._extract_procedures(sections['procedures'])
                
                # Calculate quality score
                result['parse_quality_score'] = self._calculate_parse_quality(result)
                
                # Log summary
                logger.info(f"Parsed {pdf_path}: {len(result['ingredients'])} ingredients, quality: {result['parse_quality_score']}%")
                
        except Exception as e:
            error_msg = f"Error parsing PDF: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['parse_quality_score'] = 0
        
        return result
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse text into logical sections."""
        sections = {}
        
        # Find section boundaries
        section_patterns = {
            'ingredients': [
                r'INGREDIENTS\s*:?\s*\n',
                r'Recipe Components?\s*:?\s*\n',
                r'INGREDIENTS?\s*\n',
                r'IINGREDIEENTS\s*\n',  # Common malformed version
                r'INGREDIENTS\s*$'  # End of line version
            ],
            'procedures': [
                r'PREPARATION\s*&?\s*PROCEDURES?\s*:?\s*\n',
                r'METHOD\s*:?\s*\n',
                r'INSTRUCTIONS?\s*:?\s*\n',
                r'DIRECTIONS?\s*:?\s*\n'
            ],
            'allergens': [
                r'ALLERGENS?\s*:?\s*\n'
            ],
            'description': [
                r'DESCRIPTION\s*:?\s*\n'
            ]
        }
        
        # Find section starts
        section_starts = {}
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    section_starts[section_name] = match.end()
                    if self.debug_mode:
                        logger.debug(f"Found section '{section_name}' at position {match.end()}")
                    break
        
        # Extract section content
        sorted_sections = sorted(section_starts.items(), key=lambda x: x[1])
        
        for i, (section_name, start_pos) in enumerate(sorted_sections):
            # Find end position (start of next section or end of text)
            if i + 1 < len(sorted_sections):
                end_pos = sorted_sections[i + 1][1]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_content = text[start_pos:end_pos].strip()
            
            # Clean up section content
            section_content = self._clean_section_content(section_content)
            sections[section_name] = section_content
        
        return sections
    
    def _clean_section_content(self, content: str) -> str:
        """Clean section content of footers and irrelevant text."""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip footer lines
            if re.match(r'\d{2}/\d{2}/\d{4}', line):
                continue
            if 'Page :' in line:
                continue
            if re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)', line):
                continue
            
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_metadata(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract recipe metadata with improved parsing."""
        metadata = {
            'recipe_name': None,
            'recipe_prefix': None,
            'yield': None,
            'yield_uom': None,
            'shelf_life': None,
            'shelf_life_uom': None,
            'serving_size': None,
            'serving_uom': None,
            'prep_time': None,
            'cook_time': None,
            'allergens': []
        }
        
        lines = text.split('\n')
        
        # Extract recipe name and prefix
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for prefix patterns (e.g., "DP-01 Recipe Name")
            prefix_match = re.match(r'^([A-Z]{1,3}-\d{2})\s+(.+)$', line)
            if prefix_match:
                metadata['recipe_prefix'] = prefix_match.group(1)
                metadata['recipe_name'] = prefix_match.group(2)
                break
            
            # If no prefix found and this looks like a recipe name
            if i < 3 and len(line) > 5 and not line.startswith(('Lea James', 'Type', 'Menu')):
                metadata['recipe_name'] = line
                break
        
        # Extract serving/yield information
        serving_pattern = r'Serving\s+Serving\s+Size.*?\n([^\n]+)'
        serving_match = re.search(serving_pattern, text, re.IGNORECASE | re.DOTALL)
        if serving_match:
            values_line = serving_match.group(1).strip()
            values_match = re.match(r'(\d+)\s+(\w+)', values_line)
            if values_match:
                metadata['yield'] = values_match.group(1)
                metadata['yield_uom'] = values_match.group(2)
                metadata['serving_size'] = values_match.group(1)
                metadata['serving_uom'] = values_match.group(2)
        
        # Extract allergens from section
        if 'allergens' in sections:
            allergen_text = sections['allergens']
            allergen_names = ['Eggs', 'Fish', 'Gluten', 'Milk', 'Peanuts', 'Sesame', 'Shellfish', 'Soy', 'Tree Nuts']
            
            for allergen in allergen_names:
                # Look for Yes markers
                if re.search(rf'{allergen}\s+Yes', allergen_text, re.IGNORECASE):
                    metadata['allergens'].append(allergen)
        
        return metadata
    
    def _extract_ingredients(self, ingredients_text: str, warnings: List[str]) -> List[Dict[str, Any]]:
        """Enhanced ingredient extraction with better line handling."""
        if not ingredients_text:
            warnings.append("No ingredients section found")
            return []
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        # Combine lines that might be split ingredients
        combined_lines = self._combine_split_lines(lines)
        
        for line_num, line in enumerate(combined_lines):
            line = line.strip()
            if not line:
                continue
            
            if self.debug_mode:
                logger.debug(f"Processing ingredient line: {line}")
            
            # Skip obvious non-ingredient lines
            if self._should_skip_line(line):
                if self.debug_mode:
                    logger.debug(f"Skipping line: {line}")
                continue
            
            # Try to parse ingredients from the line
            parsed_ingredients = self._parse_ingredient_line(line, warnings)
            
            if parsed_ingredients:
                if isinstance(parsed_ingredients, list):
                    ingredients.extend(parsed_ingredients)
                else:
                    ingredients.append(parsed_ingredients)
            else:
                # Store problematic line for review
                self.problematic_lines.append({
                    'line': line,
                    'line_number': line_num,
                    'context': 'ingredients'
                })
                warnings.append(f"Could not parse ingredient line: {line[:50]}...")
        
        return ingredients
    
    def _combine_split_lines(self, lines: List[str]) -> List[str]:
        """Combine lines that appear to be split ingredients."""
        combined = []
        current_line = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_line:
                    combined.append(current_line)
                    current_line = ""
                continue
            
            # If line starts with a number, it's likely a new ingredient
            if re.match(r'^\d+', line) and current_line:
                combined.append(current_line)
                current_line = line
            else:
                # Continuation of previous line
                if current_line:
                    current_line += " " + line
                else:
                    current_line = line
        
        if current_line:
            combined.append(current_line)
        
        return combined
    
    def _should_skip_line(self, line: str) -> bool:
        """Determine if a line should be skipped during ingredient parsing."""
        skip_patterns = [
            r'^Page\s*:',
            r'^\d{2}/\d{2}/\d{4}',
            r'^\d{1,2}:\d{2}\s*(AM|PM)',
            r'^(PREPARATION|PROCEDURES|METHOD|INSTRUCTIONS)',
            r'^[.-]+$',  # Just dashes or dots
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _parse_ingredient_line(self, line: str, warnings: List[str]) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Parse a single ingredient line with multiple strategies."""
        
        # Strategy 1: Multiple ingredients with prices (e.g., "2 oz Item $1.50 3 cups Other $2.00")
        price_pattern = r'(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+([^$]+?)\s+\$(\d+(?:\.\d+)?)'
        price_matches = list(re.finditer(price_pattern, line))
        
        if len(price_matches) > 1:
            # Multiple ingredients on one line
            ingredients_list = []
            for match in price_matches:
                ingredient = {
                    'ingredient_name': match.group(3).strip(),
                    'quantity': match.group(1),
                    'unit': match.group(2),
                    'cost': match.group(4),
                    'category': None,
                    'raw_line': line
                }
                self._clean_ingredient_name(ingredient)
                ingredients_list.append(ingredient)
            return ingredients_list
        
        elif len(price_matches) == 1:
            # Single ingredient with price
            match = price_matches[0]
            ingredient = {
                'ingredient_name': match.group(3).strip(),
                'quantity': match.group(1),
                'unit': match.group(2),
                'cost': match.group(4),
                'category': None,
                'raw_line': line
            }
            self._clean_ingredient_name(ingredient)
            return ingredient
        
        # Strategy 2: Ingredient without price
        no_price_pattern = r'^(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(.+)$'
        no_price_match = re.match(no_price_pattern, line)
        
        if no_price_match:
            ingredient = {
                'ingredient_name': no_price_match.group(3).strip(),
                'quantity': no_price_match.group(1),
                'unit': no_price_match.group(2),
                'cost': None,
                'category': None,
                'raw_line': line
            }
            self._clean_ingredient_name(ingredient)
            return ingredient
        
        # Strategy 3: Just ingredient name (fallback)
        if len(line) > 3 and not re.match(r'^\d+\.?\s*$', line):
            ingredient = {
                'ingredient_name': line.strip(),
                'quantity': None,
                'unit': None,
                'cost': None,
                'category': None,
                'raw_line': line
            }
            
            # Extract any embedded cost
            cost_match = re.search(r'\$(\d+(?:\.\d+)?)', line)
            if cost_match:
                ingredient['cost'] = cost_match.group(1)
                # Remove cost from name
                ingredient['ingredient_name'] = re.sub(r'\$\d+(?:\.\d+)?', '', ingredient['ingredient_name']).strip()
            
            if ingredient['ingredient_name']:
                self._clean_ingredient_name(ingredient)
                return ingredient
        
        return None
    
    def _clean_ingredient_name(self, ingredient: Dict[str, Any]) -> None:
        """Clean and validate ingredient name."""
        name = ingredient.get('ingredient_name', '')
        
        if not name:
            return
        
        # Remove trailing punctuation
        name = name.rstrip('.,;:')
        
        # Extract category if in parentheses
        category_match = re.search(r'\(([^)]+)\)$', name)
        if category_match:
            ingredient['category'] = category_match.group(1)
            name = name[:category_match.start()].strip()
        
        # Clean up common artifacts
        name = re.sub(r'\s+', ' ', name)  # Multiple spaces
        name = name.strip(' -,.')
        
        ingredient['ingredient_name'] = name
    
    def _extract_procedures(self, procedures_text: str) -> List[str]:
        """Extract procedure steps."""
        if not procedures_text:
            return []
        
        # Split into numbered steps or paragraphs
        steps = []
        lines = procedures_text.split('\n')
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this starts a new numbered step
            if re.match(r'^\d+\.', line):
                if current_step:
                    steps.append(current_step.strip())
                current_step = line
            else:
                if current_step:
                    current_step += " " + line
                else:
                    current_step = line
        
        if current_step:
            steps.append(current_step.strip())
        
        return steps


def parse_all_pdfs_enhanced(parser, pdf_dir, output_file="parsed_recipes_v2.json", failed_only=False):
    """Parse all PDFs with enhanced parser."""
    all_results = []
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    # Filter for failed files if requested
    if failed_only:
        # Load previous results to identify failed files
        try:
            with open(pdf_dir.parent / "parsed_recipes.json", 'r') as f:
                previous_results = json.load(f)
            
            failed_files = set()
            for result in previous_results:
                if (not result['ingredients'] or 
                    len(result.get('errors', [])) > 0 or
                    result.get('parse_quality_score', 0) < 50):
                    failed_files.add(result['source_file'])
            
            pdf_files = [f for f in pdf_files if f.name in failed_files]
            print(f"Reprocessing {len(pdf_files)} failed files")
        
        except FileNotFoundError:
            print("No previous results found, processing all files")
    
    print(f"\nFound {len(pdf_files)} PDF files to parse")
    print("=" * 80)
    
    high_quality_count = 0
    medium_quality_count = 0
    low_quality_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Parsing: {pdf_file.name}")
        result = parser.parse_pdf(str(pdf_file))
        
        # Categorize by quality
        quality = result['parse_quality_score']
        if quality >= 80:
            high_quality_count += 1
            quality_icon = "🟢"
        elif quality >= 60:
            medium_quality_count += 1
            quality_icon = "🟡"
        else:
            low_quality_count += 1
            quality_icon = "🔴"
        
        # Summary
        ingredient_count = len(result['ingredients'])
        error_count = len(result['errors'])
        warning_count = len(result['warnings'])
        
        print(f"  {quality_icon} Quality: {quality}% | Ingredients: {ingredient_count} | Errors: {error_count} | Warnings: {warning_count}")
        
        if result['metadata'].get('recipe_name'):
            print(f"  📋 Recipe: {result['metadata']['recipe_name']}")
        if result['metadata'].get('recipe_prefix'):
            print(f"  🏷️  Prefix: {result['metadata']['recipe_prefix']}")
        if result['metadata'].get('is_prep_recipe'):
            print(f"  🧪 Type: Prep Recipe")
        
        if error_count > 0:
            print(f"  ⚠️  Errors: {', '.join(result['errors'][:2])}")
        
        all_results.append(result)
    
    # Save results
    output_path = pdf_dir.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Save problematic lines
    if parser.problematic_lines:
        problem_log_path = pdf_dir.parent / "problematic_lines.json"
        with open(problem_log_path, 'w', encoding='utf-8') as f:
            json.dump(parser.problematic_lines, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print(f"ENHANCED PARSING COMPLETE!")
    print(f"Results saved to: {output_path}")
    print(f"Total recipes parsed: {len(all_results)}")
    print(f"Quality distribution:")
    print(f"  🟢 High (80-100%): {high_quality_count}")
    print(f"  🟡 Medium (60-79%): {medium_quality_count}")
    print(f"  🔴 Low (0-59%): {low_quality_count}")
    print(f"Total ingredients found: {sum(len(r['ingredients']) for r in all_results)}")
    print(f"Prep recipes identified: {sum(1 for r in all_results if r['metadata'].get('is_prep_recipe'))}")
    
    if parser.problematic_lines:
        print(f"Problematic lines logged: {len(parser.problematic_lines)}")
        print(f"Problem log saved to: {problem_log_path}")
    
    return all_results


def main():
    """Main entry point."""
    import argparse
    
    parser_args = argparse.ArgumentParser(description='Enhanced PDF Recipe Parser')
    parser_args.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_args.add_argument('--failed-only', action='store_true', help='Only reprocess previously failed files')
    parser_args.add_argument('--test-file', type=str, help='Test single PDF file')
    
    args = parser_args.parse_args()
    
    # Initialize parser
    parser = EnhancedPDFRecipeParser(debug_mode=args.debug)
    
    pdf_dir = Path("/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/updated_recipes_csv_pdf/pdf")
    
    if args.test_file:
        # Test single file
        test_path = pdf_dir / args.test_file
        if test_path.exists():
            print(f"Testing single file: {test_path}")
            result = parser.parse_pdf(str(test_path))
            print(json.dumps(result, indent=2))
        else:
            print(f"File not found: {test_path}")
    else:
        # Process all files
        parse_all_pdfs_enhanced(parser, pdf_dir, failed_only=args.failed_only)


if __name__ == "__main__":
    main()