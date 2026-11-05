# Tự đánh giá bản thảo: nên sửa trước khi chốt nộp

Ngày 24/10/2026. Đối tượng: nguồn bản thảo 7 trang tại
`paper/context-edit-stability/main.tex`, các phân tích E008–E011 và bản đối
chiếu đóng góp. Đây là tự đánh giá của hệ thống đã tham gia tạo bài, không
phải phản biện độc lập, chứng nhận ARA hay dự đoán quyết định của arXiv.
Không chạy lại thí nghiệm và không sửa bản thảo hoặc các gói đã đóng băng.

## Kết luận

**Mình chưa khuyên chốt nộp phiên bản này.** Bài đã có cấu trúc nghiên cứu,
chứng minh và bằng chứng kiểm tra thực chất. Tuy nhiên, theo mong muốn của
bạn về điểm mới, phần bảo vệ tính mới và lý do kết quả đáng quan tâm còn
chưa đủ thuyết phục. Khuyến nghị là sửa có trọng tâm; chưa có bằng chứng để
bác bỏ toàn bộ hướng nghiên cứu.

Đây là nhận định chất lượng khoa học của mình. Nó không có nghĩa arXiv bắt
buộc thêm thí nghiệm, đòi peer review hay chắc chắn từ chối bài.

## Phần đã làm tốt

- **Mô hình minh bạch:** hàng mục tiêu được bảo vệ, mỗi ô sửa có chi phí một,
  nhiều luật cùng RHS, hòa bị từ chối. Không đánh đồng độ bền với độ đúng.
- **Chứng minh có lập luận đủ cụ thể để kiểm tra:** chiều từ chấp nhận sang
  từ chối có cận dưới và cách sửa đạt cận; chiều ngược lại có xây dựng phương
  án lấn át theo từng hàng và chuyển được thành kết quả tối ưu toàn bảng.
- **Bằng chứng chương trình tương đối kỹ:** có đối chiếu với liệt kê sửa ô
  trực tiếp trong miền nhỏ, kiểm tra nhân chứng, ghi nhận nghiệm tối ưu và
  giới hạn thời gian riêng biệt. Các miền kiểm tra chồng lấn đã được nói rõ.
- **Báo cáo trung thực:** giữ 30 cặp không giảm chi phí, hai timeout và trường
  hợp phương pháp chuyên biệt chạy chậm hơn; ba bảng dùng lại không được
  gọi là holdout mới.

## Kiểm tra lập luận toán học lần này

Với định lý bán kính từ chấp nhận sang từ chối, một sửa ô chia nhóm làm thay
đổi biên phiếu của một luật tối đa một, sửa RHS tối đa hai. Đổi lần lượt mỗi
ô khác biệt sang giá trị cuối cùng cho phép dùng cận này với chi phí Hamming.
Trong nhóm không đơn lẻ, có đủ ô mang giá trị mục tiêu ngoài hàng được bảo
vệ để đạt cận. Nhóm đơn lẻ bắt buộc phải có một hàng đối thủ được đưa vào;
chi phí nhập hàng trong công thức là đạt được. Phép lấy min qua các luật
đúng vì chỉ cần một luật từ chối để cả bộ kiểm tra từ chối.

Với bổ đề phương án chuẩn, phép hợp các tập khóa khớp giữ/mở rộng đóng góp
dương, còn phép giao khi giữ RHS đối thủ thu hẹp đóng góp âm. Từng phép xây
dựng không tăng số ô sửa và không giảm bất kỳ biên phiếu nào. Cộng theo hàng
cho kết quả tối ưu toàn bảng. Cận số phương án cũng phù hợp phép đếm.

**Chưa tìm thấy lỗi cụ thể trong các bước trên dưới mô hình đã nêu.** Đây
là kết quả đọc lại lập luận, không chứng minh tính mới và không phải một
chứng nhận đúng cho mọi đầu vào từ việc chạy nhiều kiểm tra hữu hạn.

## Những điểm cần sửa, theo thứ tự ưu tiên

### 1. Quan trọng: cần bảo vệ phần đóng góp trước công trình sát chủ đề hơn

Bản thảo hiện nói: “The contribution presented here is the specialized
dominance and singleton characterization under explicit assumptions”.
Đó là hai mệnh đề cần bảo vệ, không phải ý tưởng tối thiểu hóa số ô sửa nói
chung. Bản đối chiếu đã loại bỏ nhiều tuyên bố mới quá rộng, nhưng vẫn cần
làm rõ liệu hai mệnh đề là kết quả riêng hay hệ quả trực tiếp của lý thuyết
sẵn có. Không cần chứng minh một tuyên bố tuyệt đối “đầu tiên thế giới”.

