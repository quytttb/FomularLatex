"""
Đề đúng/sai: camera phạt nguội tại nút giao thông.

Format Azota (xem SAMPLE LATEX FILE/README.md và mẫu De_mau_azota_latex_v1.tex):
  \\choiceTFt
  {{* mệnh đề đúng}}
  {{mệnh đề sai (không dấu *)}}
  ...
Trong nội dung không lặp nhãn a), b), c), d) — ex_test đánh số cột TT.
"""
import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple


def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"


def fmt_dec(x, comma=True):
    """Format a number: int if whole, else 1-dp with comma."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = f"{x:.1f}"
    if comma:
        s = s.replace(".", ",")
    return s


# Pre-computed Pythagorean-compatible triples
def _build_od_dh_oh_triples():
    triples = []
    for od_10 in range(30, 100):
        od = od_10 / 10
        for dh_10 in range(10, od_10):
            dh = dh_10 / 10
            oh_sq = od * od - dh * dh
            if oh_sq <= 0:
                continue
            oh = math.sqrt(oh_sq)
            oh_r = round(oh * 10) / 10
            if abs(oh - oh_r) < 1e-9 and oh_r > 0:
                triples.append((od, dh, oh_r))
    return triples


_OD_DH_OH = _build_od_dh_oh_triples()


def _build_sa_sz_oa_triples():
    triples = []
    for sa in range(15, 40):
        for sz in range(8, sa):
            oa_sq = sa * sa - sz * sz
            oa = int(round(math.sqrt(oa_sq)))
            if oa * oa == oa_sq and oa > 0:
                triples.append((sa, sz, oa))
    return triples


_SA_SZ_OA = _build_sa_sz_oa_triples()


def get_nice_parameters(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)

    random.shuffle(_OD_DH_OH)
    random.shuffle(_SA_SZ_OA)

    for od, dh, oh in _OD_DH_OH:
        for sa, sz, oa in _SA_SZ_OA:
            ab_choices = list(range(8, 22, 2))
            random.shuffle(ab_choices)
            for ab in ab_choices:
                ak = ab / 2
                xa_sq = oa * oa - ak * ak
                if xa_sq <= 0:
                    continue
                xa = math.sqrt(xa_sq)
                xa_r = round(xa * 10) / 10
                if abs(xa - xa_r) > 1e-9 or xa_r <= 0:
                    continue

                da_x = xa_r - oh
                da_y = -ak + dh
                if da_x <= 0:
                    continue

                ym_candidates = []
                for ym_10 in range(int(-ak * 10) + 1, int(-dh * 10)):
                    ym_candidates.append(ym_10 / 10)
                if not ym_candidates:
                    continue

                ym = random.choice(ym_candidates)
                xm = random.choice([30, 35, 40, 45, 50, 55, 60])

                if abs(da_y) < 1e-12:
                    continue
                t_f = (ym - (-dh)) / da_y
                xf = oh + da_x * t_f
                xf_r = round(xf * 10) / 10

                me = xm - xa_r
                if me <= 0:
                    continue

                vc = random.choice([40, 45, 50, 55, 60])
                vc_ms = vc / 3.6
                t_me = me / vc_ms
                t_me_rounded = round(t_me, 1)

                # Ensure c) is wrong: t_ME_wrong must differ from t_ME_actual
                # by at least 0.05s so the error is clearly visible
                if abs(t_me - t_me_rounded) < 0.05:
                    t_me_wrong = round(t_me + random.choice([-0.2, 0.2]), 1)
                else:
                    t_me_wrong = t_me_rounded

                di = xa_r - oh
                ae_num = ak - abs(ym)
                ae_den = ak - dh
                if abs(ae_den) < 1e-12:
                    continue
                ef = di * ae_num / ae_den
                if ef <= 0:
                    continue

                td = random.choice([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2])
                v_limit = random.choice([40, 50, 60])

                vd_ms = ef / td
                vd_kmh = vd_ms * 3.6
                d_correct = vd_kmh > v_limit

                ef_frac = Fraction(ef).limit_denominator(1000)
                td_frac = Fraction(td).limit_denominator(10)
                vd_frac = ef_frac / td_frac
                vd_kmh_frac = vd_frac * Fraction(36, 10)

                return {
                    'Sz': sz, 'SA': sa, 'OD': od, 'AB': ab, 'CD': 2 * dh,
                    'OH': oh, 'DH': dh, 'AK': ak, 'x_A': xa_r, 'OA': oa,
                    'DA_x': round(da_x, 1), 'DA_y': round(da_y, 1),
                    'x_M': xm, 'y_M': ym, 'x_F': xf_r,
                    'v_c': vc, 'ME': round(me, 1),
                    't_ME_actual': round(t_me, 2), 't_ME_wrong': t_me_wrong,
                    'EF': round(ef, 2), 'EF_frac': ef_frac,
                    't_d': td, 't_d_frac': td_frac,
                    'v_d_frac': vd_frac, 'v_d_kmh_frac': vd_kmh_frac,
                    'v_d_kmh': round(vd_kmh, 2),
                    'v_limit': v_limit, 'd_correct': d_correct,
                    'DI': round(di, 1),
                    'AE_num': round(ae_num, 1), 'AE_den': round(ae_den, 1),
                }

    raise RuntimeError("Không tìm được bộ tham số phù hợp")


def generate_question(seed_val=None) -> Tuple[str, str, str]:
    p = get_nice_parameters(seed_val)

    Sz = p['Sz']; SA = p['SA']; OD = p['OD']; AB = p['AB']; CD = p['CD']
    OH = p['OH']; DH = p['DH']; AK = p['AK']; x_A = p['x_A']; OA = p['OA']
    DA_x = p['DA_x']; DA_y = p['DA_y']
    x_M = p['x_M']; y_M = p['y_M']; x_F = p['x_F']
    v_c = p['v_c']; ME = p['ME']
    t_ME_actual = p['t_ME_actual']; t_ME_wrong = p['t_ME_wrong']
    EF_frac = p['EF_frac']; t_d = p['t_d']
    v_d_frac = p['v_d_frac']; v_d_kmh_frac = p['v_d_kmh_frac']
    v_d_kmh = p['v_d_kmh']; v_limit = p['v_limit']; d_correct = p['d_correct']
    DI = p['DI']; AE_num = p['AE_num']; AE_den = p['AE_den']

    # Format helpers
    CD_s = fmt_dec(CD); DH_s = fmt_dec(DH); OH_s = fmt_dec(OH)
    x_A_s = fmt_dec(x_A); AK_s = fmt_dec(AK)
    DA_x_s = fmt_dec(abs(DA_x)); DA_y_s = fmt_dec(abs(DA_y))
    y_M_s = fmt_dec(y_M); ME_s = fmt_dec(ME); OD_s = fmt_dec(OD)
    t_ME_wrong_s = fmt_dec(t_ME_wrong); t_ME_actual_s = fmt_dec(t_ME_actual)
    t_d_s = fmt_dec(t_d); DI_s = fmt_dec(DI)
    AE_num_s = fmt_dec(AE_num); AE_den_s = fmt_dec(AE_den)
    x_F_s = fmt_dec(x_F)

    DA_y_sign = "+" if DA_y >= 0 else "-"

    EF_frac_s = format_frac_tex(EF_frac)
    v_d_frac_s = format_frac_tex(v_d_frac)
    v_d_kmh_frac_s = format_frac_tex(v_d_kmh_frac)
    v_d_kmh_s = f"{v_d_kmh:.2f}".replace(".", ",")

    tikz_a = r"""
