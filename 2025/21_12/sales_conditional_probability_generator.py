"""
sales_conditional_probability_generator.py

Sinh bài toán xác suất có điều kiện về nhân viên bán hàng:
- 3 lần bán hàng liên tiếp
- Xác suất lần đầu bán được: a
- Nếu lần trước bán được => xác suất lần sau bán được: b
- Nếu lần trước không bán được => xác suất lần sau bán được: c
- Điều kiện: 0 < c < a < b < 1

Có 10 loại câu hỏi xác suất có điều kiện:
1. P(S1|S3) - Biết lần 3 bán được, tính xs lần 1 bán được
2. P(F1|S3) - Biết lần 3 bán được, tính xs lần 1 không bán được
3. P(S2|S3) - Biết lần 3 bán được, tính xs lần 2 bán được
4. P(F2|S3) - Biết lần 3 bán được, tính xs lần 2 không bán được
5. P(S1|S2) - Biết lần 2 bán được, tính xs lần 1 bán được
6. P(F1|S2) - Biết lần 2 bán được, tính xs lần 1 không bán được
7. P(S2|S1) - Biết lần 1 bán được, tính xs lần 2 bán được
8. P(F2|S1) - Biết lần 1 bán được, tính xs lần 2 không bán được
9. P(S3|S1) - Biết lần 1 bán được, tính xs lần 3 bán được
10. P(F3|S1) - Biết lần 1 bán được, tính xs lần 3 không bán được
"""

import random
import os
from fractions import Fraction
from typing import List, Tuple, Dict

# ==================== SCENARIOS ====================

SCENARIOS = {
    'sales': {
        'intro': r"Một nhân viên bán hàng mỗi năm đến bán ở công ty A ba lần. Xác suất để lần đầu bán được hàng là $a$. Nếu lần trước bán được hàng thì xác suất để lần sau bán được hàng tăng lên là $b$; nếu lần trước không bán được hàng thì xác suất để lần sau bán được hàng chỉ là $c$.",
        'success': "bán được hàng",
        'failure': "không bán được hàng",
        'event': "lần",
    },
    'interview': {
        'intro': r"Một ứng viên tham gia ba vòng phỏng vấn liên tiếp. Xác suất để vượt qua vòng đầu tiên là $a$. Nếu vòng trước vượt qua thì xác suất để vòng sau vượt qua tăng lên là $b$; nếu vòng trước không vượt qua thì xác suất để vòng sau vượt qua chỉ là $c$.",
        'success': "vượt qua",
        'failure': "không vượt qua",
        'event': "vòng",
    },
    'game': {
        'intro': r"Một game thủ chơi ba ván liên tiếp. Xác suất để thắng ván đầu tiên là $a$. Nếu ván trước thắng thì xác suất để ván sau thắng tăng lên là $b$; nếu ván trước thua thì xác suất để ván sau thắng chỉ là $c$.",
        'success': "thắng",
        'failure': "thua",
        'event': "ván",
    },
    'exam': {
        'intro': r"Một thí sinh thi ba môn liên tiếp. Xác suất để đậu môn đầu tiên là $a$. Nếu môn trước đậu thì xác suất để môn sau đậu tăng lên là $b$; nếu môn trước trượt thì xác suất để môn sau đậu chỉ là $c$.",
        'success': "đậu",
        'failure': "trượt",
        'event': "môn",
    },
    'sports': {
        'intro': r"Một vận động viên thi đấu ba trận liên tiếp. Xác suất để thắng trận đầu tiên là $a$. Nếu trận trước thắng thì xác suất để trận sau thắng tăng lên là $b$; nếu trận trước thua thì xác suất để trận sau thắng chỉ là $c$.",
        'success': "thắng",
        'failure': "thua",
        'event': "trận",
    },
}

# ==================== QUESTION TYPES ====================
# 10 question types for conditional probability

