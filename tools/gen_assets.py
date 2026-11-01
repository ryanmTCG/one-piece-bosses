#!/usr/bin/env python3
"""Draws the poster, trophy and lair key art and writes the item JSON and names for every rogue boss in bosses.json.
(The bosses' bodies and skins are tools/gen_models.py.)

    python3 tools/gen_assets.py src/main/resources

Needs Pillow. A new boss's trophy needs a look in TROPHIES, or this stops and says which one is missing.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_chests import CHESTS  # noqa: E402  (the lair chests' names)

# Trophy item: (main colour, shade, shape).
TROPHIES = {
    "rusted_anchor_link": ((150, 90, 50), (90, 55, 30), "ring"),
    "widows_lantern": ((230, 190, 90), (60, 50, 70), "lantern"),
    "deserters_epaulette": ((210, 180, 60), (130, 100, 30), "epaulette"),
    "hollow_menpo": ((40, 36, 46), (120, 230, 255), "mask"),
    "cracked_boiler_core": ((255, 140, 30), (80, 60, 50), "core"),
    "abyssal_conch": ((240, 220, 200), (60, 140, 160), "conch"),
    "golden_casino_chip": ((240, 200, 60), (170, 30, 40), "chip"),
    "diva_headphones": ((244, 244, 248), (232, 144, 184), "headphones"),
    "smasher_knuckle": ((110, 90, 150), (50, 50, 60), "knuckle"),
    "clank_clank_rivet": ((150, 150, 160), (70, 70, 80), "rivet"),
    "golden_lion_helm": ((140, 90, 48), (240, 200, 64), "wheel"),
}

TROPHY_NAMES = {
    "rusted_anchor_link": "Rusted Anchor Link",
    "widows_lantern": "Widow's Lantern",
    "deserters_epaulette": "Deserter's Epaulette",
    "hollow_menpo": "Hollow Menpo",
    "cracked_boiler_core": "Cracked Boiler Core",
    "abyssal_conch": "Abyssal Conch",
    "golden_casino_chip": "Tesoro's Golden Chip",
    "diva_headphones": "Diva's Headphones",
    "smasher_knuckle": "Battle Smasher Knuckle",
    "clank_clank_rivet": "Clank-Clank Rivet",
    "golden_lion_helm": "Golden Lion's Helm",
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
    elif shape == "chip":
        d.ellipse([1, 1, 14, 14], fill=main + (255,)); d.ellipse([4, 4, 11, 11], outline=dark + (255,))
        for (x, y) in ((7, 1), (7, 13), (1, 7), (13, 7)):
            box(d, x, y, 2, 2, dark)
        box(d, 7, 6, 2, 4, shade(main, 0.7))
    elif shape == "headphones":
        d.arc([2, 1, 13, 12], 180, 360, fill=main + (255,), width=2)
        box(d, 1, 7, 4, 6, dark); box(d, 11, 7, 4, 6, dark); box(d, 2, 8, 2, 4, main); box(d, 12, 8, 2, 4, main)
    elif shape == "knuckle":
        box(d, 2, 4, 12, 9, main); [box(d, x, 3, 2, 2, dark) for x in (3, 6, 9, 12)]
        box(d, 2, 8, 12, 1, dark); box(d, 4, 10, 8, 1, (200, 170, 255))
    elif shape == "rivet":
        d.polygon([(8, 1), (14, 5), (14, 11), (8, 15), (2, 11), (2, 5)], fill=main + (255,))
        d.ellipse([5, 5, 10, 10], fill=dark + (255,)); d.point([(6, 6)], fill=(230, 230, 240, 255))
    elif shape == "wheel":
        d.ellipse([2, 2, 13, 13], outline=main + (255,), width=2)
        d.line([(8, 0), (8, 15)], fill=main + (255,)); d.line([(0, 8), (15, 8)], fill=main + (255,))
        d.line([(3, 3), (12, 12)], fill=main + (255,)); d.line([(12, 3), (3, 12)], fill=main + (255,))
        d.ellipse([6, 6, 9, 9], fill=dark + (255,))
    elif shape == "key":
        # An old iron-bound key: a ring bow in the boss's colour, a long shaft and a toothed bit.
        d.ellipse([1, 1, 7, 7], outline=main + (255,), width=2); d.point([(4, 4)], fill=dark + (255,))
        d.line([(6, 6), (13, 13)], fill=shade(main, 0.8) + (255,), width=2)
        box(d, 10, 12, 2, 3, dark); box(d, 12, 10, 3, 2, dark); box(d, 13, 13, 2, 2, dark)
    elif shape == "charter":
        # A rolled charter with a gold seal: the lair's plans, to rebuild it.
        box(d, 3, 2, 10, 12, (225, 205, 160)); box(d, 2, 1, 12, 2, (150, 110, 70)); box(d, 2, 13, 12, 2, (150, 110, 70))
        for y in (4, 6, 8):
            box(d, 5, y, 6, 1, (110, 90, 70))
        d.ellipse([8, 8, 13, 13], fill=main + (255,)); d.point([(10, 10)], fill=dark + (255,))
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
    lang = {"itemGroup.opbosses.bosses": "One Piece: Rogue Bosses", "entity.opbosses.rogue_boss": "Rogue Boss",
            "entity.opbosses.wandering_hunter": "Wandering Bounty Hunter", "entity.opbosses.rookie_raider": "Rookie Raider"}
    for b in bosses:
        items = [("rumor_" + b["id"], item_texture(POSTER_SEAL[b["tier"]], None, "poster"))]
        key_c, key_d = (TROPHIES[b["trophy"]][:2] if b.get("trophy") else ((200, 170, 70), (70, 60, 50)))
        items.append(("key_" + b["id"], item_texture(key_c, key_d, "key")))
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
    charter = item_texture((220, 170, 50), (150, 30, 30), "charter")
    os.makedirs(os.path.join(assets, "textures/item"), exist_ok=True)
    charter.save(os.path.join(assets, "textures/item", "lair_charter.png"))
    write_json(os.path.join(assets, "models/item", "lair_charter.json"),
               {"parent": "minecraft:item/generated", "textures": {"layer0": "opbosses:item/lair_charter"}})
    write_json(os.path.join(assets, "items", "lair_charter.json"), {"model": {"type": "minecraft:model", "model": "opbosses:item/lair_charter"}})
    lang["item.opbosses.lair_charter"] = "Lair Restoration Charter"
    for cid, c in CHESTS.items():
        lang["block.opbosses." + cid + "_chest"] = c["name"]
    write_json(os.path.join(assets, "lang/en_us.json"), lang)
    print("Drew %d bosses" % len(bosses))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src/main/resources")
