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

# ==================== QUESTION: VERTICAL PARABOLA SHADED OUTSIDE ====================

TEMPLATE_Q = Template(
    r"""
\noindent Câu ${idx}. Tính diện tích của phần được tô đậm:

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

Ta có: \(x + y = IM = ${IM}\)

\(\dfrac{KM}{HM} = \left(\dfrac{EF}{AB}\right)^2 \Leftrightarrow \dfrac{y}{${HM}} = \dfrac{EF^2}{${AB_sq}}\) \hfill (1)

\(\dfrac{IK}{IN} = \left(\dfrac{EF}{PQ}\right)^2 \Leftrightarrow \dfrac{x}{${IN}} = \dfrac{EF^2}{${PQ_sq}}\) \hfill (2)

Lấy (2) : (1): \(\dfrac{x}{${IN}} : \dfrac{y}{${HM}} = \dfrac{EF^2}{${PQ_sq}} : \dfrac{EF^2}{${AB_sq}}\)

\(\Leftrightarrow \dfrac{x}{${IN}} : \dfrac{y}{${HM}} = \dfrac{${AB_sq}}{${PQ_sq}} = ${ratio_sq}\)

\(\Leftrightarrow \dfrac{x}{y} = \dfrac{${IN}}{${HM}} \cdot ${ratio_sq} = ${xy_ratio}\)

Từ \(\begin{cases} x + y = ${IM} \\ \dfrac{x}{y} = ${xy_ratio} \end{cases}\) ta được: \(\begin{cases} x = ${x_val} \\ y = ${y_val} \end{cases}\)

\(S_{ANB} = \dfrac{2}{3} \cdot HM \cdot AB = \dfrac{2}{3} \cdot ${HM} \cdot ${W} = ${S_ANB}\)

\(S_{IPQ} = \dfrac{2}{3} \cdot IN \cdot PQ = \dfrac{2}{3} \cdot ${IN} \cdot ${w_bot} = ${S_IPQ}\)

Từ (1): \(\dfrac{y}{${HM}} = \dfrac{EF^2}{${AB_sq}} \Rightarrow EF = \sqrt{\dfrac{y \cdot ${AB_sq}}{${HM}}} = ${EF_val}\)

\(S_{IEF} = \dfrac{2}{3} \cdot IK \cdot EF = \dfrac{2}{3} \cdot ${x_val} \cdot ${EF_val} = ${S_IEF}\)

\(S_{EMF} = \dfrac{2}{3} \cdot MK \cdot EF = \dfrac{2}{3} \cdot ${y_val} \cdot ${EF_val} = ${S_EMF}\)

\(S_{\text{trắng}} = S_{ANB} + S_{IPQ} - (S_{IEF} + S_{EMF}) = ${S_ANB} + ${S_IPQ} - (${S_IEF} + ${S_EMF}) = ${S_white}\)

\(S_{\text{cần tìm}} = S_{HCN} - S_{\text{trắng}} = ${S_rect} - ${S_white} = ${ans}\,(\text{m}^2)\)

Đáp án: \(${ans_dot}\) | \(${ans}\)
"""
)

