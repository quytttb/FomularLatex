import logging
import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple

# ==================== CONFIGURATION & HELPERS ====================

SIDE_CHOICES = list(range(20, 100))

def format_vn_number(value, precision=2):
    s = f"{value:.{precision}f}"
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def format_money(value: int) -> str:
    return "{:,}".format(int(value)).replace(",", ".")

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

# ==================== EXAMPLE 1 (QuestionType1 from nhom1.py) ====================

TEMPLATE_QUESTION_1 = Template(
    r"""
Hình vẽ dưới đây cho biết một miền \(D\) (được tô đậm) nằm trong hình vuông cạnh bằng ${side}.
Miền \(D\) này gồm những điểm có khoảng cách tới tâm hình vuông nhỏ hơn hoặc bằng khoảng cách tới cạnh gần nhất của hình vuông.
Tính diện tích miền \(D\) (kết quả làm tròn đến hàng phần chục).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION_1 = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) với gốc \(O\) là tâm hình vuông. Các cạnh của hình vuông nằm trên các đường thẳng \(x = \pm ${half_side}\) và \(y = \pm ${half_side}\).

Xét trong góc phần tư bên phải (miền \(x > |y|\)), cạnh gần nhất là \(x = ${half_side}\).

Điểm \(M(x;y)\) thuộc biên của miền \(D\) thỏa mãn: \(OM = d(M, \text{cạnh})\).

\(\sqrt{x^2 + y^2} = ${half_side} - x \Rightarrow x^2 + y^2 = (${half_side} - x)^2\)

\(\Rightarrow x^2 + y^2 = ${half_side_sq} - ${side}x + x^2 \Rightarrow y^2 = ${half_side_sq} - ${side}x\)

\(\Rightarrow x = \frac{${half_side_sq}}{${side}} - \frac{y^2}{${side}} = ${quarter_side} - \frac{y^2}{${side}}\)

Đây là một cung Parabol.

Giao điểm của cung Parabol này với đường phân giác \(y=x\) (hoặc \(y=-x\)) có hoành độ và tung độ thỏa mãn:

\(x^2 = ${half_side_sq} - ${side}x \Rightarrow x^2 + ${side}x - ${half_side_sq} = 0\)

Giải phương trình ta được nghiệm dương:

\(x_0 = y_0 = \frac{-${side} + \sqrt{${side}^2 + 4 \cdot ${half_side_sq}}}{2} = \frac{-${side} + \sqrt{2${side}^2}}{2} = \frac{${side}(\sqrt{2}-1)}{2} \approx ${intersect_val}\)

Do tính đối xứng, diện tích miền \(D\) bằng 4 lần diện tích phần nằm trong miền \(x > |y|\).

Diện tích phần này được giới hạn bởi Parabol \(x = ${quarter_side} - \frac{y^2}{${side}}\) và hai đường thẳng \(y = -y_0, y = y_0\).

\( S_1 = \int_{-y_0}^{y_0} \left( ${quarter_side} - \frac{y^2}{${side}} \right) \text{d}y = \left[ ${quarter_side}y - \frac{y^3}{3 \cdot ${side}} \right]_{-y_0}^{y_0} \)

\( S_1 = 2 \left( ${quarter_side}y_0 - \frac{y_0^3}{${three_side}} \right) \)

Thay số \(y_0 \approx ${intersect_val}\):

\( S_1 \approx 2 \left( ${quarter_side} \cdot ${intersect_val} - \frac{${intersect_val}^3}{${three_side}} \right) \approx ${s1_val} \)

Diện tích toàn bộ miền \(D\) là:

\(S = 4 \times S_1 \approx ${total_area}\)
"""
)

