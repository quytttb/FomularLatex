import random
import os
import sys

def draw_dashed(x, y):
    res = ""
    if x != 0:
        res += rf"\draw ({x},0.1) -- ({x},-0.1) node[below] {{${x}$}};"
    if y != 0:
        res += rf"\draw (0.1,{y}) -- (-0.1,{y}) node[left] {{${y}$}};"
        
    if x != 0 and y != 0:
        res += rf"\draw[dashed] ({x},0) |- (0,{y});"
        res += rf"\draw[fill=black] ({x},{y}) circle (1.5pt);"
    elif x != 0 and y == 0:
        res += rf"\draw[fill=black] ({x},0) circle (1.5pt);"
    elif x == 0 and y != 0:
        res += rf"\draw[fill=black] (0,{y}) circle (1.5pt);"
    return res

def generate_shape_1():
    h = random.randint(-2, 2)
    k = random.randint(-3, -1)
    
    xmin = min(-1, h - 1.5)
    xmax = max(1, h + 3.5)
    ymin = min(-1, k - 1)
    ymax = max(1, k + 5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=100,domain={xmin}:{xmax}] plot(\x,{{-(\x-({h}))^3+3*(\x-({h}))^2+({k})}});
    \end{{scope}}
    
    {draw_dashed(h, k)}
    {draw_dashed(h+2, k+4)}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"({h}; {h+2})"]
    dec = [rf"(-\infty; {h})", rf"({h+2}; +\infty)"]
    return code, inc, dec

def generate_shape_2():
    h = random.randint(-2, 2)
    k = random.randint(1, 4)
    
    xmin = min(-1, h - 1.5)
    xmax = max(1, h + 3.5)
    ymin = min(-1, k - 5)
    ymax = max(1, k + 1.5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=100,domain={xmin}:{xmax}] plot(\x,{{(\x-({h}))^3-3*(\x-({h}))^2+({k})}});
    \end{{scope}}
    
    {draw_dashed(h, k)}
    {draw_dashed(h+2, k-4)}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {h})", rf"({h+2}; +\infty)"]
    dec = [rf"({h}; {h+2})"]
    return code, inc, dec

def generate_shape_3():
    h = random.randint(-2, 2)
    k = random.randint(1, 4)
    
    xmin = min(-1, h - 2)
    xmax = max(1, h + 2)
    ymin = min(-1, k - 1.5)
    ymax = max(1, k + 1.5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=150,domain={xmin}:{xmax}] plot(\x,{{(\x-({h}))^4-2*(\x-({h}))^2+({k})}});
    \end{{scope}}
    
    {draw_dashed(h-1, k-1)}
    {draw_dashed(h+1, k-1)}
    {draw_dashed(h, k)}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"({h-1}; {h})", rf"({h+1}; +\infty)"]
    dec = [rf"(-\infty; {h-1})", rf"({h}; {h+1})"]
    return code, inc, dec

def generate_shape_4():
    h = random.randint(-2, 2)
    k = random.randint(-3, -1)
    
    xmin = min(-1, h - 2)
    xmax = max(1, h + 2)
    ymin = min(-1, k - 1.5)
    ymax = max(1, k + 1.5)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=150,domain={xmin}:{xmax}] plot(\x,{{-(\x-({h}))^4+2*(\x-({h}))^2+({k})}});
    \end{{scope}}
    
    {draw_dashed(h-1, k+1)}
    {draw_dashed(h+1, k+1)}
    {draw_dashed(h, k)}
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {h-1})", rf"({h}; {h+1})"]
    dec = [rf"({h-1}; {h})", rf"({h+1}; +\infty)"]
    return code, inc, dec

