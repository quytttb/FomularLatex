"""
conditional_probability_generator.py

Sinh bài toán xác suất có điều kiện dạng Đúng/Sai (Phần II) theo mô hình:
- 3 lần thực hiện liên tiếp
- Xác suất lần đầu: a
- Nếu lần trước thành công => xác suất lần sau: b
- Nếu lần trước thất bại => xác suất lần sau: c
- Điều kiện: 0 < c < a < b < 1

Có 8 trường hợp có thể:
1. SSS: a.b.b
2. SSF: a.b.(1-b)
3. SFS: a.(1-b).c
4. SFF: a.(1-b).(1-c)
5. FSS: (1-a).c.b
6. FSF: (1-a).c.(1-b)
7. FFS: (1-a).(1-c).c
8. FFF: (1-a).(1-c).(1-c)
"""

import random
import os
from fractions import Fraction
from typing import List, Tuple, Dict

# ==================== SCENARIOS ====================

SCENARIOS = {
    'sales': {
        'intro': r"Một nhân viên bán hàng mỗi năm đến bán ở công ty X ba lần. Xác suất để lần đầu bán được hàng là $a$. Nếu lần trước bán được hàng thì xác suất để lần sau bán được hàng tăng lên là $b$; nếu lần trước không bán được hàng thì xác suất để lần sau bán được hàng chỉ là $c$.",
        'success': "bán được hàng",
        'failure': "không bán được hàng",
        'event': "lần",
    },
    'sports': {
        'intro': r"Một vận động viên ném bóng rổ thực hiện ba lần ném liên tiếp. Xác suất để lần đầu ném trúng là $a$. Nếu lần trước ném trúng thì xác suất để lần sau ném trúng tăng lên là $b$; nếu lần trước ném trượt thì xác suất để lần sau ném trúng chỉ là $c$.",
        'success': "ném trúng",
        'failure': "ném trượt",
        'event': "lần ném",
    },
    'exam': {
        'intro': r"Một học sinh làm ba bài kiểm tra liên tiếp. Xác suất để lần đầu đạt điểm giỏi là $a$. Nếu lần trước đạt điểm giỏi thì xác suất để lần sau đạt điểm giỏi tăng lên là $b$; nếu lần trước không đạt điểm giỏi thì xác suất để lần sau đạt điểm giỏi chỉ là $c$.",
        'success': "đạt điểm giỏi",
        'failure': "không đạt điểm giỏi",
        'event': "bài kiểm tra",
    },
    'machine': {
        'intro': r"Một máy sản xuất hoạt động trong ba ca liên tiếp. Xác suất để ca đầu tiên máy hoạt động tốt là $a$. Nếu ca trước máy hoạt động tốt thì xác suất để ca sau máy hoạt động tốt tăng lên là $b$; nếu ca trước máy gặp sự cố thì xác suất để ca sau máy hoạt động tốt chỉ là $c$.",
        'success': "hoạt động tốt",
        'failure': "gặp sự cố",
        'event': "ca",
    },
    'weather': {
        'intro': r"Một thành phố được quan sát thời tiết trong ba ngày liên tiếp. Xác suất để ngày đầu tiên có mưa là $a$. Nếu ngày trước có mưa thì xác suất để ngày sau có mưa tăng lên là $b$; nếu ngày trước không mưa thì xác suất để ngày sau có mưa chỉ là $c$.",
        'success': "có mưa",
        'failure': "không mưa",
        'event': "ngày",
    },
}

