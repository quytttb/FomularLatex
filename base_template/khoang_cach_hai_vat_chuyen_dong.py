import random
import math
import sympy as sp
from typing import Dict, Any, List
from base_optimization_question import BaseOptimizationQuestion
from latex_utils import format_number_clean, clean_and_optimize_latex
from scipy.optimize import minimize_scalar

class KhoangCachHaiVatChuyenDongQuestion(BaseOptimizationQuestion):
    """
    Dạng toán cực trị hình học: Tìm khoảng cách nhỏ nhất giữa hai vật chuyển động trong hình hộp chữ nhật.
    """
    def generate_parameters(self) -> Dict[str, Any]:
        # Random các thông số hình học (giữ trong khoảng hợp lý)
        AB = random.randint(10, 25)
        while True:
            AC = random.randint(15, 30)
            if AC > AB:
                break
        AA_prime = random.randint(8, 20)
        v_M = round(random.uniform(1.0, 3.0), 1)
        v_N = round(random.uniform(1.5, 3.5), 1)
        return {
            'AB': AB,
            'AC': AC,
            'AA_prime': AA_prime,
            'v_M': v_M,
            'v_N': v_N
        }

    def calculate_answer(self) -> str:
        p = self.parameters
        AB = p['AB']
        AC = p['AC']
        AA_prime = p['AA_prime']
        v_M = p['v_M']
        v_N = p['v_N']
        # Tính toán các biến process
        BC = sp.sqrt(AC ** 2 - AB ** 2)
        BC_numeric = float(BC.evalf())
        distance_B_prime_A = math.sqrt(AB ** 2 + AA_prime ** 2)
        distance_CD_prime = AA_prime
        coefficient_Mx = v_M * AB / distance_B_prime_A
        coefficient_Mz = v_M * AA_prime / distance_B_prime_A
        def position_M(t):
            x = AB - coefficient_Mx * t
            y = 0
            z = AA_prime - coefficient_Mz * t
            return (x, y, z)
        def position_N(t):
            x = 0
            y = BC_numeric
            z = v_N * t
            return (x, y, z)
        def distance_function(t):
            pos_M = position_M(t)
            pos_N = position_N(t)
            dx = pos_M[0] - pos_N[0]
            dy = pos_M[1] - pos_N[1]
            dz = pos_M[2] - pos_N[2]
            return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        t_max_M = distance_B_prime_A / v_M
        t_max_N = distance_CD_prime / v_N
        t_max = min(t_max_M, t_max_N)
        result = minimize_scalar(distance_function, bounds=(0, t_max), method='bounded')
        self._solution_cache = {
            'AB': AB, 'AC': AC, 'AA_prime': AA_prime, 'v_M': v_M, 'v_N': v_N,
            'BC': BC, 'BC_numeric': BC_numeric, 'distance_B_prime_A': distance_B_prime_A,
            'coefficient_Mx': coefficient_Mx, 'coefficient_Mz': coefficient_Mz,
            't_optimal': result.x, 'd_min': result.fun
        }
        return format_number_clean(round(float(result.fun), 1), precision=1)

    def generate_wrong_answers(self) -> List[str]:
        # Sinh đáp án sai hợp lý quanh đáp án đúng
        correct_str = self.correct_answer
        if correct_str is None:
            correct_str = self.calculate_answer()
        correct = float(str(correct_str).replace(',', '.'))
        wrongs = set()
        tries = 0
        while len(wrongs) < 3 and tries < 20:
            tries += 1
            delta = random.choice([-2, -1, -0.5, 0.5, 1, 2])
            wrong = round(correct + delta, 1)
            if abs(wrong - correct) < 0.2 or wrong <= 0:
                continue
            wrongs.add(format_number_clean(wrong, precision=1))
        return list(wrongs)

    def generate_question_text(self) -> str:
        p = self.parameters
        AB = p['AB']
        AC = p['AC']
        AA_prime = p['AA_prime']
        v_M = p['v_M']
        v_N = p['v_N']
        tikz_picture = r"""
\begin{tikzpicture}[scale=1.0]
% Định nghĩa các đỉnh của hình hộp với phép chiếu đúng
\coordinate (B) at (0,0);
\coordinate (C) at (4,0);
\coordinate (A) at (1.5,1.5);
\coordinate (D) at (5.5,1.5);
\coordinate (B') at (0,3);
\coordinate (C') at (4,3);
\coordinate (A') at (1.5,4.5);
\coordinate (D') at (5.5,4.5);
% Vẽ các cạnh nhìn thấy của hình hộp
\draw (B) -- (C);
\draw (B') -- (C') -- (D') -- (A') -- cycle;
\draw (B) -- (B');
\draw (C) -- (C');
\draw (C) -- (D);
\draw (D) -- (D');
% Vẽ các cạnh ẩn bằng đường đứt nét
\draw[dashed] (B) -- (A);
\draw[dashed] (A) -- (D);
\draw[dashed] (A') -- (A);
% Định nghĩa điểm M trên đường chéo AB'
\coordinate (M) at (0.75,2.25);
% Định nghĩa điểm N trên cạnh CD'
\coordinate (N) at (4.75,2.25);
% Vẽ đường chéo AB' bằng đường đứt nét đỏ (nhưng dùng màu đen theo yêu cầu)
\draw[dashed, thick] (A) -- (B');
% Vẽ đường từ C đến N đến D' (đường xanh trong gốc, nhưng dùng màu đen)
\draw[thick] (C) -- (N) -- (D');
% Vẽ các mũi tên
\draw[->, thick] (0.1,2.7) -- (0.5,2.3);  % Mũi tên từ B' về phía M
\draw[->, thick] (4.17,0.3) -- (4.57,1.4);
% Đánh dấu các điểm
\fill (A) circle (1.2pt);
\fill (B) circle (1.2pt);
\fill (C) circle (1.2pt);
\fill (D) circle (1.2pt);
\fill (A') circle (1.2pt);
\fill (B') circle (1.2pt);
\fill (C') circle (1.2pt);
\fill (D') circle (1.2pt);
\fill (M) circle (1.2pt);
\fill (N) circle (1.2pt);
% Gắn nhãn cho các điểm
\node[below right] at (A) {$A$};
\node[below left] at (B) {$B$};
\node[below right] at (C) {$C$};
\node[below right] at (D) {$D$};
\node[above right] at (A') {$A'$};
\node[above left] at (B') {$B'$};
\node[above left] at (C') {$C'$};
\node[above right] at (D') {$D'$};
\node[right] at (M) {$M$};
\node[right] at (N) {$N$};
\end{tikzpicture}
"""
        return f"""Cho một hình hộp chữ nhật $ABCD.A'B'C'D'$ có $AB={AB}$, $AC={AC}$, $AA'={AA_prime}$ như hình vẽ. Hai con kiến chuyển động thẳng đều: $M$ bò từ $B'$ đến $A$ với tốc độ ${v_M}\ \mathrm{{cm/s}}$, $N$ bò từ $C$ đến $D'$ với tốc độ ${v_N}\ \mathrm{{cm/s}}$. Tính khoảng cách nhỏ nhất giữa hai con kiến (làm tròn đến 0.1cm)?\\
{tikz_picture}
"""

    def generate_solution(self) -> str:
        p = self.parameters
        cache = getattr(self, '_solution_cache', None)
        if cache is None:
            self.calculate_answer()
            cache = self._solution_cache
        AB = cache['AB']
        AC = cache['AC']
        AA_prime = cache['AA_prime']
        v_M = cache['v_M']
        v_N = cache['v_N']
        BC = cache['BC']
        BC_numeric = cache['BC_numeric']
        distance_B_prime_A = cache['distance_B_prime_A']
        coefficient_Mx = cache['coefficient_Mx']
        coefficient_Mz = cache['coefficient_Mz']
        t_optimal = cache['t_optimal']
        d_min = cache['d_min']
        latex_BC = sp.latex(BC)
        return f"""
Dữ kiện:
+ $AB = {AB}$, $AC = {AC}$, $AA' = {AA_prime}$
+ $A = (0, 0, 0)$, $B = ({AB}, 0, 0)$, $C = (0, {latex_BC}, 0)$, $B' = ({AB}, 0, {AA_prime})$, $D' = (0, {latex_BC}, {AA_prime})$
+ $M$ bò từ $B'$ đến $A$ với tốc độ ${v_M}$ cm/s, $N$ bò từ $C$ đến $D'$ với tốc độ ${v_N}$ cm/s

Bước 1: Phương trình chuyển động

$\overrightarrow{{B'A}} = ( {-AB}, 0, {-AA_prime} )$, $|\overrightarrow{{B'A}}| = \sqrt{{{AB}^2 + {AA_prime}^2}}$

Vận tốc $M$: $\overrightarrow{{v}}_M = \frac{{{v_M}}}{{\sqrt{{{AB ** 2 + AA_prime ** 2}}}}} \cdot ( {-AB}, 0, {-AA_prime} )$

Vị trí $M(t)$: $({AB} - {coefficient_Mx:.1f}t,\ 0,\ {AA_prime} - {coefficient_Mz:.1f}t)$

$N(t) = (0, {latex_BC}, {v_N}t)$

Bước 2: Khoảng cách tại thời điểm $t$:

$d(t) = \sqrt{{({AB} - {coefficient_Mx:.1f}t)^2 + {BC_numeric:.2f}^2 + ({AA_prime} - {coefficient_Mz:.1f}t - {v_N}t)^2}}$

Bước 3: Tìm $d_{min}$

$t^* \approx {t_optimal:.2f}$, $d_{{min}} \approx {d_min:.1f}$ cm (làm tròn 0.1cm)
"""

if __name__ == "__main__":
    # Test sinh 1 đề và xuất ra LaTeX
    from latex_document_builder import LaTeXDocumentBuilder, OutputFormat
    q = KhoangCachHaiVatChuyenDongQuestion()
    # Sinh đề trắc nghiệm ABCD
    question_str = q.generate_question(1, include_multiple_choice=True)
    print("\n===== ĐỀ TRẮC NGHIỆM ABCD =====\n")
    print(question_str)
    # Sinh đề đáp án ở cuối
    question_tuple = q.generate_question(1, include_multiple_choice=False)
    print("\n===== ĐỀ + ĐÁP ÁN Ở CUỐI =====\n")
    print(question_tuple[0])
    print("\nĐáp án đúng:", question_tuple[1])
    # Xuất ra file LaTeX
    builder = LaTeXDocumentBuilder()
    latex_content = builder.build_document([question_str], title="Bài toán khoảng cách hai vật chuyển động", output_format=OutputFormat.IMMEDIATE_ANSWERS)
    with open("khoang_cach_hai_vat_chuyen_dong_test.tex", "w", encoding="utf-8") as f:
        f.write(latex_content)
    print("\nĐã xuất ra file khoang_cach_hai_vat_chuyen_dong_test.tex (LaTeX)") 