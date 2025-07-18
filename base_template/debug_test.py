#!/usr/bin/env python3

# Test file to debug the extremum_from_tikz.py issue

print("Starting test...")

try:
    import random
    print("✓ random imported")
    
    from typing import Dict, Any, List
    print("✓ typing imported")
    
    # Test base class import
    from base_optimization_question import BaseOptimizationQuestion
    print("✓ BaseOptimizationQuestion imported")
    
    # Test tikz library import
    from tikz_figure_library import (
        generate_monotonicity_table_type1,
        generate_monotonicity_table_type2
    )
    print("✓ tikz_figure_library imported")
    
    print("All imports successful!")
    
    # Test simple parameter generation logic
    A = random.randint(-5, -1)
    B = random.randint(0, 3) 
    C = random.randint(4, 7)
    while B <= A or C <= B:
        A = random.randint(-5, -1)
        B = random.randint(0, 3)
        C = random.randint(4, 7)
    
    print(f"Generated A, B, C: {A}, {B}, {C}")
    
    # Test tikz function call
    params = {"A": A, "B": B, "C": C, "D": -8, "F": -2, "O": 9}
    result1 = generate_monotonicity_table_type1(params)
    print("✓ generate_monotonicity_table_type1 called successfully")
    print("First 100 chars:", result1[:100])
    
    result2 = generate_monotonicity_table_type2(params)
    print("✓ generate_monotonicity_table_type2 called successfully") 
    print("First 100 chars:", result2[:100])
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
