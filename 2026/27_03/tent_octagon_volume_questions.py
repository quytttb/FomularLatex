"""
Sinh đề: thể tích lều vải (H) — chóp bát giác đều với các cạnh bên là parabol,
thiết diện vuông góc SO là bát giác đều.
"""
import math
import os
import random
import sys
from fractions import Fraction
from typing import Optional, Tuple


def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"


def octagon_area_from_circumradius(R: float) -> float:
    """Diện tích bát giác đều khi biết bán kính ngoại tiếp R (m^2)."""
    return 2.0 * math.sqrt(2.0) * R * R


def parabola_coeffs_fractions(H: int, ka: int, kb: int) -> Tuple[Fraction, Fraction, int]:
    if kb >= ka or ka <= 0 or kb <= 0:
        raise ValueError("Cần 0 < kb < ka")
    alpha = Fraction(2 * H * (2 * kb - ka), ka * kb * (kb - ka))
    beta = -Fraction(2 * H, ka) - alpha * Fraction(ka, 2)
    gamma = H
    return alpha, beta, gamma


def circumradius_x(y: float, alpha: float, beta: float, gamma: float) -> float:
    disc = beta * beta - 4.0 * alpha * (gamma - y)
    if disc < 0 and disc > -1e-12:
        disc = 0.0
    if disc < 0:
        raise ValueError("Delta âm")
    return (-beta - math.sqrt(disc)) / (2.0 * alpha)


def volume_tent(H: int, ka: int, kb: int, n: int = 400_000) -> float:
    alpha_f, beta_f, gamma = parabola_coeffs_fractions(H, ka, kb)
    alpha = float(alpha_f)
    beta = float(beta_f)
    if alpha <= 0:
        raise ValueError("alpha phải dương với bộ tham số đã chọn")

    dy = H / n
    s = 0.0
    for i in range(n + 1):
        y = i * dy
        x = circumradius_x(y, alpha, beta, float(gamma))
        a = octagon_area_from_circumradius(x)
        w = 1.0 if (i == 0 or i == n) else 2.0
        s += w * a
    return s * dy / 2.0


def parabola_eq_tex(alpha_f: Fraction, beta_f: Fraction, H: int) -> str:
    if beta_f >= 0:
        bx = f"+ {format_frac_tex(beta_f)}x" if beta_f != 1 else "+ x"
    else:
        bx = f"- {format_frac_tex(-beta_f)}x" if -beta_f != 1 else "- x"
    ax2 = f"{format_frac_tex(alpha_f)}x^2" if alpha_f != 1 else "x^2"
    return f"{ax2} {bx} + {H}"

def format_system_term(coeff, var=""):
    if coeff == 1:
        return f" + {var}" if var else " + 1"
    if coeff == -1:
        return f" - {var}" if var else " - 1"
    if coeff == 0:
        return ""
    if coeff > 0:
        return f" + {format_frac_tex(coeff)}{var}"
    return f" - {format_frac_tex(abs(coeff))}{var}"
    
def format_eq_lhs(A, B, C=1):
    termA = f"{format_frac_tex(A)}a" if A != 1 else "a"
    if A == -1: termA = "-a"
    termB = format_system_term(B, "b")
    termC = format_system_term(C, "c")
    return f"{termA}{termB}{termC}"

SEED_DE_MAU = 626


