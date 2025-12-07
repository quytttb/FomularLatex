import logging
import random
import math
import sys
from string import Template
from typing import Any, Dict, Tuple

# Cấu hình
SIDE_VALUES = [round(x * 0.1, 1) for x in range(20, 120)] # 2.0 to 11.9
RADIUS_VALUES = [round(x * 0.1, 1) for x in range(5, 50)] # 0.5 to 4.9
UNIT_CHOICES = ["dm", "cm", "m"]

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
\usetikzlibrary{patterns, calc, intersections}
\begin{document}
""" + content + r"\end{document}"

# ------------------------------------------------------------------------------
# DẠNG 1: CÂU 3 (Đồng hồ - Hình vuông & Đường tròn)
# ------------------------------------------------------------------------------

TEMPLATE_QUESTION_3 = Template(
    r"""
Em học sinh đến từ TED đã thiết kế bề mặt của một chiếc đồng hồ treo tường.
Phần trong của mặt đồng hồ là hình vuông có cạnh bằng ${two_a} ${unit}.
Phần ngoài của mặt đồng hồ là đường tròn có bán kính bằng ${two_a} ${unit} (tâm trùng với tâm hình vuông).
Đường cong trung gian có tên \((L)\) là tập hợp tất cả điểm \(P\) sao cho nếu kẻ tia \(Ot\) bất kỳ cắt hình vuông và đường tròn lần lượt tại \(M, N\) thì \(P\) là trung điểm \(MN\) (\(O\) là tâm đường tròn).
Tìm diện tích hình phẳng giới hạn bởi đường cong \((L)\) theo đơn vị ${unit}\(^2\) và làm tròn đến hàng phần trăm.

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION_3 = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) với gốc \(O\) là tâm hình vuông.

Xét trong góc phần tư thứ nhất, tia \(Ot\) tạo với \(Ox\) góc \(\alpha \in [0; \frac{\pi}{4}]\).

Phương trình cạnh hình vuông là \(x = a = ${a}\). Điểm \(M(a; a\tan\alpha)\).

Phương trình đường tròn là \(x^2+y^2=4a^2\). Điểm \(N(2a\cos\alpha; 2a\sin\alpha)\).

Tọa độ điểm \(P\) là trung điểm \(MN\):
\[\begin{cases} x = \frac{a + 2a\cos\alpha}{2} = a(\frac{1}{2} + \cos\alpha) \\\\ y = \frac{a\tan\alpha + 2a\sin\alpha}{2} = a(\frac{1}{2}\tan\alpha + \sin\alpha) \end{cases}\]

Diện tích hình phẳng cần tìm là \(S = 8 \times S_{1/8}\), trong đó \(S_{1/8}\) là diện tích phần hình phẳng nằm trong góc phần tư thứ nhất.

Ta có: \(S_{1/8} = S_{\Delta} + \int_{x(\pi/4)}^{x(0)} y \text{d}x\).

Tại \(\alpha = \frac{\pi}{4}\): \(x_1 = y_1 = a(\frac{1}{2} + \frac{\sqrt{2}}{2})\).

\[S_{\Delta} = \frac{1}{2} x_1 y_1 = \frac{a^2}{8}(3+2\sqrt{2})\]

Tính tích phân \(I = \int_{x(\pi/4)}^{x(0)} y \text{d}x\). Đặt \(x = a(\frac{1}{2} + \cos\alpha) \Rightarrow \text{d}x = -a\sin\alpha \text{d}\alpha\).

Đổi cận: \(x(\pi/4) \to \alpha=\frac{\pi}{4}\); \(x(0) \to \alpha=0\).

\[I = \int_{\frac{\pi}{4}}^{0} a(\frac{1}{2}\tan\alpha + \sin\alpha)(-a\sin\alpha) \text{d}\alpha = a^2 \int_{0}^{\frac{\pi}{4}} (\frac{1}{2}\frac{\sin^2\alpha}{\cos\alpha} + \sin^2\alpha) \text{d}\alpha\]