QUESTION_TYPES = [
    {
        'id': 'S1_given_S3',
        'condition': 'lần thứ ba {success}',
        'target': 'lần đầu tiên {success}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(S1|S3) = P(S1 ∩ S3) / P(S3) = [a·b² + a·(1-b)·c] / P(S3)
        'numerator': lambda a, b, c: a * b * b + a * (1-b) * c,
        'denominator': lambda a, b, c: a * b * b + a * (1-b) * c + (1-a) * c * b + (1-a) * (1-c) * c,
        'numerator_latex': r"a \cdot b^2 + a \cdot (1-b) \cdot c",
        'denominator_latex': r"a \cdot b^2 + a \cdot (1-b) \cdot c + (1-a) \cdot c \cdot b + (1-a) \cdot (1-c) \cdot c",
    },
    {
        'id': 'F1_given_S3',
        'condition': 'lần thứ ba {success}',
        'target': 'lần đầu tiên {failure}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(F1|S3) = P(F1 ∩ S3) / P(S3) = [(1-a)·c·b + (1-a)·(1-c)·c] / P(S3)
        'numerator': lambda a, b, c: (1-a) * c * b + (1-a) * (1-c) * c,
        'denominator': lambda a, b, c: a * b * b + a * (1-b) * c + (1-a) * c * b + (1-a) * (1-c) * c,
        'numerator_latex': r"(1-a) \cdot c \cdot b + (1-a) \cdot (1-c) \cdot c",
        'denominator_latex': r"a \cdot b^2 + a \cdot (1-b) \cdot c + (1-a) \cdot c \cdot b + (1-a) \cdot (1-c) \cdot c",
    },
    {
        'id': 'S2_given_S3',
        'condition': 'lần thứ ba {success}',
        'target': 'lần thứ hai {success}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(S2|S3) = P(S2 ∩ S3) / P(S3) = [a·b² + (1-a)·c·b] / P(S3)
        'numerator': lambda a, b, c: a * b * b + (1-a) * c * b,
        'denominator': lambda a, b, c: a * b * b + a * (1-b) * c + (1-a) * c * b + (1-a) * (1-c) * c,
        'numerator_latex': r"a \cdot b^2 + (1-a) \cdot c \cdot b",
        'denominator_latex': r"a \cdot b^2 + a \cdot (1-b) \cdot c + (1-a) \cdot c \cdot b + (1-a) \cdot (1-c) \cdot c",
    },
    {
        'id': 'F2_given_S3',
        'condition': 'lần thứ ba {success}',
        'target': 'lần thứ hai {failure}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(F2|S3) = P(F2 ∩ S3) / P(S3) = [a·(1-b)·c + (1-a)·(1-c)·c] / P(S3)
        'numerator': lambda a, b, c: a * (1-b) * c + (1-a) * (1-c) * c,
        'denominator': lambda a, b, c: a * b * b + a * (1-b) * c + (1-a) * c * b + (1-a) * (1-c) * c,
        'numerator_latex': r"a \cdot (1-b) \cdot c + (1-a) \cdot (1-c) \cdot c",
        'denominator_latex': r"a \cdot b^2 + a \cdot (1-b) \cdot c + (1-a) \cdot c \cdot b + (1-a) \cdot (1-c) \cdot c",
    },
    {
        'id': 'S1_given_S2',
        'condition': 'lần thứ hai {success}',
        'target': 'lần đầu tiên {success}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(S1|S2) = P(S1 ∩ S2) / P(S2) = a·b / [a·b + (1-a)·c]
        'numerator': lambda a, b, c: a * b,
        'denominator': lambda a, b, c: a * b + (1-a) * c,
        'numerator_latex': r"a \cdot b",
        'denominator_latex': r"a \cdot b + (1-a) \cdot c",
    },
    {
        'id': 'F1_given_S2',
        'condition': 'lần thứ hai {success}',
        'target': 'lần đầu tiên {failure}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(F1|S2) = P(F1 ∩ S2) / P(S2) = (1-a)·c / [a·b + (1-a)·c]
        'numerator': lambda a, b, c: (1-a) * c,
        'denominator': lambda a, b, c: a * b + (1-a) * c,
        'numerator_latex': r"(1-a) \cdot c",
        'denominator_latex': r"a \cdot b + (1-a) \cdot c",
    },
    {
        'id': 'S2_given_S1',
        'condition': 'lần thứ nhất {success}',
        'target': 'lần thứ hai {success}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(S2|S1) = b (trực tiếp từ đề bài)
        'numerator': lambda a, b, c: b,
        'denominator': lambda a, b, c: Fraction(1),
        'numerator_latex': r"b",
        'denominator_latex': r"1",
        'is_simple': True,
    },
    {
        'id': 'F2_given_S1',
        'condition': 'lần thứ nhất {success}',
        'target': 'lần thứ hai {failure}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(F2|S1) = 1-b
        'numerator': lambda a, b, c: 1 - b,
        'denominator': lambda a, b, c: Fraction(1),
        'numerator_latex': r"1 - b",
        'denominator_latex': r"1",
        'is_simple': True,
    },
    {
        'id': 'S3_given_S1',
        'condition': 'lần thứ nhất {success}',
        'target': 'lần thứ ba {success}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(S3|S1) = P(S1 ∩ S3) / P(S1) = [a·b² + a·(1-b)·c] / a = b² + (1-b)·c
        'numerator': lambda a, b, c: b * b + (1-b) * c,
        'denominator': lambda a, b, c: Fraction(1),
        'numerator_latex': r"b^2 + (1-b) \cdot c",
        'denominator_latex': r"1",
        'is_simple': True,
    },
    {
        'id': 'F3_given_S1',
        'condition': 'lần thứ nhất {success}',
        'target': 'lần thứ ba {failure}',
        'template': "Biết nhân viên {condition}. Tính xác suất để {target}.",
        # P(F3|S1) = [a·b·(1-b) + a·(1-b)·(1-c)] / a = b·(1-b) + (1-b)·(1-c) = (1-b)·(1+b-c)
        'numerator': lambda a, b, c: b * (1-b) + (1-b) * (1-c),
        'denominator': lambda a, b, c: Fraction(1),
        'numerator_latex': r"b \cdot (1-b) + (1-b) \cdot (1-c)",
        'denominator_latex': r"1",
        'is_simple': True,
    },
]


