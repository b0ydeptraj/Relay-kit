import requests
import json
import time
import urllib3

urllib3.disable_warnings()

HUB_URL = "http://127.0.0.1:8999/api/feed?limit=1"

print("==================================================")
print("  TRẠM ĐIỀU KHIỂN CÀO DATA (UNIVERSAL CRAWLER)   ")
print("==================================================")

try:
    print("[*] Đang kết nối tới Sniffer Hub...")
    res = requests.get(HUB_URL).json()
    
    if not res.get("requests"):
        print("[!] Chưa bắt được API nào!")
        print("=> Hướng dẫn: Hãy mở Chrome, vào Facebook, TikTok, Shopee... cuộn chuột 1 phát để Extension bắt API, rồi chạy lại tool này.")
        exit()

    # Lấy API mới nhất mà Hub vừa bắt được
    target = res["requests"][0]
    print(f"[+] Đã tóm sống API: {target['method']} {target['url'][:80]}...")
    print(f"[+] Hệ thống tự động trích xuất toàn bộ Token, Cookie, Header (Chống bot) từ Extension!")

    headers = target["headers"]
    body = target.get("body", "")
    url = target["url"]

    # ----------------- CHẾ ĐỘ CÀO DATA HÀNG LOẠT -----------------
    print("\n🚀 BẮT ĐẦU AUTO CÀO DATA...")
    
    # Vòng lặp bắn API liên tục
    for i in range(1, 11):
        print(f"[*] Đang cào lượt thứ {i}...")
        
        # NOTE: Trong thực tế, bạn sẽ dùng Python để tự động đổi tham số URL hoặc Body ở đây
        # Ví dụ: url = url.replace("page=1", f"page={i}") hoặc đổi ID bài viết.
        
        if target['method'] == "GET":
            r = requests.get(url, headers=headers, timeout=10, verify=False)
        else:
            r = requests.post(url, headers=headers, data=body.encode('utf-8'), timeout=10, verify=False)
            
        print(f"  => Mã HTTP: {r.status_code} | Lấy được {len(r.text)} bytes dữ liệu.")
        if r.status_code == 200:
            print("  => Trạng thái: XUYÊN THỦNG ANTI-BOT THÀNH CÔNG!")
        else:
            print("  => Trạng thái: Thất bại hoặc API bị lỗi.")
        
        # Ngủ 1 giây để giả lập người thật, tránh bị khóa mõm
        time.sleep(1)

except Exception as e:
    print("[!] Lỗi:", e)
