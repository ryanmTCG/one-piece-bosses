#!/usr/bin/env python3
"""Builds every rogue's own body: the 3D model (Java) and the skin painted to fit it.

    python3 tools/gen_models.py .

Writes src/main/java/com/onepiecebosses/client/RogueModels.java and
src/main/resources/assets/opbosses/textures/entity/boss/<id>.png (128x128, or 256x256 if the boxes don't fit).
Change a shape or a colour here and run it again; don't edit the generated files by hand.

Model space is Minecraft's: 16 px = 1 block, y points down, the front is -z, the right side is -x, and the feet
stand on y = 24. Each part has a pivot (where it turns: the neck, the shoulders, the hips); a box's x, y, z are
measured from its part's pivot, or from the box's own pivot when it has one (rotated boxes and swaying
cloth turn around that point). Arm and leg boxes are given for the right side and copied to the left.
The parts animate like a player's (walking, swinging, looking around); "sway" boxes (coat tails, trains, skirts)
also swing back as the boss walks: sway=1 swings out behind, sway=-1 out in front.
"""
import os
import random
import sys

from PIL import Image

# ---------------- the rogues ----------------
# part pivots: head, body, arm (right shoulder; the left one is mirrored), leg (right hip; mirrored).
# box: (part, x, y, z, w, h, d, colour, pattern, extras) with extras like front='face', rot=(rx,ry,rz),
#      pivot=(px,py,pz) for a rotated box, sway=1, mirror=True (body/head boxes: also add a copy on the other side).

def B(part, x, y, z, w, h, d, colour, pattern=None, **extra):
    return dict(part=part, x=x, y=y, z=z, w=w, h=h, d=d, colour=colour, pattern=pattern, **extra)


