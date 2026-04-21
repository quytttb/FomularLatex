with open("cau_3.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(r"\tikzset{every picture/.style={line width=0.75pt}}       \n\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1]", 
              r"\begin{tikzpicture}[x=0.75pt,y=0.75pt,yscale=-1,xscale=1,line width=0.75pt]")

# Fallback just in case spacing is different
c = c.replace(r"\tikzset{every picture/.style={line width=0.75pt}}", "")

with open("cau_3.py", "w", encoding="utf-8") as f:
    f.write(c)
