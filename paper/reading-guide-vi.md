# Đọc và phản biện bản thảo trước khi đứng tên

Bản được giải thích: **Auditing Invariant Validation Benchmarks: Construction,
Error Attribution, and Probability Scores**, PDF 12 trang, tác giả dự kiến
Trần Vũ Bảo Minh, Independent Researcher, ngày 23-10-2026.
Đây là hướng dẫn đọc; không ghi nhận rằng bạn đã duyệt bài.

## 1. Bài này thực sự nghiên cứu điều gì?

Câu hỏi là: khi một bộ kiểm tra đạt điểm rất cao, bằng chứng đó cho phép kết
luận đến đâu? Bài kiểm toán hai bộ thử tự xây dựng, rồi bổ sung một phép thử
trên ba cặp bảng bẩn/tham chiếu do nhóm khác công bố. Không có mô hình AI mới
được huấn luyện trong nghiên cứu này.

Ví dụ minh họa: ta tạo hóa đơn có tổng tiền sai và viết bộ kiểm tra phép cộng.
Bộ kiểm tra có thể bắt đúng mọi lỗi đã tạo. Điều đó chưa cho biết nó xử lý được
lỗi địa chỉ hoặc lỗi thuế chưa đưa vào bộ thử. Đây là ví dụ giải thích logic,
không phải một thí nghiệm bổ sung hoặc kết quả đo trong bài.

## 2. Hai bộ thử tổng hợp nói được gì?

E001/E002 tạo các trường hợp có quan hệ định danh, bảo toàn hoặc chuyển trạng
thái. B0 kiểm tra một nhóm điều kiện cấu trúc hạn chế. M1 kiểm tra thêm các quan
hệ đã chọn. M1 khớp toàn bộ nhãn trên phần đánh giá của cả hai bộ thử.

E005 dùng cách tính chỉ số riêng để đọc lại các dự đoán đã lưu. 195 phép đối
chiếu chỉ số đều đạt sai số làm tròn quy định. Đây không phải 195 thí nghiệm
độc lập hoặc phản biện độc lập. Nó không chứng minh M1 tốt hơn mọi công cụ
kiểm tra dữ liệu hoặc tốt trong mọi ứng dụng.

E005 được thiết kế sau khi đã thấy các kết quả gốc, nên là phân tích thăm dò.
Khóa giao thức của E005 trước khi chạy kiểm toán không biến nó thành phép
xác nhận hoàn toàn chưa biết kết quả.

## 3. Vì sao Brier giảm mà xác suất vẫn cần xem lại?

Brier là trung bình của `(p - y)^2`, với `p` là xác suất trường hợp hợp lệ và
`y` là nhãn 0/1. Brier nhỏ hơn nghĩa là sai số bình phương xác suất nhỏ hơn
trên chính những trường hợp được đo.

Ta tách Brier thành `REL - RES + UNC`. REL đo độ lệch giữa xác suất và tần suất
đúng trong từng nhóm điểm; RES đo khả năng phân biệt các nhóm có tần suất khác
nhau; UNC phụ thuộc tỷ lệ nhãn. Đây là đẳng thức đã biết, không phải công thức
mới do bài phát minh.

Trong E001, B0 cho xác suất 0,5 trong tập cân bằng: Brier 0,25. M1 phân biệt
đúng nhãn nhưng xác suất được làm trơn, nên Brier khoảng 0,00005917. REL tăng
từ 0 lên khoảng 0,00005917; RES tăng đủ lớn để Brier vẫn giảm. Không thể chỉ
nhìn Brier giảm rồi nói mọi mặt của calibration đều tốt hơn.

Nếu xuất quyết định hoàn hảo thành xác suất 0/1, Brier bằng 0 trên tập này.
Điều đó không cho phép khuyến nghị xác suất tuyệt đối 0/1 cho dữ liệu mới:
chưa biết quyết định có tiếp tục hoàn hảo ngoài bộ thử hay không.

## 4. Vì sao khoảng bootstrap có thể bằng một điểm?

Bootstrap lấy lại các cụm để xem chỉ số thay đổi ra sao. Trong E001, 64 cụm
đánh giá có cùng chữ ký thống kê dùng cho các chỉ số. Lấy lại đúng số cụm
luôn tạo cùng tổng thống kê, nên khoảng có thể không có độ rộng.

Điều này mô tả cấu trúc bộ thử, không chứng minh sai số ứng dụng thực đã được
biết chính xác. E002 có sáu chữ ký trong 48 cụm; số chữ ký cũng không được
diễn giải thành cỡ mẫu hiệu dụng.

## 5. Ba bộ dữ liệu ngoài dự án kiểm tra điều gì?

E006 dùng Beers, Flights và Rayyan từ nguồn Raha đã cố định phiên bản. Một ô
được gán là khớp tham chiếu khi giá trị bảng bẩn bằng giá trị bảng tham chiếu
sau chuẩn hóa quy định. Nếu cả hai cùng trống, ô đó vẫn khớp. Nhãn này không
đồng nghĩa ô đó đầy đủ hoặc đúng cho mọi mục đích sử dụng.

