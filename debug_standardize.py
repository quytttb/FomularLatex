#!/usr/bin/env python3

import re
from base.math_utils import format_fraction_latex, standardize_math_expression

def test_standardize():
    # Test the exact case from output
    test_frac = format_fraction_latex(1, 2)
    print(f'format_fraction_latex(1, 2) = "{test_frac}"')
    
    statement = f"x = {test_frac}"
    print(f'Before standardize: "{statement}"')
    
    result = standardize_math_expression(statement)
    print(f'After standardize: "{result}"')
    
    # Test problematic rules one by one
    import re
    expr = statement
    print(f'\nStep by step:')
    print(f'Original: {expr}')
    
    # Rule 8: Simplify power notation (only for actual powers after variables)
    expr8 = re.sub(r'([a-zA-Z])\^\{1\}', r'\1', expr)
    print(f'After rule 8: {expr8}')
    
    # Rule 11: Fix LaTeX power formatting
    expr11a = re.sub(r'([a-zA-Z])\{(\d+)\}', r'\1^{\2}', expr8)
    print(f'After rule 11a: {expr11a}')
    
    expr11b = re.sub(r'(\d+)([a-zA-Z])\{(\d+)\}', r'\1\2^{\3}', expr11a)
    print(f'After rule 11b: {expr11b}')

if __name__ == '__main__':
    test_standardize()
