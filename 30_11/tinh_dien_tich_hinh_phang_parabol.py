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
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
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
\usetikzlibrary{patterns, calc, intersections}
\begin{document}
""" + content + r"\end{document}"

# ==================== QUESTION: CROSSED PARABOLAS AREA ====================

TEMPLATE_Q = Template(
    r"""
Câu ${idx}. Cho hai đường parabol như hình vẽ bên dưới. Hãy tính diện tích phần hình phẳng gạch chéo?
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

Gọi \(x = AB\), \(y = BC\). Ta có: \(x + y = AC = ${AC}\)

\(\dfrac{BC}{DC} = \left(\dfrac{EF}{${H}}\right)^2 \Leftrightarrow \dfrac{y}{${DC}} = \dfrac{EF^2}{${H_sq}}\) \hfill (1)

\(\dfrac{AB}{AG} = \left(\dfrac{EF}{${H}}\right)^2 \Leftrightarrow \dfrac{x}{${AG}} = \dfrac{EF^2}{${H_sq}}\) \hfill (2)

Lấy (2) : (1): \(\dfrac{x}{${AG}} : \dfrac{y}{${DC}} = 1\)

\(\Leftrightarrow \dfrac{x}{${AG}} = \dfrac{y}{${DC}} = \dfrac{x + y}{${AG} + ${DC}} = \dfrac{${AC}}{${sum_AG_DC}}\)

Từ đó: \(\begin{cases} x = \dfrac{${AG} \cdot ${AC}}{${sum_AG_DC}} = ${x_val} \\ y = \dfrac{${DC} \cdot ${AC}}{${sum_AG_DC}} = ${y_val} \end{cases}\)

\(\dfrac{S_{ECF}}{S_{MCG}} = \left(\dfrac{BC}{DC}\right)^{3/2} = \left(\dfrac{${y_val}}{${DC}}\right)^{3/2}\)

\(S_{MCG} = \dfrac{2}{3} \cdot ${H} \cdot ${DC} = ${S_MCG}\)

\(\Rightarrow S_{ECF} = \left(\dfrac{${y_val}}{${DC}}\right)^{3/2} \cdot ${S_MCG} = ${S_ECF}\)

\(\dfrac{S_{EAF}}{S_{NAG}} = \left(\dfrac{AB}{AG}\right)^{3/2} = \left(\dfrac{${x_val}}{${AG}}\right)^{3/2}\)

\(S_{NAG} = \dfrac{2}{3} \cdot ${H} \cdot ${AG} = ${S_NAG}\)

\(\Rightarrow S_{EAF} = \left(\dfrac{${x_val}}{${AG}}\right)^{3/2} \cdot ${S_NAG} = ${S_EAF}\)

Diện tích phần gạch chéo:

\(S = S_{ECF} + S_{EAF} = ${S_ECF} + ${S_EAF} = ${ans}\,(\text{m}^2)\)

