#!/usr/bin/env python3
"""
Generator for True/False questions about triangles in 3D space.

This script generates Vietnamese true/false questions about:
- Foot of angle bisector from vertex to opposite side
- Length of altitudes in triangles
- Angles in triangles
- Other triangle properties

Usage:
python3 true_false_triangle_questions.py [number_of_questions]
xelatex true_false_triangle_questions.tex
"""

import random
import sys
import logging
import math
from fractions import Fraction

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a pool of letters for vertices
LETTER_POOL = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T']

def format_fraction_latex(num, denom):
    """Format a fraction for LaTeX display."""
    if denom == 0:
        return "undefined"
    
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

def format_point(x, y, z):
    """Format a 3D point (x, y, z) for LaTeX."""
    def format_value(val):
        # Handle -0.0 case
        if val == 0:
            val = 0
        if isinstance(val, int):
            return str(val)
        elif isinstance(val, float):
            return f"{val:.0f}" if val == int(val) else f"{val:.2f}"
        else:  # Fraction
            return format_fraction_latex(val.numerator, val.denominator)
    
    x_str = format_value(x)
    y_str = format_value(y)
    z_str = format_value(z)
    return f"({x_str}, {y_str}, {z_str})"  # Use comma like oxy_true_false.py

def format_subtraction(a, b):
    """Format subtraction a - b for LaTeX, adding parentheses if b is negative."""
    def format_value(val):
        if isinstance(val, int):
            return str(val)
        elif isinstance(val, float):
            return f"{val:.2f}"
        else:  # Fraction
            return format_fraction_latex(val.numerator, val.denominator)
    
    a_str = format_value(a)
    b_str = format_value(b)
    if b < 0:
        return f"{a_str}-({b_str})"
    return f"{a_str}-{b_str}"

def vector_magnitude(v):
    """Calculate magnitude of vector v = (x, y, z)."""
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def vector_magnitude_exact(v):
    """Calculate exact magnitude of vector v = (x, y, z) as simplified square root."""
    square_sum = v[0]**2 + v[1]**2 + v[2]**2
    return simplify_square_root(square_sum)

def simplify_square_root(n):
    """Simplify square root of n into the form (coefficient, radicand)."""
    if n == 0:
        return (0, 1)
    if n < 0:
        return (0, 1)  # Handle negative case
    
    # Find the largest perfect square factor
    perfect_square = 1
    remaining = n
    
    i = 2
    while i * i <= remaining:
        while remaining % (i * i) == 0:
            perfect_square *= i
            remaining //= (i * i)
        i += 1
    
    return (perfect_square, remaining)

def format_exact_magnitude(coeff, radicand):
    """Format exact magnitude for LaTeX."""
    if radicand == 1:
        return str(coeff)
    elif coeff == 1:
        if radicand == 1:
            return "1"
        else:
            return f"\\sqrt{{{radicand}}}"
    else:
        return f"{coeff}\\sqrt{{{radicand}}}"

def format_exact_fraction(numerator_coeff, numerator_rad, denominator_coeff, denominator_rad):
    """Format exact fraction with square roots for LaTeX."""
    # Simplify by canceling common factors
    from math import gcd
    
    # Find GCD of coefficients
    coeff_gcd = gcd(numerator_coeff, denominator_coeff)
    numerator_coeff //= coeff_gcd
    denominator_coeff //= coeff_gcd
    
    # Handle radicands
    if numerator_rad == denominator_rad:
        # Same radicand, they cancel out
        if denominator_coeff == 1:
            return str(numerator_coeff)
        else:
            return f"\\frac{{{numerator_coeff}}}{{{denominator_coeff}}}"
    else:
        # Different radicands
        num_str = format_exact_magnitude(numerator_coeff, numerator_rad)
        den_str = format_exact_magnitude(denominator_coeff, denominator_rad)
        
        if denominator_coeff == 1 and denominator_rad == 1:
            return num_str
        else:
            return f"\\frac{{{num_str}}}{{{den_str}}}"

def vector_dot_product(v1, v2):
    """Calculate dot product of vectors v1 and v2."""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def vector_cross_product(v1, v2):
    """Calculate cross product of vectors v1 and v2."""
    return (
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    )

def calculate_foot_of_angle_bisector(A, B, C):
    """Calculate foot of angle bisector from A to BC using the angle bisector theorem."""
    # Using angle bisector theorem: BD/DC = AB/AC
    # This means D divides BC in the ratio AB:AC
    
    AB_length = vector_magnitude((B[0] - A[0], B[1] - A[1], B[2] - A[2]))
    AC_length = vector_magnitude((C[0] - A[0], C[1] - A[1], C[2] - A[2]))
    
    if AB_length == 0 or AC_length == 0:
        return B  # Degenerate case
    
    # D = (AC*B + AB*C)/(AB + AC)
    # This comes from: BD/DC = AB/AC => DC = (AC/(AB+AC))*BC and BD = (AB/(AB+AC))*BC
    ratio_sum = AB_length + AC_length
    
    D = (
        (AC_length * B[0] + AB_length * C[0]) / ratio_sum,
        (AC_length * B[1] + AB_length * C[1]) / ratio_sum,
        (AC_length * B[2] + AB_length * C[2]) / ratio_sum
    )
    
    return D

def calculate_foot_of_angle_bisector_exact(A, B, C):
    """Calculate foot of angle bisector from A to BC using exact arithmetic."""
    # Using angle bisector theorem: BD/DC = AB/AC
    # This means D divides BC in the ratio AB:AC
    
    AB_vec = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC_vec = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    
    AB_sq = AB_vec[0]**2 + AB_vec[1]**2 + AB_vec[2]**2
    AC_sq = AC_vec[0]**2 + AC_vec[1]**2 + AC_vec[2]**2
    
    AB_exact = simplify_square_root(AB_sq)
    AC_exact = simplify_square_root(AC_sq)
    
    if AB_sq == 0 or AC_sq == 0:
        return B, (1, 1), (1, 1)  # Degenerate case
    
    # Store exact lengths for later use in explanation
    AB_length_exact = AB_exact
    AC_length_exact = AC_exact
    
    # Calculate D using exact ratios
    # D = (AC*B + AB*C)/(AB + AC)
    # We'll work with the squared lengths to avoid floating point
    
    # For now, use approximate calculation for coordinates
    AB_length = math.sqrt(AB_sq)
    AC_length = math.sqrt(AC_sq)
    ratio_sum = AB_length + AC_length
    
    D = (
        (AC_length * B[0] + AB_length * C[0]) / ratio_sum,
        (AC_length * B[1] + AB_length * C[1]) / ratio_sum,
        (AC_length * B[2] + AB_length * C[2]) / ratio_sum
    )
    
    return D, AB_length_exact, AC_length_exact

