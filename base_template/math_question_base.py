#!/usr/bin/env python3
"""
Base template for generating LaTeX math multiple choice questions in Vietnamese.

This template provides:
- LaTeX document structure with Vietnamese support
- Fraction formatting utilities
- Polynomial formatting utilities
- Question generation framework
- PDF compilation support

Usage:
1. Copy this file and rename it for your specific question type
2. Modify the question generation logic in generate_question()
3. Update the main section with your specific parameters
4. Run: python3 your_question_file.py [number_of_questions]
5. Compile: xelatex output_questions.tex
"""

import random
import sys
import logging
from fractions import Fraction

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def format_coefficient(coeff, is_first=False, var='x', power=1):
    """Format coefficient with proper signs and variable."""
    if coeff == 0:
        return ""
    
    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    
    # Format the coefficient part
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
    
    # Handle variable and power
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
    
    # Handle signs
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"

def format_polynomial(coeffs, var='x'):
    """Format polynomial coefficients as LaTeX string."""
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"
    
    terms = []
    degree = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)
    
    if not terms:
        return "0"
    
    return "".join(terms)

def format_with_parentheses(value):
    """Format negative numbers with parentheses for multiplication display."""
    if value < 0:
        return f"({value})"
    return str(value)

def build_expression_dynamically(terms_list):
    """
    Build mathematical expression dynamically, handling signs properly.
    
    Args:
        terms_list: List of tuples (coefficient, display_string, condition)
        Example: [(slope, "x", slope != 0), (intercept, "", intercept != 0)]
    
    Returns:
        Formatted LaTeX expression string
    """
    parts = []
    
    for i, (coeff, var_part, condition) in enumerate(terms_list):
        if not condition:
            continue
            
        if isinstance(coeff, (int, float)):
            coeff = Fraction(coeff)
        
        # Format coefficient
        if coeff == 1 and var_part:
            term = var_part
        elif coeff == -1 and var_part:
            term = f"-{var_part}"
        else:
            coeff_str = format_fraction_latex(coeff.numerator, coeff.denominator)
            term = f"{coeff_str}{var_part}" if var_part else coeff_str
        
        # Handle signs
        if len(parts) == 0:
            parts.append(term)
        else:
            if coeff > 0:
                parts.append(f" + {term}")
            else:
                # Extract the negative sign and format properly
                if term.startswith("-"):
                    parts.append(f" - {term[1:]}")
                else:
                    parts.append(f" - {term}")
    
    return "".join(parts) if parts else "0"

class MathQuestionGenerator:
    """Base class for generating math questions."""
    
    def __init__(self, question_type="Math Question"):
        self.question_type = question_type
    
    def generate_parameters(self):
        """Override this method to generate problem parameters."""
        # Example: return random coefficients, values, etc.
        return {}
    
    def calculate_solution(self, params):
        """Override this method to calculate the correct answer."""
        # Example: solve equation, calculate result, etc.
        return None
    
    def generate_wrong_answers(self, correct_answer, params):
        """Override this method to generate plausible wrong answers."""
        # Example: common mistakes, calculation errors, etc.
        return []
    
    def format_question_stem(self, params):
        """Override this method to format the question statement."""
        return "Câu hỏi mẫu..."
    
    def format_answer_choice(self, answer):
        """Override this method to format answer choices."""
        return str(answer)
    
    def generate_detailed_solution(self, params, correct_answer):
        """Override this method to generate step-by-step solution."""
        return "\\textbf{Giải:}\n\nLời giải chi tiết..."
    
    def generate_question(self, question_number):
        """Generate a complete multiple-choice question."""
        logging.info(f"Generating question {question_number}")
        
        # Generate problem parameters
        params = self.generate_parameters()
        
        # Calculate correct answer
        correct_answer = self.calculate_solution(params)
        
        # Generate wrong answers
        wrong_answers = self.generate_wrong_answers(correct_answer, params)
        
        # Create all options
        all_options = [self.format_answer_choice(correct_answer)] + [
            self.format_answer_choice(ans) for ans in wrong_answers
        ]
        random.shuffle(all_options)
        correct_index = all_options.index(self.format_answer_choice(correct_answer))
        
        # Format question
        question_stem = self.format_question_stem(params)
        solution = self.generate_detailed_solution(params, correct_answer)
        
        # Format the complete question
        option_labels = ['A', 'B', 'C', 'D']
        question_content = (
            f"Câu {question_number}: {question_stem}\n\n"
            f"{'*' if correct_index == 0 else ''}{option_labels[0]}. {all_options[0]}\n\n"
            f"{'*' if correct_index == 1 else ''}{option_labels[1]}. {all_options[1]}\n\n"
            f"{'*' if correct_index == 2 else ''}{option_labels[2]}. {all_options[2]}\n\n"
            f"{'*' if correct_index == 3 else ''}{option_labels[3]}. {all_options[3]}\n\n"
            f"Lời giải:\n\n"
            f"{solution}\n"
        )
        
        return question_content

def create_latex_document(questions, title="Câu hỏi Trắc nghiệm Toán học"):
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
        f"\\section*{{{title}}}\n\n"
    )
    latex_content += "\n\n".join(questions)
    latex_content += "\n\n\\end{document}"
    return latex_content

def main_template(generator_class, output_filename, default_questions=4):
    """Main function template for question generation."""
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
            num_questions = default_questions
        
        logging.info("Generating %d questions", num_questions)
        
        # Create generator instance
        generator = generator_class()
        
        # Generate all questions
        all_content = []
        for i in range(1, num_questions + 1):
            logging.info("Processing question %d", i)
            content = generator.generate_question(i)
            all_content.append(content)
        
        # Create LaTeX document
        latex_content = create_latex_document(all_content, generator.question_type)
        
        # Write to file
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info("Successfully wrote LaTeX content to %s", output_filename)
        print(f"Generated {output_filename} with {num_questions} question(s). Compile with XeLaTeX.")
        
    except Exception as e:
        logging.error("Error in main: %s", e)
        print(f"Error: {e}")
        sys.exit(1)

# Example usage - uncomment and modify for your specific question type
"""
class SampleQuestionGenerator(MathQuestionGenerator):
    def __init__(self):
        super().__init__("Câu hỏi mẫu")
    
    def generate_parameters(self):
        return {
            'a': random.randint(1, 10),
            'b': random.randint(1, 10)
        }
    
    def calculate_solution(self, params):
        return params['a'] + params['b']
    
    def generate_wrong_answers(self, correct_answer, params):
        return [
            correct_answer + 1,
            correct_answer - 1,
            correct_answer * 2
        ]
    
    def format_question_stem(self, params):
        return f"Tính {params['a']} + {params['b']} = ?"
    
    def generate_detailed_solution(self, params, correct_answer):
        return f"\\textbf{{Giải:}}\\n\\n{params['a']} + {params['b']} = {correct_answer}"

if __name__ == "__main__":
    main_template(SampleQuestionGenerator, "sample_questions.tex", 5)
"""
