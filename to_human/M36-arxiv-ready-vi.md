# R4 đã sẵn sàng để đăng arXiv

Ngày 07/11/2026. Bạn giao toàn quyền chỉnh bài và nhờ mình tự đánh giá. Kết
luận của mình: **bài đã đủ để đăng arXiv dưới dạng preprint**. Việc bấm nộp do
bạn làm, vì cần tài khoản của bạn, và chỉ nên làm sau khi bạn tự đọc bài.

## Vì sao mình cho là đủ

- **Đúng:**
  - Mình đã đọc lại từng bước chứng minh và không thấy lỗi toán học.
  - Kiểm tra bằng máy cũng khớp: E013 duyệt hết 81.893 trường hợp, và một
    script kiểm tra riêng chạy 10.900 bảng ngẫu nhiên ngoài phạm vi đó.
  - Một chỗ phát biểu thiếu phạm vi (chỉ đúng khi dòng đích ban đầu bị từ
    chối) đã được sửa, kèm ví dụ phản chứng.
- **Trung thực:** bài ghi rõ giới hạn, nói chưa có người phản biện độc lập,
  khai báo có dùng AI, và tách phần phân tích làm sau khi đã có kết quả.
- **Kiểm chứng được:** có link repo, mã commit và supplement có script replay.
- **Đúng chuẩn kỹ thuật arXiv:** `source.zip` biên dịch bằng pdfLaTeX ra 11
  trang, không cảnh báo, font nhúng đủ. Abstract nằm trong giới hạn ký tự.

## Những gì đã cải thiện lần này

- **Động lực:** dẫn hai hệ thống làm sạch dữ liệu thật có dùng lựa chọn theo đa
  số (Bohannon và cộng sự, SIGMOD 2005; Horizon, PVLDB 2021). Thêm ví dụ thực
  tế về bộ luật không laminar.
- **Tính được w(F):** thêm câu nói w(F) tính được trong thời gian đa thức (định
  lý Dilworth, quy về bài toán matching; trích Fulkerson 1956).
- **Quy hoạch động:** ghi cận cụ thể thay cho lời khẳng định chung chung.
- **Các bài liên quan:** thêm so sánh với resilience (Freire và cộng sự), mua
  phiếu trong bầu cử (bribery, Faliszewski và cộng sự) và kiểm soát bầu cử
  (Bartholdi, Tovey, Trick). Mình đã tra lại thông tin xuất bản của từng bài.
- **Câu hỏi mở:** thêm đoạn câu hỏi mở cuối bài: tỉ lệ có đạt được ở mọi quy
  mô không, chưa có thuật toán xấp xỉ, và các mở rộng.
- **Gọn hơn:** rút gọn mục 6, bỏ Table 4 vốn lệch khỏi kết quả chính, và đổi
  tên nội bộ (E008–E013) thành tên mô tả.

## Điểm yếu vẫn còn (không ngăn việc đăng arXiv)

- Chưa có người trong ngành đọc chứng minh. Mình không phải phản biện độc lập.
- Tìm tài liệu có mục tiêu, chưa hệ thống, nên không khẳng định được "đầu tiên".
- Chưa có dữ liệu thực với schema không laminar.
- Mô hình hẹp. Để vào hội nghị lớn nhiều khả năng cần mở rộng thêm.

## Các bước nộp

Mọi thông tin cần điền nằm trong
`paper/context-edit-stability-r4/arxiv-metadata.md`.

1. Đọc bài ít nhất mục 3. Bạn đứng tên một mình nên phải tự trả lời được nếu
   có người hỏi.
2. Vào arXiv, chọn New Submission, chọn giấy phép:
   - Giấy phép non-exclusive của arXiv: chặt nhất, dễ đăng tạp chí sau này.
   - CC BY 4.0: ai cũng được dùng lại, miễn ghi nguồn.
3. Chọn mục cs.DB, có thể thêm cs.DS.
4. Tải lên `paper/context-edit-stability-r4/source.zip`.
5. Điền tiêu đề, tác giả, abstract và comments từ file metadata.
6. Xem bản PDF arXiv tự biên dịch, so với `preview.pdf`, rồi bấm Submit.
7. Nếu arXiv yêu cầu endorsement, nhờ một người đã đăng bài ở cs.DB xác nhận.
