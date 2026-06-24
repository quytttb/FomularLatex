import random
import sys
import logging
from fractions import Fraction
import math
#sqrt_monotonicity_2
# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def gcd(a, b):
    """Compute the greatest common divisor of a and b."""
    while b:
        a, b = b, a % b
    return a

def simplify_fraction(num, denom):
    """Simplify a fraction by dividing numerator and denominator by their GCD."""
    if denom < 0:
        num, denom = -num, -denom
    if num == 0:
        return 0, 1
    g = gcd(abs(num), abs(denom))
    return num // g, denom // g

def format_latex_number(value, is_left_endpoint=True):
    """Format a number for LaTeX, always using fractions for non-integers."""
    if value == float('-inf'):
        return "-\\infty"
    elif value == float('inf'):
        return "+\\infty"
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, (float, Fraction)):
        frac = Fraction(value).limit_denominator(100)
        num, denom = simplify_fraction(frac.numerator, frac.denominator)
        if denom == 1:
            return str(num)
        if num < 0:
            return f"-\\frac{{{-num}}}{{{denom}}}"
        return f"\\frac{{{num}}}{{{denom}}}"
    else:
        logging.warning(f"Unexpected value type for LaTeX formatting: {value}")
        return str(value)

def format_function_for_latex(a, b, c):
    """Format the function y = sqrt(ax^2 + bx + c) for LaTeX, omitting coefficient 1."""
    terms = []
    if a != 0:
        if a == 1:
            terms.append("x^2")
        elif a == -1:
            terms.append("-x^2")
        else:
            terms.append(f"{a}x^2")
    if b != 0:
        if b == 1:
            terms.append("+x")
        elif b == -1:
            terms.append("-x")
        else:
            terms.append(f"+{b}x" if b > 0 else f"{b}x")
    if c != 0:
        terms.append(f"+{c}" if c > 0 else f"{c}")
    inner = "".join(terms)
    if inner.startswith("+"):
        inner = inner[1:]
    return f"\\sqrt{{{inner}}}"

def is_perfect_square(n):
    """Check if n is a perfect square."""
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n

def get_domain_and_critical_points(a, b, c):
    """Compute domain and critical point for f(x) = sqrt(ax^2 + bx + c)."""
    discriminant = b * b - 4 * a * c
    critical_point = Fraction(-b, 2 * a)
    
    if discriminant < 0:
        return float('-inf'), float('inf'), critical_point
    sqrt_disc = int(discriminant ** 0.5)
    if not is_perfect_square(discriminant):
        return None, None, None
    x1 = Fraction(-b - sqrt_disc, 2 * a)
    x2 = Fraction(-b + sqrt_disc, 2 * a)
    if x1 == x2:  # Single root, invalid for intervals
        return None, None, None
    return x1, x2, critical_point

def get_monotonicity_intervals(a, b, c):
    """Determine increasing and decreasing intervals."""
    x1, x2, critical_point = get_domain_and_critical_points(a, b, c)
    if x1 is None:
        return [], []
    
    increasing = []
    decreasing = []
    
    if x1 == float('-inf'):
        decreasing.append((float('-inf'), critical_point))
        increasing.append((critical_point, float('inf')))
    else:
        if critical_point <= x1:
            increasing.append((x2, float('inf')))
            decreasing.append((float('-inf'), x1))
        elif critical_point >= x2:
            increasing.append((float('-inf'), x1))
            increasing.append((x2, float('inf')))
        else:
            increasing.append((x2, float('inf')))
            decreasing.append((float('-inf'), x1))
    
    increasing = [i for i in increasing if i[0] < i[1]]
    decreasing = [d for d in decreasing if d[0] < d[1]]
    
    return increasing, decreasing