Đáp án: \(${ans_dot}\) | \(${ans}\)
"""
)

class ParabolCrossAreaQuestion:
    def __init__(self):
        self.W = 24
        self.H = 12
        self.dist_left = 9
        self.dist_right = 6

    def generate_parameters(self):
        self.H = random.choice([10, 12, 14])
        ratio = random.choice([1.5, 2.0, 2.5])
        self.W = int(self.H * ratio)
        if self.W % 2 != 0: self.W += 1 
        
        self.dist_left = random.randint(int(self.W * 0.2), int(self.W * 0.45))
        self.dist_right = random.randint(int(self.W * 0.2), int(self.W * 0.45))

    def to_fraction_str(self, num, den):
        if den == 0:
            return "0"
        common = math.gcd(int(abs(num)), int(abs(den)))
        n = int(num/common)
        d = int(den/common)
        if d == 1: return str(n)
        if d == -1: return str(-n)
        if d < 0:
            n = -n
            d = -d
        return f"\\dfrac{{{n}}}{{{d}}}"

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        W, H = self.W, self.H
        d_L, d_R = self.dist_left, self.dist_right
        half_W = W / 2
        half_H = H / 2
        half_H_sq = half_H ** 2

        # Tọa độ các điểm trên trục ngang
        # A = (-half_W, 0), G = (half_W, 0)
        # B = (-half_W + d_L, 0), D = (half_W - d_R, 0)
        x_B = -half_W + d_L
        x_D = half_W - d_R

        # Các khoảng cách
        AD = x_D - (-half_W)  # = x_D + half_W
        GB = half_W - x_B      # = half_W + half_W - d_L = W - d_L
        BD = x_D - x_B         # = x + y

        # MQ = NP = H (chiều cao hình chữ nhật)
        MQ = H
        NP = H
        MQ_sq = MQ ** 2
        NP_sq = NP ** 2

        # Tỉ lệ x/y = AD/GB (vì MQ = NP)
        xy_ratio = AD / GB

        # Giải hệ: x + y = BD, x/y = xy_ratio
        y_val = BD / (xy_ratio + 1)
        x_val = xy_ratio * y_val

        # Tính EF từ (1): x/AD = EF^2/MQ^2
        EF_sq = x_val * MQ_sq / AD
        EF_val = math.sqrt(EF_sq)

        # Tính y_int (tọa độ y của giao điểm E, F)
        # Từ phương trình parabol
        a1_num = -half_W - x_D
        a2_num = half_W - x_B
        a1 = a1_num / half_H_sq
        a2 = a2_num / half_H_sq
        
        diff_a = (a1_num - a2_num) / half_H_sq
        y_sq = (x_B - x_D) / diff_a if diff_a != 0 else 0
        y_sq = max(y_sq, 0)
        y_int = math.sqrt(y_sq)
        
        # Tọa độ x của C
        x_C = a1 * y_int**2 + x_D

        # Diện tích các vùng
        S_MDQ = (2/3) * MQ * AD
        S_NBP = (2/3) * NP * GB
        S_EDF = (2/3) * EF_val * x_val
        S_EBF = (2/3) * EF_val * y_val

        # Tổng diện tích phần gạch chéo
        area = S_EDF + S_EBF

        diagram_q = self.generate_tikz_question(y_int, x_C)
        diagram_sol = self.generate_tikz_solution(y_int, x_C)

        ans_comma = format_vn_number(area, 2)
        ans_dot = ans_comma.replace(',', '.')

        # Mapping variables to template names to match solution logic
        # Logic in template: x=AB, y=BC => x+y=AC. 
        # Mapping from code vars to template vars:
        # Code: x_val, y_val correspond to segments BD split at C.
        # The template uses A, B, C, D, E, F, G, M, N different from code var names?
        # Let's stick to the template's variable names in the dict.
        # Template: AC = x+y. Code: BD = x+y. => AC (template) = BD (code).
        # Template: BC/DC = ... => y/DC. Code: y_val corresponds to part near D (right side?).
        # Let's check geometry:
        # Code: x_val = xy_ratio * y_val. xy_ratio = AD/GB.
        # If x/y = AD/GB, then x corresponds to AD side (left), y to GB side (right).
        # Template: x/AG = y/DC (wait, template says x/AG = y/DC = 1 ? No)
        # Template: x/AG : y/DC = 1 => x/AG = y/DC.
        # So x corresponds to AG (left?), y to DC (right?).
        
        # Let's just pass the values calculated which are correct numerically.
        # Code: AD (left base), GB (right base). 
        # Template uses "AG" and "DC".
        # Let's map: Code AD -> Template AG. Code GB -> Template DC.
        # Code BD -> Template AC.

        return ans_comma, {
            "idx": 1, 
            "W": W, "H": H, 
            "dist_left": d_L, "dist_right": d_R,
            "AG": format_vn_number(AD),
            "DC": format_vn_number(GB),
            "AC": format_vn_number(BD), # Total distance between vertices
            "H_sq": format_vn_number(MQ_sq),
            "sum_AG_DC": format_vn_number(AD + GB),
            "x_val": format_vn_number(x_val, 3),
            "y_val": format_vn_number(y_val, 3),
            "EF_val": format_vn_number(EF_val, 3),
            "S_MCG": format_vn_number(S_NBP), # Right parabola area
            "S_NAG": format_vn_number(S_MDQ), # Left parabola area
            "S_ECF": format_vn_number(S_EBF, 3),
            "S_EAF": format_vn_number(S_EDF, 3),
            "ans": ans_comma,
            "ans_dot": ans_dot,
            "diagram_q": diagram_q,
            "diagram_sol": diagram_sol
        }

    def generate_tikz_question(self, y_int_val: float, x_C: float = 0) -> str:
        scale_x = 10 / self.W
        scale_y = 6 / self.H
        scale = min(scale_x, scale_y) * 0.8
        
        W, H = self.W, self.H
        d_L, d_R = self.dist_left, self.dist_right
        hw, hh = W/2, H/2
        
        x_B = -hw + d_L
        x_D = hw - d_R
        
        a1 = (-hw - x_D) / (hh ** 2)
        a2 = (hw - x_B) / (hh ** 2)
        
        return f"""
