#!/usr/bin/env python3
"""
canvas_spoof.py - Generate canvas fingerprint spoofing JavaScript injection code.
Outputs JS that can be injected into a page to randomize/spoof canvas fingerprints.

Usage:
    python scripts/canvas_spoof.py --output spoof.js
    python scripts/canvas_spoof.py --output spoof.js --noise 0.00005 --mode noise
    python scripts/canvas_spoof.py --mode block --output spoof.js  (blocks canvas reads)
"""
import argparse
import os
import random
import sys


def generate_noise_js(noise_level: float = 0.00003) -> str:
    """Generate JS that adds subtle noise to canvas pixel data."""
    seed = random.randint(10000, 99999)
    return f"""
// Canvas fingerprint noise injection (noise level: {noise_level})
// Inject via playwright context.add_init_script() or browser extension
(function() {{
    const SEED = {seed};
    const NOISE = {noise_level};

    function seededRandom(seed, i) {{
        let x = Math.sin(seed + i) * 10000;
        return x - Math.floor(x);
    }}

    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            const imgData = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imgData.data.length; i += 4) {{
                imgData.data[i]   = Math.min(255, imgData.data[i]   + Math.floor(seededRandom(SEED, i)   * NOISE * 255));
                imgData.data[i+1] = Math.min(255, imgData.data[i+1] + Math.floor(seededRandom(SEED, i+1) * NOISE * 255));
                imgData.data[i+2] = Math.min(255, imgData.data[i+2] + Math.floor(seededRandom(SEED, i+2) * NOISE * 255));
            }}
            ctx.putImageData(imgData, 0, 0);
        }}
        return origToDataURL.call(this, type, quality);
    }};

    const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {{
        const data = origGetImageData.call(this, x, y, w, h);
        for (let i = 0; i < data.data.length; i += 4) {{
            data.data[i]   = Math.min(255, data.data[i]   + (seededRandom(SEED, i)   < NOISE ? 1 : 0));
            data.data[i+1] = Math.min(255, data.data[i+1] + (seededRandom(SEED, i+1) < NOISE ? 1 : 0));
        }}
        return data;
    }};

    // WebGL fingerprint spoof
    const origGetParam = WebGLRenderingContext.prototype.getParameter;
    const params = {{
        37445: 'Google Inc. (NVIDIA)',
        37446: 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    }};
    WebGLRenderingContext.prototype.getParameter = function(param) {{
        if (params[param]) return params[param];
        return origGetParam.call(this, param);
    }};

    console.log('[Stealth] Canvas fingerprint noise active (seed={seed})');
}})();
"""


def generate_block_js() -> str:
    """Block all canvas read operations."""
    return """
// Canvas read blocker - returns blank/empty data for all reads
(function() {
    HTMLCanvasElement.prototype.toDataURL = function() { return 'data:image/png;base64,'; };
    HTMLCanvasElement.prototype.toBlob = function(cb) { cb(new Blob()); };
    CanvasRenderingContext2D.prototype.getImageData = function(x,y,w,h) {
        return new ImageData(w, h);
    };
    console.log('[Stealth] Canvas reads blocked');
})();
"""


def main():
    p = argparse.ArgumentParser(description="Canvas fingerprint spoofing JS generator")
    p.add_argument("--mode", choices=["noise","block"], default="noise")
    p.add_argument("--noise", type=float, default=0.00003, help="Noise level (0.00001 to 0.0001)")
    p.add_argument("--output", default="canvas_spoof.js")
    args = p.parse_args()

    if args.mode == "noise":
        js = generate_noise_js(args.noise)
    else:
        js = generate_block_js()

    with open(args.output, "w") as f:
        f.write(js)
    print(f"[+] Canvas spoof JS written to {args.output} ({os.path.getsize(args.output):,} bytes)")
    print(f"[*] Inject via: context.add_init_script(open('{args.output}').read())")


if __name__ == "__main__":
    main()
