import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple

# ==================== CONFIGURATION & HELPERS ====================

def format_money(value: int) -> str:
    return "{:,}".format(int(value)).replace(",", ".")

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

# ==================== QUESTION 8: WELL AND RIVER (PARABOLA LOCUS) ====================

TEMPLATE_Q8 = Template(
    r"""
Một lập trình viên tạo một trò chơi. Trong trò chơi đó có một vùng đất hình chữ nhật \(ABCD\) có độ dài các cạnh \(AB = ${length}\) m và \(AD = ${width}\) m. Một con sông nằm bên cạnh vùng đất đó với \(AD\) là bờ sông. Một giếng nước khoan được đặt tại điểm \(I\) nằm trong hình chữ nhật, cách các cạnh \(AB, CD\) một khoảng ${half_width} m, cách cạnh \(BC\) ${dist_BC} m và cách cạnh \(AD\) ${dist_river} m. Nhân vật trong game khi đến cùng đất này cần phải di chuyển đến giếng nước hoặc bờ sông để lấy nước. Lập trình viên muốn tô màu một phần của vùng đất đó sao cho khi đứng trong cùng tô màu này, nhân vật di chuyển đến giếng nước để lấy nước nhanh hơn so với đến bờ sông. Diện tích vùng tô màu đó là bao nhiêu mét vuông?

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOL_Q8 = Template(
    r"""
Chọn hệ trục \(Axy\) với \(A(0;0)\), \(D(0;${width})\), \(B(${length};0)\). Giếng \(I(${dist_river}; ${half_width})\).

Điều kiện để đến giếng nhanh hơn: \(MI < d(M, Oy) \Leftrightarrow x > \frac{(y-${half_width})^2}{${two_xi}} + ${half_xi}\).

Diện tích vùng tô màu:

\(S = \int_{0}^{${width}} \left( ${length} - \left[ \frac{(y-${half_width})^2}{${two_xi}} + ${half_xi} \right] \right) dy = ${val_rect_part} - ${val_integral_1} \approx ${area_final} \, (\text{m}^2)\).

Chi phí: \(T = S \times ${raw_price_color} \approx ${total_cost} \text{ đồng}\).
"""
)

class Question8:
    def __init__(self):
        self.width = 40
        self.length = 80
        self.dist_river = 60
        self.price_color = 50000

    def generate_parameters(self):
        self.width = random.randint(20, 80)
        self.length = random.randint(self.width + 20, self.width * 3)
        
        min_xi = int(self.length * 0.4)
        max_xi = int(self.length * 0.9)
        self.dist_river = random.randint(min_xi, max_xi)
        
        for _ in range(10):
            val_at_boundary = (self.width/2)**2 / (2*self.dist_river) + self.dist_river/2
            if val_at_boundary < self.length:
                break
            self.dist_river = random.randint(min_xi, max_xi)

        self.price_color = random.randint(20, 100) * 1000

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        W = self.width
        L = self.length
        x_I = self.dist_river
        
        term1 = (W**3) / (24 * x_I)
        term2 = (x_I * W) / 2
        
        area_left = term1 + term2
        area_final = (L * W) - area_left
        
        cost = area_final * self.price_color
        cost_k = cost / 1000
        
        return f"{format_vn_number(cost_k, 0)}", {
            "width": W, "length": L, "dist_river": x_I,
            "dist_BC": L - x_I,
            "half_width": format_vn_number(W/2, 1),
            "two_xi": 2*x_I,
            "half_xi": format_vn_number(x_I/2, 1),
            "val_integral_1": format_vn_number(term1, 2),
            "val_rect_part": format_vn_number(L*W - term2, 2),
            "area_final": format_vn_number(area_final, 2),
            "raw_price_color": self.price_color,
            "price_color": format_money(self.price_color),
            "total_cost": format_money(round(cost)),
            "total_cost_k": format_vn_number(cost_k, 0)
        }

    def generate_tikz(self) -> str:
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.6,violet]
   \draw 
   (0,0) coordinate (C)
   (8,0) coordinate (D)
   (8,4) coordinate (A)
   (0,4) coordinate (B)
   (2,2) coordinate (I)
   ;
   \draw (C)--(D)--(A)--(B)--cycle;
    \foreach \p/\r in {A/120,B/60,C/-60,D/-120,I/0}
    \fill (\p) circle (1.2pt) node[shift={(\r:3mm)}]{\(\p\)};
   \draw 
   (D)--($(D)!-0.25!(A)$) coordinate (D')
   (A)--($(A)!-0.25!(D)$) coordinate (A')
   ([xshift=1.5cm]D')--([xshift=1.5cm]A')
   ($(A)!0.5!(D)+(0.75,0)$) node[]{Sông}
   ;  
 \end{tikzpicture}"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_Q8.substitute(params, diagram=tikz)
        solution = TEMPLATE_SOL_Q8.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== MAIN ====================

def main():
    question_types = [Question8]
    
    num_questions = 1
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
            q_type = random.choice(question_types)
        else:
            q_type = question_types[question_type_idx - 1]
        q = q_type()
        questions.append(q.generate_question(i+1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    import os
    output_path = os.path.join(os.path.dirname(__file__), "cac_bai_toan_ve_bieu_dien_thong_thuong.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong cac_bai_toan_ve_bieu_dien_thong_thuong.tex")

if __name__ == "__main__":
    main()
