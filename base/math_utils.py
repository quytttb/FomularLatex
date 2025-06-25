"""
Mathematical formatting utilities for LaTeX output.
"""

from fractions import Fraction
from typing import Union, List


def format_fraction_latex(num: int, denom: int) -> str:
    """Format a fraction for LaTeX display.
    
    Args:
        num: Numerator
        denom: Denominator
        
    Returns:
        LaTeX formatted fraction string
    """
    if denom == 0:
        return "undefined"
    
    frac = Fraction(num, denom)
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"


def format_coefficient(coeff: Union[int, float, Fraction], 
                      is_first: bool = False, 
                      var: str = 'x', 
                      power: int = 1) -> str:
    """Format coefficient with proper signs and variable.
    
    Args:
        coeff: The coefficient value
        is_first: Whether this is the first term
        var: Variable name (default 'x')
        power: Power of the variable
        
    Returns:
        Formatted coefficient string
    """
    if coeff == 0:
        return ""
    
    # Handle Fraction coefficients
    if isinstance(coeff, Fraction):
        num, denom = coeff.numerator, coeff.denominator
    else:
        num, denom = int(coeff), 1
    
    # Format the coefficient part
    if denom == 1:
        coeff_str = str(abs(num)) if abs(num) != 1 or power == 0 else ""
    else:
        coeff_str = f"\\frac{{{abs(num)}}}{{{denom}}}"
    
    # Handle variable and power
    if power == 0:
        var_str = coeff_str if coeff_str else "1"
    elif power == 1:
        var_str = f"{coeff_str}{var}" if coeff_str else var
    else:
        var_str = f"{coeff_str}{var}^{{{power}}}" if coeff_str else f"{var}^{{{power}}}"
    
    # Handle signs
    if is_first:
        if num < 0:
            return f"-{var_str}"
        else:
            return var_str
    else:
        if num < 0:
            return f" - {var_str}"
        else:
            return f" + {var_str}"


def format_polynomial(coeffs: List[Union[int, float, Fraction]], var: str = 'x') -> str:
    """Format polynomial coefficients as LaTeX string.
    
    Args:
        coeffs: List of coefficients from highest to lowest degree
        var: Variable name
        
    Returns:
        LaTeX formatted polynomial string
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"
    
    terms = []
    degree = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        power = degree - i
        term = format_coefficient(coeff, len(terms) == 0, var, power)
        if term:
            terms.append(term)
    
    if not terms:
        return "0"
    
    return "".join(terms)


def format_with_parentheses(value: Union[int, float, str]) -> str:
    """Format value with parentheses if negative.
    
    Args:
        value: Value to format
        
    Returns:
        Value with parentheses if negative
    """
    if isinstance(value, (int, float)):
        return f"({value})" if value < 0 else str(value)
    elif isinstance(value, str):
        if value.startswith('-'):
            return f"({value})"
    return str(value)


def standardize_math_expression(expr: str) -> str:
    """Standardize mathematical expressions for LaTeX.
    
    Args:
        expr: Mathematical expression string
        
    Returns:
        Standardized expression
    """
    import re
    
    # Rule 1: Handle coefficients of 1 and -1
    expr = re.sub(r'\b1([a-zA-Z])', r'\1', expr)  # 1x -> x
    expr = re.sub(r'-1([a-zA-Z])', r'-\1', expr)  # -1x -> -x
    
    # Rule 2: Remove operations with 0
    expr = re.sub(r'\s*\+\s*0\b', '', expr)
    expr = re.sub(r'\s*-\s*0\b', '', expr)
    
    # Rule 3: Format negative numbers in parentheses for multiplication
    expr = re.sub(r'(-\d+)\s*×', r'(\1) ×', expr)
    
    # Rule 4: Fix double signs
    expr = re.sub(r'\+\s*-', '- ', expr)
    expr = re.sub(r'-\s*-', '+ ', expr)
    
    # Rule 5: Remove leading plus signs
    expr = re.sub(r'=\s*\+', '= ', expr)
    
    # Rule 6: Clean LaTeX fractions
    expr = re.sub(r'\\frac\{\+(\d+)', r'\\frac{\1', expr)
    
    # Rule 7: Handle coefficient 1 in fractions
    expr = re.sub(r'\\frac\{1([a-zA-Z])', r'\\frac{\1', expr)
    
    # Rule 8: Simplify power notation
    expr = re.sub(r'\^\{1\}', '', expr)
    
    # Rule 9: Remove multiplication by 1
    expr = re.sub(r'\b1\s*⋅\s*', '', expr)
    
    # Rule 10: Format decimal numbers
    expr = re.sub(r'(\d+)\.00\b', r'\1', expr)  # 4.00 -> 4
    
    # Rule 11: Fix LaTeX power formatting
    expr = re.sub(r'([a-zA-Z])\{(\d+)\}', r'\1^{\2}', expr)
    expr = re.sub(r'(\d+)([a-zA-Z])\{(\d+)\}', r'\1\2^{\3}', expr)
    
    return expr.strip()
