"""
LaTeX Document Builder - Chuyên tạo và quản lý LaTeX documents
"""
from typing import List, Union, Tuple, Optional, Any
from enum import Enum


class OutputFormat(Enum):
    """Định nghĩa các format output"""
    IMMEDIATE_ANSWERS = 1  # Đáp án ngay sau mỗi câu hỏi
    ANSWERS_AT_END = 2     # Đáp án tập trung ở cuối


class LaTeXTemplate:
    """Quản lý template LaTeX"""
    
    # Template cơ bản
    DOCUMENT_HEADER = r"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}
\usepackage{{polyglossia}}
\setmainlanguage{{vietnamese}}
\setmainfont{{Times New Roman}}
\usepackage{{tikz}}
\usepackage{{tkz-tab}}
\usepackage{{tkz-euclide}}
\usetikzlibrary{{calc,decorations.pathmorphing,decorations.pathreplacing}}
\begin{{document}}
\title{{{title}}}
\author{{{author}}}
\maketitle

"""

    DOCUMENT_FOOTER = r"""
\end{document}"""

    ANSWER_SECTION_HEADER = r"""
\section*{Đáp án}"""

    @staticmethod
    def create_header(title: str, author: str = "dev") -> str:
        """Tạo header LaTeX với title và author"""
        return LaTeXTemplate.DOCUMENT_HEADER.format(title=title, author=author)


class LaTeXDocumentBuilder:
    """
    Builder class chuyên tạo LaTeX documents từ dữ liệu câu hỏi
    """
    
    def __init__(self, template: Optional[LaTeXTemplate] = None):
        """
        Khởi tạo builder với template tùy chọn
        
        Args:
            template: Template LaTeX tùy chỉnh (mặc định dùng LaTeXTemplate)
        """
        self.template = template or LaTeXTemplate()
        
    def build_document(
        self, 
        questions_data: List[Any], 
        title: str,
        output_format: OutputFormat,
        author: str = "dev"
    ) -> str:
        """
        Tạo document LaTeX hoàn chỉnh
        
        Args:
            questions_data: Dữ liệu câu hỏi
                - Nếu format=IMMEDIATE_ANSWERS: List[str] (câu hỏi hoàn chỉnh)
                - Nếu format=ANSWERS_AT_END: List[Tuple[str, str]] (content, answer)
            title: Tiêu đề tài liệu
            output_format: Định dạng output (OutputFormat enum)
            author: Tác giả (mặc định: "dev")
            
        Returns:
            str: Nội dung LaTeX hoàn chỉnh
            
        Raises:
            ValueError: Khi dữ liệu đầu vào không hợp lệ
        """
        if not questions_data:
            raise ValueError("Danh sách câu hỏi không được rỗng")
            
        if not title.strip():
            raise ValueError("Tiêu đề không được rỗng")
        
        # Tạo header
        latex_content = self.template.create_header(title, author)
        
        # Xử lý content theo format
        if output_format == OutputFormat.IMMEDIATE_ANSWERS:
            latex_content += self._format_immediate_answers(questions_data)
        elif output_format == OutputFormat.ANSWERS_AT_END:
            latex_content += self._format_answers_at_end(questions_data)
        else:
            raise ValueError(f"Format không hỗ trợ: {output_format}")
        
        # Thêm footer
        latex_content += self.template.DOCUMENT_FOOTER
        
        return latex_content
    
    def _format_immediate_answers(self, questions_data: List[Any]) -> str:
        """
        Format cho kiểu đáp án ngay sau mỗi câu hỏi
        
        Args:
            questions_data: Danh sách câu hỏi hoàn chỉnh
            
        Returns:
            str: Nội dung được format
        """
        if not all(isinstance(q, str) for q in questions_data):
            raise ValueError("Với format IMMEDIATE_ANSWERS, tất cả items phải là string")
            
        return "\n\n".join(questions_data)
    
    def _format_answers_at_end(self, questions_data: List[Any]) -> str:
        """
        Format cho kiểu đáp án ở cuối
        
        Args:
            questions_data: Danh sách tuple (question_content, correct_answer)
            
        Returns:
            str: Nội dung được format
        """
        if not all(isinstance(q, tuple) and len(q) == 2 for q in questions_data):
            raise ValueError("Với format ANSWERS_AT_END, tất cả items phải là tuple (content, answer)")
        
        # Tách questions và answers
        questions = [q[0] for q in questions_data]
        answers = [q[1] for q in questions_data]
        
        # Join questions
        content = "\n\n".join(questions)
        
        # Thêm section đáp án
        content += self.template.ANSWER_SECTION_HEADER
        
        # Thêm từng đáp án
        for idx, answer in enumerate(answers, 1):
            content += f"\n\\textbf{{Câu {idx}}}: {answer}"
            
        return content

    @staticmethod
    def format_to_enum(format_int: int) -> OutputFormat:
        """
        Chuyển đổi integer format sang OutputFormat enum
        
        Args:
            format_int: 1 hoặc 2
            
        Returns:
            OutputFormat enum
            
        Raises:
            ValueError: Khi format không hợp lệ
        """
        if format_int == 1:
            return OutputFormat.IMMEDIATE_ANSWERS
        elif format_int == 2:
            return OutputFormat.ANSWERS_AT_END
        else:
            raise ValueError(f"Format không hợp lệ: {format_int}. Chỉ hỗ trợ 1 hoặc 2")
