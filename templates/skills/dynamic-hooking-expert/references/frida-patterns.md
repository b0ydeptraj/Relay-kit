# Mẫu Mã Frida (Frida Hooking Patterns)

Frida là công cụ Dynamic Instrumentation mạnh nhất thế giới. Dưới đây là các đoạn mã (snippets) mẫu để `dynamic-hooking-expert` sử dụng.

## 1. Hook Hàm Java (Android)
Đánh tráo kết quả trả về của một hàm trên Android.
Ví dụ: Ép hàm `isPremiumUser()` của class `com.app.Billing` trả về `true`.

```javascript
Java.perform(function() {
    // Trỏ tới Class
    var BillingClass = Java.use("com.app.Billing");
    
    // Ghi đè hàm
    BillingClass.isPremiumUser.implementation = function() {
        console.log("[*] Đã chặn hàm isPremiumUser(). Trả về true!");
        // return this.isPremiumUser(); // Nếu muốn gọi lại hàm gốc
        return true; 
    };
});
```

## 2. Hook Native C/C++ (iOS & Android NDK)
Dùng cho game (như file `libil2cpp.so` của Unity) hoặc App viết bằng C++.

```javascript
// Bước 1: Tìm địa chỉ gốc của thư viện
var baseAddr = Module.findBaseAddress("libil2cpp.so");

// Bước 2: Tìm địa chỉ hàm (Ví dụ qua dịch ngược là offset 0x123456)
var funcAddr = baseAddr.add(0x123456);

// Bước 3: Đánh chặn (Hook)
Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        console.log("[*] Gọi hàm kiểm tra tiền. Tham số 1: " + args[0].toInt32());
        // Có thể sửa tham số tại đây: args[0] = ptr("999999");
    },
    onLeave: function(retval) {
        console.log("[*] Kết quả gốc: " + retval.toInt32());
        // Thay đổi kết quả trả về thành 1 (True / Success)
        retval.replace(1);
    }
});
```

## 3. Bypass Root & Jailbreak Detection (Mẫu chung)
Một số App kiểm tra đường dẫn file hệ thống để phát hiện Root.
Ta sẽ hook vào hàm `File.exists()` của ngôn ngữ nền để nói dối.

```javascript
Java.perform(function() {
    var File = Java.use("java.io.File");
    
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        if (path.indexOf("su") !== -1 || path.indexOf("magisk") !== -1) {
            console.log("[*] Bypass Root Check cho đường dẫn: " + path);
            return false; // Nói dối là file không tồn tại
        }
        return this.exists(); // File bình thường thì báo đúng
    };
});
```

## 4. Chống phát hiện Frida (Anti-Anti-Frida)
Nếu App phát hiện Frida bằng cách đọc `/proc/self/maps` hoặc thư viện tên `frida-agent`.
- **Cách 1:** Đổi tên tiến trình Frida server thành một tên vô hại.
- **Cách 2:** Dùng script hook vào chính hàm `open()` / `fopen()` trong ngôn ngữ C (libc) để làm giả file `maps` khi App cố gắng đọc danh sách thư viện đang nạp vào RAM.
