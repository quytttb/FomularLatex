with open("cau_3.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(r"""sol_d = f"d) {'Đúng' if d_correct else 'Sai'}.\n{sol_d_text}" """, "")
c = c.replace(r"sol_d = f\"d) {{'Đúng' if d_correct else 'Sai'}}.\n{{sol_d_text}}\"", "sol_d = f\"d) {'Đúng' if d_correct else 'Sai'}.\\n{sol_d_text}\"")

with open("cau_3.py", "w", encoding="utf-8") as f:
    f.write(c)

