import sys
sys.path.append('.')
from asymptote_mc import generate_detailed_solution, calculate_oblique_asymptote_formula, format_polynomial

# Test case cố định - dễ tính toán
A, B, C = 1, -4, 3  # x^2 - 4x + 3
D, E = 2, -3        # 2x - 3

print("=== TEST ASYMPTOTE_MC.PY ===")
print(f"Coefficients: A={A}, B={B}, C={C}, D={D}, E={E}")
print(f"Function: y = ({A}x^2 + ({B})x + {C}) / ({D}x + ({E}))")

# Calculate slope and intercept
slope, intercept = calculate_oblique_asymptote_formula(A, B, C, D, E)
print(f"Slope: {slope}")
print(f"Intercept: {intercept}")

# Generate solution
solution = generate_detailed_solution(A, B, C, D, E, slope, intercept)
print("\n=== SOLUTION ===")
print(solution)
print("\n=== END ===") 