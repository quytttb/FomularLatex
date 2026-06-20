"""
OPTIMIZATION QUESTIONS GENERATOR
Optimized version - Removed redundant utilities and streamlined style styles.
"""

import logging
import random
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#================================================================================
# TIKZ_FIGURE_LIBRARY.PY
#================================================================================

"""
Thư viện hình vẽ TikZ cho hệ thống sinh câu hỏi toán tối ưu hóa
Tách từ math_template.py - PHẦN 2
"""
def generate_tikz_latex(style: str, params: Dict[str, Any]) -> str:
    """
    Sinh LaTeX đồ thị/bảng biến thiên hợp nhất dựa trên kiểu (style) và tham số truyền vào
    """
    if style == "tkztab":
        A, B, C = params["A"], params["B"], params["C"]
        D, E, F = params["D"], params["E"], params["F"]
        pattern = params.get("pattern", "type1")
        if pattern == "type1":
            return f"""
\\begin{{tikzpicture}}[scale=0.8]
\\tkzTabInit[lgt=1.2,espcl=2.5]
{{\\(x\\)/0.8,\\(f'(x)\\)/0.8,\\(f(x)\\)/2}}
{{$-\\infty$,\\({A}\\),\\({B}\\),\\({C}\\),$+\\infty$}}
\\tkzTabLine{{,-,$0$,+,$0$,-,$0$,+,}}
\\tkzTabVar{{+/$+\\infty$, -/\\({D}\\), +/\\({E}\\), -/\\({F}\\), +/$+\\infty$}}
\\end{{tikzpicture}}
"""
        else:
            return f"""
\\begin{{tikzpicture}}[scale=0.8]
\\tkzTabInit[lgt=1.2,espcl=2.5]
{{\\(x\\)/0.8,\\(f'(x)\\)/0.8,\\(f(x)\\)/2}}
{{$-\\infty$,\\({A}\\),\\({B}\\),\\({C}\\),$+\\infty$}}
\\tkzTabLine{{,+, $0$, -, $0$, +, $0$, -,}}
\\tkzTabVar{{-/$-\\infty$, +/\\({D}\\), -/\\({E}\\), +/\\({F}\\), -/$-\\infty$}}
\\end{{tikzpicture}}
"""

    elif style == "cubic_type1":
        A, B, D, E = params["A"], params["B"], params["D"], params["E"]
        B_offset = B + params.get("m", 0)
        return f"""
\\begin{{tikzpicture}}[line join=round, line cap=round,>=stealth,scale=1]
\\tikzset{{label style/.style={{font=\\footnotesize}}}}
\\draw[->] (-2.1,0)--(2.5,0) node[below right] {{\\(x\\)}};
\\draw[->] (0,-3.1)--(0,2.1) node[below left] {{\\(y\\)}};
\\draw (0,0) node [below right] {{\\(O\\)}}circle(1.5pt);

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed,thin](-1,0)--(-1,1)--(0,1);
\\draw[dashed,thin](1,0)--(1,-3)--(0,-3);
\\draw (1,0) node[above]{{\\( {B_offset} \\)}}; 
\\draw (-1,0) node[below]{{\\( {A} \\)}};
\\draw (0,-3) node[left]{{\\( {E} \\)}};
\\draw (0,1) node[right]{{\\( {D} \\)}};

% Vẽ đường cong hàm số bậc 3 loại 1
\\begin{{scope}}
\\clip (-2,-3) rectangle (2,2);
\\draw[samples=200,domain=-2:2,smooth,variable=\\x] plot (\\x,{{(\\x)^3-3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

    elif style == "cubic_type2":
        A, B, D, E = params["A"], params["B"], params["D"], params["E"]
        B_offset = B + params.get("m", 0)
        return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-2.5,0)--(3.5,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[below left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[fill=black] (-1,0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] (1,0) circle (1pt) node[below] {{\\({B_offset}\\)}};
\\draw[fill=black] (0,1) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,-3) circle (1pt) node[below left] {{\\({D}\\)}};

% Đường kẻ phụ - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed] (-1,0)--(-1,-3)--(2,-3)--(2,0);
\\draw[dashed] (-2,0)--(-2,1)--(1,1)--(1,0);

% Vẽ đường cong hàm số bậc 3 loại 2 (ngược)
\\begin{{scope}}
\\clip (-2.5,-3.5) rectangle (3.5,2.5);
\\draw[smooth,samples=100,domain=-2.5:3.5] plot(\\x,{{-1*(\\x)^3+3*(\\x)-1}});
\\end{{scope}}
\\end{{tikzpicture}}
"""

    elif style == "quartic":
        A, C, D, E = params["A"], params["C"], params["D"], params["E"]
        return f"""
\\begin{{tikzpicture}}[scale=1, font=\\footnotesize, line join=round, line cap=round, >=stealth]
\\draw[->] (-3,0)--(3,0) node[below] {{\\(x\\)}};
\\draw[->] (0,-3.5)--(0,2.5) node[left] {{\\(y\\)}};
\\draw[fill=black] (0,0) circle (1pt) node[above left=-2pt] {{\\(O\\)}};

% Đánh dấu các điểm cực trị - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[fill=black] (-1,0) circle (1pt) node[below] {{\\({A}\\)}};
\\draw[fill=black] (1,0) circle (1pt) node[below] {{\\({C}\\)}};
\\draw[fill=black] (0,-2) circle (1pt) node[above left] {{\\({E}\\)}};
\\draw[fill=black] (0,-3) circle (1pt);
\\draw[fill=black] (0,-3.12) node[above left] {{\\({D}\\)}};

% Đường kẻ phụ - VỊ TRÍ TRÊN HÌNH VẼ CỐ ĐỊNH
\\draw[dashed] (-1,0)--(-1,-3)--(1,-3)--(1,0);

% Vẽ đường cong hàm số bậc 4
\\begin{{scope}}
\\clip (-2,-3.5) rectangle (2,3.25);
\\draw[smooth,samples=100,domain=-1.8:1.8] plot(\\x,{{(\\x)^4-2*(\\x)^2-2}});
\\end{{scope}}
\\end{{tikzpicture}}
"""
    return ""


