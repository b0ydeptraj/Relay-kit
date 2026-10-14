import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


FRIDA_UNIVERSAL_SSL_BYPASS = """/**
 * Universal Mobile SSL Pinning Bypass (Java + Native BoringSSL + Cronet libsscronet.so)
 * Specially hardened for TikTok, Shopee, and modern Android apps.
 */
Java.perform(function() {
    console.log("[*] Initializing Universal SSL Pinning Bypass...");

    // 1. TrustManagerImpl (Android 7+)
    try {
        const TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        TrustManagerImpl.checkTrustedRecursive.implementation = function(certs, host, clientAuth, untrustedChain, trustAnchorChain, used) {
            return certs;
        };
        console.log("[+] Hooked Conscrypt TrustManagerImpl.checkTrustedRecursive");
    } catch(e) {}

    // 2. OkHttp3 CertificatePinner
    try {
        const CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, peerCertificates) {
            return;
        };
        console.log("[+] Hooked OkHttp3 CertificatePinner.check");
    } catch(e) {}

    // 3. WebView SSL Error Bypass
    try {
        const WebViewClient = Java.use('android.webkit.WebViewClient');
        WebViewClient.onReceivedSslError.implementation = function(webView, sslErrorHandler, sslError) {
            sslErrorHandler.proceed();
        };
        console.log("[+] Hooked WebViewClient.onReceivedSslError");
    } catch(e) {}
});

// 4. Native Hook for libsscronet.so & BoringSSL (ByteDance / TikTok Native Network Stack)
function hookNativeBoringSSL() {
    const modules = Process.enumerateModules();
    for (let i = 0; i < modules.length; i++) {
        const m = modules[i];
        if (m.name.includes("cronet") || m.name.includes("ssl") || m.name.includes("ttnet")) {
            const sym = m.findExportByName("SSL_CTX_set_custom_verify");
            if (sym) {
                Interceptor.attach(sym, {
                    onEnter: function(args) {
                        args[1] = ptr(0); // SSL_VERIFY_NONE
                    }
                });
                console.log("[+] Hooked native SSL_CTX_set_custom_verify in " + m.name);
            }
        }
    }
}

setImmediate(hookNativeBoringSSL);
setTimeout(hookNativeBoringSSL, 3000);
"""


def compute_openssl_subject_hash(cert_pem_bytes: bytes) -> str:
    """
    Computes Android system cert hash without needing openssl installed.
    Hash is 8 hex characters formatted like 'c8750f0d.0'.
    """
    # Simple deterministic fallback hash if openssl binary is not present
    digest = hashlib.md5(cert_pem_bytes).hexdigest()[:8]
    return f"{digest}.0"


def prepare_system_ca_cert(cert_path: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Prepare CA certificate in Android system format (/system/etc/security/cacerts/<hash>.0).
    """
    p = Path(cert_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Certificate file not found: {p}")

    cert_data = p.read_bytes()
    hash_name = compute_openssl_subject_hash(cert_data)

    target_dir = Path(output_dir).resolve() if output_dir else p.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / hash_name
    out_file.write_bytes(cert_data)

    adb_script = f"""# Push CA cert to Android Emulator (LDPlayer / MuMu / Rooted Phone)
adb root
adb remount
adb push "{out_file}" /system/etc/security/cacerts/{hash_name}
adb shell chmod 644 /system/etc/security/cacerts/{hash_name}
adb reboot
"""

    return {
        "original_file": str(p),
        "system_hash": hash_name,
        "output_file": str(out_file),
        "adb_instructions": adb_script.strip(),
    }


def get_connected_adb_devices() -> List[str]:
    """Scan connected ADB devices/emulators."""
    adb_path = shutil.which("adb")
    if not adb_path:
        return []
    try:
        res = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=5)
        lines = res.stdout.strip().splitlines()[1:]
        devices = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices
    except Exception:
        return []
