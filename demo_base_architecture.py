#!/usr/bin/env python3
"""
Demo script showing how to use the new base architecture.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base import generate_latex_document
from generators.asymptote_generator import AsymptoteGenerator


def main():
    """Generate sample questions using the new base architecture."""
    
    # Create generator instance
    generator = AsymptoteGenerator()
    
    # Get number of questions from command line or use default
    num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    
    # Generate LaTeX document
    output_file = "demo_asymptote_questions.tex"
    document = generate_latex_document(generator, num_questions, output_file)
    
    print(f"✅ Generated {num_questions} asymptote questions in {output_file}")
    print("📝 To compile to PDF, run: xelatex demo_asymptote_questions.tex")
    
    # Show first question as preview
    lines = document.split('\n')
    start_idx = next(i for i, line in enumerate(lines) if 'Câu 1:' in line)
    end_idx = start_idx + 10
    
    print("\n📖 Preview of first question:")
    print("=" * 50)
    for line in lines[start_idx:end_idx]:
        print(line)
    print("=" * 50)


if __name__ == "__main__":
    main()