ROGUES = {
    # A walking wall of muscle: barrel chest, Popeye forearms that reach the ground, little legs,
    # a slab of an underbite jaw, and his anchor slung across his back.
    "saltjaw_rourke": dict(
        pivots=dict(head=(0, 1, -2), body=(0, 0, 0), arm=(-9.5, 3, 0), leg=(-3, 19, 0)),
        boxes=[
            B('head', -3.5, -7, -3.5, 7, 6, 7, '#c48c64', None, front='face', eyes='#202020', brows='#3a2a1a', mouth=None),
            B('head', -5, -3, -5.5, 10, 5, 8, '#c48c64', 'stubble', front='jaw', teeth='underbite'),
            B('head', -4, -8, -4, 8, 2, 8, '#a82828', 'cloth'),                       # bandana
            B('head', 0, -0.5, -1, 3, 1, 4, '#a82828', 'cloth', rot=(0, 0, 0.5), pivot=(3.5, -7, 3)),  # bandana knot tail
            B('body', -8, 1, -5, 16, 11, 10, '#9a8c70', 'cloth', front='vest'),        # barrel chest in an open vest
            B('body', -7, 12, -4.5, 14, 7, 9, '#4a4a5a', 'cloth', front='belt'),       # belly and belt
            B('body', -1, -3, 5, 2, 20, 2, '#7a7a80', 'iron'),                         # anchor shank on his back
            B('body', -7, 13, 5, 14, 2, 2, '#7a7a80', 'iron'),                         # anchor arms
            B('body', -8, 9, 5, 2, 5, 2, '#7a7a80', 'iron', mirror=True),              # anchor flukes
            B('body', -3, -6, 5, 6, 3, 2, '#7a7a80', 'iron'),                          # anchor ring
            B('body', -6, 0, -5.4, 2, 12, 1, '#8a8a90', 'chain', rot=(0, 0, -0.5)),     # chain across the chest
            B('arm', -3, -3, -3, 6, 7, 6, '#9a8c70', 'cloth'),                         # shoulder
            B('arm', -4.5, 4, -4, 8, 10, 8, '#c48c64', 'tattoo'),                      # huge forearm
            B('arm', -4, 14, -3.5, 7, 5, 7, '#b88060', None, front='knuckles'),        # fist
            B('leg', -2, 0, -2, 4, 3, 4, '#4a4a5a', 'cloth'),
            B('leg', -2.5, 3, -3, 5, 2, 5, '#3a2a1a', 'leather'),
        ]),
    # Impossibly tall and thin: stilt legs, a wasp waist, arms past her knees, a hat as wide as a table
    # with a veil, and a long train of fog-grey coat behind her. Her lantern hangs from one hand.
    "corvina_fog_widow": dict(
        pivots=dict(head=(0, -9, 0), body=(0, -9, 0), arm=(-4.5, -7, 0), leg=(-1.6, 5, 0)),
        boxes=[
            B('head', -3, -7, -3, 6, 7, 6, '#e6d2c8', None, front='face', eyes='#8cc8dc', brows='#1a1820', mouth='smirk', lashes=True),
            B('head', -3.5, -7.5, 1.5, 7, 13, 2, '#1a1820', 'hair'),                   # long black hair
            B('head', -9, -7.5, -9, 18, 1, 18, '#24202e', 'cloth'),                    # hat brim
            B('head', -3.5, -12, -3.5, 7, 5, 7, '#24202e', 'cloth', front='hatband'),   # hat crown
            B('head', -3.5, -6.5, -3.9, 7, 3, 1, '#3c3848', 'veil'),                   # veil
            B('body', -3.5, 0, -2, 7, 6, 4, '#3c3448', 'cloth', front='corset'),
            B('body', -4.5, -1.5, -3, 9, 3, 6, '#6a6478', 'ruff'),                    # high collar
            B('body', -1.5, 6, -1.5, 3, 4, 3, '#2a2434', 'cloth'),                     # wasp waist
            B('body', -3.5, 10, -2.5, 7, 4, 5, '#2a2434', 'cloth'),                    # hips
            B('body', -5, 0, 0, 10, 30, 1, '#4a4658', 'fog', sway=1, pivot=(0, 1, 2.5)),  # long coat train
            B('arm', -1.5, -1, -1, 2, 17, 2, '#3c3448', 'cloth'),
            B('arm', -1.7, 15, -1.2, 2.4, 2, 2.4, '#e6d2c8'),                          # hand
            B('arm', -2.5, 17, -1.5, 3, 4, 3, '#e8c060', None, front='lantern', only='right'),
            B('leg', -1, 0, -1, 2, 17, 2, '#2a2434', 'cloth'),
            B('leg', -1.2, 17, -2, 2.4, 2, 3, '#14121a', 'leather'),
        ]),
    # A slab-shouldered officer gone bad: V-shaped torso twice as wide as his hips, a chin you could
    # land a ship on, a towering Marine cap, epaulettes like serving trays and a torn "Justice" coat.
    "iron_tide_graves": dict(
        pivots=dict(head=(0, -5, -1), body=(0, -4, 0), arm=(-10, -2, 0), leg=(-2.2, 13, 0)),
        boxes=[
            B('head', -3, -8, -3.5, 6, 6, 7, '#cda07d', None, front='face', eyes='#284060', brows='#9a9aa0', mouth=None, scar=True),
            B('head', -4, -2.5, -5.5, 8, 4, 7, '#cda07d', 'stubble', front='jaw', teeth='grim'),   # the chin
            B('head', -4.5, -13, -4.5, 9, 5, 9, '#f0f0f4', 'cloth', front='anchor_badge'),   # cap crown
            B('head', -4, -8.5, -4, 8, 1, 8, '#28304a', 'cloth'),                    # cap band
            B('head', -4, -8.5, -6.5, 8, 1, 3, '#14141c', 'leather'),                # peak
            B('body', -8, 0, -4, 16, 7, 8, '#f0f0f4', 'cloth', front='shirt'),        # shoulders and chest
            B('body', -5.5, 7, -3, 11, 7, 6, '#323850', 'cloth', front='buttons'),
            B('body', -6, 13, -3.5, 12, 3, 7, '#14141c', 'leather', front='buckle'),
            B('body', -8, 0, 0, 16, 12, 1, '#f0f0f4', 'justice', sway=1, pivot=(0, 0, 4.5)),   # coat cape
            B('body', -9, 0, 0, 18, 10, 1, '#f0f0f4', 'justice_low', sway=1, pivot=(0, 12, 0), parent='sway0'),
            B('arm', -3.5, -3, -3.5, 7, 3, 7, '#d8b040', 'fringe'),                  # epaulette
            B('arm', -2.5, 0, -2.5, 5, 13, 5, '#f0f0f4', 'cloth'),
            B('arm', -2, 13, -2, 4, 3, 4, '#cda07d'),
            B('leg', -2, 0, -2, 4, 8, 4, '#323850', 'cloth'),
            B('leg', -2.5, 8, -2.5, 5, 3, 5, '#14141c', 'leather'),
        ]),
    # Hollow armour with nothing inside: every piece floats apart from the rest, held by nothing.
    # A crescent-crested helm over two glowing eyes, shoulder plates like doors, a plated skirt.
    "hollow_ronin_tsurugi": dict(
        pivots=dict(head=(0, -6, 0), body=(0, -2, 0), arm=(-8, 0, 0), leg=(-2.4, 15, 0)),
        boxes=[
            B('head', -4, -6, -4, 8, 4, 8, '#08080c', None, front='void_eyes'),       # empty face
            B('head', -4.5, -10, -4.5, 9, 5, 9, '#2c2834', 'lacquer'),                 # kabuto bowl
            B('head', -6, -6, -2, 12, 3, 7, '#2c2834', 'plates'),                     # neck guard
            B('head', -3.5, -3, -4.8, 7, 4, 1, '#8c2028', 'lacquer', front='menpo'),   # mask
            B('head', -0.5, -7, -0.5, 1, 8, 1, '#c8a040', 'gold', rot=(0, 0, -0.55), pivot=(-1, -9, -4.6), mirror=True),  # crest
            B('body', -3.5, 0, -2, 7, 13, 4, '#08080c'),                              # the void inside
            B('body', -5, 1, -3, 10, 9, 6, '#8c2028', 'lacquer', front='lacing'),     # chest armour
            B('body', -5.5, 0, 0, 11, 6, 1, '#2c2834', 'plates', sway=-1, pivot=(0, 10, -3.6)),  # front skirt plates
            B('body', -5.5, 0, 0, 11, 6, 1, '#2c2834', 'plates', sway=1, pivot=(0, 10, 3.0)),     # back skirt plates
            B('arm', -5, -3, -3.5, 6, 8, 7, '#8c2028', 'plates'),                    # sode (shoulder plate)
            B('arm', -1.5, 5, -1.5, 3, 9, 3, '#2c2834', 'lacquer'),
            B('arm', -2, 14, -2, 4, 3, 4, '#2c2834', 'plates'),
            B('leg', -2, 0, -2, 4, 7, 4, '#2c2834', 'plates'),
            B('leg', -2.5, 7, -3, 5, 2, 5, '#1c1820', 'lacquer'),
        ]),
    # A ship's boiler with a man somewhere on top: a riveted belly as big as a cabin with a glowing firebox,
    # two smokestacks, piston arms ending in sledgehammer fists, stubby iron legs and a tiny goggled head.
    "boilerheart_gantz": dict(
        pivots=dict(head=(0, -7, -4), body=(0, -6, 0), arm=(-11, -2, 0), leg=(-4.5, 19, 0)),
        boxes=[
            B('head', -2.5, -5, -2.5, 5, 5, 5, '#b4785a', None, front='face', eyes=None, brows=None, mouth='grit', goggles=True),
            B('head', -3, -4, -3, 6, 2, 6, '#5a4a3a', 'leather'),                    # goggle strap
            B('body', -9, 0, -8, 18, 20, 16, '#8a5a3a', 'rivets', front='firebox'),   # the boiler
            B('body', -9.5, 4, -8.5, 19, 2, 17, '#5a5a62', 'iron'),                   # boiler bands
            B('body', -9.5, 14, -8.5, 19, 2, 17, '#5a5a62', 'iron'),
            B('body', -6, -9, 4, 3, 10, 3, '#3a3a40', 'soot'),                        # smokestacks
            B('body', 3, -12, 4, 3, 13, 3, '#3a3a40', 'soot'),
            B('body', -1.5, -2, -8.6, 3, 2, 1, '#d8c070', 'gold'),                    # pressure gauge
            B('arm', -3, -3, -3, 6, 6, 6, '#5a5a62', 'rivets'),                       # shoulder joint
            B('arm', -1.5, 3, -1.5, 3, 8, 3, '#9a9aa4', 'piston'),                    # piston rod
            B('arm', -4, 11, -4, 8, 8, 8, '#5a5a62', 'rivets', front='knuckles'),     # sledgehammer fist
            B('leg', -2.5, 0, -2.5, 5, 5, 5, '#5a5a62', 'rivets'),
        ]),
    # Tall and eerie: a long robed body, arms that hang to his knees, a great dorsal fin, fin ears,
    # a shark's jaw full of fangs, white hair streaming back and a crown of coral.
    "nereus_vane": dict(
        pivots=dict(head=(0, -6, 0), body=(0, -6, 0), arm=(-8, -5, 0), leg=(-2.5, 14, 0)),
        boxes=[
            B('head', -4, -8, -4, 8, 6, 8, '#5a96a0', 'scales', front='face', eyes='#f8f078', brows=None, mouth=None, slit=True),
            B('head', -4.5, -3, -5, 9, 4, 6, '#5a96a0', 'scales', front='jaw', teeth='fangs'),
            B('head', -4, -1.5, -0.5, 8, 16, 2, '#e8eef0', 'hair', sway=1, pivot=(0, -7, 3)),   # white hair
            B('head', -0.5, -5, -2, 1, 5, 5, '#3c7884', 'fin', rot=(0, 0, -0.6), pivot=(-4.2, -5, 0), mirror=True),   # fin ears
            B('head', -0.5, -6, -0.5, 1, 6, 1, '#e87860', 'coral', rot=(0, 0, -0.35), pivot=(-2.5, -8, -2), mirror=True),
            B('head', -0.5, -7, -0.5, 1, 7, 1, '#e87860', 'coral', pivot=(0, -8, -2.5)),
            B('body', -7, 0, -3.5, 14, 4, 7, '#1e3a5a', 'robe', front='trim'),        # broad shoulders
            B('body', -5, 4, -3, 10, 14, 6, '#1e3a5a', 'robe', front='trim'),         # long body
            B('body', -0.5, -3, 0, 1, 12, 7, '#3c7884', 'fin', rot=(0.25, 0, 0), pivot=(0, 1, 3)),   # dorsal fin
            B('body', -6, 0, 0, 12, 12, 1, '#1e3a5a', 'robe', sway=-1, pivot=(0, 18, -3.4)),   # robe, front
            B('body', -6, 0, 0, 12, 13, 1, '#1e3a5a', 'robe', sway=1, pivot=(0, 18, 3.2)),     # robe, back
            B('arm', -2, -1, -2, 4, 20, 4, '#5a96a0', 'scales', front='bands'),
            B('arm', -2.5, 19, -2.5, 5, 4, 5, '#4a8690', 'web'),
            B('leg', -2, 0, -2, 4, 10, 4, '#5a96a0', 'scales'),
        ]),
}