def calculate_foot_of_perpendicular(A, B, C):
    """Calculate foot of perpendicular from A to BC."""
    # Vector BC
    BC = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
    # Vector BA
    BA = (A[0] - B[0], A[1] - B[1], A[2] - B[2])
    
    # Parameter t for point D on BC: D = B + t*BC
    # AD perpendicular to BC means AD·BC = 0
    # (A - (B + t*BC))·BC = 0
    # (BA - t*BC)·BC = 0
    # BA·BC - t*(BC·BC) = 0
    # t = (BA·BC)/(BC·BC)
    
    dot_BA_BC = vector_dot_product(BA, BC)
    dot_BC_BC = vector_dot_product(BC, BC)
    
    if dot_BC_BC == 0:  # B and C are the same point
        return B
    
    t = dot_BA_BC / dot_BC_BC
    
    # D = B + t*BC
    D = (
        B[0] + t * BC[0],
        B[1] + t * BC[1],
        B[2] + t * BC[2]
    )
    
    return D

def format_vector_latex(v, name=""):
    """Format vector for LaTeX display."""
    x_str = f"{v[0]:.0f}" if v[0] == int(v[0]) else f"{v[0]:.2f}"
    y_str = f"{v[1]:.0f}" if v[1] == int(v[1]) else f"{v[1]:.2f}"
    z_str = f"{v[2]:.0f}" if v[2] == int(v[2]) else f"{v[2]:.2f}"
    if name:
        return f"\\overrightarrow{{{name}}} = ({x_str}, {y_str}, {z_str})"
    return f"({x_str}, {y_str}, {z_str})"

def calculate_triangle_area(A, B, C):
    """Calculate area of triangle ABC using cross product."""
    AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    
    cross = vector_cross_product(AB, AC)
    magnitude = vector_magnitude(cross)
    
    return magnitude / 2

def calculate_triangle_area_exact(A, B, C):
    """Calculate exact area of triangle ABC using cross product."""
    AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    
    cross = vector_cross_product(AB, AC)
    cross_magnitude_sq = cross[0]**2 + cross[1]**2 + cross[2]**2
    
    # Area = (1/2) * |cross product|
    # So Area^2 = (1/4) * |cross product|^2
    cross_exact = simplify_square_root(cross_magnitude_sq)
    
    # Return (coefficient/2, radicand) for area = (coefficient/2) * sqrt(radicand)
    return (cross_exact[0], cross_exact[1], 2)  # (coeff, radicand, denominator)

def calculate_altitude_length(A, B, C, from_vertex='A'):
    """Calculate altitude length from specified vertex."""
    area = calculate_triangle_area(A, B, C)
    
    if from_vertex == 'A':
        base_length = vector_magnitude((C[0] - B[0], C[1] - B[1], C[2] - B[2]))
    elif from_vertex == 'B':
        base_length = vector_magnitude((C[0] - A[0], C[1] - A[1], C[2] - A[2]))
    else:  # from_vertex == 'C'
        base_length = vector_magnitude((B[0] - A[0], B[1] - A[1], B[2] - A[2]))
    
    if base_length == 0:
        return 0
    
    return (2 * area) / base_length

def calculate_altitude_length_exact(A, B, C, from_vertex='A'):
    """Calculate exact altitude length from specified vertex."""
    area_coeff, area_rad, area_denom = calculate_triangle_area_exact(A, B, C)
    
    if from_vertex == 'A':
        base_vec = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
    elif from_vertex == 'B':
        base_vec = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    else:  # from_vertex == 'C'
        base_vec = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    
    base_length_sq = base_vec[0]**2 + base_vec[1]**2 + base_vec[2]**2
    base_exact = simplify_square_root(base_length_sq)
    
    if base_length_sq == 0:
        return (0, 1, 1)  # Degenerate case
    
    # Altitude = 2 * Area / Base
    # = 2 * (area_coeff * sqrt(area_rad) / area_denom) / (base_coeff * sqrt(base_rad))
    # = (2 * area_coeff * sqrt(area_rad)) / (area_denom * base_coeff * sqrt(base_rad))
    
    numerator_coeff = 2 * area_coeff
    numerator_rad = area_rad
    denominator_coeff = area_denom * base_exact[0]
    denominator_rad = base_exact[1]
    
    return (numerator_coeff, numerator_rad, denominator_coeff, denominator_rad)

def calculate_angle(vertex, point1, point2):
    """Calculate angle at vertex between lines to point1 and point2."""
    v1 = (point1[0] - vertex[0], point1[1] - vertex[1], point1[2] - vertex[2])
    v2 = (point2[0] - vertex[0], point2[1] - vertex[1], point2[2] - vertex[2])
    
    dot = vector_dot_product(v1, v2)
    mag1 = vector_magnitude(v1)
    mag2 = vector_magnitude(v2)
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    cos_angle = dot / (mag1 * mag2)
    # Clamp to [-1, 1] to avoid floating point errors
    cos_angle = max(-1, min(1, cos_angle))
    
    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg

