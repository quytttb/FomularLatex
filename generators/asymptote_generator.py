"""
Asymptote question generator implementation.
"""

from typing import Dict, Any, List
import random
from fractions import Fraction

from base import MultipleChoiceGenerator, format_polynomial, format_fraction_latex


class AsymptoteGenerator(MultipleChoiceGenerator):
    """Generator for asymptote multiple choice questions."""
    
    def __init__(self):
        super().__init__("Asymptote Questions")
    
    def generate_parameters(self) -> Dict[str, Any]:
        """Generate coefficients for rational function with oblique asymptote."""
        # For oblique asymptote, numerator degree = denominator degree + 1
        
        # Generate denominator (linear): Dx + E  
        D = random.choice(self.config.NONZERO_VALUES)
        E = random.randint(*self.config.COEFFICIENT_RANGE)
        
        # Generate numerator (quadratic): Ax^2 + Bx + C
        A = random.choice(self.config.NONZERO_VALUES)
        B = random.randint(*self.config.COEFFICIENT_RANGE)
        C = random.randint(*self.config.COEFFICIENT_RANGE)
        
        return {
            'num_coeffs': [A, B, C],
            'denom_coeffs': [D, E],
            'A': A, 'B': B, 'C': C, 'D': D, 'E': E
        }
    
    def calculate_solution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the oblique asymptote equation."""
        A, B, C, D, E = params['A'], params['B'], params['C'], params['D'], params['E']
        
        # Oblique asymptote: y = (A/D)x + (BD-AE)/D²
        slope = Fraction(A, D)
        y_intercept = Fraction(B*D - A*E, D*D)
        
        return {
            'slope': slope,
            'y_intercept': y_intercept,
            'equation': f"y = {format_fraction_latex(A, D)}x + {format_fraction_latex(B*D - A*E, D*D)}"
        }
    
    def generate_wrong_answers(self, correct_answer: Dict[str, Any], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plausible wrong asymptote equations."""
        A, B, C, D, E = params['A'], params['B'], params['C'], params['D'], params['E']
        correct_slope = correct_answer['slope']
        correct_intercept = correct_answer['y_intercept']
        
        wrong_answers = []
        
        # Wrong answer 1: Use A/D but wrong intercept (common mistake: use B/D)
        wrong1_intercept = Fraction(B, D)
        wrong1 = {
            'slope': correct_slope,
            'y_intercept': wrong1_intercept,
            'equation': f"y = {format_fraction_latex(A, D)}x + {format_fraction_latex(B, D)}"
        }
        wrong_answers.append(wrong1)
        
        # Wrong answer 2: Wrong slope (use B/D) but correct intercept calculation  
        wrong2_slope = Fraction(B, D)
        wrong2 = {
            'slope': wrong2_slope,
            'y_intercept': correct_intercept,
            'equation': f"y = {format_fraction_latex(B, D)}x + {format_fraction_latex(B*D - A*E, D*D)}"
        }
        wrong_answers.append(wrong2)
        
        # Wrong answer 3: Both slope and intercept wrong (use simpler calculation)
        wrong3_slope = Fraction(A, D)
        wrong3_intercept = Fraction(C, E) if E != 0 else Fraction(C, 1)
        wrong3 = {
            'slope': wrong3_slope,
            'y_intercept': wrong3_intercept, 
            'equation': f"y = {format_fraction_latex(A, D)}x + {format_fraction_latex(C, E if E != 0 else 1)}"
        }
        wrong_answers.append(wrong3)
        
        return wrong_answers
    
    def format_question_text(self, params: Dict[str, Any]) -> str:
        """Format the asymptote question statement."""
        num_poly = format_polynomial(params['num_coeffs'])
        denom_poly = format_polynomial(params['denom_coeffs'])
        
        return f"""Tìm phương trình tiệm cận xiên của hàm số $y = \\dfrac{{{num_poly}}}{{{denom_poly}}}$."""
    
    def format_answer_choice(self, answer: Dict[str, Any]) -> str:
        """Format answer choice for display."""
        return answer['equation']
    
    def generate_solution_text(self, params: Dict[str, Any], answer: Dict[str, Any]) -> str:
        """Generate detailed solution for asymptote calculation."""
        A, B, C, D, E = params['A'], params['B'], params['C'], params['D'], params['E']
        
        num_poly = format_polynomial(params['num_coeffs'])
        denom_poly = format_polynomial(params['denom_coeffs'])
        
        solution = f"""Cho hàm số $y = \\dfrac{{{num_poly}}}{{{denom_poly}}}$.

Để tìm tiệm cận xiên, ta thực hiện phép chia đa thức:

$$\\dfrac{{{num_poly}}}{{{denom_poly}}} = {format_fraction_latex(A, D)}x + {format_fraction_latex(B*D - A*E, D*D)} + \\dfrac{{\\text{{dư}}}}{{{denom_poly}}}$$

Khi $x \\to \\pm\\infty$, phần dư tiến về 0.

Vậy tiệm cận xiên là: $y = {answer['equation'].replace('y = ', '')}$.
"""
        
        return solution