\[I = a^2 \left[ \frac{1}{2}(\ln|\sec\alpha+\tan\alpha| - \sin\alpha) + (\frac{\alpha}{2} - \frac{\sin2\alpha}{4}) \right]_{0}^{\frac{\pi}{4}}\]

\[I = a^2 \left( \frac{1}{2}\ln(\sqrt{2}+1) - \frac{\sqrt{2}}{4} + \frac{\pi}{8} - \frac{1}{4} \right)\]

Tổng diện tích:

\[S = 8(S_{\Delta} + I) = a^2 (\pi + 4\ln(\sqrt{2} + 1) + 1)\]

Thay số \(a = ${a}\):

\[S \approx ${area_val} \, (${unit}^2)\]
"""
)

class SquareCircleLocusQuestion:
    def __init__(self):
        self.two_a = 0
        self.unit = ""

    def generate_parameters(self):
        self.two_a = random.choice(SIDE_VALUES)
        self.unit = random.choice(UNIT_CHOICES)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        two_a = self.two_a
        a = two_a / 2
        
        val = math.pi + 4 * math.log(math.sqrt(2) + 1) + 1
        area = (a**2) * val
        
        ans_comma = format_vn_number(area, 2)
        ans_dot = ans_comma.replace(',', '.')
        ans_str = f"{ans_dot} | {ans_comma}" if ',' in ans_comma else ans_comma
        
        return ans_str, {
            "two_a": format_vn_number(two_a),
            "a": format_vn_number(a),
            "unit": self.unit,
            "area_val": format_vn_number(area, 2)
        }

    def generate_tikz(self) -> str:
        return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.7]
   \draw[fill=red!30] (0,0) circle(3.2cm);
   \draw[line width=2pt,green!50!black] 
   (90:3.2)--(90:3) node[shift=(-90:10pt)]{$$12$$}
   (60:3.2)--(60:3) node[shift=(-90-30:10pt)]{$$1$$}
   (30:3.2)--(30:3) node[shift=(-90-60:10pt)]{$$2$$}
   (0:3.2)--(0:3) node[shift=(-90-90:10pt)]{$$3$$}
   (-30:3.2)--(-30:3) node[shift=(-180-30:10pt)]{$$4$$}
   (-60:3.2)--(-60:3) node[shift=(-180-60:10pt)]{$$5$$}
   (-90:3.2)--(-90:3) node[shift=(-180-90:10pt)]{$$6$$}
   (-120:3.2)--(-120:3) node[shift=(-180-90:10pt)]{$$7$$}
   (-150:3.2)--(-150:3) node[shift=(-180-120:10pt)]{$$8$$}
   (-180:3.2)--(-180:3) node[shift=(-180-150:10pt)]{$$9$$}
   (-210:3.2)--(-210:3) node[shift=(-360:10pt)]{$$10$$}
   (-240:3.2)--(-240:3) node[shift=(-360-30:10pt)]{$$11$$}
   ;
   \draw[fill=black!50!orange] (45:2.5)..controls +(140:1) and +(40:1).. (135:2.5)..controls +(-130:1) and +(130:1).. (-135:2.5)..controls +(-40:1) and +(-140:1).. (-45:2.5)..controls +(50:1) and +(-50:1).. cycle;
   \definecolor{xanhdatroi}{RGB}{30,144,255}
   \fill[inner color=xanhdatroi, outer color=xanhdatroi!50] (45:2)--(135:2)--(-135:2)--(-45:2)--cycle;
   
   \draw[->,line width=4pt] (0,0)--(-90:2);
   \draw[->,line width=4pt] (0,0)--(110:1);
   \fill[red] (0,0) circle(3.5pt);
  \end{tikzpicture}
"""

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_QUESTION_3.substitute(
            two_a=params["two_a"],
            unit=params["unit"],
            diagram=tikz
        )
        solution = TEMPLATE_SOLUTION_3.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"


# ------------------------------------------------------------------------------
# DẠNG 2: CÂU 12 (Tam giác đều & Đường tròn)
# ------------------------------------------------------------------------------