def generate_triangle_coordinates():
    """Generate coordinates for a valid triangle using patterns from solver.tex."""
    # Generate random base point A
    x_a = random.randint(-3, 3)
    y_a = random.randint(-3, 3) 
    z_a = random.randint(-3, 3)
    A = (x_a, y_a, z_a)
    
    # Solver.tex patterns - các bộ điểm tạo tam giác đặc biệt
    solver_patterns = [
        # Pattern 1: B(x_a ± 4; y_a; z_a ± 3) và C(x_a ± 6; y_a ± 8; z_a)
        {
            'B_offset': [(4, 0, 3), (4, 0, -3), (-4, 0, 3), (-4, 0, -3)],
            'C_offset': [(6, 8, 0), (6, -8, 0), (-6, 8, 0), (-6, -8, 0)]
        },
        # Pattern 2: B(x_a ± 4; y_a ± 2; z_a ± 6) và C(x_a ± 2; y_a ± 1; z_a ± 3) - So le dấu một phần
        {
            'B_offset': [(4, 2, 6), (4, 2, -6), (4, -2, 6), (4, -2, -6), 
                        (-4, 2, 6), (-4, 2, -6), (-4, -2, 6), (-4, -2, -6)],
            'C_offset': [(-2, 1, 3), (-2, 1, -3), (-2, -1, 3), (-2, -1, -3),
                        (2, 1, 3), (2, 1, -3), (2, -1, 3), (2, -1, -3)]
        },
        # Pattern 3: B(x_a ± 4; y_a ± 2; z_a ± 1) và C(x_a ± 13; y_a ± 4; z_a ± 2)
        {
            'B_offset': [(4, 2, 1), (4, 2, -1), (4, -2, 1), (4, -2, -1),
                        (-4, 2, 1), (-4, 2, -1), (-4, -2, 1), (-4, -2, -1)],
            'C_offset': [(13, 4, 2), (13, 4, -2), (13, -4, 2), (13, -4, -2),
                        (-13, 4, 2), (-13, 4, -2), (-13, -4, 2), (-13, -4, -2)]
        },
        # Pattern 4: B(x_a ± 3; y_a ± 2; z_a) và C(x_a ± 10; y_a ± 4; z_a ± 1)
        {
            'B_offset': [(3, 2, 0), (3, -2, 0), (-3, 2, 0), (-3, -2, 0)],
            'C_offset': [(10, 4, 1), (10, 4, -1), (10, -4, 1), (10, -4, -1),
                        (-10, 4, 1), (-10, 4, -1), (-10, -4, 1), (-10, -4, -1)]
        }
    ]
    
    # Choose random pattern
    pattern = random.choice(solver_patterns)
    
    # Choose random B and C offsets from the pattern
    B_offset = random.choice(pattern['B_offset'])
    C_offset = random.choice(pattern['C_offset'])
    
    # Apply offsets to base point A
    B = (x_a + B_offset[0], y_a + B_offset[1], z_a + B_offset[2])
    C = (x_a + C_offset[0], y_a + C_offset[1], z_a + C_offset[2])
    
    # Hoán đổi vị trí hoành độ, tung độ, cao độ (như ghi chú trong solver.tex)
    coordinate_permutations = [
        (0, 1, 2),  # x, y, z (không đổi)
        (0, 2, 1),  # x, z, y
        (1, 0, 2),  # y, x, z
        (1, 2, 0),  # y, z, x
        (2, 0, 1),  # z, x, y
        (2, 1, 0)   # z, y, x
    ]
    
    perm = random.choice(coordinate_permutations)
    
    # Apply permutation to all points
    A = (A[perm[0]], A[perm[1]], A[perm[2]])
    B = (B[perm[0]], B[perm[1]], B[perm[2]])
    C = (C[perm[0]], C[perm[1]], C[perm[2]])
    
    # Verify triangle is valid (non-zero area)
    area = calculate_triangle_area(A, B, C)
    if area < 0.1:  # If area is too small, use a guaranteed valid triangle
        # Use pattern 1 with safe values
        A = (0, 0, 0)
        B = (4, 0, 3)
        C = (6, 8, 0)
    
    return A, B, C

