#!/usr/bin/env python3
"""Find exact hex values for the 6 clinical-severity tokens needing contrast fixes."""
import math

def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb):
    def channel(c):
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

def contrast_ratio(hex1, hex2):
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    return (max(l1,l2) + 0.05) / (min(l1,l2) + 0.05)

canvas = '#F5F6F8'
white = '#FFFFFF'

candidates = {
    # on-surface-light (target ≥4.6:1 for safety)
    'clinical-severity-normal-on-surface-light': [
        ('#188242', '#1A8C47'),
        ('#177B3E', '#1A8C47'),
        ('#167437', '#1A8C47'),
        ('#157034', '#1A8C47'),
    ],
    'clinical-severity-watch-on-surface-light': [
        ('#906B04', '#B88A06'),
        ('#8A6500', '#B88A06'),
        ('#876100', '#B88A06'),
        ('#805C00', '#B88A06'),
    ],
    'clinical-severity-urgent-on-surface-light': [
        ('#B44E00', '#BD5000'),
        ('#AD4A00', '#BD5000'),
        ('#A84800', '#BD5000'),
    ],
    'clinical-severity-critical-on-surface-light': [
        ('#CE3449', '#E83D54'),
        ('#C53042', '#E83D54'),
        ('#C22D40', '#E83D54'),
        ('#B8283A', '#E83D54'),
    ],
    # signal-light (target ≥3.3:1 for safety)
    'clinical-severity-normal-signal-light': [
        ('#1E9448', '#23A352'),
        ('#1B8A40', '#23A352'),
        ('#1A853D', '#23A352'),
    ],
    'clinical-severity-urgent-signal-light': [
        ('#DA5E00', '#E96806'),
        ('#D05800', '#E96806'),
        ('#CC5500', '#E96806'),
    ],
}

for token, options in candidates.items():
    print(f"\n--- {token} ---")
    orig = options[0][1]
    cr_orig_canvas = contrast_ratio(orig, canvas)
    cr_orig_white = contrast_ratio(orig, white)
    print(f"  ORIGINAL: {orig}  canvas={cr_orig_canvas:.2f}:1  white={cr_orig_white:.2f}:1")
    
    for new_hex, _ in options:
        cr_c = contrast_ratio(new_hex, canvas)
        cr_w = contrast_ratio(new_hex, white)
        cr_min = min(cr_c, cr_w)
        if 'signal' in token:
            status = 'PASS' if cr_min >= 3.0 else 'FAIL'
            target_str = '≥3.0:1'
        else:
            status = 'PASS' if cr_min >= 4.5 else 'FAIL'
            target_str = '≥4.5:1'
        
        # Also check if the new color still looks like the right hue
        r, g, b = hex_to_rgb(new_hex)
        print(f"  → {new_hex}  rgb({r},{g},{b})  canvas={cr_c:.2f}:1  white={cr_w:.2f}:1  {target_str} [{status}]")