Lần đọc này bổ sung công trình [Debosschere và Geerts, *Cell-Based Causality
for Data Repairs*, TaPP 2015](https://www.usenix.org/system/files/tapp15-debosschere.pdf).
Mục 2 định nghĩa sửa ở cấp ô và tối thiểu hóa số vị trí thay đổi; mục 3 nối
sửa dữ liệu với nguyên nhân và trách nhiệm. Nó chưa có trong sáu tài liệu
tham khảo của bản thảo đang xét.

Khác biệt đáng giữ: công trình 2015 đòi sửa để thỏa các FD; bài mình chỉ
lật một quyết định plurality của hàng được bảo vệ, bảng sau sửa có thể vẫn
vi phạm FD. Những định nghĩa và mệnh đề được đọc chưa cho thấy nó phát biểu
hai kết quả của bài mình. **Thiếu so sánh là một khoảng trống định vị, chưa
phải bằng chứng bài mình đã bị làm trước.**

[Bertossi, bản v7 năm 2020](https://arxiv.org/html/1712.01001v7), mục 4,
cũng có nguyên nhân cấp thuộc tính, nhưng phép sửa cụ thể là thay bằng NULL.
Khác biệt phép sửa và mục tiêu cần được viết rõ trong bảng đối chiếu, thay
vì chỉ liệt kê tên công trình. [Xia, mục 3–4](https://arxiv.org/html/1204.1231v3)
đã có mục tiêu tối thiểu thao tác để thắng/thua và ràng buộc điểm nguyên;
những thành phần đó tiếp tục không được tính là đóng góp riêng.

Sửa cần làm: đối chiếu cụ thể đầu vào, ô được sửa, mục tiêu, chi phí và kết
quả nào suy ra trực tiếp được từ từng công trình; nêu phần lập luận còn cần
thêm để có hai định lý hiện tại. Không kết luận mới chỉ vì tìm không thấy từ khóa.

### 2. Quan trọng: kết quả đáng dùng để làm gì còn thiếu sức thuyết phục

Chứng minh ngắn tự nó không phải điểm yếu. Vấn đề là cần giải thích vì sao
sự đơn giản đó giải quyết một câu hỏi đáng quan tâm, thay vì chỉ mô tả một
bộ kiểm tra dễ phân tích do mình chọn.

E011 cho thấy 1.133 chuyển INF sang hữu hạn và chỉ một giảm hữu hạn. Điều
này minh họa rõ sự khác biệt giữa hai mô hình sửa, nhưng chưa cho thấy một
quy trình kiểm tra dữ liệu được cải thiện. Bài không có kết quả tăng độ chính
xác và không nên được đánh giá như đã có kết quả đó.

Sửa cần làm: chọn một tác dụng cụ thể phù hợp bằng chứng, chẳng hạn tính
chính xác mức nhạy của quyết định khi cột chia nhóm có thể sai, và giải thích
bán kính/nhân chứng dẫn đến quyết định kiểm tra nào. Một ví dụ làm việc đầy
đủ hoặc hệ quả thuật toán rõ có thể hữu ích; không mặc định phải có ứng dụng
thương mại, dữ liệu lớn hay thêm kết quả dương mới được viết preprint.

### 3. Vừa: phép so sánh tốc độ chỉ nâng đỡ một kết luận hẹp

Bản thảo tự ghi: “The rejected generator contains no target-valued RHS
context rows”. Ở phép thử tốc độ cho chiều từ chối sang chấp nhận, nhánh của
bổ đề dành cho hàng ban đầu mang RHS mục tiêu vì vậy không được khảo sát.
E008 có kiểm tra đúng trong miền nhỏ; đây là thiếu bao phủ về hiệu năng,
không phải bằng chứng bổ đề sai.

Các bảng dựng có 16/128 hàng, 2/4/6 khóa và hai lần đo trên một máy. Kết quả
trung vị khoảng 3 lần nhanh hơn so với công thức MILP tổng quát đã triển khai
không xác lập ưu thế với mọi bộ giải hay dữ liệu thực. Hai timeout E011 vẫn
là kết quả chưa biết, không được suy ra bằng nhau hay tốt hơn.

Sửa cần làm: giữ phát biểu hiệu năng đúng phạm vi hiện có. Nếu muốn dùng
tốc độ làm lý do chính của bài, cần một thiết kế khóa trước có hàng ngữ cảnh
RHS mục tiêu lẫn đối thủ và cách so sánh phù hợp. Đây là điều kiện cho tuyên
bố hiệu năng mạnh hơn, không là yêu cầu bắt buộc cho định lý hiện tại.

## Quyết định thực tế

Mình ưu tiên hoàn tất đối chiếu sát chủ đề và làm rõ giá trị của hai kết quả
trước khi thúc bạn duyệt để nộp. Bài có thể phát triển thành một ghi chú lý
thuyết ngắn với phạm vi khiêm tốn nếu phần còn mới được bảo vệ rõ. Nếu so
sánh cho thấy kết quả chỉ là hệ quả sẵn có, cần ghi nhận điều đó và đổi hướng.

Không cần chạy thêm hàng loạt thí nghiệm hoặc tìm bằng được một kết quả
dương. Nghiên cứu hiện tại vẫn có giá trị kiểm tra và kết quả âm; câu hỏi còn
lại là đóng góp khoa học đủ rõ và đủ đáng quan tâm để công bố dưới tên bạn.