# ---------------- painting ----------------

def rgb(hexstr):
    h = hexstr.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def paint_face_texture(img, x0, y0, w, h, colour, pattern, rnd, face):
    """One face of a box: base colour, light per face, then the pattern."""
    px = img.load()
    light = {'top': 1.12, 'bottom': 0.72, 'front': 1.0, 'back': 0.86, 'right': 0.92, 'left': 0.92}[face]
    base = shade(colour, light)
    for y in range(h):
        for x in range(w):
            c = base
            n = rnd.random()
            if pattern in ('cloth', 'robe', 'fog'):
                c = shade(base, 0.94 + 0.1 * n)
                if pattern == 'robe' and y % 5 == 0:
                    c = shade(base, 0.9)
                if pattern == 'fog' and (x + y * 2) % 7 == 0:
                    c = shade(base, 1.15)
            elif pattern in ('hair',):
                c = shade(base, 0.85 + 0.25 * ((x * 3 + n * 2) % 3) / 3)
            elif pattern == 'stubble':
                c = shade(base, 0.82) if n < 0.3 else base
            elif pattern == 'tattoo':
                c = (40, 70, 120) if (x + y) % 6 == 0 and 2 < y < h - 2 else shade(base, 0.96 + 0.06 * n)
            elif pattern in ('iron', 'soot'):
                c = shade(base, 0.85 + 0.25 * n)
                if pattern == 'soot' and y < 2:
                    c = (25, 25, 28)
            elif pattern == 'rivets':
                c = shade(base, 0.9 + 0.12 * n)
                if (x % 4 == 1 and y % 4 == 1):
                    c = (200, 190, 170)
                if y % 8 == 0:
                    c = shade(base, 0.7)
            elif pattern == 'chain':
                c = shade(base, 1.2) if y % 2 == 0 else shade(base, 0.6)
            elif pattern == 'leather':
                c = shade(base, 0.9 + 0.15 * n)
            elif pattern == 'veil':
                c = shade(base, 1.3) if (x + y) % 2 == 0 else shade(base, 0.7)
            elif pattern == 'ruff':
                c = shade(base, 1.2) if x % 2 == 0 else shade(base, 0.85)
            elif pattern in ('justice', 'justice_low'):
                c = shade(base, 0.95 + 0.07 * n)
                if pattern == 'justice_low' and y >= h - 2 and (x * 7 + y) % 3 == 0:
                    c = (0, 0, 0)   # ragged hem (cut out)
            elif pattern == 'fringe':
                c = shade(base, 1.15) if y == 0 else (shade(base, 0.85) if x % 2 else base)
            elif pattern == 'lacquer':
                c = shade(base, 1.0 + 0.08 * n)
                if x == 0 or y == 0:
                    c = shade(base, 1.35)
            elif pattern == 'plates':
                c = shade(base, 0.95 + 0.05 * n)
                if y % 3 == 2:
                    c = (200, 160, 70)   # gold lacing between the plates
            elif pattern == 'gold':
                c = shade(base, 0.9 + 0.3 * n)
            elif pattern == 'piston':
                c = shade(base, 1.25) if x == w // 2 else shade(base, 0.9)
            elif pattern == 'scales':
                c = shade(base, 0.92 + 0.12 * ((x + (y % 2)) % 2))
            elif pattern == 'fin':
                c = shade(base, 0.85) if y % 2 == 0 else base
            elif pattern == 'coral':
                c = shade(base, 1.2) if n < 0.3 else base
            elif pattern == 'web':
                c = shade(base, 0.8) if x % 2 == 0 else base
            if c == (0, 0, 0):
                px[x0 + x, y0 + y] = (0, 0, 0, 0)
            else:
                px[x0 + x, y0 + y] = c + (255,)


