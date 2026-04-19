"""
Hệ thống sinh đề toán về radar chỏm cầu và tên lửa trong không gian 3D
Bài toán: Tìm thời gian từ khi tên lửa bị radar phát hiện đến khi bắn trúng radar
Hệ tọa độ Oxyz
Dạng câu hỏi: Điền số (kết quả làm tròn đến hàng đơn vị)
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
from fractions import Fraction
from string import Template
from typing import Any, Dict, List, Optional, Tuple

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# CẤU HÌNH VÀ HẰNG SỐ
# ==============================================================================

@dataclass
class GeneratorConfig:
    """Cấu hình cho generator"""
    seed: Optional[int] = None


# Tọa độ điểm A (vị trí tên lửa)
A_X_VALUES: List[int] = list(range(10, 61, 5))          # 10 đến 60, bước 5
A_Y_VALUES: List[int] = list(range(-900, -399, 20))     # -900 đến -400, bước 20
A_Z_VALUES: List[int] = list(range(20, 81, 5))          # 20 đến 80, bước 5

# Bán kính đáy chỏm cầu trên mặt đất (km)
RADIUS_VALUES: List[int] = list(range(200, 601, 50))    # 200 đến 600, bước 50

# Chiều cao chỏm cầu (km)
HEIGHT_VALUES: List[int] = list(range(10, 51, 5))       # 10 đến 50, bước 5

# Vận tốc tên lửa (km/giây)
SPEED_VALUES: List[int] = list(range(3, 11))            # 3 đến 10


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def format_decimal_vn(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu phẩy (kiểu VN)"""
    formatted = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",")


def format_decimal_dot(val: float, decimals: int = 1) -> str:
    """Format số thập phân với dấu chấm"""
    return f"{val:.{decimals}f}".rstrip('0').rstrip('.')


def format_number(val: float, decimals: int = 2) -> str:
    """Format số: nếu là số nguyên thì bỏ phần thập phân"""
    if val == int(val):
        return str(int(val))
    return format_decimal_vn(val, decimals)


def format_number_dot(val: float, decimals: int = 2) -> str:
    """Format số với dấu chấm"""
    if val == int(val):
        return str(int(val))
    return format_decimal_dot(val, decimals)


def format_point_3d(name: str, x, y, z) -> str:
    """Format tọa độ điểm 3D theo kiểu Việt Nam"""
    return f"{name}({format_number(x)};{format_number(y)};{format_number(z)})"


def format_coef_t(val: float) -> str:
    """Format hệ số nhân với t trong phương trình tham số"""
    if val == int(val):
        v = int(val)
    else:
        v = val
    if v >= 0:
        return str(v)
    return str(v)


def format_fraction(val: Fraction) -> str:
    """Chuyển đổi Fraction thành phân số chính xác (dạng LaTeX)"""
    if val.denominator == 1:
        return str(val.numerator)
    
    top = val.numerator
    bot = val.denominator
    
    if top < 0:
        return rf"-\dfrac{{{abs(top)}}}{{{bot}}}"
    return rf"\dfrac{{{top}}}{{{bot}}}"


def format_fraction_inline(val: Fraction) -> str:
    """Chuyển đổi Fraction thành phân số inline dạng a/b (vd: -1/3)"""
    if val.denominator == 1:
        return str(val.numerator)
    
    return f"{val.numerator}/{val.denominator}"


def simplify_sqrt(n: int) -> Tuple[int, int]:
    """
    Rút gọn căn bậc 2 của số nguyên n.
    Trả về (ngoài_căn, trong_căn) sao cho ngoài_căn * sqrt(trong_căn) = sqrt(n).
    """
    if n == 0:
        return 0, 0
    if n < 0:
        raise ValueError("Cannot square root negative number")
        
    outside = 1
    inside = n
    d = 2
    while d * d <= inside:
        if inside % (d * d) == 0:
            outside *= d
            inside //= (d * d)
        else:
            d += 1
    return outside, inside


def format_sqrt(n_sq_numerator: int, n_sq_denominator: int = 1) -> str:
    """Chuyển đổi tử số và mẫu số của bình phương khoảng cách thành chuỗi căn thức LaTeX"""
    num_out, num_in = simplify_sqrt(abs(n_sq_numerator))
    den_out, den_in = simplify_sqrt(abs(n_sq_denominator))
    
    # Rút gọn trước
    if num_in == 0:
        if den_out == 1:
            return "0"
        return "0"
        
    def _format_part(out_val, in_val):
        if in_val == 1:
            return str(out_val)
        if out_val == 1:
            return f"\\sqrt{{{in_val}}}"
        return f"{out_val}\\sqrt{{{in_val}}}"
        
    top_str = _format_part(num_out, num_in)
    
    if n_sq_denominator == 1:
        return top_str
        
    bot_str = _format_part(den_out, den_in)
    if bot_str == "1":
        return top_str
        
    return rf"\dfrac{{{top_str}}}{{{bot_str}}}"


