"""
Test suite for FomularLatex base architecture.
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import (
    QuestionGenerator, MultipleChoiceGenerator, TrueFalseGenerator,
    format_fraction_latex, format_polynomial, standardize_math_expression
)
from generators import TriangleGenerator, AsymptoteGenerator, AdvancedAsymptoteGenerator


class TestBaseMathUtils(unittest.TestCase):
    """Test math utilities in base package."""
    
    def test_format_fraction_latex(self):
        """Test LaTeX fraction formatting."""
        # Test simple fractions
        self.assertEqual(format_fraction_latex(1, 2), "\\frac{1}{2}")
        self.assertEqual(format_fraction_latex(3, 4), "\\frac{3}{4}")
        self.assertEqual(format_fraction_latex(-2, 3), "\\frac{-2}{3}")
        
        # Test integers (denominator = 1)
        self.assertEqual(format_fraction_latex(5, 1), "5")
        self.assertEqual(format_fraction_latex(-3, 1), "-3")
        
        # Test zero
        self.assertEqual(format_fraction_latex(0, 5), "0")
        
        # Test simplification
        self.assertEqual(format_fraction_latex(4, 8), "\\frac{1}{2}")
        self.assertEqual(format_fraction_latex(6, 9), "\\frac{2}{3}")
        
        # Test undefined (division by zero)
        self.assertEqual(format_fraction_latex(1, 0), "undefined")
    
    def test_format_polynomial(self):
        """Test polynomial formatting."""
        # Test linear polynomials
        self.assertEqual(format_polynomial([2, 3]), "2x + 3")
        self.assertEqual(format_polynomial([1, -2]), "x - 2")
        self.assertEqual(format_polynomial([-1, 5]), "-x + 5")
        
        # Test quadratic polynomials
        self.assertEqual(format_polynomial([1, 2, 3]), "x^{2} + 2x + 3")
        self.assertEqual(format_polynomial([2, -1, 0]), "2x^{2} - x")
        
        # Test constant polynomial
        self.assertEqual(format_polynomial([5]), "5")
        self.assertEqual(format_polynomial([0]), "0")
        
        # Test leading coefficient 1
        self.assertEqual(format_polynomial([1, 0, 3]), "x^{2} + 3")
    
    def test_standardize_math_expression(self):
        """Test math expression standardization."""
        # Test coefficient of 1 removal
        self.assertEqual(standardize_math_expression("1x + 2"), "x + 2")
        self.assertEqual(standardize_math_expression("-1x + 3"), "-x + 3")
        
        # Test zero term removal
        self.assertEqual(standardize_math_expression("x + 0"), "x")
        self.assertEqual(standardize_math_expression("x - 0"), "x")
        
        # Test power simplification
        self.assertEqual(standardize_math_expression("x^{1}"), "x")
        
        # Test that LaTeX fractions are not affected
        self.assertEqual(standardize_math_expression("\\frac{1}{2}"), "\\frac{1}{2}")
        self.assertEqual(standardize_math_expression("\\dfrac{1}{3}"), "\\dfrac{1}{3}")
        
        # Test decimal formatting
        self.assertEqual(standardize_math_expression("4.00"), "4")


class TestBaseQuestionGenerators(unittest.TestCase):
    """Test base question generator classes."""
    
    def test_question_generator_abstract(self):
        """Test that base QuestionGenerator is abstract."""
        with self.assertRaises(TypeError):
            QuestionGenerator()
    
    def test_multiple_choice_generator_methods(self):
        """Test MultipleChoiceGenerator has required methods."""
        class TestMCGenerator(MultipleChoiceGenerator):
            def __init__(self):
                super().__init__("Test MC")
            
            def generate_parameters(self):
                return {"test": "value"}
            
            def generate_choices(self, params):
                return ["A", "B", "C", "D"]
            
            def calculate_solution(self, params):
                return 0
            
            def format_question_text(self, params):
                return "Test question"
            
            def format_answer_choice(self, choice, index):
                return f"{chr(ord('A') + index)}) {choice}"
            
            def generate_solution_text(self, params, correct_answer):
                return "Test solution"
            
            def generate_wrong_answers(self, params, correct_answer):
                return ["Wrong 1", "Wrong 2", "Wrong 3"]
        
        generator = TestMCGenerator()
        self.assertEqual(generator.question_type, "Test MC")
        self.assertIsInstance(generator.generate_parameters(), dict)
        self.assertIsInstance(generator.generate_choices({}), list)
        self.assertIsInstance(generator.calculate_solution({}), int)
        self.assertIsInstance(generator.format_question_text({}), str)
    
    def test_true_false_generator_methods(self):
        """Test TrueFalseGenerator has required methods."""
        class TestTFGenerator(TrueFalseGenerator):
            def __init__(self):
                super().__init__("Test TF")
            
            def generate_parameters(self):
                return {"test": "value"}
            
            def generate_statements(self, params):
                return [
                    {"text": "Statement 1", "is_correct": True},
                    {"text": "Statement 2", "is_correct": False}
                ]
            
            def calculate_solution(self, params):
                return self.generate_statements(params)
            
            def format_question_text(self, params):
                return "Test question"
            
            def generate_solution_text(self, params, statements):
                return "Test solution"
        
        generator = TestTFGenerator()
        self.assertEqual(generator.question_type, "Test TF")
        statements = generator.generate_statements({})
        self.assertIsInstance(statements, list)
        self.assertTrue(all("text" in stmt and "is_correct" in stmt for stmt in statements))


class TestTriangleGenerator(unittest.TestCase):
    """Test TriangleGenerator functionality."""
    
    def setUp(self):
        self.generator = TriangleGenerator()
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.question_type, "Triangle True/False Questions")
        self.assertIsNotNone(self.generator.logger)
    
    def test_generate_parameters(self):
        """Test parameter generation."""
        params = self.generator.generate_parameters()
        
        # Check required keys
        self.assertIn('vertices', params)
        self.assertIn('labels', params)
        self.assertIn('coordinates', params)
        
        # Check data types
        self.assertIsInstance(params['vertices'], dict)
        self.assertIsInstance(params['labels'], list)
        self.assertIsInstance(params['coordinates'], dict)
        
        # Check that we have 3 vertices
        self.assertEqual(len(params['vertices']), 3)
        self.assertEqual(len(params['labels']), 3)
        self.assertEqual(len(params['coordinates']), 3)
    
    def test_triangle_coordinates_valid(self):
        """Test that generated triangle coordinates form a valid triangle."""
        for _ in range(10):  # Test multiple generations
            A, B, C = self.generator._generate_triangle_coordinates()
            
            # Check that points are tuples of 3 coordinates
            self.assertEqual(len(A), 3)
            self.assertEqual(len(B), 3)
            self.assertEqual(len(C), 3)
            
            # Check that all coordinates are numbers
            for point in [A, B, C]:
                for coord in point:
                    self.assertIsInstance(coord, (int, float))
            
            # Check that triangle has non-zero area
            area = self.generator._calculate_triangle_area(A, B, C)
            self.assertGreater(area, 0.01)
    
    def test_generate_statements(self):
        """Test statement generation."""
        params = self.generator.generate_parameters()
        statements = self.generator.generate_statements(params)
        
        # Check we have 4 statements
        self.assertEqual(len(statements), 4)
        
        # Check statement structure
        for stmt in statements:
            self.assertIn('text', stmt)
            self.assertIn('is_correct', stmt)
            self.assertIsInstance(stmt['text'], str)
            self.assertIsInstance(stmt['is_correct'], bool)
            
            # Check LaTeX formatting in text
            self.assertNotIn('\\dfrac^{', stmt['text'])  # No malformed fractions
            self.assertNotIn('\\frac^{', stmt['text'])   # No malformed fractions
    
    def test_format_question_text(self):
        """Test question text formatting."""
        params = self.generator.generate_parameters()
        question_text = self.generator.format_question_text(params)
        
        self.assertIsInstance(question_text, str)
        self.assertIn("tam giác", question_text.lower())
        self.assertIn("mệnh đề", question_text.lower())


class TestAsymptoteGenerator(unittest.TestCase):
    """Test AsymptoteGenerator functionality."""
    
    def setUp(self):
        self.generator = AsymptoteGenerator()
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.question_type, "Asymptote Questions")
    
    def test_generate_parameters(self):
        """Test parameter generation."""
        params = self.generator.generate_parameters()
        
        # Check required keys
        self.assertIn('A', params)
        self.assertIn('B', params)
        self.assertIn('D', params)
        self.assertIn('E', params)
        
        # Check that coefficients are integers
        for key in ['A', 'B', 'D', 'E']:
            self.assertIsInstance(params[key], int)
    
    def test_format_question_text(self):
        """Test question text formatting."""
        params = self.generator.generate_parameters()
        question_text = self.generator.format_question_text(params)
        
        self.assertIsInstance(question_text, str)
        self.assertIn("tiệm cận xiên", question_text)
        self.assertIn("\\dfrac", question_text)


class TestAdvancedAsymptoteGenerator(unittest.TestCase):
    """Test AdvancedAsymptoteGenerator functionality."""
    
    def setUp(self):
        self.generator = AdvancedAsymptoteGenerator()
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.question_type, "Advanced Asymptote Questions")
    
    def test_generate_statements(self):
        """Test statement generation."""
        params = self.generator.generate_parameters()
        statements = self.generator.generate_statements(params)
        
        # Check we have 4 statements
        self.assertEqual(len(statements), 4)
        
        # Check statement structure and LaTeX formatting
        for stmt in statements:
            self.assertIn('text', stmt)
            self.assertIn('is_correct', stmt)
            self.assertIsInstance(stmt['text'], str)
            self.assertIsInstance(stmt['is_correct'], bool)
            
            # Check for proper LaTeX formatting
            self.assertNotIn('\\dfrac^{', stmt['text'])
            self.assertNotIn('\\frac^{', stmt['text'])
            self.assertNotRegex(stmt['text'], r'\d+\.\d{5,}')  # No long decimals


if __name__ == '__main__':
    unittest.main()