def generate_question(seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)

    ka_pool = [3, 6, 9, 12]
    H_pool = [6, 9, 12]

    if seed == SEED_DE_MAU:
        ka, kb, H = 6, 2, 6
        V = volume_tent(H, ka, kb)
        ans = round(V, 1)
    else:
        while True:
            ka = random.choice(ka_pool)
            kb = ka // 3
            if kb < 1 or kb >= ka:
                continue
            H = random.choice(H_pool)
            try:
                V = volume_tent(H, ka, kb)
            except (ValueError, ZeroDivisionError):
                continue
            if V <= 0:
                continue
            ans = round(V, 1)
            if ans > 0:
                break

    alpha_f, beta_f, gamma = parabola_coeffs_fractions(H, ka, kb)

    R0 = Fraction(ka, 2)
    Rmid = Fraction(kb, 2)
    R0_tex = format_frac_tex(R0)
    Rmid_tex = format_frac_tex(Rmid)
    
    H_mid = Fraction(H, 2)
    H_mid_tex = format_frac_tex(H_mid)

    alpha_tex = format_frac_tex(alpha_f)
    beta_tex = format_frac_tex(beta_f)
    y_eq_tex = parabola_eq_tex(alpha_f, beta_f, H)

    V_exact_comma = f"{V:.6f}".replace(".", ",")
    ans_comma = f"{ans:.1f}".replace(".", ",")
    ans_dot = f"{ans:.1f}"
    
    # Delta elements scaling to make sure integers are used inside sqrt
    def lcm(a, b):
        return abs(a*b) // math.gcd(a, b)
    
    M = lcm(alpha_f.denominator, beta_f.denominator)
    A_prime = int(alpha_f * M)
    B_prime = int(beta_f * M)
    C_const = int(gamma * M)
    
    # Quadratic eq: A_prime * x^2 + B_prime * x + C_const - M * y = 0
    delta_const = B_prime**2 - 4 * A_prime * C_const
    delta_y_coeff = 4 * A_prime * M
    
    # Factor simple square factors from delta safely if possible
    gcd_delta = math.gcd(abs(delta_const), abs(delta_y_coeff))
    sq_factor = 1
    for i in [2, 3, 4, 5, 6, 7]:
        while gcd_delta % (i*i) == 0:
            sq_factor *= i
            gcd_delta //= (i*i)
            delta_const //= (i*i)
            delta_y_coeff //= (i*i)
            
    prefix_sq = f"{sq_factor}" if sq_factor > 1 else ""

    def format_val(v):
        if v == 1: return "+ y"
        if v == -1: return "- y"
        if v > 0: return f"+ {v}y"
        return f"- {abs(v)}y"
        
    term1 = str(delta_const) if delta_const != 0 else ""
    term2 = format_val(delta_y_coeff)
    
    delta_in_sqrt = ""
    if term1:
        if term2.startswith("+ "): 
            delta_in_sqrt = f"{term1} + {term2[2:]}"
        elif term2.startswith("- "):
            delta_in_sqrt = f"{term1} - {term2[2:]}"
        else:
            delta_in_sqrt = term1
    else:
        if term2.startswith("+ "): 
            delta_in_sqrt = term2[2:]
        elif term2.startswith("- "):
            delta_in_sqrt = f"-{term2[2:]}"
        else:
            delta_in_sqrt = "0"

    delta_latex = f"{prefix_sq}\\sqrt{{{delta_in_sqrt}}}" if prefix_sq else f"\\sqrt{{{delta_in_sqrt}}}"
    
    num_part1 = -B_prime
    denom = 2 * A_prime
    
    # Reduce fraction (-B \pm sqrt) / Denom
    gcd_all = math.gcd(abs(num_part1), math.gcd(sq_factor, abs(denom)))
    if gcd_all > 1:
        num_part1 //= gcd_all
        denom //= gcd_all
        sq_factor //= gcd_all
        prefix_sq = f"{sq_factor}" if sq_factor > 1 else ""
        delta_latex = f"{prefix_sq}\\sqrt{{{delta_in_sqrt}}}" if prefix_sq else f"\\sqrt{{{delta_in_sqrt}}}"

    if denom < 0:
        num_part1 = -num_part1
        denom = -denom
        # \pm handles sign flip easily
    
    if num_part1 == 0:
        if denom == 1:
            x_eq_pm = rf"\pm {delta_latex}"
            x_eq_minus = rf"{delta_latex}"
        else:
            x_eq_pm = rf"\frac{{\pm {delta_latex}}}{{{denom}}}"
            x_eq_minus = rf"\frac{{{delta_latex}}}{{{denom}}}"
    else:
        if denom == 1:
            x_eq_pm = rf"{num_part1} \pm {delta_latex}"
            x_eq_minus = rf"{num_part1} - {delta_latex}"
        else:
            x_eq_pm = rf"\frac{{{num_part1} \pm {delta_latex}}}{{{denom}}}"
            x_eq_minus = rf"\frac{{{num_part1} - {delta_latex}}}{{{denom}}}"
            
    sys_eq1 = format_eq_lhs(R0**2, R0)
    sys_eq2 = format_eq_lhs(Rmid**2, Rmid)

    tikz_code = r"""
\begin{center}
\begin{tikzpicture}[scale=.9, >=stealth,color=red!75!black, line width=1pt]
   \draw (-1.5,4.1) -- (-1.6,3.5) -- (-0.6,3.1) -- (0.7,3.1) -- (1.5,3.5) -- (1.6,4.1) 
   .. controls +(-66:1) and +(126.9:1) .. (3, 1.6) 
   .. controls +(-53.1:0.3) and +(180:0.8) .. (4.8, 0.8) -- (4.8,-0.8) -- (2,-2) -- (-2,-2) -- (-4.8,-0.8) -- (-4.8,0.8) 
   .. controls +(0:0.8) and +(-135:0.6) .. (-3, 1.6) -- (-4.8,0.8);
   \draw (-3,1.6) 
   .. controls +(45:0.6) and +(-113.2:1) .. (-1.5, 4.1) 
   .. controls +(66.8:0.8) and +(-112.1:1.4) .. (0, 7.8) 
   .. controls +(-110.4:1.6) and +(67.2:1.5) .. (-1.6, 3.5) 
   .. controls +(-112.8:2.1) and +(0:1) .. (-4.8, -0.8);
   \draw (-2,-2) 
   .. controls +(45:0.8) and +(-100.3:1.1) .. (-0.6, 3.1) 
   .. controls +(79.7:1.6) and +(-97.3:1.6) .. (0, 7.8) 
   .. controls +(-81.5:1.6) and +(99:1.6) .. (0.7, 3.1) 
   .. controls +(-81:1.9) and +(146.3:0.7) .. (2, -2);
   \draw (4.8,-0.8) 
   .. controls +(180:1) and +(-71.6:0.9) .. (1.5, 3.5) 
   .. controls +(108.4:1.4) and +(-70.8:1.5) .. (0, 7.8) 
   .. controls +(-66.6:1.4) and +(114:1) .. (1.6, 4.1);
   \draw (4.8,0.8) -- (3,1.6);
   \draw [dashed] (1.6,4.1) -- (0.6,4.5) -- (-0.7,4.5) -- (-1.5,4.1);
   \draw [dashed] (3,1.6) -- (2,2) -- (-2,2) -- (-3,1.6);
   \draw [dashed] (-2,2) -- (0,0) -- (-4.8,0.8);
   \draw [dashed] (-4.8,-0.8) -- (0,0) -- (-2,-2);
   \draw [dashed] (2,-2) -- (0,0) -- (4.8,-0.8);
   \draw [dashed] (4.8,0.8) -- (0,0) -- (2,2) 
   .. controls +(-143.1:1) and +(-77.5:0.3) .. (0.6, 4.5) 
   .. controls +(102.5:0.9) and +(-79.7:1.1) .. (0, 7.8) 
   .. controls +(-102:1.1) and +(78.7:1.1) .. (-0.7, 4.5) 
   .. controls +(-101.3:0.5) and +(-26.6:0.9) .. (-2, 2);
   \draw [dashed] (0,0) -- (0,3.8) -- (0,7.8);
   % --- Point Dots (Free) ---
   \fill (0,0) circle (1.2pt) node[shift={(45:3mm)}]{$O$};
   \fill (-4.8,-0.8) circle (1.2pt) node[shift={(165:3mm)}]{$d_1$};
   \fill (-2,-2) circle (1.2pt) node[shift={(240:3mm)}]{$d_2$};
   \fill (2,-2) circle (1.2pt) node[shift={(300:3mm)}]{$d_3$};
   \fill (4.8,-0.8) circle (1.2pt) node[shift={(345:3mm)}]{$d_4$};
   \fill (4.8,0.8) circle (1.2pt) node[shift={(15:3mm)}]{$d_5$};
   \fill (2,2) circle (1.2pt) node[shift={(120:3mm)}]{$d_6$};
   \fill (-2,2) circle (1.2pt) node[shift={(90:3mm)}]{$d_7$};
   \fill (-4.8,0.8) circle (1.2pt) node[shift={(150:3mm)}]{$d_8$};
   \fill (0,7.8) circle (1.2pt) node[shift={(90:3mm)}]{$S$};
\end{tikzpicture}
\end{center}"""

    question = rf'''Người ta dựng một cái lều vải $(H)$ có dạng hình "chóp bát giác cong đều" như hình vẽ bên. Đáy của $(H)$ là một hình bát giác đều độ dài cạnh $a = {ka}\sin\left(\frac{{\pi}}{{8}}\right)\text{{ m}}$. Chiều cao $SO = {H}\text{{ m}}$ (vuông góc với mặt phẳng đáy). Các cạnh bên của $(H)$ là các sợi dây $d_1, d_2, d_3, d_4, d_5, d_6, d_7, d_8$ nằm trên các đường parabol có trục đối xứng song song với $SO$. Giả sử giao tuyến (nếu có) của $(H)$ với mặt phẳng $(P)$ vuông góc với $SO$ là một bát giác đều và khi $(P)$ qua trung điểm của $SO$ thì bát giác đều có độ dài cạnh $b = {kb}\sin\left(\frac{{\pi}}{{8}}\right)\text{{ m}}$. Thể tích phần không gian nằm bên trong cái lều $(H)$ là bao nhiêu mét khối? (làm tròn kết quả đến hàng phần chục).{tikz_code}'''

    solution = f'''Chọn trục tọa độ $Oy$ trùng với $OS$ và $Ox$ trùng với $OA_1$.

Chú ý. Ở đây chọn trục $Oy$ trùng với $OS$ vì đề bài cho trục đối xứng của các đường parabol song song với $OS$.

Sử dụng định lí sin trong tam giác, ta có: $OA_1 = \\frac{{a}}{{2\\sin\\left(\\frac{{2\\pi}}{{16}}\\right)}} = {R0_tex}$; $OB_1 = \\frac{{b}}{{2\\sin\\left(\\frac{{2\\pi}}{{16}}\\right)}} = {Rmid_tex}$ (bán kính ngoại tiếp = độ dài cạnh chia cho hai lần sin góc đối).

Phương trình đường cong parabol $d_1$ là $y = ax^2 + bx + c$ đi qua các điểm $A_1({R0_tex};0)$, $B_1({Rmid_tex};{H_mid_tex})$, $S(0;{H})$
Do đó 
$$ \\begin{{cases}} c = {H} \\\\ {sys_eq1} = 0 \\\\ {sys_eq2} = {H_mid_tex} \\end{{cases}} \\Leftrightarrow a = {alpha_tex},\\ b = {beta_tex},\\ c = {H} \\Rightarrow y = {y_eq_tex}.$$

Khi cắt $(H)$ bởi mặt phẳng vuông góc với trục $Oy$ tại điểm có tung độ $y\\ (0 \\le y \\le {H})$ ta được thiết diện là một hình bát giác đều có bán kính ngoại tiếp là $x$ xác định bởi $y = {y_eq_tex}$.

Giải phương trình bậc hai ẩn $x$, rút ra $x = {x_eq_pm}$ với $0 \\le x \\le {R0_tex}$ nên nhận $x = {x_eq_minus}$.

Do đó diện tích thiết diện vuông góc với trục $Oy$ tại điểm có tung độ $y\\ (0 \\le y \\le {H})$ là
$$ S(y) = 8 \\cdot \\frac{{1}}{{2}}x^2 \\sin\\left(\\frac{{2\\pi}}{{8}}\\right) = 2\\sqrt{{2}}x^2 = 2\\sqrt{{2}}\\left({x_eq_minus}\\right)^2. $$

Và thể tích của $(H)$ là 
$$ V_{{Oy}} = \\int_0^{{{H}}} S(y)\\,dy = \\int_0^{{{H}}} 2\\sqrt{{2}}\\left({x_eq_minus}\\right)^2\\,dy \\approx {ans_comma}\\text{{ m}}^3. $$'''

    return question, solution, f"{ans_comma} | {ans_dot}"


def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])

    content = ""
    answers = []

    for i in range(num_questions):
        q, s, a = generate_question(seed + i if seed is not None else None)
        answers.append(a)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\shortans{{{a}}}\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows,intersections}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}
\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "tent_octagon_volume_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    print("\n=== ĐÁP ÁN ===")
    for i, a in enumerate(answers):
        print(f"Câu {i+1}: Đáp án: {a}")

if __name__ == "__main__":
    main()
