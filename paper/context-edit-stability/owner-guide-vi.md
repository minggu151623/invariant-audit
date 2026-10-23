# Cách đọc bản thảo mới 7 trang

Đây là bản bài mới về độ bền quyết định. Nó thay hướng bài audit trước đây;
tên tác giả vẫn là Trần Vũ Bảo Minh, affiliation Independent Researcher theo
thông tin bạn đã cung cấp. Bạn chưa duyệt nội dung hoặc cho phép công bố.

**Câu hỏi của bài:** giữ nguyên một hàng đang xét, phải sửa ít nhất bao nhiêu
ô ở các hàng khác để bộ kiểm tra đổi ý? Cho sửa cả cột khóa dùng để chia nhóm
và cột giá trị được kiểm tra. Mỗi ô thay đổi tính một đơn vị. Đây là mô hình
sửa đổi đã chọn, không phải giả định mọi sửa đổi đều có cùng chi phí ngoài đời.

Trang 1 giới thiệu câu hỏi và kết quả. Trang 2 định nghĩa bộ kiểm tra: giá trị
của hàng mục tiêu phải phổ biến hơn từng giá trị đối thủ trong mọi nhóm liên
quan; hòa thì bị từ chối. Hàng mục tiêu được bảo vệ hoàn toàn. Bán kính 3 nghĩa
là mọi cách sửa tối đa hai ô ngữ cảnh đều giữ quyết định, và tồn tại cách sửa
ba ô làm quyết định đổi. Nó không có nghĩa ô mục tiêu có xác suất đúng cao.

**Kết quả cấu trúc thứ nhất, trang 2--3:** nếu ô ban đầu được chấp nhận, nhóm
có nhiều hàng có chi phí lật quyết định đúng bằng biên phiếu chia hai, làm tròn
lên. Sửa khóa không thể rẻ hơn. Riêng nhóm chỉ có hàng mục tiêu, ta phải nhập
một hàng bên ngoài mang giá trị cạnh tranh vào nhóm; chi phí là số ô khóa cần
đổi, cộng thêm một nếu phải đổi cả giá trị. So sánh hai chi phí này cho biết
chính xác khi nào sửa khóa làm bán kính giảm.

Ví dụ dữ liệu thực ở trang 6: ô journal_title của hàng 644 Rayyan thuộc hai
nhóm có 4 và 1 hàng. Giữ khóa thì bán kính là 2. Chỉ cần sửa journal_issn ở
hàng 1 để đưa một đối thủ vào nhóm đơn lẻ thì quyết định đổi với một ô sửa.
Hàng 644 giữ nguyên. Đây là một ví dụ được chọn sau khi xem toàn bộ kết quả,
không phải một kiểm định độc lập mới.

**Kết quả cấu trúc thứ hai, trang 3--4:** chiều ngược lại khó hơn vì muốn được
chấp nhận phải vượt qua đồng thời mọi luật. Chứng minh cho phép bỏ các kiểu
sửa bị một kiểu khác lấn át: tốn không ít hơn nhưng không cải thiện được các
biên so sánh tốt hơn. Sau phép rút gọn vẫn còn ít nhất một nghiệm tối ưu, nếu
nghiệm tồn tại. Bài dùng bài toán tối ưu nguyên để tìm trong các phương án còn
lại. Số phương án mỗi hàng vẫn tăng theo hàm mũ của số cột khóa, nên không có
lời hứa luôn chạy nhanh.

Trang 4--5 trình bày kiểm tra trên bảng dựng sẵn. Trang 5--6 là ba bảng nguồn
đã dùng trước đây trong dự án. Chúng không phải kiểm định mù mới. Kết quả thực
tế khá hẹp: 1.133 chuyển từ bán kính vô hạn của mô hình giữ khóa sang hữu hạn;
chỉ một trường hợp bán kính hữu hạn giảm. Với chiều đang bị từ chối, không
có cải thiện chi phí trong 30 cặp giải chính xác; hai bài toán đầy đủ hết năm
giây mà chưa có nghiệm. Cả kết quả âm lẫn hết thời gian đều nằm trong bài.

Một kết quả quan trọng khác: 1.493 ô được chấp nhận có bán kính ít nhất 2 nhưng
vẫn khác bản tham chiếu. Do đó bài không đề xuất dùng độ bền thay cho kiểm
tra đúng/sai hay cam kết tăng độ chính xác làm sạch dữ liệu.

Trang 6--7 nêu công trình liên quan, phạm vi và khả năng tái kiểm tra. Ý tưởng
phản thực, chia miền giá trị và tối ưu số sửa đổi đã có trước; bài không nhận
chúng là mới. Đóng góp được trình bày ở mức định lý chuyên biệt và hệ quả thuật
toán trong mô hình này. Đối chiếu hiện tại chưa chứng minh được tuyên bố “đầu
tiên trên thế giới”, nên bản thảo không viết như vậy.

Những điều tác giả cần hiểu trước khi quyết định công bố là: mô hình cho sửa
những ô nào, hai chiều đổi quyết định khác nhau ra sao, vì sao không thể suy
từ bền sang đúng, và những kết quả âm trên dữ liệu nguồn. Mình đang chuẩn bị
gói bằng chứng đi kèm để các kết luận này có thể kiểm tra thuận tiện hơn; chưa
coi việc bạn cung cấp tên là duyệt bài.

[Bản PDF mới](../context-edit-stability-preview.pdf) ·
[Nguồn LaTeX](main.tex) ·
[Kết quả nguồn và giới hạn](../../experiments/E011-reused-source-stability/analysis.md).
