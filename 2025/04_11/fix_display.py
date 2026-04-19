import sys

def fix():
    filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the \({expr}\) with {expr} for line expressions
    content = content.replace(r"\({line_expr_a}\)", "{line_expr_a}")
    content = content.replace(r"\({line1_expr_c}\)", "{line1_expr_c}")
    content = content.replace(r"\({line2_expr_c}\)", "{line2_expr_c}")
    content = content.replace(r"\({delta_expr}\)", "{delta_expr}")
    # correct_line_expr is inside options, not wrapped
    
    # Update format_param_line
    idx_start = content.find("def format_param_line(")
    idx_end = content.find("def format_canonical_line(", idx_start)

    old_func = content[idx_start:idx_end]
    new_func = '''def format_param_line(base: Point, direction: Vector) -> str:
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
    return "\\\\[ \\\\begin{cases} " + joined + " \\\\end{cases} \\\\]"

'''
    content = content.replace(old_func, new_func)

    # Update format_line_expression to wrap canonical
    func2_start = content.find("def format_line_expression(")
    func2_end = content.find("def format_sphere_expression(", func2_start)
    
    old_func2 = content[func2_start:func2_end]
    new_func2 = '''def format_line_expression(line_data: Dict[str, Any]) -> str:
    direction = line_data["direction"]
    # Chỉ dùng dạng chính tắc nếu cả 3 thành phần đều khác 0
    if line_data.get("style") == "canonical" and all(d != 0 for d in direction):
        expr = format_canonical_line(line_data["point"], direction)
        if expr:
            return "\\\\(" + expr + "\\\\)"
    return format_param_line(line_data["point"], direction)

'''
    content = content.replace(old_func2, new_func2)

    # Also update the correct_line_expr options because before they were NOT wrapped in true_text_d! What about options array?
    # the correct_line_expr is used in options
    # Wait, the options list is just printed. But before they were wrapped inside question_lines.append(f"{prefix}{label_letter}) \\({text}\\)") ???
    # Let's check how choices are formatted.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix()