#================================================================================
# EXTREMUM_FROM_TIKZ.PY
#================================================================================

"""
Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu của hàm số dựa trên bảng biến thiên (tkzTabInit) hoặc đồ thị (tikzpicture).
"""


class ExtremumFromTikzQuestion:
    """
    Dạng toán nhận diện cực trị, giá trị cực trị, điểm cực trị, hoặc tính đơn điệu
    Dựa trên bảng biến thiên hoặc đồ thị hàm số (tkzTabInit hoặc tikzpicture)
    """
    # Danh sách các câu hỏi dạng cực trị, loại bỏ trùng lặp
    QUESTION_TEMPLATES = [
        "Hàm số đạt cực trị tại điểm nào?",
        "Hàm số đạt cực đại tại điểm nào?",
        "Hàm số đạt cực tiểu tại điểm nào?",
        "Hàm số có cực đại là giá trị nào?",
        "Hàm số có cực tiểu là giá trị nào?",
        "Đồ thị hàm số có điểm cực đại là điểm nào?",
        "Đồ thị hàm số có điểm cực tiểu là điểm nào?",
        "Hàm số đồng biến trên khoảng nào dưới đây?",
        "Hàm số nghịch biến trên khoảng nào dưới đây?"
    ]

    def __init__(self):
        self.parameters = {}
        self.correct_answer = None
        self.wrong_answers = []

    def generate_full_question(self, question_number: int = 1) -> str:
        """Tạo câu hỏi hoàn chỉnh với 4 đáp án A/B/C/D"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        self.wrong_answers = self.generate_wrong_answers()
        question_text = self.generate_question_text()
        all_answers = [self.correct_answer] + self.wrong_answers
        random.shuffle(all_answers)
        correct_index = all_answers.index(self.correct_answer)
        question_content = f"Câu {question_number}: {question_text}\n\n"
        for j, ans in enumerate(all_answers):
            letter = chr(65 + j)
            marker = "*" if j == correct_index else ""
            question_content += f"{marker}{letter}. {ans}\n\n"
        return question_content

    def generate_question_only(self, question_number: int = 1) -> Tuple[str, str]:
        """Tạo câu hỏi chỉ có đề bài"""
        logging.info(f"Đang tạo câu hỏi {question_number}")
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        question_content = f"Câu {question_number}: {question_text}\n\n"
        return question_content, self.correct_answer

    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        latex_content += "\n\n".join(questions)
        latex_content += "\n\\end{document}"
        return latex_content

    @staticmethod
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với 2 format khác nhau"""
        latex_content = f"""\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{fontspec}}
\\usepackage{{tikz}}
\\usepackage{{tkz-tab}}
\\usepackage{{tkz-euclide}}
\\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\\begin{{document}}
\\title{{{title}}}
\\maketitle

"""
        if fmt == 1:
            # Format 1: In trực tiếp nội dung từng câu (bao gồm 4 đáp án A B C D)
            for question_data in questions_data:
                # Tránh lỗi nếu parse có tuple, fallback lấy phần tử đầu 
                if isinstance(question_data, tuple):
                    latex_content += f"{question_data[0]}\n\n"
                else:
                    latex_content += f"{question_data}\n\n"
        else:
            # Format 2: In hết câu hỏi không đáp án A B C D, đáp án gom xuống cuối
            correct_answers = []
            for question_data in questions_data:
                if isinstance(question_data, tuple):
                    question_content, correct_answer = question_data
                    latex_content += question_content.strip() + "\n\n"
                    correct_answers.append(correct_answer)
                else:
                    latex_content += str(question_data) + "\n\n"

            latex_content += "Đáp án\n\n"
            for idx, answer in enumerate(correct_answers, 1):
                ans = str(answer).strip()
                # Loại bỏ ký hiệu LaTeX \(\) hoặc $$ khi xuất ra đáp án ở cuối
                if ans.startswith("\\(") and ans.endswith("\\)"):
                    ans = ans[2:-2].strip()
                elif ans.startswith("$") and ans.endswith("$"):
                    ans = ans[1:-1].strip()

                # Định dạng số thập phân tự động dấu chấm / phẩy
                if ',' in ans:
                    ans_dot = ans.replace(',', '.')
                    latex_content += f"{idx}. {ans}|{ans_dot}\n\n"
                else:
                    latex_content += f"{idx}. {ans}\n\n"

        latex_content += "\n\\end{document}"
        return latex_content

    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số cho bài toán cực trị từ bảng biến thiên hoặc đồ thị"""
        # Chọn kiểu thể hiện trước để sinh tham số phù hợp
        style = random.choice(['tkztab', 'cubic_type1', 'cubic_type2', 'quartic'])
        
        if style == 'tkztab':
            # Bảng biến thiên - sinh như cũ nhưng chuẩn hóa toán học
            pattern = random.choice(['type1', 'type2'])
            A = random.randint(-4, -1)
            B = random.randint(0, 2)
            C = random.randint(3, 6)
            
            if pattern == 'type1':  # W shape
                D = random.randint(-5, 0)
                F = random.randint(-5, 0)
                E = random.randint(1, 5)
            else:  # M shape
                D = random.randint(1, 5)
                F = random.randint(1, 5)
                E = random.randint(-5, 0)
            m = 0
            
        elif style in ['cubic_type1', 'tikzpicture']:
            # Cubic type 1: A âm (cực đại), B dương (cực tiểu)
            A = random.randint(-3, -1)  # x cực đại (âm)
            B = random.randint(1, 2)    # x cực tiểu (dương)
            m = random.randint(1, 3)    # offset
            D = random.randint(1, 4)    # y cực đại (dương)
            E = random.randint(-4, -1)  # y cực tiểu (âm)
            C = 0
            F = 0
            pattern = 'type1'
            
        elif style == 'cubic_type2':
            # Cubic type 2: A âm (cực tiểu), B dương (cực đại)
            A = random.randint(-3, -1)  # x cực tiểu (âm)
            B = random.randint(1, 2)    # x cực đại (dương)
            m = random.randint(1, 3)    # offset
            D = random.randint(-4, -1)  # y cực tiểu (âm)
            E = random.randint(1, 4)    # y cực đại (dương)
            C = 0
            F = 0
            pattern = 'type2'
            
        else:  # quartic
            # Quartic: A âm (cực tiểu trái), C dương (cực tiểu phải), 0 (cực đại)
            A = random.randint(-3, -1)  # x cực tiểu trái (âm)
            C = random.randint(1, 3)     # x cực tiểu phải (dương)
            D = random.randint(-4, -2)   # y cực tiểu (âm)
            E = random.randint(-1, 1)    # y cực đại (cao hơn D)
            B = 0
            F = 0
            m = 0
            pattern = 'type1'
        
        # Sinh thêm các giá trị ngẫu nhiên khác để làm đáp án nhiễu
        all_x = [A, B, B + m, C, 0]
        all_y = [D, E, F]
        extra_x = random.sample([i for i in range(-15, 16) if i not in all_x], 6)
        extra_y = random.sample([i for i in range(-15, 16) if i not in all_y and i != 0], 6)
        
        return {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "pattern": pattern,
            "extra_x": extra_x,
            "extra_y": extra_y,
            "style": style,
            "m": m
        }

    def generate_question_text(self) -> str:
        """Sinh đề bài bằng LaTeX, random chọn bảng biến thiên hoặc đồ thị"""
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        
        # Gọi hàm sinh TikZ hợp nhất
        figure = generate_tikz_latex(p["style"], p)
        intro = "Cho hàm số \\(y=f(x)\\) có bảng biến thiên như dưới đây:" if p["style"] == "tkztab" else "Cho đồ thị hàm số \\(y=f(x)\\) có đồ thị như hình vẽ dưới đây:"
        
        if not hasattr(self, '_current_question'):
            self._current_question = random.choice(self.QUESTION_TEMPLATES)
        question = self._current_question
        
        return f"""{intro}

