import os
import random
import logging
from fractions import Fraction
from typing import Dict, Any, List, Tuple
from string import Template

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ==============================================================================
# 10 NGỮ CẢNH NÂNG CAO (Mô hình tương thích 4 nhóm)
# ==============================================================================
# Cấu trúc toán học giống blood_transfusion:
#   - group_O (base, tương thích ngược) ~ nhóm O
#   - group_A ~ nhóm A
#   - group_B ~ nhóm B
#   - group_AB (universal receiver) ~ nhóm AB
# Quy tắc: AB nhận tất cả. A/B/O chỉ nhận cùng loại hoặc O.

CONTEXTS = [
    # 1. CNTT - Đồng bộ máy chủ
    {
        "intro": Template(
            r"Trong kỷ nguyên chuyển đổi số, việc đồng bộ hóa dữ liệu giữa các trung tâm dữ liệu của một tập đoàn công nghệ đa quốc gia là thao tác bắt buộc để duy trì tính liên tục của dịch vụ và ngăn ngừa mất mát thông tin. Hiện tại, mạng lưới của tập đoàn sử dụng 4 định dạng tệp tin lưu trữ chính với tỷ lệ phân bổ không đồng đều do lịch sử sáp nhập các công ty con. Thống kê cho thấy: định dạng Type-A chiếm khoảng ${P_A_pct}, định dạng lõi thô (Raw) chiếm tới ${P_O_pct}, hệ thống siêu tương thích (Omni) chỉ chiếm ${P_AB_pct} và định dạng Type-B chiếm ${P_B_pct}. Việc chuyển giao dữ liệu được thực hiện liên tục để sao lưu dự phòng. Quá trình chuyển file được coi là thành công nếu máy chủ nhận có khả năng giải mã định dạng của máy chủ gửi. Biết rằng một máy chủ dùng hệ Omni có thể giải mã tệp tin từ bất kỳ hệ thống nào. Ngược lại, nếu máy chủ nhận dùng định dạng Type-A, Type-B hoặc Raw thì nó chỉ có thể giải mã được các tệp tin cùng định dạng với chính nó hoặc tệp tin từ máy chủ hệ Raw (do định dạng Raw là văn bản thuần túy không mã hóa)."
        ),
        "stmt_a": "Chọn ngẫu nhiên một máy chủ gửi và một máy chủ nhận, xác suất quá trình đồng bộ dữ liệu thành công là {val}$.",
        "stmt_b": "Chọn ngẫu nhiên hai máy chủ gửi và một máy chủ nhận, xác suất quá trình đồng bộ dữ liệu thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Chọn ngẫu nhiên một máy chủ gửi và một máy chủ nhận. Biết rằng quá trình đồng bộ thực hiện thành công, xác suất máy chủ nhận sử dụng định dạng Type-B là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Chọn ngẫu nhiên một máy chủ gửi và một máy chủ nhận. Biết rằng quá trình đồng bộ thực hiện thành công, xác suất máy chủ nhận sử dụng định dạng Type-A là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "máy chủ nhận",
        "sol_sender": "máy chủ gửi",
        "sol_action": "đồng bộ dữ liệu",
        "sol_group_O": "Raw",
        "sol_group_A": "Type-A",
        "sol_group_B": "Type-B",
        "sol_group_AB": "Omni",
    },
    # 2. Logistic - Cảng biển
    {
        "intro": Template(
            r"Logistics toàn cầu phụ thuộc rất lớn vào việc tối ưu hóa quy trình bốc dỡ hàng hóa tại các cảng biển lớn. Để đáp ứng nhu cầu thương mại, có 4 tiêu chuẩn thiết kế cần cẩu bốc dỡ tương ứng với các loại container chuyên dụng đang được lưu hành. Tỷ lệ phân bố các tiêu chuẩn cần cẩu tại các cảng ở khu vực Đông Nam Á như sau: Cần cẩu chuẩn Beta chiếm ${P_B_pct}, cần cẩu đa năng thế hệ mới (Super) chiếm ${P_AB_pct}, cần cẩu chuẩn phổ thông (Standard) chiếm ${P_O_pct} và cần cẩu chuẩn Alpha chiếm ${P_A_pct}. Quá trình cập cảng yêu cầu cẩu phải tương thích với chốt của container để tiến hành bốc dỡ an toàn, giảm thiểu rủi ro đứt gãy cáp neo. Biết rằng cảng sở hữu cần cẩu Super có thể bốc dỡ bất kỳ loại hình container nào cập bến. Tuy nhiên, nếu cảng dùng cần cẩu Alpha, Beta hoặc Standard thì cảng đó chỉ có thể bốc dỡ được container cùng tiêu chuẩn thiết kế với mình hoặc container loại Standard."
        ),
        "stmt_a": "Lấy ngẫu nhiên một chuyến tàu chở container và một cảng biển tiếp nhận, xác suất bốc dỡ thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai chuyến tàu chở container và một cảng biển tiếp nhận, xác suất bốc dỡ thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một chuyến tàu chở container và một cảng biển tiếp nhận. Biết rằng quá trình bốc dỡ thực hiện thành công, xác suất cảng nhận dùng chuẩn Beta là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một chuyến tàu chở container và một cảng biển tiếp nhận. Biết rằng quá trình bốc dỡ thực hiện thành công, xác suất cảng nhận dùng chuẩn Alpha là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "cảng tiếp nhận",
        "sol_sender": "chuyến tàu",
        "sol_action": "bốc dỡ",
        "sol_group_O": "Standard",
        "sol_group_A": "Alpha",
        "sol_group_B": "Beta",
        "sol_group_AB": "Super",
    },
    # 3. Xe điện - Trạm sạc EV
    {
        "intro": Template(
            r"Trong nỗ lực giảm thiểu khí thải nhà kính, thị trường xe điện (EV) đang bùng nổ với nhiều chuẩn sạc khác nhau, gây ra tình trạng phân mảnh hạ tầng lưới điện. Tại một thành phố lớn, mạng lưới phương tiện sử dụng 4 chuẩn sạc chính. Theo báo cáo thường niên, xe sử dụng chuẩn Base (cơ bản) chiếm ${P_O_pct}, xe chuẩn X-Class chiếm ${P_A_pct}, xe dùng chuẩn Y-Class chiếm ${P_B_pct} và xe thuộc dòng Hybrid-Max (hỗ trợ sạc vạn năng) chiếm ${P_AB_pct}. Việc kết nối sạc giữa trụ cấp điện và phương tiện là yếu tố cốt lõi để duy trì hoạt động giao thông đô thị mà chưa có giải pháp thay thế pin đồng bộ. Quá trình sạc điện thành công khi hệ thống quản lý pin của xe nhận diện được giao thức của trụ sạc. Một chiếc xe dòng Hybrid-Max có thể cắm sạc ở bất kỳ trụ điện nào. Nhưng nếu xe thuộc dòng X-Class, Y-Class hoặc Base thì chỉ có thể sạc được tại trụ có cùng chuẩn giao thức với mình, hoặc sạc ở các trụ công cộng chuẩn Base."
        ),
        "stmt_a": "Lấy ngẫu nhiên một trụ sạc và một chiếc xe điện cần sạc, xác suất sạc điện thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai trụ sạc và một chiếc xe điện cần sạc, xác suất sạc điện thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một trụ sạc và một chiếc xe điện. Biết rằng quá trình kết nối sạc thực hiện thành công, xác suất chiếc xe thuộc dòng Y-Class là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một trụ sạc và một chiếc xe điện. Biết rằng quá trình kết nối sạc thực hiện thành công, xác suất chiếc xe thuộc dòng X-Class là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "xe điện",
        "sol_sender": "trụ sạc",
        "sol_action": "sạc điện",
        "sol_group_O": "Base",
        "sol_group_A": "X-Class",
        "sol_group_B": "Y-Class",
        "sol_group_AB": "Hybrid-Max",
    },
    # 4. Nông nghiệp - Ghép cành
    {
        "intro": Template(
            r"Nhằm đối phó với biến đổi khí hậu gây ra hạn hán kéo dài, các viện nghiên cứu nông nghiệp đang tiến hành lai ghép các giống cây ăn quả để tăng sức chống chịu. Bộ gen của các loại cây trong khu vực thực nghiệm được chia làm 4 nhóm chính. Số liệu thống kê sinh học cho thấy: Giống cây đột biến bậc cao (Gen-Z) chiếm ${P_AB_pct}, giống cây bản địa (Gen-Cơ bản) chiếm tới ${P_O_pct}, giống cây chịu mặn (Gen-M) chiếm ${P_B_pct} và giống cây chịu nhiệt (Gen-N) chiếm ${P_A_pct}. Kỹ thuật ghép cành là phương pháp nhân giống vô tính phổ biến nhất để truyền tính trạng tốt sang gốc ghép mới nhằm cứu sống các vườn ươm đang suy thoái. Việc ghép cành phụ thuộc hoàn toàn vào độ tương thích màng tế bào. Biết rằng một gốc ghép thuộc Gen-Z có thể tiếp nhận cành ghép từ bất kỳ giống cây nào. Trong khi đó, nếu gốc ghép thuộc Gen-M, Gen-N hoặc Gen-Cơ bản thì nó chỉ có thể dung hợp được với cành ghép cùng bộ gen với mình, hoặc cành ghép từ giống Gen-Cơ bản (do tính trạng bản địa dễ thích nghi)."
        ),
        "stmt_a": "Chọn ngẫu nhiên một cành ghép (cho) và một gốc ghép (nhận), xác suất dung hợp thành công là {val}$.",
        "stmt_b": "Chọn ngẫu nhiên hai cành ghép và một gốc ghép, xác suất dung hợp thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Chọn ngẫu nhiên một cành ghép và một gốc ghép. Biết rằng quá trình dung hợp thành công, xác suất gốc ghép thuộc Gen-M là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Chọn ngẫu nhiên một cành ghép và một gốc ghép. Biết rằng quá trình dung hợp thành công, xác suất gốc ghép thuộc Gen-N là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "gốc ghép",
        "sol_sender": "cành ghép",
        "sol_action": "dung hợp",
        "sol_group_O": "Gen-Cơ bản",
        "sol_group_A": "Gen-N",
        "sol_group_B": "Gen-M",
        "sol_group_AB": "Gen-Z",
    },
    # 5. Sản xuất Điện tử - Lắp ráp Bo mạch
    {
        "intro": Template(
            r"Quy trình chế tạo thiết bị điện tử gia dụng tại các nhà máy tự động hóa đòi hỏi sự đồng bộ khắt khe giữa vi mạch (chip) và bảng mạch chủ (motherboard). Do tình trạng thiếu hụt bán dẫn toàn cầu, nhà máy phải luân phiên sử dụng 4 thế hệ bảng mạch khác nhau. Quản lý kho vật tư ghi nhận: Bảng mạch Series-A chiếm ${P_A_pct}, bảng mạch cao cấp Ultra chiếm ${P_AB_pct}, bảng mạch Series-B chiếm ${P_B_pct}, và bo mạch phổ thông (Standard) chiếm ${P_O_pct}. Công đoạn đóng gói linh kiện là khâu quyết định, nơi vi mạch được hàn lên bo mạch để tạo thành thiết bị hoàn chỉnh. Nếu chân tiếp xúc không khớp, sản phẩm sẽ bị loại bỏ ngay tại xưởng. Theo thông số kỹ thuật, bảng mạch Ultra được trang bị khe cắm đa nhiệm nên tiếp nhận được mọi loại vi mạch. Tuy nhiên, nếu dùng bảng mạch Series-A, Series-B hoặc Standard thì dây chuyền chỉ có thể lắp được vi mạch tương ứng cùng Series, hoặc dùng chung dòng vi mạch Standard cơ sở."
        ),
        "stmt_a": "Chọn ngẫu nhiên một vi mạch và một bảng mạch, xác suất dây chuyền lắp ráp thành công là {val}$.",
        "stmt_b": "Chọn ngẫu nhiên hai vi mạch và một bảng mạch, xác suất dây chuyền lắp ráp thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Chọn ngẫu nhiên một vi mạch và một bảng mạch. Biết rằng quá trình lắp ráp thành công, xác suất bảng mạch thuộc Series-B là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Chọn ngẫu nhiên một vi mạch và một bảng mạch. Biết rằng quá trình lắp ráp thành công, xác suất bảng mạch thuộc Series-A là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "bảng mạch",
        "sol_sender": "vi mạch",
        "sol_action": "lắp ráp",
        "sol_group_O": "Standard",
        "sol_group_A": "Series-A",
        "sol_group_B": "Series-B",
        "sol_group_AB": "Ultra",
    },
    # 6. Streaming - Bản quyền
    {
        "intro": Template(
            r"Các nền tảng phát video trực tuyến (Streaming) thường xuyên áp dụng hệ thống Quản lý bản quyền kỹ thuật số (DRM) để kiểm soát việc phân phối nội dung tới người dùng cuối. Hệ thống chia người dùng thành 4 cấp độ tài khoản với quyền truy cập các luồng dữ liệu khác nhau. Theo báo cáo kinh doanh quý III, người dùng Gói Premium (đặc quyền cao nhất) chiếm ${P_AB_pct}, Gói Thể thao chiếm ${P_B_pct}, Gói Phim ảnh chiếm ${P_A_pct} và người dùng Gói Miễn phí (Free) chiếm lượng lớn nhất với ${P_O_pct}. Việc máy chủ đẩy luồng video đến thiết bị người dùng là một tác vụ liên tục tiêu tốn nhiều băng thông. Trình phát video trên thiết bị phải giải mã được luồng dữ liệu thì hình ảnh mới được hiển thị. Trình phát của tài khoản Premium có thể giải mã và xem được nội dung từ bất kỳ gói nào. Nhưng nếu người dùng sở hữu tài khoản Gói Phim ảnh, Gói Thể thao hoặc Gói Free thì thiết bị chỉ có thể phát được nội dung gốc của gói đó, hoặc các nội dung được gắn cờ Free."
        ),
        "stmt_a": "Lấy ngẫu nhiên một luồng nội dung được phát và một thiết bị nhận tín hiệu, xác suất thiết bị phát video thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai luồng nội dung được phát và một thiết bị nhận tín hiệu, xác suất thiết bị phát video thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một luồng nội dung và một thiết bị nhận. Biết rằng trình phát hiển thị video thành công, xác suất thiết bị đang dùng Gói Thể thao là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một luồng nội dung và một thiết bị nhận. Biết rằng trình phát hiển thị video thành công, xác suất thiết bị đang dùng Gói Phim ảnh là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "thiết bị nhận",
        "sol_sender": "luồng nội dung",
        "sol_action": "phát video",
        "sol_group_O": "Gói Free",
        "sol_group_A": "Gói Phim ảnh",
        "sol_group_B": "Gói Thể thao",
        "sol_group_AB": "Gói Premium",
    },
    # 7. Nhà hàng - Chế độ ăn kiêng
    {
        "intro": Template(
            r"Trong ngành dịch vụ tổ chức sự kiện và tiệc cưới, việc đáp ứng các yêu cầu về chế độ dinh dưỡng (Dietary restrictions) của khách mời là thử thách lớn nhất đối với các đầu bếp. Tại một trung tâm hội nghị quốc tế, hệ thống bếp chuẩn bị 4 loại thực đơn chính để phục vụ đa dạng thực khách. Phân tích dữ liệu đặt tiệc cho thấy: Khách yêu cầu thực đơn không Lactose (Dairy-Free) chiếm ${P_B_pct}, khách ăn thực đơn thuần chay (Vegan) chiếm ${P_O_pct}, khách ăn uống tự do không kiêng cữ (Omnivore) chiếm ${P_AB_pct}, và khách ăn thực đơn không Gluten (Gluten-Free) chiếm ${P_A_pct}. Việc phân phối suất ăn từ nhà bếp đến bàn tiệc phải được kiểm soát gắt gao để tránh nguy cơ sốc phản vệ hoặc vi phạm đức tin tôn giáo. Biết rằng một vị khách thuộc nhóm Omnivore có thể tiêu thụ bất kỳ suất ăn nào mang ra. Ngược lại, nếu khách thuộc nhóm Gluten-Free, Dairy-Free hoặc Vegan thì họ chỉ có thể dùng bữa nếu nhận đúng suất ăn đặc chế của nhóm mình, hoặc có thể dùng chung các suất ăn Vegan (do đồ thuần chay được coi là an toàn cơ bản nhất)."
        ),
        "stmt_a": "Chọn ngẫu nhiên một suất ăn mang ra và một vị khách, xác suất vị khách có thể dùng bữa an toàn là {val}$.",
        "stmt_b": "Chọn ngẫu nhiên hai suất ăn mang ra và một vị khách, xác suất vị khách có thể dùng bữa an toàn với cả 2 suất là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Chọn ngẫu nhiên một suất ăn và một vị khách. Biết rằng vị khách đã dùng bữa an toàn, xác suất vị khách đó thuộc nhóm Dairy-Free là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Chọn ngẫu nhiên một suất ăn và một vị khách. Biết rằng vị khách đã dùng bữa an toàn, xác suất vị khách đó thuộc nhóm Gluten-Free là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "vị khách",
        "sol_sender": "suất ăn",
        "sol_action": "dùng bữa an toàn",
        "sol_group_O": "Vegan",
        "sol_group_A": "Gluten-Free",
        "sol_group_B": "Dairy-Free",
        "sol_group_AB": "Omnivore",
    },
    # 8. Quân sự - Khí tài đạn dược
    {
        "intro": Template(
            r"Hậu cần quân đội luôn đặt ưu tiên hàng đầu vào khả năng tương thích của đạn pháo giữa các đơn vị binh chủng khác nhau để đảm bảo hỏa lực yểm trợ trong các chiến dịch quy mô lớn. Một sư đoàn pháo binh hiện đang biên chế 4 loại tổ hợp hỏa lực. Kiểm kê quân số cho thấy: Pháo cỡ nòng 105mm chiếm ${P_B_pct}, tổ hợp pháo điện từ thế hệ mới chiếm ${P_AB_pct}, pháo cỡ nòng 155mm chiếm ${P_A_pct}, và các khẩu cối cơ sở (Base-Mortar) chiếm đa số với ${P_O_pct}. Việc tiếp tế đạn dược trên chiến trường là khâu sống còn, quyết định trực tiếp đến sự sinh tồn của bộ binh tuyến đầu. Khẩu đội pháo phải nhận đúng loại đạn tương thích với rãnh khương tuyến để khai hỏa thành công. Biết rằng tổ hợp pháo điện từ thế hệ mới được thiết kế với buồng nòng linh hoạt nên có thể nạp và bắn bất kỳ loại đạn nào. Tuy nhiên, nếu là pháo 155mm, 105mm hoặc cối cơ sở thì chỉ có thể bắn được đạn đúng chuẩn kích cỡ của mình, hoặc sử dụng loại đạn cối cơ sở (do đây là chuẩn đạn rời không vỏ bọc tương thích ngược)."
        ),
        "stmt_a": "Lấy ngẫu nhiên một lô đạn tiếp tế và một khẩu đội pháo, xác suất tiếp tế và khai hỏa thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai lô đạn tiếp tế và một khẩu đội pháo, xác suất tiếp tế và khai hỏa thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một lô đạn và một khẩu đội pháo. Biết rằng việc nạp đạn và khai hỏa thành công, xác suất khẩu đội pháo đang dùng cỡ nòng 105mm là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một lô đạn và một khẩu đội pháo. Biết rằng việc nạp đạn và khai hỏa thành công, xác suất khẩu đội pháo đang dùng cỡ nòng 155mm là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "khẩu đội pháo",
        "sol_sender": "lô đạn tiếp tế",
        "sol_action": "khai hỏa",
        "sol_group_O": "Base-Mortar",
        "sol_group_A": "155mm",
        "sol_group_B": "105mm",
        "sol_group_AB": "Pháo điện từ",
    },
    # 9. Viễn tưởng - Cấy ghép mô
    {
        "intro": Template(
            r"Tại một trạm xá liên hành tinh trong tương lai, các bác sĩ thú y vũ trụ thường xuyên phải xử lý các ca chấn thương phức tạp đòi hỏi phải cấy ghép mô nhân tạo để tái tạo chi bị đứt lìa cho các loài sinh vật khác nhau. Có 4 chủng tộc sinh vật ngoại lai đang sinh sống tại trạm với tỷ lệ phân bổ cụ thể: Chủng Alpha chiếm ${P_A_pct}, chủng bậc cao Omega (có hệ miễn dịch siêu cấp) chiếm ${P_AB_pct}, chủng nguyên thủy (Basic) chiếm tới ${P_O_pct} và chủng Beta chiếm ${P_B_pct}. Thao tác cấy ghép sinh học được thực hiện bằng robot vi phẫu nhằm cứu sống bệnh nhân mất máu cấp tính. Việc phẫu thuật thành công phụ thuộc vào việc hệ miễn dịch của sinh vật nhận không đào thải mô ghép từ cá thể cho. Biết rằng một bệnh nhân thuộc chủng Omega có thể tiếp nhận mô ghép từ bất kỳ chủng tộc nào. Nếu bệnh nhân thuộc chủng Alpha, Beta hoặc Basic thì hệ miễn dịch của chúng chỉ chấp nhận mô cấy từ đồng loại của mình, hoặc mô cấy sinh học từ chủng Basic (do cấu trúc tế bào gốc nguyên thủy)."
        ),
        "stmt_a": "Lấy ngẫu nhiên một cá thể hiến mô và một bệnh nhân nhận mô, xác suất phẫu thuật cấy ghép thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai cá thể hiến mô và một bệnh nhân nhận mô, xác suất phẫu thuật cấy ghép thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một cá thể hiến mô và một bệnh nhân nhận. Biết rằng ca phẫu thuật không xảy ra phản ứng đào thải (thành công), xác suất bệnh nhân thuộc chủng Beta là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một cá thể hiến mô và một bệnh nhân nhận. Biết rằng ca phẫu thuật không xảy ra phản ứng đào thải (thành công), xác suất bệnh nhân thuộc chủng Alpha là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "bệnh nhân",
        "sol_sender": "cá thể hiến mô",
        "sol_action": "cấy ghép",
        "sol_group_O": "Basic",
        "sol_group_A": "Alpha",
        "sol_group_B": "Beta",
        "sol_group_AB": "Omega",
    },
    # 10. Nhân sự - Mentorship
    {
        "intro": Template(
            r"Để nâng cao năng lực cạnh tranh, một tập đoàn tài chính triển khai chương trình cố vấn (Mentorship) chéo giữa các phòng ban. Hệ thống nhân sự nội bộ phân loại nhân viên thành 4 nhóm năng lực cốt lõi. Báo cáo đánh giá cuối năm chia tỷ lệ như sau: Nhóm nhân sự Đa nhiệm (Polymath) chỉ chiếm ${P_AB_pct}, nhóm chuyên môn Kỹ thuật chiếm ${P_A_pct}, nhóm chuyên môn Kinh tế chiếm ${P_B_pct}, và nhóm Kỹ năng mềm (Soft-skills) chiếm phần lớn với ${P_O_pct}. Việc truyền đạt kiến thức từ người cố vấn (Mentor) sang người được cố vấn (Mentee) là hoạt động bắt buộc trong quý, giúp thu hẹp khoảng cách thế hệ và giải quyết các bài toán đình trệ dự án. Hoạt động cố vấn được đánh giá là thành công khi người học hiểu và áp dụng được các chỉ dẫn của người dạy. Biết rằng một nhân viên thuộc nhóm Đa nhiệm có khả năng tư duy linh hoạt nên có thể học hỏi từ bất kỳ Mentor nào. Nếu nhân viên thuộc nhóm Kỹ thuật, Kinh tế hoặc Kỹ năng mềm thì họ chỉ có thể lĩnh hội được kiến thức nếu Mentor thuộc cùng nhóm chuyên môn với mình, hoặc Mentor đến từ nhóm Kỹ năng mềm (do phương pháp sư phạm dễ tiếp cận)."
        ),
        "stmt_a": "Lấy ngẫu nhiên một Mentor và một Mentee, xác suất chương trình cố vấn diễn ra thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai Mentor và một Mentee, xác suất chương trình cố vấn diễn ra thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một Mentor và một Mentee. Biết rằng hoạt động cố vấn đã thành công, xác suất Mentee thuộc nhóm chuyên môn Kinh tế là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một Mentor và một Mentee. Biết rằng hoạt động cố vấn đã thành công, xác suất Mentee thuộc nhóm chuyên môn Kỹ thuật là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "Mentee",
        "sol_sender": "Mentor",
        "sol_action": "cố vấn",
        "sol_group_O": "Kỹ năng mềm",
        "sol_group_A": "Kỹ thuật",
        "sol_group_B": "Kinh tế",
        "sol_group_AB": "Đa nhiệm",
    },
    # 11. Y tế - Truyền máu ABO
    {
        "intro": Template(
            r"Hệ nhóm máu $$ABO$$ gồm 4 nhóm máu là $$A, B, O$$ và $$AB$$ với tỷ lệ phân bố trong cộng đồng khác nhau ở từng chủng tộc. Ở Việt Nam, tỷ lệ này là: nhóm $$A$$ khoảng ${P_A_pct}, nhóm $$B$$ khoảng ${P_B_pct}, nhóm $$O$$ khoảng ${P_O_pct} và nhóm $$AB$$ khoảng ${P_AB_pct}. Truyền máu là một thao tác rất phổ biến trong y học nhằm cứu sống những bệnh nhân đang bị mất máu cấp tính và có khả năng bị nguy hiểm đến tính mạng. Việc truyền máu được thực hiện để giúp bệnh nhân có được sự bù đắp cho lượng máu đã mất và điều chỉnh những bất thường trong máu mà không thể sử dụng cách thức nào khác để thay thế được. Biết rằng một người có nhóm máu $$AB$$ có thể nhận máu của bất kỳ nhóm máu nào. Nếu người đó có nhóm máu $$A, B$$ hoặc $$O$$ thì chỉ có thể nhận được máu của người cùng nhóm máu với mình hoặc người có nhóm máu $$O$$."
        ),
        "stmt_a": "Lấy ngẫu nhiên một người cho máu và một người nhận máu, xác suất truyền máu thành công là {val}$.",
        "stmt_b": "Lấy ngẫu nhiên hai người cho máu và một người nhận máu, xác suất truyền máu thành công là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_c": "Lấy ngẫu nhiên một người cho máu và một người nhận máu. Biết rằng quá trình truyền máu thực hiện thành công, xác suất người nhận máu thuộc nhóm máu $$B$$ là {val}$ (làm tròn đến hàng đơn vị).",
        "stmt_d": "Lấy ngẫu nhiên một người cho máu và một người nhận máu. Biết rằng quá trình truyền máu thực hiện thành công, xác suất người nhận máu thuộc nhóm máu $$A$$ là {val}$ (làm tròn đến hàng đơn vị).",
        "sol_receiver": "người nhận máu",
        "sol_sender": "người cho máu",
        "sol_action": "truyền máu",
        "sol_group_O": "nhóm O",
        "sol_group_A": "nhóm A",
        "sol_group_B": "nhóm B",
        "sol_group_AB": "nhóm AB",
    },
]


