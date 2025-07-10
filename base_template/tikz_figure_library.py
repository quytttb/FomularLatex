"""
Thư viện hình vẽ TikZ cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 2
"""

class TikZFigureLibrary:
    """Thư viện hình vẽ TikZ"""

    # ===== THÊM TIKZ FIGURES MỚI TẠI ĐÂY =====
    # @staticmethod
    # def get_your_new_figure():
    #     """Mô tả hình vẽ của bạn"""
    #     return """
    #     \\begin{tikzpicture}
    #         % Code TikZ của bạn ở đây
    #     \\end{tikzpicture}
    #     """

def generate_tkztabinit_latex(params):
    """
    Sinh LaTeX cho bảng biến thiên tkzTabInit với các tham số truyền vào.
    params: dict chứa A, B, C, D, E, F (số nguyên) và pattern (dạng bảng biến thiên)
    """
    A, B, C = params["A"], params["B"], params["C"]  # Điểm cực trị
    D, E, F = params["D"], params["E"], params["F"]  # Giá trị cực trị
    pattern = params.get("pattern", "type1")  # Mặc định là dạng 1
    
    # Tạo các nhãn cho trục x (điểm cực trị)
    x_labels = ["\\(-\\infty\\)", f"\\( {A} \\)", f"\\( {B} \\)", f"\\( {C} \\)", "\\(+\\infty\\)"]
    x_labels_str = ",".join(x_labels)
    
    # Chọn dạng bảng biến thiên theo pattern
    if pattern == "type1":
        # Dạng 1: -, 0, +, 0, -, 0, + (Cực đại - Cực tiểu - Cực đại)
        sign_line = ",".join(["-", "0", "+", "0", "-", "0", "+"])
        # D và F là cực đại (vị trí cao), E là cực tiểu (vị trí thấp)
        node_positions = f"""
(N12)node[shift={{(0,-0.2)}}](A){{\\(+\\infty\\)}}
(N23)node[shift={{(0,0.2)}}](B){{\\({D}\\)}}
(N32)node[shift={{(0,-1.5)}}](C){{\\({E}\\)}}
(N43)node[shift={{(0,0.2)}}](D){{\\({F}\\)}}
(N52)node[shift={{(0,-0.2)}}](E){{\\(+\\infty\\)}}"""
    else:  # pattern == "type2"
        # Dạng 2: +, 0, -, 0, +, 0, - (Cực đại - Cực tiểu - Cực đại nhưng xu hướng ngược)
        sign_line = ",".join(["+", "0", "-", "0", "+", "0", "-"])
        # Điều chỉnh vị trí node để phù hợp với dạng 2
        node_positions = f"""
(N13)node[shift={{(0,0.2)}}](A){{\\(+\\infty\\)}}
(N22)node[shift={{(0,-0.2)}}](B){{\\({D}\\)}}
(N32)node[shift={{(0,-1.5)}}](C){{\\({E}\\)}}
(N42)node[shift={{(0,-0.2)}}](D){{\\({F}\\)}}
(N53)node[shift={{(0,0.2)}}](E){{\\(+\\infty\\)}}"""
    
    return f"""
\\begin{{tikzpicture}}[>=stealth, scale=1]
\\tkzTabInit[lgt=2,espcl=2]
{{\\(x\\)/1,\\(f'(x)\\)/0.8,\\(f(x)\\)/3}}
{{{x_labels_str}}}
\\tkzTabLine{{{sign_line}}}
\\path{node_positions};
\\foreach\\X/\\Y in{{A/B,B/C,C/D,D/E}}\\draw[->](\\X)--(\\Y);
\\end{{tikzpicture}}
"""

