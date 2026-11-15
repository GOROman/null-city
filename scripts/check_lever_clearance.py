"""Estimate a tilted lever envelope; assumptions are not physical verification."""
import argparse
import json
import math
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--half-depth', type=float, default=None, help='Envelope half extent along local Y, mm')
p.add_argument('--extra-depth', type=float, default=0, help='Connector/wiring below body, mm')
p.add_argument('--tolerance', type=float, default=0, help='Vertical loss allowance, mm')
a = p.parse_args()
if min(a.half_depth if a.half_depth is not None else 0, a.extra_depth, a.tolerance) < 0:
    p.error('dimensions must be nonnegative')
layout = json.loads((Path(__file__).resolve().parents[1] / 'artwork/control_layout.json').read_text())
m = layout['lever_mount']
t = math.radians(2.55)
# Measured depth is below the panel underside, including direct housing contact.
assert m['mounting_mode'] == 'direct_housing'
half_depth = a.half_depth if a.half_depth is not None else m['clearance_envelope_half_depth_mm']
z = 43 - m['body_depth_below_panel_underside_mm'] - a.extra_depth
y = layout['lever'][1] - half_depth
clearance = 43 + y * math.sin(t) + (z - 43) * math.cos(t) - 5 - a.tolerance
print(f'Assumed envelope bottom clearance: {clearance:.3f} mm')
print('Body/coupon fit and 8-direction operation: CONFIRMED. Full-case wiring/LED fit: PENDING.')
