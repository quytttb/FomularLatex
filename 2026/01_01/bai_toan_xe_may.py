import random
import sys
import os
from string import Template
from fractions import Fraction

# ==================== CONFIGURATION & HELPERS ====================

def to_latex_num(value):
    """Format number to LaTeX string, using fractions if appropriate"""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        if value.numerator < 0:
            return f"-\\frac{{{abs(value.numerator)}}}{{{value.denominator}}}"
        return f"\\frac{{{value.numerator}}}{{{value.denominator}}}"
    
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
        f = Fraction(value).limit_denominator(100)
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            if f.numerator < 0:
                return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
    return str(value)


def to_latex_num_display(value):
    """Format number to LaTeX string for display math, using dfrac"""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        if value.numerator < 0:
            return f"-\\dfrac{{{abs(value.numerator)}}}{{{value.denominator}}}"
        return f"\\dfrac{{{value.numerator}}}{{{value.denominator}}}"
    
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        if abs(value - round(value)) < 1e-9:
            return str(round(value))
        f = Fraction(value).limit_denominator(100)
        if abs(float(f) - value) < 1e-9:
            if f.denominator == 1:
                return str(f.numerator)
            if f.numerator < 0:
                return f"-\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"
            return f"\\dfrac{{{f.numerator}}}{{{f.denominator}}}"
    return str(value)


def create_latex_document(content):
    return r"""\documentclass[a4paper,12pt]{article}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{polyglossia}
\setmainlanguage{vietnamese}
\setmainfont{Times New Roman}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{tkz-tab}
\begin{document}
""" + content + r"\end{document}"


# ==================== TEMPLATES ====================

