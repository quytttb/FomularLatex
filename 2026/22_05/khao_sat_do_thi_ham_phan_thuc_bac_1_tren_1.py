import math
import os
import sys
import random
from fractions import Fraction
from typing import Tuple

def format_equation(coeffs, terms):
    """Format polynomial equation from coeffs and terms."""
    res = ""
    for c, t in zip(coeffs, terms):
        if c == 0:
            continue
        if c == 1 and t != "":
            res += f" + {t}"
        elif c == -1 and t != "":
            res += f" - {t}"
        elif c > 0:
            res += f" + {c}{t}"
        else:
            res += f" - {abs(c)}{t}"
    
    if res.startswith(" + "):
        res = res[3:]
    elif res.startswith(" - "):
        res = "-" + res[3:]
    if res == "":
        return "0"
    return res

def fmt_x_minus_a(a):
    if a < 0:
        return f"x + {abs(a)}"
    elif a > 0:
        return f"x - {a}"
    return "x"

def fmt_frac(num, den):
    if num % den == 0:
        return str(num // den)
    if den < 0:
        num, den = -num, -den
    if num < 0:
        return rf"-\frac{{{abs(num)}}}{{{den}}}"
    return rf"\frac{{{num}}}{{{den}}}"

def fmt_num(n):
    if isinstance(n, Fraction):
        return fmt_frac(n.numerator, n.denominator)
    if isinstance(n, float):
        if n == int(n):
            return str(int(n))
        fr = Fraction(n).limit_denominator(100)
        return fmt_frac(fr.numerator, fr.denominator)
    return str(n)

def fmt_point(x, y):
    return f"({fmt_num(x)}; {fmt_num(y)})"

def fmt_x_plus_c(c):
    if c > 0:
        return f"x + {c}"
    if c < 0:
        return f"x - {abs(c)}"
    return "x"

def fmt_x_minus_c(c):
    if c > 0:
        return f"x - {c}"
    if c < 0:
        return f"x + {abs(c)}"
    return "x"

def fmt_paren_x_minus_c(c):
    if c > 0:
        return f"(x - {c})"
    if c < 0:
        return f"(x + {abs(c)})"
    return "(x)"

def fmt_const_minus_x(c):
    return f"({fmt_num(c)} - x)"

def fmt_sub_const(var, c):
    if c > 0:
        return f"{var} - {c}"
    if c < 0:
        return f"{var} + {abs(c)}"
    return var

def fmt_add_ints(*values):
    res = "x"
    for v in values:
        if v > 0:
            res += f" + {v}"
        elif v < 0:
            res += f" - {abs(v)}"
    return res

def fmt_x_shift_sq(c):
    if c > 0:
        return f"(x - {c})^2"
    if c < 0:
        return f"(x + {abs(c)})^2"
    return "x^2"

def fmt_y_shift_sq(c):
    if c > 0:
        return f"(y - {c})^2"
    if c < 0:
        return f"(y + {abs(c)})^2"
    return "y^2"

def fmt_tex_set(*items):
    inner = ", ".join(fmt_num(i) for i in items)
    return rf"\{{{inner}\}}"

def fmt_coef_var(coef, var="b"):
    if coef == 1:
        return var
    if coef == -1:
        return f"-{var}"
    return f"{coef}{var}"

def fmt_quad(b, c):
    parts = ["x^2"]
    if b > 0:
        parts.append(f" + {b}x")
    elif b < 0:
        parts.append(f" - {abs(b)}x")
    if c > 0:
        parts.append(f" + {c}")
    elif c < 0:
        parts.append(f" - {abs(c)}")
    return "".join(parts)

def format_rational_func(a, b, c, d):
    num = format_equation([a, b], ["x", ""])
    den = format_equation([c, d], ["x", ""])
    return rf"\frac{{{num}}}{{{den}}}"

def generate_stmt_a():
    # y = (ax+b)/(cx+d) = m + k/(x-x0)
    # A(xA, yA). M is midpoint of KA. M in px + qy + r = 0
    # Let's use p=1, q=1, so x + y + r = 0
    # M((x+xA)/2, (y+yA)/2) => x + y + xA + yA + 2r = 0
    # x + m + k/(x-x0) + xA + yA + 2r = 0
    # Let C = m + xA + yA + 2r.
    # x + C + k/(x-x0) = 0 => x^2 + (C-x0)x - C*x0 + k = 0
    # We want roots to be nice. Let roots be r1, r2.
    # r1 + r2 = x0 - C. r1 * r2 = -C*x0 + k.
    # Sum of abscissas = r1 + r2 = x0 - C.
    
    x0 = random.choice([-2, -1, 1, 2])
    m = random.choice([-2, -1, 1, 2])
    k = random.choice([-3, -2, -1, 1, 2, 3])
    
    # roots r1, r2
    r1 = random.choice([-3, -2, -1, 1, 2, 3])
    r2 = random.choice([-3, -2, -1, 1, 2, 3])
    if r1 == r2 or r1 == x0 or r2 == x0:
        r2 = r1 + 1
        if r2 == x0: r2 += 1
        if r1 == x0: r1 -= 1
        
    C = x0 - (r1 + r2)
    k = r1 * r2 + C * x0
    if k == 0:
        k = 1
        r1_plus_r2 = x0 - C
        # Just use sum = x0 - C
    
    a = m
    b = k - m*x0
    
    xA = random.choice([-2, -1, 0, 1, 2])
    yA = random.choice([-2, -1, 0, 1, 2])
    
    # C = m + xA + yA + 2r => 2r = C - m - xA - yA
    # To make r integer, C - m - xA - yA must be even
    if (C - m - xA - yA) % 2 != 0:
        yA += 1
        
    r = (C - m - xA - yA) // 2
    
    func_str = format_rational_func(a, b, 1, -x0)
    line_str = format_equation([1, 1, r], ["x", "y", ""]) + " = 0"
    
    sum_x = x0 - C
    
    is_correct = random.choice([True, False])
    sum_val = sum_x if is_correct else sum_x + random.choice([-2, -1, 1, 2])
    
    stmt = rf"Cho hàm số \(y = {func_str}\) có đồ thị \((C_1)\) và điểm \(A{fmt_point(xA, yA)}\). Gọi \(S\) là tập hợp các điểm \(K \in (C_1)\) sao cho trung điểm đoạn \(KA\) nằm trên đường thẳng \(d_1: {line_str}\). Tổng các hoành độ của các điểm thuộc \(S\) bằng \({sum_val}\)."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    quad_b = C - x0
    quad_c = -C * x0 + k
    
    sol = rf"""+) {sol_correct_str}.

Gọi \(K(x; {m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}) \in (C_1)\) (với \(x \neq {x0}\)).
Trung điểm \(M\) của đoạn \(KA\) có tọa độ:
\(x_M = \frac{{{fmt_x_plus_c(xA)}}}{{2}}\)
\(y_M = \frac{{{m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} {'+' if yA >= 0 else '-'} {abs(yA)}}}{{2}}\)
Vì \(M \in d_1: {line_str}\) nên:
\(\frac{{{fmt_x_plus_c(xA)}}}{{2}} + \frac{{{m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} {'+' if yA >= 0 else '-'} {abs(yA)}}}{{2}} {'+' if r > 0 else '-'} {abs(r) if r != 0 else ''} = 0\)
\(\Leftrightarrow {fmt_add_ints(xA, m + yA + 2*r)} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} = 0\)
\(\Leftrightarrow {fmt_x_plus_c(C)} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} = 0\)
\(\Leftrightarrow ({fmt_x_plus_c(C)})({fmt_x_minus_a(x0)}) {'+' if k > 0 else '-'} {abs(k)} = 0\)
\(\Leftrightarrow {fmt_quad(quad_b, quad_c)} = 0\)
Phương trình bậc hai này có \(\Delta = ({quad_b})^2 - 4({quad_c}) = {(C-x0)**2 - 4*(-C*x0+k)}\).
Kiểm tra thấy \(\Delta > 0\) và \(x = {x0}\) không là nghiệm, nên phương trình luôn có 2 nghiệm phân biệt \(x_1, x_2\).
Theo định lý Vi-ét, tổng các hoành độ là \(x_1 + x_2 = {sum_x}\).
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_stmt_b():
    # y = m + k/(x-x0)
    # G in px + qy + r = 0. Let p=1, q=-1 => x - y + r = 0
    # G((x+xA+xB)/3, (y+yA+yB)/3)
    # x + xA + xB - (y + yA + yB) + 3r = 0
    # x - y + xA + xB - yA - yB + 3r = 0
    # x - m - k/(x-x0) + C = 0 => x^2 + (C-m-x0)x - (C-m)x0 - k = 0
    
    is_correct = random.choice([True, False])
    # If correct, we want exactly 2 points => delta > 0
    # If false, we want 0 points => delta < 0, or 1 point => delta = 0
    
    B_PARAMS = [
        # (x0, m, k, C_minus_m, xA, xB, yA, yB) — delta > 0
        (1, 1, 2, 0, 0, 1, 1, 0),
        (-1, 2, -2, 1, 1, -1, 0, 1),
        (2, -1, 1, -1, -1, 2, 1, -1),
        # delta <= 0
        (1, 1, -3, -4, 0, 0, 0, 0),
        (-2, 2, 3, -5, 1, 1, 1, 1),
    ]
    if is_correct:
        pool = [p for p in B_PARAMS[:3]]
    else:
        pool = [p for p in B_PARAMS[3:]]
    x0, m, k, C_minus_m, xA, xB, yA, yB = random.choice(pool)
    delta = (C_minus_m - x0)**2 + 4 * ((C_minus_m) * x0 + k)
    C = C_minus_m + m
    
    # C = xA + xB - yA - yB + 3r => 3r = C - xA - xB + yA + yB
    for _ in range(6):
        if (C - xA - xB + yA + yB) % 3 == 0:
            break
        yA += 1
        
    r = (C - xA - xB + yA + yB) // 3
    
    a = m
    b = k - m*x0
    func_str = format_rational_func(a, b, 1, -x0)
    line_str = format_equation([1, -1, r], ["x", "y", ""]) + " = 0"
    
    num_pts = 2 if is_correct else (0 if delta < 0 else 1)
    stmt_pts = 2
    
    stmt = rf"Cho hàm số \(y = {func_str}\) có đồ thị \((C_2)\) và hai điểm \(A{fmt_point(xA, yA)}, B{fmt_point(xB, yB)}\). Có đúng {stmt_pts} điểm \(K \in (C_2)\) phân biệt sao cho trọng tâm tam giác \(KAB\) thuộc đường thẳng \(d_2: {line_str}\)."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    qb = C - m - x0
    qc = -(C - m) * x0 - k
    
    sol = rf"""+) {sol_correct_str}.

