#!/usr/bin/env python3
"""
frida_pinning_bypass.py - Generate and inject Frida scripts to bypass SSL certificate pinning.
Supports multiple Android/iOS pinning implementations.

Usage:
    python scripts/frida_pinning_bypass.py --generate android-generic --output ssl_bypass.js
    python scripts/frida_pinning_bypass.py --generate android-okhttp  --output ssl_bypass.js
    python scripts/frida_pinning_bypass.py --generate ios-generic      --output ssl_bypass.js
    python scripts/frida_pinning_bypass.py --inject --package com.target.app --script ssl_bypass.js

Requirements: pip install frida frida-tools  (for --inject)
Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import os
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

SCRIPTS = {
    "android-generic": """
// Android Generic SSL Pinning Bypass
// Targets: TrustManager, HostnameVerifier, SSLContext

Java.perform(function() {
    // Bypass TrustManager
    var TrustManager = Java.registerClass({
        name: 'com.bypass.CustomTrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    // Bypass SSLContext
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    var init = SSLContext.init.overload(
        '[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom'
    );
    init.implementation = function(keyManager, trustManager, secureRandom) {
        var tm = Java.array('javax.net.ssl.TrustManager', [TrustManager.$new()]);
        this.init(keyManager, tm, secureRandom);
    };

    // Bypass HostnameVerifier
    var hostnameVerifier = Java.use('javax.net.ssl.HttpsURLConnection');
    hostnameVerifier.setDefaultHostnameVerifier.implementation = function(verifier) {
        this.setDefaultHostnameVerifier(Java.use('javax.net.ssl.HttpsURLConnection')
            .getDefaultHostnameVerifier());
    };

    console.log('[+] Android Generic SSL Pinning Bypass active');
});
""",
    "android-okhttp": """
// Android OkHttp / OkHttp3 SSL Pinning Bypass
Java.perform(function() {
    // OkHttp3 CertificatePinner bypass
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(a, b) {
            console.log('[+] OkHttp3 CertificatePinner.check bypassed for: ' + a);
        };
        CertificatePinner.check.overload('java.lang.String', '[Ljava.security.cert.Certificate;').implementation = function(a, b) {
            console.log('[+] OkHttp3 CertificatePinner.check (cert) bypassed for: ' + a);
        };
    } catch(e) { console.log('OkHttp3 not found: ' + e); }

    // OkHttp2
    try {
        var OkHttpCertPinner = Java.use('com.squareup.okhttp.CertificatePinner');
        OkHttpCertPinner.check.overload('java.lang.String', '[Ljava.security.cert.Certificate;').implementation = function(a, b) {
            console.log('[+] OkHttp2 CertificatePinner bypassed for: ' + a);
        };
    } catch(e) { console.log('OkHttp2 not found: ' + e); }

    // TrustKit (iOS-style on Android)
    try {
        var TrustKit = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
        TrustKit.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function(a, b) {
            return true;
        };
    } catch(e) {}

    console.log('[+] OkHttp SSL Pinning Bypass active');
});
""",
    "ios-generic": """
// iOS Generic SSL Pinning Bypass (requires Frida on jailbroken device)
// Targets: NSURLSession, SecTrustEvaluate, TrustKit

var SecTrustEvaluate = new NativeFunction(
    Module.findExportByName('Security', 'SecTrustEvaluate'), 'int', ['pointer', 'pointer']
);
Interceptor.replace(SecTrustEvaluate, new NativeCallback(function(trust, result) {
    var kSecTrustResultProceed = 1;
    Memory.writeU32(result, kSecTrustResultProceed);
    return 0; // errSecSuccess
}, 'int', ['pointer', 'pointer']));

// Also hook SecTrustEvaluateWithError (iOS 12+)
try {
    var SecTrustEvaluateWithError = new NativeFunction(
        Module.findExportByName('Security', 'SecTrustEvaluateWithError'), 'bool', ['pointer', 'pointer']
    );
    Interceptor.replace(SecTrustEvaluateWithError, new NativeCallback(function(trust, error) {
        if (error !== null) Memory.writePointer(error, NULL);
        return 1; // true = trusted
    }, 'bool', ['pointer', 'pointer']));
} catch(e) {}

console.log('[+] iOS SSL Pinning Bypass active (SecTrustEvaluate patched)');
""",
}


def generate_script(target: str, output_path: str):
    if target not in SCRIPTS:
        print(f"[-] Unknown target: {target}. Available: {', '.join(SCRIPTS.keys())}")
        sys.exit(1)
    script = SCRIPTS[target]
    with open(output_path, "w") as f:
        f.write(script)
    print(f"[+] Frida script written: {output_path} ({os.path.getsize(output_path):,} bytes)")
    print(f"[*] Usage: frida -U -f com.target.app -l {output_path} --no-pause")
    print(f"[*] Or: frida -U -n TargetApp -l {output_path}")


def inject_script(package: str, script_path: str):
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)
    try:
        import frida
    except ImportError:
        print("[-] frida not installed: pip install frida frida-tools"); sys.exit(1)

    with open(script_path) as f:
        script_code = f.read()

    device = frida.get_usb_device(timeout=10)
    session = device.attach(package)
    script = session.create_script(script_code)
    script.on("message", lambda msg, _: print(f"[Frida] {msg}"))
    script.load()
    print(f"[+] Script injected into {package}")
    print("[*] Press Ctrl+C to stop...")
    import signal
    signal.pause()


def main():
    p = argparse.ArgumentParser(description="SSL pinning bypass via Frida (authorized use only)")
    p.add_argument("--generate", choices=list(SCRIPTS.keys()), help="Generate Frida script")
    p.add_argument("--inject", action="store_true", help="Inject script into running app")
    p.add_argument("--package", help="Android package or iOS bundle ID")
    p.add_argument("--script", default="ssl_bypass.js", help="Frida script file")
    p.add_argument("--output", default="ssl_bypass.js")
    args = p.parse_args()

    if args.generate:
        generate_script(args.generate, args.output)
    elif args.inject:
        if not args.package: print("[-] --package required"); sys.exit(1)
        inject_script(args.package, args.script)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