# Scenario 1: Xe máy và công trường (Original)
SCENARIO_1 = {
    'vehicle': 'xe máy',
    'location': 'công trường đang thi công',
    'sign_type': 'biển báo giới hạn tốc độ tối đa cho phép',
    'exit_location': 'công trường',
    'template_q': Template(
        r"""
Câu ${idx}: Một người điều khiển xe máy với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có công trường đang thi công có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe máy bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe máy vừa đến vị trí đặt biển báo thì tốc độ của xe máy bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực công trường. Khi vừa ra khỏi công trường, xe máy tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe máy vừa ra khỏi công trường. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe máy đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe máy đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe máy đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe máy đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 2: Ô tô và khu vực trường học
SCENARIO_2 = {
    'vehicle': 'ô tô',
    'location': 'khu vực trường học',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực trường học',
    'template_q': Template(
        r"""
Câu ${idx}: Một người lái ô tô với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực trường học có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, ô tô bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi ô tô vừa đến vị trí đặt biển báo thì tốc độ của ô tô bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực trường học. Khi vừa ra khỏi khu vực trường học, ô tô tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi ô tô vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, ô tô đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường ô tô đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Ô tô đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường ô tô đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 3: Xe tải và khu dân cư
SCENARIO_3 = {
    'vehicle': 'xe tải',
    'location': 'khu dân cư',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu dân cư',
    'template_q': Template(
        r"""
Câu ${idx}: Một tài xế điều khiển xe tải với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu dân cư đông đúc có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe tải bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe tải vừa đến vị trí đặt biển báo thì tốc độ của xe tải bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu dân cư. Khi vừa ra khỏi khu dân cư, xe tải tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe tải vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe tải đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe tải đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe tải đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe tải đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 4: Xe buýt và trạm dừng
SCENARIO_4 = {
    'vehicle': 'xe buýt',
    'location': 'khu vực bệnh viện',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực bệnh viện',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe buýt đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực bệnh viện có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe buýt bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe buýt vừa đến vị trí đặt biển báo thì tốc độ của xe buýt bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực bệnh viện. Khi vừa ra khỏi khu vực, xe buýt tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe buýt vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe buýt đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe buýt đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe buýt đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe buýt đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 5: Taxi và khu du lịch
SCENARIO_5 = {
    'vehicle': 'taxi',
    'location': 'khu du lịch',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu du lịch',
    'template_q': Template(
        r"""
Câu ${idx}: Một chiếc taxi đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu du lịch có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, taxi bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi taxi vừa đến vị trí đặt biển báo thì tốc độ của taxi bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu du lịch. Khi vừa ra khỏi khu vực, taxi tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi taxi vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, taxi đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường taxi đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Taxi đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường taxi đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 6: Xe đạp điện và đường nội bộ
SCENARIO_6 = {
    'vehicle': 'xe đạp điện',
    'location': 'đường nội bộ khu chung cư',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'đường nội bộ',
    'template_q': Template(
        r"""
Câu ${idx}: Một người điều khiển xe đạp điện với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có đường nội bộ khu chung cư có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe đạp điện bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe đạp điện vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi đường nội bộ. Khi vừa ra khỏi đường nội bộ, xe đạp điện tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe đạp điện đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe đạp điện đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe đạp điện đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe đạp điện đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 7: Xe cứu thương và khu vực đông người
SCENARIO_7 = {
    'vehicle': 'xe cứu thương',
    'location': 'khu vực chợ đông người',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực chợ',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe cứu thương đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực chợ đông người có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe cứu thương bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe cứu thương vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực chợ. Khi vừa ra khỏi khu vực, xe cứu thương tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa ra khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe cứu thương đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe cứu thương đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe cứu thương đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe cứu thương đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 8: Xe tải chở hàng và cầu yếu
SCENARIO_8 = {
    'vehicle': 'xe tải chở hàng',
    'location': 'cầu yếu',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'cầu',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe tải chở hàng đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có cầu yếu có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe tải bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe tải vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi qua khỏi cầu. Khi vừa qua khỏi cầu, xe tải tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa qua khỏi cầu. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe tải đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe tải đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe tải đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe tải đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 9: Xe khách và đường đèo
SCENARIO_9 = {
    'vehicle': 'xe khách',
    'location': 'đường đèo nguy hiểm',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'đường đèo',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe khách đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có đường đèo nguy hiểm có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe khách bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe khách vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi qua khỏi đường đèo. Khi vừa qua khỏi đường đèo, xe khách tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa qua khỏi đường đèo. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe khách đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe khách đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe khách đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe khách đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 10: Xe container và khu công nghiệp
SCENARIO_10 = {
    'vehicle': 'xe container',
    'location': 'khu công nghiệp',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu công nghiệp',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe container đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu công nghiệp có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe container bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe container vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu công nghiệp. Khi vừa rời khỏi khu vực, xe container tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe container đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe container đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe container đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe container đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 11: Xe ben và khu vực xây dựng
SCENARIO_11 = {
    'vehicle': 'xe ben',
    'location': 'khu vực xây dựng',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực xây dựng',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe ben đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực xây dựng có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe ben bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe ben vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực xây dựng. Khi vừa rời khỏi khu vực, xe ben tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe ben đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe ben đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe ben đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe ben đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 12: Xe limousine và khu nghỉ dưỡng
SCENARIO_12 = {
    'vehicle': 'xe limousine',
    'location': 'khu nghỉ dưỡng',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu nghỉ dưỡng',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe limousine đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu nghỉ dưỡng có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe limousine bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe limousine vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu nghỉ dưỡng. Khi vừa rời khỏi khu vực, xe limousine tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe limousine đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe limousine đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe limousine đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe limousine đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 13: Xe cứu hỏa và đường hầm
SCENARIO_13 = {
    'vehicle': 'xe cứu hỏa',
    'location': 'đường hầm',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'đường hầm',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe cứu hỏa đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có đường hầm có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe cứu hỏa bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe cứu hỏa vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi qua khỏi đường hầm. Khi vừa qua khỏi đường hầm, xe cứu hỏa tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa qua khỏi đường hầm. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe cứu hỏa đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe cứu hỏa đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe cứu hỏa đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe cứu hỏa đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 14: Xe đầu kéo và khu vực cảng biển
SCENARIO_14 = {
    'vehicle': 'xe đầu kéo',
    'location': 'khu vực cảng biển',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực cảng',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe đầu kéo đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực cảng biển có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe đầu kéo bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe đầu kéo vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực cảng. Khi vừa rời khỏi khu vực, xe đầu kéo tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe đầu kéo đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe đầu kéo đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe đầu kéo đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe đầu kéo đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 15: Xe chở khách du lịch và khu bảo tồn thiên nhiên
SCENARIO_15 = {
    'vehicle': 'xe chở khách du lịch',
    'location': 'khu bảo tồn thiên nhiên',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu bảo tồn',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe chở khách du lịch đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu bảo tồn thiên nhiên có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu bảo tồn. Khi vừa rời khỏi khu vực, xe tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 16: Xe bồn chở xăng và trạm xăng
SCENARIO_16 = {
    'vehicle': 'xe bồn chở xăng',
    'location': 'khu vực trạm xăng',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực trạm xăng',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe bồn chở xăng đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực trạm xăng có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe bồn bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe bồn vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực trạm xăng. Khi vừa rời khỏi khu vực, xe bồn tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe bồn đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe bồn đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe bồn đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe bồn đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 17: Xe chở rác và khu dân cư mới
SCENARIO_17 = {
    'vehicle': 'xe chở rác',
    'location': 'khu dân cư mới',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu dân cư',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe chở rác đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu dân cư mới có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe chở rác bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe chở rác vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu dân cư. Khi vừa rời khỏi khu vực, xe chở rác tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe chở rác đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe chở rác đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe chở rác đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe chở rác đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 18: Xe cấp cứu và đường cao tốc
SCENARIO_18 = {
    'vehicle': 'xe cấp cứu',
    'location': 'đoạn đường đang sửa chữa trên cao tốc',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'đoạn đường sửa chữa',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe cấp cứu đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có đoạn đường đang sửa chữa trên cao tốc có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe cấp cứu bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe cấp cứu vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi qua khỏi đoạn đường sửa chữa. Khi vừa qua khỏi đoạn đường, xe cấp cứu tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa qua khỏi đoạn đường. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe cấp cứu đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe cấp cứu đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe cấp cứu đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe cấp cứu đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 19: Xe công nông và đường làng
SCENARIO_19 = {
    'vehicle': 'xe công nông',
    'location': 'khu vực đường làng hẹp',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'đường làng',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe công nông đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực đường làng hẹp có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe công nông bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe công nông vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi qua khỏi đường làng. Khi vừa qua khỏi đường làng, xe công nông tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa qua khỏi đường làng. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe công nông đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe công nông đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe công nông đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe công nông đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# Scenario 20: Xe tải nhỏ và khu vực trung tâm thành phố
SCENARIO_20 = {
    'vehicle': 'xe tải nhỏ',
    'location': 'khu vực trung tâm thành phố',
    'sign_type': 'biển báo giới hạn tốc độ',
    'exit_location': 'khu vực trung tâm',
    'template_q': Template(
        r"""
Câu ${idx}: Một xe tải nhỏ đang di chuyển với vận tốc ${v0_kmh} km/h thì phát hiện ở phía trước cách vị trí xe một đoạn ${d_detect} m có khu vực trung tâm thành phố có gắn biển báo giới hạn tốc độ tối đa cho phép là ${v_sign_kmh} km/h. ${t_react} giây sau đó, xe tải nhỏ bắt đầu giảm tốc với vận tốc \(v_1(t) = at + b\) (m/s) \((a, b \in \mathbb{R}, a < 0)\), trong đó \(t\) là thời gian tính bằng giây kể từ khi xe bắt đầu giảm tốc độ. Khi xe tải nhỏ vừa đến vị trí đặt biển báo thì tốc độ của xe bằng ${v_sign_kmh} km/h và giữ nguyên vận tốc như vậy cho đến khi rời khỏi khu vực trung tâm. Khi vừa rời khỏi khu vực, xe tải nhỏ tăng tốc với vận tốc \(v_2(t_1) = mt_1 + n\) (m/s) \((m, n \in \mathbb{R}, m > 0)\), trong đó \(t_1\) là thời gian tính bằng giây kể từ khi xe vừa rời khỏi khu vực. Biết rằng đúng ${t_accel} giây sau khi tăng tốc, xe tải nhỏ đạt vận tốc ${v_final_kmh} km/h.

Các mệnh đề sau đúng hay sai?

${label_a}) Quãng đường xe tải nhỏ đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ là ${prop_a_val} m.

${label_b}) \(b = ${prop_b_val}\).

${label_c}) Xe tải nhỏ đến vị trí đặt biển báo tốc độ tối đa cho phép sau ${prop_c_val} giây kể từ khi giảm tốc.

${label_d}) Quãng đường xe tải nhỏ đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là ${prop_d_val} m.
"""
    )
}

# List of all scenarios (20 values)
ALL_SCENARIOS = [
    SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4, SCENARIO_5,
    SCENARIO_6, SCENARIO_7, SCENARIO_8, SCENARIO_9, SCENARIO_10,
    SCENARIO_11, SCENARIO_12, SCENARIO_13, SCENARIO_14, SCENARIO_15,
    SCENARIO_16, SCENARIO_17, SCENARIO_18, SCENARIO_19, SCENARIO_20
]

TEMPLATE_SOL = Template(
    r"""
Lời giải:

Ta có ${v0_kmh} km/h = ${v0} m/s; ${v_sign_kmh} km/h = ${v_sign} m/s; ${v_final_kmh} km/h = ${v_final} m/s.

a) Quãng đường xe máy đi được từ khi phát hiện biển báo giới hạn tốc độ đến khi bắt đầu giảm tốc độ (trong ${t_react} giây với vận tốc ${v0} m/s) là \(${v0} \cdot ${t_react} = ${d_react}\) m.

b) \(v_1(0) = ${v0} \Leftrightarrow b = ${v0} \Rightarrow v_1(t) = at + ${v0}\) m/s.