Gọi \(K(x; {m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}) \in (C_2)\) (với \(x \neq {x0}\)).
Trọng tâm \(G\) của tam giác \(KAB\) có tọa độ:
\(x_G = \frac{{{fmt_x_plus_c(xA + xB)}}}{{3}}\)
\(y_G = \frac{{{m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} {'+' if yA + yB >= 0 else '-'} {abs(yA + yB)}}}{{3}}\)
Vì \(G \in d_2: {line_str}\) nên:
\(\frac{{{fmt_x_plus_c(xA + xB)}}}{{3}} - \frac{{{m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} {'+' if yA + yB >= 0 else '-'} {abs(yA + yB)}}}{{3}} {'+' if r > 0 else '-'} {abs(r) if r != 0 else ''} = 0\)
\(\Leftrightarrow {fmt_add_ints(xA + xB)} - ({m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}) {'+' if yA + yB >= 0 else '-'} {abs(yA + yB)}) {'+' if 3*r > 0 else '-'} {abs(3*r) if r != 0 else ''} = 0\)
\(\Leftrightarrow {fmt_x_plus_c(C - m)} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} = 0\)
\(\Leftrightarrow ({fmt_x_plus_c(C - m)})({fmt_x_minus_a(x0)}) {'+' if k > 0 else '-'} {abs(k)} = 0\)
\(\Leftrightarrow {fmt_quad(qb, qc)} = 0\)
Phương trình bậc hai này có \(\Delta = ({qb})^2 - 4({qc}) = {delta}\).
Vì \(\Delta {'> 0' if delta > 0 else '< 0' if delta < 0 else '= 0'}\) nên phương trình có {'2 nghiệm phân biệt' if delta > 0 else 'vô nghiệm' if delta < 0 else 'nghiệm kép'}.
Vậy có đúng {num_pts} điểm \(K\) thỏa mãn.
Mệnh đề này là {sol_correct_str.lower()}."""

    return stmt, sol, is_correct

def generate_stmt_c():
    # y = m + k/(x-x0)
    # A(xA, y0), B(xB, y0) -> horizontal line AB
    # H(x, yH) in x + y + r = 0
    # yH = y0 + (x-xA)(xB-x) / (yK - y0)
    # yK = m + k/(x-x0)
    # yH = y0 + (x-xA)(xB-x)(x-x0) / (m(x-x0) + k - y0(x-x0))
    # Let y0 = m. Then yK - y0 = k/(x-x0)
    # yH = m + (x-xA)(xB-x)(x-x0) / k
    # H in x + y + r = 0 => x + m + (x-xA)(xB-x)(x-x0)/k + r = 0
    # k(x+m+r) + (x-xA)(xB-x)(x-x0) = 0
    # (x-xA)(x-xB)(x-x0) - kx - k(m+r) = 0
    # x^3 - (xA+xB+x0)x^2 + (xA xB + xA x0 + xB x0)x - xA xB x0 - kx - k(m+r) = 0
    # We want this cubic to have a nice root, say x=0.
    # If x=0 is a root: -xA xB x0 - k(m+r) = 0 => k(m+r) = -xA xB x0
    
    xA = random.choice([-3, -2, -1, 1, 2, 3])
    xB = random.choice([-3, -2, -1, 1, 2, 3])
    if xA == xB: xB += 1
    x0 = random.choice([-2, -1, 1, 2])
    
    k = random.choice([-2, -1, 1, 2])
    m_plus_r = -xA * xB * x0 // k
    if -xA * xB * x0 % k != 0:
        # adjust k to divide xA*xB*x0
        k = 1
        m_plus_r = -xA * xB * x0
        
    m = random.choice([-2, -1, 1, 2])
    r = m_plus_r - m
    y0 = m
    
    a = m
    b = k - m*x0
    func_str = format_rational_func(a, b, 1, -x0)
    line_str = format_equation([1, 1, r], ["x", "y", ""]) + " = 0"
    
    # Root is x=0. yK = m + k/(-x0)
    yK_val = m - k/x0
    
    is_correct = random.choice([True, False])
    
    # Let's ask about a specific value, e.g. x0 * b = ...
    # Wait, the statement says: "Tồn tại một điểm K(a, b) ... hoành độ dương ... giá trị 5b = 9"
    # Actually, the root x=0 is NOT positive.
    # Let's make the root x_root > 0.
    x_root = random.choice([1, 2, 3, 4])
    if x_root == x0 or x_root == xA or x_root == xB:
        x_root += 1
        if x_root == x0: x_root += 1
        
    # (x_root-xA)(x_root-xB)(x_root-x0) - k*x_root - k(m+r) = 0
    # k(m+r) = (x_root-xA)(x_root-xB)(x_root-x0) - k*x_root
    val = (x_root-xA)*(x_root-xB)*(x_root-x0) - k*x_root
    if val % k != 0:
        k = 1
        val = (x_root-xA)*(x_root-xB)*(x_root-x0) - k*x_root
        
    m_plus_r = val // k
    r = m_plus_r - m
    
    line_str = format_equation([1, 1, r], ["x", "y", ""]) + " = 0"
    
    yK_val = m + k/(x_root - x0)
    yK_frac = Fraction(m*(x_root-x0) + k, x_root-x0)
    
    # We ask for denominator * b = numerator
    den = yK_frac.denominator
    num = yK_frac.numerator
    
    b_val = num if is_correct else num + random.choice([-2, 2, 1])
    
    stmt = rf"Cho hàm số \(y = {func_str}\) có đồ thị \((C_3)\) và hai điểm \(A{fmt_point(xA, y0)}, B{fmt_point(xB, y0)}\). Tồn tại một điểm \(K(a; b) \in (C_3)\) với hoành độ \(a = {x_root}\) sao cho trực tâm \(H\) của tam giác \(KAB\) nằm trên đường thẳng \(d_3: {line_str}\). Khi đó, giá trị \({fmt_coef_var(den, 'b')} = {b_val}\)."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    sol = rf"""+) {sol_correct_str}.