Bốn chính sách gán nghi ngờ từ điều kiện không rỗng và xung đột phụ thuộc hàm.
Ví dụ, một mã nhà máy được kỳ vọng đi với một tên nhà máy. Khi cùng mã lại có
nhiều tên, ta biết có xung đột; chưa biết ngay tên nào sai. Rall đánh dấu các
ô tham gia xung đột. Rmode đánh dấu giá trị phụ thuộc ngoài giá trị phổ biến
duy nhất; nếu hòa thì đánh dấu các giá trị phụ thuộc. Chúng là baseline chẩn
đoán đơn giản, không phải thuật toán Raha.

Các chính sách khác M1 về phương pháp, nhiệm vụ và nhãn. So sánh điểm hai phần
không chứng minh M1 chuyển sang dữ liệu thật bị giảm hiệu năng. Quy tắc dùng
ngữ cảnh bảng bẩn trong cùng phần chia: đây là thiết lập transductive, không
phải dự đoán từng dòng mới tách biệt.

## 6. Kết quả ngoài dự án có đánh đổi nào?

Trong bài, dương tính là **hợp lệ/khớp tham chiếu**. FPR là chấp nhận ô sai;
FNR là từ chối ô đúng. Cần đọc kỹ vì nhiều bài phát hiện lỗi lại gọi chính lỗi
là dương tính.

| Bộ dữ liệu | FNR của Rall | FNR của Rmode | FPR của Rall | FPR của Rmode |
| --- | ---: | ---: | ---: | ---: |
| Beers | 12,66% | 0,43% | 93,76% | 93,76% |
| Flights | 74,41% | 8,02% | 0% | 12,22% |
| Rayyan | 19,48% | 18,17% | 91,73% | 92,86% |

Nguồn: dòng `evaluation`, `all_cells`, `Rall`/`Rmode` trong
[bảng chỉ số đóng băng](../data/E006-v1-metrics.csv); phần trăm làm tròn hai số.
FPR và FNR có mẫu số khác nhau, không được cộng thành một tỷ lệ.

Flights minh họa đánh đổi rõ nhất: Rmode giảm từ chối nhầm nhưng chấp nhận
thêm ô sai. Beers và Rayyan có tỷ lệ chấp nhận ô sai rất cao. Không nên đọc
bài như đề xuất đưa các baseline này vào hệ thống thực tế.

## 7. Dự đoán nào không được ủng hộ đầy đủ?

H6b dự đoán Brier của lookup thấp hơn bản xác suất nhị phân cho Rmode ở cả ba
bộ, với cận trên khoảng bootstrap nhỏ hơn 0. Điểm ước lượng đều giảm, nhưng
khoảng Flights xấp xỉ `[-0,02086; +0,00138]` cắt 0. Dự đoán toàn bộ ba bộ do
đó không được ủng hộ đầy đủ. Bài giữ kết quả này.

Khoảng cắt 0 không chứng minh hai cách hoàn toàn tương đương; nó không đạt
tiêu chí chiều cải thiện đã đặt ra. Lookup giữ mức điểm thô còn bản nhị phân
gộp các mức khác 0. Chênh lệch có thể do cả REL và RES, không phải hiệu ứng
nhân quả riêng của calibration.

10.000 lần lấy lại cụm không tạo thêm 10.000 bộ dữ liệu độc lập. Khoảng chỉ
mô tả phép lấy lại cụm trên bảng và quy tắc cố định. Flights có 17 cụm đánh
giá; chưa có suy rộng chắc chắn sang dữ liệu chuyến bay ngoài thực tế.

## 8. Đóng góp và điểm yếu cần tự đánh giá

Đóng góp dự kiến là case study có số liệu, giao thức và chuỗi bằng chứng kiểm
tra được: điểm hoàn hảo trên thiết kế tổng hợp, cách đọc điểm xác suất và đánh
đổi gán lỗi khi dùng nhãn tham chiếu ngoài dự án. Ý tưởng nền tảng về oracle,
Brier và xung đột quy tắc đã có trong tài liệu trước; bài ghi nhận điều đó.
Không có thuật toán mới hoặc chứng minh tổng quát mới.

Điểm yếu lớn nhất còn lại là liệu case study này có đủ giá trị khoa học để
lưu trữ công khai trong cộng đồng phù hợp hay không. Code chạy đúng và PDF
đẹp không trả lời được câu hỏi đó. Chưa có phản biện khoa học độc lập. AI đã
hỗ trợ đáng kể thiết kế, code, phân tích và viết; kiểm toán cùng tác nhân
không thay thế một người có chuyên môn đọc lại lập luận.

## 9. Cách đọc và gửi sửa đổi

Đọc Abstract và Conclusion trước để xem bài có nói đúng điều bạn muốn đứng
tên hay không. Đọc tiếp mục 6 và bảng ngoài dự án, rồi mục 8 về giới hạn.
Khi cần kiểm tra cách tính, đọc mục 4 và 7, cùng Appendix A.

Bạn có thể phản hồi theo mục hoặc trang: “trang 8, tôi chưa hiểu khoảng cắt
0”, “tôi muốn bỏ câu kết luận này”, hoặc “giải thích thêm cách gán nhãn”.
Chưa hiểu một phần thì nên làm rõ trước khi xác nhận đã đọc, hiểu và chịu
trách nhiệm cho bản sẽ nộp.
