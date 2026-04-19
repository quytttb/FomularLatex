# SAMPLE LATEX FILE

Thư mục này chứa các file mẫu phục vụ việc sinh đề thi LaTeX theo format Azota.

## Files

| File | Mô tả |
|------|-------|
| `ex_test.sty` | Package LaTeX cho đề thi Việt Nam (v3.1, Trần Anh Tuấn). Cần cài vào texmf để dùng toàn cục. |
| `De_mau_azota_latex_v1.tex` | File đề thi mẫu Azota — tham khảo format câu hỏi trắc nghiệm và Đúng/Sai. |
| `Huong-dan-ex-test-v3.1.pdf` | Hướng dẫn sử dụng package `ex_test` v3.1. |

## Cài đặt `ex_test.sty`

Nguồn gốc: [OneDrive của tác giả](https://huseduvn-my.sharepoint.com/personal/tuanta_hus_edu_vn/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Ftuanta%5Fhus%5Fedu%5Fvn%2FDocuments%2FLaTeX%2Fex%5Ftest%20up%20web&ga=1)

### Cài vào hệ thống (one-time)

```bash
mkdir -p ~/texmf/tex/latex/ex_test
cp "SAMPLE LATEX FILE/ex_test.sty" ~/texmf/tex/latex/ex_test/ex_test.sty
mktexlsr ~/texmf
```

### Packages phụ thuộc cần cài trước

```bash
sudo apt-get install -y texlive-lang-other texlive-science texlive-latex-extra
```

## Format Azota — Câu hỏi Đúng/Sai

```latex
\usepackage[solcolor]{ex_test}

\begin{ex}
Đề bài câu hỏi...
\choiceTFt
{Phát biểu a -- Sai (không có dấu *)}
{* Phát biểu b -- Đúng (có dấu *)}
{Phát biểu c -- Sai}
{* Phát biểu d -- Đúng}
\loigiai{
  Giải thích...
}
\end{ex}
```

> **Lưu ý:** Azota đọc dấu `*` trước mệnh đề để đánh dấu **Đúng**. Mệnh đề không có `*` là **Sai**.
