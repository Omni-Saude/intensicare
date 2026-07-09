#!/usr/bin/env python3
"""Final verification of all 6 fixed tokens."""
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
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

canvas = '#F5F6F8'

fixed = {
    'clinical-severity-normal-on-surface-light': ('#1A8C47', '#177B3E', 4.5),
    'clinical-severity-watch-on-surface-light': ('#B88A06', '#8A6500', 4.5),
    'clinical-severity-urgent-on-surface-light': ('#BD5000', '#B44E00', 4.5),
    'clinical-severity-critical-on-surface-light': ('#E83D54', '#C53042', 4.5),
    'clinical-severity-normal-signal-light': ('#23A352', '#1E9448', 3.0),
    'clinical-severity-urgent-signal-light': ('#E96806', '#DA5E00', 3.0),
}

print("FINAL CONTRAST VERIFICATION")
print(f"Background: {canvas}")
print()
print(f"{'TOKEN':<48} {'BEFORE':>8} {'AFTER':>8} {'TARGET':>8} {'STATUS'}")
print("-" * 85)

all_pass = True
for name, (old, new, target) in fixed.items():
    cr_before = contrast_ratio(old, canvas)
    cr_after = contrast_ratio(new, canvas)
    status = "PASS" if cr_after >= target else "FAIL"
    if cr_after < target:
        all_pass = False
    print(f"{name:<48} {cr_before:>5.2f}:1 {cr_after:>5.2f}:1   ≥{target}:1  [{status}]")

print()
if all_pass:
    print("✅ ALL 6 TOKENS PASS WCAG AA CONTRAST REQUIREMENTS")
else:
    print("❌ SOME TOKENS STILL FAIL")
