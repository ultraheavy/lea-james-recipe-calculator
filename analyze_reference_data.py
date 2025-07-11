#!/usr/bin/env python3
"""
Analyze all CSV files in the reference/LJ_DATA_Ref folder
"""
import os
import csv
import pandas as pd
from pathlib import Path
import chardet
from collections import defaultdict

def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # Read first 10KB
        result = chardet.detect(raw_data)
        return result['encoding']

def analyze_csv_file(file_path):
    """Analyze a single CSV file"""
    try:
        # Detect encoding
        encoding = detect_encoding(file_path)
        
        # Try to read with pandas first
        try:
            df = pd.read_csv(file_path, encoding=encoding, nrows=5)
            headers = list(df.columns)
            sample_rows = df.head(3).to_dict('records')
            delimiter = ','  # pandas default
            
        except:
            # Fall back to csv module
            with open(file_path, 'r', encoding=encoding) as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader, [])
                sample_rows = []
                for i, row in enumerate(reader):
                    if i >= 3:
                        break
                    sample_rows.append(row)
        
        # Check for blank or duplicate headers
        blank_headers = [i for i, h in enumerate(headers) if not h or h.strip() == '']
        duplicate_headers = [h for h in headers if headers.count(h) > 1]
        
        return {
            'file_name': os.path.basename(file_path),
            'encoding': encoding,
            'delimiter': delimiter,
            'headers': headers,
            'num_columns': len(headers),
            'sample_rows': sample_rows,
            'blank_headers': blank_headers,
            'duplicate_headers': list(set(duplicate_headers)),
            'error': None
        }
        
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': str(e)
        }

def main():
    """Main analysis function"""
    ref_dir = Path("/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref")
    
    # Group files by type
    files_by_type = defaultdict(list)
    
    for file_path in ref_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            ext = file_path.suffix.lower()
            files_by_type[ext].append(file_path)
    
    print("=== FILE INVENTORY ===\n")
    
    # Sort extensions and display counts
    for ext in sorted(files_by_type.keys()):
        print(f"{ext if ext else 'no extension'}: {len(files_by_type[ext])} files")
    
    print("\n=== CSV FILE ANALYSIS ===\n")
    
    # Analyze CSV files
    csv_files = files_by_type.get('.csv', [])
    
    # Group CSV files by directory
    main_csvs = []
    recipe_csvs = []
    
    for csv_file in csv_files:
        if 'updated_recipes_csv_pdf' in str(csv_file):
            recipe_csvs.append(csv_file)
        else:
            main_csvs.append(csv_file)
    
    # Analyze main CSV files
    if main_csvs:
        print("## Main CSV Files:\n")
        for csv_file in sorted(main_csvs):
            analysis = analyze_csv_file(csv_file)
            
            print(f"### {analysis['file_name']}")
            if analysis.get('error'):
                print(f"   ERROR: {analysis['error']}")
            else:
                print(f"   Encoding: {analysis['encoding']}")
                print(f"   Delimiter: '{analysis['delimiter']}'")
                print(f"   Columns: {analysis['num_columns']}")
                if analysis['blank_headers']:
                    print(f"   ⚠️  Blank headers at positions: {analysis['blank_headers']}")
                if analysis['duplicate_headers']:
                    print(f"   ⚠️  Duplicate headers: {analysis['duplicate_headers']}")
                print(f"\n   Headers:")
                for i, header in enumerate(analysis['headers']):
                    print(f"      [{i}] {header}")
                print(f"\n   Sample rows (first 3):")
                for i, row in enumerate(analysis['sample_rows']):
                    print(f"      Row {i+1}: {row}")
            print()
    
    # Analyze recipe CSV files (sample a few)
    if recipe_csvs:
        print("\n## Recipe CSV Files (sample analysis):\n")
        print(f"Total recipe CSV files: {len(recipe_csvs)}\n")
        
        # Sample first 3 unique recipe types
        sampled = []
        for csv_file in sorted(recipe_csvs):
            base_name = os.path.basename(csv_file).split('_')[0]
            if base_name not in [os.path.basename(s).split('_')[0] for s in sampled]:
                sampled.append(csv_file)
                if len(sampled) >= 3:
                    break
        
        for csv_file in sampled:
            analysis = analyze_csv_file(csv_file)
            
            print(f"### {analysis['file_name']}")
            if analysis.get('error'):
                print(f"   ERROR: {analysis['error']}")
            else:
                print(f"   Encoding: {analysis['encoding']}")
                print(f"   Delimiter: '{analysis['delimiter']}'")
                print(f"   Columns: {analysis['num_columns']}")
                if analysis['blank_headers']:
                    print(f"   ⚠️  Blank headers at positions: {analysis['blank_headers']}")
                if analysis['duplicate_headers']:
                    print(f"   ⚠️  Duplicate headers: {analysis['duplicate_headers']}")
                print(f"\n   Headers:")
                for i, header in enumerate(analysis['headers']):
                    print(f"      [{i}] {header}")
                print(f"\n   Sample rows (first 3):")
                for i, row in enumerate(analysis['sample_rows']):
                    print(f"      Row {i+1}: {row}")
            print()
    
    # List PDF files
    pdf_files = files_by_type.get('.pdf', [])
    if pdf_files:
        print("\n=== PDF FILES ===\n")
        print(f"Total PDF files: {len(pdf_files)}")
        print("\nSample PDF files:")
        for pdf_file in sorted(pdf_files)[:10]:
            print(f"   - {os.path.basename(pdf_file)}")
        if len(pdf_files) > 10:
            print(f"   ... and {len(pdf_files) - 10} more")

if __name__ == "__main__":
    main()