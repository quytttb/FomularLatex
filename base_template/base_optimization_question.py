import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseOptimizationQuestion(ABC):
    """
    Lớp cơ sở cho tất cả các dạng bài toán tối ưu hóa
    """

    def __init__(self):
        self.parameters = {}
        self.correct_answer = None
        self.wrong_answers = []
        self.solution_steps = []

    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Sinh tham số ngẫu nhiên cho bài toán"""
        pass

    @abstractmethod
    def calculate_answer(self) -> str:
        """
        Tính đáp án đúng dựa trên parameters
        LƯU Ý: Không được dùng các hàm format hoặc f-string trong hàm này
        vì tính toán phải chuẩn, không làm tròn hoặc định dạng
        """
        pass

    @abstractmethod
    def generate_wrong_answers(self) -> List[str]:
        """
        Sinh 3 đáp án sai hợp lý

        Returns:
            List[str]: Danh sách chứa đúng 3 đáp án sai, không trùng với đáp án đúng

        Note:
            - Phải đảm bảo trả về đúng 3 đáp án
            - Các đáp án phải khác nhau và khác với đáp án đúng
            - Các đáp án sai nên hợp lý và có tính nhiễu cao
        """
        pass

    @abstractmethod
    def generate_question_text(self) -> str:
        """
        Sinh đề bài câu hỏi

        Returns:
            str: Nội dung đề bài dạng LaTeX

        Note:
            - Sử dụng định dạng LaTeX cho các công thức toán học
            - Đề bài phải rõ ràng, đầy đủ thông tin
        """
        pass

    @abstractmethod
    def generate_solution(self) -> str:
        """
        Sinh lời giải chi tiết bằng LaTeX

        Returns:
            str: Lời giải chi tiết dạng LaTeX

        Note:
            1. Có thể sử dụng các hàm format hoặc f-string trong hàm này,
               vì phần này chỉ để hiển thị, không ảnh hưởng đến tính toán
            2. Không được tính toán lại đáp án trong hàm này,
               vì đáp án đã được tính toán trong calculate_answer()
            3. Lời giải phải chi tiết, dễ hiểu và có các bước logic
        """
        pass

    def generate_question(self, question_number: int = 1, include_multiple_choice: bool = True):
        """
        Tạo câu hỏi

        Args:
            question_number (int): Số thứ tự câu hỏi (mặc định: 1)
            include_multiple_choice (bool): True để tạo câu hỏi trắc nghiệm A/B/C/D,
                                          False để chỉ tạo đề bài và lời giải

        Returns:
            str | tuple: 
                - Nếu include_multiple_choice=True: str (câu hỏi hoàn chỉnh với đáp án)
                - Nếu include_multiple_choice=False: tuple (question_content, correct_answer)

        Raises:
            ValueError: Khi include_multiple_choice=True và generate_wrong_answers() 
                       không trả về đúng 3 đáp án hoặc có đáp án trùng nhau
        """
        print(f"Đang tạo câu hỏi {question_number}")
        
        # Sinh tham số và tính toán chung
        self.parameters = self.generate_parameters()
        self.correct_answer = self.calculate_answer()
        question_text = self.generate_question_text()
        solution = self.generate_solution()
        
        # Tạo nội dung cơ bản
        question_content = f"Câu {question_number}: {question_text}\n\n"
        
        if include_multiple_choice:
            # Tạo câu hỏi trắc nghiệm với 4 đáp án A/B/C/D
            self.wrong_answers = self.generate_wrong_answers()

            # Kiểm soát số lượng đáp án sai
            if len(self.wrong_answers) != 3:
                raise ValueError(
                    f"generate_wrong_answers() phải trả về đúng 3 đáp án sai, nhưng đã trả về {len(self.wrong_answers)} đáp án"
                )

            # Kiểm tra đáp án trùng nhau
            all_answers = [self.correct_answer] + self.wrong_answers
            if len(set(all_answers)) != 4:
                duplicates = [ans for ans in all_answers if all_answers.count(ans) > 1]
                raise ValueError(
                    f"Có đáp án trùng nhau: {duplicates}. Tất cả 4 đáp án phải khác nhau."
                )

            # Trộn đáp án và tạo format trắc nghiệm
            random.shuffle(all_answers)
            correct_index = all_answers.index(self.correct_answer)

            # Sử dụng môi trường choices của LaTeX
            question_content += "\\begin{choices}\n"
            for j, ans in enumerate(all_answers):
                # Không đánh dấu * trong LaTeX, chỉ dùng cho kiểm tra nội bộ
                question_content += f"  \\choice {ans}\\n"
            question_content += "\\end{choices}\n\n"

            question_content += f"Lời giải:\n\n{solution}\n\n"
            return question_content
        else:
            # Chỉ tạo đề bài và lời giải (không có đáp án trắc nghiệm)
            question_content += f"Lời giải:\n\n{solution}\n\n"
            return question_content, self.correct_answer
