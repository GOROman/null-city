"""Estimate a tilted lever envelope; assumptions are not physical verification."""
import argparse
import json
import math
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--half-depth', type=float, default=47.5, help='Envelope half extent along local Y, mm')
p.add_argument('--extra-depth', type=float, default=0, help='Connector/wiring below body, mm')
p.add_argument('--tolerance', type=float, default=0, help='Vertical loss allowance, mm')
a = p.parse_args()
if min(a.half_depth, a.extra_depth, a.tolerance) < 0:
    p.error('dimensions must be nonnegative')
layout = json.loads((Path(__file__).resolve().parents[1] / 'artwork/control_layout.json').read_text())
m = layout['lever_mount']
t = math.radians(2.55)
# Local panel top 47, underside 43. Body depth is from MS plate TOP;
# the 1.6 mm plate is already included in that datum and must not be counted twice.
z = 47 - 4 - m['spacer_height_mm'] - m['body_depth_below_plate_top_mm'] - a.extra_depth
y = layout['lever'][1] - a.half_depth
clearance = 43 + y * math.sin(t) + (z - 43) * math.cos(t) - 5 - a.tolerance
print(f'Assumed envelope bottom clearance: {clearance:.3f} mm')
print('Physical verification: PENDING; envelope and connector dimensions must be measured.')
