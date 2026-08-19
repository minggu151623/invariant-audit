# InvariantAudit Research Workspace Design

- **Ngày thiết kế:** 2026-08-19
- **Trạng thái:** Approved design
- **Tên dự kiến của public GitHub repository:** `invariant-audit`
- **Đường dẫn của spec này:** `docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md`

## 1. Mục tiêu và phạm vi

InvariantAudit là một workspace nghiên cứu có lịch sử Git rõ ràng, trong đó mỗi
claim có thể lần ngược về protocol, result, data và milestone đã được kiểm chứng.
Thiết kế này mô tả quy ước lưu trữ, thứ tự thực hiện, provenance, review và
publication gate cho một repository dự kiến public.

Repository GitHub và remote public chưa được tạo bởi spec này. Việc tạo remote,
push, đăng nhập GitHub hoặc công bố nội dung là các hành động riêng, cần có
authority tương ứng. Workspace local vẫn phải tuân thủ toàn bộ quy ước dưới đây
trước khi remote được cấu hình.

## 2. Quy tắc nguồn sự thật

Mỗi định dạng có đúng một vai trò:

1. **Markdown là nguồn chính cho nội dung nghiên cứu của con người.** Câu hỏi,
   hypothesis, protocol, diễn giải result, literature note, figure description,
   milestone summary, content draft và paper prose đều được viết trước hết bằng
   Markdown. Markdown phải chứa liên kết tới các commit và file dữ liệu liên quan
   khi một claim phụ thuộc vào chúng.
2. **YAML là nguồn chính cho state vận hành.** State hiện tại của workspace được
   lưu trong `state/`, với file canonical là `state/workspace.yaml` khi file state
   được khởi tạo. YAML chỉ mô tả trạng thái, ID, đường dẫn, commit reference và
   quan hệ máy đọc được; nó không thay thế narrative Markdown.
3. **CSV và JSONL là định dạng chính cho data dạng dòng.** CSV dùng cho bảng có
   schema ổn định; JSONL dùng cho record có schema linh hoạt hoặc nested fields.
   Mỗi data file phải có tên/metadata cho biết experiment, nguồn, đơn vị và
   version hoặc commit tạo ra nó. Một data file không được là nơi duy nhất chứa
   diễn giải khoa học.
4. **Generated output không phải nguồn sự thật mới.** Bản render, chart, export
   hoặc bản chuyển đổi phải trỏ về Markdown và data nguồn; nếu có khác biệt,
   source Markdown/data và provenance quyết định nội dung đúng.

## 3. Cấu trúc workspace chuẩn

Các thư mục sau là namespace chuẩn của dự án. Spec này chỉ định nghĩa cấu trúc;
nó không yêu cầu scaffold các file nghiên cứu khác.

| Thư mục | Nội dung được phép và trách nhiệm |
| --- | --- |
| `milestones/` | Milestone records bằng Markdown, mục tiêu, tiêu chí hoàn thành, evidence và trạng thái verification. |
| `experiments/` | Protocol, run record, result narrative và data của các experiment. Protocol và result là Markdown; data dạng dòng là CSV/JSONL. |
| `literature/` | Literature notes bằng Markdown, citation metadata, claim được trích dẫn và quan hệ với milestone hoặc experiment. |
| `figures/` | Figure specification, caption, source mapping và các figure artifact cần thiết để kiểm tra claim; mỗi figure phải trỏ về result/data commit. |
| `content/` | Draft nội dung diễn giải cho audience bên ngoài, chỉ được sinh từ verified milestone và luôn cần human review. |
| `paper/` | Markdown source của paper, outline, sections, appendix và bibliography/provenance liên quan. |
| `ara/` | Artifact provenance/review của ARA được tạo ở cuối session; không tạo ARA artifact giữa session. |
| `state/` | YAML state canonical của workspace, session, milestone, experiment và các commit reference. |

### 3.1. Trạng thái milestone

Mỗi milestone có một ID ổn định và một Markdown record. YAML state có thể tham
chiếu record đó và commit gần nhất. Trạng thái hợp lệ là:

- `planned`: đã định nghĩa nhưng chưa bắt đầu;
- `active`: đang thực hiện hoặc đang thu thập evidence;
- `verified`: tất cả tiêu chí và evidence đã được review, đủ điều kiện làm nguồn
  cho `content/` và claim public;
