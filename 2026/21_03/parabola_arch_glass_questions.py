r"""
Đề: Chi phí ốp kính cường lực vòm cổng Parabol — tham số ngẫu nhiên.

- Parabol cao $H$ m, rộng $W$ m; lối đi giữa $W_{WALK}$ m $\times$ $H_{WALK}$ m; $N_{layers}$ lớp ngang,
  mỗi lớp cao $DY$ m; đơn giá lớp $i$: $c_i = C_0 + DC(i-1)$ (triệu đồng/m²).
- Đáp án: làm tròn tổng chi phí đến một chữ số thập phân (nửa lên); shortans kiểu
  «Đáp án: 184,6 | 184.6» (phẩy và chấm thường, không dùng ký hiệu {,} của LaTeX).
- Số lớp ngẫu nhiên từ 8 đến 39 (\texttt{range(8, 40)}); hình TikZ minh họa cố định 8 vạch, nhãn theo $N$.

Trình bày LaTeX: dấu phẩy thập phân kiểu Việt Nam trong đề; hai ý đơn giá không dùng
môi trường itemize (theo chuẩn swimming_pool_area_questions.py).
"""

from __future__ import annotations

import logging
import math
import os
import sys
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)

# ==============================================================================
# HẰNG SỐ ĐỀ
# ==============================================================================

DY_VALUES = [0.5, 1.0, 2.0]
N_LAYERS_VALUES = list(range(8, 40))  # 8 .. 39 layers
# Rộng đủ để giữ 0,6 ≤ H/W ≤ 1,4 khi H = N·DY lớn (ví dụ N=39, DY=2).
W_BASE_VALUES = list(range(6, 200))
W_WALK_VALUES = [1.5 + i*0.1 for i in range(26)]
C0_VALUES = [1.0 + round(i*0.1, 1) for i in range(20)]
DC_VALUES = [0.1 + round(i*0.05, 2) for i in range(20)]

def format_decimal_vn(val: float, decimals: int = 2) -> str:
    formatted = f"{val:.{decimals}f}".rstrip("0").rstrip(".")
    return formatted.replace(".", ",")

def simplify_sqrt_frac(rad: int, den: int) -> str:
    a = 1
    for i in range(2, int(math.sqrt(rad)) + 1):
        if rad % (i*i) == 0:
            a = i
    b = rad // (a*a)
    g = math.gcd(a, den)
    a_red = a // g
    den_red = den // g
    
    if b == 1:
        if den_red == 1:
            return f"{a_red}"
        else:
            return f"\\dfrac{{{a_red}}}{{{den_red}}}"
    else:
        if a_red == 1:
            num_str = f"\\sqrt{{{b}}}"
        else:
            num_str = f"{a_red}\\sqrt{{{b}}}"
            
        if den_red == 1:
            return num_str
        else:
            return f"\\dfrac{{{num_str}}}{{{den_red}}}"

def layer_area_i(i: int, N: int, K: int, DY: float) -> float:
    return (2.0 / 3.0) * math.sqrt(K) * (DY ** 1.5) * ((N - i + 1) ** 1.5 - (N - i) ** 1.5)

def compute_totals(p: Dict[str, Any]) -> Dict[str, Any]:
    K = p["K"]
    DY = p["DY"]
    N_LAYERS = p["N_LAYERS"]
    W_WALK = p["W_WALK"]
    N_WALK_LAYERS = p["N_WALK_LAYERS"]
    C0 = p["C0"]
    DC = p["DC"]
    
    a = 0.0
    for i in range(1, N_LAYERS + 1):
        s_i = layer_area_i(i, N_LAYERS, K, DY)
        c_i = C0 + DC * (i - 1)
        a += s_i * c_i
        
    b = 0.0
    hole_area = W_WALK * DY
    for i in range(1, N_WALK_LAYERS + 1):
        c_i = C0 + DC * (i - 1)
        b += hole_area * c_i
        
    diff = a - b
    ans = round(diff + 1e-12, 1)
    
    return {
        "A": a,
        "B": b,
        "diff": diff,
        "answer_round1": ans,
    }