class QuestionType1:
    def __init__(self):
        self.side = 0

    def generate_parameters(self):
        self.side = random.choice(SIDE_CHOICES)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        half_a = a / 2
        quarter_a = a / 4
        
        # Intersection y0 = a(sqrt(2)-1)/2
        y0 = (a * (math.sqrt(2) - 1)) / 2
        
        # Integral calculation
        # Term 1: a/4 * y0
        term1 = quarter_a * y0
        # Term 2: y0^3 / (3a)
        term2 = (y0 ** 3) / (3 * a)
        
        s1 = 2 * (term1 - term2)
        total_area = 4 * s1
        
        ans_comma = format_vn_number(total_area, 1)
        ans_dot = ans_comma.replace(',', '.')
        ans_str = f"{ans_dot} | {ans_comma}" if ',' in ans_comma else ans_comma
        
        return ans_str, {
            "side": a,
            "half_side": format_vn_number(half_a, 2),
            "half_side_sq": format_vn_number(half_a**2, 2),
            "quarter_side": format_vn_number(quarter_a, 2),
            "three_side": 3 * a,
            "intersect_val": format_vn_number(y0, 4),
            "s1_val": format_vn_number(s1, 4),
            "total_area": format_vn_number(total_area, 1)
        }

    def generate_tikz(self) -> str:
        a = self.side
        fixed_half = 4.0
        fixed_radius = fixed_half * (math.sqrt(2) - 1)
        
        tikz_template = r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.6]
   \draw[blue,line width=1pt] (-HALF,-HALF) rectangle (HALF,HALF) ;
   \draw[fill=orange!20,draw=red,line width=1pt] 
   (45:RADIUS) ..controls +(160:1) and +(20:1) ..  (135:RADIUS) 
   ..controls +(-110:1) and +(110:1) ..  (-135:RADIUS) 
   ..controls +(-20:1) and +(-160:1) ..(-45:RADIUS) 
   ..controls +(70:1) and +(-70:1) ..  cycle
   ;
   \fill 
   (0,0) circle(2pt)
   (45:RADIUS)circle(2pt)
   (135:RADIUS)circle(2pt)
   (-135:RADIUS)circle(2pt)
   (-45:RADIUS)circle(2pt)
   (-45:0.8) node[]{$D$}
   ;
   \draw 
   (-HALF,-HALF)--(HALF,-HALF)node[below,pos=0.5]{$SIDE_LABEL$}
   (-HALF,-HALF)--(-HALF,HALF)node[left,pos=0.5]{$SIDE_LABEL$}
   (-HALF,HALF)--(HALF,HALF)node[above,pos=0.5]{$SIDE_LABEL$}
   (HALF,HALF)--(HALF,-HALF)node[right,pos=0.5]{$SIDE_LABEL$}
   ;
 \end{tikzpicture}
"""
        return tikz_template.replace("HALF", f"{fixed_half}") \
                            .replace("RADIUS", f"{fixed_radius:.4f}") \
                            .replace("SIDE_LABEL", f"{a}")

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        
        tikz = self.generate_tikz()
        
        question = TEMPLATE_QUESTION_1.substitute(
            side=params["side"],
            diagram=tikz
        )
        
        solution = TEMPLATE_SOLUTION_1.substitute(params)
        
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== EXAMPLE 2 (QuestionType2 from nhom1.py) ====================

TEMPLATE_QUESTION_2 = Template(
    r"""
Bác An có một mảnh đất hình vuông \(ABCD\) cạnh ${side} m. Mảnh đất của bác rất phù hợp để trồng hoa màu vì bên trong có một ao nước tự nhiên được giới hạn bởi các đường cong \((L_1)\), \((L_2)\) và ba cạnh của hình vuông (xem hình vẽ).
Biết rằng đường cong \((L_1)\) là một nhánh của parabol nhận điểm \(E\) (trung điểm \(AB\)) làm đỉnh và đi qua điểm \(F\) với \(F \in AD\) và \(${k}AF = ${h}AD\).
Đường cong \((L_2)\) là tập hợp tất cả điểm \(M\) sao cho khoảng cách từ \(M\) đến tâm \(I\) bằng với khoảng cách từ \(M\) đến cạnh \(AB\).
Tính diện tích còn lại của mảnh đất mà bác An có thể trồng hoa màu (làm tròn đến hàng đơn vị).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION_2 = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) sao cho \(A(0;0)\), \(B(0;${side})\), \(D(${side};0)\). Khi đó \(C(${side};${side})\).

Cạnh hình vuông là \(a = ${side}\).

