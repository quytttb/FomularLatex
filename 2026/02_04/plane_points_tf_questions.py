import math
import os
import sys
import random
from typing import Tuple
from fractions import Fraction

def format_frac_tex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator < 0:
        return rf"-\frac{{{-f.numerator}}}{{{f.denominator}}}"
    return rf"\frac{{{f.numerator}}}{{{f.denominator}}}"

def fmt_point(p):
    return f"({p[0]}; {p[1]}; {p[2]})"

def format_plane_eq(nx, ny, nz, D):
    terms = []
    if nx != 0:
        if nx == 1: terms.append("x")
        elif nx == -1: terms.append("-x")
        else: terms.append(f"{nx}x")
    if ny != 0:
        if ny == 1: terms.append("+ y" if terms else "y")
        elif ny == -1: terms.append("- y" if terms else "-y")
        else: terms.append(f"+ {ny}y" if ny > 0 and terms else f"{ny}y")
    if nz != 0:
        if nz == 1: terms.append("+ z" if terms else "z")
        elif nz == -1: terms.append("- z" if terms else "-z")
        else: terms.append(f"+ {nz}z" if nz > 0 and terms else f"{nz}z")
    if D != 0:
        terms.append(f"+ {D}" if D > 0 else f"- {-D}")
    return " ".join(terms) + " = 0"

def _get_configs():
    configs = []
    normals = [
        (2, 1, -2), (2, -1, 2), (-2, 1, 2), (1, 2, 2),
        (1, -2, 2), (2, 2, 1), (-1, 2, 2), (2, -2, 1)
    ]
    for nx, ny, nz in normals:
        for D in range(-20, 21):
            for xA in range(-4, 5):
                for yA in range(-4, 5):
                    for zA in range(-4, 5):
                        fA = nx*xA + ny*yA + nz*zA + D
                        if fA in [-18, -9, 9, 18]:
                            configs.append({
                                'n': (nx, ny, nz),
                                'D': D,
                                'A': (xA, yA, zA),
                                'fA': fA
                            })
    return configs

