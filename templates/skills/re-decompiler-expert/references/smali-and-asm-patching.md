# Kỹ Thuật Vá Mã (Patching) Smali & Assembly

Dưới đây là các kỹ thuật đổi lệnh (Opcode modification) phổ biến nhất để bẻ khóa luồng kiểm tra của ứng dụng.

## 1. Smali Patching (Android APK)

Smali là ngôn ngữ Assembly dành cho máy ảo Dalvik/ART của Android. Nó được sinh ra khi dùng Apktool decompile file `.dex`.

**Mẫu 1: Đảo ngược điều kiện `if`**
Khi app kiểm tra `if (isVIP == false)`, lệnh trong Smali sẽ là `if-eqz` (if equal to zero). Để bypass, hãy đổi thành `if-nez` (if not equal to zero).

```smali
# Mã gốc
invoke-virtual {v0}, Lcom/app/User;->isVIP()Z
move-result v0
if-eqz v0, :cond_0  # Nếu v0 == 0 (False), nhảy tới cond_0 (Báo lỗi)

# Mã đã vá (Patch)
invoke-virtual {v0}, Lcom/app/User;->isVIP()Z
move-result v0
if-nez v0, :cond_0  # Đổi thành if-nez: Nếu v0 != 0 (True), mới báo lỗi!
```

**Mẫu 2: Thay đổi giá trị trả về (Force Return True)**
Ép một hàm luôn trả về True (boolean 1) bất chấp logic bên trong.

```smali
.method public isPremium()Z
    .locals 1
    
    # Xóa hết logic kiểm tra phức tạp bên dưới, chèn dòng này lên đầu:
    const/4 v0, 0x1
    return v0
    
    # ... logic cũ của app
.end method
```

## 2. ARM64 Assembly Patching (iOS & Android Native)

Khi sửa file `.so` hoặc Mach-O (iOS), ta phải làm việc với mã Hex của kiến trúc ARM64. Bạn cần nhớ các cặp lệnh nhảy nhánh (Branch instructions) hoặc lệnh gán (Move instructions).

**Mẫu 1: Force Return True (MOV W0, #1; RET)**
Để ép một hàm C++ luôn trả về True (số nguyên 1), ta thay thế byte ở đầu hàm thành lệnh gán thanh ghi w0 = 1 và return.

```assembly
; Hợp ngữ ARM64:
MOV W0, #1  -> Hex: 20 00 80 52
RET         -> Hex: C0 03 5F D6

; Kỹ thuật vá: Mở file nhị phân bằng Hex Editor hoặc Python Script
; Tìm đến offset của hàm, đè 8 bytes gốc bằng chuỗi Hex: 20008052C0035FD6
```

**Mẫu 2: NOP Sled (Vô hiệu hóa lệnh gọi hàm)**
Nếu có một hàm `KillProcess()` hoặc `ShowAds()`, ta không muốn nó chạy. Ta thay thế lệnh gọi hàm đó (`BL` trong ARM) bằng lệnh `NOP` (No Operation - không làm gì cả).

```assembly
; Hợp ngữ ARM64:
NOP -> Hex: 1F 20 03 D5

; Kỹ thuật vá: Tìm offset của dòng gọi hàm (ví dụ 4 bytes), đè bằng 1F2003D5.
```

**Lưu ý khi cung cấp Output:** Luôn cung cấp cho `developer` offset chính xác và chuỗi Hex để họ viết script Python `seek()` và `write()`.
