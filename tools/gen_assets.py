#!/usr/bin/env python3
"""Draws the poster and trophy art and writes the item JSON and names for every rogue boss in bosses.json.
(The bosses' bodies and skins are tools/gen_models.py.)

    python3 tools/gen_assets.py src/main/resources

Needs Pillow. A new boss's trophy needs a look in TROPHIES, or this stops and says which one is missing.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

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
    missing = [b["trophy"] for b in bosses if b.get("trophy") and b["trophy"] not in TROPHIES]
    if missing:
        sys.exit("No look yet for: " + ", ".join(missing) + " (add them to TROPHIES)")
    lang = {"itemGroup.opbosses.bosses": "One Piece: Rogue Bosses", "entity.opbosses.rogue_boss": "Rogue Boss"}
    for b in bosses:
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
