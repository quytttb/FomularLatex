"""
Thư viện hình vẽ TikZ cho hệ thống sinh câu hỏi toán về tính đơn điệu hàm số
Copy từ dothihamso3.py
"""

def generate_monotonicity_table_type1(params):
    """
    Sinh bảng biến thiên Type 1 - Tìm khoảng nghịch biến
    Dấu: -, 0, +, 0, -, 0, +
    """
    A, B, C = params["A"], params["B"], params["C"]
    D, F, O = params["D"], params["F"], params["O"]
    
    return f"""\\begin{{tikzpicture}}[>=stealth, scale=1]
\t\\tkzTabInit[lgt=2,espcl=2]
\t{{$x$/1,$f''(x)$/0.8,$f'(x)$/3}}
\t{{$-\\infty$,${A}$,${B}$,${C}$,$+\\infty$}}
\t\\tkzTabLine{{,-,0,+,0,-,0,+,}}
\t\\path
\t(N12)node[shift={{(0,-0.2)}}](A){{$+\\infty$}}
\t(N23)node[shift={{(0,0.2)}}](B){{${D}$}}
\t(N32)node[shift={{(0,-1.5)}}](C){{${O}$}}
\t(N43)node[shift={{(0,0.2)}}](D){{${F}$}}
\t(N52)node[shift={{(0,-0.2)}}](E){{$+\\infty$}};
\t\\foreach \\X/\\Y in {{A/B,B/C,C/D,D/E}} \\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}"""

def generate_monotonicity_table_type2(params):
    """
    Sinh bảng biến thiên Type 2 - Tìm khoảng đồng biến  
    Dấu: +, 0, -, 0, +, 0, -
    """
    A, B, C = params["A"], params["B"], params["C"]
    D, F, O = params["D"], params["F"], params["O"]
    
    return f"""\\begin{{tikzpicture}}[>=stealth, scale=1]
\t\\tkzTabInit[lgt=2,espcl=2]
\t{{$x$/1,$f''(x)$/0.8,$f'(x)$/3}}
\t{{$-\\infty$,${A}$,${B}$,${C}$,$+\\infty$}}
\t\\tkzTabLine{{,+,0,-,0,+,0,-,}}
\t\\path
\t(N13)node[shift={{(0,0.2)}}](A){{$+\\infty$}}
\t(N22)node[shift={{(0,-0.2)}}](B){{${D}$}}
\t(N32)node[shift={{(0,-1.5)}}](C){{${O}$}}
\t(N42)node[shift={{(0,-0.2)}}](D){{${F}$}}
\t(N53)node[shift={{(0,0.2)}}](E){{$+\\infty$}};
\t\\foreach \\X/\\Y in {{A/B,B/C,C/D,D/E}} \\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}"""

def generate_cubic_graph_type3(params):
    """
    Sinh đồ thị Type 3 - f'(x) = x³ - 3x - 1
    Hàm bậc 3 với 2 điểm cắt trục hoành
    """
    A, B, C, D, E, F = params["A"], params["B"], params["C"], params["D"], params["E"], params["F"]
    m = params.get("m", 1)
    A_plus_m = A + m
    E_plus_m = E + m

    return f"""\\begin{{tikzpicture}}[line join=round, line cap=round,>=stealth,scale=1]
\t\\tikzset{{label style/.style={{font=\\footnotesize}}}}
\t\\draw[->] (-2.7,0)--(2.7,0) node[below right] {{$x$}};
\t\\draw[->] (0,-3.1)--(0,2.1) node[below left] {{$y$}};
\t\\draw (0,0) node [below right] {{$O$}}circle(1.5pt);
\t\\foreach \\x in {{}}
\t\\draw[thin] (\\x,1pt)--(\\x,-1pt) node [below] {{$\\x$}};
\t\\foreach \\y in {{}}
\t\\draw[thin] (1pt,\\y)--(-1pt,\\y) node [left] {{$\\y$}};
\t\\draw[dashed,thin](-1,0)--(-1,1)--(0,1);
\t\\draw[dashed,thin](1,0)--(1,-3)--(0,-3);
\t\\draw (1,0) node[above]{{${A_plus_m}$}}; 
\t\\draw (-1.1,0) node[below]{{${-A}$}};
\t\\draw (0,-3) node[left]{{${-C}$}};
\t\\draw (0,1) node[right]{{${B}$}};
\t\\draw (-2,0) node[below]{{${-D}$}};
\t\\draw[fill=black] (-1.53,0)circle(1pt);
\t\\draw (2,0) node[below]{{${E}$}};
\t\\draw[fill=black] (1.86,0)circle(1pt);
\t\\draw (-.4,0) node[above]{{${-F}$}};
\t\\draw[fill=black] (-.34,0)circle(1pt);
\t\\begin{{scope}}
\t\t\\clip (-2,-3) rectangle (2,2);
\t\t\\draw[samples=200,domain=-2:2,smooth,variable=\\x] plot (\\x,{{(\\x)^3-3*(\\x)-1}});
\t\\end{{scope}}
\\end{{tikzpicture}}"""

def generate_parabolic_graph_type4(params):
    """
    Sinh đồ thị Type 4 - f'(x) = (x-2)(x-1)²
    Có nghiệm kép tại x=1, nghiệm đơn tại x=2
    """
    A, B = params["A"], params["B"]
    
    return f"""\\begin{{tikzpicture}}[scale=.9, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\t\\draw[->] (-1,0)--(0,0) node[below left]{{$O$}}--(3,0) node[below]{{$x$}};
\t\\draw[->] (0,-2)--(0,2) node[right]{{$y$}};
\t\\foreach \\x in {{1,2}}{{
\t\t\\draw[fill] (\\x,0) circle (1pt);
\t}}
\t\\draw[fill] (1,0) node[below]{{${A}$}};
\t\\draw[fill] (2,0) node[below]{{${B}$}};
\t\\draw [domain=.1:2.5, samples=100] plot (\\x, {{((\\x)-2)*((\\x)-1)^2}});
\t\\draw[fill] (0,0) circle (1pt);
\\end{{tikzpicture}}"""
