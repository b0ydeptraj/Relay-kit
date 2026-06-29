# Kỹ thuật Bypass SSL Pinning

SSL Pinning là kỹ thuật mà lập trình viên dùng để đảm bảo App chỉ giao tiếp đúng với Server có chứng chỉ (Certificate) chỉ định. Nếu cài chứng chỉ giả của Charles/BurpSuite/Mitmproxy, App sẽ từ chối kết nối.

## 1. Phương pháp Android: Dùng Objection / Frida
Đây là phương pháp mạnh và phổ biến nhất. Yêu cầu máy đã Root hoặc giả lập có quyền Root.

**Cài đặt:**
```bash
pip install frida-tools objection
```

**Thực thi Bypass:**
```bash
# Gắn (hook) vào app đang chạy và tự động chèn script bypass SSL pinning
objection -g com.package.name explore -s "android sslpinning disable"
```
Nếu Objection không hoạt động do cơ chế pinning custom (như OkHttp3 bị obfuscate), cần tìm các script Frida custom trên mạng (`frida-multiple-unpinning.js`) và chạy thủ công:
```bash
frida -U -f com.package.name -l unpin.js --no-pause
```

## 2. Phương pháp Android: Patch file APK (Network Security Config)
Dành cho máy không có Root. Ta sẽ unpack APK, sửa đổi file cấu hình và repack lại.

1. Unpack APK (ví dụ dùng `apktool`).
2. Sửa file `AndroidManifest.xml`, thêm thẻ: `android:networkSecurityConfig="@xml/network_security_config"` vào thẻ `<application>`.
3. Tạo file `res/xml/network_security_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" /> <!-- Cho phép chứng chỉ của người dùng (mitmproxy) -->
        </trust-anchors>
    </base-config>
</network-security-config>
```
4. Repack và Sign lại APK.

## 3. Thao túng luồng bằng Mitmproxy Script (Python)
Khi đã bypass được SSL Pinning, dùng Mitmproxy để thao túng nội dung trả về.

```python
# mitm_script.py
from mitmproxy import http
import json

def response(flow: http.HTTPFlow):
    # Nếu URL chứa api/verify-license
    if "api/verify-license" in flow.request.pretty_url:
        try:
            data = json.loads(flow.response.content)
            # Sửa đổi dữ liệu trả về từ server
            data["isValid"] = True
            data["plan"] = "LIFETIME_PRO"
            
            # Gán lại cho response
            flow.response.content = json.dumps(data).encode("utf-8")
            print("[+] Đã thao túng License thành công!")
        except Exception as e:
            print(f"Lỗi: {e}")

# Chạy mitmproxy với script này:
# mitmdump -s mitm_script.py
```
