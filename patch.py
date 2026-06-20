import sys

def patch_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Part 1: Replace create_latex_document and add create_latex_document_with_format
    old_meth = r'''    @staticmethod
    def create_latex_document(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        latex_content = r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{tikz}
\usepackage{tkz-tab}
\usepackage{tkz-euclide}
\usetikzlibrary{calc,decorations.pathmorphing,decorations.pathreplacing}
\begin{document}
\title{""" + title + r"""}
\maketitle

"""
        if fmt == 1:
            latex_content += "\n\n".join(questions_data)
        else:
            # fmt == 2: in đề bài trước, in đáp án ở cuối trang mới
            questions = []
            answers = []
            for i, (q_text, ans) in enumerate(questions_data, 1):
                questions.append(q_text)
                answers.append(f"Câu {i}: {ans}")
            
            latex_content += "\n\n".join(questions)
            latex_content += "\n\n\\newpage\n\\section*{Đáp án}\n"
            latex_content += "\n\n".join(answers)
            
        latex_content += "\n\\end{document}"
        return latex_content'''

    new_meth = r'''    @staticmethod
    def create_latex_document(questions: List[str], title: str = "Câu hỏi Tối ưu hóa") -> str:
        """Tạo document LaTeX hoàn chỉnh"""
        latex_content = f"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usepackage{{tkz-tab}}
\usepackage{{tkz-euclide}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\begin{{document}}
\title{{{title}}}
\maketitle

"""
        latex_content += "\n\n".join(questions)
        latex_content += "\n\\end{document}"
        return latex_content

    @staticmethod
    def create_latex_document_with_format(questions_data: List, title: str = "Câu hỏi Tối ưu hóa", fmt: int = 1) -> str:
        """Tạo document LaTeX với format cụ thể"""
        latex_content = f"""\documentclass[a4paper,12pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{fontspec}}
\usepackage{{tikz}}
\usepackage{{tkz-tab}}
\usepackage{{tkz-euclide}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\begin{{document}}
\title{{{title}}}
\maketitle

"""
        for question_data in questions_data:
            latex_content += f"{question_data}\n\n"
        latex_content += "\n\\end{document}"
        return latex_content'''

    content = content.replace(old_meth, new_meth)

    # Part 2: update main() logic
    old_main_gen = r'''        # Tạo file LaTeX
        latex_content = ExtremumFromTikzQuestion.create_latex_document(questions_data, "Câu hỏi Tối ưu hóa", fmt)'''
    
    new_main_gen = r'''        # Tạo file LaTeX
        if fmt == 1:
            latex_content = ExtremumFromTikzQuestion.create_latex_document(questions_data, "Câu hỏi Tối ưu hóa")
        else:
            latex_content = ExtremumFromTikzQuestion.create_latex_document_with_format(questions_data, "Câu hỏi Tối ưu hóa", fmt)'''

    content = content.replace(old_main_gen, new_main_gen)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Patched successfully")

patch_file('/home/haiquy/Documents/Projects/FomularLatex/2025/src/cuc_tri_don_dieu_tu_do_thi_bbt.py')