# ==============================================================================
# TEMPLATE LỜI GIẢI (Tổng quát cho mô hình 4 nhóm tương thích)
# ==============================================================================
TEMPLATE_SOLUTION = Template(r"""
Lời giải

Gọi các biến cố ${sol_receiver} thuộc nhóm ${sol_group_O}, ${sol_group_A}, ${sol_group_B}, ${sol_group_AB} lần lượt là $$O, A, B, AB$$.
Gọi $$X$$ là biến cố ${sol_action} thành công.

a) ${ans_a}. Ta có $$P(X) = P(O) \cdot P(X|O) + P(A) \cdot P(X|A) + P(B) \cdot P(X|B) + P(AB) \cdot P(X|AB)$$
* ${sol_receiver} nhóm ${sol_group_O} chỉ nhận ${sol_sender} cùng nhóm nên $$P(X|O) = ${P_O}$$.
* ${sol_receiver} nhóm ${sol_group_A} nhận ${sol_sender} cùng nhóm hoặc nhóm ${sol_group_O} nên $$P(X|A) = ${P_A} + ${P_O} = ${P_X_A}$$.
* ${sol_receiver} nhóm ${sol_group_B} nhận ${sol_sender} cùng nhóm hoặc nhóm ${sol_group_O} nên $$P(X|B) = ${P_B} + ${P_O} = ${P_X_B}$$.
* ${sol_receiver} nhóm ${sol_group_AB} nhận ${sol_sender} từ bất kỳ nhóm nào nên $$P(X|AB) = 1$$.
Vậy $$P(X) = ${P_O} \times ${P_O} + ${P_A} \times ${P_X_A} + ${P_B} \times ${P_X_B} + ${P_AB} \times 1 = ${P_X1_val} = ${P_X1_pct}$$.

b) ${ans_b}.
* $$P(X_2|O) = ${P_O}^2 = ${P_X2_O}$$
* $$P(X_2|A) = (${P_A} + ${P_O})^2 = ${P_X2_A}$$
* $$P(X_2|B) = (${P_B} + ${P_O})^2 = ${P_X2_B}$$
* $$P(X_2|AB) = 1$$
Vậy: $$P(X_2) = ${P_O} \times ${P_X2_O} + ${P_A} \times ${P_X2_A} + ${P_B} \times ${P_X2_B} + ${P_AB} \times 1 = ${P_X2_val} \approx ${P_X2_pct_round}$$.

c) ${ans_c}. $$P(B|X) = \dfrac{P(B) \cdot P(X|B)}{P(X)} = \dfrac{${P_B} \times ${P_X_B}}{${P_X1_val}} = ${P_B_X1_frac} \approx ${P_B_X1_pct_round}$$.

d) ${ans_d}. $$P(A|X) = \dfrac{P(A) \cdot P(X|A)}{P(X)} = \dfrac{${P_A} \times ${P_X_A}}{${P_X1_val}} = ${P_A_X1_frac} \approx ${P_A_X1_pct_round}$$.
""")