def generate_nice_fractions() -> Tuple[Fraction, Fraction, Fraction]:
    """
    Generate a, b, c as Fractions satisfying 0 < c < a < b < 1.
    Use simple denominators (2, 3, 4, 5, 6, 8, 10) for nice numbers.
    """
    denominators = [2, 3, 4, 5, 6, 8, 10]
    
    candidates = []
    for d1 in denominators:
        for d2 in denominators:
            for d3 in denominators:
                for n1 in range(1, d1):       # c
                    for n2 in range(1, d2):   # a
                        for n3 in range(1, d3):  # b
                            c = Fraction(n1, d1)
                            a = Fraction(n2, d2)
                            b = Fraction(n3, d3)
                            if c < a < b:
                                candidates.append((a, b, c))
    
    return random.choice(candidates)


def fraction_to_latex(f: Fraction) -> str:
    """Convert Fraction to LaTeX string."""
    if f.denominator == 1:
        return str(f.numerator)
    return rf"\dfrac{{{f.numerator}}}{{{f.denominator}}}"


def format_numerator_substitution(a: Fraction, b: Fraction, c: Fraction, q_type: Dict) -> str:
    """Build numerator substitution string for the solution."""
    a_str = fraction_to_latex(a)
    b_str = fraction_to_latex(b)
    c_str = fraction_to_latex(c)
    one_minus_a = fraction_to_latex(1 - a)
    one_minus_b = fraction_to_latex(1 - b)
    one_minus_c = fraction_to_latex(1 - c)
    b_squared = fraction_to_latex(b * b)
    
    q_id = q_type['id']
    
    # Map each question type to its numerator substitution
    if q_id == 'S1_given_S3':
        return rf"{a_str} \cdot {b_squared} + {a_str} \cdot {one_minus_b} \cdot {c_str}"
    elif q_id == 'F1_given_S3':
        return rf"{one_minus_a} \cdot {c_str} \cdot {b_str} + {one_minus_a} \cdot {one_minus_c} \cdot {c_str}"
    elif q_id == 'S2_given_S3':
        return rf"{a_str} \cdot {b_squared} + {one_minus_a} \cdot {c_str} \cdot {b_str}"
    elif q_id == 'F2_given_S3':
        return rf"{a_str} \cdot {one_minus_b} \cdot {c_str} + {one_minus_a} \cdot {one_minus_c} \cdot {c_str}"
    elif q_id == 'S1_given_S2':
        return rf"{a_str} \cdot {b_str}"
    elif q_id == 'F1_given_S2':
        return rf"{one_minus_a} \cdot {c_str}"
    elif q_id == 'S2_given_S1':
        return b_str
    elif q_id == 'F2_given_S1':
        return one_minus_b
    elif q_id == 'S3_given_S1':
        return rf"{b_squared} + {one_minus_b} \cdot {c_str}"
    elif q_id == 'F3_given_S1':
        return rf"{b_str} \cdot {one_minus_b} + {one_minus_b} \cdot {one_minus_c}"
    
    return ""