def try_random_params(max_attempts: int = 120_000) -> Dict[str, Any]:
    for _ in range(max_attempts):
        DY = random.choice(DY_VALUES)
        N_LAYERS = random.choice(N_LAYERS_VALUES)
        H = N_LAYERS * DY
        
        if not (4 <= H <= 100):
            continue
            
        W = random.choice(W_BASE_VALUES)
        if not (0.6 <= H / W <= 1.4):
            continue
        if (W * W) % H != 0:
            continue
        if (W * W) / H != int((W * W) / H):
            continue
        K = int((W * W) / H)
        
        N_WALK_LAYERS = random.randint(1, N_LAYERS - 1)
        H_WALK = N_WALK_LAYERS * DY
        
        if not (1.5 <= H_WALK <= 4.0):
            continue
        if H_WALK > 0.7 * H:
            continue
        if H < H_WALK + 1.5:
            continue
            
        W_WALK = random.choice(W_WALK_VALUES)
        if W_WALK > 0.5 * W:
            continue
        if (W - W_WALK) / 2 < 1.8:
            continue
        max_w = math.sqrt(K * (H - H_WALK))
        if W_WALK >= max_w - 0.2:
            continue
            
        C0 = random.choice(C0_VALUES)
        DC = random.choice(DC_VALUES)
        
        return {
            "DY": DY,
            "N_LAYERS": N_LAYERS,
            "H": H,
            "W": W,
            "N_WALK_LAYERS": N_WALK_LAYERS,
            "W_WALK": W_WALK,
            "H_WALK": H_WALK,
            "C0": C0,
            "DC": DC,
            "K": K
        }
    raise RuntimeError("Không tìm được bộ tham số hợp lệ")

@dataclass
class GeneratorConfig:
    seed: Optional[int] = None

def _hardcoded_layer_labels(n_layers: int, indent: str = "   ") -> str:
    """Tám đường lớp cố định (vòm 4 m × 4 m, bước 0{,}5 m); chỉ nhãn thay đổi."""
    lines: list[str] = []
    for i in range(1, 5):
        lines.append(f"{indent}\\pgfmathsetmacro{{\\y}}{{{i}*0.5}}")
        lines.append(f"{indent}\\pgfmathsetmacro{{\\x}}{{sqrt((4-\\y)/1)}}")
        lines.append(f"{indent}\\draw[thick, cyan!50!blue] (-\\x,\\y) -- (\\x,\\y);")
        if n_layers <= 8:
            if i <= n_layers:
                lines.append(
                    f"{indent}\\node[left,scale=0.6] at (-\\x+0.45,\\y-0.25) {{Lớp {i}}};"
                )
        else:
            lines.append(
                f"{indent}\\node[left,scale=0.6] at (-\\x+0.45,\\y-0.25) {{Lớp {i}}};"
            )
    if n_layers > 8:
        lines.append(f"{indent}\\node[left,scale=0.65] at (-1.35,2.25) {{$\\cdots$}};")
    for i in range(5, 9):
        lines.append(f"{indent}\\pgfmathsetmacro{{\\y}}{{{i}*0.5}}")
        lines.append(f"{indent}\\pgfmathsetmacro{{\\x}}{{sqrt((4-\\y)/1)}}")
        lines.append(f"{indent}\\draw[thick, cyan!50!blue] (-\\x,\\y) -- (\\x,\\y);")
        if n_layers <= 8:
            if i <= n_layers:
                lines.append(
                    f"{indent}\\node[left,scale=0.7] at (0.25,\\y-0.25) {{Lớp {i}}};"
                )
        else:
            ln = n_layers - 8 + i
            lines.append(
                f"{indent}\\node[left,scale=0.7] at (0.25,\\y-0.25) {{Lớp {ln}}};"
            )
    return "\n".join(lines)


