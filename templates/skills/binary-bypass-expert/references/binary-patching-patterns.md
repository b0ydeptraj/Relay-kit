# Các mẫu (Patterns) thao tác Nhị phân (Binary Patching)

Dưới đây là các kỹ thuật chuẩn (Best Practices) mà `binary-bypass-expert` nên tham khảo để đưa ra tư vấn cho `plan-hub` hoặc `developer` khi cần code Python sửa đổi byte nhị phân.

## 1. Tìm kiếm bằng Mẫu động (Dynamic Pattern Scanning) thay vì Hardcode Offset
Game luôn cập nhật, offset file luôn đổi. Hãy scan mảng byte bằng `find()` hoặc regex.

```python
# Tìm chuỗi (path) cố định trong file
entry_path = b'Ages/Prefab_Characters/Prefab_Hero/CommonActions.pkg.bytes'
idx = payload.find(entry_path)

if idx == -1:
    print("Không tìm thấy entry, file đã an toàn.")
```

## 2. Unpack cấu trúc Struct
Sử dụng module `struct` của Python để đọc số nguyên (Integers) như số lượng Array Count, độ dài chuỗi (Length Prefix).

```python
import struct

# Đọc 4-byte Little-endian Unsigned Integer (Kích thước array)
# Chú ý: Cần biết chính xác offset của biến count
count_offset = idx - 100 # Ví dụ tìm ngược lại
old_count = struct.unpack_from('<I', payload, count_offset)[0]

# Viết lại giá trị đã giảm đi 1
new_count = old_count - 1
struct.pack_into('<I', payload, count_offset, new_count)
```

## 3. Kỹ thuật "Shift & Pad Zeros" (Bảo toàn Kích thước)
Đây là kỹ thuật mạnh nhất để Bypass verification mà không làm hỏng cấu trúc offset của file.
Khi xóa một Item có độ dài `X` ở giữa Payload, nếu chỉ cắt mảng đi `X` byte, tất cả các offset ở phía sau (trong engine) sẽ bị lệch, gây Crash. Giải pháp: Dịch (Shift) toàn bộ byte phía sau lên lấp chỗ trống, và điền Zeros vào đuôi cuối cùng.

```python
# Xác định vị trí bắt đầu và kết thúc của một entry (Ví dụ: 72 bytes)
entry_start = idx - 4 # Vị trí length prefix
entry_size = 72
entry_end = entry_start + entry_size

# Shift: Kéo toàn bộ phần đuôi file lên lấp vào khoảng trống
after_entry = payload[entry_end:]
payload[entry_start : entry_start + len(after_entry)] = after_entry

# Pad Zeros: Điền số byte 0 bằng đúng kích thước đã xóa ở đuôi mảng
new_tail_start = entry_start + len(after_entry)
payload[new_tail_start:] = b'\x00' * (len(payload) - new_tail_start)

# => Kích thước len(payload) KHÔNG thay đổi.
```

## 4. In-place String Replacement
Sử dụng khi không muốn/không thể thay đổi logic (Shift).
Chỉ thay chuỗi Text bằng một chuỗi khác **có cùng độ dài** để đổi tên/bẻ gãy đường dẫn.

```python
target = b"https://api.game.com/check"
replacement = b"http://127.0.0.1:8080/check" # Dài 27 bytes, target là 26
# Phải đảm bảo cùng size!
replacement = b"http://127.0.0.1/auth/mock" # 26 bytes
payload = payload.replace(target, replacement)
```
