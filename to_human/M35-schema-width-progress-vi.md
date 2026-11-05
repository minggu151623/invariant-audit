# Tiến triển mới: khi nào sửa khóa thực sự có ích?

Ngày 05/11/2026. Đây là báo cáo nghiên cứu E013, chưa phải bản nộp arXiv.
Bản PDF R3 được giữ nguyên; kết quả dưới đây chưa nằm trong PDF đó.

## Kết quả chính

Mình đã hoàn chỉnh một chứng minh cho câu hỏi cụ thể hơn: **chỉ nhìn vào cấu
trúc các luật, ta xác định được mức lợi ích lớn nhất mà việc cho sửa khóa có
thể mang lại hay không?** Trong mô hình đang nghiên cứu, câu trả lời là có.

Gọi chi phí cố định khóa là số ô ít nhất phải sửa khi chỉ được sửa cột giá
trị đang xét. Chi phí cho sửa khóa còn cho phép sửa các cột dùng để gom nhóm.
Ở đây ta muốn chuyển một dòng đang bị từ chối thành được tất cả luật chấp nhận;
không được sửa chính dòng đó. Mỗi ô sửa có giá một đơn vị.

Kết quả là:

    chi phí cho sửa khóa ≤ chi phí cố định khóa
                        ≤ w × chi phí cho sửa khóa.

Số w chỉ phụ thuộc cấu trúc các luật. Để hiểu nó, chọn một cột khóa, lấy các
luật chứa cột đó, rồi tìm nhiều nhất bao nhiêu bộ khóa mà không bộ nào chứa
trọn bộ khác. Làm với mọi cột; số lớn nhất thu được chính là w.

Không chỉ có cận trên: với **mỗi bộ luật**, chứng minh còn xây được một bảng
nhị phân đạt đúng tỉ lệ w. Vì vậy w mô tả mức lợi ích tối đa thực sự có thể xảy
ra trong mô hình, chứ không phải một giới hạn rất rộng không bao giờ đạt tới.

## Ví dụ: một lần sửa khóa thay cho hai lần sửa giá trị

Hai luật dùng bộ khóa {a,b} và {a,c}. Chúng chung a nhưng không bộ nào chứa
bộ kia, nên w=2.

| Dòng | a | b | c | Giá trị y |
|---|---:|---:|---:|---:|
| Dòng được bảo vệ | 0 | 0 | 0 | 0 |
| Dòng thứ nhất | 0 | 0 | 1 | 1 |
| Dòng thứ hai | 0 | 1 | 0 | 1 |
| Dòng hỗ trợ | 1 | 0 | 0 | 0 |

Luật {a,b} nhìn dòng được bảo vệ và dòng thứ nhất: hòa 0 với 1. Luật {a,c}
nhìn dòng được bảo vệ và dòng thứ hai: cũng hòa. Hòa bị từ chối.

Nếu chỉ sửa y, phải sửa y của cả hai dòng có giá trị 1: tốn **hai ô**.
Nếu được sửa khóa, đổi a của dòng hỗ trợ từ 1 thành 0: dòng ấy gia nhập cả hai
nhóm, khiến mỗi nhóm có hai phiếu 0 và một phiếu 1. Chỉ tốn **một ô**.

Ngược lại, với các bộ khóa lồng nhau như {a} và {a,b}, hoặc không giao nhau
như {a} và {b}, w=1. Nếu toàn bộ họ luật có tính chất “giao nhau thì lồng
nhau”, hai chi phí luôn bằng nhau trên mọi bảng. Nếu có một cặp giao nhau mà
không lồng nhau, sẽ tồn tại bảng có lợi ích nghiêm ngặt từ sửa khóa.

Điều này **không** nói mọi bảng với w>1 đều có lợi ích, hoặc w=1 thì tìm đáp
án dễ. Kết quả NP-complete trước đây vẫn đúng khi có nhiều luật khóa đơn,
dù những luật đó có w=1. Việc loại được biến sửa khóa có thể giúp mô hình gọn
hơn, nhưng mình chưa đo tốc độ chạy để khẳng định mức tăng tốc.

## Vì sao điều này giải thích thí nghiệm cũ?

Cả chín cấu hình E011 trên Beers, Flights và Rayyan đều dùng bộ khóa đơn.
Do đó chúng có w=1. Định lý giải thích rằng hai chi phí phải bằng nhau cho
**toàn bộ 4.972 trường hợp bị từ chối** trong thống kê cũ. Đây là kết luận về
sự bằng nhau; mình chưa tính giá trị tối ưu cụ thể cho cả 4.972 trường hợp.