{figure}

{question}"""

    def _solve_question(self, q: str, p: Dict[str, Any]) -> Tuple[str, List[str]]:
        style = p["style"]
        A, B, C = p["A"], p["B"], p["C"]
        D, E, F = p["D"], p["E"], p["F"]
        extra_x = p["extra_x"]
        extra_y = p["extra_y"]
        m = p.get("m", 0)
        B_actual = B + m
        
        # Xác định từ khóa câu hỏi
        q_key = None
        if "cực trị tại điểm" in q: q_key = "cuc_tri"
        elif "cực đại tại điểm" in q: q_key = "cuc_dai"
        elif "cực tiểu tại điểm" in q: q_key = "cuc_tieu"
        elif "cực đại là giá trị" in q: q_key = "val_cuc_dai"
        elif "cực tiểu là giá trị" in q: q_key = "val_cuc_tieu"
        elif "điểm cực đại" in q: q_key = "pt_cuc_dai"
        elif "điểm cực tiểu" in q: q_key = "pt_cuc_tieu"
        elif "đồng biến" in q: q_key = "dong_bien"
        elif "nghịch biến" in q: q_key = "nghich_bien"
        
        # Bản đồ cấu hình đáp án (correct, wrongs) cho từng kiểu thể hiện
        config = {}
        pattern = p.get("pattern", "type1")
        if style == "tkztab":
            if pattern == "type1":  # W shape
                config = {
                    "cuc_tri": (f"\\(x={B}\\)", [f"\\(x={D}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                    "cuc_dai": (f"\\(x={B}\\)", [f"\\(x={A}\\)", f"\\(x={C}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)"]),
                    "cuc_tieu": (f"\\(x={A}\\)", [f"\\(x={B}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                    "val_cuc_dai": (f"\\(y={E}\\)", [f"\\(y={D}\\)", f"\\(y={F}\\)", f"\\(y={B}\\)", f"\\(y={extra_y[0]}\\)"]),
                    "val_cuc_tieu": (f"\\(y={D}\\)", [f"\\(y={E}\\)", f"\\(y={B}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                    "pt_cuc_dai": (f"\\(({B},{E})\\)", [f"\\(({A},{D})\\)", f"\\(({C},{F})\\)", f"\\(({E},{B})\\)", f"\\(({B},{D})\\)"]),
                    "pt_cuc_tieu": (f"\\(({A},{D})\\)", [f"\\(({B},{E})\\)", f"\\(({D},{A})\\)", f"\\(({C},{E})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                    "dong_bien": (f"\\(({A};{B})\\)", [f"\\((-\\infty;{A})\\)", f"\\(({B};{C})\\)", f"\\(({A};{C})\\)", f"\\(({B};+\\infty)\\)"]),
                    "nghich_bien": (f"\\(({B};{C})\\)", [f"\\(({A};{B})\\)", f"\\(({C};+\\infty)\\)", f"\\(({A};{C})\\)", f"\\((-\\infty;{B})\\)"])
                }
            else:  # M shape
                config = {
                    "cuc_tri": (f"\\(x={B}\\)", [f"\\(x={D}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                    "cuc_dai": (f"\\(x={A}\\)", [f"\\(x={B}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                    "cuc_tieu": (f"\\(x={B}\\)", [f"\\(x={A}\\)", f"\\(x={C}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)"]),
                    "val_cuc_dai": (f"\\(y={D}\\)", [f"\\(y={E}\\)", f"\\(y={B}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                    "val_cuc_tieu": (f"\\(y={E}\\)", [f"\\(y={D}\\)", f"\\(y={F}\\)", f"\\(y={B}\\)", f"\\(y={extra_y[0]}\\)"]),
                    "pt_cuc_dai": (f"\\(({A},{D})\\)", [f"\\(({B},{E})\\)", f"\\(({D},{A})\\)", f"\\(({C},{E})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                    "pt_cuc_tieu": (f"\\(({B},{E})\\)", [f"\\(({A},{D})\\)", f"\\(({C},{F})\\)", f"\\(({E},{B})\\)", f"\\(({B},{D})\\)"]),
                    "dong_bien": (f"\\(({B};{C})\\)", [f"\\(({A};{B})\\)", f"\\(({C};+\\infty)\\)", f"\\(({A};{C})\\)", f"\\((-\\infty;{B})\\)"]),
                    "nghich_bien": (f"\\(({A};{B})\\)", [f"\\((-\\infty;{A})\\)", f"\\(({B};{C})\\)", f"\\(({A};{C})\\)", f"\\(({B};+\\infty)\\)"])
                }
        elif style == "cubic_type1":
            config = {
                "cuc_tri": (f"\\(x={A}\\)", [f"\\(x={D}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "cuc_dai": (f"\\(x={A}\\)", [f"\\(x={B_actual}\\)", f"\\(x={D}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "cuc_tieu": (f"\\(x={B_actual}\\)", [f"\\(x={A}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "val_cuc_dai": (f"\\(y={D}\\)", [f"\\(y={E}\\)", f"\\(y={A}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "val_cuc_tieu": (f"\\(y={E}\\)", [f"\\(y={D}\\)", f"\\(y={B_actual}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "pt_cuc_dai": (f"\\(({A},{D})\\)", [f"\\(({B_actual},{E})\\)", f"\\(({D},{A})\\)", f"\\(({A},{E})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "pt_cuc_tieu": (f"\\(({B_actual},{E})\\)", [f"\\(({A},{D})\\)", f"\\(({E},{B_actual})\\)", f"\\(({B_actual},{D})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "dong_bien": (f"\\(({B_actual};+\\infty)\\)", [f"\\(({A};{B_actual})\\)", f"\\(({A};+\\infty)\\)", f"\\((-\\infty;{B_actual})\\)", f"\\(({A}-1;{B_actual}+1)\\)"]),
                "nghich_bien": (f"\\(({A};{B_actual})\\)", [f"\\((-\\infty;{A})\\)", f"\\(({B_actual};+\\infty)\\)", f"\\((-\\infty;{B_actual})\\)", f"\\(({A}-1;{B_actual}+1)\\)"])
            }
        elif style == "cubic_type2":
            config = {
                "cuc_tri": (f"\\(x={A}\\)", [f"\\(x={D}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "cuc_dai": (f"\\(x={B_actual}\\)", [f"\\(x={A}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "cuc_tieu": (f"\\(x={A}\\)", [f"\\(x={B_actual}\\)", f"\\(x={D}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "val_cuc_dai": (f"\\(y={E}\\)", [f"\\(y={D}\\)", f"\\(y={B_actual}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "val_cuc_tieu": (f"\\(y={D}\\)", [f"\\(y={E}\\)", f"\\(y={A}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "pt_cuc_dai": (f"\\(({B_actual},{E})\\)", [f"\\(({A},{D})\\)", f"\\(({E},{B_actual})\\)", f"\\(({B_actual},{D})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "pt_cuc_tieu": (f"\\(({A},{D})\\)", [f"\\(({B_actual},{E})\\)", f"\\(({D},{A})\\)", f"\\(({A},{E})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "dong_bien": (f"\\(({A};{B_actual})\\)", [f"\\((-\\infty;{A})\\)", f"\\(({B_actual};+\\infty)\\)", f"\\((-\\infty;{B_actual})\\)", f"\\(({A}-1;{B_actual}+1)\\)"]),
                "nghich_bien": (f"\\(({B_actual};+\\infty)\\)", [f"\\(({A};{B_actual})\\)", f"\\(({A};+\\infty)\\)", f"\\((-\\infty;{B_actual})\\)", f"\\(({A}-1;{B_actual}+1)\\)"])
            }
        else:  # quartic
            config = {
                "cuc_tri": (f"\\(x=0\\)", [f"\\(x={D}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "cuc_dai": (f"\\(x=0\\)", [f"\\(x={A}\\)", f"\\(x={C}\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)"]),
                "cuc_tieu": (f"\\(x={A}\\)", [f"\\(x=0\\)", f"\\(x={E}\\)", f"\\(x={extra_x[0]}\\)", f"\\(x={extra_x[1]}\\)"]),
                "val_cuc_dai": (f"\\(y={E}\\)", [f"\\(y={D}\\)", f"\\(y={A}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "val_cuc_tieu": (f"\\(y={D}\\)", [f"\\(y={E}\\)", f"\\(y={C}\\)", f"\\(y={extra_y[0]}\\)", f"\\(y={extra_y[1]}\\)"]),
                "pt_cuc_dai": (f"\\((0,{E})\\)", [f"\\(({A},{D})\\)", f"\\(({C},{D})\\)", f"\\(({E},0)\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "pt_cuc_tieu": (f"\\(({A},{D})\\)", [f"\\((0,{E})\\)", f"\\(({D},{A})\\)", f"\\(({C},{E})\\)", f"\\(({extra_x[0]},{extra_y[0]})\\)"]),
                "dong_bien": (f"\\(({A};0)\\)", [f"\\((-\\infty;{A})\\)", f"\\((0;{C})\\)", f"\\(({A};{C})\\)", f"\\((-\\infty;0)\\)"]),
                "nghich_bien": (f"\\((0;{C})\\)", [f"\\(({A};0)\\)", f"\\(({C};+\\infty)\\)", f"\\(({A};{C})\\)", f"\\((0;+\\infty)\\)"])
            }
        
        correct, wrongs = config.get(q_key, ("", []))

        # Tập hợp TẤT CẢ các đáp án đúng có thể có để loại trừ chúng khỏi danh sách sai
        all_corrects = [correct]
        if q_key == "cuc_tri":
            if style == "tkztab": all_corrects.extend([f"\\(x={A}\\)", f"\\(x={B}\\)", f"\\(x={C}\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(x={A}\\)", f"\\(x=0\\)", f"\\(x={C}\\)"])
            else: all_corrects.extend([f"\\(x={A}\\)", f"\\(x={B_actual}\\)"])
        elif q_key == "cuc_dai":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(x={B}\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(x={A}\\)", f"\\(x={C}\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(x=0\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(x={A}\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(x={B_actual}\\)"])
        elif q_key == "cuc_tieu":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(x={A}\\)", f"\\(x={C}\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(x={B}\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(x={A}\\)", f"\\(x={C}\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(x={B_actual}\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(x={A}\\)"])
        elif q_key == "val_cuc_dai":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(y={E}\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(y={D}\\)", f"\\(y={F}\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(y={E}\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(y={D}\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(y={E}\\)"])
        elif q_key == "val_cuc_tieu":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(y={D}\\)", f"\\(y={F}\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(y={E}\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(y={D}\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(y={E}\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(y={D}\\)"])
        elif q_key == "pt_cuc_dai":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(({B},{E})\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(({A},{D})\\)", f"\\(({C},{F})\\)"])
            elif style == "quartic": all_corrects.extend([f"\\((0,{E})\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(({A},{D})\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(({B_actual},{E})\\)"])
        elif q_key == "pt_cuc_tieu":
            if style == "tkztab" and pattern == "type1": all_corrects.extend([f"\\(({A},{D})\\)", f"\\(({C},{F})\\)"])
            elif style == "tkztab" and pattern == "type2": all_corrects.extend([f"\\(({B},{E})\\)"])
            elif style == "quartic": all_corrects.extend([f"\\(({A},{D})\\)", f"\\(({C},{D})\\)"])
            elif style == "cubic_type1": all_corrects.extend([f"\\(({B_actual},{E})\\)"])
            elif style == "cubic_type2": all_corrects.extend([f"\\(({A},{D})\\)"])

        # Lọc đáp án sai
        unique_wrongs = []
        for w in wrongs:
            if w not in all_corrects and w not in unique_wrongs:
                unique_wrongs.append(w)
        
        # Bổ sung nếu thiếu (sử dụng extra_x, extra_y)
        idx = 2  # Bắt đầu từ 2 do 0, 1 có thể đã dùng ở config
        while len(unique_wrongs) < 3 and idx < len(extra_x):
            if "điểm" in q and "cực" in q:
                new_w = f"\\(({extra_x[idx]},{extra_y[idx]})\\)"
            elif "giá trị" in q or "y=" in correct:
                new_w = f"\\(y={extra_y[idx]}\\)"
            elif "khoảng" in q or ";" in correct:
                new_w = f"\\(({extra_x[idx]};{extra_x[idx]+1})\\)"
            else:
                new_w = f"\\(x={extra_x[idx]}\\)"
                
            if new_w not in all_corrects and new_w not in unique_wrongs:
                unique_wrongs.append(new_w)
            idx += 1
                
        return correct, random.sample(unique_wrongs, 3)

    def calculate_answer(self) -> str:
        """Tính đáp án đúng dựa trên tham số và câu hỏi"""
        # Đảm bảo parameters đã được khởi tạo
        if not self.parameters:
            self.parameters = self.generate_parameters()
            
        p = self.parameters
        # Lưu trữ câu hỏi hiện tại để có thể phân tích
        if not hasattr(self, '_current_question'):
            self._current_question = random.choice(self.QUESTION_TEMPLATES)
        q = self._current_question
        
        correct, wrongs = self._solve_question(q, p)
        self._computed_wrongs = wrongs
        return correct

    def generate_wrong_answers(self) -> List[str]:
        """Sinh đáp án sai (nhiễu) dựa trên câu hỏi hiện tại"""
        if not hasattr(self, '_computed_wrongs'):
            self.calculate_answer()
        return self._computed_wrongs

 

# Alias để tương thích với naming convention
ExtremumFromTikz = ExtremumFromTikzQuestion

#================================================================================
# MAIN_RUNNER.PY
#================================================================================

#!/usr/bin/env python3
"""
MAIN FUNCTION để chạy hệ thống tối ưu hóa
"""

import sys
import os

def main():
    """
    Hàm main để chạy generator với hỗ trợ 2 format
    Cách sử dụng:
    python cuc_tri_don_dieu_tu_do_thi_bbt.py [số_câu] [format]
    """
    try:
        # Lấy tham số từ command line
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        fmt = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] in ['1', '2'] else 1

        # Tạo câu hỏi
        questions_data = []

        for i in range(1, num_questions + 1):
            try:
                question_instance = ExtremumFromTikzQuestion()
                if fmt == 1:
                    question = question_instance.generate_full_question(i)
                    questions_data.append(question)
                else:
                    question_content, correct_answer = question_instance.generate_question_only(i)
                    questions_data.append((question_content, correct_answer))
                logging.info(f"Đã tạo thành công câu hỏi {i}")
            except Exception as e:
                logging.error(f"Lỗi tạo câu hỏi {i}: {e}")
                continue

        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)

        # Tạo file LaTeX
        if fmt == 1:
            latex_content = ExtremumFromTikzQuestion.create_latex_document(questions_data, "Câu hỏi Tối ưu hóa")
        else:
            latex_content = ExtremumFromTikzQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Tối ưu hóa", fmt)

        # Tự động lấy tên file script chạy để làm output tex
        filename = os.path.basename(__file__).replace(".py", ".tex")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)

        print(f"Đã tạo thành công {filename} với {len(questions_data)} câu hỏi")
        print(f"Biên dịch bằng: xelatex {filename}")
        print(f"Format: {fmt} ({'có A B C D' if fmt == 1 else 'đáp án ở cuối'})")

    except ValueError:
        print("Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

