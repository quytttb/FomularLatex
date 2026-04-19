import math
import os
import sys
import random
from typing import Tuple

def fmt_dec(x, comma=True):
    """Format a number: int if whole, else decimal with comma."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = f"{x:.4f}".rstrip('0').rstrip('.')
    if comma:
        s = s.replace(".", ",")
    return s

def _get_configs():
    configs = []
    for a0_1k in range(2, 21):
        a0 = a0_1k / 1000.0
        for t1 in range(20, 101, 10):
            l = (a0 / 6) * (t1 ** 3)
            # l must be integer
            if abs(l - round(l)) > 1e-9:
                continue
            l = int(round(l))
            
            for t2 in range(t1 + 10, 151, 10):
                vt2 = (a0 / 2) * (t2 ** 2)
                vt2_kmh = vt2 * 3.6
                if abs(vt2_kmh - round(vt2_kmh, 1)) > 1e-9:
                    continue
                
                for tb in range(10, 150):
                    # L must be integer and between 100 and 1500
                    L = tb * vt2 - l
                    if 100 <= L <= 1500 and abs(L - round(L)) < 1e-9:
                        L = int(round(L))
                        configs.append({
                            'a0': a0,
                            'a0_1k': a0_1k,
                            't1': t1,
                            't2': t2,
                            'l': l,
                            'vt2': vt2,
                            'vt2_kmh': vt2_kmh,
                            'L': L,
                            'tb': tb,
                            'C1': a0 / 2
                        })
    return configs

_CONFIGS = _get_configs()

def generate_question(seed_val=None) -> Tuple[str, str, str]:
    if seed_val is not None:
        random.seed(seed_val)
    
    cfg = random.choice(_CONFIGS)
    a0 = cfg['a0']
    a0_1k = cfg['a0_1k']
    t1 = cfg['t1']
    t2 = cfg['t2']
    l = cfg['l']
    vt2 = cfg['vt2']
    vt2_kmh = cfg['vt2_kmh']
    L = cfg['L']
    tb = cfg['tb']
    C1 = cfg['C1']
    
    a_correct = random.choice([True, False])
    b_correct = random.choice([True, False])
    c_correct = random.choice([True, False])
    d_correct = random.choice([True, False])
    
    # Statement a
    C1_1k_correct = fmt_dec(C1 * 1000)
    C1_1k_wrong = fmt_dec(a0 * 1000) 
    if C1_1k_wrong == C1_1k_correct: 
        C1_1k_wrong = fmt_dec(C1 * 1000 * 3)
    val_a = C1_1k_correct if a_correct else C1_1k_wrong
    
    # Statement b
    l_wrong = round((a0 / 2) * (t1 ** 3))
    if l_wrong == l: 
        l_wrong = l + 20
    val_b = l if b_correct else l_wrong
    
    # Statement c
    vt2_kmh_wrong = vt2_kmh + random.choice([-10, 10, -5, 5])
    if vt2_kmh_wrong <= 0: 
        vt2_kmh_wrong = vt2_kmh + 10
    val_c = vt2_kmh if c_correct else vt2_kmh_wrong
    
    # Statement d
    tb_wrong = int(round(L / vt2))
    if tb_wrong == tb: 
        tb_wrong = tb + random.choice([5, -5])
    val_d = tb if d_correct else tb_wrong

    a0_s = fmt_dec(a0)
    
    stem = f"Một đoàn tàu đứng yên trong sân ga, ngay trước đầu tàu có một cái cây. Đoàn tàu khởi hành từ trạng thái đứng yên với gia tốc $a = {a0_s}t \\, (\\mathrm{{m/s^2}})$ và đi qua cái cây trong thời gian ${t1}$ giây. Sau ${t2}$ giây đoàn tàu chuyển sang trạng thái chuyển động đều."
    
    stmt_a = f"{'*' if a_correct else ''}a) Vận tốc của đoàn tàu là $v = {val_a} \\cdot 10^{{-3}}t^2 \\, (\\mathrm{{m/s}})$."
    stmt_b = f"{'*' if b_correct else ''}b) Chiều dài của đoàn tàu là $l = {val_b} \\, (\\mathrm{{m}})$."
    stmt_c = f"{'*' if c_correct else ''}c) Sau ${t2}$ giây, đoàn tàu chuyển động với tốc độ ${fmt_dec(val_c)} \\, (\\mathrm{{km/h}})$."
    stmt_d = f"{'*' if d_correct else ''}d) Sau khi chuyển động đều một thời gian, đoàn tàu gặp một cây cầu có chiều dài ${L} \\, (\\mathrm{{m}})$. Khi đó đoàn tàu đi qua cây cầu đó trong thời gian ${val_d}$ giây."
    
    c_actual_str = fmt_dec(C1 * 1000)
    
    sol_a = f"a) {'Đúng' if a_correct else 'Sai'}: Vận tốc của đoàn tàu là $v = \\displaystyle\\int a \\, \\mathrm{{d}}t = \\int {a0_s}t \\, \\mathrm{{d}}t = {c_actual_str} \\cdot 10^{{-3}}t^2 + C$.\n\n"
    sol_a += f"Vì ban đầu tàu đứng yên nên $C = 0$\n\n"
    sol_a += f"Vậy $v = {c_actual_str} \\cdot 10^{{-3}}t^2$."
    
    sol_b = f"b) {'Đúng' if b_correct else 'Sai'}: Quãng đường đoàn tàu đi được là\n"
    sol_b += f"$s = \\displaystyle\\int v \\, \\mathrm{{d}}t = \\int {c_actual_str} \\cdot 10^{{-3}}t^2 \\, \\mathrm{{d}}t = \\dfrac{{{c_actual_str} \\cdot 10^{{-3}}}}{{3}} t^3$\n\n"
    sol_b += f"Chiều dài của đoàn tàu là $l = \\dfrac{{{c_actual_str} \\cdot 10^{{-3}}}}{{3}} \\cdot {t1}^3 = {l} \\, (\\mathrm{{m}})$."
    
    sol_c = f"c) {'Đúng' if c_correct else 'Sai'}: Sau ${t2}$ giây vận tốc của đoàn tàu là\n"
    sol_c += f"$v = {c_actual_str} \\cdot 10^{{-3}} \\cdot {t2}^2 = {fmt_dec(vt2)} \\, (\\mathrm{{m/s}}) = {fmt_dec(vt2_kmh)} \\, (\\mathrm{{km/h}})$."
    
    sol_d = f"d) {'Đúng' if d_correct else 'Sai'}: Khi bắt đầu chuyển động đều, vận tốc của đoàn tàu là $v = {fmt_dec(vt2)} \\, (\\mathrm{{m/s}})$\n\n"
    sol_d += f"Tổng quãng đường đoàn tàu đi để vượt qua cây cầu là\n"
    sol_d += f"$S_t = {l} + {L} = {l + L} \\, (\\mathrm{{m}})$\n\n"
    sol_d += f"Vậy thời gian đoàn tàu qua cầu là $t = \\dfrac{{{l + L}}}{{{fmt_dec(vt2)}}} = {fmt_dec(tb)} \\, (\\text{{giây}})$."
    
    solution = "\n\n".join([sol_a, sol_b, sol_c, sol_d])
    key_arr = ["Đ" if x else "S" for x in (a_correct, b_correct, c_correct, d_correct)]
    key = ", ".join(key_arr)
    
    question = "\n\n".join([stem, stmt_a, stmt_b, stmt_c, stmt_d])
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
    output_file = os.path.join(out_dir, "train_bridge_tf_questions.tex")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {output_file}")
    for i, k in enumerate(keys):
        print(f"Câu {i+1}: {k}")

if __name__ == "__main__":
    main()