Tâm \(I\) có tọa độ \((\frac{a}{2}; \frac{a}{2})\). Điểm \(E(0; \frac{a}{2})\).

Từ điều kiện \(${k}AF = ${h}AD\) suy ra \(AF = \frac{${h}}{${k}}AD = \frac{${h}a}{${k}}\). Điểm \(F(\frac{${h}a}{${k}}; 0)\).

1. Xét đường cong \((L_1)\):

Đây là nhánh parabol đỉnh \(E(0; \frac{a}{2})\), trục đối xứng song song với \(Oy\) (do tiếp tuyến tại đỉnh nằm ngang).

Phương trình có dạng: \(y = px^2 + \frac{a}{2}\).

Đi qua \(F(\frac{${h}a}{${k}}; 0)\):
\[0 = p\left(\frac{${h}a}{${k}}\right)^2 + \frac{a}{2} \Rightarrow p \cdot \frac{${h_sq}a^2}{${k_sq}} = -\frac{a}{2} \Rightarrow p = -\frac{${k_sq}}{2${h_sq}a}\]

Vậy \((L_1): y = -\frac{${k_sq}}{2${h_sq}a}x^2 + \frac{a}{2}\).

Diện tích phần tô đậm góc \(A\) (giới hạn bởi \((L_1)\), \(Ox\), \(Oy\)):
\[ S_1 = \int_{0}^{\frac{${h}a}{${k}}} \left( -\frac{${k_sq}}{2${h_sq}a}x^2 + \frac{a}{2} \right) \text{d}x = \left[ -\frac{${k_sq}}{6${h_sq}a}x^3 + \frac{a}{2}x \right]_0^{\frac{${h}a}{${k}}} \]

\[ S_1 = -\frac{${k_sq}}{6${h_sq}a} \cdot \frac{${h_cube}a^3}{${k_cube}} + \frac{a}{2} \cdot \frac{${h}a}{${k}} = -\frac{${h}a^2}{6${k}} + \frac{${h}a^2}{2${k}} = \frac{${h}a^2}{${three_h}} \]

Thay số: \(S_1 = \frac{${k} \times ${side}^2}{${three_h}} \approx ${s1_val}\).


2. Xét đường cong \((L_2)\):

Tập hợp điểm \(M(x;y)\) cách đều \(I(\frac{a}{2}; \frac{a}{2})\) và đường thẳng \(AB\) (\(x=0\)).

\[\sqrt{(x - \frac{a}{2})^2 + (y - \frac{a}{2})^2} = x \Rightarrow (x - \frac{a}{2})^2 + (y - \frac{a}{2})^2 = x^2\]

\[\Rightarrow x^2 - ax + \frac{a^2}{4} + (y - \frac{a}{2})^2 = x^2 \Rightarrow ax = (y - \frac{a}{2})^2 + \frac{a^2}{4}\]

\[\Rightarrow x = \frac{1}{a}(y - \frac{a}{2})^2 + \frac{a}{4}\]

Diện tích phần giới hạn bởi \((L_2)\) và cạnh \(AB\) (phần trắng bên trái \((L_2)\)):

\[ S_{\text{trắng}} = \int_{0}^{a} x \text{d}y = \int_{0}^{a} \left[ \frac{1}{a}(y - \frac{a}{2})^2 + \frac{a}{4} \right] \text{d}y \]

Đặt \(u = y - \frac{a}{2} \Rightarrow \text{d}u = \text{d}y\). Cận: \(-\frac{a}{2} \to \frac{a}{2}\).

\[ S_{\text{trắng}} = \int_{-a/2}^{a/2} \left( \frac{1}{a}u^2 + \frac{a}{4} \right) \text{d}u = 2 \int_{0}^{a/2} \left( \frac{1}{a}u^2 + \frac{a}{4} \right) \text{d}u \]

\[ = 2 \left[ \frac{u^3}{3a} + \frac{au}{4} \right]_0^{a/2} = 2 \left( \frac{a^3/8}{3a} + \frac{a^2/2}{4} \right) = 2 \left( \frac{a^2}{24} + \frac{a^2}{8} \right) = 2 \cdot \frac{4a^2}{24} = \frac{a^2}{3} \]

