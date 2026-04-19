import logging
import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple

# Helper for integration
def integrate(f, a, b, n=1000):
    h = (b - a) / n
    s = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        s += f(a + i * h)
    return s * h

def format_vn_number(value, precision=2):
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

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

# ------------------------------------------------------------------
# Question Type 11: Flower
# ------------------------------------------------------------------
class QuestionType11:
    def __init__(self):
        self.side = 0

    def generate_parameters(self):
        self.side = random.randint(40, 100)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        b = a / 2.0
        
        def x_curve(y):
            term = 2*y**2 - 4*b*y + 3*b**2
            if term < 0: return y
            return y - b + math.sqrt(term)
            
        def gap_func(y):
            return b - x_curve(y)
            
        gap_area_octant = integrate(gap_func, 0, b, 1000)
        total_gap = 8 * gap_area_octant
        flower_area = a**2 - total_gap
        
        return f"{round(flower_area)}", {
            "side": a,
            "area": format_vn_number(flower_area, 2)
        }

    def generate_tikz(self) -> str:
        return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
   \draw[line width=1pt] (-2,-2)coordinate (A)--(2,-2)coordinate (B)--(2,2)coordinate (C)--(-2,2)coordinate (D)--cycle
   ;
   
   \draw[fill=violet!30,draw=red] (-2,2) ..controls +(-15:2) and +(-135:1) .. (2,2)
   ..controls +(-125+10:2) and +(90+15:1) ..
   (2,-2)..controls +(165:2) and +(45:1) ..(-2,-2)
   ..controls +(55:2) and +(-75:1) .. cycle
   ; 
   
   \foreach \p/\r in {A/-140,B/-40,C/40,D/140}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
   
   \fill 
   (0,0) circle(1.2pt)
   (1,-0.5) node[]{$\color{red} (L)$}
   ;
 \end{tikzpicture}
"""

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        
        question_template = Template(
            r"""
Người ta thiết kế hoa văn trên những viên gạch lát sàn hình vuông \(ABCD\) có độ dài cạnh là ${side} cm với phần ở giữa là một bông hoa giới hạn bởi đường cong kín \((L)\).
Biết rằng nếu \(M\) là điểm thuộc \((L)\) thì tích khoảng cách từ nó đến hai đường chéo của hình vuông bằng tích khoảng cách từ nó đến hai cạnh \(AB, AD\) hoặc \(CB, CD\).
Diện tích của bông hoa trên mỗi viên gạch này là bao nhiêu \(cm^2\) (làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
        )
        
        solution_template = Template(
            r"""
Chọn hệ trục tọa độ với gốc \(O\) là tâm hình vuông, các trục tọa độ song song với các cạnh.\\
Giả sử cạnh hình vuông là \(a = ${side}\), suy ra \(b = a/2\).\\
Xét trong góc phần tư thứ nhất (phần tám thứ nhất \(0 \le y \le x \le b\)).\\
Phương trình đường chéo là \(y=x\). Khoảng cách đến hai đường chéo là \(d_1 = \frac{x-y}{\sqrt{2}}\) và \(d_2 = \frac{x+y}{\sqrt{2}}\).\\
Tích khoảng cách đến hai đường chéo: \(d_1 d_2 = \frac{x^2 - y^2}{2}\).\\
Khoảng cách đến hai cạnh \(x=b\) và \(y=b\) là \(b-x\) và \(b-y\).\\
Theo giả thiết: \(\frac{x^2 - y^2}{2} = (b-x)(b-y)\).\\
Giải phương trình này theo \(x\), ta được: \(x = y - b + \sqrt{2y^2 - 4by + 3b^2}\).\\
Diện tích phần "khe hở" (phần nằm ngoài bông hoa) trong một phần tám hình vuông là diện tích giới hạn bởi đường cong và đường thẳng \(x=b\):\\
\(S_{gap\_oct} = \int_{0}^{b} (b - x) \text{d}y = \int_{0}^{b} (2b - y - \sqrt{2y^2 - 4by + 3b^2}) \text{d}y\).\\
Tổng diện tích các khe hở là \(8 \times S_{gap\_oct}\).\\
Diện tích bông hoa: \(S = a^2 - 8 S_{gap\_oct} \approx ${area} \, (cm^2)\).
"""
        )
        
        question = question_template.substitute(side=params["side"], diagram=self.generate_tikz())
        solution = solution_template.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ------------------------------------------------------------------
