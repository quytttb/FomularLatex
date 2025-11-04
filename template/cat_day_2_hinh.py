import argparse
import math
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sympy as sp


# Bài toán tối ưu cắt dây thành hai đoạn để uốn thành hai hình khác nhau
# Tối ưu tổng diện tích hai hình
# Hình học: hình vuông, vòng tròn, hình tam giác đều
# Đầu vào: chiều dài dây, đơn vị đo, hai hình học, chọn hình cần hỏi
# Đầu ra: chiều dài đoạn dây uốn thành hình được chọn để tổng diện tích hai hình nhỏ nhất
# Yêu cầu: làm tròn đến hàng phần trăm


# ========================================================================================
# Base class
# ========================================================================================
class BaseOptimizationQuestion(ABC):
    def __init__(self):
        self.parameters: Dict[str, Any] = {}
        self.correct_answer: Optional[str] = None
        self.solution_steps: List[str] = []

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        pass

    def generate_question(self, question_number: int = 1) -> str:
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        return f"Câu {question_number}: {q_text}\n\n{solution}\n\nĐáp án: {self.correct_answer}\n\n"


# ========================================================================================
# Geometry Rope Problem
# ========================================================================================
class RopeCutOptimizationQuestion:

    # Khởi tạo tham số ngẫu nhiên
    def __init__(self):
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()

    def generate_parameters(self):
        # ropeLength: giá trị chiều dài dây dẫn, random trong khoảng [1;10]
        rope_length = random.randint(1, 10)

        # linearUnit: đơn vị đo chiều dài theo hệ mét, random (m;dm;cm)
        linear_unit = random.choice(["m", "dm", "cm"])

        # firstShape và secondShape: hình học, random (hình vuông, vòng tròn, hình tam giác đều)
        shapes = ["hình vuông", "vòng tròn", "hình tam giác đều"]
        first_shape = random.choice(shapes)

        # Điều kiện: firstShape != secondShape
        remaining_shapes = [shape for shape in shapes if shape != first_shape]
        second_shape = random.choice(remaining_shapes)

        # firstOrSecondShape: random (firstShape; secondShape)
        target_shapes = [first_shape, second_shape]
        first_or_second_shape = random.choice(target_shapes)

        return {
            "ropeLength": rope_length,
            "linearUnit": linear_unit,
            "firstShape": first_shape,
            "secondShape": second_shape,
            "firstOrSecondShape": first_or_second_shape
        }

    # Tính diện tích từ chu vi cho trước
    def area_from_perimeter(self, shape: str, P: float):
        if shape == "hình vuông":
            return (P / 4) ** 2
        elif shape == "vòng tròn":
            r = P / (2 * sp.pi)
            return sp.pi * r ** 2
        elif shape == "hình tam giác đều":
            a = P / 3
            return sp.sqrt(3) / 4 * a ** 2
        return 0

    # Tính chiều dài đoạn dây uốn thành hình được chọn để tổng diện tích hai hình nhỏ nhất

    def calculate_answer(self) -> str:
        p = self.parameters
        L = float(p["ropeLength"])
        x = sp.symbols('x', real=True)

        # Biểu thức diện tích symbolic
        A1 = self.area_from_perimeter(p["firstShape"], x)
        A2 = self.area_from_perimeter(p["secondShape"], L - x)
        A = sp.simplify(A1 + A2)

        # Đạo hàm
        dA = sp.diff(A, x)

        # 1) Tìm nghiệm symbolic (hoặc rỗng nếu không tìm được)
        raw_sols = []
        try:
            raw_sols = sp.solve(sp.Eq(dA, 0), x)
        except Exception:
            raw_sols = []

        # 2) Lọc nghiệm thực trong [0, L] (chuyển về số với tolerance)
        candidates = {0.0, float(L)}
        for sol in raw_sols:
            try:
                c = complex(sol.evalf())
            except Exception:
                continue
            if abs(c.imag) < 1e-8:
                xv = float(c.real)
                if 0.0 <= xv <= L:
                    candidates.add(xv)

        # Nếu không có nghiệm từ solve, thử lấy nghiệm số (nroots) — tuỳ trường hợp
        if len(candidates) <= 2:  # chỉ có biên
            try:
                nrs = sp.nroots(sp.together(sp.simplify(dA)))
                for r in nrs:
                    if abs(sp.im(r)) < 1e-8:
                        rv = float(sp.re(r))
                        if 0.0 <= rv <= L:
                            candidates.add(rv)
            except Exception:
                pass

        # 3) Đánh giá A(x) tại tất cả candidates — đây là cách "chắc ăn" để chọn min
        # Dùng lambdify cho hiệu năng (máy tính scalar => 'math' module)
        fA = sp.lambdify(x, A, 'math')
        best_x = None
        best_val = math.inf

        for xv in sorted(candidates):
            try:
                aval = float(fA(xv))
            except Exception:
                # bỏ qua trường hợp không thể tính (ví dụ domain error)
                continue
            if math.isfinite(aval) and aval < best_val:
                best_val = aval
                best_x = xv

        # 4) Dự phòng nếu không tìm được candidate hợp lệ
        if best_x is None:
            best_x = L / 2.0

        # 5) Chọn đoạn dây ứng với firstOrSecondShape
        if p["firstOrSecondShape"] == p["firstShape"]:
            length = float(best_x)
        else:
            length = float(L - best_x)

        # Định dạng đáp án theo format 2.17|2,17 (không có đơn vị)
        value = f"{length:.2f}"
        value_comma = value.replace(".", ",")
        return f"{value}|{value_comma}"

    def generate_question_text(self) -> str:
        p = self.parameters
        return (
            f"Một sợi dây kim loại dài {p['ropeLength']}{p['linearUnit']} được cắt thành hai đoạn. "
            f"Đoạn thứ nhất được uốn thành một {p['firstShape']}, đoạn thứ hai được uốn thành một {p['secondShape']}. "
            f"Hỏi khi tổng diện tích của {p['firstShape']} và {p['secondShape']} ở trên nhỏ nhất thì chiều dài đoạn dây uốn thành {p['firstOrSecondShape']} bằng bao nhiêu (làm tròn đến hàng phần trăm)?"
        )

    def generate_solution(self) -> str:
        p = self.parameters
        L = p["ropeLength"]
        unit = p["linearUnit"]
        x = sp.symbols('x', positive=True)

        # Các bước giải
        A1 = self.area_from_perimeter(p["firstShape"], x)
        A2 = self.area_from_perimeter(p["secondShape"], L - x)
        A = A1 + A2
        dA = sp.diff(A, x)

        steps = [
            "Lời giải:\n",
            f"Gọi \\(x\\) ({unit}) là độ dài đoạn dây uốn thành {p['firstShape']}\n",
            f"Khi đó đoạn còn lại là \\({L}-x\\)\n",
            f"Diện tích {p['firstShape']}: \\(S_1(x) = {sp.latex(A1)}\\)\n",
            f"Diện tích {p['secondShape']}: \\(S_2(x) = {sp.latex(A2)}\\)\n",
            f"Tổng diện tích: \\(S(x) = {sp.latex(A)}\\)\n",
            f"Đạo hàm: \\(S'(x) = {sp.latex(dA)}\\). Giải phương trình \\(S'(x)=0\\)\n"
        ]

        # Nghiệm tới hạn
        critical = sp.solve(sp.Eq(dA, 0), x)
        sols = [sp.latex(sol) for sol in critical if sol.is_real and 0 < sol.evalf() < L]
        if sols:
            steps.append(f"Nghiệm trong khoảng \\((0;{L})\\): \\(x = {', '.join(sols)}\\)\n")
        else:
            steps.append("Không có nghiệm trong \\((0;L)\\)\n")

        # Thêm bước xét đầu mút
        steps.append(
            f"Ta xét giá trị của \\(S(x)\\) tại các nghiệm trên và tại đầu mút "
            f"\\(x=0\\), \\(x={L}\\), rồi chọn giá trị nhỏ nhất\n"
        )
        return "\n".join(steps)

    # Thêm hàm tạo câu hỏi hoàn chỉnh
    def generate_question(self, question_number: int = 1) -> str:
        q_text = self.generate_question_text()
        solution = self.generate_solution()
        return f"Câu {question_number}: {q_text}\n\n{solution}\n\nĐáp án: {self.correct_answer}\n\n"


