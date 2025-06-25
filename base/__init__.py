"""
Base classes and utilities for math question generation.
"""

from .question_generator import QuestionGenerator, MultipleChoiceGenerator, TrueFalseGenerator, generate_latex_document
from .math_utils import (
    format_fraction_latex,
    format_coefficient, 
    format_polynomial,
    format_with_parentheses,
    standardize_math_expression
)
from .latex_formatter import LaTeXFormatter
from .constants import QuestionConfig

__all__ = [
    'QuestionGenerator',
    'MultipleChoiceGenerator', 
    'TrueFalseGenerator',
    'generate_latex_document',
    'format_fraction_latex',
    'format_coefficient',
    'format_polynomial', 
    'format_with_parentheses',
    'standardize_math_expression',
    'LaTeXFormatter',
    'QuestionConfig'
]
