# Subtraction Audit Reference (Kiểm toán Cắt giảm Code & Độ phức tạp)

## Core Philosophy
> *"The best code is no code at all. The second best is code that someone else maintains without bugs. Every line added is a liability."*

Subtraction Audit là phương pháp tư duy đối kháng: Luôn tìm cách **loại bỏ, đơn giản hóa, hoặc thu hẹp** trước khi chấp nhận thêm mới.

---

## 5 Câu hỏi Kiểm toán Bắt buộc

1. **Dead Code & Zombie Paths:**
   - Đoạn code/function/branch này có thực sự còn được gọi không?
   - Có cờ tính năng (feature flag) hoặc code tương thích cũ (legacy fallback) nào đã hết hạn cần dọn dẹp không?

2. **Premature Abstraction:**
   - Abstraction này có phục vụ ít nhất 3 nơi gọi độc lập không?
   - Nếu chỉ có 1 nơi gọi: Gộp thẳng (inline) lại, xóa interface/factory thừa.

3. **Over-Defensive Code:**
   - Có đang bọc `try/catch` vô tội vạ chỉ để nuốt lỗi (swallow errors) mà không xử lý thực chất không?
   - Có đang kiểm tra `null/undefined` 5 lần liên tiếp trên cùng một object không?

4. **Dependency Minimization:**
   - Thư viện/package mới thêm vào có đáng để kéo theo 50 sub-dependencies không?
   - Vấn đề có thể giải quyết bằng 10 dòng code native chuẩn không?

5. **Comment & Yap Purge:**
   - Xóa bỏ mọi comment giải thích cú pháp hiển nhiên.
   - Giữ lại duy nhất các comment giải thích **TẠI SAO (Why)** - ví dụ: bypass bug của OS, workaround của browser engine.

---

## Checklist khi Thực hiện Subtraction Audit

- [ ] Đã quét và loại bỏ các import không sử dụng.
- [ ] Đã inline các hàm/biến trung gian chỉ dùng đúng 1 lần nếu không tăng tính dễ đọc.
- [ ] Đã kiểm tra diff: Số dòng xóa (-) có lớn hơn hoặc tương đương số dòng thêm (+) cho các tác vụ refactor không?
- [ ] Không làm gãy public contract và test suite hiện có.
