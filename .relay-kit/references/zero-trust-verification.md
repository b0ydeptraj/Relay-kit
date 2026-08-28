# Zero-Trust Code & Fix Verification Reference

## Core Philosophy
> *"Never trust an unverified assumption. If a test hasn't failed first or a reproduction hasn't been observed, you don't know what you're fixing."*

Phương pháp kiểm chứng Zero-Trust yêu cầu phân lập giữa **sự thật đã chứng minh** và **suy diễn chủ quan**.

---

## 4 Nguyên tắc Zero-Trust

### 1. Phân loại Failure Modes (Nguyên nhân lỗi)
Khi xảy ra lỗi hoặc sai lệch quy định:
- **`[LOAD-FAIL]`**: Agent không có tài liệu, spec hoặc quy định trong context.
  - *Giải pháp*: Cung cấp tài liệu/file link cụ thể. Không trách phạt hay đoán mò.
- **`[COMPLY-FAIL]`**: Agent đã được cấp tài liệu/rule đầy đủ nhưng bỏ qua hoặc vi phạm.
  - *Giải pháp*: Báo cáo vi phạm, kích hoạt gate chặn completion, yêu cầu sửa ngay.

### 2. Reproduction Before Fix
- Đối với bug: Phải xác định được điều kiện gây lỗi (reproduction case) trước khi sửa code.
- Nếu không thể tái hiện: Dừng lại đặt câu hỏi làm rõ, không đoán mò sửa bậy.

### 3. Concrete Fact Anchoring
- Mọi câu khẳng định phải gắn liền với đường dẫn `file:line` hoặc output terminal thực tế.
- Tuyệt đối không trích dẫn code từ trí nhớ ảo giác (hallucinated memory).

### 4. Verification Evidence Matrix
| Loại thay đổi | Bằng chứng bắt buộc |
| :--- | :--- |
| **Logic Backend / Algorithm** | Unit test pass + Terminal exit code 0 |
| **Giao diện Frontend / CSS** | Screenshot rendering thực tế qua browser subagent |
| **API / Endpoint** | Request/Response payload thật (cURL / test log) |
| **Bypass / Reverse Engineering** | HTTP 200 payload / Token trích xuất thành công |