def format_denominator_substitution(a: Fraction, b: Fraction, c: Fraction, q_type: Dict) -> str:
    """Build denominator substitution string for the solution."""
    a_str = fraction_to_latex(a)
    b_str = fraction_to_latex(b)
    c_str = fraction_to_latex(c)
    one_minus_a = fraction_to_latex(1 - a)
    one_minus_b = fraction_to_latex(1 - b)
    one_minus_c = fraction_to_latex(1 - c)
    b_squared = fraction_to_latex(b * b)
    
    q_id = q_type['id']
    
    # Questions with P(S3) as denominator
    if q_id in ['S1_given_S3', 'F1_given_S3', 'S2_given_S3', 'F2_given_S3']:
        return rf"{a_str} \cdot {b_squared} + {a_str} \cdot {one_minus_b} \cdot {c_str} + {one_minus_a} \cdot {c_str} \cdot {b_str} + {one_minus_a} \cdot {one_minus_c} \cdot {c_str}"
    
    # Questions with P(S2) as denominator
    elif q_id in ['S1_given_S2', 'F1_given_S2']:
        return rf"{a_str} \cdot {b_str} + {one_minus_a} \cdot {c_str}"
    
    # Simple cases (denominator = 1)
    else:
        return "1"


class SalesConditionalProbabilityQuestion:
    def __init__(self):
        self.scenario_key = ""
        self.scenario = {}
        self.a = Fraction(0)
        self.b = Fraction(0)
        self.c = Fraction(0)
        self.selected_questions = []
        self.results = []  # List of result dicts
    
    def generate_parameters(self):
        """Pick random scenario and generate a, b, c."""
        self.scenario_key = random.choice(list(SCENARIOS.keys()))
        self.scenario = SCENARIOS[self.scenario_key]
        self.a, self.b, self.c = generate_nice_fractions()
    
    def select_questions(self):
        """Select 4 random questions from the 10 types."""
        self.selected_questions = random.sample(QUESTION_TYPES, 4)
    
    def calculate_and_distort(self):
        """
        For each selected question, decide if it's True or False.
        If False, distort the value.
        Ensure at least 1 True and at least 1 False.
        """
        self.results = []
        
        # Random number of true statements: 1, 2, or 3 (ensure at least 1 true and 1 false)
        num_true = random.choice([1, 2, 3])
        true_indices = set(random.sample(range(4), num_true))
        
        for i, q in enumerate(self.selected_questions):
            numerator = q['numerator'](self.a, self.b, self.c)
            denominator = q['denominator'](self.a, self.b, self.c)
            true_value = numerator / denominator if denominator != 0 else numerator
            
            is_correct = i in true_indices
            
            if is_correct:
                displayed_value = true_value
            else:
                # Distort: use wrong formula or multiply/add small error
                distortions = [
                    q['numerator'](1 - self.a, self.b, self.c) / denominator if denominator != Fraction(1) else q['numerator'](1 - self.a, self.b, self.c),
                    q['numerator'](self.a, 1 - self.b, self.c) / denominator if denominator != Fraction(1) else q['numerator'](self.a, 1 - self.b, self.c),
                    true_value * 2,
                    true_value / 2,
                    1 - true_value,  # Complement
                ]
                # Filter out same values and invalid values
                distortions = [d for d in distortions if d != true_value and d > 0 and d < 1]
                
                if distortions:
                    displayed_value = random.choice(distortions)
                else:
                    # Fallback: just use complement
                    displayed_value = 1 - true_value if true_value != Fraction(1, 2) else true_value + Fraction(1, 10)
            
            self.results.append({
                'is_correct': is_correct,
                'displayed_value': displayed_value,
                'true_value': true_value,
                'numerator': numerator,
                'denominator': denominator,
                'question_type': q,
            })
    
    def format_question_text(self, q_type: Dict) -> str:
        """Format question text using scenario terms."""
        condition = q_type['condition'].format(
            success=self.scenario['success'],
            failure=self.scenario['failure'],
        )
        target = q_type['target'].format(
            success=self.scenario['success'],
            failure=self.scenario['failure'],
        )
        return f"Biết {self.scenario['event']} thứ {condition.split()[-1]} {condition.rsplit(' ', 1)[0]}. Tính xác suất để {target}"
    
    def build_question_latex(self, idx: int) -> str:
        """Build the complete question in LaTeX format (Part II style)."""
        # Only generate if not already done
        if not self.results:
            self.generate_parameters()
            self.select_questions()
            self.calculate_and_distort()
        
        a_str = fraction_to_latex(self.a)
        b_str = fraction_to_latex(self.b)
        c_str = fraction_to_latex(self.c)
        
        # Build intro
        intro = self.scenario['intro'].replace("$a$", f"${a_str}$")
        intro = intro.replace("$b$", f"${b_str}$")
        intro = intro.replace("$c$", f"${c_str}$")
        
        lines = []
        lines.append(r"\begin{ex}%Câu " + str(idx))
        lines.append(intro)
        lines.append(r"\choiceTFt")
        
        # Build 4 statements
        for i, res in enumerate(self.results):
            q_type = res['question_type']
            val_str = fraction_to_latex(res['displayed_value'])
            
            # Build statement text
            condition = q_type['condition'].format(
                success=self.scenario['success'],
                failure=self.scenario['failure'],
            )
            target = q_type['target'].format(
                success=self.scenario['success'],
                failure=self.scenario['failure'],
            )
            
            stmt = f"Biết {condition}. Tính xác suất để {target} là ${val_str}$"
            
            if res['is_correct']:
                statement = rf"{{\True {stmt}}}"
            else:
                statement = rf"{{{stmt}}}"
            lines.append(statement)
        
        # Build solution (only numerical calculations)
        lines.append(r"\loigiai{")
        lines.append(r"\begin{itemchoice}")
        
        for res in self.results:
            q_type = res['question_type']
            true_val = res['true_value']
            numerator = res['numerator']
            denominator = res['denominator']
            
            # Reconstruct the question text for clarity
            condition = q_type['condition'].format(
                success=self.scenario['success'],
                failure=self.scenario['failure'],
            )
            target = q_type['target'].format(
                success=self.scenario['success'],
                failure=self.scenario['failure'],
            )
            stmt_text = f"Biết {condition}. Tính xác suất để {target}"
            
            # Build solution line: only numerical calculations
            num_sub = format_numerator_substitution(self.a, self.b, self.c, q_type)
            num_val = fraction_to_latex(numerator)
            result_str = fraction_to_latex(true_val)
            
            is_simple = q_type.get('is_simple', False)
            
            if is_simple:
                # Simple case: just the calculation
                sol_line = rf"\itemch {stmt_text}: ${num_sub} = {result_str}$"
            else:
                # Full fraction case
                denom_sub = format_denominator_substitution(self.a, self.b, self.c, q_type)
                denom_val = fraction_to_latex(denominator)
                sol_line = rf"\itemch {stmt_text}: $\dfrac{{{num_sub}}}{{{denom_sub}}} = \dfrac{{{num_val}}}{{{denom_val}}} = {result_str}$"
            
            lines.append(sol_line)
        
        lines.append(r"\end{itemchoice}")
        lines.append(r"}")
        lines.append(r"\end{ex}")
        
        return "\n".join(lines)