Diện tích phần tô đậm bên phải (giới hạn bởi \((L_2)\) và các cạnh \(BC, CD, DA\)):

\[ S_2 = S_{ABCD} - S_{\text{trắng}} = a^2 - \frac{a^2}{3} = \frac{2a^2}{3} \]

3. Tổng diện tích trồng hoa màu:

\[ S = S_1 + S_2 = \frac{${k}a^2}{${three_h}} + \frac{2a^2}{3} = a^2 \left( \frac{${k}}{${three_h}} + \frac{2}{3} \right) \]

Thay số \(a = ${side}\):

\[ S \approx ${total_area} \, (\text{m}^2) \]
"""
)

class QuestionType2:
    def __init__(self):
        self.side = 0
        self.ratio_k = 1
        self.ratio_h = 4

    def generate_parameters(self):
        self.side = random.choice(SIDE_CHOICES)
        self.ratio_k = random.choice([1, 2, 3])
        self.ratio_h = random.choice([3, 4, 5, 6, 7, 8])
        while self.ratio_k >= self.ratio_h:
            self.ratio_h = random.choice([3, 4, 5, 6, 7, 8])

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        k = self.ratio_k
        h = self.ratio_h
        
        s1 = (k * (a ** 2)) / (3 * h)
        s2 = (2 * (a ** 2)) / 3
        total_area = s1 + s2
        
        return f"{format_vn_number(total_area, 0)}", {
            "side": a,
            "k": k,
            "h": h,
            "h_sq": h**2,
            "k_sq": k**2,
            "h_cube": h**3,
            "k_cube": k**3,
            "three_h": 3*h,
            "s1_val": format_vn_number(s1, 2),
            "total_area": format_vn_number(total_area, 0)
        }

    def generate_tikz(self) -> str:
        tikz = r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.6]
  
  \draw (0,0)coordinate (A) -- (8,0) coordinate (D)--(8,8) coordinate (C)--(0,8) coordinate (B)--cycle
  (0,4) coordinate (E)
  (2,0) coordinate (F)
  (4,4) coordinate (I)
  ;
  
  \draw[fill=violet!40] (0,4) ..controls +(0:1) and +(100:1) .. (2,0)--(0,0)--cycle;
  \draw[fill=violet!40] (4,8)..controls +(-130:4) and +(130:4) .. (4,0)--(8,0)--(8,8)--cycle;
  \draw 
  (0.5,5) node[]{SIDE m}
  (3.5,7.5) node[]{SIDE m}
  (8.5,4) node[]{SIDE m}
  ;
  
  \foreach \p/\r in {A/45,B/-45,C/-135,D/135,E/40,F/45,I/0}
  \fill (\p) circle (1.2pt) node[scale=1.25,shift={(\r:3mm)}]{$\boldsymbol\p$};
\end{tikzpicture}
"""
        return tikz.replace("SIDE", str(self.side))

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        
        tikz = self.generate_tikz()
        
        question = TEMPLATE_QUESTION_2.substitute(
            side=params["side"],
            k=params["k"],
            h=params["h"],
            diagram=tikz
        )
        
        solution = TEMPLATE_SOLUTION_2.substitute(params)
        
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== EXAMPLE 4 (QuestionType4 from nhom3.py) ====================

