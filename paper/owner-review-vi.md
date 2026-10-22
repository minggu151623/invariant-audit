# Bản thảo hiện tại và những việc cần chốt

Ngày 23-10-2026. Đây là bản để bạn đọc và phản biện, chưa phải bài đã được nộp.

Bài nghiên cứu hiện có hai phần bằng chứng. Phần đầu kiểm toán lại hai bộ thử
tổng hợp của dự án, giải thích vì sao điểm hoàn hảo chưa chứng minh hiệu năng
bên ngoài và vì sao Brier giảm trong khi một chỉ số calibration tăng. Phần mới
khóa phép thử trước khi đọc các cặp dữ liệu tham chiếu Beers, Flights và Rayyan.
Các nhãn tham chiếu do nhóm khác cung cấp; mình không dựng nhãn theo validator.

Kết quả mới có đánh đổi rõ: trên Flights, cách đánh dấu mọi ô tham gia xung đột
quy tắc từ chối nhầm 74,4% ô khớp tham chiếu. Cách chỉ đánh dấu giá trị thiểu số
hạ mức đó xuống 8,0%, nhưng bỏ sót 12,2% ô không khớp tham chiếu. Dự đoán lookup
cải thiện Brier trên cả ba bộ không được ủng hộ đầy đủ vì khoảng của Flights
cắt 0. Bài giữ lại kết quả này và các trường hợp hiệu năng kém.

Các giới hạn cần hiểu trước khi đứng tên:

- “Khớp tham chiếu” không đồng nghĩa dữ liệu hoàn chỉnh hoặc đúng trong mọi ứng
  dụng. Một ô trống giống nhau ở cả hai bảng vẫn được tính là khớp.
- Các cách kiểm tra là baseline đơn giản, không phải thuật toán mới hoặc bản
  sao của Raha. Không có chứng minh rằng M1 cũ chuyển sang dữ liệu thật bị giảm điểm.
- Những vấn đề tổng quát về lỗi sinh nhân tạo và gán lỗi cho ô đã có trong
  nghiên cứu trước. Đóng góp dự kiến là case study định lượng có thể kiểm tra,
  không phải nhận các ý tưởng đó là phát minh của mình.
- Toàn bộ thiết kế, code, phân tích và bản nháp được AI hỗ trợ đáng kể. Tính
  toán đã được kiểm tra nhưng chưa có phản biện khoa học độc lập. Bạn cần đọc,
  hiểu và chịu trách nhiệm cho bản cuối nếu là tác giả đứng tên.

Bạn đã cung cấp tên **Trần Vũ Bảo Minh** và affiliation **Independent Researcher**.
Bài giữ nguyên thứ tự và dấu tiếng Việt của tên này. Dự kiến có một tác giả;
bạn chưa có tài khoản arXiv. Các việc còn cần chốt là license/category và
việc bạn đọc, hiểu, duyệt nội dung. Thông tin tác giả lấy từ câu trả lời của bạn.
Việc tạo tài khoản và endorsement sẽ xử lý sau khi có bản khoa học bạn chấp nhận;
không có cam kết rằng arXiv sẽ nhận đăng.
