import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple
import os

# ==================== CONFIGURATION & HELPERS ====================

def format_money(value: int) -> str:
    return "{:,}".format(int(value)).replace(",", ".")

def format_vn_number(value, precision=2):
    if isinstance(value, int) or value.is_integer():
        return str(int(value))
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

# ==================== QUESTION: PYRAMID OF ARCHES AREA ====================

TEMPLATE_Q = Template(
    r"""
Tính diện tích hình được tô đậm như hình vẽ:
\begin{center}
${diagram_q}
\end{center}
"""
)

TEMPLATE_SOL = Template(
    r"""
Lời giải:

\begin{center}
${diagram_sol}
\end{center}

Gọi \(G, H, I, J\) lần lượt là các điểm trên đáy; \(A, B, C\) là các đỉnh cung tầng 1; \(D, E\) là các đỉnh cung tầng 2; \(F\) là đỉnh cung tầng 3.

Ta có: \(GJ = ${w_bottom}\), \(GH = ${w_left}\), \(HI = ${w_para_mid}\), \(IJ = ${w_right}\), chiều cao mỗi tầng \(= ${h}\).

Tầng 1 (từ đáy đến AB, BC):

\(S_{GHJC} = GJ \cdot ${h} = ${w_bottom} \cdot ${h} = ${s_hcn_duoi}\)

\(S_{\text{cung } GAH} = \dfrac{2}{3} \cdot GH \cdot ${h} = \dfrac{2}{3} \cdot ${w_left} \cdot ${h} = ${s_para_left_str}\)

\(S_{\text{cung } HBI} = \dfrac{2}{3} \cdot HI \cdot ${h} = \dfrac{2}{3} \cdot ${w_para_mid} \cdot ${h} = ${s_para_mid_str}\)

\(S_{\text{cung } ICJ} = \dfrac{2}{3} \cdot IJ \cdot ${h} = \dfrac{2}{3} \cdot ${w_right} \cdot ${h} = ${s_para_right_str}\)

\(S_{\text{tầng 1}} = S_{GHJC} - S_{\text{cung } GAH} - S_{\text{cung } HBI} - S_{\text{cung } ICJ} = ${s_tang1_str}\)

Tầng 2 (từ AC đến DE):

\(S_{ACEF_{hcn}} = AC \cdot ${h} = ${w_top} \cdot ${h} = ${s_hcn_tren}\)

\(S_{\text{cung } ADB} = \dfrac{2}{3} \cdot AB \cdot ${h} = \dfrac{2}{3} \cdot ${w_side_gap} \cdot ${h} = ${s_para_side_str}\)

\(S_{\text{cung } BEC} = \dfrac{2}{3} \cdot BC \cdot ${h} = \dfrac{2}{3} \cdot ${w_side_gap} \cdot ${h} = ${s_para_side_str}\)

\(S_{\text{tầng 2}} = S_{ACEF_{hcn}} - S_{\text{cung } ADB} - S_{\text{cung } BEC} = ${s_tang2_str}\)

Tầng 3 (cung DFE):

\(S_{\text{cung } DFE} = \dfrac{2}{3} \cdot DE \cdot ${h} = \dfrac{2}{3} \cdot ${w_top} \cdot ${h} = ${s_para_top_str}\)

Tổng diện tích:

\(S = S_{\text{tầng 1}} + S_{\text{tầng 2}} + S_{\text{tầng 3}} = ${s_tang1_str} + ${s_tang2_str} + ${s_para_top_str} = ${total_area_str}\)

Đáp án: \(${ans_dot}\) | \(${ans}\)
"""
)