# Question Type 16: Orange Shapes
# ------------------------------------------------------------------
class QuestionType16:
    def __init__(self):
        self.side = 0

    def generate_parameters(self):
        self.side = random.randint(40, 100)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        
        k = 0.5 + math.sqrt(2) - (2 + math.sqrt(2)) * math.log((1 + math.sqrt(2)) / math.sqrt(2))
        
        area = (a**2) * (1 - 4*k)
        
        return f"{round(area)}", {
            "side": a,
            "area": format_vn_number(area, 2)
        }

    def generate_tikz(self) -> str:
        return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1.2]
   \draw[fill=yellow] (-1.425,-1.425) coordinate (B) --(1.425,-1.425) coordinate (C) -- (1.425,1.425)
   coordinate (D) -- (-1.425,1.425) coordinate (A)--cycle
   ;
   \foreach \p/\r in {A/140,B/-140,C/-40,D/40}
   \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{$\p$};
   
   
   \draw[fill=orange!50!yellow] 
   (45:0.7) ..controls +(-135+30:0.1) and +(135-10:1) .. (-45:2)
   ..controls +(135+10:1) and +(45-30:0.1) .. (-135:0.7)
   ..controls +(45+30:0.1) and +(-45-10:1) .. (135:2)
   ..controls +(-45+10:1) and +(-135-30:0.1) ..cycle
   ;
   \draw (135:0.5) node{$s$};
   
   \draw[fill=orange] 
   (45:0.7)..controls +(90:0.5) and +(-135-25:0.1).. (45:2)
   ..controls +(-135+25:0.5) and +(45-45:0.5).. cycle
   ;
   \draw[fill=orange,xscale=-1,yscale=-1] 
   (45:0.7)..controls +(90:0.5) and +(-135-25:0.1).. (45:2)
   ..controls +(-135+25:0.5) and +(45-45:0.5).. cycle
   ;
   \end{tikzpicture}
"""

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        
        question_template = Template(
            r"""
Cho hình vuông \(ABCD\) cạnh bằng ${side} cm.
Gọi \(M\) là tập hợp các điểm thỏa mãn với các tam giác vuông có đỉnh của hình vuông \(ABCD\) nhận \(AC\) làm cạnh huyền.
Tích khoảng cách từ \(M\) đến cạnh huyền \(AC\) và một cạnh góc vuông bằng tích độ dài cạnh hình vuông và khoảng cách từ \(M\) đến cạnh góc vuông còn lại.
Tập hợp các điểm \(M\) tạo thành đường cong \((L)\) như hình vẽ.
Hãy xác định diện tích phần tô đậm \(S\) như hình vẽ (phần tô màu cam chứa tâm hình vuông ở giữa). Kết quả làm tròn đến hàng đơn vị.

\begin{center}
${diagram}
\end{center}
"""
        )
        
        solution_template = Template(
            r"""
Xét một cạnh của hình vuông, ví dụ cạnh \(BC\) với \(B(0;0)\), \(C(a;0)\) và \(A(0;a)\).\\
Cạnh huyền \(AC\) có phương trình \(x+y-a=0\).\\
Điểm \(M(x;y)\) thỏa mãn tích khoảng cách từ \(M\) đến \(AC\) và \(AB\) (\(x=0\)) bằng tích cạnh hình vuông \(a\) và khoảng cách đến \(BC\) (\(y=0\)):\\
\(\frac{a-x-y}{\sqrt{2}} \cdot x = a \cdot y \Rightarrow ax - x^2 - xy = y a \sqrt{2} \Rightarrow y(a\sqrt{2} + x) = ax - x^2\).\\
Suy ra phương trình đường cong giới hạn một cánh hoa: \(y = \frac{ax - x^2}{x + a\sqrt{2}}\).\\
Diện tích một cánh hoa (phần màu cam ở cạnh):\\
\(S_p = \int_{0}^{a} \frac{ax - x^2}{x + a\sqrt{2}} \text{d}x = a^2 \left( \frac{1}{2} + \sqrt{2} - (2+\sqrt{2})\ln\frac{1+\sqrt{2}}{\sqrt{2}} \right)\).\\
Diện tích phần tô đậm ở giữa bằng diện tích hình vuông trừ đi 4 lần diện tích cánh hoa:\\
\(S = a^2 - 4S_p = a^2 \left[ 1 - 4\left( \frac{1}{2} + \sqrt{2} - (2+\sqrt{2})\ln\frac{1+\sqrt{2}}{\sqrt{2}} \right) \right] \approx ${area} \, (cm^2)\).
"""
        )
        
        question = question_template.substitute(side=params["side"], diagram=self.generate_tikz())
        solution = solution_template.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    question_types = [QuestionType11, QuestionType16]
    
    num_questions = 2
    question_type_idx = None
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            print("Tham số 1 phải là số nguyên (số lượng câu hỏi)")
            return
    
    if len(sys.argv) > 2:
        try:
            question_type_idx = int(sys.argv[2])
            if question_type_idx < 1 or question_type_idx > len(question_types):
                print(f"Tham số 2 phải từ 1 đến {len(question_types)}")
                return
        except ValueError:
            print("Tham số 2 phải là số nguyên (loại câu hỏi)")
            return
            
    questions = []
    for i in range(num_questions):
        if question_type_idx is None:
            q_class = question_types[i % len(question_types)]
        else:
            q_class = question_types[question_type_idx - 1]
        q = q_class()
        questions.append(q.generate_question(i+1))
        
    content = "\n\n".join(questions)
    latex = create_latex_document(content)
    
    import os
    output_path = os.path.join(os.path.dirname(__file__), "cac_bai_toan_ve_tich_khoang_cach.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong cac_bai_toan_ve_tich_khoang_cach.tex")

if __name__ == "__main__":
    main()
