import os
import random
import logging
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Any, List, Tuple
from string import Template

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def format_percentage(val: float, decimals: int = 2) -> str:
    """Format tỉ lệ float thành chuỗi % VD: 0.725 -> 72,5%"""
    perc = val * 100
    if perc == int(perc):
        return f"{int(perc)}\\%"
    formatted = f"{perc:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",") + "\\%"

TEMPLATE_QUESTION = Template(r"""Trước 3 tiếng khi diễn ra trận Derby thành Manchester giữa MU-MC. Người ta phỏng vấn ngẫu nhiên ${N} người hâm mộ của MU (có ${N_M} người đang mặc áo của đội bóng) về việc có nên xem trận đấu đó hay không. Kết quả cho thấy rằng ${N_B} người trả lời sẽ xem, ${N_notB} người trả lời sẽ không xem. Nhưng thực tế cho thấy rằng tỉ lệ người hâm mộ MU thực sự xem trận đấu tương ứng với những cách trả lời "có xem" và "không xem" là ${P_A_B_pct} và ${P_A_notB_pct}. Gọi $$A$$ là biến cố "Người được phỏng vấn thực sự sẽ xem trận đấu", gọi $$B$$ là biến cố "Người được phỏng vấn trả lời sẽ xem trận đấu".


${stmt_a}

${stmt_b}

${stmt_c}

${stmt_d}
""")

TEMPLATE_SOLUTION = Template(r"""
Lời giải

a) ${ans_a}. Tỉ lệ người được phỏng vấn thực sự sẽ xem trận đấu là:
$$P(A) = P(B) \cdot P(A|B) + P(\overline{B}) \cdot P(A|\overline{B})$$

$$P(A) = ${P_B} \cdot ${P_A_B} + ${P_notB} \cdot ${P_A_notB} = ${P_A_val}$$

b) ${ans_b}. Sử dụng công thức Bayes: $$P(\overline{B}|A) = \dfrac{P(\overline{B} \cap A)}{P(A)} = \dfrac{P(\overline{B}) \cdot P(A|\overline{B})}{P(A)}$$

$$P(\overline{B}|A) = \dfrac{${P_notB} \cdot ${P_A_notB}}{${P_A_val}} \approx ${P_notB_A_pct}$$

c) ${ans_c}. Gọi $$M$$ là biến cố "Mặc áo đội bóng". Theo đề: $$n(M) = ${N_M}$$ người.
Số người thực sự xem và mặc áo là: $$n(A \cap M) = ${N_A_M}$$ người.
Số người mặc áo nhưng thực sự không xem là: $$n(\overline{A} \cap M) = ${N_M} - ${N_A_M} = ${N_notA_M}$$ người.
Tỉ lệ người mặc áo nhưng thực sự không xem là: $$\dfrac{n(\overline{A} \cap M)}{n(M)} = \dfrac{${N_notA_M}}{${N_M}} = ${P_notA_M_pct}$$

d) ${ans_d}. Ta có: $$E$$ là biến cố "Trả lời sai sự thật". Theo đề: $$P(E|M) = ${P_E_M_pct} = ${P_E_M}$$.
Suy ra xác suất trả lời đúng trong nhóm mặc áo là: $$P(\overline{E}|M) = 1 - ${P_E_M} = ${P_notE_M}$$.

Ta có $$P(M) = ${P_M} \Rightarrow P(\overline{M}) = ${P_notM}$$. Mà $$P(\overline{E}|M) = ${P_notE_M} = \dfrac{P(\overline{E}M)}{P(M)} \Rightarrow P(\overline{E}M) = ${P_notE_M_and_M}$$

Lại có: $$P(E) = P(\overline{A}B) + P(A\overline{B}) = ${P_E_val}$$
$$\Rightarrow P(\overline{E}) = P(AB) + P(\overline{A}\overline{B}) = ${P_notE_val}$$. Mà $$P(\overline{E}) = P(\overline{E}M) + P(\overline{E}\overline{M}) = ${P_notE_val}$$
$$\Rightarrow P(\overline{E}\overline{M}) = P(\overline{E}) - P(\overline{E}M) = ${P_notE_val} - ${P_notE_M_and_M} = ${P_notE_notM_val}$$

$$\Rightarrow P(\overline{E}|\overline{M}) = \dfrac{P(\overline{E}\overline{M})}{P(\overline{M})} = \dfrac{${P_notE_notM_val}}{${P_notM}} = ${P_notE_given_notM_pct}$$
""")