def generate_tikzpicture_latex(params):
    """
    Sinh LaTeX cho đồ thị tikzpicture với các tham số truyền vào.
    params: dict chứa A, B, C, D, E, F (số nguyên), etc.
    """
    A, B, C = params["A"], params["B"], params["C"]  # Điểm cực trị
    D, E, F = params["D"], params["E"], params["F"]  # Giá trị cực trị
    
    return f"""
\\begin{{tikzpicture}}[line join=round, line cap=round,>=stealth,scale=1]
\\tikzset{{label style/.style={{font=\\footnotesize}}}}
\\draw[->] (-2.1,0)--(2.5,0) node[below right] {{\\(x\\)}};
\\draw[->] (0,-3.1)--(0,2.1) node[below left] {{\\(y\\)}};
\\draw (0,0) node [below right] {{\\(O\\)}}circle(1.5pt);

% Đánh dấu các điểm cực trị
\\draw[dashed,thin](-1,0)--(-1,1)--(0,1);
\\draw[dashed,thin](1,0)--(1,-3)--(0,-3);
\\draw (1,0) node[above]{{\\( {B} \\)}}; 
\\draw (-1,0) node[below]{{\\( {A} \\)}};
\\draw (0,-3) node[left]{{\\( {E} \\)}};
\\draw (0,1) node[right]{{\\( {D} \\)}};

% Vẽ đường cong hàm số (ví dụ đơn giản)
\\begin{{scope}}
\\clip (-2,-3) rectangle (2,2);
\\draw[samples=200,domain=-2:2,smooth,variable=\\x] plot (\\x,{{(\\x)^3-3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

def generate_cubic_type1_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 3 loại 1 (như Câu 3 trong 1200k.tex)
    Cực đại trước, cực tiểu sau: x^3 - 3x - 1
    params: dict chứa A, B (điểm cực trị), D, E (giá trị cực trị), m (offset)
    """
    A = params["A"]  # x của cực đại (âm)
    B = params["B"]  # x của cực tiểu (dương) 
    D = params["D"]  # y của cực đại (dương)
    E = params["E"]  # y của cực tiểu (âm)
    m = params.get("m", 0)  # offset cho điểm B
    B_offset = B + m  # tính toán trước
    
    return f"""
\\begin{{tikzpicture}}[line join=round, line cap=round,>=stealth,scale=1]
\\tikzset{{label style/.style={{font=\\footnotesize}}}}
\\draw[->] (-2.1,0)--(2.5,0) node[below right] {{\\(x\\)}};
\\draw[->] (0,-3.1)--(0,2.1) node[below left] {{\\(y\\)}};
\\draw (0,0) node [below right] {{\\(O\\)}}circle(1.5pt);

% Đánh dấu các điểm cực trị
\\draw[dashed,thin]({A},0)--({A},{D})--(0,{D});
\\draw[dashed,thin]({B_offset},0)--({B_offset},{E})--(0,{E});
\\draw ({B_offset},0) node[above]{{\\( {B}+m \\)}}; 
\\draw ({A},0) node[below]{{\\( {A} \\)}};
\\draw (0,{E}) node[left]{{\\( {E} \\)}};
\\draw (0,{D}) node[right]{{\\( {D} \\)}};

% Vẽ đường cong hàm số bậc 3 loại 1
\\begin{{scope}}
\\clip (-2,-3) rectangle (2,2);
\\draw[samples=200,domain=-2:2,smooth,variable=\\x] plot (\\x,{{(\\x)^3-3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

def generate_cubic_type2_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 3 loại 2 (như Câu 4 trong 1200k.tex)
    Cực tiểu trước, cực đại sau: -x^3 + 3x - 1
    params: dict chứa A, B (điểm cực trị), D, E (giá trị cực trị), m (offset)
    """
    A = params["A"]  # x của cực tiểu (âm)
    B = params["B"]  # x của cực đại (dương)
    D = params["D"]  # y của cực tiểu (âm)  
    E = params["E"]  # y của cực đại (dương)
    m = params.get("m", 0)  # offset cho điểm B
    B_offset = B + m  # tính toán trước
    
    return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-2.5,0)--(3.5,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[below left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị
\\draw[fill=black] ({A},0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] ({B_offset},0) circle (1pt) node[below] {{\\({B}+m\\)}};
\\draw[fill=black] (0,{E}) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,{D}) circle (1pt) node[below left] {{\\({D}\\)}};

% Đường kẻ phụ
\\draw[dashed] ({A},0)--({A},{D})--({B_offset},{D})--({B_offset},0);
\\draw[dashed] (-2,0)--(-2,{E})--({B},{E})--({B},0);

% Vẽ đường cong hàm số bậc 3 loại 2 (ngược)
\\begin{{scope}}
\\clip (-2.5,-3.5) rectangle (3.5,2.5);
\\draw[smooth,samples=100,domain=-2.5:3.5] plot(\\x,{{-1*(\\x)^3+3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

def generate_quartic_latex(params):
    """
    Sinh LaTeX cho đồ thị hàm bậc 4 (như Câu 5 trong 1200k.tex)
    Cực đại giữa, 2 cực tiểu hai bên: x^4 - 2x^2 - 2
    params: dict chứa A, C (điểm cực tiểu), B=0 (điểm cực đại), D, E, F (giá trị)
    """
    A = params["A"]  # x của cực tiểu trái (âm)
    C = params["C"]  # x của cực tiểu phải (dương) 
    D = params["D"]  # y của cực tiểu (âm, giống F)
    E = params["E"]  # y của cực đại (âm nhưng cao hơn D)
    
    return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-3,0)--(3,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[above left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị
\\draw[fill=black] ({A},0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] ({C},0) circle (1pt) node[below] {{\\({C}\\)}};
\\draw[fill=black] (0,{E}) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,-3) circle (1pt);
\\draw[fill=black] (0,-3.12) node[above left] {{\\({D}\\)}};

% Đường kẻ phụ  
\\draw[dashed] ({A},0)--({A},{D})--({C},{D})--({C},0);

% Vẽ đường cong hàm số bậc 4
\\begin{{scope}}
\\clip (-2,-3.5) rectangle (2,3.25);
\\draw[smooth,samples=100,domain=-1.8:1.8] plot(\\x,{{(\\x)^4-2*(\\x)^2-2}});
\\end{{scope}}
\\end{{tikzpicture}}
"""
