with open("/home/haiquy/PycharmProjects/FomularLatex/27_03/parabolic_tunnel_volume_questions.py", "r", encoding="utf-8") as f:
    content = f.read()

tikz_code = r'''
\begin{center}
\begin{tikzpicture}[scale=0.8, font=\footnotesize, line join=round, line cap=round, >=stealth]
   % Draw the tunnel base (trapezoid)
   \coordinate (A) at (0,0);
   \coordinate (C) at (4,0);
   \coordinate (D) at (5,2);
   \coordinate (F) at (-1,2);
   \draw[thick] (C) -- (D) -- (F);
   \draw[dashed] (A) -- (C) (A) -- (F);
   
   % Tunnel curve
   \coordinate (S) at (2,5);
   \draw[thick] (C) .. controls (3.5,4) and (2.5,5) .. (S);
   \draw[dashed] (A) .. controls (0.5,4) and (1.5,5) .. (S);
   
   % Section curve P
   \coordinate (B) at (1.5,0); % point B on AC
   \coordinate (E) at (1.1,1.5); % point E matching B
   \coordinate (G) at (2,3.5); % point G on curve
   \draw[dashed] (B) -- (E);
   \draw[thick] (B) -- (G);
   \draw[dashed, blue, thick] (E) .. controls (1.5,2.5) and (1.8,3.2) .. (G);
   
   % Labels
   \node[below right] at (A) {$A$};
   \node[below] at (C) {$C$};
   \node[right] at (D) {$D$};
   \node[left] at (F) {$F$};
   \node[below] at (B) {$B$};
   \node[left] at (E) {$E$};
   \node[right] at (G) {$G$};
   \node[above] at (S) {$S$};
   
   % Fill section region
   \fill[yellow, opacity=0.3] (B) -- (E) .. controls (1.5,2.5) and (1.8,3.2) .. (G) -- cycle;
   
   \coordinate (H) at (2,0);
   \draw[dashed] (S) -- (H);
   \node[below] at (H) {$H$};
   \draw (H) ++(0,0.2) -- ++(-0.2,0) -- ++(0,-0.2);
   \draw (B) ++(0,0.2) -- ++(-0.2,0) -- ++(0,-0.2);
   \draw (A) ++(0,0.2) -- ++(0.2,0) -- ++(0,-0.2);
\end{tikzpicture}
\end{center}'''

tikz_solution = r'''
\begin{center}
\begin{tikzpicture}[scale=0.8, font=\footnotesize, line join=round, line cap=round, >=stealth]
    % Model Parabola
    \draw[->] (-3,0) -- (3,0) node[below] {$x$};
    \draw[->] (0,-1) -- (0,4) node[left] {$y$};
    \node[below right] at (0,0) {$O$};
    
    \draw[thick, blue, smooth, samples=100, domain=-1.414:1.414] plot (\x, {-2*\x*\x + 2});
    
    \node[above right] at (0,2) {$S(0;2)$};
    \fill (0,2) circle (1.5pt);
    
    \coordinate (H) at (0,0);
    \node[below left] at (-1,0) {$E$};
    \fill (-1,0) circle (1.5pt);
    
    \coordinate (B) at (0.5,0);
    \coordinate (G) at (0.5,1.5);
    \draw[dashed] (B) -- (G);
    \node[below] at (B) {$B$};
    \node[right] at (G) {$G$};
    \fill (G) circle (1.5pt);
    
    % Fill integrated region
    \fill[yellow, opacity=0.3] (-1,0) -- plot[domain=-1:0.5, smooth] (\x, {-2*\x*\x + 2}) -- (0.5,0) -- cycle;
\end{tikzpicture}
\end{center}'''

target1 = "Biết $AC = {L}$ mét, $AF = {a}$ m, $CD = {b}$ m. Tìm thể tích đường hầm trên và làm tròn đến hàng đơn vị của m$^3$.'''"
content = content.replace(target1, target1 + "\n\n    stem += r'''" + tikz_code + "'''\n")

target2 = "$$\\Leftrightarrow BE = {a} - {m_dec}x$$"
content = content.replace(target2, target2 + "\n\n    solution += r'''" + tikz_solution + "'''\n")

with open("/home/haiquy/PycharmProjects/FomularLatex/27_03/parabolic_tunnel_volume_questions.py", "w", encoding="utf-8") as f:
    f.write(content)
