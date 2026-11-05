# Giải thích bài mới và lựa chọn giấy phép

Ngày 24/10/2026. Bản giải thích bổ sung cho bản thảo 7 trang
*Exact Context-Edit Stability for Plurality-Based Functional-Dependency Checks*.

Bạn đã trả lời: chưa duyệt nội dung; chưa chọn giấy phép; chưa có tài khoản
arXiv. Các câu trả lời này được giữ nguyên. Tài liệu này giúp bạn hiểu để quyết
định sau, không ghi nhận thay bạn một quyết định công bố.

## Bài đang nghiên cứu điều gì?

Giả sử bảng có mã tạp chí và tên tạp chí. Bộ kiểm tra gom các hàng cùng mã,
rồi chấp nhận tên của hàng đang xét khi tên ấy xuất hiện nhiều hơn từng tên
cạnh tranh. Hòa phiếu thì từ chối. Nếu dùng nhiều cách chia nhóm, hàng phải
vượt qua tất cả các cách đó.

Ở đây, “cột khóa” là cột dùng để chia nhóm, không nhất thiết là khóa duy nhất
của cơ sở dữ liệu. Bộ kiểm tra dùng số đông để đánh giá sự nhất quán; nó không
biết chắc tên đúng ngoài đời là gì.

Bài giữ nguyên toàn bộ hàng đang xét và hỏi: **cần sửa ít nhất bao nhiêu ô ở
các hàng khác để kết luận đổi?** Có thể sửa cả cột chia nhóm lẫn cột tên đang
kiểm tra. Mỗi ô sửa tính một đơn vị, không thêm hoặc xóa hàng. Tất cả các luật
đang xét phải kiểm tra cùng một cột giá trị. Đây là phạm vi của mô hình và các
chứng minh, không phải mô tả mọi hệ thống làm sạch dữ liệu.

Nếu đáp án là 3, mọi cách sửa tối đa 2 ô đều giữ kết luận và có một cách sửa
3 ô làm kết luận đổi. Con số này gọi là bán kính ổn định. Nó không phải xác
suất hàng đúng và không đưa ra một bản sửa dữ liệu được xác nhận là đúng.

## Đóng góp có thể trình bày là gì?

**Kết quả thứ nhất: mô tả chính xác khi nào sửa cột chia nhóm giúp lật một
kết luận đang chấp nhận với ít ô sửa hơn.**

Với nhóm có nhiều hơn một hàng, chi phí lật là một nửa khoảng cách giữa số
phiếu của giá trị mục tiêu và đối thủ mạnh nhất, làm tròn lên. Ví dụ có 3
phiếu A và 1 phiếu B: đổi một A ở hàng khác thành B tạo 2–2, đủ để từ chối.
Cho sửa thêm cột chia nhóm cũng không làm rẻ hơn trong trường hợp này.

Nhóm chỉ có hàng mục tiêu thì khác. Nếu giữ cột chia nhóm, sửa các hàng bên
ngoài không thay đổi được nhóm ấy. Nếu cho sửa cột chia nhóm, có thể đưa một
hàng mang giá trị B vào nhóm để tạo hòa A–B. Chi phí là số ô chia nhóm cần
đổi, cộng một nếu còn phải đổi giá trị của hàng được đưa vào.

Khi có nhiều luật, bài so sánh chi phí rẻ nhất của hai loại nhóm này. Sửa cột
chia nhóm chỉ giúp khi đường đi qua nhóm đơn lẻ rẻ hơn đường đi qua các nhóm
còn lại. Có nhóm đơn lẻ là điều kiện cần, chưa đủ. Đây là phát biểu có chứng
minh trong mô hình đã nêu, không chỉ là quan sát từ ví dụ.

**Kết quả thứ hai: bỏ bớt phương án sửa mà vẫn giữ được ít nhất một nghiệm
tối ưu để chuyển từ từ chối sang chấp nhận, nếu nghiệm tồn tại.**

Chiều này khó hơn vì phải làm mọi luật cùng chấp nhận. Một sửa đổi có thể ảnh
hưởng nhiều nhóm. Chứng minh cho biết một số phương án luôn có thể được thay
bằng phương án khác tốn không nhiều hơn và không làm xấu bất kỳ so sánh phiếu
nào. Vì vậy có thể bỏ các phương án bị lấn át trước khi giải tối ưu.

Đây là rút gọn chính xác, không phải mẹo chấp nhận mất nghiệm tốt. Tuy nhiên,
số phương án mỗi hàng vẫn có thể tới 2^q + 1, với q là số cột chia nhóm.
Không có kết luận rằng thuật toán luôn nhanh hoặc xử lý được mọi bảng lớn.

## Điểm mới mạnh đến đâu?

Ý tưởng tìm số ô sửa tối thiểu, dùng phản thực, biên phiếu hoặc tối ưu nguyên
đã có trong nghiên cứu trước. Bài không nên nhận chúng là phát minh của mình.
Đóng góp đề xuất nằm ở **hai kết quả cấu trúc chuyên biệt bên trên và hệ quả
thuật toán của chúng**. Đối chiếu tài liệu hiện tại chưa xác lập được quyền
ưu tiên “đầu tiên trên thế giới”. Các kiểm tra do cùng hệ thống thực hiện
cũng không phải thẩm định khoa học độc lập.

Đánh giá của mình: hướng này có nội dung toán học cụ thể hơn bài audit cũ,
nhưng phạm vi còn hẹp và giá trị ứng dụng chưa mạnh. Mình chưa có cơ sở gọi
đây là đột phá hoặc một phương pháp làm sạch dữ liệu tốt hơn.

