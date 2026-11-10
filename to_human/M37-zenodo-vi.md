# Rà soát R4 và chuẩn bị đăng Zenodo

Ngày 10/11/2026. Bạn quyết định đăng Zenodo trước và nhờ mình rà lại bài. Mình
đã rà, sửa và chuẩn bị xong hai file để tải lên. Việc đăng nhập, chọn giấy
phép và bấm Publish là của bạn.

## Rà soát tìm thấy gì

1. **Câu hỏi mở đầu tiên của bài trả lời được.** Bản cũ hỏi: tỉ lệ w(F) có đạt
   được khi chi phí tối ưu lớn hơn 1 không? Mình chứng minh được và thêm vào
   bài thành Proposition 1:
   - Nếu cột y có ít nhất k+1 giá trị thì với mọi bộ luật, có bảng mà sửa được
     khóa tốn k ô, còn không sửa được khóa tốn đúng w(F)·k ô.
   - Nếu y chỉ có 2 giá trị và bộ luật là {a,b}, {a,c} thì hai chi phí lệch
     nhau nhiều nhất 1 ô. Tức là tỉ lệ 2 chỉ xảy ra khi chi phí bằng 1.
2. **Abstract gọi thí nghiệm của chính mình là "an earlier study".** Người đọc
   sẽ hiểu là bài của người khác. Đã sửa thành thí nghiệm benchmark của chính
   chúng ta.
3. **Lỗi nhỏ:** "RHS" dùng mà chưa định nghĩa; bài nhắc tới supplement nhưng
   không nói nó ở đâu; file PDF không có tiêu đề và tên tác giả trong
   metadata. Cả ba đã sửa.

Phần còn lại của bài mình đọc lại và không thấy lỗi.

## Kiểm chứng kết quả mới (E014)

Mình khóa protocol trước, rồi mới viết code, rồi chạy một lần. Mọi dự đoán
đều khớp, không phải sửa gì sau khi chạy.

- Phần (a): dựng 9 bảng theo công thức và 1 bảng đối chứng. Máy duyệt hết
  5.594.099 cách sửa rẻ hơn mức dự đoán, không cách nào làm dòng đích được
  chấp nhận.
- Phần (b): duyệt hết 74.612 bảng có từ 1 đến 6 dòng. Trong 34.393 bảng bị từ
  chối, không bảng nào lệch quá 1 ô.

Chứng minh và code đều do AI viết và AI kiểm. Chưa có người độc lập đọc.

## Bài bây giờ

12 trang, ngày 10/11/2026. `check_revision.py` chạy lại toàn bộ và đạt: biên
dịch bằng cả hai engine không cảnh báo, supplement giải nén ra chạy lại được
cả E013 lẫn E014.

## Điểm yếu còn lại

- Chưa có người trong ngành đọc chứng minh, kể cả Proposition 1 mới.
- Proposition 1(b) chỉ xử lý một bộ luật gồm hai luật. Trường hợp y có từ 3
  đến k giá trị còn mở.
- Tìm tài liệu có mục tiêu, chưa hệ thống. Không khẳng định được "đầu tiên".
  Mình chưa lấy được toàn văn bài Tao và cộng sự (FAW 2021).
- Chưa có dữ liệu thực với bộ luật không laminar.
- Mô hình hẹp: một cột y, chi phí đơn vị, hòa thì từ chối.

Các điểm này đều đã ghi trong bài. Chúng không ngăn việc đăng preprint, nhưng
sẽ là điểm bị hỏi nếu nộp hội nghị.

## Các bước đăng Zenodo

Mọi trường cần điền nằm trong
`paper/context-edit-stability-r4/zenodo-metadata.md`.

1. Đọc file PDF, ít nhất mục 3. Bạn đứng tên một mình.
2. Kiểm tra các commit mới đã có trên GitHub, vì PDF trích mã commit.
3. Vào zenodo.org, đăng nhập, chọn New upload.
4. Tải lên hai file trong `paper/context-edit-stability-r4/zenodo/`:
   - `schema-width-editable-keys.pdf`
   - `schema-width-editable-keys-supplement.zip`
5. Điền các trường theo file metadata: Resource type là Publication →
   Preprint; tiêu đề; tác giả; mô tả là abstract; từ khóa; Related works trỏ
   tới repo GitHub.
6. Chọn giấy phép. Đây là quyết định của bạn:
   - CC BY 4.0: Zenodo gợi ý sẵn, ai cũng được dùng lại miễn ghi nguồn. arXiv
     và hầu hết tạp chí chấp nhận.
   - Giấy phép chặt hơn như CC BY-NC-ND 4.0: hạn chế dùng lại, một số nơi
     open-access không nhận.
   - Giấy phép Creative Commons đã cấp thì không rút lại được với các bản đã
     phát hành.
7. Bấm Preview để xem lại, rồi Publish.

## Ba điều cần biết trước khi bấm Publish

- **Không sửa được file sau khi Publish.** Muốn sửa phải tạo phiên bản mới, có
  DOI riêng. Bản cũ vẫn công khai.
- **Zenodo không phản biện.** Có DOI không có nghĩa là bài đã được kiểm tra.
- **Sau này vẫn đăng arXiv được.** `source.zip` và `arxiv-metadata.md` đã cập
  nhật theo bản 12 trang.

## Tùy chọn: in DOI vào PDF

Zenodo cho giữ trước DOI khi tạo bản nháp (nút Get a DOI now). Nếu bạn muốn
DOI xuất hiện trong PDF, gửi mình DOI đó, mình thêm vào bài và dựng lại file
trước khi bạn Publish. Không làm bước này cũng không sao.