_CONFIGS = None

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    global _CONFIGS
    if _CONFIGS is None:
        _CONFIGS = _get_configs()
    
    if seed_val is not None:
        random.seed(seed_val)
        
    cfg = random.choice(_CONFIGS)
    nx, ny, nz = cfg['n']
    D = cfg['D']
    xA, yA, zA = cfg['A']
    fA = cfg['fA']
    
    # Generate B
    valid_B = []
    for _ in range(1000):
        xB, yB, zB = random.randint(-6, 6), random.randint(-6, 6), random.randint(-6, 6)
        if (xB, yB, zB) == (xA, yA, zA): continue
        fB = nx*xB + ny*yB + nz*zB + D
        if fB == 0: continue
        if fB == fA: continue  # tránh AB // (alpha)
        
        ABx, ABy, ABz = xB - xA, yB - yA, zB - zA
        Nx = ny * ABz - nz * ABy
        Ny = nz * ABx - nx * ABz
        Nz = nx * ABy - ny * ABx
        
        if Ny != 0:
            valid_B.append((xB, yB, zB, fB, Nx, Ny, Nz))
            
    random.shuffle(valid_B)
    nice_B = [b for b in valid_B if b[4] % b[5] == 0 and b[6] % b[5] == 0]
    B_choice = nice_B[0] if nice_B else valid_B[0]
        
    xB, yB, zB, fB, Nx, Ny, Nz = B_choice
    
    a_frac = Fraction(Nx, Ny)
    c_frac = Fraction(Nz, Ny)
    a_plus_c = a_frac + c_frac
    
    d_A = abs(fA) // 3
    
    a_correct = random.choice([True, False])
    val_a = d_A if a_correct else d_A + random.choice([1, -1, 2])
    if val_a <= 0: val_a = d_A + 1
    
    stmt_a = f"{'*' if a_correct else ''}a) $d(A, (\\alpha)) = {val_a}$."
    
    is_opposite = (fA * fB < 0)
    b_correct = random.choice([True, False])
    if b_correct:
        phrase_b = "nằm trong" if is_opposite else "nằm ngoài"
    else:
        phrase_b = "nằm ngoài" if is_opposite else "nằm trong"
        
    stmt_b = f"{'*' if b_correct else ''}b) Đường thẳng $AB$ cắt $(\\alpha)$ tại một điểm {phrase_b} đoạn $AB$."
    
    c_correct = random.choice([True, False])
    if c_correct:
        ac_val = a_plus_c
    else:
        ac_val = a_plus_c + random.choice([1, -1, 2, Fraction(1,2)])
        
    ac_str = format_frac_tex(ac_val)
    stmt_c = f"{'*' if c_correct else ''}c) Nếu $(\\beta): ax + y + cz + d = 0$ là mặt phẳng đi qua $A, B$ và $(\\beta) \\perp (\\alpha)$ thì $a + c = {ac_str}$."
    
    tA = -fA // 9
    xH, yH, zH = xA + tA*nx, yA + tA*ny, zA + tA*nz
    xA_p, yA_p, zA_p = 2*xH - xA, 2*yH - yA, 2*zH - zA
    
    AB_sq = (xB - xA)**2 + (yB - yA)**2 + (zB - zA)**2
    ApB_sq = (xB - xA_p)**2 + (yB - yA_p)**2 + (zB - zA_p)**2
    
    if is_opposite:
        min_sq = AB_sq
        trap_sq = ApB_sq
        t_M = Fraction(fA, fA - fB)
        start_x, start_y, start_z = xA, yA, zA
        dir_x, dir_y, dir_z = xB - xA, yB - yA, zB - zA
        
        # Wrong M: dùng A'B thay vì AB (fA+fB != 0 vì fA=-|fA|, fB=+|fB| nhưng |fA|!=|fB| do fA!=fB)
        if fA + fB != 0:
            t_w = Fraction(fA, fA + fB)
        else:
            t_w = Fraction(1, 2)  # fallback an toàn
        sx_w, sy_w, sz_w = xA_p, yA_p, zA_p
        dx_w, dy_w, dz_w = xB - xA_p, yB - yA_p, zB - zA_p
    else:
        min_sq = ApB_sq
        trap_sq = AB_sq
        t_M = Fraction(fA, fA + fB)
        start_x, start_y, start_z = xA_p, yA_p, zA_p
        dir_x, dir_y, dir_z = xB - xA_p, yB - yA_p, zB - zA_p
        
        # Wrong M: dùng AB thay vì A'B (fA-fB != 0 vì đã loại fA==fB)
        t_w = Fraction(fA, fA - fB)
        sx_w, sy_w, sz_w = xA, yA, zA
        dx_w, dy_w, dz_w = xB - xA, yB - yA, zB - zA
        
    Mx = start_x + t_M * dir_x
    My = start_y + t_M * dir_y
    Mz = start_z + t_M * dir_z
    sum_abc = Mx + 2 * My + Mz

    Mx_w = sx_w + t_w * dx_w
    My_w = sy_w + t_w * dy_w
    Mz_w = sz_w + t_w * dz_w
    sum_abc_w = Mx_w + 2 * My_w + Mz_w
    
    min_root_int = int(math.sqrt(int(min_sq)))
    is_perfect = (min_root_int * min_root_int == int(min_sq))
    
    trap_root_int = int(math.sqrt(int(trap_sq)))
    is_trap_perfect = (trap_root_int * trap_root_int == int(trap_sq))
    
    if is_perfect:
        disp_expr = format_frac_tex(sum_abc + min_root_int)
    else:
        sum_str = format_frac_tex(sum_abc)
        if sum_str == "0":
            disp_expr = f"\\sqrt{{{int(min_sq)}}}"
        else:
            disp_expr = f"{sum_str} + \\sqrt{{{int(min_sq)}}}"
            
    if is_trap_perfect:
        disp_expr_w = format_frac_tex(sum_abc_w + trap_root_int)
    else:
        sum_str_w = format_frac_tex(sum_abc_w)
        if sum_str_w == "0":
            disp_expr_w = f"\\sqrt{{{int(trap_sq)}}}"
        else:
            disp_expr_w = f"{sum_str_w} + \\sqrt{{{int(trap_sq)}}}"
            
    if disp_expr_w == disp_expr:
        disp_expr_w = f"{format_frac_tex(sum_abc + 1)} + \\sqrt{{{int(min_sq)}}}" if not is_perfect else format_frac_tex(sum_abc + min_root_int + 1)
        
    d_correct = random.choice([True, False])
    final_expr = disp_expr if d_correct else disp_expr_w
            
    stmt_d = f"{'*' if d_correct else ''}d) Giá trị nhỏ nhất của $MA + MB = m$ khi $M(a; b; c)$. Khi đó $a+2b+c+m = {final_expr}$."
    
    alpha_eq = format_plane_eq(nx, ny, nz, D)
    stem = f"Trong không gian $Oxyz$, cho mặt phẳng $(\\alpha): {alpha_eq}$ và hai điểm $A{fmt_point((xA, yA, zA))}$, $B{fmt_point((xB, yB, zB))}$. Gọi $M$ là điểm chạy trên mặt phẳng $(\\alpha)$."
    
    dist_calc = f"\\dfrac{{|{nx}({xA}) + {ny}({yA}) + {nz}({zA}) {f'+ ' + str(D) if D > 0 else ('- ' + str(-D) if D < 0 else '')}|}}{{\\sqrt{{{nx}^2 + {ny}^2 + {nz}^2}}}} = \\dfrac{{|{fA}|}}{{\\sqrt{{9}}}} = {d_A}"
    dist_calc = dist_calc.replace("+-", "-")
    sol_a = f"a) {'Đúng' if a_correct else 'Sai'}: Bán kính khoảng cách từ $A$ đến mặt phẳng $(\\alpha)$ là:\n"
    sol_a += f"$d(A, (\\alpha)) = {dist_calc}$."
    
    sol_b = f"b) {'Đúng' if b_correct else 'Sai'}: Đặt $f(x, y, z) = {alpha_eq.replace(' = 0', '')}$. Ta có:\n\n"
    sol_b += f"$f(A) = {fA}$\n\n"
    fB_calc = f"{nx}({xB}) + {ny}({yB}) + {nz}({zB}) {f'+ ' + str(D) if D > 0 else ('- ' + str(-D) if D < 0 else '')}"
    fB_calc = fB_calc.replace("+-", "-")
    sol_b += f"$f(B) = {fB_calc} = {fB}$\n\n"
    if is_opposite:
        sol_b += f"Vì $f(A)\\cdot f(B) = {fA}\\cdot({fB}) < 0$ nên $A$ và $B$ nằm về hai phía của $(\\alpha)$.\n\n"
        sol_b += "Do đó, đường thẳng $AB$ cắt $(\\alpha)$ tại một điểm nằm trong đoạn $AB$."
    else:
        sol_b += f"Vì $f(A)\\cdot f(B) = {fA}\\cdot({fB}) > 0$ nên $A$ và $B$ nằm cùng phía đối với $(\\alpha)$.\n\n"
        sol_b += "Do đó, đường thẳng $AB$ cắt $(\\alpha)$ tại một điểm nằm ngoài đoạn $AB$."
        
    vAB = (xB-xA, yB-yA, zB-zA)
    sol_c = f"c) {'Đúng' if c_correct else 'Sai'}: Mặt phẳng $(\\alpha)$ có VTPT $\\vec{{n}}_{{\\alpha}} = {fmt_point((nx, ny, nz))}$.\n\n"
    sol_c += f"Vectơ $\\overrightarrow{{AB}} = {fmt_point(vAB)}$.\n\n"
    sol_c += f"Mặt phẳng $(\\beta)$ đi qua $A, B$ và vuông góc với $(\\alpha)$ nên có VTPT $\\vec{{n}}_{{\\beta}} = [\\vec{{n}}_{{\\alpha}}, \\overrightarrow{{AB}}] = {fmt_point((Nx, Ny, Nz))}$.\n\n"
    sol_c += f"Phương trình mặt phẳng $(\\beta)$ có dạng $ax + y + cz + d = 0$, nghĩa là hệ số của $y$ bằng $1$.\n\n"
    sol_c += f"Ta chọn VTPT cùng phương với $\\vec{{n}}_{{\\beta}}$ sao cho tung độ bằng $1$, đó là $\\vec{{n}}'_{{\\beta}} = ({format_frac_tex(a_frac)}; 1; {format_frac_tex(c_frac)})$.\n\n"
    sol_c += f"Do đó $a = {format_frac_tex(a_frac)}, c = {format_frac_tex(c_frac)} \\implies a + c = {format_frac_tex(a_plus_c)}$."
    
    sol_d = f"d) {'Đúng' if d_correct else 'Sai'}: "
    if is_opposite:
        sol_d += f"Vì $A$ và $B$ nằm về hai phía của mặt phẳng $(\\alpha)$ nên với mọi điểm $M \\in (\\alpha)$, ta luôn có $MA + MB \\ge AB$.\n\n"
        sol_d += f"Đẳng thức xảy ra khi $M = AB \\cap (\\alpha)$.\n\n"
        sol_d += f"Vậy $m = \\min(MA + MB) = AB = \\sqrt{{({xB} - {xA})^2 + ({yB} - {yA})^2 + ({zB} - {zA})^2}} = {'\\sqrt{'+str(int(min_sq))+'}' if not is_perfect else min_root_int}$.\n\n"
        sol_d += f"Mặt khác, $M \\in AB$ nên $\\overrightarrow{{AM}} = t \\overrightarrow{{AB}} \\implies f(A+t\\overrightarrow{{AB}}) = 0 \\implies t = \\frac{{-f(A)}}{{f(B)-f(A)}} = {format_frac_tex(t_M)}$.\n\n"
        sol_d += f"Suy ra $M({format_frac_tex(Mx)}; {format_frac_tex(My)}; {format_frac_tex(Mz)})$.\n\n"
        sol_d += f"Nên $a+2b+c+m = {format_frac_tex(Mx)} + 2\\cdot({format_frac_tex(My)}) + ({format_frac_tex(Mz)}) + {'\\sqrt{'+str(int(min_sq))+'}' if not is_perfect else min_root_int} = {disp_expr}$."
        if not d_correct and final_expr == disp_expr_w:
            sol_d += f"\n\n(Chú ý: Cách tính sai thường là lấy $M = A'B \\cap (\\alpha)$ (dành cho A, B cùng phía) dẫn tới kết quả $a+2b+c+m = {disp_expr_w}$)."
    else:
        sol_d += f"Vì $A$ và $B$ nằm cùng phía đối với mặt phẳng $(\\alpha)$, gọi $A'$ là điểm đối xứng của $A$ qua $(\\alpha)$.\n\n"
        sol_d += f"Khi đó với mọi $M \\in (\\alpha)$, ta có $MA + MB = MA' + MB \\ge A'B$.\n\n"
        sol_d += f"Đẳng thức xảy ra khi $M = A'B \\cap (\\alpha)$.\n\n"
        sol_d += f"Tìm $A'$: Đường thẳng $d_A$ qua $A$ vuông góc với $(\\alpha)$ có PT: $\\begin{{cases}} x = {xA} {'+' if nx>0 else ''} {nx}t \\\\ y = {yA} {'+' if ny>0 else ''} {ny}t \\\\ z = {zA} {'+' if nz>0 else ''} {nz}t \\end{{cases}}$.\n\n"
        sol_d += f"Giao điểm $H$ của $d_A$ và $(\\alpha)$ có $t$ là nghiệm của: ${nx}({xA} {'+' if nx>0 else ''} {nx}t) + {ny}({yA} {'+' if ny>0 else ''} {ny}t) + {nz}({zA} {'+' if nz>0 else ''} {nz}t) {f'+ ' + str(D) if D > 0 else ('- ' + str(-D) if D < 0 else '')} = 0$\n\n"
        sol_d += f"$\\Leftrightarrow 9t {fA:+} = 0 \\Leftrightarrow t = {format_frac_tex(Fraction(-fA, 9))} = {int(tA)}$.\n\n"
        sol_d += f"Suy ra $H{fmt_point((int(xH), int(yH), int(zH)))}$. $A'$ đối xứng $A$ qua $H$ nên $A'{fmt_point((int(xA_p), int(yA_p), int(zA_p)))}$.\n\n"
        sol_d += f"Vậy $m = \\min(MA + MB) = A'B = \\sqrt{{({xB} - {int(xA_p)})^2 + ({yB} - {int(yA_p)})^2 + ({zB} - {int(zA_p)})^2}} = {'\\sqrt{'+str(int(min_sq))+'}' if not is_perfect else min_root_int}$.\n\n"
        sol_d += f"Lại có $M \\in A'B$ nên $\\overrightarrow{{A'M}} = t \\overrightarrow{{A'B}} \\implies f(A'+t\\overrightarrow{{A'B}}) = 0 \\implies t = \\frac{{-f(A')}}{{f(B)-f(A')}} = \\frac{{f(A)}}{{f(A)+f(B)}} = {format_frac_tex(t_M)}$.\n\n"
        sol_d += f"Suy ra $M({format_frac_tex(Mx)}; {format_frac_tex(My)}; {format_frac_tex(Mz)})$.\n\n"
        sol_d += f"Nên $a+2b+c+m = {format_frac_tex(Mx)} + 2\\cdot({format_frac_tex(My)}) + ({format_frac_tex(Mz)}) + {'\\sqrt{'+str(int(min_sq))+'}' if not is_perfect else min_root_int} = {disp_expr}$."
        if not d_correct and final_expr == disp_expr_w:
            sol_d += f"\n\n(Chú ý: Cách tính sai thường là lấy $M = AB \\cap (\\alpha)$ (dành cho A, B khác phía) dẫn tới kết quả $a+2b+c+m = {disp_expr_w}$)."

    key_arr = ["Đ" if x else "S" for x in (a_correct, b_correct, c_correct, d_correct)]
    key = ", ".join(key_arr)
    
    question = "\n\n".join([stem, stmt_a, stmt_b, stmt_c, stmt_d])
    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])
    
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
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usetikzlibrary{{angles,patterns,calc,arrows,intersections}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\newcommand{{\\heva}}[1]{{\\left\\{{\\begin{{aligned}}#1\\end{{aligned}}\\right.}}

\\begin{{document}}
{content}\\end{{document}}
"""

    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(out_dir, "plane_points_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