def generate_shape_5():
    h = random.choice([-2, -1, 1, 2])
    k = random.choice([-2, -1, 1, 2])
    
    xmin = min(-1, h - 3)
    xmax = max(1, h + 3)
    ymin = min(-1, k - 3)
    ymax = max(1, k + 3)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=100,domain={xmin}:{h-0.1}] plot(\x,{{-1/(\x-({h}))+({k})}});
        \draw[smooth,samples=100,domain={h+0.1}:{xmax}] plot(\x,{{-1/(\x-({h}))+({k})}});
    \end{{scope}}
    
    \draw[dashed] ({h},{ymin}) -- ({h},{ymax});
    \draw[dashed] ({xmin},{k}) -- ({xmax},{k});
    
    \draw ({h},0.1) -- ({h},-0.1) node[below right] {{${h}$}};
    \draw (0.1,{k}) -- (-0.1,{k}) node[above left] {{${k}$}};
\end{{tikzpicture}}
\end{{center}}"""
    inc = [rf"(-\infty; {h})", rf"({h}; +\infty)"]
    dec = []
    return code, inc, dec

def generate_shape_6():
    h = random.choice([-2, -1, 1, 2])
    k = random.choice([-2, -1, 1, 2])
    
    xmin = min(-1, h - 3)
    xmax = max(1, h + 3)
    ymin = min(-1, k - 3)
    ymax = max(1, k + 3)
    
    code = rf"""\begin{{center}}
\begin{{tikzpicture}}[>=stealth, font=\footnotesize, line join=round, scale=0.8]
    \draw[->] ({xmin}, 0) -- ({xmax}, 0) node[anchor=north] {{$x$}};
    \draw[->] (0, {ymin}) -- (0, {ymax}) node[anchor=west] {{$y$}};
    \draw[fill=black] (0,0) circle (1pt) node[below right] {{$O$}};
    
    \begin{{scope}}
        \clip ({xmin}, {ymin}) rectangle ({xmax}, {ymax});
        \draw[smooth,samples=100,domain={xmin}:{h-0.1}] plot(\x,{{1/(\x-({h}))+({k})}});
        \draw[smooth,samples=100,domain={h+0.1}:{xmax}] plot(\x,{{1/(\x-({h}))+({k})}});
    \end{{scope}}
    
    \draw[dashed] ({h},{ymin}) -- ({h},{ymax});
    \draw[dashed] ({xmin},{k}) -- ({xmax},{k});
    
    \draw ({h},0.1) -- ({h},-0.1) node[below right] {{${h}$}};
    \draw (0.1,{k}) -- (-0.1,{k}) node[above left] {{${k}$}};
\end{{tikzpicture}}
\end{{center}}"""
    inc = []
    dec = [rf"(-\infty; {h})", rf"({h}; +\infty)"]
    return code, inc, dec

def generate_question(seed=None, force_sample=False):
    if seed is not None:
        random.seed(seed)
        
    generators = [generate_shape_1, generate_shape_2, generate_shape_3, generate_shape_4, generate_shape_5, generate_shape_6]
    
    if force_sample:
        random.seed(42)
        code, inc, dec = generate_shape_1()
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
            
    stem = r"Cho hàm số $y = f(x)$ có đồ thị như hình vẽ bên. Mệnh đề nào sau đây đúng về hàm số đó?" + "\n"
    stem += code + "\n"
    
    inc_str = " và ".join([f"${i}$" for i in inc])
    dec_str = " và ".join([f"${d}$" for d in dec])
    
    sol = r"Quan sát đồ thị, ta thấy:" + "\n"
    sol += r"\begin{itemize}" + "\n"
    if inc:
        sol += rf"\item Đồ thị đi lên từ trái sang phải trên các khoảng {inc_str} nên hàm số đồng biến trên các khoảng đó." + "\n"
    if dec:
        sol += rf"\item Đồ thị đi xuống từ trái sang phải trên các khoảng {dec_str} nên hàm số nghịch biến trên các khoảng đó." + "\n"
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
\usepackage{tikz}
\usepackage[solcolor]{ex_test}

\begin{document}

#CONTENT#

\end{document}
"""
    tex_content = template.replace("#CONTENT#", content)
    out_path = os.path.join(out_dir, "don_dieu_do_thi_questions.tex")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Đã tạo {num_questions} câu và lưu: {out_path}")

if __name__ == "__main__":
    main()