class DerbyProbabilityQuestion:
    def __init__(self):
        self.params = {}
        self.calcs = {}

    def generate_parameters(self) -> Dict[str, Any]:
        attempts = 0
        while attempts < 1000:
            attempts += 1
            # 1. Base variables
            N = random.choice([100, 200, 500])
            N_M = random.choice([int(N * 0.1), int(N * 0.2), int(N * 0.25), int(N * 0.3)])
            N_B = random.choice([int(N * 0.6), int(N * 0.7), int(N * 0.75), int(N * 0.8)])
            N_notB = N - N_B

            # P(A|B) and P(A|notB)
            P_A_B_pct = random.choice([70, 75, 80, 85, 90])
            P_A_notB_pct = random.choice([10, 15, 20, 25, 30])
            P_A_B = P_A_B_pct / 100
            P_A_notB = P_A_notB_pct / 100

            # 2. Part c dependencies
            N_A_M = random.randint(int(N_M * 0.4), int(N_M * 0.8))
            N_notA_M = N_M - N_A_M

            # 3. Part d dependencies
            P_E_M_pct = random.choice([10, 15, 20, 25, 30])
            P_E_M = P_E_M_pct / 100
            
            # Tính xác suất để valid
            P_B = N_B / N
            P_notB = N_notB / N
            
            P_A = P_B * P_A_B + P_notB * P_A_notB
            
            # P(notB | A)
            if P_A == 0: continue
            P_notB_A = (P_notB * P_A_notB) / P_A
            
            # P(notA | M)
            P_notA_M_val = N_notA_M / N_M
            
            # Tính d
            P_notE_M = 1 - P_E_M
            P_M = N_M / N
            P_notM = 1 - P_M
            P_notE_M_and_M = P_notE_M * P_M
            
            # P(E) = P(notA intersect B) + P(A intersect notB)
            # P(notA intersect B) = P(B) * P(notA | B) = P(B) * (1 - P(A|B))
            P_notA_B = P_B * (1 - P_A_B)
            # P(A intersect notB) = P(notB) * P(A | notB) 
            P_A_notB_joint = P_notB * P_A_notB
            
            P_E = P_notA_B + P_A_notB_joint
            P_notE = 1 - P_E
            P_notE_notM_val = P_notE - P_notE_M_and_M
            
            if P_notE_notM_val < 0 or P_notM == 0:
                continue
                
            P_notE_given_notM = P_notE_notM_val / P_notM
            if P_notE_given_notM < 0 or P_notE_given_notM > 1:
                continue

            return {
                "N": N, "N_M": N_M, "N_B": N_B, "N_notB": N_notB,
                "P_A_B_pct": P_A_B_pct, "P_A_notB_pct": P_A_notB_pct,
                "P_A_B": P_A_B, "P_A_notB": P_A_notB,
                "P_B": P_B, "P_notB": P_notB,
                "N_A_M": N_A_M, "N_notA_M": N_notA_M,
                "P_E_M_pct": P_E_M_pct, "P_E_M": P_E_M,
                
                "P_A": P_A,
                "P_notB_A": P_notB_A,
                "P_notA_M_val": P_notA_M_val,
                "P_notE_M": P_notE_M,
                "P_M": P_M,
                "P_notM": P_notM,
                "P_notE_M_and_M": P_notE_M_and_M,
                "P_E": P_E,
                "P_notE": P_notE,
                "P_notE_notM_val": P_notE_notM_val,
                "P_notE_given_notM": P_notE_given_notM
            }
        raise ValueError("Could not find valid parameters")

    def format_decimal_vn(self, val: float, decimals: int=4) -> str:
        s = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
        if s == "": s = "0"
        return s.replace(".", ",")

    def generate(self, q_num: int) -> Tuple[str, str]:
        p = self.generate_parameters()
        
        # Decide true/false for each statement
        # According to user, if True, add *, if False, don't.
        # But wait, does Azota `\choice` support `*` at start?
        # The user said: "mệnh đề đúng thêm * vào trước, còn mệnh đề sai thì không cần"
        # i.e. `\choice{* Phát biểu đúng}` vs `\choice{Phát biểu sai}`
        
        TF = [random.choice([True, False]) for _ in range(4)]
        
        # Generate statements
        # a) P(A)
        val_a = p['P_A'] if TF[0] else p['P_A'] + random.choice([-0.05, 0.05, -0.1, 0.1])
        stmt_a_text = f"Tỉ lệ người được phỏng vấn thực sự sẽ xem trận đấu là ${format_percentage(val_a)}$."
        stmt_a = ("*a) " if TF[0] else "a) ") + stmt_a_text
        
        # b) P(notB | A)
        val_b = p['P_notB_A'] if TF[1] else p['P_notB_A'] + random.choice([-0.02, 0.02, -0.05, 0.05])
        stmt_b_text = f"Trong số người được phỏng vấn thực sự sẽ xem có ${format_percentage(val_b)}$ người trả lời không xem khi được phỏng vấn."
        stmt_b = ("*b) " if TF[1] else "b) ") + stmt_b_text
        
        # c) P(notA_M)
        val_c = p['P_notA_M_val'] if TF[2] else p['P_notA_M_val'] + random.choice([-0.05, 0.05])
        stmt_c_text = f"Trong số những người mặc áo đội bóng có ${format_percentage(val_c)}$ người được phỏng vấn thực sự sẽ không xem trận đấu biết rằng số người được phỏng vấn thực sự sẽ xem trận đấu mặc áo đội bóng là {p['N_A_M']} người."
        stmt_c = ("*c) " if TF[2] else "c) ") + stmt_c_text
        
        # d) P(notE | notM)
        val_d = p['P_notE_given_notM'] if TF[3] else p['P_notE_given_notM'] + random.choice([-0.01, 0.01, -0.05, 0.05])
        stmt_d_text = f"Gọi $E$ là biến cố \"Người trả lời sai sự thật\" (tức là trả lời phỏng vấn là có và thực tế lại không xem và ngược lại). Biết rằng trong nhóm người mặc áo đội bóng, xác suất để xảy ra biến cố $E$ là ${p['P_E_M_pct']}\\%$. Xác suất để một người trả lời đúng sự thật trong những người không mặc áo là ${format_percentage(val_d)}$."
        stmt_d = ("*d) " if TF[3] else "d) ") + stmt_d_text
        
        question_text = TEMPLATE_QUESTION.substitute(
            N=p['N'], N_M=p['N_M'], N_B=p['N_B'], N_notB=p['N_notB'],
            P_A_B_pct=f"${p['P_A_B_pct']}\\%$",
            P_A_notB_pct=f"${p['P_A_notB_pct']}\\%$",
            stmt_a=stmt_a, stmt_b=stmt_b, stmt_c=stmt_c, stmt_d=stmt_d
        )
        
        ans_labels = ["Đúng" if tf else "Sai" for tf in TF]
        
        solution_text = TEMPLATE_SOLUTION.substitute(
            ans_a=ans_labels[0], ans_b=ans_labels[1], ans_c=ans_labels[2], ans_d=ans_labels[3],
            P_B=self.format_decimal_vn(p['P_B']),
            P_A_B=self.format_decimal_vn(p['P_A_B']),
            P_notB=self.format_decimal_vn(p['P_notB']),
            P_A_notB=self.format_decimal_vn(p['P_A_notB']),
            P_A_val=self.format_decimal_vn(p['P_A']),
            
            P_notB_A_pct=format_percentage(p['P_notB_A']),
            
            N_M=p['N_M'], N_A_M=p['N_A_M'], N_notA_M=p['N_notA_M'],
            P_notA_M_pct=format_percentage(p['P_notA_M_val']),
            
            P_E_M_pct=p['P_E_M_pct'], P_E_M=self.format_decimal_vn(p['P_E_M']),
            P_notE_M=self.format_decimal_vn(p['P_notE_M']),
            P_M=self.format_decimal_vn(p['P_M']),
            P_notM=self.format_decimal_vn(p['P_notM']),
            P_notE_M_and_M=self.format_decimal_vn(p['P_notE_M_and_M']),
            
            P_E_val=self.format_decimal_vn(p['P_E']),
            P_notE_val=self.format_decimal_vn(p['P_notE']),
            P_notE_notM_val=self.format_decimal_vn(p['P_notE_notM_val']),
            
            P_notE_given_notM_pct=format_percentage(p['P_notE_given_notM'])
        )
        
        final_str = f"\\begin{{ex}}%C\u00e2u {q_num}\n" + question_text.strip() + "\n\n\\loigiai{\n" + solution_text.strip() + "\n}\n\\end{ex}"
        
        return final_str, ""

def create_document(questions: List[Tuple[str, str]]) -> str:
    content = "\n\n".join(q for q, _ in questions)
    doc = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

""" + content + r"""

\end{document}
"""
    return doc

if __name__ == "__main__":
    import sys
    num_q = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(1, 10000)
    random.seed(seed)
    logging.info(f"Generating {num_q} questions with seed {seed}")
    
    gen = DerbyProbabilityQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i+1))
        
    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "derby_probability_questions.tex")
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