TEMPLATE_QUESTION_12 = Template(
    r"""
Cho tam giác đều \(ABC\) có cạnh bằng ${a} ${unit}, trọng tâm \(O\) và một hình tròn tâm \(O\) bán kính bằng ${r} ${unit}.
Kẻ tia \(Ot\) bất kỳ cắt đường tròn tại \(M\), cắt một cạnh tam giác tại \(N\) (\(OM, ON\) cùng hướng).
Gọi \(P\) là trung điểm của \(MN\). Khi tia \(Ot\) quay quanh gốc \(O\) thì tập hợp các điểm \(P\) tạo thành hình \((H)\).
Tính diện tích hình \((H)\) theo đơn vị ${unit}\(^2\) và làm tròn đến hàng phần trăm.

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION_12 = Template(
    r"""
Chọn hệ trục tọa độ \(Oxy\) gốc \(O\).

Bán kính đường tròn nội tiếp tam giác đều cạnh \(a\) là \(r_{in} = \frac{a\sqrt{3}}{6}\).

Với \(a = ${a}\), ta có \(r_{in} = \frac{${a}\sqrt{3}}{6} \approx ${r_in_val}\).

Bán kính đường tròn đã cho là \(r_c = ${r}\).

Xét một phần đối xứng trong góc \(\alpha \in [0; \frac{\pi}{3}]\).

Điểm \(M\) trên đường tròn: \(M(r_c\cos\alpha; r_c\sin\alpha)\).

Điểm \(N\) trên cạnh tam giác (\(x=r_{in}\)): \(N(r_{in}; r_{in}\tan\alpha)\).

Điểm \(P\) là trung điểm \(MN\):
\[\begin{cases} x = \frac{1}{2}(r_c\cos\alpha + r_{in}) \\\\ y = \frac{1}{2}(r_c\sin\alpha + r_{in}\tan\alpha) \end{cases}\]

Diện tích hình \((H)\) là \(S = 6(S_{\Delta} + I)\).

Tại \(\alpha = \frac{\pi}{3}\): \(x_1 = \frac{1}{2}(\frac{r_c}{2} + r_{in})\), \(y_1 = \sqrt{3}x_1\).

\[S_{\Delta} = \frac{1}{2} x_1 y_1 = \frac{\sqrt{3}}{2} x_1^2 = \frac{\sqrt{3}}{8}(\frac{r_c}{2} + r_{in})^2\]

Tính \(I = \int_{x(\pi/3)}^{x(0)} y \text{d}x\). Đặt \(x\) theo \(\alpha\), \(\text{d}x = -\frac{1}{2}r_c\sin\alpha \text{d}\alpha\).

\[I = \int_{\frac{\pi}{3}}^{0} \frac{1}{2}(r_c\sin\alpha + r_{in}\tan\alpha)(-\frac{1}{2}r_c\sin\alpha) \text{d}\alpha\]

\[I = \frac{r_c}{4} \int_{0}^{\frac{\pi}{3}} (r_c\sin^2\alpha + r_{in}\frac{\sin^2\alpha}{\cos\alpha}) \text{d}\alpha\]

\[I = \frac{r_c}{4} \left[ r_c(\frac{\pi}{6} - \frac{\sqrt{3}}{8}) + r_{in}(\ln(2+\sqrt{3}) - \frac{\sqrt{3}}{2}) \right]\]

Tổng diện tích:

\[S = \frac{\pi}{4} r_c^2 + \frac{3}{2} r_c r_{in} \ln(2+\sqrt{3}) + \frac{3\sqrt{3}}{4} r_{in}^2\]

Thay số \(r_c = ${r}, r_{in} = \frac{${a}\sqrt{3}}{6}\):

\[S \approx ${area_val} \, (${unit}^2)\]
"""
)

class TriangleLocusQuestion:
    def __init__(self):
        self.a = 0
        self.r = 0
        self.unit = ""

    def generate_parameters(self):
        self.a = random.choice(SIDE_VALUES)
        r_in = self.a * math.sqrt(3) / 6
        possible_r = [x for x in RADIUS_VALUES if x < r_in * 0.9]
        if not possible_r:
            self.r = round(r_in * 0.5, 1)
        else:
            self.r = random.choice(possible_r)
        self.unit = random.choice(UNIT_CHOICES)

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.a
        r_c = self.r
        r_in = a * math.sqrt(3) / 6
        
        term1 = (math.pi / 4) * (r_c**2)
        term2 = 1.5 * r_c * r_in * math.log(2 + math.sqrt(3))
        term3 = (3 * math.sqrt(3) / 4) * (r_in**2)
        
        area = term1 + term2 + term3
        
        ans_comma = format_vn_number(area, 2)
        ans_dot = ans_comma.replace(',', '.')
        ans_str = f"{ans_dot} | {ans_comma}" if ',' in ans_comma else ans_comma
        
        return ans_str, {
            "a": format_vn_number(a),
            "r": format_vn_number(r_c),
            "r_in_val": format_vn_number(r_in, 3),
            "unit": self.unit,
            "area_val": format_vn_number(area, 2)
        }

    def generate_tikz(self) -> str:
        R_circum = self.a * math.sqrt(3) / 3
        k = 4.0 / R_circum
        
        r_tikz = self.r * k
        R_tikz_outer = 4.0 # Fixed
        
        curve_dist = 2.0 + r_tikz / 2.0
        
        return Template(r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.7]
   \draw[name path=duongtron] (0,0) coordinate (O) circle(${r_tikz}cm);
   \draw[name path=cong] 
   (90:${curve_dist})..controls +(-90+70:0.5) and 
   +(150-70:0.5) ..  (-30:${curve_dist})..controls +(150+70:0.5) 
   and +(30-70:0.5) .. (-150:${curve_dist})  ..controls +(30+70:0.5) 
   and +(-90-70:0.5) .. cycle; 
   \draw[fill=pink,opacity=0.5,name path=tamgiac] 
   (90:${R_outer})coordinate (A)--(-30:${R_outer})coordinate (C)--(-150:${R_outer})coordinate (B)--cycle
   ;
   \draw ($$(A)!0.5!(C)$$)coordinate (M')--(B);
   \draw[name path=duong] (O)--++(80:4)node[above right]{$$t$$};
   \path [name intersections={of=duong and duongtron, by=M}];
   \path [name intersections={of=duong and cong, by=P}];
   \path [name intersections={of=duong and tamgiac, by=N}];
   \fill
   (O) circle(1.5pt) node[below]{$$O$$}
   (B) circle(1.5pt) node[below left]{$$B$$}
   (M') circle(1.5pt) node[above right]{$$M'$$}
   (P) circle(1.5pt) node[below left]{$$P$$}
   (M) circle(1.5pt) node[above right]{$$M$$}
   (N) circle(1.5pt) node[above right]{$$N$$}
   (90:${curve_dist}) circle(1.5pt)
   (-30:${curve_dist}) circle(1.5pt)
   (-150:${curve_dist}) circle(1.5pt)
   ;
 \end{tikzpicture}
""").substitute(
            r_tikz=f"{r_tikz:.2f}",
            R_outer=f"{R_tikz_outer:.2f}",
            curve_dist=f"{curve_dist:.2f}"
        )

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_QUESTION_12.substitute(
            a=params["a"],
            r=params["r"],
            unit=params["unit"],
            diagram=tikz
        )
        solution = TEMPLATE_SOLUTION_12.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"