## Dữ liệu thực nói gì, và chưa nói được gì?

Trên ba bảng Beers, Flights và Rayyan đã dùng trước đây trong dự án:

- Với các ô đang được chấp nhận, có 1.134 lần bán kính giảm khi cho sửa cột
  chia nhóm. Trong đó 1.133 lần chuyển từ không thể lật bằng mô hình giữ khóa
  sang có thể lật; chỉ một lần bán kính hữu hạn giảm từ 2 xuống 1. Phần lớn
  hiệu ứng vì vậy gắn với nhóm đơn lẻ.
- Trong 32 ô đang bị từ chối được chọn theo quy tắc đã định, có 30 cặp giải
  được chính xác. Cả 30 đều có cùng chi phí ở hai mô hình. Hai bài toán cho
  sửa đầy đủ hết giới hạn 5 giây, chưa xác định được đáp án tối ưu. Không
  được tính chúng thành bằng chứng cải thiện hoặc bằng nhau.
- Có 1.493 ô đang được chấp nhận, có bán kính ít nhất 2, nhưng vẫn khác bản
  tham chiếu. Quyết định bền vẫn có thể sai theo tham chiếu; tham chiếu cũng
  không được xem là chân lý đã thẩm định tuyệt đối.

Các bảng này đã được xem trong nghiên cứu trước, nên đây là bằng chứng khám
phá trên nguồn dùng lại, không phải kiểm định mù mới. Kiểm tra trên bảng dựng
sẵn hỗ trợ việc kiểm tra công thức và chương trình, không thay thế chứng
minh hoặc đảm bảo hiệu quả ngoài thực tế. Bản thảo giữ cả kết quả âm và hết
thời gian.

## Giấy phép: cho đọc và cho tái sử dụng là hai việc khác nhau

Theo [hướng dẫn arXiv](https://info.arxiv.org/help/license/index.html), bài đã
đăng đều được đọc và tải miễn phí. Hai lựa chọn đã hỏi trước đó khác nhau ở
quyền phân phối và tái sử dụng:

| Lựa chọn | Ý nghĩa thực tế |
| --- | --- |
| [arXiv non-exclusive](https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html) | Bạn giữ bản quyền và cấp cho arXiv quyền phân phối lâu dài, không độc quyền. Giấy phép này tự nó không cấp rộng rãi cho mọi người quyền chuyển thể hoặc khai thác lại nội dung. |
| [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Bạn vẫn giữ bản quyền, đồng thời cho phép người khác chia sẻ và chuyển thể, kể cả thương mại, theo điều kiện ghi công, dẫn giấy phép và báo thay đổi. Họ không được ngụ ý bạn bảo trợ việc sử dụng của họ. |

Ví dụ: CC BY cho phép người khác đưa hình của bài vào một sách bán thương
mại nếu tuân thủ điều kiện. Giấy phép arXiv riêng không tự cấp quyền rộng
như vậy; việc sử dụng có thể cần phép riêng hoặc dựa trên ngoại lệ pháp luật.
Ghi công không có nghĩa người khác được nhận mình là tác giả của bài gốc.

Nếu mục tiêu của bạn là cho arXiv phân phối mà chưa muốn cấp quyền tái sử dụng
rộng, giấy phép arXiv phù hợp với ý muốn đó. Nếu muốn người khác dễ chia sẻ,
dịch hoặc phát triển tài liệu, kể cả trong sản phẩm thương mại, CC BY phù hợp
với ý muốn ấy. Đây là hai lựa chọn đang giải thích, không phải toàn bộ danh
sách arXiv cung cấp. Chưa có lựa chọn nào được ghi thay bạn.

arXiv nói giấy phép của **từng phiên bản đã đăng** không thể đổi lại; các
phiên bản khác có thể mang giấy phép khác. Đăng phiên bản mới không thu hồi
quyền đã cấp cho bản cũ. Với CC BY, quyền của người đang tuân thủ giấy phép
không thể bị thu hồi. Nếu sau này nhắm một tạp chí cụ thể, cần xem chính sách
của tạp chí đó thay vì suy đoán một lựa chọn phù hợp với tất cả.

## Tài khoản và bước tiếp theo

Bạn xác nhận chưa có tài khoản. Việc hiểu và chỉnh nội dung vẫn có thể làm
trước. Bạn nói đúng: [arXiv không thực hiện peer review](https://info.arxiv.org/help/moderation/index.html).
Họ có kiểm duyệt nội dung; việc nộp không đảm bảo sẽ được đăng. Người nộp
lần đầu còn cần đáp ứng [quy trình endorsement](https://info.arxiv.org/help/endorsement.html),
theo tình trạng tài khoản và lĩnh vực nộp thực tế.

Hiện trạng là một bản thảo để xem xét, chưa phải bài đã đăng. Không cần chốt
giấy phép chỉ để đọc bản giải thích này. Bước tiếp theo về nội dung là xác
định xem hai kết quả trên có phải đóng góp bạn muốn đứng tên và hiểu được hay
còn cần giải thích/chỉnh sửa; chưa ghi nhận sự đồng ý của bạn ở bước này.

## Nguồn để đối chiếu

- [Nguồn bản thảo](../paper/context-edit-stability/main.tex): định nghĩa, bổ đề và định lý.
- [Kết quả và giới hạn E011](../experiments/E011-reused-source-stability/analysis.md).
- [Đối chiếu đóng góp với công trình trước](../literature/structural-theorem-comparison-20261023.md).
- Các trang chính thức về giấy phép và arXiv bên trên được kiểm tra ngày 24/10/2026.