- `superseded`: bị thay thế bởi milestone khác nhưng vẫn giữ lịch sử;
- `blocked`: không thể tiến hành do một blocker đã ghi rõ.

Chỉ `verified` là trạng thái đủ điều kiện cho content public-facing. Việc đổi
trạng thái phải có lý do, evidence path và commit reference trong record hoặc
state tương ứng.

## 4. Luồng nghiên cứu bắt buộc

Mỗi experiment và mỗi thay đổi nghiên cứu có ý nghĩa đi qua thứ tự sau:

### 4.1. Init

Khởi tạo workspace và các quy ước nền tảng. Commit thiết kế bootstrap hiện tại
được chỉ định riêng là:

```text
docs(design): define InvariantAudit research workflow
```

Đây là commit tài liệu bắt buộc của workspace ban đầu, không thay thế các pattern
`research(...)` dành cho các thay đổi nghiên cứu tiếp theo.

### 4.2. Protocol trước results

Trước khi chạy một experiment, phải tạo hoặc cập nhật protocol Markdown. Protocol
phải nêu rõ câu hỏi/hypothesis, inputs, phương pháp, tham số, evaluation metric,
expected output, tiêu chí dừng, cách ghi data và các hạn chế đã biết.

Protocol phải được commit thành một commit riêng trước khi ghi hoặc commit bất kỳ
result nào của run đó. Result record phải lưu `protocol_path`, `protocol_commit`
và experiment/run ID. Nếu protocol thay đổi sau khi một run đã bắt đầu, thay đổi
đó tạo một protocol version mới và run mới; không sửa lịch sử để làm như thể
protocol mới đã tồn tại trước result cũ.

### 4.3. Results và data

Sau protocol commit, result Markdown phải ghi điều đã chạy, deviation so với
protocol, outcome, failure/null result, limitation và đường dẫn tới CSV/JSONL
data. Result commit phải tham chiếu đúng protocol commit của run.

Điều kiện lịch sử bắt buộc là `protocol_commit` phải là ancestor của
`results_commit`. Có thể kiểm tra bằng:

```text
git merge-base --is-ancestor <protocol_commit> <results_commit>
```

Lệnh kiểm tra chỉ là phép xác nhận read-only; quy tắc thực tế là protocol phải
được commit trước results trong Git history. Không được ghi result chưa có
protocol commit tương ứng.

### 4.4. Reflect và verification

Reflect record bằng Markdown phải nối result với interpretation, uncertainty,
alternative explanation, literature liên quan và quyết định milestone. Một
milestone chỉ chuyển sang `verified` khi evidence đã được review, provenance
đầy đủ và các limitation quan trọng đã được ghi. Verification commit phải được
tham chiếu trong milestone record và YAML state.

### 4.5. Paper và content

`paper/` và `content/` chỉ được lấy claim, số liệu, figure và kết luận từ
milestone `verified` hoặc literature đã được ghi provenance. Mỗi content draft
phải nêu source milestone ID và verification commit trong metadata hoặc phần
provenance của Markdown.

Content không được tự đăng, tự gửi, tự publish hoặc tự gọi external publishing
API. Human owner phải review và thực hiện publication bằng một hành động riêng có
authority rõ ràng. Paper có thể tiếp tục được chỉnh sửa sau verified milestone,
nhưng mọi claim mới phải quay lại một result/literature source đã có provenance.

## 5. Commit, push và lịch sử

### 5.1. Thay đổi nghiên cứu có ý nghĩa

Một diff được xem là **meaningful research change** nếu nó thay đổi ít nhất một
trong các loại sau: research question/hypothesis, protocol hoặc tham số run,
data/result, analysis/interpretation, literature claim, figure evidence,
milestone status/evidence, content claim hoặc paper prose có ý nghĩa khoa học.

Mỗi meaningful research change phải được validate, commit và push ngay sau thay
đổi đó. Commit local là bắt buộc. Push là bắt buộc khi remote đã được cấu hình
và hành động public/external đã được user authorize; nếu chưa có remote thì
không tự tạo remote hay push thay thế. Các typo hoặc formatting-only diff không
đổi meaning có thể đi cùng commit meaningful gần nhất.