# ------------------------------------------------------------------------------
# DẠNG 3: CÂU 14 (Lục giác đều & Đường tròn - Chi phí)
# ------------------------------------------------------------------------------

TEMPLATE_QUESTION_14 = Template(
    r"""
Một bồn hoa được xây dựng từ một hình tròn và một hình lục giác đều cùng tâm \(O\) có bán kính và cạnh lần lượt là ${r} ${unit} và ${a} ${unit}.
Người ta xây dựng đường cong \((L)\) chính là tập hợp tất cả điểm \(P\) sao cho khi kẻ tia \(Ot\) bất kỳ cắt đường tròn, lục giác lần lượt tại \(M, N\) thì điểm \(P\) đối xứng với \(M\) qua \(N\).
Phần bên trong đường tròn người ta trồng hoa với chi phí ${c1} nghìn đồng/${unit}\(^2\).
Phần ngoài đường tròn và bên trong lục giác người ta trồng cỏ với chi phí ${c2} nghìn đồng/${unit}\(^2\).
Phần bên ngoài lục giác và bên trong đường \((L)\) thì người ta lát gạch để tạo lối đi với chi phí ${c3} nghìn đồng/${unit}\(^2\).
Hãy tính tổng số tiền người ta phải bỏ ra để làm bồn hoa như trên theo đơn vị triệu đồng (làm tròn đến hàng phần chục).

\begin{center}
${diagram}
\end{center}
"""
)