class QuestionType4:
    def __init__(self):
        self.side = 0
        self.ratio_num = 1
        self.ratio_den = 2

    def generate_parameters(self):
        self.side = random.randint(40, 100)
        ratio = random.choice([(1,2), (1,3), (2,3), (1,4), (3,4)])
        self.ratio_num = ratio[0]
        self.ratio_den = ratio[1]

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.side
        num = self.ratio_num
        den = self.ratio_den
        
        x_a = (a / 2) * (num / den)
        
        val = 1 - math.log(2)
        area = 4 * (x_a**2) * val
        
        return f"{round(area)}", {
            "side": a,
            "num": num,
            "den": den,
            "x_a": format_vn_number(x_a, 2),
            "half_x_a": format_vn_number(x_a/2, 2),
            "total_area": format_vn_number(area, 2)
        }

    def generate_tikz(self) -> str:
        return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.55]
    \draw[fill=pink!40] 
    (3.5,0) node[scale=2]{$S_1$}
    (0,0)--(4,4)--(4,-4)--cycle
    (2,0) ..controls +(60:1) and +(200:0.7).. (4,2)--(4,-2) ..controls +(160:1) and +(-60:0.7).. cycle;
    \draw[fill=orange!30,rotate=90]
    (3.5,0) node[scale=2]{$S_2$} 
    (0,0)--(4,4)--(4,-4)--cycle
    (2,0) ..controls +(60:1) and +(200:0.7).. (4,2)--(4,-2) ..controls +(160:1) and +(-60:0.7).. cycle;
    \draw[fill=pink!40,rotate=180] 
    (3.5,0) node[scale=2]{$S_3$}
    (0,0)--(4,4)--(4,-4)--cycle
    (2,0) ..controls +(60:1) and +(200:0.7).. (4,2)--(4,-2) ..controls +(160:1) and +(-60:0.7).. cycle;
    \draw[fill=orange!40,rotate=-90] 
    (3.5,0) node[scale=2]{$S_4$}
    (0,0)--(4,4)--(4,-4)--cycle
    (2,0) ..controls +(60:1) and +(200:0.7).. (4,2)--(4,-2) ..controls +(160:1) and +(-60:0.7).. cycle;
    \draw (-4,-4) rectangle (4,4);
    \draw (-4,-4) -- (4,4);
    \draw[rotate=90] (-4,-4) -- (4,4);
    \draw[->] (-4,0)--(5,0) node[above]{$x$};
    \draw[->] (0,-4)--(0,5) node[right]{$y$};
    \fill(0,0) circle(1.5pt) node[left]{$O$};
    \draw[opacity=0.2,dashed] (-2,-3) grid (3,2);
    \draw [dashed] 
    (3.45,1.65)--(4,0)
    (3.45,1.65)--(2.5,2.5)
    ;
    \fill 
    (1.2,1.7) node[above]{$\Delta$}
    (1.7,0.5) node[above]{$(L_1)$}
    (3.45,1.65) circle(3pt) node[above]{$M$}
    (4,0) circle(3pt) node[below right]{$A$}
    (2.5,2.5) circle(3pt) 
    ;
   \end{tikzpicture}
"""

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        
        question_template = Template(
            r"""
Một viên gạch lát nền nhà có dạng hình vuông với hoa văn được thiết kế bởi một học sinh lớp 12.
Xét hình phẳng có diện tích \(S_1\) được tạo thành bởi các đường cong \((L_1), (L_2)\) và một cạnh viên gạch.
Trong đó đường cong \((L_1)\) là tập hợp các điểm \(M\) thỏa mãn \(MA = \sqrt{2} d(M, \Delta)\) (\(A\) là điểm nằm trên đoạn thẳng nối tâm viên gạch với trung điểm một cạnh sao cho khoảng cách từ \(A\) đến tâm viên gạch bằng \(\frac{${num}}{${den}}\) độ dài nửa cạnh viên gạch; \(\Delta\) là đường phân giác góc phần tư thứ nhất theo hình vẽ).
\((L_2)\) đối xứng với \((L_1)\) qua trục \(Ox\).
Biết viên gạch này có kích thước cạnh bằng ${side} cm.
Tính tổng diện tích \(S_1 + S_2 + S_3 + S_4\) và làm tròn đến hàng đơn vị của \(cm^2\).

\begin{center}
${diagram}
\end{center}
"""
        )
        
        solution_template = Template(
            r"""
Chọn hệ trục tọa độ \(Oxy\) với gốc \(O\) là tâm viên gạch.\\
Cạnh viên gạch có phương trình \(x = \frac{a}{2}\).\\
Điểm \(A\) nằm trên trục hoành, có tọa độ \(A(x_A; 0)\) với \(x_A = \frac{${num}}{${den}} \cdot \frac{a}{2}\).\\
Vậy \(A(${x_a}; 0)\).

Đường thẳng \(\Delta\) là phân giác góc phần tư thứ nhất: \(y=x\).

