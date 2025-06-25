"""
Advanced asymptote question generator implementation for true/false questions.
"""

from typing import Dict, Any, List, Tuple
import random
import math
from fractions import Fraction

from base import TrueFalseGenerator, format_polynomial, format_fraction_latex, standardize_math_expression


class AdvancedAsymptoteGenerator(TrueFalseGenerator):
    """Generator for advanced asymptote true/false questions."""
    
    def __init__(self):
        super().__init__("Advanced Asymptote Questions")
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Generate parameters for advanced asymptote questions."""
        # This generator creates 4 different types of questions
        question_types = ['vertical_horizontal', 'area_rectangle', 'asymptote_count', 'oblique']
        
        return {
            'question_types': question_types,
            'current_type': random.choice(question_types)
        }
    
    def generate_statements(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate 4 true/false statements about advanced asymptotes."""
        statements = []
        
        # Generate each type of question
        q1_data = self._generate_vertical_horizontal_question()
        q2_data = self._generate_area_rectangle_question()  
        q3_data = self._generate_asymptote_count_question()
        q4_data = self._generate_oblique_question()
        
        # Create statements from each question type
        statements.append({
            'text': q1_data['statement'],
            'is_correct': q1_data['is_correct']
        })
        
        statements.append({
            'text': q2_data['statement'],
            'is_correct': q2_data['is_correct']
        })
        
        statements.append({
            'text': q3_data['statement'],
            'is_correct': q3_data['is_correct']
        })
        
        statements.append({
            'text': q4_data['statement'],
            'is_correct': q4_data['is_correct']
        })
        
        return statements
    
    def _generate_vertical_horizontal_question(self) -> Dict[str, Any]:
        """Generate question about vertical and horizontal asymptotes with parameters."""
        # Generate random parameters m, n
        m = random.randint(-5, 5)
        n = random.randint(-5, 5)
        
        # Generate function coefficients
        a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.randint(-7, 7)
        c = random.choice([-3, -2, -1, 1, 2, 3])
        d = random.randint(-7, 7)
        
        # Function: f(x) = (ax + b) / (cx + d)
        # Vertical asymptote: x = -d/c
        # Horizontal asymptote: y = a/c
        
        vertical_asymptote = -d / c if c != 0 else 0
        horizontal_asymptote = a / c if c != 0 else 0
        
        # Create true statement about asymptotes depending on m, n values
        if abs(vertical_asymptote - m) < 0.1 and abs(horizontal_asymptote - n) < 0.1:
            # True case
            is_correct = True
            statement = f"Hàm số $y = \\dfrac{{{format_polynomial([a, b])}}}{{{format_polynomial([c, d])}}}$ có tiệm cận đứng $x = {m}$ và tiệm cận ngang $y = {n}$."
        else:
            # False case - modify one asymptote
            is_correct = random.choice([True, False])
            if is_correct:
                # Use correct asymptotes
                statement = f"Hàm số $y = \\dfrac{{{format_polynomial([a, b])}}}{{{format_polynomial([c, d])}}}$ có tiệm cận đứng $x = {format_fraction_latex(-d, c)}$ và tiệm cận ngang $y = {format_fraction_latex(a, c)}$."
            else:
                # Use incorrect asymptotes
                wrong_vert = format_fraction_latex(-d, c) if random.choice([True, False]) else str(m)
                wrong_horiz = format_fraction_latex(a, c) if random.choice([True, False]) else str(n)
                statement = f"Hàm số $y = \\dfrac{{{format_polynomial([a, b])}}}{{{format_polynomial([c, d])}}}$ có tiệm cận đứng $x = {wrong_vert}$ và tiệm cận ngang $y = {wrong_horiz}$."
        
        return {
            'statement': standardize_math_expression(statement),
            'is_correct': is_correct,
            'function_data': {'a': a, 'b': b, 'c': c, 'd': d}
        }
    
    def _generate_area_rectangle_question(self) -> Dict[str, Any]:
        """Generate question about area of rectangle formed by asymptotes."""
        # Generate function with vertical and horizontal asymptotes
        a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.randint(-7, 7)
        c = random.choice([-3, -2, -1, 1, 2, 3])
        d = random.randint(-7, 7)
        
        # Asymptotes
        vert_asymptote = -d / c if c != 0 else 0
        horiz_asymptote = a / c if c != 0 else 0
        
        # Area of rectangle formed by asymptotes and axes
        # Area = |vert_asymptote| * |horiz_asymptote|
        true_area = abs(vert_asymptote * horiz_asymptote)
        
        # Generate wrong areas
        wrong_area1 = true_area + random.choice([1, 2, 0.5])
        wrong_area2 = true_area * random.choice([2, 0.5])
        
        is_correct = random.choice([True, False])
        if is_correct:
            area_value = true_area
        else:
            area_value = random.choice([wrong_area1, wrong_area2])
        
        # Format area value properly
        if isinstance(area_value, float):
            if area_value == int(area_value):
                area_value_str = str(int(area_value))
            else:
                # Convert to fraction if it's a simple rational number
                from fractions import Fraction
                frac = Fraction(area_value).limit_denominator(100)
                if abs(float(frac) - area_value) < 0.001:
                    area_value_str = format_fraction_latex(frac.numerator, frac.denominator)
                else:
                    area_value_str = f"{area_value:.2f}"
        else:
            area_value_str = str(area_value)
        
        statement = f"Diện tích hình chữ nhật được tạo bởi các tiệm cận của hàm số $y = \\dfrac{{{format_polynomial([a, b])}}}{{{format_polynomial([c, d])}}}$ và các trục tọa độ bằng ${area_value_str}$."
        
        return {
            'statement': standardize_math_expression(statement),
            'is_correct': is_correct,
            'area_data': {'true_area': true_area, 'given_area': area_value_str}
        }
    
    def _generate_asymptote_count_question(self) -> Dict[str, Any]:
        """Generate question about counting total number of asymptotes."""
        # Generate a function with 2 vertical asymptotes and 1 horizontal asymptote
        # Example: f(x) = 1/((x-a)(x-b)) has vertical asymptotes at x=a, x=b
        # and horizontal asymptote at y=0
        
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while b == a:  # Ensure different values
            b = random.randint(-5, 5)
        
        # Function: 1/((x-a)(x-b)) = 1/(x² - (a+b)x + ab)
        coeff_x2 = 1
        coeff_x1 = -(a + b)
        coeff_x0 = a * b
        
        # This function has 2 vertical asymptotes and 1 horizontal asymptote = 3 total
        true_count = 3
        
        # Generate wrong counts
        wrong_counts = [2, 4, 5]
        
        is_correct = random.choice([True, False])
        if is_correct:
            count = true_count
        else:
            count = random.choice(wrong_counts)
        
        denominator = format_polynomial([coeff_x2, coeff_x1, coeff_x0])
        statement = f"Hàm số $y = \\dfrac{{1}}{{{denominator}}}$ có tổng cộng ${count}$ đường tiệm cận."
        
        return {
            'statement': standardize_math_expression(statement),
            'is_correct': is_correct,
            'count_data': {'true_count': true_count, 'given_count': count}
        }
    
    def _generate_oblique_question(self) -> Dict[str, Any]:
        """Generate question about oblique asymptote."""
        # Generate rational function with oblique asymptote
        # Numerator degree = denominator degree + 1
        
        # Denominator (linear): dx + e
        d = random.choice([-3, -2, -1, 1, 2, 3])
        e = random.randint(-5, 5)
        
        # Numerator (quadratic): ax² + bx + c
        a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.randint(-7, 7)
        c = random.randint(-7, 7)
        
        # Oblique asymptote: y = (a/d)x + (bd-ae)/d²
        slope = Fraction(a, d)
        intercept = Fraction(b*d - a*e, d*d)
        
        # True oblique asymptote equation
        true_equation = f"y = {format_fraction_latex(slope.numerator, slope.denominator)}x + {format_fraction_latex(intercept.numerator, intercept.denominator)}"
        
        # Generate wrong equations
        wrong_slope = Fraction(b, d)  # Common mistake
        wrong_equation1 = f"y = {format_fraction_latex(wrong_slope.numerator, wrong_slope.denominator)}x + {format_fraction_latex(intercept.numerator, intercept.denominator)}"
        
        wrong_intercept = Fraction(b, d)  # Another common mistake
        wrong_equation2 = f"y = {format_fraction_latex(slope.numerator, slope.denominator)}x + {format_fraction_latex(wrong_intercept.numerator, wrong_intercept.denominator)}"
        
        is_correct = random.choice([True, False])
        if is_correct:
            equation = true_equation
        else:
            equation = random.choice([wrong_equation1, wrong_equation2])
        
        num_poly = format_polynomial([a, b, c])
        denom_poly = format_polynomial([d, e])
        
        statement = f"Hàm số $y = \\dfrac{{{num_poly}}}{{{denom_poly}}}$ có tiệm cận xiên ${equation}$."
        
        return {
            'statement': standardize_math_expression(statement),
            'is_correct': is_correct,
            'oblique_data': {'true_equation': true_equation, 'given_equation': equation}
        }
    
    def calculate_solution(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate solutions for verification."""
        return self.generate_statements(params)
    
    def format_question_text(self, params: Dict[str, Any]) -> str:
        """Format the main question text."""
        return "Chọn các mệnh đề đúng về tiệm cận của hàm số:"
    
    def generate_solution_text(self, params: Dict[str, Any], statements: List[Dict[str, Any]]) -> str:
        """Generate detailed solution explanation."""
        solution = "**Phân tích các mệnh đề về tiệm cận:**\n\n"
        
        for i, stmt in enumerate(statements):
            letter = chr(ord('a') + i)
            correct_text = "ĐÚNG" if stmt['is_correct'] else "SAI"
            solution += f"**{letter})** {correct_text}\n\n"
        
        # Add correct answer summary  
        correct_letters = [chr(ord('a') + i) for i, stmt in enumerate(statements) if stmt['is_correct']]
        solution += f"**Đáp án đúng:** {', '.join(correct_letters)}"
        
        return solution