\begin{center}
\begin{tikzpicture}[>=latex, line join=bevel, font=\large]
    \coordinate (O) at (0,0);
    \coordinate (H) at (3,0);
    \coordinate (K) at (6,0);
    \coordinate (C) at (3,1.5);
    \coordinate (D) at (3,-1.2);
    \coordinate (B) at (6,3);
    \coordinate (A) at (6,-2.4);

    \draw[->, thick] (-1,0) -- (8,0) node[above] {$x$};
    \draw[->, thick] (0,-3) -- (0,4) node[right] {$y$};

    \draw[thick] (C) -- (B);
    \draw[thick] (O) -- (D) -- (A);
    \draw[thick] (C) -- (D);
    \draw[thick] (B) -- (A);

    \fill (O) circle (1.5pt) node[above left] {$O$};
    \fill (H) circle (1.5pt) node[below left] {$H$};
    \fill (K) circle (1.5pt) node[below] {$K$};
    \fill (C) circle (1.5pt) node[above left] {$C$};
    \fill (D) circle (1.5pt) node[below left] {$D$};
    \fill (B) circle (1.5pt) node[above] {$B$};
    \fill (A) circle (1.5pt) node[below] {$A$};
\end{tikzpicture}
\end{center}"""

    y_M_abs_s = fmt_dec(abs(y_M))
    max_x = int(math.ceil(x_M + 5))
    min_y = -int(math.ceil(AK + 3))
    max_y = int(math.ceil(AK + 5))

    y_M_abs_dot = fmt_dec(abs(y_M), comma=False)
    OH_dot = fmt_dec(OH, comma=False)
    DH_dot = fmt_dec(DH, comma=False)
    x_A_dot = fmt_dec(x_A, comma=False)
    AK_dot = fmt_dec(AK, comma=False)
    x_F_dot = fmt_dec(x_F, comma=False)

    tikz_c = f"""\\begin{{center}}
