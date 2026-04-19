filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
with open(filepath, 'r') as f:
    text = f.read()

text = text.replace(r")\).\n" + '            f"Khi đó', r")\). " + '            f"Khi đó')

with open(filepath, 'w') as f:
    f.write(text)
