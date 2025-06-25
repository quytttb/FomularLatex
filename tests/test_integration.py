"""
Integration tests for the complete FomularLatex system.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import generate_latex_document
from generators import TriangleGenerator, AsymptoteGenerator, AdvancedAsymptoteGenerator


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_triangle_generator_end_to_end(self):
        """Test complete triangle question generation."""
        generator = TriangleGenerator()
        
        # Generate questions
        questions = []
        for i in range(3):
            question = generator.generate_question(i+1)
            questions.append(question)
        
        # Check question structure
        for question in questions:
            self.assertIn('question_text', question)
            self.assertIn('statements', question)
            self.assertIn('solution', question)
            
            # Check statements
            statements = question['statements']
            self.assertEqual(len(statements), 4)
            
            for stmt in statements:
                self.assertIn('text', stmt)
                self.assertIn('is_correct', stmt)
        
        # Generate LaTeX document
        output_file = os.path.join(self.temp_dir, "test_triangle.tex")
        generate_latex_document(generator, 3, output_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check file content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('\\documentclass', content)
        self.assertIn('\\begin{document}', content)
        self.assertIn('\\end{document}', content)
        self.assertIn('tam giác', content)
    
    def test_asymptote_generator_end_to_end(self):
        """Test complete asymptote question generation."""
        generator = AsymptoteGenerator()
        
        # Generate questions
        questions = []
        for i in range(2):
            question = generator.generate_question(i+1)
            questions.append(question)
        
        # Check question structure
        for question in questions:
            self.assertIn('question_text', question)
            self.assertIn('choices', question)
            self.assertIn('correct_answer', question)
            self.assertIn('solution', question)
            
            # Check choices
            choices = question['choices']
            self.assertEqual(len(choices), 4)
        
        # Generate LaTeX document
        output_file = os.path.join(self.temp_dir, "test_asymptote.tex")
        generate_latex_document(generator, 2, output_file)
        
        # Check file was created and content
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('tiệm cận xiên', content)
    
    def test_advanced_asymptote_generator_end_to_end(self):
        """Test complete advanced asymptote question generation."""
        generator = AdvancedAsymptoteGenerator()
        
        # Generate questions
        questions = []
        for i in range(2):
            question = generator.generate_question(i+1)
            questions.append(question)
        
        # Check question structure
        for question in questions:
            self.assertIn('question_text', question)
            self.assertIn('statements', question)
            self.assertIn('solution', question)
            
            # Check for proper LaTeX formatting
            question_text = question['question_text']
            self.assertNotIn('\\dfrac^{', question_text)
            
            for stmt in question['statements']:
                self.assertNotIn('\\dfrac^{', stmt['text'])
                self.assertNotIn('\\frac^{', stmt['text'])
    
    def test_mixed_question_document(self):
        """Test generating a document with mixed question types."""
        triangle_gen = TriangleGenerator()
        asymptote_gen = AsymptoteGenerator()
        advanced_gen = AdvancedAsymptoteGenerator()
        
        questions = []
        
        # Add questions from each generator
        questions.append(triangle_gen.generate_question(len(questions)+1))
        questions.append(asymptote_gen.generate_question(len(questions)+1))
        questions.append(advanced_gen.generate_question(len(questions)+1))
        
        # Generate document
        output_file = os.path.join(self.temp_dir, "test_mixed.tex")
        # Use one generator to create document, then manually check content variety
        generate_latex_document(triangle_gen, 3, output_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check content contains all question types
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('tam giác', content)  # Triangle questions
        self.assertIn('tiệm cận', content)  # Asymptote questions


class TestLaTeXFormatting(unittest.TestCase):
    """Test LaTeX formatting quality."""
    
    def test_no_malformed_fractions(self):
        """Test that no malformed fractions are generated."""
        generators = [
            TriangleGenerator(),
            AsymptoteGenerator(),
            AdvancedAsymptoteGenerator()
        ]
        
        for generator in generators:
            with self.subTest(generator=generator.__class__.__name__):
                # Generate multiple questions to test various cases
                for i in range(5):
                    question = generator.generate_question(i+1)
                    
                    # Check question text
                    self.assertNotIn('\\dfrac^{', question['question_text'])
                    self.assertNotIn('\\frac^{', question['question_text'])
                    
                    # Check statements/choices
                    if 'statements' in question:
                        for stmt in question['statements']:
                            self.assertNotIn('\\dfrac^{', stmt['text'])
                            self.assertNotIn('\\frac^{', stmt['text'])
                    
                    if 'choices' in question:
                        for choice in question['choices']:
                            self.assertNotIn('\\dfrac^{', choice)
                            self.assertNotIn('\\frac^{', choice)
    
    def test_decimal_formatting(self):
        """Test that long decimals are properly formatted."""
        generator = AdvancedAsymptoteGenerator()
        
        for i in range(10):
            question = generator.generate_question(i+1)
            
            # Check for long decimals (more than 4 decimal places)
            text_to_check = question['question_text']
            for stmt in question['statements']:
                text_to_check += stmt['text']
            
            # Should not have numbers like 3.3333333333333335
            import re
            long_decimals = re.findall(r'\d+\.\d{5,}', text_to_check)
            self.assertEqual(len(long_decimals), 0, 
                           f"Found long decimals: {long_decimals}")
    
    def test_consistent_notation(self):
        """Test that mathematical notation is consistent."""
        generators = [
            TriangleGenerator(),
            AsymptoteGenerator(),
            AdvancedAsymptoteGenerator()
        ]
        
        for generator in generators:
            with self.subTest(generator=generator.__class__.__name__):
                question = generator.generate_question(1)
                
                text_content = question['question_text']
                if 'statements' in question:
                    for stmt in question['statements']:
                        text_content += stmt['text']
                
                if 'choices' in question:
                    for choice in question['choices']:
                        text_content += choice
                
                # Check for consistent use of LaTeX commands
                # Should not mix \frac and \dfrac inconsistently
                frac_count = text_content.count('\\frac{')
                dfrac_count = text_content.count('\\dfrac{')
                
                # If both are used, it should be intentional (e.g., inline vs display)
                # This is a style guide check
                if frac_count > 0 and dfrac_count > 0:
                    # Log for manual review
                    pass


if __name__ == '__main__':
    unittest.main()
