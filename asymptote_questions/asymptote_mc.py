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
        var_str = f"{coeff_str}x" if coeff_str else "x"
    else:
        var_str = f"{coeff_str}x^{{{power}}}" if coeff_str else f"x^{{{power}}}"
    
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

def generate_rational_function_coefficients():
    """Generate coefficients for rational function with oblique asymptote."""
    # For oblique asymptote, numerator degree = denominator degree + 1
    
    # Generate denominator (linear): Dx + E
    D = random.choice([-3, -2, -1, 1, 2, 3])
    E = random.randint(-5, 5)
    denom_coeffs = [D, E]
    
    # Generate numerator (quadratic): Ax^2 + Bx + C
    A = random.choice([-3, -2, -1, 1, 2, 3])
    B = random.randint(-7, 7)
    C = random.randint(-7, 7)
    num_coeffs = [A, B, C]
    
    return num_coeffs, denom_coeffs

def calculate_oblique_asymptote_formula(A, B, C, D, E):
    """Calculate oblique asymptote using the formula y = (A/D)x + (BD-AE)/D²"""
    
    # Slope coefficient: A/D
    slope = Fraction(A, D)
    
    # Y-intercept: (BD - AE)/D²
    intercept = Fraction(B * D - A * E, D * D)
    
    return slope, intercept

def generate_wrong_answers(correct_slope, correct_intercept):
    """Generate 3 wrong answers based on common mistakes."""
    wrong_answers = []
    
    # Wrong answer 1: Change slope slightly
    wrong_slope1 = correct_slope + random.choice([Fraction(-1), Fraction(1), Fraction(-1, 2), Fraction(1, 2)])
    wrong_answers.append((wrong_slope1, correct_intercept))
    
    # Wrong answer 2: Change intercept
    wrong_intercept2 = correct_intercept + random.choice([Fraction(-2), Fraction(-1), Fraction(1), Fraction(2)])
    wrong_answers.append((correct_slope, wrong_intercept2))
    
    # Wrong answer 3: Common formula mistake (BD + AE instead of BD - AE)
    # This simulates using (BD + AE)/D² instead of (BD - AE)/D²
    wrong_intercept3 = correct_intercept + Fraction(2 * correct_slope.denominator * correct_intercept.denominator, correct_intercept.denominator)
    if wrong_intercept3 == correct_intercept:
        wrong_intercept3 = correct_intercept + Fraction(3)
    wrong_answers.append((correct_slope, wrong_intercept3))
    
    return wrong_answers

def format_asymptote_equation(slope, intercept):
    """Format the asymptote equation y = mx + b"""
    slope_str = format_fraction_latex(slope.numerator, slope.denominator)
    intercept_str = format_fraction_latex(intercept.numerator, intercept.denominator)
    
    if slope == 0:
        return intercept_str
    elif slope == 1:
        if intercept == 0:
            return "x"
        elif intercept > 0:
            return f"x + {intercept_str}"
        else:
            return f"x - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}"
    elif slope == -1:
        if intercept == 0:
            return "-x"
        elif intercept > 0:
            return f"-x + {intercept_str}"
        else:
            return f"-x - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}"
    else:
        if intercept == 0:
            return f"{slope_str}x"
        elif intercept > 0:
            return f"{slope_str}x + {intercept_str}"
        else:
            return f"{slope_str}x - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}"

def format_full_asymptote_equation(A, B, C, D, E):
    """Format the asymptote equation using standard formula y = (A/D)x + (BD-AE)/D²"""
    # Calculate slope and intercept using standard formula
    slope = Fraction(A, D)
    intercept = Fraction(B * D - A * E, D * D)
    
    # Format slope term
    slope_display = format_fraction_latex(slope.numerator, slope.denominator)
    
    if slope == 0:
        slope_term = ""
    elif slope.numerator == 1 and slope.denominator == 1:
        slope_term = "x"
    elif slope.numerator == -1 and slope.denominator == 1:
        slope_term = "-x"
    else:
        slope_term = f"{slope_display}x"
    
    # Build the equation with proper sign handling
    terms = []
    
    # Add slope term
    if slope != 0:
        terms.append(slope_term)
    
    # Add intercept term (avoid + with negative numbers)
    if intercept != 0:
        intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
        if len(terms) > 0:
            if intercept > 0:
                terms.append(f" + {intercept_display}")
            else:
                terms.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
        else:
            terms.append(intercept_display)
    
    # If all terms are zero
    if not terms:
        return "0"
    
    return "".join(terms)

