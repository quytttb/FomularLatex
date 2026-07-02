import os
import random
import sys
import sympy as sp
from typing import Tuple


def format_angle(a, b):
    res = ""
    if a == 1:
        res += "x"
    elif a == -1:
        res += "-x"
    else:
        res += f"{a}x"

    if b != 0:
        if b > 0:
            res += " + " + sp.latex(b)
        else:
            res += " - " + sp.latex(-b)
    return res


def generate_question(seed=None) -> Tuple[str, str, str]:
    if seed is not None:
        random.seed(seed)

    x = sp.Symbol("x")

    A_VALUES = [1, 2, 3]
    B_VALUES = [
        sp.pi / 6,
        sp.pi / 4,
        sp.pi / 3,
        sp.pi / 2,
        2 * sp.pi / 3,
        3 * sp.pi / 4,
        5 * sp.pi / 6,
        sp.pi,
        -sp.pi / 6,
        -sp.pi / 4,
        -sp.pi / 3,
        -sp.pi / 2,
        -2 * sp.pi / 3,
        -3 * sp.pi / 4,
        -5 * sp.pi / 6,
    ]

    while True:
        a = random.choice(A_VALUES)
        b = random.choice(B_VALUES)
        c = random.choice(B_VALUES)

        if b == c:
            continue

        C1 = sp.cos(b) + sp.sin(c)
        C2 = sp.sin(b) - sp.cos(c)

        R_sq = C1**2 + C2**2
        if float(R_sq) < 1e-6:
            continue

        C1 = C1.simplify()
        C2 = C2.simplify()

        if C1 == 0:
            V = sp.pi / 2
        else:
            V = sp.atan(-C2 / C1).simplify()

        if C2 == 0:
            W = sp.pi / 2
        else:
            W = sp.atan(C1 / C2).simplify()

        if V.has(sp.atan) or W.has(sp.atan):
            continue

        break

    def get_root(k):
        return (V + k * sp.pi) / a

    def get_extremum(m):
        return (W + m * sp.pi) / a

    def is_max(m):
        val = (
            C1 * sp.sin(a * get_extremum(m)) + C2 * sp.cos(a * get_extremum(m))
        ).simplify()
        return float(val) > 0

    def is_min(m):
        val = (
            C1 * sp.sin(a * get_extremum(m)) + C2 * sp.cos(a * get_extremum(m))
        ).simplify()
        return float(val) < 0

    # Statement a
    m_start = 0
    while get_extremum(m_start) <= 0 or not is_max(m_start):
        m_start += 1

    y_max = get_extremum(m_start)
    y_min = get_extremum(m_start + 1)

    a_correct = random.choice([True, False])
    if a_correct:
        u_a = y_max
        v_a = y_min
    else:
        u_a = y_min
        v_a = get_extremum(m_start + 2)

    stmt_a_text = (
        f"Hàm số nghịch biến trên $\\left({sp.latex(u_a)}; {sp.latex(v_a)}\\right)$"
    )

    # Statement b
    b_interval_choices = [(-sp.pi, sp.pi), (0, 2 * sp.pi), (-2 * sp.pi, 2 * sp.pi)]
    u_b, v_b = random.choice(b_interval_choices)

    pos_roots_b = []
    for k in range(-10, 10):
        root = get_root(k)
        if float(root) > 0 and float(root) > float(u_b) and float(root) < float(v_b):
            pos_roots_b.append(root)

    if not pos_roots_b:
        pos_roots_b = [get_root(1)]
        u_b, v_b = 0, 2 * sp.pi

    max_root_b = max(pos_roots_b, key=lambda v: float(v))

    b_correct = random.choice([True, False])
    if b_correct:
        ans_b = max_root_b
    else:
        if len(pos_roots_b) > 1:
            ans_b = min(pos_roots_b, key=lambda v: float(v))
        else:
            ans_b = max_root_b + sp.pi / a

    stmt_b_text = f"Nghiệm dương lớn nhất của phương trình $f(x) = 0$ trên khoảng $\\left({sp.latex(u_b)}; {sp.latex(v_b)}\\right)$ là ${sp.latex(ans_b)}$"

    # Statement c
    c_interval_choices = [
        (0, sp.pi / 6),
        (0, sp.pi / 4),
        (0, sp.pi / 3),
        (0, sp.pi / 2),
    ]
    u_c, v_c = random.choice(c_interval_choices)

    vals_c = [
        (C1 * sp.sin(a * u_c) + C2 * sp.cos(a * u_c)).simplify(),
        (C1 * sp.sin(a * v_c) + C2 * sp.cos(a * v_c)).simplify(),
    ]
    for m in range(-5, 5):
        ext = get_extremum(m)
        if float(ext) >= float(u_c) and float(ext) <= float(v_c):
            vals_c.append((C1 * sp.sin(a * ext) + C2 * sp.cos(a * ext)).simplify())

    min_val_c = min(vals_c, key=lambda v: float(v))
    max_val_c = max(vals_c, key=lambda v: float(v))

    c_correct = random.choice([True, False])
    if c_correct:
        ans_c = min_val_c
    else:
        if min_val_c != max_val_c:
            ans_c = max_val_c
        else:
            ans_c = min_val_c + 1

    stmt_c_text = f"Giá trị nhỏ nhất của $f(x)$ trên đoạn $\\left[{sp.latex(u_c)}; {sp.latex(v_c)}\\right]$ là ${sp.latex(ans_c)}$"

    # Statement d
    u_d = 0
    v_d = random.choice([5, 8, 10, 12, 15])

    max_count_d = 0
    for m in range(-20, 50):
        ext = get_extremum(m)
        if float(ext) > float(u_d) and float(ext) < float(v_d) and is_max(m):
            max_count_d += 1

    d_correct = random.choice([True, False])
    if d_correct:
        ans_d = max_count_d
    else:
        ans_d = max_count_d + random.choice([-1, 1])
        if ans_d < 0:
            ans_d = 1

    stmt_d_text = (
        f"Trong khoảng từ $({u_d}; {v_d})$ có {ans_d} lần hàm số đạt giá trị lớn nhất"
    )

    # Statement e
    u_e = random.choice([-5, -4, -3, -2])
    v_e = random.choice([3, 4, 5, 6, 8])

    max_count_e = 0
    for m in range(-20, 20):
        ext = get_extremum(m)
        if float(ext) > float(u_e) and float(ext) < float(v_e) and is_max(m):
            max_count_e += 1

    e_correct = random.choice([True, False])
    if e_correct:
        ans_e = max_count_e
    else:
        ans_e = max_count_e + random.choice([-1, 1])
        if ans_e < 0:
            ans_e = 1

    stmt_e_text = (
        f"Trong khoảng từ $({u_e}; {v_e})$ đồ thị hàm số có {ans_e} điểm cực đại"
    )

    # Statement f
    u_f = random.choice([-6, -5, -4, -3])
    v_f = random.choice([4, 5, 6, 7, 8])

    min_count_f = 0
    for m in range(-20, 20):
        ext = get_extremum(m)
        if float(ext) > float(u_f) and float(ext) < float(v_f) and is_min(m):
            min_count_f += 1

    f_correct = random.choice([True, False])
    if f_correct:
        ans_f = min_count_f
    else:
        ans_f = min_count_f + random.choice([-1, 1])
        if ans_f < 0:
            ans_f = 1

    stmt_f_text = (
        f"Trong khoảng từ $({u_f}; {v_f})$ đồ thị hàm số có {ans_f} điểm cực tiểu"
    )

    # Statement g
    u_g = 0
    v_g = random.choice([sp.Rational(3, 2), 2, sp.Rational(5, 2), 3])

    exts_g = []
    for m in range(-10, 20):
        ext = get_extremum(m)
        if float(ext) > float(u_g) and float(ext) < float(v_g):
            exts_g.append(ext)

    if not exts_g:
        v_g = 5
        for m in range(-10, 20):
            ext = get_extremum(m)
            if float(ext) > float(u_g) and float(ext) < float(v_g):
                exts_g.append(ext)

    max_ext_g = max(exts_g, key=lambda v: float(v))

    g_correct = random.choice([True, False])
    if g_correct:
        ans_g = float(max_ext_g)
    else:
        out_exts = []
        for m in range(-10, 20):
            ext = get_extremum(m)
            if float(ext) >= float(v_g):
                out_exts.append(ext)
        if out_exts:
            ans_g = float(min(out_exts, key=lambda v: float(v)))
        else:
            ans_g = float(max_ext_g) + float(sp.pi / a)

    ans_g_str = f"{ans_g:.5f}..."
    stmt_g_text = f"Nghiệm lớn nhất của phương trình $f'(x) = 0$ trên $\\left({sp.latex(u_g)}; {sp.latex(v_g)}\\right)$ xấp xỉ {ans_g_str}"

    pool = [
        (stmt_a_text, a_correct),
        (stmt_b_text, b_correct),
        (stmt_c_text, c_correct),
        (stmt_d_text, d_correct),
        (stmt_g_text, g_correct),
    ]

    if random.choice([True, False]):
        pool.append((stmt_e_text, e_correct))
    else:
        pool.append((stmt_f_text, f_correct))

    random.shuffle(pool)
    selected = pool[:4]

    labels = ["a", "b", "c", "d"]
    statements_str = []
    keys = []
    for i in range(4):
        stmt_text, is_corr = selected[i]
        prefix = "*" if is_corr else ""
        statements_str.append(f"{prefix}{labels[i]}) {stmt_text}")
        keys.append("Đ" if is_corr else "S")

    f_str = f"f(x) = \\sin\\left({format_angle(a, b)}\\right) - \\cos\\left({format_angle(a, c)}\\right)"

    question = f"Cho hàm số ${f_str}$.\n\nCác mệnh đề:\n" + "\n".join(statements_str)

    key_str = ", ".join(keys)
    return question, "", key_str


def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])

    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    keys = []

    for i in range(num_questions):
        seed = (seed_val + i) if seed_val is not None else None
        q, s, k = generate_question(seed=seed)
        keys.append(k)
        content += rf"Câu {i + 1}: {q}" + "\n\n"

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=2cm}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\usepackage{esvect}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    output_file = os.path.join(out_dir, "ham_so_luong_giac_dung_sai_questions.tex")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i + 1}: {k}")


if __name__ == "__main__":
    main()