Điểm \(M(x;y)\) thuộc \((L_1)\) thỏa mãn \(MA = \sqrt{2} d(M, \Delta)\):\\
\((x - x_A)^2 + y^2 = 2 \left( \frac{|x-y|}{\sqrt{2}} \right)^2 = (x-y)^2\)\\
\(x^2 - 2x x_A + x_A^2 + y^2 = x^2 - 2xy + y^2\)\\
\(-2x x_A + x_A^2 = -2xy \Rightarrow y = \frac{2x x_A - x_A^2}{2x} = x_A - \frac{x_A^2}{2x}\).

Đường cong \((L_2)\) đối xứng với \((L_1)\) qua \(Ox\) nên có phương trình \(y = -(x_A - \frac{x_A^2}{2x}) = \frac{x_A^2}{2x} - x_A\).\\
Giao điểm của \((L_1)\) và \((L_2)\) nằm trên \(Ox\) (\(y=0\)):\\
\(x_A - \frac{x_A^2}{2x} = 0 \Rightarrow 2x = x_A \Rightarrow x = \frac{x_A}{2} = ${half_x_a}\).

Diện tích \(S_1\) giới hạn bởi \((L_1), (L_2)\) và đường thẳng \(x=x_A\) (đi qua A vuông góc Ox):\\
\(S_1 = \int_{x_A/2}^{x_A} \left( (L_1) - (L_2) \right) \text{d}x = 2 \int_{x_A/2}^{x_A} \left( x_A - \frac{x_A^2}{2x} \right) \text{d}x\)\\
\(S_1 = 2 \left[ x_A x - \frac{x_A^2}{2} \ln|x| \right]_{x_A/2}^{x_A} = 2 \left( (x_A^2 - \frac{x_A^2}{2} \ln x_A) - (\frac{x_A^2}{2} - \frac{x_A^2}{2} \ln \frac{x_A}{2}) \right)\)\\
\(S_1 = 2 \left( \frac{x_A^2}{2} - \frac{x_A^2}{2} \ln 2 \right) = x_A^2 (1 - \ln 2)\).

Tổng diện tích 4 hình cánh hoa:\\
\(S = 4 S_1 = 4 x_A^2 (1 - \ln 2) \approx ${total_area} \, (cm^2)\).
"""
        )
        
        question = question_template.substitute(side=params["side"], num=params["num"], den=params["den"], diagram=self.generate_tikz())
        solution = solution_template.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== EXAMPLE 7 (Question1 from nhom5.py) ====================

TEMPLATE_Q7 = Template(
    r"""
Một hộ gia đình thiết kế một khu vui chơi lớn cho gia đình có dạng hình chữ nhật với chiều rộng và chiều dài lần lượt là \(AD = ${width}\) m và \(AB = ${length}\) m. Trong đó, phần được tô màu đậm làm nơi trồng hoa, phần còn lại để làm sân chơi. Mỗi phần trồng hoa có đường biên cong là đường cong \((C)\) và các cạnh của hình chữ nhật. Biết mỗi điểm \(M\) trên đường cong \((C)\) luôn có tích khoảng cách đến các cạnh \(AB\), \(AD\) bằng ${k_value} m. Số tiền chi phí để trồng hoa là ${price_flower} đ trên một mét vuông, số tiền làm sân chơi là ${price_playground} đ trên một mét vuông. Số tiền hộ gia đình cần dùng để làm sân chơi là bao nhiêu triệu đồng?

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOL_Q7 = Template(
    r"""
Diện tích khu đất: \(S = ${width} \times ${length} = ${area_total} \, (\text{m}^2)\).

Phương trình đường cong \((C)\): \(xy = ${k_value}\).

Diện tích phần trồng hoa:
\(S_{\text{hoa}} = \int_{${x_min}}^{${x_max}} \frac{${k_value}}{x} dx = ${k_value} \ln\left(\frac{${x_max}}{${x_min}}\right) \approx ${area_flower} \, (\text{m}^2)\).

Diện tích sân chơi: \(S_{\text{sân}} = S - S_{\text{hoa}} \approx ${area_playground} \, (\text{m}^2)\).

Tổng chi phí:
\(T = S_{\text{hoa}} \times ${raw_price_flower} + S_{\text{sân}} \times ${raw_price_playground} \approx ${total_cost} \, \text{đ} = ${total_cost_million} \, \text{triệu đồng}\).
"""
)