def generate_detailed_solution(A, B, C, D, E, slope, intercept):
    """Generate detailed solution following the LaTeX base file format exactly."""
    
    # Format the original function
    num_str = format_polynomial([A, B, C])
    denom_str = format_polynomial([D, E])
    
    # Calculate R using the formula from LaTeX base
    BD = B * D
    AE = A * E
    BD_minus_AE = BD - AE
    D_squared = D * D
    R_numerator = BD_minus_AE * E
    R = C - Fraction(R_numerator, D_squared)
    
    # Format values for display
    R_display = format_fraction_latex(R.numerator, R.denominator)
    slope_display = format_fraction_latex(slope.numerator, slope.denominator)
    intercept_display = format_fraction_latex(intercept.numerator, intercept.denominator)
    
    # Format slope coefficient for "Ta có:" line - avoid "1 · x" 
    if slope.numerator == 1 and slope.denominator == 1:
        slope_ta_co = "x"
    elif slope.numerator == -1 and slope.denominator == 1:
        slope_ta_co = "-x"
    else:
        slope_ta_co = f"{slope_display}x"
    
    # Build "Ta có:" equation dynamically - skip intercept if it's 0
    ta_co_parts = [slope_ta_co]
    
    # Add intercept term only if not zero
    if intercept != 0:
        if intercept > 0:
            ta_co_parts.append(f" + {intercept_display}")
        else:
            ta_co_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
    
    # Add R term
    if R != 0:
        if R > 0:
            ta_co_parts.append(f" + \\frac{{{R_display}}}{{{denom_str}}}")
        else:
            ta_co_parts.append(f" - \\frac{{{format_fraction_latex(abs(R.numerator), abs(R.denominator))}}}{{{denom_str}}}")
    
    ta_co_equation = "".join(ta_co_parts)
    
    # Build the final equation for tiệm cận xiên (chỉ có 2 hệ số)
    final_parts = []
    
    # Add slope term
    if slope.numerator == 1 and slope.denominator == 1:
        final_parts.append("x")
    elif slope.numerator == -1 and slope.denominator == 1:
        final_parts.append("-x")
    elif slope != 0:
        final_parts.append(f"{slope_display}x")
    
    # Add intercept term (handle sign properly)
    if intercept != 0:
        if len(final_parts) > 0:
            if intercept > 0:
                final_parts.append(f" + {intercept_display}")
            else:
                final_parts.append(f" - {format_fraction_latex(abs(intercept.numerator), abs(intercept.denominator))}")
        else:
            final_parts.append(intercept_display)
    
    final_equation = "".join(final_parts) if final_parts else "0"
    
    solution = f"""\\textbf{{Giải:}}

Ta có: \\(y = \\frac{{{num_str}}}{{{denom_str}}} = {ta_co_equation}\\)

\\(\\Rightarrow \\displaystyle\\lim_{{x \\to +\\infty}} \\left(\\left(\\frac{{{num_str}}}{{{denom_str}}}\\right) - \\left({ta_co_equation}\\right)\\right) = \\displaystyle\\lim_{{x \\to +\\infty}} \\frac{{{R_display}}}{{{denom_str}}} = \\displaystyle\\lim_{{x \\to +\\infty}} \\frac{{\\frac{{{R_display}}}{{x}}}}{{{D} + \\frac{{{E}}}{{x}}}} = 0\\)

\\(\\Rightarrow\\) Tiệm cận xiên: \\(y = {final_equation}\\)"""
    
    return solution

