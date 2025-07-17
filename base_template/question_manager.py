"""
Question Manager - Quản lý quá trình sinh câu hỏi với retry, timeout và error handling
"""
import random
import signal
from typing import List, Type, Union, Tuple, Any, Optional
from question_type_loader import QuestionTypeLoader


class QuestionTimeoutError(Exception):
    """Exception cho timeout khi sinh câu hỏi"""
    pass


class QuestionGenerationError(Exception):
    """Exception cho lỗi sinh câu hỏi"""
    pass


class QuestionManager:
    """
    Manager class quản lý quá trình sinh câu hỏi với các tính năng:
    - Retry mechanism
    - Timeout protection
    - Error handling và reporting
    - Progress tracking
    """
    
    # Constants
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT_SECONDS = 30
    
    def __init__(
        self, 
        question_types: Optional[List[Type]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    ):
        """
        Khởi tạo QuestionManager
        
        Args:
            question_types: Danh sách các class câu hỏi khả dụng
            max_retries: Số lần thử lại tối đa khi sinh câu hỏi thất bại
            timeout_seconds: Timeout (giây) cho mỗi lần sinh câu hỏi
        """
        self.question_types = question_types or []
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.failed_count = 0
        self.stats = {
            'total_generated': 0,
            'total_failed': 0,
            'retry_attempts': 0,
            'timeout_errors': 0
        }
        
    def set_question_types(self, question_types: List[Type]) -> None:
        """
        Cập nhật danh sách question types
        
        Args:
            question_types: Danh sách class câu hỏi mới
        """
        self.question_types = question_types
        
    def generate_questions(
        self, 
        num_questions: int, 
        output_format: int, 
        verbose: bool = False
    ) -> List[Union[str, Tuple[str, str]]]:
        """
        Sinh danh sách câu hỏi với retry và timeout protection
        
        Args:
            num_questions: Số lượng câu hỏi cần sinh
            output_format: 1 - đáp án sau từng câu, 2 - đáp án ở cuối
            verbose: In chi tiết quá trình sinh câu hỏi
            
        Returns:
            List[Union[str, Tuple[str, str]]]: Danh sách câu hỏi đã sinh
            
        Raises:
            QuestionGenerationError: Khi không thể sinh được câu hỏi nào
            ValueError: Khi tham số không hợp lệ
        """
        # Validate input
        if num_questions <= 0:
            raise ValueError("Số câu hỏi phải lớn hơn 0")
            
        if not self.question_types:
            raise QuestionGenerationError("Không có loại câu hỏi nào khả dụng")
            
        if output_format not in [1, 2]:
            raise ValueError("Format chỉ có thể là 1 hoặc 2")
        
        # Reset stats
        self.stats = {
            'total_generated': 0,
            'total_failed': 0,
            'retry_attempts': 0,
            'timeout_errors': 0
        }
        self.failed_count = 0
        
        questions_data = []
        
        if verbose:
            print(f"📋 Có {len(self.question_types)} loại câu hỏi khả dụng")
            
        for i in range(1, num_questions + 1):
            question_result = self._generate_single_question(i, output_format, verbose)
            if question_result is not None:
                questions_data.append(question_result)
                self.stats['total_generated'] += 1
            else:
                self.stats['total_failed'] += 1
        
        # Report final stats
        if self.failed_count > 0:
            print(f"⚠️  Có {self.failed_count} câu hỏi không tạo được")
            
        if verbose:
            self._print_final_stats()
            
        if not questions_data:
            raise QuestionGenerationError("Không thể tạo được câu hỏi nào")
            
        return questions_data
    
    def _generate_single_question(
        self, 
        question_number: int, 
        output_format: int, 
        verbose: bool
    ) -> Union[str, Tuple[str, str], None]:
        """
        Sinh một câu hỏi duy nhất với retry mechanism
        
        Args:
            question_number: Số thứ tự câu hỏi
            output_format: Format output
            verbose: Verbose mode
            
        Returns:
            Union[str, Tuple[str, str], None]: Câu hỏi đã sinh hoặc None nếu thất bại
        """
        for retry in range(self.max_retries):
            try:
                # Setup timeout
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.timeout_seconds)
                
                # Random chọn loại câu hỏi
                question_type = random.choice(self.question_types)
                question_instance = question_type()
                
                # Generate dựa trên format
                if output_format == 1:
                    result = question_instance.generate_question(question_number, include_multiple_choice=True)
                else:
                    result = question_instance.generate_question(question_number, include_multiple_choice=False)
                
                # Cancel timeout
                signal.alarm(0)
                
                if verbose:
                    print(f"✅ Đã tạo thành công câu hỏi {question_number} (loại: {question_type.__name__})")
                
                return result
                
            except QuestionTimeoutError:
                signal.alarm(0)  # Cancel timeout
                self.stats['timeout_errors'] += 1
                error_msg = f"Timeout tạo câu hỏi {question_number}"
                self._handle_retry_error(retry, question_number, error_msg, verbose)
                
            except Exception as e:
                signal.alarm(0)  # Cancel timeout
                error_msg = f"Lỗi tạo câu hỏi {question_number}: {e}"
                self._handle_retry_error(retry, question_number, error_msg, verbose)
            
            self.stats['retry_attempts'] += 1
        
        # Tất cả retry đều thất bại
        self.failed_count += 1
        return None
    
    def _handle_retry_error(
        self, 
        retry: int, 
        question_number: int, 
        error_msg: str, 
        verbose: bool
    ) -> None:
        """
        Xử lý error trong retry loop
        
        Args:
            retry: Lần thử hiện tại (0-based)
            question_number: Số câu hỏi
            error_msg: Thông báo lỗi
            verbose: Verbose mode
        """
        if retry == self.max_retries - 1:
            # Lần thử cuối cũng thất bại
            print(f"❌ {error_msg} sau {self.max_retries} lần thử")
        elif verbose:
            # Chưa phải lần thử cuối, và đang ở verbose mode
            print(f"⚠️  {error_msg}, thử lại ({retry + 1}/{self.max_retries})")
    
    def _timeout_handler(self, signum, frame):
        """
        Signal handler cho timeout
        
        Args:
            signum: Signal number
            frame: Frame object
            
        Raises:
            QuestionTimeoutError: Luôn raise timeout error
        """
        raise QuestionTimeoutError("Quá thời gian tạo câu hỏi")
    
    def _print_final_stats(self) -> None:
        """In thống kê cuối cùng"""
        print(f"📊 Thống kê sinh câu hỏi:")
        print(f"   - Tổng số sinh thành công: {self.stats['total_generated']}")
        print(f"   - Tổng số thất bại: {self.stats['total_failed']}")
        print(f"   - Số lần retry: {self.stats['retry_attempts']}")
        print(f"   - Số lần timeout: {self.stats['timeout_errors']}")
    
    def get_stats(self) -> dict:
        """
        Trả về thống kê hiện tại
        
        Returns:
            dict: Dictionary chứa các thống kê
        """
        return self.stats.copy()


# Convenience function để dùng trực tiếp
def generate_questions_with_manager(
    num_questions: int,
    output_format: int,
    question_types: Optional[List[Type]] = None,
    verbose: bool = False,
    max_retries: int = QuestionManager.DEFAULT_MAX_RETRIES,
    timeout_seconds: int = QuestionManager.DEFAULT_TIMEOUT_SECONDS
) -> List[Union[str, Tuple[str, str]]]:
    """
    Hàm tiện ích để sinh câu hỏi sử dụng QuestionManager
    
    Args:
        num_questions: Số câu hỏi cần sinh
        output_format: Format output (1 hoặc 2)
        question_types: Danh sách question types (nếu None sẽ auto-load)
        verbose: Verbose mode
        max_retries: Số lần retry tối đa
        timeout_seconds: Timeout cho mỗi câu hỏi
        
    Returns:
        List[Union[str, Tuple[str, str]]]: Danh sách câu hỏi
    """
    if question_types is None:
        loader = QuestionTypeLoader(silent=not verbose)
        question_types = loader.load_available_types()
    
    manager = QuestionManager(
        question_types=question_types,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds
    )
    
    return manager.generate_questions(num_questions, output_format, verbose)