def generate_question(question_number):
    """Generate a true/false question about triangles."""
    logging.info(f"Generating question {question_number}")
    
    # Generate triangle coordinates
    A, B, C = generate_triangle_coordinates()
    
    # Chọn ngẫu nhiên 3 nhãn điểm khác nhau từ LETTER_POOL (loại trừ 'D' vì đã dùng cho điểm khác)
    available_letters = [letter for letter in LETTER_POOL if letter != 'D']
    labels = random.sample(available_letters, 3)
    l1, l2, l3 = labels[0], labels[1], labels[2]
    vertices = {l1: A, l2: B, l3: C}
    
    logging.info(f"Triangle: {l1}{A}, {l2}{B}, {l3}{C}")
    
    # Generate 4 propositions (a, b, c, d)
    propositions = []
    
    # Proposition a: Foot of angle bisector - always from l1 to l2l3 (không cố định là A, B, C)
    from_vertex = l1  # Always from l1
    foot, AB_exact, AC_exact = calculate_foot_of_angle_bisector_exact(A, B, C)  # Always l1 to l2l3
    prop_text = f"Tọa độ chân đường phân giác kẻ từ {l1} xuống {l2}{l3}"
    base_edge = f"{l2}{l3}"
    
    # Format foot coordinates as exact fractions
    from fractions import Fraction
    foot_x_frac = Fraction(foot[0]).limit_denominator()
    foot_y_frac = Fraction(foot[1]).limit_denominator()
    foot_z_frac = Fraction(foot[2]).limit_denominator()
    
    def format_coord_frac(frac):
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    true_foot = f"({format_coord_frac(foot_x_frac)}, {format_coord_frac(foot_y_frac)}, {format_coord_frac(foot_z_frac)})"
    
    # Create false foot by modifying one coordinate  
    false_foot_x = foot_x_frac + Fraction(random.choice([-1, 1]))
    false_foot = f"({format_coord_frac(false_foot_x)}, {format_coord_frac(foot_y_frac)}, {format_coord_frac(foot_z_frac)})"
    
    propositions.append({
        'true': f"{prop_text} là \\( D{true_foot} \\).",
        'false': f"{prop_text} là \\( D{false_foot} \\).",
        'from_vertex': from_vertex,
        'base_edge': base_edge,
        'foot': foot,
        'AB_exact': AB_exact,
        'AC_exact': AC_exact
    })
    
    # Proposition b: Altitude length
    altitude_from = random.choice([l1, l2, l3])
    if altitude_from == l1:
        altitude_exact = calculate_altitude_length_exact(A, B, C, 'A')
        prop_text = f"Độ dài đường cao kẻ từ {l1} trong \\( \\triangle {l1}{l2}{l3} \\)"
        altitude_name = f"{l1}H"
    elif altitude_from == l2:
        altitude_exact = calculate_altitude_length_exact(A, B, C, 'B')
        prop_text = f"Độ dài đường cao kẻ từ {l2} trong \\( \\triangle {l1}{l2}{l3} \\)"
        altitude_name = f"{l2}K"
    else:
        altitude_exact = calculate_altitude_length_exact(A, B, C, 'C')
        prop_text = f"Độ dài đường cao kẻ từ {l3} trong \\( \\triangle {l1}{l2}{l3} \\)"
        altitude_name = f"{l3}I"
    
    # Format exact altitude
    true_altitude_str = format_exact_fraction(altitude_exact[0], altitude_exact[1], altitude_exact[2], altitude_exact[3])
    
    # Create a false altitude by slightly modifying the coefficients
    false_altitude_coeff = altitude_exact[0] + random.choice([-1, 1])
    false_altitude_str = format_exact_fraction(false_altitude_coeff, altitude_exact[1], altitude_exact[2], altitude_exact[3])
    
    propositions.append({
        'true': f"{prop_text} = \\( {true_altitude_str} \\).",
        'false': f"{prop_text} = \\( {false_altitude_str} \\).",
        'altitude_from': altitude_from,
        'altitude_name': altitude_name,
        'altitude_exact': altitude_exact
    })
    
    # Proposition c: Angle
    angle_vertex = random.choice([l1, l2, l3])
    if angle_vertex == l1:
        angle = calculate_angle(A, B, C)
        prop_text = f"\\( \\triangle {l1}{l2}{l3} \\) có góc \\( \\widehat{{{l2}{l1}{l3}}} \\)"
        angle_name = f"\\widehat{{{l2}{l1}{l3}}}"
    elif angle_vertex == l2:
        angle = calculate_angle(B, A, C)
        prop_text = f"\\( \\triangle {l1}{l2}{l3} \\) có góc \\( \\widehat{{{l1}{l2}{l3}}} \\)"
        angle_name = f"\\widehat{{{l1}{l2}{l3}}}"
    else:
        angle = calculate_angle(C, A, B)
        prop_text = f"\\( \\triangle {l1}{l2}{l3} \\) có góc \\( \\widehat{{{l1}{l3}{l2}}} \\)"
        angle_name = f"\\widehat{{{l1}{l3}{l2}}}"
    
    true_angle = f"{angle:.1f}°"
    false_angle = f"{angle + random.choice([-5, 5]):.1f}°"
    
    propositions.append({
        'true': f"{prop_text} = \\( {true_angle} \\).",
        'false': f"{prop_text} = \\( {false_angle} \\).",
        'angle_vertex': angle_vertex,
        'angle_name': angle_name,
        'angle_value': angle
    })
    
    # Proposition d: Coplanar condition for 4 points l1, l2, l3, D
    # Generate D(x, y, a*m + b) where a, b are nice integers and m is the variable
    x_d, y_d = random.randint(-5, 5), random.randint(-5, 5)
    a_coeff = random.choice([1, 2, 3, -1, -2, -3])  # Nice integer coefficient
    b_const = random.randint(-10, 10)  # Nice integer constant
    
    # Calculate the value of m for coplanarity using the determinant condition
    # For 4 points to be coplanar: det(AB, AC, AD) = 0
    # Where AB = B - A, AC = C - A, AD = D - A
    AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    
    # For D(x_d, y_d, a*m + b), AD = (x_d - A[0], y_d - A[1], a*m + b - A[2])
    # The determinant is calculated using cofactor expansion
    # det = AB[0]*(AC[1]*(a*m + b - A[2]) - AC[2]*(y_d - A[1])) 
    #     - AB[1]*(AC[0]*(a*m + b - A[2]) - AC[2]*(x_d - A[0])) 
    #     + AB[2]*(AC[0]*(y_d - A[1]) - AC[1]*(x_d - A[0]))
    
    # Use the SAME logic as in solution explanation to ensure consistency
    # Calculate vectors and cross product
    AB_vector = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC_vector = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    cross_product = (
        AB_vector[1] * AC_vector[2] - AB_vector[2] * AC_vector[1],
        AB_vector[2] * AC_vector[0] - AB_vector[0] * AC_vector[2], 
        AB_vector[0] * AC_vector[1] - AB_vector[1] * AC_vector[0]
    )
    
    # Calculate components EXACTLY like in solution explanation
    x_d_minus_ax = x_d - A[0]
    y_d_minus_ay = y_d - A[1]
    z_simplified_const = b_const - A[2]
    
    # Calculate individual terms
    term1 = cross_product[0] * x_d_minus_ax
    term2 = cross_product[1] * y_d_minus_ay
    constant_from_z = cross_product[2] * z_simplified_const
    coeff_of_m = cross_product[2] * a_coeff
    
    # Total constant = term1 + term2 + constant_from_z
    total_constant = term1 + term2 + constant_from_z
    
    # Ensure we don't get coefficient of m = 0, which makes the problem degenerate
    attempt_count = 0
    while coeff_of_m == 0 and attempt_count < 5:
        # Try different parameters
        a_coeff = random.choice([1, 2, 3, -1, -2, -3])
        x_d, y_d = random.randint(-5, 5), random.randint(-5, 5)
        b_const = random.randint(-10, 10)
        
        # Recalculate with new parameters
        x_d_minus_ax = x_d - A[0]
        y_d_minus_ay = y_d - A[1]
        z_simplified_const = b_const - A[2]
        
        term1 = cross_product[0] * x_d_minus_ax
        term2 = cross_product[1] * y_d_minus_ay
        constant_from_z = cross_product[2] * z_simplified_const
        coeff_of_m = cross_product[2] * a_coeff
        total_constant = term1 + term2 + constant_from_z
        attempt_count += 1
    
    # Calculate the CORRECT m_value for the solution first using exact fractions
    if coeff_of_m != 0:
        from fractions import Fraction
        # Keep as exact fraction to avoid rounding errors
        correct_m_fraction = Fraction(-total_constant, coeff_of_m)
        correct_m_value = correct_m_fraction  # Store exact fraction
    else:
        # For degenerate case, use a simple fallback
        correct_m_value = None  # Will be handled specially
    
    # Store the correct value to be used in solution
    solution_m_value = correct_m_value
    
    # For proposition, we'll decide later whether to use correct or incorrect value
    # Create false value by adding/subtracting a small amount
    if correct_m_value is not None:
        from fractions import Fraction
        false_m_value = correct_m_value + Fraction(random.choice([-1, -2, 1, 2]), random.choice([1, 2]))
    else:
        false_m_value = Fraction(1, 1)
    
    # Format the proposition text with proper z expression
    if a_coeff == 1:
        if b_const >= 0:
            z_expr = f"m + {b_const}"
        else:
            z_expr = f"m - {abs(b_const)}"
    elif a_coeff == -1:
        if b_const >= 0:
            z_expr = f"-m + {b_const}"
        else:
            z_expr = f"-m - {abs(b_const)}"
    else:
        if b_const >= 0:
            z_expr = f"{a_coeff}m + {b_const}"
        else:
            z_expr = f"{a_coeff}m - {abs(b_const)}"
    
    # Format m_value and false_m_value as fractions for display
    def format_m_value(value):
        if value is None:
            return "\\text{vô nghiệm}"
        from fractions import Fraction
        if isinstance(value, Fraction):
            # Already a fraction, use directly
            frac = value
        elif isinstance(value, (int, float)):
            # Convert to fraction
            frac = Fraction(value).limit_denominator()
        else:
            return str(value)
        
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            if frac.numerator < 0:
                return f"\\(-\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}\\)"
            else:
                return f"\\(\\frac{{{frac.numerator}}}{{{frac.denominator}}}\\)"
    
    # Format correct and false values
    correct_m_formatted = format_m_value(correct_m_value)
    false_m_formatted = format_m_value(false_m_value)
    
    propositions.append({
        'true': f"Bốn điểm {l1}, {l2}, {l3}, D({x_d}; {y_d}; {z_expr}) đồng phẳng khi m = {correct_m_formatted}.",
        'false': f"Bốn điểm {l1}, {l2}, {l3}, D({x_d}; {y_d}; {z_expr}) đồng phẳng khi m = {false_m_formatted}.",
        'x_d': x_d,
        'y_d': y_d,
        'a_coeff': a_coeff,
        'b_const': b_const,
        'z_expr': z_expr,
        'correct_m_value': correct_m_value,
        'false_m_value': false_m_value,
        'solution_m_value': solution_m_value  # Store for solution consistency
    })
    
    # Randomly determine which propositions are true
    num_true = random.randint(1, 4)
    true_indices = random.sample(range(4), num_true)
    
    # Format question stem
    question_stem = (
        f"Cho \\( \\triangle {l1}{l2}{l3} \\) với "
        f"\\( {l1}{format_point(A[0], A[1], A[2])} \\), "
        f"\\( {l2}{format_point(B[0], B[1], B[2])} \\), "
        f"\\( {l3}{format_point(C[0], C[1], C[2])} \\). "
        f"Chọn các lựa chọn đúng:"
    )
    
    option_labels = ['a', 'b', 'c', 'd']
    question_content = f"Câu {question_number}: {question_stem}\n\n"
    
    # Add propositions with correct marking style
    for i, (label, prop) in enumerate(zip(option_labels, propositions)):
        is_true = i in true_indices
        prop_text = prop['true'] if is_true else prop['false']
        marker = '*' if is_true else ''
        question_content += f"{marker}{label}) {prop_text}\n\n"
    
    # Add solution
    
    # Add calculation details for ALL answers (both correct and incorrect) with bold formatting
    # For proposition a - foot of perpendicular (always from l1 to l2l3)
    foot_data = propositions[0]
    from_vertex = l1
    vertex_coord = A
    base_start, base_end = B, C
    base_start_name, base_end_name = l2, l3
    
    # Calculate vectors for detailed explanation
    foot_coord = foot_data['foot']
    BA_vector = (A[0] - B[0], A[1] - B[1], A[2] - B[2])
    BC_vector = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
    BD_vector = (foot_coord[0] - B[0], foot_coord[1] - B[1], foot_coord[2] - B[2])
    
    # Get exact lengths from the calculation
    AB_exact = foot_data['AB_exact']
    AC_exact = foot_data['AC_exact']
    
    # Format exact lengths
    AB_str = format_exact_magnitude(AB_exact[0], AB_exact[1])
    AC_str = format_exact_magnitude(AC_exact[0], AC_exact[1])
    
    # Calculate exact ratio AB/AC
    ratio_str = format_exact_fraction(AB_exact[0], AB_exact[1], AC_exact[0], AC_exact[1])
    
    # Calculate the simplified sum (ratio + 1) for cleaner display
    # AB_exact = (coeff, radicand), AC_exact = (coeff, radicand)
    # ratio = AB/AC = (AB_coeff * sqrt(AB_rad)) / (AC_coeff * sqrt(AC_rad))
    
    if AB_exact[1] == AC_exact[1]:  # Same radicand
        # ratio = AB_coeff/AC_coeff, so ratio + 1 = (AB_coeff + AC_coeff)/AC_coeff
        ratio_num = AB_exact[0]  # AB coefficient
        ratio_den = AC_exact[0]  # AC coefficient
        total_num = ratio_num + ratio_den  # (AB_coeff + AC_coeff)
        total_den = ratio_den  # AC_coeff
        
        # Simplify the fraction
        from math import gcd
        common_divisor = gcd(abs(total_num), abs(total_den))
        total_num //= common_divisor
        total_den //= common_divisor
        
        if total_den == 1:
            ratio_plus_one_str = str(total_num)
        else:
            ratio_plus_one_str = f"\\frac{{{total_num}}}{{{total_den}}}"
    else:
        # Different radicands, keep as (ratio + 1)
        ratio_plus_one_str = f"({ratio_str} + 1)"
    
    # Format exact foot coordinates for display in solution
    foot_exact = foot_data['foot']
    foot_x_exact = Fraction(foot_exact[0]).limit_denominator()
    foot_y_exact = Fraction(foot_exact[1]).limit_denominator()
    foot_z_exact = Fraction(foot_exact[2]).limit_denominator()
    
    def format_exact_coord(frac):
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    exact_foot_display = f"({format_exact_coord(foot_x_exact)}, {format_exact_coord(foot_y_exact)}, {format_exact_coord(foot_z_exact)})"
    
    foot_formula_explanation = (
        f"\\(\\left. \\begin{{array}}{{l}}\n"
        f"{l1}{l2} = {AB_str} \\\\\n" 
        f"{l1}{l3} = {AC_str} \\\\\n"
        f"\\text{{Do {l1}D là đường phân giác của }} \\widehat{{{l2}{l1}{l3}}}\n"
        f"\\end{{array}} \\right\\}} \\Rightarrow \\frac{{{l1}{l2}}}{{{l1}{l3}}} = \\frac{{{l2}D}}{{D{l3}}} = {ratio_str}\\)\n\n"
        f"\\(\\Rightarrow \\overrightarrow{{{l2}D}} = {ratio_str}\\overrightarrow{{D{l3}}} \\Leftrightarrow D - {l2} = {ratio_str}({l3} - D) \\Leftrightarrow {ratio_plus_one_str}D = {ratio_str}{l3} + {l2}\\)\n\n"
        f"\\(\\Leftrightarrow D = \\frac{{{ratio_str}{l3} + {l2}}}{{{ratio_plus_one_str}}} = \\frac{{{ratio_str}{format_point(C[0], C[1], C[2])} + {format_point(B[0], B[1], B[2])}}}{{{ratio_plus_one_str}}} = {exact_foot_display}\\)"
    )
    
    if 0 in true_indices:
        question_content += f"Lời giải cho mệnh đề a):\n\n{foot_formula_explanation}\n\n"
    else:
        question_content += f"Lời giải cho mệnh đề a):\n\n{foot_formula_explanation}\n\n"
    
    # For proposition b - altitude length with detailed calculation using exact values
    alt_data = propositions[1]
    altitude_from = alt_data['altitude_from']
    altitude_exact = alt_data['altitude_exact']
    
    # Calculate exact area and cross product
    area_coeff, area_rad, area_denom = calculate_triangle_area_exact(A, B, C)
    AB_vector = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC_vector = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    cross_product = vector_cross_product(AB_vector, AC_vector)
    cross_exact = vector_magnitude_exact(cross_product)
    
    # Determine base edge and calculate exact base length
    if altitude_from == l1:
        base_edge_name = f'{l2}{l3}'
        base_vec = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
        altitude_name = f'{l1}H'
    elif altitude_from == l2:
        base_edge_name = f'{l1}{l3}'
        base_vec = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
        altitude_name = f'{l2}K'
    else:
        base_edge_name = f'{l1}{l2}'
        base_vec = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        altitude_name = f'{l3}I'
    
    base_exact = vector_magnitude_exact(base_vec)
    
    # Format strings
    cross_str = format_exact_magnitude(cross_exact[0], cross_exact[1])
    area_str = format_exact_fraction(area_coeff, area_rad, area_denom, 1)
    base_str = format_exact_magnitude(base_exact[0], base_exact[1])
    altitude_str = format_exact_fraction(altitude_exact[0], altitude_exact[1], altitude_exact[2], altitude_exact[3])
    
    altitude_formula_explanation = (
        f"\\([\\overrightarrow{{{l1}{l2}}}, \\overrightarrow{{{l1}{l3}}}] = {format_vector_latex(cross_product)} \\Rightarrow |[\\overrightarrow{{{l1}{l2}}}, \\overrightarrow{{{l1}{l3}}}]| = {cross_str}\\)\n\n"
        f"\\(\\Rightarrow S_{{\\triangle {l1}{l2}{l3}}} = \\frac{{1}}{{2}} |[\\overrightarrow{{{l1}{l2}}}, \\overrightarrow{{{l1}{l3}}}]| = {area_str}\\)\n\n"
        f"\\({base_edge_name} = {base_str}\\).\n\nTa có: \\({{}}S_{{\\triangle {l1}{l2}{l3}}} = \\frac{{1}}{{2}} {altitude_name} \\cdot {base_edge_name} \\Leftrightarrow {altitude_name} = \\frac{{2 \\cdot S_{{\\triangle {l1}{l2}{l3}}}}}{{{base_edge_name}}} = {altitude_str}\\)"
    )
    
    if 1 in true_indices:
        question_content += f"Lời giải cho mệnh đề b):\n\n{altitude_formula_explanation}\n\n"
    else:
        question_content += f"Lời giải cho mệnh đề b):\n\n{altitude_formula_explanation}\n\n"
    
    # For proposition c - angle calculation with detailed steps
    angle_data = propositions[2]
    angle_vertex = angle_data['angle_vertex']
    angle_name = angle_data['angle_name']
    angle_value = angle_data['angle_value']
    
    # Calculate vectors and their dot product based on which vertex
    if angle_vertex == l1:  # Angle at l1
        v1 = (B[0] - A[0], B[1] - A[1], B[2] - A[2])  # l1l2 vector
        v2 = (C[0] - A[0], C[1] - A[1], C[2] - A[2])  # l1l3 vector
        v1_name = f"{l1}{l2}"
        v2_name = f"{l1}{l3}"
    elif angle_vertex == l2:  # Angle at l2
        v1 = (A[0] - B[0], A[1] - B[1], A[2] - B[2])  # l2l1 vector
        v2 = (C[0] - B[0], C[1] - B[1], C[2] - B[2])  # l2l3 vector
        v1_name = f"{l2}{l1}"
        v2_name = f"{l2}{l3}"
    else:  # Angle at l3
        v1 = (A[0] - C[0], A[1] - C[1], A[2] - C[2])  # l3l1 vector
        v2 = (B[0] - C[0], B[1] - C[1], B[2] - C[2])  # l3l2 vector
        v1_name = f"{l3}{l1}"
        v2_name = f"{l3}{l2}"
    
    # Calculate dot product and magnitudes
    dot_product = vector_dot_product(v1, v2)
    mag1 = vector_magnitude(v1)
    mag2 = vector_magnitude(v2)
    cos_value = dot_product / (mag1 * mag2) if (mag1 * mag2) != 0 else 0
    
    # Format cos as simplified fraction
    from math import gcd
    mag1_int = int(round(mag1))
    mag2_int = int(round(mag2))
    dot_product_int = int(round(dot_product))
    
    # Simplify the fraction dot_product / (mag1 * mag2)
    denominator = mag1_int * mag2_int
    numerator = dot_product_int
    
    if denominator != 0:
        common_divisor = gcd(abs(numerator), abs(denominator))
        numerator //= common_divisor
        denominator //= common_divisor
        
        if denominator == 1:
            cos_fraction_str = str(numerator)
        else:
            cos_fraction_str = f"\\frac{{{numerator}}}{{{denominator}}}"
    else:
        cos_fraction_str = "0"
    
    angle_formula_explanation = (
        f"\\( \\cos({angle_name}) = \\frac{{\\overrightarrow{{{v1_name}}} \\cdot \\overrightarrow{{{v2_name}}}}}{{|\\overrightarrow{{{v1_name}}}| \\cdot |\\overrightarrow{{{v2_name}}}|}} = \\frac{{{dot_product_int}}}{{{mag1_int} \\cdot {mag2_int}}} = {cos_fraction_str} \\) "
        f"\\( \\Rightarrow {angle_name} = {angle_value:.1f}° \\)."
    )
    
    if 2 in true_indices:
        question_content += f"Lời giải cho mệnh đề c):\n\n{angle_formula_explanation}\n\n"
    else:
        question_content += f"Lời giải cho mệnh đề c):\n\n{angle_formula_explanation}\n\n"
    
    # For proposition d - coplanar condition with detailed calculation
    coplanar_data = propositions[3]
    
    # Calculate vectors l1l2, l1l3, l1D for the determinant  
    AB_vector = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    AC_vector = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
    
    # l1D vector in terms of m: D = (x_d, y_d, a_coeff*m + b_const)
    # l1D = (x_d - A[0], y_d - A[1], a_coeff*m + b_const - A[2])
    x_d_minus_ax = coplanar_data['x_d'] - A[0]
    y_d_minus_ay = coplanar_data['y_d'] - A[1]
    const_z_part = coplanar_data['b_const'] - A[2]
    
    # Create simplified z expression for l1D vector
    z_simplified_const = coplanar_data['b_const'] - A[2]
    if coplanar_data['a_coeff'] == 1:
        if z_simplified_const == 0:
            z_simplified_expr = "m"
        elif z_simplified_const > 0:
            z_simplified_expr = f"m + {z_simplified_const}"
        else:
            z_simplified_expr = f"m - {abs(z_simplified_const)}"
    elif coplanar_data['a_coeff'] == -1:
        if z_simplified_const == 0:
            z_simplified_expr = "-m"
        elif z_simplified_const > 0:
            z_simplified_expr = f"-m + {z_simplified_const}"
        else:
            z_simplified_expr = f"-m - {abs(z_simplified_const)}"
    else:
        if z_simplified_const == 0:
            z_simplified_expr = f"{coplanar_data['a_coeff']}m"
        elif z_simplified_const > 0:
            z_simplified_expr = f"{coplanar_data['a_coeff']}m + {z_simplified_const}"
        else:
            z_simplified_expr = f"{coplanar_data['a_coeff']}m - {abs(z_simplified_const)}"
    
    # Calculate cross product [l1l2, l1l3] 
    cross_product = (
        AB_vector[1] * AC_vector[2] - AB_vector[2] * AC_vector[1],
        AB_vector[2] * AC_vector[0] - AB_vector[0] * AC_vector[2], 
        AB_vector[0] * AC_vector[1] - AB_vector[1] * AC_vector[0]
    )
    
    # Build detailed explanation following the handwritten image format
    # Calculate the actual dot product step by step for detailed explanation
    # Dot product calculation: (cross_product[0] * x_d_minus_ax) + (cross_product[1] * y_d_minus_ay) + (cross_product[2] * z_component) = 0
    # where z_component = coplanar_data['a_coeff']*m + (coplanar_data['b_const'] - A[2])
    
    # Calculate coefficients for the equation
    dot_x_term = cross_product[0] * x_d_minus_ax
    dot_y_term = cross_product[1] * y_d_minus_ay
    dot_z_constant = cross_product[2] * (coplanar_data['b_const'] - A[2])
    dot_z_coefficient = cross_product[2] * coplanar_data['a_coeff']
    
    # The equation becomes: dot_x_term + dot_y_term + dot_z_constant + dot_z_coefficient * m = 0
    constant_sum = dot_x_term + dot_y_term + dot_z_constant
    
    # Format constant_sum and coefficient to avoid + - patterns
    def format_coefficient(value):
        if value >= 0:
            return f"{value}"
        else:
            return f"{value}"
    
    def format_equation_term(coeff, var="m"):
        if coeff == 0:
            return "0"
        elif coeff == 1:
            return var
        elif coeff == -1:
            return f"-{var}"
        else:
            return f"{coeff}{var}"
    
    def format_term_with_sign(term, is_first=False):
        """Format a term with proper + or - sign."""
        if is_first:
            return str(term)
        else:
            if term >= 0:
                return f" + {term}"
            else:
                return f" - {abs(term)}"
    
    constant_term_str = format_coefficient(constant_sum)
    coeff_term_str = format_equation_term(dot_z_coefficient)
    
    # Build the equation step by step showing expansion  
    # First show the detailed expansion with proper sign handling
    if cross_product[1] >= 0:
        sign2 = f" + {cross_product[1]}"
    else:
        sign2 = f" - {abs(cross_product[1])}"
    
    if cross_product[2] >= 0:
        sign3 = f" + {cross_product[2]}"
    else:
        sign3 = f" - {abs(cross_product[2])}"
    
    expansion_str = (f"{cross_product[0]} \\cdot ({x_d_minus_ax}){sign2} \\cdot ({y_d_minus_ay}){sign3} \\cdot ({z_simplified_expr})")
    
    # Calculate individual terms for expansion display
    term1 = cross_product[0] * x_d_minus_ax
    term2 = cross_product[1] * y_d_minus_ay
    
    # For the third term, show the expansion of coefficient * (am + b)
    coeff_z_const = cross_product[2] * z_simplified_const
    
    # Helper function to format terms properly avoiding + - patterns
    def format_product_term(coeff, factor):
        if coeff >= 0:
            return f"{coeff} \\cdot {factor}"
        else:
            return f"({coeff}) \\cdot {factor}"
    
    if coplanar_data['a_coeff'] == 1:
        if z_simplified_const == 0:
            term3_expansion = format_product_term(cross_product[2], "m")
        elif z_simplified_const > 0:
            term3_expansion = f"{format_product_term(cross_product[2], 'm')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
        else:
            term3_expansion = f"{format_product_term(cross_product[2], 'm')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
    elif coplanar_data['a_coeff'] == -1:
        if z_simplified_const == 0:
            term3_expansion = format_product_term(cross_product[2], "(-m)")
        elif z_simplified_const > 0:
            term3_expansion = f"{format_product_term(cross_product[2], '(-m)')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
        else:
            term3_expansion = f"{format_product_term(cross_product[2], '(-m)')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
    else:
        if z_simplified_const == 0:
            term3_expansion = format_product_term(cross_product[2], f"({coplanar_data['a_coeff']}m)")
        elif z_simplified_const > 0:
            term3_expansion = f"{format_product_term(cross_product[2], f'({coplanar_data['a_coeff']}m)')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
        else:
            term3_expansion = f"{format_product_term(cross_product[2], f'({coplanar_data['a_coeff']}m)')} + {format_product_term(cross_product[2], str(z_simplified_const))}"
    
    # Calculate expanded form
    coeff_of_m = cross_product[2] * coplanar_data['a_coeff']
    constant_from_z = cross_product[2] * z_simplified_const
    total_constant = term1 + term2 + constant_from_z
    
    # Note: m_value is already calculated correctly when creating the proposition,
    # so no need to update it here anymore
    
    # Format the final simplified equation and handle degenerate cases
    if coeff_of_m == 0:
        if total_constant == 0:
            equation_str = "0 = 0"
            final_conclusion = "\\text{(Phương trình nghiệm đúng với mọi m)}"
        else:
            equation_str = f"{total_constant} = 0"
            final_conclusion = "\\text{(Phương trình vô nghiệm)}"
    elif total_constant == 0:
        if coeff_of_m == 1:
            equation_str = "m = 0"
        elif coeff_of_m == -1:
            equation_str = "-m = 0"
        else:
            equation_str = f"{coeff_of_m}m = 0"
        final_conclusion = f"\\Leftrightarrow m = 0"
    else:
        # Build equation avoiding + - patterns
        if coeff_of_m > 0 and total_constant > 0:
            equation_str = f"{total_constant} + {coeff_of_m}m = 0"
        elif coeff_of_m > 0 and total_constant < 0:
            equation_str = f"{coeff_of_m}m - {abs(total_constant)} = 0"
        elif coeff_of_m < 0 and total_constant > 0:
            equation_str = f"{total_constant} - {abs(coeff_of_m)}m = 0"
        else:  # both negative
            equation_str = f"-{abs(total_constant)} - {abs(coeff_of_m)}m = 0"
        
        # Format m_value as fraction using the solution value
        solution_m = coplanar_data['solution_m_value']
        if solution_m is None:
            final_conclusion = "\\text{(Phương trình vô nghiệm)}"
        else:
            from fractions import Fraction
            if isinstance(solution_m, Fraction):
                # Already a fraction, use directly
                m_fraction = solution_m
            elif isinstance(solution_m, (int, float)):
                # Convert to fraction
                m_fraction = Fraction(solution_m).limit_denominator()
            else:
                m_value_str = str(solution_m)
                final_conclusion = f"\\Leftrightarrow m = {m_value_str}"
                return
            
            if m_fraction.denominator == 1:
                m_value_str = str(m_fraction.numerator)
            else:
                if m_fraction.numerator < 0:
                    m_value_str = f"-\\frac{{{abs(m_fraction.numerator)}}}{{{m_fraction.denominator}}}"
                else:
                    m_value_str = f"\\frac{{{m_fraction.numerator}}}{{{m_fraction.denominator}}}"
            final_conclusion = f"\\Leftrightarrow m = {m_value_str}"
    
    # Format the equation steps with proper signs to avoid + - patterns
    term1_str = format_term_with_sign(term1, True)
    term2_str = format_term_with_sign(term2)
    constant_from_z_str = format_term_with_sign(constant_from_z)
    
    # Format coeff_of_m with proper sign handling to avoid + - patterns  
    if coeff_of_m >= 0:
        coeff_m_str = f" + {coeff_of_m}m"
    else:
        coeff_m_str = f" - {abs(coeff_of_m)}m"
    
    det_explanation = (
        f"\\([\\overrightarrow{{{l1}{l2}}}, \\overrightarrow{{{l1}{l3}}}] = ({cross_product[0]}; {cross_product[1]}; {cross_product[2]})\\)\n\n"
        f"\\(\\overrightarrow{{{l1}D}} = ({x_d_minus_ax}; {y_d_minus_ay}; {z_simplified_expr})\\)\n\n"
        f"\\({l1}, {l2}, {l3}, D \\text{{ đồng phẳng }} \\Leftrightarrow [\\overrightarrow{{{l1}{l2}}}, \\overrightarrow{{{l1}{l3}}}] \\cdot \\overrightarrow{{{l1}D}} = 0\\)\n\n"
        f"\\(\\Leftrightarrow {expansion_str} = 0\\)\n\n"
        f"\\(\\Leftrightarrow {term1_str}{term2_str} + {term3_expansion} = 0\\)\n\n"
        f"\\(\\Leftrightarrow {term1_str}{term2_str}{coeff_m_str}{constant_from_z_str} = 0\\)\n\n"
        f"\\(\\Leftrightarrow {equation_str}\\)\n\n"
        f"\\({final_conclusion}\\)"
    )
    
    coplanar_formula_explanation = det_explanation
    
    if 3 in true_indices:
        question_content += f"Lời giải cho mệnh đề d):\n\n{coplanar_formula_explanation}\n\n"
    else:
        question_content += f"Lời giải cho mệnh đề d):\n\n{coplanar_formula_explanation}\n\n"
    
    # Final answer format like oxy_true_false.py
    correct_letters = [option_labels[i] for i in true_indices]
    correct_letters.sort()  # Sort alphabetically
    
    return question_content

