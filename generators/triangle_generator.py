"""
Triangle question generator implementation for true/false questions.
"""

from typing import Dict, Any, List, Tuple
import random
import math
from fractions import Fraction

from base import TrueFalseGenerator, format_fraction_latex


class TriangleGenerator(TrueFalseGenerator):
    """Generator for true/false questions about triangles in 3D space."""
    
    # Pool of letters for vertices
    LETTER_POOL = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T']
    
    def __init__(self):
        super().__init__("Triangle True/False Questions")
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Generate triangle coordinates and vertex labels."""
        # Generate triangle coordinates
        A, B, C = self._generate_triangle_coordinates()
        
        # Choose 3 different vertex labels
        available_letters = [letter for letter in self.LETTER_POOL if letter != 'D']
        labels = random.sample(available_letters, 3)
        l1, l2, l3 = labels[0], labels[1], labels[2]
        
        vertices = {l1: A, l2: B, l3: C}
        
        self.logger.info(f"Triangle: {l1}{A}, {l2}{B}, {l3}{C}")
        
        return {
            'vertices': vertices,
            'labels': [l1, l2, l3],
            'coordinates': {'A': A, 'B': B, 'C': C}
        }
    
    def _generate_triangle_coordinates(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
        """Generate valid triangle coordinates."""
        patterns = [
            # Pattern 1: Standard triangle in xy-plane with some z variation
            lambda: ((0, 0, 0), (random.randint(3, 6), 0, random.randint(0, 3)), 
                    (random.randint(2, 5), random.randint(4, 8), random.randint(0, 2))),
            
            # Pattern 2: Triangle with one vertex at origin
            lambda: ((0, 0, 0), (random.randint(2, 5), random.randint(1, 4), random.randint(1, 3)), 
                    (random.randint(1, 4), random.randint(2, 6), random.randint(2, 4))),
            
            # Pattern 3: More general triangle
            lambda: ((random.randint(-2, 2), random.randint(-1, 2), random.randint(0, 1)), 
                    (random.randint(2, 5), random.randint(0, 3), random.randint(1, 4)), 
                    (random.randint(1, 4), random.randint(3, 6), random.randint(0, 3)))
        ]
        
        # Choose random pattern
        pattern = random.choice(patterns)
        A, B, C = pattern()
        
        # Apply random coordinate permutation
        coordinate_permutations = [
            (0, 1, 2),  # x, y, z (original)
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
        area = self._calculate_triangle_area(A, B, C)
        if area < 0.1:  # If area is too small, use a guaranteed valid triangle
            A = (0, 0, 0)
            B = (4, 0, 3)
            C = (6, 8, 0)
        
        return A, B, C
    
    def _calculate_triangle_area(self, A: Tuple, B: Tuple, C: Tuple) -> float:
        """Calculate triangle area using cross product."""
        # Vectors AB and AC
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
        
        # Cross product AB × AC
        cross = (
            AB[1] * AC[2] - AB[2] * AC[1],
            AB[2] * AC[0] - AB[0] * AC[2],
            AB[0] * AC[1] - AB[1] * AC[0]
        )
        
        # Area = |AB × AC| / 2
        magnitude = math.sqrt(cross[0]**2 + cross[1]**2 + cross[2]**2)
        return magnitude / 2
    
    def generate_statements(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate 4 true/false statements about the triangle."""
        vertices = params['vertices']
        labels = params['labels']
        coords = params['coordinates']
        l1, l2, l3 = labels
        A, B, C = coords['A'], coords['B'], coords['C']
        
        statements = []
        
        # Statement a: Foot of angle bisector
        foot = self._calculate_foot_of_angle_bisector(A, B, C)
        foot_x_frac = Fraction(foot[0]).limit_denominator()
        foot_y_frac = Fraction(foot[1]).limit_denominator()
        foot_z_frac = Fraction(foot[2]).limit_denominator()
        
        true_foot = f"({self._format_coord_frac(foot_x_frac)}, {self._format_coord_frac(foot_y_frac)}, {self._format_coord_frac(foot_z_frac)})"
        false_foot_x = foot_x_frac + Fraction(random.choice([-1, 1]))
        false_foot = f"({self._format_coord_frac(false_foot_x)}, {self._format_coord_frac(foot_y_frac)}, {self._format_coord_frac(foot_z_frac)})"
        
        statements.append({
            'text': f"Tọa độ chân đường phân giác kẻ từ {l1} xuống {l2}{l3} là \\( D{true_foot} \\).",
            'is_correct': True
        })
        
        # Statement b: Altitude length
        altitude_from = random.choice([l1, l2, l3])
        if altitude_from == l1:
            altitude_exact = self._calculate_altitude_length_exact(A, B, C, 'A')
            prop_text = f"Độ dài đường cao kẻ từ {l1} trong \\( \\triangle {l1}{l2}{l3} \\)"
        elif altitude_from == l2:
            altitude_exact = self._calculate_altitude_length_exact(A, B, C, 'B')
            prop_text = f"Độ dài đường cao kẻ từ {l2} trong \\( \\triangle {l1}{l2}{l3} \\)"
        else:
            altitude_exact = self._calculate_altitude_length_exact(A, B, C, 'C')
            prop_text = f"Độ dài đường cao kẻ từ {l3} trong \\( \\triangle {l1}{l2}{l3} \\)"
        
        true_altitude_str = self._format_exact_fraction(*altitude_exact)
        
        statements.append({
            'text': f"{prop_text} = \\( {true_altitude_str} \\).",
            'is_correct': True
        })
        
        # Statement c: Angle calculation
        angle_vertex = random.choice([l1, l2, l3])
        if angle_vertex == l1:
            angle = self._calculate_angle(A, B, C)
            angle_name = f"\\widehat{{{l2}{l1}{l3}}}"
        elif angle_vertex == l2:
            angle = self._calculate_angle(B, A, C)
            angle_name = f"\\widehat{{{l1}{l2}{l3}}}"
        else:
            angle = self._calculate_angle(C, A, B)
            angle_name = f"\\widehat{{{l1}{l3}{l2}}}"
        
        true_angle = f"{angle:.1f}°"
        
        statements.append({
            'text': f"\\( \\triangle {l1}{l2}{l3} \\) có góc {angle_name} = \\( {true_angle} \\).",
            'is_correct': True
        })
        
        # Statement d: Coplanar condition
        x_d, y_d = random.randint(-5, 5), random.randint(-5, 5)
        a_coeff = random.choice([1, 2, 3, -1, -2, -3])
        b_const = random.randint(-10, 10)
        
        m_value = self._calculate_coplanar_m_value(A, B, C, x_d, y_d, a_coeff, b_const)
        z_expr = self._format_z_expression(a_coeff, b_const)
        m_formatted = self._format_m_value(m_value)
        
        statements.append({
            'text': f"Bốn điểm {l1}, {l2}, {l3}, \\( D({x_d}, {y_d}, {z_expr}) \\) đồng phẳng khi \\( m = {m_formatted} \\).",
            'is_correct': True
        })
        
        # Randomly make some statements false
        num_true = random.randint(1, 3)
        indices_to_make_false = random.sample(range(4), 4 - num_true)
        
        for idx in indices_to_make_false:
            statements[idx]['is_correct'] = False
            statements[idx]['text'] = self._make_statement_false(statements[idx]['text'], idx)
        
        return statements
    
    def _make_statement_false(self, statement: str, statement_type: int) -> str:
        """Convert a true statement to false by modifying values."""
        if statement_type == 0:  # Foot of bisector
            # Change one coordinate
            import re
            coords = re.findall(r'\\frac\{-?\d+\}\{\d+\}|\d+', statement)
            if coords:
                # Modify first coordinate
                return statement.replace(coords[0], str(int(coords[0]) + 1) if coords[0].isdigit() else coords[0])
        elif statement_type == 1:  # Altitude length
            # Modify the coefficient
            return statement.replace("=", "≠")
        elif statement_type == 2:  # Angle
            # Change angle value
            import re
            angle_match = re.search(r'(\d+\.\d+)°', statement)
            if angle_match:
                old_angle = float(angle_match.group(1))
                new_angle = old_angle + random.choice([-5, 5])
                return statement.replace(f"{old_angle}°", f"{new_angle:.1f}°")
        elif statement_type == 3:  # Coplanar
            # Change m value
            import re
            m_match = re.search(r'm = ([^\\]+)', statement)
            if m_match:
                old_m = m_match.group(1)
                try:
                    new_m = float(old_m) + random.choice([-0.5, 0.5])
                    return statement.replace(f"m = {old_m}", f"m = {new_m}")
                except:
                    return statement.replace(old_m, "2")
        
        return statement
    
    def calculate_solution(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate solutions for verification."""
        return self.generate_statements(params)
    
    def format_question_text(self, params: Dict[str, Any]) -> str:
        """Format the main question text."""
        vertices = params['vertices']
        labels = params['labels']
        l1, l2, l3 = labels
        
        # Format coordinate display
        coord_text = ", ".join([f"{label}{self._format_point(*coord)}" for label, coord in vertices.items()])
        
        return f"Cho tam giác {l1}{l2}{l3} với {coord_text}. Chọn các mệnh đề đúng:"
    
    def generate_solution_text(self, params: Dict[str, Any], statements: List[Dict[str, Any]]) -> str:
        """Generate detailed solution explanation."""
        labels = params['labels']
        l1, l2, l3 = labels
        
        solution = f"**Phân tích tam giác {l1}{l2}{l3}:**\n\n"
        
        for i, stmt in enumerate(statements):
            letter = chr(ord('a') + i)
            correct_text = "ĐÚNG" if stmt['is_correct'] else "SAI"
            solution += f"**{letter})** {correct_text}\n\n"
        
        # Add correct answer summary
        correct_letters = [chr(ord('a') + i) for i, stmt in enumerate(statements) if stmt['is_correct']]
        solution += f"**Đáp án đúng:** {', '.join(correct_letters)}"
        
        return solution
    
    # Helper methods
    def _format_point(self, x, y, z) -> str:
        """Format a 3D point for display."""
        def format_value(val):
            if val == 0:
                return "0"
            if isinstance(val, int):
                return str(val)
            elif isinstance(val, float):
                return f"{val:.0f}" if val == int(val) else f"{val:.2f}"
            else:  # Fraction
                return format_fraction_latex(val.numerator, val.denominator)
        
        return f"({format_value(x)}, {format_value(y)}, {format_value(z)})"
    
    def _format_coord_frac(self, frac: Fraction) -> str:
        """Format coordinate as fraction."""
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    def _calculate_foot_of_angle_bisector(self, A: Tuple, B: Tuple, C: Tuple) -> Tuple:
        """Calculate foot of angle bisector from A to BC."""
        # Using the angle bisector theorem: BD/DC = AB/AC
        AB = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2 + (B[2] - A[2])**2)
        AC = math.sqrt((C[0] - A[0])**2 + (C[1] - A[1])**2 + (C[2] - A[2])**2)
        
        if AB + AC == 0:
            return B  # Fallback
        
        # Point D divides BC in ratio AB:AC
        t = AB / (AB + AC)
        
        D = (
            B[0] + t * (C[0] - B[0]),
            B[1] + t * (C[1] - B[1]),
            B[2] + t * (C[2] - B[2])
        )
        
        return D
    
    def _calculate_altitude_length_exact(self, A: Tuple, B: Tuple, C: Tuple, from_vertex: str) -> Tuple:
        """Calculate exact altitude length."""
        # This is a simplified version - in practice, this would involve
        # complex calculations for exact radical expressions
        if from_vertex == 'A':
            # Distance from A to line BC
            area = self._calculate_triangle_area(A, B, C)
            BC_length = math.sqrt((C[0] - B[0])**2 + (C[1] - B[1])**2 + (C[2] - B[2])**2)
            height = 2 * area / BC_length if BC_length > 0 else 0
        elif from_vertex == 'B':
            area = self._calculate_triangle_area(A, B, C)
            AC_length = math.sqrt((C[0] - A[0])**2 + (C[1] - A[1])**2 + (C[2] - A[2])**2)
            height = 2 * area / AC_length if AC_length > 0 else 0
        else:  # from_vertex == 'C'
            area = self._calculate_triangle_area(A, B, C)
            AB_length = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2 + (B[2] - A[2])**2)
            height = 2 * area / AB_length if AB_length > 0 else 0
        
        # Return as (coefficient, numerator, denominator, radicand) for exact representation
        return (1, int(height * 100), 100, 1)  # Simplified representation
    
    def _calculate_angle(self, vertex: Tuple, point1: Tuple, point2: Tuple) -> float:
        """Calculate angle at vertex between two points."""
        # Vectors from vertex to the two points
        v1 = (point1[0] - vertex[0], point1[1] - vertex[1], point1[2] - vertex[2])
        v2 = (point2[0] - vertex[0], point2[1] - vertex[1], point2[2] - vertex[2])
        
        # Dot product and magnitudes
        dot_product = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
        
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def _calculate_coplanar_m_value(self, A: Tuple, B: Tuple, C: Tuple, 
                                   x_d: int, y_d: int, a_coeff: int, b_const: int) -> float:
        """Calculate m value for coplanar condition."""
        # For 4 points to be coplanar: det(AB, AC, AD) = 0
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
        
        # Coefficient of m and constant term
        coeff_m = (AB[0]*AC[1] - AB[1]*AC[0]) * a_coeff
        const_term = (AB[0]*(AC[1]*(b_const - A[2]) - AC[2]*(y_d - A[1])) - 
                      AB[1]*(AC[0]*(b_const - A[2]) - AC[2]*(x_d - A[0])) + 
                      AB[2]*(AC[0]*(y_d - A[1]) - AC[1]*(x_d - A[0])))
        
        if coeff_m != 0:
            return round(-const_term / coeff_m, 1)
        else:
            return 1.0  # Fallback
    
    def _format_z_expression(self, a_coeff: int, b_const: int) -> str:
        """Format z coordinate expression."""
        if a_coeff == 1:
            if b_const >= 0:
                return f"m + {b_const}"
            else:
                return f"m - {abs(b_const)}"
        elif a_coeff == -1:
            if b_const >= 0:
                return f"-m + {b_const}"
            else:
                return f"-m - {abs(b_const)}"
        else:
            if b_const >= 0:
                return f"{a_coeff}m + {b_const}"
            else:
                return f"{a_coeff}m - {abs(b_const)}"
    
    def _format_m_value(self, value: float) -> str:
        """Format m value for display."""
        if isinstance(value, float):
            frac = Fraction(value).limit_denominator()
            return self._format_coord_frac(frac)
        return str(value)
    
    def _format_exact_fraction(self, coeff: int, num: int, denom: int, radicand: int) -> str:
        """Format exact fraction with radical."""
        if radicand == 1:
            return format_fraction_latex(coeff * num, denom)
        else:
            if coeff == 1:
                return f"\\frac{{\\sqrt{{{radicand}}} \\cdot {num}}}{{{denom}}}"
            else:
                return f"\\frac{{{coeff}\\sqrt{{{radicand}}} \\cdot {num}}}{{{denom}}}"