# ==============================================================================
# HÀM TÍNH TOÁN HÌNH HỌC 3D
# ==============================================================================

def calculate_sphere_center_a(h: int, R: int) -> Fraction:
    """
    Tính tung độ tâm mặt cầu I(0;0;a) từ chiều cao h và bán kính đáy R
    IB² = IC² => a = (h² - R²) / (2h), a < 0
    """
    return Fraction(h**2 - R**2, 2 * h)


def calculate_sphere_radius_sq(R: int, a: Fraction) -> Fraction:
    """Tính bình phương bán kính mặt cầu: r² = R² + a²"""
    return R**2 + a**2


def find_intersection_t(A: Tuple[int, int, int], h: int, R: int) -> Tuple[Fraction, Fraction]:
    """
    Tìm tham số t cho giao điểm đường thẳng OA với mặt cầu (S)
    """
    ax, ay, az = A
    A_sq = ax**2 + ay**2 + az**2

    disc_scaled = (az * (h**2 - R**2))**2 + A_sq * (2 * h * R)**2
    root = math.isqrt(disc_scaled)

    t1 = Fraction(-az * (h**2 - R**2) - root, 2 * h * A_sq)
    t2 = Fraction(-az * (h**2 - R**2) + root, 2 * h * A_sq)

    return t1, t2


def calculate_M(A: Tuple[int, int, int], t: Fraction) -> Tuple[Fraction, Fraction, Fraction]:
    """Tính tọa độ điểm M trên đường OA: M = t * (-ax, -ay, -az)"""
    ax, ay, az = A
    return (-ax * t, -ay * t, -az * t)


def calculate_MO_sq(A: Tuple[int, int, int], t: Fraction) -> Fraction:
    """Tính bình phương khoảng cách MO"""
    ax, ay, az = A
    return (ax**2 + ay**2 + az**2) * t**2


# ==============================================================================
# LATEX TEMPLATES
# ==============================================================================

def build_tikz_question(point_A_label: str) -> str:
    """Tạo TikZ cho đề bài (có nhãn HTN)"""
    return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
