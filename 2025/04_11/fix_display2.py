import sys

def fix():
    filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The string looks like f"\\({correct_line_expr}\\)."
    content = content.replace(r"\({correct_line_expr}\)", "{correct_line_expr}")
    # Also for false_text_d replace
    # false_text_d = true_text_d.replace(correct_line_expr, options[(correct_index + 1) % 4])
    # Which is fine because true_text_d no longer has \(\) around it.
    
    # Wait, earlier I might not have replaced \({delta_expr}\) correctly if it was f"\\({delta_expr}\\) "
    content = content.replace(r"\\({delta_expr}\\)", "{delta_expr}")
    content = content.replace(r"\\({line_expr_a}\\)", "{line_expr_a}")
    content = content.replace(r"\\({line1_expr_c}\\)", "{line1_expr_c}")
    content = content.replace(r"\\({line2_expr_c}\\)", "{line2_expr_c}")
    content = content.replace(r"\\({correct_line_expr}\\)", "{correct_line_expr}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix()