def dot(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgb(c) + (255,) if isinstance(c, str) else c + (255,))


def decorate_front(img, x0, y0, w, h, box):
    """The details drawn on a box's front face: faces, jaws, buckles, the firebox..."""
    kind = box.get('front')
    cx = x0 + w // 2
    if kind == 'face':
        ey = y0 + h // 2
        if box.get('goggles'):
            for gx in (cx - 2, cx + 1):
                for dx in range(2):
                    dot(img, gx + dx, ey - 1, '#ffb43c'); dot(img, gx + dx, ey, '#c87820')
            dot(img, cx - 1, ey - 1, '#5a4a3a'); dot(img, cx, ey - 1, '#5a4a3a')
        elif box.get('eyes'):
            for ex in (cx - 2 - (w > 6), cx + 1 + (w > 6)):
                dot(img, ex, ey, '#f4f4f4' if not box.get('slit') else box['eyes'])
                dot(img, ex + (1 if ex < cx else -1) * 0, ey, box['eyes'])
                if box.get('lashes'):
                    dot(img, ex, ey - 1, '#101010')
        if box.get('brows'):
            for bx in range(w // 2 - 1):
                dot(img, x0 + 1 + bx, ey - 2, box['brows']); dot(img, x0 + w - 2 - bx, ey - 2, box['brows'])
        if box.get('scar'):
            for i in range(4):
                dot(img, x0 + 1 + i, ey - 3 + i, '#a05a50')
        mouth = box.get('mouth')
        my = y0 + h - 2
        if mouth == 'smirk':
            dot(img, cx - 1, my, '#8a3a4a'); dot(img, cx, my, '#8a3a4a'); dot(img, cx + 1, my - 1, '#8a3a4a')
        elif mouth == 'grit':
            for dx in range(-2, 2):
                dot(img, cx + dx, my, '#f0f0e8' if dx % 2 else '#303030')
    elif kind == 'jaw':
        my = y0 + h // 2
        teeth = box.get('teeth')
        for dx in range(-(w // 2) + 1, w // 2 - 1):
            dot(img, cx + dx, my, '#3a1a1a')
            if teeth == 'underbite' and dx % 2 == 0:
                dot(img, cx + dx, my - 1, '#f4f0e0')
            if teeth == 'fangs':
                dot(img, cx + dx, my - 1, '#f8f8f0'); dot(img, cx + dx, my + 1, '#f8f8f0' if dx % 2 else '#3a1a1a')
            if teeth == 'grim' and abs(dx) < 3:
                dot(img, cx + dx, my - 1, '#e8e4dc')
    elif kind == 'vest':
        for y in range(h):
            for x in range(w // 2 - 3, w // 2 + 3):
                dot(img, x0 + x, y0 + y, shade(rgb(box['colour']) if False else (196, 140, 100), 0.95 + 0.05 * ((x + y) % 2)))
        for y in range(2, 5):
            dot(img, cx - 1, y0 + y, '#6a4a30'); dot(img, cx + 1, y0 + y, '#6a4a30')   # chest hair
    elif kind == 'belt':
        for x in range(w):
            dot(img, x0 + x, y0 + 1, '#3a2a1a'); dot(img, x0 + x, y0 + 2, '#3a2a1a')
        for dx in range(-1, 2):
            dot(img, cx + dx, y0 + 1, '#d0b040'); dot(img, cx + dx, y0 + 2, '#d0b040')
    elif kind == 'knuckles':
        for x in range(1, w - 1, 2):
            dot(img, x0 + x, y0 + 1, shade(rgb(box['colour']), 0.75))
    elif kind == 'hatband':
        for x in range(w):
            dot(img, x0 + x, y0 + h - 2, '#8a2a3a')
        dot(img, x0 + 1, y0 + h - 3, '#d8d8e0'); dot(img, x0 + 2, y0 + h - 4, '#d8d8e0')   # a feather
    elif kind == 'corset':
        for y in range(0, h, 2):
            dot(img, cx - 1, y0 + y, '#c8a050'); dot(img, cx, y0 + y + 1, '#c8a050')
    elif kind == 'lantern':
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                dot(img, x0 + x, y0 + y, '#fff0a0')
    elif kind == 'anchor_badge':
        for dy in range(3):
            dot(img, cx, y0 + 1 + dy, '#d8b040')
        dot(img, cx - 1, y0 + 3, '#d8b040'); dot(img, cx + 1, y0 + 3, '#d8b040')
    elif kind == 'shirt':
        for y in range(h):
            dot(img, cx, y0 + y, '#c8c8d0')
        for y in range(2, h):
            dot(img, x0 + 1, y0 + y, '#323850'); dot(img, x0 + 2, y0 + y, '#323850')
            dot(img, x0 + w - 2, y0 + y, '#323850'); dot(img, x0 + w - 3, y0 + y, '#323850')
    elif kind == 'buttons':
        for y in range(1, h, 2):
            dot(img, cx - 2, y0 + y, '#d8b040'); dot(img, cx + 1, y0 + y, '#d8b040')
    elif kind == 'buckle':
        for dx in range(-1, 2):
            dot(img, cx + dx, y0 + 1, '#d8b040')
    elif kind == 'void_eyes':
        ey = y0 + h // 2
        for ex in (cx - 2, cx + 1):
            dot(img, ex, ey, '#78e6ff'); dot(img, ex + 1, ey, '#c8f8ff')
    elif kind == 'menpo':
        for dx in range(-2, 2):
            dot(img, cx + dx, y0 + 2, '#f0f0f0' if dx % 2 else '#200808')
    elif kind == 'lacing':
        for y in range(1, h, 2):
            for x in range(1, w - 1):
                dot(img, x0 + x, y0 + y, '#d8b048' if (x + y) % 3 else '#a07a30')
    elif kind == 'firebox':
        gy, gh = y0 + h // 2, 6
        for y in range(gh):
            for x in range(-4, 4):
                c = '#ffd060' if (x + y) % 2 == 0 else '#ff7a18'
                if y in (0, gh - 1) or x in (-4, 3) or x == 0:
                    c = '#2a2a2e'
                dot(img, cx + x, gy + y, c)
    elif kind == 'trim':
        for y in range(h):
            dot(img, cx - 1, y0 + y, '#f0dc96'); dot(img, cx, y0 + y, '#f0dc96')
    elif kind == 'bands':
        for y in range(2, h, 5):
            for x in range(w):
                dot(img, x0 + x, y0 + y, '#f0dc96')


# ---------------- layout ----------------

def expand(spec):
    """Mirrors the arm and leg boxes to the left side, and mirrored body/head boxes to the other side."""
    out = []
    for i, b in enumerate(spec['boxes']):
        part = b['part']
        if part in ('arm', 'leg'):
            right = dict(b, part='right_' + part)
            left = dict(b, part='left_' + part, x=-(b['x'] + b['w']))
            if 'pivot' in b:
                px, py, pz = b['pivot']
                left['pivot'] = (-px, py, pz)
            if 'rot' in b:
                rx, ry, rz = b['rot']
                left['rot'] = (rx, -ry, -rz)
            only = b.get('only')
            if only != 'left':
                out.append(right)
            if only != 'right':
                out.append(left)
        else:
            out.append(b)
            if b.get('mirror'):
                m = dict(b, x=-(b['x'] + b['w']), mirror=False)
                if 'pivot' in b:
                    px, py, pz = b['pivot']
                    m['pivot'] = (-px, py, pz)
                if 'rot' in b:
                    rx, ry, rz = b['rot']
                    m['rot'] = (rx, -ry, -rz)
                out.append(m)
    return out


def pack(boxes, size):
    """Shelf-packs every box's UV net (2d+2w wide, d+h tall). Returns (u, v) per box, or None if it won't fit."""
    x = y = shelf = 0
    spots = []
    for b in boxes:
        bw, bh = int(2 * b['d'] + 2 * b['w']) + 1, int(b['d'] + b['h']) + 1
        if x + bw > size:
            x, y, shelf = 0, y + shelf, 0
        if y + bh > size or bw > size:
            return None
        spots.append((x, y))
        x += bw
        shelf = max(shelf, bh)
    return spots


def paint_box(img, u, v, b, rnd):
    w, h, d = int(round(b['w'])), int(round(b['h'])), int(round(b['d']))
    colour = rgb(b['colour'])
    pat = b.get('pattern')
    faces = {
        'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
        'right': (u, v + d, d, h), 'front': (u + d, v + d, w, h),
        'left': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h),
    }
    for name, (fx, fy, fw, fh) in faces.items():
        paint_face_texture(img, fx, fy, fw, fh, colour, pat, rnd, name)
    if b.get('front'):
        fx, fy, fw, fh = faces['front']
        decorate_front(img, fx, fy, fw, fh, b)
    if b.get('pattern') in ('justice', ) and b['w'] >= 12:
        # The Navy's "Justice" on the back of the coat, torn through.
        fx, fy, fw, fh = faces['back']
        for i, x in enumerate(range(fx + 2, fx + fw - 2)):
            if i % 3 != 2 and i != 5:
                dot(img, x, fy + 3, (40, 48, 74)); dot(img, x, fy + 4 + (i % 2), (40, 48, 74))


# ---------------- Java ----------------

def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return (s if s not in ('-0', '') else '0') + 'F'


def java(rogues, layouts):
    lines = []
    w = lines.append
    w('package com.onepiecebosses.client;')
    w('')
    w('import java.util.Map;')
    w('import java.util.Set;')
    w('')
    w('import net.minecraft.client.model.HumanoidModel;')
    w('import net.minecraft.client.model.geom.ModelLayerLocation;')
    w('import net.minecraft.client.model.geom.PartPose;')
    w('import net.minecraft.client.model.geom.builders.CubeDeformation;')
    w('import net.minecraft.client.model.geom.builders.CubeListBuilder;')
    w('import net.minecraft.client.model.geom.builders.LayerDefinition;')
    w('import net.minecraft.client.model.geom.builders.MeshDefinition;')
    w('import net.minecraft.client.model.geom.builders.PartDefinition;')
    w('')
    w('import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;')
    w('')
    w('import com.onepiecebosses.BossesMod;')
    w('')
    w('/**')
    w(' * Every rogue\'s own body, with wild One Piece proportions instead of the player shape. Each keeps the player')
    w(' * model\'s parts (head, body, arms, legs) so it walks, swings and looks around like one, but the parts sit where')
    w(' * that rogue\'s body needs them and are built from its own boxes. Skins are 128x128 and match these boxes.')
    w(' * GENERATED by tools/gen_models.py, which also paints the skins: change the shapes there and run it again')
    w(' * instead of editing this file.')
    w(' */')
    w('public final class RogueModels {')
    w('\tpublic static final Set<String> IDS = Set.of(%s);' % ', '.join('"%s"' % i for i in rogues))
    w('')
    w('\t/** Each rogue\'s right shoulder (x, y, z); RogueModel keeps the arms there while the boss swings. */')
    w('\tpublic static final Map<String, float[]> SHOULDERS = Map.of(%s);' % ', '.join(
        '"%s", new float[] {%s}' % (i, ', '.join(f(v) for v in rogues[i]['pivots']['arm'])) for i in rogues))
    w('')
    w('\t/** How far below the shoulder each rogue\'s hand is, in pixels (a player\'s is about 10). */')
    w('\tpublic static final Map<String, Float> HANDS = Map.of(%s);' % ', '.join(
        '"%s", %s' % (i, f(max(b['y'] + b['h'] for b in rogues[i]['boxes'] if b['part'] == 'arm' and 'pivot' not in b and 'only' not in b) - 1.5)) for i in rogues))
    w('')
    w('\tprivate RogueModels() {')
    w('\t}')
    w('')
    w('\tpublic static ModelLayerLocation layer(String id) {')
    w('\t\treturn new ModelLayerLocation(BossesMod.id("rogue_" + id), "main");')
    w('\t}')
    w('')
    w('\t/** Registers one model layer per rogue. BossesClient calls this. */')
    w('\tpublic static void register() {')
    w('\t\tfor (String id : IDS) {')
    w('\t\t\tModelLayerRegistry.registerModelLayer(layer(id), () -> create(id));')
    w('\t\t}')
    w('\t}')
    w('')
    w('\tpublic static LayerDefinition create(String id) {')
    w('\t\t// Start from the player model so every part HumanoidModel looks for exists, then rebuild the parts.')
    w('\t\tMeshDefinition mesh = HumanoidModel.createMesh(CubeDeformation.NONE, 0.0F);')
    w('\t\tint size = switch (id) {')
    for i in rogues:
        w('\t\t\tcase "%s" -> %s(mesh);' % (i, camel(i)))
    w('\t\t\tdefault -> 64;')
    w('\t\t};')
    w('\t\treturn LayerDefinition.create(mesh, size, size);')
    w('\t}')
    w('')
    w('\t/** The basic parts at this rogue\'s pivots, with no boxes of their own (the boxes are their children). */')
    w('\tprivate static PartDefinition[] parts(MeshDefinition mesh, float[] head, float[] body, float[] arm, float[] leg) {')
    w('\t\tPartDefinition root = mesh.getRoot();')
    w('\t\tPartDefinition headPart = root.addOrReplaceChild("head", CubeListBuilder.create(), PartPose.offset(head[0], head[1], head[2]));')
    w('\t\theadPart.addOrReplaceChild("hat", CubeListBuilder.create(), PartPose.ZERO);')
    w('\t\treturn new PartDefinition[] {')
    w('\t\t\theadPart,')
    w('\t\t\troot.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(body[0], body[1], body[2])),')
    w('\t\t\troot.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offset(arm[0], arm[1], arm[2])),')
    w('\t\t\troot.addOrReplaceChild("left_arm", CubeListBuilder.create(), PartPose.offset(-arm[0], arm[1], arm[2])),')
    w('\t\t\troot.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(leg[0], leg[1], leg[2])),')
    w('\t\t\troot.addOrReplaceChild("left_leg", CubeListBuilder.create(), PartPose.offset(-leg[0], leg[1], leg[2])),')
    w('\t\t};')
    w('\t}')
    sway = {}
    for i, spec in rogues.items():
        boxes, spots, size = layouts[i]
        p = spec['pivots']
        w('')
        w('\tprivate static int %s(MeshDefinition mesh) {' % camel(i))
        w('\t\tPartDefinition[] p = parts(mesh, new float[] {%s}, new float[] {%s}, new float[] {%s}, new float[] {%s});' % tuple(
            ', '.join(f(v) for v in p[k]) for k in ('head', 'body', 'arm', 'leg')))
        w('\t\tPartDefinition head = p[0], body = p[1], rightArm = p[2], leftArm = p[3], rightLeg = p[4], leftLeg = p[5];')
        var = {'head': 'head', 'body': 'body', 'right_arm': 'rightArm', 'left_arm': 'leftArm', 'right_leg': 'rightLeg', 'left_leg': 'leftLeg'}
        sways = []
        named = {}
        paths = {}
        for n, (b, (u, v)) in enumerate(zip(boxes, spots)):
            name = 'b%d' % n
            parent = var[b['part']]
            if b.get('parent'):
                parent = named[b['parent']]
            if b.get('sway'):
                name = 'sway%d' % len(sways)
                path = (paths[b['parent']] if b.get('parent') else b['part']) + '/' + name
                paths[name] = path
                sways.append((path, b['sway'], b.get('parent') is not None))
            pv = b.get('pivot', (0, 0, 0))
            rot = b.get('rot', (0, 0, 0))
            # A box with its own pivot is drawn relative to that pivot (its x, y, z start from there).
            decl = 'PartDefinition %s = ' % name if b.get('sway') else ''
            w('\t\t%s%s.addOrReplaceChild("%s", CubeListBuilder.create().texOffs(%d, %d).addBox(%s, %s, %s, %s, %s, %s),' % (
                decl, parent, name, u, v, f(b['x']), f(b['y']), f(b['z']), f(b['w']), f(b['h']), f(b['d'])))
            w('\t\t\t\tPartPose.offsetAndRotation(%s, %s, %s, %s, %s, %s));' % tuple(f(x) for x in tuple(pv) + tuple(rot)))
            if b.get('sway'):
                named[name] = name
                named['sway%d' % (len(sways) - 1)] = name
        w('\t\treturn %d;' % size)
        w('\t}')
        sway[i] = sways
    w('')
    w('\t/** Coat tails, trains and skirts that swing as the boss walks, by their path from the model root: 1 swings out behind, -1 in front. */')
    w('\tpublic static Map<String, Integer> sway(String id) {')
    w('\t\treturn switch (id) {')
    for i, sw in sway.items():
        if sw:
            w('\t\t\tcase "%s" -> Map.of(%s);' % (i, ', '.join('"%s", %d' % (n, d) for n, d, _ in sw)))
    w('\t\t\tdefault -> Map.of();')
    w('\t\t};')
    w('\t}')
    w('}')
    return '\n'.join(lines) + '\n'


def camel(s):
    a = s.split('_')
    return a[0] + ''.join(x.title() for x in a[1:])


def main(root):
    res = os.path.join(root, 'src/main/resources/assets/opbosses/textures/entity/boss')
    os.makedirs(res, exist_ok=True)
    layouts = {}
    for i, spec in ROGUES.items():
        boxes = expand(spec)
        for size in (128, 256):
            spots = pack(boxes, size)
            if spots:
                break
        else:
            sys.exit('%s: the boxes do not fit in a 256x256 skin' % i)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        rnd = random.Random(i)
        for b, (u, v) in zip(boxes, spots):
            paint_box(img, u, v, b, rnd)
        img.save(os.path.join(res, i + '.png'))
        layouts[i] = (boxes, spots, size)
    out = os.path.join(root, 'src/main/java/com/onepiecebosses/client/RogueModels.java')
    with open(out, 'w') as fh:
        fh.write(java(ROGUES, layouts))
    print('Built %d rogue models' % len(ROGUES))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