def create_latex_document(questions, title="Câu hỏi Đúng/Sai về Tam Giác"):
    """Create complete LaTeX document with questions."""
    latex_content = (
        "\\documentclass[a4paper,12pt]{article}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{amsfonts}\n"
        "\\usepackage{amssymb}\n"
        "\\usepackage{geometry}\n"
        "\\geometry{a4paper, margin=1in}\n"
        "\\usepackage{polyglossia}\n"
        "\\setmainlanguage{vietnamese}\n"
        "\\setmainfont{Times New Roman}\n"
        "\\begin{document}\n\n"
        f"{title}\n\n"
    )
    latex_content += "\n\n".join(questions)
    latex_content += "\n\n\\end{document}"
    return latex_content

def main():
    """Main function for question generation."""
    try:
        # Parse command line arguments
        if len(sys.argv) > 1:
            try:
                num_questions = int(sys.argv[1])
                if num_questions <= 0:
                    raise ValueError("Number of questions must be positive")
            except ValueError:
                logging.error("Invalid number of questions: %s", sys.argv[1])
                print("Error: Number of questions must be a positive integer")
                sys.exit(1)
        else:
            num_questions = 3  # Default to 3 questions
        
        logging.info("Generating %d questions", num_questions)
        
        # Generate all questions
        all_content = []
        for i in range(1, num_questions + 1):
            logging.info("Processing question %d", i)
            content = generate_question(i)
            all_content.append(content)
        
        # Create LaTeX document
        latex_content = create_latex_document(all_content)
        
        # Write to file
        output_filename = "true_false_triangle_questions.tex"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info("Successfully wrote LaTeX content to %s", output_filename)
        print(f"Generated {output_filename} with {num_questions} question(s). Compile with XeLaTeX.")
        
    except Exception as e:
        logging.error("Error in main: %s", e)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
