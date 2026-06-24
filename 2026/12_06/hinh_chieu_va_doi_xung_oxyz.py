import random
import sys
from dataclasses import dataclass

@dataclass
class GeneratorConfig:
    seed: int = None

def format_point(pt):
    return f"({pt[0]}; {pt[1]}; {pt[2]})"

def get_projection(pt, target):
    x, y, z = pt
    if target == "(Oxy)": return (x, y, 0)
    if target == "(Oyz)": return (0, y, z)
    if target == "(Oxz)": return (x, 0, z)
    if target == "Ox": return (x, 0, 0)
    if target == "Oy": return (0, y, 0)
    if target == "Oz": return (0, 0, z)

def get_reflection(pt, target):
    x, y, z = pt
    if target == "(Oxy)": return (x, y, -z)
    if target == "(Oyz)": return (-x, y, z)
    if target == "(Oxz)": return (x, -y, z)
    if target == "Ox": return (x, -y, -z)
    if target == "Oy": return (-x, y, -z)
    if target == "Oz": return (-x, -y, z)
    if target == "O": return (-x, -y, -z)

def generate_question(config: GeneratorConfig = GeneratorConfig()):
    if config.seed is not None:
        random.seed(config.seed)

    point_name = random.choice(["M", "A", "B", "C", "N", "P", "Q", "E", "F", "G", "H", "I", "K"])
    lo, hi = -15, 15
    x, y, z = random.randint(lo, hi), random.randint(lo, hi), random.randint(lo, hi)
    while x == 0 or y == 0 or z == 0 or abs(x) == abs(y) or abs(y) == abs(z) or abs(x) == abs(z):
        x, y, z = random.randint(lo, hi), random.randint(lo, hi), random.randint(lo, hi)
        
    pt = (x, y, z)
    
    question_type = random.choice(["projection", "reflection"])
    if question_type == "projection":
        target = random.choice(["(Oxy)", "(Oyz)", "(Oxz)", "Ox", "Oy", "Oz"])
        ans_pt = get_projection(pt, target)
        question_text = f"Trong không gian với hệ tọa độ $Oxyz$, cho điểm ${point_name}{format_point(pt)}$. Hình chiếu vuông góc của ${point_name}$ lên {('mặt phẳng ' if '(' in target else 'trục ')}${target}$ có tọa độ là:"
    else:
        target = random.choice(["(Oxy)", "(Oyz)", "(Oxz)", "Ox", "Oy", "Oz", "O"])
        ans_pt = get_reflection(pt, target)
        if target == "O":
            tgt_str = "gốc tọa độ $O$"
        else:
            tgt_str = f"{('mặt phẳng ' if '(' in target else 'trục ')}${target}$"
        question_text = f"Trong không gian với hệ tọa độ $Oxyz$, cho điểm ${point_name}{format_point(pt)}$. Điểm đối xứng của ${point_name}$ qua {tgt_str} có tọa độ là:"
        
    options = [ans_pt]
    while len(options) < 4:
        if question_type == "projection":
            distractor = [
                random.choice([x, 0, -x]),
                random.choice([y, 0, -y]),
                random.choice([z, 0, -z])
            ]
        else:
            distractor = [
                random.choice([x, -x, 0]),
                random.choice([y, -y, 0]),
                random.choice([z, -z, 0])
            ]
        distractor = tuple(distractor)
        if distractor not in options:
            options.append(distractor)
            
    random.shuffle(options)
    
    correct_idx = options.index(ans_pt)
    correct_label = chr(65 + correct_idx)
    
    options_text = "\\choice\n"
    for i in range(4):
        if i == correct_idx:
            options_text += f"{{\\True ${format_point(options[i])}$}}\n"
        else:
            options_text += f"{{${format_point(options[i])}$}}\n"
            
    question_str = question_text + "\n" + options_text.strip()
    
    sol = f"Tọa độ đúng là ${format_point(ans_pt)}$."
    
    return question_str, sol, correct_label

def main():
    num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    with open("hinh_chieu_va_doi_xung_oxyz_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass[12pt,a4paper]{article}\n\\usepackage{amsmath,amssymb}\n\\usepackage{polyglossia}\n\\setdefaultlanguage{vietnamese}\n\\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}\n\\usepackage[solcolor]{ex_test}\n\\begin{document}\n")
        for i in range(num_questions):
            q, s, k = generate_question(GeneratorConfig())
            f.write(f"\\begin{{ex}}\n{q}\n\\end{{ex}}\n\n")
        f.write("\\end{document}\n")

if __name__ == "__main__":
    main()
