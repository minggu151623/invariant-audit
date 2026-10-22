# Hồ sơ nộp arXiv: bản chuẩn bị để tác giả duyệt

Đối chiếu hướng dẫn chính thức ngày 23-10-2026. Chưa đăng nhập, tạo tài khoản,
upload hoặc nộp bài. Các lựa chọn dưới đây chưa thay thế quyết định của tác giả.

## Nội dung khoa học cần chốt trước

Đọc [hướng dẫn tiếng Việt](reading-guide-vi.md) cùng
[bản PDF](arxiv-preview.pdf). Tên đã có: Trần Vũ Bảo Minh; affiliation:
Independent Researcher. Việc cung cấp tên chưa xác nhận đã duyệt nội dung.
arXiv yêu cầu khai báo việc dùng AI đáng kể và tác giả chịu trách nhiệm về
nội dung. Bài đã khai báo, nhưng việc bạn hiểu và chấp nhận nội dung còn chờ.
[Chính sách chính thức](https://info.arxiv.org/help/moderation/index.html).

Phản biện khoa học độc lập hiện chưa có. Đây là giới hạn chất lượng của dự án,
không phải khẳng định arXiv bắt buộc mọi bài phải có phản biện tạp chí trước.
Không có bảo đảm case study này đạt mức quan tâm khoa học mà moderator yêu cầu.

## Tài khoản và endorsement

Bạn tự tạo tài khoản bằng thông tin và email mình kiểm soát tại
[trang đăng ký arXiv](https://arxiv.org/user/register). Không cần cung cấp mật
khẩu hoặc mã xác thực trong cuộc trò chuyện.

Khi bắt đầu submission và chọn category, hệ thống cho biết bước endorsement.
Nếu cần người bảo trợ, yêu cầu được cấp từ luồng nộp bài. Người phù hợp là
người có chuyên môn và đủ điều kiện endorsement; endorsement không phải phản
biện xác nhận kết quả. Chưa biết trạng thái áp dụng cho tài khoản của bạn.
[Hướng dẫn endorsement](https://info.arxiv.org/help/endorsement.html).

## Category đang đề xuất

Giữ **cs.SE** là ứng viên vì bài tập trung vào đánh giá validator, oracle và
chỉ số kiểm thử. **cs.DB** có liên quan đến phần dữ liệu bảng. Đây là nhận định
về độ phù hợp nội dung của bản hiện tại, không phải xác nhận của moderator;
chưa chọn cross-list. [Mô tả category](https://arxiv.org/category_taxonomy).

## License chưa chọn

| Lựa chọn để cân nhắc | Quyền sử dụng được mô tả trong hướng dẫn arXiv |
| --- | --- |
| CC BY 4.0 | Cho phép chia sẻ, sửa đổi và sử dụng thương mại nếu ghi công. |
| arXiv perpetual, non-exclusive license | Cấp quyền phân phối cho arXiv; quyền tái sử dụng của người khác hạn chế hơn. |

License đã chọn cho một phiên bản là không thể thu hồi. Bạn cần tự chọn sau
khi hiểu quyền cấp và kiểm tra chính sách nơi dự định gửi tiếp nếu có. Trường
license trong hồ sơ vẫn để trống.
[Thông tin license chính thức](https://info.arxiv.org/help/license/index.html).

## Điền metadata và upload đúng tệp

[submission-fields-draft.json](submission-fields-draft.json) chuẩn bị title,
abstract, tên, affiliation và comments. Abstract ở
[abstract.txt](abstract.txt) là nguyên văn abstract hiện tại, 1.419 ký tự ASCII,
không có tiêu đề “Abstract”; dưới giới hạn 1.920 ký tự được hướng dẫn nêu.
Journal reference, DOI và mã báo cáo để trống vì chưa có những thông tin đó.
[Hướng dẫn metadata](https://info.arxiv.org/help/prep.html).

PDF giữ tên có dấu. Hướng dẫn metadata có lưu ý về ký tự và cách nhập dấu;
cần kiểm tra hiển thị trong form thực tế. Hồ sơ chuẩn bị thêm cách viết
`Tran Vu Bao Minh` làm phương án không dấu, chưa coi đó là lựa chọn bạn đã
duyệt. Không thay tên trong PDF hoặc đổi thứ tự tên một cách tự động.

Tệp upload nguồn là **arxiv-source-draft.zip** gồm bốn tệp. Chọn `main.tex` làm
tệp chính, **xelatex** làm processor vì nguồn dùng `fontspec`, và kiểm tra PDF
do arXiv tạo. Hệ thống hiện hỗ trợ XeLaTeX; nguồn dùng tên tệp font OpenType
theo hướng dẫn. Biên dịch Tectonic cục bộ đã đạt, nhưng chưa kiểm tra trên máy
chủ arXiv. [TeX Live tại arXiv](https://info.arxiv.org/help/faq/texlive.html).

Không dùng ZIP bằng chứng 35 tệp thay cho gói nguồn bốn tệp. PDF xem trước là
để đọc; với bài tạo từ TeX, hướng dẫn yêu cầu nộp nguồn thay vì chỉ PDF.
[Hướng dẫn nộp nguồn](https://info.arxiv.org/help/submit/index.html).

## Trước thao tác Submit cuối cùng

Đối chiếu lại title, tên tác giả, category, license và PDF do arXiv tạo. Xem
đủ dấu tên, công thức, hai hình, các bảng và tài liệu tham khảo. Xóa các dấu
“working draft” và câu chờ duyệt trong bản cuối sau khi nội dung đã được duyệt,
rồi biên dịch/kiểm tra lại. Không tự coi bản hiện tại là bản cuối đã chấp nhận.

Trạng thái của từng điều kiện cùng hash bản được kiểm tra nằm trong
[submission-readiness.json](submission-readiness.json). Posting còn phụ thuộc
moderation; công việc chỉ hoàn thành mục tiêu đăng bài khi có kết quả thực tế,
không phải khi bộ hồ sơ này được tạo.