# ==============================================================================
# UTILS
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

def format_fraction(val: Fraction) -> str:
    r"""Chuyển Fraction thành chuỗi LaTeX \dfrac"""
    if val.denominator == 1:
        return str(val.numerator)
    if val.numerator < 0:
        return rf"-\dfrac{{{abs(val.numerator)}}}{{{val.denominator}}}"
    return rf"\dfrac{{{val.numerator}}}{{{val.denominator}}}"


# ==============================================================================
# GENERATOR
# ==============================================================================

class AdvancedContextQuestion:
    def generate_parameters(self) -> Dict[str, Any]:
        attempts = 0
        while attempts < 1000:
            attempts += 1
            p_o_pct = random.randint(35, 50)
            p_a_pct = random.randint(15, 30)
            p_b_pct = random.randint(15, 35)
            p_ab_pct = 100 - p_o_pct - p_a_pct - p_b_pct

            if p_ab_pct < 2 or p_ab_pct > 15:
                continue

            P_O = Fraction(p_o_pct, 100)
            P_A = Fraction(p_a_pct, 100)
            P_B = Fraction(p_b_pct, 100)
            P_AB = Fraction(p_ab_pct, 100)

            P_X_O = P_O
            P_X_A = P_A + P_O
            P_X_B = P_B + P_O
            P_X_AB = Fraction(1, 1)

            P_X1 = P_O * P_X_O + P_A * P_X_A + P_B * P_X_B + P_AB * P_X_AB

            P_X2_O = P_X_O ** 2
            P_X2_A = P_X_A ** 2
            P_X2_B = P_X_B ** 2
            P_X2 = P_O * P_X2_O + P_A * P_X2_A + P_B * P_X2_B + P_AB

            P_B_X1 = (P_B * P_X_B) / P_X1
            P_A_X1 = (P_A * P_X_A) / P_X1

            return {
                "P_O_pct": p_o_pct, "P_A_pct": p_a_pct, "P_B_pct": p_b_pct, "P_AB_pct": p_ab_pct,
                "P_O": P_O, "P_A": P_A, "P_B": P_B, "P_AB": P_AB,
                "P_X_O": P_X_O, "P_X_A": P_X_A, "P_X_B": P_X_B,
                "P_X1": P_X1,
                "P_X2_O": P_X2_O, "P_X2_A": P_X2_A, "P_X2_B": P_X2_B,
                "P_X2": P_X2,
                "P_B_X1": P_B_X1, "P_A_X1": P_A_X1,
            }
        raise ValueError("Could not find valid parameters")

    def generate(self, q_num: int) -> Tuple[str, str]:
        ctx = random.choice(CONTEXTS)
        p = self.generate_parameters()
        TF = [random.choice([True, False]) for _ in range(4)]

        intro_text = ctx["intro"].substitute(
            P_O_pct=f"${p['P_O_pct']}\\%$",
            P_A_pct=f"${p['P_A_pct']}\\%$",
            P_B_pct=f"${p['P_B_pct']}\\%$",
            P_AB_pct=f"${p['P_AB_pct']}\\%$",
        )

        # a) P(X1)
        val_a = float(p['P_X1']) if TF[0] else float(p['P_X1']) + random.choice([-0.05, 0.05, -0.1, 0.1])
        stmt_a = ("*a) " if TF[0] else "a) ") + ctx["stmt_a"].format(val=f"${format_percentage(val_a)}")

        # b) P(X2) làm tròn hàng đơn vị
        p_x2_round = round(float(p['P_X2']) * 100)
        val_b_round = p_x2_round if TF[1] else p_x2_round + random.choice([-3, 3, -5, 5])
        stmt_b = ("*b) " if TF[1] else "b) ") + ctx["stmt_b"].format(val=f"${val_b_round}\\%")

        # c) P(B|X1) làm tròn hàng đơn vị
        p_b_x1_round = round(float(p['P_B_X1']) * 100)
        val_c_round = p_b_x1_round if TF[2] else p_b_x1_round + random.choice([-2, 2, -4, 4])
        stmt_c = ("*c) " if TF[2] else "c) ") + ctx["stmt_c"].format(val=f"${val_c_round}\\%")

        # d) P(A|X1) làm tròn 1 chữ số thập phân
        p_a_x1_val = round(float(p['P_A_X1']) * 100, 1)
        val_d = p_a_x1_val if TF[3] else p_a_x1_val + random.choice([-1.5, 1.5, -2.5, 2.5])
        val_d_str = str(val_d).replace(".", ",")
        stmt_d = ("*d) " if TF[3] else "d) ") + ctx["stmt_d"].format(val=f"${val_d_str}\\%")

        question_text = f"{intro_text}\n\n{stmt_a}\n\n{stmt_b}\n\n{stmt_c}\n\n{stmt_d}"

        ans_labels = ["Đúng" if tf else "Sai" for tf in TF]

        solution_text = TEMPLATE_SOLUTION.substitute(
            ans_a=ans_labels[0], ans_b=ans_labels[1], ans_c=ans_labels[2], ans_d=ans_labels[3],
            sol_receiver=ctx["sol_receiver"], sol_sender=ctx["sol_sender"],
            sol_action=ctx["sol_action"],
            sol_group_O=ctx["sol_group_O"], sol_group_A=ctx["sol_group_A"],
            sol_group_B=ctx["sol_group_B"], sol_group_AB=ctx["sol_group_AB"],
            P_O=format_decimal_vn(float(p['P_O'])),
            P_A=format_decimal_vn(float(p['P_A'])),
            P_B=format_decimal_vn(float(p['P_B'])),
            P_AB=format_decimal_vn(float(p['P_AB'])),
            P_X_A=format_decimal_vn(float(p['P_X_A'])),
            P_X_B=format_decimal_vn(float(p['P_X_B'])),
            P_X1_val=format_decimal_vn(float(p['P_X1'])),
            P_X1_pct=format_percentage(float(p['P_X1'])),
            P_X2_O=format_decimal_vn(float(p['P_X2_O'])),
            P_X2_A=format_decimal_vn(float(p['P_X2_A'])),
            P_X2_B=format_decimal_vn(float(p['P_X2_B'])),
            P_X2_val=format_decimal_vn(float(p['P_X2'])),
            P_X2_pct_round=f"{round(float(p['P_X2']) * 100)}\\%",
            P_B_X1_frac=format_fraction(p['P_B_X1']),
            P_B_X1_pct_round=f"{round(float(p['P_B_X1']) * 100)}\\%",
            P_A_X1_frac=format_fraction(p['P_A_X1']),
            P_A_X1_pct_round=f"{round(float(p['P_A_X1']) * 100, 1)}".replace(".", ",") + "\\%",
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

    gen = AdvancedContextQuestion()
    qs = []
    for i in range(num_q):
        qs.append(gen.generate(i + 1))

    latex_content = create_document(qs)
    out_file = os.path.join(os.path.dirname(__file__), "advanced_context_probability_questions.tex")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    logging.info(f"Saved to {out_file}")
