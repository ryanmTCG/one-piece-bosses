#!/usr/bin/env python3
"""Draws the placeholder art and writes the item JSON for every rogue boss in bosses.json.

    python3 tools/gen_assets.py src/main/resources

Needs Pillow. Skins are 64x64 (the zombie / classic player layout); swap any of them for a real skin with the
same name in assets/opbosses/textures/entity/boss/. A new boss needs an entry in SKINS (and TROPHIES for its
trophy's look), or this stops and says which one is missing.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

# Per boss: skin, hair, eyes, shirt, coat (None = no coat), pants, boots, accent, and extras drawn on top.
SKINS = {
    "saltjaw_rourke": dict(skin=(196, 140, 100), hair=(70, 50, 35), eyes=(30, 30, 30), shirt=(150, 140, 120),
                           coat=(95, 70, 45), pants=(60, 60, 75), boots=(45, 35, 25), accent=(120, 120, 125),
                           extras=["beard", "chain", "bandana"]),
    "corvina_fog_widow": dict(skin=(225, 205, 195), hair=(25, 22, 30), eyes=(140, 200, 220), shirt=(60, 55, 75),
                              coat=(35, 32, 45), pants=(40, 38, 50), boots=(25, 22, 30), accent=(230, 190, 90),
                              extras=["veil", "long_hair", "lantern"]),
    "iron_tide_graves": dict(skin=(205, 160, 125), hair=(150, 150, 155), eyes=(40, 60, 90), shirt=(235, 235, 240),
                             coat=(50, 55, 70), pants=(55, 60, 80), boots=(30, 30, 35), accent=(200, 170, 60),
                             extras=["cap", "epaulettes", "torn_justice"]),
    "hollow_ronin_tsurugi": dict(skin=(20, 18, 24), hair=(20, 18, 24), eyes=(120, 230, 255), shirt=(90, 25, 30),
                                 coat=(55, 50, 60), pants=(40, 36, 46), boots=(30, 28, 34), accent=(170, 140, 70),
                                 extras=["kabuto", "menpo", "lacing"]),
    "boilerheart_gantz": dict(skin=(180, 120, 90), hair=(40, 30, 25), eyes=(255, 140, 30), shirt=(80, 70, 60),
                              coat=None, pants=(70, 60, 50), boots=(50, 45, 45), accent=(180, 100, 40),
                              extras=["boiler", "goggles", "pipes"]),
    "nereus_vane": dict(skin=(90, 150, 160), hair=(220, 230, 235), eyes=(250, 240, 120), shirt=(30, 60, 90),
                        coat=(20, 40, 70), pants=(25, 45, 65), boots=(70, 120, 130), accent=(240, 220, 150),
                        extras=["fins", "robe_trim", "long_hair"]),
}

# Trophy item: (main colour, shade, shape).
TROPHIES = {
    "rusted_anchor_link": ((150, 90, 50), (90, 55, 30), "ring"),
    "widows_lantern": ((230, 190, 90), (60, 50, 70), "lantern"),
    "deserters_epaulette": ((210, 180, 60), (130, 100, 30), "epaulette"),
    "hollow_menpo": ((40, 36, 46), (120, 230, 255), "mask"),
    "cracked_boiler_core": ((255, 140, 30), (80, 60, 50), "core"),
    "abyssal_conch": ((240, 220, 200), (60, 140, 160), "conch"),
}

TROPHY_NAMES = {
    "rusted_anchor_link": "Rusted Anchor Link",
    "widows_lantern": "Widow's Lantern",
    "deserters_epaulette": "Deserter's Epaulette",
    "hollow_menpo": "Hollow Menpo",
    "cracked_boiler_core": "Cracked Boiler Core",
    "abyssal_conch": "Abyssal Conch",
}


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def box(d, x, y, w, h, c):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c + (255,))


def cube(d, u, v, w, h, depth, c):
    """Fills one cube's unwrapped faces (the Minecraft box UV layout) with a lightly shaded colour."""
    box(d, u + depth, v, w, depth, shade(c, 1.1))              # top
    box(d, u + depth + w, v, w, depth, shade(c, 0.8))          # bottom
    box(d, u, v + depth, depth, h, shade(c, 0.9))              # right
    box(d, u + depth, v + depth, w, h, c)                      # front
    box(d, u + depth + w, v + depth, depth, h, shade(c, 0.9))  # left
    box(d, u + 2 * depth + w, v + depth, w, h, shade(c, 0.85)) # back


