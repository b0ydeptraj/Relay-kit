import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

def scan_drive(drive_path):
    print(f"[*] Đang quét ổ {drive_path} (Quá trình này có thể mất 1-3 phút)...")
    dir_sizes = {}
    
    for root, dirs, files in os.walk(drive_path):
        # Bỏ qua thư mục ShadowX
        if 'shadowx' in root.lower():
            dirs[:] = [] # Ngừng quét các thư mục con bên trong
            continue
            
        size = 0
        try:
            for f in files:
                if 'shadowx' in f.lower():
                    continue
                fp = os.path.join(root, f)
                if not os.path.islink(fp):
                    size += os.path.getsize(fp)
        except Exception:
            pass
            
        # Cộng dồn dung lượng cho tất cả các thư mục cha
        parts = root.split(os.sep)
        for i in range(1, len(parts) + 1):
            parent = os.sep.join(parts[:i])
            if parent == drive_path.rstrip(os.sep): 
                parent = drive_path
            if not parent: continue
            dir_sizes[parent] = dir_sizes.get(parent, 0) + size

    sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n=== TOP 25 THƯ MỤC NẶNG NHẤT Ổ {drive_path} ===")
    count = 0
    for path, size in sorted_dirs:
        size_gb = size / (1024**3)
        if size_gb < 0.2: # Chỉ hiện trên 200MB
            continue
        # Bỏ qua ổ gốc (vd: C:\) để tránh loãng list
        if path == drive_path:
            print(f"--------------------------------------------------")
            print(f"TỔNG DUNG LƯỢNG ĐÃ QUÉT (trừ ShadowX): {size_gb:.2f} GB")
            print(f"--------------------------------------------------")
            continue
            
        print(f"{size_gb:6.2f} GB | {path}")
        count += 1
        if count >= 25:
            break
    print("\n")

if __name__ == "__main__":
    start = time.time()
    if os.path.exists('C:\\'):
        scan_drive('C:\\')
    if os.path.exists('D:\\'):
        scan_drive('D:\\')
    print(f"[+] Quét hoàn tất trong {time.time() - start:.1f} giây.")