def generate_multiple_questions(n: int = 5) -> str:
    """Generate n questions, each with a different scenario."""
    questions = []
    scenario_keys = list(SCENARIOS.keys())
    
    for i in range(n):
        q = SalesConditionalProbabilityQuestion()
        # Force different scenarios for variety
        q.scenario_key = scenario_keys[i % len(scenario_keys)]
        q.scenario = SCENARIOS[q.scenario_key]
        q.a, q.b, q.c = generate_nice_fractions()
        q.select_questions()
        q.calculate_and_distort()
        
        questions.append(q.build_question_latex(i + 1))
    
    return "\n\n".join(questions)


def create_latex_document(content: str) -> str:
    """Wrap content in a complete LaTeX document."""
    return r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usepackage{enumerate}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\rfoot{Trang \thepage}

\newcounter{excounter}
\setcounter{excounter}{0}
\newenvironment{ex}[1][]{\refstepcounter{excounter}\par\medskip\noindent\textbf{Câu \theexcounter.} }{\par\medskip}
\newcommand{\choiceTFt}{\par}
\newcommand{\True}{\textbf{[Đ]} }
\newcommand{\loigiai}[1]{\par\noindent\textit{Lời giải:}\par #1}
\newenvironment{itemchoice}{\begin{enumerate}[a)]}{\end{enumerate}}
\newcommand{\itemch}{\item}

\begin{document}

""" + content + r"""

\end{document}
"""


def main():
    import sys
    
    num_questions = 5
    if len(sys.argv) > 1:
        try:
            num_questions = max(1, int(sys.argv[1]))
        except ValueError:
            print("Tham số không hợp lệ, sử dụng mặc định 5 câu hỏi.")
    
    content = generate_multiple_questions(num_questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "sales_conditional_probability.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    
    print(f"Đã tạo {num_questions} câu hỏi trong {output_path}")


if __name__ == "__main__":
    main()

