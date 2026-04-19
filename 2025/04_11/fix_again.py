with open("/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py", "r") as f:
    text = f.read()

text = text.replace(r"\(\(M", r"\(M")
text = text.replace(r"\)\)", r"\)")
text = text.replace(r"\(\(N", r"\(N")

with open("/home/haiquy/PycharmProjects/FomularLatex/2025/04_11/duongthang_matphang_matcau_3.py", "w") as f:
    f.write(text)
