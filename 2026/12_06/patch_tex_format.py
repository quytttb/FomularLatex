import os

def fix_cau_1():
    with open('tinh_chat_tam_giac_va_goc_oxyz.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the generation part
    old_gen = """    question_lines = [f"Trong không gian với hệ tọa độ $Oxyz$, cho ba điểm $A({xA}; {yA}; {zA})$, $B({xB}; {yB}; {zB})$ và $C({xC}; {yC}; {zC})$. Xét tính đúng/sai của các mệnh đề sau:"]
    markers = []
    solutions = []
    
    for idx, (s_true, s_false, label) in enumerate(statements):
        is_true = random.choice([True, False])
        markers.append("Đ" if is_true else "S")
        question_lines.append(f"{label}) " + (s_true if is_true else s_false))"""
        
    new_gen = """    question_lines = [f"Trong không gian với hệ tọa độ $Oxyz$, cho ba điểm $A({xA}; {yA}; {zA})$, $B({xB}; {yB}; {zB})$ và $C({xC}; {yC}; {zC})$.\\\\choiceTFt"]
    markers = []
    solutions = []
    
    for idx, (s_true, s_false, label) in enumerate(statements):
        is_true = random.choice([True, False])
        markers.append("Đ" if is_true else "S")
        if is_true:
            question_lines.append(f"{{\\\\True {s_true}}}")
        else:
            question_lines.append(f"{{{s_false}}}")"""
            
    content = content.replace(old_gen, new_gen)
    
    # Fix the main part
    old_main = """    with open("cau_1_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\\n\\usepackage[utf8]{inputenc}\\n\\usepackage[vietnamese]{babel}\\n\\usepackage{amsmath,amssymb}\\n\\begin{document}\\n")
        for i in range(num_questions):
            q, s, m = generate_question(GeneratorConfig())
            f.write(f"\\section*{{Câu {i+1}}}\\n")
            f.write(f"\\textbf{{Đề bài:}}\\n\\n{q}\\n\\n")
            f.write(f"\\textbf{{Đáp án:}} " + ", ".join(m) + "\\n\\n")
            f.write(f"\\textbf{{Lời giải:}}\\n\\n{s}\\n\\n")
        f.write("\\end{document}\\n")"""
        
    new_main = """    with open("tinh_chat_tam_giac_va_goc_oxyz_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass[12pt,a4paper]{article}\\n\\usepackage{amsmath,amssymb}\\n\\usepackage{polyglossia}\\n\\setdefaultlanguage{vietnamese}\\n\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}\\n\\usepackage[solcolor]{ex_test}\\n\\begin{document}\\n")
        for i in range(num_questions):
            q, s, m = generate_question(GeneratorConfig())
            f.write(f"\\\\begin{{ex}}\\n{q}\\n\\\\loigiai{{\\n{s}\\n}}\\n\\\\end{{ex}}\\n\\n")
        f.write("\\end{document}\\n")"""
        
    content = content.replace(old_main, new_main)
    with open('tinh_chat_tam_giac_va_goc_oxyz.py', 'w', encoding='utf-8') as f:
        f.write(content)


def fix_cau_2():
    with open('hinh_chieu_va_doi_xung_oxyz.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_gen = """    options_text = ""
    for i in range(4):
        options_text += f"\\\\textbf{{{chr(65+i)}.}} ${format_point(options[i])}$ \\\\quad "
        
    question_str = question_text + "\\n\\n" + options_text.strip()"""
    
    new_gen = """    options_text = "\\\\choice\\n"
    for i in range(4):
        if i == correct_idx:
            options_text += f"{{\\\\True ${format_point(options[i])}$}}\\n"
        else:
            options_text += f"{{${format_point(options[i])}$}}\\n"
            
    question_str = question_text + "\\n" + options_text.strip()"""
    
    content = content.replace(old_gen, new_gen)
    
    old_main = """    with open("cau_2_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\\n\\usepackage[utf8]{inputenc}\\n\\usepackage[vietnamese]{babel}\\n\\usepackage{amsmath,amssymb}\\n\\begin{document}\\n")
        for i in range(num_questions):
            q, s, k = generate_question(GeneratorConfig())
            f.write(f"\\section*{{Câu {i+1}}}\\n")
            f.write(f"\\textbf{{Đề bài:}}\\n\\n{q}\\n\\n")
            f.write(f"\\textbf{{Đáp án:}} {k}\\n\\n")
        f.write("\\end{document}\\n")"""
        
    new_main = """    with open("hinh_chieu_va_doi_xung_oxyz_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass[12pt,a4paper]{article}\\n\\usepackage{amsmath,amssymb}\\n\\usepackage{polyglossia}\\n\\setdefaultlanguage{vietnamese}\\n\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}\\n\\usepackage[solcolor]{ex_test}\\n\\begin{document}\\n")
        for i in range(num_questions):
            q, s, k = generate_question(GeneratorConfig())
            f.write(f"\\\\begin{{ex}}\\n{q}\\n\\\\loigiai{{\\n{s}\\n}}\\n\\\\end{{ex}}\\n\\n")
        f.write("\\end{document}\\n")"""
        
    content = content.replace(old_main, new_main)
    with open('hinh_chieu_va_doi_xung_oxyz.py', 'w', encoding='utf-8') as f:
        f.write(content)

fix_cau_1()
fix_cau_2()