class Question7:
    def __init__(self):
        self.width = 0
        self.length = 0
        self.ratio_k = 0.5
        self.price_flower = 0
        self.price_playground = 0

    def generate_parameters(self):
        self.width = random.randint(30, 100)
        self.length = random.randint(self.width + 20, 200)
        self.ratio_k = random.randint(30, 100) / 100.0
        self.price_flower = random.randint(200, 500) * 1000
        self.price_playground = random.randint(300, 600) * 1000

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        w = self.width
        l = self.length
        ratio = self.ratio_k
        
        x_m = ratio * l
        y_m = w
        
        k_value = x_m * y_m
        
        x_min = k_value / w
        x_max = l
        
        area_integral = k_value * (math.log(x_max) - math.log(x_min)) if x_min > 0 else k_value * math.log(x_max)
        s_flower = area_integral
        
        s_total = w * l
        s_playground = s_total - s_flower
        
        cost_flower = s_flower * self.price_flower
        cost_playground = s_playground * self.price_playground
        cost = cost_flower + cost_playground
        cost_million = cost / 1_000_000
        
        return f"{format_vn_number(cost_million, 2)}", {
            "width": w, "length": l, "ratio_k": ratio,
            "k_value": format_vn_number(k_value, 2),
            "x_min": format_vn_number(x_min, 2),
            "x_max": format_vn_number(x_max, 2),
            "area_total": int(s_total),
            "area_playground": format_vn_number(s_playground, 2),
            "area_flower": format_vn_number(s_flower, 2),
            "raw_price_flower": self.price_flower,
            "raw_price_playground": self.price_playground,
            "price_flower": format_money(self.price_flower),
            "price_playground": format_money(self.price_playground),
            "cost_flower": format_money(round(cost_flower)),
            "cost_playground": format_money(round(cost_playground)),
            "total_cost": format_money(round(cost)),
            "total_cost_million": format_vn_number(cost_million, 2)
        }

    def generate_tikz(self) -> str:
                return r"""\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.7]
     \pgfmathsetmacro{\a}{(0.5)^2.5}
     \pgfmathsetmacro{\b}{(0.5)^4.5}
     \clip (-2,-1) rectangle (5,5);
     \draw[fill=orange!3,line width=2pt] (-2,-1) rectangle (5,5);
     \draw[fill=red,opacity=0.3] plot[domain=-2:5] (\x, {(0.5)^(\x-1)})--(5,\b)--(5,-1)--(-2,-1)--(-2,5)--cycle;
     \draw[green!50!black,line width=2pt] plot[domain=-2:5] (\x, {(0.5)^(\x-1)});
    \draw (0.2,3) node[]{\((c)\)};
     \draw[dashed] (-2,\a)--(3.5,\a)--(3.5,-1);
    \fill (3.5,\a) circle(2pt) node[above right]{\(M\)};
 \end{tikzpicture}"""

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_Q7.substitute(params, diagram=tikz)
        solution = TEMPLATE_SOL_Q7.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ==================== MAIN ====================

def main():
    # Danh sách các loại câu hỏi khả dụng
    question_types = [QuestionType1, QuestionType2, QuestionType4, Question7]
    
    num_questions = 4
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
            # If random, pick one from the list. 
            # But user wants specific examples in specific files.
            # The user said "nhóm lại các ví dụ".
            # So this file should probably generate all of them or allow selecting.
            # Let's just pick random for now or cycle through them.
            q_class = question_types[i % len(question_types)]
        else:
            q_class = question_types[question_type_idx - 1]
        q = q_class()
        questions.append(q.generate_question(i + 1))
    
    content = "\n\n".join(questions)
    latex = create_latex_document(content)
    
    import os
    output_path = os.path.join(os.path.dirname(__file__), "khoang_cach_diem_den_duong_thang.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong khoang_cach_diem_den_duong_thang.tex")


if __name__ == "__main__":
    main()
