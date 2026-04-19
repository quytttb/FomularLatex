r"""
Đề toán: Diện tích hồ bơi — thửa đất $EFGH$, bốn cung $(C_1)$–$(C_4)$.

- $HG$, $FG$, $AB$, $CD$, khoảng cách $K$–$EF$, và $R_4^2$ (trong $\sqrt{R_4^2}$) mỗi cái
  được chọn ngẫu nhiên trong đúng 20 giá trị (xem hằng *_VALUES). Khoảng cách
  $I$–$HG$/$HE$ = $AB/2$, $K$–$FG$ = $CD/2$; $FG$ đồng bộ $FG = AB + d_{K,EF} - CD/2$.
- Giá trị ghi trong ô đáp án: $\lfloor S + 1/2\rfloor$ (làm tròn đến đơn vị, nửa lên) khớp đề.
"""

import logging
import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from scipy.integrate import quad

logging.basicConfig(level=logging.INFO)

# ==============================================================================
# 20 GIÁ TRỊ / THAM SỐ
# ==============================================================================


@dataclass
class GeneratorConfig:
    seed: Optional[int] = None


HG_VALUES: List[int] = list(range(14, 34))  # 14..33
FG_VALUES: List[int] = list(range(10, 30))  # 10..29
AB_VALUES: List[int] = [6 + 2 * i for i in range(20)]  # 6,8,...,44 (đường kính)
CD_VALUES: List[int] = [4 + 2 * i for i in range(20)]  # 4,6,...,42
DIST_K_EF_VALUES: List[int] = list(range(3, 23))  # 3..22 (K đến cạnh EF)
R4_SQ_VALUES: List[int] = [18 + 2 * i for i in range(20)]  # 18,20,...,56 (R_4^2)

for _name, _lst in [
    ("HG_VALUES", HG_VALUES),
    ("FG_VALUES", FG_VALUES),
    ("AB_VALUES", AB_VALUES),
    ("CD_VALUES", CD_VALUES),
    ("DIST_K_EF_VALUES", DIST_K_EF_VALUES),
    ("R4_SQ_VALUES", R4_SQ_VALUES),
]:
    assert len(_lst) == 20, f"{_name} phải có đúng 20 phần tử, có {len(_lst)}"


# ==============================================================================
# HÌNH HỌC
# ==============================================================================


def round_answer_positive(area: float) -> int:
    """Làm tròn đến hàng đơn vị, nửa đơn vị làm tròn lên (đề: làm tròn đến đơn vị)."""
    return int(math.floor(area + 0.5))


def solve_o3(W: float, d1: float, x1: float, x2: float) -> Optional[Tuple[float, float, float]]:
    """
    Đường tròn qua (x1,d1), (x2,d1), tiếp xúc y=W, tâm phía dưới EF (b < W).
    Trả về (a, b, R3) hoặc None.
    """
    if abs(W - d1) < 1e-9:
        return None
    h = abs(x2 - x1) / 2
    num = W * W - d1 * d1 - h * h
    den = 2 * (W - d1)
    b = num / den
    a = (x1 + x2) / 2
    R3 = W - b
    if R3 <= 1e-6 or b <= 1e-6:
        return None
    if (a - x1) ** 2 + (b - d1) ** 2 > R3 * R3 + 1e-4:
        return None
    return (a, b, R3)


def solve_o4_lower(
    x1: float, x2: float, y_d: float, r4_sq: float
) -> Optional[Tuple[float, float]]:
    """Tâm đường tròn qua B(x1,0), D(x2,y_d), bán kính sqrt(r4_sq); chọn tâm có tung độ nhỏ hơn (cung dưới)."""
    R = math.sqrt(r4_sq)
    dx = x2 - x1
    dy = y_d - 0.0
    d_chord = math.hypot(dx, dy)
    if d_chord > 2 * R + 1e-9:
        return None
    mx = (x1 + x2) / 2
    my = y_d / 2
    if d_chord < 1e-12:
        return None
    u = (-dy / d_chord, dx / d_chord)
    half = d_chord / 2
    h_sq = R * R - half * half
    if h_sq < -1e-9:
        return None
    h_off = math.sqrt(max(0.0, h_sq))
    c1 = (mx + h_off * u[0], my + h_off * u[1])
    c2 = (mx - h_off * u[0], my - h_off * u[1])
    dist_b1 = (c1[0] - x1) ** 2 + c1[1] ** 2
    dist_b2 = (c2[0] - x1) ** 2 + c2[1] ** 2
    if abs(dist_b1 - r4_sq) > 0.01 or abs(dist_b2 - r4_sq) > 0.01:
        return None
    return c1 if c1[1] < c2[1] else c2