class MaiVomAreaQuestion:
    def __init__(self):
        # Mặc định đúng theo ví dụ mẫu:
        # - Chiều cao mỗi cung: 8
        # - Đáy dưới: 20
        # - Cung parabol giữa đáy: rộng 12
        # - Phần "tầng trên": rộng 10, hai vai: 5
        self.h = 8
        self.w_bottom = 20
        self.w_para_mid = 12
        self.w_top = 10
        self.w_side_gap = 5
        self.w_left = 4  # Cung trái
        self.w_right = 4 # Cung phải

    def generate_parameters(self):
        """
        Random các tham số:
        - h: chiều cao mỗi tầng (bội số của 3 để 2/3*h đẹp, hoặc số nguyên nhỏ)
        - w_top: độ rộng tầng trên (số chẵn để chia đôi đẹp)
        - w_side_gap: độ rộng vai (số nguyên)
        - w_bottom = w_left + w_para_mid + w_right
        - w_para_mid: độ rộng cung giữa đáy
        """
        self.h = random.choice([3, 6, 9, 12]) 
        
        # w_top chẵn từ 6 đến 14
        self.w_top = random.randrange(6, 16, 2) 
        
        # gap từ 3 đến 8 (khoảng cách AB và BC)
        self.w_side_gap = random.randint(3, 8)
        
        # w_left, w_right: độ rộng cung trái và phải ở tầng dưới
        self.w_left = random.randint(3, 6)
        self.w_right = random.randint(3, 6)
        
        # w_para_mid: độ rộng cung giữa đáy
        self.w_para_mid = self.w_top + 2 * self.w_side_gap - self.w_left - self.w_right
        if self.w_para_mid < 2:
            self.w_para_mid = random.randint(4, 8)
        
        self.w_bottom = self.w_left + self.w_para_mid + self.w_right

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        h = self.h
        w_bot = self.w_bottom
        w_mid = self.w_para_mid
        w_top = self.w_top
        w_side = self.w_side_gap
        w_left = self.w_left
        w_right = self.w_right
        
        # Tầng 1: Hình chữ nhật đáy - 3 cung parabol
        s_hcn_duoi = w_bot * h
        s_para_left = (2/3) * w_left * h
        s_para_mid = (2/3) * w_mid * h
        s_para_right = (2/3) * w_right * h
        s_tang1 = s_hcn_duoi - s_para_left - s_para_mid - s_para_right
        
        # Tầng 2: Hình chữ nhật AC - 2 cung vai
        s_hcn_tren = w_top * h
        s_para_side_one = (2/3) * w_side * h
        s_tang2 = s_hcn_tren - 2 * s_para_side_one
        
        # Tầng 3: Cung trên cùng
        s_para_top = (2/3) * w_top * h
        
        total_area_val = s_tang1 + s_tang2 + s_para_top
        
        # Format đáp án
        answer_comma = format_vn_number(total_area_val)
        answer_dot = answer_comma.replace(',', '.')
        
        return answer_comma, {
            "h": h,
            "w_bottom": w_bot,
            "w_para_mid": w_mid,
            "w_top": w_top,
            "w_side_gap": w_side,
            "w_left": w_left,
            "w_right": w_right,
            "s_hcn_duoi": format_vn_number(s_hcn_duoi),
            "s_para_left_str": format_vn_number(s_para_left),
            "s_para_mid_str": format_vn_number(s_para_mid),
            "s_para_right_str": format_vn_number(s_para_right),
            "s_tang1_str": format_vn_number(s_tang1),
            "s_hcn_tren": format_vn_number(s_hcn_tren),
            "s_para_side_str": format_vn_number(s_para_side_one),
            "s_tang2_str": format_vn_number(s_tang2),
            "s_para_top_str": format_vn_number(s_para_top),
            "total_area_str": format_vn_number(total_area_val),
            "ans": answer_comma,
            "ans_dot": answer_dot,
            "diagram_q": self.generate_tikz_question(),
            "diagram_sol": self.generate_tikz_solution()
        }

    def generate_tikz_question(self) -> str:
        """Vẽ hình cho đề bài - không có nhãn điểm."""
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8]

   \draw[xstep=1cm,ystep=2cm,opacity=0.2] 
   (0,0) grid (8,6) 
   ;

   \draw[fill=violet!50,opacity=0.5] (0,0) ..controls +(80:0.7) and +(180:0.6) .. (1.5,2) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2)..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)  .. controls +(0:0.6) and +(100:0.7) .. ++(1.5,-2)--cycle;

   \draw[<->] (0.,-0.25)--++(1,0) node[below,pos=0.5]{$4$};
   \draw[<->] (-0.25,0)--++(0,2)node[left,pos=0.5]{$8$};

   \begin{scope}[red]
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
   \end{scope}

  \end{tikzpicture}"""

    def generate_tikz_solution(self) -> str:
        """Vẽ hình cho lời giải - có đầy đủ nhãn điểm."""
        return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8]

   \draw[xstep=1cm,ystep=2cm,opacity=0.2] 
   (0,0) grid (8,6) 
   ;

   \draw[fill=violet!50,opacity=0.5] (0,0) ..controls +(80:0.7) and +(180:0.6) .. (1.5,2) ..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2)..controls +(80:0.7) and +(180:0.6) .. ++(1.25,2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2) .. controls +(0:0.6) and +(100:0.7) .. ++(1.25,-2)  .. controls +(0:0.6) and +(100:0.7) .. ++(1.5,-2)--cycle;

   \draw[<->] (0.,-0.25)--++(1,0) node[below,pos=0.5]{$4$};
   \draw[<->] (-0.25,0)--++(0,2)node[left,pos=0.5]{$8$};

   \begin{scope}[red]
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
   \end{scope}

   % Điểm trên đáy
   \fill (0,0) circle(1.5pt) node[below left]{$G$};
   \fill (3,0) circle(1.5pt) node[below]{$H$};
   \fill (5,0) circle(1.5pt) node[below]{$I$};
   \fill (8,0) circle(1.5pt) node[below right]{$J$};
   
   % Điểm tầng 1
   \fill (1.5,2) coordinate (A) circle(1.5pt) node[above left]{$A$};
   \fill (4,2) circle(1.5pt) node[above]{$B$};
   \fill (6.5,2) circle(1.5pt) node[above right]{$C$};
   
   % Điểm tầng 2
   \fill ($(A)+(1.25,2)$) coordinate (D) circle(1.5pt) node[above left]{$D$};
   \fill ($(A)+(3.75,2)$) coordinate (E) circle(1.5pt) node[above right]{$E$};
   
   % Điểm tầng 3
   \fill ($(D)+(1.25,2)$) circle(1.5pt) node[above]{$F$};

  \end{tikzpicture}"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        return f"Câu {idx}: {question}\n\n{solution}"

# ==================== MAIN ====================

def main():
    question_types = [MaiVomAreaQuestion]
    
    num_questions = 1
    
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            print("Tham số 1 phải là số nguyên (số lượng câu hỏi)")
            return
    
    questions = []
    for i in range(num_questions):
        q = MaiVomAreaQuestion()
        questions.append(q.generate_question(i+1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "tinh_dien_tich_mai_vom.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong tinh_dien_tich_mai_vom.tex")

if __name__ == "__main__":
    main()
