# M32: đã sửa phần định vị, chưa chốt chất lượng để nộp

Ngày 05/11/2026. Bạn cho phép tiếp tục sau đánh giá nội bộ rằng bài chưa đủ
thuyết phục để khuyên chốt nộp. Mục tiêu vẫn là nghiên cứu để có bài đăng
arXiv; chưa ghi nhận duyệt nội dung, chọn giấy phép hoặc quyền công bố thay bạn.

## Những thay đổi đã làm

Mình đọc và đối chiếu trực tiếp định nghĩa/mệnh đề trong bốn công trình gần:
Debosschere–Geerts 2015, Bertossi v7 2020, Meliou và cộng sự 2011, Xia v3.
Bản sửa thêm hai tài liệu còn thiếu, nói rõ phần nào đã có trước và phần
lập luận chuyên biệt nào bài mình thực sự trình bày. Không dùng việc tìm
không thấy một phát biểu để tuyên bố đầu tiên trên thế giới.

Một bổ sung về nội dung: **chi phí sửa toàn bảng để thỏa FD và chi phí làm
bộ kiểm tra đổi ý không thay thế được cho nhau, kể cả xấp xỉ theo một hệ số
cố định, trong mô hình so sánh đã nêu.** Có thể dựng:

- Bảng chỉ cần sửa một ô để thỏa FD, nhưng cần sửa h ô để lật quyết định;
  h có thể lớn tùy ý.
- Bảng cần sửa k ô để thỏa FD, nhưng chỉ cần một ô để lật quyết định;
  k có thể lớn tùy ý.

Lập luận cho hai họ bảng nằm trong bài. Mình kiểm tra các trường hợp h,k bằng
1,2,3 bằng cách liệt kê trực tiếp mọi bảng đích. Thêm một ví dụ bốn hàng cho
thấy một lần sửa khóa có thể làm hai luật cùng đổi quyết định. Tổng cộng tám
kiểm tra, 285.032 bảng đích, đều khớp lập luận và có nhân chứng cụ thể.
Đây là ví dụ phân biệt hai mục tiêu, không phải kết quả ứng dụng trên dữ liệu
thực và không được quảng bá như một phát minh độc lập.

Bản sửa định vị tác dụng ở mức kiểm tra độ nhạy theo ngân sách: nếu cho phép
tối đa B ô ngữ cảnh sai/đổi, kết luận hiện tại có chắc giữ nguyên không, hoặc
có cách sửa trong ngân sách làm nó đổi? Điều đó không chỉ ra ô nào thực sự
sai, không tự chọn B hợp lý và không chứng minh tăng độ chính xác làm sạch.

## Phần giữ nguyên và kiểm tra bàn giao

- Hai kết quả cấu trúc chính và phần kết quả E008–E011 giữ nguyên nội dung.
- Vẫn giữ 30 cặp không giảm chi phí, hai timeout chưa biết nghiệm tối ưu và
  giới hạn nguồn dữ liệu đã dùng trước đó.
- Bản PDF sửa có chín trang, ba bảng, tám tài liệu tham khảo; cả chín trang
  đã được xem, phông chữ nhúng đầy đủ và tên tiếng Việt hiển thị đúng.
- Nguồn ZIP một tệp biên dịch từ thư mục tách riêng cho cùng văn bản từng
  trang; log cuối không có cảnh báo bố cục/tham chiếu.
- 186 tệp khoa học cũ, gồm bản M30 và các gói M31, không đổi nội dung.

Bộ nhớ đệm CSV gốc dùng cho E011 hiện không còn ở đường dẫn ghi trong nghiên
cứu tháng 10. Lần này không chạy lại hoặc tuyên bố tái kiểm tra dữ liệu nguồn;
các kiểm tra tháng 10 được giữ nguyên với đúng thời điểm và phạm vi của chúng.

## Đánh giá sau sửa

Phần phân biệt với nghiên cứu trước và cách giải thích đã rõ hơn. Mình vẫn
chưa gọi bài là một đóng góp mạnh hoặc đề nghị bạn chốt nộp ngay: các định
lý chuyên biệt còn đơn giản và hiệu quả ứng dụng chưa được chứng minh. Một
bài ngắn có thể có giá trị nhờ một câu trả lời sắc nét, không cần biến nó thành
một hệ thống lớn; nhưng tính đáng quan tâm phải được lập luận tốt hơn nữa.

Hướng nghiên cứu tiếp theo ưu tiên là ranh giới tính toán của chiều từ chối
sang chấp nhận: có những cấu trúc luật nào giải được nhanh, và khi nào độ khó
là bản chất? Mình có một hướng quy dẫn từ bài toán phủ tập cần kiểm tra. Nó
chưa phải định lý đã xác nhận và chưa được đưa vào bản thảo như kết quả.
Không cần quyết định giấy phép hay phê duyệt để làm phần nghiên cứu cục bộ này.

## Tệp hiện tại

- [PDF sửa](../paper/context-edit-stability-r2/preview.pdf).
- [Nguồn](../paper/context-edit-stability-r2/tex/main.tex).
- [Đối chiếu cụ thể](../literature/direct-positioning-20261105.md).
- [Bộ kiểm tra ví dụ](../paper/context-edit-stability-r2/verify_examples.py).
- [Kết quả ví dụ](../paper/context-edit-stability-r2/example-checks.json).
- [Kiểm tra bản sửa](../paper/context-edit-stability-r2/revision-verification.json).

Các phần này do cùng hệ thống nghiên cứu và tự kiểm tra, chưa phải phản biện
độc lập. Bài chưa được nộp và chưa có mã arXiv.
