# Định dạng nén và đóng gói (Compression & Packing)

Trong MMO Apps và Game (đặc biệt là Mobile), dữ liệu nhị phân thường không được để dạng thô (raw) mà được đóng gói vào các Container và Nén. Khi sử dụng `binary-bypass-expert`, AI phải biết cách bóc tách container và giải nén trước khi đọc hex, sau đó thao tác byte, và ráp lại.

## 1. UnityFS / AssetBundle
Các game dùng Unity thường lưu file cấu hình và tài nguyên trong AssetBundle. Các bản Unity hiện đại sử dụng chuẩn **UnityFS** (bắt đầu bằng magic bytes `UnityFS`).

- **Đặc điểm:** Header chứa thông tin về kích thước block, theo sau là các block nén LZ4.
- **Quy tắc Patch:** Không thay đổi bất kỳ thứ gì trên Header (đặc biệt là SerializedFile file_size). Cách an toàn nhất là giữ nguyên Header, giải nén toàn bộ Block payload, can thiệp payload (Shift & Pad) sao cho kích thước cuối cùng y hệt, sau đó lắp ghép Header + Payload.
- **Công cụ khuyên dùng:** Thường dùng module `lz4.block` trong Python để thao tác block. Không nên phụ thuộc hoàn toàn vào các thư viện bóc tách mạnh (như UnityPy) nếu game có áp dụng Obfuscation, vì thư viện sẽ parse lỗi. Tốt nhất là dùng Binary Struct Parsing.

## 2. LZ4 / LZ4HC
Rất phổ biến trong game do tốc độ giải nén siêu nhanh.

- **Dấu hiệu:** Tùy vào cách đóng gói, thường đi kèm block size ở dạng little-endian hoặc big-endian. Flag `0x03` thường tượng trưng cho LZ4 trong UnityFS block info.
- **Cách xử lý an toàn:** Dùng `pip install lz4`, sử dụng `lz4.block.decompress(data, uncompressed_size=...)` để lấy payload. Nếu kích thước payload thay đổi, việc nén lại (`lz4.block.compress`) có thể tạo ra size lệch với file gốc, gây lỗi Header. Do đó, khuyến khích bypass bằng cách thay đổi uncompressed payload sao cho size y nguyên.

## 3. Zstandard (Zstd)
Thường được dùng trong các bộ từ điển (dictionaries) của game, hoặc file Manifest.

- **Dấu hiệu:** Magic bytes `28 B5 2F FD`.
- **Cách xử lý:** Sử dụng `pip install zstandard`. Các file zstd thường chứa nguyên một JSON hoặc CSV. Có thể giải nén in-memory, sửa text/json, sau đó nén lại và thay thế hoàn toàn file gốc.

## 4. Protobuf (Protocol Buffers)
Sử dụng rộng rãi trong giao thức mạng MMO và file config offline.

- **Dấu hiệu:** Không có magic bytes rõ ràng nhưng thường có cấu trúc tag-wire (kiểu `08 XX 12 XX`).
- **Cách xử lý:** Nếu không có `.proto` schema gốc, nên dùng công cụ `protoc --decode_raw` để xem cấu trúc, sau đó tìm đúng vị trí byte lưu trữ giá trị và sửa. Không tự ý chèn thêm string dài hơn nếu không cập nhật length varint ở trước đó.
