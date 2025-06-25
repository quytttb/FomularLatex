#!/usr/bin/env python3
"""
Fix test files to use correct generate_question(question_number) signature.
"""

import os
import re

def fix_test_file(file_path):
    """Fix a test file to use correct generate_question signature."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace generate_question() with generate_question(1) or appropriate number
    # Pattern 1: Simple calls
    content = re.sub(r'generator\.generate_question\(\)', 'generator.generate_question(1)', content)
    content = re.sub(r'([a-zA-Z_]+)\.generate_question\(\)', r'\1.generate_question(1)', content)
    
    # Pattern 2: In loops - use loop variable
    # For range loops
    content = re.sub(
        r'for (\w+) in range\((\d+)\):\s*\n(\s*)question = generator\.generate_question\(1\)',
        r'for \1 in range(\2):\n\3question = generator.generate_question(\1+1)',
        content,
        flags=re.MULTILINE
    )
    
    content = re.sub(
        r'for (\w+) in range\((\d+)\):\s*\n(\s*)([a-zA-Z_]+)\.generate_question\(1\)',
        r'for \1 in range(\2):\n\3\4.generate_question(\1+1)',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 3: Append calls
    content = re.sub(
        r'questions\.append\(([a-zA-Z_]+)\.generate_question\(1\)\)',
        r'questions.append(\1.generate_question(len(questions)+1))',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def main():
    """Fix all test files."""
    test_dir = os.path.dirname(__file__)
    
    test_files = [
        'test_integration.py',
        'test_edge_cases.py'
    ]
    
    for test_file in test_files:
        file_path = os.path.join(test_dir, test_file)
        if os.path.exists(file_path):
            fix_test_file(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == '__main__':
    main()
