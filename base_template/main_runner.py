# Imports for new architecture
from question_type_loader import QuestionTypeLoader
from question_manager import QuestionManager  
from latex_document_builder import LaTeXDocumentBuilder, OutputFormat
from latex_document_builder import LaTeXDocumentBuilder, OutputFormat
from question_manager import QuestionManager
from question_type_loader import QuestionTypeLoader
import argparse
import logging
import sys
from typing import List, Tuple, Union, Any

# Hằng số cấu hình mặc định
DEFAULT_NUM_QUESTIONS = 3  # Số câu hỏi mặc định
DEFAULT_FORMAT = 1         # 1: đáp án sau từng câu, 2: đáp án ở cuối
DEFAULT_FILENAME = "optimization_questions.tex"  # Tên file xuất ra mặc định
DEFAULT_TITLE = "Câu hỏi Tối ưu hóa"             # Tiêu đề mặc định


def parse_arguments() -> argparse.Namespace:
    """
    Xử lý và lấy các tham số dòng lệnh từ người dùng.
    Trả về đối tượng Namespace chứa các tham số đã parse.
    """
    parser = argparse.ArgumentParser(
        description="Generator câu hỏi tối ưu hóa với hỗ trợ 2 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python3 main_runner.py                    # Tạo 3 câu hỏi, format 1
  python3 main_runner.py 5                  # Tạo 5 câu hỏi, format 1
  python3 main_runner.py 5 2                # Tạo 5 câu hỏi, format 2
  python3 main_runner.py -n 10 -f 2 -o test.tex  # Tùy chỉnh đầy đủ
        """
    )
    
    parser.add_argument(
        'num_questions', 
        nargs='?', 
        type=int, 
        default=DEFAULT_NUM_QUESTIONS,
        help=f'Số câu hỏi cần tạo (mặc định: {DEFAULT_NUM_QUESTIONS})'
    )
    
    parser.add_argument(
        'format', 
        nargs='?', 
        type=int, 
        choices=[1, 2], 
        default=DEFAULT_FORMAT,
        help=f'Format: 1=đáp án ngay sau câu hỏi, 2=đáp án ở cuối (mặc định: {DEFAULT_FORMAT})'
    )
    
    parser.add_argument(
        '-n', '--num-questions',
        type=int,
        dest='num_questions_override',
        help='Số câu hỏi cần tạo (ghi đè positional argument)'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=int,
        choices=[1, 2],
        dest='format_override',
        help='Format output (ghi đè positional argument)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=DEFAULT_FILENAME,
        help=f'Tên file output (mặc định: {DEFAULT_FILENAME})'
    )
    
    parser.add_argument(
        '-t', '--title',
        type=str,
        default=DEFAULT_TITLE,
        help=f'Tiêu đề document (mặc định: "{DEFAULT_TITLE}")'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Hiển thị thông tin chi tiết'
    )
    
    args = parser.parse_args()
    
    # Override positional args with named args if provided
    if args.num_questions_override is not None:
        args.num_questions = args.num_questions_override
    if args.format_override is not None:
        args.format = args.format_override
        
    # Validate
    if args.num_questions <= 0:
        parser.error("Số câu hỏi phải lớn hơn 0")
        
    return args


def generate_questions(num_questions: int, output_format: int, verbose: bool = False) -> List[Any]:
    """
    Sinh danh sách câu hỏi tối ưu hóa theo định dạng mong muốn.
    
    Tham số:
        num_questions: Số lượng câu hỏi cần sinh
        output_format: 1 - đáp án sau từng câu, 2 - đáp án ở cuối
        verbose: In chi tiết quá trình sinh câu hỏi
    Trả về:
        Danh sách câu hỏi (dạng string hoặc tuple tuỳ format)
    """
    # Load question types
    loader = QuestionTypeLoader(silent=not verbose)
    question_types = loader.load_available_types()
    
    # Create manager và sinh câu hỏi
    manager = QuestionManager(question_types=question_types)
    return manager.generate_questions(num_questions, output_format, verbose)


def create_latex_file(questions_data: List, filename: str, title: str, output_format: int) -> None:
    """
    Tạo file LaTeX chứa danh sách câu hỏi đã sinh.
    
    Tham số:
        questions_data: Danh sách câu hỏi
        filename: Tên file xuất ra
        title: Tiêu đề tài liệu
        output_format: Định dạng đáp án
    """
    try:
        latex_builder = LaTeXDocumentBuilder()
        output_format_enum = OutputFormat.IMMEDIATE_ANSWERS if output_format == 1 else OutputFormat.ANSWERS_AT_END
        
        latex_content = latex_builder.build_document(questions_data, title, output_format_enum)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_content)
            
    except IOError as e:
        raise IOError(f"Không thể ghi file {filename}: {e}")


def main() -> None:
    """
    Hàm main: điều phối toàn bộ quá trình sinh câu hỏi tối ưu hóa và xuất ra file LaTeX.
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
            
        # Generate questions
        questions_data = generate_questions(
            args.num_questions, 
            args.format, 
            args.verbose
        )
        
        if not questions_data:
            print("❌ Lỗi: Không tạo được câu hỏi nào")
            sys.exit(1)
            
        # Create LaTeX file
        create_latex_file(questions_data, args.output, args.title, args.format)
        
        # Success messages
        print(f"✅ Đã tạo thành công {args.output} với {len(questions_data)} câu hỏi")
        print(f"📄 Biên dịch bằng: xelatex {args.output}")
        print(f"📋 Format: {args.format} ({'đáp án ngay sau câu hỏi' if args.format == 1 else 'đáp án ở cuối'})")
        
    except KeyboardInterrupt:
        print("\n❌ Đã hủy bởi người dùng")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Lỗi tham số: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"❌ Lỗi file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