def get_valid_coefficients(nice_numbers, coeff_range=(-10, 10)):
    """Generate valid coefficients ensuring nice domain endpoints and critical point."""
    valid_configs = []
    a_choices = [a for a in range(1, coeff_range[1] + 1)]  # a > 0
    b_choices = [b for b in range(coeff_range[0], coeff_range[1] + 1)]
    c_choices = [c for c in range(coeff_range[0], coeff_range[1] + 1)]
    
    for a in a_choices:
        for b in b_choices:
            if a == b:
                continue
            for c in c_choices:
                x1, x2, critical_point = get_domain_and_critical_points(a, b, c)
                if x1 is None:
                    continue
                if x1 == float('-inf') and critical_point in nice_numbers:
                    valid_configs.append((a, b, c))
                elif x1 in nice_numbers and x2 in nice_numbers and critical_point in nice_numbers:
                    valid_configs.append((a, b, c))
    
    logging.debug(f"Found {len(valid_configs)} valid coefficient sets")
    return valid_configs

def generate_question(question_number, coeff_range=(-10, 10)):
    """Generate a multiple-choice question for square root function monotonicity."""
    max_attempts = 500
    nice_numbers = [
        -5, -4, -3, -2, -1, Fraction(-1, 2), 0,
        Fraction(1, 2), 1, 2, 3, 4, 5
    ]
    valid_configs = get_valid_coefficients(nice_numbers, coeff_range)
    if not valid_configs:
        raise RuntimeError("No valid coefficient sets found.")
    
    for attempt in range(max_attempts):
        logging.debug(f"Attempt {attempt + 1}: Generating function")
        
        a, b, c = random.choice(valid_configs)
        x1, x2, critical_point = get_domain_and_critical_points(a, b, c)
        increasing_intervals, decreasing_intervals = get_monotonicity_intervals(a, b, c)
        logging.debug(f"Domain: [{x1}, {x2}], Critical point: {critical_point}")
        
        function_latex = format_function_for_latex(a, b, c)
        statements = [None] * 4
        labels = ['A', 'B', 'C', 'D']
        
        monotonicity = random.choice(["đồng biến", "nghịch biến"])
        question = f"Câu {question_number}: Hàm số \\(y = {function_latex}\\) {monotonicity} trên khoảng nào sau đây?"
        correct_index = random.randint(0, 3)
        
        # Correct option
        correct_intervals = increasing_intervals if monotonicity == "đồng biến" else decreasing_intervals
        if not correct_intervals:
            continue
        if len(correct_intervals) > 1:
            statements[correct_index] = (
                " \\text{ và } ".join(
                    f"\\(({format_latex_number(interval[0])}, {format_latex_number(interval[1], False)})\\)"
                    for interval in correct_intervals
                )
            )
        else:
            interval = correct_intervals[0]
            statements[correct_index] = (
                f"\\(({format_latex_number(interval[0])}, {format_latex_number(interval[1], False)})\\)"
            )
        
        # Generate incorrect options
        wrong_intervals = decreasing_intervals if monotonicity == "đồng biến" else increasing_intervals
        incorrect_options_pool = []
        
        def fmt_int(start, end):
            return f"\\(({format_latex_number(start)}, {format_latex_number(end, False)})\\)"
            
        # 1. The exact wrong intervals
        for interval in wrong_intervals:
            incorrect_options_pool.append(fmt_int(interval[0], interval[1]))
            
        # 2. Undefined region if exists
        if x1 is not None and x1 != float('-inf') and x1 < x2:
            incorrect_options_pool.append(fmt_int(x1, x2))
            
        # 3. Subsets of the wrong intervals
        possible_offsets = [Fraction(1, 2), 1, 2, 3]
        for interval in wrong_intervals:
            for offset in possible_offsets:
                if interval[0] == float('-inf'):
                    sub_end = interval[1] - offset
                    if sub_end in nice_numbers:
                        incorrect_options_pool.append(fmt_int(float('-inf'), sub_end))
                elif interval[1] == float('inf'):
                    sub_start = interval[0] + offset
                    if sub_start in nice_numbers:
                        incorrect_options_pool.append(fmt_int(sub_start, float('inf')))
                        
        # 4. Intervals crossing the critical point / undefined region
        if x1 != float('-inf'):
            for offset in possible_offsets:
                cross_start = x1 - offset
                cross_end = x2 + offset
                if cross_start in nice_numbers and cross_end in nice_numbers:
                    incorrect_options_pool.append(fmt_int(cross_start, cross_end))
        else:
            for offset in possible_offsets:
                cross_start = critical_point - offset
                cross_end = critical_point + offset
                if cross_start in nice_numbers and cross_end in nice_numbers:
                    incorrect_options_pool.append(fmt_int(cross_start, cross_end))
                    
        # 5. Union of disjoint intervals
        if x1 != float('-inf'):
            incorrect_options_pool.append(
                f"\\((-\\infty, {format_latex_number(x1, False)}) \\cup ({format_latex_number(x2)}, +\\infty)\\)"
            )
        else:
            for offset in possible_offsets:
                u_start = critical_point - offset
                u_end = critical_point + offset
                if u_start in nice_numbers and u_end in nice_numbers:
                    incorrect_options_pool.append(
                        f"\\((-\\infty, {format_latex_number(u_start, False)}) \\cup ({format_latex_number(u_end)}, +\\infty)\\)"
                    )
                    
        correct_str = statements[correct_index]
        distinct_wrongs = list(dict.fromkeys([opt for opt in incorrect_options_pool if opt != correct_str]))
        
        if len(distinct_wrongs) < 3:
            continue
            
        random.shuffle(distinct_wrongs)
        chosen_wrongs = distinct_wrongs[:3]
        
        # Assign incorrect options
        incorrect_indices = [i for i in range(4) if i != correct_index]
        for i, wrong_str in zip(incorrect_indices, chosen_wrongs):
            statements[i] = wrong_str
        
        if None in statements:
            logging.warning("Failed to generate intervals. Retrying...")
            continue
        
        formatted_statements = statements
        if len(formatted_statements) != len(set(formatted_statements)):
            logging.warning(f"Duplicate options detected: {formatted_statements}. Retrying...")
            continue
        
        options = [
            f"{'*' if idx == correct_index else ''}{labels[idx]}. {statements[idx]}"
            for idx in range(4)
        ]
        
        content = [
            question,
            "", options[0],
            "", options[1],
            "", options[2],
            "", options[3],
            ""
        ]
        return "\n".join(content), labels[correct_index]
    
    logging.error(f"Max attempts reached for function.")
    raise RuntimeError("Failed to generate valid question after maximum attempts.")