\draw 
(-0.85,-0.85)--++(3.5,0)coordinate (R1)
(-0.85,-0.85)--++(-3.5,0)coordinate (R1')
(0.85,0.85)--++(3.5,0)coordinate (R2)
(0.85,0.85)--++(-3.5,0)coordinate (R2')
(R1)--(R2)(R1')--(R2')
;
\begin{scope}
 \clip (R2')--(R1')--(R1);
\draw (R1') ellipse (1.5cm and 0.75cm); 
\draw ($(R1')+(0.25,0)$) node[above right,rotate=-5]{$Oxy$};
\end{scope}

\draw (-4,4)coordinate (A)(0,0)coordinate (O);

\draw[->](A)node[above]{$""" + point_A_label + r"""$}--($(A)!0.1!(O)$);
\fill(A) circle(2pt);

\draw[fill=red!50,opacity=0.8] 
(0:3) arc(0:-180:3cm and 0.85cm) --++(0,0.5) 
arc(-180:-360:3cm and 2.5cm)--cycle
; 

\draw[fill=brown,opacity=0.6] 
(0:3) arc(0:-360:3cm and 0.85cm) ;

\draw[fill=brown,opacity=0.6] 
(0:1.5) arc(0:-360:1.5cm and 0.5cm) ;

\draw[dashed] (0:3) arc(0:180:3cm and 0.85cm) ;
\draw[dashed] 
(0:1.5) arc(0:180:1.5cm and 0.5cm) 
arc(180:360:1.5cm and 0.5cm) 
;
\foreach \x/\y in {1/2,2/3,3/4,4/5,5/6,6/7,7/8,8/9}
{\draw[->,thick]($(A)!0.\x2!(O)$)--($(A)!0.\y!(O)$);}

\fill (O) circle(2.5pt);

\draw[->] (0,0)coordinate (O)--++(5,0)node[above]{$y$};
\draw[->] (0,0)coordinate (O)--++(0,4)node[above]{$z$};
\draw[->] (0,0)coordinate (O)--++(-2,-2)node[above left]{$x$};

\node at (1.5, 1.2) {HTN};

\end{tikzpicture}
"""


def build_tikz_solution(point_A_label: str, point_B_label: str, point_C_label: str) -> str:
    """Tạo TikZ cho lời giải (bỏ HTN, thêm B và C)"""
    return r"""
\begin{tikzpicture}[line join = round, line cap=round,>=stealth,font=\footnotesize,scale=1]
\draw 
(-0.85,-0.85)--++(3.5,0)coordinate (R1)
(-0.85,-0.85)--++(-3.5,0)coordinate (R1')
(0.85,0.85)--++(3.5,0)coordinate (R2)
(0.85,0.85)--++(-3.5,0)coordinate (R2')
(R1)--(R2)(R1')--(R2')
;
\begin{scope}
 \clip (R2')--(R1')--(R1);
\draw (R1') ellipse (1.5cm and 0.75cm); 
\draw ($(R1')+(0.25,0)$) node[above right,rotate=-5]{$Oxy$};
\end{scope}

\draw (-4,4)coordinate (A)(0,0)coordinate (O);

\draw[->](A)node[above]{$""" + point_A_label + r"""$}--($(A)!0.1!(O)$);
\fill(A) circle(2pt);

\draw[fill=red!50,opacity=0.8] 
(0:3) arc(0:-180:3cm and 0.85cm) --++(0,0.5) 
arc(-180:-360:3cm and 2.5cm)--cycle
; 

\draw[fill=brown,opacity=0.6] 
(0:3) arc(0:-360:3cm and 0.85cm) ;

\draw[fill=brown,opacity=0.6] 
(0:1.5) arc(0:-360:1.5cm and 0.5cm) ;

\draw[dashed] (0:3) arc(0:180:3cm and 0.85cm) ;
\draw[dashed] 
(0:1.5) arc(0:180:1.5cm and 0.5cm) 
arc(180:360:1.5cm and 0.5cm) 
;
\foreach \x/\y in {1/2,2/3,3/4,4/5,5/6,6/7,7/8,8/9}
{\draw[->,thick]($(A)!0.\x2!(O)$)--($(A)!0.\y!(O)$);}

\fill (O) circle(2.5pt);

\draw[->] (0,0)coordinate (O)--++(5,0)node[above]{$y$};
\draw[->] (0,0)coordinate (O)--++(0,4)node[above]{$z$};
\draw[->] (0,0)coordinate (O)--++(-2,-2)node[above left]{$x$};

\node[right] at (0, 4) {$""" + point_B_label + r"""$};
\node[below] at (5, 0) {$""" + point_C_label + r"""$};

\end{tikzpicture}
"""


TEMPLATE_QUESTION = Template(r"""Hình chỏm cầu có một đáy là một phần của hình cầu bị chia bởi một mặt phẳng. Một rada có thể phát hiện các mục tiêu trong khu vực của một hình chỏm cầu với chiều rộng trên mặt đất là một hình tròn với bán kính ${R} (km) và chiều cao ${h} (km). Chọn hệ trục tọa độ $$Oxyz$$ với mặt phẳng $$Oxy$$ là mặt đất (xem mặt đất là mặt phẳng), trục $$Oz$$ hướng lên cao và gốc tọa độ $$O$$ trùng với vị trí của rada (tham khảo hình vẽ bên), mỗi đơn vị trên trục là $$1$$ (km). Một tên lửa bắt đầu từ vị trí điểm ${point_A}, dự định bay thẳng với vận tốc không đổi ${v} (km)/giây hướng thẳng đến vị trí của rada. Thời gian dự kiến từ khi tên lửa bị rada phát hiện đến khi nó bắn trúng rada là bao nhiêu giây? \textit{(làm tròn đến hàng đơn vị)}

\begin{center}
${tikz_diagram}
\end{center}
""")


TEMPLATE_SOLUTION = Template(r"""
${tikz_diagram}

Giả sử trục $$Oz$$ cắt mặt cầu tại điểm $$${point_B}$$, trục $$Oy$$ cắt mặt cầu tại điểm $$${point_C}$$.

Gọi mặt cầu là $$(S)$$ và có tâm là $$I(0;0;a)$$ với $$a < 0$$.

Ta có $$IB^2 = IC^2 \Rightarrow a = ${a_val}$$. Suy ra phương trình mặt cầu $$(S)$$: $$x^2 + y^2 + \left(z + ${abs_a}\right)^2 = ${r_squared}$$.

Khi đó $$OA \cap (S)$$ thỏa mãn hệ phương trình:
\[\begin{cases} x = ${dx}t \\\\ y = ${dy}t \\\\ z = ${dz}t \\\\ x^2 + y^2 + \left(z + ${abs_a}\right)^2 = ${r_squared} \end{cases} \Leftrightarrow \begin{cases} t = ${t1_val} \\\\ t = ${t2_val} \end{cases}\]

Do $$z_M > 0$$ nên nhận $$t = ${t1_val} \Rightarrow M\!\left(${M_x};${M_y};${M_z}\right) \Rightarrow MO = ${MO_val}$$.

Thời gian dự kiến từ khi tên lửa bị rada phát hiện đến khi nó bắn trúng rada là:
\[t = \dfrac{MO}{v} = \dfrac{${MO_val}}{${v}} \approx ${time_val} \text{ (giây).}\]
""")


# ==============================================================================
# LỚP SINH ĐỀ
# ==============================================================================

class RadarMissile3DQuestion:
    """Bài toán radar chỏm cầu và tên lửa trong không gian 3D"""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên, đảm bảo constraint hợp lệ"""
        max_attempts = 10000
        for _ in range(max_attempts):
            ax = random.choice(A_X_VALUES)
            ay = random.choice(A_Y_VALUES)
            az = random.choice(A_Z_VALUES)
            R = random.choice(RADIUS_VALUES)
            h = random.choice(HEIGHT_VALUES)
            v = random.choice(SPEED_VALUES)

            # Đảm bảo h < R
            if h >= R:
                continue

            A = (ax, ay, az)
            # a = (h^2 - R^2)/(2h)
            # disc_scaled = (az*(h^2-R^2))^2 + (ax^2+ay^2+az^2)*(2hR)^2
            A_sq = ax**2 + ay**2 + az**2
            disc_scaled = (az * (h**2 - R**2))**2 + A_sq * (2 * h * R)**2
            root = math.isqrt(disc_scaled)
            
            # Kiểm tra nghiệm có "đẹp" (rational) hay không
            if root**2 != disc_scaled:
                continue

            # Kiểm tra điểm A phải nằm hoàn toàn bên ngoài radar (ngoài chỏm cầu)
            if A_sq * h - az * (h**2 - R**2) <= R**2 * h:
                continue

            a = calculate_sphere_center_a(h, R)
            t1, t2 = find_intersection_t(A, h, R)
            
            # Chọn t thích hợp (cắt vào chỏm cầu)
            valid_t = None
            if t1 < 0:
                valid_t = t1
            elif t2 > 0:
                valid_t = t2
                
            if valid_t is None:
                continue

            M = calculate_M(A, valid_t)

            # Kiểm tra z_M trong phạm vi chỏm cầu
            if M[2] <= 0 or M[2] > h:
                continue

            MO_sq = calculate_MO_sq(A, valid_t)
            time_val = math.sqrt(float(MO_sq)) / v

            # Kiểm tra thời gian hợp lý (10 đến 200 giây)
            if time_val < 10 or time_val > 200:
                continue

            r_squared = calculate_sphere_radius_sq(R, a)

            return {
                "A": A,
                "R": R,
                "h": h,
                "v": v,
                "a": a,
                "r_squared": r_squared,
            }

        raise ValueError("Không thể sinh tham số hợp lệ sau nhiều lần thử")

    def calculate_values(self) -> Dict[str, Any]:
        """Tính toán các giá trị từ tham số"""
        params = self.parameters

        A = params["A"]
        R = params["R"]
        h = params["h"]
        v = params["v"]
        a = params["a"]
        r_squared = params["r_squared"]

        # Tìm giao điểm
        t1, t2 = find_intersection_t(A, h, R)
        M = calculate_M(A, t1)
        MO_sq = calculate_MO_sq(A, t1)
        MO = math.sqrt(float(MO_sq))
        time_val = MO / v
        time_rounded = round(time_val)

        # Tính khoảng cách MO dạng exact LaTeX sqrt
        MO_latex = format_sqrt(MO_sq.numerator, MO_sq.denominator)

        # Điểm B và C trên mặt cầu
        B = (0, 0, h)
        C = (0, R, 0)

        # Hướng tham số: (-ax, -ay, -az)
        dx = -A[0]
        dy = -A[1]
        dz = -A[2]

        return {
            "B": B,
            "C": C,
            "t1": t1,
            "t2": t2,
            "M": M,
            "MO": MO,
            "MO_latex": MO_latex,
            "time_val": time_val,
            "time_rounded": time_rounded,
            "dx": dx,
            "dy": dy,
            "dz": dz,
        }

    def generate_question_text(self) -> str:
        """Tạo nội dung đề bài"""
        params = self.parameters
        A = params["A"]

        point_A_label = f"A({A[0]};{A[1]};{A[2]})"

        tikz = build_tikz_question(point_A_label)

        return TEMPLATE_QUESTION.substitute(
            R=params["R"],
            h=params["h"],
            point_A=f"A({A[0]};{A[1]};{A[2]})",
            v=params["v"],
            tikz_diagram=tikz,
        )

    def generate_solution(self) -> str:
        """Tạo lời giải chi tiết"""
        params = self.parameters
        calc = self.calculated_values

        A = params["A"]
        h = params["h"]
        R = params["R"]
        a = params["a"]
        abs_a = abs(a)
        r_squared = params["r_squared"]
        M = calc["M"]

        point_A_label = f"A({A[0]};{A[1]};{A[2]})"
        point_B_label = f"B(0;0;{h})"
        point_C_label = f"C(0;{R};0)"

        tikz = build_tikz_solution(point_A_label, point_B_label, point_C_label)

        tikz_block = f"\\begin{{center}}\n{tikz}\n\\end{{center}}"

        return TEMPLATE_SOLUTION.substitute(
            point_B=f"B(0;0;{h})",
            point_C=f"C(0;{R};0)",
            tikz_diagram=tikz_block,
            a_val=format_fraction(a),
            abs_a=format_fraction(abs_a),
            r_squared=format_fraction(r_squared),
            dx=int(calc["dx"]),
            dy=int(calc["dy"]),
            dz=int(calc["dz"]),
            t1_val=format_fraction(calc["t1"]),
            t2_val=format_fraction(calc["t2"]),
            M_x=format_fraction(M[0]),
            M_y=format_fraction(M[1]),
            M_z=format_fraction(M[2]),
            MO_val=calc["MO_latex"],
            v=params["v"],
            time_val=calc["time_rounded"],
            answer=calc["time_rounded"],
        )

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Sinh một câu hỏi hoàn chỉnh dạng Azota"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()

        question_text = self.generate_question_text().strip()
        solution = self.generate_solution().strip()
        answer = str(self.calculated_values["time_rounded"])

        question_content = (
            f"\\begin{{ex}}%C\u00e2u {question_number}\n"
            f"{question_text}\n\n"
            f"\\shortans{{{answer}}}\n"
            f"\\loigiai{{\n{solution}\n}}\n"
            f"\\end{{ex}}\n"
        )

        return question_content, answer

    @staticmethod
    def create_latex_document(
        questions_data: List[Tuple[str, str]],
        title: str = "Bài tập Radar Chỏm Cầu và Tên Lửa 3D",
    ) -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        questions_content = "\n\n".join(
            [q_content for q_content, _ in questions_data]
        )

        latex_document = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

""" + questions_content + r"""

\end{document}
"""
        return latex_document


# ==============================================================================
# HÀM MAIN
# ==============================================================================

def main():
    """
    Hàm main để chạy generator
    Usage: python radar_missile_3d_questions.py <num_questions> [seed]
    """
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

        if seed is None:
            seed = os.environ.get("OPT_SEED")
            if seed:
                seed = int(seed)

        if seed is not None:
            random.seed(seed)
            logging.info(f"Sử dụng seed: {seed}")

        logging.info(f"Đang sinh {num_questions} câu hỏi radar chỏm cầu 3D...")

        questions_data: List[Tuple[str, str]] = []

        for i in range(num_questions):
            config = GeneratorConfig(seed=seed)
            question = RadarMissile3DQuestion(config)
            question_content, answer = question.generate_question_only(i + 1)
            questions_data.append((question_content, answer))
            logging.info(f"  Câu {i + 1}: t ≈ {answer} giây")

        latex_content = RadarMissile3DQuestion.create_latex_document(
            questions_data,
            title="Bài tập Radar Chỏm Cầu và Tên Lửa 3D"
        )

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "radar_missile_3d_questions.tex")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)

        logging.info(f"Đã ghi file: {output_file}")
        print(f"\nĐã tạo {num_questions} câu hỏi và lưu vào: {output_file}")

        print("\n=== ĐÁP ÁN ===")
        for i, (_, answer) in enumerate(questions_data):
            print(f"Câu {i + 1}: t ≈ {answer} giây")

    except ValueError as e:
        print(f"Lỗi: Tham số không hợp lệ - {e}")
        print("Usage: python radar_missile_3d_questions.py <num_questions> [seed]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")
        raise


if __name__ == "__main__":
    main()
