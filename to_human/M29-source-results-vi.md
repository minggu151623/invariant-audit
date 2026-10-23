# Kết quả trên dữ liệu thực và hướng viết bài mới

Ngày 23-10-2026. Chưa nộp arXiv. Ba bảng Beers, Flights và Rayyan đã được dùng
trong dự án trước đây; đây không phải kiểm định mù trên dữ liệu chưa từng xem.

Mình đã kiểm tra toàn bộ 18.734 ô mục tiêu thuộc chín nhiệm vụ. Có 13.762 ô
được bộ kiểm tra chấp nhận. Với các ô này, kết quả về ảnh hưởng của sửa khóa là:

- 1.133 ô: nếu giữ khóa thì không thể lật quyết định, nhưng cho sửa khóa thì
  lật được. Đây là các trường hợp nhóm đơn lẻ.
- Một ô: chi phí tối thiểu giảm từ 2 xuống 1.
- Không có ô nào thiếu nhóm đơn lẻ mà lại giảm chi phí, đúng với định lý.

Trường hợp giảm từ 2 xuống 1 là ô journal_title ở hàng 644 của Rayyan. Ô này
thuộc hai nhóm có 4 và 1 hàng. Giữ khóa thì cần sửa hai giá trị ở hàng khác;
cho sửa khóa thì chỉ cần đổi journal_issn ở hàng 1 để đưa một đối thủ vào nhóm
đơn lẻ. Hàng 644 được giữ nguyên. Toàn bộ phương án sửa đã được kiểm tra lại.

**Kết quả âm cần giữ trong bài:** với chiều làm ô đang bị từ chối được chấp
nhận, 30 cặp đã giải chính xác chưa cho thấy sửa khóa giúp giảm chi phí. Hai
trường hợp khác của Rayyan hết giới hạn năm giây mà chưa tìm được phương án
trong mô hình đầy đủ. Mình không thay chúng bằng trường hợp dễ hơn hay chạy
lại để lấy kết quả đẹp hơn.

Một giới hạn khác cũng được xác nhận: **bền không có nghĩa là đúng**. Có 1.493
ô được chấp nhận, cần ít nhất hai sửa đổi để lật quyết định, nhưng giá trị vẫn
khác bản tham chiếu. Vì vậy không thể dùng bán kính ổn định làm xác suất đúng.

Sau đối chiếu sâu với công trình trước, mình sẽ không nhận ý tưởng chia giá trị
khóa thành khớp/không khớp, phản thực hoặc tối ưu số ô sửa là mới. Bài mới sẽ
tập trung vào hai kết quả chuyên biệt: phép rút gọn hành động vẫn giữ tối ưu,
và công thức chính xác cho nhóm đơn lẻ. Các giới hạn mô hình và kết quả âm sẽ
được ghi trong phần chính của bài.

Các kiểm tra tính toán đã hoàn tất, gồm 162 bài kiểm tra nhỏ trước khi chạy,
hai lượt tính giống hệt nhau cho toàn bộ ô được chấp nhận, và kiểm tra lại
26.453 phương án sửa hữu hạn trên dữ liệu nguồn. Đây vẫn là kiểm tra do cùng
môi trường nghiên cứu thực hiện, không phải một nhóm độc lập xác nhận.

Tiếp theo là soạn bản thảo mới xoay quanh đóng góp này và chuẩn bị gói bằng
chứng. Mục tiêu hiện tại không còn là cố hoàn thiện bản bài audit cũ.

Nguồn: [phân tích đầy đủ](../experiments/E011-reused-source-stability/analysis.md),
[kiểm tra kết quả](../data/E011-v1-checks.json),
[đối chiếu định lý](../literature/structural-theorem-comparison-20261023.md).