def build_geometry(
    L: int, W: int, d1: int, d2: int, dist_k_ef: int, r4_sq: int
) -> Optional[Dict[str, Any]]:
    """
    H(0,0), G(L,0), F(L,W), E(0,W).
    I = (d1/2, d1/2), K = (L - d2/2, W - dist_k_ef).
    Điều kiện đồng bộ: W = d1 + dist_k_ef - d2/2.
    """
    if abs(W - (d1 + dist_k_ef - d2 / 2)) > 1e-9:
        return None

    x1 = d1 / 2
    x2 = L - d2 / 2
    if x2 <= x1 + 1e-6:
        return None
    # Tránh phần giữa quá hẹp (hình vẽ và đề không hợp lý)
    if x2 - x1 < 3:
        return None

    y_k = W - dist_k_ef
    if y_k < d2 / 2 - 1e-9:
        return None

    y_c = y_k + d2 / 2
    if abs(y_c - d1) > 1e-6:
        return None

    y_d = y_k - d2 / 2
    if y_d < -1e-9:
        return None

    o3 = solve_o3(float(W), float(d1), x1, x2)
    if o3 is None:
        return None
    a3, b3, R3 = o3

    # Đảm bảo hệ 3 phương trình giải ra a, b, R3 có giá trị nguyên
    if not (float(a3).is_integer() and float(b3).is_integer() and float(R3).is_integer()):
        return None

    o4 = solve_o4_lower(x1, x2, y_d, float(r4_sq))
    if o4 is None:
        return None
    m4, n4 = o4
    R4 = math.sqrt(r4_sq)

    def f_top(x: float) -> float:
        rad = R3**2 - (x - a3) ** 2
        return b3 + math.sqrt(max(0.0, rad))

    def g_bot(x: float) -> float:
        rad = R4**2 - (x - m4) ** 2
        return n4 + math.sqrt(max(0.0, rad))

    def integrand(x: float) -> float:
        return f_top(x) - g_bot(x)

    try:
        s_mid, _ = quad(integrand, x1, x2, limit=200)
    except Exception:
        return None

    if s_mid <= 0 or not math.isfinite(s_mid):
        return None

    R1 = d1 / 2
    R2 = d2 / 2
    s_ngoai = 0.5 * math.pi * R1**2 + 0.5 * math.pi * R2**2
    total = s_ngoai + s_mid

    if not math.isfinite(total):
        return None

    ans = round_answer_positive(total)
    if abs(ans - total) > 0.5 + 1e-6:
        return None

    return {
        "L": L,
        "W": W,
        "d1": d1,
        "d2": d2,
        "dist_k_ef": dist_k_ef,
        "r4_sq": r4_sq,
        "x1": x1,
        "x2": x2,
        "y_d": y_d,
        "a3": a3,
        "b3": b3,
        "R3": R3,
        "m4": m4,
        "n4": n4,
        "R4": R4,
        "R1": R1,
        "R2": R2,
        "s_ngoai": s_ngoai,
        "s_mid": s_mid,
        "total": total,
        "answer": ans,
    }


def try_random_params(max_attempts: int = 8000) -> Dict[str, Any]:
    for _ in range(max_attempts):
        L = random.choice(HG_VALUES)
        d1 = random.choice(AB_VALUES)
        d2 = random.choice(CD_VALUES)
        dist_k_ef = random.choice(DIST_K_EF_VALUES)
        W_float = d1 + dist_k_ef - d2 / 2
        if abs(W_float - round(W_float)) > 1e-9:
            continue
        W = int(round(W_float))
        if W not in FG_VALUES:
            continue
        if dist_k_ef < d2 / 2 - 1e-9:
            continue
        if W < dist_k_ef + d2 / 2 - 1e-9:
            continue
        r4_sq = random.choice(R4_SQ_VALUES)
        g = build_geometry(L, W, d1, d2, dist_k_ef, r4_sq)
        if g is not None:
            return g
    raise RuntimeError("Không tìm được bộ tham số hợp lệ; mở rộng tập giá trị hoặc max_attempts.")


