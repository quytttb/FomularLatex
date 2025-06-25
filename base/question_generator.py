"""
Abstract base classes for math question generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union
import random
import logging
from .constants import QuestionConfig
from .latex_formatter import LaTeXFormatter
from .math_utils import standardize_math_expression


class QuestionGenerator(ABC):
    """Abstract base class for all question generators."""
    
    def __init__(self, question_type: str = "Math Question"):
        """Initialize the question generator.
        
        Args:
            question_type: Type description for this generator
        """
        self.question_type = question_type
        self.formatter = LaTeXFormatter()
        self.config = QuestionConfig()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def generate_parameters(self) -> Dict[str, Any]:
        """Generate random parameters for the question.
        
        Returns:
            Dictionary of parameters for the question
        """
        pass
    
    @abstractmethod
    def calculate_solution(self, params: Dict[str, Any]) -> Any:
        """Calculate the correct answer for given parameters.
        
        Args:
            params: Question parameters
            
        Returns:
            The correct answer
        """
        pass
    
    @abstractmethod
    def format_question_text(self, params: Dict[str, Any]) -> str:
        """Format the question statement.
        
        Args:
            params: Question parameters
            
        Returns:
            Formatted question text
        """
        pass
    
    @abstractmethod
    def generate_solution_text(self, params: Dict[str, Any], answer: Any) -> str:
        """Generate detailed solution explanation.
        
        Args:
            params: Question parameters
            answer: The correct answer
            
        Returns:
            Detailed solution text
        """
        pass
    
    def generate_question(self, question_number: int) -> Tuple[str, str]:
        """Generate a complete question with solution.
        
        Args:
            question_number: The question number
            
        Returns:
            Tuple of (question_latex, solution_latex)
        """
        self.logger.info(f"Generating {self.question_type} question {question_number}")
        
        # Generate parameters and calculate solution
        params = self.generate_parameters()
        answer = self.calculate_solution(params)
        
        # Format question and solution
        question_text = self.format_question_text(params)
        solution_text = self.generate_solution_text(params, answer)
        
        return question_text, solution_text


class MultipleChoiceGenerator(QuestionGenerator):
    """Base class for multiple choice questions."""
    
    @abstractmethod
    def generate_wrong_answers(self, correct_answer: Any, params: Dict[str, Any]) -> List[Any]:
        """Generate plausible wrong answers.
        
        Args:
            correct_answer: The correct answer
            params: Question parameters
            
        Returns:
            List of wrong answers
        """
        pass
    
    @abstractmethod
    def format_answer_choice(self, answer: Any) -> str:
        """Format an answer choice for display.
        
        Args:
            answer: The answer to format
            
        Returns:
            Formatted answer string
        """
        pass
    
    def generate_question(self, question_number: int) -> Tuple[str, str]:
        """Generate a complete multiple choice question.
        
        Args:
            question_number: The question number
            
        Returns:
            Tuple of (question_latex, solution_latex)
        """
        self.logger.info(f"Generating MC {self.question_type} question {question_number}")
        
        # Generate parameters and solutions
        params = self.generate_parameters()
        correct_answer = self.calculate_solution(params)
        wrong_answers = self.generate_wrong_answers(correct_answer, params)
        
        # Format all options
        all_options = [self.format_answer_choice(correct_answer)]
        all_options.extend([self.format_answer_choice(ans) for ans in wrong_answers])
        
        # Shuffle options and track correct position
        correct_index = 0
        combined = list(zip(all_options, [True] + [False] * len(wrong_answers)))
        random.shuffle(combined)
        
        shuffled_options = []
        for i, (option, is_correct) in enumerate(combined):
            shuffled_options.append(option)
            if is_correct:
                correct_index = i
        
        # Format question
        question_text = self.format_question_text(params)
        question_latex = self.formatter.format_multiple_choice_question(
            question_number, question_text, shuffled_options, correct_index
        )
        
        # Generate solution
        solution_text = self.generate_solution_text(params, correct_answer)
        solution_latex = self.formatter.format_solution_section(solution_text)
        
        return question_latex, solution_latex


class TrueFalseGenerator(QuestionGenerator):
    """Base class for true/false questions with multiple statements."""
    
    @abstractmethod
    def generate_statements(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate true/false statements.
        
        Args:
            params: Question parameters
            
        Returns:
            List of statement dictionaries with 'text' and 'is_correct' keys
        """
        pass
    
    def generate_question(self, question_number: int) -> Tuple[str, str]:
        """Generate a complete true/false question.
        
        Args:
            question_number: The question number
            
        Returns:
            Tuple of (question_latex, solution_latex)
        """
        self.logger.info(f"Generating T/F {self.question_type} question {question_number}")
        
        # Generate parameters and statements
        params = self.generate_parameters()
        statements = self.generate_statements(params)
        
        # Format question
        question_text = self.format_question_text(params)
        question_latex = self.formatter.format_true_false_question(
            question_number, question_text, statements
        )
        
        # Generate solution
        solution_text = self.generate_solution_text(params, statements)
        solution_latex = self.formatter.format_solution_section(solution_text)
        
        return question_latex, solution_latex


def generate_latex_document(generator: QuestionGenerator, 
                          num_questions: int,
                          output_filename: str) -> str:
    """Generate a complete LaTeX document with questions.
    
    Args:
        generator: Question generator instance
        num_questions: Number of questions to generate
        output_filename: Output file name
        
    Returns:
        Complete LaTeX document string
    """
    questions = []
    solutions = []
    
    for i in range(1, num_questions + 1):
        question, solution = generator.generate_question(i)
        questions.append(question)
        solutions.append(solution)
    
    # Create complete document
    document = LaTeXFormatter.create_complete_document(questions, solutions)
    
    # Write to file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(document)
    
    logging.info(f"Generated {num_questions} questions in {output_filename}")
    return document
