import random
import sys
from string import Template
from typing import Any, Dict, Optional, Tuple
import os
from fractions import Fraction

# ==================== CONFIGURATION & HELPERS ====================

def format_money(value: int) -> str:
    return "{:,}".format(int(value)).replace(",", ".")

def format_vn_number(value, precision=2):
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def format_fraction_or_int(value):
    """Format số: nếu nguyên thì hiển thị nguyên, nếu không thì hiển thị phân số."""
    frac = Fraction(value).limit_denominator(1000)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"\\dfrac{{{frac.numerator}}}{{{frac.denominator}}}"

def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{patterns, calc}
\begin{document}
""" + content + r"\end{document}"

# ==================== QUESTION: PYRAMID OF ARCHES AREA ====================

TEMPLATE_Q = Template(
    r"""
Tính diện tích hình được tô đậm như hình vẽ:
${diagram_q}
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:

Tầng 1: \(S_{\text{hình chữ nhật}} = ${h} \cdot ${rect1_w} = ${s_rect1}\).

\(S_{\text{parabol}} = \dfrac{2}{3} \cdot ${h} \cdot ${wing1_w} = ${s_wing1}\).

Tầng 2: \(S_{\text{hình chữ nhật}} = ${h} \cdot ${rect2_w} = ${s_rect2}\).

\(S_{\text{parabol}} = \dfrac{2}{3} \cdot ${h} \cdot ${wing2_w} = ${s_wing2}\).

Tầng 3: \(S_{\text{parabol}} = \dfrac{2}{3} \cdot ${h} \cdot ${arch6_w} = ${s_arch3}\).

\(\Rightarrow S = (${s_rect1} + ${s_wing1}) + (${s_rect2} + ${s_wing2}) + ${s_arch3} = ${ans_tex}\).

Đáp án: ${ans_dot} | ${ans}
"""
)

# Seed đặc biệt: ép w=4, h=8 (đề mẫu; wh=32 không thỏa wh%3==0 nên không random ra được).
SEED_DEMO_W4_H8 = 48

# w chẵn (để 2.5w nguyên), wh chia hết 3 (để tất cả trung gian nguyên)
W_POOL = list(range(2, 42, 2))  # 20 giá trị chẵn: 2, 4, 6, ..., 40
H_POOL = list(range(2, 22))     # 20 giá trị: 2, 3, ..., 21

class MaiVomAreaQuestion:
    """Nếu fixed_wh không None thì generate_parameters dùng (w, h) cố định."""
    fixed_wh: Optional[Tuple[int, int]] = None

    def __init__(self):
        self.w = 4
        self.h = 8

    def generate_parameters(self):
        """Random w (chẵn) và h sao cho wh chia hết cho 3, trừ khi có fixed_wh."""
        if self.fixed_wh is not None:
            self.w, self.h = self.fixed_wh
            return
        while True:
            self.w = random.choice(W_POOL)
            self.h = random.choice(H_POOL)
            if (self.w * self.h) % 3 == 0:
                break

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        w = Fraction(self.w)
        h = Fraction(self.h)

        # TikZ cố định: cung 1,3 rộng 3 ô, cung 2 rộng 2 ô,
        # cung 4,5,6 rộng 2.5 ô. Mỗi ô = w, mỗi tầng cao = h.
        # A_x=1.5w, B_x=4w, C_x=6.5w, D_x=2.75w, E_x=5.25w

        # Tầng 1: HCN trong (A→C) + 2 cánh parabol (nửa cung 1 + nửa cung 3)
        rect1_w = Fraction(5) * w           # C_x - A_x = 5w
        wing1_w = Fraction(3) * w           # nửa(3w) + nửa(3w) = 3w
        s_rect1 = rect1_w * h
        s_wing1 = Fraction(2, 3) * wing1_w * h

        # Tầng 2: HCN trong (D→E) + 2 cánh parabol (nửa cung 4 + nửa cung 5)
        rect2_w = Fraction(5, 2) * w        # E_x - D_x = 2.5w
        wing2_w = Fraction(5, 2) * w        # nửa(2.5w) + nửa(2.5w) = 2.5w
        s_rect2 = rect2_w * h
        s_wing2 = Fraction(2, 3) * wing2_w * h

        # Tầng 3: 1 cung parabol đầy đủ (D→E)
        arch6_w = Fraction(5, 2) * w        # 2.5w
        s_arch3 = Fraction(2, 3) * arch6_w * h

        total = (s_rect1 + s_wing1) + (s_rect2 + s_wing2) + s_arch3

        f = format_fraction_or_int
        answer = f(total)
        if total.denominator == 1:
            ans_comma = str(int(total))
        else:
            ans_comma = format_vn_number(float(total))
        ans_dot = ans_comma.replace(",", ".")

        return answer, {
            "h": f(h),
            "rect1_w": f(rect1_w), "s_rect1": f(s_rect1),
            "wing1_w": f(wing1_w), "s_wing1": f(s_wing1),
            "rect2_w": f(rect2_w), "s_rect2": f(s_rect2),
            "wing2_w": f(wing2_w), "s_wing2": f(s_wing2),
            "arch6_w": f(arch6_w), "s_arch3": f(s_arch3),
            "ans_tex": answer,
            "ans": ans_comma,
            "ans_dot": ans_dot,
            "diagram_q": self.generate_tikz_question()
        }

    def generate_tikz_question(self) -> str:
        """Hình TikZ cố định; chỉ thay nhãn độ dài: 1 ô ngang = w, 2 ô dọc = h."""
        w_lbl = format_vn_number(self.w)
        h_lbl = format_vn_number(self.h)
        return rf"""