Không được tạo empty commit. Trước mỗi commit phải xác nhận staged diff có ít
nhất một thay đổi; một commit chỉ có message mà không có file change bị từ chối.
Không gom một protocol change và result của nó vào cùng commit, vì điều đó phá
vỡ protocol-before-results gate.

### 5.2. Commit message patterns

Các commit nghiên cứu dùng đúng một trong năm pattern sau, với summary ngắn,
khẳng định và mô tả được change:

```text
research(init): <summary>
research(protocol): <summary>
research(results): <summary>
research(reflect): <summary>
research(paper): <summary>
```

Phân loại được dùng như sau:

- `research(init)`: khởi tạo hoặc thay đổi cấu trúc/metadata nền tảng của research
  workflow sau commit thiết kế bootstrap;
- `research(protocol)`: tạo hoặc version hóa protocol;
- `research(results)`: ghi run, result hoặc data;
- `research(reflect)`: analysis, literature synthesis, milestone verification và
  end-of-session ARA provenance;
- `research(paper)`: paper prose hoặc content/presentation draft đã vượt qua
  verified-milestone gate.

Không dùng một pattern để che giấu việc đảo thứ tự protocol/results. Commit hiện
tại của spec là ngoại lệ được user chỉ định bằng message `docs(design): ...`;
các commit nghiên cứu kế tiếp phải dùng một trong năm pattern trên.

### 5.3. Push gate cho public repository

Trước mỗi push tới public `invariant-audit`, phải kiểm tra staged/committed diff,
provenance, secrets và kích thước artifact. Không push:

- secrets, token, API key, private key, credential, session material hoặc dữ liệu
  cá nhân/riêng tư;
- model weights, checkpoint hoặc artifact có thể tái dựng model;
- raw/bulk data lớn hoặc artifact không thể review hợp lý trong source repository;
- cache, build output và file tạm không cần cho provenance/reproduction.

Trong workspace này, file đơn từ 50 MiB trở lên được coi là large artifact và bị
từ chối khỏi public Git history. Raw/bulk dataset bị từ chối ngay cả khi nhỏ hơn
ngưỡng đó nếu không cần thiết cho claim hoặc chứa dữ liệu nhạy cảm. Khi cần
tham chiếu data lớn, chỉ lưu một sample/aggregate reviewable cùng pointer,
version và checksum tới nơi lưu trữ được cấp quyền riêng; pointer không được
chứa credential.

## 6. ARA và ranh giới session

ARA **chỉ chạy một lần ở cuối session**, sau khi toàn bộ research change trong
session đã được hoàn tất, validate, commit và push theo các gate ở trên. Không
chạy ARA giữa protocol, run, result, reflect hoặc paper work để thay thế các
gate đó.

Quy trình cuối session là:

1. hoàn thành và commit/push meaningful research change cuối cùng;
2. chạy ARA trên provenance của session;
3. ghi artifact ARA vào `ara/` nếu artifact được tạo hoặc cập nhật;
4. nếu ARA tạo meaningful provenance change, commit bằng
   `research(reflect): record end-of-session ARA provenance` và push theo push
   gate;
5. không bắt đầu research mới sau ARA trong cùng session.

ARA không được dùng để tự publish content, tự sửa claim mà không có evidence,
hoặc làm mất record của failure/null result.

## 7. Checklist trước khi đóng session

Workspace chỉ được coi là sẵn sàng đóng khi tất cả điều kiện sau đúng:

- branch local là `main`;
- mọi meaningful research change đã có commit không rỗng;
- mọi result commit có protocol commit tương ứng và protocol là ancestor;
- milestone được dùng cho content/paper đã ở trạng thái `verified`;
- content chưa bị tự đăng hoặc tự gửi;
- không có secrets, model weights, dữ liệu cá nhân hoặc large artifact bị đưa vào
  lịch sử public;
- ARA đã chạy ở cuối session và không có research mới sau ARA;
- worktree sạch, hoặc mọi thay đổi còn lại đã được user ghi nhận là ngoài scope.

Thiết kế này giữ Markdown làm narrative source, YAML làm state source và
CSV/JSONL làm row-data source; các commit reference và verification gate là cầu
nối bắt buộc giữa ba lớp đó.