def generate_customer_first_question():
    """Generate the specific question requested by customer."""
    
    # Customer's specific example: y = (x² + 3x - 2)/(x - 1)
    A, B, C = 1, 3, -2
    D, E = 1, -1
    
    # Customer's specific options - using standard format
    slope, intercept = calculate_oblique_asymptote_formula(A, B, C, D, E)
    correct_option = format_asymptote_equation(slope, intercept)
    options = [
        correct_option,  # Correct answer - standard format
        "2x + 4",      # Wrong option 1
        "3x + 2",      # Wrong option 2 
        "x + 2"        # Wrong option 3
    ]
    
    # The correct answer is option A (index 0)
    correct_index = 0
    
    # Format function for question
    num_str = format_polynomial([A, B, C])
    denom_str = format_polynomial([D, E])
    
    # Generate question text
    question_stem = f"Cho hàm số \\(y = \\frac{{{num_str}}}{{{denom_str}}}\\)."
    question_text = f"Phương trình đường tiệm cận xiên của đồ thị hàm số này là:"
    
    # Generate detailed solution
    solution = generate_detailed_solution(A, B, C, D, E, slope, intercept)
    
    # Shuffle options
    all_options = options[:]
    random.shuffle(all_options)
    correct_answer = options[correct_index]
    correct_index = all_options.index(correct_answer)
    option_labels = ['A', 'B', 'C', 'D']
    
    # Format the complete question
    question_content = (
        f"Câu 1: {question_stem}\n\n"
        f"{question_text}\n\n"
        f"{'*' if correct_index == 0 else ''}{option_labels[0]}. \\(y = {all_options[0]}\\)\n\n"
        f"{'*' if correct_index == 1 else ''}{option_labels[1]}. \\(y = {all_options[1]}\\)\n\n"
        f"{'*' if correct_index == 2 else ''}{option_labels[2]}. \\(y = {all_options[2]}\\)\n\n"
        f"{'*' if correct_index == 3 else ''}{option_labels[3]}. \\(y = {all_options[3]}\\)\n\n"
        f"Lời giải:\n\n"
        f"{solution}\n"
    )
    
    return question_content

def generate_question(question_number):
    """Generate a multiple-choice question about oblique asymptote."""
    logging.info(f"Generating question {question_number}")
    
    # Generate coefficients
    num_coeffs, denom_coeffs = generate_rational_function_coefficients()
    A, B, C = num_coeffs
    D, E = denom_coeffs
    
    # Calculate correct answer using the formula
    correct_slope, correct_intercept = calculate_oblique_asymptote_formula(A, B, C, D, E)
    
    # Generate wrong answers using full format
    wrong_answers = generate_wrong_answers(correct_slope, correct_intercept)
    
    # Create options using full format
    correct_answer = format_full_asymptote_equation(A, B, C, D, E)
    wrong_answer_strs = []
    
    # Generate wrong options using standard format 
    for slope, intercept in wrong_answers:
        wrong_answer_strs.append(format_asymptote_equation(slope, intercept))
    
    # Create all options
    all_options = [correct_answer] + wrong_answer_strs
    random.shuffle(all_options)
    correct_index = all_options.index(correct_answer)
    
    # Format function for question
    num_str = format_polynomial([A, B, C])
    denom_str = format_polynomial([D, E])
    
    # Generate question text
    question_stem = f"Cho hàm số \\(y = \\frac{{{num_str}}}{{{denom_str}}}\\)."
    question_text = f"Phương trình đường tiệm cận xiên của đồ thị hàm số này là:"
    
    # Generate detailed solution
    solution = generate_detailed_solution(A, B, C, D, E, correct_slope, correct_intercept)
    
    # Format the complete question
    option_labels = ['A', 'B', 'C', 'D']
    question_content = (
        f"Câu {question_number}: {question_stem}\n\n"
        f"{question_text}\n\n"
        f"{'*' if correct_index == 0 else ''}{option_labels[0]}. \\(y = {all_options[0]}\\)\n\n"
        f"{'*' if correct_index == 1 else ''}{option_labels[1]}. \\(y = {all_options[1]}\\)\n\n"
        f"{'*' if correct_index == 2 else ''}{option_labels[2]}. \\(y = {all_options[2]}\\)\n\n"
        f"{'*' if correct_index == 3 else ''}{option_labels[3]}. \\(y = {all_options[3]}\\)\n\n"
        f"Lời giải:\n\n"
        f"{solution}\n"
    )
    
    return question_content

if __name__ == "__main__":
    try:
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
            num_questions = 4  # Default to 4 questions
        
        logging.info("Generating %d questions", num_questions)

        # Generate all questions
        all_content = []
        for i in range(1, num_questions + 1):
            logging.info("Processing question %d", i)
            content = generate_question(i)
            all_content.append(content)

        # Combine content into a single LaTeX document
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
            "\\section*{Câu hỏi Trắc nghiệm về Tiệm cận xiên}\n\n"
        )
        latex_content += "\n\n".join(all_content)
        latex_content += "\n\n\\end{document}"

        # Write to file
        filename = "asymptote_mc_questions.tex"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        logging.info("Successfully wrote LaTeX content to %s", filename)
        print(f"Generated {filename} with {num_questions} question(s). Compile with XeLaTeX.")
        
    except Exception as e:
        logging.error("Error in main: %s", e)
        print(f"Error: {e}")
        sys.exit(1)