\\begin{{tikzpicture}}[scale={scale}, >=stealth, font=\\footnotesize]
    % Define points
    \\coordinate (M) at ({-hw},{hh});
    \\coordinate (N) at ({hw},{hh});
    \\coordinate (P) at ({hw},{-hh});
    \\coordinate (Q) at ({-hw},{-hh});
    \\coordinate (A) at ({-hw}, 0);
    \\coordinate (G) at ({hw}, 0);
    \\coordinate (B) at ({x_B}, 0);
    \\coordinate (D) at ({x_D}, 0);
    
    % Draw Rectangle
    \\draw[thick] (M) -- (N) -- (P) -- (Q) -- cycle;
    
    % Dimensions
    \\draw[<->] ($(M)+(0, 0.5)$) -- node[fill=white] {{{W}}} ($(N)+(0, 0.5)$);
    \\draw[<->] ($(M)+(-0.5, 0)$) -- node[fill=white, rotate=90] {{{H}}} ($(Q)+(-0.5, 0)$);
    
    % Axis
    \\draw[dashed, gray] ({-hw}, 0) -- ({hw}, 0);
    \\draw[dashed, gray] (0, {-hh}) -- (0, {hh});
    
    \\begin{{scope}}
        \\clip (M) rectangle (P);
        
        % Parabolas
        \\draw[thick, red]  plot[domain={-hh}:{hh}, samples=160] ({{ {a1:.6f}*\\x*\\x + {x_D:.6f} }}, \\x);
        \\draw[thick, blue] plot[domain={-hh}:{hh}, samples=160] ({{ {a2:.6f}*\\x*\\x + {x_B:.6f} }}, \\x);
        
        % Shaded intersection
        \\fill[pattern=north east lines, pattern color=purple]
            plot[domain={-y_int_val}:{y_int_val}, samples=120] ({{ {a1:.6f}*\\x*\\x + {x_D:.6f} }}, \\x) --
            plot[domain={y_int_val}:{-y_int_val}, samples=120] ({{ {a2:.6f}*\\x*\\x + {x_B:.6f} }}, \\x) -- cycle;
    \\end{{scope}}
    
    % Distances
    \\draw[<->] (A) -- node[above, fill=white] {{{d_L}}} (B);
    \\draw[<->] (G) -- node[above, fill=white] {{{d_R}}} (D);
\\end{{tikzpicture}}
"""

    def generate_tikz_solution(self, y_int_val: float, x_C: float = 0) -> str:
        scale_x = 10 / self.W
        scale_y = 6 / self.H
        scale = min(scale_x, scale_y) * 0.8
        
        W, H = self.W, self.H
        d_L, d_R = self.dist_left, self.dist_right
        hw, hh = W/2, H/2
        
        x_B = -hw + d_L
        x_D = hw - d_R
        
        a1 = (-hw - x_D) / (hh ** 2)
        a2 = (hw - x_B) / (hh ** 2)
        
        # Calculate intersection points E (top) and F (bottom)
        x_E = a1 * y_int_val**2 + x_D
        x_F = a1 * (-y_int_val)**2 + x_D
        
        return f"""
