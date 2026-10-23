# Kết quả mới đang kiểm tra: khi nào sửa khóa làm quyết định kém bền?

Ngày 23-10-2026. Đây là kết quả nghiên cứu cục bộ; chưa kết luận về tính mới.

Bài toán mới không hỏi cách làm điểm benchmark cao hơn. Nó hỏi: giữ nguyên
ô đang xét và cả hàng chứa ô đó, phải sửa ít nhất bao nhiêu ô ở những hàng
khác để bộ kiểm tra đổi quyết định? Cả khóa dùng để chia nhóm lẫn giá trị
được kiểm tra đều được phép sửa. Một ô sửa tính một đơn vị chi phí.

Giả sử kiểm tra dựa trên các luật cùng dự đoán một cột. Trong mỗi nhóm có cùng
khóa, giá trị của ô đang xét phải xuất hiện nhiều hơn từng giá trị cạnh tranh.
Nếu hòa thì từ chối. Ô chỉ được chấp nhận khi vượt qua tất cả các luật.

**Kết quả vừa chứng minh:** với một ô ban đầu được chấp nhận, nếu mọi nhóm
liên quan đều có ít nhất hai hàng, sửa khóa không làm giảm chi phí tối thiểu
để lật quyết định. Cách tốt nhất vẫn đạt được bằng cách sửa giá trị trong nhóm.

Nếu có nhóm chỉ chứa chính hàng đang xét, tình hình khác: ta có thể sửa khóa
để đưa một hàng bên ngoài vào nhóm, tạo ra giá trị cạnh tranh. Chi phí chính
xác là số ô khóa phải sửa, cộng thêm một nếu cần sửa cả giá trị của hàng đó.
Chỉ khi cách này rẻ hơn cách lật một nhóm có nhiều hàng thì khóa mới giúp giảm
chi phí. Có nhóm đơn lẻ không có nghĩa là chi phí chắc chắn giảm.

Ví dụ: hai hàng `(a,b,c,y)` là `(0,0,0,0)` và `(1,0,0,1)`; kiểm tra
`(a,b) -> y` và `(a,c) -> y`. Hàng đầu đang được chấp nhận vì đứng một mình
trong cả hai nhóm. Chỉ sửa `a` của hàng thứ hai từ 1 thành 0 là đủ tạo hòa
1–1 và đổi quyết định. Nếu cấm sửa khóa, không thể lật bằng sửa giá trị ở
hàng thứ hai, vì hàng đó vẫn nằm ngoài nhóm.

Mình đã kiểm tra công thức trên toàn bộ 18.779 trường hợp được chấp nhận
trong miền bảng nhỏ đã định trước: không có sai khác so với duyệt đầy đủ
mọi sửa đổi. Ngoài ra, mô hình tối ưu tổng quát độc lập khớp 2.118 trường hợp.
Đây là kiểm tra tính toán, không phải 18.779 thí nghiệm độc lập trên dữ liệu thật.

**Điều có thể thành đóng góp:** mô tả chính xác ảnh hưởng của khóa có thể sửa,
và thuật toán chuyên biệt cho hai chiều đổi quyết định. Chiều từ chấp nhận sang
từ chối có công thức trực tiếp; chiều ngược lại vẫn cần xử lý tương tác giữa
các luật. Kết quả E008 cung cấp phép rút gọn hành động cho chiều ngược lại.

**Điều chưa được giải quyết:** công thức biên phiếu và ý tưởng sửa ít nhất đã
có trước. Cần kiểm tra sâu xem định lý chuyên biệt có bị công trình khác bao
hàm hay không, đo lợi ích tính toán trên bảng lớn hơn và đánh giá ý nghĩa trên
dữ liệu thực. Độ bền của một quyết định cũng không chứng minh dữ liệu là đúng.

Mình tiếp tục nghiên cứu theo các câu hỏi đó. Bản PDF 12 trang cũ được giữ làm
mốc đối chiếu; chưa dùng các kiểm tra nhỏ này để tuyên bố đã có bài mới đủ mạnh.

Bằng chứng: [chứng minh](../experiments/E009-singleton-characterization/theory.md),
[kết quả kiểm tra](../data/E009-v1-checks.json),
[đối chiếu tài liệu](../literature/singleton-collision-20261023.md).
