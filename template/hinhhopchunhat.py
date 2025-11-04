import math
import random
import sys
from typing import List, Tuple
from fractions import Fraction


class RectPrismQuestion:
    """Bài toán hình hộp chữ nhật: sinh dữ liệu và tạo các phần a,b,c,d như mô tả."""

    def __init__(self):
        self._gen_params()

    # --------- THAM SỐ ---------
    def _gen_params(self):
        self.x = random.randint(2, 6)
        self.y = random.randint(2, 6)
        self.z = random.randint(2, 6)
        self.k = random.choice([3, 4, 5])  # k>1, tránh 2
        self.l = random.choice([2, 3, 4, 5])
        # Điểm E: AE = AC'/k
        self.E = (self.x / self.k, self.y / self.k, self.z / self.k)
        # Điểm F: B'F = B'D / l -> F = B' + (1/l)B'D
        self.F = (
            self.x * (1 - 1 / self.l),
            self.y / self.l,
            self.z * (1 - 1 / self.l),
        )

    # --------- HỆ SỐ BIỂU DIỄN ---------
    def vector_coeffs(self):
        k, l = self.k, self.l
        data = {
            # A'F: A'(0,0,z) -> F(x(l-1)/l, y/l, z(l-1)/l) so coefficients ((l-1)/l, 1/l, -1/l)
            "A'F": (Fraction(l - 1, l), Fraction(1, l), Fraction(-1, l)),
            "D'E": (Fraction(1, k), Fraction(1 - k, k), Fraction(1 - k, k)),
            "AF": (Fraction(l - 1, l), Fraction(1, l), Fraction(l - 1, l)),
            "C'F": (Fraction(-1, l), Fraction(1 - l, l), Fraction(-1, l)),
            "EF": (
                Fraction(k * l - k - l, k * l),
                Fraction(k - l, k * l),
                Fraction(k * l - k - l, k * l),
            ),
        }
        return data

    @staticmethod
    def frac(fr: Fraction) -> str:
        return str(fr.numerator) if fr.denominator == 1 else f"\\frac{{{fr.numerator}}}{{{fr.denominator}}}"

    @classmethod
    def linear_expr(cls, a: Fraction, b: Fraction, c: Fraction) -> str:
        parts = []
        for coeff, name in [(a, 'AB'), (b, 'AD'), (c, "AA'")]:
            if coeff == 0:
                continue
            parts.append(cls.frac(coeff) + f"\\overrightarrow{{{name}}}")
        if not parts:
            return "0"
        expr = " + ".join(parts)
        return expr.replace("+ -", "- ")

    # --------- PHẦN a ---------
    def gen_part_a(self) -> List[Tuple[str, bool]]:
        coeffs = self.vector_coeffs()
        names = list(coeffs.keys())
        name = random.choice(names)
        a, b, c = coeffs[name]
        # Lưu lại lựa chọn cho phần lời giải
        self.a_selected_name = name
        self.a_selected_coeffs = (a, b, c)
        out: List[Tuple[str, bool]] = []
        # 50% chọn dạng biểu diễn vectơ, 50% chọn dạng tổ hợp tuyến tính p a + q b + r c
        if random.random() < 0.5:
            expr_true = self.linear_expr(a, b, c)
            if random.random() < 0.6:
                out.append((f"\\overrightarrow{{{name}}} = {expr_true}", True))
            else:
                which = random.choice([0, 1, 2])
                da, db, dc = a, b, c
                delta = Fraction(random.choice([1, -1]), random.choice([1, 2, 3]))
                if which == 0:
                    da += delta
                elif which == 1:
                    db += delta
                else:
                    dc += delta
                out.append((f"\\overrightarrow{{{name}}} = {self.linear_expr(da, db, dc)}", False))
        else:
            p, q, r = [random.randint(1, 4) for _ in range(3)]
            value = p * a + q * b + r * c
            if random.random() < 0.6:
                rhs = self.frac(value)
                ok = True
            else:
                wrong = Fraction(value.numerator + random.choice([1, -1]), value.denominator)
                rhs = self.frac(wrong)
                ok = False
            out.append((
                f"Với \\overrightarrow{{{name}}} = a\\overrightarrow{{AB}}+b\\overrightarrow{{AD}}+c\\overrightarrow{{AA'}} (a,b,c\\in\\mathbb{{R}}) thì {p}a+{q}b+{r}c = {rhs}",
                ok,
            ))
        return out

    # --------- CÁC GIÁ TRỊ B,C,D ---------
    def derived_symbolic(self):
        """Trả về cos, tích vô hướng và các thể tích (dạng LaTeX)."""
        x, y, z, k, l = self.x, self.y, self.z, self.k, self.l
        cos1 = f"\\frac{{{x}^2 - ({k}-1)({y}^2+{z}^2)}}{{\\sqrt{{{x}^2 + ({k}-1)^2({y}^2+{z}^2)}}\\,\\sqrt{{{x}^2 + {y}^2 + {z}^2}}}}"
        # cos2: Sửa mẫu số: khoảng cách theo phương z không nhân (l-1); đúng là x^2 + (l-1)^2 y^2 + z^2
        cos2 = f"\\frac{{{x}^2 + (1-{l}){y}^2}}{{\\sqrt{{{x}^2 + ({l}-1)^2 {y}^2 + {z}^2}}\\,\\sqrt{{{x}^2 + {y}^2}}}}"
        dot_num = y * y - (l - 1) * x * x
        if dot_num % l == 0:
            dot_expr = f"{dot_num // l}"
        else:
            dot_expr = f"\\frac{{{dot_num}}}{{{l}}}"
        from math import gcd
        def frac_simplify(num: int, den: int) -> str:
            g = gcd(abs(num), abs(den))
            num //= g
            den //= g
            return f"{num}" if den == 1 else f"\\frac{{{num}}}{{{den}}}" if num != 0 else "0"
        V1 = frac_simplify(x * y * z, 6 * k)
        V2 = frac_simplify(x * y * z, 6 * l)
        V3 = frac_simplify((k - 2) * x * y * z, 6 * k * l)
        return cos1, cos2, dot_expr, V1, V2, V3


    def build(self, idx: int) -> Tuple[str, List[bool]]:
        cos1, cos2, dotv, V1, V2, V3 = self.derived_symbolic()
        x, y, z, k, l = self.x, self.y, self.z, self.k, self.l
        cos1_num = (x**2 - (k - 1) * (y**2 + z**2)) / (
            math.sqrt(x**2 + (k - 1) ** 2 * (y**2 + z**2)) * math.sqrt(x**2 + y**2 + z**2)
        )
        cos2_num = (x**2 + (1 - l) * y**2) / (
            # Sửa mẫu số: sqrt(x^2 + (l-1)^2 y^2 + z^2) * sqrt(x^2 + y^2)
            math.sqrt(x**2 + (l - 1) ** 2 * y**2 + z**2) * math.sqrt(x**2 + y**2)
        )
        header = (
            f"Câu {idx}: Cho hình hộp chữ nhật ABCD.A'B'C'D' với AB={self.x}, AD={self.y}, AA'={self.z}. "
            f"Lấy điểm E trên AC' sao cho AC'=k AE (k={self.k}) và điểm F trên B'D sao cho B'D = l B'F (l={self.l})."
        ) + "\\par\n"  # line break after intro

        # Part a
        part_a_list = self.gen_part_a()
        if part_a_list:
            txt, ok_a = part_a_list[0]
            if txt.startswith("Với ") and " thì " in txt:
                before, after = txt.split(" thì ", 1)
                body_a = f"Với \\({before[4:].strip()}\\) thì \\({after.strip()}\\)"
            else:
                body_a = f"\\({txt}\\)"
            a_text = f"{'* ' if ok_a else ''}a) {body_a}\\par\n"
        else:
            ok_a = False
            a_text = "a) (lỗi sinh dữ liệu)\\par\n"

        import re
        def perturb(expr: str) -> str:
            # Chỉ tạo sai khác nhỏ có kiểm soát: ±1 ở tử số (nếu là phân số) hoặc ở số nguyên.
            if expr.startswith("\\frac{"):
                m = re.match(r"^\\frac{(-?\d+)}{(-?\d+)}$", expr)
                if m:
                    num = int(m.group(1))
                    den = m.group(2)
                    delta = random.choice([-1, 1])
                    return f"\\frac{{{num + delta}}}{{{den}}}"
            if re.fullmatch(r"-?\d+", expr):
                val = int(expr)
                return str(val + random.choice([-1, 1]))
            return expr  # Không thay đổi nếu không nhận dạng được dạng đơn giản

        def make_stmt(label: str, correct: str) -> Tuple[str, bool, str]:
            if random.random() < 0.6:
                return f"{label} = {correct}", True, correct
            fake = perturb(correct)
            if fake == correct:
                fake = perturb(correct)
            return f"{label} = {fake}", False, correct

        b_label, b_val = random.choice([
            ("\\cos\\big(\\overrightarrow{D'E},\\overrightarrow{AC'}\\big)", cos1),
            ("\\cos\\big(\\overrightarrow{C'F},\\overrightarrow{B'D'}\\big)", cos2),
        ])
        def format_decimal(val: float, ndigits: int = 3) -> str:
            s = f"{val:.{ndigits}f}".rstrip('0').rstrip('.')
            return s if s else "0"
        def make_stmt_approx(label: str, numeric_value: float) -> Tuple[str, bool]:
            if random.random() < 0.6:
                return f"{label} \\approx {format_decimal(numeric_value, 3)}", True
            delta = random.choice([-0.2, -0.1, 0.1, 0.2])
            wrong_val = numeric_value + delta
            if abs(wrong_val - numeric_value) < 1e-9:
                wrong_val += 0.1
            return f"{label} \\approx {format_decimal(wrong_val, 3)}", False
        numeric_value = cos1_num if b_val == cos1 else cos2_num
        b_stmt, b_ok = make_stmt_approx(b_label, numeric_value)
        b_correct = b_val
        b_text = f"{'* ' if b_ok else ''}b) \\( {b_stmt} \\)\\par\n"

        c_stmt, c_ok, c_correct = make_stmt("\\overrightarrow{AF} \\cdot \\overrightarrow{B'D'}", dotv)
        c_text = f"{'* ' if c_ok else ''}c) \\( {c_stmt} \\)\\par\n"

        d_label, d_val = random.choice([
            ("V_{A.EBD}", V1),
            ("V_{B'.FC'D'}", V2),
            ("V_{E.FA'B'}", V3),
        ])
        d_stmt, d_ok, d_correct = make_stmt(d_label, d_val)
        d_text = f"{'* ' if d_ok else ''}d) \\( {d_stmt} \\)\\par\n"

        # Solution lines (each ends with line break)
        lines: List[str] = ["Lời giải:\\par"]
        lines.append("Chọn hệ trục toạ độ: gốc tại A, các trục trùng với AB, AD, AA'.\\par")
        lines.append("Toạ độ:\\par")
        from math import gcd as _gcd
        def _simp(num: int, den: int) -> str:
            g = _gcd(abs(num), abs(den))
            num //= g
            den //= g
            return f"{num}" if den == 1 else f"\\frac{{{num}}}{{{den}}}"
        L = self.l
        Lm1 = L - 1
        Fx = _simp(self.x * Lm1, L)
        Fy = _simp(self.y, L)
        Fz = _simp(self.z * Lm1, L)
        lines.append(
            f"\\( B({self.x},0,0),\\ D(0,{self.y},0),\\ A'(0,0,{self.z}),\\ E\\big( \\frac{{{self.x}}}{{{self.k}}}, \\frac{{{self.y}}}{{{self.k}}}, \\frac{{{self.z}}}{{{self.k}}} \\big),\\ F\\big( {Fx}, {Fy}, {Fz} \\big) \\)\\par"
        )
        lines.append("Biểu diễn vectơ cho ý a):\\par")
        if hasattr(self, 'a_selected_name') and hasattr(self, 'a_selected_coeffs'):
            a_name = self.a_selected_name
            a_a, a_b, a_c = self.a_selected_coeffs
            lines.append(
                f"\\( \\overrightarrow{{{a_name}}} = {self.linear_expr(a_a, a_b, a_c)} \\)\\par"
            )
        else:
            # Fallback: giữ cách cũ nếu chẳng may không có trạng thái
            for name, (a, b, c) in self.vector_coeffs().items():
                expr = self.linear_expr(a, b, c)
                lines.append(
                    f"\\( \\overrightarrow{{{name}}} = {expr} \\)\\par"
                )
        lines.append("Kết quả ý b):\\par")
        if "D'E" in b_label:
            u_name, v_name = "D'E", "AC'"
        else:
            u_name, v_name = "C'F", "B'D'"
        # Trình bày gọn lại công thức cos với biểu thức đã suy ra ở phần trên.
        lines.append(
            f"\\(\\cos\\big(\\overrightarrow{{{u_name}}},\\overrightarrow{{{v_name}}}\\big) = {b_correct} \\approx {format_decimal(numeric_value, 3)}\\)\\par"
        )
        if u_name == "C'F":
            # Giải thích chuẩn hoá biểu thức cos: hệ số 1/l chung triệt tiêu.
            lines.append("Do cả tích vô hướng và độ dài \\(|\\overrightarrow{C'F}|\\) cùng mang thừa số \\(\\tfrac{1}{l}\\) nên triệt tiêu, được biểu thức trên không còn 1/l.\\par")
        lines.append("Tích vô hướng ở ý c):\\par")
        lines.append(f"Do \\(\\overrightarrow{{AB}}\\perp\\overrightarrow{{AD}}\\perp\\overrightarrow{{AA'}}\\), với \\(|AB|={x}, |AD|={y}, |AA'|={z}\\).\\par")
        lines.append(
            f"\\( \\overrightarrow{{AF}} = \\frac{{{l-1}}}{{{l}}}\\overrightarrow{{AB}} + \\frac1{{{l}}}\\overrightarrow{{AD}} + \\frac{{{l-1}}}{{{l}}}\\overrightarrow{{AA'}} \\), \\( \\overrightarrow{{B'D'}} = -\\overrightarrow{{AB}} + \\overrightarrow{{AD}} \\).\\par"
        )
        lines.append(
            "\\( \\Rightarrow \\overrightarrow{AF}\\cdot\\overrightarrow{B'D'} = -\\frac{l-1}{l}\\,\\overrightarrow{AB}\\!\\cdot\\!\\overrightarrow{AB} + \\frac1l\\,\\overrightarrow{AD}\\!\\cdot\\!\\overrightarrow{AD} = -\\frac{l-1}{l}x^2 + \\frac1l y^2 \\).\\par"
        )
        lines.append(f"\\( = {c_correct} \\).\\par")
        lines.append("Thể tích ở ý d):\\par")
        lines.append("Quy ước \\( V_{P.QRS} = \\tfrac16\\,\\big|[\\overrightarrow{PQ},\\overrightarrow{PR},\\overrightarrow{PS}]\\big| \\).\\par")
        if d_label == "V_{A.EBD}":
            lines.append(
                "\\( \\overrightarrow{AE} = \\tfrac1k(\\overrightarrow{AB}+\\overrightarrow{AD}+\\overrightarrow{AA'}) \\Rightarrow [\\overrightarrow{AB},\\overrightarrow{AD},\\overrightarrow{AE}] = \\tfrac1k[\\overrightarrow{AB},\\overrightarrow{AD},\\overrightarrow{AA'}] = \\tfrac1k\\,x y z \\).\\par"
            )
            lines.append(
                f"Do đó \\( V_{{A.EBD}} = \\tfrac16\\,\\big|[\\overrightarrow{{AB}},\\overrightarrow{{AD}},\\overrightarrow{{AE}}]\\big| = \\tfrac{{{x}\\,{y}\\,{z}}}{{6\\,{k}}} = {d_correct} \\).\\par"
            )
        elif d_label == "V_{B'.FC'D'}":
            lines.append("Chọn gốc tại B'. Khi đó (giữ hệ trục song song AB,AD,AA').\\par")
            lines.append(
                f"\\( \\overrightarrow{{B'F}} = \\tfrac1l\\,\\overrightarrow{{B'D}} = ( -\\tfrac{{{x}}}{{{l}}}, \\tfrac{{{y}}}{{{l}}}, -\\tfrac{{{z}}}{{{l}}} ) ,\\ \\overrightarrow{{B'C'}}=(0,{y},0),\\ \\overrightarrow{{B'D'}}=(-{x},{y},0) \\)\\par"
            )
            lines.append("Tính tích có hướng: \\( (\\overrightarrow{B'F} \\times \\overrightarrow{B'C'}) = (\\tfrac{yz}{l},0,-\\tfrac{xy}{l}) \\).\\par")
            lines.append(
                f"Suy ra hỗn hợp vô hướng: \\( [\\overrightarrow{{B'F}},\\overrightarrow{{B'C'}},\\overrightarrow{{B'D'}}] = (\\overrightarrow{{B'F}} \\times \\overrightarrow{{B'C'}}) \\cdot \\overrightarrow{{B'D'}} = -\\tfrac{{x y z}}{{l}} \\).\\par"
            )
            lines.append(
                f"\\( V_{{B'.FC'D'}} = \\tfrac16\\,\\big|[\\overrightarrow{{B'F}},\\overrightarrow{{B'C'}},\\overrightarrow{{B'D'}}]\\big| = \\tfrac1{{6\\,{l}}}\\,{x}\\,{y}\\,{z} = {d_correct} \\)\\par"
            )
        else:  # V_{E.FA'B'}
            lines.append(
                "Lấy gốc tại E. Theo cơ sở \\( (\\overrightarrow{AB},\\overrightarrow{AD},\\overrightarrow{AA'}) \\): \\par"
            )
            lines.append(
                "\\( \\overrightarrow{EA'} = (-\\tfrac1k,-\\tfrac1k,1-\\tfrac1k),\\ \\overrightarrow{EB'}=(1-\\tfrac1k,-\\tfrac1k,1-\\tfrac1k),\\ \\overrightarrow{EF}=(\\tfrac{l-1}{l}-\\tfrac1k,\\tfrac1l-\\tfrac1k,\\tfrac{l-1}{l}-\\tfrac1k) \\).\\par"
            )
            lines.append(
                "Biến đổi cột: \\( C_2 \\leftarrow C_2 - C_1,\\ C_3 \\leftarrow C_3 - C_1 \\) được \\( C_2=(1,0,0),\\ C_3=(\\tfrac{l-1}{l},\\tfrac1l,-\\tfrac1l) \\).\\par"
            )
            lines.append(
                "Suy ra \\( \\det M = -\\det \\begin{pmatrix} -\\tfrac1k & \\tfrac1l \\\\[2pt] 1-\\tfrac1k & -\\tfrac1l \\end{pmatrix} = \\tfrac{k-2}{k l} \\).\\par"
            )
            lines.append(
                f"\\( V_{{E.FA'B'}} = \\tfrac16\\,|\\det M|\\,{x}\\,{y}\\,{z} = {d_correct} \\).\\par"
            )

        full = "\n".join([header, a_text, b_text, c_text, d_text, "\n".join(lines)])
        flags = [ok_a, b_ok, c_ok, d_ok]
        return full, flags