Ta thấy \(y_A = y_B = {y0}\), nên đường thẳng \(AB\) nằm ngang có phương trình \(y = {y0}\).
Gọi \(K(x; {m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}) \in (C_3)\).
Trực tâm \(H(x_H; y_H)\) của tam giác \(KAB\):
Vì \(AB\) nằm ngang nên đường cao từ \(K\) là đường thẳng đứng \(x = x_K = x\), suy ra \(x_H = x\).
Đường cao từ \(A\) vuông góc với \(KB\). Ta có \(\overrightarrow{{KB}} = {fmt_const_minus_x(xB)}; {fmt_num(y0)} - y_K)\), \(\overrightarrow{{AH}} = {fmt_paren_x_minus_c(xA)}; {fmt_sub_const('y_H', y0)})\).
\(\overrightarrow{{AH}} \cdot \overrightarrow{{KB}} = 0 \Leftrightarrow {fmt_paren_x_minus_c(xA)}{fmt_const_minus_x(xB)} + ({fmt_sub_const('y_H', y0)})({fmt_num(y0)} - y_K) = 0\)
\(\Rightarrow {fmt_sub_const('y_H', y0)} = \frac{{{fmt_paren_x_minus_c(xA)}{fmt_const_minus_x(xB)}}}{{{fmt_num(y0)} - ({m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}})}} = -\frac{{{fmt_paren_x_minus_c(xA)}{fmt_const_minus_x(xB)} \cdot ({fmt_x_minus_a(x0)})}}{{{k}}}\).
Suy ra \(y_H = {y0} - \frac{{{fmt_paren_x_minus_c(xA)}{fmt_const_minus_x(xB)} \cdot ({fmt_x_minus_a(x0)})}}{{{k}}}\).
Vì \(H \in d_3: {line_str}\) nên \(x_H + y_H {'+' if r > 0 else '-'} {abs(r) if r != 0 else ''} = 0\).
Thay \(x = {x_root}\) vào, ta thấy điều kiện thỏa mãn.
Vậy \(x = {x_root}\) là hoành độ của điểm \(K\).
Tung độ \(b = y_K = {fmt_frac(num, den)}\).
Suy ra \({fmt_coef_var(den, 'b')} = {num}\).
Mệnh đề này là {sol_correct_str.lower()}."""

    return stmt, sol, is_correct

def generate_stmt_d():
    # y = m + k/(x-x0)
    # Circumcenter I(xI, yI) on line px + qy + r = 0
    # Circle (x-xI)^2 + (y-yI)^2 = R^2
    # Let m = yI - xI.
    # Intersection: u^4 - R^2 u^2 + k^2 = 0 where u = x - xI
    # We want 4 integer points => u^2 = t1, t2 perfect squares
    t1 = random.choice([1, 4])
    t2 = random.choice([9, 16])
    
    R2 = t1 + t2
    k2 = t1 * t2
    k = int(math.sqrt(k2))
    if random.choice([True, False]): k = -k
    
    xI = random.choice([-1, 0, 1, 2])
    yI = random.choice([-1, 0, 1, 2])
    
    m = yI - xI
    x0 = xI
    
    # Pick A, B on the circle
    # (x-xI)^2 + (y-yI)^2 = R2
    # If R2 = 1+9=10, points are (+-1, +-3) or (+-3, +-1) relative to I
    # If R2 = 4+9=13, points are (+-2, +-3) or (+-3, +-2)
    # If R2 = 1+16=17, points are (+-1, +-4) or (+-4, +-1)
    # If R2 = 4+16=20, points are (+-2, +-4) or (+-4, +-2)
    
    if R2 == 10:
        dxA, dyA = 1, 3
        dxB, dyB = 3, -1
    elif R2 == 13:
        dxA, dyA = 2, 3
        dxB, dyB = 3, -2
    elif R2 == 17:
        dxA, dyA = 1, 4
        dxB, dyB = 4, -1
    elif R2 == 20:
        dxA, dyA = 2, 4
        dxB, dyB = 4, -2
        
    xA, yA = xI + dxA, yI + dyA
    xB, yB = xI + dxB, yI + dyB
    
    # Line d4 passing through I
    # Let's use x + 2y + r = 0 => r = -(xI + 2yI)
    r = -(xI + 2*yI)
    line_str = format_equation([1, 2, r], ["x", "y", ""]) + " = 0"
    
    a = m
    b = k - m*x0
    func_str = format_rational_func(a, b, 1, -x0)
    
    # Roots for u: +-sqrt(t1), +-sqrt(t2)
    # x = xI + u
    u_vals = [int(math.sqrt(t1)), -int(math.sqrt(t1)), int(math.sqrt(t2)), -int(math.sqrt(t2))]
    x_vals = [xI + u for u in u_vals]
    
    # Sum of squares of abscissas
    sum_sq = sum(x**2 for x in x_vals)
    
    is_correct = random.choice([True, False])
    sum_val = sum_sq if is_correct else sum_sq + random.choice([-4, 4, 2])
    
    u_list = [int(math.sqrt(t1)), -int(math.sqrt(t1)), int(math.sqrt(t2)), -int(math.sqrt(t2))]
    u_set = fmt_tex_set(*u_list)
    x_set = fmt_tex_set(*x_vals)
    sum_sq_terms = " + ".join(
        f"({fmt_num(x)})^2" if x < 0 else f"{fmt_num(x)}^2" for x in x_vals
    )
    half_b = R2 + 2 * k
    
    stmt = rf"Cho hàm số \(y = {func_str}\) có đồ thị \((C_4)\) và hai điểm \(A{fmt_point(xA, yA)}, B{fmt_point(xB, yB)}\). Có đúng 4 điểm \(K \in (C_4)\) có tọa độ nguyên sao cho tâm đường tròn ngoại tiếp tam giác \(KAB\) nằm trên đường thẳng \(d_4: {line_str}\). Tổng bình phương hoành độ của 4 điểm \(K\) đó bằng \({sum_val}\)."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    sol = rf"""+) {sol_correct_str}.