\\begin{{tikzpicture}}[scale={scale}, >=stealth]
    % Define points
    \\coordinate (M) at ({-hw},{hh});
    \\coordinate (N) at ({hw},{hh});
    \\coordinate (P) at ({hw},{-hh});
    \\coordinate (Q) at ({-hw},{-hh});
    \\coordinate (A) at ({-hw}, 0);
    \\coordinate (G) at ({hw}, 0);
    \\coordinate (B) at ({x_B}, 0);
    \\coordinate (D) at ({x_D}, 0);
    \\coordinate (C) at ({x_C:.6f}, 0);
    \\coordinate (E) at ({x_E:.6f}, {y_int_val:.6f});
    \\coordinate (F) at ({x_F:.6f}, {-y_int_val:.6f});
    
    % Draw Rectangle
    \\draw[thick] (M) -- (N) -- (P) -- (Q) -- cycle;
    \\node[above left] at (M) {{M}};
    \\node[above right] at (N) {{N}};
    \\node[below right] at (P) {{P}};
    \\node[below left] at (Q) {{Q}};
    
    % Dimensions
    \\draw[<->] ($(M)+(0, 0.5)$) -- node[fill=white] {{{W}}} ($(N)+(0, 0.5)$);
    \\draw[<->] ($(M)+(-0.5, 0)$) -- node[fill=white, rotate=90] {{{H}}} ($(Q)+(-0.5, 0)$);
    
    % Axis
    \\draw[dashed, gray] ({-hw}, 0) -- ({hw}, 0);
    \\draw[dashed, gray] (0, {-hh}) -- (0, {hh});
    
    \\begin{{scope}}
        \\clip (M) rectangle (P);
        
        % Parabolas
        \\draw[thick, red]  plot[domain={-hh}:{hh}, samples=160] ({{ {a1:.6f}*\\x*\\x + {x_D:.6f} }}, \\x);
        \\draw[thick, blue] plot[domain={-hh}:{hh}, samples=160] ({{ {a2:.6f}*\\x*\\x + {x_B:.6f} }}, \\x);
        
        % Shaded intersection
        \\fill[pattern=north east lines, pattern color=purple]
            plot[domain={-y_int_val}:{y_int_val}, samples=120] ({{ {a1:.6f}*\\x*\\x + {x_D:.6f} }}, \\x) --
            plot[domain={y_int_val}:{-y_int_val}, samples=120] ({{ {a2:.6f}*\\x*\\x + {x_B:.6f} }}, \\x) -- cycle;
    \\end{{scope}}
    
    % Mark points
    \\fill (A) circle (2pt) node[left=3mm] {{A}};
    \\fill (G) circle (2pt) node[right=3mm] {{G}};
    \\fill (B) circle (2pt) node[below left] {{B}};
    \\fill (C) circle (2pt) node[below] {{C}};
    \\fill (D) circle (2pt) node[below right] {{D}};
    \\fill (E) circle (2pt) node[above right] {{E}};
    \\fill (F) circle (2pt) node[below right] {{F}};
    
    % Distances
    \\draw[<->] (A) -- node[above] {{{d_L}}} (B);
    \\draw[<->] (G) -- node[above] {{{d_R}}} (D);
\\end{{tikzpicture}}
"""

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        ans, params = self.calculate_answer()
        params['idx'] = idx
        question = TEMPLATE_Q.substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        return f"{question}\n\n{solution}"

# ==================== MAIN ====================

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        try:
            num_questions = int(sys.argv[1])
        except ValueError:
            pass
    
    questions = []
    for i in range(num_questions):
        q = ParabolCrossAreaQuestion()
        questions.append(q.generate_question(i+1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "tinh_dien_tich_hinh_phang_parabol.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong tinh_dien_tich_hinh_phang_parabol.tex")

if __name__ == "__main__":
    main()