c) Xe máy đến vị trí đặt biển báo tốc độ tối đa cho phép sau \(t\) giây kể từ khi giảm tốc khi \(v_1(t) = at + ${v0} = ${v_sign} \Leftrightarrow t = -\dfrac{${v0_minus_vsign}}{a}\) và quãng đường đi được trong khoảng thời gian đó là \(\displaystyle\int_0^{t} v_1(t) \, dt = ${d_decel} \Leftrightarrow \displaystyle\int_0^{-\frac{${v0_minus_vsign}}{a}} (at + ${v0}) \, dt = ${d_decel} \Leftrightarrow a = -\dfrac{${v0_minus_vsign}}{${t_decel}} \Rightarrow t = ${t_decel}\).

d) Ta có \(v_2(0) = ${v_sign} \Leftrightarrow n = ${v_sign}\); \(v_2(${t_accel}) = ${v_final} \Leftrightarrow ${t_accel}m + ${v_sign} = ${v_final} \Leftrightarrow m = ${m_val} \Rightarrow v_2(t_1) = ${m_val_display}t_1 + ${v_sign}\) m/s.

Quãng đường xe máy đi được kể từ khi tăng tốc đến khi đạt vận tốc ${v_final_kmh} km/h là \(\displaystyle\int_0^{${t_accel}} v_2(t_1) \, dt_1 = \displaystyle\int_0^{${t_accel}} \left(${m_val_display}t_1 + ${v_sign}\right) dt_1 = ${d_accel}\) m.