\\begin{{tikzpicture}}[line join = round, line cap=round,>=stealth, font=\\footnotesize, yscale=1/2, xscale=1/5]
 
 % Trục
 \\draw[->] (-10,0)--(55,0) node[above]{{$x$}};
 \\draw[->] (0,-8)--(0,10) node[below right]{{$y$}};
 
 % Điểm
 \\path 
 (0,0) coordinate (O)
 (22,-7) coordinate (A)
 (22,0) coordinate (K)
 (22,7) coordinate (B)
 (50,-6) coordinate (M)
 (0,-4.8) coordinate (O1)
 (22,-4.8) coordinate (I)
 (22,-6) coordinate (F)
 
 (intersection of I--O1 and O--A) coordinate (D)
 ($(O)!(D)!(K)$) coordinate (H)
 ($2*(H)-(D)$) coordinate (C)
 ;
 
 % Hình chính
 \\draw (B)--(A)--(O);
 \\draw (K)--(B);
 \\draw (H)--(C);
 \\draw (C)--(B);
 \\draw (O)--(A) (D)--(H);
 
 % Nét đứt
 \\draw[dashed] (0,-4.8)--(22,-4.8);
 \\draw[dashed] (0,-6)--(50,-6);
 \\draw[dashed] (0,-7)--(22,-7);
 \\draw[dashed] (50,0)--(50,-6);
 
 % Điểm
 \\foreach \\p/\\pos in {{
  O/left,
  H/above left,
  K/below left,
  B/above,
  C/left,
  D/above right,
  I/right,
  F/right,
  A/below,
  M/right}}
 \\fill (\\p) circle (1.2pt) node[\\pos]{{$\\p$}};
 
 % Nhãn số
 \\node[above right] at (22,0) {{${x_A_s}$}};
 \\node[above] at (50,0) {{${x_M}$}};
 \\node[left] at (0,-4.8) {{$-{DH_s}$}};
 \\node[left] at (0,-6) {{$-{y_M_abs_s}$}};
 \\node[left] at (0,-7) {{$-{AK_s}$}};
 
\\end{{tikzpicture}}
\\end{{center}}"""

    tikz_code = r"""