class VerticalParabolShadowQuestion:
    def __init__(self):
        # Default parameters matching the image (12x16, d_top=4, d_bot=6, w_bot=8)
        self.W = 12
        self.H = 16
        self.d_top = 4
        self.d_bot = 6
        self.w_bot = 8

    def generate_parameters(self):
        # Randomize dimensions
        self.H = random.randrange(12, 21, 2) # Even numbers from 12 to 20
        self.W = random.randrange(10, 17, 2)  # Even numbers from 10 to 16
        
        # d_top: khoảng cách từ mép trên xuống đỉnh P1
        self.d_top = random.randint(int(self.H * 0.15), int(self.H * 0.3))
        
        # d_bot: khoảng cách từ mép dưới lên đỉnh P2
        self.d_bot = random.randint(int(self.H * 0.25), int(self.H * 0.4))
        
        # w_bot: khoảng cách giữa 2 chân của P1 trên mép dưới
        min_w_bot = int(self.W * 0.5)
        max_w_bot = int(self.W * 0.8)
        self.w_bot = random.randint(min_w_bot, max_w_bot)
        if self.w_bot % 2 != 0: self.w_bot += 1
        
        # Đảm bảo đỉnh P1 cao hơn đỉnh P2 để có giao điểm
        # y_v1 = H - d_top, y_v2 = d_bot
        # Cần y_v1 > y_v2 + 2
        while self.H - self.d_top <= self.d_bot + 2:
            if self.d_bot > 2:
                self.d_bot -= 1
            elif self.d_top > 2:
                self.d_top -= 1
            else:
                self.H += 2
                break

    def to_fraction_str(self, num, den):
        """Convert to simplified fraction string"""
        if den == 0:
            return "0"
        common = math.gcd(int(abs(num)), int(abs(den)))
        n = int(num / common)
        d = int(den / common)
        if d == 1:
            return str(n)
        if d == -1:
            return str(-n)
        if d < 0:
            n = -n
            d = -d
        return f"\\dfrac{{{n}}}{{{d}}}"

    def calculate_answer(self) -> Tuple[str, Dict[str, Any]]:
        W, H = self.W, self.H
        d_top, d_bot, w_bot = self.d_top, self.d_bot, self.w_bot
        
        # Các điểm trên trục đối xứng
        # N = (0, 0), H = (0, H)
        # I = đỉnh P1 = (0, y_v1), M = đỉnh P2 = (0, y_v2)
        y_v1 = H - d_top  # = IN (khoảng cách từ I đến N)
        y_v2 = d_bot       # = MN (khoảng cách từ M đến N)
        
        # Các khoảng cách
        IN = y_v1           # Từ I đến N
        HM = H - y_v2       # Từ H đến M
        IM = y_v1 - y_v2    # = x + y
        
        # Các đáy
        AB = W              # Đáy trên (dây cung P2)
        PQ = w_bot          # Đáy dưới (dây cung P1)
        
        AB_sq = AB ** 2
        PQ_sq = PQ ** 2
        
        # Tỉ lệ từ (2) : (1)
        # (x/IN) / (y/HM) = AB^2 / PQ^2
        # => x/y = (IN/HM) * (AB^2/PQ^2)
        ratio_sq = AB_sq / PQ_sq
        xy_ratio = (IN / HM) * ratio_sq
        
        # Giải hệ: x + y = IM, x/y = xy_ratio
        # x = xy_ratio * y
        # xy_ratio * y + y = IM
        # y = IM / (xy_ratio + 1)
        y_val = IM / (xy_ratio + 1)
        x_val = xy_ratio * y_val
        
        # Tính EF từ (1): y/HM = EF^2/AB^2 => EF^2 = y * AB^2 / HM
        EF_sq = y_val * AB_sq / HM
        EF_val = math.sqrt(EF_sq)
        
        # Tính các diện tích
        S_ANB = (2/3) * HM * AB      # Diện tích parabol P2 (từ M đến AB)
        S_IPQ = (2/3) * IN * PQ      # Diện tích parabol P1 (từ I đến PQ)
        S_IEF = (2/3) * x_val * EF_val  # Đoạn parabol P1 từ I đến EF
        S_EMF = (2/3) * y_val * EF_val  # Đoạn parabol P2 từ M đến EF
        
        # Diện tích trắng (bên trong cả 2 parabol)
        S_white = S_ANB + S_IPQ - (S_IEF + S_EMF)
        
        # Diện tích hình chữ nhật
        S_rect = W * H
        
        # Diện tích phần tô đậm (bên ngoài cả 2 parabol)
        S_shaded = S_rect - S_white
        
        # Tính y_int (tọa độ y của K)
        y_int = y_v2 + y_val  # K cách M một đoạn y
        x_int = EF_val / 2     # E và F đối xứng qua trục
        
        # Format fractions
        w_bot_half = w_bot / 2
        half_W = W / 2
        a1_num = int(y_v1)
        a1_den = int(w_bot_half ** 2)
        a2_num = int(H - y_v2)
        a2_den = int(half_W ** 2)
        
        # a1 và a2 cho TikZ
        a1 = y_v1 / (w_bot_half ** 2)
        a2 = (H - y_v2) / (half_W ** 2)
        
        diagram_q = self.generate_tikz_question(a1, y_v1, a2, y_v2, w_bot_half, half_W, x_int, y_int)
        diagram_sol = self.generate_tikz_solution(a1, y_v1, a2, y_v2, w_bot_half, half_W, x_int, y_int)
        
        # Format for both dot and comma versions
        ans_comma = format_vn_number(S_shaded, 2)
        ans_dot = ans_comma.replace(',', '.')
        
        return ans_comma, {
            "idx": 1,
            "W": W, "H": H,
            "d_top": d_top, "d_bot": d_bot, "w_bot": w_bot,
            "y_v1": y_v1,
            "IN": format_vn_number(IN),
            "HM": format_vn_number(HM),
            "IM": format_vn_number(IM),
            "AB_sq": format_vn_number(AB_sq),
            "PQ_sq": format_vn_number(PQ_sq),
            "ratio_sq": self.to_fraction_str(int(AB_sq), int(PQ_sq)),
            "xy_ratio": self.to_fraction_str(int(IN * AB_sq), int(HM * PQ_sq)),
            "x_val": self.to_fraction_str(int(x_val * 1000), 1000) if not (x_val * 10).is_integer() else format_vn_number(x_val, 3),
            "y_val": self.to_fraction_str(int(y_val * 1000), 1000) if not (y_val * 10).is_integer() else format_vn_number(y_val, 3),
            "EF_val": format_vn_number(EF_val, 3),
            "S_ANB": format_vn_number(S_ANB, 2),
            "S_IPQ": format_vn_number(S_IPQ, 2),
            "S_IEF": format_vn_number(S_IEF, 3),
            "S_EMF": format_vn_number(S_EMF, 3),
            "S_white": format_vn_number(S_white, 2),
            "S_rect": format_vn_number(S_rect),
            "ans": ans_comma,
            "ans_dot": ans_dot,
            "diagram_q": diagram_q,
            "diagram_sol": diagram_sol
        }

    def generate_tikz_question(self, a1, y_v1, a2, y_v2, w_bot_half, half_W, x_int, y_int) -> str:
        W, H = self.W, self.H
        scale = min(8/W, 10/H) * 0.8
        
        hw = W / 2
        
        return f"""
\\begin{{tikzpicture}}[scale={scale}, >=stealth, font=\\footnotesize]
    % Define points
    \\coordinate (A) at ({-hw},{H});
    \\coordinate (B) at ({hw},{H});
    \\coordinate (C) at ({hw},0);
    \\coordinate (D) at ({-hw},0);
    
    % Fill entire rectangle with pattern
    \\fill[purple!30] (-{hw}, 0) rectangle ({hw}, {H});
    
    % Fill inside P1 (area under P1 from P to Q) with WHITE
    \\fill[white] ({-w_bot_half}, 0) -- 
        plot[domain={-w_bot_half}:{w_bot_half}, samples=100] (\\x, {{-{a1:.6f}*\\x*\\x + {y_v1}}}) 
        -- ({w_bot_half}, 0) -- cycle;
    
    % Fill inside P2 (area above P2 from A to B) with WHITE  
    \\fill[white] (-{hw}, {H}) -- 
        plot[domain={-hw}:{hw}, samples=100] (\\x, {{{a2:.6f}*\\x*\\x + {y_v2}}}) 
        -- ({hw}, {H}) -- cycle;

    % Draw Parabolas
    \\draw[thick, red] plot[domain={-w_bot_half}:{w_bot_half}, samples=100] (\\x, {{-{a1:.6f}*\\x*\\x + {y_v1}}});
    \\draw[thick, red] plot[domain=-{hw}:{hw}, samples=100] (\\x, {{{a2:.6f}*\\x*\\x + {y_v2}}});
    
    % Rectangle outline
    \\draw[thick] (A) -- (B) -- (C) -- (D) -- cycle;
    
    % Dimensions
    \\draw[<->] ($(-{hw},{H})+(0, 0.5)$) -- node[fill=white] {{{W}}} ($({hw},{H})+(0, 0.5)$);
    \\draw[<->] ($({hw},0)+(0.5, 0)$) -- node[fill=white, rotate=90] {{{H}}} ($({hw},{H})+(0.5, 0)$);
    
    % Dimensions on axis
    % Top gap (d_top)
    \\draw[<->] (0, {H}) -- node[fill=white, inner sep=1pt] {{{self.d_top}}} (0, {y_v1});
    % Bottom gap (d_bot)
    \\draw[<->] (0, 0) -- node[fill=white, inner sep=1pt] {{{self.d_bot}}} (0, {y_v2});
    
    % Bottom width
    \\draw[<->] ({-w_bot_half}, -0.5) -- node[fill=white] {{{self.w_bot}}} ({w_bot_half}, -0.5);
    \\draw[dashed] ({-w_bot_half}, 0) -- ({-w_bot_half}, -0.5);
    \\draw[dashed] ({w_bot_half}, 0) -- ({w_bot_half}, -0.5);
    
    % Label shaded region (H2)
    \\node at ({-hw*0.75}, {H*0.4}) {{$(H_2)$}};
\\end{{tikzpicture}}
"""

    def generate_tikz_solution(self, a1, y_v1, a2, y_v2, w_bot_half, half_W, x_int, y_int) -> str:
        W, H = self.W, self.H
        scale = min(8/W, 10/H) * 0.8
        
        hw = W / 2
        
        return f"""
\\begin{{tikzpicture}}[scale={scale}, >=stealth]
    % Define points
    \\coordinate (A) at ({-hw},{H});
    \\coordinate (B) at ({hw},{H});
    \\coordinate (C) at ({hw},0);
    \\coordinate (D) at ({-hw},0);
    
    \\coordinate (P) at ({-w_bot_half}, 0);
    \\coordinate (Q) at ({w_bot_half}, 0);
    
    \\coordinate (I) at (0, {y_v1}); % Dinh P1
    \\coordinate (M) at (0, {y_v2}); % Dinh P2
    
    \\coordinate (H) at (0, {H});
    \\coordinate (N) at (0, 0);
    
    \\coordinate (K) at (0, {y_int:.6f});
    \\coordinate (E) at ({-x_int:.6f}, {y_int:.6f});
    \\coordinate (F) at ({x_int:.6f}, {y_int:.6f});
    
    % Fill entire rectangle with pattern
    \\fill[purple!30] (-{hw}, 0) rectangle ({hw}, {H});
    
    % Fill inside P1 (area under P1 from P to Q) with WHITE
    \\fill[white] ({-w_bot_half}, 0) -- 
        plot[domain={-w_bot_half}:{w_bot_half}, samples=100] (\\x, {{-{a1:.6f}*\\x*\\x + {y_v1}}}) 
        -- ({w_bot_half}, 0) -- cycle;
    
    % Fill inside P2 (area above P2 from A to B) with WHITE  
    \\fill[white] (-{hw}, {H}) -- 
        plot[domain={-hw}:{hw}, samples=100] (\\x, {{{a2:.6f}*\\x*\\x + {y_v2}}}) 
        -- ({hw}, {H}) -- cycle;

    % Draw Parabolas
    \\draw[thick, red] plot[domain={-w_bot_half}:{w_bot_half}, samples=100] (\\x, {{-{a1:.6f}*\\x*\\x + {y_v1}}});
    \\draw[thick, red] plot[domain=-{hw}:{hw}, samples=100] (\\x, {{{a2:.6f}*\\x*\\x + {y_v2}}});
    
    % Rectangle outline
    \\draw[thick] (A) -- (B) -- (C) -- (D) -- cycle;
    
    % Axis of symmetry
    \\draw[thin] (H) -- (N);
    % Line connecting intersections
    \\draw[thin] (E) -- (F);

    % Mark rectangle corners
    \\node[above left] at (A) {{A}};
    \\node[above right] at (B) {{B}};
    \\node[below right] at (C) {{C}};
    \\node[below left] at (D) {{D}};
    
    % Mark points on axis
    \\node[above, yshift=4mm] at (H) {{H}};
    \\node[below, yshift=-4mm] at (N) {{N}};
    \\fill (I) circle (1.5pt) node[above right] {{I}};
    \\fill (M) circle (1.5pt) node[below right] {{M}};
    \\node[above right] at (K) {{K}};
    
    % Mark points on bottom edge (feet of P1)
    \\node[below left] at (P) {{P}};
    \\node[below right] at (Q) {{Q}};
    
    % Mark intersection points E, F
    \\node[left] at (E) {{E}};
    \\node[right] at (F) {{F}};

    % Dimensions
    \\draw[<->] ($(-{hw},{H})+(0, 0.5)$) -- node[fill=white] {{{W}}} ($({hw},{H})+(0, 0.5)$);
    \\draw[<->] ($({hw},0)+(0.5, 0)$) -- node[fill=white, rotate=90] {{{H}}} ($({hw},{H})+(0.5, 0)$);
    
    % Dimensions on axis (4 and 6 in example)
    % Top gap (d_top)
    \\draw[<->] (0, {H}) -- node[right] {{{self.d_top}}} (0, {y_v1});
    % Bottom gap (d_bot)
    \\draw[<->] (0, 0) -- node[right] {{{self.d_bot}}} (0, {y_v2});
    
    % Bottom width
    \\draw[<->] ({-w_bot_half}, -0.5) -- node[fill=white] {{{self.w_bot}}} ({w_bot_half}, -0.5);
    \\draw[dashed] ({-w_bot_half}, 0) -- ({-w_bot_half}, -0.5);
    \\draw[dashed] ({w_bot_half}, 0) -- ({w_bot_half}, -0.5);
    
    % Label shaded region (H2)
    \\node at ({-hw*0.75}, {H*0.4}) {{$(H_2)$}};
    
    % Labels for x, y regions in the lens (optional based on image)
    \\node at ({-x_int*0.3}, {y_int + (y_v1 - y_int)*0.3}) {{x}};
    \\node at ({-x_int*0.3}, {y_int - (y_int - y_v2)*0.3}) {{y}};

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
        q = VerticalParabolShadowQuestion()
        questions.append(q.generate_question(i+1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "tinh_dien_tich_hinh_phang_parabol_dung.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong tinh_dien_tich_hinh_phang_parabol_dung.tex")

if __name__ == "__main__":
    main()
