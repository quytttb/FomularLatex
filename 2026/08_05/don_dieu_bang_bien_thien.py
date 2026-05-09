import random
import os
import sys

def generate_tikz_1():
    x1 = random.randint(-5, -1)
    x2 = random.randint(x1+1, 2)
    x3 = random.randint(x2+1, 5)
    y1 = random.randint(-5, 0)
    y2 = random.randint(1, 5)
    y3 = random.randint(-5, 0)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[scale=.7]
	\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
	{{$x$ /0.6,$y'$ /0.6,$y$ /2}}
	{{$-\infty$,${x1}$,${x2}$,${x3}$,$+\infty$}}
	\tkzTabLine{{,-,$0$,+,$0$,-,$0$,+,}}
	\tkzTabVar{{+/$+\infty$, -/${y1}$,+/${y2}$,-/${y3}$,+/$+\infty$}}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"({x1}; {x2})", rf"({x3}; +\infty)"]
    dec = [rf"(-\infty; {x1})", rf"({x2}; {x3})"]
    return code, inc, dec

def generate_tikz_2():
    x1 = random.randint(-5, 0)
    x2 = random.randint(x1+1, 5)
    y1 = random.randint(1, 5)
    y2 = random.randint(-5, y1-1)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[scale=.7, font=\footnotesize, line join=round, line cap=round, >=stealth]
	\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
	{{$x$ /0.6,$y'$ /0.6,$y$ /2}}
	{{$-\infty$,${x1}$,${x2}$,$+\infty$}}
	\tkzTabLine{{,+,$0$,-,$0$,+,}}
	\tkzTabVar{{-/$-\infty$,+/${y1}$,-/${y2}$,+/$+\infty$}}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {x1})", rf"({x2}; +\infty)"]
    dec = [rf"({x1}; {x2})"]
    return code, inc, dec

def generate_tikz_3():
    x1 = random.randint(-5, -1)
    x2 = random.randint(x1+1, 2)
    x3 = random.randint(x2+1, 5)
    y1 = random.randint(1, 5)
    y3 = random.randint(1, 5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}
	\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
	{{$x$ /0.6,$y'$ /0.6,$y$ /2}}
	{{$-\infty$,${x1}$,${x2}$,${x3}$,$+\infty$}}
	\tkzTabLine{{,+,$0$,-,d,-,$0$,+,}}
	\tkzTabVar{{-/$-\infty$,+/${y1}$,-D+/$-\infty$/$+\infty$,-/${y3}$,+/$+\infty$}}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {x1})", rf"({x3}; +\infty)"]
    dec = [rf"({x1}; {x2})", rf"({x2}; {x3})"]
    return code, inc, dec

def generate_tikz_4():
    x1 = random.randint(-5, 5)
    y1 = random.randint(-5, 5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}
	\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
	{{$x$ /0.6,$y'$ /0.6,$y$ /2}}
	{{$-\infty$,${x1}$,$+\infty$}}
	\tkzTabLine{{,-,d,-,}}
	\tkzTabVar{{+/${y1}$,-D+/$-\infty$/$+\infty$,-/${y1}$}}
\end{{tikzpicture}}
\end{{center}}"""
    inc = []
    dec = [rf"(-\infty; {x1})", rf"({x1}; +\infty)"]
    return code, inc, dec

def generate_tikz_5():
    x1 = random.randint(-5, -1)
    x2 = random.randint(x1+1, 2)
    x3 = random.randint(x2+1, 5)
    y1 = random.randint(1, 5)
    y2 = random.randint(-5, 0)
    y3 = random.randint(1, 5)
    y4 = random.randint(-2, 2)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[scale=.7]
	\tkzTabInit[nocadre=false,lgt=1.2,espcl=2.5,deltacl=0.6]
	{{$x$/1, $y'$/1, $y$/2}}
	{{$-\infty$,${x1}$,${x2}$,${x3}$,$+\infty$}}
	\tkzTabLine{{,+,z,-,d,+,z,-,}}
	\tkzTabVar{{-/$-\infty$,+/${y1}$,-/${y2}$,+/${y3}$,-/${y4}$}}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {x1})", rf"({x2}; {x3})"]
    dec = [rf"({x1}; {x2})", rf"({x3}; +\infty)"]
    return code, inc, dec

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    generators = [generate_tikz_1, generate_tikz_2, generate_tikz_3, generate_tikz_4, generate_tikz_5]
    
    if force_sample:
        # Use a fixed seed for the first item to act as sample
        random.seed(42)
        code, inc, dec = generate_tikz_1()
    else:
        code, inc, dec = random.choice(generators)()
    
    true_pool = []
    for i in inc:
        true_pool.append(rf"Hàm số đồng biến trên khoảng ${i}$.")
    for d in dec:
        true_pool.append(rf"Hàm số nghịch biến trên khoảng ${d}$.")
        
    false_pool = []
    for i in inc:
        false_pool.append(rf"Hàm số nghịch biến trên khoảng ${i}$.")
    for d in dec:
        false_pool.append(rf"Hàm số đồng biến trên khoảng ${d}$.")
        
    false_pool.append(r"Hàm số đồng biến trên $\mathbb{R}$.")
    false_pool.append(r"Hàm số nghịch biến trên $\mathbb{R}$.")
    
    if len(inc) >= 2:
        false_pool.append(rf"Hàm số đồng biến trên khoảng ${inc[0]} \cup {inc[1]}$.")
    if len(dec) >= 2:
        false_pool.append(rf"Hàm số nghịch biến trên khoảng ${dec[0]} \cup {dec[1]}$.")
        
    correct_statement = random.choice(true_pool)
    incorrect_statements = random.sample(false_pool, 3)
    
    choices = [(correct_statement, True)]
    for stmt in incorrect_statements:
        choices.append((stmt, False))
        
    random.shuffle(choices)
    
    options_text = "\\choice\n"
    for text, is_correct in choices:
        if is_correct:
            options_text += rf"{{\True {text}}}" + "\n"
        else:
            options_text += rf"{{{text}}}" + "\n"
            
    stem = r"Cho hàm số $y = f(x)$ có bảng biến thiên như sau:" + "\n"
    stem += code + "\n"
    stem += r"Mệnh đề nào dưới đây đúng?"
    
    inc_str = " và ".join([f"${i}$" for i in inc])
    dec_str = " và ".join([f"${d}$" for d in dec])
    
    sol = r"Quan sát bảng biến thiên, ta thấy:" + "\n"
    sol += r"\begin{itemize}" + "\n"
    if inc:
        sol += rf"\item $y' > 0$ trên các khoảng {inc_str} nên hàm số đồng biến trên các khoảng đó." + "\n"
    if dec:
        sol += rf"\item $y' < 0$ trên các khoảng {dec_str} nên hàm số nghịch biến trên các khoảng đó." + "\n"
    sol += r"\end{itemize}" + "\n"
    
    return stem, options_text, sol

def main():
    num_questions = 1
    if len(sys.argv) > 1:
        num_questions = int(sys.argv[1])
        
    seed_val = None
    if len(sys.argv) > 2:
        seed_val = int(sys.argv[2])
        
    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = ""
    
    for i in range(num_questions):
        seed = seed_val + i if seed_val is not None else None
        force = (i == 0 and seed_val is None)
        q, opts, s = generate_question(seed, force_sample=force)
        
        content += rf"""\begin{{ex}}
{q}
{opts}
\loigiai{{
{s}
}}
\end{{ex}}

"""

    template = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage{tikz, tkz-tab}
\usepackage[solcolor]{ex_test}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    out_path = os.path.join(out_dir, "don_dieu_bang_bien_thien_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