def generate_tikz_question(N_LAYERS: int) -> str:
    layer = _hardcoded_layer_labels(N_LAYERS, indent="   ")
    tikz = (
        r"""\begin{tikzpicture}[>=stealth, scale=1.2,xscale=1, font=\footnotesize]
   % Parabol
   \draw[cyan!20, opacity=0.4, domain=-2.5:2.5,very thick, blue!70!black, domain=-2:2, samples=100] 
   plot (\x, {-1*\x*\x + 4});
   
   % Các lớp ngang + nhãn
"""
        + layer
        + r"""
   
   % Cửa
   \fill[orange!80] (-1,0) rectangle (1,2);
   \draw[very thick, brown!80!black] (-1,0) rectangle (1,2);
   
   % Đáy
   \draw[thick] (-2,0) -- (2,0);
   
   \tikzset{Icon-Tau/.pic={
\draw[fill=black] (0.37,0.23) .. controls +(-60.71:0.08) and +(104.82:0.09) .. (0.56,0.01) .. controls +(-78.4:0.03) and +(-7.1:0.07) .. (0.43,0) .. controls +(-174.06:0.06) and +(-36.62:0.09) .. (0.25,0.05) .. controls +(133.77:0.05) and +(-106.6:0.04) .. (0.23,0.16) .. controls +(172.87:0.04) and +(-47.56:0.04) .. (0.12,0.17) .. controls +(161.57:0.04) and +(-72:0.03) .. (0.06,0.25) .. controls +(45.45:0.13) and +(-139.82:0.13) .. (0.27,0.52) .. controls +(106.35:0.05) and +(-110.94:0.05) .. (0.29,0.66) .. controls +(43.15:0.14) and +(-120.39:0.16) .. (0.52,0.98) .. controls +(105.69:0.1) and +(-79.19:0.11) .. (0.51,1.29) .. controls +(90.68:0.11) and +(-88.95:0.1) .. (0.56,1.61) .. controls +(80.32:0.05) and +(-90.87:0.07) .. (0.54,1.78) .. controls +(-118.25:0.08) and +(43.23:0.07) .. (0.42,1.59) .. controls +(-100.12:0.09) and +(82.21:0.04) .. (0.38,1.38) .. controls +(-109.02:0.06) and +(-82.33:0.13) .. (0.23,1.39) .. controls +(87.77:0.08) and +(-106.95:0.08) .. (0.28,1.62) .. controls +(66.31:0.11) and +(-95.39:0.1) .. (0.36,1.9) .. controls +(74.4:0.13) and +(-100.48:0.11) .. (0.48,2.19) .. controls +(69.58:0.09) and +(-122.32:0.07) .. (0.63,2.34) .. controls +(101.22:0.04) and +(-93.63:0.05) .. (0.63,2.45) .. controls +(160.29:0.01) and +(-65.09:0.04) .. (0.57,2.52) .. controls +(139.42:0.03) and +(-90.41:0.08) .. (0.53,2.74) .. controls +(76.93:0.06) and +(-148.46:0.05) .. (0.65,2.88) .. controls +(15.5:0.1) and +(174.72:0.07) .. (0.88,2.9) .. controls +(-19.58:0.08) and +(106.35:0.04) .. (0.99,2.79) .. controls +(-101.61:0.05) and +(144.18:0.05) .. (0.99,2.66) .. controls +(-111.42:0.03) and +(52.53:0.05) .. (0.96,2.53) .. controls +(-155.31:0.06) and +(43.5:0.06) .. (0.82,2.44) .. controls +(-92.84:0.03) and +(87.23:0.03) .. (0.82,2.34) .. controls +(-40.52:0.2) and +(85.62:0.15) .. (0.97,1.94) .. controls +(-20.93:0.14) and +(132.63:0.18) .. (1.43,1.55) .. controls +(-90:0.06) and +(56.49:0.04) .. (1.4,1.41) .. controls +(178.14:0.04) and +(-1.93:0.04) .. (1.27,1.41) .. controls +(121.93:0.04) and +(-57.98:0.04) .. (1.2,1.52) .. controls +(103.92:0.04) and +(-38.57:0.05) .. (1.09,1.63) .. controls +(175.16:0.03) and +(-4.76:0.04) .. (0.99,1.7) .. controls +(-169.9:0.05) and +(100.73:0.04) .. (0.9,1.59) .. controls +(-64:0.12) and +(74.72:0.09) .. (0.95,1.31) .. controls +(-42.11:0.15) and +(98.72:0.14) .. (1.22,0.93) .. controls +(-84.72:0.06) and +(103.38:0.06) .. (1.25,0.76) .. controls +(-63.41:0.11) and +(91.99:0.08) .. (1.31,0.51) .. controls +(-53.82:0.11) and +(102.98:0.09) .. (1.4,0.26) .. controls +(-36.79:0.04) and +(143.16:0.04) .. (1.51,0.18) .. controls +(0:0.05) and +(180:0.06) .. (1.67,0.18) .. controls +(-47.53:0.07) and +(-0.53:0.07) .. (1.64,0.02) .. controls +(-165.74:0.06) and +(-22.76:0.07) .. (1.46,0.04) .. controls +(-148.94:0.06) and +(-4.77:0.07) .. (1.3,0) .. controls +(137.46:0.08) and +(-69.09:0.07) .. (1.24,0.18) .. controls +(125.81:0.1) and +(-91.19:0.09) .. (1.14,0.42) .. controls +(95.65:0.07) and +(-85.24:0.09) .. (1.06,0.68) .. controls +(108.14:0.12) and +(-55.9:0.12) .. (0.9,0.98) .. controls +(165.73:0.07) and +(66.1:0.06) .. (0.73,0.93) .. controls +(-53.66:0.07) and +(78.79:0.05) .. (0.75,0.77) .. controls +(-140.06:0.12) and +(38.48:0.11) .. (0.53,0.52) .. controls +(-116.62:0.05) and +(63.43:0.05) .. (0.46,0.39) .. controls +(-135.16:0.08) and +(82.23:0.06) .. (0.37,0.23);
   }}
   \foreach \x in {0,0.5,...,3.5}
   \draw[<->] (2.5,\x)--(2.5,\x+0.5)node[pos=0.5,right]{$0{,}5$ m};
   
   % Kích thước chiều cao (4m)
   \draw[<->] (-2.5,0) -- (-2.5,4);
   \node[rotate=90,above] at (-2.5,2) {$4$ m};
   
   % Kích thước chiều rộng (4m)
   \draw[<->] (-2, -0.5) -- (2, -0.5);
   \node[below] at (0,-0.5) {$4$ m};
   
   % Kích thước cửa (2m)
   \draw[<->] (-1, -1) -- (1, -1);
   \node[below] at (0,-1) {$2$ m};
   \path (0,4.5) node[above]{\textbf{Khu Vực Ốp Lát Kính}};
   
   \path (-0.45,0) pic[scale=0.7]{Icon-Tau};
\end{tikzpicture}"""
    )
    return tikz.strip()