def skin(spec):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s, coat = spec["skin"], spec["coat"]
    # Head, body, arms, legs (right side at the top, left side in the bottom half).
    cube(d, 0, 0, 8, 8, 8, s)
    box(d, 8, 0, 8, 8, spec["hair"])                    # hair on top
    box(d, 8, 8, 8, 2, spec["hair"])                    # fringe
    box(d, 24, 8, 8, 6, spec["hair"])                   # back of head
    box(d, 9, 12, 2, 1, spec["eyes"]); box(d, 13, 12, 2, 1, spec["eyes"])
    box(d, 11, 14, 2, 1, shade(s, 0.7))                 # mouth
    cube(d, 16, 16, 8, 12, 4, spec["shirt"])            # body
    for u, v in ((40, 16), (32, 48)):                   # arms
        cube(d, u, v, 4, 12, 4, coat or s)
        box(d, u + 4, v + 4 + 9, 4, 3, s)               # hands
    for u, v in ((0, 16), (16, 48)):                    # legs
        cube(d, u, v, 4, 12, 4, spec["pants"])
        box(d, u, v + 4 + 9, 16, 3, spec["boots"])
    if coat:
        box(d, 20, 20, 2, 12, coat); box(d, 26, 20, 2, 12, coat)   # open coat over the shirt
        box(d, 32, 20, 8, 12, coat)                                  # back of the coat
    box(d, 20, 29, 8, 1, spec["accent"])                             # belt

    ex = spec["extras"]
    a = spec["accent"]
    if "beard" in ex:
        box(d, 8, 13, 8, 3, spec["hair"]); box(d, 11, 14, 2, 1, shade(s, 0.7))
    if "bandana" in ex:
        box(d, 40, 8, 8, 2, (170, 40, 40))
        box(d, 32, 8, 32, 2, (170, 40, 40))
    if "chain" in ex:
        for i in range(0, 12, 2):
            box(d, 21 + (i // 2) % 2 * 5, 20 + i, 2, 1, a)
    if "veil" in ex:
        box(d, 40, 8, 8, 4, (60, 60, 70)); box(d, 32, 8, 32, 3, (60, 60, 70))
        box(d, 40, 0, 8, 8, (40, 36, 50))
    if "long_hair" in ex:
        box(d, 0, 8, 8, 8, spec["hair"]); box(d, 16, 8, 8, 8, spec["hair"]); box(d, 24, 8, 8, 8, spec["hair"])
        box(d, 32, 20, 8, 5, spec["hair"])
    if "lantern" in ex:
        box(d, 44, 28, 4, 4, a)
    if "cap" in ex:
        box(d, 40, 0, 8, 8, (240, 240, 245)); box(d, 32, 8, 32, 2, (240, 240, 245)); box(d, 40, 10, 8, 1, (40, 40, 60))
    if "epaulettes" in ex:
        box(d, 44, 16, 4, 4, a); box(d, 36, 48, 4, 4, a)
    if "torn_justice" in ex:
        box(d, 33, 22, 6, 1, (200, 200, 205)); box(d, 34, 24, 3, 1, (200, 200, 205))
    if "kabuto" in ex:
        box(d, 40, 0, 8, 8, (50, 46, 56)); box(d, 32, 8, 32, 3, (50, 46, 56)); box(d, 42, 8, 4, 1, a)
    if "menpo" in ex:
        box(d, 8, 13, 8, 3, (60, 20, 24))
    if "lacing" in ex:
        for y in range(21, 29, 2):
            box(d, 20, y, 8, 1, a)
    if "boiler" in ex:
        box(d, 21, 21, 6, 6, (90, 90, 95)); box(d, 23, 23, 2, 2, (255, 140, 30))
        box(d, 33, 20, 6, 10, (90, 90, 95))
    if "goggles" in ex:
        box(d, 40, 11, 8, 2, (60, 50, 40)); box(d, 41, 11, 2, 2, (255, 180, 60)); box(d, 45, 11, 2, 2, (255, 180, 60))
    if "pipes" in ex:
        box(d, 44, 20, 1, 9, a); box(d, 36, 52, 1, 9, a)
    if "fins" in ex:
        box(d, 32, 8, 8, 6, shade(s, 0.8)); box(d, 48, 8, 8, 6, shade(s, 0.8))
        box(d, 36, 32, 4, 2, shade(s, 0.8))
    if "robe_trim" in ex:
        box(d, 20, 20, 1, 12, a); box(d, 27, 20, 1, 12, a)
    return img


def item_texture(main, dark, shape):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shape == "ring":
        d.ellipse([2, 3, 13, 12], outline=main + (255,), width=3); d.point([(4, 9), (10, 5)], fill=dark + (255,))
    elif shape == "lantern":
        box(d, 6, 1, 4, 2, dark); box(d, 4, 3, 8, 10, dark); box(d, 5, 4, 6, 8, main); box(d, 5, 13, 6, 2, dark)
    elif shape == "epaulette":
        d.ellipse([2, 4, 13, 10], fill=main + (255,)); [box(d, x, 10, 1, 4, dark) for x in range(3, 13, 2)]
    elif shape == "mask":
        d.ellipse([2, 2, 13, 14], fill=main + (255,)); box(d, 4, 6, 3, 2, dark); box(d, 9, 6, 3, 2, dark)
        box(d, 5, 11, 6, 1, (90, 20, 24))
    elif shape == "core":
        d.ellipse([2, 2, 13, 13], fill=dark + (255,)); d.ellipse([5, 5, 10, 10], fill=main + (255,))
        d.line([(3, 4), (7, 8), (6, 12)], fill=(20, 20, 20, 255))
    elif shape == "conch":
        d.polygon([(2, 12), (8, 2), (14, 9), (9, 14)], fill=main + (255,)); d.line([(4, 11), (9, 5), (12, 9)], fill=dark + (255,))
    elif shape == "poster":
        box(d, 2, 1, 12, 14, (215, 190, 140)); box(d, 3, 2, 10, 2, (90, 40, 30))
        box(d, 5, 5, 6, 5, (120, 110, 100)); box(d, 7, 6, 2, 1, (40, 30, 30))   # a figure in shadow
        box(d, 4, 11, 8, 1, (90, 40, 30)); box(d, 6, 13, 4, 1, (90, 40, 30))
        box(d, 12, 1, 2, 2, main)                                                  # tier-coloured seal
    return img


POSTER_SEAL = {1: (230, 230, 230), 2: (120, 200, 120), 3: (240, 200, 60), 4: (170, 80, 220), 5: (220, 40, 40)}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main(res):
    bosses = json.load(open(os.path.join(res, "opbosses/bosses.json")))["bosses"]
    assets = os.path.join(res, "assets/opbosses")
    missing = [b["id"] for b in bosses if b["id"] not in SKINS] + [b["trophy"] for b in bosses if b.get("trophy") and b["trophy"] not in TROPHIES]
    if missing:
        sys.exit("No look yet for: " + ", ".join(missing) + " (add them to SKINS / TROPHIES)")
    lang = {"itemGroup.opbosses.bosses": "One Piece: Rogue Bosses", "entity.opbosses.rogue_boss": "Rogue Boss"}
    for b in bosses:
        os.makedirs(os.path.join(assets, "textures/entity/boss"), exist_ok=True)
        skin(SKINS[b["id"]]).save(os.path.join(assets, "textures/entity/boss", b["id"] + ".png"))
        items = [("rumor_" + b["id"], item_texture(POSTER_SEAL[b["tier"]], None, "poster"))]
        if b.get("trophy"):
            main_c, dark, shape = TROPHIES[b["trophy"]]
            items.append((b["trophy"], item_texture(main_c, dark, shape)))
            lang["item.opbosses." + b["trophy"]] = TROPHY_NAMES.get(b["trophy"], b["trophy"].replace("_", " ").title())
        for name, texture in items:
            os.makedirs(os.path.join(assets, "textures/item"), exist_ok=True)
            texture.save(os.path.join(assets, "textures/item", name + ".png"))
            write_json(os.path.join(assets, "models/item", name + ".json"),
                       {"parent": "minecraft:item/generated", "textures": {"layer0": "opbosses:item/" + name}})
            write_json(os.path.join(assets, "items", name + ".json"),
                       {"model": {"type": "minecraft:model", "model": "opbosses:item/" + name}})
    write_json(os.path.join(assets, "lang/en_us.json"), lang)
    print("Drew %d bosses" % len(bosses))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src/main/resources")
