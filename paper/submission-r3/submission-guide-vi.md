# Hồ sơ nộp dự thảo R3

Kiểm tra ngày 05/11/2026. Đây là hồ sơ cho bản 10 trang sau khi bổ sung định lý
về độ khó tính toán. Chưa được tác giả duyệt và chưa nộp.

- Bản để đọc: [PDF R3](/Users/mac/Documents/ChatGPT/research_vibing/paper/context-edit-stability-r3/preview.pdf).
- Giải thích nội dung: [bản tiếng Việt có ví dụ](/Users/mac/Documents/ChatGPT/research_vibing/to_human/M33-theory-progress-vi.md).
- Thông tin điền form: [submission-fields-draft.json](/Users/mac/Documents/ChatGPT/research_vibing/paper/submission-r3/submission-fields-draft.json).
- Nguồn hiện tại: [source.zip](/Users/mac/Documents/ChatGPT/research_vibing/paper/context-edit-stability-r3/source.zip).

## Đã chuẩn bị

Tên bài: **Exact Context-Edit Stability for Plurality-Based Functional-Dependency
Checks**. Tác giả duy nhất trên PDF là **Trần Vũ Bảo Minh**, affiliation
**Independent Researcher**. Metadata đề xuất ghi **Tran Vu Bao Minh**, giữ nguyên
thứ tự tên. Hướng dẫn form yêu cầu ASCII; cũng cho phép một số lệnh dấu TeX,
nhưng cách hiển thị trên form thực chưa được kiểm tra. Abstract lấy nguyên văn
từ R3, có 1311 ký tự, dưới giới hạn 1920. Comments đề xuất: `10 pages, 3 tables,
no figures`. [Hướng dẫn metadata](https://info.arxiv.org/help/prep.html).

Đề xuất chuyên mục chính **cs.DB (Databases)**, vì trọng tâm là các kiểm tra FD
và thay đổi ô trong bảng dữ liệu. Chưa đề xuất cross-list; kết quả NP-complete
là một phần của bài, không khiến nó tự động thuộc mọi chuyên mục lý thuyết.
Đây là đánh giá về độ phù hợp, không phải xác nhận của moderator.
[Phân loại arXiv](https://arxiv.org/category_taxonomy).

Chọn bộ xử lý **XeLaTeX**, TeX Live **2025** theo hướng dẫn hiện hành. Bốn phông
Latin Modern được gọi bằng tên tệp trong nguồn đều có trong danh sách arXiv.
Kiểm tra cục bộ và checksum đã qua; biên dịch trên máy chủ vẫn chưa thực hiện.
[Bộ xử lý](https://info.arxiv.org/help/faq/texlive.html),
[phông sẵn có](https://info.arxiv.org/help/faq/font-info-tl2025.html).

## Giấy phép: lựa chọn này có ý nghĩa gì?

| Lựa chọn | Ý nghĩa thực tế theo mô tả của arXiv |
|---|---|
| arXiv perpetual, non-exclusive license | Cho arXiv quyền phân phối bài; không cấp quyền tái sử dụng rộng cho mọi người theo cách CC BY làm. |
| CC BY 4.0 | Cho người khác chia sẻ, chỉnh sửa và phát triển từ bài, kể cả thương mại, với yêu cầu ghi công. |

Ví dụ: nếu muốn bài được đọc công khai trên arXiv nhưng chưa muốn cấp quyền
chuyển thể rộng rãi qua CC BY, lựa chọn không độc quyền của arXiv phù hợp với
ý định đó. Nếu chủ động muốn cho phép cộng đồng tái sử dụng rộng với ghi công,
CC BY 4.0 thể hiện ý định ấy. Đây chỉ là hai lựa chọn để bạn so sánh; trang
chính thức còn liệt kê các giấy phép khác.

**Giấy phép của phiên bản đã nộp không thể thu hồi hay đổi lại.** Phiên bản
khác có thể dùng giấy phép khác; việc đó không thu hồi quyền đã cấp cho bản cũ.
Hồ sơ đang để trống giấy phép, không có lựa chọn mặc định thay bạn.
[Thông tin giấy phép chính thức](https://info.arxiv.org/help/license/index.html).

## Những bước còn phải thực hiện

1. Bạn đọc và chấp thuận nội dung R3 đứng tên mình, hoặc chỉ rõ phần cần giải
   thích/chỉnh sửa. Trước đây bạn đã nói chưa duyệt; lời “tiếp đi” chỉ cho phép
   tiếp tục nghiên cứu. arXiv yêu cầu sự đồng ý của tác giả và tác giả chịu
   trách nhiệm về nội dung. [Metadata](https://info.arxiv.org/help/prep.html),
   [chính sách sử dụng AI](https://info.arxiv.org/help/moderation/index.html).
2. Bạn chọn giấy phép. Sau khi được duyệt, bản phát hành bỏ câu “tác giả chưa
   duyệt”, giữ công khai việc sử dụng AI, rồi biên dịch và kiểm tra lại. Bản R3
   hiện tại được giữ làm mốc nội dung bạn đã đọc.
3. Tạo/đăng nhập tài khoản arXiv của bạn và hoàn tất xác minh. Trạng thái ghi nhận
   gần nhất là bạn chưa có tài khoản. Mình không cần mật khẩu hoặc mã xác minh
   trong cuộc trò chuyện.
4. Kiểm tra yêu cầu endorsement trên chính tài khoản/chuyên mục đó. Nếu cần,
   xử lý theo hướng dẫn trước khi hoàn tất nộp; chưa liên hệ ai thay bạn.
   Endorsement không phải peer review.
   [Hướng dẫn endorsement](https://info.arxiv.org/help/endorsement.html).
5. Tải nguồn LaTeX, chọn `main.tex`, kiểm tra PDF do arXiv tạo và thông tin form,
   rồi hoàn tất nộp trong phạm vi bạn đã đồng ý. Không tải riêng PDF thay nguồn
   cho bài được tạo từ LaTeX.
   [Hướng dẫn nộp](https://info.arxiv.org/help/submit/index.html).
6. Theo dõi trạng thái chính thức. Biên dịch thành công không chứng minh đã
   nộp; đã nộp cũng chưa chứng minh có bài công khai. Mã bài/trang công khai
   mới là bằng chứng cho mục tiêu đăng lên arXiv.

Các hồ sơ cũ cho bản 7 trang hoặc bài audit 12 trang vẫn được giữ làm lịch sử.
`paper/current-submission.json` trỏ đến đúng hồ sơ R3 để tránh dùng nhầm.
