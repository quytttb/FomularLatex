import os
import random
import logging
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Any, List, Tuple
from string import Template

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ==============================================================================
# 20 NGỮ CẢNH
# ==============================================================================
# Mỗi ngữ cảnh chứa các text template để điền vào đề bài và lời giải.
# Các placeholder dùng string.Template: ${N}, ${N_M}, ${N_B}, ${N_notB}, etc.
# Lưu ý: $$ dùng để escape ký tự $ trong LaTeX math mode.

CONTEXTS = [
    # 1. Bầu cử địa phương
    {
        "intro": Template(
            r"Trong một cuộc khảo sát trước thềm bầu cử thị trưởng, kết quả cho thấy ${N_B} người nói sẽ bầu cho ứng viên X và ${N_notB} người nói sẽ không bầu. Thực tế lịch sử chỉ ra tỉ lệ người thực sự đi bầu cho X tương ứng với nhóm ""nói có"" và ""nói không"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Cuộc khảo sát này được thực hiện trên tổng cộng ${N} cử tri (trong đó có ${N_M} người là đảng viên lâu năm)."
        ),
        "event_A": "Người được khảo sát thực sự bầu cho ứng viên X",
        "event_B": "Người được khảo sát trả lời sẽ bầu cho ứng viên X",
        "subject": "người được khảo sát",
        "action_positive": "bầu cho ứng viên X",
        "action_negative": "không bầu cho ứng viên X",
        "reply_positive": "bầu",
        "reply_negative": "không bầu",
        "group_M": "đảng viên lâu năm",
        "group_notM": "không phải đảng viên lâu năm",
        "sol_M_label": "Đảng viên lâu năm",
    },
    # 2. Mua điện thoại mới
    {
        "intro": Template(
            r"Một hãng công nghệ nhận thấy tỉ lệ khách hàng thực sự mua sản phẩm mới dựa trên câu trả lời khảo sát ""sẽ mua"" và ""không mua"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Trong chiến dịch ra mắt, họ phỏng vấn ngẫu nhiên ${N} người (có ${N_M} người đang dùng sản phẩm cũ của hãng). Kết quả có ${N_notB} người nói không mua và ${N_B} người cho biết sẽ mua."
        ),
        "event_A": "Người được phỏng vấn thực sự mua điện thoại mới",
        "event_B": "Người được phỏng vấn trả lời sẽ mua điện thoại mới",
        "subject": "người được phỏng vấn",
        "action_positive": "mua điện thoại",
        "action_negative": "không mua điện thoại",
        "reply_positive": "mua",
        "reply_negative": "không mua",
        "group_M": "người đang dùng sản phẩm cũ",
        "group_notM": "không dùng sản phẩm cũ",
        "sol_M_label": "Dùng sản phẩm cũ",
    },
    # 3. Tham gia đêm nhạc
    {
        "intro": Template(
            r"Có ${N_notB} sinh viên nói không đi và ${N_B} sinh viên khẳng định sẽ đi khi được khảo sát ngẫu nhiên về việc tham gia đêm nhạc hội (tổng cộng phỏng vấn ${N} người, trong đó ${N_M} bạn thuộc ban tổ chức). Số liệu thực tế cho thấy tỉ lệ người thực sự có mặt tương ứng với câu trả lời ""có đi"" và ""không đi"" là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Sinh viên thực sự tham gia đêm nhạc hội",
        "event_B": "Sinh viên trả lời sẽ tham gia đêm nhạc hội",
        "subject": "sinh viên được khảo sát",
        "action_positive": "tham gia đêm nhạc",
        "action_negative": "không tham gia",
        "reply_positive": "tham gia",
        "reply_negative": "không tham gia",
        "group_M": "sinh viên thuộc ban tổ chức",
        "group_notM": "không thuộc ban tổ chức",
        "sol_M_label": "Ban tổ chức",
    },
    # 4. Đăng ký tập Gym
    {
        "intro": Template(
            r"Tỉ lệ đăng ký thực tế đối với nhóm trả lời ""có"" và ""không"" lần lượt đạt mức ${P_A_B_pct} và ${P_A_notB_pct}. Dữ liệu này được rút ra từ việc lấy ý kiến ${N} khách hàng tham quan phòng tập (có ${N_M} người từng là hội viên cũ). Kết quả cho thấy ${N_B} người nói sẽ đăng ký và ${N_notB} người nói sẽ không đăng ký."
        ),
        "event_A": "Khách hàng thực sự đăng ký gói tập",
        "event_B": "Khách hàng trả lời sẽ đăng ký gói tập",
        "subject": "khách hàng được phỏng vấn",
        "action_positive": "đăng ký",
        "action_negative": "không đăng ký",
        "reply_positive": "đăng ký",
        "reply_negative": "không đăng ký",
        "group_M": "hội viên cũ",
        "group_notM": "không phải hội viên cũ",
        "sol_M_label": "Hội viên cũ",
    },
    # 5. Xem phim rạp suất chiếu sớm
    {
        "intro": Template(
            r"Khảo sát ${N} khán giả (có ${N_M} người là fan cứng của đạo diễn), có ${N_B} người cho biết họ sẽ đi xem suất chiếu sớm, ${N_notB} người từ chối. Tỉ lệ khán giả thực sự ra rạp ứng với câu trả lời ""có đi xem"" và ""không đi xem"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Khán giả thực sự đi xem suất chiếu sớm",
        "event_B": "Khán giả trả lời sẽ đi xem suất chiếu sớm",
        "subject": "khán giả được phỏng vấn",
        "action_positive": "xem phim",
        "action_negative": "không xem phim",
        "reply_positive": "xem",
        "reply_negative": "không xem",
        "group_M": "fan cứng của đạo diễn",
        "group_notM": "không phải fan cứng",
        "sol_M_label": "Fan cứng",
    },
    # 6. Đầu tư cổ phiếu
    {
        "intro": Template(
            r"Công ty chứng khoán khảo sát ${N} nhà đầu tư (có ${N_M} người là khách hàng VIP). Tỉ lệ giải ngân thực sự của nhóm ""có ý định mua"" và ""không có ý định mua"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Kết quả ghi nhận ${N_notB} người không có ý định mua và ${N_B} người có ý định mua mã cổ phiếu XYZ."
        ),
        "event_A": "Nhà đầu tư thực sự mua cổ phiếu",
        "event_B": "Nhà đầu tư trả lời có ý định mua cổ phiếu",
        "subject": "nhà đầu tư được phỏng vấn",
        "action_positive": "mua cổ phiếu",
        "action_negative": "không mua cổ phiếu",
        "reply_positive": "mua",
        "reply_negative": "không mua",
        "group_M": "khách hàng VIP",
        "group_notM": "không phải khách VIP",
        "sol_M_label": "Khách VIP",
    },
    # 7. Nâng cấp ứng dụng Premium
    {
        "intro": Template(
            r"Trong số ${N} người dùng bản miễn phí (có ${N_M} người từng dùng thử gói Premium), có ${N_B} người nói sẽ nâng cấp và ${N_notB} người nói không. Tỉ lệ nâng cấp thực tế của những người nói ""sẽ nâng cấp"" và ""không nâng cấp"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Người dùng thực sự nâng cấp Premium",
        "event_B": "Người dùng trả lời sẽ nâng cấp Premium",
        "subject": "người dùng được phỏng vấn",
        "action_positive": "nâng cấp",
        "action_negative": "không nâng cấp",
        "reply_positive": "nâng cấp",
        "reply_negative": "không nâng cấp",
        "group_M": "người từng dùng thử",
        "group_notM": "chưa từng dùng thử",
        "sol_M_label": "Từng dùng thử",
    },
    # 8. Đăng ký khóa học Tiếng Anh
    {
        "intro": Template(
            r"Xác suất một học viên đóng học phí thực tế sau khi nói ""có học"" và ""không học"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Trong buổi học thử, trung tâm phỏng vấn ${N} người (trong đó ${N_M} người là sinh viên năm cuối), ghi nhận ${N_notB} người từ chối và ${N_B} người nói sẽ đăng ký."
        ),
        "event_A": "Học viên thực sự đóng học phí",
        "event_B": "Học viên trả lời sẽ đóng học phí",
        "subject": "học viên được phỏng vấn",
        "action_positive": "đóng học phí",
        "action_negative": "không đóng học phí",
        "reply_positive": "đóng",
        "reply_negative": "không đóng",
        "group_M": "sinh viên năm cuối",
        "group_notM": "không phải sinh viên năm cuối",
        "sol_M_label": "Sinh viên năm cuối",
    },
    # 9. Mua tour du lịch hè
    {
        "intro": Template(
            r"Khảo sát ${N} khách hàng (gồm ${N_M} khách hàng có thẻ thành viên), có ${N_B} khách dự định đi tour và ${N_notB} khách dự định ở nhà. Hãng lữ hành chỉ ra tỉ lệ khách thực sự chốt mua tour của nhóm ""dự định đi"" và ""dự định ở nhà"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Khách hàng thực sự chốt mua tour",
        "event_B": "Khách hàng trả lời có dự định mua tour",
        "subject": "khách hàng được phỏng vấn",
        "action_positive": "mua tour",
        "action_negative": "không mua tour",
        "reply_positive": "mua",
        "reply_negative": "không mua",
        "group_M": "người có thẻ thành viên",
        "group_notM": "không có thẻ thành viên",
        "sol_M_label": "Có thẻ thành viên",
    },
    # 10. Thử món ăn mới tại nhà hàng
    {
        "intro": Template(
            r"Khả năng khách thực sự gọi món mới ứng với phản hồi ""muốn"" và ""không muốn"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Trước đó, có ${N_notB} người nói không muốn thử và ${N_B} người nói muốn thử trong khảo sát ${N} thực khách (có ${N_M} người đang đi ăn theo gia đình)."
        ),
        "event_A": "Thực khách thực sự gọi món mới",
        "event_B": "Thực khách trả lời muốn gọi món mới",
        "subject": "thực khách được phỏng vấn",
        "action_positive": "gọi món mới",
        "action_negative": "không gọi món mới",
        "reply_positive": "muốn",
        "reply_negative": "không muốn",
        "group_M": "người đi ăn gia đình",
        "group_notM": "không đi ăn gia đình",
        "sol_M_label": "Đi ăn gia đình",
    },
    # 11. Mua xe ô tô điện
    {
        "intro": Template(
            r"Có ${N_B} người đánh giá ""có mua"" và ${N_notB} người đánh giá ""không mua"" trong nhóm ${N} khách hàng tham gia sự kiện lái thử (${N_M} người trong đó đang sở hữu xe xăng). Tỉ lệ chuyển đổi mua xe thành công của nhóm ""có mua"" và ""không mua"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Khách hàng thực sự mua xe điện",
        "event_B": "Khách hàng đánh giá sẽ mua xe điện",
        "subject": "khách hàng được phỏng vấn",
        "action_positive": "mua xe điện",
        "action_negative": "không mua xe điện",
        "reply_positive": "mua",
        "reply_negative": "không mua",
        "group_M": "người sở hữu xe xăng",
        "group_notM": "không sở hữu xe xăng",
        "sol_M_label": "Sở hữu xe xăng",
    },
    # 12. Tham gia hiến máu nhân đạo
    {
        "intro": Template(
            r"Ban tổ chức nhận thấy tỉ lệ người thực sự hiến máu đối với những ai cam kết trước và nói không tham gia lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Khảo sát ${N} tình nguyện viên (có ${N_M} người thuộc đội thanh niên xung kích), có ${N_notB} người từ chối và ${N_B} người cam kết hiến máu."
        ),
        "event_A": "Tình nguyện viên thực sự hiến máu",
        "event_B": "Tình nguyện viên cam kết sẽ hiến máu",
        "subject": "tình nguyện viên được phỏng vấn",
        "action_positive": "hiến máu",
        "action_negative": "không hiến máu",
        "reply_positive": "tham gia",
        "reply_negative": "không tham gia",
        "group_M": "đội thanh niên xung kích",
        "group_notM": "ngoài đội xung kích",
        "sol_M_label": "Thanh niên xung kích",
    },
    # 13. Tham dự hội thảo trực tuyến
    {
        "intro": Template(
            r"Có ${N} khách hàng được gửi email (có ${N_M} người từng tham gia sự kiện trước đó). Ghi nhận có ${N_notB} người báo bận và ${N_B} người đăng ký tham dự. Tỉ lệ online thực tế của người đăng ký tham dự và người báo bận lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Khách hàng thực sự online xem hội thảo",
        "event_B": "Khách hàng trả lời sẽ tham dự hội thảo",
        "subject": "khách hàng được phỏng vấn",
        "action_positive": "xem hội thảo",
        "action_negative": "không xem hội thảo",
        "reply_positive": "tham dự",
        "reply_negative": "không tham dự",
        "group_M": "người từng tham gia sự kiện trước",
        "group_notM": "chưa từng tham gia",
        "sol_M_label": "Từng tham gia sự kiện",
    },
    # 14. Tiệc tất niên công ty
    {
        "intro": Template(
            r"Phòng nhân sự gửi khảo sát cho ${N} nhân viên (trong đó có ${N_M} nhân viên cấp quản lý). Thống kê thu về ${N_B} người đồng ý tham gia và ${N_notB} người từ chối. Thực tế chỉ có tỉ lệ thực sự dự tiệc của những người nói ""đồng ý"" và nói ""từ chối"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Nhân viên thực sự đến dự tiệc",
        "event_B": "Nhân viên trả lời đồng ý tham dự",
        "subject": "nhân viên được khảo sát",
        "action_positive": "dự tiệc",
        "action_negative": "không dự tiệc",
        "reply_positive": "đồng ý",
        "reply_negative": "từ chối",
        "group_M": "nhân viên cấp quản lý",
        "group_notM": "không phải quản lý",
        "sol_M_label": "Cấp quản lý",
    },
    # 15. Mua trò chơi điện tử
    {
        "intro": Template(
            r"Tỉ lệ mua game thực tế của những người trả lời ""có mua"" và ""không mua"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Trong đợt khảo sát ${N} game thủ ngẫu nhiên (có ${N_M} người đã chơi bản dùng thử), kết quả thu về ${N_notB} ý kiến không mua và ${N_B} ý kiến sẽ mua."
        ),
        "event_A": "Game thủ thực sự mua game",
        "event_B": "Game thủ trả lời sẽ mua game",
        "subject": "game thủ được phỏng vấn",
        "action_positive": "mua game",
        "action_negative": "không mua game",
        "reply_positive": "mua",
        "reply_negative": "không mua",
        "group_M": "người đã chơi bản dùng thử",
        "group_notM": "chưa chơi thử",
        "sol_M_label": "Đã chơi bản thử",
    },
    # 16. Tham gia giải chạy Marathon
    {
        "intro": Template(
            r"Có ${N_B} người xác nhận sẽ chạy, ${N_notB} người nói không khi hỏi ${N} người về giải chạy cuối tuần (có ${N_M} người là thành viên câu lạc bộ điền kinh). Tỉ lệ người thực sự ra đường chạy của nhóm ""nói có"" và ""nói không"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Người được hỏi thực sự chạy marathon",
        "event_B": "Người được hỏi trả lời sẽ chạy marathon",
        "subject": "người được phỏng vấn",
        "action_positive": "chạy marathon",
        "action_negative": "không chạy marathon",
        "reply_positive": "chạy",
        "reply_negative": "không chạy",
        "group_M": "thành viên CLB điền kinh",
        "group_notM": "ngoài CLB",
        "sol_M_label": "CLB điền kinh",
    },
    # 17. Mua đồ uống theo mùa
    {
        "intro": Template(
            r"Chỉ có tỉ lệ thực sự mua đồ uống mới của khách nói ""rất thích"" và nói ""không thích"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Quán cà phê phỏng vấn ${N} khách (${N_M} người là sinh viên) và thu được ${N_notB} lượt trả lời ""không thích"", ${N_B} lượt trả lời ""rất thích""."
        ),
        "event_A": "Khách hàng thực sự mua đồ uống mới",
        "event_B": "Khách hàng trả lời rất thích đồ uống mới",
        "subject": "khách hàng được phỏng vấn",
        "action_positive": "mua đồ uống",
        "action_negative": "không mua đồ uống",
        "reply_positive": "thích",
        "reply_negative": "không thích",
        "group_M": "khách sinh viên",
        "group_notM": "không phải sinh viên",
        "sol_M_label": "Sinh viên",
    },
    # 18. Tham gia chiến dịch nhặt rác
    {
        "intro": Template(
            r"Theo ghi nhận từ ${N} thanh niên (có ${N_M} người là đoàn viên), có ${N_B} người xác nhận sẽ đến, ${N_notB} người nói không đến. Tỉ lệ có mặt làm nhiệm vụ của nhóm xác nhận ""sẽ đến"" và nhóm ""không đến"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Thanh niên thực sự tham gia nhặt rác",
        "event_B": "Thanh niên xác nhận sẽ đến nhặt rác",
        "subject": "thanh niên được phỏng vấn",
        "action_positive": "tham gia",
        "action_negative": "không tham gia",
        "reply_positive": "tham gia",
        "reply_negative": "không tham gia",
        "group_M": "đoàn viên",
        "group_notM": "không phải đoàn viên",
        "sol_M_label": "Đoàn viên",
    },
    # 19. Nhận nuôi động vật
    {
        "intro": Template(
            r"Khả năng nhận nuôi thực sự của những gia đình điền form ""có nuôi"" và ""không nuôi"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}. Trạm cứu hộ tiếp đón ${N} gia đình (${N_M} gia đình sống ở chung cư). Qua khảo sát, ${N_notB} gia đình điền ""không nuôi"" và ${N_B} gia đình điền ""có nuôi""."
        ),
        "event_A": "Gia đình thực sự nhận nuôi động vật",
        "event_B": "Gia đình điền form có nhận nuôi động vật",
        "subject": "gia đình được phỏng vấn",
        "action_positive": "nhận nuôi",
        "action_negative": "không nhận nuôi",
        "reply_positive": "nuôi",
        "reply_negative": "không nuôi",
        "group_M": "gia đình sống ở chung cư",
        "group_notM": "không ở chung cư",
        "sol_M_label": "Ở chung cư",
    },
    # 20. Mua vé đi công viên giải trí
    {
        "intro": Template(
            r"Có ${N_B} người nói sẽ đi công viên và ${N_notB} người nói không đi khi hỏi ${N} người dân (có ${N_M} người có trẻ nhỏ). Tỉ lệ thực tế mua vé đi của nhóm trả lời ""sẽ đi"" và nhóm ""không đi"" lần lượt là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Người dân thực sự mua vé đi công viên",
        "event_B": "Người dân trả lời sẽ đi công viên",
        "subject": "người dân được phỏng vấn",
        "action_positive": "đi công viên",
        "action_negative": "không đi công viên",
        "reply_positive": "đi",
        "reply_negative": "không đi",
        "group_M": "người có trẻ nhỏ",
        "group_notM": "không có trẻ nhỏ",
        "sol_M_label": "Có trẻ nhỏ",
    },
    # 21. Derby Manchester
    {
        "intro": Template(
            r"Trước 3 tiếng khi diễn ra trận Derby thành Manchester giữa MU-MC. Người ta phỏng vấn ngẫu nhiên ${N} người hâm mộ của MU (có ${N_M} người đang mặc áo của đội bóng) về việc có nên xem trận đấu đó hay không. Kết quả cho thấy rằng ${N_B} người trả lời sẽ xem, ${N_notB} người trả lời sẽ không xem. Nhưng thực tế cho thấy rằng tỉ lệ người hâm mộ MU thực sự xem trận đấu tương ứng với những cách trả lời ""có xem"" và ""không xem"" là ${P_A_B_pct} và ${P_A_notB_pct}."
        ),
        "event_A": "Người được phỏng vấn thực sự sẽ xem trận đấu",
        "event_B": "Người được phỏng vấn trả lời sẽ xem trận đấu",
        "subject": "người được phỏng vấn",
        "action_positive": "xem trận đấu",
        "action_negative": "không xem trận đấu",
        "reply_positive": "có xem",
        "reply_negative": "không xem",
        "group_M": "người đang mặc áo của đội bóng",
        "group_notM": "không mặc áo của đội bóng",
        "sol_M_label": "Mặc áo đội bóng",
    },
]

# ==============================================================================
# TEMPLATE LỜI GIẢI (tổng quát)
# ==============================================================================
TEMPLATE_SOLUTION = Template(r"""
Lời giải

a) ${ans_a}. Tỉ lệ ${subject} thực sự sẽ ${action_positive} là:
$$P(A) = P(B) \cdot P(A|B) + P(\overline{B}) \cdot P(A|\overline{B})$$

$$P(A) = ${P_B} \cdot ${P_A_B} + ${P_notB} \cdot ${P_A_notB} = ${P_A_val}$$

b) ${ans_b}. Sử dụng công thức Bayes: $$P(\overline{B}|A) = \dfrac{P(\overline{B} \cap A)}{P(A)} = \dfrac{P(\overline{B}) \cdot P(A|\overline{B})}{P(A)}$$

$$P(\overline{B}|A) = \dfrac{${P_notB} \cdot ${P_A_notB}}{${P_A_val}} \approx ${P_notB_A_pct}$$

c) ${ans_c}. Gọi $$M$$ là biến cố "${sol_M_label}". Theo đề: $$n(M) = ${N_M}$$ người.
Số ${subject} thực sự ${action_positive} và thuộc nhóm ${group_M} là: $$n(A \cap M) = ${N_A_M}$$ người.
Số ${subject} thuộc nhóm ${group_M} nhưng thực sự ${action_negative} là: $$n(\overline{A} \cap M) = ${N_M} - ${N_A_M} = ${N_notA_M}$$ người.
Tỉ lệ ${group_M} nhưng thực sự ${action_negative} là: $$\dfrac{n(\overline{A} \cap M)}{n(M)} = \dfrac{${N_notA_M}}{${N_M}} = ${P_notA_M_pct}$$

d) ${ans_d}. Ta có: $$E$$ là biến cố "Trả lời sai sự thật". Theo đề: $$P(E|M) = ${P_E_M_pct} = ${P_E_M}$$.
Suy ra xác suất trả lời đúng trong nhóm ${group_M} là: $$P(\overline{E}|M) = 1 - ${P_E_M} = ${P_notE_M}$$.

Ta có $$P(M) = ${P_M} \Rightarrow P(\overline{M}) = ${P_notM}$$. Mà $$P(\overline{E}|M) = ${P_notE_M} = \dfrac{P(\overline{E}M)}{P(M)} \Rightarrow P(\overline{E}M) = ${P_notE_M_and_M}$$

Lại có: $$P(E) = P(\overline{A}B) + P(A\overline{B}) = ${P_E_val}$$
$$\Rightarrow P(\overline{E}) = P(AB) + P(\overline{A}\overline{B}) = ${P_notE_val}$$. Mà $$P(\overline{E}) = P(\overline{E}M) + P(\overline{E}\overline{M}) = ${P_notE_val}$$
$$\Rightarrow P(\overline{E}\overline{M}) = P(\overline{E}) - P(\overline{E}M) = ${P_notE_val} - ${P_notE_M_and_M} = ${P_notE_notM_val}$$

$$\Rightarrow P(\overline{E}|\overline{M}) = \dfrac{P(\overline{E}\overline{M})}{P(\overline{M})} = \dfrac{${P_notE_notM_val}}{${P_notM}} = ${P_notE_given_notM_pct}$$
""")


# ==============================================================================
# HÀM UTILS
# ==============================================================================

def format_percentage(val: float, decimals: int = 2) -> str:
    perc = val * 100
    if perc == int(perc):
        return f"{int(perc)}\\%"
    formatted = f"{perc:.{decimals}f}".rstrip('0').rstrip('.')
    return formatted.replace(".", ",") + "\\%"

def format_decimal_vn(val: float, decimals: int = 4) -> str:
    s = f"{val:.{decimals}f}".rstrip('0').rstrip('.')
    if s == "": s = "0"
    return s.replace(".", ",")


# ==============================================================================
# GENERATOR
# ==============================================================================

class MultiContextProbabilityQuestion:
    def generate_parameters(self) -> Dict[str, Any]:
        attempts = 0
        while attempts < 1000:
            attempts += 1
            N = random.choice([100, 200, 500])
            N_M = random.choice([int(N * 0.1), int(N * 0.2), int(N * 0.25), int(N * 0.3)])
            N_B = random.choice([int(N * 0.6), int(N * 0.7), int(N * 0.75), int(N * 0.8)])
            N_notB = N - N_B

            P_A_B_pct = random.choice([70, 75, 80, 85, 90])
            P_A_notB_pct = random.choice([10, 15, 20, 25, 30])
            P_A_B = P_A_B_pct / 100
            P_A_notB = P_A_notB_pct / 100

            N_A_M = random.randint(int(N_M * 0.4), int(N_M * 0.8))
            N_notA_M = N_M - N_A_M

            P_E_M_pct = random.choice([10, 15, 20, 25, 30])
            P_E_M = P_E_M_pct / 100

            P_B = N_B / N
            P_notB = N_notB / N
            P_A = P_B * P_A_B + P_notB * P_A_notB

            if P_A == 0: continue
            P_notB_A = (P_notB * P_A_notB) / P_A
            P_notA_M_val = N_notA_M / N_M

            P_notE_M = 1 - P_E_M
            P_M = N_M / N
            P_notM = 1 - P_M
            P_notE_M_and_M = P_notE_M * P_M

            P_notA_B = P_B * (1 - P_A_B)
            P_A_notB_joint = P_notB * P_A_notB

            P_E = P_notA_B + P_A_notB_joint
            P_notE = 1 - P_E
            P_notE_notM_val = P_notE - P_notE_M_and_M

            if P_notE_notM_val < 0 or P_notM == 0:
                continue

            P_notE_given_notM = P_notE_notM_val / P_notM
            if P_notE_given_notM < 0 or P_notE_given_notM > 1:
                continue

            return {
                "N": N, "N_M": N_M, "N_B": N_B, "N_notB": N_notB,
                "P_A_B_pct": P_A_B_pct, "P_A_notB_pct": P_A_notB_pct,
                "P_A_B": P_A_B, "P_A_notB": P_A_notB,
                "P_B": P_B, "P_notB": P_notB,
                "N_A_M": N_A_M, "N_notA_M": N_notA_M,
                "P_E_M_pct": P_E_M_pct, "P_E_M": P_E_M,
                "P_A": P_A,
                "P_notB_A": P_notB_A,
                "P_notA_M_val": P_notA_M_val,
                "P_notE_M": P_notE_M,
                "P_M": P_M, "P_notM": P_notM,
                "P_notE_M_and_M": P_notE_M_and_M,
                "P_E": P_E, "P_notE": P_notE,
                "P_notE_notM_val": P_notE_notM_val,
                "P_notE_given_notM": P_notE_given_notM,
            }
        raise ValueError("Could not find valid parameters")

    def generate(self, q_num: int) -> Tuple[str, str]:
        ctx = random.choice(CONTEXTS)
        p = self.generate_parameters()
        TF = [random.choice([True, False]) for _ in range(4)]

        # Render intro
        intro_text = ctx["intro"].substitute(
            N=p['N'], N_M=p['N_M'], N_B=p['N_B'], N_notB=p['N_notB'],
            P_A_B_pct=f"${p['P_A_B_pct']}\\%$",
            P_A_notB_pct=f"${p['P_A_notB_pct']}\\%$",
        )

        # Định nghĩa biến cố
        events_text = (
            f"Gọi $$A$$ là biến cố \"{ctx['event_A']}\", "
            f"gọi $$B$$ là biến cố \"{ctx['event_B']}\"."
        )

        # a) P(A)
        val_a = p['P_A'] if TF[0] else p['P_A'] + random.choice([-0.05, 0.05, -0.1, 0.1])
        stmt_a_text = f"Tỉ lệ {ctx['subject']} thực sự sẽ {ctx['action_positive']} là ${format_percentage(val_a)}$."
        stmt_a = ("*a) " if TF[0] else "a) ") + stmt_a_text

        # b) P(notB | A)
        val_b = p['P_notB_A'] if TF[1] else p['P_notB_A'] + random.choice([-0.02, 0.02, -0.05, 0.05])
        stmt_b_text = f"Trong số {ctx['subject']} thực sự sẽ {ctx['action_positive']} có ${format_percentage(val_b)}$ người trả lời {ctx['reply_negative']} khi được phỏng vấn."
        stmt_b = ("*b) " if TF[1] else "b) ") + stmt_b_text

        # c) P(notA | M)
        val_c = p['P_notA_M_val'] if TF[2] else p['P_notA_M_val'] + random.choice([-0.05, 0.05])
        stmt_c_text = f"Trong số những {ctx['group_M']} có ${format_percentage(val_c)}$ {ctx['subject']} thực sự sẽ {ctx['action_negative']} biết rằng số {ctx['subject']} thực sự sẽ {ctx['action_positive']} và thuộc nhóm {ctx['group_M']} là {p['N_A_M']} người."
        stmt_c = ("*c) " if TF[2] else "c) ") + stmt_c_text

        # d) P(notE | notM)
        val_d = p['P_notE_given_notM'] if TF[3] else p['P_notE_given_notM'] + random.choice([-0.01, 0.01, -0.05, 0.05])
        stmt_d_text = (
            f"Gọi $E$ là biến cố \"Người trả lời sai sự thật\" "
            f"(tức là trả lời phỏng vấn là có và thực tế lại không {ctx['action_positive']} và ngược lại). "
            f"Biết rằng trong nhóm {ctx['group_M']}, xác suất để xảy ra biến cố $E$ là ${p['P_E_M_pct']}\\%$. "
            f"Xác suất để một người trả lời đúng sự thật trong những người {ctx['group_notM']} là ${format_percentage(val_d)}$."
        )
        stmt_d = ("*d) " if TF[3] else "d) ") + stmt_d_text

        # Ghép đề bài
        question_text = f"{intro_text} {events_text}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"

        # Lời giải
        ans_labels = ["Đúng" if tf else "Sai" for tf in TF]

        solution_text = TEMPLATE_SOLUTION.substitute(
            ans_a=ans_labels[0], ans_b=ans_labels[1], ans_c=ans_labels[2], ans_d=ans_labels[3],
            subject=ctx["subject"],
            action_positive=ctx["action_positive"],
            action_negative=ctx["action_negative"],
            group_M=ctx["group_M"],
            group_notM=ctx["group_notM"],
            sol_M_label=ctx["sol_M_label"],
            P_B=format_decimal_vn(p['P_B']),
            P_A_B=format_decimal_vn(p['P_A_B']),
            P_notB=format_decimal_vn(p['P_notB']),
            P_A_notB=format_decimal_vn(p['P_A_notB']),
            P_A_val=format_decimal_vn(p['P_A']),
            P_notB_A_pct=format_percentage(p['P_notB_A']),
            N_M=p['N_M'], N_A_M=p['N_A_M'], N_notA_M=p['N_notA_M'],
            P_notA_M_pct=format_percentage(p['P_notA_M_val']),
            P_E_M_pct=p['P_E_M_pct'], P_E_M=format_decimal_vn(p['P_E_M']),
            P_notE_M=format_decimal_vn(p['P_notE_M']),
            P_M=format_decimal_vn(p['P_M']),
            P_notM=format_decimal_vn(p['P_notM']),
            P_notE_M_and_M=format_decimal_vn(p['P_notE_M_and_M']),
            P_E_val=format_decimal_vn(p['P_E']),
            P_notE_val=format_decimal_vn(p['P_notE']),
            P_notE_notM_val=format_decimal_vn(p['P_notE_notM_val']),
            P_notE_given_notM_pct=format_percentage(p['P_notE_given_notM']),
        )

        final_str = (
            f"\\begin{{ex}}%Câu {q_num}\n"
            + question_text.strip()
            + "\n\n\\loigiai{\n"
            + solution_text.strip()
            + "\n}\n\\end{ex}"
        )

        return final_str, ""


def create_document(questions: List[Tuple[str, str]]) -> str:
    content = "\n\n".join(q for q, _ in questions)
    doc = r"""\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage[top=1.5cm, bottom=2cm, left=2cm, right=1.5cm]{geometry}
\usepackage[solcolor]{ex_test}

\begin{document}

""" + content + r"""

\end{document}
"""
    return doc


if __name__ == "__main__":
    import sys
    num_q = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else random.randint(1, 10000)
    random.seed(seed)
    logging.info(f"Generating {num_q} questions with seed {seed}")

    gen = MultiContextProbabilityQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i + 1))

    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "multi_context_probability_questions.tex")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