def generate_tikz_solution(N_LAYERS: int, K: int, H_tex: str) -> str:
    layer = _hardcoded_layer_labels(N_LAYERS, indent="    ")
    inner = f"\\sqrt{{{K}({H_tex}-y)}}"
    draw_formula = (
        "    \\draw[<-] (1.5, 1.5) -- (2.5, 1.5) "
        "node[right] {$x = d(y) = " + inner + "$};\n"
    )
    tikz = (
        r"""\begin{tikzpicture}[>=stealth, scale=1.5,xscale=1, font=\footnotesize]
    % Parabol
    \draw[cyan!20, opacity=0.4, domain=-2.5:2.5,very thick, blue!70!black, domain=-2:2, samples=100] 
    plot (\x, {-1*\x*\x + 4});
    
    % Các lớp ngang + nhãn
"""
        + layer
        + r"""
    
    % Cửa
    \fill[orange!80] (-1,0) rectangle (1,2);
    \draw[very thick, brown!80!black] (-1,0) rectangle (1,2);
    
    % Đáy
    \draw[thick] (-2,0) -- (2,0);
    
    % Kích thước chiều cao (4m)
    \draw[<->] (-2.5,0) -- (-2.5,4);
    \node[rotate=90,above] at (-2.5,2) {$4$ m};
    
    % Kích thước chiều rộng (4m)
    \draw[<->] (-2, -0.5) -- (2, -0.5);
    \node[below] at (0,-0.5) {$4$ m};
    
    % Kích thước cửa (2m)
    \draw[<->] (-1, -1) -- (1, -1);
    \node[below] at (0,-1) {$2$ m};
    \path (0,4.5) node[above]{\textbf{Khu Vực Ốp Lát Kính}};
    \draw[<->] (-2,-0.25)--(-2.5,-0.25) node[below]{$0{,}5$ m};
    
"""
        + draw_formula
        + r"""
    % Trục mờ
    \draw[->, gray!60] (-3.5,0) -- (4,0);
    \draw[->, gray!60] (0,-0.5) -- (0,5.8);
\end{tikzpicture}"""
    )
    return tikz.strip()

