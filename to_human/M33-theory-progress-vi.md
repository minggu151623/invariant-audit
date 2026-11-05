# Bản mới đã tốt hơn ở đâu?

Ngày 05/11/2026. Bản hiện tại: `paper/context-edit-stability-r3/preview.pdf`,
10 trang. Đây là đánh giá nội bộ và bản để bạn đọc, chưa phải bài đã nộp.

**Mình đánh giá bản này đã đủ thành một preprint lý thuyết hẹp để chuyển sang
bước tác giả đọc và duyệt.** So với bản trước, nó có thêm một kết quả toán học
giải thích vì sao hai chiều đổi quyết định có độ khó khác nhau. Mình chưa có
cơ sở gọi đây là đóng góp lớn, phương pháp làm sạch dữ liệu tốt hơn, hay kết quả
đầu tiên trên thế giới. Tìm tài liệu và tự kiểm tra không bảo đảm những điều đó.

## Câu hỏi của bài, bằng ngôn ngữ thông thường

Một luật gom các dòng có cùng khóa rồi xem giá trị của ô đang xét có nhiều
phiếu nhất hay không. Ví dụ, gom các dòng cùng mã nhà máy để kiểm tra tên nhà
máy. Ô đang xét và cả dòng của nó được giữ nguyên. Ta hỏi: cần sửa ít nhất bao
nhiêu ô ở các dòng khác để quyết định về nó đổi chiều?

Nếu được sửa khóa, một dòng có thể chuyển vào hoặc ra khỏi nhóm. Nếu có nhiều
luật, một lần sửa có thể tác động đến nhiều nhóm. “Được chấp nhận” ở đây chỉ là
vượt qua phép kiểm tra này; nó không đồng nghĩa với đúng ngoài đời.

## Kết quả bổ sung

| Chiều đổi quyết định | Điều bài chứng minh |
|---|---|
| Đang được tất cả luật chấp nhận, muốn làm bị từ chối | Có công thức chính xác và thuật toán tính trong thời gian đa thức. Chỉ cần làm một luật thất bại. |
| Đang bị từ chối, muốn được tất cả luật chấp nhận | Bài toán quyết định là NP-complete khi số cột và số luật được tăng theo đầu vào, dù dữ liệu chỉ có 0/1 và mỗi luật chỉ dùng một cột khóa. |

NP-complete không có nghĩa là mọi bảng đều chạy chậm, hoặc đã chứng minh không
thể giải nhanh. Nó có nghĩa: bài toán nằm trong một lớp khó tiêu chuẩn; nếu có
thuật toán đa thức giải đúng mọi đầu vào của nó thì P = NP. Bài cũng giải thích
rằng khi cố định số cột và số loại giá trị, vẫn có một thuật toán đa thức theo
số dòng, dù số mũ có thể rất lớn.

Độ khó tồn tại ngay khi **không được sửa khóa**. Vì vậy không được viết rằng
cho phép sửa khóa là nguyên nhân làm bài toán khó. Kết quả mới giúp đặt đúng
kỳ vọng cho thuật toán tối ưu của bài, không biến hai lần hết thời gian trên
dữ liệu cũ thành một bằng chứng của NP-completeness.

## Một ví dụ để hiểu chứng minh

Giả sử cần phủ ba phần tử a, b, c bằng ba tập:

- S1 chứa a, b.
- S2 chứa b, c.
- S3 chứa a, c.

Chọn bất kỳ hai tập là phủ hết; một tập chưa đủ. Bài biến mỗi phần tử thành
một luật và mỗi tập thành một dòng dữ liệu:

| Dòng | Khóa a | Khóa b | Khóa c | Giá trị y |
|---|---:|---:|---:|---:|
| Dòng được bảo vệ | 0 | 0 | 0 | 0 |
| S1 | 0 | 0 | 1 | 1 |
| S2 | 1 | 0 | 0 | 1 |
| S3 | 0 | 1 | 0 | 1 |
| Dòng hỗ trợ a | 0 | 1 | 1 | 0 |
| Dòng hỗ trợ b | 1 | 0 | 1 | 0 |
| Dòng hỗ trợ c | 1 | 1 | 0 | 0 |

Luật a nhìn những dòng có khóa a = 0; b và c tương tự. Ban đầu mỗi nhóm có
hai giá trị 0 và hai giá trị 1, nên hòa và bị từ chối. Đổi y của S1 thành 0
làm a, b vượt qua, nhưng c vẫn hòa. Đổi thêm y của S2 thành 0 thì cả ba vượt
qua. Chi phí hai ô đúng bằng số tập tối thiểu cần chọn.

Phần quan trọng là chứng minh không thể lách bằng sửa khóa: bất cứ cách sửa
thành công nào tốn K ô cũng cho phép lấy ra một bộ phủ dùng không quá K tập.
Cột khóa nào bị sửa thì chọn một tập chứa phần tử tương ứng. Cột nào không bị
sửa giữ nguyên nhóm, nên muốn thoát hòa phải có một dòng thuộc tập chứa phần
tử đó đổi y từ 1 thành 0. Lấy tập đó vào bộ phủ. Mỗi lần chọn được tính vào
một ô đã sửa. Lập luận này đúng cho mọi kích thước, không chỉ ví dụ ba phần tử.

## Đã kiểm tra gì?

Chương trình duyệt đầy đủ 111 cấu hình nhỏ theo kế hoạch đã lưu trước khi chạy,
thử cả khóa cố định và khóa được sửa. Cả 222 giá trị tối ưu đều khớp phép tính
bộ phủ riêng. Trong 147.523 lần kiểm tra bảng đích, mọi trường hợp chấp nhận
đều cho phép lấy ra bộ phủ như chứng minh yêu cầu. Có 24.288 trường hợp thành
công có sửa khóa. Số đếm giữa hai chế độ có chồng lặp, không phải các thử nghiệm
độc lập. Đây là kiểm tra hữu hạn; chứng minh tổng quát nằm trong Định lý 3.

Kỹ thuật dùng Set Cover và cân bằng phiếu đã có trong nghiên cứu về tác động
đến nhiều cuộc bỏ phiếu. Bản thảo đã dẫn nguồn, không nhận kỹ thuật chung đó
là phát minh. Phần bài trình bày riêng là phép quy dẫn cho mô hình ô dữ liệu này
và lập luận vẫn giữ được cận dưới khi khóa được sửa tùy ý.

## Còn giới hạn gì, còn phải làm gì?

Kết quả thực nghiệm cũ được giữ nguyên: 30 cặp tính được chính xác không có
lợi ích giảm chi phí ở chiều chuyển sang chấp nhận; hai trường hợp vẫn hết thời
gian. Chưa có bằng chứng bài giúp phát hiện lỗi đúng hơn hoặc mang lại lợi ích
trong một quy trình sử dụng thực tế. Đây vẫn là bài lý thuyết/thuật toán có phạm
vi nhỏ, và kiểm tra nội bộ chưa xác nhận mức độ mới trên toàn bộ tài liệu.

Phần còn lại để đi đến nộp bài là bạn hiểu và duyệt nội dung đứng tên mình,
quyết định giấy phép, và thiết lập tài khoản/quy trình nộp. Những việc đó chưa
được thực hiện thay bạn. Mình không coi phản biện độc lập là điều kiện bắt buộc
để tiếp tục chuẩn bị preprint, và cũng không coi việc sửa xong PDF là bạn đã duyệt.
