import sys

def modify_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. modify LaTeXTemplate to replace \choiceTFt usage and add \heva
    content = content.replace(
        r"\usepackage[solcolor]{ex_test}",
        r"\usepackage[solcolor]{ex_test}" + "\n\\newcommand{\\heva}[1]{\\left\\{\\begin{aligned}#1\\end{aligned}\\right.}"
    )

    # 2. modified generation of question_lines
    ol_str = '''            prefix = "* " if is_true else ""
            question_lines.append(f"{{{prefix}{text}}}")'''
    
    new_str = '''            prefix = "*" if is_true else ""
            label_letter = ["a", "b", "c", "d"][idx]
            question_lines.append(f"{prefix}{label_letter}) {text}")'''
    
    content = content.replace(ol_str, new_str)
    
    # 3. Modify question_body
    qb_old = '''        question_body = "\\choiceTFt\\n" + "\\n".join(question_lines)
        solution_text = "\\loigiai{\\n" + "\\n\\n".join(solutions) + "\\n}"

        content = (
            f"\\\\begin{{ex}}\\n"
            f"\\\\textbf{{Câu {question_number}.}} Chọn các mệnh đề đúng.\\n\\n"
            f"{question_body}\\n\\n{solution_text}\\n"
            f"\\\\end{{ex}}\\n"
        )'''
    
    qb_new = '''        question_body = "\\n\\n".join(question_lines)
        solution_text = "\\\\loigiai{\\n" + "\\n\\n".join(solutions) + "\\n}"

        content = (
            f"\\\\begin{{ex}}%Câu {question_number}\\n"
            f"Chọn các mệnh đề đúng.\\n\\n"
            f"{question_body}\\n\\n{solution_text}\\n"
            f"\\\\end{{ex}}\\n"
        )'''
    content = content.replace(qb_old, qb_new)
    
    # 4. Update format_param_line to use \heva and newlines
    fn_old = '''def format_param_line(base: Point, direction: Vector) -> str:
    rows: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            rows.append(f"{name} = {b}")
        else:
            sign = "+" if d > 0 else "-"
            coeff = abs(d)
            if coeff == 1:
                term = "t"
            else:
                term = f"{coeff}t"
            rows.append(f"{name} = {b} {sign} {term}")
    joined = " \\\\ ".join(rows)
    return "\\\\begin{cases} " + joined + " \\\\end{cases}"'''
    
    fn_new = '''def format_param_line(base: Point, direction: Vector) -> str:
    rows: List[str] = []
    for name, b, d in zip(("x", "y", "z"), base, direction):
        if d == 0:
            rows.append(f"{name} = {b}")
        else:
            sign = "+" if d > 0 else "-"
            coeff = abs(d)
            if coeff == 1:
                term = "t"
            else:
                term = f"{coeff}t"
            rows.append(f"{name} = {b} {sign} {term}")
    joined = " \\\\\\\\\\n".join(rows)
    return "\\\\heva{\\n" + joined + "\\n}"'''

    content = content.replace(fn_old, fn_new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Done editing", filepath)

modify_file("/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py")
