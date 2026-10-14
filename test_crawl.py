import requests
import time
import urllib3
urllib3.disable_warnings()

res = requests.get('http://127.0.0.1:8999/api/feed').json()
target = next((r for r in res.get('requests', []) if r['method'] in ['GET', 'POST']), None)

if not target:
    print("Khong tim thay HTTP request nao!")
else:
    print(f"[*] API muc tieu: {target['method']} {target['url'][:100]}...")
    for i in range(1, 4):
        print(f"[*] Dang cao luot {i}...")
        r = requests.request(
            target['method'], 
            target['url'], 
            headers=target['headers'], 
            data=target.get('body', '').encode('utf-8'), 
            verify=False
        )
        print(f"  => HTTP {r.status_code} | XUYEN QUA LOP BAO VE THANH CONG! (Data size: {len(r.text)} bytes)")
        time.sleep(1)
