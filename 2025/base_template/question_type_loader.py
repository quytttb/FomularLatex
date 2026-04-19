"""
Question Type Loader - Quản lý việc load và import các loại câu hỏi
"""
from typing import List, Type, Tuple, Dict, Any, Optional
import importlib
import logging


class QuestionTypeLoader:
    """
    Class chuyên load và quản lý các loại câu hỏi từ modules khác nhau
    """
    
    def __init__(self, silent: bool = False):
        """
        Khởi tạo loader
        
        Args:
            silent: True để không in thông báo load, False để in chi tiết
        """
        self.silent = silent
        self.loaded_types: List[Type] = []
        self.failed_loads: Dict[str, str] = {}
        
    def add_module_mapping(self, module_name: str, class_name: str) -> None:
        """
        Thêm mapping module-class để load
        
        Args:
            module_name: Tên module để import
            class_name: Tên class trong module
        """
        try:
            question_class = self._load_single_module(module_name, class_name)
            if question_class:
                self.loaded_types.append(question_class)
                if not self.silent:
                    print(f"✅ Đã load thành công: {class_name} từ {module_name}")
        except Exception as e:
            self.failed_loads[f"{module_name}.{class_name}"] = str(e)
            if not self.silent:
                print(f"❌ Lỗi khi load {class_name} từ {module_name}: {e}")
    
    def load_available_types(self, modules_mapping: Optional[List[Tuple[str, str]]] = None) -> List[Type]:
        """
        Load tất cả các loại câu hỏi khả dụng
        
        Args:
            modules_mapping: Danh sách (module_name, class_name) để load.
                           Nếu None, sẽ dùng mapping mặc định.
        
        Returns:
            List[Type]: Danh sách các class câu hỏi đã load thành công
        """
        if modules_mapping is None:
            modules_mapping = self._get_default_modules_mapping()
        
        self.loaded_types.clear()
        self.failed_loads.clear()
        
        for module_name, class_name in modules_mapping:
            self.add_module_mapping(module_name, class_name)
        
        # In summary
        if not self.silent:
            self._print_load_summary()
        
        return self.loaded_types.copy()
    
    def get_loaded_types(self) -> List[Type]:
        """
        Trả về danh sách các types đã load
        
        Returns:
            List[Type]: Danh sách các class đã load
        """
        return self.loaded_types.copy()
    
    def get_failed_loads(self) -> Dict[str, str]:
        """
        Trả về danh sách các module/class load thất bại và lý do
        
        Returns:
            Dict[str, str]: {module.class: error_message}
        """
        return self.failed_loads.copy()
    
    def _load_single_module(self, module_name: str, class_name: str) -> Type:
        """
        Load một module và lấy class từ đó
        
        Args:
            module_name: Tên module
            class_name: Tên class
            
        Returns:
            Type: Class đã load
            
        Raises:
            ImportError: Khi không thể import module
            AttributeError: Khi class không tồn tại trong module
        """
        try:
            # Import module sử dụng importlib
            module = importlib.import_module(module_name)
            
            # Kiểm tra class có tồn tại
            if not hasattr(module, class_name):
                raise AttributeError(f"Class {class_name} không tồn tại trong module {module_name}")
            
            # Lấy class
            question_class = getattr(module, class_name)
            
            # Validate class (optional - có thể thêm validation logic)
            self._validate_question_class(question_class, class_name)
            
            return question_class
            
        except ImportError as e:
            raise ImportError(f"Không thể import module {module_name}: {e}")
        except Exception as e:
            raise Exception(f"Lỗi không xác định khi load {module_name}.{class_name}: {e}")
    
    def _validate_question_class(self, question_class: Type, class_name: str) -> None:
        """
        Validate class có đúng là question class không
        
        Args:
            question_class: Class cần validate
            class_name: Tên class để báo lỗi
            
        Raises:
            ValueError: Khi class không hợp lệ
        """
        # Kiểm tra có phải class không
        if not isinstance(question_class, type):
            raise ValueError(f"{class_name} không phải là một class")
        
        # Có thể thêm các validation khác như:
        # - Kiểm tra inherit từ BaseOptimizationQuestion
        # - Kiểm tra có các method required không
        # - etc.
    
    def _get_default_modules_mapping(self) -> List[Tuple[str, str]]:
        """
        Trả về mapping mặc định của modules và classes
        
        Returns:
            List[Tuple[str, str]]: Danh sách (module_name, class_name)
        """
        return [
            ("force_equilibrium_three_legs", "CanBangLucBaChan"),
            # Có thể thêm modules khác ở đây trong tương lai
            # ("optimization_problem_2", "OptimizationProblem2"),
            # ("calculus_problems", "CalculusQuestion"),
        ]
    
    def _print_load_summary(self) -> None:
        """In summary về quá trình load"""
        successful_count = len(self.loaded_types)
        failed_count = len(self.failed_loads)
        
        if failed_count > 0:
            print(f"⚠️  Có {failed_count} module/class load thất bại:")
            for module_class, error in self.failed_loads.items():
                print(f"   - {module_class}: {error}")
        
        if successful_count == 0:
            print("⚠️  Không có dạng toán nào được load. Hệ thống có thể không hoạt động đúng.")
        else:
            print(f"📚 Tổng cộng đã load {successful_count} dạng toán")


# Convenience function để dùng trực tiếp (backward compatibility)
def get_available_question_types(silent: bool = False) -> List[Type]:
    """
    Hàm tiện ích để load các loại câu hỏi (tương thích với code cũ)
    
    Args:
        silent: True để không in thông báo
        
    Returns:
        List[Type]: Danh sách các class câu hỏi
    """
    loader = QuestionTypeLoader(silent=silent)
    return loader.load_available_types()