\begin{center}
\begin{tikzpicture}[>=stealth, font=\footnotesize, line join=round, line cap=round,transform shape]
   \coordinate (O) at (0,0);
   \coordinate (S) at (0,3.5);
   \coordinate (D) at (-1.82, -0.8);
   \coordinate (C) at (1.18, -0.8);
   \coordinate (A) at (-4.0, -2.5);
   \coordinate (B) at (2.0, -2.5);
   \coordinate (X) at (-1.8, -4.5);
   \coordinate (Y) at (3.5, 0);
   \coordinate (Z) at (0, 4.5);
   \fill[yellow!90!orange, opacity=0.85] (A) -- (B) -- (C) -- (D) -- cycle;
   \draw[->, dashed, thick] (O) -- (X) node[right] {$x$};
   \draw[->, dashed, thick] (O) -- (Y) node[above] {$y$};
   \draw[->, dashed, thick] (O) -- (Z) node[left] {$z$};
   \draw[thick] (S) -- (A);
   \draw[thick] (S) -- (B);
   \draw[dashed, thick] (S) -- (C);
   \draw[dashed, thick] (S) -- (D);
   \draw[line width=3.5pt, blue!30!black, cap=round] (-3.8, 0) -- (-3.8, 3.5); 
   \draw[thick] (-3.8, 3.5) -- (S); 
   \fill[yellow!90!black, rounded corners=4pt] (-1.8, 3.35) rectangle (-1.0, 3.65);
   \fill (-1.6, 3.5) circle (1pt);
   \fill (-1.4, 3.5) circle (1pt);
   \fill (-1.2, 3.5) circle (1pt);
   \begin{scope}[shift={(-3.28,-4.2)}, rotate=-48, scale=0.7]
    \fill[yellow!95!orange, rounded corners=3pt, draw=black, thick] (-0.8, -1.6) rectangle (0.8, 1.6);
    \fill[black!80, rounded corners=1pt] (-0.6, 0.6) rectangle (0.6, 1.1);
    \fill[black!80, rounded corners=1pt] (-0.6, -1.3) rectangle (0.6, -0.8);
    \fill[black!70, rounded corners=2pt] (-0.65, -0.6) rectangle (0.65, 0.4);
    \fill[red!80, rounded corners=0.5pt] (-0.7, 1.5) rectangle (-0.4, 1.6);
    \fill[red!80, rounded corners=0.5pt] (0.4, 1.5) rectangle (0.7, 1.6);
   \end{scope}
   \fill (O) circle (1.5pt) node[above right] {$O$};
   \fill (S) circle (1.5pt) node[right, yshift=2pt] {$S$};
   \fill (A) circle (1.5pt) node[left] {$A$};
   \fill (B) circle (1.5pt) node[right] {$B$};
   \fill (C) circle (1.5pt) node[right] {$C$};
   \fill (D) circle (1.5pt) node[left] {$D$};
   \begin{scope}[xshift=-0.75cm,yshift=3.7cm,scale=0.25]
    \filldraw[gray!60] (2.8,-0.6) rectangle (3.0,0.6);
    \filldraw[gray!55]
    (3.0, 0.4) -- (1.8, 0.4)
    to[out=180, in=90] (1.0, -0.4)
    to[out=270, in=180] (1.4, -0.8)
    -- (3.0, -0.8) -- cycle;
    \filldraw[gray!50] (0.6,-1.2) arc(180:270:0.5) -- ($(1.1,-1.2)+(-60:1.1)$) arc(-60:180:1.1) -- cycle;
    \begin{scope}[shift={(1.1,-1.2)}, rotate=20]
     \fill[black!80] (0,-0.3) circle (0.55);
     \draw[gray!60, thick] (0,-0.3) circle (0.3);
     \draw[gray!40] (0,-0.3) circle (0.15);
     \foreach \a in {0,60,...,300} \fill[black!90] ($(0,-0.3)+(\a:0.5)$) circle (1.5pt);
    \end{scope}
   \end{scope}
