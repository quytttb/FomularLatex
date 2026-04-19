import sys
with open('/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py', 'r') as f:
    text = f.read()

# Replace prefix and append
old_append = """            prefix = "*" if is_true else ""
            question_lines.append(f"{prefix}{option_labels[idx]}) {text}")"""
new_append = """            prefix = "* " if is_true else ""
            question_lines.append(f"{{{prefix}{text}}}")"""
text = text.replace(old_append, new_append)

# Replace solution start
old_sol = "        solutions: List[str] = [\"Lời giải.\"]"
new_sol = "        solutions: List[str] = []"
text = text.replace(old_sol, new_sol)

# Replace final content structure
old_content = """        question_body = "\\n\\n".join(question_lines)
        solution_text = "\\n\\n".join(solutions)

        content = (
            f"Câu {question_number}: Chọn các mệnh đề đúng.\\n\\n"
            f"{question_body}\\n\\n{solution_text}\\n"
        )"""
new_content = """        question_body = "\\\\choiceTFt\\n" + "\\n".join(question_lines)
        solution_text = "\\\\loigiai{\\n" + "\\n\\n".join(solutions) + "\\n}"

        content = (
            f"\\\\begin{{ex}}\\n"
            f"\\\\textbf{{Câu {question_number}.}} Chọn các mệnh đề đúng.\\n\\n"
            f"{question_body}\\n\\n{solution_text}\\n"
            f"\\\\end{{ex}}\\n"
        )"""
text = text.replace(old_content, new_content)

# Replace LaTeXTemplate
old_template = """class LaTeXTemplate:
    DOCUMENT_HEADER = r\"\"\"\\documentclass[a4paper,12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{polyglossia}}
\\setmainlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage{{tikz}}
\\begin{{document}}
\\title{{{title}}}
\\author{{{author}}}
\\maketitle

\"\"\""""
new_template = """class LaTeXTemplate:
    DOCUMENT_HEADER = r\"\"\"\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{polyglossia}}
\\setdefaultlanguage{{vietnamese}}
\\setmainfont{{Times New Roman}}
\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{{geometry}}
\\usepackage[solcolor]{{ex_test}}
\\usepackage{{tikz}}
\\begin{{document}}
\\title{{{title}}}
\\author{{{author}}}
\\maketitle

\"\"\""""
text = text.replace(old_template, new_template)

with open('/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py', 'w') as f:
    f.write(text)