# ==============================================================================
# LATEX / TIKZ
# ==============================================================================


def pf(v: float) -> str:
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s.replace(".", ",") if s else "0"


def format_int(n: int) -> str:
    return str(n)


def format_decimal_vn(val: float, decimals: int = 2) -> str:
    formatted = f"{val:.{decimals}f}".rstrip("0").rstrip(".")
    return formatted.replace(".", ",")


def _simplify_pi_over_8(num: int) -> str:
    """Rút gọn num·π/8 thành dạng tối giản."""
    g = math.gcd(num, 8)
    n_red, d_red = num // g, 8 // g
    if d_red == 1:
        return f"{n_red}\\pi"
    return f"\\dfrac{{{n_red}\\pi}}{{{d_red}}}"


def format_s_ngoai_pi_latex(d1: int, d2: int) -> str:
    return _simplify_pi_over_8(d1 * d1 + d2 * d2)


# TikZ cố định theo đề mẫu (Câu 21) — không tham số hóa theo random.
TIKZ_QUESTION_HARD = r"""
\begin{tikzpicture}[scale=0.6,>=stealth, font=\footnotesize, line join=round, line cap=round]
   \path
   (5,10) coordinate (A)
   (5,0) coordinate (B)
   (13,10) coordinate (C)
   (13,4) coordinate (D)
   (0,0) coordinate (H)
   (16,0) coordinate (G)
   (0,12) coordinate (E)
   (16,12) coordinate (F)
   ($(A)!0.5!(B)$) coordinate (I)
   ($(C)!0.5!(D)$) coordinate (K)
   ;
   \draw (A) arc (90:270:5) ;
   \draw (C) arc (90:-90:3) ;
   \draw (C) arc ({atan(3/4)}:{180-atan(3/4)}:5) ;
   \draw (D) arc ({atan(3)}:{180-atan(1/3)}:{sqrt(40)}) ;
   \draw (H)--(G)--(F)--(E)--cycle;
   \draw[dashed](A)--(B)  (C)--(D) ;
   \foreach \x/\g in {A/120,B/-90,C/40,D/-90,E/120,F/40,H/-140,G/-40,I/140,K/140}
   \fill[black] (\x) circle (1pt) +  (\g:5mm) node {$\x$};
  \end{tikzpicture}
"""

TIKZ_SOLUTION_HARD = r"""
\begin{tikzpicture}[scale=0.5,>=stealth, font=\footnotesize, line join=round, line cap=round]
  \path
  (5,10) coordinate (A)
  (5,0) coordinate (B)
  (13,10) coordinate (C)
  (13,4) coordinate (D)
  (0,0) coordinate (H)
  (16,0) coordinate (G)
  (0,12) coordinate (E)
  (16,12) coordinate (F)
  (9,7) coordinate (O_3)
  (11,-2) coordinate (O_4)
  ($(A)!0.5!(B)$) coordinate (I)
  ($(E)!0.55!(F)$) coordinate (J)
  ($(C)!0.5!(D)$) coordinate (K)
  ;
  \draw (A) arc (90:270:5) ;
  \draw (C) arc (90:-90:3) ;
  \draw (C) arc ({atan(3/4)}:{180-atan(3/4)}:5) ;
  \draw (D) arc ({atan(3)}:{180-atan(1/3)}:{sqrt(40)}) ;
  \draw (H)--(G)--(F)--(E)--cycle (A)--(B)--(D)--(C)--(A) (A)--(O_3)--(C) (B)--(O_4)--(D);
  \foreach \x/\g in {A/120,B/-90,C/40,D/-70,E/120,F/40,H/-140,G/-40,J/90,O_3/-40,O_4/-40}
  \fill[black] (\x) circle (1pt) +  (\g:5mm) node {$\x$};
 \end{tikzpicture}
"""


def _tpl(s: str, mapping: Dict[str, Any]) -> str:
    """Thay <key> bằng str(value); thay khóa dài trước để tránh cắt nhầm."""
    out = s
    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(f"<{k}>", str(mapping[k]))
    return out