def _tpl(s: str, mapping: Dict[str, Any]) -> str:
    out = s
    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(f"<{k}>", str(mapping[k]))
    return out

TEMPLATE_QUESTION = r"""Để hoàn thiện mặt tiền của một tòa nhà, người ta trang trí một cổng chào dạng vòm Parabol bằng kính cường lực. Cổng có chiều cao $<H>$ m và chiều rộng là $<W>$ m. Ở chính giữa cổng là một lối đi hình chữ nhật cao $<H_WALK_STR>$ m và rộng $<W_WALK_STR>$ m. Diện tích phần cổng chào Parabol (sau khi đã trừ đi lối đi hình chữ nhật) được chia thành $<N_LAYERS>$ lớp ngang, mỗi lớp cao $<DY_STR>$ m để lắp đặt các tấm kính màu khác nhau.

\begin{center}
<tikz_question>
\end{center}

Đơn giá thi công lắp kính cường lực được tính như sau:

Lớp dưới cùng của cổng là $<C0_STR>$ triệu đồng/m$^2$.

Càng lên cao, giá thi công mỗi lớp tiếp theo tăng thêm $<DC_STR>$ triệu đồng/m$^2$ so với lớp ngay dưới nó.

Tính tổng chi phí (đơn vị: triệu đồng) lắp kính cường lực màu cho phần diện tích còn lại của cổng sau khi đã loại bỏ lối đi (không làm tròn kết quả các phép toán trung gian, chỉ làm tròn kết quả phép toán cuối cùng đến hàng phần mười).
"""

TEMPLATE_SOLUTION = r"""\begin{center}
<tikz_solution>
\end{center}

Ta chọn hệ trục tọa độ $Oxy$ như hình vẽ, khi đó đồ thị Parabol có đỉnh là $(0;<H>)$ và đi qua điểm $(<W_HALF_STR>;0)$.
Suy ra phương trình của Parabol là $<PARABOLA_EQ>$.
Khi đó độ rộng của vòm cổng tại độ cao $y$ (m) là:
\[ x = d(y) = 2\sqrt{<FRAC_W2_4H>(<H>-y)} = \sqrt{<K>(<H>-y)}. \]
Ta có vòm cổng được chia thành $<N_LAYERS>$ lớp ngang với độ cao $<DY_STR>$ m mỗi lớp, nên lớp thứ $i$ (với $1 \le i \le <N_LAYERS>$) được giới hạn từ tung độ $y = <LOWER_BOUND>$ đến $y = <UPPER_BOUND>$ và có đơn giá tương ứng là $c_i = <C0_STR> + <DC_STR>(i-1)$ (triệu đồng/m$^2$).

Diện tích của lớp thứ $i$ là:
\[ S_i = \int_{<LOWER_BOUND>}^{<UPPER_BOUND>} \sqrt{<K>(<H>-y)}\,dy = <SQRT_FRAC>\left[(<N_LAYERS_PLUS_1>-i)\sqrt{<N_LAYERS_PLUS_1>-i} - (<N_LAYERS>-i)\sqrt{<N_LAYERS>-i}\right]. \]
Suy ra tổng chi phí giả định nếu ốp kính cho toàn bộ diện tích vòm Parabol là:
\[ A = \sum_{i=1}^{<N_LAYERS>} \left[ \int_{<LOWER_BOUND>}^{<UPPER_BOUND>} \sqrt{<K>(<H>-y)}\,dy \cdot c_i \right] \]
\[ A = \sum_{i=1}^{<N_LAYERS>} \left[ <SQRT_FRAC>\left[(<N_LAYERS_PLUS_1>-i)\sqrt{<N_LAYERS_PLUS_1>-i} - (<N_LAYERS>-i)\sqrt{<N_LAYERS>-i}\right] \cdot [<C0_STR> + <DC_STR>(i-1)] \right] \approx <A_approx> \text{ (triệu đồng)}. \]
Ta có phần lối đi trống ở giữa là hình chữ nhật rộng $<W_WALK_STR>$ m và cao $<H_WALK_STR>$ m, nằm trọn vẹn trong không gian của $<N_WALK_LAYERS>$ lớp ngang dưới cùng, diện tích bị khuyết ở mỗi lớp này bằng $<W_WALK_STR> \times <DY_STR> = <HOLE_AREA_STR>$ m$^2$.
Suy ra phần chi phí lối đi hình chữ nhật cần trừ ra là:
\[ B = \sum_{i=1}^{<N_WALK_LAYERS>} <HOLE_AREA_STR> \cdot c_i = \sum_{i=1}^{<N_WALK_LAYERS>} <HOLE_AREA_STR> \cdot [<C0_STR> + <DC_STR>(i-1)] = <B_exact> \text{ (triệu đồng)}. \]
Vậy số tiền cần tìm là:
\[ A - B = <A_approx> - <B_exact> = <diff_approx> \approx <answer> \text{ (triệu đồng)}. \]
"""

