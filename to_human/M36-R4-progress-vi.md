# R4: bản thảo mới đặt kết quả "độ rộng schema" làm trọng tâm

Ngày 07/11/2026. Đây là báo cáo tiến độ nghiên cứu, **không phải** đề nghị nộp
bài. Bạn chưa duyệt nội dung, chưa chọn giấy phép; mình không suy ra hai việc đó.

## Đã làm trong lượt này

1. **Đọc trực tiếp toàn bộ 18 trang slide SYNASC 2026** (Miclăuș, Mureșan, Popa)
   về thao túng bầu cử qua truyền thông. Đây là công trình gần nhất về kỹ thuật
   mà mình tìm được. Đã ghi đối chiếu vào
   `literature/schema-width-positioning-20261105.md` (phần Addendum 2026-11-07).
   Không tìm thấy bản full paper công khai.
2. **Rà lại chứng minh E013 từng dòng**: chuẩn hóa, bất biến margin chặn ở 1,
   các nhóm không tới hạn trong phép dựng cận, giả định miền giá trị và chi phí.
   Không thấy lỗi. Biên bản: `experiments/E013-schema-width/proof-audit-20261107.md`.
3. **Viết R4** tại `paper/context-edit-stability-r4/`: PDF 10 trang, source,
   supplement và script replay chỉ-đọc. R3 giữ nguyên.

## Kết quả chính của R4, nói ngắn gọn

Bài toán: một dòng đích đang bị luật FD kiểu "đa số" từ chối. Muốn nó được
chấp nhận thì phải sửa ít nhất bao nhiêu ô ở các dòng khác?

- `rho_fixed`: chỉ được sửa cột giá trị y.
- `rho_full`: được sửa cả cột khóa (cột dùng để gom nhóm) lẫn y.

Định lý: `rho_full ≤ rho_fixed ≤ w × rho_full`, trong đó w chỉ phụ thuộc vào
danh sách luật. Với mỗi cột khóa, lấy các luật chứa cột đó, đếm nhiều nhất bao
nhiêu bộ khóa mà không bộ nào chứa bộ kia; w là số lớn nhất.

Ví dụ: luật {a,b} và {a,c} có w=2. Bảng 4 dòng trong bài cho thấy sửa 1 ô
khóa thay được 2 ô y. Với **mọi** bộ luật, có bảng đạt đúng tỉ lệ w. Hai chi phí
bằng nhau trên mọi bảng **khi và chỉ khi** bộ luật laminar: hai bộ khóa có
chung cột thì bộ này phải chứa bộ kia.

Hệ quả thực tế: với luật laminar (rất phổ biến, ví dụ mỗi luật một cột khóa),
có thể bỏ hẳn biến khóa khỏi bài toán tối ưu mà không mất gì. Điều này giải
thích vì sao thí nghiệm E011 trên Beers/Flights/Rayyan không thấy lợi ích nào:
cả 9 schema đều laminar, nên lợi ích đó **không thể** xảy ra. Đây là lỗi thiết
kế của E011, bài viết công khai nó thay vì đổi luật sau khi thấy kết quả.

## So với slide SYNASC 2026: giống gì, khác gì

**Giống:** cả hai cùng dùng ý tưởng "trên một chuỗi tập lồng nhau, một hành động
ở đúng đầu chuỗi trội hơn các hành động khác", và cùng chia thành chuỗi
(Dilworth). Vì vậy R4 **không** nhận kỹ thuật này là mới.

**Khác:**
- Slide giải một bài toán tối ưu trong *một* không gian hành động (chọn chiến
  lược truyền thông). R4 so sánh *hai* không gian chỉnh sửa và đưa ra tỉ lệ
  chính xác cho từng schema, kèm điều kiện "khi và chỉ khi".
- Laminar ở slide là trên tập cử tri. Ở R4 là trên tập cột; các nhóm dòng luôn
  cùng chứa dòng đích nên không bao giờ rời nhau, thuật toán của họ không áp
  dụng nguyên dạng.
- Slide coi hòa là thắng (co-winner); R4 coi hòa là bị từ chối, và phép dựng cận
  sắc dựa vào điều này.

Mình mới xem slide, chưa đọc chứng minh đầy đủ, nên không loại trừ được việc
bài đầy đủ hoặc bài Tao và cộng sự (FAW 2021) có bổ đề tương tự.

## Đánh giá thẳng về độ mới và ý nghĩa

- **Điểm mạnh:** đây là một mệnh đề cấu trúc gọn, có cận trên, cận dưới đạt
  được cho *mọi* schema, và đặc trưng chính xác. Nó trả lời một câu hỏi cụ thể
  ("khi nào cần nghi ngờ cột khóa?") và giải thích được một kết quả âm thật.
- **Điểm yếu:**
  - Kết quả hẹp: cần cùng một cột y, chi phí đơn vị, hòa bị từ chối, không
    ràng buộc hợp lệ. Đổi một giả định là chứng minh có thể hỏng.
  - Kỹ thuật chứng minh (chuỗi, dominance) là kỹ thuật quen thuộc. Phần đóng góp
    nằm ở phát biểu và phép dựng, không ở công cụ mới.
  - Chưa có ai ngoài dự án kiểm tra chứng minh. Các lần "kiểm tra" đều do AI.
  - Chưa có dữ liệu thực cho thấy tỉ lệ w xuất hiện; E011 chỉ có schema laminar.
  - Tìm kiếm tài liệu có mục tiêu, chưa hệ thống. Không thể khẳng định "đầu tiên".
- **Mức độ phù hợp:** một preprint lý thuyết ngắn trong cs.DB hoặc cs.DS là hợp
  lý về nội dung. Trước khi nộp nên có ít nhất một người hiểu lý thuyết đọc lại
  chứng minh Theorem 1–2.

## Kiểm tra đã chạy

- Biên dịch R4 bằng Tectonic: 10 trang, không cảnh báo, font nhúng đầy đủ.
  Đã render và xem từng trang.
- `replay_e013.py` kiểm lại toàn bộ 81.893 hồ sơ nghiệm bằng code viết riêng,
  và tùy chọn `--reenumerate` chạy lại phép duyệt gốc, khớp từng dòng.
- Kiểm tra các file khoa học cũ và R3 không bị thay đổi.

## Bạn cần quyết định gì (không gấp)

Chưa cần quyết định nộp. Nếu muốn đi tiếp theo hướng xuất bản, việc có ích nhất
là nhờ một người có chuyên môn đọc chứng minh, và tự đọc mục 3 của R4 xem phần
giải thích có dễ hiểu không. Giấy phép và tài khoản arXiv vẫn để sau.