Vậy a) ${ans_a}; b) ${ans_b}; c) ${ans_c} và d) ${ans_d}.
"""
)

# ==================== MAIN CLASS ====================

class MotorcycleQuestion:
    def __init__(self):
        # Velocities in m/s
        self.v0 = 0  # initial velocity
        self.v_sign = 0  # speed limit at sign
        self.v_final = 0  # final velocity after acceleration
        
        # Time intervals
        self.t_react = 0  # reaction time before deceleration
        self.t_decel = 0  # time to decelerate to v_sign
        self.t_accel = 0  # time to accelerate to v_final
        
        # Distance
        self.d_detect = 0  # distance when sign detected
        
        # Coefficients
        self.a_val = Fraction(0)  # deceleration coefficient (negative)
        self.m_val = Fraction(0)  # acceleration coefficient (positive)
        
        # Props
        self.res_a = True
        self.res_b = True
        self.res_c = True
        self.res_d = True
        
        self.prop_a_val = ""
        self.prop_b_val = ""
        self.prop_c_val = ""
        self.prop_d_val = ""
        
        # Scenario selection
        self.scenario = None

    def generate_parameters(self):
        """
        Generate parameters for motorcycle problem.
        
        Phase 1 (reaction): constant velocity v0 for t_react seconds
        Phase 2 (decel): v1(t) = at + b, from v0 to v_sign
        Phase 3 (const): maintain v_sign through construction zone
        Phase 4 (accel): v2(t1) = mt1 + n, from v_sign to v_final
        
        For nice results:
        - v0, v_sign, v_final should be multiples of 5 (in m/s) -> km/h multiples of 18
        - t_react, t_decel, t_accel should give nice integer distances
        """
        # Randomly select a scenario
        self.scenario = random.choice(ALL_SCENARIOS)
        
        # Pre-computed nice combinations (20 values)
        # Format: (v0_ms, v_sign_ms, v_final_ms) all in m/s
        # Common km/h values: 18->5, 36->10, 54->15, 72->20, 90->25, 108->30
        velocity_combos = [
            (10, 5, 15),   # 36, 18, 54 km/h
            (15, 5, 20),   # 54, 18, 72 km/h
            (20, 10, 25),  # 72, 36, 90 km/h
            (15, 10, 20),  # 54, 36, 72 km/h
            (10, 5, 20),   # 36, 18, 72 km/h
            (20, 5, 25),   # 72, 18, 90 km/h
            (15, 5, 25),   # 54, 18, 90 km/h
            (20, 10, 30),  # 72, 36, 108 km/h
            (25, 10, 30),  # 90, 36, 108 km/h
            (25, 15, 30),  # 90, 54, 108 km/h
            (20, 15, 25),  # 72, 54, 90 km/h
            (15, 10, 25),  # 54, 36, 90 km/h
            (25, 5, 30),   # 90, 18, 108 km/h
            (30, 10, 35),  # 108, 36, 126 km/h
            (30, 15, 35),  # 108, 54, 126 km/h
            (25, 20, 30),  # 90, 72, 108 km/h
            (20, 5, 30),   # 72, 18, 108 km/h
            (30, 20, 35),  # 108, 72, 126 km/h
            (35, 15, 40),  # 126, 54, 144 km/h
            (35, 20, 40),  # 126, 72, 144 km/h
        ]
        
        self.v0, self.v_sign, self.v_final = random.choice(velocity_combos)
        
        # Reaction time (20 values: 1-20 seconds)
        t_react_values = list(range(1, 21))  # [1, 2, 3, ..., 20]
        self.t_react = random.choice(t_react_values)
        
        # d_react = v0 * t_react
        d_react = self.v0 * self.t_react
        
        # For deceleration phase, we want nice t_decel
        # v1(t) = at + v0, v1(t_decel) = v_sign
        # => a * t_decel + v0 = v_sign => a = (v_sign - v0) / t_decel
        # Distance: integral of (at + v0) from 0 to t_decel = (a/2)*t_decel^2 + v0*t_decel
        #         = (v_sign - v0)/2 * t_decel + v0*t_decel = (v_sign + v0)/2 * t_decel
        
        # We want d_decel to be integer: (v_sign + v0)/2 * t_decel
        # Ensure parity match for integer distance (20 values each case)
        if (self.v0 + self.v_sign) % 2 != 0:
            # sum is odd, t_decel must be even (20 even values: 2, 4, 6, ..., 40)
            t_decel_values = [2 * i for i in range(1, 21)]  # [2, 4, 6, ..., 40]
            self.t_decel = random.choice(t_decel_values)
        else:
            # sum is even, any t_decel works (20 values: 1-20)
            t_decel_values = list(range(1, 21))  # [1, 2, 3, ..., 20]
            self.t_decel = random.choice(t_decel_values)
        
        d_decel = (self.v0 + self.v_sign) * self.t_decel // 2
        
        # Total distance from detection to sign
        self.d_detect = d_react + d_decel
        
        # Deceleration coefficient
        self.a_val = Fraction(self.v_sign - self.v0, self.t_decel)
        
        # Acceleration phase (20 values: 1-20 seconds)
        # v2(t1) = mt1 + n, n = v_sign, v2(t_accel) = v_final
        # m = (v_final - v_sign) / t_accel
        t_accel_values = list(range(1, 21))  # [1, 2, 3, ..., 20]
        self.t_accel = random.choice(t_accel_values)
        self.m_val = Fraction(self.v_final - self.v_sign, self.t_accel)

    def solve(self):
        # a) Distance during reaction
        d_react = self.v0 * self.t_react
        
        # b) b = v0 (initial velocity when starting deceleration)
        b_true = self.v0
        
        # c) Time to reach sign = t_decel
        t_decel_true = self.t_decel
        
        # d) Distance during acceleration
        # integral of (m*t1 + v_sign) from 0 to t_accel
        # = (m/2)*t_accel^2 + v_sign*t_accel
        # = (v_final - v_sign)/2 * t_accel + v_sign * t_accel
        # = (v_final + v_sign)/2 * t_accel
        d_accel = (self.v_final + self.v_sign) * self.t_accel // 2
        
        # Distance from start of decel to sign
        d_decel = (self.v0 + self.v_sign) * self.t_decel // 2
        
        return {
            'd_react': d_react,
            'b_true': b_true,
            't_decel_true': t_decel_true,
            'd_accel': d_accel,
            'd_decel': d_decel,
        }

    def distort_and_set_props(self, sol_data):
        # A: Distance during reaction
        if random.random() < 0.5:
            self.res_a = True
            self.prop_a_val = str(sol_data['d_react'])
        else:
            self.res_a = False
            fake = sol_data['d_react'] + random.choice([5, -5, 10, -10])
            self.prop_a_val = str(fake)
        
        # B: Value of b
        if random.random() < 0.5:
            self.res_b = True
            self.prop_b_val = str(sol_data['b_true'])
        else:
            self.res_b = False
            # Common mistake: using v_sign instead of v0, or using km/h value
            fake_choices = [self.v_sign, self.v0 + 5, self.v0 - 5]
            fake = random.choice(fake_choices)
            self.prop_b_val = str(fake)
        
        # C: Time to reach sign
        if random.random() < 0.5:
            self.res_c = True
            self.prop_c_val = str(sol_data['t_decel_true'])
        else:
            self.res_c = False
            fake = sol_data['t_decel_true'] + random.choice([1, -1, 2, -2])
            if fake <= 0:
                fake = sol_data['t_decel_true'] + 2
            self.prop_c_val = str(fake)
        
        # D: Distance during acceleration
        if random.random() < 0.5:
            self.res_d = True
            self.prop_d_val = str(sol_data['d_accel'])
        else:
            self.res_d = False
            fake = sol_data['d_accel'] + random.choice([4, -4, 8, -8])
            self.prop_d_val = str(fake)

    @staticmethod
    def label_with_star(letter: str, is_true: bool) -> str:
        return f"*{letter}" if is_true else f"{letter}"

    def generate_question(self, idx: int) -> str:
        self.generate_parameters()
        sol_data = self.solve()
        self.distort_and_set_props(sol_data)
        
        # Convert velocities to km/h for display
        v0_kmh = self.v0 * 18 // 5  # v0 * 3.6
        v_sign_kmh = self.v_sign * 18 // 5
        v_final_kmh = self.v_final * 18 // 5
        
        params = {
            'idx': idx,
            'v0': self.v0,
            'v0_kmh': v0_kmh,
            'v_sign': self.v_sign,
            'v_sign_kmh': v_sign_kmh,
            'v_final': self.v_final,
            'v_final_kmh': v_final_kmh,
            'd_detect': self.d_detect,
            't_react': self.t_react,
            't_accel': self.t_accel,
            
            'label_a': self.label_with_star('a', self.res_a),
            'label_b': self.label_with_star('b', self.res_b),
            'label_c': self.label_with_star('c', self.res_c),
            'label_d': self.label_with_star('d', self.res_d),
            
            'res_a_text': "Đúng" if self.res_a else "Sai",
            'res_b_text': "Đúng" if self.res_b else "Sai",
            'res_c_text': "Đúng" if self.res_c else "Sai",
            'res_d_text': "Đúng" if self.res_d else "Sai",
            
            'prop_a_val': self.prop_a_val,
            'prop_b_val': self.prop_b_val,
            'prop_c_val': self.prop_c_val,
            'prop_d_val': self.prop_d_val,
            
            # Solution params
            'd_react': sol_data['d_react'],
            'd_decel': sol_data['d_decel'],
            't_decel': sol_data['t_decel_true'],
            'v0_minus_vsign': self.v0 - self.v_sign,
            'm_val': to_latex_num(self.m_val),
            'm_val_display': to_latex_num_display(self.m_val),
            'd_accel': sol_data['d_accel'],
            
            'ans_a': "đúng" if self.res_a else "sai",
            'ans_b': "đúng" if self.res_b else "sai",
            'ans_c': "đúng" if self.res_c else "sai",
            'ans_d': "đúng" if self.res_d else "sai",
        }
        
        # Use the scenario's template for question
        question = self.scenario['template_q'].substitute(params)
        solution = TEMPLATE_SOL.substitute(params)
        
        return f"{question}\n{solution}"


# ==================== MAIN ====================

def main():
    num_questions = 5
    if len(sys.argv) > 1:
        try:
            num_questions = max(1, int(sys.argv[1]))
        except ValueError:
            print("Tham số không hợp lệ, sử dụng mặc định 5 câu hỏi.")
    
    questions = []
    for i in range(num_questions):
        q = MotorcycleQuestion()
        questions.append(q.generate_question(i + 1))
        
    content = "\n\\newpage\n".join(questions)
    latex = create_latex_document(content)
    
    output_path = os.path.join(os.path.dirname(__file__), "bai_toan_xe_may.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Đã tạo {num_questions} câu hỏi trong bai_toan_xe_may.tex")


if __name__ == "__main__":
    main()
