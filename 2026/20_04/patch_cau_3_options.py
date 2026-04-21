with open("cau_3.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(r"\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]", 
              r"\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1,line width=0.75pt]")

# Clean up empty strings and fix spaces if necessary
c = c.replace(r"\begin{center}" + "\n       \n" + r"\begin{tikzpicture}", 
              r"\begin{center}" + "\n" + r"\begin{tikzpicture}")

with open("cau_3.py", "w", encoding="utf-8") as f:
    f.write(c)