# ========================================================================================
# Question Manager
# ========================================================================================
class QuestionManager:
    def __init__(self):
        self.question_types = [RopeCutOptimizationQuestion]

    def generate_questions(self, num_questions: int) -> List[str]:
        questions = []
        for i in range(1, num_questions + 1):
            q = self.question_types[0]()
            questions.append(q.generate_question(i))
        return questions


# ========================================================================================
# Main
# ========================================================================================


def main():
    parser = argparse.ArgumentParser(description="Sinh câu hỏi tối ưu hóa cắt dây tạo hình")
    parser.add_argument('num_positional', nargs='?', type=int,
                        help='Số câu hỏi (tuỳ chọn, nếu cung cấp sẽ ghi đè --num-questions)')
    parser.add_argument('-n', '--num-questions', type=int, default=3,
                        help='Số câu hỏi cần sinh (mặc định: 3)')
    parser.add_argument('-o', '--output', type=str, default="rope_questions.tex",
                        help='Tên file đầu ra .tex')
    parser.add_argument('-t', '--title', type=str, default="Câu hỏi Tối ưu hóa Dây kim loại",
                        help='Tiêu đề tài liệu')
    args = parser.parse_args()

    # Nếu người dùng truyền tham số vị trí, ưu tiên nó
    if args.num_positional is not None:
        args.num_questions = args.num_positional

    qm = QuestionManager()
    questions = qm.generate_questions(args.num_questions)

    content = f"\\documentclass[a4paper,12pt]{{article}}\n"
    content += "\\usepackage{amsmath}\n\\begin{document}\n"
    content += f"\\title{{{args.title}}}\n\\maketitle\n\n"
    content += "\n".join(questions)
    content += "\\end{document}"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã tạo file {args.output} với {len(questions)} câu hỏi")


if __name__ == "__main__":
    main()