class ParabolaArchGlassQuestion:
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        return try_random_params()

    def calculate_values(self) -> Dict[str, Any]:
        p = self.parameters
        t = compute_totals(p)
        
        H = p["H"]
        W = p["W"]
        W_WALK = p["W_WALK"]
        H_WALK = p["H_WALK"]
        C0 = p["C0"]
        DC = p["DC"]
        K = p["K"]
        DY = p["DY"]
        N_LAYERS = p["N_LAYERS"]
        N_WALK_LAYERS = p["N_WALK_LAYERS"]
        
        a_s = format_decimal_vn(t["A"], 4).replace(",", "{,}")
        diff_s = format_decimal_vn(t["diff"], 4).replace(",", "{,}")
        ans_s = format_decimal_vn(t["answer_round1"], 1)
        ans_tex = ans_s.replace(",", "{,}")
        ans_dot = ans_s.replace(",", ".")
        answer_shortans_tex = f"Đáp án: {ans_s} | {ans_dot}"
        answer_plain_shortans = answer_shortans_tex
        
        W_WALK_STR = format_decimal_vn(W_WALK, 1) if W_WALK != int(W_WALK) else str(int(W_WALK))
        H_WALK_STR = format_decimal_vn(H_WALK, 1) if H_WALK != int(H_WALK) else str(int(H_WALK))
        C0_STR = format_decimal_vn(C0, 1)
        DC_STR = format_decimal_vn(DC, 2)
        
        W_HALF = W / 2
        W_HALF_STR = format_decimal_vn(W_HALF, 1) if W_HALF != int(W_HALF) else str(int(W_HALF))
        
        num = int(4 * H)
        den = int(W * W)
        g = math.gcd(num, den)
        n_red = num // g
        d_red = den // g
        if d_red == 1:
            parabola_eq = f"y = -{n_red}x^2 + {H}"
        else:
            parabola_eq = f"y = -\\dfrac{{{n_red}}}{{{d_red}}}x^2 + {H}"
            
        num2 = int(W * W)
        den2 = int(4 * H)
        g2 = math.gcd(num2, den2)
        n2_red = num2 // g2
        d2_red = den2 // g2
        if d2_red == 1:
            frac_w2_4h = f"{n2_red}"
        else:
            frac_w2_4h = f"\\dfrac{{{n2_red}}}{{{d2_red}}}"
            
        M = int(2 * K * (2 * DY)**3)
        sqrt_frac = simplify_sqrt_frac(M, 6)
        if sqrt_frac == "1":
            sqrt_frac = ""
            
        if DY == 0.5:
            lower_bound = r"\dfrac{i-1}{2}"
            upper_bound = r"\dfrac{i}{2}"
            dy_str = "0{,}5"
        elif DY == 1.0:
            lower_bound = r"i-1"
            upper_bound = r"i"
            dy_str = "1"
        elif DY == 2.0:
            lower_bound = r"2(i-1)"
            upper_bound = r"2i"
            dy_str = "2"
        
        hole_area = W_WALK * DY
        hole_area_str = format_decimal_vn(hole_area, 2).replace(",", "{,}")
        if hole_area == int(hole_area):
            hole_area_str = str(int(hole_area))
            
        b_exact_str = format_decimal_vn(t["B"], 2).replace(",", "{,}")
        if t["B"] == int(t["B"]):
            b_exact_str = str(int(t["B"]))
            
        H_STR = format_decimal_vn(H, 1) if H != int(H) else str(int(H))
        W_STR = format_decimal_vn(W, 1) if W != int(W) else str(int(W))
        H_tex = H_STR.replace(",", "{,}")
        
        return {
            "H": H_tex,
            "W": W_STR.replace(",", "{,}"),
            "W_WALK_STR": W_WALK_STR.replace(",", "{,}"),
            "H_WALK_STR": H_WALK_STR.replace(",", "{,}"),
            "N_LAYERS": N_LAYERS,
            "N_WALK_LAYERS": N_WALK_LAYERS,
            "C0_STR": C0_STR.replace(",", "{,}"),
            "DC_STR": DC_STR.replace(",", "{,}"),
            "W_HALF_STR": W_HALF_STR.replace(",", "{,}"),
            "PARABOLA_EQ": parabola_eq,
            "FRAC_W2_4H": frac_w2_4h,
            "K": K,
            "SQRT_FRAC": sqrt_frac,
            "N_LAYERS_PLUS_1": N_LAYERS + 1,
            "HOLE_AREA_STR": hole_area_str,
            "B_exact": b_exact_str,
            "A_approx": a_s,
            "diff_approx": diff_s,
            "answer": ans_tex,
            "answer_tex": ans_tex,
            "answer_shortans_tex": answer_shortans_tex,
            "answer_plain_shortans": answer_plain_shortans,
            "DY_STR": dy_str,
            "LOWER_BOUND": lower_bound,
            "UPPER_BOUND": upper_bound,
            "tikz_question": generate_tikz_question(N_LAYERS),
            "tikz_solution": generate_tikz_solution(N_LAYERS, K, H_tex),
        }

    def generate_question_text(self) -> str:
        c = self.calculated_values
        return _tpl(TEMPLATE_QUESTION, c).strip()

    def generate_solution(self) -> str:
        c = self.calculated_values
        return _tpl(TEMPLATE_SOLUTION, c).strip()

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info("Đang tạo câu hỏi %s", question_number)
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()

        question_text = self.generate_question_text()
        solution = self.generate_solution()
        shortans_body = self.calculated_values["answer_shortans_tex"]

        question_content = (
            f"\\begin{{ex}}%Câu {question_number}\n"
            f"{question_text}\n\n"
            f"\\shortans{{{shortans_body}}}\n"
            f"\\loigiai{{\n{solution}\n}}\n"
            f"\\end{{ex}}\n"
        )
        return question_content, self.calculated_values["answer_plain_shortans"]

    @staticmethod
    def create_latex_document(questions_data: List[Tuple[str, str]]) -> str:
        questions_content = "\n\n".join(q for q, _ in questions_data)
        return (
            r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{calc,arrows}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}
\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

"""
            + questions_content
            + r"""

\end{document}
"""
        )

def main() -> None:
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        if seed is not None:
            random.seed(seed)
            logging.info("Sử dụng seed: %s", seed)

        questions_data: List[Tuple[str, str]] = []
        for i in range(num_questions):
            q = ParabolaArchGlassQuestion(GeneratorConfig(seed=seed))
            content, ans = q.generate_question_only(i + 1)
            questions_data.append((content, ans))

        latex_content = ParabolaArchGlassQuestion.create_latex_document(questions_data)
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "parabola_arch_glass_questions.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        logging.info("Đã ghi file: %s", output_file)
        print(f"\nĐã tạo {num_questions} câu và lưu: {output_file}")
        print("\n=== ĐÁP ÁN (triệu đồng) ===")
        for i, (_, a) in enumerate(questions_data):
            print(f"Câu {i + 1}: {a}")
    except ValueError as e:
        print(f"Lỗi: {e}")
        print("Usage: python parabola_arch_glass_questions.py <num_questions> [seed]")
        sys.exit(1)

if __name__ == "__main__":
    main()