Điều này cũng chỉ ra một sai sót trong kỳ vọng nghiên cứu trước: dự đoán sẽ
tìm được trường hợp giảm chi phí ở chiều chấp nhận trong cấu hình Rayyan đã
chọn là bất khả thi dưới mô hình này. Kết quả âm được giữ lại và nguyên nhân
thiết kế được ghi rõ, không đổi luật sau khi xem kết quả để làm số liệu đẹp hơn.

Hai trường hợp Rayyan, dòng 509 và 146, từng hết thời gian khi cho sửa khóa.
Mỗi trường hợp đã có nghiệm tối ưu khóa cố định bằng 104, kèm cận dưới và kiểm
tra nghiệm trong hồ sơ cũ. Theo định lý bằng nhau, **chi phí tối ưu cho sửa
khóa cũng là 104** ở cả hai trường hợp.

Mình kiểm tra lại các mã băm, cấu trúc luật, chi phí, cận và danh sách sửa
đã lưu. Mình không chạy lại bộ giải, không có lại CSV nguồn trong bộ nhớ đệm,
và không tính lại phiếu từ dữ liệu gốc. Do đó kết luận số này dựa trên chứng
chỉ E011 đã lưu cộng với chứng minh mới. Hai lần chạy cũ vẫn mang trạng thái
hết thời gian; không được báo thành hai lần giải thành công mới.

## Mức độ kiểm tra và tính mới

E013 đã duyệt 81.893 cặp bảng/bộ luật bị từ chối trong các miền nhỏ đã chốt
trước khi chạy; tất cả khớp dự đoán. Có cả dữ liệu ba loại giá trị, 39.379 cặp
thuộc họ luật lồng nhau hoặc rời nhau, và 139 cấu trúc đạt cận đã được kiểm
tra. Những số này có chồng lặp, không phải các mẫu thực nghiệm độc lập.

Chứng minh tổng quát gồm ba phần: đơn giản hóa cách sửa từng dòng; thay mỗi
lần sửa khóa bằng một số lần sửa y có giới hạn; dựng bảng đạt đúng giới hạn.
Phần phân chia các tập thành chuỗi sử dụng định lý Dilworth đã có từ năm 1950.
Mình không nhận định lý đó, tối ưu can thiệp nói chung hay kỹ thuật quy dẫn
Set Cover là phát minh của bài.

Mình đã đối chiếu trực tiếp với một cận chuyển đổi trong nghiên cứu sửa cơ
sở dữ liệu của Livshits, Kimelfeld và Roy. Hai công trình dùng tham số khác
nhau, tối ưu mục tiêu khác nhau và có lập luận chuyển đổi khác nhau. Tìm kiếm
còn phát hiện một công trình về ảnh hưởng truyền thông lên bỏ phiếu có dùng
cấu trúc lồng nhau và phân chia chuỗi; cần đọc kỹ lập luận đó trước khi kết
luận mạnh hơn về độ mới. Hiện chưa có đánh giá khoa học độc lập.

## Đánh giá hiện tại

Đây là tiến triển thực chất hơn việc thêm số trang hay thêm một thí nghiệm:
bài có ứng viên kết quả trung tâm giải thích được một ranh giới rõ ràng và
cả kết quả âm trước đây. Mình đánh giá hướng này đáng phát triển thành phần
chính của một preprint lý thuyết hẹp.

Tuy nhiên, chưa đủ cơ sở nói đây là kết quả chưa từng có, có ảnh hưởng lớn,
hay giúp làm sạch dữ liệu chính xác hơn. Bước tiếp theo là đọc sâu các công
trình gần nhất, tiếp tục tìm điểm hở của chứng minh, rồi viết lại bản thảo
quanh kết quả này nếu nó vẫn đứng vững. Không cần bạn duyệt nộp bài hay chọn
giấy phép để mình tiếp tục các bước nghiên cứu đó.

Tài liệu chi tiết: [chứng minh](../experiments/E013-schema-width/theory.md),
[phân tích kiểm tra](../experiments/E013-schema-width/analysis.md),
[đối chiếu tài liệu](../literature/schema-width-positioning-20261105.md),
[suy luận từ E011](../experiments/E013-schema-width/results/e011-analytical-reanalysis.json).
