filepath = "/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py"
with open(filepath, 'r') as f:
    text = f.read()

text = text.replace('joined = " \\\\ ".join(rows)', 'joined = " \\\\\\\\ ".join(rows)')
text = text.replace('MN đạt GTLN là M khi \\(M(p, q, r)\\) và \\(N(k, l, e)\\).\\nKhi đó', 'MN đạt GTLN là M khi \\(M(p, q, r)\\) và \\(N(k, l, e)\\). Khi đó')

with open(filepath, 'w') as f:
    f.write(text)
