# Tiến độ tìm đóng góp mới: khi chính cột khóa có thể sai

Ngày 23-10-2026. Đây là kết quả nghiên cứu đang phát triển, chưa phải tuyên bố
đã xác lập tính mới hay bản thảo đã được nộp.

Câu hỏi hiện tại là: **cần sửa ít nhất bao nhiêu ô ngữ cảnh để bộ kiểm tra đổi
kết luận về một ô mục tiêu, kể cả khi được phép sửa cột dùng để chia nhóm?**
Ô và toàn bộ dòng mục tiêu được giữ nguyên. Điều này đo độ ổn định của kết
luận trước thay đổi ở các dòng khác; nó chưa nói kết luận ban đầu đúng hay sai.

## Ví dụ đã được kiểm tra bằng vét cạn

Hai quy tắc dùng (a,b) và (a,c) để gom nhóm rồi so sánh giá trị y. Giá trị của
dòng mục tiêu phải phổ biến duy nhất trong cả hai nhóm mới được chấp nhận.

| Dòng | a | b | c | y |
| --- | ---: | ---: | ---: | ---: |
| Mục tiêu, giữ nguyên | 0 | 0 | 0 | 0 |
| Ngữ cảnh 1 | 0 | 0 | 1 | 1 |
| Ngữ cảnh 2 | 0 | 1 | 0 | 1 |
| Ngữ cảnh 3 | 1 | 0 | 0 | 0 |

Ban đầu, mỗi nhóm có một giá trị 0 và một giá trị 1, nên hòa và dòng mục tiêu
bị từ chối. Nếu chỉ sửa y, cần đổi y của cả dòng ngữ cảnh 1 và 2: hai ô.

Nhưng chỉ cần đổi **a của dòng ngữ cảnh 3 từ 1 thành 0**. Dòng này lập tức vào
cả hai nhóm, khiến mỗi nhóm có hai số 0 và một số 1. Kết luận đổi sau một ô sửa.
Vét cạn trên các ô thô xác nhận chi phí tối thiểu là một trong mô hình cho phép
sửa khóa, so với hai khi khóa được bảo vệ.

## Phần phương pháp đang hình thành

Một cột khóa có thể có hàng nghìn giá trị. Với nhiệm vụ cụ thể này, ta chỉ cần
biết từng giá trị khóa có khớp dòng mục tiêu hay không, đồng thời vẫn đếm đúng
chi phí sửa ô. Mình đã viết lập luận rằng khi tìm cách làm mục tiêu được chấp
nhận, có thể bỏ những hành động sửa bị một hành động khác tốt hơn lấn át.

Nếu có q cột khóa, mỗi dòng chỉ cần giữ tối đa `2^q + 1` hành động chuẩn trong
mô hình đã nêu, thay vì xét mọi tổ hợp giá trị khóa và y. Sau đó thuật toán quy
hoạch động tìm chi phí nhỏ nhất và xuất ra các ô thực sự phải sửa. Chiều làm
mục tiêu bị từ chối dùng một phép tính riêng và cũng đã được kiểm tra.

Đây là ứng viên đóng góp về **rút gọn chính xác không gian sửa đổi có tính đến
vai trò khóa**. Các ý tưởng tổng quát về phản thực, sửa ít ô nhất và SAT đã có
trước; mình không nhận chúng là phát minh của nghiên cứu này.

## Đã kiểm tra đến đâu?

- 30.642 đối chiếu chi phí tối ưu trên 5.107 bảng nhỏ, sáu họ quy tắc: không lệch.
- 61.854 kiểm tra phép rút gọn hành động theo từng dòng: không có phản ví dụ.
- Cả 30.618 phương án sửa hữu hạn xuất ra đều đổi kết luận với đúng số ô đã báo.
- Có trường hợp khóa cố định cho kết luận không thể đổi, nhưng sửa khóa thì đổi
  được. Điều đó cho thấy cần khai báo đúng mô hình được phép sửa.

Các con số là phép kiểm tra đầy đủ trong miền nhỏ đã khóa, không phải tỷ lệ
hiệu năng trên dữ liệu thật hoặc bằng chứng rằng phương pháp đã mới.

## Việc cần làm tiếp để trở thành đóng góp nghiên cứu

So sánh thuật toán chuyên biệt với cách giải tối ưu tổng quát đã có; kiểm tra
khả năng chạy ở kích thước lớn hơn; đối chiếu sâu xem phép rút gọn này có trùng
kết quả trước hay không. Chỉ khi những việc đó cho thấy khác biệt có ý nghĩa,
mình mới viết lại bài quanh đóng góp mới. Không chờ peer review để làm các bước
nghiên cứu này, cũng không yêu cầu bạn duyệt bản cũ để tiếp tục.

Nguồn kiểm tra: [kết quả E008](../data/E008-v1-checks.json),
[phương án sửa cụ thể](../data/E008-v1-witnesses.json),
[bản chứng minh](../experiments/E008-mutable-key-certificates/theory.md),
[đối chiếu công trình trước](../literature/mutable-key-novelty-20261023.md).
