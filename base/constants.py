"""
Configuration constants for math question generation.
"""

class QuestionConfig:
    """Configuration constants for question generation."""
    
    # Random coefficient ranges
    COEFFICIENT_RANGE = (-7, 7)
    SMALL_COEFFICIENT_RANGE = (-3, 3)
    POSITIVE_COEFFICIENT_RANGE = (1, 5)
    
    # Question count defaults
    DEFAULT_QUESTIONS = 4
    MAX_QUESTIONS = 20
    
    # LaTeX formatting
    DECIMAL_PRECISION = 2
    
    # Answer choice configuration
    MULTIPLE_CHOICE_OPTIONS = 4
    WRONG_ANSWER_VARIATIONS = 3
    
    # Common non-zero values for denominators
    NONZERO_VALUES = [-3, -2, -1, 1, 2, 3]
    
    # File extensions
    LATEX_EXTENSION = '.tex'
    PDF_EXTENSION = '.pdf'