# Đề bài — bám sát hình mẫu (Câu 21): chiều dài HG, chiều rộng FG, bốn đường tròn, câu hỏi làm tròn.
TEMPLATE_QUESTION = r"""Trên một mảnh đất hình chữ nhật có chiều dài $HG = <HG>$ m, chiều rộng $FG = <FG>$ m, người ta xây một hồ bơi là phần diện tích giới hạn bởi bốn đường tròn $(C_1)$, $(C_2)$, $(C_3)$, $(C_4)$ như hình vẽ. Biết rằng đường tròn $(C_1)$ có đường kính $AB = <AB>$ m và tâm là điểm $I$, khoảng cách từ điểm $I$ đến hai cạnh $HG$ và $HE$ cùng bằng $<dist_I>$ m. Đường tròn $(C_2)$ có đường kính $CD = <CD>$ m và tâm là điểm $K$ với khoảng cách từ $K$ đến cạnh $FG$ bằng $<dist_K_FG>$ m và khoảng cách từ $K$ đến cạnh $EF$ bằng $<dist_K_EF>$ m. Đường tròn $(C_3)$ đi qua hai điểm $A$, $C$ và tiếp xúc với cạnh $EF$. Đường tròn $(C_4)$ đi qua hai điểm $B$, $D$ và có bán kính bằng $\sqrt{<R4SQ>}$ m. Hãy tính diện tích của hồ bơi như hình vẽ theo đơn vị $m^2$. (Nếu ra số gần đúng thì làm tròn kết quả đến hàng đơn vị).

\begin{center}
<tikz_question>
\end{center}
"""


TEMPLATE_SOLUTION = r"""Diện tích nửa đường tròn $(C_1)$ là $S_1 = <S1_pi>$.
Diện tích nửa đường tròn $(C_2)$ là $S_2 = <S2_pi>$.

\begin{center}
<tikz_solution>
\end{center}

Chọn hệ trục tọa độ $Oxy$ sao cho gốc $O \equiv H$, trục $Ox$ trùng với tia $HG$, trục $Oy$ trùng với tia $HE$. Khi đó: $H(0;0)$, $G(<HG>;0)$, $F(<HG>;<FG>)$, $E(0;<FG>)$. Dựa vào giả thiết, ta xác định tọa độ các điểm:
Tâm $I(<xI>;<yI>)$, bán kính $R_1 = <R1>$. Điểm $A(<x1>;<yA>)$, $B(<x1>;0)$.
Tâm $K(<xK>;<yK>)$, bán kính $R_2 = <R2>$. Điểm $C(<x2>;<yA>)$, $D(<x2>;<yD>)$.

Diện tích hai nửa đường tròn bên ngoài: Phần diện tích giới hạn bởi cung tròn $(C_1)$ (phía trái $AB$) và $(C_2)$ (phía phải $CD$) là:
\[ S_{\text{ngoài}} = \dfrac{1}{2}\pi \cdot <R1>^2 + \dfrac{1}{2}\pi \cdot <R2>^2 = <S_ngoai_pi>. \]

Xác định phương trình cung tròn $(C_3)$: Gọi tâm $O_3(a;b)$. Vì $(C_3)$ đi qua $A(<x1>;<yA>)$, $C(<x2>;<yA>)$ và tiếp xúc với $EF : y = <FG>$ nên:
\[
\begin{cases}
(a-<x1>)^2 + (b-<yA>)^2 = R_3^2 \\
(a-<x2>)^2 + (b-<yA>)^2 = R_3^2 \\
|<FG> - b| = R_3
\end{cases}
\Rightarrow \begin{cases} a = <a3> \\ b = <b3> \\ R_3 = <R3>. \end{cases}
\]
Phương trình cung trên $(C_3)$ là: $f(x) = <b3> + \sqrt{<R3sq> - (x-<a3>)^2}$.

Xác định phương trình cung tròn $(C_4)$: Gọi tâm $O_4(m;n)$. Vì $(C_4)$ đi qua $B(<x1>;0)$, $D(<x2>;<yD>)$ và có bán kính $R_4 = \sqrt{<R4SQ>}$ nên:
\[
\begin{cases}
(m-<x1>)^2 + n^2 = <R4SQ> \\
(m-<x2>)^2 + (n-<yD>)^2 = <R4SQ>
\end{cases}
\Rightarrow \left[ \begin{array}{l} <branch_bad> \\ <branch_good> \end{array} \right.
\]
Phương trình cung trên $(C_4)$ là: $g(x) = <n4> + \sqrt{<R4SQ> - (x-<m4>)^2}$.

Tính tổng diện tích: Diện tích phần thân giữa giới hạn bởi $f(x)$ và $g(x)$ từ $x = <x1>$ đến $x = <x2>$ là:
\[ S_{\text{giữa}} = \int_{<x1>}^{<x2>} \bigl[f(x) - g(x)\bigr]\,dx. \]
Tổng diện tích hồ bơi là:
\[ S = <S_ngoai_pi> + \int_{<x1>}^{<x2>} \left[ <b_minus_n> + \sqrt{<R3sq> - (x-<a3>)^2} - \sqrt{<R4SQ> - (x-<m4>)^2} \right] dx \approx <answer> \text{ m}^2. \]
"""