\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.7]
   \draw[xstep=1cm,ystep=2cm,opacity=0.2] 
   (0,0) grid (8,6) 
   ;
   \draw[fill=violet!50,opacity=0.2] (0,0) ..controls +(80:0.7) and +(180:0.6) .. (1.5,2) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2)..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)  .. controls +(0:0.6) and +(100:0.7) .. ++(1.5,-2)--cycle;
   \draw[<->] (0.,-0.25)--++(1,0) node[below,pos=0.5]{{${w_lbl}$}};
   \draw[<->] (-0.25,0)--++(0,2)node[left,pos=0.5]{{${h_lbl}$}};
   \begin{{scope}}[red]
    \draw (0,0)--(8,0);
    \draw (0,0) ..controls +(80:0.7) and +(180:0.6) .. (1.5,2).. controls +(0:0.6) and +(100:0.7) .. (3,0);
    \draw (3,0) ..controls +(80:0.7) and +(180:0.6) .. (4,2) 
    .. controls +(0:0.6) and +(100:0.7) .. (5,0)
    ;
    \draw (5,0) ..controls +(80:0.7) and +(180:0.6) .. ++(1.5,2) 
    .. controls +(0:0.6) and +(100:0.7) .. ++(1.5,-2)
    ;
    \draw (1.5,2) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) 
    .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)
    ;
    \draw (4,2) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) 
    .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)
    ;
    \draw (2.75,4) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) 
    .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)
    ;
   \end{{scope}}
   \fill 
   (1.5,2) coordinate (A) circle(1.5pt) node[above left]{{$A$}}
   (4,2) circle(1.5pt) node[above left]{{$B$}}
   (6.5,2) circle(1.5pt) node[above right]{{$C$}}
   ($(A)+(1.25,2)$)coordinate (D) circle(1.5pt) node[above left]{{$D$}}
   ($(D)+(1.25,2)$) circle(1.5pt) node[above left]{{$F$}}
   ($(A)+(3.75,2)$)coordinate (D) circle(1.5pt) node[above right]{{$E$}}
   ;
  \end{{tikzpicture}}
"""


    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        return f"Câu {idx}: {question}\n\n{solution}"

# ==================== MAIN ====================

def main():
    num_questions = 1
    seed = None
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            print("Tham số 1 phải là số nguyên (số lượng câu hỏi)")
            return
    
    if len(sys.argv) > 2:
        try:
            seed = int(sys.argv[2])
            random.seed(seed)
        except ValueError:
            pass

    MaiVomAreaQuestion.fixed_wh = None
    if seed == SEED_DEMO_W4_H8:
        MaiVomAreaQuestion.fixed_wh = (4, 8)
        print("Seed 48: cố định w = 4, h = 8 (đề mẫu).")

    questions = []
    for i in range(num_questions):
        q = MaiVomAreaQuestion()
        questions.append(q.generate_question(i+1))

    MaiVomAreaQuestion.fixed_wh = None
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "tinh_dien_tich_mai_vom.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong tinh_dien_tich_mai_vom.tex")

if __name__ == "__main__":
    main()