TEMPLATE_SOLUTION_14 = Template(
    r"""
Diện tích hình tròn bán kính \(r = ${r}\) là \(S_1 = \pi r^2 \approx ${s1_val}\).

Diện tích lục giác đều cạnh \(a = ${a}\) là \(S_{hex} = \frac{3\sqrt{3}}{2} a^2 \approx ${shex_val}\).

Diện tích phần trồng cỏ (trong lục giác, ngoài tròn): \(S_2 = S_{hex} - S_1 \approx ${s2_val}\).

Xét đường cong \((L)\). Chọn hệ trục \(Oxy\).

Bán kính nội tiếp lục giác \(r_{in} = \frac{a\sqrt{3}}{2}\).

Xét trong góc \(\alpha \in [0; \frac{\pi}{6}]\).

Điểm \(M\) trên đường tròn: \(M(r\cos\alpha; r\sin\alpha)\).

Điểm \(N\) trên cạnh lục giác (\(x=r_{in}\)): \(N(r_{in}; r_{in}\tan\alpha)\).

Điểm \(P\) đối xứng với \(M\) qua \(N\) (\(N\) là trung điểm \(MP\)):
\[\begin{cases} x_P = 2x_N - x_M = 2r_{in} - r\cos\alpha \\\\ y_P = 2y_N - y_M = 2r_{in}\tan\alpha - r\sin\alpha \end{cases}\]

Diện tích hình phẳng giới hạn bởi \((L)\) là \(S_L = 12(S_{\Delta} + I)\).

Tại \(\alpha = \frac{\pi}{6}\): \(x_1 = 2r_{in} - \frac{\sqrt{3}}{2}r\), \(y_1 = \frac{1}{\sqrt{3}}x_1\).

\[S_{\Delta} = \frac{1}{2} x_1 y_1 = \frac{1}{2\sqrt{3}} x_1^2\]

Tính \(I = \int_{x(\pi/6)}^{x(0)} y \text{d}x\). \(\text{d}x = r\sin\alpha \text{d}\alpha\).

\[I = \int_{\frac{\pi}{6}}^{0} (2r_{in}\tan\alpha - r\sin\alpha)(r\sin\alpha) \text{d}\alpha = -r \int_{0}^{\frac{\pi}{6}} (2r_{in}\frac{\sin^2\alpha}{\cos\alpha} - r\sin^2\alpha) \text{d}\alpha\]

\[I = -r \left[ 2r_{in}(\frac{1}{2}\ln 3 - 0.5) - r(\frac{\pi}{12} - \frac{\sqrt{3}}{8}) \right]\]

Tổng diện tích \(S_L = 6\sqrt{3} a^2 - 6\sqrt{3} a r \ln 3 + \pi r^2 \approx ${sl_val}\).

Diện tích phần lát gạch (trong L, ngoài lục giác): \(S_3 = S_L - S_{hex} \approx ${s3_val}\).

Tổng chi phí:

\[T = S_1 \times ${c1} + S_2 \times ${c2} + S_3 \times ${c3}\] (nghìn đồng).

\[T \approx ${total_cost_k}\] nghìn đồng \(= ${total_cost_m}\) triệu đồng.
"""
)