Gọi \(I\) là tâm đường tròn ngoại tiếp tam giác \(KAB\). \(I\) nằm trên đường trung trực của \(AB\).
Trung điểm \(M\) của \(AB\) là \(M{fmt_point((xA+xB)/2, (yA+yB)/2)}\), \(\overrightarrow{{AB}} = {fmt_point(xB-xA, yB-yA)}\).
Giải hệ phương trình gồm đường trung trực và \(d_4: {line_str}\), ta tìm được \(I{fmt_point(xI, yI)}\).
Bán kính đường tròn ngoại tiếp là \(R = IA = \sqrt{{{R2}}}\).
Phương trình đường tròn \((C): {fmt_x_shift_sq(xI)} + {fmt_y_shift_sq(yI)} = {R2}\).
Điểm \(K \in (C_4) \cap (C)\), ta có hệ:
\(\heva{{y &= {m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}} \\ {fmt_x_shift_sq(xI)} + {fmt_y_shift_sq(yI)} &= {R2}}}\)
Đặt \(u = {fmt_x_minus_c(xI)}\), thay \(y\) vào phương trình đường tròn và rút gọn:
\(2u^4 - {half_b}u^2 + {k**2} = 0 \Leftrightarrow u^4 - {fmt_frac(half_b, 2)}u^2 + {fmt_frac(k**2, 2)} = 0\).
Giải ra ta được \(u^2 = {t1}\) hoặc \(u^2 = {t2}\).
Suy ra \(u \in {u_set}\).
Hoành độ các điểm \(K\) là \(x = {fmt_num(xI)} + u \in {x_set}\).
Tổng bình phương hoành độ là: \({sum_sq_terms} = {sum_sq}\).
Mệnh đề này là {sol_correct_str.lower()}."""

    return stmt, sol, is_correct

def generate_stmt_e():
    # y = m + k/(x-x0)
    # Number of lines cutting at 2 integer points = C(N, 2)
    k_vals = {
        1: 2, -1: 2,
        2: 4, -2: 4,
        3: 4, -3: 4,
        4: 6, -4: 6,
        5: 4, -5: 4,
        6: 8, -6: 8
    }
    k = random.choice(list(k_vals.keys()))
    num_pts = k_vals[k]
    
    num_lines = (num_pts * (num_pts - 1)) // 2
    
    x0 = random.choice([-2, -1, 1, 2])
    m = random.choice([-2, -1, 1, 2])
    
    a = m
    b = k - m*x0
    
    func_str = format_rational_func(a, b, 1, -x0)
    
    is_correct = random.choice([True, False])
    lines_val = num_lines if is_correct else num_lines + random.choice([-2, 2, 4])
    if lines_val <= 0: lines_val = num_lines + 2
    
    stmt = rf"Cho hàm số \(y = {func_str}\). Có {lines_val} đường thẳng cắt đồ thị hàm số tại hai điểm phân biệt có tọa độ nguyên."
    
    sol_correct_str = "Đúng" if is_correct else "Sai"
    
    sol = rf"""+) {sol_correct_str}.