\end{tikzpicture}
\end{center}"""

    stem = f'''Tại một nút giao thông của một khu vực đông dân cư với tốc độ tối đa cho phép đối với ô tô là ${v_limit}$ (km/h), người ta gắn một camera phạt nguội tại điểm $S(0;0;{Sz})$ trong không gian $Oxyz$ (đơn vị trên mỗi trục tọa độ là mét), mặt phẳng $Oxy$ song song với mặt đường và chứa vùng nhận diện biển số xe của các phương tiện tham gia giao thông.{tikz_code}
Biết rằng camera nhận diện tốt nhất biển số xe của các phương tiện tham gia giao thông là khi biển số của chúng nằm trong hình thang cân $ABCD$ với: $SA=SB={SA}$ mét, $OD=OC={OD_s}$ mét, $AB={AB}$ mét và $CD={CD_s}$ mét. Tia $Ox$ nằm trên đường trung trực các đoạn thẳng $AB$ và $CD$ (xem hình vẽ minh họa). Giả sử tại thời điểm $9 \\mathrm{{h}} 00$ (được xem là thời điểm xuất phát) một ô tô chuyển động thẳng đều theo phương song song với trục $Ox$, hướng về phía trục $Oy$ và có vị trí của biển số xe là $M({x_M}; {y_M_s}; 0)$.'''

    is_a_correct = random.choice([True, False])
    is_b_correct = random.choice([True, False])
    is_c_correct = random.choice([True, False])
    is_d_correct = random.choice([True, False])

    wrong_y_D_s = f"{DH_s}"
    if is_a_correct:
        stmt_a_text = f"$D({OH_s}; -{DH_s}; 0)$."
        stmt_a = f"*a) {stmt_a_text}"
    else:
        stmt_a_text = f"$D({OH_s}; {wrong_y_D_s}; 0)$."
        stmt_a = f"a) {stmt_a_text}"

    if is_b_correct:
        stmt_b_text = f"Đường thẳng $AD$ có phương trình là $\\begin{{cases}} x = {OH_s} + {DA_x_s}t \\\\ y = -{DH_s} {DA_y_sign} {DA_y_s}t ,\\ (t \\in \\mathbb{{R}}) \\\\ z = 0 \\end{{cases}}$."
        stmt_b = f"*b) {stmt_b_text}"
    else:
        wrong_DA_y_sign = "-" if DA_y_sign == "+" else "+"
        stmt_b_text = f"Đường thẳng $AD$ có phương trình là $\\begin{{cases}} x = {OH_s} + {DA_x_s}t \\\\ y = -{DH_s} {wrong_DA_y_sign} {DA_y_s}t ,\\ (t \\in \\mathbb{{R}}) \\\\ z = 0 \\end{{cases}}$."
        stmt_b = f"b) {stmt_b_text}"

    if is_c_correct:
        stmt_c_text = f"Nếu ô tô đi với vận tốc ${v_c}$ (km/h) thì sau đúng ${t_ME_actual_s}$ giây kể từ thời điểm xuất phát thì biển số của xe ôtô đã nằm trong vùng nhận diện tốt nhất của camera."
        stmt_c = f"*c) {stmt_c_text}"
    else:
        stmt_c_text = f"Nếu ô tô đi với vận tốc ${v_c}$ (km/h) thì sau đúng ${t_ME_wrong_s}$ giây kể từ thời điểm xuất phát thì biển số của xe ôtô đã nằm trong vùng nhận diện tốt nhất của camera."
        stmt_c = f"c) {stmt_c_text}"

    if d_correct:
        if is_d_correct:
            stmt_d_text = f"Nếu camera ghi nhận được hình ảnh biển số xe ô tô liên tục trong một khoảng thời gian kéo dài đúng ${t_d_s}$ giây, và khoảng thời gian ${t_d_s}$ giây này kết thúc đồng thời với thời điểm xe vừa ra khỏi vùng nhận diện tốt nhất, thì ôtô đã vượt quá tốc độ cho phép."
            stmt_d = f"*d) {stmt_d_text}"
        else:
            stmt_d_text = f"Nếu camera ghi nhận được hình ảnh biển số xe ô tô liên tục trong một khoảng thời gian kéo dài đúng ${t_d_s}$ giây, và khoảng thời gian ${t_d_s}$ giây này kết thúc đồng thời với thời điểm xe vừa ra khỏi vùng nhận diện tốt nhất, thì ôtô không vượt quá tốc độ cho phép."
            stmt_d = f"d) {stmt_d_text}"
    else:
        if is_d_correct:
            stmt_d_text = f"Nếu camera ghi nhận được hình ảnh biển số xe ô tô liên tục trong một khoảng thời gian kéo dài đúng ${t_d_s}$ giây, và khoảng thời gian ${t_d_s}$ giây này kết thúc đồng thời với thời điểm xe vừa ra khỏi vùng nhận diện tốt nhất, thì ôtô không vượt quá tốc độ cho phép."
            stmt_d = f"*d) {stmt_d_text}"
        else:
            stmt_d_text = f"Nếu camera ghi nhận được hình ảnh biển số xe ô tô liên tục trong một khoảng thời gian kéo dài đúng ${t_d_s}$ giây, và khoảng thời gian ${t_d_s}$ giây này kết thúc đồng thời với thời điểm xe vừa ra khỏi vùng nhận diện tốt nhất, thì ôtô đã vượt quá tốc độ cho phép."
            stmt_d = f"d) {stmt_d_text}"

    solution = f'''a) Xét $(Oxy)$, gọi $H$ là trung điểm $CD$, ta có $CD={CD_s} \\Rightarrow DH={DH_s} \\Rightarrow y_D=-{DH_s}$

{tikz_a}

Tam giác $DOH$ vuông tại $H$ nên $OH = \\sqrt{{OD^2 - DH^2}} = \\sqrt{{{OD_s}^2 - {DH_s}^2}} = {OH_s} \\Rightarrow x_D = {OH_s}$

Vậy $D({OH_s}; -{DH_s}; 0)$ nên mệnh đề a) {'đúng' if is_a_correct else 'sai'}.

b) Do $AB={AB} \\Rightarrow AK={AK_s} \\Rightarrow A(x_A; -{AK_s}; 0),\\ (x_A > 0)$ mà $\\Delta SOA$ vuông tại $O$ nên ta có:
$$ OA^2 + SO^2 = SA^2 \\Leftrightarrow OA^2 = {SA}^2 - {Sz}^2 = {OA**2} \\Rightarrow OA = {OA} $$
$$ x_A^2 + {AK_s}^2 = {OA}^2 \\Leftrightarrow x_A = {x_A_s} \\Rightarrow A({x_A_s}; -{AK_s}; 0) \\Rightarrow \\overrightarrow{{DA}} = ({DA_x_s}; {DA_y_sign}{DA_y_s}; 0) $$
Vậy đường thẳng $AD$: $\\begin{{cases}} D({OH_s}; -{DH_s}; 0) \\\\ \\vec{{u}}_{{AD}} = \\overrightarrow{{DA}} = ({DA_x_s}; {DA_y_sign}{DA_y_s}; 0) \\end{{cases}}$ có phương trình $\\begin{{cases}} x = {OH_s} + {DA_x_s}t \\\\ y = -{DH_s} {DA_y_sign} {DA_y_s}t ,\\ (t \\in \\mathbb{{R}}) \\\\ z = 0 \\end{{cases}}$

nên mệnh đề b) {'đúng' if is_b_correct else 'sai'}.

c) Biển số của xe ôtô bắt đầu nằm trong vùng nhận diện tốt nhất của camera khi ô tô đi qua hình thang cân $ABCD$ tạo hai giao điểm $E$ (thuộc đoạn $AB$) và $F$ (thuộc đoạn $AD$) như hình vẽ.

{tikz_c}

Khoảng cách từ điểm xuất phát đến vùng nhận diện (đoạn $ME$) là: $ME = {x_M} - {x_A_s} = {ME_s}$ (m).

Thời gian từ $M$ đến $E$ là $t_{{M \\to E}} = \\dfrac{{ME}}{{v_{{\\text{{ô tô}}}}}} = \\dfrac{{{ME_s}}}{{\\dfrac{{{v_c}}}{{3,6}}}} = {t_ME_actual_s}$ (giây) nên mệnh đề c) {'đúng' if is_c_correct else 'sai'}.

d) Áp dụng định lý Talet trong tam giác $ADI$:
$\\dfrac{{EF}}{{DI}} = \\dfrac{{AE}}{{AI}} = \\dfrac{{{AK_s} - {fmt_dec(abs(y_M))}}}{{{AK_s} - {DH_s}}} = \\dfrac{{{AE_num_s}}}{{{AE_den_s}}} \\Rightarrow EF = DI \\cdot \\dfrac{{{AE_num_s}}}{{{AE_den_s}}} = \\dfrac{{{DI_s} \\cdot {AE_num_s}}}{{{AE_den_s}}} = {EF_frac_s}$

Suy ra $v = \\dfrac{{s}}{{t}} = \\dfrac{{EF}}{{t}} = \\dfrac{{{EF_frac_s}}}{{{t_d_s}}} = {v_d_frac_s} \\text{{ (m/s)}} = {v_d_kmh_frac_s} \\text{{ (km/h)}} \\approx {v_d_kmh_s} \\text{{ (km/h)}}'''

    if d_correct:
        solution += f''' > {v_limit} \\text{{ (km/h)}}$

Vậy xe đã vượt quá tốc độ cho phép nên mệnh đề d) {'đúng' if is_d_correct else 'sai'}.

Vậy a) {'đúng' if is_a_correct else 'sai'}; b) {'đúng' if is_b_correct else 'sai'}; c) {'đúng' if is_c_correct else 'sai'} và d) {'đúng' if is_d_correct else 'sai'}.'''
    else:
        solution += f''' < {v_limit} \\text{{ (km/h)}}$

Vậy xe không vượt quá tốc độ cho phép nên mệnh đề d) {'đúng' if is_d_correct else 'sai'}.

Vậy a) {'đúng' if is_a_correct else 'sai'}; b) {'đúng' if is_b_correct else 'sai'}; c) {'đúng' if is_c_correct else 'sai'} và d) {'đúng' if is_d_correct else 'sai'}.'''

    key_list = []
    key_list.append("Đ" if is_a_correct else "S")
    key_list.append("Đ" if is_b_correct else "S")
    key_list.append("Đ" if is_c_correct else "S")
    key_list.append("Đ" if is_d_correct else "S")
    key = ", ".join(key_list)

    question = f"""{stem}

{stmt_a}

{stmt_b}

{stmt_c}

{stmt_d}"""

    return question, solution, key


def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    seed = None
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])

    content = ""
    keys = []

    for i in range(num_questions):
        q, s, k = generate_question(seed + i if seed is not None else None)
        keys.append(k)
        content += f"\\begin{{ex}}%Câu {i+1}\n{q}\n\n\\loigiai{{\n{s}\n}}\n\\end{{ex}}\n\n"

    tex_content = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb,fancyhdr,longtable}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
% \\setmainfont{{Times New Roman}}
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
    output_file = os.path.join(out_dir, "traffic_camera_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