class RectPrismGenerator:
    @classmethod
    def generate_single_mixed_question(cls, question_number: int = 1) -> Tuple[str, List[bool]]:
        return RectPrismQuestion().build(question_number)

    @classmethod
    def generate_multiple_questions(cls, num_questions: int = 5) -> List[str]:
        return [cls.generate_single_mixed_question(i)[0] for i in range(1, num_questions + 1)]

    @staticmethod
    def create_latex_document(questions_data, title: str = "Bài tập Hình hộp chữ nhật") -> str:
        header = (
            "\\documentclass[a4paper,12pt]{article}\n"
            "\\usepackage{amsmath,amssymb,mathtools}\n"
            "\\usepackage{geometry}\n"
            "\\geometry{a4paper, margin=1in}\n"
            "\\usepackage{polyglossia}\n"
            "\\setmainlanguage{vietnamese}\n"
            "\\setmainfont{TeX Gyre Termes}\n"
            "\\begin{document}\n"
            f"\\title{{{title}}}\n"
            "\\maketitle\n"
        )
        # Ensure footer starts on a fresh line so trailing \\ from last question doesn't swallow the backslash
        footer = "\n\\end{document}\n"
        body = "\n\n".join(questions_data)
        return header + body + footer

    @classmethod
    def create_latex_file(cls, questions_data, filename: str = "hinh_hop_questions.tex", title: str = "Bài tập Hình hộp chữ nhật") -> str:
        latex_content = cls.create_latex_document(questions_data, title)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Đã tạo file: {filename}")
        return filename



# =============================
# MAIN
# =============================
def main():
    try:
        num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        gen = RectPrismGenerator()
        questions_data = gen.generate_multiple_questions(num_questions)
        if not questions_data:
            print("Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
        filename = gen.create_latex_file(questions_data)
        print(f"📄 Biên dịch bằng: xelatex {filename}")
    except ValueError:
        print("❌ Lỗi: Vui lòng nhập số câu hỏi hợp lệ")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()