Ta có \(y = {func_str} = {m} {'+' if k > 0 else '-'} \frac{{{abs(k)}}}{{{fmt_x_minus_a(x0)}}}\).
Để điểm thuộc đồ thị có tọa độ nguyên thì \(x\) và \(y\) đều phải là số nguyên.
Do đó \({fmt_x_minus_a(x0)}\) phải là ước của \({abs(k)}\).
Các ước của \({abs(k)}\) là: {', '.join(map(str, [i for i in range(-abs(k), abs(k)+1) if i != 0 and abs(k) % i == 0]))}.
Có tất cả {num_pts} ước, tương ứng với {num_pts} điểm trên đồ thị có tọa độ nguyên.
Cứ qua 2 điểm phân biệt ta vẽ được 1 đường thẳng.
Số đường thẳng cắt đồ thị tại 2 điểm phân biệt có tọa độ nguyên là số cách chọn 2 điểm từ {num_pts} điểm nguyên đó: \(C_{{{num_pts}}}^2 = {num_lines}\).
Mệnh đề này là {sol_correct_str.lower()}."""
    
    return stmt, sol, is_correct

def generate_question() -> Tuple[str, str, str]:
    generators = [generate_stmt_a, generate_stmt_b, generate_stmt_c, generate_stmt_d, generate_stmt_e]
    selected_gens = random.sample(generators, 4)
    
    stmts = []
    sols = []
    is_corrects = []
    
    labels = ['a', 'b', 'c', 'd']
    
    for i, gen in enumerate(selected_gens):
        stmt, sol, is_correct = gen()
        sol = sol.replace("+)", f"{labels[i]})", 1)
        
        stmts.append(rf"{'*' if is_correct else ''}{labels[i]}) {stmt}")
        sols.append(sol)
        is_corrects.append(is_correct)
        
    stem = "Xét tính đúng, sai của các phát biểu sau:"
    
    question = f"{stem}\n\n" + "\n\n".join(stmts)
    solution = "\n\n".join(sols)
    
    key_arr = ["Đ" if x else "S" for x in is_corrects]
    key = ", ".join(key_arr)
    
    return question, solution, key

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])

    content = ""
    keys = []
    
    for i in range(num_questions):
        q, s, k = generate_question()
        keys.append(k)
        content += f"Câu {i+1}: {q}\n\nLời giải:\n\n{s}\n\n"

    template = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
% \setmainfont{Times New Roman}
\usepackage{tikz}
\usetikzlibrary{calc,angles,quotes}

\newcommand{\heva}[1]{\left\{\begin{aligned}#1\end{aligned}\right.}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    script_base = os.path.splitext(os.path.basename(__file__))[0]
    output_file = os.path.join(out_dir, f"{script_base}_questions.tex")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