def generate_latex_file(num_questions, filename="square_root_monotonicity_questions.tex"):
    """Generate LaTeX file with multiple-choice questions."""
    latex_content = [
        "\\documentclass[12pt]{article}",
        "\\usepackage{amsmath, amssymb}",
        "\\usepackage{geometry}",
        "\\geometry{a4paper, margin=1in}",
        "\\usepackage{polyglossia}",
        "\\setmainlanguage{vietnamese}",
        "\\usepackage{fontspec}",
        "\\setmainfont{Times New Roman}",
        "\\usepackage{unicode-math}",
        "\\setmathfont{XITS Math}",
        "\\setmathfont{Times New Roman}[range=up/{Latin,latin}]",
        "\\begin{document}",
        "\\section*{Danh sách câu hỏi}",
        ""
    ]
    
    correct_answers = []
    for i in range(1, num_questions + 1):
        content, correct_answer = generate_question(i)
        latex_content.append(content)
        correct_answers.append(f"Câu {i}: {correct_answer}")
    
    latex_content.append("\\end{document}")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    print(f"LaTeX file '{filename}' with {num_questions} multiple-choice questions has been generated. Compile with XeLaTeX.")
    print("Correct answers:")
    print("\n".join(correct_answers))

def main():
    if len(sys.argv) != 2:
        print("Usage: python square_root_monotonicity.py <number-questions>")
        sys.exit(1)
    
    try:
        num_questions = int(sys.argv[1])
        if num_questions <= 0:
            print("Number of questions must be positive.")
            sys.exit(1)
    except ValueError:
        print("Number of questions must be an integer.")
        sys.exit(1)
    
    generate_latex_file(num_questions)

if __name__ == "__main__":
    main()