class HexagonLocusQuestion:
    def __init__(self):
        self.a = 0
        self.r = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.unit = "m"

    def generate_parameters(self):
        self.a = random.choice(SIDE_VALUES)
        r_in = self.a * math.sqrt(3) / 2
        possible_r = [x for x in RADIUS_VALUES if x < r_in * 0.8 and x > 1.0]
        if not possible_r:
            self.r = round(r_in * 0.6, 1)
        else:
            self.r = random.choice(possible_r)
            
        self.c1 = random.choice([100, 150, 200, 250, 300])
        self.c2 = random.choice([50, 80, 100, 120])
        self.c3 = random.choice([200, 300, 400, 500])

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        a = self.a
        r = self.r
        
        s1 = math.pi * r**2
        s_hex = (3 * math.sqrt(3) / 2) * a**2
        s2 = s_hex - s1
        
        s_l = 6 * math.sqrt(3) * a**2 - 6 * math.sqrt(3) * a * r * math.log(3) + math.pi * r**2
        s3 = s_l - s_hex
        
        total_cost_k = s1 * self.c1 + s2 * self.c2 + s3 * self.c3
        total_cost_m = total_cost_k / 1000.0
        
        return f"{format_vn_number(total_cost_m, 1)}", {
            "a": format_vn_number(a),
            "r": format_vn_number(r),
            "unit": self.unit,
            "c1": self.c1,
            "c2": self.c2,
            "c3": self.c3,
            "s1_val": format_vn_number(s1, 2),
            "shex_val": format_vn_number(s_hex, 2),
            "s2_val": format_vn_number(s2, 2),
            "sl_val": format_vn_number(s_l, 2),
            "s3_val": format_vn_number(s3, 2),
            "total_cost_k": format_vn_number(total_cost_k, 0),
            "total_cost_m": format_vn_number(total_cost_m, 1)
        }

    def generate_tikz(self) -> str:
        k = 3.0 / self.a
        r_tikz = self.r * k
        
        curve_dist = 6.0 - r_tikz
        
        return Template(r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=.8]
   \draw (0:${curve_dist}) ..controls +(180-30:1) and +(-120+30:1)..  (60:${curve_dist})
   ..controls +(-120-30:1) and +(-60+30:1).. (120:${curve_dist})
   ..controls +(-60-30:1) and +(0+30:1).. (180:${curve_dist})
   ..controls +(0-30:1) and +(60+30:1)..(240:${curve_dist})
   ..controls +(60-30:1) and +(120+30:1)..  (300:${curve_dist})
   ..controls +(120-30:1) and +(180+30:1)..  cycle;
   \shade[shading=radial, inner color=white, outer color=violet!40!white, line width=1pt] (0:3)--(60:3)--(120:3)--(180:3)--(240:3)--(300:3)--cycle; 
   \shade[shading=radial, inner color=white, outer color=pink!60!white, line width=1pt] (0,0) circle(${r_tikz}cm); 
   \draw (0:3)--(60:3)--(120:3)--(180:3)--(240:3)--(300:3)--cycle;
   \draw (0,0)--(0:3) (0,0)--(60:3) (0,0)--(120:3) (0,0)--(180:3) (0,0)--(240:3) (0,0)--(300:3);
 \end{tikzpicture}
""").substitute(
            r_tikz=f"{r_tikz:.2f}",
            curve_dist=f"{curve_dist:.2f}"
        )

    def generate_question(self, idx: int = 1) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        tikz = self.generate_tikz()
        question = TEMPLATE_QUESTION_14.substitute(
            a=params["a"],
            r=params["r"],
            unit=params["unit"],
            c1=params["c1"],
            c2=params["c2"],
            c3=params["c3"],
            diagram=tikz
        )
        solution = TEMPLATE_SOLUTION_14.substitute(params)
        return f"Câu {idx}: {question}\n\nLời giải:\n{solution}\n\nĐáp án: {ans}"

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    question_types = [SquareCircleLocusQuestion, TriangleLocusQuestion, HexagonLocusQuestion]
    
    num_questions = 3
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
        questions.append(q.generate_question(i + 1))
        
    content = "\n\n".join(questions)
    latex = create_latex_document(content)
    
    import os
    output_path = os.path.join(os.path.dirname(__file__), "cac_bai_toan_ve_trung_diem.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong cac_bai_toan_ve_trung_diem.tex")

if __name__ == "__main__":
    main()