def compute_o4_branches(
    x1: float, x2: float, y_d: float, r4_sq: int, m_good: float, n_good: float
) -> Tuple[str, str]:
    """Hai nghiệm (m,n) cho hệ tâm O_4; nhánh xấu (loại) và nhánh tốt (nhận)."""
    R = math.sqrt(r4_sq)
    dx = x2 - x1
    dy = y_d
    d_chord = math.hypot(dx, dy)
    mx = (x1 + x2) / 2
    my = y_d / 2
    u = (-dy / d_chord, dx / d_chord)
    half = d_chord / 2
    h_off = math.sqrt(max(0.0, R * R - half * half))
    c1 = (mx + h_off * u[0], my + h_off * u[1])
    c2 = (mx - h_off * u[0], my - h_off * u[1])
    tol = 1e-3
    if math.hypot(c1[0] - m_good, c1[1] - n_good) < tol:
        bad = c2
    else:
        bad = c1
    mb, nb = bad
    return (
        rf"m={pf(mb)};\ n={pf(nb)}\ \text{{(loại vì cung nằm dưới)}}",
        rf"m={pf(m_good)};\ n={pf(n_good)}\ \text{{(nhận)}}",
    )


class SwimmingPoolAreaQuestion:
    """Diện tích hồ bơi — tham số ngẫu nhiên (mỗi tham số trong tập 20 giá trị)."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.parameters: Dict[str, Any] = {}
        self.calculated_values: Dict[str, Any] = {}
        self.config = config or GeneratorConfig()

    def generate_parameters(self) -> Dict[str, Any]:
        return try_random_params()

    def calculate_values(self) -> Dict[str, Any]:
        g = self.parameters
        L, W, d1, d2 = g["L"], g["W"], g["d1"], g["d2"]
        x1, x2 = g["x1"], g["x2"]
        y_d = g["y_d"]
        r4_sq = g["r4_sq"]
        branch_bad, branch_good = compute_o4_branches(
            x1, x2, y_d, r4_sq, g["m4"], g["n4"]
        )
        R3sq_str = pf(g["R3"] ** 2)
        if abs(g["R3"] ** 2 - round(g["R3"] ** 2)) < 1e-6:
            R3sq_str = str(int(round(g["R3"] ** 2)))
        bmn = g["b3"] - g["n4"]
        b_minus_n = str(int(bmn)) if abs(bmn - round(bmn)) < 1e-9 else pf(bmn)
        s_ngoai_pi = format_s_ngoai_pi_latex(d1, d2)
        return {
            "answer": g["answer"],
            "area_approx": format_decimal_vn(g["total"], 2),
            "tikz_question": TIKZ_QUESTION_HARD.strip(),
            "tikz_solution": TIKZ_SOLUTION_HARD.strip(),
            "branch_bad": branch_bad,
            "branch_good": branch_good,
            "HG": L,
            "FG": W,
            "AB": d1,
            "CD": d2,
            "dist_I": int(g["R1"]) if abs(g["R1"] - round(g["R1"])) < 1e-9 else g["R1"],
            "dist_K_FG": int(g["R2"])
            if abs(g["R2"] - round(g["R2"])) < 1e-9
            else g["R2"],
            "dist_K_EF": g["dist_k_ef"],
            "R4SQ": r4_sq,
            "x1": pf(x1),
            "x2": pf(x2),
            "yA": int(d1) if d1 == int(d1) else pf(d1),
            "yD": pf(y_d),
            "xI": pf(x1),
            "yI": pf(g["R1"]),
            "xK": pf(x2),
            "yK": pf(W - g["dist_k_ef"]),
            "R1": pf(g["R1"]),
            "R2": pf(g["R2"]),
            "S1_pi": _simplify_pi_over_8(d1 * d1),
            "S2_pi": _simplify_pi_over_8(d2 * d2),
            "a3": pf(g["a3"]),
            "b3": pf(g["b3"]),
            "R3": pf(g["R3"]),
            "R3sq": R3sq_str,
            "m4": pf(g["m4"]),
            "n4": pf(g["n4"]),
            "S_ngoai_pi": s_ngoai_pi,
            "b_minus_n": b_minus_n,
        }

    def generate_question_text(self) -> str:
        c = self.calculated_values
        return _tpl(
            TEMPLATE_QUESTION,
            {
                "HG": c["HG"],
                "FG": c["FG"],
                "AB": c["AB"],
                "CD": c["CD"],
                "dist_I": c["dist_I"],
                "dist_K_FG": c["dist_K_FG"],
                "dist_K_EF": c["dist_K_EF"],
                "R4SQ": c["R4SQ"],
                "tikz_question": c["tikz_question"],
            },
        ).strip()

    def generate_solution(self) -> str:
        c = self.calculated_values
        return _tpl(
            TEMPLATE_SOLUTION,
            {
                "HG": c["HG"],
                "FG": c["FG"],
                "x1": c["x1"],
                "x2": c["x2"],
                "yA": c["yA"],
                "yD": c["yD"],
                "xI": c["xI"],
                "yI": c["yI"],
                "xK": c["xK"],
                "yK": c["yK"],
                "R1": c["R1"],
                "R2": c["R2"],
                "S1_pi": c["S1_pi"],
                "S2_pi": c["S2_pi"],
                "a3": c["a3"],
                "b3": c["b3"],
                "R3": c["R3"],
                "R3sq": c["R3sq"],
                "m4": c["m4"],
                "n4": c["n4"],
                "R4SQ": c["R4SQ"],
                "branch_bad": c["branch_bad"],
                "branch_good": c["branch_good"],
                "answer": c["answer"],
                "tikz_solution": c["tikz_solution"],
                "S_ngoai_pi": c["S_ngoai_pi"],
                "b_minus_n": c["b_minus_n"],
            },
        ).strip()

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        logging.info("Đang tạo câu hỏi %s", question_number)
        self.parameters = self.generate_parameters()
        self.calculated_values = self.calculate_values()

        question_text = self.generate_question_text()
        solution = self.generate_solution()
        answer = str(self.calculated_values["answer"])

        question_content = (
            f"\\begin{{ex}}%Câu {question_number}\n"
            f"{question_text}\n\n"
            f"\\shortans{{{answer}}}\n"
            f"\\loigiai{{\n{solution}\n}}\n"
            f"\\end{{ex}}\n"
        )
        return question_content, answer

    @staticmethod
    def create_latex_document(questions_data: List[Tuple[str, str]], title: str = "") -> str:
        questions_content = "\n\n".join(q for q, _ in questions_data)
        return (
            r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,fancyhdr}
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


# ==============================================================================
# MAIN
# ==============================================================================


def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        if seed is None:
            s = os.environ.get("OPT_SEED")
            seed = int(s) if s else None
        if seed is not None:
            random.seed(seed)
            logging.info("Sử dụng seed: %s", seed)

        questions_data: List[Tuple[str, str]] = []
        for i in range(num_questions):
            q = SwimmingPoolAreaQuestion(GeneratorConfig(seed=seed))
            content, ans = q.generate_question_only(i + 1)
            questions_data.append((content, ans))
            logging.info("  Câu %s: S ≈ %s m²", i + 1, ans)

        latex_content = SwimmingPoolAreaQuestion.create_latex_document(questions_data)
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "swimming_pool_area_questions.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_content)
        logging.info("Đã ghi file: %s", output_file)
        print(f"\nĐã tạo {num_questions} câu và lưu: {output_file}")
        print("\n=== ĐÁP ÁN ===")
        for i, (_, a) in enumerate(questions_data):
            print(f"Câu {i + 1}: S = {a} m²")
    except ValueError as e:
        print(f"Lỗi: {e}")
        print("Usage: python swimming_pool_area_questions.py <num_questions> [seed]")
        sys.exit(1)


if __name__ == "__main__":
    main()
