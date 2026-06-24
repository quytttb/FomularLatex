---
name: generate-math-script
description: >
  **WORKFLOW SKILL** — Generates a Python script capable of procedurally producing dynamic Math problems (True/False format and Short Answer format) based on a sample input problem (đề bài mẫu).
  Use when: the user provides a sample math problem (đề bài mẫu) and asks to write a Python random generator script for it, or when asked to create a new script file in the project's framework format.
---

# Generate Math Script Workflow

This skill guides the agent to properly convert a sample math problem into a functional, standalone Python script that can procedurally generate variants of that problem with randomized parameters, calculations (`sympy` or standard math), and LaTeX TikZ diagrams.

## Prerequisites
- The user provides a **sample problem** (`đề bài mẫu`) which typically includes context, given values, asked targets. It can be a True/False format (4 statements) or a Short Answer format (1 final value).
- The project scripts are independent from each other. Do NOT use OOP, classes, or heavy generic boilerplates. Instead, rely on procedural standard Python functions (`def generate_question():` and `def main():`).

## Workflow Steps

### 1. Extract and Analyze Problem Logic
- Identify the core geometric or algebraic shapes.
- Identify the fixed and variable parameters (e.g. dimensions, speeds, functions).
- Deduce the mathematical operations required to verify the 4 statements.
- Outline how the sample coordinates or values map to a Cartesian coordinate system, if applicable.

### 2. Scaffold the Boilerplate
- Prepare imports: `logging`, `math`, `os`, `random`, `sys`, `ABC`, `abstractmethod`, `dataclass`, `Fraction`, `Template`, `Tuple`, `Dict`, `Any`, and `sympy as sp`.
- Setup a `GeneratorConfig` dataclass for seeding.
- Add utility functions for Vietnamese decimal and fraction formatting (e.g., `format_fraction_vn`, replacing dots with commas).

### 3. Setup Parameter Arrays & Processing
- Define arrays of randomized values (e.g., `WIDTH_VALUES`, `HEIGHT_VALUES`, or `PARAM_SETS`). **CRITICAL: Generate a large and diverse set of parameters (at least 50 or more "nice/beautiful" clean numbers) for each variable** to ensure high variance between generated tests.
- Alternatively, use `random.randint` or `random.choice` on large ranges and write checking loops to filter out bad values (e.g. ignoring floats when integers are needed).
- Write small, isolated functional blocks using `sympy` components so there are no floating-point errors (e.g., intersection derivations, polynomial integrations, vector products) if the math is complex.

### 4. Create LaTeX and TikZ Templates
- Define exact TikZ drawings in `TIKZ_DIAGRAM` and `TIKZ_SOLUTION`. Keep it parameterized by ensuring variables map correctly inside the raw string or utilizing python string templates.
- Define `TEMPLATE_QUESTION` describing the context and formatting statements (a, b, c, d).
- Define `TEMPLATE_SOLUTION` outlining the step-by-step mathematical reasoning.
- **LaTeX Formatting Rules**:
  - Always use `\overrightarrow` instead of `\vv` for vectors to ensure broad platform compatibility (e.g., Azota).
  - When writing vectors with fraction coordinates, always wrap them in `\left(` and `\right)` (e.g., `\left( \dfrac{1}{2}; 3 \right)`).
  - Do NOT use `\textbf` for texts like "Lời giải", "Đúng", or "Sai" in the generated LaTeX strings. Keep the text normal.
  - Do NOT generate a standalone "Đáp án" line at the end of the `Lời giải` block for True/False (Đúng/Sai) format. However, STILL print the "Đáp án" line at the end of the solution for Short Answer / Essay (Trả lời ngắn / Tự luận) format.

### 5. Define the Generator Function
- **Do NOT use OOP (classes, ABC, or inheritance).** Scripts run independently and do not need heavy architectural boilerplate.
- Define a functional entry point `def generate_question(seed=None):` or similar.
- In `generate_question`, select random parameters, calculate the correct math logic.
- For True/False (Đúng/Sai) format: Randomly toggle correct statements into false ones, construct the 4 statements (a, b, c, d), and return `(question, solution, markers)`.
- For Short Answer (Trả lời ngắn) or Essay (Tự luận) format: Calculate the final floating-point or integer value. If the answer is an integer, just format it as a simple string (e.g. `key = str(int(val))`). If the answer is a decimal, format the final key to show both dot and comma notations separated by a pipe (e.g., `ans_dot = str(val); ans_comma = ans_dot.replace('.', ','); key = f"{ans_dot} | {ans_comma}"`). Return `(question, solution, key)`.

### 6. Implement CLI / Main Execution
- Define `def main():` parsing `sys.argv` for `num_questions`.
- Call `generate_question()` in a loop.
- Generate a standalone `.tex` document compiling all generated problems so the user can visually test them immediately.

### 7. Review and Refine
- Ensure ALL `sympy` calculations convert properly to LaTeX strings strings.
- Verify escaping convention for string templates (`$$` vs `\$$` where appropriate).
- Verify the script contains no syntax errors.

## Post-Execution Check
- Ask the user to run the generated script (`python <script_name.py>`) to test output validity.
- Ask if the bounding boxes or TIKZ scaling needs tuning.
