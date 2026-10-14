#!/usr/bin/env python3
"""hardware_re_toolkit.py - Hardware RE: firmware analysis, entropy, filesystem detection, secret hunting.
Usage:
    python scripts/hardware_re_toolkit.py --analyze-firmware firmware.bin
    python scripts/hardware_re_toolkit.py --hunt-secrets firmware.bin
    python scripts/hardware_re_toolkit.py --list-tools
    python scripts/hardware_re_toolkit.py --detect-uart --port COM3
"""
import argparse, hashlib, json, math, os, re, sys

TOOLS = {
    "UART":  {"hw":["USB-UART CP2102/CH340"],"cmd":"screen /dev/ttyUSB0 115200",
              "tip":"TX->RX, RX->TX, GND->GND. Logic level 3.3V, try 115200 baud"},
    "JTAG":  {"hw":["J-Link/OpenOCD adapter","JTAGulator"],"cmd":"openocd -f interface/jlink.cfg",
              "tip":"TDI,TDO,TMS,TCK,TRST,GND. JTAGulator auto-discovers pins"},
    "SPI Flash":{"hw":["CH341A + SOIC8 clip"],"cmd":"flashrom -p ch341a_spi -r fw.bin",
                 "tip":"Identify IC (Winbond W25Q / Macronix MX25L). Use clip in-circuit"},
    "I2C EEPROM":{"hw":["Arduino/Bus Pirate"],"cmd":"i2cdump -y 0 0x50",
                  "tip":"24Cxx at 0x50-0x57. Use i2c-tools on Linux"},
}

FS_SIGS = {
    "SquashFS":(b"sqsh",0,"unsquashfs"), "JFFS2":(b"\x19\x85",0,"jefferson"),
    "gzip":(b"\x1f\x8b",0,"gzip -d"), "LZMA":(b"\xfd7zXZ\x00",0,"xz -d"),
    "UBoot":(b"\x27\x05\x19\x56",0,"binwalk"), "ELF":(b"\x7fELF",0,"readelf -a"),
    "PKZIP":(b"PK\x03\x04",0,"unzip"), "7zip":(b"7z\xbc\xaf\x27\x1c",0,"7z x"),
    "Android Boot":(b"ANDROID!",0,"abootimg"), "CramFS":(b"\x45\x3d\xcd\x28",0,"mount -t cramfs"),
    "Linux Kernel":(b"Linux version",0,"extract-vmlinux"),
}

SECRET_PATS = [
    (r"password\s*[=:]\s*['\"]?([^\s'\"]{6,50})","password"),
    (r"secret\s*[=:]\s*['\"]?([^\s'\"]{8,80})","secret"),
    (r"api[_-]?key\s*[=:]\s*['\"]?([^\s'\"]{16,80})","api_key"),
    (r"AKIA[0-9A-Z]{16}","aws_key"),
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----","pem_private_key"),
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}","email"),
    (r"https?://\S{20,}","url"),
]

def entropy(data, block=1024):
    blocks=[]
    for i in range(0,len(data),block):
        b=data[i:i+block]
        if not b: break
        cnt=[0]*256
        for x in b: cnt[x]+=1
        e=sum(-(c/len(b))*math.log2(c/len(b)) for c in cnt if c>0)
        blocks.append(round(e,2))
    avg=sum(blocks)/len(blocks) if blocks else 0
    hi=[i*block for i,e in enumerate(blocks) if e>7.5]
    return {"avg":round(avg,2),"high_entropy_offsets":[hex(x) for x in hi[:5]],
            "likely_encrypted":avg>7.5,"likely_compressed":6<avg<=7.5}

def find_fs(data):
    found=[]
    for name,(magic,off,tool) in FS_SIGS.items():
        pos=off
        while True:
            idx=data.find(magic,pos)
            if idx==-1 or len(found)>15: break
            found.append({"type":name,"offset":hex(idx),"tool":tool}); pos=idx+1
    return found

def hunt_secrets(data):
    text=data.decode("utf-8","replace")
    hits=[]; seen=set()
    for pat,ptype in SECRET_PATS:
        for m in re.findall(pat,text,re.I):
            v=m[0] if isinstance(m,tuple) else m
            if v and v not in seen and len(v)>=4 and len(set(v))>=3:
                seen.add(v); hits.append({"type":ptype,"value":v[:80]})
    return hits

def analyze(path):
    data=open(path,"rb").read()
    size=len(data); md5=hashlib.md5(data).hexdigest()
    print(f"[*] {path} | {size:,} bytes | MD5:{md5}")
    e=entropy(data)
    print(f"[*] Entropy: {e['avg']} | encrypted:{e['likely_encrypted']} | compressed:{e['likely_compressed']}")
    if e["high_entropy_offsets"]: print(f"    High-entropy offsets: {e['high_entropy_offsets']}")
    comps=find_fs(data)
    print(f"[*] Components: {len(comps)}")
    for c in comps: print(f"  [{c['type']}] {c['offset']} | {c['tool']}")
    secrets=hunt_secrets(data)
    interesting=[s for s in secrets if s["type"]!="url"]
    print(f"[*] Secrets: {len(interesting)}")
    for s in interesting[:10]: print(f"  [{s['type']}] {s['value'][:60]}")
    return {"file":path,"size":size,"md5":md5,"entropy":e,"components":comps,"secrets":interesting[:20]}

def main():
    p=argparse.ArgumentParser(description="Hardware RE toolkit")
    p.add_argument("--analyze-firmware"); p.add_argument("--hunt-secrets")
    p.add_argument("--detect-uart",action="store_true"); p.add_argument("--port")
    p.add_argument("--list-tools",action="store_true"); p.add_argument("--output")
    args=p.parse_args()

    if args.list_tools:
        print("[*] Hardware RE Tools:")
        for t,i in TOOLS.items():
            print(f"\n  [{t}]  hw:{', '.join(i['hw'])}")
            print(f"    cmd: {i['cmd']}")
            print(f"    tip: {i['tip']}")
        return

    if args.detect_uart:
        port=args.port or ("COM3" if sys.platform=="win32" else "/dev/ttyUSB0")
        print(f"[*] UART Guide:\n  Port: {port}\n  Baud: 115200\n  Wiring: TX->RX, RX->TX, GND->GND")
        print(f"  Connect: {'putty -serial '+port+' -sercfg 115200,8,n,1,N' if sys.platform=='win32' else 'screen '+port+' 115200'}")
        try:
            import serial
            s=serial.Serial(port,115200,timeout=3)
            d=s.read(512); s.close()
            print(f"  UART data ({len(d)} bytes):\n  {d.decode('utf-8','replace')[:200]}")
        except ImportError: print("[!] pip install pyserial for live capture")
        except Exception as e: print(f"  Error: {e}")
        return

    if args.analyze_firmware:
        if not os.path.exists(args.analyze_firmware):
            print(f"[-] Not found: {args.analyze_firmware}"); sys.exit(1)
        r=analyze(args.analyze_firmware)
        if args.output: json.dump(r,open(args.output,"w"),indent=2); print(f"[+] {args.output}")
        return

    if args.hunt_secrets:
        if not os.path.exists(args.hunt_secrets):
            print(f"[-] Not found: {args.hunt_secrets}"); sys.exit(1)
        data=open(args.hunt_secrets,"rb").read()
        secrets=hunt_secrets(data)
        print(f"[*] Secrets in {args.hunt_secrets}: {len(secrets)}")
        for s in secrets[:20]: print(f"  [{s['type']}] {s['value'][:70]}")
        return
    p.print_help()

if __name__=="__main__": main()
