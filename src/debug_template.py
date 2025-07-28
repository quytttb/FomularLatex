#!/usr/bin/env python3

from extremum import ExtremumFromTikzQuestion

def debug_template_values():
    print("=== Debug Template Values ===")
    
    q = ExtremumFromTikzQuestion()
    
    # Step 1: Generate parameters
    print("Step 1: Generate parameters")
    q.parameters = q.generate_parameters()
    print(f"Initial template values: so_cuc_tri={q.parameters['so_cuc_tri']}")
    
    # Step 2: Call _ensure_template_values directly 
    print("\nStep 2: Call _ensure_template_values")
    q._ensure_template_values()
    print(f"After _ensure_template_values: so_cuc_tri={q.parameters['so_cuc_tri']}")
    
    # Step 3: Check other template values
    print(f"Template values: so_cuc_tri={q.parameters['so_cuc_tri']}, so_cuc_tieu={q.parameters['so_cuc_tieu']}, so_cuc_dai={q.parameters['so_cuc_dai']}, so_nghiem={q.parameters['so_nghiem']}")
    
    # Step 4: Try to format template
    print("\nStep 4: Try to format template")
    template = "Hàm số có đúng {so_cuc_tri} cực trị"
    try:
        formatted = template.format(**q.parameters)
        print(f"Formatted: {formatted}")
    except Exception as e:
        print(f"Format error: {e}")

if __name__ == "__main__":
    debug_template_values()