# 8 question types with formulas
QUESTION_TYPES = [
    {
        'id': 'SSS',
        'template': "Cả ba {event} đều {success}",
        'formula': lambda a, b, c: a * b * b,
        'latex_formula': r"a \cdot b \cdot b",
    },
    {
        'id': 'SSF',
        'template': "Chỉ hai {event} đầu {success}",
        'formula': lambda a, b, c: a * b * (1 - b),
        'latex_formula': r"a \cdot b \cdot (1-b)",
    },
    {
        'id': 'SFS',
        'template': "Chỉ {event} thứ 2 {failure}",
        'formula': lambda a, b, c: a * (1 - b) * c,
        'latex_formula': r"a \cdot (1-b) \cdot c",
    },
    {
        'id': 'SFF',
        'template': "Chỉ {event} đầu tiên {success}",
        'formula': lambda a, b, c: a * (1 - b) * (1 - c),
        'latex_formula': r"a \cdot (1-b) \cdot (1-c)",
    },
    {
        'id': 'FSS',
        'template': "Chỉ {event} đầu tiên {failure}",
        'formula': lambda a, b, c: (1 - a) * c * b,
        'latex_formula': r"(1-a) \cdot c \cdot b",
    },
    {
        'id': 'FSF',
        'template': "Chỉ {event} thứ hai {success}",
        'formula': lambda a, b, c: (1 - a) * c * (1 - b),
        'latex_formula': r"(1-a) \cdot c \cdot (1-b)",
    },
    {
        'id': 'FFS',
        'template': "Chỉ {event} cuối cùng {success}",
        'formula': lambda a, b, c: (1 - a) * (1 - c) * c,
        'latex_formula': r"(1-a) \cdot (1-c) \cdot c",
    },
    {
        'id': 'FFF',
        'template': "Cả ba {event} đều {failure}",
        'formula': lambda a, b, c: (1 - a) * (1 - c) * (1 - c),
        'latex_formula': r"(1-a) \cdot (1-c) \cdot (1-c)",
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


def format_substitution(a: Fraction, b: Fraction, c: Fraction, q_id: str) -> str:
    """Build substitution string based on question ID (SSS, SSF, etc.)."""
    a_str = fraction_to_latex(a)
    b_str = fraction_to_latex(b)
    c_str = fraction_to_latex(c)
    one_minus_a = fraction_to_latex(1 - a)
    one_minus_b = fraction_to_latex(1 - b)
    one_minus_c = fraction_to_latex(1 - c)
    
    # Build substitution based on question type
    parts = {
        'SSS': [a_str, b_str, b_str],
        'SSF': [a_str, b_str, one_minus_b],
        'SFS': [a_str, one_minus_b, c_str],
        'SFF': [a_str, one_minus_b, one_minus_c],
        'FSS': [one_minus_a, c_str, b_str],
        'FSF': [one_minus_a, c_str, one_minus_b],
        'FFS': [one_minus_a, one_minus_c, c_str],
        'FFF': [one_minus_a, one_minus_c, one_minus_c],
    }
    
    p = parts.get(q_id, [a_str, b_str, c_str])
    return rf"{p[0]} \cdot {p[1]} \cdot {p[2]}"


class ConditionalProbabilityQuestion:
    def __init__(self):
        self.scenario_key = ""
        self.scenario = {}
        self.a = Fraction(0)
        self.b = Fraction(0)
        self.c = Fraction(0)
        self.selected_questions = []
        self.results = []  # List of (is_correct, displayed_value, true_value)
    
    def generate_parameters(self):
        """Pick random scenario and generate a, b, c."""
        self.scenario_key = random.choice(list(SCENARIOS.keys()))
        self.scenario = SCENARIOS[self.scenario_key]
        self.a, self.b, self.c = generate_nice_fractions()
    
    def select_questions(self):
        """Select 4 random questions from the 8 types."""
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
            true_value = q['formula'](self.a, self.b, self.c)
            
            is_correct = i in true_indices
            
            if is_correct:
                displayed_value = true_value
            else:
                # Distort: use wrong formula or multiply/add small error
                distortions = [
                    q['formula'](1 - self.a, self.b, self.c),
                    q['formula'](self.a, 1 - self.b, self.c),
                    q['formula'](self.a, self.b, 1 - self.c),
                    q['formula'](self.c, self.b, self.a),  # swap a and c
                    true_value * 2,
                    true_value / 2,
                ]
                # Filter out same values
                distortions = [d for d in distortions if d != true_value and d > 0 and d < 1]
                
                if distortions:
                    displayed_value = random.choice(distortions)
                else:
                    # Fallback: just use a different fraction
                    displayed_value = true_value + Fraction(1, 10) if true_value < Fraction(9, 10) else true_value - Fraction(1, 10)
            
            self.results.append({
                'is_correct': is_correct,
                'displayed_value': displayed_value,
                'true_value': true_value,
                'question_type': q,
            })
    
    def format_question_text(self, q_type: Dict) -> str:
        """Format question text using scenario terms."""
        template = q_type['template']
        return template.format(
            event=self.scenario['event'],
            success=self.scenario['success'],
            failure=self.scenario['failure'],
        )
    
    def build_question_latex(self, idx: int) -> str:
        """Build the complete question in LaTeX format (Part II style)."""
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
            q_text = self.format_question_text(res['question_type'])
            val_str = fraction_to_latex(res['displayed_value'])
            
            if res['is_correct']:
                statement = rf"{{\True Xác suất để {q_text} là ${val_str}$}}"
            else:
                statement = rf"{{Xác suất để {q_text} là ${val_str}$}}"
            lines.append(statement)
        
        # Build solution
        lines.append(r"\loigiai{")
        lines.append(r"\begin{itemchoice}")
        
        for res in self.results:
            q_type = res['question_type']
            true_val = res['true_value']
            is_correct = res['is_correct']
            
            # Build solution line: only numerical calculations
            substitution = format_substitution(self.a, self.b, self.c, q_type['id'])
            result_str = fraction_to_latex(true_val)
            
            # Get question text for clarity
            q_text = self.format_question_text(q_type)
            
            sol_line = rf"\itemch Xác suất để {q_text} là: ${substitution} = {result_str}$"
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
        q = ConditionalProbabilityQuestion()
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
    
    output_path = os.path.join(os.path.dirname(__file__), "conditional_probability.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    
    print(f"Đã tạo {num_questions} câu hỏi trong {output_path}")


if __name__ == "__main__":
    main()

