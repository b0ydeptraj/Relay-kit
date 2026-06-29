# Kỹ năng tìm khoá (Encryption Keys)

Dưới đây là các kỹ thuật tìm kiếm khoá mã hoá (Key/IV/Salt) bị giấu trong Game hoặc Ứng dụng.

## 1. Static Key Finding (Tìm trong code)
Rất nhiều Lập trình viên hardcode Key trực tiếp vào mã nguồn.
Dùng Decompiler (Apktool/Jadx/IDA) tìm kiếm:
- Tên biến: `SECRET_KEY`, `AES_KEY`, `ENCRYPT_KEY`, `SALT`, `KEY_SPEC`.
- Các chuỗi ngẫu nhiên có độ dài chuẩn: 16 bytes (16 ký tự), 32 bytes (32 ký tự).
- Các chuỗi Base64 dài nằm lơ lửng trong code.

```java
// Ví dụ mã Java bị decompile
private static final String SECRET_KEY = "MySuperSecretKey123";
private static final byte[] IV = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 };
```

## 2. XOR Cipher và Magic Bytes
Đôi khi thuật toán không phải là AES mà chỉ là XOR đơn giản với một chuỗi cố định.
Đặc điểm của XOR: Nếu bạn biết được `Magic Bytes` gốc (Ví dụ: file ảnh thường bắt đầu bằng `89 50 4E 47` tức `PNG`), và bạn có file bị mã hóa, bạn chỉ cần lấy 4 bytes đầu của file bị mã hóa XOR với `89 50 4E 47` để tìm ra Khoá (XOR Key).

```python
# Kỹ thuật tìm XOR Key từ Magic Byte
encrypted_byte = 0xE1
known_magic_byte = 0x89 # Ký tự đầu của PNG
xor_key = encrypted_byte ^ known_magic_byte
print(hex(xor_key)) # Chìa khóa bị giấu
```

## 3. Dynamic Key Logging (Bắt Key trên RAM)
Nếu Key không bị hardcode mà được tính toán phức tạp thông qua JNI (C++), hãy nhờ `dynamic-hooking-expert` viết kịch bản Frida gắn vào bộ mã hoá chuẩn của hệ điều hành.

**Bắt AES Key trên Android Java (javax.crypto.spec.SecretKeySpec):**
```javascript
Java.perform(function() {
    var SecretKeySpec = Java.use("javax.crypto.spec.SecretKeySpec");
    SecretKeySpec.$init.overload('[B', 'java.lang.String').implementation = function(keyBytes, algorithm) {
        var keyHex = "";
        for (var i = 0; i < keyBytes.length; i++) {
            keyHex += ("0" + (keyBytes[i] & 0xFF).toString(16)).slice(-2) + " ";
        }
        console.log("[*] Tìm thấy khóa AES (" + algorithm + "): " + keyHex);
        return this.$init(keyBytes, algorithm);
    };
});
```

Sau khi có Key, ta sẽ đưa cho `developer` viết đoạn code Python dùng `Crypto.Cipher.AES` để giải mã file, sửa thông tin, và mã hoá lại bằng đúng Key đó.
